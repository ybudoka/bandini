# M16 Cent missions

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M16 — Cent missions (**ajout**, taille 8, en quatre tranches de 2)_

_Demande de Martin (13 sept. 2026) :_ « je veux plus de 100 missions avec les personnages
existants et de nouveaux personnages, partout sur la carte, plein de nouvelles idées ! »

⚠️ **Où l'on en est, le 18 sept. 2026.** La **tranche 1 (« le moteur, et le Faubourg »)** est
entamée, pas finie. Sont **commités** (`14fd7ae` et `b23f2e4`) :

- les **neuf types d'objectifs** déclarés (`TYPES_OBJECTIFS`) et **joués** dans
  `histoire.js` — chacun réutilise un mécanisme existant : `sauter` = le vol du Grand Saut,
  `boulots` = le compteur du klaxon, `payer`/`acheter` = l'économie, `eteindre` = `Incendies`,
  `detruire` = un char de mission, `proteger` = `e.suit` (le petit qui colle à sa mère),
  `suivre` = le fuyard, `pickpocket` = le jet des poches de m2 ;
- les **deux échecs** (`etoile`, `protege_mort`) et les **quatre options transverses**
  (`chrono_s`, `sans_etoile`, `sans_arme`, `contre`) ;
- **`exige`/`ferme`** au modèle (`missions.py` `Mission`) et au filtre JS
  (`Histoire.disponibles`, `exigeTenu`, `estFermee`) ;
- **`donne` étendu** (`calme`, `dette: -n`, `casier: -n`, plus `libere`/`contacts`
  généralisés) ;
- la **sauvegarde** (`p.calmes`, `p.fermees`, `p.choix` et leur repli champ par champ) et
- les **résolveurs de lieux** : `district:`, `boutique:`, `pont`, `quai`, `bois`,
  `rampe:` (tous déterministes — aucun `B.rng()`).

⚠️ **Ce qui manque encore, et c'est le plus dur** : les **juges de banc** d'un type par an
(un type n'est pas « livré » tant que le singe ne l'a pas joué sans le trouver mort), le
**téléphone qui trie** (un appel par demi-journée, non du `disponibles()` actuel qui appelle
sans compter), et **l'arc F** (f01–f13) — ses treize missions, scènes et répliques compris.
Jusque-là, le moteur est **prêt mais pas prouvé**.

_Ce que ça donne :_ une ville où **chaque quartier a une histoire**, et où le téléphone
sonne pour autre chose que les cinq missions du Faubourg. **109 missions de plus** (114 en
tout), **9 arcs**, **34 personnages de plus**, et une raison d'aller dans chacun des cinq
districts, à chaque heure du jour. Les deux fins de M13 sont les trois dernières lignes du
catalogue : ce jalon est celui qui les rend **atteignables**.

⚠️ **Cent missions, c'est un catalogue, pas cent scripts.** Les cinq missions de la v1
tiennent sur onze types d'objectifs et quatre causes d'échec, et `histoire.js` ne connaît
aucune mission par son nom. La règle tient : **une mission est une liste d'objectifs dans
`missions.py`**, et si une idée ne s'écrit pas avec les types existants, on ajoute **un
type** — jamais un `if (slug === 'q07')`. Ce jalon en ajoute neuf, listés plus bas, et
c'est tout ce que le moteur apprend. Les cent missions sont des **données** — objectifs,
répliques **et scènes**.

⚠️ **Chaque mission vient avec ses animations et ses dialogues** (décision du 16 sept.
2026, « Les missions mises en scène ») : une scène d'intro qui montre où l'on va, une scène
de fin où l'on voit ce qu'on gagne, et une réplique à chaque temps — appel, intro, **pendant**,
fin, échec. Les tables ci-dessous disent ce qu'on **fait** ; la scène et les répliques
s'écrivent **ensemble**, dans la tranche qui livre la mission, avec le vocabulaire de plans
déjà livré. Une mission qui n'a que ses objectifs n'est pas livrée.

### Ce que le moteur apprend (et rien d'autre)

- **Rien pour la mise en scène.** Le vocabulaire de plans (`camera`, `marcher`, `conduire`,
  `geste`, `coupe`…) et les six gestes sont livrés **avant** ce jalon. M16 n'y ajoute un type
  que si une de ses scènes ne s'écrit pas avec les existants — sur la même règle que les
  objectifs, et avec son juge de banc.

- **Neuf types d'objectifs de plus** dans `TYPES_OBJECTIFS`, chacun avec son juge de banc :
  `suivre` (filer un piéton ou un char sans être vu : trop près ou trop loin, c'est raté),
  `proteger` (un personnage te suit à pied ou monte avec toi ; s'il meurt, échec
  `protege_mort`), `pickpocket` (les poches d'un piéton **précis**, par-derrière — le
  mécanisme de M2 existe), `payer` (donner un montant), `acheter` (un article à un
  comptoir), `detruire` (un véhicule de la mission), `sauter` (une rampe, `vol_px` — le
  juge du défi _Le Grand Saut_), `eteindre` (un feu à l'extincteur — le jet existe, le feu
  de char aussi) et `boulots` (`n` boulots d'une `sorte` : généralise `courses`, qui reste
  pour le taxi). `parler` et `survivre`, déclarés depuis M6 et jamais utilisés, servent
  enfin.
- **Quatre options qui traversent les types** : `chrono_s` sur n'importe quel objectif (le
  défi l'avait, la mission non), `sans_etoile` (échec `etoile` dès qu'on est vu : les
  missions discrètes), `sans_arme` (entrer en territoire de gang les mains vides), `contre`
  (des adversaires sur une `course`). `ECHECS` gagne `etoile` et `protege_mort`.
- **`exige`** : ce qu'il faut avoir **en plus** des prérequis — `argent_min` (m99),
  `proprietes` et `liberes` (m98), `dette` (d08), `tenue` (f10), `heure`. Un prérequis dit
  « après quoi » ; `exige` dit « dans quel état ». Les deux se lisent dans le carnet.
- **`ferme`** : une mission qui en **ferme** une autre. C'est ce qui fait les choix (q10 ou
  q11, r03 ou r04, d07 ou d08) : une mission fermée n'apparaît plus jamais, ni au téléphone
  ni au carnet. ⚠️ Un choix est un choix **parce qu'il coûte** : chaque paire ferme aussi une
  récompense, et le juge vérifie qu'aucune des deux branches ne rapporte plus du double de
  l'autre.
- **`donne` grossit** : `libere: "<district>"` (généralise `faubourg_libere` ; le gang
  devient des passants, la zone s'efface de `carte.zones()`, c'est ce que compte _Le Boss_),
  `calme: "<gang>"` (`hostile_toujours` et `hostile_si_arme` tombent — la seule façon de
  marcher dans La Shop), `contact` (un numéro de plus au téléphone), `vehicule` (un char
  garé devant la planque), `tenue`, `munitions`, `rabais` par comptoir, `dette: -n`,
  `casier: -n`, `ami`/`ennemi` (Roy, Sal), `boulot` (un boulot de plus au klaxon),
  `manchette`. Chaque clé a **un** endroit qui la lit, dans `Histoire.recompenser()`.
- **Des lieux qu'on peut nommer.** `resoudre()` apprend `district:<slug>` (une tuile
  marchable tirée dans le district), `boutique:<genre>` (la plus proche de ce genre :
  pharmacie, taverne, quincaillerie…), `pont`, `quai`, `bois`, `rampe:<district>`. Et
  **quatre lieux spéciaux de plus** dans `carte.SPECIAUX`, parce qu'une mission a besoin
  d'une adresse stable : la **villa du maire** (Les Érables), le **Salon Ferraro** (Faubourg,
  le barbier-shylock), le **bureau du Clairon** (Faubourg) et la **cour à ferraille de
  Ti-Loup** (La Shop). ⚠️ Pas cinq : chaque lieu spécial est une pièce à dessiner, une
  porte à poser et un juge de plus. Tout le reste passe par `boutique:` et `district:`.
- **Le téléphone trie.** Avec cent missions, il sonnerait sans arrêt. Règles : **un appel
  par demi-journée**, jamais pendant une mission, jamais à 3★ et plus ; le donneur **le plus
  proche** appelle d'abord ; un donneur qu'on croise **hèle** (la bulle de M6) même si le
  téléphone n'a pas encore sonné. Le carnet (P2) liste ce qui est disponible, par district :
  c'est là que cent missions deviennent lisibles, et c'est pour ça que le carnet passe
  avant.
- **Les dialogues sortent du paquet.** 114 missions × 7 répliques ≈ 150 Ko bruts : le
  paquet (370 Ko, plafond 600) les prendrait en brut, mais pas sur le fil : 50 Ko de texte
  gzippé par-dessus les 43 d'aujourd'hui, et les 70 Ko sautent. Le catalogue (objectifs, prérequis, `donne`)
  reste dedans — c'est ce que le carnet et le GPS lisent — et les répliques viennent par
  `/api/dialogue/<slug>` **quand le téléphone sonne**, avec un ETag comme le reste. Une
  requête par mission, avant que la première voix se charge de toute façon. ⚠️ **Les scènes
  voyagent avec les répliques** : une dizaine de plans par scène, deux scènes par mission,
  ≈ 130 Ko bruts de plus sur le catalogue — la même route, la même requête, et le paquet ne
  les voit jamais.
- **Trois personnages qui ne sont pas des donneurs** dans `pietons.py`, fréquence 0, posés
  par les missions comme le fuyard de m2 : le **matelot** (les gars de Sven), le **ciseau**
  (les hommes de main de Sal), le **gardien** (les gardes de Prévost et du lot). Et
  **Biscuit**, le premier animal du jeu : un sprite de 8 × 6, quatre images, qui court comme
  un fuyard et ne rapporte rien — le promeneur de chien de La Pointe n'a toujours pas de
  chien, c'est l'occasion.
- **La sauvegarde** : `p.libere` (par district), `p.calmes` (par gang), `p.dette`,
  `p.contacts`, `p.fermees`, `p.choix`. `Sauvegarde.completer()` a le repli champ par champ :
  une vieille partie repart avec tout à vide, et m6 lui est proposée dès qu'elle a fini m5.

### Les 34 personnages de plus

⚠️ **Trente-quatre voix, c'est le vrai coût.** La règle de M6 est _une voix par
personnage_ (la table a trente-cinq lignes : Lachance était déjà promis à _Patrick_).

⚠️ **Recompté le 17 sept. 2026 : Martin a ajouté dix voix le 15, et plusieurs sont
multilingues.** Le compte en a cinquante. Ce qui dit le français qu'on obtient, ce n'est pas
l'étiquette `language` (la langue d'origine), c'est `verified_languages` dans
`GET /v2/voices` — gratuit, et `elevenlabs_list_voices` ne le montre pas.
⚠️ **Recompté le 18 sept. 2026 : cinq voix féminines de plus, le compte passe à
cinquante-cinq.** Deux comptent pour le jeu — **Claudia** (jeune, confiante) et
**Caroline - Soft Quebec accent** (douce, narration), toutes deux québécoises d'origine
(fr-CA) — et trois non-francophones qu'on n'utilisera pas : Meera (tamoul), Riya Rao
(hindi), Ana (britannique). Le manque de femmes québécoises (ci-dessous) se resserre donc
de trois à cinq en une journée.

| Origine | Hommes | Femmes |
|---|---|---|
| **québécoise** (enregistrée en fr-CA) | Felix, Khaivan, Québec Tremblay, Alexandre, Léo, Patrick — pris ou promis ; **Alexandre Boutin** et **Premium Male teacher** (Adam), libres ; les deux **annonceurs** générés (le 1 lit le Clairon) | Jeanne Mance, Julia, Amélie — prises ; **Claudia** (jeune) et **Caroline** (douce) — ajoutées le 18 sept. 2026, **libres** |
| **France** | Luca, Nicolas Petit (parisien), Martin Dupont Intime, Roland Lescalde, Troy | Clara Dupont |
| **multilingue** (née ailleurs) | Bubba Marshal (rocailleux, Sud des É.-U.), Omar J et Lutz (jeunes) | Ruby Roo (jeune, « fr-quebec »), Nadine (rauque, « fr-swiss »), Kriti, Arabella, Piku (une enfant) |

- **Aucune voix du compte n'est vérifiée en `eleven_v3`**, et le jeu ne génère qu'en v3
  (`interpretation.MODELE`). Une québécoise d'origine garde son accent quand même : il est
  dans son échantillon, et les huit du jeu le prouvent. Une **multilingue**, non : son
  français « vérifié » est au mieux un échantillon en `multilingual_v2`, le plus souvent un
  **aperçu fabriqué** par flash ou turbo (le « fr-quebec » de Ruby Roo en est un) — ce que
  v3 en fera, rien ne le dit.
- **`language_code: "fr"` ne connaît pas le Québec** : il dit la langue, pas l'accent. Le
  seul levier serait une balise d'accent, et v3 n'en tolère **qu'une par réplique, en
  tête** (sinon les trous de 1,2–1,6 s) : elle prendrait la place de l'émotion. À mesurer,
  pas à supposer.
- **Le manque, c'est les femmes.** Onze dans la table, plus Josée et Mme Thibodeau, pour
  trois voix québécoises qui parlent déjà toutes. Les hommes sont vingt-huit pour huit voix :
  ça se partage. ⚠️ Le 18 sept. 2026, Martin a ajouté **Claudia** et **Caroline**, deux
  québécoises d'origine, au compte : le manque passe de trois à **cinq** voix de femmes —
  elles couvriront deux des cinq rôles féminins encore sans voix (en attendant l'audition).

Ce qu'on fait, dans cet ordre :

1. **Une voix québécoise d'origine** pour quiconque est né dans la ville.
2. **Une voix générée** (_Voice Design_, comme les deux annonceurs) quand il n'en reste
   pas : décrite en français, « accent québécois marqué » — le narrateur parle déjà québécois
   en v3. Le palier _starter_ tient **dix voix à soi, deux sont prises** : huit places, les
   femmes d'abord. Le serveur MCP n'a pas l'outil ; Martin les crée dans l'interface, ou le
   serveur l'apprend.
3. **Une voix de France ou multilingue** seulement quand l'accent **fait le personnage** —
   Sven Haugen, le Norvégien, est le seul de la table ; Me Desjardins et Norbert, qui se
   donnent des airs, sont à trancher par Martin — ou pour boucher un trou **après une
   audition qu'il a écoutée**. Un accent ne se juge pas à la mesure.
4. **Partager ce qui reste**, comme prévu : entre personnages qui ne parlent **jamais dans
   la même mission**, avec un réglage différent (stabilité, style). Les **petites jobs**
   (arc T) gardent les voix des passants : zéro voix de plus.

**L'audition passe avant la première tranche** : la même réplique québécoise (≈ 80
caractères, un « icitte », un « tu-suite ») par voix candidate, en v3 et passée à la
finition du jeu — ≈ 1 500 crédits pour quinze voix (il en restait ≈ 24 000 le 17 sept.).
Martin classe : passe pour d'ici, passe pour d'ailleurs, non.

**Ce que le code apprend** : la fiche du personnage (`missions.PERSONNAGES`, champ `voix`)
gagne l'**origine** de sa voix (`quebec`, `generee`, `france`, `multilingue`) ;
`scripts/audio_elevenlabs.py --voix` la confronte à `verified_languages` (ou à la catégorie
`generated`) **avant de payer** et refuse un écart ; une voix qui n'est pas québécoise porte
sa **raison** (« vient de Norvège », « auditionnée le … ») et le juge refuse une fiche sans.
Le juge d'avant tient : jamais deux personnages de même voix dans un même dialogue.

| Slug | Qui | Où il se tient | Ce qu'il est |
|---|---|---|---|
| `gus` | Gus Lévesque | Chez Gus, derrière le comptoir | l'armurier ; bourru, vend à tout le monde, n'aime personne |
| `rosa` | Rosa Di Meo | Boutique Rosa | la couturière ; l'ancienne blonde de Rocco, en sait long |
| `mo` | Le Grand Mo | le banc du terminus | l'itinérant qui a tout vu ; se paie en bière et en potins |
| `fern` | Fern Côté | porte du terminus, côté quai d'autobus | le chauffeur du dernier autobus |
| `mado` | Mado | Casse-croûte du Faubourg | la propriétaire ; nourrit le sergent, et te nourrit |
| `lachance` | Dr Lachance | Hôpital, bureau | l'urgentologue ; prévu depuis la vision, jamais posé |
| `ginette` | Ginette | Hôpital, comptoir | l'infirmière-chef ; sait ce que le docteur ne dit pas |
| `sal` | Sal « Le Barbier » Ferraro | Salon Ferraro | le shylock de Rocco : 15 000 $, coupe à 12 $ |
| `desjardins` | Me Pierre-Luc Desjardins | Bar Le Brouillard, table du fond | l'avocat du Carré ; cher, et jamais deux fois le même jour |
| `louise` | Louise Tremblay-Dion | bureau du Clairon | la journaliste ; veut la une, quoi qu'il en coûte |
| `roy` | Inspectrice Claudine Roy | Poste, bureau d'en haut | la police honnête ; enquête sur Bouchard |
| `momo` | Momo Taxi | porte du casse-croûte | le chauffeur rival de Marco, endetté chez Sal |
| `lulu` | Lucienne « Lulu » Pelletier | Cantine des Quais | la sœur de Josée ; la cantine, le poisson du vendredi |
| `gege` | Gérard « Gégé » Morin | porte de la cantine | chef des débardeurs ; syndiqué jusqu'aux dents |
| `sven` | Sven Haugen, « Le Norvégien » | le quai, à côté de son cargo | le contrebandier qui veut Les Quais |
| `mireille` | Mireille | la Brume, près de l'hôtel | une fille de la Brume qui veut sortir de la rue |
| `norbert` | Norbert | Hôtel Bandini, réception | le concierge ; discret, tarifé |
| `berube` | Capitaine Aurèle Bérubé | le quai du traversier | le traversier de nuit — la deuxième fin |
| `denis` | Le Beau Denis | zone des Morues | le lieutenant de Josée, et le souteneur de Mireille |
| `tipaul` | Ti-Paul Gagnon | Dépanneur Chez Ti-Paul | le dépanneur des Érables ; bière, potins, drifts dans son parking |
| `diane` | Diane Larivière | villa d'à côté (porte de logement, Érables) | conseillère municipale ; veut la paix, et le pouvoir |
| `maire` | Le maire Réal Tanguay | villa du maire | corrompu, jovial, dort à l'Hôtel Bandini |
| `jo` | Jo Bellemare | stationnement du dépanneur, le soir | chef des Chevreuils — et le fils de Diane |
| `beaulieu` | Mme Beaulieu | un sentier des Érables, avec Biscuit | la promeneuse ; perd son chien, puis déménage |
| `xavier` | Xavier | porte du dépanneur | l'ado qui veut un selfie avec un coupé sport |
| `prevost` | Réjean Prévost | Usine Prévost, bureau | le patron ; a mis à pied la moitié de La Shop |
| `raymonde` | Raymonde Fortin | porte de l'usine | présidente du syndicat |
| `sauve` | Bob Sauvé | cour de l'usine | le contremaître ; joue sur deux tableaux |
| `gilles` | Gilles Thériault | guérite de la fourrière | le gardien du lot ; prend sa retraite à la fin |
| `boulon` | Gros-Boulon (Marcel Boulanger) | zone des Boulonneux | chef des Boulonneux — les gars que Prévost a mis dehors |
| `tiloup` | Ti-Loup Ferraille | cour à ferraille | le ferrailleur ; achète les épaves, ne pose pas de questions |
| `ovila` | Ovila Saint-Onge | Le phare | le gardien, presque aveugle, voit des lumières la nuit |
| `zed` | Zed (Zacharie Lemieux) | stationnement de La Pointe | chef des Skateux ; respecte ceux qui sautent |
| `maude` | Maude | un mur de La Pointe | la muraliste ; peint la ville qu'on lui laisse |
| `trappeur` | Le Trappeur (Armand) | les bois de La Pointe | l'ermite ; collets, fronde, et pas de police |

Et deux qui existent déjà et changent : **Josée** s'appelle Josée Pelletier (Lulu est sa
sœur, ça compte dans q12), et **Marco** a une fin (m97).

### Les 109 missions

Colonnes : **Après** = prérequis (`exige` entre crochets) ; **Ce qu'on fait** = les
objectifs, dans l'ordre, avec le type en italique quand il est nouveau ; **Paie** = la
récompense, puis ce que `donne` accorde. ⏳ = la mission attend un autre jalon, et elle est
alors en `phase: 2` — **jamais un prérequis d'une autre** : un arc ne bloque pas sur ce qui
n'est pas livré. Les montants sont en dollars du jeu.

**Le tronc** — Josée ouvre la ville, Marco la referme.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| m6 | Le tour du propriétaire | Josée | m5 | aller au dépanneur, à la cantine, à l'usine, au phare — un district à la fois, en un jour ; _parler_ à Ti-Paul, Lulu, Raymonde, Ovila | 300 ; **ouvre les neuf arcs**, quatre contacts |
| m97 | Marco te vend | Marco | 3 districts libérés | l'appel : « viens au garage » — c'est un piège, 5★ à l'intro ; semer ; rattraper le taxi de Marco (fuyard) ; le coucher **ou** le laisser filer (choix dans la fin) | 0 ; le taxi de Marco garé à la planque, Marco disparu du jeu |
| m98 | Le Boss | Josée | m97 [4 propriétés, 4 districts libérés] | le maire envoie tout ce qu'il a sur le Brouillard : _survivre_ 180 s à 5★ avec les Morues, les Skateux et les Boulonneux à tes côtés ; aller à la villa ; _parler_ au maire, qui cède | 0 ; **le générique** — la ville change de couleur (M13) |
| m99 | Le dernier traversier | Capitaine Bérubé | m6 [15 000 $ en poche] | de nuit, 0★ (`sans_etoile`) : aller au quai du traversier ; _payer_ le passage ; monter ⏳ traversier (M12) — repli : la chaloupe du capitaine, un fondu au quai | 0 ; **l'autre générique** (M13) |

**Arc F — Le Faubourg après les Cravates** (12) — les commerçants respirent, Marco compte.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| f01 | Les Cravates reviennent | Ti-Guy | m6 | de nuit, six Cravates mettent le feu à la porte du bar : ramasser l'extincteur derrière le comptoir, _eteindre_ ; _survivre_ 120 s à la porte ; coucher celui qui reste (chef) | 300 ; la caisse du bar tient un jour de plus |
| f02 | Le stock de Gus | Gus | f01 | le camion de munitions de Gus est à la fourrière : le prendre de nuit (`sans_etoile`), le livrer à l'armurerie sans bosse | 350 ; munitions, armurerie à −20 % |
| f03 | La robe de Rosa | Rosa | f01 | un Chevreuil est parti avec sa livraison dans une berline de luxe : le rattraper (fuyard, en auto), ramasser la caisse, retourner | 250 ; le complet gris, Boutique Rosa à −25 % |
| f04 | Le Grand Mo sait tout | Le Grand Mo | m6 | _acheter_ trois bières à la taverne, les lui apporter ; il dit où Rocco cachait trois paquets : les ramasser | 150 ; trois paquets comptés |
| f05 | Le dernier autobus | Fern | m6 | monter dans l'autobus au terminus ; _boulots_ n=4 sorte autobus (quatre arrêts, des passagers qui montent) ; le ramener | 200 ; le boulot **autobus** au klaxon |
| f06 | Deuxième service | Bouchard | f01 | un témoin de m4 parle : _suivre_ le stool du casse-croûte jusqu'au poste sans être vu ; puis _payer_ 200 son silence **ou** l'assommer à mains nues | 300 |
| f07 | La caisse, encore | Mme Thibodeau | f04 | quelqu'un vide le kiosque : c'est un Cravate en complet gris ; _pickpocket_ pour reprendre la clé ; retourner | 200 |
| f08 | Le char de Rocco | Ti-Guy | f02, f03 | la berline de luxe de Rocco est au lot : la prendre de nuit (1★, le lot appelle), semer, la livrer au garage pour la repeindre | 0 ; **la berline de luxe** garée à la planque |
| f09 | Marco veut sa part | Marco | f06 | _proteger_ Marco, qui monte avec toi, jusqu'au kiosque, au bar et au garage pour ramasser les caisses ; deux Cravates tendent une embuscade ; sans bosse | 250 ; Marco a vu où est l'argent (ça se paie en m97) |
| f10 | La chemise hawaïenne | Rosa | f03 [tenue : chemise hawaïenne] | un client a oublié une chemise, une lettre dans la poche : la porter — **en la portant** — à Norbert, à l'Hôtel Bandini | 300 ; contact Norbert |
| f11 | Le feu chez Mado | Mado | m6 | un char brûle devant le casse-croûte : ramasser l'extincteur, _eteindre_ avant l'explosion, chrono 40 s | 150 ; l'extincteur |
| f12 | Le Faubourg te dit merci | Mme Thibodeau | f08, f09, f10 | cinq commerçants ont mis une enveloppe : _parler_ à cinq commis dans cinq boutiques du Faubourg avant la nuit, `sans_etoile` (on ne paie pas un gars recherché) | 500 ; toutes les boutiques du Faubourg à −10 % |

**Arc Q — Les Quais** (13) — Josée tient le port, Sven le veut, Mireille veut en sortir.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| q01 | La cantine de Lulu | Lulu | m6 | trois matelots mangent sans payer : les mettre dehors (tuer n=3, à la porte de la cantine) | 150 ; cantine à −25 % |
| q02 | Le poisson du vendredi | Lulu | q01 | un camion de poisson à livrer à trois poissonneries (`boutique:marine`) dans trois districts avant qu'il tourne, chrono 180 s | 250 |
| q03 | Les briseurs de grève | Gégé | m6 | Prévost fait venir des scabs par camion : l'intercepter sur le boulevard et le _detruire_ avant l'usine | 300 |
| q04 | La cargaison du Norvégien | Josée | q01 | de nuit, le cargo décharge : ramasser une caisse sur le quai pendant que quatre matelots patrouillent, `sans_etoile` ; la porter au bar | 400 |
| q05 | Mireille veut sortir | Mireille | q04 | _proteger_ Mireille, à pied, de la Brume jusqu'à l'hôtel, de nuit, pendant que Le Beau Denis te court après | 100 ; Mireille travaille à la réception — l'hôtel rapportera 10 % de plus |
| q06 | Le Beau Denis | Josée | q05 | Josée est furieuse — règle ça toi-même : coucher Denis (chef) en zone des Morues, `sans_arme` ; semer 2★ | 350 ; les Morues te laissent passer (`calme`) |
| q07 | La chambre 12 | Norbert | f10 | un client est mort dans la chambre 12 — un comptable de Prévost ; de nuit, porter le « colis » (lourd, on marche) au camion, le livrer à la cour de Ti-Loup, `sans_etoile` | 500 ; **l'Hôtel Bandini est à vendre** (10 000) |
| q08 | Le moteur du capitaine | Capitaine Bérubé | m6 | les Skateux ont volé le moteur de sa chaloupe : le ramasser dans leur stationnement (trois Skateux), le rapporter | 200 ; ⏳ eau — la chaloupe devient conduisible quand l'eau s'ouvre |
| q09 | La course des débardeurs | Gégé | q03 | _course_ en camion autour des Quais `contre` deux débardeurs, quatre points, chrono 150 s | 300 |
| q10 | Le Norvégien te reçoit | Sven | q04 | Sven propose mieux que Josée : une moto chargée au pont, à livrer au phare sans bosse, chrono 120 s | 600 ; **ferme q11** ; les Morues redeviennent méfiantes un jour |
| q11 | Le cargo brûle | Josée | q04 | _detruire_ les deux camions de Sven sur le quai (explosion, 2★), semer 3★ | 700 ; **ferme q10** ; manchette _Le Norvégien lève l'ancre_ |
| q12 | La Chef a un cœur | Josée | q06 | la mère de Josée et Lulu fait une crise aux Érables : monter dans l'ambulance, la ramasser, la livrer à l'hôpital, chrono 120 s, chocs pénalisés | 300 ; Josée amie (le bar rapporte 10 % de plus) |
| q13 | La nuit des Morues | Josée | q06, q11 ou q10 | Sven se venge : _survivre_ 120 s à l'hôtel, les Morues à tes côtés ; coucher le chef des matelots | 500 ; **Les Quais libérés** (`libere: quais`), manchette |

**Arc E — Les Érables** (13) — la banlieue, le maire, et des ados qui tournent en rond.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| e01 | Les drifts de Ti-Paul | Ti-Paul | m6 | tous les soirs, les Chevreuils font des ronds dans son stationnement : _survivre_ 60 s de nuit et en coucher trois quand ils descendent | 150 ; dépanneur à −25 % |
| e02 | La bière de Ti-Paul | Ti-Paul | e01 | un camion de bière attend au quai : le ramener au dépanneur sans bosse, à travers la ville | 250 |
| e03 | Biscuit s'est sauvé | Mme Beaulieu | m6 | le chien a filé dans les bois de La Pointe : le rattraper (fuyard, à pied) et le ramener | 80 ; Biscuit te suit dans les Érables |
| e04 | La course des Chevreuils | Jo | e01 | _course_ sur le boulevard des Érables `contre` trois Chevreuils, cinq points, chrono 90 s, le char que tu veux | 300 ; les Chevreuils respectent (`calme`) |
| e05 | Le char dans la piscine | Diane | e01 | les Chevreuils ont poussé une auto dans sa piscine : la sortir à la remorqueuse, la livrer au lot | 200 ; ⏳ terrains de banlieue |
| e06 | Le maire ne dort pas chez lui | Diane | m6 | de nuit, _suivre_ la berline du maire de la villa à… l'Hôtel Bandini, sans être vu | 300 |
| e07 | La clé de la villa | Diane | e06 | _pickpocket_ le chauffeur du maire au dépanneur ; fouiller la villa (ramasser le dossier), `sans_etoile` | 400 ; **le dossier** (sert en e11 et c02) |
| e08 | Jo a un problème | Jo | e04 | sa mère a trouvé sa cachette : deux paquets à ramasser au stationnement des Skateux avant eux, en coupé sport, chrono 200 s | 250 |
| e09 | Le barbecue | Ti-Paul | e02 | quatre poutines du camion-restaurant à livrer à quatre maisons **en vélo** avant qu'elles refroidissent, chrono 120 s | 150 |
| e10 | Diane veut la paix | Diane | e04, e07 | vider les Chevreuils : tuer n=6 sur deux coins, puis le chef — et le chef, c'est Jo ; la fin le dit à Diane | 600 ; **Les Érables libérés**, manchette |
| e11 | Le maire te reçoit | Le maire | e07 | il veut le dossier : le lui vendre (_payer_ à l'envers : 1 000 $) **ou** le garder pour Louise — le choix se fait dans le dialogue | 1 000 si vendu ; sinon 0 et **c02 s'ouvre** |
| e12 | Le selfie de Xavier | Xavier | m6 | amener un coupé sport au dépanneur et _sauter_ la rampe des Érables devant lui, 40 px de vol | 200 |
| e13 | Le char de Diane | Diane | e10 | sa berline de luxe est au lot : la reprendre sans payer (1★), semer, la livrer à la villa sans bosse | 300 |

**Arc S — La Shop** (13) — une usine, un syndicat, et les gars qu'on a mis dehors.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| s01 | Gilles à la guérite | Gilles | m6 | un Boulonneux est parti avec la remorqueuse du lot : la reprendre en zone des Boulonneux, la ramener | 200 ; rachat au lot à −20 % |
| s02 | La ferraille de Ti-Loup | Ti-Loup | m6 | _boulots_ n=3 sorte remorquage, destination la cour à ferraille | 250 ; le boulot **ferraille** : Ti-Loup achète les épaves |
| s03 | La paie de la Prévost | Raymonde | q03 | le camion de paie arrive le vendredi, deux gardiens dedans : le prendre, le livrer derrière l'usine, semer 2★ | 500 |
| s04 | Le quart de nuit | Bob Sauvé | m6 | les Boulonneux menacent le quart de nuit : _survivre_ 120 s à la porte de l'usine contre huit | 300 |
| s05 | Gros-Boulon te parle | Gros-Boulon | s02 | Ti-Loup t'a présenté : voler la berline de luxe de Prévost dans la cour de l'usine, la livrer à la ferraille pour la compacter | 400 ; **les Boulonneux te laissent vivre** (`calme`) — la seule façon de marcher dans La Shop |
| s06 | Le rat de l'usine | Raymonde | s03 | quelqu'un a vendu la liste du syndicat : _suivre_ Bob Sauvé de l'usine au bar sans être vu | 250 |
| s07 | Le camion de Prévost | Prévost | s04 | un camion de pièces doit être au quai avant le départ du bateau : livrer sans bosse, chrono 150 s — tu travailles pour les deux bords, et c'est le propos | 350 |
| s08 | Le lot se fait vider | Gilles | s01 | de nuit, trois Boulonneux volent des chars au lot : les coucher sur place | 200 |
| s09 | L'explosion | Gros-Boulon | s05 | faire sauter le réservoir de l'usine : _detruire_ le camion-citerne stationné dans la cour (au pistolet ou en le percutant), 2★, semer 3★ | 600 |
| s10 | Raymonde négocie | Raymonde | s06 | _proteger_ Raymonde, qui monte avec toi, jusqu'à la villa du maire et retour, deux gardiens de Prévost en poursuite | 300 |
| s11 | La paix des Boulonneux | Prévost | s09, s10 | Prévost plie : ramasser l'accord à l'usine, l'apporter à Gros-Boulon en zone des Boulonneux `sans_arme` | 500 ; **La Shop libérée** — les Boulonneux redeviennent des machinistes, manchette _La Prévost rembauche_ |
| s12 | Le dernier char du lot | Gilles | s08 | Gilles prend sa retraite : _boulots_ n=5 sorte remorquage en un jour, chrono jour | 0 ; **la remorqueuse** garée à la planque |
| s13 | Le prototype | Prévost | s07 | un coupé sport volé à l'usine dort au stationnement des Skateux, le pont est bloqué par les Chevreuils : le reprendre, _sauter_ la rampe du stationnement (30 px), le livrer à l'usine sans bosse | 400 |

**Arc P — La Pointe** (11) — un phare, des bois, des planches à roulettes.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| p01 | La lampe du phare | Ovila | m6 | l'ampoule est morte : en _acheter_ une à la quincaillerie la plus proche, la rapporter avant la nuit | 100 ; Ovila te connaît |
| p02 | Le pont est bloqué | Bilodeau (retraité, porte de logement) | m6 | les Skateux ont fermé le seul pont avec des cônes : ramasser quatre cônes (ce sont des armes), coucher deux Skateux | 150 |
| p03 | La murale de Maude | Maude | m6 | trois bombes de peinture à l'atelier de La Shop, à rapporter en moto, chrono 180 s | 150 |
| p04 | Zed veut un défi | Zed | p02 | _course_ **à pied** dans les sentiers `contre` Zed, cinq points, chrono 60 s — les Skateux courent à 1,3 | 200 ; les Skateux respectent (`calme`) |
| p05 | Les collets du Trappeur | Le Trappeur | p01 | quelqu'un vole ses collets : attendre la nuit dans les bois, coucher les deux Skateux qui viennent | 120 ; la fronde et 60 billes |
| p06 | Ovila voit des lumières | Ovila | p01, q04 | de nuit, une chaloupe accoste sous le phare : _suivre_ les deux matelots jusqu'à leur cabane sans être vu, ramasser la caisse, l'apporter à Josée | 300 |
| p07 | Les Bilodeau déménagent | Bilodeau | p02 | l'autobus : ramasser quatre retraités à quatre maisons du bout, les livrer à l'Hôtel Bandini, chocs pénalisés | 250 |
| p08 | La fête au stationnement | Zed | p04 | deux caisses de bière de la taverne, en camion, sans bosse ; la police arrive : semer 1★ | 200 |
| p09 | Le phare s'éteint | Ovila | p05 | des Skateux ont grimpé au phare et éteint la lampe, un bateau approche : monter (aller dedans), coucher trois Skateux, chrono 90 s | 300 ; manchette _Le phare a tenu_ |
| p10 | Le saut de La Pointe | Zed | p04 | _sauter_ la rampe du stationnement en moto, 80 px de vol, devant les Skateux | 250 |
| p11 | Zed et la Chef | Josée | p09, p10 | _proteger_ Zed, à pied puis en char, par le pont jusqu'au Brouillard ; les Chevreuils attaquent en autos sur le boulevard | 500 ; **La Pointe libérée**, manchette |

**Arc H — L'hôpital** (7) — le Dr Lachance a des secrets, et des ordonnances.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| h01 | L'ambulance de nuit | Dr Lachance | m6 | _boulots_ n=3 sorte ambulance, de nuit | 300 ; facture d'hôpital à moitié |
| h02 | Les pilules | Ginette | h01 | quelqu'un vide la pharmacie : _suivre_ le commis à sa sortie — il vend aux Chevreuils au dépanneur | 200 |
| h03 | Le docteur a une dette | Dr Lachance | h01, d01 | _proteger_ Lachance, qui monte avec toi, jusqu'au Salon Ferraro et retour ; deux ciseaux suivent | 250 |
| h04 | Le cœur | Dr Lachance | h02 | une glacière arrive par autobus au terminus : la ramasser, la livrer à l'hôpital en 90 s, n'importe quel char | 400 |
| h05 | Le patient qui s'est sauvé | Ginette | h02 | un patient a filé — c'est le chef des Cravates de m5, recousu : le rattraper (fuyard, à pied), le ramener vivant | 200 |
| h06 | Les ordonnances | Dr Lachance | h04 | trois ordonnances à porter à trois pharmacies dans trois districts, `sans_etoile` — elles sont fausses | 350 |
| h07 | La nuit des urgences | Dr Lachance | h06, 1 district libéré | la guerre de gangs a rempli l'urgence : _boulots_ n=5 sorte ambulance en un jour | 500 ; un séjour à l'hôpital gratuit |

**Arc D — La dette de Rocco** (8) — Sal coupe les cheveux, et le reste. ⚠️ L'arc **ne dépend
pas de M10** : la dette y est un compteur de partie (`p.dette`, 15 000 au départ, que `donne`
fait baisser). M10 la fera vivre en dehors des missions (intérêts, rappels, hommes de main).

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| d01 | Le barbier | Sal | m6 | Sal appelle : « Rocco me devait 15 000 » ; _acheter_ une coupe au salon — c'est la rencontre | 0 ; la dette s'affiche au carnet |
| d02 | Le premier versement | Sal | d01 | _payer_ 500 avant demain, chrono jour ; sinon deux ciseaux passent te voir | 0 ; dette −500 |
| d03 | Les Ciseaux | Sal | d02 | collecter chez Momo Taxi : _parler_ ; il refuse ; le coucher, _pickpocket_ | 300 ; dette −300 |
| d04 | La collecte du barbier | Sal | d03 | trois débiteurs dans trois districts : Ti-Paul, Lulu, Ovila ; _parler_ à chacun — et _payer_ pour eux si tu veux qu'ils t'aiment encore | 400, ou dette −800 si tu couvres les trois |
| d05 | L'avocat du Carré | Me Desjardins | d02 | Sal veut saisir le garage : ramasser les papiers de Rocco dans le coffre de la planque, les porter au bar | 0 ; casier −2 (M11 : il efface une page) |
| d06 | Sal perd patience | Ti-Guy | d04 | les ciseaux s'en prennent au garage : _survivre_ 120 s, en coucher quatre | 200 |
| d07 | Le coffre de Sal | Josée | d06 | de nuit, vider le salon : ramasser le coffre (lourd, on marche), 2★, semer, le porter au bar | 2 000 ; **ferme d08** ; Sal ennemi — des ciseaux toutes les nuits, pour de bon |
| d08 | La dernière coupe | Sal | d06 [dette 0] | Sal te coupe les cheveux gratis et te donne la bague de Rocco | 0 ; **ferme d07** ; dette payée (le fil de _Sacrer son camp_) |

**Arc C — Le Clairon** (6) — Louise veut la une. Toi aussi, parfois.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| c01 | Une photo pour la une | Louise | m6 | _proteger_ Louise, qui monte avec toi : le poste, l'usine, le quai, dans la journée, pour ses photos | 150 |
| c02 | Le scoop du maire | Louise | e11 (dossier gardé) | lui porter le dossier de la villa | 800 ; manchette _Le maire dort à l'hôtel_ |
| c03 | La source | Louise | c01 | _proteger_ son informateur, un commis du poste, du poste à l'hôtel, de nuit, deux ciseaux aux trousses | 300 |
| c04 | La manchette sur toi | Louise | c01 | elle titrera si tu fais parler de toi : monter à 3★ et les semer en moins de 90 s | 200 ; manchette _Bandini l'insaisissable_ |
| c05 | Le Clairon brûle | Louise | c02 | les hommes du maire (des Chevreuils) attaquent le bureau : _survivre_ 120 s à l'intérieur, en coucher cinq | 400 |
| c06 | L'entrevue | Louise | 3 districts libérés | _parler_ seulement : trois questions, trois réponses au choix ; le narrateur lit la une le lendemain | 0 ; manchette au choix, lue par le narrateur |

**Arc R — Roy contre Bouchard** (7) — deux polices, et il faut choisir la sienne.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| r01 | La nouvelle inspectrice | Bouchard | m6 | Roy enquête sur lui : ramasser son carnet dans son bureau au poste, de nuit, `sans_etoile` | 400 |
| r02 | Roy te convoque | Roy | r01 | elle sait que c'est toi : _parler_ — elle offre un marché ; **r03 ou r04**, pas les deux | 0 |
| r03 | Le stool, c'est toi | Roy | r02 | être au casse-croûte à midi (`heure`), à moins de six tuiles de Bouchard quand Mado lui glisse l'enveloppe : _suivre_, _survivre_ 30 s sans qu'il te voie | 500 ; **ferme r04** ; Roy amie (casier −5), le sergent n'est plus ton ami |
| r04 | Le sergent contre-attaque | Bouchard | r02 | faire partir Roy : voler son auto-patrouille, la livrer au lot sous un faux nom (⏳ eau : au fond de la baie) | 500 ; **ferme r03** ; sergent ami pour de bon (pot-de-vin toujours accepté) |
| r05 | La salle des pièces | Bouchard | r01 | tes armes confisquées dorment au poste : en ramasser trois, de nuit, 2★, semer | 200 ; les armes reviennent |
| r06 | Une affiche de moins | Roy | r03 | arracher cinq affiches _Recherché_ dans le Faubourg avant le matin | 0 ; casier −3 |
| r07 | L'auto banalisée | Bouchard | r04 | en auto-patrouille (le déguisement), « arrêter » trois ciseaux de Sal pour lui — tuer n=3 en zone du Faubourg, sans étoile tant que tu es au volant | 400 |

**Arc T — Les petites jobs** (15) — des gens ordinaires, un peu partout. ⚠️ Le donneur est un
**archétype** (`pieton:<slug>@district:<slug>`), pas un personnage : le jeu en pose **un par
jour**, tiré parmi celles qu'on n'a pas faites, près d'un lieu du district, avec la bulle
« Hé! ». Ses répliques sont dites par les voix des passants. Une par jour, pas plus : ce
sont des rencontres, pas un tableau de bord.

| # | Titre | Qui, où | Ce qu'on fait | Paie |
|---|---|---|---|---|
| t01 | Mon char est au lot | banlieusard, Érables | reprendre son auto au lot (payer ou voler), la livrer chez lui | 80 |
| t02 | Le lunch des gars | débardeur, Quais | trois hot-dogs au kiosque, à rapporter avant midi | 30, et un hot-dog |
| t03 | Un lift au terminus | dame du Faubourg | la conduire au terminus en 60 s, sans un choc | 40 |
| t04 | Mon vélo | ado, La Pointe | un Skateux a son vélo : le reprendre, le lui ramener | 25 |
| t05 | La sacoche | passante, Faubourg | un itinérant est parti avec sa sacoche : le rattraper à pied | 50 |
| t06 | La commande de la taverne | commis, taverne (partout) | deux caisses de bière au quai, en camion | 90 |
| t07 | Le p'tit est perdu | mère, partout | trouver l'enfant (intouchable, il se cache), _proteger_ jusqu'à sa mère | 60 |
| t08 | Une job de bras | ouvrier, La Shop | trois boîtes à porter dans l'usine (lourdes, on marche) | 45 |
| t09 | La tournée du Clairon | marchand de journaux, Faubourg | six journaux à six portes, en vélo, 90 s | 60 |
| t10 | Le quart commence | machiniste, La Shop | le conduire à l'usine avant le quart, chrono 45 s | 40 |
| t11 | Le feu de camp | promeneur, La Pointe | un feu dans les bois : trouver un extincteur, _eteindre_ | 50 |
| t12 | Une course avec le livreur | livreur, Faubourg | _course_ en moto jusqu'à l'hôpital `contre` lui | 70 |
| t13 | La pelle du vieux | itinérant, Quais | une Morue a sa pelle : la reprendre | 20, et la pelle |
| t14 | Les mariés | dame, Érables | les conduire, à deux, en berline de luxe jusqu'au phare, sans bosse | 120 |
| t15 | L'autobus manqué | passant, terminus | il rate son quart à l'usine : taxi, chrono 90 s | 40 |

**Cinq défis de plus**, un par district, sur le modèle des trois qui existent (un panneau,
un chrono, une prime, une fois) : _Le tour des Quais_ (camion, 3 tours < 2:30) · _La descente
des Érables_ (vélo, du dépanneur à la villa < 0:45, sans tomber) · _Le drift de La Shop_
(coupé sport, dix stationnements traversés < 1:30) · _Le sentier de La Pointe_ (moto, six
points dans les bois < 1:00) · _Le port à port_ (n'importe quoi, du quai au phare < 1:20).
250 $ chacun.

### Ajouté le 15 sept. 2026 — vingt missions de plus, après une tournée du net

_Demande de Martin :_ « regarde sur le net pour des idées de missions et tu peux en ajouter ou
modifier ce qui est dans le plan. »

Ce qui est ressorti de la comparaison avec les classiques vus d'en haut (GTA 1 et 2,
Chinatown Wars) : le catalogue d'ici **couvre déjà leurs verbes** — voler un véhicule précis,
filer quelqu'un, protéger, détruire, livrer au chrono, tenir un siège. Trois formes leur
appartiennent encore, et les voici. Les activités qui n'en sont pas (frénésies, liste du quai,
boulots gradés) ont leur propre fiche, plus haut.

**Arc I — L'Île-aux-Corneilles** (8) — la fiche de l'île est plus haut ; voici ce qu'on y
fait. Deux personnages de plus : **Sœur Jeanne** (`jeanne`, la dernière religieuse de la
chapelle) et **Léo Cyr** (`leo`, l'insulaire qui garde le hangar et ne pose pas de questions).

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| i01 | Le moteur tourne | Capitaine Bérubé | q08 | la chaloupe marche enfin : lui porter sa caisse d'outils **sur l'île**, et y mettre le pied pour la première fois | 120 ; l'île au carnet, contact Léo |
| i02 | La cloche de Sœur Jeanne | Sœur Jeanne | i01 | la cloche de la chapelle a fini chez Ti-Loup : la racheter (_payer_ 200) ou la reprendre, et la ramener par l'eau (lourde, on marche) | 150 ; **on dort à la chapelle** — une deuxième sauvegarde, à l'autre bout de la baie |
| i03 | Le hangar sans nom | Josée | q04, i01 | de nuit, `sans_etoile` : deux caisses à ramasser dans le hangar de Sven et à charger sur le bateau | 400 |
| i04 | Laisser refroidir | Léo | i01 | y amener un char **chaud** (3★ au départ), le laisser une journée entière, revenir le chercher | 0 ; le char repeint, les plaques changées — et la règle de l'île comprise |
| i05 | L'usine à poisson | Sœur Jeanne | i02 | des squatteurs ont mis le feu à l'ancienne usine : _eteindre_, puis en coucher trois | 200 |
| i06 | Le dernier bateau du Norvégien | Josée | i03, q11 | _detruire_ le bateau de Sven à quai, 3★ **sur l'eau** — et la police ne nage pas vite | 500 |
| i07 | Le tour de l'île | Léo | i04 | _course_ en bateau autour de l'île `contre` Léo, six points ⏳ bateau (repli : à la nage, trois points) | 200 |
| i08 | La cache de Rocco | Ti-Guy | i01, d05 | les papiers du coffre parlaient d'une île : ramasser la cache sous la chapelle, 2★ (quelqu'un d'autre la cherchait) | 1 200 |

**Le casse — arc X, _Le coup de la Caisse populaire_** (4) — la forme que le plan n'avait pas :
**trois préparatifs, puis le coup, et ce qu'on a préparé change le coup**. C'est le patron des
casses modernes, et il ne demande **aucun type neuf** : `exige` fait tout le travail.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| x01 | Le repérage | Josée | d06, q11 ou q10 | la caisse populaire du Faubourg : y aller à trois heures différentes (matin, midi, soir) et _suivre_ le convoyeur jusqu'à son camion | 0 ; **ouvre x02, x03, x04** |
| x02 | Le char qui part vite | Josée | x01 | voler un **coupé sport**, le faire repeindre au garage, le garer à la planque | 0 ; le char à la planque (`exige` de x04) |
| x03 | Le linge propre | Rosa | x01 | une tenue de livreur oubliée à la boutique : la prendre et la porter | 0 ; la tenue (`exige` de x04) |
| x04 | Le coup | Josée | x01 [ce qu'on a préparé] | entrer à la caisse, _survivre_ 60 s, ramasser les sacs, semer 4★, livrer au bar | 2 500 ; **ferme d08** (Sal prend sa part) |

⚠️ **Sans les préparatifs, x04 se joue quand même — plus mal**, et c'est tout l'intérêt : sans
la tenue, on entre à 2★ au lieu de 0 ; sans le coupé sport, la police tient la poursuite ; sans
arme à feu, les 60 secondes se font aux poings. Le juge : la mission est **finissable** dans
les quatre combinaisons, et chaque préparatif manquant se **dit** à l'intro.

⚠️ **La caisse populaire est un cinquième lieu spécial** — le plan s'en tenait à quatre
exprès (une pièce à dessiner, une porte, un juge). Celui-là se paie : c'est le seul intérieur
où l'on se bat contre le temps.

**Huit missions de plus dans les arcs existants** — chacune vient d'un verbe des classiques
que Bandini n'utilisait pas encore :

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| f13 | Les volontaires | Mado | f11 | trois feux dans la nuit, aux quatre coins du Faubourg : _eteindre_ chacun avant qu'il gagne la façade | 200 ; **le boulot pompier volontaire** |
| q14 | La liste du Norvégien | Sven (ou Ti-Loup si q11) | q10 ou q11 | quatre modèles sur l'ardoise du quai, à livrer sans bosse, un par jour | 250 ; **la liste du quai** (l'activité) |
| e14 | C'était un accident | Diane | e07 | la berline du maire doit finir dans sa propre piscine, et personne ne doit t'avoir vu (`sans_etoile`) | 300 ; Louise a sa photo |
| s14 | La casse à Ti-Loup | Ti-Loup | s02 | trois **autos-patrouilles** au compacteur dans la même nuit — chacune coûte au moins 1★, et il faut semer entre les deux | 450 |
| p12 | Le radeau de Zed | Zed | p04, i01 | les Skateux veulent l'île : leur amener un bateau au quai de La Pointe, sans le couler | 150 |
| h08 | La traverse de l'urgence | Dr Lachance | h04, i01 | quelqu'un s'est blessé sur l'île : y aller, le ramasser, le ramener à l'hôpital, chrono 200 s ⏳ traversier (repli : la chaloupe) | 250 |
| r08 | La patrouille de Roy | Inspectrice Roy | r03 | cinq fuyards rattrapés en auto-patrouille, en une semaine de jeu — le boulot patrouille, avec sa bénédiction | 250 ; casier −2 |
| d09 | Un compte sur l'île | Sal | d04, i01 | Léo doit 800 à Sal : _parler_, puis choisir — le coucher, ou payer pour lui | 250, ou dette −800 |

**Et deux choses qui changent dans ce qui existait :**

- **m99 _Le dernier traversier_ a enfin une dernière image.** Le traversier ne s'en va plus
  dans un fondu au noir : il **passe devant l'île**, Sœur Jeanne sonne sa cloche si on la lui a
  rendue (i02), et la ville rapetisse derrière. Rien de neuf à écrire — un trajet, et la caméra
  qui reste sur le quai.
- **p02 _Le pont est bloqué_ cesse d'être une fiction.** Les cônes des Skateux deviennent une
  **vraie barrière** du catalogue (fiche des zones conditionnelles) : fermée aux chars, jamais
  aux jambes, et forçable en défonçant. La mission ne pose plus le décor, elle **ouvre la
  barrière**.

### Le compte, et l'équilibre

- **134 missions** (5 + 109 + 20), **8 défis**, **11 arcs**, **36 personnages**, 3 piétons de
  mission et un chien. Les missions **paient 35 990 $** si l'on additionne tout, un peu
  moins dans une vraie partie (les choix en ferment) — de quoi rembourser Rocco (15 000)
  **ou** acheter les quatre propriétés (17 800), jamais les deux : le reste vient des
  boulots, des propriétés et de ce qu'on vole.
  - ⚠️ **Et voilà exactement ce que vingt missions de plus coûtent à l'équilibre**, compté :
    elles paient **7 370 $** (368 en moyenne, contre 340 pour les 109 — les deux gros coups,
    le casse et la cache, en portent la moitié à eux seuls). La somme passe donc de 28 620 à
    **35 990**, soit **2,4 fois la dette** : la borne absolue du juge (24 000–32 000) ne
    survit pas à un catalogue qui grossit, et il faut le dire au lieu de le découvrir.
    - Ce qui la remplace est un **rapport**, parce que c'est lui qui porte le sens :
      **la somme reste sous 2,4 fois la dette**, et surtout **une vraie partie reste sous
      32 800** — le prix des deux fins ensemble (15 000 de dette + 17 800 de propriétés).
    - Et c'est tenable sans rien couper, parce que les **choix ferment** : q10/q11, r03/r04,
      d07/d08, e11, et maintenant x04 qui ferme d08. Une partie qui va au bout en perd
      environ 3 000 en chemin — donc ≈ 33 000 encaissés pour 32 800 à dépenser. ⚠️ **C'est
      serré exprès**, et c'est le juge à écrire : la partie la plus gourmande possible ne doit
      pas dépasser le prix des deux fins de plus de 5 %.
- **Chaque type d'objectif est utilisé au moins trois fois**, sinon il ne valait pas un
  type. Chaque district a **au moins dix missions** qui s'y passent, et chaque heure
  (jour, soir, nuit) en a.
- **Les fins tiennent.** _Le Boss_ demande quatre districts libérés : le Faubourg (m5), Les
  Quais (q13), Les Érables (e10), La Shop (s11), La Pointe (p11) — cinq possibles, quatre
  suffisent. _Sacrer son camp_ demande 15 000 $, et l'arc D ne l'exige pas : on peut partir
  sans payer Rocco, c'est même le propos de cette fin-là.
- ⚠️ **Le budget de voix** : ≈ 109 × 7 répliques × 75 caractères ≈ **57 000 caractères**,
  dix fois la v1, générés **par tranche** et jamais tous d'un coup. Les tests de
  `test_missions.py` qui bornent le catalogue à 30–60 voix et 4 000 caractères deviennent
  des bornes **par arc** ; la borne globale monte à 70 000. Et la règle de M6 tient : une
  réplique dont le fichier manque s'affiche sans voix.
  - ⚠️ **Recompté le 16 sept. 2026, et les 70 000 ne tiennent plus.** Le compte ci-dessus
    date d'avant les vingt missions de l'île et du casse : 129 missions neuves × 7 × 75 font
    déjà ≈ 68 000. Et la mise en scène ajoute **une réplique `pendant` par mission** :
    129 × 8 × 75 ≈ **77 000**, plus les cinq de la v1 ≈ **80 000 caractères**. La borne
    globale monte donc à **85 000** ; les bornes par arc gagnent une réplique par mission.
    ⚠️ La mise en scène, elle, ne coûte **aucune voix de plus** hors de `pendant` : une fin
    passée au combiné ne se régénère pas (le combiné est un filtre joué), et une `coupe` fait
    parler le donneur chez lui avec les mots qu'il avait déjà.

### Comment on le livre — quatre tranches, chacune jouable et déployée

⚠️ **Une tranche livre ses missions mises en scène, ou ne se livre pas.** Chaque mission
d'une tranche arrive avec ses deux scènes, ses répliques à chaque temps et leurs voix ; le juge
du catalogue (« Les missions mises en scène ») refuse la tranche sinon. C'est aussi ce qui
fixe son coût : écrire une mission, c'est écrire sa scène **en même temps** que ses mots —
jamais une passe « animations » à la fin, qui ne viendrait pas.

1. **Le moteur, et le Faubourg** (taille 2) : les neuf types, `exige`, `ferme`, `donne`
   étendu, les résolveurs de lieux, les dialogues **et les scènes** hors paquet, le
   téléphone qui trie ; m6 et l'arc F comme banc d'essai — douze missions qui utilisent
   tout. ⚠️ Le carnet (P2) doit être livré avant : sans lui, treize missions disponibles sont
   treize appels qu'on oublie. ⚠️ **Et les missions mises en scène (P2) aussi** : douze
   missions écrites sans le vocabulaire de plans s'écriraient deux fois.
2. **Les trois districts** (taille 2) : arcs Q, E, S et leurs dix-neuf personnages, les
   quatre lieux spéciaux, les trois piétons de mission, `libere` et `calme`.
3. **La Pointe, l'hôpital, la dette, le Clairon, la police** (taille 2) : arcs P, H, D, C,
   R ; Biscuit ; les choix (`ferme`).
4. **Les petites jobs, les défis et les fins** (taille 2) : arc T, les cinq défis, m97 à
   m99 — cette tranche-là **est** M13, qui garde les génériques et la ville qui change de
   couleur.
5. **L'île et le casse** (taille 2, ajoutée le 15 sept. 2026) : l'île et ses barrières
   d'abord (les deux fiches plus haut), puis l'arc I, l'arc X et les huit missions des autres
   arcs. ⚠️ Elle vient **en dernier** et elle ne bloque rien : aucune mission des quatre
   premières tranches n'en dépend, et les deux fins tiennent sans elle.

### Juges

- **Le catalogue** : chaque mission a un donneur placé (jamais deux à la même porte), des
  lieux que `resoudre()` connaît, des types connus, des objectifs en majuscules de moins de
  60 caractères ; les prérequis sont sans cycle ; **une mission ⏳ n'est le prérequis de
  rien** ; chaque arc est atteignable depuis m6 ; chaque paire `ferme` ferme dans les deux
  sens et ne rapporte pas plus du double d'un côté ; la somme des récompenses reste dans sa
  fourchette ; chaque type sert au moins trois fois ; chaque district a ses dix missions.
- **Les fins** : un test rejoue le catalogue en respectant prérequis, `exige` et `ferme`, et
  atteint m98 **et** m99 (pas dans la même partie : m98 exige quatre propriétés et m99 quinze
  mille dollars en poche, le test le prouve).
- **Les voix** : un slug par réplique, ≤ 110 caractères, ≤ 2 phrases, un personnage connu
  avec une voix nommée ; jamais deux personnages de même voix dans un même dialogue ; le
  compte par arc et le total sous leurs bornes.
- **Les scènes** : les juges de « Les missions mises en scène » tournent sur tout le
  catalogue — deux scènes et une réplique `pendant` par mission, des plans de types connus
  et des lieux qui se résolvent, aucune fin dite par un absent, aucun slug de mission dans
  `histoire.js` ; le singe **regarde** les scènes de ses vingt missions et n'en trouve
  aucune qui ne se termine pas, qui tire un dé ou qui déplace le joueur ; chaque type de plan
  sert au moins trois fois, sinon il ne valait pas un type.
- **Le paquet** : sans les dialogues ni les scènes, il reste sous 600 Ko bruts et 70 Ko gzip ;
  `/api/dialogue/<slug>` répond 304 au deuxième passage et 404 pour un slug inconnu.
- **Le banc** : m6 de bout en bout ; **une mission par nouveau type**, jouée jusqu'à la
  récompense ; le singe qui prend vingt missions au hasard et ne trouve **aucune mission
  morte** (un objectif qu'on ne peut pas commencer depuis l'état où on le reçoit — un char
  qui naît dans un mur, un fuyard sans rue) ; le téléphone ne sonne jamais deux fois dans la
  même demi-journée, jamais en mission, jamais à 3★ ; une mission fermée n'apparaît ni au
  téléphone ni au carnet ; `libere` retire la zone du gang et `calme` retire l'hostilité, et
  les deux survivent à une sauvegarde.
- **Martin** : finir un arc par district au téléphone ; ne jamais se demander quoi faire
  (le carnet le dit) ; entendre trente-quatre personnes différentes sans qu'une seule
  paraisse en avoir la voix d'une autre ; **voir** chaque mission commencer et finir — un
  geste, un lieu montré, ce qu'on gagne — sans qu'aucune ressemble à la précédente.

## Notes

demande de Martin : « plus de 100 missions avec les personnages existants et de nouveaux
personnages, partout sur la carte ». **109 missions de plus** en 9 arcs, 34 personnages, 9
types d'objectifs de plus — et rien d'autre : le moteur apprend neuf verbes, le reste est du
catalogue.

- ⚠️ Le carnet passe avant (cent missions sans carnet, c'est cent appels qu'on oublie) ; M13
  en devient la dernière tranche.
- ⚠️ **Depuis le 16 sept. 2026, chaque mission vient avec ses scènes et ses dialogues**
  (« Les missions mises en scène », qui passe avant) : une tranche livre ses missions mises
  en scène, ou ne se livre pas
