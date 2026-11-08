# Review of the language engine's output: run a24559 (PW-986), 2026-11-04

Reviewer's read of `runs/a24559/languages.json` (137 MB, seed 12, RATE_SCALE 5, REPLACE_SCALE 1.25), done the way a historical
linguist would look at a field survey: are sisters sisters, are the changes believable, do the numbers mean what they say.
The `names` block was skipped (being regenerated). Every number below was computed from the file; scripts are in the session
scratchpad, not the repo.

**In plain words.** The machinery works: there is a family tree, words are borrowed along food routes, sound changes spread
between neighbours, conquered peoples switch language and keep local words, and grammar words wear down into endings. Read
as a linguist, though, three things spoil the result. (1) **Every language drifts toward the same sound.** Words lose their
consonants and pick up a glottal catch and a mid-central vowel, so after 20 kyr a third of all core words in every species
start with ʔ, and humans, dragons and bird-folk sound alike (`ʔɛ˦e̞˨me̞`, `ʔɜʔɜʔɜ`). (2) **Old words are replaced mostly by
words made from nothing**, not by derivation, borrowing or meaning shift, so families lose their shared vocabulary quickly,
and fast-breeding species (aarakocra, kobolds) lose it completely within 5 kyr. (3) **The shift count is inflated about
three times**: a deme that has already switched to its conquerors' language "switches" again every 0.5 kyr. The horizon
check misses (13 kyr against 6-10) mostly because of how it is measured, not because sound change is too slow; the speed-up
used to chase it (5x) is what makes sister dialects only 52% intelligible after 500 years.

Run at a glance: 1,434 lects (321 protos, 573 living), 255 true families among the living, 547 "languages" for 573 living
lects (almost every lect is its own language), 399 shifts, 172 food routes, 236,172 logged sound changes (102,669 by wave).

## 1. Cognate tables

Key: `=` inherited from the family's proto; `N` a new root coined inside the family (date and coining lect in the note);
`L` a loan from another family; `+d` derived/compounded on the way. Spelling in ‹›.

### 1a. Human family p279 (Simath, south-west): d493, d541 split at 20 kyr; d748 and d787 budded from d493 at 8.5 and 6.5 kyr

| concept | proto p279 (20 kyr) | d493 human 11 | d541 human 17 | d748 human 60 | d787 human 78 |
| --- | --- | --- | --- | --- | --- |
| WATER | kmjaː˧ | ʔɜ˦mɜɜ˦ ‹'ë́mëë́› = | ʔɛ̃˦kxɛ̃˦me̞˧ ‹'ẹ̃́kxẹ̃́me› =+d | ʔə˦lɨ˧dʰɨ˨ ‹'ë́lïdhï̀› L | ʔɜ̃˦mɜɜ˨ ‹'ë̃́mëë̀› = |
| FIRE | t.su˧ɲ | ɲi˧mɛ˧e̞˧ ‹nyimẹe› =+d | ɲə̃˧mə˧ə˧ ‹nyë̃mëë› L | ʔa˦mɛ˧e̞˨ ‹'ámẹè› N | ɲĩ˦mɛ˧e̞˨ ‹nyĩ́mẹè› =+d |
| HAND | ma˨ | ma˨ ‹mà› = | ʔɛ̃˦t̪e̞˦tʰe˦ ‹'ẹ̃́t̪éthé› N | ma˨ ‹mà› = | ma˨ ‹mà› = |
| ONE | te˧ | ʔe˦ ‹'é› = | ʔɛ̃˦t̪e̞˦ʔɛ̃˦ =+d | me˨˦ ‹mě› N | ʔe˦ ‹'é› = |
| TWO | pi˧kɛ˦h | ʔi˦ʒe̞˦ ‹'ížé› N | ʔə̃˦ʃə˨ə ‹'ë̃́šë̀ë› = | ʔɛ˦ʔɛ˦ɛ˨ =+d | ʔɨ˦ə˨ ‹'ḯë̀› N (same coin as d493) |
| STONE | çla˨wu˦vnje˦k | ʃɨ˦dʰɘ˦ʔɘ˦ɲɘ˧ L | ʔɛ̃˦ʔɛ̃˦me̞˧ L | na˦ɡʰa˨e̞˨ ‹nághàè› N | na˦a˨e̞˨ ‹náàè› N (same coin) |
| TREE | ɡi˧tkra˦lɡ | la˧me̞˧ʔɛ˦ʔi˦ L | kxə˦ ‹kxë́› L | ʔɛ˦ʔa˦mɛ˧ N | ʔɛ˦ɲĩ˦mɛ˧ =+d |
| NIGHT | mu˦ | ʔɛ˦ʔi˦ne˧ L | ʔɛ̃˦ʔɛ̃˦e̞˧ =+d | mɨ˦ ‹mḯ› = | ɹɛ˧ ‹rẹ› L |
| DRINK | ŋjeː˨tɛ˧m (= EAT) | ŋɜ˧ɘ˦ɨ˧ ‹ngëë́ï› = | ŋə˧ə˨ʔɨ̃˦ = | ŋɜ˧ɘ˨ɨ˧ ‹ngëë̀ï› = | ŋɜ˧ə˨ɨ˧ ‹ngëë̀ï› = |
| BONE | twu˨ | ʔi˦nɛ˧dʰi˦ L | ʔə̃˦nə˧ə˧ L | ʔɛ˦ʔɛ˦e̞˨ =+d | ʔɛ˦çe˨ɗe̞˨ =+d |
| FISH | ɲeː˨tri˧ | ʔɘ˦lɨ˨ ‹'ë́lï̀› N | ŋə˧mə˧ə˧ N | ʔa˦ne˦˨ N | ʔə˦lɨ˨ ‹'ë́lï̀› N (same coin) |
| I | tʰi˦mdnu˦n̪ | ʔɛ˦i˨ ‹'ẹ́ì› = | tʰĩ˦me̞ʔɛ̃˦ɲĩ˦n̪e̞ = | ʔə˦lɜ˨nə N | ʔɛ˦i˨ ‹'ẹ́ì› = |
| THOU | ble˨ | ʔɜ˦lɘ˨ ‹'ë́lë̀› = | t̪a˦e̞˦lĩ˨ne̞ N | ʔə˦lɘ˨ = | xʋĩ˨kʰxne˧ N |
| WE | ɡɛ˧fu˧m | tʰɪ̞˦li̠˦mɪ̞ N | kxɛ˦ĩ˧ne̞ = | ʔɛ˦i˨ = (d493's I) | ʔa˦je̞˨ɛ˦ L |
| HEAR | mɛ˦rkza˨ | ɲɪ̞ɛ˦nɪ̞˨dʼi̠˨nɪ̞ N | ʔə̃˦lɨ˧ʔɨ̃˦ L | ɲəɜ˨nɘ˨dʼɨ˨nə N | ɲəɜ̃˨nə˨dʼɨ˨nə N (same coin) |

**Verdict: sisters look like sisters, but only in their vowels.** d493 and d787 (parted 6.5 kyr) share a root in 27 of the
100 core words, 8 of them identical bar tone; consonants match one for one (ʔ:ʔ 21, ɲ:ɲ 9, l:l 6, m:m 4) and every
difference is a vowel. Regular, statable correspondences: d493 **ɪ̞** = d787 **ə** (9 tokens: GREEN, HEAR), d493 **ɘ** = d787
**ə** (DRINK, EGG, FISH, SIT), d493 **i̠** = d787 **ɨ**, d493 oral **i, ɜ** = d787 nasal **ĩ, ɜ̃** next to a nasal (FIRE, WOMAN,
WATER). From the proto: *k > ʔ and *t > ʔ word-initially (WATER *kmjaː > ʔɜmɜɜ, ONE *te > ʔe), clusters reduce to their last
sonorant (*kmj > m), final consonants are lost (*-m, *-h, *-k), long vowels break into two vowel letters (*aː > ɜɜ). d748-d787
(8.5 kyr) share 18 roots, d493-d541 (20 kyr) 2: **distant lects do look distant.** Two problems a linguist would stop on:
the proto forms are not possible words of a human language (`çla˨wu˦vnje˦k`, `tsla˨zkbleː˦t̪`, `t.su˧ɲ` with a stray syllable
dot), and every descendant has the same shape `ʔV˦CV˨` regardless of what the proto looked like, so resemblance across
families is high too. Also TWO, FISH, STONE, HEAR are new coinages shared by d493 and its daughters: real numerals and body
parts are not replaced by invented roots this often.

### 1b. Aarakocra family p222 (Sothasor): d353, d389 split at 20 kyr; d697 and d799 budded from d389 at 12 and 5 kyr

| concept | proto p222 | d353 aarakocra 14 | d389 aarakocra 18 | d697 aarakocra 32 | d799 aarakocra 36 |
| --- | --- | --- | --- | --- | --- |
| WATER | ji˦˨kli˧ʕ | tə̟˦ɓə̟˨ L | ʔɜ˦lɜ˦˨ɜ˧ ‹'álâa› N | ʔɜ̠˦ʔɜ̠˦ɜ̠˧ L | ʔɘ˦ɘ˧ɨ˧ ‹'áaï› L |
| FIRE | ko˧ | ʈə̟˦lə̟˧i̠˨r‼ə̟ N | ʔɜ˦ɜ˨ȶɜ˨ɨ˨ N | ʔɜ̠˦ʔʼɜ̠˦ɜ̠˦ N | ʔɘ˦ʈʰɘ˦ħɨ˨ N |
| EYE | hu˦hi˨˦ | ʈi˦ħe̞˨ ‹ṭíḥè› N | ʔɜ˦ʔɜ˦ɨ˨ N | ʔɪ˦ɡʰʱɛ˦ʕɛ˨ N | kʰji˧lcçɫi˦˨lʔ N |
| HAND | mo˦˨ | ħə̟˦ħə̟˨cçə̟˨ L | ħɛ˧i˧ɹi˧e̞˧ L | ʔɜ̠˦lɜ̠˨ N | ʔɘ˦ɜ˨ L |
| TWO | sri˨˦so˨j | li˦˨ʃi˨ N | ɬɜ˦lɜ˧ ‹hlála› L | tɜ̠˦ɫɜ̠˨˦ɘ˦ N | kʰle˦je˨ɗ N |
| ONE | to˧dso˦˨ | cçə̠˦ħə̠˨ə̠ N | ʔɪ˦ɗələ˦˨ N | tɜ̠˦ɜ̠˦ N | ʔɘ˦ɬɘ˨ɹɜ L |
| STONE | rɪ˨ɡzu˨˦ | ʈə̠˦lə̠˧ɹə̠˧ N | tsi˦kʰi˨ ‹tsíkhì› N | kʰɜ̠˧r‼ɜ̠˧wɜ̠˧ L | lɨ˦jmȶi˦ N |
| TREE | ʈju˨tku˦˨kbu˨˦ | ʔi̠˦ʔɛ˦lə̟˧ N | ʈʰɜ˦r‼ətʰɨ˨kʰəʈʰɘ˨ N | ʔɪ˦ʔɪ̞˧ɹi˧ L | lji˧ʃi˦˨jtʰɨ˨ N |
| SUN | hɛ˨˦hli˦˨ | tʰə̠˦ N | te˧ɫe˧ ‹telle› L | lɜ̠˨˦ɜ̠˨lɨ̠˧ N | ʂɘ˦ɘ˧lɨ˧ L |
| NAME | ziː˨˦ᴖtju˦ʈʔli˨ | ħɛ˦ɹɛ˦˨i˨ȶe̞˨ N | tɜ˦ɜ˨˦mɘ N | ʔɜ̠˦ʔɜ̠˦ɜ̠˦ N | lɘ˨˦ɘ˨˦lɘʔɜ˦ N |
| DOG | kɛ˦hʈli˦˨tʃ | ɗli˧wki˦˨ N | ʔi˦ ‹'í› L | ʔɜ̠˦ɜ̠˦ʔɜ̠˦lʼɜ̠˧ N | ʔɘ˦ɹɘ˧ɹɘ˧ɹɘ˧ʃɘ˨ɘ˨ L |
| FISH | li˦˨sjo˦˨sjo˨˦lȶ | ʈe̞˦k ‹ṭék› N | ȶʰɜ˦ʔɘ˦ N | ɗɪ˧ȶɨ̠˨˦ N | ʔɘ˦ɘ˨˦ʔɘ˦ʃɘ˨ L |
| BLOOD | ti˧tɡtʃu˧ | xɛ̠˧tɛ̠˧r‼ɛ̠˧ L | ʔɜ˦ʔʼɨ˦ N | mɜ̠˦˨ʔɜ̠˦li˧ N | ȶɘ˦ʔɜ˦ N |
| EAT | mlu˨ro˨˦ | li˨˦ʃe̞˨ N | ʔɜ˦ɹəɹɨ˧ L | ʔɪ̞˧ɹi˧ʒɪ̞˧ L | ʔɘ˦ɘ˧ʔɨ˦ N |
| I | ʈɛ˨llo˧k | cçə̠˦wə̠ N | ʔɜ˦lɨ˦ ‹'álḯ› N (= WE) | r‼i˧ L | ʔɘ˦ɘɘwɜ N |

**Verdict: no family is visible at all.** Not one of the 15 is inherited in any living lect; d389 and d799, parted only 5
kyr ago, share **0 of 100** core roots (their I words are two different coinages, both dated in d389's own history). With a
5.8-year generation the aarakocra pass ~860 generations in 5 kyr, about what humans pass in 24 kyr, and lexical replacement is
counted per generation. Loans (`L`) come from other families (p161, p71, p62, p54 and more). The proto forms are
again unpronounceable (`ʈju˨tku˦˨kbu˨˦`, `ziː˨˦ᴖtju˦ʈʔli˨`), and d389's I and WE are the same word. The house spelling leaves
raw IPA in a third of these cells (`tə̟˦ɓə̟˨` is spelled ‹tə̟́'bə̟̀›).

### 1c. Contact across families: kenku d565 (p139) and kobold d185 (p151), neighbours in the south of Simath since 20 kyr

| concept | kenku proto p139 | d565 kenku 23 | kobold proto p151 | d185 kobold 5 |
| --- | --- | --- | --- | --- |
| WATER | zi | ʔe̞ː˦ɓe̞˨ L | t̪akɛ | ʔɜ̠˦ɜ̠ʔːɜ̠˦ ‹'ɜ̠́ɜ̠':ɜ̠́› L |
| FIRE | ɾabujʈkɹirk | ʔe̞ː˦ɾɫe̞ N | hikli | nɜ̠ʔɜ̠˦nɜ̠ɗːə̠ N |
| EYE | jiqʷi | pəː˦ɫwə̠ N | a‼dkaːkʷʰaː | t̪ɜ̠˦ɜ̠ɜ̠˦nɜ̠ɜ̠ɜ̠ɜ̠ə̠nːə̠ = |
| HAND | tːuni | m‼ə̠ə̠˦li L | a‼ | nɜ̠˨˦ N |
| TWO | litso | ʂe̞ː˦ɫe̞ N | n‼a | ʔə̠˦ʒːi˨ N |
| ONE | ʈwohzip | ʔi˦ ‹'í› **loan from d185** | zɛpa | ʔɜ̠˦ɜ̠wə̠nːə̠ N |
| STONE | wi | ʔe̞ːwe̞li N | zajn̪ɛtidʒ | la N |
| TREE | ɡɾahjaʈla | we̞ːwbe̞˦ʒe̞˦ N | aŋ | ʔin‼e̞a‼ L |
| DOG | sapla | j‼e̞ːɾʒi˦ N | aːtaɡ | t̪ə̠˦ N |
| FISH | tɔ | ne̞ːɖʰe̞˦ N | ɾa | ɫːɜ̠ʔə̠˦ɾːə̠ N |
| BONE | ahsi | nəʔ L | ŋa | nə̠ɫːɜ̠nːɜ̠˨˦ N |
| EAT | kirh | ʔəː˦wə̠ = | paɡaːdʒ | kʰə̠˦ɫːə̠ L |
| I | kwi | kəː˦wə̠ = | tadʒtan‼ | kʰɜ̠˦ (= WE) N |
| WE | pozon | ʔe̞ː˦ʒe̞˦e̞ɓe̞˨ N | rɛkad | kʰɜ̠˦ N |

**Areal verdict: heavy contact in the log, little in the languages.** 376 of d565's 1,064 sound changes came from d185 by
wave (and 529 of 1,064 by wave in all), the most of any cross-family pair; yet the two share only 19 of 72 segments, 17 of 41
typology values and one core loan (ONE). The adopted rules land on different inputs: the kobold lect has a gemination
areal feature (ɫː nː ɓː ʔː ...), the kenku lect has long vowels instead. A linguist would see shared *types* of change
(ʔ-onsets, central vowels) but those are everywhere in the run (section 9), so they do not mark an area. Also: EYE in d185 has
six vowels in a row (`ɜ̠ɜ̠ɜ̠ɜ̠ə̠`), and the protos again carry 5-consonant clusters (`ɾabujʈkɹirk`).

## 2. Four etymologies

**(a) HAND in d587 (human 26), 10 steps, a loan, three meaning changes.** 15.5 kyr d587 coins *nuln̪wiː* 'far' > 14.5
sound change (ə-epenthesis S123, nasalization) *nulən̪əvɨ* > 13.5 **borrowed back** from d643 (human 37, another family)
as *nolənəmɘ* 'far' > 10.5 back harmony, inventory merge *ɲiliɲimi* > 10.0 derived 'far' + 'like' = *ɲiʔəʔə* 'long' >
8.0 tone split *ɲiʔẽ˦ʔẽ˦* > 7.5 taboo replacement: 'long' becomes *ɲiʔẽʔĩ* 'claw' > 6.5 denasalization *ɲiʔe̞ʔi* > 6.0
compound CLAW + FIVE *ɲiʔe̞ʔitʰʉ* 'hand' > 2.0 harmony, nasalization and 22 more changes > now *ɲɨʔɜ˦ʔɨ˦ɗɨ˨* ‹nyï'ë́'ḯ'dï̀›.
'Far-like' for 'long' and 'claw-five' for 'hand' are good, believable paths; a taboo on 'long' is the weak link. (HEAD in d831
is as good: a green-dragon word for 'hair' borrowed at 10.5 kyr, shifted to 'head', compounded HEAD + LEAF = 'hair', then
HAIR + 'thing' = 'head' again.)

**(b) Maize, from food routes: 13 borrowings across 10 species in 8 kyr** (route of `crop:maize` from d25, 104 hops; the
chain below is the line that reaches d854, human). 11.0 kyr hill giant d25 coins *ʔa˦ŋɗiː˦n* 'seed' > 8.0 'seed' + 'little'
= *mɨ˦ʔa˦ɗje˨* 'maize' > 8.0 leonin *mɨʔaɗje* > 8.0 brass dragon *vɨ̠ʔaɗɲe* (m heard as v: dragons have no lips) > 7.5 hill
giant *vɨʔɛ̠tʰɲɘ* > 7.5 brass dragon *pfɨ̠˧ʔe̞˧ɗi˨ɳə̠˧* > 7.5 copper dragon *fɨʔe̞tʼiɻɜ* > 7.5 halfling *mɨ˧ʔe˧tʰi˧ɲ̟ɐ˧* (labial
restored) > 7.5 human *mɨ˧ʔø˧tʰi˧ɲɐ˧* > 7.5 halfling > 7.5 orc *mɨ˧ʔe̞˧t̪ʰi˧ɲɜ˧*, then lengthening > 7.0 human *mɨː˧ʔə˧t̪ɨ̞˧ɲɜ˧* >
5.5 kobold, kept through three of that deme's re-shifts as "substrate" > 4.5 red dragon *n̪ɨʔɜɗɜɲɜ* > elf *niʔɜ̠dʰɜ̠nɜ̠* > human
d570.2 *niʔɑ̟tʰɑ̟nɑ̟* > 3.0 halfling *nɨʔatʰana* > 2.0 back into d570.2 > now d854 *nɨ˧ʔɛː˧je˧nɛ˧* ‹nï'ẹẹyenẹ›. Each hop's
adaptation is sensible (m > v > f among lipless speakers, m back among humans); the route as a whole is too fast (eight hops
between 8.0 and 7.5 kyr; 14% of all hops fall in their route's first frame) and it ping-pongs.

**(c) A substrate survivor: 'goat' (`animal:caprine`) in d127.1 (dwarf 1, now speaking a human language).** 20.0 kyr proto
p100 *ɡoːɲunĩ* > by 3.5 kyr d127 (dwarvish) *kʰo˦ɲʷunʷu* (devoicing, labialization) > 3.5 the deme shifts to the human lect
of d643 and keeps the word as substrate, heard through the new sound system: *kʰoɲunu* (ɲʷ, nʷ have no human match here) >
now *kʰo˦ɲũnu* ‹kónyũnu›. FISH did the same: p100 *koːʔɛ* > d127 *ʔy˦ʔœ˦* > substrate *ʔiʔɛ* (front rounded vowels heard as
unrounded) > *ʔi˦ʔã˦*. Exactly what a substrate word should look like.

**(d) A compound: cooking greens in d713.2 (human).** 20.0 kyr blue-dragon proto p29 *lesitets* 'stick' > 12.5 *lesi˦ʔe˨dze̞*
> 10.0 meaning shift 'stick' > 'tree' > 5.0 compound TREE + ROUND, clipped, *lesitadʰʱe̞* 'cooking greens (brassicas, leeks)'
> 5.0 brass dragon *le̞ʃitatʰe̞* > gold dragon *le̞sitate̞* > dragonborn *ɹe̞s̪itʰatʰe̞* (two re-shift "substrate" steps) > 4.0
hill giant *ɹə̟nɪtʰɜtʰə̟* > hill giant > green dragon *ɹe̞netəte̞* > orc *ɹɛ˧ne˧tʰɜ˧tʰɛ˧* > 3.5 human d713.1 *ɹənədʰʱːɜdʰʱːə* >
now *ɹɘ̃˧nɘdʰʱɜː˨dʰʱɘ˦* ‹rë̃nëdhë̀ëdhë́›. 'Round tree' for a cabbage is a nice image; the double-marked *dʰʱ* is a defect
(section 9).

## 3. One shift in full: dwarf 1 (deme 127, the west of Simath) to human, 3.5 kyr ago

- **Trigger (plain words):** about 6 kyr ago humans of deme 643 (human 37) took five dwarf sites (`takeover`, strength 0.7,
  held from 6.2 kyr to now; source: settlements.json holders). The dwarves stayed, under human rule, and learned the rulers'
  speech over three thousand years.
- **Shares of the rulers' lect among the dwarves:** 7.5 kyr 0.03, 7.0 0.06, 6.5 0.08, 6.0 0.14, 5.5 0.23, 5.0 0.31, 4.5 0.41,
  4.0 0.48, **3.5 0.525: shift**. A neighbouring human lect (d750) reached 0.085. After the shift the deme record still
  shows 0.44 of the old dwarvish (falling to 0.29 now), yet lect d127 is marked dead at 3.5: either dwarvish is still spoken
  by a third of the deme, or the number means something else. A minority language should stay alive.
- **Old lect d127 (dwarvish, at death):** 33 consonants `ħʷ v ŋʷ kʰ ŋ l n ɗ x ʔ m nʷ s ɳ ʒ kʼ ɲ pʰ kx bʰ ʃʷ t kxʷ t̪ʷʰ ɡ ɲʷ ɡʰ ʒʷ lʷ k
  w l̪ ʃ`, 20 vowels `y ɶ a i ɛ e o ɔ ɒ u ɨ ɘ ä œ ə o̞ ø øː oː ɜ`, no tone, open syllables only (CV 0.85, V 0.15), VOS, few
  cases. Core: WATER t̪ʷʰo˦, FIRE nava˨mi, STONE kiɲaʔe, EYE nʷy, HAND kʰa˦ŋi˨, TWO lese˦ʔe˦, I mɨnɘʔɘ˦, EAT = DRINK mɨnɘ,
  DOG kxʷy˦ŋʷy, FISH ʔy˦ʔœ˦.
- **New lect d127.1 (now):** 22 consonants `ʔ l n θ f ŋ ʃ kʰ kx h pʰ tʰ ɲ ɗ ɓ ts ɲ̟ s ð ʒ bʰʱ ɡʰʱ`, 15 vowels; the rulers' d643 has
  24 and 15. Core words track d643 closely: WATER ŋo / ŋo, EYE ʔɨ̃˦nɜlaɨ / ʔɨ̃˦nəlaɨ, HAND ʔe˦liʔi˦le / ʔe˦le̞ʔi˦le, TWO kxo˦ / kʰo˨.
- **Kept as substrate:** 57 concepts, the whole "local" list: FISH, BIRD, DOG, LEAF, LOUSE, ROOT, STONE, TREE, BARK, CLAW,
  EARTH, MOUNTAIN, SAND, SEED (14 of them Swadesh-100 items), plus landscape (HILL, LAND, SEA, RIVER, MARSH, PASS, FORD,
  COAST, DESERT, CAVE, ISLAND ...), wild animals, goat, cattle, horse, fowl, seals, shellfish, wheat, vine. Landscape and
  livestock are right; DOG, FISH, BIRD, LOUSE, TREE, STONE are not what shifting populations keep (median over all shifts: 56
  words, 14 core-100 items).
- **Accent (old sounds substituted for new):** c>t, dʰʱ>ɗ, dʱ>t, e̞>e, n̪>n, tʰ>t, ĩ>i, ũ>u, ɓ>bʰ, ɟʱ>ɡ, ɡʰʱ>ɡʰ, ɡʱ>ɡ, ɣ>x,
  ɨ̃>ɨ, ɪ>e, ɲ̟>ɲ, ɹ>n. Sensible (dwarvish had no nasal vowels, no c, no breathy stops). They did not stick: d127.1 has tʰ, ɓ,
  bʰʱ again now (taken back from d643 by wave).
- **Calque:** head direction initial (from dwarvish) instead of the rulers' final. Plausible.

This is a good shift. The problem is that most of the 399 shifts are not like it (section 9).

## 4. Two paradigms and how they got there

**d587 (human 26, family p235, VSO, no case).** Nouns: WATER ȶa˦e̞ʒi˨, plural **pʰi˦-**ȡa˦e̞ʒi˨ (the stem's ȶ voices after the
prefix); DOG ʔa˦i˨ / pʰi˦-ʔa˦i˨; TREE nʷãme̞ / pʰĩ˦-nʷãme̞. Verbs: GO xʷɜ̠˨, 3SG xʷɜ̠˨-**ʔɜ̠˦**, 1SG xʷɜ̃˨-**ɲɨ**; SEE ʃʷɨ˦ʐɨ˨,
ʃʷɨ˦ʐɨ˨-ʔə˦, ʃʷɨ˦ʐɨ̃˨-ɲɨ (the vowel nasalizes before the 1SG suffix: a nice irregularity). Periphrastic: REFL ʂa˦ʔi˦ (from
HEAD, 2.5 kyr), ACC ŋʷuɲu (from TAKE, born now).
- PL, from ALL: free word *pʰukʰe* (20 kyr) > *pʰʉ˦kʰɵ˦* (17.0) > clitic *pʰʉ˦kʰɵ˨* (12.0) > affix *pʰʉ˦* (10.5) > *pʰi˦* (9.0).
- 3SG, from HE/SHE/IT: *tʃɔka* (20) > *ʃɔ˦ɛ˦* (18.0) > *ʃɔ˦we˦* > *xɔ˦o˦* (14.5) > *ɔ˦o˦* > *ʔɔ˦o˦* (13.5) > clitic (13.0) > affix
  *ʔɑ˦* (12.0) > *ʔɛ̃˦* > *ʔə˦*. A textbook pronoun-to-agreement path; the erosion t͡ʃ > ʃ > x > ∅ > ʔ is the run's usual one.
- 1SG, from I: *ɲiʃe̞˦* free (7.5) > clitic (4.5) > affix *ɲɨ* (4.0): 3.5 kyr from pronoun to suffix is fast but possible.
- NEG *ni* died at 19.0 and was never renewed; the lect negates with its free word NOT. 409 of 573 living lects have no NEG
  gram; that is fine only because NOT is in every lexicon.
- Defect: EAT and TREE are the same word, *nʷãme̞*.

**d192 (storm giant 4, Sothasor, SOV, many cases; 4 fused grams and 40 paradigm cells, among the most complex lects).** Nouns: WATER haːvamu, PL haːvamu-**ŋe̞**,
CLASS:2 **ʔɛ˦i**-havamu (stem h ~ v alternation), ACC haːvamu-**βɛ˨ŋe̞**, PL.ACC haːvamu-ŋe̞-βɛ˨ŋe̞; PERSON takes CLASS:1
**tʰə̠˦vɜ̠˨**-; DOG CLASS:2 ʔɛ˦i-dʰɛ˨ɛɛ˨ (the stem's vowels change with the prefix: real allomorphy). Verbs: GO ʔaː˦ŋe̞, NEG
**hi˦**-jɛŋe̞ (suppletive-looking), PERF ʔaː˦ŋe̞-**hi˦**, 1PL ʔaː˦ŋɛ (fused to a vowel change, its affix is empty). Sources:
PL < ALL, NEG coined, CLASS:1 < PERSON, CLASS:2 < PEOPLE, ACC < TAKE, PERF < HOLD, DAT < GIVE (clitic ʔu˦ŋɔ, homophonous with
the verb GIVE: right for a young gram), LOC < IN, AGENT < PERSON. All attested paths.
- LOC runs a full cycle: free *ɡrosjil* (20) > clitic (16.0) > affix *ɡə* (13.0) > fused *ɛ̠* (12.0) > zero (10.5) > lost (5.5) >
  renewed from IN as free *fɨ˦ə̠* (3.0) > *hɨ˦*. Exactly the grammaticalization cycle the design wants.
- CLASS:1 *dɛhin* free (20) > clitic (18.5) > affix *dɛ* (15.0) > fused *dɔ, dɑ, tʰa˨, tʰɔ˨* > *tʰwe˦* (7.0, ɔ > we) > *tʰve˦* >
  *tʰəvɛ˦* (5.5, ə-epenthesis) > *tʰɜ̠˦fɜ̠˨*: a fused prefix that **grows** back to two syllables through epenthesis and
  diphthong breaking. Possible, but it shows the epenthesis rules re-firing (section 9).
- Defect: PL was worn to nothing (`""` at 4.0-2.5 kyr) and came back as *ŋe̞* at 2.0 with born_kyr still 20.0. Sound change
  cannot do that; something resets gram forms (`grammar.py`).
- The run's grammar is thin overall: median 2 live grams per living lect (10th-90th percentile 1-5), 47 lects with none.

## 5. Sound change over time: d587 (human 26)

317 logged changes in 20 kyr (15.9 per kyr in this lect alone): coarticulation 107, effort 65, dispersion 63 (26 of them
inventory-cap merges), prosody 38, perception 27, tonogenesis 17. **164 of 317 came by wave**, first from d444 (19.5-16.5), then
mostly from d643, d577, d177 (human lects of family p145), d127.1 (the shifted dwarves) and once from d25 (a hill giant).

| kyr | consonants | vowels |
| --- | --- | --- |
| 20 | 38: m βʲ n j p s t ŋʷ ɳ ʔ k pʰ d b ɣ ʂ l w ɲ ts kː ɾ ɓ χ h dʒ ʃ ʈ tʃ kʰ ʐ kʷ tʰ c z ȶ ɭ ɹ | 10: e ə eː i a u ɔ o aː ɛ |
| 10 | 42: j ʔ ɲ ɭ m l ɖʰ tʰ ɹ n kʰ ɡʰ lʷ ɗ ɳ ɓ ʈ pʰ v ȶ ɟʰ dʰ ŋʷ xʷ ʐ ʂ ŋ f ɾ bʰ ʈʷ ɡʷʰ c ɖʷʰ kʷʰ ȡʰ dʷʰ nʷ ɖʷ ɟ ɗʷ ɾʷ | 10: i ʉ e̞ ɘ ə a ɛ o e ɔ |
| 5 | 45 (cap): ʔ ɲ ʒ ɭ m l ɖʰ tʰ nʷ ŋ dʰ lʷ ɗ ʂ ʃʷ pʰ ȶ ŋʷ kʰ ɟʰ ɹ β ȡ dʒ ɖ ʐ ɳ n d ɓ ɣ bʰ ɾ ɡʰ ʈ ɣʷ ʈʷ ɖʷ ɗʷ cʰ c ɟ ɲʷ ʒʷ ɡ | 15: ɨ ə ɜ̠̃ ɜ̠ e̞ i ĩ o ɜ a ɛ̃ e ɛ ẽ̞ ɔ |
| 0 | 45 (cap): ʔ ɲ l tʰ j ʒ ɭ m ɖʰ xʷ ɗ kʰ ʂ ŋ ʃʷ pʰ c ȶ ŋʷ n ɹ h ɾ ɳ ʈ nʷ ɖʷʰ cʰ ʐ v ɓ ɣʷ dʰ ȡʰ ɗʷ ʈʰ lʷ ɟʰ ɖ ʈʷʰ ȡ ɟ ȶʰ bʰ ɡʰ | 15: ɨ a i ə e ɜ ɜ̃ ɜ̠ e̞ ĩ ɛ ã ɨ̃ ẽ̞ u |

The log in order, condensed (own change unless "<source"): **19.5-18.0** u > ʉ (push); ɛ > je, ɔ > we; nasal place
assimilation; k > tʃ before front vowels <d444; long vowels shorten <d444; j > dʒ initially <d444; tone split after voiced
obstruents; ts > s; k > h between vowels <d444; h lost; n > ɲ before i; a > ɛ in open stressed syllables; kʷ > p; VC
lengthening; s > z between vowels; tʃ > ʃ <d25 (hill giant); t > θ between vowels; geminates shorten; j > ʒ; **p > f, t > θ,
k > x** <d444 (a Grimm's-law-like shift). **17.5-15.0** w > b initially; ə-epenthesis between consonants; iː > ai, uː > au; z >
s; b > ɓ, d > ɗ <d444; harmony; **ʔ inserted before initial vowels**; voiced stops > breathy; t > ʔ between vowels; f > h
<d643; voiced fricatives after unstressed vowels; w > v; a 28-sound vowel merge at 15.0 (the vowel inventory had briefly
passed 40). **14.5-10.0** s > ʃ before i; rhotacism <d643; h lost again; harmony again; intervocalic voicing; syncope; s > h;
w > v <d577; tone split again (<d577, <d692, <d643). **10.0-5.0** f > h;
spirantization; nasalization; j > ʒ; harmony again and again (from d177, d643, d577, d177.1). **5.0-0** harmony nine more
times; intervocalic voicing seven more; umlaut <d127.1; ʃ > x; tone split five more; e > i, o > u (raising); ɛ > je again.

Words at 20 / 15 / 10 / 5 / 0 kyr: EYE *tʃi* > *ʃi˦* > *ʔi˦* > *ʔĩ˦* > *ʔi˦* (the whole erosion chain tʃ > ʃ > h > ∅ > ʔ in
one word); WATER *paː* > *fɛ˦* > *əjɘ˦*, then replaced by *ȶa˦e̞ji* (river + 'thing', 14.5) > *ȶa˦e̞ʒi˨*; TWO *deːɣu* > *θe˨xʉ˨* >
*ti˨ɣi˨* > *ʔə˦ji˨* > coined anew as *ce̞˦* at 5.0. A linguist reading this log sees good individual changes and a bad
**ensemble**: the same rule fires again and again (harmony 25 times, nasalization 15, voicing 15, tone split 13), voicing and devoicing
alternate, lenition never meets a counter-move, and the consonant inventory sits at the 45 cap for the last 5 kyr with no
plain p, t or k but six voiced aspirates and two alveolo-palatal stop series. Despite twelve tone-split events, the lect's
tone inventory is empty and its typology says "no tone" (section 9).

## 6. Intelligibility and continua

`continua` is **empty**. `intelligibility.now` holds 817 pairs, all but one inside a true family (cross-family pairs are
mostly not stored). Values by how long ago the pair parted:

| parted | pairs | 10% | 25% | median | 75% | 90% | share > 0.7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| this frame (0 kyr) | 26 | | | 0.74 | | | |
| 0.5 kyr | 13 | | | 0.53 | | | |
| 1.0 kyr | 27 | | | 0.35 | | | |
| <= 2 kyr (all) | 151 | 0.18 | 0.27 | 0.37 | 0.50 | 0.73 | 12% |
| 2-5 kyr | 330 | 0.08 | 0.11 | 0.15 | 0.21 | 0.30 | 0 |
| 5-10 kyr | 192 | 0.07 | 0.09 | 0.12 | 0.15 | 0.20 | 0 |
| > 10 kyr | 143 | 0.06 | 0.07 | 0.09 | 0.13 | 0.16 | 0 |
| different families | 1 | | | 0.07 | | | |

Too steep at the young end: Swedish and Norwegian, apart about a millennium, understand each other well; here lects one
kyr apart sit at 0.35, and d860, budded from d604 in the last interval, keeps only 17 of 100 core forms identical
(intelligibility 0.48). The 5-10 and >10 kyr rows hardly differ (0.12 vs 0.09): past ~3 kyr the measure is reading chance
resemblance in a run where everything sounds alike. **No dialect continuum exists**: `families.continua` needs adjacent
values above 0.5 and ends below 0.5 (INTEL_ADJ = INTEL_ENDS = 0.5); only 42 pairs in the run exceed 0.5 at all, and the three
triples that pass a relaxed search (for example d604-d864-d862, ends 0.486) are lects budded in the last frame hovering
around 0.5, not a chain across a landscape. Cause: sound change at 5x speed per lect, with wave spread too weak to keep
neighbours together.

## 7. Species

| people | living | generation (yr) | changes/kyr (own; whole line) | C / V median | mean segments | homophones | core inherited / coined / loans from other families |
| --- | --- | --- | --- | --- | --- | --- | --- |
| human | 92 | 27.7 | 19.8; 24.7 | 28 / 15 | 5.44 | 8.2% | 23% / 63% / 12% |
| elf | 20 | 144.9 | 6.3; 8.8 | 25 / 9 | 5.31 | 12.1% | 67% / 26% / 6% |
| dwarf | 9 | 70.8 | 7.8 | 32 / 12 | 5.34 | 7.8% | 52% / 41% / 7% |
| kobold | 52 | 11.7 | 39.3; 42.2 | 26 / 13 | 5.45 | 8.1% | 6% / 80% / 13% |
| dragonborn | 49 | 24.7 | 25.1; 25.4 | 28 / 13 | 5.54 | 8.1% | 19% / 66% / 14% |
| aarakocra | 24 | 5.8 | 62.0; 70.1 | 26 / 9 | 5.50 | 8.2% | 6% / 75% / 18% |
| kenku | 26 | 19.3 | 42.4; 42.6 | 30 / 15 | 5.42 | 8.0% | 12% / 75% / 12% |
| red dragon | 10 | 430 | 4.8; 5.6 | 23 / 14 | 5.25 | 15.4% | 88% / 11% / 2% |
| gold dragon | 14 | 430 | 4.5; 4.6 | 28 / 10 | 4.95 | 15.6% | 87% / 10% / 2% |
| silver dragon | 16 | 430 | 3.6 | 31 / 12 | 4.92 | 15.2% | 85% / 12% / 3% |

- Rates order the right way (dragons 4-5 per kyr, elves 6-9, humans 20-25, kobolds 40, aarakocra 60-70), but 15x fewer
  generations buys dragons only ~5x fewer changes because they adopt short-lived neighbours' changes by wave, and kenku
  (19-yr generations) change faster than dragonborn (25 yr) for the same reason. Lexically the generation clock is decisive:
  dragons keep 85-88% of their core words, aarakocra and kobolds 6%.
- **Aarakocra are not "mush" by the numbers**: mean 5.50 segments and 8.2% homophones, the same as humans. They are mush by
  ear, but so is everyone (section 9). Dragons have the most homophones (15%), from their small growl-heavy inventories.
- **Labials** (share of all segments in core words, proto then living): human 18.4% > 6.6%, elf 17.1% > 9.3%, kenku 12.9% >
  7.8%, aarakocra 5.3% > 4.5%, kobold 4.1% > 2.5%, red dragon 4.1% > 1.9%. The voice profiles work at the start (aarakocra protos
  have a third of the human labial share; kenku, mimics with labial cost 1.6, sit in between), but the general erosion takes
  humans down to nearly the avian level, so the species difference shrinks from 3.5x to 1.5x.
- **Second-source segments (ᴖ)**: aarakocra 1.9% of segments in protos > 0.7% now, kenku 1.7% > 1.0%; none elsewhere, as
  designed. Growl (‼) stays strong in dragons (red 15.5% > 13.7%). Second-source sounds are being lost by the same erosion and
  inventory merges; they should be among the most stable features of a species' speech.

## 8. The checks

| check | value | target | pass | my reading |
| --- | --- | --- | --- | --- |
| proto inventories vs PHOIBLE | C median 23, V 8; 51% / 54% of protos inside the IQR; top-20 overlap 19 | medians in IQR, 35-75% in IQR, overlap >= 10 | yes | Right target, too narrow: it checks inventories only. The protos' **words** break every phonotactic norm (`çla˨wu˦vnje˦k`, `ʈju˨tku˦˨kbu˨˦`, `ɾabujʈkɹirk`); add a word-shape check (max cluster, sonority) against the declared `shapes`. |
| sisters recognisable, distant not | sisters <= 2 kyr 0.506 (true roots 0.585); cross-family 0.005; floor 0.016 | > 0.5 and < 0.15 | yes (on the line) | Target right. 0.506 is luck; true-root share 0.585 means 41% of core words replaced within ~1.5 kyr on average across species, faster than Swadesh's 86%/kyr (~0.65 expected). The pooled figure hides 0 shared roots for aarakocra at 5 kyr. Report per species. |
| scholars' horizon (human) | 13 kyr (all 13; clade 20) | 6-10 kyr | no | See below: mainly the **measure**. |
| language shift happened | 399 shifts, 83 living lects off their descent | > 0 | yes | Target trivially met; 272 of the 399 are re-shifts (section 9). Count first shifts per deme. |
| long generations change less | humans 22.1 rules/kyr, long-lived 6.1, ratio 3.6 | long-lived < a third | yes | Right, and honestly met; note the wave makes dragons 5x, not 15x, slower. |
| hubs simpler, isolated richer | 1.67 vs 2.41 | hubs < isolated | yes | Direction right, but with a median of 2 live grams per lect the scores are near the floor; one seed. |

**The horizon.** Human pairs by depth: 0-9 kyr all bins pass; 10-11 kyr 3 pairs (2 pass); 12-13 kyr 35 pairs, 57% pass
(blind share 0.068, true-root share 0.064); 13-14 kyr 13 pairs, 0%. So the reading rests on one bin of 35 pairs that sits on
the 50% line, which calibration.md already notes flips between 11 and 13 between runs. Three measurement problems: (1) the 35
pairs are not 35 observations: they come from one or two old splits (every lect of one clade against every lect of the
other), so the horizon is decided by one or two tree nodes; test **splits** (clade against clade, e.g. median pair per
node) instead of pairs. (2) Edit distance under 0.45 is far looser than the comparative method, which needs recurring
correspondences, not lookalikes; in a run where every word is `ʔV˦CV˨`, two unrelated words pass 0.45 easily, and the
per-pair chance level (0.012 mean) only partly corrects for that. (3) At 12-13 kyr the true-root share is genuinely 6.4%,
about 2.4x Swadesh's expectation (0.86^24 = 2.7%): within-family borrowing, re-shift substrate and the slow tail of core
words keep roots alive. **The rates are not the lever**: calibration.md shows RATE_SCALE 4 > 5 left the horizon unchanged,
and the speed-up already costs young sisters their intelligibility (section 6). The 6-10 kyr target is right for "what a
comparativist could prove"; fix the measure (per split, correspondence-based or a stricter distance), then bring
RATE_SCALE back down (2-3) and re-calibrate the lexical tail.

## 9. Defects visible in the data

**Convergence (the biggest).** In the protos, ʔ is not among the six commonest word-initial sounds (k leads with 10%); in the
living lects **33% of core words begin with ʔ** and ʔ is the commonest segment overall (29,903 tokens; the next, l, 9,259),
in every species (dragons 28%, elves 31%). Plain p, t, k drop out of the top twelve. Causes in the log: ʔ-prothesis S042
fired 8,685 times, t > ʔ S038 2,418, final stops > ʔ ~1,000, against one ʔ-removing rule (glottal coda > tone, 1,369);
ə-epenthesis S124 + S123 + cluster epenthesis 18,823; h-loss 6,693; back harmony 15,059. Rules re-fire: a lect's most-repeated
rule fires a median 6 times, 90th percentile 44, maximum 147 (back harmony in aarakocra d23); 245 lects ran harmony 20+ times.
Coined words are then built from the eroded inventory, which feeds the loop.

**Inventories.** Five largest living: d298 dragonborn 45 C / 20 V (`ɡʷʰʱ ȡʰʱ dʰʱ bʰʱ n‼ r‼` and growled vowels e‼ a‼ i‼ ɨ‼);
d473 orc 45 / 20 (`ɢʷʰ qʰ ɴ ɲʼ` and a doubly-lowered `ʊ̞̞`); d484 human 45 / 20 + 3 tones (`ȴ ȶ ȡ kʷʰ ɡʷʰ ɟʰ cʰ dʼ tʼ ɡʼ kʼ`); d89 gold
dragon 44 / 20 (`dʒʰ tʃʰ l‼ r‼ j‼ ɾ‼` and seven growled vowels); d224.2 dragonborn 44 / 20 (`ɡʷʼ dʷʼ ɟʷʰ` and `y ø ø̞ ɶ œ`). 19
lects sit at the 45-consonant cap; living quartiles 21/27/34. The cap hides the problem rather than solving it (14,241 merge
events, one merging 28 vowels at once). Malformed segments: `ʰʱ` (aspirated and breathy at once) all over, `ʊ̞̞` and `ɞ̞̞`
(diacritic doubled).

**Feature braces.** None in lexicons; **254 in the file**: 214 in snapshots (e.g. d154), 16 in etymology nodes, 3 in
inventories (d423), 2 in paradigms (d711), the kind seen is `m{retroflex=1}` (d551 `mĩ˦˨mprə̃˦m{retroflex=1}fu˦`), a labial
nasal handed a retroflex place by `assimilation.nasal_place`.

**Tone bookkeeping.** 407 of 573 living lects have tone letters on their words (median 75% of words) but an **empty tone
inventory**; typology says tone "yes" for only 162. Tonogenesis marks words without phonemicizing tone (d587, d185).

**Words.** 0 empty forms. 627 words over 12 segments, up to 19: d748 SEE `tsə˦lɜ˨ɲəd̪ʰə˨ɹɜ˦n̪əɗə˨rə˦lɜ˨ɨ˨`, d128 IF, d821 ROAD,
d792 SISTER (all coinages or compounds). Runs of one vowel (`ɜ̠ɜ̠ɜ̠ɜ̠ə̠`) are not repaired. **10.6% of all words share their form
with another concept** in the same lect (I = WE in d389 and d185; EAT = TREE in d587; BEAR = DEER in d127.1); real languages
tolerate a few percent. Replacement sources are skewed: across living lexicons the latest step of a word is a coinage 64,618
times and a derivation 40,193 times, against intended weights of 0.15 and 0.35, because every derive/compound/taboo that
makes a homophone falls back to a coin; numerals and pronouns are replaced by coinages (TWO in d587 at 5.0 kyr).

**Spelling.** 29.6% of living words' house spellings contain raw IPA (ɜ 20.6k, ə 15.2k, ɛ 10.8k, ɘ 10.6k, ɨ 9.7k, the
retracted-diacritic ◌̠ 59.7k): ‹tə̟́'bə̟̀›, ‹'ɜ̠́'ɜ̠́ɜ̠›. 1,176 spellings stand for two different IPA forms in one lect (e/e̞, a/ɐ).
`romanization_failures` is empty, so these are not errors the speller noticed: it has no letter for central and retracted
vowels.

**Shifts: 399 is about three times too many.** They fall on only **104 demes**; **272 are re-shifts** where the old lect is
already in the ruler's family, triggered by the same still-active takeover. Kobold deme 435 "shifted" 13 times, every 0.5-1
kyr from 7.0 kyr to now, alternating between rulers d507 and d570.x, each time re-running substrate transfer and accent. The
gap between a deme's successive shifts has a median of 0.5 kyr. By kind: takeover 246, swamp 146, trade 6, elite 1 (one
elite shift in 20 kyr of conquest is too few for a designed trigger). Real first shifts:
about 127, still a lively history.

**Koine: 0 entries.** calibration.md explains it: koine is only "a sound hard for the city majority", and every mixed city
in a24559 is humans with human-voiced peoples. That is a spec gap, not a data quirk: koineization is above all levelling
among related dialects in a mixed town (dropping marked variants, simplifying), which should fire in human-only cities too.

**Food routes.** 172 routes; only 1 starts "tamed here", 108 start "first known here", so most routes are cut off from the
crop's real origin, and maize has 8 independent names (8 routes). 9% of hops show a donor form that cannot have produced the
receiver's (alliums: triton *saɡʱe̞sə* > human *nɐ˧kʰə˧nə˧*; d562 > d416.7 maize hop from a word d562 never had in that route).
Hop chains run 10+ deep inside one 0.5-kyr frame.

**Other.** 547 "languages" for 573 living lects: LANG_SHARE 0.7 almost never holds, a symptom of section 6. `lects[].stats`
is null for protos (fine). The shifted deme's share record keeps a dead lect at 29% (section 3).

## 10. Fix first (ranked)

1. **Stop the convergence** (`planet/language/rules.py`, `lect.py` rule draw, `lexicon.coin`). Make a rule's draw weight
   depend on how many words it would change (no re-firing on a handful of new inputs), cap re-draws of one rule per lect per
   few kyr, add the counter-moves real languages have (initial ʔ loss, vowel coalescence and contraction, syncope making new
   clusters, fortition of glides), and let `coin` build words from the lect's declared shapes and proto-era segment frequencies
   rather than its eroded current inventory. Judge with: share of ʔ-initial words, labial share by species, top-20 segments
   of living lects vs PHOIBLE (a living-lect version of check 1).
2. **End the re-shift loop** (`history.py`/`lect.py` shift step). A deme that already speaks a lect of the ruler's family
   stays put; the trigger then drives borrowing and levelling, not a new shift. Restrict substrate to genuinely local terms
   (`lexicon.local_concepts` and the concept table's `local` flag: no Swadesh-100 items). Keep a minority old lect alive while
   its share is above, say, 0.2.
3. **Re-weight word replacement** (`lexicon.step`, around the source draw and the homophone fallback). When derive/compound
   clash, try another non-coin source or accept the homophone; protect numerals 1-5 and pronouns; and decide the per-generation
   clock for 5-12-year species (aarakocra and kobolds lose everything in 5 kyr). That last is a judgement call for Daniel:
   per-generation as now, or per-generation with a floor in years.
4. **Fix the horizon measure, then lower RATE_SCALE** (`families.horizon_pairs`, `_horizon`, `intelligibility`). Score
   splits, not pairs; require correspondences or a stricter distance; then bring RATE_SCALE back toward 2-3 and re-check sisters,
   young-lect intelligibility (should be ~0.8 at 0.5 kyr) and continua.
5. **Output hygiene** (`inventory.py`/`lect.py` tone inventory, `rules.py` assimilation that yields `m{retroflex=1}`,
   `percepts.to_ipa` for `ʰʱ` and doubled diacritics, `romanize.py` letters for central and retracted vowels, `grammar.py` gram
   forms reappearing from zero, proto word shapes in `inventory.py`, food-route hop forms and origins in `history.py`, a koine
   rule for same-voice mixed cities).
