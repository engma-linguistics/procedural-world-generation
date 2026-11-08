# Demo material: run a24559, final languages.json (2026-11-04, shipped run)

Extracted from `runs/a24559/languages.json` (117 MB; 1,194 lects, 623 living, 596 languages, 261 true families, 159 shifts,
85 food routes, 5/6 checks pass, human horizon 11.0 kyr against a 6-10 target). Every number was computed from the file; the
scripts are in the session scratchpad, not the repo. Lect ids and words differ from the previous run, so all samples are new.
IPA in plain text, book spelling in ‹›. Tags in cognate tables: `=` inherited from the family's proto; `N` a root coined
inside the family; `L` a loan from outside the family; `+d` derived or compounded on the way; `~` a meaning shift on the way.

### INVENTORIES

**PHOIBLE reference** (`phoible_inventory_sizes.tsv`, 2,175 inventories): consonants median 21 (IQR 17-27), vowels median 9
(IQR 6-12), tones median 0 (IQR 0-0).

| proto | speakers | C | consonants | V | vowels | tones, syllables |
| --- | --- | --- | --- | --- | --- | --- |
| p306 | human | 26 | p b ɓ f v m t d tʰ ts dz s z ʃ tʃ n r l ȶ ʈ j k ɡ ŋ w h | 10 | i e ɛ a ɔ o u ɨ aː ɔː | 5 tones; up to CCVC; stress penult |
| p255 | kobold | 21 | β tʰ d ts s n l ɻ tʃ dʒ j k kʰ ɡ x ɣ ŋ χ ʔ h hʲ | 10 | i iː e̞ ẽ̞ ə a aː ɑ o̞ u | no tone; up to CCVC |
| p222 | aarakocra | 24 | m b t d s z r r‼ l tɬ ɮ ȶ ʈ ɖ tʃ ɟʝ j k kʰ ɡ w ʔ h ʕ | 6 | i iːᴖ ɪ ɛ o u | 5 tones; up to CCVCC; stress final |

All three sit inside PHOIBLE's consonant IQR. **Avian labials are scarce, as ruled:** p222 has only m and b (p306 has six);
over all protos the median is 6 labials for humans, 3 for aarakocra, 2 for kobolds and dragons. **Second-source and harsh
segments are there and fade:** 52% of aarakocra protos carry a ᴖ segment and 57% a harsh one; among living aarakocra lects 24%
and 36%. Kobolds fall from 72% to 43% harsh; dragons stay at 99%. Humans and elves have none.

**Living inventories by species group** (quartiles q1 / median / q3):

| group | living lects | consonants | vowels | tones |
| --- | --- | --- | --- | --- |
| human | 104 | 18 / 22 / 27 | 8 / 10 / 12 | 0 / 4 / 5 |
| dragons (10 kinds) | 118 | 18 / 23 / 28.8 | 7 / 9 / 12 | 0 / 0 / 0 |
| elves (elf, drow, sea elf) | 25 | 16 / 23 / 27 | 7 / 8 / 8 | 0 / 0 / 4 |
| kobolds | 53 | 21 / 23 / 26 | 7 / 9 / 11 | 0 / 3 / 4 |
| aarakocra | 25 | 17 / 21 / 27 | 7 / 8 / 9 | 3 / 4 / 5 |

**The inventory blow-up is gone.** All living lects: median 22 C and 9 V, PHOIBLE's own medians (previous run 28 and 13).
20% of living lects are above PHOIBLE's upper quartile for consonants (was 51%) and 20% for vowels (was 46%); 36% are above it
on one or the other. Only 1.4% exceed 1.25 times their proto's size (the cap is soft; the largest ratio is 1.31). **Tone is now
in 48% of living lects** (was 98%; protos 24%; real languages about 40%), and it sits where it should: dragons and elves mostly
toneless, aarakocra and humans mostly tonal.

### SAMPLES

**(a) Human family p306** (proto 20 kyr; 35 living lects, 14 of them spoken by halflings and orcs after shifts). Five human
lects of the d604 branch and one of the d774 branch. Split dates: d604-d856 1.5 kyr; d604-d702 12; d604-d691 13; d604-d666 15;
d774 against all the others 19.

| concept | proto p306 | d604 | d856 | d666 | d691 | d702 | d774 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WATER | pjo˨˦dzku˨ | iː˨vːə˨tʰ ‹ìivvë̀t› =+d | i˨və˨tʰ ‹ìvë̀t› =+d | ɡa˦˨ɡ ‹gâg› N | ʒɛ˨˦ɪ˨ʃ ‹zhẹ̌ị̀sh› = | ʔa˨i˨ɹi˨bʱ ‹'àìrìb› = | ʔa˨i˨ȶ ‹'àìť› N+d |
| FIRE | tja˦˨brɔ˧r | ʁːu˨˦ʈv ‹ġġǔṭv› N | ʁu˨˦ʈe˨ ‹ġǔṭè› N | kxu˧ ‹kxu› L | i˨˦ ‹ǐ› N | ʔɛː˨bʱi˨ ‹'ẹ̀ẹbì› = | ʔə̃ː˧ŋi˧ə˧f N+d |
| HAND | ȶɨ˧ | ȶi˧ ‹ťi› = | ȶi˧ ‹ťi› = | lɛ˨˦ʒe˨i˦˨ N+d | li˨˦ʔa˦˨ɓu˨ N+d | ȶa˨˦ ‹ťǎ› N~ | ɣʷɪ˦ ‹ghwị́› N |
| EYE | daː˦˨p | ʔe˨ə˨ʃ ‹'èë̀sh› = | ʔɛ˨ə˨ʒ ‹'ẹ̀ë̀zh› = | mi˨ɛ˨ɫ ‹mìẹ̀ll› =~ | ʔɛ˨ɪ˨ʃ ‹'ẹ̀ị̀sh› = | ʔi˨lə˧ɘ˨lɛ˦˨ L+d | li˨˦f ‹lǐf› =+d |
| ONE | ŋa˧ | ʈru˦˨ŋĩ˨˦ŋtʰu˦˨ɓ N~ | li˨˦ɲ̟ʒe˦f N+d | ɲ̟ʒe˨˦ĩ˨˦ N | li˨˦ɛ˧ ‹lǐẹ› L+d~ | la˦ ‹lá› N~ | si˦ ‹sí› N |
| TWO | e˨ȶa˨ | ʒə̃˦mː ‹zhë̃́mm› N~ | ʒə˦me˧ə˨˦ N~ | ɡɣʒe˨˦ ‹gɣžě› N | ʒʒi˨ʃ ‹zhzhìsh› N | ʔi˨ȶ ‹'ìť› = | li˨˦ ‹lǐ› =+d |
| STONE | mo˨˦mɔː˨tʃ | ʈə˨˦ə˨ʒi˦ə˦ɓ =+d | ʈə˨˦ə˨ʒe˦ə˦ɓ =+d | ʔĩ˧ɛ˨ɓa˨ʒe˨i˨ɫ =~ | ʔu˧nʷu˧u˧lɲi˦ L+d~ | ʈi˦ə˨ɘ˨mi˨ =+d | la˧u˧ɹ ‹laur› N+d |
| TREE | mi˦so˦˨vʃa˧d | ʈə˨˦bʱə˨iː˦˨mːə˨ʃ =+d | ʈə˨˦bʱe˨hɹə˦ɲi˨˦ =+d | ʈi˦ʔã˦˨ĩ˦˨ɲu˨ =+d~ | ʈi˧ʔa˧i˧ɲu˧ =+d~ | ʔi˦ʔaː˦fɛ˨ N+d | mu˨ʒi˦˨f N+d |
| NIGHT | ze˦˨m | hru˦˨ʁːə˨˦ʃ N~ | ɛ˧ə˧ ‹ẹë› L | ʒʒe˨˦i˨˦ =+d~ | ʈvi˦˨ ‹ṭvî› =~ | ʈɛː˦xi˨x =~ | ʈʒi˦˨ ‹ṭzhî› =~ |
| DOG | kɛ˦ru˨˦ | ɡi˨ ‹gì› N | mi˧lʷə˦ N+d | ʔĩ˧ɲɛ˧ɓa˧ɹi˧ =+d | vri˨˦ ‹vrrǐ› N | mu˧ŋɘ˨˦ȶə˦ʁ N+d | mi˧la˧ĩ˧m N+d~ |
| FISH | su˨˦me˨˦w | lĩ˧ŋːə˦ʃ L+d | li˧ŋə˦ʃ L+d | ɲ̟ʒi˨˦ ‹ɲ̟žǐ› N | mu˧ɛ˦˨mi˧ N+d | mi˨i˨x ‹mììkh› N | i˨ ‹ì› L+d |
| I | ŋa˨˦ɡ | na˦˨ɡla˨ɡu˧ N | ɲi˨˦ ‹nyǐ› =~ | ɲ̟ʒi˨ ‹ɲ̟žì› = | ʒrɛ˦˨mtʰi˨˦vi˧ɦ N | ʔi˧f ‹'if› =~ | vʒi˨˦f ‹vzhǐf› N~ |
| THOU | sɨ˧vɔ˦p | ɲi˨˦ ‹nyǐ› =~ | ɲi˨˦ ‹nyǐ› =~ | ʔĩ˨vɛ˧ N~ | ʔi˧ ‹'i› = | ʔu˧ ‹'u› L | ʔə˦˨ɪ˨ə˦f N~ |
| WE | tʃɔ˦ | ɲi˦˨ ‹nyî› N~ | ʁə˧ ‹ġë› L~ | tʰʒi˦˨ ‹thžî› N | mi˧mʊ˧ ‹mimụ› N | bʱwʒi˧ ‹bwzhi› L | ʒi˨ ‹zhì› N~ |
| EAT | be˧bwo˧ | ʒi˧ ‹zhi› N~ | ʒi˧ ‹zhi› N~ | ɲĩ˧nĩ˨ N | tʰi˦ ‹tí› =~ | mu˧ɫ ‹mull› N | li˧f ‹lif› L |

Correspondences that can be stated. **d604 : d856** (1.5 kyr, 59 of 100 core roots shared; shared new coinages FIRE ʁu˨˦ʈ-
(2.0 kyr), TWO ʒəme- (3.5), EAT ʒi (11.0)): d604 ʃ = d856 ʒ (7 tokens: ASH, EYE, NAME, RAIN ...); d604 long consonants = d856
short ones (ɖʱː : ɖʱ in ASH, HEART, KNEE, LIVER; ʁː : ʁ in BLACK, EGG, FIRE, SEED; vː : v; ŋː : ŋ): d856 degeminated; d604 long
vowel = d856 short (iː : i in EGG, SMOKE, WATER); d604 nasal vowels = d856 oral ones (ə̃ : ə, ĩ : i): d856 denasalized.
**From the proto:** *d- > ʔ and *-p > ʃ (EYE *daːp > d604 ʔeəʃ, d691 ʔɛɪʃ; ʒ in d856, f in d774); *ȶ is stable (HAND *ȶɨ >
ȶi in d604 and d856, ȶa in d702; TWO *eȶa > d702 ʔiȶ); *z- > ʈ (NIGHT *zem > ʈvi, ʈɛːxix, ʈʒi in three lects 12-19 kyr
apart); *ŋ before front vowels > ɲ (I *ŋaɡ > ɲi, ɲ̟ʒi). Deeper pairs share little (median true share at 12-15 kyr about
0.1). **What a linguist would stop on:** ʒ everywhere (TWO, NIGHT, FISH, I, WE, EAT in several lects; see DEFECTS); THOU = I in
d856 (ɲi˨˦ for both), THOU = WE in d604 (ɲi˨˦ / ɲi˦˨ differ only in tone). The old lɨ˨˦- prefix that faked cognates is gone (0
words in this family start with lɨ).

**(b) Elvish family p301** (elf and drow; proto 20 kyr; d551 continues the proto in place, d835 budded 3.5 kyr ago, d688 13.5,
the drow d689 12.0 and d725 from d689 at 10.0). Elves keep half their core after 20 kyr, so this is the most readable family
in the run.

| concept | proto p301 | d551 elf | d835 elf | d688 elf | d689 drow | d725 drow |
| --- | --- | --- | --- | --- | --- | --- |
| WATER | ɭə˨nmʷu˦cĩ˨ | ɲɨ˨vũ˨mɨ˨dʒi˧ʔu˨ N | ɲɨ˨vy˨ɲɨ˨ʒi˧ʔo˨ N | ɭə˨ɲĩ˨mĩ˦ɲɨ˨ = | ɭə˨nɨ˨mɨ˦ɲɨ˨ = | ɭə˨nɨ˨mɨ˦ɲɨ˨ = |
| FIRE | dʒu˦ci˦˨m | dʒu˦ɟu˦˨ ‹júgyû› = | ʒu˦bʱu˦˨ ‹žúbhû› = | ʒũ˦ɲʷu˦˨ = | ʒu˦ɲu˦˨ ‹zhúnyû› = | ʒu˦ɲu˦˨ ‹žúnyû› = |
| HAND | βlu˧ŋ | ku˨wi˦dʒu˦˨ =+d | ky˨hi˦ʒu˦˨ =+d | vu˨lũ˧ŋɨ˨ = | vu˨lu˧nɨ˨ = | vu˨lu˧nɨ˨ = |
| EYE | mu˧ŋkʰə˨m | mũ˧ŋu˨ku˨ = | mu˧ŋu˨bʱo˨ = | mũ˧ŋʷu˨pʰo˨ = | mu˧ŋu˨ɡʱo˨ = | mu˧ŋu˨ɡo˨ = |
| ONE | mi˦n̪ | tʃi˨i˦ ‹čìí› =+d | ʃi˨hi˦ ‹šìhí› =+d | mĩ˦n̪ɨ˨ = | mi˦n̪ɨ˨ = | mi˦n̪ɨ˨ = |
| TWO | rũ˦˨ti˨m | hĩ˦ɲi˨ʔu˦ =+d | hi˦ɲi˨dʱu˦ =+d | ɹu˦˨dʱu˨ ‹rûdhù› = | ʁu˦˨dʱu˨ ‹ġûdù› = | ʁu˦˨du˨ ‹ġûdù› = |
| STONE | fe˦lu˦˨ɣə˦˨ɲ | tʃe˨dʒĩ˦ŋi˨i˦ =+d | ʃe˨ʒi˦ŋi˨hi˦ =+d | ʃe˨ʒĩ˦ŋi˨ʒi˦ =+d | e˨ʒi˦ŋi˨ʒi˦ =+d | ʃe˨ʒi˦ŋi˨di˦˨mi˨ɲi˨ =+d~ |
| TREE | ɲju˦ɳȶe˨ | he˦˨he˦˨ȶe˧ N | he˦˨he˦˨ȶe˧ N | ʃe˦˨e˦˨ȶe˧ N | e˦˨bʱe˦˨bʱe˨ N+d | ʃe˦˨be˦˨ȡe˧ N |
| NIGHT | vi˨kʷlu˧ɲ | vi˨dʒi˨lĩ˧ɲɨ˨ = | vi˨ʒi˨li˧ɲɨ˨ = | vi˨ʒi˨lĩ˧ɲɨ˨ = | i˨i˦ ‹ìí› =+d | vi˨ʒi˨li˧ɲɨ˨ = |
| DOG | su˨ɲ | ʈu˦˨wu˦ =+d | ʈu˦˨hu˦ =+d | ɾe˧i˨ ‹reì› N+d | ɡʱu˧ ‹gu› N | ɡu˧ ‹gu› N |
| FISH | ju˨m | dʒu˨ ‹jù› = | ʒu˨ ‹žù› = | ʒu˨ ‹žù› = | ʒu˨ ‹zhù› = | ʒu˨ ‹žù› = |
| I | ʃɭə˦˨ | hu˨ɭu˦˨ = | hu˨ɭo˦˨ = | ʒu˨ɭo˦˨ = | u˨ɭo˦˨ = | ʃu˨ɭo˦˨ = |
| THOU | nĩ˧ri˨n | vũ˧ɲɨ˨ =~ | ɲi˧ri˨nɨ˨ = | vũ˧ɲɨ˨ =~ | ɲi˧ʁi˨nɨ˨ = | ɲi˧ʁi˨nɨ˨ = |
| WE | di˧ | dʒi˧ ‹ji› = | ʒi˧ ‹ži› = | ʒi˧ ‹ži› = | ʒi˧ ‹zhi› = | ʒi˧ ‹ži› = |
| EAT | βu˦ | vu˦vu˨lu˦ =+d | vu˦vu˨lu˦ =+d | vu˦vu˨lu˦ =+d | vu˦vu˨lu˦ =+d | vu˦vu˨lu˦ =+d |

Correspondences, all regular: d551 dʒ = ʒ in the four others (FIRE, NIGHT, FISH, WE, STONE: *j, *d > dʒ, then dʒ > ʒ outside
d551); d551 tʃ = d835 ʃ (ONE, STONE); d551 w = d835 h (HAND kuwidʒu : kyhiʒu, DOG ʈuwu : ʈuhu); d551 u = d835 y after k (HAND).
**Drow : drow** (d689 : d725, 10 kyr, 63 roots shared): d689 breathy stops = d725 plain (bʱ : b 9 tokens, ɡʱ : ɡ 7, dʱ : d 5):
d725 lost breathiness; and d725 has ʃ or f where d689 has nothing (ʃ: BLOOD, CLAW, DRY; f: HEAD, MOON, SUN). **From the proto:** *r >
ʁ in the drow lects, ɹ in d688 (TWO, THOU); final *-m, *-ŋ, *-n > paragogic -ɨ (HAND *βluŋ > vulunɨ, ONE *min̪ > min̪ɨ, THOU
*nĩrin > ɲirinɨ); *β > v (HAND, EAT); *kʰ in EYE gives k, bʱ, pʰ, ɡʱ, ɡ across the five, a textbook set. Shared new coinage TREE
(17 kyr, all five), DOG ɡu (11 kyr, both drow). **Winces:** EAT vu˦vu˨lu˦ is identical in all five lects after 3.5-13.5 kyr of
separation (an old derived form that none of the sound changes touched); HAND, ONE, TWO in d551 and d835 are derived forms
that replaced inherited words the other three keep.

**(c) Four etymologies.**

1. **SMALL in d507 (human), 17 steps, three loans.** 20 kyr blue-dragon proto p28 *kɛje‼ː* 'vomit' > 19.0 d48 *dzaːja‼* > 14.5
   VOMIT + 'do' = *pɛdzaːja‼* 'carry' > 9.5 **borrowed by halflings** (d479) *pʰædʒaːʒu* > 6.5 CARRY + 'agent' = 'male person' >
   4.5 MALE PERSON + FRIEND = 'man', then MAN + HUSBAND = *ʒiʒilũɲpʰæ* 'person' > 3.0 PERSON + CHILD (DESCENDANT) = *æiʒiʒi*
   'child' > 2.0 **borrowed by halflings** d636 *aiʒiʒi* > 1.5 **borrowed by humans** d507 *a˧i˧ʒi˧ʒi˧* > 1.0 CHILD + 'like' =
   *ʔĩ˨˦a˧i˧* 'small' > now *ʔĩ˨˦e̞˧e̞˧* ‹'ĩee›. 'Child-like' for 'small' and 'carrier' for 'man' are good; vomit > carry is not.
2. **Foxtail millet, by food route** (route `crop:foxtail_millet`, "first known here" at hobgoblin d514, 7.0 kyr; 65 hops).
   The hobgoblins made the word as TREE + FLOWER, *ʔɛ̃ɳɛʔyʒə*, from a 'tree' that was itself GRASS + EAT. The chain to the gold
   dragons: 7.0 leonin d456 *ʔa˨ɲa˨ʔi˨ʒe˨* (nasal vowel and retroflex lost, tones added) > 6.5 hill giant d25 *ʔã˨ɲa˨ʔi˨ʒ* >
   6.0 bronze dragon d62 *ʔaɳaʔiʒ* (tones dropped) > 4.0 triton d767 *kaɲakiʒɨ* (ʔ heard as k) > 3.5 *haɲaiʒ* > 3.0 brass dragon
   d51 *ʁaɲaiʒ* > 2.0 gold dragon d88 *ʁa˨ɲa˨i˨* ‹ġànyàì›, its present word. Six hops, seven peoples, and every hop is in the
   receiver's own etymology. But the same route's hop to aarakocra d530 (2.0, *ʁa˨ɲa˨i˨*) does not match d530's present word
   *pɛː˨˦ʈaː˦ɲi˨ʒi˦˨*: 27% of hops into living lects are like that (see DEFECTS).
3. **A substrate survivor: STONE in d148.1** (dragonborn now speaking a human language; see (d)). 20 kyr dragonborn proto
   p120 *ʔaɖkiːʈ* 'cloud' > 19.0 CLOUD + WHITE = 'fog' > 17.5 FOG + STAR = 'smoke' > 11.5 SMOKE + FOG = 'dust' > 11.0 DUST +
   'place' = *lu‼ɫʔəɖʁə* 'land' > 8.5 LAND + GREEN = *luʔəːkuɫləː* 'stone' > 2.5 *lɛʔ* > 2.0 **kept through the shift** as
   *ɹɛʔ* (accent: the human lect's l-less ear) > 0.5 *ɹɛ* ‹rè›. Each step is a real compounding type, but 'green land' for
   'stone' is a wince. FISH, DEER, LAKE and 'cattle' in the same lect are substrate too ('cattle' = substrate ANIMAL + LONG).
4. **A compound: MARSH in d806.1 (human).** p307 *wuneɡ* 'water' > 10.0 d562 *ɓʒiəʔ* > 3.0 d144.1 *ɗi˨*; WATER + YELLOW =
   *ɗi˨ɲĩ˨ɲ* 'rain' > 1.0 RAIN + LONG = 'water' (a renewal), then WATER + EARTH = *ɗiː˨ɲi˨vyː˨ʒɜː˨ɗ* 'marsh'. Water-earth for
   marsh is good. Also good: BERRY = TREE + SEED in d787. Odd: SOUTH in d584 is NORTH + WARM, where 'north' was once 'south'
   (SUNRISE + 'place'), and DAY = THINK + 'thing' in d570.1.

**(d) One shift in full: deme 148 (dragonborn 4, the west of Trojanel) to human, 2.0 kyr ago.**
- **Trigger:** humans of deme 791 took 76 dragonborn sites, a town or city among them, from 2.2 kyr ago (`takeover`, strength
  1.0, held to now; source settlements.json holders).
- **Shares of the rulers' lect d791 among the dragonborn:** 2.5 kyr 0.23, **2.0 kyr 0.53: shift** (another human lect, d584,
  0.05). After the shift the old dragonborn lect keeps 0.38 (1.5 kyr), 0.31, 0.25, **0.21 now**; d584 rises to 0.14.
- **The old lect lives on:** d148 is alive, flagged `minority` (one of 50 minority lects in the run).
- **Old d148 (dragonborn, family p120):** 20 C `c h ʃ l ʒ w ɹ ʔ ʁ ɫ ɖ ʈ k χ t ɾ qʰ s ts lː`, 10 V `u ɛ i ɪ ɛː e i‼ a ĩ eː`: no
  nasal consonants, one labial (w). **New d148.1 (family p314):** 16 C `vʲ ŋ ʁ ʃ χ ɲ̟ ʒ kx ɹ ʔ ɲ k f n pʷ fʲ`, 15 V; the rulers'
  d791 has 17 C and 13 V.
- **Core words, old / new / rulers' now:** WATER ʔiliʒaiʃ / kxɛ̃ɲiʒĩɲ̟ʒṳ / ɛfʔɛ̃ɲi; FIRE ʒiɛɾɛʃ / ŋĩːɹĩn / vũvĩnũ; HAND i / i /
  i; EYE ʁʒi / ŋṳʒiʒɛːʒi / ŋṳʒiʒɛʒi; I ʈɛʃ / kxiɐ / kxiɛ̠; WE ʈɛʃ / ɹaiχ / ɹɛiʁ; NIGHT ʒʒi / kxuɹ / kxũn; EAT kʒi / pʷɹĩnɛ / ũɣã.
  EYE, I, WE, HAND, NIGHT match the rulers'; the new WATER is the substrate word LAKE + RAIN; ONE ʔaɹfeɹu is the rulers' 'few'
  that shifted to 'one' at 1.0 kyr.
- **Substrate kept:** 65 concepts: landscape (HILL, MOUNTAIN, RIVER, LAKE, SEA, FORD, PASS, COAST, MARSH ...), wild and farm
  animals (DEER, WOLF, BEAR, horses, cattle, goats, fowl), FISH, BIRD, DOG, TREE, STONE, and the crops.
- **Accent (new sound heard as old):** m, n > ɹ; pʷ > k; v, ɣ, ɡɣ > ʁ; fʲ > x; nasal vowels > oral (ã > a; õ, ũ > u; ỹ > ĩ);
  i̤ > i. Sensible for speakers with no nasal consonants and almost no labials; later borrowing restored n, ŋ, f.
- **Calque from dragonborn:** a diminutive (the rulers have none).
- **Wince:** the old lect has one word ʈɛʃ for both I and WE, and a homophone share of 0.19 (median for dragonborn 0.13).

**(e) Two paradigms from living lects** (`paradigms` per lect; history from the snapshots' `grams`).

*d690 (human 48, the west of Simath, SVO; 56 cells, the richest human lect).* Verbs are all prefixing:

| verb | lemma | 3SG | 2SG | 1SG | 1PL | PAST | FUT | PAST.1SG | REFL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GO | ɲi | ʔiɲ | ʔa | ʒiɲi | miɲ | ɓi | ɲɜ̠ɪɲ | ʒiɓɜ̠ɪɲ | ʒɑ̟ |
| EAT | ŋaiɡʱaaɜ̠ɪn | ʔi- | ʔa- | ʒi- | mi- | ɓɜ̠ɪ- | ɲɜ̠ɪ- | ʒiɓɜ̠ɪ- | ʒa- |
| SEE | nʊŋim | ʔi- | ʔa- | ʒi- | mi- | ɓɜ̠ɪ- | ɲɜ̠ɪ- | ʒiɓɜ̠ɪ- | ʒɑ̟- |
| GIVE | maɡʱ | ʔimːaɡʱ | ʔamːaɡʱ | ʒimːaɡʱ | mimːaɡʱ | ɓɜ̠ɪmːaɡʱ | ɲɜ̠ɪmːaɡʱ | ʒiɓɜ̠ɪmːaɡʱ | ʒamːaɡʱ |

GO is suppletive-looking: its monosyllabic stem fuses with every prefix (11 of 13 cells marked irregular; 2SG is just ʔa, PAST
just ɓi). GIVE geminates its m after any prefix; REFL is ʒɑ̟- before back-vowel stems (SEE) and ʒa- elsewhere: real, statable
allomorphy. Nouns: one class suffix, CLASS:3 -m (WATER ʁaɓ, irregular). Gram paths:
- PAST from YESTERDAY: *biki* (20 kyr, clitic) > *bihi* > *bi* > *ɓi* (17.0) > affix (13.5) > *ɓəɪ* > *ɓɜ̠ɪ*. Attested type.
- FUT from GO: *ɲi* (14.5, free) > clitic (10.0) > affix (9.5) > *ɲəɪ* > *ɲɜ̠ɪ*. The go-future, attested; GO's own stem is ɲi.
- REFL from HEAD: *ʒänɨ* (10.5) > clitic (10.0) > *ʒɑ̟̃* > affix *ʒɑ̟* (5.0). Head-reflexives are attested (Basque, Fula).
- 3SG from HE/SHE/IT *ɨsrẽ* (20) > *ʔɨʁɨʁ* > *ʔɨ̃* (14.0, affix) > *ʔi*; 2SG from THOU (15.0) *ɜdʱɜ* > *ʔa*; 1SG from I *ʒe* (17.0)
  > *ʒi*; 1PL from WE *mi* (11.0). Agreement from free pronouns: attested.
- NEG *su* fused and died at 14.5, a new *ũk* (5.5) wore to *uf* and died at 3.5: the lect has no negator now.
- Defects: 1SG ʒi- and REFL ʒa- differ by one vowel; 3SG ʔi- and 2SG ʔa- likewise (that alone is fine).

*d726 (aarakocra 34, the north of Sothasor, family p204).* Nouns: WATER ɛ˨, COM **ɛ˦˨**-ɛ˨, DEF ɛ˨-**kʷɛ˨**, LOC
**hɛ˦˨**-ɛ˨; PERSON tɛ˦nŋo˦to˦ɾy˦; DOG ɻe˨ni˨; TREE ɳi˨ʒi˨ko˨. Verbs are all prefixing:

| verb | lemma | CAUS | REFL | 2SG | 1SG | IPFV | 2PL | 1PL | IPFV.1SG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GO | ka˦ɾe˦ | ʔe˦**h**a˦ɾe˦ | la˨**h**a˦ɾe˦ | ʔɛ˦**h**a˦ɾe˦ | ɻa˨ka˦ɾe˦ | ly˦˨ka˦ɾe˦ | tɾa˨ka˦ɾe˦ | ʔɛ˨**h**a˦ɾe˦ | ɻa˨ly˦˨**h**a˦ɾe˦ |
| EAT | tʃi˨ɻɛ˨ | ʔe˦- | la˨- | ʔɛ˦- | ɻa˨- | ly˦˨- | tɾa˨- | ʔɛ˨- | ɻa˨ly˦˨- |
| GIVE | ɣɛ˨i˨ʒi˨ʒa˨ | ʔe˦ɛ˨i˨ʒi˨ʒa˨ | la˨ɣɛ˨- | ʔɛ˦ɛ˨i˨- | ɻa˨ɣɛ˨- | ly˦˨ɣɛ˨- | tɾa˨ɣɛ˨- | ʔɛ˨ɣɛ˨- | ɻa˨ly˦˨ɣɛ˨- |

GO alternates k ~ h after vowel-final prefixes and GIVE drops ɣ after ʔ-prefixes: lenition frozen into the paradigm, but not
consistently (after ɻa˨-, ly˦˨-, tɾa˨- GO keeps k). Gram paths: FUT from GO (*ka˦ɾe˦* = the verb GO itself, a clitic at 0.0:
the go-future again); REFL from HEAD (*la˨o˨* 11.5 > *la˨* affix 7.5); LOC from BELLY (*hɛ˦˨*, 1.0, after three earlier LOCs
died); DEF from THAT (*kʷɛ˨*, renewed at 3.0); COM from FRIEND (6.0 > fused 1.0); IPFV from the PROG gram (3.0 > fused 0.0):
a progressive becoming an imperfective, attested; CAUS from DO/MAKE (*ʔe˦*, 12.5, fused 1.5). **Winces:** grammar churns (DAT,
PERF, PAST, NEG, 3PL all died in the last 1.5 kyr; 2PL renewed three times); 2SG ʔɛ˦- = AGENT ʔɛ˦-, and 1PL ʔɛ˨- differs only
in tone; the lect now has no negator.

**(f) Names.**

| people | endonym | book spelling | gloss | pattern | made from |
| --- | --- | --- | --- | --- | --- |
| firbolg | nʷomɪa | Nwomia | the hunters | E8 way of life | nwomi 'hunt' (coined 7.5 kyr ago) + -a, the plural |
| gnome | ãɲynaf | Anyünaf | the real people | E2 | anyüran 'people' (compounded 8 kyr ago) + naf 'real' (9 kyr) |
| goliath | ŋʷa˨i˨ŋi˨ | Ngwaingi | the river people | E4 | ngwaishi 'river' (once 'water') + -ngi, the plural |
| lizardfolk | i‼˨dʱːə˨ʔy˦ə˨ | Irhdde'üe | the snake people | E11 totem | irhddezhen 'people' + üeeh 'snake' (17 kyr) |
| tortle | ʔãɲiʔãʔy | Anyi'an'ü | the old people (first on Simath) | E7 | an'üü 'people' (3 kyr) + anyiza 'old' (1.5 kyr) |

| by -> of | exonym | book spelling | gloss | pattern | basis |
| --- | --- | --- | --- | --- | --- |
| orc -> triton | u˧ɛ̃˧ | Uen | the enemies (raiders) | X5 | tritons settled among orcs on 20 cells in 2 kyr; en 'enemy' borrowed from a blue-dragon lect |
| green dragon -> hill giant | dziɾa‼ɲiɗid̪ʱɨ‼ | Dzirarhnyi'didirh | the mutes | X3 | dzirarh 'mute' + people class |
| elf -> dragonborn | ɡʷʱuɭud̪ʱuɡʷʱomuɛʒi | Gwuḷudugwomuezhi | the strangers | X2 | ezhizhi 'stranger' + people class |
| drow -> tortle | ũ˨vo˦ŋi˨pʰɨ˨ | Unvongipï | the beaked ones (bird-mouths) | X7 body | 'people' + 'bird' + 'mouth' |
| red dragon -> frost giant | a‼ː˧ɫi‼˨ɓi‼ː˨ʒi‼˨ | Aarh-llirh'birhzhirh | the big ones | X7 body | 'big' + plural |

Place names, each with its chain:
- **River Ich'e'iliaw, 'the big river' (deme 77, copper dragon; P2, substrate).** Kobold d442: *hi˦˨e˦˨kɛ˨˦* 'big' (coined 8.5
  kyr) > *i˦˨tʃːɛ˨˦*; *slɪ˦a˦˨w* 'river' (7.5) > *hlɨ˦a˦˨w*; name *i˦˨tʃːɛ˨˦hɨ˨lɨ˦a˦˨w* > heard by the copper dragons, who came
  later, as *itʃʼɛʔɪlɪaw* (tones dropped, h > ʔ, long tʃː as ejective tʃʼ). The name is dated 20 kyr, its words 7-8.5.
- **Lake Aaïzha, 'the big lake' (deme 24, hill giant; P2).** Firbolg d197: SEA + 'little' = *ɛɑxʷy* 'lake' (6.0) > *ɛavi*;
  *həʒjɛh* 'big' (4.0) > *əʒɛ*; name *ɛaəʒɛ* > the hill giants' *aaɨʒa*. 'Little sea' for 'lake' is good.
- **Sea Finywizinwu, 'the cold sea' (deme 787, human).** p279 *e˨mt̪a˨b* 'sea' (20 kyr) > 8.5 d493 *i˨n̪ʷo˨t̪a˦bʱu˨* > now
  *ĩ˨n̪ʷu˨d̪ʱa˦bʱu˨*; *fĩ˧ɲwi˦z* 'cold' (coined 0.0); name *fĩ˧ɲwi˦zĩ˨n̪ʷu˨*, both words clipped.

### CHANGELOG

**d691 (human 49, the west of Ratal; p306 > d561 > d604 (19.0) > d691 (13.0)).** 332 sound changes in 20 kyr (16.6 per kyr):
by cause effort 96, coarticulation 84, dispersion 61, perception 43, prosody 38, tonogenesis 10. 285 own, 47 adopted by wave
(24 from d666, 11 from d375, 5 from d604). 77 rules fired more than once ('rare sounds merged' 32 times). In order (`[dX]` =
adopted from lect dX; "rare sounds merged" left out):

- 19.5 (d561): ɨ˨ epenthesis; pt > tt; s lost finally; t > d /V_V; m lost finally [d467]; r > ɹ, s > ʃ before i, p t k > f θ x [d375]; l > ɫ [d381]; j > dʒ /#_ [d432]; d > ð, o > a unstressed [d485]
- 19.0 (d604): labialization before u, o; back harmony; final devoicing; sk metathesis; z > s; a > ɛ stressed open; ɡ > dʒ before front V; e, o > i, u before Ci; n > ɲ, ɡ > ɣ, nasal place assimilation [d375]; ruki [d580]
- 18.5: low tone before voiceless stop; j > dʒ /#_; final C lost; ɛ, ɔ > je, we stressed; kt > jt; w > ɡw /#_; p > b /V_V; aː > ɛː, d > ð [d375]; dʒ > ʒ [d466]
- 18.0: b d ɡ > p t k; nasalization before nasals; j > ʒ; ð lost /V_V; s > z /V_V; r > ɹ; k > h /V_V; k > tʃ; h lost
- 17.5: w after u; stops voiced after nasals; i, u > j, w before V; p lost; t > tʃ before i; kʷ > p; p > ɸ; l > w finally; u˨ epenthesis
- 17.0: dz > z; ts > s; eː, oː > iː, uː; p t k > pf ts kx initially; u > o before Ca; long vowels shorten; w > v; f > h; intervocalic voicing [d375]
- 16.5: tʃ > ʃ; u > y; voiced stops > breathy; s > ʃ before i; e > i before nasals; s > h; t > ʔ /V_V, finally [d375]
- 16.0: a > ɛ; m lost finally; y > i; n > ɲ; gemination; i˨ epenthesis. 15.5: ts > θ; θ > f
- 15.0: breaking (e > ea); k > x after V; palatalization before j; z > s; j > ʒ; dʒ > ʒ; labialization; h lost; **tone phonemic**
- 14.5: k, ɡ > tʃ, dʒ; s > z; o > a unstressed; ʃ > x; l > r after C [d375]
- 14.0: b d ɡ > p t k; r > ɹ; prothetic i˨; p t k > f θ x; ɛ, ɔ > je, we; degemination; w > b /#_
- 13.5: l > ʎ; θ > s; w > v; s > h; final unstressed vowel lost (twice); final devoicing; i˨ epenthesis
- 11.5 (d691): b, d > ɓ, ɗ; k > ʔ finally; m > n, x > f, n > ŋ finally; f > h; h lost; j > ʒ; ʃ > x; z > s, labialization [d666]
- 11.0: k > x; p t k > f θ x; tʃ > ʃ; s > ʃ; s > r /V_V; ɛ, ɔ > je, we; r > ʁ; x > h, e, o > i, u, nasalization after h, ʔ [d666]
- 10.5: CjV metathesis; nasal place assimilation; n > ɲ; CCC simplified; nasalization; ɛ > æ, ɔ > ɑ [d666]
- 10.0: palatalization before j; aː > ɛː; o > a; f > h, iː > əɪ, low tone, w > b, æ > eə [d666]
- 9.5: s > h; denasalization; ruki; e, o > i, u unstressed; **tone phonemic**; ə > ɜ̠ [d604]; l > ɫ, final C lost, w > v [d666]
- 9.0: degemination; ɑ > a; intervocalic voicing; l > r after C; r > ɹ; dʒ > ʒ; regressive voicing, u˨ epenthesis [d666]
- 8.5: labialization; b d ɡ > β ð ɣ /V_V; β > v; f > h; breathy voice, m lost finally [d666]. 8.0: dz > z; kʷ > p; p > f; s > h
- 7.5: nasal place; n > ɲ; CCC simplified; w > ɡw; gemination; ʃ > x. 7.0: s > z /V_V
- 6.5: x lost with lengthening; palatalization; f > h; w > v; j > dʒ; initial unstressed V lost; e, o > i, u
- 6.0: stressed lengthening; dʒ > ʒ; regressive voicing; a > ɛ; m > n, n > ŋ finally; iː > əɪ; **tone phonemic**. 5.5: h lost; ŋ > n; r > ɹ; j > ʒ
- 5.0: ɛ, ɔ > je, we; gemination; o > a. 4.5: nasal place; e > i before nasals; e, o > i, u stressed; breathy voice
- 4.0: intervocalic voicing; degemination; s lost finally; z > r; nasalization. 3.5: denasalization; labialization; w > v
- 3.0: regressive voicing; CjV metathesis; l > r; CrV > CVr; ə > ɜ̠. 2.5: r > ʁ; n > ŋ finally; final C lost; a > ɛ
- 2.0: ɔ > ɑ; s > z; iː > ai; y > i. 1.5: aː > ɛː; prothetic ʔ; z > s; f > h; ʃ > x; final unstressed V lost [d604]
- 1.0: m lost finally; long V shorten; x > h; s lost; j > ʒ; m > n; final devoicing; nasalization; k > ʔ; h lost; ʔ lost in codas; χ > ħ, s > h [d604]; n > ɲ [d666]
- 0.5: ln > ll; nasal lost after nasal V; degemination; denasalization; intervocalic voicing. 0.0: s > h before C; h lost in codas; l > r

Inventory of the line at four moments:

| kyr | lect | C | consonants | V | vowels |
| --- | --- | --- | --- | --- | --- |
| 20 | p306/d561 | 26 | v l m j b n d t h z ȶ tʃ s ɡ p w ʃ ts ɓ f dz ʈ ŋ k tʰ r | 10 | e i a u ɛ ɔ o aː ɨ ɔː |
| 10 | d691 | 25 | h ʒ ɲ l j s ȶ tʰ dʱ m ŋ ɡʱ bʱ ʃ f v ʈ w dz ɓ ɹ n ʁ kʷ z | 11 | i a ĩ e u æ iː ã ɑ ɔː o |
| 5 | d691 | 28 | ʒ ɲː l ɦ ʒː ɲ m mː tʰ ŋ bʱ v vː ɹ ʈ ȶ ɓ n bʱː ɡ lː j z w s nʷː f ɡː | 12 | i ə ɪ ʊ a e u aː ɔ o ɛ ɔː |
| 0 | d691 | 22 | ȶ ʒ ɲ l ɦ ʃ m tʰ ŋ bʱ ʔ v ʈ ɓ r f ɹ ɡʱ nʷ n h s | 8 | i ɛ ɪ ʊ u a ɑ e |

Read as a linguist: each change is an attested type and the chains are natural (s > h > ∅; p t k > f θ x > h; voiced stops >
breathy; j > dʒ > ʒ). The inventory now stays the size of a real one (22 + 8, against 36 + 15 in the previous run). Still too
much churn: 16.6 changes per kyr, the same few recurring (h-loss, j > ʒ, dʒ > ʒ, ɛ/ɔ breaking, a > ɛ four or five times each),
and "tone becomes phonemic" fires three times on one line.

**d726 (aarakocra 34, the north of Sothasor; p204 > d292 > d726 (9.5)), in brief.** 394 changes (19.7 per kyr; generation 6
years): effort 147, coarticulation 95, dispersion 73, perception 35, prosody 26, tonogenesis 18. Only **8 adopted** (all from
d180, a hill-giant lect): aarakocra change on their own. 69 rules repeat (merges 30 times; s > h, k > h, h-loss 7 times each).
The first step (19.5) alone has 23 changes. No change and its inverse fire in one step any more, but they alternate across
steps: n > ŋ finally at 7.0, 3.5 and 0.5, ŋ > n finally at 8.0, 4.0 and 0.0. Inventory: 20 kyr 19 C (kʷ tʼ ɻ x ts) / 12 V
(with iːᴖ, ẽ); 10 kyr 21 / 15, the second voice gone; 5 kyr 22 / 9; now 21 C `ʁ ʒ ɡʷʱ ʔ ɾ ŋ k h tʃ ɻ ɹ n l r ɣ ɳ dʱ t s x kʷ` /
9 V `i a ɛ o e ə ɪ y ẽ`. No labials at all (p was lost in the first step): fine for a beaked people.

### CHECKS

| check | measured | target | pass |
| --- | --- | --- | --- |
| proto inventories vs PHOIBLE | 110 human-voiced protos: median 23 C, 8 V; 51% inside the C IQR, 54% inside the V IQR, 23% both; top-20 segment overlap 19 | medians inside the IQR (C 17-27, V 6-12); 35-75% inside per measure; top-20 overlap >= 10 | yes |
| sisters recognisable, distant not | blind cognate share: sisters parted <= 2 kyr 0.512 (207 pairs); different families 0.003 (191,691 pairs); chance floor 0.013 | sisters > 0.5, different families < 0.15 | yes |
| scholars' horizon (human lects) | **11.0 kyr** (all lects 9.2; old per-pair measure 11.0, all 10.0) | 6-10 kyr | **no** |
| language shift happened | 159 shifts (takeover 93, swamp 49, trade 11, elite 1, unrecorded 5); 96 of 623 living lects speak outside their deme's descent | > 0 | yes |
| long generations change less | humans 15.2 rules/kyr, long-lived peoples 4.4 (ratio 3.49) | long-lived < a third of humans | yes |
| hubs simpler, isolated richer | complexity: hubs 1.32 (204 lects), isolated 2.89 (60) | hubs < isolated | yes |

**Horizon: share of true splits the scholars' tree recovers, by age (2-kyr windows, human lects, all splits scored).**

| split age kyr | 0-2 | 1-3 | 2-4 | 3-5 | 4-6 | 5-7 | 6-8 | 7-9 | 8-10 | 9-11 | 10-12 | 11-13 | 12-14 | 13-22 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| splits | 10 | 14 | 9 | 5 | 10 | 11 | 10 | 13 | 7 | 2 | 2 | 1 | 3 | 2-5 each |
| recovered | 0.90 | 0.93 | 0.89 | 0.80 | 0.60 | 0.55 | 0.70 | 0.85 | 1.00 | 0 | 0 | 0 | 0 | 0 |
| mean cognate share | 0.54 | 0.40 | 0.33 | 0.21 | 0.12 | 0.10 | 0.08 | 0.06 | 0.07 | 0.015 | 0.015 | 0.002 | 0.003 | <= 0.01 |

The fail is a near miss on thin data: the tree recovers every split up to 10 kyr (the 8-10 window, 7 splits, at 1.00) and
none of the 2 splits in the 9-11 window, so the reading lands at 11.0, one kyr over the target. Splits at 4-7 kyr are the
weak spot (0.55-0.60). On another seed this would move by a kyr or two either way. Over all lects the horizon is 9.2.

**Shares, three ways:** sisters parted <= 2 kyr: loose 0.512, strict (aligned distance under the threshold and recurring
correspondences) 0.453, true (same root in the etymologies) 0.562. Different families: loose 0.003, strict 0.000, true 0.0003.

**Intelligibility now** (`intelligibility.now`, 874 pairs):

| pair | pairs | 10th / median / 90th pct | share > 0.7 | share < 0.4 |
| --- | --- | --- | --- | --- |
| sisters parted <= 2 kyr | 207 | 0.22 / 0.42 / 0.70 | 0.10 | 0.47 |
| parted 2-5 kyr | 170 | 0.08 / 0.15 / 0.39 | 0.02 | 0.91 |
| parted 5-10 kyr | 357 | 0.06 / 0.09 / 0.21 | 0 | 0.99 |
| parted > 10 kyr | 129 | 0.06 / 0.10 / 0.28 | 0 | 0.98 |
| different families | 11 | 0.05 / 0.07 / 0.10 | 0 | 1.00 |

Sisters parted under 2 kyr are half intelligible (median 0.42); by 2-5 kyr they are not. **Continua found by the pass: 1.**
Family p269: human d177.1 – gnome d470.1 – gnome d765.1 (links 0.56, 0.54; ends 0.43), the west of Simath; the gnomes speak
the lect after a shift. The viewer's in-browser search finds more chains at earlier frames.

### SPECIES

| group | lects (living) | generation yr | rules per kyr (median, q1-q3) | inherited core share (median; living with 0) | mean word length (segments) | homophone share | inventory C+V | shifts as speakers / rulers | ʔ-initial core words |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human | 131 (104) | 28 | 15.1 (11.8-18.4) | 0.10; 1% | 5.18 | 0.111 | 32 | 21 / 89 | 13% |
| dragons | 131 (118) | 430 | 3.7 (3.0-4.5) | **0.78**; 0% | 5.00 | 0.142 | 32 | 2 / 13 | 5% |
| elves | 34 (25) | 145 | 5.3 (4.5-8.0) | 0.51; 0% | 5.22 | 0.125 | 30 | 2 / 9 | 5% |
| kobolds | 95 (53) | 12 | 20.9 (17.2-23.9) | 0.01; **34%** | 5.26 | 0.147 | 33 | 13 / 4 | 13% |
| aarakocra | 44 (25) | 6 | **20.9** (16.0-29.1) | **0.00; 72%** | 5.50 | **0.155** | 31 | 14 / 0 | 8% |
| dragonborn | 91 (55) | 25 | 15.5 (13.7-17.2) | 0.07; 0% | 5.15 | 0.133 | 34 | 18 / 4 | 16% |
| all others | 347 (243) | 30 | 14.6 (8.8-19.2) | 0.12; 0% | 5.14 | 0.123 | 32 | 89 / 40 | 13% |

("Rules per kyr" counts every change on the lect's line of descent over 20 kyr, wave-adopted ones included: dragons adopt 55%
of theirs, elves 34%, humans 21%, aarakocra 11%.)

- **Human:** the reference. One core word in ten survives 20 kyr, roughly what glottochronology predicts; sound change is fast.
- **Aarakocra: normal in sound, amnesiac in words.** Inventories are ordinary (31 segments, few or no labials, 8% ʔ-initial),
  but at 21 changes per kyr and a 6-year generation 72% of living lects keep no proto core word, so no family is visible
  after a few kyr; they also have the most homophones (15.5%) and the longest words.
- **Elves: conservative, as wanted.** A third of the human rate and half the core kept after 20 kyr (see the p301 table).
- **Dragons: very conservative.** 78% of the core kept, most of their changes come by wave from neighbours, homophones high
  (14%). Almost never shift.
- **Kobolds: as fast as aarakocra** (21 changes per kyr, 12-year generation): families barely visible (a third keep nothing).
- **Dragonborn: human-like** in speed and retention; 18 of their lects arose by shifting, mostly to human rulers.
- Words are a little longer than before (about 5.2 segments, was 4.8) and homophone shares a little higher (0.11-0.16, was
  0.08-0.14): the cost of smaller inventories.

### DEFECTS

Measured over the 623 living lects (214,713 words):

- **Vowel quality: i leads but no longer swamps.** Among vowel tokens (tone and length set aside) i is 29.6%, a 14.4%, u 7.4%,
  ɛ 7.3%, e 6.4%, ə 5.0%, ɨ only 3.2% (it was three of the top four vowels in the previous run). One vowel at twice the next
  is still high for a world sample, where a usually leads; not a single-vowel monoculture any more.
- **ʒ is the new monoculture.** Top segments by token: i 7.6%, **ʒ 6.0%**, ʔ 4.2, a 3.8, i˨ 3.2, n 3.1, l 2.9, m 2.7, ɲ 2.5, ŋ
  2.4, u 2.1, v 2.1. ʒ is the commonest consonant in the world (j > ʒ, dʒ > ʒ, z > ʒ before j all fire again and again;
  see the d691 log); it is visible in every sample above (ʒi for EAT, WE, FISH in two families).
- **Tone:** 48% of living lects are tonal (protos 24%, real languages about 40%). Fixed, slightly high.
- **ʔ-initial words:** 10.1% of all words, 11.1% of core words (was 15.6% and 17.1%).
- **Inventories above PHOIBLE's upper quartile:** 20% for consonants (> 27), 20% for vowels (> 12), 36% on either (was 51%
  and 46%). Largest: dragonborn d298 34 C + 16 V (ɡʷʱ, n‼, r‼ and three harsh vowels), dragonborn d281 35 + 14, green dragon
  d95 32 + 16, orc d423 and human d465 32 + 16. PHOIBLE's upper quartile is 27 + 12, so these are large but not absurd.
- **Same-spelling pairs:** in 279 of 623 lects two inventory segments get the same letter (ɹ and ɾ both ‹r›, ə and ɛ both
  ‹e›, n‼ and n̪‼ both ‹nrh›); 145 pairs of different words share one spelling, in 87 lects (was 546 in 217).
- **Shifts per deme:** at most 3 (6 demes), 35 demes with 2, 71 with 1 (was up to 6). The gap between a deme's shifts is
  never below, and has a median of, exactly 6.0 kyr: the cooldown still sets the pace when shifts repeat. 53 of the 159
  shifts are a deme moving to another lect of the same true family (the cap at 0.3 share lets them through).
- **Koine levelling:** 109 entries (was 237). Example: d375.1 (halfling) borrows from d785.1, "koine levelling in city 31386".
- **Food routes:** 85 routes, 2,900 hops (median 15 per route, the longest 193); 20 start at a taming site, 9 "inherited by
  the donor", 56 "first known here". **In 27% of hops into living lects (717 of 2,626) the receiver's present word shows no
  borrowing** (unchanged from 28%; see foxtail millet in SAMPLES c2).
- **Derivation:** 24% of living words have a derivation in their history. The six affixes are now evenly used: 'do' 5.0% of
  all words, 'little' 5.0, 'like' 4.6, 'thing' 4.4, 'agent' 4.0, 'place' 3.8. Per lect the commonest affix has a median share
  of 5.5% and reaches 12.2%; 77% of lects have one affix above the 5% cap (the cap binds at coinage time, not on the result).
  Sensible ones: SAY + 'thing' = 'word', TIE + 'thing' = 'rope', SAND + 'place' = 'desert', STONE + 'place' = 'cave', SUN +
  'place' = 'sunset', HONEY + 'like' = 'sweet', FIVE + 'little' = 'four'. **Absurd ones still common:** RAIN + 'do' = 'burn'
  (d792), TURN AROUND + 'like' = 'cold' (d481), THROW + 'thing' = 'skin' (d537), LAUGH + 'thing' = 'egg' (d622), SWELL +
  'agent' = 'bird', now 'wolf' (d850), DIE + 'agent' = 'man' (d611) and 'claw' (d817), HIDE + 'thing' = 'head' (d797), FLOAT + 'thing' =
  'night' (d437), BLOW + 'thing' = 'five' (d579), THINK + 'thing' = 'day' (d570.1), and the chain cloud > fog > smoke > dust >
  land > stone in d148.
- **Same-step reversals:** none (were 1,315). They now alternate across steps instead (d726: n > ŋ and ŋ > n finally three
  times each, half a kyr apart).
- **Words over 12 segments:** 214 (0.1%); the longest is kenku d474 BULL, 20 segments, a reduplicated string
  (sə˨ɪ˨we˨ɛ˨ʒe˨ɛ˨ʒe˨ɛ˨ʔe˨ɛ˨ʒe˨ɛ˨we˨). No brace segments, no empty word forms; 38 fused grams with a zero form (acceptable).
- **Names:** one people uses the same exonym form for different peoples 165 times (509 exonyms); some are fair (green dragons
  call hill giants and fire giants both 'the mutes'), some are not (kenku call red dragons Wei'teuhi, 'the river people',
  which is the kenku's own endonym). Place names are still dated 20 kyr when their words were coined 7-8 kyr ago (River
  Ich'e'iliaw), or even 0.5 kyr ago (River Egii in deme 226, built on a green-dragon 'river' borrowed 0.5 kyr ago).
- **Seen in the samples:** I = WE in d148 (ʈɛʃ), THOU = I in d856; elvish EAT identical in five lects after 13 kyr; grammar
  churn in aarakocra (five grams died in the last 1.5 kyr) and two lects with no negator (d690, d726).

**Fix first, in order:**
1. **ʒ everywhere.** The palatalization and affrication rules (j > ʒ, dʒ > ʒ) fire repeatedly on every line; ʒ is now the
   commonest consonant. Give these rules the same lifetime cap as prothesis and harmony, or make ʒ costlier to keep.
2. **Derivation semantics.** The 5% cap fixed the lɨ- flood, but the source-meaning pairs are still free: half the sampled
   derivations make no sense. Restrict each affix to plausible source-target pairs (instrument, agent of a verb, diminutive of
   a thing) and apply the 5% cap to the final lexicon, not only at coinage.
3. **Food-route bookkeeping.** A quarter of hops claim a loan the receiver's word does not show. Record a hop only when the
   receiver's word for the crop actually comes from the donor, or mark the hop as "word replaced since".
4. **Shift pacing.** Repeat shifts happen exactly at the 6-kyr cooldown; a deme already speaking the rulers' family should
   level (koine) rather than shift, and the trigger, not the clock, should time the next one.
5. **Small bookkeeping a reader sees:** names dated before their words; exonyms that equal the namer's own endonym; rule
   pairs that undo each other half a kyr apart; the horizon reading resting on bins of 2 splits.
