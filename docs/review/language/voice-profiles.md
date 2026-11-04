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
  Multipliers of all the classes a sound belongs to multiply (kʷʼ is velar x stop x labialized x ejective).
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
| impossible | harsh/growl and purr phonation, percussives, a second simultaneous voice, sub-bass and ultra registers |
| hear | 1 on every axis; second voice 0.3 (heard as timbre, not as a contrast); `sub` 0, `ultra` 0 |

PHOIBLE is read from `planet/language/data/phoible_segments.tsv` (2175 languages, one inventory per Glottocode; the other agent's
table). 99% of its frequency mass parses into the percept space; what does not is diphthongs (stored as vowel sequences) and
PHOIBLE's unspecified archiphonemes (N). Several PHOIBLE symbols land on one percept (n̺ and n; k͈ and k: the fortis/lenis marks are
not an axis yet); the commonest wins. If the file were missing, a built-in snapshot of its top 120 is used.

## Avian line

**avian stem** (aarakocra, kenku)

| key | value | why |
| --- | --- | --- |
| articulators | syrinx, beak, tongue_tip, tongue_body, pharynx | no lips, teeth, velum or phonating larynx |
| labial | 2.5 | heard as labial, made by beak closure or tongue against the beak (Patterson & Pepperberg 1998 compare a Grey parrot's stops with a human's; the parrot has no lips) |
| labiodental | 4.0 | needs lip and teeth: a substitute of a substitute |
| dental | 2.0 | no teeth: the tongue meets the beak tip |
| nasal, nasal_vowel | 2.0, 3.0 | no velum to shut the nose off cleanly |
| round_vowel | 1.5 | parrots get rounded-vowel resonances from tongue height, the oropharyngeal cavity and beak opening (Patterson & Pepperberg 1994; Beckers et al. 2004 show the tongue moves the formants) |
| sibilant | 1.3 | the beak edge is a poorer noise obstacle than incisors |
| trill | 0.7 | syringeal trills are everyday birdsong |
| tone | 0.7 | pitch is under fine syringeal control |
| source2 | 1.5 | two voices at once are natural (Suthers 1990) but a marked choice in speech: cheaper than impossible, dearer than plain |
| harsh | 3.0 | no ventricular folds; growl-like rasps exist but are not the norm |
| ejective, implosive, aspirated | 2.0, 2.0, 1.5 | these are laryngeal airstream and timing tricks; the syrinx sits low in the chest |
| hear | length 1.5, source2 1.5, tone 1.0, sub 0, ultra 0 | birds resolve fine time structure better than humans (Dooling et al. 2002); frequency discrimination is about human or worse (Dooling's reviews), so **not** "fine pitch hearing" |
| register | +1 | |

**aarakocra**: `labial = 3.0`, per your ruling: costly substitutes, as parrots do.
**kenku**: lower substitute costs (labial 1.6, dental 1.5, nasal 1.5): they are the mimics. The canon's "kenku cannot invent
words" is a note, not a mechanism: their languages change by the ordinary rules.

## Reptilian line

**reptilian stem** (shared by the saurian peoples and the draconic line)

| key | value | why |
| --- | --- | --- |
| articulators | teeth, tongue_tip, tongue_body, larynx, pharynx | no mobile lips; no mammal-type soft palate |
| labial, labiodental, round_vowel | 4.0, 5.0, 3.0 | lipless: a "labial" is a jaw-and-tongue imitation; rounding's lowered resonances come from tongue retraction and larynx lowering |
| nasal, nasal_vowel | 1.8, 3.0 | no velum to keep oral and nasal apart |
| fricative, sibilant, aspirated | 0.8, 0.7, 0.8 | the hiss is the reptile default |
| harsh | 2.0 | possible (crocodilian bellows) but not cheap |
| tone | 1.3 | judgement: modest laryngeal control |
| hear | sibilant 0.6, place 0.9, sub 0, ultra 0 | lizards hear best at 0.5-4 kHz, little above ~5 kHz (Brittan-Powell et al. 2010; Wever 1978): the 4-8 kHz band that tells s from ʃ is coarse |

**saurian**: inherits the stem unchanged.
**lizardfolk**: sibilant 0.6, harsh 1.5 (teeth and a big mouth).
**troglodyte**: inherits; I found no reason to differ.
**tortle**: articulators `-teeth +beak`; labial **2.0** (closing a beak shuts the front of the tract much as lips do, so a beak labial is
a nearer substitute than a lipless lizard's), round_vowel 2.0, dental 2.0, sibilant 1.5 (no teeth for the sibilant obstacle;
Shadle 1985). Hearing: sibilant 0.2, place 0.5, back 0.6, height 1.0, length 1.2. Turtle ears are best at 300-500 Hz with little
above ~1.2 kHz (Christensen-Dalsgaard et al. 2012): F1 (height) sits in range, F2 (backness) and consonant bursts mostly above it.
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

| percept | symbol | source |
| --- | --- | --- |
| harsh / growl phonation | V‼ (e.g. a‼, ɣ‼) | VoQS: ventricular phonation (VoQS harsh voice V! is harshness *without* ventricular vibration; a growl is ventricular, so ‼) |
| purr phonation | ᵣ (U+1D63) after the segment | house, Phonetic Extensions block |
| second simultaneous source | ᴖ (U+1D16) after the segment | house; VoQS diplophonia V̬‼ is glottal + ventricular, not two independent sources, so not reused |
| sub-bass register | ˯ (U+02EF) | house, Spacing Modifier Letters (a UPA-style arrowhead) |
| ultra register | ˰ (U+02F0) | house |
| lip smack, teeth clack | ʬ ʭ | extIPA percussives |
| beak or mandible clap | ʞ | house: the IPA letter for the velar click, withdrawn in 1970, reused for a knock heard as velar-region |

## Open doubts

1. **Is a beak closure heard as labial?** I assumed yes for tortles (cheaper) and partly for birds. The 1998 parrot-stop paper is
   the place to check how Alex actually made /p/; I have only its title and venue confirmed tonight.
2. **Two voices as contrast.** I let `source2` carry contrast for birds (cost 1.5). Real birds use two voices in song, not (as far as
   anyone knows) to contrast words. A conservative alternative is a purely phonetic layer with no contrast.
3. **Harsh and purr are impossible for humans.** That follows the contract, but humans do produce ventricular and aryepiglottic
   voice, and a few languages use epiglottalized or harsh-voiced vowels contrastively (as I recall, !Xóõ). Cost 8 instead of inf
   would be more honest; I left it impossible so non-human percepts stay non-human.
4. **Dragon hearing** is extrapolated from elephants and from the general "bigger animals hear lower" pattern; reptile ears
   (archosaur) are tuned low too, which agrees, but there is no animal of dragon size to compare.
5. **Cat lips** (above) and **giants' slowness** are judgement with no measured source.
6. **The place-distance geometry** (labial nearer velar than dental) drives how labials are heard by beaked listeners. It follows
   Jakobson's grave/acute, which is acoustically sound, but listeners in noise confuse labials with dentals too (f/θ).
7. **PHOIBLE fortis/lenis** (k͈, k͉, Korean-type) has no axis yet: those segments count as plain. Small (3% of languages).
