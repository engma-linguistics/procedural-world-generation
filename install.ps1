# procgen_world installer and manager for native Windows (x86-64), the twin of install.sh (PW-1760).
#
#   irm <raw github url>/install.ps1 | iex                          install the newest release tag
#   powershell -ExecutionPolicy Bypass -File install.ps1            install from this checkout or unpacked zip
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Source C:\src\procgen -Ref v1.0.0
#   & ([scriptblock]::Create((irm <raw url>/install.ps1))) -Data D:\worlds    options with the one-liner
#
# Nothing needs to be on the machine but Windows PowerShell 5.1 (built in): the pinned uv below fetches a private
# Python 3.14 and the wheels. git is used when it is there; a GitHub source works without it (the zip of the tag).
#
# After install, the `planet` command manages it:
#   planet self open | first-run | probe | update | rollback | uninstall | status
#
# Layout (the install root, default %LOCALAPPDATA%\procgen-world):
#   uv\uv.exe            a pinned uv, private to this install
#   python\              the Python 3.14 uv fetched (private too)
#   cache\               uv's cache
#   app\<version>\       the code of one version and its .venv; numba's cache sits beside the code
#   app\current.txt, app\previous.txt   the version in use and the one `rollback` returns to (no symlinks on Windows)
#   bin\planet.cmd       the launcher; bin\ is added to your user PATH (uninstall takes it out again)
#   bin\manage.ps1       this script, as shipped by the current version
#   install.json         what the installer did (source, data, config, shortcut, PATH), for update and uninstall
# The config is %APPDATA%\procgen-world\config.toml; the data folder (default %USERPROFILE%\procgen-world-data) is never
# touched by update or rollback, and uninstall asks before deleting it. Start menu: "Procgen World".
#
# Options (both -Name and --name spellings work):
#   -Root DIR  -Data DIR  -Source SRC  -Ref REF  -Port N  -Jobs N  -Uv PATH\uv.exe
#   -NoDesktop (no Start-menu shortcut)  -NoModifyPath  -NoFirstRun  -Starter / -NoStarter
#   -DeleteData / -KeepData (uninstall)  -Yes  -DryRun  -Help
# Environment: PROCGEN_ROOT, PROCGEN_SOURCE, PLANET_DATA, PROCGEN_NO_GIT=1 (use the GitHub zip even with git),
# PROCGEN_MIN_FREE_GB (the least free disk accepted, default 20).

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$UV_VERSION = '0.12.7'
$DEFAULT_SOURCE = 'https://github.com/engma-linguistics/procedural-world-generation'
$APP = 'procgen-world'

# uv release checksums (https://github.com/astral-sh/uv/releases/tag/$UV_VERSION)
$UV_SHA256 = @{
    'x86_64-pc-windows-msvc' = 'bf1518af459a3915511a11fdc6e2f43ef9a2afa138b9d498eeb9642fe9d85218'
}

# ---------------------------------------------------------------------------------------------- options
$S = @{
    Cmd = 'install'; Root = $env:PROCGEN_ROOT; Data = $env:PLANET_DATA; Source = $env:PROCGEN_SOURCE; Ref = ''
    Port = 8765; Jobs = ''; Uv = ''; DryRun = $false; Yes = $false; Desktop = $true; ModifyPath = $true
    FirstRun = $true; Starter = 'ask'; DeleteData = 'ask'; Help = $false
}
$ScriptFile = $PSCommandPath  # (empty under `irm | iex`)

function Read-Options([object[]]$argv) {
    $i = 0
    $verbs = 'install', 'update', 'rollback', 'uninstall', 'status', 'first-run', 'probe', 'open'
    while ($i -lt $argv.Count) {
        $a = [string]$argv[$i]
        $name = ($a -replace '^-{1,2}', '').ToLower() -replace ':$', ''
        $val = { if ($i + 1 -ge $argv.Count) { throw "$a needs a value" }; [string]$argv[$i + 1] }
        if ($a -notlike '-*') {
            if ($a -eq 'self') { $i++; continue }  # (planet self <verb> passes "self" through)
            if ($verbs -notcontains $a) { throw "unknown command: $a (see -Help)" }
            $S.Cmd = $a
        } else {
            switch ($name) {
                'root' { $S.Root = & $val; $i++ }
                'data' { $S.Data = & $val; $i++ }
                'source' { $S.Source = & $val; $i++ }
                'ref' { $S.Ref = & $val; $i++ }
                'port' { $S.Port = [int](& $val); $i++ }
                'jobs' { $S.Jobs = & $val; $i++ }
                'uv' { $S.Uv = & $val; $i++ }
                { $_ -in 'nodesktop', 'no-desktop' } { $S.Desktop = $false }
                { $_ -in 'nomodifypath', 'no-modify-path' } { $S.ModifyPath = $false }
                { $_ -in 'nofirstrun', 'no-first-run' } { $S.FirstRun = $false }
                'starter' { $S.Starter = 'y' }
                { $_ -in 'nostarter', 'no-starter' } { $S.Starter = 'n' }
                { $_ -in 'deletedata', 'delete-data' } { $S.DeleteData = 'y' }
                { $_ -in 'keepdata', 'keep-data' } { $S.DeleteData = 'n' }
                { $_ -in 'yes', 'y' } { $S.Yes = $true }
                { $_ -in 'dryrun', 'dry-run' } { $S.DryRun = $true }
                { $_ -in 'help', 'h' } { $S.Help = $true }
                default { throw "unknown argument: $a (see -Help)" }
            }
        }
        $i++
    }
}

# ---------------------------------------------------------------------------------------------- helpers
function Say([string]$m) { Write-Host $m }
function Step([string]$m) { Write-Host "==> $m" }
function Warn([string]$m) { Write-Warning $m }
function Die([string]$m) { throw "error: $m" }
function Now { [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() }

# run a native program with its output discarded and return its exit code (Windows PowerShell 5.1 turns a redirected
# native stderr into errors, which $ErrorActionPreference = 'Stop' would make fatal)
function Quiet([scriptblock]$b) {
    $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & $b *> $null } finally { $ErrorActionPreference = $old }
    $LASTEXITCODE
}

# the least free disk (GB) the installer accepts; PROCGEN_MIN_FREE_GB lowers it (the CI runners have little)
function Min-Free { if ($env:PROCGEN_MIN_FREE_GB) { [int]$env:PROCGEN_MIN_FREE_GB } else { 20 } }

function Ask([string]$q, [string]$default) {
    if ($S.Yes) { return $default -eq 'y' }
    $interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
    if (-not $interactive) { return $default -eq 'y' }
    $p = if ($default -eq 'y') { '[Y/n]' } else { '[y/N]' }
    $a = Read-Host "$q $p"
    if ($a -match '^[Yy]') { return $true }
    if ($a -match '^[Nn]') { return $false }
    return $default -eq 'y'
}

function Run-Or-Print([string]$what, [scriptblock]$do) {
    if ($S.DryRun) { Say "  [dry-run] $what" } else { & $do }
}

function Free-GB([string]$path) {
    $p = $path
    while ($p -and -not (Test-Path -LiteralPath $p)) { $p = Split-Path -Parent $p }
    if (-not $p) { $p = $env:SystemDrive + '\' }
    $drive = New-Object System.IO.DriveInfo ([System.IO.Path]::GetPathRoot((Resolve-Path -LiteralPath $p).Path))
    [int][math]::Floor($drive.AvailableFreeSpace / 1GB)
}

function Fetch-Url([string]$url, [string]$dest) {
    $tls = [Net.ServicePointManager]::SecurityProtocol
    [Net.ServicePointManager]::SecurityProtocol = $tls -bor [Net.SecurityProtocolType]::Tls12
    $old = $ProgressPreference; $ProgressPreference = 'SilentlyContinue'  # (5.1's progress bar slows downloads tenfold)
    try {
        for ($t = 1; $t -le 3; $t++) {
            try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dest; return }
            catch { if ($t -eq 3) { throw } ; Start-Sleep -Seconds 2 }
        }
    } finally { $ProgressPreference = $old }
}

function Have-Git { ($env:PROCGEN_NO_GIT -ne '1') -and [bool](Get-Command git -ErrorAction SilentlyContinue) }
function Is-GitUrl([string]$src) { $src -match '^(https?://|git@|ssh://|git://)' }
function Is-GitRepo([string]$src) {
    if (-not (Have-Git) -or -not (Test-Path -LiteralPath $src -PathType Container)) { return $false }
    (Quiet { git -C $src rev-parse --git-dir }) -eq 0
}
function GitHub-Slug([string]$src) {
    if ($src -match '^https://github\.com/([^/]+/[^/]+?)(\.git)?/?$') { return $Matches[1] }
    return $null
}
function Use-Archive { (-not (Have-Git)) -and [bool](GitHub-Slug $S.Source) }

# every uv call runs with a private Python, a private cache and no user config; the caller's environment is restored
function Invoke-Uv([string[]]$uvArgs, [string]$cwd) {
    $set = @{ UV_PYTHON_INSTALL_DIR = "$($S.Root)\python"; UV_CACHE_DIR = "$($S.Root)\cache"
              UV_PYTHON_PREFERENCE = 'only-managed'; UV_NO_CONFIG = '1'; UV_NO_PROGRESS = '1'
              VIRTUAL_ENV = $null; UV_PROJECT_ENVIRONMENT = $null }
    $saved = @{}
    foreach ($k in $set.Keys) { $saved[$k] = [Environment]::GetEnvironmentVariable($k, 'Process')
                                [Environment]::SetEnvironmentVariable($k, $set[$k], 'Process') }
    Push-Location -LiteralPath $cwd
    $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & $script:UV @uvArgs; return $LASTEXITCODE -eq 0 }
    finally { $ErrorActionPreference = $old; Pop-Location; foreach ($k in $saved.Keys) { [Environment]::SetEnvironmentVariable($k, $saved[$k], 'Process') } }
}

# run the installed planet with extra environment variables, its output indented
function Invoke-Planet([hashtable]$envs, [string[]]$planetArgs) {
    $saved = @{}
    foreach ($k in $envs.Keys) { $saved[$k] = [Environment]::GetEnvironmentVariable($k, 'Process')
                                 [Environment]::SetEnvironmentVariable($k, $envs[$k], 'Process') }
    try {
        $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'  # (5.1 turns a native program's stderr into errors)
        & (Join-Path $S.Root 'bin\planet.cmd') @planetArgs 2>&1 | ForEach-Object { Say "    | $_" }
        $code = $LASTEXITCODE
        $ErrorActionPreference = $old
        return $code -eq 0
    } finally { foreach ($k in $saved.Keys) { [Environment]::SetEnvironmentVariable($k, $saved[$k], 'Process') } }
}

# ---------------------------------------------------------------------------------------------- paths and state
function Init-Paths {
    if (-not $S.Root) { $S.Root = Join-Path $env:LOCALAPPDATA $APP }
    $S.Root = [System.IO.Path]::GetFullPath($S.Root)
    $S.ConfigDir = Join-Path $env:APPDATA $APP
    $S.Config = Join-Path $S.ConfigDir 'config.toml'
    $S.State = Join-Path $S.Root 'install.json'
    $script:UV = Join-Path $S.Root 'uv\uv.exe'
    $S.Shortcut = ''; $S.PathAdded = ''
    if (Test-Path -LiteralPath $S.State) {  # what an earlier install recorded fills what this call did not give
        $st = Get-Content -Raw -LiteralPath $S.State | ConvertFrom-Json
        if (-not $S.Source) { $S.Source = $st.source }
        if (-not $S.Data) { $S.Data = $st.data }
        if ($st.config) { $S.Config = $st.config; $S.ConfigDir = Split-Path -Parent $st.config }
        $S.Shortcut = [string]$st.shortcut; $S.PathAdded = [string]$st.path_added
    }
}

function Save-State {
    if ($S.DryRun) { return }
    @{ source = $S.Source; data = $S.Data; config = $S.Config; shortcut = $S.Shortcut; path_added = $S.PathAdded } |
        ConvertTo-Json | Set-Content -LiteralPath $S.State -Encoding UTF8
}

function Current-Version { $f = Join-Path $S.Root 'app\current.txt'; if (Test-Path -LiteralPath $f) { (Get-Content -LiteralPath $f -TotalCount 1).Trim() } else { '' } }
function Previous-Version { $f = Join-Path $S.Root 'app\previous.txt'; if (Test-Path -LiteralPath $f) { (Get-Content -LiteralPath $f -TotalCount 1).Trim() } else { '' } }
function Write-Text([string]$path, [string]$text) {  # UTF-8 without a BOM (5.1's -Encoding UTF8 writes one; cmd and tomllib don't want it)
    [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))
}

# ---------------------------------------------------------------------------------------------- platform
function Get-Target {
    if ([Environment]::OSVersion.Platform -ne 'Win32NT') { Die 'install.ps1 is for Windows; on Linux and macOS run install.sh' }
    if (-not [Environment]::Is64BitOperatingSystem) { Die 'a 64-bit Windows is needed' }
    $arch = $env:PROCESSOR_ARCHITECTURE
    if ($env:PROCESSOR_ARCHITEW6432) { $arch = $env:PROCESSOR_ARCHITEW6432 }
    # uv.lock's piper-tts has no wheel for Windows on ARM (it would need a C compiler), so only x86-64 is installed
    if ($arch -eq 'ARM64') { Die 'Windows on ARM is not supported yet: piper-tts publishes no ARM64 wheel for Windows' }
    if ($arch -ne 'AMD64') { Die "unsupported CPU: $arch" }
    'x86_64-pc-windows-msvc'
}

function Check-Disk([string]$path) {
    $f = Free-GB $path
    if ($f -lt (Min-Free)) { Die "only $f GB free under $path; procgen_world needs at least 20 GB (an L7 world family is ~3 GB, plus the tile cache)" }
    elseif ($f -lt 50) { Warn "only $f GB free under $path; 50 GB or more is recommended" }
}

# ---------------------------------------------------------------------------------------------- uv
function Install-Uv([string]$target) {
    if (Test-Path -LiteralPath $script:UV) {
        $v = & $script:UV --version
        if ("$v" -match " $([regex]::Escape($UV_VERSION))( |$)") { Say "    uv $UV_VERSION already in $($S.Root)\uv"; return }
    }
    Run-Or-Print "mkdir $($S.Root)\uv" { New-Item -ItemType Directory -Force -Path (Join-Path $S.Root 'uv') | Out-Null }
    if ($S.Uv) {
        $v = & $S.Uv --version
        if ("$v" -notmatch " $([regex]::Escape($UV_VERSION))( |$)") { Warn "$($S.Uv) is not uv $UV_VERSION ($v)" }
        Run-Or-Print "copy $($S.Uv) $script:UV" { Copy-Item -LiteralPath $S.Uv -Destination $script:UV -Force }
        return
    }
    $sum = $UV_SHA256[$target]
    if (-not $sum) { Die "no pinned uv for $target" }
    $url = "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$target.zip"
    Say "    downloading uv $UV_VERSION ($target)"
    if ($S.DryRun) { Say "  [dry-run] fetch $url, check sha256 $sum"; return }
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("procgen-uv-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        Fetch-Url $url "$tmp\uv.zip"
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath "$tmp\uv.zip").Hash.ToLower() -ne $sum) { Die 'uv download failed its checksum' }
        Expand-Archive -LiteralPath "$tmp\uv.zip" -DestinationPath "$tmp\x" -Force
        Copy-Item -LiteralPath "$tmp\x\uv.exe" -Destination $script:UV -Force
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

# ---------------------------------------------------------------------------------------------- source
function Default-Source {
    if ($ScriptFile) {
        $here = Split-Path -Parent $ScriptFile
        if ((Test-Path "$here\pyproject.toml") -and (Test-Path "$here\planet") -and ($here -ne (Join-Path $S.Root 'bin'))) { return $here }
    }
    $DEFAULT_SOURCE
}

function Sort-Versions([string[]]$tags) {  # v1.10.0 after v1.9.0 (sort -V)
    $tags | Where-Object { $_ -match '^v\d' } | Sort-Object { $p = ($_ -replace '^v', '') -split '[^0-9]+' | Where-Object { $_ -ne '' }
                                                              ($p | ForEach-Object { '{0:D8}' -f [int]$_ }) -join '.' }
}

function Newest-Tag {
    if (Use-Archive) {
        $tmp = [System.IO.Path]::GetTempFileName()
        try {
            Fetch-Url "https://api.github.com/repos/$(GitHub-Slug $S.Source)/tags?per_page=100" $tmp
            $names = (Get-Content -Raw -LiteralPath $tmp | ConvertFrom-Json) | ForEach-Object { $_.name }
        } catch { $names = @() } finally { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    } elseif (Is-GitUrl $S.Source) {
        $names = & git ls-remote --tags --refs $S.Source 'v[0-9]*' | ForEach-Object { $_ -replace '.*refs/tags/', '' }
    } elseif (Is-GitRepo $S.Source) {
        $names = & git -C $S.Source tag -l 'v[0-9]*'
    } else { return '' }
    $sorted = @(Sort-Versions @($names))
    if ($sorted.Count) { $sorted[-1] } else { '' }
}

function Resolve-Version {
    if ((Is-GitUrl $S.Source) -or (Is-GitRepo $S.Source)) {
        if ((Is-GitUrl $S.Source) -and -not (Use-Archive) -and -not (Have-Git)) { Die "git is needed to install from $($S.Source)" }
        if (-not $S.Ref) { $S.Ref = Newest-Tag }
        if (-not $S.Ref) {
            if (-not (Is-GitRepo $S.Source)) { Die "no release tag in $($S.Source); pass -Ref" }
            $S.Ref = 'HEAD'
        }
        if (Is-GitRepo $S.Source) {
            if ((Quiet { git -C $S.Source rev-parse --verify -q "$($S.Ref)^{commit}" }) -ne 0) { Die "no $($S.Ref) in $($S.Source)" }
            if ((Quiet { git -C $S.Source rev-parse --verify -q "refs/tags/$($S.Ref)" }) -eq 0) { $S.Version = $S.Ref }
            else { $S.Version = ($S.Ref -replace '/', '-') + '-' + (& git -C $S.Source rev-parse --short "$($S.Ref)^{commit}") }
        } else { $S.Version = $S.Ref -replace '/', '-' }
    } else {
        if (-not (Test-Path -LiteralPath (Join-Path $S.Source 'pyproject.toml'))) { Die "$($S.Source) is not a procgen_world source folder" }
        $S.Source = (Resolve-Path -LiteralPath $S.Source).Path
        $m = Select-String -LiteralPath (Join-Path $S.Source 'pyproject.toml') -Pattern '^version *= *"(.*)"' | Select-Object -First 1
        $S.Version = $m.Matches[0].Groups[1].Value + '-local'
    }
}

function Fetch-Code([string]$dest) {
    if (Use-Archive) {
        $url = "https://github.com/$(GitHub-Slug $S.Source)/archive/$($S.Ref).zip"
        if ($S.DryRun) { Say "  [dry-run] fetch $url, unzip into $dest (no git here)"; return }
        $tmp = Join-Path (Split-Path -Parent $dest) ('.src-' + [guid]::NewGuid())  # (beside dest: Move-Item can't cross drives)
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
            Fetch-Url $url "$tmp\src.zip"
            Expand-Archive -LiteralPath "$tmp\src.zip" -DestinationPath "$tmp\x" -Force
            $top = Get-ChildItem -LiteralPath "$tmp\x" -Directory | Select-Object -First 1
            Move-Item -LiteralPath $top.FullName -Destination $dest
        } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
    } elseif (Is-GitUrl $S.Source) {
        Run-Or-Print "git clone --depth 1 --branch $($S.Ref) $($S.Source) $dest" {
            & git clone -q --depth 1 --branch $S.Ref $S.Source $dest
            if ($LASTEXITCODE -ne 0) { Die "git clone of $($S.Source) failed" }
            Remove-Item -LiteralPath (Join-Path $dest '.git') -Recurse -Force
        }
    } elseif (Is-GitRepo $S.Source) {
        Run-Or-Print "git -C $($S.Source) archive $($S.Ref) | unzip into $dest" {
            $zip = Join-Path ([System.IO.Path]::GetTempPath()) ("procgen-src-" + [guid]::NewGuid() + '.zip')
            try {
                & git -C $S.Source archive --format=zip -o $zip $S.Ref
                if ($LASTEXITCODE -ne 0) { Die "git archive $($S.Ref) failed" }
                Expand-Archive -LiteralPath $zip -DestinationPath $dest -Force
            } finally { Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue }
        }
    } else {
        Run-Or-Print "copy $($S.Source) to $dest" {
            New-Item -ItemType Directory -Force -Path $dest | Out-Null
            $skip = '.venv', '.git', 'runs', 'worlds', 'zooms', 'grids', 'data', '.tiles'
            Get-ChildItem -LiteralPath $S.Source -Force | Where-Object { $skip -notcontains $_.Name } |
                ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse -Force }
        }
    }
}

function Smoke([string]$dir) {  # the app at $dir imports and its CLI answers
    $py = Join-Path $dir '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $py)) { return $false }
    $old = $env:PYTHONPATH; $env:PYTHONPATH = $dir
    try {
        if ((Quiet { & $py -c 'import numba, numpy, planet.server, planet.make' }) -ne 0) { return $false }
        return (Quiet { & $py -m planet --help }) -eq 0
    } finally { $env:PYTHONPATH = $old }
}

# fetch, sync and smoke-check one version into app\<version> (kept if already there and working)
function Build-Version {
    $dir = Join-Path $S.Root "app\$($S.Version)"
    if ((Test-Path -LiteralPath $dir) -and (Smoke $dir)) { Say "    $($S.Version) is already installed"; return }
    $part = Join-Path $S.Root "app\.$($S.Version).partial"
    if (Test-Path -LiteralPath $part) { Run-Or-Print "remove $part" { Remove-Item -LiteralPath $part -Recurse -Force } }
    Step "Fetching $($S.Version) from $($S.Source)"
    Run-Or-Print "mkdir $($S.Root)\app" { New-Item -ItemType Directory -Force -Path (Join-Path $S.Root 'app') | Out-Null }
    Fetch-Code $part
    if (Test-Path -LiteralPath $dir) { Run-Or-Print "remove $dir" { Remove-Item -LiteralPath $dir -Recurse -Force } }
    Run-Or-Print "move $part $dir" { Move-Item -LiteralPath $part -Destination $dir }
    Step 'Installing Python 3.14 and the dependencies (uv sync --frozen --no-dev)'
    $t = Now
    if ($S.DryRun) { Say "  [dry-run] (cd $dir; uv sync --frozen --no-dev)"; return }
    # the version only becomes current after it syncs and starts (Switch-To); a failure leaves current alone
    if (-not (Invoke-Uv @('sync', '--frozen', '--no-dev', '--quiet') $dir) -or -not (Smoke $dir)) {
        Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
        Die "$($S.Version) did not install or does not start; the current version is unchanged"
    }
    Say "    done in $((Now) - $t) s"
}

# make $v current, the old current previous; drop versions that are neither
function Switch-To([string]$v) {
    $old = Current-Version
    $appDir = Join-Path $S.Root 'app'
    Run-Or-Print "current = $v" {
        if ($old -and $old -ne $v) { Write-Text (Join-Path $appDir 'previous.txt') $old }
        Write-Text (Join-Path $appDir 'current.txt') $v
        Copy-Item -LiteralPath (Join-Path $appDir "$v\install.ps1") -Destination (Join-Path $S.Root 'bin\manage.ps1') -Force
    }
    if ($S.DryRun) { return }
    $keep = @($v, (Previous-Version))
    Get-ChildItem -LiteralPath $appDir -Directory | Where-Object { $keep -notcontains $_.Name -and $_.Name -notlike '.*' } |
        ForEach-Object { Say "    removing old version $($_.Name)"; Remove-Item -LiteralPath $_.FullName -Recurse -Force }
}

# ---------------------------------------------------------------------------------------------- launcher, config, menu
function Write-Launcher {
    $bin = Join-Path $S.Root 'bin'
    if ($S.DryRun) { Say "  [dry-run] write $bin\planet.cmd"; return }
    New-Item -ItemType Directory -Force -Path $bin | Out-Null
    # `planet self ...` runs from a copy of this file in %TEMP%: uninstall deletes bin\ (and update rewrites this file) while
    # cmd is still reading the batch file, and cmd then fails with "The system cannot find the path specified" and exit 1.
    # The copy is started without `call`, so cmd hands over to it and never reads this file again.
    $cmd = @"
@echo off
rem procgen_world launcher (written by install.ps1). "planet self ..." manages the install.
setlocal
set "ROOT=$($S.Root)"
set "PLANET_CONFIG=$($S.Config)"
if /I not "%~1"=="self" goto run
if /I "%~dp0"=="%TEMP%\" goto self
copy /y "%~f0" "%TEMP%\procgen_world-self.cmd" >nul && "%TEMP%\procgen_world-self.cmd" %*
:self
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\bin\manage.ps1" -Root "%ROOT%" %*
goto :eof
:run
set /p VER=<"%ROOT%\app\current.txt"
set "APP=%ROOT%\app\%VER%"
if not exist "%APP%\.venv\Scripts\python.exe" ( echo procgen_world: no current version in %ROOT%\app 1>&2 & exit /b 1 )
if not defined PLANET_DATA for /f "usebackq tokens=1,* delims==" %%a in (``findstr /r /b /c:"data *=" "%PLANET_CONFIG%"``) do set "PLANET_DATA=%%b"
if defined PLANET_DATA set "PLANET_DATA=%PLANET_DATA:"=%"
if defined PLANET_DATA for /f "tokens=*" %%c in ("%PLANET_DATA%") do set "PLANET_DATA=%%c"
if defined PYTHONPATH ( set "PYTHONPATH=%APP%;%PYTHONPATH%" ) else ( set "PYTHONPATH=%APP%" )
rem UTF-8 for files and the console: Python 3.14 on Windows still defaults to the ANSI code page
set "PYTHONUTF8=1"
"%APP%\.venv\Scripts\python.exe" -m planet %*
"@
    Write-Text (Join-Path $bin 'planet.cmd') ($cmd -replace "`r?`n", "`r`n")
}

function Toml-Path([string]$p) { $p -replace '\\', '/' }  # (forward slashes: a TOML string with \U would not parse)

function Write-Config {
    if (Test-Path -LiteralPath $S.Config) {
        Say "    keeping $($S.Config)"
        $m = Select-String -LiteralPath $S.Config -Pattern '^data *= *["''](.*)["'']' | Select-Object -First 1
        if ($m) { $S.Data = $m.Matches[0].Groups[1].Value -replace '/', '\' }
        return
    }
    if ($S.DryRun) { Say "  [dry-run] write $($S.Config) (data = $($S.Data), port = $($S.Port))"; return }
    New-Item -ItemType Directory -Force -Path $S.ConfigDir | Out-Null
    $jobs = if ($S.Jobs) { "jobs = $($S.Jobs)" } else { '# jobs = 4' }
    Write-Text $S.Config (@(
        '# procgen_world settings (written by install.ps1; edit freely, update keeps this file)'
        "data = `"$(Toml-Path $S.Data)`""
        ''
        '[serve]'
        "port = $($S.Port)    # the first port tried; the next free one is used if it is taken"
        $jobs
        ''
        '# [presets]  machine-aware defaults: `planet self probe` (run by first-run) writes them here'
        ''
    ) -join "`n")
}

function Add-ToPath {
    $bin = Join-Path $S.Root 'bin'
    if (-not $S.ModifyPath) { Say "    not adding $bin to PATH (-NoModifyPath): run $bin\planet.cmd"; return }
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $parts = @(); if ($user) { $parts = $user -split ';' | Where-Object { $_ } }
    if ($parts -contains $bin) { return }
    Run-Or-Print "add $bin to the user PATH" {
        [Environment]::SetEnvironmentVariable('Path', (($parts + $bin) -join ';'), 'User')
        $env:Path = "$env:Path;$bin"
        $S.PathAdded = $bin
        Say "    added $bin to your user PATH (new terminals see it; this one does too)"
    }
}

function Remove-FromPath {
    if (-not $S.PathAdded) { return }
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not $user) { return }
    $rest = ($user -split ';' | Where-Object { $_ -and $_ -ne $S.PathAdded }) -join ';'
    Run-Or-Print "remove $($S.PathAdded) from the user PATH" { [Environment]::SetEnvironmentVariable('Path', $rest, 'User') }
}

function Write-Shortcut {
    if (-not $S.Desktop) { $S.Shortcut = ''; return }
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'Procgen World.lnk'
    if ($S.DryRun) { Say "  [dry-run] Start-menu shortcut $lnk"; return }
    $sh = New-Object -ComObject WScript.Shell
    $lnkObj = $sh.CreateShortcut($lnk)
    $lnkObj.TargetPath = Join-Path $S.Root 'bin\planet.cmd'
    $lnkObj.Arguments = 'self open'
    $lnkObj.WorkingDirectory = $env:USERPROFILE
    $lnkObj.Description = 'Simulated planets and their peoples, in a 3D viewer'
    $lnkObj.Save()
    $S.Shortcut = $lnk
}

# ---------------------------------------------------------------------------------------------- commands
function Cmd-Install {
    $target = Get-Target
    if (-not $S.Source) { $S.Source = Default-Source }
    if (-not $S.Data) { $S.Data = Join-Path $env:USERPROFILE 'procgen-world-data' }
    $S.Data = [System.IO.Path]::GetFullPath($S.Data)
    Resolve-Version
    Say 'procgen_world installer'
    Say "    version  $($S.Version)   (from $($S.Source))"
    Say "    install  $($S.Root)"
    Say "    data     $($S.Data)"
    Say "    config   $($S.Config)"
    if ($S.DryRun) { Say '    (dry run: nothing is changed)' }
    Check-Disk $S.Root
    if ([System.IO.Path]::GetPathRoot($S.Root) -ne [System.IO.Path]::GetPathRoot($S.Data)) { Check-Disk $S.Data }
    $t0 = Now
    Step "uv $UV_VERSION (private to this install)"
    Install-Uv $target
    Build-Version
    Step 'Launcher, config and Start-menu shortcut'
    Run-Or-Print "mkdir $($S.Root)\bin, $($S.Data)" {
        New-Item -ItemType Directory -Force -Path (Join-Path $S.Root 'bin'), $S.Data | Out-Null }
    Switch-To $S.Version
    Write-Config
    Write-Launcher
    Add-ToPath
    Write-Shortcut
    Save-State
    if ($S.DryRun) { Say 'Dry run done.'; return }
    $mb = [int]((Get-ChildItem -LiteralPath $S.Root -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB)
    Say "Installed $($S.Version) in $((Now) - $t0) s ($mb MB under $($S.Root))."
    if ($S.FirstRun) { Cmd-FirstRun }
    Say ''
    Say 'Start it with:  planet self open     (or Procgen World in the Start menu)'
    Say 'Manage it with: planet self update | rollback | uninstall | status'
}

function Need-Installed { if (-not (Test-Path -LiteralPath (Join-Path $S.Root 'bin\planet.cmd'))) { Die "not installed in $($S.Root)" } }

function Cmd-Probe {
    Need-Installed
    Step 'Sizing the app to this machine (cores, memory, disk, graphics)'
    if ($S.DryRun) { Say '  [dry-run] planet machine probe --write'; return }
    if (-not (Invoke-Planet @{} @('machine', 'probe', '--write'))) { Warn 'the machine probe failed: the presets are not written (nothing is gated)' }
    Say '    change any of it in the viewer''s Machine panel, or: planet machine set GATE allow|warn|off|auto'
}

function Cmd-FirstRun {
    Need-Installed
    Cmd-Probe
    Step 'First run: compiling the simulation (numba) on a tiny level-4 planet'
    Say '    this happens once per version; later runs start straight away'
    $warm = Join-Path $S.Root 'warmup'
    if (Test-Path -LiteralPath $warm) { Run-Or-Print "remove $warm" { Remove-Item -LiteralPath $warm -Recurse -Force } }
    $t = Now
    if ($S.DryRun) { Say "  [dry-run] PLANET_DATA=$warm planet make --seed 7 --level 4 --myr 20 --kyr 10 --zooms 1" }
    else {
        $ok = Invoke-Planet @{ PYTHONUNBUFFERED = '1'; PLANET_DATA = $warm } @('make', '--seed', '7', '--level', '4', '--myr', '20', '--kyr', '10', '--zooms', '1', '--name', 'warmup')
        if (-not $ok) { Die 'the warm-up run failed' }
        Remove-Item -LiteralPath $warm -Recurse -Force -ErrorAction SilentlyContinue
        Say "    compiled in $((Now) - $t) s"
    }
    if ($S.Starter -eq 'y' -or ($S.Starter -eq 'ask' -and (Ask 'Make a starter world now (level 6, seed 7, about 20 min)?' 'n'))) {
        Step 'Making the starter world (planet make --seed 7 --level 6)'
        $t = Now
        if ($S.DryRun) { Say '  [dry-run] planet make --seed 7 --level 6 --name starter' }
        elseif (Invoke-Planet @{} @('make', '--seed', '7', '--level', '6', '--name', 'starter')) { Say "    made in $((Now) - $t) s; open the viewer with: planet self open" }
    } else {
        Say '    no starter world now; make one any time with: planet make --seed 7 --level 6'
    }
}

function Cmd-Update {
    $target = Get-Target
    if (-not (Test-Path -LiteralPath $script:UV)) { Die "not installed in $($S.Root)" }
    $cur = Current-Version
    if (-not $S.Ref) { $S.Ref = Newest-Tag }
    if (-not $S.Ref) { Die "no release tag found in $($S.Source)" }
    Resolve-Version
    if ($S.Version -eq $cur) { Say "procgen_world $cur is up to date (source $($S.Source))."; return }
    Say "Updating procgen_world $cur -> $($S.Version) (your data in $($S.Data) is not touched)"
    $t = Now
    Install-Uv $target
    Build-Version
    Switch-To $S.Version
    Write-Launcher
    Say "Now on $($S.Version) ($((Now) - $t) s). Back to $cur with: planet self rollback"
    if ($S.FirstRun) { $S.Starter = 'n'; Cmd-FirstRun }  # (the numba cache is per version: warm the new one now)
    else { Say 'The numba cache is per version: run planet self first-run to compile it before first use.' }
}

function Cmd-Rollback {
    $cur = Current-Version; $prev = Previous-Version
    if (-not $prev -or -not (Test-Path -LiteralPath (Join-Path $S.Root "app\$prev"))) { Die 'no previous version to roll back to' }
    Run-Or-Print "swap current $cur and previous $prev" {
        Write-Text (Join-Path $S.Root 'app\previous.txt') $cur
        Write-Text (Join-Path $S.Root 'app\current.txt') $prev
        Copy-Item -LiteralPath (Join-Path $S.Root "app\$prev\install.ps1") -Destination (Join-Path $S.Root 'bin\manage.ps1') -Force
    }
    Say "Rolled back $cur -> $prev (planet self rollback again returns to $cur)."
}

function Size-Of([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) { return '?' }
    "$([int]((Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB)) MB"
}

function Cmd-Status {
    Say "install  $($S.Root) ($(Size-Of $S.Root))"
    Say "current  $(Current-Version)"
    Say "previous $(Previous-Version)"
    Say "source   $(if ($S.Source) { $S.Source } else { '?' })"
    $newest = '?'; if ($S.Source) { try { $newest = Newest-Tag } catch { } }
    Say "newest   $newest"
    Say "data     $(if ($S.Data) { $S.Data } else { '?' }) ($(if ($S.Data) { Size-Of $S.Data } else { '?' }))"
    Say "config   $($S.Config)"
}

# the presets' memory cap (mem_cap_gb) is applied on Linux only (systemd-run); on Windows the server runs uncapped and
# its RAM guards (GlobalMemoryStatusEx) and the machine gates still apply
function Cmd-Open {
    Need-Installed
    & (Join-Path $S.Root 'bin\planet.cmd') serve
}

function Cmd-Uninstall {
    if (-not (Test-Path -LiteralPath $S.Root)) { Die "nothing installed in $($S.Root)" }
    Say "This removes procgen_world from $($S.Root) ($(Size-Of $S.Root)): every version, its private uv"
    Say "and Python, the launcher, the PATH entry, the Start-menu shortcut and $($S.Config)."
    if (-not (Ask 'Uninstall?' 'y')) { Say 'Nothing removed.'; return }
    Remove-FromPath
    if ($S.Shortcut -and (Test-Path -LiteralPath $S.Shortcut)) { Run-Or-Print "remove $($S.Shortcut)" { Remove-Item -LiteralPath $S.Shortcut -Force } }
    if (Test-Path -LiteralPath $S.Config) { Run-Or-Print "remove $($S.Config)" { Remove-Item -LiteralPath $S.Config -Force } }
    Run-Or-Print "rmdir $($S.ConfigDir) (if empty)" {
        if ((Test-Path -LiteralPath $S.ConfigDir) -and -not (Get-ChildItem -LiteralPath $S.ConfigDir -Force)) { Remove-Item -LiteralPath $S.ConfigDir } }
    foreach ($d in 'app', 'uv', 'python', 'cache', 'bin', 'warmup') {
        $p = Join-Path $S.Root $d
        if (Test-Path -LiteralPath $p) { Run-Or-Print "remove $p" { Remove-Item -LiteralPath $p -Recurse -Force } }
    }
    Run-Or-Print "remove $($S.State)" { Remove-Item -LiteralPath $S.State -Force -ErrorAction SilentlyContinue }
    Run-Or-Print "rmdir $($S.Root) (if empty)" {
        if (-not (Get-ChildItem -LiteralPath $S.Root -Force)) { Remove-Item -LiteralPath $S.Root } }
    if ($S.Data -and (Test-Path -LiteralPath $S.Data -PathType Container)) {
        $size = Size-Of $S.Data
        if ($S.DeleteData -eq 'y' -or ($S.DeleteData -eq 'ask' -and (Ask "Also delete your data folder $($S.Data) ($size of runs and worlds)?" 'n'))) {
            if ((Get-Item -LiteralPath $S.Data -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                Die "$($S.Data) is a link; delete what it points to yourself" }
            Run-Or-Print "remove $($S.Data)" { Remove-Item -LiteralPath $S.Data -Recurse -Force }
            if (-not $S.DryRun) { Say "Deleted $($S.Data)." }
        } else { Say "Kept your data folder $($S.Data) ($size)." }
    }
    Say 'procgen_world is uninstalled.'
}

function Show-Help {
    if ($ScriptFile) { Get-Content -LiteralPath $ScriptFile | Where-Object { $_ -match '^#' } | Select-Object -First 31 | ForEach-Object { $_ -replace '^# ?', '' } }
    Say 'Commands: install (default), update, rollback, uninstall, status, first-run, probe, open'
}

# ---------------------------------------------------------------------------------------------- main
# (under `irm | iex` an `exit` would close the user's window: errors are reported and the script returns)
$failed = $false
try {
    Read-Options $args
    if ($S.Help) { Show-Help }
    else {
        Init-Paths
        switch ($S.Cmd) {
            'install' { Cmd-Install }
            'update' { Cmd-Update }
            'rollback' { Cmd-Rollback }
            'uninstall' { Cmd-Uninstall }
            'status' { Cmd-Status }
            'first-run' { $S.FirstRun = $true; Cmd-FirstRun }
            'probe' { Cmd-Probe }
            'open' { Cmd-Open }
        }
    }
} catch {
    Write-Host ($_.Exception.Message) -ForegroundColor Red
    $failed = $true
}
if ($failed -and $ScriptFile) { exit 1 }
