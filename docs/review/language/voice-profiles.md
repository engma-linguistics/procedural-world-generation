# Species voice profiles: a sourced draft (PW-1423)

Builder A, 2026-11-03. For Daniel. The numbers live in `planet/language/data/voice_profiles.toml`; the machinery in
`planet/language/percepts.py` (the percept space) and `planet/language/profiles.py` (costs, hearing, inheritance, nativization).
This is a draft to react to, not a gate.

## How to read a profile

Every sound is stored **as heard**, in one percept space for all species (place, manner, voicing, airstream, phonation,
secondary articulation, vowel height/backness/rounding, nasality, length, tone, plus two non-human axes: a second simultaneous
source, and a pitch register below or above human hearing). A profile says three things:

- **make_cost**: for each percept class (labial, sibilant, round vowel, purr, ...), a multiplier on what that sound costs a human.
  The human cost of a sound is `-ln(share of the world's languages that have it)` from PHOIBLE, clamped to 0.1..8. So `labial = 3`
  for aarakocra means "a /p/ is three times as dear for them as for us, though they hear it as a /p/". `inf` means impossible.
  Multipliers of all the classes a sound belongs to multiply (kʷʼ is velar x stop x labialized x ejective). A dearer-than-human
  sound is a substitute and costs effort however common it is among humans, so a combined multiplier m > 1 also adds
  `SUBSTITUTE x (m - 1)` (SUBSTITUTE = 1): cost = human cost x m + (m - 1). Without that term x3 on /m/'s near-floor cost
  (0.1 -> 0.3) changed almost nothing; with it, aarakocra `labial = 5` gives about 2 labial consonants per proto-inventory
  against about 5 for humans (200 draws each; `tests/test_language_profiles.py`).
- **hear**: per axis, how finely the species tells values apart (1 = as humans, 0.5 = half as finely, 0 = ignored). Two extra keys,
  `sub` and `ultra`, say whether a percept carried below ~20 Hz or above ~20 kHz reaches the ear at all; if not, the sound is lost
  when this species hears another's word.
- **register**: the habitual voice pitch against a human's, in rough octaves. Descriptive (for the brief and the workbench); it
  does not move percepts by itself.

Profiles inherit down the first-parent chain of the lineage tree, key by key, from the stem to the kind; a lineage's own `voice`
table in the spec overrides the data file. A lineage with nothing on its chain says "human default (not yet profiled)"; one judged
human on purpose says so in a note (`same_as_human = true`).

What a profile does downstream: inventories are drawn with probability falling with `species_cost` (so aarakocra protolanguages
rarely have labials, and when they do the labials are rare and fragile); sound changes whose output is dear are down-weighted
and those that remove a dear sound up-weighted; borrowing between species runs every sound through the listener's ear and
inventory (`hear_word`).

## Sources: what I actually opened tonight

Searched and confirmed (abstract or full record): Patterson & Pepperberg 1994 and 1998 (JASA); Beckers, Nelson & Suthers 2004
(Current Biology); Dooling, Leek, Gleich & Dent 2002 (JASA, temporal resolution in birds) and the summaries of Dooling's
psychophysics reviews; Christensen-Dalsgaard et al. 2012 (Proc R Soc B, turtle ear: ABR best at 300-500 Hz); Brittan-Powell et al.
2010 (JASA, ABR in geckos and anoles: best 1.6-2 kHz, similar to ~5 kHz); Christensen-Dalsgaard & Manley 2005 (lizard ear
directionality); Herbst et al. 2023 (Current Biology, cat larynges purr at 25-30 Hz without neural input); Weissengruber et al.
2002 (J Anat, hyoid and pharynx in lion, jaguar, tiger, cheetah and cat); the VoQS chart (Ball, Esling & Dickson; harsh voice
V!, ventricular V‼, diplophonia V̬‼).

From memory, not re-opened (marked `[memory]` in the TOML): Warren, Patterson & Pepperberg 1996 (Auk); Suthers 1990 (Nature,
two sides of the syrinx); Wever 1978 (The Reptile Ear); Ferrara et al. 2013 (turtle vocalizations); Shadle 1985 (teeth as the
sibilant obstacle); Heffner & Heffner 1985 (cat hearing 48 Hz-85 kHz) and 1980 (elephant hearing); Herbst et al. 2012 and Payne
et al. 1986 (elephant infrasound); Fitch 1997 (vocal-tract length and formants); Titze 1994; Peters 2002 (purring in mammals);
Møller & Pedersen 2004 (human hearing at infrasonic frequencies). I am confident these exist; their details as I use them are
textbook-level, but please treat them as unchecked.

## The human default

| | |
| --- | --- |
| make cost | PHOIBLE: `-ln(freq)` per segment, 0.1..8 (m, i, k, j, a at the floor; ʛ, ʘ near the ceiling); unattested 8 |
| harsh | x30: humans make epiglottalized and harsh voice, and a few languages contrast it (the !Xóõ epiglottalized vowels, Bai's harsh-voiced tones), so very dear, not impossible. Not 8: the inventory adds harsh variants at 0.25 x share / make_cost, and x8 put a growled sound in ~14% of human proto-inventories; x30 gives ~2% |
| impossible | purr phonation, percussives, a second simultaneous voice, sub-bass and ultra registers |
| hear | 1 on every axis; second voice 0.3 (heard as timbre, not as a contrast); `sub` 0, `ultra` 0 |

PHOIBLE is read from `planet/language/data/phoible_segments.tsv` (2175 languages, one inventory per Glottocode; the other agent's
table). 99% of its frequency mass parses into the percept space; what does not is diphthongs (stored as vowel sequences) and
PHOIBLE's unspecified archiphonemes (N). Several PHOIBLE symbols land on one percept (n̺ and n; k͈ and k: the fortis/lenis marks are
not an axis yet); the commonest wins. If the file were missing, a built-in snapshot of its top 120 is used.

## Avian line

**avian stem** (aarakocra, kenku)

| key | value | why |
| --- | --- | --- |
| articulators | syrinx, beak, tongue_tip, tongue_body, larynx, pharynx | no lips, teeth or velum. The larynx is there (at the top of the trachea) and opens and closes, so a glottal stop is possible, but it does not vibrate: the syrinx is the voice |
| voiced | 1.3 | voicing comes from the syrinx, so voiced vs voiceless is a contrast of syrinx timing: a little dear, not impossible |
| labial | 2.5 | heard as labial, made by beak closure or tongue against the beak (Patterson & Pepperberg 1998 compare a Grey parrot's stops with a human's; the parrot has no lips) |
| labiodental | 4.0 | needs lip and teeth: a substitute of a substitute |
| dental | 2.0 | no teeth: the tongue meets the beak tip |
| nasal, nasal_vowel | 3.5, 4.0 | no velum: the nose opens to the mouth through the choanal slit in the palate, which the tongue can block but nothing raises and lowers as a soft palate does |
| round_vowel | 1.5 | parrots get rounded-vowel resonances from tongue height, the oropharyngeal cavity and beak opening (Patterson & Pepperberg 1994; Beckers et al. 2004 show the tongue moves the formants) |
| sibilant | 1.3 | the beak edge is a poorer noise obstacle than incisors |
| trill | 0.7 | syringeal trills are everyday birdsong |
| tone | 0.7 | pitch is under fine syringeal control |
| source2 | 1.5 | two voices at once are natural (Suthers 1990) but a marked choice in speech: cheaper than impossible, dearer than plain |
| harsh | 3.0 | no ventricular folds; growl-like rasps exist but are not the norm |
| ejective, implosive, aspirated | 2.0, 2.0, 1.5 | these are laryngeal airstream and timing tricks; the syrinx sits low in the chest |
| hear | length 1.0, source2 1.5, tone 1.0, sub 0, ultra 0 | Dooling et al. 2002 show birds resolve the fine time structure *inside* a sound (within a pitch period) better than humans; that is not duration, and duration discrimination is about human, so length stays 1.0 (it was 1.5 in the first draft, citing that paper wrongly). Frequency discrimination is about human or worse (Dooling's reviews), so **not** "fine pitch hearing" |
| register | +1 | |

**aarakocra**: `labial = 5.0`, per your ruling: costly substitutes, as parrots do (with the substitute term, about 2 labials per
proto-inventory against a human's 5; at 3.0 it was about 3).
**kenku**: lower substitute costs (labial 1.6, dental 1.5, nasal 2.0, nasal vowel 2.5): they are the mimics. The canon's "kenku cannot invent
words" is a note, not a mechanism: their languages change by the ordinary rules.

## Reptilian line

**reptilian stem** (shared by the saurian peoples and the draconic line)

| key | value | why |
| --- | --- | --- |
| articulators | teeth, tongue_tip, tongue_body, larynx, pharynx | no mobile lips; no velum (the internal nostrils open into the roof of the mouth with nothing to raise and lower; crocodilians close the throat with a palatal valve, all or nothing) |
| labial, labiodental, round_vowel | 4.0, 5.0, 3.0 | lipless: a "labial" is a jaw-and-tongue imitation; rounding's lowered resonances come from tongue retraction and larynx lowering |
| nasal, nasal_vowel | 3.5, 4.0 | no velum to keep oral and nasal apart (1.8 in the first draft was too cheap for that) |
| fricative, sibilant, aspirated | 0.8, 0.7, 0.8 | the hiss is the reptile default |
| harsh | 2.0 | possible (crocodilian bellows) but not cheap |
| tone | 1.3 | judgement: modest laryngeal control |
| hear | sibilant 0.6, place 0.9, sub 0, ultra 0 | lizards hear best at 0.5-4 kHz, little above ~5 kHz (Brittan-Powell et al. 2010; Wever 1978): the 4-8 kHz band that tells s from ʃ is coarse |

**saurian**: inherits the stem unchanged.
**lizardfolk**: sibilant 0.6, harsh 1.5 (teeth and a big mouth).
**troglodyte**: inherits; I found no reason to differ.
**tortle**: articulators `-teeth +beak`; labial **2.0** (closing a beak shuts the front of the tract much as lips do, so a beak labial is
a nearer substitute than a lipless lizard's), round_vowel 2.0, dental 2.0, sibilant 1.5 (no teeth for the sibilant obstacle;
Shadle 1985). Hearing: sibilant 0.2, place 0.4, back 0.4, height 1.0, length 1.2. Turtle ears are best at 300-500 Hz with little
above ~1.2 kHz (Christensen-Dalsgaard et al. 2012): F1 (height, 300-800 Hz) sits in range; F2 is ~2 kHz for a front vowel and
~0.8 kHz for a back one, and consonant bursts and transitions are mostly above 1.5 kHz, so backness and place are heard only from
what leaks below the cut-off (0.4 each; the first draft's 0.6 and 0.5 were generous).
**kobold** (draconic line): register +1, otherwise the reptilian mouth and ear.
**dragonborn**: inherits the reptilian mouth. The canon has them speaking Common well; I read that as a learned accent with
substitutes, not as lips.
**chromatic and metallic dragons** (same table twice): register -2; sub_register 0.5 (cheap: like elephants, whose rumbles reach
~14-24 Hz by ordinary flow-induced fold vibration, Herbst et al. 2012), harsh 0.7, long 0.8, sibilant 0.6; hear sub 1.0, sibilant
0.5, place 0.8 (big animals hear lower and lose the top: elephants hear down to ~17 Hz, Heffner & Heffner 1980). Human listeners
have `sub = 0`, so the sub-bass part of a dragon word is lost to them (human hearing below ~20 Hz needs very high levels, Møller &
Pedersen 2004). Dragons are sapient; their languages are languages.

## Mammalian line

**feline stem**: purr 0.8 (the cat larynx purrs at ~25-30 Hz by itself, from pads of tissue in the folds: Herbst et al. 2023;
until tonight this was impossible for every profile), harsh 0.8, labial 1.5, labiodental 3.0, round_vowel 2.0, fricative 0.9;
hear sibilant 1.5, place 1.2, ultra 1.0 (cats hear to ~85 kHz: Heffner & Heffner 1985). **The lip call**: cats have lips, short
and little protruded over a long jaw; the tongue is long and mobile. So I made lip sounds mildly dear and rounding dearer, and left
tongue sounds at human cost. I found no measured source on cat lip mobility; this is anatomy by eye.
**tabaxi**: the stem as it stands.
**leonin**: purr 3.0, harsh 0.6, register -1. Roaring cats do not purr continuously the way small cats do (Peters 2002); note that
Weissengruber et al. 2002 showed the hyoid is not what decides it, so I give no anatomical reason, only the behaviour.
**goblinoid** (goblins, hobgoblins, bugbears): human profile; goblin register +1, bugbear -1 (body size).
**giantkin**: register -1, long 0.8; **true giants** register -2. Longer folds and tract lower the voice (Titze 1994; Fitch 1997),
still within human hearing. "Slow" became cheaper length, a weak judgement.
**orc**: labial 1.2, round_vowel 1.2 (the lower tusks).
**dwarf, human, halfling, elf, gnome, triton**: human profile, said so on purpose. Halflings and gnomes register +1 (small bodies).
Tritons: speech in air only; underwater speech is not modelled. Half-elves, half-orcs, tieflings, aasimar and genasi follow their
first parent (human). The `mammalian` and `hominid` stems themselves carry nothing and read "human default".

The antelope and cervid peoples are not in `dnd.toml` today; when they are, the obvious first profile is a ruminant mouth (mobile
lips, dental pad instead of upper incisors: dental and labiodental dear) and big mobile ears (place and sibilant heard finely).

## Symbols for non-human percepts

The IPA keeps the exact symbol; the house romanization (for names in the book) spells each in plain ASCII letters so a reader
can say it (`planet/language/data/romanization.tsv` header).

| percept | symbol | source | spelled |
| --- | --- | --- | --- |
| harsh / growl phonation | V‼ (e.g. a‼, ɣ‼) | VoQS: ventricular phonation (VoQS harsh voice V! is harshness *without* ventricular vibration; a growl is ventricular, so ‼) | rh after: arh, ghrh |
| purr phonation | ᵣ (U+1D63) after the segment | house, Phonetic Extensions block | rr after: arr, mrr |
| second simultaneous source | ᴖ (U+1D16) after the segment | house; VoQS diplophonia V̬‼ is glottal + ventricular, not two independent sources, so not reused | wh after: awh |
| sub-bass register | ˯ (U+02EF) | house, Spacing Modifier Letters (a UPA-style arrowhead) | mh after: amh |
| ultra register | ˰ (U+02F0) | house | ih after: iih, sih |
| lip smack, teeth clack | ʬ ʭ | extIPA percussives | pk, tk |
| beak or mandible clap | ʞ | house: the IPA letter for the velar click, withdrawn in 1970, reused for a knock heard as velar-region | ck |

## Open doubts

1. **Is a beak closure heard as labial?** I assumed yes for tortles (cheaper) and partly for birds. The 1998 parrot-stop paper is
   the place to check how Alex actually made /p/; I have only its title and venue confirmed tonight.
2. **Two voices as contrast.** I let `source2` carry contrast for birds (cost 1.5). Real birds use two voices in song, not (as far as
   anyone knows) to contrast words. A conservative alternative is a purely phonetic layer with no contrast.
3. **Harsh voice for humans** is now x30 rather than impossible (see the human default); purr stays impossible. The number is
   set by how often the inventory then draws a growled sound (~2% of human proto-inventories), not by a measurement of effort.
4. **Dragon hearing** is extrapolated from elephants and from the general "bigger animals hear lower" pattern; reptile ears
   (archosaur) are tuned low too, which agrees, but there is no animal of dragon size to compare.
5. **Cat lips** (above) and **giants' slowness** are judgement with no measured source.
6. **The place-distance geometry** (labial nearer velar than dental) drives how labials are heard by beaked listeners. It follows
   Jakobson's grave/acute, which is acoustically sound, but listeners in noise confuse labials with dentals too (f/θ).
7. **PHOIBLE fortis/lenis** (k͈, k͉, Korean-type) has no axis yet: those segments count as plain. Small (3% of languages).
