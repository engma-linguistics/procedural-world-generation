"""Write the two knowledge-authored language tables (no download behind them).

    uv run python -I tools/language/knowledge_tables.py [--out DIR]

grammaticalization_paths.tsv: common grammaticalization paths written from general
knowledge of Heine & Kuteva's World Lexicon of Grammaticalization (2002; 2nd ed.
Kuteva et al. 2019) and the wider literature (Bybee, Perkins & Pagliuca 1994;
Hopper & Traugott 2003). NOT extracted from the book.

sound_changes.tsv: attested, context-conditioned sound changes written from general
historical-linguistics knowledge; the Index Diachronica (a hobbyist compilation) was
inspiration only. Rows are typical patterns, not a corpus; examples are textbook cases.

Rows are kept below as ' | '-separated strings so the TSV can never pick up stray tabs.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "tools/language/knowledge_tables.py"
TODAY = "2026-11-03"

# source_concept | target_function | intermediate_stages | fusion_endpoint | frequency_class | example
GRAM_PATHS = """
GO (motion toward) | FUTURE | intention ('be going to') > immediate future > future | auxiliary > proclitic/prefix | very common | English be going to > gonna; French je vais chanter
COME | FUTURE | motion toward speaker > future | auxiliary > affix | common | Swedish kommer att + inf. 'will'; Zulu -zo- future (< -za 'come')
COME (FROM) | RECENT PAST | 'come from doing' > 'have just done' | auxiliary | common | French je viens de manger 'I have just eaten'
WANT / DESIRE | FUTURE | volition > intention > prediction | auxiliary > clitic > prefix | very common | English will (Old English willan 'want'); Modern Greek tha (< thelo na 'I want that'); Swahili -ta- (< -taka 'want')
HAVE TO / OWE (obligation) | FUTURE | obligation > intention > future | auxiliary > suffix | common | Latin cantare habeo 'I have to sing' > French chanterai; English shall (Old English sceal 'owe')
HAVE (possession) | PERFECT | resultative possessive ('have it written') > perfect | auxiliary | very common | English I have written; Spanish he cantado
HAVE (possession) | OBLIGATION | possession of a task > deontic necessity | auxiliary > clitic | common | English have to > hafta; Spanish tener que
BE AT (locative) | PROGRESSIVE | locative 'be at/in doing' > progressive > imperfective | auxiliary > affix | very common | Dutch ik ben aan het werken; Irish tá sé ag obair 'he is at working'; Mandarin zài
SIT / STAND / LIE (posture) | PROGRESSIVE | posture + action > continuous > progressive | serial verb > auxiliary | common | Dutch hij zit te lezen 'he sits to read' = is reading; Danish sidder og laeser
WALK / GO AROUND | PROGRESSIVE > PRESENT | continuous motion > progressive > present | suffix | attested | Turkish -iyor present/progressive (< Old Turkic yori- 'walk')
STAY / EXIST | PROGRESSIVE / RESULTATIVE | locative existence > continuous or resulting state | auxiliary suffix | common | Japanese tabete iru 'is eating' (iru 'exist, stay')
PROGRESSIVE | IMPERFECTIVE / PRESENT | progressive > general present/imperfective | affix | common | English -ing progressive spreading to statives; Turkish -iyor now the general present
FINISH / COMPLETE | COMPLETIVE > PERFECT > PERFECTIVE | 'finish doing' > completive > perfect > perfective/past | serial verb > clitic/suffix | very common | Mandarin le (< liao 'finish'); Thai laeew 'already'
THROW AWAY / PUT AWAY | COMPLETIVE | 'do and discard' > completive with regret | serial verb > auxiliary suffix | attested | Japanese -te shimau 'end up doing' (shimau 'put away'); Korean -a pelita 'throw away'
PERFECT | PERFECTIVE / PAST | perfect > past (perfect drift) | auxiliary > affix | very common | French passe compose replacing the simple past; southern German Perfekt as general past
PASS / CROSS OVER | EXPERIENTIAL PERFECT | 'pass through' > 'have ever done' | suffix-like particle | attested | Mandarin qu-guo 'have been (there)' (guo 'pass')
ARRIVE / REACH | TERMINATIVE / ALLATIVE | 'reach X' > 'up to, until' > 'to' | preposition | common | Mandarin dao 'arrive' > 'to'; Thai thueng 'reach' > 'until, to'
KNOW (how to) | ABILITY > HABITUAL | knowledge > ability > habitual | auxiliary > preverbal particle | attested | Tok Pisin save (< Portuguese sabe 'knows') ability and habitual
GET / OBTAIN | ABILITY / PERMISSION / PAST | 'manage to get' > ability > permission; also > past | auxiliary > particle | common | Lao and Thai dai 'get' > 'can' and 'did'; Cantonese dak 'can'
ABILITY (CAN) | PERMISSION > EPISTEMIC POSSIBILITY | root ability > permission > possibility | auxiliary | common | English can/may (may < Old English magan 'be able')
SEE / LOOK | ATTEMPTIVE | 'do and see' > 'try doing' | serial verb > suffix | attested | Japanese tabete miru 'try eating' (miru 'see'); Mandarin kan-kan
SEE | DIRECT EVIDENTIAL | perception verb > witnessed evidential | suffix / clitic | attested | Tibetan (Lhasa) -thong visual evidential (< mthong 'see')
SAY | QUOTATIVE > COMPLEMENTIZER > PURPOSE | 'say' introducing speech > complementizer for cognition verbs > purpose | particle | very common | Ewe be 'say' > 'that'; Akan se; Tok Pisin (olsem) 'like that'
SAY | HEARSAY EVIDENTIAL | 'they say' > reportative marker | clitic | common | Spanish dizque 'allegedly' (< dice que 'says that'); Estonian -vat reportative (via participle)
LIKE / SIMILAR (manner) | QUOTATIVE / COMPLEMENTIZER | 'like' > approximation > quotative | particle | common | English 'she was like, no'; Swedish typ
GIVE | BENEFACTIVE / DATIVE | serial 'give to X' > 'for/to X' | serial verb > preposition / applicative | very common | Mandarin gei 'give' > 'for, to'; Thai hai 'give' > 'for'
GIVE | CAUSATIVE / PERMISSIVE | 'give (someone) to do' > let > make | auxiliary | common | Thai hai 'give' > 'make, let'; Finnish antaa 'give, let'
MAKE / DO | CAUSATIVE | 'make (him) do' > causative auxiliary > causative affix | auxiliary > affix | very common | French faire faire 'have done'; English make him go
DO | DUMMY AUXILIARY / EMPHATIC / HABITUAL | causative 'do' > periphrastic auxiliary | auxiliary | attested | English do-support (did you go?); southwest British English habitual 'I do go'
TAKE / HOLD | OBJECT MARKER (accusative) / INSTRUMENTAL | serial 'take X and V' > object or instrument marker | serial verb > preposition | common | Mandarin ba 'take' > object marker; Twi de 'take' > instrumental
USE | INSTRUMENTAL | serial 'use X to V' > 'with' | preposition | common | Mandarin yong 'use' > 'with (instrument)'
SUFFER / RECEIVE / GET | PASSIVE | adversative 'suffer X doing' > passive | auxiliary > particle | common | Mandarin bei (< 'suffer, cover'); Vietnamese bi 'suffer'; English get-passive
BECOME | PASSIVE / FUTURE | change of state > passive auxiliary | auxiliary | common | German er wird gesehen 'is seen' and er wird kommen 'will come' (werden 'become')
LET / LEAVE | PERMISSIVE > HORTATIVE | 'let me' > 'let us' > hortative particle | particle | common | English let's > lets (go); Russian davai 'give' > hortative
FEAR | APPREHENSIVE ('lest') | 'fear that' > negative purpose | conjunction / mood marker | attested | Latin timeo ne > ne 'lest'; Australian apprehensive markers (e.g. Dyirbal -bila)
LATER / AFTERWARD (adverb) | FUTURE | temporal adverb > preverbal future particle | particle > prefix | common | Tok Pisin bai (< baimbai 'by and by') future
BACK (body part) | BEHIND > AFTER | body part > spatial relational noun > adposition > temporal | relational noun > adposition | very common | Swahili nyuma 'back' > nyuma ya 'behind'; English (a)back; Mixtec sata 'back' > 'behind'
FACE / EYE / FOREHEAD | FRONT > BEFORE | body part > 'in front of' > 'before (time)' | relational noun > adposition | very common | Chalcatongo Mixtec nuu 'face' > 'in front of, at'; Swahili mbele 'front' (cf. 'breast')
HEAD | TOP > ON / ABOVE | body part > top region > 'on, over' | relational noun > adposition | very common | Mixtec sini 'head' > 'on top of'; Ewe ta 'head' > 'on, about'
BELLY / STOMACH | INSIDE > IN | body part > interior > 'in' | relational noun > adposition > case suffix | very common | Mixtec ini 'belly' > 'inside'; Ewe me 'inside' (relational noun)
BUTTOCKS / BASE / ROOT | BOTTOM > UNDER | body part or landmark > underside > 'under' | relational noun > adposition | common | K'iche' chuxe' 'under' (-xe' 'base, root'); Ewe te 'under' (relational noun)
SIDE / RIB / FLANK | BESIDE / NEAR | body part > lateral region > 'beside' | adposition | common | English beside (< by side); Swahili kando 'side, edge' > 'beside'
COMPANION / FRIEND | COMITATIVE > INSTRUMENTAL | 'companion' > 'with' > instrumental case | postposition > case suffix | common | Estonian -ga comitative (< kaasa 'with' < kaas 'companion')
COMITATIVE (WITH) | INSTRUMENTAL > NP CONJUNCTION (AND) | 'with X' > means > 'and' | preposition / conjunction | very common | English with (instrument); Swahili na 'with, and'
ALLATIVE (TO) | DATIVE > ACCUSATIVE (differential object) | direction > recipient > animate object | preposition > case | very common | Spanish a (< Latin ad 'to') marking animate objects; Hindi ko dative > object
ALLATIVE (TO) | PURPOSE > INFINITIVE MARKER | direction > purpose > infinitive | particle | common | English to + infinitive; German um zu / zu
ABLATIVE (FROM) | COMPARATIVE STANDARD (THAN) | source > standard of comparison | case suffix / postposition | common | Turkish senden buyuk 'bigger than you' (-den 'from'); Japanese yori 'from, than'
SURPASS / EXCEED | COMPARATIVE MARKER | 'X surpass Y (in) big' > 'than' | serial verb > particle | common | Thai kwaa 'surpass' > 'more than'; Yoruba ju 'exceed'
ADPOSITION | CASE AFFIX | free postposition > clitic > case suffix | case suffix | very common | Hungarian -ban/-ben 'in' (< bel 'innards'); Estonian -ga
ONE | INDEFINITE ARTICLE | numeral > presentative > specific indefinite > general indefinite | clitic | very common | English a/an (< Old English an 'one'); French un; German ein
DEMONSTRATIVE (distal) | DEFINITE ARTICLE | demonstrative > anaphoric > definite > specific | clitic > affix | very common | Latin ille 'that' > French le, Spanish el; Romanian lupul 'the wolf' (suffixed -ul)
DEFINITE ARTICLE | NOUN MARKER / GENDER-CLASS MARKER | definite > specific > generic noun marker (Greenberg's stage III) | prefix / suffix | attested | Greenberg 1978: e.g. Bantu augment prefixes; Gur and Kordofanian class affixes
DEMONSTRATIVE | THIRD PERSON PRONOUN | demonstrative > anaphoric pronoun | pronoun > clitic | very common | Latin ille > French il, elle; Japanese kare 'that one' > 'he'
THIRD PERSON PRONOUN | VERB AGREEMENT | pronoun > clitic doubling > agreement affix | prefix / suffix | very common | Colloquial French moi je l'ai vu; Bantu subject concords; Tok Pisin predicate marker i (< he)
DEMONSTRATIVE | RELATIVE / COMPLEMENTIZER | demonstrative > relativizer > complementizer | particle | common | English that (relative and complementizer); German der (relative), dass
DEMONSTRATIVE | COPULA | topic pronoun 'X, this (is) Y' > copula | particle | common | Mandarin shi 'this' > copula; Hebrew hu 'he' used as copula
COPULA | FOCUS MARKER | cleft 'it is X that' > focus particle | particle | common | Mandarin shi...de clefts; Yoruba ni focus marker; Hausa ne/ce
WH-INTERROGATIVE | RELATIVE PRONOUN | question word > relative pronoun | pronoun | very common | English who/which as relatives; Latin qui; Russian kotoryj
BODY / HEAD / BONE / SOUL (self) | REFLEXIVE > RECIPROCAL | 'his body' > emphatic 'himself' > reflexive | noun > pronoun > affix | very common | Basque bere burua 'his head' = himself; Hebrew atsmo 'his bone' = himself; Sanskrit atman 'soul, self'
REFLEXIVE | MIDDLE > PASSIVE | reflexive > middle (anticausative) > passive | clitic > suffix | common | Russian -sja (myt'sja 'wash oneself', stroit'sja 'be built'); Spanish se vende 'is sold'
PERSON / MAN (generic noun) | INDEFINITE PRONOUN > FIRST PERSON PLURAL | 'a man' > 'one, people' > 'we' | pronoun > clitic | common | German man (< Mann); French on (< homo) now 'we' (on y va)
THING | INDEFINITE PRONOUN / NOMINALIZER | 'thing' > 'something' > nominalizing particle | pronoun / suffix | common | English something; Japanese koto and mono as nominalizers
CHILD / SON | DIMINUTIVE | 'child of X' > small X > diminutive affix | suffix | very common | Mandarin -zi (zi 'child'); Ewe -vi diminutive (vi 'child'); Akan -ba
ALL / PEOPLE / MANY | PLURAL MARKER | quantifier or group noun > plural marker | particle > affix | common | Tok Pisin ol (< all) plural marker; Indonesian para; Japanese -tachi (group)
HAND | FIVE (numeral) | body part > numeral 'five' > base of quinary counting | lexical | common | Austronesian lima 'five' (also 'hand'); many Papuan body-tally systems
NOUN (shape or kind: body, tree, fruit, head) | NUMERAL CLASSIFIER > NOUN CLASS | generic noun > classifier > (rarely) gender | particle > prefix | common | Thai tua 'body' (classifier for animals); Mandarin ge; Japanese -hon 'stem' for long things
BELONG / PROPERTY | GENITIVE MARKER | 'X that belongs to Y' > possessive linker | preposition | attested | Tok Pisin bilong (< belong) 'of'; Hawaiian Creole fo
MINIMIZER (step, crumb, point, nothing) | NEGATION | emphatic 'not a step' > obligatory second negator > sole negator (Jespersen's cycle) | particle | very common | French ne...pas 'not...step' > colloquial pas; English not (< nawiht 'nothing')
NEGATIVE EXISTENTIAL ('there is not') | STANDARD NEGATION | negative existential > verbal negator (Croft's negative-existential cycle) | particle / auxiliary | common | Croft 1991: attested in Polynesian and Dravidian, among others
TIME / WHILE (noun) | TEMPORAL > CONCESSIVE / CAUSAL CONJUNCTION | 'the time that' > 'while' > 'although' | conjunction | common | English while (< Old English hwil 'time'); German weil 'because' (< 'while')
SINCE (temporal) | CAUSAL | temporal sequence > cause (post hoc) | conjunction | common | English since; French puisque
USE / BE ACCUSTOMED | PAST HABITUAL | 'be accustomed to' > past habitual | auxiliary | attested | English used to; Latin solere 'be wont'
"""

# family | rule | cause | articulators_or_axes_needed | naturalness | example
SOUND_CHANGES = """
lenition | p > ɸ / V_V | effort | lips | 4 | Tuscan Italian gorgia: la pipa [la ɸiːpa]
lenition | t > θ / V_V | effort | tongue_tip | 4 | Tuscan gorgia la tana [la θaːna]; Hebrew begadkefat t > θ after vowels
lenition | k > h / V_V | effort | tongue_body, larynx | 4 | Tuscan gorgia la casa [la haːsa]
lenition | k > x / V_ | effort | tongue_body | 4 | Biblical Hebrew begadkefat: k > x after vowels
lenition | b > β / V_V | effort | lips | 5 | Spanish lobo [loβo]
lenition | d > ð / V_V | effort | tongue_tip | 5 | Spanish nada [naða]; Danish gade [ɡæːðə]
lenition | g > ɣ / V_V | effort | tongue_body | 5 | Spanish lago [laɣo]
lenition | ð > ∅ / V_V | effort | tongue_tip | 4 | Colloquial Spanish cansado > cansao
lenition | ɣ > ∅ / V_V | effort | tongue_body | 4 | Turkish dağı [daːɯ] (soft g lost, vowel lengthened)
lenition | p > b / V_V | coarticulation | larynx | 5 | Latin lupum > Spanish lobo
lenition | t > d / V_V | coarticulation | larynx | 5 | Latin vitam > Spanish vida
lenition | k > g / V_V | coarticulation | larynx | 5 | Latin acutum > Spanish agudo
lenition | t, d > ɾ / V́_V | effort | tongue_tip, timing | 5 | American English water [ˈwɑɾɚ]
lenition | β > v | perception | lips | 3 | Latin habere > Italian avere
lenition | p > f | effort | lips | 4 | Grimm's law: Latin pater vs English father
lenition | ɸ > h / #_ | effort | lips, larynx | 4 | Old Japanese *pana > ɸana > hana 'flower'
lenition | f > h / #_ | effort | larynx | 3 | Latin facere > Old Spanish hazer > hacer
lenition | h > ∅ | effort | larynx | 5 | Spanish hacer [aθer]; Cockney 'ouse; French h-loss
lenition | s > h / #_, V_V | effort | tongue_tip, larynx | 4 | Proto-Indo-European *septm > Greek hepta, Avestan hapta
lenition | s > h / _C, _# | effort | tongue_tip, larynx | 5 | Andalusian and Caribbean Spanish los perros [loh pero]
lenition | p, t, k > f, θ/h, x (initial mutation) | prosody | lips, tongue_tip, tongue_body | 4 | Irish lenition: cat 'cat' > a chat [ə xat] 'his cat'
lenition | p > ∅ / #_, V_V (via ɸ > h) | effort | lips, larynx | 3 | Proto-Celtic *p loss: Latin pater vs Old Irish athair
lenition | x > h / #_ | effort | tongue_body, larynx | 5 | Proto-Germanic *xundaz > Old English hund
lenition | x > ∅ / _C (with compensatory lengthening) | effort | tongue_body, timing | 4 | Middle English night [nixt] > [niːt] > [naɪt]
lenition | x > f / _# (after rounded vowel) | perception | tongue_body, lips | 2 | English laugh, enough [f] (< [x])
lenition | χ, x > h | effort | tongue_body, larynx | 4 | Caribbean Spanish jamón [hamon]
lenition | w > ∅ / _u, _o | dispersion | lips | 4 | English sword, two (w lost before back rounded vowels)
lenition | w > ∅ / #_ (before back vowel) | effort | lips | 3 | Ancient Greek digamma loss: *woikos > oikos
lenition | ʎ > j | effort | tongue_body | 5 | Spanish yeísmo: calle [kaʎe] > [kaje]; French fille [fij]
lenition | j > ʒ | perception | tongue_blade | 3 | Rioplatense Spanish yo [ʒo] > [ʃo]
lenition | tʃ > ʃ | effort | tongue_blade | 4 | Old French chanter [tʃ] > French [ʃ]
lenition | ts > s | effort | tongue_tip | 5 | Old French cent [ts] > [s]
lenition | dʒ > ʒ | effort | tongue_blade | 4 | Old French jour [dʒ] > [ʒ]
lenition | dz > z | effort | tongue_tip | 4 | Old Spanish dezir [dz] > [z] (later devoiced)
lenition | CC > C (degemination) | effort | timing | 5 | Latin gutta > Spanish gota; Latin cuppa > French coupe
lenition | k > ʔ / _# | effort | tongue_body, larynx | 4 | Malay budak [budaʔ]
lenition | p, t, k > ʔ / _# | effort | larynx | 4 | Proto-Burmish final stops > glottal stop in Burmese
lenition | t > ʔ / V_V, _# | effort | tongue_tip, larynx | 4 | London English butter [bʌʔə], what [wɒʔ]
fortition | w > gw / #_ | perception | lips, tongue_body | 3 | Frankish *werra > French guerre, Italian guerra; Welsh gw-
fortition | w > b / #_ | perception | lips | 3 | Latin vivere > Spanish vivir [biβir]
fortition | j > dʒ / #_ | perception | tongue_blade | 4 | Latin iam > Italian già; Latin iugum > Italian giogo
fortition | ∅ > ʔ / #_V | prosody | larynx | 4 | German Apfel [ʔapfl̩]
fortition | ∅ > t / n_s (excrescent stop) | coarticulation | tongue_tip, velum | 4 | English prince [prɪnts]
fortition | ∅ > b / m_r, m_l | coarticulation | lips, velum | 4 | Latin camera > French chambre; Latin numerus > French nombre
fortition | ∅ > d / n_r | coarticulation | tongue_tip, velum | 4 | Old English þunor > thunder; Latin tenerum > French tendre
fortition | C > CC / V́_j (West Germanic gemination) | prosody | timing | 3 | Proto-Germanic *satjan > Old English settan 'set'
fortition | C > CC / V́_ (stressed short vowel) | prosody | timing, stress | 3 | Italian raddoppiamento: Latin femina > Italian femmina
fortition | l > d / N_ | coarticulation | tongue_tip, velum | 4 | Swahili -refu 'long' > ndefu (class 9/10, Bantu *l > d after nasal)
palatalization | k > tʃ / _[+front V] | coarticulation | tongue_body, tongue_blade | 5 | Latin centum [k] > Italian cento [tʃ]; Old English cirice > church
palatalization | g > dʒ / _[+front V] | coarticulation | tongue_body, tongue_blade | 5 | Latin gentem > Italian gente [dʒ]
palatalization | k > ts > s / _[+front V] | coarticulation | tongue_body, tongue_tip | 4 | Latin centum > Old French [ts]ent > French cent [sɑ̃]
palatalization | k > tʃ / i_ (progressive) | coarticulation | tongue_body, tongue_blade | 3 | Old English dic > ditch; ic > (northern) ich > I
palatalization | t > tʃ / _i | coarticulation | tongue_tip, tongue_blade | 5 | Japanese *ti > chi; Brazilian Portuguese tia [tʃia]
palatalization | d > dʒ / _i | coarticulation | tongue_tip, tongue_blade | 5 | Brazilian Portuguese dia [dʒia]; Japanese *di > ji
palatalization | s > ʃ / _i | coarticulation | tongue_blade | 5 | Japanese *si > shi; Korean si [ɕi]
palatalization | t, d, s, z > tʃ, dʒ, ʃ, ʒ / _j (yod coalescence) | coarticulation | tongue_blade | 5 | English nature, 'did you' [dɪdʒu], measure
palatalization | n > ɲ / _j, _i | coarticulation | tongue_body, velum | 5 | Latin vinea > Spanish viña, Italian vigna
palatalization | l > ʎ / _j | coarticulation | tongue_body | 5 | Latin palea > Italian paglia [ʎ]; Latin filia > Portuguese filha
palatalization | pl, kl, fl > ʎ / #_ | coarticulation | tongue_body | 3 | Latin plorare > Spanish llorar; clamare > llamar
palatalization | pl, kl, fl > pj, kj, fj | coarticulation | tongue_body | 4 | Latin plenum > Italian pieno; florem > fiore
palatalization | kt > jt > tʃ | coarticulation | tongue_body, tongue_blade | 3 | Latin factum > Spanish hecho; Latin noctem > noche
palatalization | kt > jt | coarticulation | tongue_body | 4 | Latin factum > French fait; Latin lactem > Portuguese leite
palatalization | k, g > tʃ, dʒ / _e, i, j (First Slavic palatalization) | coarticulation | tongue_body, tongue_blade | 4 | Proto-Slavic *kelo > Russian čelo; *gena > žena
palatalization | a > ɛ / [+stress] open syllable | coarticulation | tongue_body | 3 | Latin mare > French mer; patrem > père
labial | kʷ > p | perception | lips, tongue_body | 3 | Proto-Indo-European *kʷetwores > Welsh pedwar vs Old Irish cethair; Greek pente
labial | gʷ > b | perception | lips, tongue_body | 3 | Proto-Indo-European *gʷem- > Greek bainō 'go'
labial | kʷ > k | effort | lips | 4 | Latin quis > Spanish quién [kjen]; Latin quattuor > Portuguese quatro [kw] retained vs French quatre [k]
labial | C > Cʷ / _u, _o (labialization, phonologized when vowel lost) | coarticulation | lips | 3 | English coo [kʷuː] allophonic; Northwest Caucasian labialized consonants traced to lost rounded vowels (Colarusso)
labial | w > v | effort | lips | 4 | Latin v [w] > Romance [v]; Old High German w > German [v]
labial | ɸ > f | perception | lips | 4 | Proto-Germanic *ɸ (< *p) > f
labial | θ > f | perception | tongue_tip, lips | 3 | London English think [fɪŋk]; Old Russian Fëdor < Greek Theodoros
labial | m > n / _# | dispersion | lips, tongue_tip | 4 | Proto-Indo-European *-om > Greek -on; Spanish álbum [alβun]
labial | u > y | dispersion | tongue_body | 3 | Latin murum > French mur [myʁ]; Attic Greek u > y
labial | y > i | effort | lips | 4 | Old English cyning [y] > king; Greek υ [y] > [i]
assimilation | N > [αplace] / _C[αplace] | coarticulation | velum, lips, tongue_tip, tongue_body | 5 | Latin in- + possibilis > impossibilis; English input [ɪmpʊt]
assimilation | [−son] > [−voice] / _[−voice] | coarticulation | larynx | 5 | Russian lodka [lotkə]
assimilation | [−son] > [+voice] / _[+voice −son] | coarticulation | larynx | 5 | Russian vokzal [vɐɡzal]
assimilation | pt > tt | coarticulation | lips, tongue_tip, timing | 5 | Latin septem > Italian sette
assimilation | kt > tt | coarticulation | tongue_body, tongue_tip, timing | 5 | Latin noctem > Italian notte; factum > fatto
assimilation | ks > ss | coarticulation | tongue_body, timing | 4 | Latin saxum > Italian sasso
assimilation | mb > mm, nd > nn | coarticulation | velum | 4 | Latin quando > Neapolitan quanno; Catalan cama (< camba)
assimilation | ln > ll, nl > ll | coarticulation | velum, tongue_tip | 4 | Latin *colnis > collis
assimilation | T > D / N_ (postnasal voicing) | coarticulation | larynx, velum | 5 | Modern Greek pente [pende]; Southern Italian campo [kambo]
assimilation | ᵐb > b, ⁿd > d / #_ | effort | velum | 3 | Modern Greek μπ, ντ word-initially [b], [d]
assimilation | ns > s with compensatory lengthening (V n s > Ṽː s > Vː s) | coarticulation | velum, timing | 4 | Latin mensa > mesa; Proto-Germanic *gans > English goose
assimilation | rt > ʈ, rd > ɖ, rn > ɳ, rs > ʂ | coarticulation | tongue_tip | 4 | Swedish kort [kɔʈ], barn [bɑːɳ]
assimilation | s > ʂ, x / {r, u, k, i}_ (RUKI) | coarticulation | tongue_tip, tongue_body | 3 | Sanskrit -ṣ-; Proto-Slavic *s > x (Russian -ax locative plural)
assimilation | V > Ṽ / _N | coarticulation | velum | 5 | French bon, Portuguese bom (vowel nasalized before nasal)
assimilation | V > Ṽ / h_, ʔ_ (spontaneous nasalization) | perception | velum, larynx | 2 | Hindi ū̃ṭ 'camel' (< Sanskrit uṣṭra); rhinoglottophilia (Matisoff 1975)
assimilation | e > i / _N | coarticulation | tongue_body, velum | 4 | Southern US English pen = pin merger
dissimilation | r...r > l...r | perception | tongue_tip | 3 | Latin peregrinus > Italian pellegrino; arborem > Spanish árbol
dissimilation | l...l > l...r | perception | tongue_tip | 3 | Latin -alis > -aris after l (militaris)
dissimilation | Cʰ...Cʰ > C...Cʰ (Grassmann's law) | perception | larynx | 2 | Proto-Indo-European *dʰidʰeh₁- > Sanskrit dadhāti, Greek tithēmi
dissimilation | n...n > l...n, r...n | perception | velum, tongue_tip | 2 | Latin Bononia > Italian Bologna; Latin anima > *anma > Spanish alma (nm > lm)
devoicing | [−son] > [−voice] / _# (final devoicing) | effort | larynx | 5 | German Rad [ʁaːt]; Dutch hond [ɦɔnt]; Russian, Polish, Turkish
devoicing | z > s | effort | larynx | 4 | Old Spanish casa [z] > [s] (merger with s)
devoicing | b, d, g > p, t, k (Grimm) | dispersion | larynx | 3 | Latin decem vs English ten; genu vs knee
devoicing | bʰ, dʰ, gʰ > b, d, g (Grimm) | dispersion | larynx | 3 | Sanskrit bharati vs English bear; Proto-Indo-European *dʰwer- > door
deletion | C > ∅ / _# | effort | timing | 4 | French petit [pəti]; Proto-Oceanic *ikan > Hawaiian iʻa 'fish'
deletion | m > ∅ / _# | effort | lips, velum | 4 | Latin rosam > Italian rosa
deletion | s > ∅ / _# | effort | tongue_tip | 4 | French les [le]; Florentine and southern Italian plurals
deletion | r > ∅ / _C, _# (non-rhotic, compensatory lengthening) | effort | tongue_tip, timing | 4 | RP English car [kɑː], card [kɑːd]
deletion | V[−stress] > ∅ / _# (apocope) | prosody | stress | 5 | Middle English name [naːmə] > [naːm]
deletion | V[−stress] > ∅ / VC_CV (syncope) | prosody | stress | 5 | Latin calidus > caldus > Italian caldo; oculus > *oclus
deletion | V > ∅ / #_ [−stress] (aphaeresis) | prosody | stress | 3 | English (a)mend, (e)squire
deletion | CV > ∅ / _CV (same CV repeated: haplology) | effort | timing | 2 | Latin *nutritrix > nutrix; English probably [ˈprɒbli]
deletion | ʕ > ∅ (with vowel lengthening) | effort | tongue_root | 3 | Maltese ʕ lost (spelled għ), vowel lengthened
deletion | ħ > h | effort | tongue_root, larynx | 3 | Maltese ħ [ħ] > [h] in many speakers; Modern Hebrew ħ > χ
cluster | kn > n / #_ | effort | tongue_body | 4 | English knight, knee (k lost)
cluster | wr > r / #_ | effort | lips | 4 | English write, wrong
cluster | mb > m / _# | effort | lips | 4 | English lamb, climb
cluster | gn > n / #_ | effort | tongue_body | 4 | English gnaw
cluster | CCC > CC (medial reduction) | effort | timing | 5 | English Christmas [krɪsməs], exactly [ɪɡzækli]
cluster | ps, pt > s, t / #_ | effort | lips | 3 | Greek-derived English psychology, pterodactyl; Latin psallere > Italian salmo
reduction | V[−stress] > ə | prosody | tongue_body, stress | 5 | English photograph vs photography
reduction | o > a / [−stress] (akanye) | prosody | tongue_body, stress | 4 | Russian voda [vɐˈda]
reduction | e, o > i, u / [−stress] (unstressed raising) | prosody | tongue_body, stress | 4 | European Portuguese and Bulgarian unstressed vowel raising
reduction | Vː > V (loss of length) | prosody | timing | 4 | Latin vowel quantity collapsed in Romance; Classical > Koine Greek
reduction | Vː > V / _CC (closed syllable shortening) | prosody | timing | 4 | Old English cēpte > kept; wīsdōm > wisdom
reduction | V́ > V́ː / _CV (open syllable lengthening) | prosody | timing, stress | 4 | Middle English name [namə] > [naːmə]
reduction | VC > Vː / _C (compensatory lengthening) | prosody | timing | 4 | Proto-Greek *esmi > Attic ēmi (εἰμί)
epenthesis | ∅ > e / #_sC (prothesis) | perception | tongue_body | 4 | Latin schola > Spanish escuela; Latin stella > French étoile
epenthesis | ∅ > ə, ɨ / C_C (anaptyxis) | perception | tongue_body | 4 | Irish film [fʲɪlʲəm]; Hindi iskūl 'school'
epenthesis | ∅ > V / C_# (paragoge) | perception | tongue_body | 4 | Japanese loan adaptation bed > beddo; Italian dialects con > cone
epenthesis | ∅ > j / i_V, ∅ > w / u_V (hiatus glide) | coarticulation | tongue_body, lips | 5 | English seeing [sijɪŋ], doing [duwɪŋ]
epenthesis | V1V2 > V2 (elision in hiatus) | prosody | timing | 4 | French le ami > l'ami
epenthesis | i, u > j, w / _V (glide formation) | prosody | tongue_body, lips | 5 | Latin filius > *filjus; Spanish diario [djaɾjo]
metathesis | CoRC > CRaC (liquid metathesis) | prosody | tongue_tip | 3 | Proto-Slavic *gordъ > Old Church Slavonic gradъ, Polish gród (Russian gorod: pleophony)
metathesis | CrV > CVr | perception | tongue_tip | 3 | Old English brid > bird; hros > horse
metathesis | sk > ks | perception | tongue_tip, tongue_body | 2 | Old English ascian > dialectal English ax 'ask'
metathesis | VCjV > VjCV (palatal metathesis) | coarticulation | tongue_body | 3 | Latin basium > Portuguese beijo; Latin capio > Spanish quepo
harmony | V[suffix] > [αback] / V[αback]C*_ | coarticulation | tongue_body | 5 | Turkish ev-ler 'houses' vs at-lar 'horses'; Finnish talo-ssa vs kylä-ssä
harmony | V[suffix] > [αround] / V[αround]C*_ | coarticulation | lips | 4 | Turkish göz-ün 'of the eye' vs kız-ın 'of the girl'
harmony | V[−ATR] > [+ATR] / [+ATR] word | coarticulation | tongue_root | 4 | Akan and other West African ATR harmony
harmony | V[+back] > [−back] / _C(C)i (i-umlaut) | coarticulation | tongue_body | 4 | Proto-Germanic *mūsiz > Old English mȳs > mice; German Gast > Gäste
harmony | u > o / _C(C)a (a-umlaut) | coarticulation | tongue_body | 3 | Proto-Germanic *hurną > Old English, Old Norse horn
harmony | a > ǫ / _C(C)u (u-umlaut) | coarticulation | lips | 3 | Old Norse *landu > lǫnd 'lands'
harmony | e, o > i, u / _C(C)i, u# (metaphony) | coarticulation | tongue_body | 3 | Neapolitan nire 'black (m.)' vs nera 'black (f.)'
harmony | e > ea / _r C, _l C, _h (breaking) | coarticulation | tongue_body | 3 | Old English *erþō > eorþe 'earth'; *ald > eald
nasal | N > ∅ / Ṽ_{C, #} (nasal loss after nasalization) | effort | velum | 4 | Latin bonum > French bon [bɔ̃]; Latin manum > Portuguese mão
nasal | Ṽ > V (denasalization) | effort | velum | 3 | Polish colloquial final ę > e (idę [idɛ])
nasal | N C > ᴺC (cluster reanalysed as prenasalized stop) | prosody | velum, timing | 3 | Proto-Oceanic *mp, *nt > Fijian b [ᵐb], d [ⁿd]
nasal | ŋ > n / _# (unstressed -ing) | effort | tongue_body, tongue_tip | 5 | English running [ɹʌnɪn]
nasal | n > ŋ / _# | effort | tongue_body | 4 | Caribbean and Andalusian Spanish pan [paŋ]
nasal | N > ∅ / _# with nasal vowel, then Ṽ > V (full nasal loss) | effort | velum | 3 | Proto-Germanic *-an infinitive > Old Norse -a
rhotic | s > z / V_V | coarticulation | larynx | 5 | Latin rosa [z] in Romance; English houses [zɪz]
rhotic | z > r / V_V (rhotacism) | effort | tongue_tip | 3 | Old Latin *flosis > floris; Proto-Germanic *wēzum > English were
rhotic | r > ʁ, ʀ | perception | tongue_body | 3 | French, Standard German, Brazilian and European Portuguese (Lisbon) uvular r
rhotic | r > ɹ | effort | tongue_tip | 4 | English approximant r (< trilled r)
rhotic | l > r / C_ | perception | tongue_tip | 3 | Latin blancus > Portuguese branco; Latin clavum > Portuguese cravo
rhotic | l > w, u / _C, _# (l-vocalization) | effort | tongue_tip, tongue_body | 4 | Latin altrum > French autre; London English milk [mɪʊk]; Polish ł [w]
rhotic | l > ɫ / _C, _# (velarization) | coarticulation | tongue_body | 5 | English dark l in feel, milk
debuccalization | q > ʔ | effort | tongue_body, larynx | 4 | Cairene and Levantine Arabic qalb > ʔalb 'heart'
debuccalization | q > g | effort | larynx | 3 | Bedouin and Gulf Arabic qalb > galb
debuccalization | q > k | dispersion | tongue_body | 3 | Classical Arabic q merged with k in many loans (e.g. Swahili kalamu < qalam)
debuccalization | χ > ħ | perception | tongue_root | 1 | Rare; uvular-to-pharyngeal shifts reported for some Caucasian and Salishan varieties (example not verified)
dental | θ > t | effort | tongue_tip | 4 | Irish and New York English think [tɪŋk]; Proto-Germanic *þrīz > Swedish tre
dental | ð > d | effort | tongue_tip | 4 | Proto-Germanic *þ/*ð > German drei, das
dental | θ > s | perception | tongue_tip | 3 | Urban Arabic θ > s in learned words (θawra > sawra); Afrikaans and Dutch loans
dental | ts > θ (via s̪) | dispersion | tongue_tip | 2 | Old Spanish ç [ts] > Castilian [θ] (cinco [θiŋko])
dental | ʃ > x | dispersion | tongue_body | 2 | Old Spanish dixo [ʃ] > dijo [x]
laryngeal | tt > ʰt (preaspiration) | prosody | larynx, timing | 2 | Icelandic takka [tʰaʰka]; Scottish Gaelic mac [maʰk]
laryngeal | D > ɗ, ɓ (implosivization of voiced stops) | effort | larynx | 2 | Sindhi implosives from Prakrit geminate voiced stops (*bb > ɓ)
laryngeal | Cʔ > Cʼ (stop + glottal stop > ejective) | prosody | larynx | 2 | Ossetian ejectives (contact with Kartvelian); widely proposed in reconstructions
laryngeal | D > D̤ (voiced stops > breathy, register) | tonogenesis | larynx, pitch_ear | 3 | Khmer and Mon registers from Old Khmer voiced onsets
tone | V > V˩ / D_ ; V > V˥ / T_ ; then D > T (tone split from onset voicing) | tonogenesis | larynx, pitch_ear | 4 | Middle Chinese yin/yang tone split; Kammu dialects (voicing in Eastern Kammu, tone in Northern)
tone | V > V˧˥ / _ʔ ; then ʔ > ∅ (tone from glottal coda) | tonogenesis | larynx, pitch_ear | 3 | Vietnamese: final *-ʔ gave one tone pair (Haudricourt 1954)
tone | V > V˥˩ / _h ; then h > ∅ (tone from h coda, < s) | tonogenesis | larynx, pitch_ear | 3 | Vietnamese: final *-h (< *-s) gave a second tone pair (Haudricourt 1954)
tone | V > tone class by coda (open or sonorant = A, ʔ = B, h = C, stop = D), each split by onset voicing | tonogenesis | larynx, pitch_ear | 3 | Proto-Tai tones from coda type and onset voicing (Thai five tones)
tone | 1-syllable vs 2-syllable stress contours > lexical pitch accent | prosody | pitch_ear, stress | 2 | Swedish and Norwegian accent 1 vs accent 2 (anden 'the duck' vs 'the spirit')
tone | H > ∅ / H_ (Meeussen's rule, adjacent high tones dissimilate) | dispersion | pitch_ear | 3 | Bantu tonology (e.g. Shona, Kirundi)
tone | tone > stress (tone loss) | prosody | pitch_ear, stress | 2 | Swahili lost Proto-Bantu tone; stress fixed on penult
prosody | [−voice fricative] > [+voice] / [−stress]V_ (Verner's law) | prosody | larynx, stress | 3 | Proto-Indo-European *ph₂tḗr > Proto-Germanic *fadēr (vs brother *brōþēr)
prosody | ɛ, ɔ > je, we / [+stress] (diphthongization) | prosody | tongue_body, stress | 4 | Latin petra > Spanish piedra; porta > puerta
prosody | ai, au > eː, oː (monophthongization) | effort | tongue_body | 5 | Latin causa > Spanish cosa; Old High German ou > ō
prosody | iː, uː > ai, au (diphthongization of high vowels) | dispersion | tongue_body | 4 | German Haus (< hūs); English Great Vowel Shift
chain_shift | p t k > f θ x (Grimm, step 1) | effort | lips, tongue_tip, tongue_body | 4 | Latin pater, tres, cornu vs English father, three, horn
chain_shift | p t k > pf ts kx / #_, C_ ; f s x / V_ (High German shift) | effort | lips, tongue_tip, tongue_body | 3 | German Pfund, zehn, machen vs English pound, ten, make
chain_shift | iː uː > əɪ əʊ > aɪ aʊ (Great Vowel Shift, top) | dispersion | tongue_body | 3 | English time [tiːm] > [taɪm], house [huːs] > [haʊs]
chain_shift | eː oː > iː uː (Great Vowel Shift, mid) | dispersion | tongue_body | 3 | Middle English meet [meːt] > [miːt], moon [moːn] > [muːn]
chain_shift | aː > ɛː > eː (Great Vowel Shift, low) | dispersion | tongue_body | 3 | Middle English name [naːm] > [neːm]
chain_shift | æ > eə ; ɑ > a ; ɔ > ɑ (Northern Cities Shift) | dispersion | tongue_body | 2 | Chicago and Detroit English cat [keət], cot [kat]
analogy | paradigm leveling: irregular alternant replaced by regular | analogy | none | 4 | English holp > helped; kine > cows
analogy | analogical extension of an alternation (four-part proportion) | analogy | none | 3 | English dove (past of dive, after drive:drove); sneak > snuck
click | ǀ ǃ ǂ ǁ > ts, k, c, tɬ (click replacement) | effort | tongue_tip, tongue_body | 2 | Kalahari Khoe click replacement (e.g. Shua, Tshwa; Traill and Vossen 1997)
"""

GRAM_COLUMNS = ["id", "source_concept", "target_function", "intermediate_stages", "fusion_endpoint",
                "frequency_class", "example"]
SC_COLUMNS = ["id", "family", "rule", "cause", "articulators_or_axes_needed", "naturalness", "example"]


def parse(block: str, ncols: int) -> list[list[str]]:
    rows = []
    for line in block.strip().splitlines():
        parts = [p.strip() for p in line.split(" | ")]
        if len(parts) != ncols:
            raise SystemExit(f"bad row ({len(parts)} cols): {line}")
        rows.append(parts)
    return rows


def write(path: Path, header: list[str], columns: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        for h in header:
            fh.write(f"# {h}\n")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(columns)
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)}: {len(rows)} rows")


CAUSES = {"coarticulation", "effort", "perception", "prosody", "tonogenesis", "dispersion", "analogy"}
AXES = {"lips", "tongue_tip", "tongue_blade", "tongue_body", "tongue_root", "velum", "larynx", "pitch_ear",
        "timing", "stress", "none"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "planet" / "language" / "data")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    g = parse(GRAM_PATHS, 6)
    g = [[f"G{i:03d}", *r] for i, r in enumerate(g, 1)]
    write(a.out / "grammaticalization_paths.tsv", [
        "source: WRITTEN FROM KNOWLEDGE, not extracted from any book or database. Modelled on the paths catalogued in "
        "Heine & Kuteva, World Lexicon of Grammaticalization (CUP 2002; 2nd ed. Kuteva, Heine, Hong, Long, Narrog & Rhee 2019), "
        "with Bybee, Perkins & Pagliuca 1994 (The Evolution of Grammar) and Hopper & Traugott 2003.",
        f"version: hand-authored {TODAY}",
        "licence: original text for this repository (no third-party data copied); cite the works above when using it.",
        f"script: {SCRIPT}",
        "columns: source_concept = lexical or grammatical source meaning; target_function = the gram it becomes; "
        "intermediate_stages = typical bridging stages (' > ' ordered); fusion_endpoint = how bound the marker typically ends up; "
        "frequency_class = very common (many families on several continents) | common | attested (a handful of families); "
        "example = one or two real-language cases (romanized; tone marks and some diacritics dropped).",
        "frequency classes are judgement, not counts. Paths are unidirectional in the normal case (lexical > grammatical).",
    ], GRAM_COLUMNS, g)

    s = parse(SOUND_CHANGES, 6)
    for r in s:
        if r[2] not in CAUSES:
            raise SystemExit(f"bad cause {r[2]!r}: {r}")
        bad = {x.strip() for x in r[3].split(",")} - AXES
        if bad:
            raise SystemExit(f"bad axes {bad}: {r}")
        if r[4] not in "12345":
            raise SystemExit(f"bad weight: {r}")
    s = [[f"S{i:03d}", *r] for i, r in enumerate(s, 1)]
    write(a.out / "sound_changes.tsv", [
        "source: WRITTEN FROM KNOWLEDGE of standard historical phonology (Campbell, Historical Linguistics; Hock 1991; "
        "Blevins 2004, Evolutionary Phonology; Kümmel 2007). The Index Diachronica (https://chridd.nfshost.com/diachronica/, a "
        "hobbyist compilation) was used only as inspiration for coverage; nothing was copied from it.",
        f"version: hand-authored {TODAY}",
        "licence: original text for this repository; examples are textbook cases.",
        f"script: {SCRIPT}",
        "rule notation: input > output / environment. V vowel, C consonant, N nasal, T voiceless stop, D voiced stop, "
        "# word boundary, _ the changing segment, [+stress]/[−stress] or V́ stressed vowel, Ṽ nasal vowel, ∅ zero, "
        "[αF] agreement in feature F, C* any number of consonants, {a, b} either context. Comma lists are parallel changes.",
        "cause: coarticulation | effort | perception | prosody | tonogenesis | dispersion | analogy (the dominant driver; "
        "judgement). articulators_or_axes_needed: lips, tongue_tip, tongue_blade, tongue_body, tongue_root, velum, larynx, "
        "pitch_ear (tone/pitch perception), timing (length, gemination), stress; 'none' for analogy. A people lacking an axis "
        "(e.g. no lips) should not get changes that need it.",
        "naturalness: 1 (rare, needs special conditions) .. 5 (extremely common, recurs independently everywhere). Judgement, "
        "loosely informed by Kümmel 2007 and Blevins 2004, not counted.",
    ], SC_COLUMNS, s)


if __name__ == "__main__":
    main()
