#!/bin/sh
# procgen_world installer and manager (Linux x86-64/arm64; macOS best effort; Windows through WSL2).
#
#   curl -LsSf <release>/install.sh | sh                 install the newest release tag
#   sh install.sh                                        install from this checkout or unpacked tarball
#   sh install.sh --source /path/to/repo --ref v1.0.0    install a tag (or branch) of a local git repo
#
# After install, the `planet` launcher manages it:
#   planet self open | first-run | probe | update | rollback | uninstall | status
#
# Layout (the install root, default ~/.local/share/procgen-world):
#   uv/uv               a pinned uv, private to this install
#   python/             the Python 3.14 uv fetched (private too)
#   cache/              uv's cache (the per-version venvs hardlink from it)
#   app/<version>/      the code of one version and its .venv; numba's cache sits beside the code
#   app/current, app/previous   symlinks: the version in use and the one `rollback` returns to
#   bin/planet          the launcher (symlinked into --bin-dir, default ~/.local/bin)
#   bin/manage.sh       this script, as shipped by the current version
#   install.env         what the installer did (source, links, config), for update and uninstall
# The config is ~/.config/procgen-world/config.toml; the data folder (default ~/procgen-world-data) is
# never touched by update or rollback, and uninstall asks before deleting it.
set -eu

UV_VERSION=0.12.7
DEFAULT_SOURCE=https://github.com/engma-linguistics/procedural-world-generation
APP=procgen-world

# uv release checksums (https://github.com/astral-sh/uv/releases/tag/$UV_VERSION)
uv_sha256() {
    case "$1" in
        x86_64-unknown-linux-gnu) echo 788f18abea7c5f55d6216e4f5613fd89d4d59b631efeec117b2b07fe72f1da21 ;;
        aarch64-unknown-linux-gnu) echo 66393193038dd7eb108abd7a218d9cec04ac70ab98242b0720fa94de19223b7c ;;
        aarch64-apple-darwin) echo 127ebdda7ad953cdf198e964b570ea5771b85467ea93eb7cb6d6f8e6f55408f3 ;;
        x86_64-apple-darwin) echo 06b8ae1da8c2661c5434507a66f8c2b0b835933bf955b5958a9ac357a37d1959 ;;
        *) return 1 ;;
    esac
}

# ---------------------------------------------------------------------------------------------- helpers
say() { printf '%s\n' "$*"; }
step() { printf '==> %s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

# run a command, or with --dry-run only print it
run() {
    if [ "$DRY_RUN" = 1 ]; then
        printf '  [dry-run]'; printf ' %s' "$@"; printf '\n'
    else
        "$@"
    fi
}

# ask "question" default(y|n): reads the terminal even under `curl | sh`; no terminal or --yes -> the default
ask() {
    _q=$1 _d=$2
    if [ "$ASSUME_YES" = 1 ]; then [ "$_d" = y ]; return; fi
    if [ "$_d" = y ]; then _p='[Y/n]'; else _p='[y/N]'; fi
    if ! { : </dev/tty; } 2>/dev/null; then [ "$_d" = y ]; return; fi
    printf '%s %s ' "$_q" "$_p" >/dev/tty
    read -r _a </dev/tty || _a=
    case "$_a" in
        [Yy]*) return 0 ;;
        [Nn]*) return 1 ;;
        *) [ "$_d" = y ] ;;
    esac
}

now() { date +%s; }

# free GB on the filesystem holding $1 (or its nearest existing parent)
free_gb() {
    _p=$1
    while [ ! -e "$_p" ]; do _p=$(dirname "$_p"); done
    df -Pk "$_p" | awk 'NR==2 { printf "%d", $4 / 1048576 }'
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
    else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

fetch_url() {  # url dest
    if command -v curl >/dev/null 2>&1; then curl -fsSL --retry 3 -o "$2" "$1"
    elif command -v wget >/dev/null 2>&1; then wget -q -O "$2" "$1"
    else die "neither curl nor wget is installed"; fi
}

is_git_url() { case "$1" in http://* | https://* | git@* | ssh://* | git://*) return 0 ;; *) return 1 ;; esac; }
is_git_repo() { [ -d "$1" ] && git -C "$1" rev-parse --git-dir >/dev/null 2>&1; }

# ---------------------------------------------------------------------------------------------- options
CMD=install
ROOT=${PROCGEN_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/$APP}
CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/$APP
DATA=${PLANET_DATA:-}
SOURCE=${PROCGEN_SOURCE:-}
REF=
BIN_DIR=${PROCGEN_BIN_DIR:-$HOME/.local/bin}
APPS_DIR=${XDG_DATA_HOME:-$HOME/.local/share}/applications
PORT=8765
JOBS=
UV_BIN=
DRY_RUN=0
ASSUME_YES=0
DESKTOP=1
FIRST_RUN=1
STARTER=ask
DELETE_DATA=ask

usage() {
    sed -n '2,/^set -eu/p' "$0" 2>/dev/null | sed '$d; s/^# \{0,1\}//' || true
    cat <<EOF

Commands: install (default), update, rollback, uninstall, status, first-run, probe, open
Options:
  --root DIR        install root (default \$XDG_DATA_HOME/$APP, now $ROOT)
  --data DIR        data folder, PLANET_DATA (default ~/procgen-world-data)
  --source SRC      a git URL, a local git repo or a plain source folder (default: this checkout, else $DEFAULT_SOURCE)
  --ref REF         a tag or branch of a git source (default: the newest v* tag, else HEAD)
  --bin-dir DIR     where the \`planet\` link goes (default ~/.local/bin; it is never added to your shell profile)
  --port N          the viewer's first port to try (default 8765)
  --jobs N          jobs the server runs at once (default: planet's)
  --uv PATH         use this uv binary instead of downloading uv $UV_VERSION
  --no-desktop      no app-menu entry
  --no-first-run    skip the numba warm-up and the starter world
  --starter / --no-starter    make (or not) the L6 starter world without asking
  --delete-data / --keep-data uninstall: delete (or keep) the data folder without asking
  --yes             take the default answer to every question
  --dry-run         print what would be done, change nothing
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        install | update | rollback | uninstall | status | first-run | probe | open) CMD=$1 ;;
        --root) ROOT=$2; shift ;;
        --data) DATA=$2; shift ;;
        --source) SOURCE=$2; shift ;;
        --ref) REF=$2; shift ;;
        --bin-dir) BIN_DIR=$2; shift ;;
        --port) PORT=$2; shift ;;
        --jobs) JOBS=$2; shift ;;
        --uv) UV_BIN=$2; shift ;;
        --no-desktop) DESKTOP=0 ;;
        --no-first-run) FIRST_RUN=0 ;;
        --starter) STARTER=y ;;
        --no-starter) STARTER=n ;;
        --delete-data) DELETE_DATA=y ;;
        --keep-data) DELETE_DATA=n ;;
        --yes | -y) ASSUME_YES=1 ;;
        --dry-run) DRY_RUN=1 ;;
        -h | --help) usage; exit 0 ;;
        *) die "unknown argument: $1 (see --help)" ;;
    esac
    shift
done

case "$ROOT" in /*) ;; *) ROOT=$(pwd)/$ROOT ;; esac
CONFIG=$CONFIG_DIR/config.toml
STATE=$ROOT/install.env
UV=$ROOT/uv/uv
DESKTOP_FILE=$APPS_DIR/$APP.desktop

# what an earlier install recorded (source, data, links) fills what this call did not give
if [ -f "$STATE" ]; then
    # shellcheck disable=SC1090
    . "$STATE"
    [ -n "$SOURCE" ] || SOURCE=${S_SOURCE:-}
    [ -n "$DATA" ] || DATA=${S_DATA:-}
    CONFIG=${S_CONFIG:-$CONFIG}
fi

uv_env() {  # the environment every uv call runs in: private Python, private cache, no user config
    env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT UV_PYTHON_INSTALL_DIR="$ROOT/python" UV_CACHE_DIR="$ROOT/cache" \
        UV_PYTHON_PREFERENCE=only-managed UV_NO_CONFIG=1 UV_NO_PROGRESS=1 "$@"
}

# ---------------------------------------------------------------------------------------------- platform
platform() {
    _os=$(uname -s) _arch=$(uname -m)
    case "$_arch" in x86_64 | amd64) _arch=x86_64 ;; arm64 | aarch64) _arch=aarch64 ;; *) die "unsupported CPU: $_arch" ;; esac
    case "$_os" in
        Linux) TARGET=$_arch-unknown-linux-gnu OS=linux ;;
        Darwin) TARGET=$_arch-apple-darwin OS=mac ;;
        *) die "unsupported OS: $_os (on Windows, use WSL2)" ;;
    esac
}

check_disk() {
    _f=$(free_gb "$1")
    if [ "$_f" -lt 20 ]; then
        die "only $_f GB free under $1; procgen_world needs at least 20 GB (an L7 world family is ~3 GB, plus the tile cache)"
    elif [ "$_f" -lt 50 ]; then
        warn "only $_f GB free under $1; 50 GB or more is recommended"
    fi
}

# ---------------------------------------------------------------------------------------------- uv
install_uv() {
    if [ -x "$UV" ] && "$UV" --version 2>/dev/null | grep -q " $UV_VERSION"; then
        say "    uv $UV_VERSION already in $ROOT/uv"
        return
    fi
    run mkdir -p "$ROOT/uv"
    if [ -n "$UV_BIN" ]; then
        "$UV_BIN" --version | grep -q " $UV_VERSION" || warn "$UV_BIN is not uv $UV_VERSION ($("$UV_BIN" --version))"
        run cp "$UV_BIN" "$UV"
        return
    fi
    _sum=$(uv_sha256 "$TARGET") || die "no pinned uv for $TARGET"
    _url=https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$TARGET.tar.gz
    say "    downloading uv $UV_VERSION ($TARGET)"
    [ "$DRY_RUN" = 1 ] && { say "  [dry-run] fetch $_url, check sha256 $_sum"; return; }
    _tmp=$(mktemp -d)
    fetch_url "$_url" "$_tmp/uv.tar.gz"
    [ "$(sha256_of "$_tmp/uv.tar.gz")" = "$_sum" ] || { rm -rf "${_tmp:?}"; die "uv download failed its checksum"; }
    tar -xzf "$_tmp/uv.tar.gz" -C "$_tmp"
    cp "$_tmp/uv-$TARGET/uv" "$UV"
    chmod +x "$UV"
    rm -rf "${_tmp:?}"
}

# ---------------------------------------------------------------------------------------------- source
# the default source: the checkout or tarball this script sits in, else the release repo
default_source() {
    _here=$(cd "$(dirname "$0")" 2>/dev/null && pwd -P) || _here=
    if [ -n "$_here" ] && [ -f "$_here/pyproject.toml" ] && [ -d "$_here/planet" ] && [ "$_here" != "$ROOT/bin" ]; then
        echo "$_here"
    else
        echo "$DEFAULT_SOURCE"
    fi
}

# the newest release tag of the source (v1.2.3; sort -V), empty if none
newest_tag() {
    if is_git_url "$SOURCE"; then
        git ls-remote --tags --refs "$SOURCE" 'v[0-9]*' | sed 's#.*refs/tags/##' | sort -V | tail -n 1
    elif is_git_repo "$SOURCE"; then
        git -C "$SOURCE" tag -l 'v[0-9]*' | sort -V | tail -n 1
    fi
}

# resolve REF and VERSION (the app folder's name) for the source
resolve_version() {
    if is_git_url "$SOURCE" || is_git_repo "$SOURCE"; then
        command -v git >/dev/null 2>&1 || die "git is needed to install from $SOURCE"
        [ -n "$REF" ] || REF=$(newest_tag)
        if [ -z "$REF" ]; then
            is_git_repo "$SOURCE" || die "no release tag in $SOURCE; pass --ref"
            REF=HEAD
        fi
        if is_git_repo "$SOURCE"; then
            git -C "$SOURCE" rev-parse --verify -q "$REF^{commit}" >/dev/null || die "no $REF in $SOURCE"
            if git -C "$SOURCE" rev-parse --verify -q "refs/tags/$REF" >/dev/null; then
                VERSION=$REF
            else  # a branch or commit: name it with its commit
                VERSION=$(printf '%s' "$REF" | tr '/' '-')-$(git -C "$SOURCE" rev-parse --short "$REF^{commit}")
            fi
        else
            VERSION=$(printf '%s' "$REF" | tr '/' '-')
        fi
    else
        [ -f "$SOURCE/pyproject.toml" ] || die "$SOURCE is not a procgen_world source folder"
        VERSION=$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$SOURCE/pyproject.toml" | head -n 1)-local
    fi
}

fetch_code() {  # into $1
    if is_git_url "$SOURCE"; then
        run git clone -q --depth 1 --branch "$REF" "$SOURCE" "$1"
        run rm -rf "${1:?}/.git"
    elif is_git_repo "$SOURCE"; then
        run mkdir -p "$1"
        if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] git -C $SOURCE archive $REF | tar -x -C $1"
        else git -C "$SOURCE" archive --format=tar "$REF" | tar -xf - -C "$1"; fi
    else
        run mkdir -p "$1"
        if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] copy $SOURCE to $1"
        else (cd "$SOURCE" && tar -cf - --exclude=./.venv --exclude=./.git --exclude=./runs --exclude=./worlds \
            --exclude=./zooms --exclude=./grids --exclude=./data --exclude=./.tiles .) | tar -xf - -C "$1"; fi
    fi
}

# fetch, sync and smoke-check one version into app/$VERSION (kept if already there and working)
build_version() {
    _dir=$ROOT/app/$VERSION
    if [ -x "$_dir/.venv/bin/python" ] && smoke "$_dir" 2>/dev/null; then
        say "    $VERSION is already installed"
        return
    fi
    _part=$ROOT/app/.$VERSION.partial
    if [ -e "$_part" ]; then run rm -rf "${_part:?}"; fi
    step "Fetching $VERSION from $SOURCE"
    fetch_code "$_part"
    if [ -e "$_dir" ]; then run rm -rf "${_dir:?}"; fi
    run mv "$_part" "$_dir"
    step "Installing Python 3.14 and the dependencies (uv sync --frozen --no-dev)"
    _t=$(now)
    if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] (cd $_dir && uv sync --frozen --no-dev)"; return; fi
    # the version only becomes current after it syncs and starts (switch_to); a failure leaves current alone
    if ! (cd "$_dir" && uv_env "$UV" sync --frozen --no-dev --quiet) || ! smoke "$_dir"; then
        rm -rf "${_dir:?}"
        die "$VERSION did not install or does not start; the current version is unchanged"
    fi
    say "    done in $(($(now) - _t)) s"
}

smoke() {  # the app at $1 imports and its CLI answers
    PYTHONPATH=$1 "$1/.venv/bin/python" -c "import numba, numpy, planet.server, planet.make" &&
        PYTHONPATH=$1 "$1/.venv/bin/python" -m planet --help >/dev/null
}

current_version() { [ -L "$ROOT/app/current" ] && basename "$(readlink "$ROOT/app/current")" || true; }
previous_version() { [ -L "$ROOT/app/previous" ] && basename "$(readlink "$ROOT/app/previous")" || true; }

# point current at $1, previous at what current was; drop versions that are neither
switch_to() {
    _old=$(current_version)
    if [ -n "$_old" ] && [ "$_old" != "$1" ]; then run ln -sfn "$_old" "$ROOT/app/previous"; fi
    run ln -sfn "$1" "$ROOT/app/current"
    run cp "$ROOT/app/$1/install.sh" "$ROOT/bin/manage.sh"
    _keep_prev=$(previous_version)
    for _d in "$ROOT"/app/*/; do
        [ -d "$_d" ] || continue  # (no match: the pattern itself)
        _v=$(basename "$_d")
        case "$_v" in current | previous | "$1" | "$_keep_prev") ;;
            *) [ -L "${_d%/}" ] || { say "    removing old version $_v"; run rm -rf "${ROOT:?}/app/${_v:?}"; } ;;
        esac
    done
}

# ---------------------------------------------------------------------------------------------- launcher, config, menu
write_launcher() {
    run mkdir -p "$ROOT/bin"
    [ "$DRY_RUN" = 1 ] && { say "  [dry-run] write $ROOT/bin/planet"; return; }
    cat >"$ROOT/bin/planet" <<EOF
#!/bin/sh
# procgen_world launcher (written by install.sh). \`planet self ...\` manages the install.
ROOT='$ROOT'
CONFIG='$CONFIG'
if [ "\${1:-}" = self ]; then shift; exec sh "\$ROOT/bin/manage.sh" --root "\$ROOT" "\$@"; fi
APP=\$(cd "\$ROOT/app/current" && pwd -P) || { echo "procgen_world: no current version in \$ROOT/app" >&2; exit 1; }
if [ -z "\${PLANET_DATA:-}" ]; then
    PLANET_DATA=\$(sed -n 's/^data *= *"\\(.*\\)"/\\1/p' "\$CONFIG" 2>/dev/null | head -n 1)
fi
export PLANET_DATA PLANET_CONFIG="\$CONFIG" PYTHONPATH="\$APP\${PYTHONPATH:+:\$PYTHONPATH}"
exec "\$APP/.venv/bin/python" -m planet "\$@"
EOF
    chmod +x "$ROOT/bin/planet"
}

write_config() {
    if [ -f "$CONFIG" ]; then
        say "    keeping $CONFIG"
        DATA=$(sed -n 's/^data *= *"\(.*\)"/\1/p' "$CONFIG" | head -n 1)
        return
    fi
    run mkdir -p "$CONFIG_DIR"
    [ "$DRY_RUN" = 1 ] && { say "  [dry-run] write $CONFIG (data = $DATA, port = $PORT)"; return; }
    {
        echo "# procgen_world settings (written by install.sh; edit freely, update keeps this file)"
        echo "data = \"$DATA\""
        echo
        echo "[serve]"
        echo "port = $PORT    # the first port tried; the next free one is used if it is taken"
        if [ -n "$JOBS" ]; then echo "jobs = $JOBS"; else echo "# jobs = 4"; fi
        echo
        echo "# [presets]  machine-aware defaults: \`planet self probe\` (run by first-run) writes them here"
    } >"$CONFIG"
}

link_bin() {
    _link=$BIN_DIR/planet
    if [ -e "$_link" ] && ! [ "$(readlink "$_link" 2>/dev/null)" = "$ROOT/bin/planet" ]; then
        warn "$_link exists and is not this install's; not replacing it. Run $ROOT/bin/planet, or link it yourself."
        BIN_LINK=
        return
    fi
    run mkdir -p "$BIN_DIR"
    run ln -sfn "$ROOT/bin/planet" "$_link"
    BIN_LINK=$_link
    case ":$PATH:" in
        *":$BIN_DIR:"*) ;;
        *) say "    note: $BIN_DIR is not on your PATH. Add it (e.g. in ~/.profile: export PATH=\"$BIN_DIR:\$PATH\")," \
            "or run $ROOT/bin/planet." ;;
    esac
}

write_desktop() {
    [ "$DESKTOP" = 1 ] || { DESKTOP_FILE=; return; }
    if [ "$OS" = mac ]; then  # best effort: a double-clickable .command in ~/Applications
        DESKTOP_FILE="$HOME/Applications/Procgen World.command"
        run mkdir -p "$HOME/Applications"
        [ "$DRY_RUN" = 1 ] && return
        printf '#!/bin/sh\nexec "%s" self open\n' "$ROOT/bin/planet" >"$DESKTOP_FILE"
        chmod +x "$DESKTOP_FILE"
        return
    fi
    run mkdir -p "$APPS_DIR"
    [ "$DRY_RUN" = 1 ] && { say "  [dry-run] write $DESKTOP_FILE"; return; }
    cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Procgen World
Comment=Simulated planets and their peoples, in a 3D viewer
Exec=$ROOT/bin/planet self open
Terminal=true
Categories=Education;Science;Graphics;
EOF
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" 2>/dev/null || true
}

save_state() {
    [ "$DRY_RUN" = 1 ] && return
    {
        echo "S_SOURCE='$SOURCE'"
        echo "S_DATA='$DATA'"
        echo "S_CONFIG='$CONFIG'"
        echo "S_BIN_LINK='${BIN_LINK:-}'"
        echo "S_DESKTOP_FILE='${DESKTOP_FILE:-}'"
    } >"$STATE"
}

# ---------------------------------------------------------------------------------------------- commands
cmd_install() {
    platform
    [ -n "$SOURCE" ] || SOURCE=$(default_source)
    [ -n "$DATA" ] || DATA=$HOME/procgen-world-data
    case "$DATA" in /*) ;; *) DATA=$(pwd)/$DATA ;; esac
    resolve_version
    say "procgen_world installer"
    say "    version  $VERSION   (from $SOURCE)"
    say "    install  $ROOT"
    say "    data     $DATA"
    say "    config   $CONFIG"
    [ "$DRY_RUN" = 1 ] && say "    (dry run: nothing is changed)"
    check_disk "$ROOT"
    [ "$(free_gb "$ROOT")" = "$(free_gb "$DATA")" ] || check_disk "$DATA"
    _t0=$(now)
    step "uv $UV_VERSION (private to this install)"
    install_uv
    build_version
    step "Launcher, config and app-menu entry"
    run mkdir -p "$ROOT/bin" "$DATA"
    switch_to "$VERSION"
    write_config
    write_launcher
    link_bin
    write_desktop
    save_state
    [ "$DRY_RUN" = 1 ] && { say "Dry run done."; return; }
    say "Installed $VERSION in $(($(now) - _t0)) s ($(du -sh "$ROOT" 2>/dev/null | cut -f1) under $ROOT)."
    if [ "$FIRST_RUN" = 1 ]; then cmd_first_run; fi
    say ""
    say "Start it with:  planet self open     (or Procgen World in the app menu)"
    say "Manage it with: planet self update | rollback | uninstall | status"
}

cmd_probe() {
    _planet=$ROOT/bin/planet
    [ -x "$_planet" ] || die "not installed in $ROOT"
    step "Sizing the app to this machine (cores, memory, disk, graphics)"
    if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] planet machine probe --write"; return; fi
    "$_planet" machine probe --write 2>&1 | sed 's/^/    /' || warn "the machine probe failed: the presets are not written (nothing is gated)"
    say "    change any of it in the viewer's Machine panel, or: planet machine set GATE allow|warn|off|auto"
}

cmd_first_run() {
    _planet=$ROOT/bin/planet
    [ -x "$_planet" ] || die "not installed in $ROOT"
    cmd_probe
    step "First run: compiling the simulation (numba) on a tiny level-4 planet"
    say "    this happens once per version; later runs start straight away"
    _warm=$ROOT/warmup
    if [ -e "$_warm" ]; then run rm -rf "${_warm:?}"; fi
    _t=$(now)
    if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] PLANET_DATA=$_warm planet make --seed 7 --level 4 --myr 20 --kyr 10 --zooms 1"
    else
        PYTHONUNBUFFERED=1 PLANET_DATA=$_warm "$_planet" make --seed 7 --level 4 --myr 20 --kyr 10 --zooms 1 --name warmup 2>&1 |
            sed 's/^/    | /' || die "the warm-up run failed"
        rm -rf "${_warm:?}"
        say "    compiled in $(($(now) - _t)) s"
    fi
    if [ "$STARTER" = y ] || { [ "$STARTER" = ask ] && ask "Make a starter world now (level 6, seed 7, about 20 min)?" n; }; then
        step "Making the starter world (planet make --seed 7 --level 6)"
        _t=$(now)
        run "$_planet" make --seed 7 --level 6 --name starter
        say "    made in $(($(now) - _t)) s; open the viewer with: planet self open"
    else
        say "    no starter world now; make one any time with: planet make --seed 7 --level 6"
    fi
}

cmd_update() {
    platform
    [ -x "$UV" ] || die "not installed in $ROOT"
    _cur=$(current_version)
    REF=${REF:-$(newest_tag)}
    [ -n "$REF" ] || die "no release tag found in $SOURCE"
    resolve_version
    if [ "$VERSION" = "$_cur" ]; then say "procgen_world $_cur is up to date (source $SOURCE)."; return; fi
    say "Updating procgen_world $_cur -> $VERSION (your data in $DATA is not touched)"
    _t=$(now)
    install_uv
    build_version
    switch_to "$VERSION"
    write_launcher
    say "Now on $VERSION ($(($(now) - _t)) s). Back to $_cur with: planet self rollback"
    if [ "$FIRST_RUN" = 1 ]; then
        STARTER=n
        cmd_first_run  # the numba cache is per version: warm the new one now
    else
        say "The numba cache is per version: run planet self first-run to compile it before first use."
    fi
}

cmd_rollback() {
    _cur=$(current_version) _prev=$(previous_version)
    [ -n "$_prev" ] && [ -d "$ROOT/app/$_prev" ] || die "no previous version to roll back to"
    run ln -sfn "$_cur" "$ROOT/app/previous"
    run ln -sfn "$_prev" "$ROOT/app/current"
    run cp "$ROOT/app/$_prev/install.sh" "$ROOT/bin/manage.sh"
    say "Rolled back $_cur -> $_prev (planet self rollback again returns to $_cur)."
}

cmd_status() {
    say "install  $ROOT ($(du -sh "$ROOT" 2>/dev/null | cut -f1))"
    say "current  $(current_version)"
    say "previous $(previous_version)"
    say "source   ${SOURCE:-?}"
    say "newest   $( [ -n "$SOURCE" ] && newest_tag 2>/dev/null || echo ?)"
    say "data     ${DATA:-?} ($(du -sh "$DATA" 2>/dev/null | cut -f1))"
    say "config   $CONFIG"
}

# the presets' memory cap (planet machine probe) for the server and its jobs: a systemd user scope on Linux, if one can be
# made; otherwise the server runs uncapped (its RAM guards and the gates still apply)
mem_cap() { sed -n 's/^mem_cap_gb *= *\([0-9][0-9]*\).*/\1/p' "$CONFIG" 2>/dev/null | head -n 1; }

cmd_open() {
    _cap=$(mem_cap)
    if [ -n "$_cap" ] && [ "${PLANET_NO_CAP:-}" != 1 ] && command -v systemd-run >/dev/null 2>&1 &&
        systemd-run --user --scope --quiet -p MemoryMax=1G true >/dev/null 2>&1; then
        say "(capped at ${_cap} GB of memory, the machine presets' mem_cap_gb; PLANET_NO_CAP=1 to run without)"
        exec systemd-run --user --scope --quiet -p MemoryMax="${_cap}G" -p MemorySwapMax=0 "$ROOT/bin/planet" serve
    fi
    exec "$ROOT/bin/planet" serve
}

cmd_uninstall() {
    [ -d "$ROOT" ] || die "nothing installed in $ROOT"
    say "This removes procgen_world from $ROOT ($(du -sh "$ROOT" 2>/dev/null | cut -f1)): every version, its private uv"
    say "and Python, the launcher${S_BIN_LINK:+ ($S_BIN_LINK)}, the app-menu entry and $CONFIG."
    ask "Uninstall?" y || { say "Nothing removed."; return; }
    if [ -n "${S_BIN_LINK:-}" ] && [ "$(readlink "$S_BIN_LINK" 2>/dev/null)" = "$ROOT/bin/planet" ]; then
        run rm -f "$S_BIN_LINK"
    fi
    if [ -n "${S_DESKTOP_FILE:-}" ] && [ -f "$S_DESKTOP_FILE" ]; then
        run rm -f "$S_DESKTOP_FILE"
        if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(dirname "$S_DESKTOP_FILE")" 2>/dev/null || true; fi
    fi
    if [ -f "$CONFIG" ]; then run rm -f "$CONFIG"; fi
    run rmdir "$(dirname "$CONFIG")" 2>/dev/null || true
    for _d in app uv python cache bin warmup; do
        if [ -e "$ROOT/$_d" ]; then run rm -rf "${ROOT:?}/${_d:?}"; fi
    done
    run rm -f "$STATE"
    run rmdir "$ROOT" 2>/dev/null || true
    if [ -n "$DATA" ] && [ -d "$DATA" ]; then
        _size=$(du -sh "$DATA" 2>/dev/null | cut -f1)
        if [ "$DELETE_DATA" = y ] || { [ "$DELETE_DATA" = ask ] && ask "Also delete your data folder $DATA ($_size of runs and worlds)?" n; }; then
            [ -L "$DATA" ] && die "$DATA is a symlink; delete what it points to yourself"
            run rm -rf "${DATA:?}"
            say "Deleted $DATA."
        else
            say "Kept your data folder $DATA ($_size)."
        fi
    fi
    say "procgen_world is uninstalled."
}

case "$CMD" in
    install) cmd_install ;;
    update) cmd_update ;;
    rollback) cmd_rollback ;;
    uninstall) cmd_uninstall ;;
    status) cmd_status ;;
    first-run) FIRST_RUN=1; cmd_first_run ;;
    probe) cmd_probe ;;
    open) cmd_open ;;
esac
