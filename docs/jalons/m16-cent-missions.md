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
  `/api/mission/<slug>` **quand le téléphone sonne**, avec un ETag comme le reste. Une
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

⚠️ **Cette table date du 18 sept. 2026 et ne se tient plus à jour** : depuis, Alexandre Boutin, Premium
Male teacher, Claudia et Caroline sont données, et **Frederic** (québécois d'origine, arrivé au compte
ensuite) et **Clara Dupont** sont **réservées au scanner de police** (25 sept. 2026). Qui parle avec
quoi se lit par `uv run python scripts/audio_elevenlabs.py --libres`, qui interroge le compte et le
jeu à la fois ; `audio.VOIX_RESERVEES` dit ce qui ne se partage pas.

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

⚠️ **Martin, 25 sept. 2026 : « Tu peux utiliser des voix non québécoises, parce qu'elles sont
souvent assez bonnes. »** L'ancienne règle ne permettait une voix de France ou multilingue que
si l'accent faisait le personnage, ou après une audition — et elle poussait vers une voix
générée, qui coûte une des huit places à soi. Elle passe donc **avant** la voix générée, sans
audition préalable : Martin écoute à la génération, comme pour toutes les autres.

1. **Une voix québécoise d'origine** pour quiconque est né dans la ville, **s'il en reste une
   libre** (`scripts/audio_elevenlabs.py --libres` ; au 25 sept. 2026, il n'en reste plus une
   seule de femme, ni au compte ni dans la bibliothèque).
2. **Une voix non québécoise du compte** — de France ou multilingue — sinon. Elle est souvent
   assez bonne ; choisis-la pour son **grain** et son **ton** (`docs/jeu-d-acteur.md`), lis son
   français dans `verified_languages`, et mesure-la contre les autres pour l'égalisation. Quand
   l'accent **fait le personnage** (Sven Haugen, le Norvégien), c'est même le premier choix.
3. **Une voix générée** (_Voice Design_, comme les deux annonceurs) seulement si rien du
   compte ne va : décrite en français, « accent québécois marqué ». Le palier _starter_
   tient **dix voix à soi, deux sont prises** : huit places. Le serveur MCP n'a pas l'outil ;
   Martin les crée dans l'interface, ou le serveur l'apprend.
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
  `/api/mission/<slug>` répond 304 au deuxième passage et 404 pour un slug inconnu.
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
- **21 sept. 2026 : dix missions de plus, et huit juges de banc.** `f04` (Le Grand Mo,
  `acheter`), `f05` (Fern, `boulots` — l'autobus gagne son propre `economie.BOULOTS`/`SORTES`),
  `f06` (Bouchard, `suivre`+`payer`), `f07` (Mme Thibodeau, `pickpocket`), `f09` (Marco,
  `proteger`), `f11` (Mado, `survivre`+`tuer` — pas `eteindre`, voir plus bas), `h01`
  (Dr Lachance, `boulots`), `p01` (Ovila, `acheter`+`tuer`), `q03` (Gégé, `detruire`), `e12`
  (Xavier, `sauter`) — `tests/test_dix_missions_js.py` joue huit des neuf types neufs de bout
  en bout, sur le modèle de `test_cinq_missions_js.py`. Six personnages de plus
  (`docs/personnages/`), tous posés à un lieu **déjà dessiné** (`carte.SPECIAUX`) : aucune
  pièce neuve cette tranche-ci.
  - ⚠️ **Trois bogues trouvés en écrivant les juges, corrigés dans `histoire.js`** :
    `proteger` n'avançait jamais (aucune condition de succès — corrigé : comme `aller`, via
    `lieu`+`rayon`, la cible toujours vivante) ; `pickpocket` guettait `assomme`, que
    `Combat.pickpocket` (un vol par-derrière réussi) ne produit **jamais** — il laisse la
    victime `fuit`, poches vides (corrigé : on guette `argent <= 0`) ; et `retourner` ne se
    règle pas avec un donneur **dedans** (`point:`) — il ne pose jamais de `Histoire.donneur`
    en ville (`f06`, `h01` finissent sur leur dernier objectif utile à la place, comme `m51`
    avant elles). Le GPS (`cible()`) et le compteur du HUD (`ligneObjectif()`) apprennent les
    neuf types neufs.
  - ⚠️ **`eteindre` reste sans mission.** `Incendies.feuActif()` est un tirage **déterministe
    par heure de la ville** (`jour:heure`, `carte.incendies.regle`) — rien ne permet à une
    mission d'allumer SON feu à elle. Lui donner un vrai porteur demande un feu **scopé à la
    mission** (son propre `feuActif`-like, éteint par le même jet), pas encore écrit.
  - ⚠️ **`FORMES_DE_LIEU`** (Python) apprend `boutique`, `district`, `rampe` : les résolveurs
    de lieux de cette tranche existaient déjà côté JS (`Histoire.resoudre`) mais la scène par
    défaut, qui les cite, n'était pas jugée pour eux — deux scènes par défaut (`f04`, `p01`)
    sautaient sans lieu à montrer avant ce correctif.
- **22 sept. 2026 : dix missions de plus, et la foire devient un vrai lieu de mission.**
  `f02` (Gus, armurier neuf), `f03` (Rosa, couturière neuve), `f08` (Marco, la berline de
  Rocco), `q04` (Josée, `sans_etoile` — première mission à l'exercer vraiment), `e02`
  (Ti-Paul), `h02` (Ginette, infirmière-chef neuve, `suivre`+`pickpocket`+`retourner`), `r01`
  (Bouchard, `sans_etoile` une deuxième fois — et un fuyard à pattes plutôt qu'un objet posé
  dedans : `ramasser` ne connaît QUE le patron du fuyard, jamais un objet statique), `s01`
  (Gilles, gardien de fourrière neuf, `zone:boulonneux`), `p13`/`p14` (le Bonimenteur,
  personnage neuf — comme Mo/Fern/Mado/Gégé/Xavier avant lui — posé DANS l'enceinte de la
  foire). Cinq personnages de plus, tous à un lieu déjà dessiné (`carte.SPECIAUX`), sauf le
  Bonimenteur.
  - ⚠️ **La foire prend vie, à la demande de Martin (« profite-en pour améliorer la foire »)** :
    un nouveau résolveur de lieu, `ou: "foire"` (`histoire.js::lieuFoire`/`poserDonneurFoire`,
    même patron que `lieuPont` pour la barrière du pont — aucun changement à `app/carte.py`,
    les coordonnées voyagent déjà dans l'export JSON). C'est le premier personnage de mission
    posé DANS l'enceinte, hélable et vivant en ville — contrairement à un donneur `point:`, un
    `retourner` le retrouve, prouvé par `p13`. Les kiosques de nourriture restent du décor, les
    trois manèges décoratifs (carrousel, tasses, chaises volantes) restent non montables : la
    règle du jalon de la foire (« aucun manège n'est montable ») tient telle quelle.
  - ⚠️ **`s02` (Ti-Loup, la cour à ferraille) reste écartée** : son lieu fait partie des quatre
    lieux spéciaux encore pas dessinés — aucune pièce neuve cette tranche-ci non plus. `s01`
    (Gilles) le remplace dans l'arc S.
  - ⚠️ **`ramasser` ne pose JAMAIS d'objet statique.** Découvert en concevant `q04`/`r01` :
    `Histoire.poser()` ne fait naître une `caisse` que par le mécanisme du fuyard qui tombe
    (m2/m50/m97/f03) — un `ramasser` sans `cible: "fuyard"` ne trouve jamais rien à ramasser.
    `q04` et `r01` sont donc devenues un vol de camion (`monter`+`livrer`) et un fuyard à
    pattes, plutôt que la fouille statique prévue au plan d'origine.
  - ⚠️ **Ti-Guy ne peut plus être donneur après m1** (`parti_apres`) : `Histoire.creerDonneurs`
    le retire de la ville pour de bon une fois m1 faite — `f08` (prévue pour lui dans le plan
    d'origine) donne plutôt à Marco, toujours vivant `porte:garage`.
  - Trois juges de banc de plus (`tests/test_dix_missions_deux_js.py`) : les deux missions de
    la foire (`p13` prouve le donneur `foire` vivant + `retourner` ; `p14` reprend `proteger`)
    et `sans_etoile` (`q04`, jamais jouée avant cette tranche). Les sept autres missions ne
    réutilisent que des types déjà prouvés — couvertes par `scripts/verifier_missions.py`.
- **24 sept. 2026 : les dialogues et les scènes sortent du paquet — en cours.** Ce n'est plus
  une précaution, c'est une réparation : le paquet des définitions pèse **369 224 octets bruts
  pour un plafond de 250 000** et **75 138 octets gzip pour 54 000** (mesure du 24 sept.), et le
  juge est rouge. Trois sessions l'ont grossi le même jour, chacune sans voir les deux autres.
  Le remède est celui écrit ici le 16 sept. : le **catalogue** reste dans le paquet (c'est ce
  que le carnet, le GPS et le téléphone lisent), les **répliques et les scènes** partent par
  `/api/mission/<slug>` avec son ETag, sur la route qu'`app/routes.py` a déjà (`_revalide`).
  - ⚠️ **Une requête par mission, et elle arrive avant la première voix de toute façon** :
    `Son.Voix.chargerHistoire(mission)` télécharge déjà les mp3 d'une mission quand on
    commence à lui parler. Le texte prend la même route, au même moment.
  - ⚠️ **Sauf qu'un texte ne peut pas arriver en retard**, lui. Une voix qui manque laisse la
    réplique s'afficher (`Voix.attendue` la dit quand elle arrive) ; un dialogue qui manque
    n'a **rien** à afficher. Les deux portes doivent donc attendre : le téléphone qui sonne, et
    le donneur qu'on hèle.
  - ⚠️ **Et hors ligne**, le travailleur garde les dialogues **à l'usage**, comme les mp3 — pas
    dans la coquille : cent adresses dans la coquille, ce serait cent requêtes à l'installation
    pour un joueur qui en jouera trois.
  - ✅ **Livré le 24 sept. 2026.** Mesures, avant et après, prises sur la même
    construction :

    | | bruts | gzip | plafond |
    |---|---|---|---|
    | le paquet, avant | 369 224 | 75 138 | 250 000 / 54 000 — **rouge** |
    | le paquet, après | **239 190** | **53 097** | vert, de 10 810 et de **903 octets** |
    | les 36 dialogues | 131 956 en tout | — | 3,7 Ko chacun, le plus gros 5,4 |

    Ce qui est parti : les **répliques**, les **scènes**, et — trouvé en mesurant —
    la **déclaration des voix** de chaque mission. `audio.histoire` annonçait 485 mp3 au
    premier écran pour en jouer sept ; il en reste **65**, les trois bancs qui
    n'appartiennent à aucune mission (le journal du matin, l'ouverture, le mot de repos
    de chaque personnage). Les 420 autres voyagent avec le dialogue de leur mission :
    même règle, même route, même instant.
  - ⚠️ **SANS LES VOIX, LE DÉCOUPAGE NE SUFFISAIT PAS.** Répliques et scènes seules
    laissaient le paquet à 294 727 octets bruts — encore 45 Ko au-dessus. `audio` faisait
    **47 % du paquet** à lui seul, et personne ne l'avait regardé : la tranche ne serait
    pas allée au bout de sa propre raison d'être.
  - ⚠️ **ET LA MARGE GZIP EST DE 903 OCTETS.** Le catalogue reste dans le paquet et pèse
    **170 octets gzip par mission** : cinq de plus et il repasse au-dessus. Ce qui sort
    ensuite est déjà mesuré : les **`objectifs`** (18 391 bruts / 4 319 gzip des 26 158 /
    6 074 du catalogue — ils ne servent qu'à partir de `commencer()`, donc après le
    dialogue, donc par la même porte), puis les **notes de `musique.py`** (39 314 bruts /
    7 823 gzip, et la musique se charge déjà par district). Les 109 missions de M16 ne
    tiennent pas sans le premier.
  - ⚠️ **`m.dialogue.appel.length` A DISPARU DU TÉLÉPHONE**, et c'était une tautologie
    que rien ne tenait : la seule mission sans réplique d'appel est la première, et elle
    n'a pas de prérequis. `histoire.js` choisit maintenant sur les prérequis seuls, et un
    juge tient les deux ensemble dans les deux sens (une mission avec des prérequis a un
    appel ; une sans prérequis n'en écrit pas, personne n'irait le chercher).
  - ⚠️ **QUATRE PORTES, PAS UNE.** On croyait n'en avoir qu'une (parler au donneur) ;
    il y en a quatre, et les trois autres se voient mal : le **téléphone** (il ne doit pas
    sonner pour une mission qui n'a rien à dire — la réplique d'appel arrive pendant
    `DELAI_APPEL`), une **partie reprise en pleine mission** (sauvegardée bien après son
    intro : elle a `partie.mission` et pas une ligne de dialogue, et tout ce que `maj()`
    lit ensuite le cherche dedans), et le **menu de triche** (`demarrer`). La marge, elle,
    se gagne ailleurs : la **bulle du donneur** demande son texte dès qu'elle s'allume, et
    il est visible à plusieurs secondes de marche.
  - ⚠️ **HORS LIGNE, À L'USAGE — jamais dans la coquille.** `addAll` les prendrait tous à
    l'installation : trente-six requêtes pour un joueur qui jouera trois missions, cent
    quarante-cinq quand M16 sera là. Le travailleur les garde par leur **chemin sans la
    requête** (`?e=` change à chaque construction, et hors ligne un dialogue d'avant-hier
    vaut infiniment mieux qu'une mission qui ne peut pas commencer — un texte n'a pas de
    repli, contrairement à un son), et « tout télécharger » les prend **d'abord** : 132 Ko
    contre 14 Mo de son, pour que celui qui veut jouer hors ligne ait toutes ses missions
    jouables même si le téléchargement des sons s'arrête en chemin.
  - ⚠️ **LE BANC POSE LES DIALOGUES D'AVANCE, et un juge le dit à voix haute.**
    `o.frame()` est synchrone et une réponse de `fetch` arrive sur une micro-tâche : entre
    deux images du banc il n'y en a aucune. Une centaine de juges qui jouent une mission
    de bout en bout devraient chacun devenir asynchrones pour attendre un texte qui, dans
    le vrai jeu, est arrivé pendant qu'on marchait. Le chemin du téléchargement a donc ses
    juges à lui, qui partent d'un **catalogue nu** (`banc(..., poser_les_dialogues=False)`)
    et attendent vraiment.
  - ⚠️ **ET DEUX JUGES QUI SERAIENT DEVENUS VERTS EN NE REGARDANT PLUS RIEN**, trouvés
    par la suite complète : « le `jeu=` ne part pas au navigateur » et « le navigateur
    reçoit l'humeur et jamais le jeu » lisaient les répliques **dans le paquet**. Il n'y
    en a plus une seule : ils auraient passé pour toujours, sur zéro réplique. Ils lisent
    maintenant les dialogues, et une mutation qui laisse le `jeu=` passer les rougit tous
    les deux (plus celui de la route).
  - ⚠️ **UN JUGE QUI PASSAIT POUR RIEN**, trouvé par la mutation : celui des deux coups
    d'ACTION mesurait `cinema.i`, qui vaut zéro que l'intro se joue une fois ou trois —
    la garde neutralisée, il restait vert. Il compte maintenant **les demandes de voix**
    de la première réplique : ce qu'on entendrait vraiment, trois fois.
  - **Juges** (12 neufs ; treize mutations, toutes rouges) : `/api/mission/<slug>` rend
    son ETag, revalide en 304 (faible compris) et **404 pour un slug inconnu** ; le paquet
    ne porte plus ni répliques, ni scènes, ni voix de mission, et le catalogue y reste en
    entier ; chaque mission a son dialogue, aucune voix ne se déclare deux fois ni ne
    tombe entre les deux moitiés ; toute mission à prérequis s'annonce au téléphone, et
    l'inverse ; le travailleur nomme les trente-six chemins, ne les met pas dans la
    coquille, et son empreinte change quand une mission s'ajoute ; au banc, sur un
    catalogue nu : la bulle du donneur demande son texte (**une fois**, pas soixante par
    seconde), la porte attend qu'il arrive puis pose la mission et déclare ses voix, deux
    coups d'ACTION ne la posent pas deux fois, un réseau qui tombe ne ferme pas la mission
    pour le reste de la partie, le téléphone reste muet tant qu'il n'a rien à dire, une
    partie reprise en pleine mission redemande son texte — et le banc pose bien les
    dialogues par défaut, sans quoi les cent autres juges ne prouveraient plus rien.
- **24 sept. 2026 : et les `objectifs` sortent avec le reste — la route se renomme.** La
  tranche d'il y a une heure laissait **903 octets de marge gzip** et 170 octets par mission :
  cinq missions avant de repasser au-dessus. Les `objectifs` pesaient **18 391 octets bruts /
  4 319 gzip** des 26 158 / 6 074 du catalogue — les deux tiers — et ils ne servent qu'à
  partir de `commencer()`, donc **après** l'intro, donc après le dialogue. La même porte, le
  même instant.

  | | bruts | gzip | par mission (gzip) |
  |---|---|---|---|
  | le paquet, la veille | 369 224 | 75 138 | 170 |
  | après les répliques, les scènes et les voix | 239 190 | 53 097 | 170 |
  | **après les objectifs** | **220 367** | **48 971** | **53** |

  **94 missions de marge au lieu de cinq.** Les 109 de M16 y sont presque ; le reste viendra
  des notes de `musique.py` (39 314 bruts / 7 823 gzip, et la musique se charge déjà par
  district).
  - ⚠️ **`/api/dialogue/<slug>` EST DEVENUE `/api/mission/<slug>`.** Une route qui rend des
    objectifs ne s'appelle pas un dialogue. Renommée le jour même, avant que quoi que ce soit
    s'y accroche : `missions.pour_jouer(slug)` rend les quatre choses, et le nom dit ce qu'elle
    fait — **tout ce qu'une mission demande pour se jouer**. Ce qui reste au paquet, c'est ce
    qui sert à la **choisir** (titre, donneur, prérequis, récompense) ; ce qui part, c'est ce
    qui sert à la **jouer**.
  - ⚠️ **TROIS LECTEURS DE PLUS, ET ILS TOURNENT À CHAQUE IMAGE** : `Histoire.objectif()`,
    `cible()` (la flèche du GPS) et `ligneObjectif()` (la ligne du HUD) indexaient
    `m.objectifs` sans regarder s'ils étaient là. Une partie reprise en pleine mission faisait
    **tomber la boucle de dessin** — pas la logique de mission, qui a sa garde depuis la
    tranche d'avant, mais le HUD, qui lit ça soixante fois par seconde. Les trois rendent
    maintenant « rien à montrer » tant que la mission n'est pas arrivée.
  - **Juges** : les mêmes, resserrés — le catalogue nu **dit encore quelle mission est
    possible et chez qui** (c'est ce qui sert à choisir, et il le garde en entier), la réponse
    porte ses objectifs avec un `type` chacun, et le juge du plafond raconte sa propre
    guérison avec la mesure.
- **25 sept. 2026 : deux gardes de plus sur les objectifs absents.** Le carnet
  (`Hud.menuCarnetEnCours`) indexait `m.objectifs` : ouvert pendant qu'une partie reprise
  attend sa mission, il tombait — et le joueur l'ouvre quand il veut, pas quand `maj` le
  permet. `avancer`, `poser`, `majObjectif` et le piratage ont la même garde, pour un appel
  direct (la triche, un événement). Un juge le tient sur un réseau qui ne répond jamais (la
  mission reste à son étape, rien n'est payé, le carnet s'ouvre), et la mutation (la garde du
  carnet retirée) le rougit.
  - ⚠️ **Deux sessions ont sorti les objectifs du paquet le même jour**, chacune sans voir
    l'autre : celle du 24 au soir (`23f97f5`, arrivée par `origin` le 25) et une seconde le 25,
    qui l'a découverte en voulant pousser. La seconde a retiré son commit (gardé sous
    `refs/wip/objectifs-doublon`) et n'a reporté que ces gardes. Un `git fetch` suivi de
    `git log dev..origin/dev` **avant** de marquer une ligne « en cours » l'aurait montré —
    à condition que la première l'ait marquée elle aussi.
- **25 sept. 2026 : quatre missions de plus, et le premier choix du catalogue.** `q01`
  (Lulu : trois Morues de sa sœur mangent sans payer, le quatrième file avec la caisse du
  midi — la cantine à −25 %), `q10`/`q11` (**Sven ou Josée** : la moto du pont au phare en
  une minute, ou les deux camions de Sven à faire sauter ; chacune `ferme` l'autre, pour de
  bon), `s08` (Gilles : la nuit au lot, trois Boulonneux, l'auto volée à ramener dans sa
  case). Aucun personnage neuf, aucune pièce neuve. 41 voix générées (3 781 caractères),
  relues par Scribe ; une refaite (`gilles-s08-3`, « Les Boulonneux » mâché).
  - **Jouées au bouton** (`tests/test_quatre_missions_js.py`, six juges) : chaque mission de
    l'appel à la prime ; `q10` sans bosse (900 $), avec une bosse (600 $), et ratée au chrono
    (rien ne se ferme) ; faire `q10` ferme `q11` et l'inverse — la première mission du
    catalogue qui exerce `ferme`.
  - ⚠️ **`ou: "quai"` ne pose rien.** `Histoire.tuileDeQuai` cherche les glyphes `q`/`j`, que
    la carte n'a plus (le quai est `Q`) : il rend `null`, et le camion de `q11` ne naissait
    pas — aucun juge de structure ne le voit, le banc l'a vu. Le camion est posé derrière la
    cantine (`ruelle:cantine:12`), et `missions.LIEUX_NOMMES` (ce que la scène par défaut peut
    filmer sans forme : `pont`, `bois`, `foire`) ne nomme pas `quai`.
  - ⚠️ **`sans_arme` est déclarée et personne ne la lit** (`OPTIONS_OBJECTIFS`, aucune ligne
    de `histoire.js`). Aucune mission ne s'en sert — ce n'est pas encore un mensonge, mais
    la première qui l'écrira en fera un : la brancher avant (`q06`, `s11` la prévoient).
  - ⚠️ **Le texte d'un objectif dit ce que le jeu fait** : le second camion de Sven est garé
    au pont, il « attend », il ne « file » pas ; la prime sans bosse de `q10` est une prime,
    l'objectif dit « IL PAIE PLUS », pas « SANS UNE ÉGRATIGNURE ».
  - ⚠️ **Des hommes posés là où la fin se joue tirent des dés pendant la scène.** Les trois
    Morues de `q01` étaient d'abord à la porte de la cantine ; le juge qui passe la fin à
    n'importe quelle image (`test_passer_une_scene…`) part de la dernière étape sans jouer
    les autres — elles étaient debout à côté du joueur, se battaient, et le monde divergeait
    selon qu'on regardait la scène ou non. Au vrai jeu elles sont couchées depuis longtemps,
    mais la garantie vaut pour tout le catalogue : elles sont maintenant dans leur coin du
    port (`zone:morues`), et on va leur présenter la facture. Un `tuer` à l'étape 0 ne se pose
    pas là où la mission finit.
  - ⚠️ **Deux intros écrites (`q01`, `q11`) pour une seule raison** : le défaut dit la première
    réplique sous la coupe (190 images), et une voix de six secondes se faisait couper par la
    suivante. La recette de `q02` : la coupe en `ensemble`, puis la `dire` qui retient la scène.
  - Le banc a montré deux faux rouges, à retenir pour les prochains juges : un fuyard qui n'a
    pas encore démarré laisse tomber sa caisse à la porte du donneur (le retour se fait dans
    la même image — laisser filer 300 images) ; et la cour de la fourrière se roule jusqu'au
    point du lieu, alors que la rue fléchée la plus proche est à seize tuiles (`s01` et `s08`
    se livrent en entrant dans la cour).
- **28 sept. 2026 : `eteindre` a son feu, le téléphone trie, et l'arc F est au complet.**
  Trois missions de plus — `f13` (Mado, _Les volontaires_), `f10` (Rosa, _La chemise
  hawaïenne_), `f12` (Madame Thibodeau, _Le Faubourg te dit merci_) — et avec elles les
  douze missions du tableau de l'arc F existent toutes (f01–f13 ; f11 est devenue _Mado tient
  tête_ le 21 sept., et le feu qu'elle devait éteindre est passé à f13). Un personnage de
  plus : **Norbert**, le concierge de l'Hôtel Bandini (`point:norbert`, au bout du comptoir
  du hall — un point dans une pièce déjà dessinée, aucune tuile de la ville ne bouge), sa
  fiche, son visage, son repos au vouvoiement, une voix de France (Martin Dupont Intime).
  41 voix générées (≈ 3 900 caractères).
  - ⚠️ **`eteindre` passait dans la même image.** Il attendait qu'aucun feu DE L'HEURE ne
    brûle (`Incendies.feuActif()`), vrai presque toujours. Chaque `eteindre` allume maintenant
    LE SIEN (`Incendies.allumerPourMission`) sur la façade la plus proche de son `ou` — une
    spirale sans dé qui préfère un mur à une porte — posé avant l'intro (la caméra le filme
    qui brûle). Il résiste vingt images de jet (un tiers de seconde : trois feux en coûtent
    60 sur les 100 d'un extincteur), fume et flambe plus fort que celui de l'heure, à
    l'empreinte (`hash2`, aucun `B.rng()` : une scène qui le filme ne décale rien), ne paie
    pas la prime du pompier volontaire, et s'en va avec la mission (`nettoyer`). La flèche le
    pointe. ⚠️ Le `ou` doit être une porte **déjà** lieu de mission : une porte neuve
    élargirait son devant (`devants.lieux_de_mission`) et la ville glisserait.
  - **Deux options transverses de plus** : `remet` (le donneur met une arme dans les mains,
    pleine et dégainée — ou une tenue au sac) et `tenue` (l'objectif ne s'accomplit qu'en la
    portant : un `aller` attend « ENFILE : … », un `parler` refuse la poignée de main). Et la
    ligne d'objectif affiche le temps qui reste d'un `chrono_s` — q10 avait « une minute »
    sans montre.
  - **Le téléphone qui trie** : jamais deux appels dans la même demi-journée (`p.dernierAppel`,
    `jour × 2 + midi passé`, dans la sauvegarde — une vieille partie la reçoit à `null` par
    `completer`), jamais à 3★ et plus, et le donneur dont la **porte** est la plus proche du
    joueur appelle d'abord (l'ordre du catalogue ne départage plus qu'à distance égale). Le
    donneur qu'on croise hélait déjà (`majBulles`) sans attendre le téléphone.
  - **Juges** (neuf neufs, sept mutations, toutes rouges) : `test_eteindre_js.py` (f13 au jet
    tenu au bouton J, de l'appel à la prime ; un coup ne suffit pas ; la mission ratée au
    chrono oublie son feu ; un feu qui brûle ne tire aucun dé), `test_telephone_qui_trie_js.py`
    (deux appels jamais dans la même demi-journée ; muet à 3★ puis il sonne ; le plus proche
    d'abord, des deux bouts de la ville), `test_arc_f_js.py` (f10 : la chemise au sac, rien
    n'avance dans le chandail, Norbert refuse puis accueille ; f12 : cinq poignées de main
    dites, et une étoile fait tout rater).
  - ⚠️ **Au banc, trois faux verts évités** : planté devant la cantine, le joueur se faisait
    coucher par les Morues et l'hôpital (dedans) retenait le téléphone — invincible ; à 3★
    vraies, la police l'arrêtait en cinq secondes et le menu figeait la partie (le juge
    « muet à 3★ » passait sur une partie arrêtée) — la police se tait au banc et le juge
    compte les images qui ont vraiment passé ; et `B.msg` est une chaîne, pas un objet.
  - ⚠️ **Le paquet** : `dev` était à 59 983 octets gzip pour 60 000 ; la vague en ajoute 151 —
    plafond à 62 000, mesure écrite dans `test_definitions.py`.
  - **`libere` et `calme` lus par la rue** (`Entites.gangChasse`, `Entites.gangCalme`) : un
    district libéré n'a plus de membres de son gang qui traînent dehors, et un gang calmé ne
    prend plus l'arme au poing pour une provocation (frappé, il riposte quand même). ⚠️ Avant,
    `faubourgLibere` (m5) coupait la naissance des membres de TOUS les gangs : après m5, plus
    une Morue ni un Chevreuil ne sortait en ville. Juge : `test_libere_calme_js.py` (deux,
    sauvegarde comprise). Aucune mission ne donne encore `libere` ni `calme` : ce sont
    `q13`, `e10`, `s11`, `p11` (districts) et `q06`, `e04`, `s05` (gangs) qui les écriront.
  - **Ce qui reste** : les arcs Q, E, S, P, H, D, C, R, T, I, X (≈ 70 missions), dont les quatre
    qui libèrent un district (`q13`, `e10`, `s11`, `p11`) — c'est ce qu'attend _Le Boss_ (M13) ;
    `sans_arme` toujours lue par personne ; `cible: "arch:"` d'un `parler` ne pose aucun
    figurant (f12 a pris cinq commerçants qui existent).
- **29 sept. 2026 : le chemin vers les quatre libérations — en cours** (Martin : « fais avancer M16 vers les
  quatre missions qui LIBÈRENT un district », pour _Le Boss_ de M13). Ce qui manque avant chacune, dans
  le catalogue tel qu'il est (les prérequis écrits dans le code ont parfois glissé de la fiche : `q04`
  vient après `q02`, `q10` après `m54`) :

  | Libération | Ce qui existe | Ce qui manque, dans l'ordre | Marches |
  |---|---|---|---|
  | `q13` Les Quais | `q01`–`q04`, `q10`/`q11` | `q05` → `q06` → `q13` | **3** |
  | `e10` Les Érables | `e01`, `e02`, `e12` | `e04` ; `e06` → `e07` ; puis `e10` | **4** |
  | `s11` La Shop | `s01`, `s03`, `s08` | `s02` → `s05` → `s09` ; `s06` → `s10` ; puis `s11` | **6** |
  | `p11` La Pointe | `p01`, `p13`, `p14` | `p02` → `p04` → `p10` ; `p05` → `p09` ; puis `p11` | **6** |

  Dix-neuf missions, **par vagues, un arc à la fois**, le plus court d'abord : **Q, puis E, puis S et P**.
  Chaque vague atterrit seule, verte, avec ses voix, et un juge de banc qui JOUE chaque mission au bouton.
  Ce que chacune demande au moteur ou au monde, trouvé en lisant `histoire.js` avant d'écrire :
  - **Arc Q.** ⚠️ **La Mireille de la fiche ne peut plus s'appeler Mireille** : le slug `mireille` est
    Mireille Dion, du DOJO DION (29 sept. 2026). La fille de la Brume qui veut sortir de la rue devient
    **Cindy** (`cindy`, personnage neuf, voix à choisir), devant la cantine. `q05` : la protéger jusqu'à
    l'hôtel, puis les gars du Beau Denis arrivent (le patron de `p14` : `proteger`, puis `tuer` `ou: donneur`).
    `q06` : coucher Denis, `sans_arme` — ⚠️ **l'option est déclarée et lue par personne** : elle se branche
    ici (dégainer une arme pendant l'objectif, c'est raté), puis semer ; `donne.calme: morues`. `q13` :
    après `q06` **et l'un des deux côtés du choix** (`q10` ou `q11`) — un prérequis ne sait dire que « et » :
    `exige.une_de` l'apprend (lu par `exigeTenu`, tenu par le banc) ; survivre à l'hôtel, puis coucher le
    chef des matelots de Sven — ⚠️ **aucun matelot n'existe** (ni archétype ni gang) : un archétype
    `matelot` de fréquence 0 (comme le `gardien`), et `tuer` apprend `pieton` (qui on envoie, le gang
    restant ce qu'il est) ; `donne.libere: quais`.
  - **Arc E.** Deux personnages neufs, **Diane** et **Jo** ; ⚠️ `contre` (des adversaires sur une `course`)
    n'est **lu par personne** non plus : `e04` le branche ou se réécrit ; `e06` file la berline du maire
    depuis la villa (le bloc de l'infiltration) ; `e07` fouille la villa (`obtenir`, comme `v01`) ; `e10`
    couche six Chevreuils sur deux coins (`coins`), puis Jo, et `donne.libere: erables`.
  - **Arc S.** Trois personnages neufs, **Ti-Loup** (la cour à scrap de la gare a son bureau du ferrailleur
    depuis le 29 sept.), **Gros-Boulon**, **Réjean Prévost** ; Bob Sauvé est une cible (`s06`, `suivre`).
    ⚠️ `usine` n'est jamais un `lieu` (barrière d'heure) : ce qui s'y prend se prend par `ou`. `s11` se
    joue `sans_arme` et donne `libere: shop`.
  - **Arc P.** Trois personnages neufs, **Bilodeau**, **Zed**, **le Trappeur** ; `p04` est la seconde
    `course` `contre` ; `p11` protège Zed jusqu'au bar et donne `libere: pointe`.
  - **Ce que M13 attend** : `p.libere` compte le district (m97 en veut 3, m98 4 : le Faubourg de m5 plus
    trois des quatre suffisent). Le juge de chaque libération le vérifie **dans le monde** : le gang ne sort
    plus dans son district (`Entites.gangChasse`), ne prend ni ne perd plus de coin (`Territoires.horsJeu`),
    et `exigeTenu({liberes: n})` monte d'un cran — sauvegarde comprise.
  - Hors du chemin : le brouillon `refs/wip/m16-q07` (`q07`, `a_vendre`) sert _Le Boss_ par la quatrième
    propriété, pas `q13` : il reste où il est.
- **29 sept. 2026 : vague 1 — l'arc Q jusqu'à sa libération. Les Quais sont libres.** Trois missions :
  `q05` (Cindy, _Cindy veut sortir_ : l'escorter de la cantine à l'hôtel, puis les deux gars du Beau Denis
  qui arrivent là où elle est — 100 $, elle quitte la rue), `q06` (Josée, _Le Beau Denis_ : ses deux gardes
  puis lui, chez les Morues, **à mains nues**, puis semer — 350 $, `calme: morues`), `q13` (Josée, _La nuit
  des Morues_ : de nuit devant l'hôtel, deux chaloupes de matelots de Sven puis leur bosco — 500 $,
  **`libere: quais`**, la manchette _Nuit blanche à l'Hôtel Bandini_). Un personnage neuf, **Cindy Boivin**
  (sa fiche, son visage, voix Ruby Roo — à écouter), qui n'est devant la cantine qu'entre q04 et q05.
  35 voix générées (≈ 3 300 caractères).
  - **Le moteur apprend quatre choses, chacune jugée et mutée** : `sans_arme` enfin lue (une arme au poing
    en territoire de gang, c'est l'échec `arme` — un échec de plus dans `ECHECS` — et la ligne dit « RANGE TON
    ARME » avant qu'on y entre) ; `exige.une_de` (q13 s'ouvre après q10 **ou** q11 : un prérequis ne sait dire
    que « et ») ; `tuer` `pieton` (qui on envoie : les **matelots**, un archétype de fréquence 0 au bout de
    `pietons.CATALOGUE`, comme le gardien) ; et la libération **se voit** : le gang libéré ne saute plus sur
    personne (`gangCalme`), rend les coins qu'il avait pris (`Territoires.liberer`), et sa cour redevient le
    nom du quartier sous la mini-carte (`Hud.nomIci` : « Les Quais », en blanc).
  - **Juges** (`tests/test_arc_q_js.py`, six ; sept mutations, toutes rouges) : q05 de l'appel à la prime,
    et Cindy couchée qui fait rater ; q06 ratée pistolet au poing, puis gagnée à mains nues (`calmes`) ; q13
    fermée sans le choix, ouverte par l'un ou l'autre côté ; q13 jouée — trois vagues de matelots, puis **les
    Quais libres dans le monde** : le gang sort du jeu, les Chevreuils non, le coin pris aux Cravates revient,
    celui pris AUX Morues ne bouge pas, « Les Quais » sous la mini-carte, `exigeTenu({liberes: 2})`, la
    sauvegarde relue. `test_missions_en_scene_js.py` complet : vert (531, 3 xfail connus).
  - ⚠️ **La « Mireille » de la fiche s'appelle Cindy** : le slug `mireille` est Mireille Dion, du DOJO DION.
  - ⚠️ **Un personnage posé dès l'ouverture décale les identifiants de la ville** (la mémoire « décor eager ») :
    Cindy `arrive_apres: q04`. Et comme q05 ne demande que q04, elle a toujours sa mission à donner : pas de
    repos (`_sa_mission_l_attend_toujours` l'apprend — ses deux repos, générés avant qu'on s'en rende compte,
    sont effacés : ≈ 156 caractères perdus).
  - ⚠️ **Le Beau Denis ne parle pas** : un `pendant` dit par quelqu'un d'absent passe au combiné, et Denis n'a
    pas ton numéro. Il est un chef (`chef`, 180 de vie, les poings) et c'est tout — sa voix attendra une
    mission où il est là quand il parle.
  - ⚠️ **Le paquet** : 280 579 bruts / 62 857 gzip sur `dev`, **282 815 / 63 357** avec la vague (+500 gzip :
    trois missions au catalogue, Cindy, le matelot, la manchette). Plafond 64 000 : **643 octets de marge**. La
    vague E ne tiendra pas dessous.
  - **Ce qui reste jusqu'aux trois autres libérations** : `e04`, `e06`, `e07`, `e10` (Érables — Diane et Jo,
    et `contre`/`course` qui ne sont lus par personne : `e04` se réécrit) ; `s02`, `s05`, `s06`, `s09`,
    `s10`, `s11` (La Shop — Ti-Loup, Gros-Boulon, Prévost) ; `p02`, `p04`, `p05`, `p09`, `p10`, `p11` (La
    Pointe — Bilodeau, Zed, le Trappeur). _Le Boss_ en demande quatre : Faubourg et Quais, plus deux.
- **29 sept. 2026 : vague 2 — l'arc E jusqu'à sa libération. Les Érables sont libres.** Quatre missions :
  `e04` (Jo, _La course des Chevreuils_ : son pilote part devant en sport, on le rattrape, on rapporte ses clés
  — 300 $, `calme: chevreuils`), `e06` (Diane, _Le maire ne dort pas chez lui_ : filer sa berline jusqu'à
  l'Hôtel Bandini — 300 $), `e07` (Diane, _La clé de la villa_ : la clé dans la poche du chauffeur, par-derrière,
  puis la villa du maire comme v02, le dossier du bureau d'en haut, sans une étoile — 400 $, le dossier reste au
  sac pour e11 et c02), `e10` (Diane, _Diane veut la paix_ : deux coins de Chevreuils, leur chef — c'était Jo —,
  la police — 600 $, **`libere: erables`**, la manchette _Plus un drift dans les Érables_). Deux personnages
  neufs, **Diane Larivière** (voix Riya Rao) et **Jo Bellemare** (voix Omar J) — fiches, visages ; tous deux
  devant le dépanneur, et seulement après e01 (`arrive_apres`) ; Jo s'en va après e04.
  - ⚠️ **`e04` est réécrite** : la fiche voulait une `course` `contre` trois Chevreuils, et **ni `course` ni
    `contre` ne sont lus par `histoire.js`** (une `course` avancerait dans la même image). La course se joue avec
    le fuyard de m2/m50/f03 : le pilote file en sport, on le rattrape ou on le casse. `course`/`contre` restent à
    brancher — `p04` (la course à pied contre Zed) en aurait besoin aussi.
  - **Ce que M13 attend, vrai au banc** : trois districts libérés (Faubourg, Quais, Érables) — _Marco te vend_
    (m97, `exige: liberes 3`) s'ouvre ; le juge le vérifie.
  - **Juges** (`tests/test_arc_e_js.py`, quatre ; trois mutations, toutes rouges) : e04 de l'appel à la prime
    (personne devant le dépanneur avant e01, Jo parti après) ; e06, une vraie filature jusqu'à l'hôtel ; e07, la
    clé du chauffeur puis la villa par le trou de la clôture, le dossier, ressortir sans étoile — le parcours des
    juges de l'infiltration ; e10 — six Chevreuils sur deux coins loin du dépanneur, leur chef, la police, et les
    Érables libres dans le monde (« Les Érables » sous la mini-carte, le gang hors jeu, son coin pris à La Shop
    rendu, la sauvegarde relue, m97 offerte).
  - ⚠️ **Le paquet passe son plafond** : 285 836 bruts / **64 020 gzip** pour 64 000 avec la vague. Relevé à
    **290 000 / 66 000**, la mesure écrite dans `test_definitions.py`. Ce qui en libérerait **dix Ko sans
    risque** : les notes de `musique.py` (`audio.musiques`, 62 089 bruts / 10 302 gzip — le sixième du paquet),
    qui peuvent venir avec leur district, par la route des mp3 ; c'était déjà écrit le 24 sept., et c'est le
    moment. Pas fait ici : ce n'est pas le chemin des libérations.
- **29 sept. 2026 : vague 3 — l'arc P jusqu'à sa libération. La Pointe est libre.** Six missions : `p02` (M.
  Bilodeau, _Le pont est bloqué_ : trois Skateux au pont, leur grand au cône — 150 $), `p05` (le Trappeur, _Les
  collets du Trappeur_ : la nuit, deux Skateux derrière leur stationnement — 120 $ et sa fronde), `p04` (Zed, _Zed
  veut un défi_ : **la première `course` d'une mission**, quatre points à pied sous son temps — 200 $, `calme:
  skateux`), `p09` (Ovila, _Le phare s'éteint_ : trois Skateux en 90 s, puis rallumer avec lui — 300 $, la
  manchette _Le phare a tenu_), `p10` (Zed, _Le saut de La Pointe_ : 80 px de vol — 250 $), `p11` (Josée, _Zed
  et la Chef_ : mener Zed au Brouillard, les Skateux qui refusent la paix — 500 $, **`libere: pointe`**, la
  manchette _La Pointe signe la paix_). Trois personnages neufs, tous devant le phare après une mission
  (`arrive_apres`) : **Roméo Bilodeau** (voix Bill), **Zed** (voix Lutz), **Armand, le Trappeur** (voix George) —
  fiches, visages, repos.
  - ⚠️ **`course` est enfin lue** (elle avançait dans la même image) : ses `points` se passent dans l'ordre, à
    `rayon` tuiles, la flèche vise le suivant, la ligne compte « 2/4 », `a_pied` ne compte rien au volant. Le
    parcours de Zed mesure ≈ 324 tuiles de sentiers (un parcours en largeur au banc) : 33 s au sprint, 43 à la
    course — 80 s de chrono. `contre` (courir CONTRE lui) reste lu par personne.
  - ⚠️ **`ou: "bois"` ne pose rien**, comme `ou: "quai"` : `tuileDeBois` cherche le glyphe `n`, que la carte n'a
    plus. Les deux Skateux de p05 naissaient sur le joueur ; ils sont derrière leur stationnement (`zone:skateux`).
  - ⚠️ **La moto de Zed est une motoneige l'hiver** (« pas de moto l'hiver ») : les répliques disent « ma
    machine », qui va aux deux.
  - **Ce que M13 attend, vrai au banc** : **quatre districts libérés** (Faubourg, Quais, Érables, Pointe) —
    `exigeTenu({liberes: 4})`, ce que _Le Boss_ demande.
  - **Juges** (`tests/test_arc_p_js.py`, sept ; quatre mutations, toutes rouges) : chaque mission de l'appel à la
    prime ; la course au volant qui ne compte pas, puis à pied dans l'ordre ; trop lente, ratée ; et La Pointe
    libre dans le monde (« La Pointe » sous la mini-carte, le gang hors jeu, la sauvegarde relue, quatre districts).
  - ⚠️ **Le paquet** : 290 969 bruts / 65 061 gzip — relevé à 300 000 / 67 000, pour l'arc S aussi (mesure dans
    `test_definitions.py`).
- **29 sept. 2026 : vague 4 — l'arc S jusqu'à sa libération. La Shop est libre, et les quatre libérations sont
  livrées.** Six missions : `s02` (Ti-Loup, _La ferraille de Ti-Loup_ : sa remorqueuse, trois épaves au lot —
  250 $), `s06` (Raymonde, _Le rat de l'usine_ : filer le char de Bob Sauvé jusqu'au Brouillard, où Prévost
  l'attend — 250 $), `s05` (Gros-Boulon, _Gros-Boulon te parle_ : la berline de Prévost au compacteur — 400 $,
  `calme: boulonneux`), `s09` (Gros-Boulon, _L'explosion_ : le camion-citerne de Prévost, trois étoiles — 600 $),
  `s10` (Raymonde, _Raymonde négocie_ : la mener au maire, qui dort à l'hôtel (e06), et les gardiens de Prévost qui
  la suivaient — 300 $), `s11` (Prévost, _La paix des Boulonneux_ : l'accord porté à Gros-Boulon **sans arme** —
  500 $, **`libere: shop`**, la manchette _La Prévost rembauche_). Trois personnages neufs : **Ti-Loup** (voix
  Chris) et **Gros-Boulon** (voix Roger) devant la fourrière après une mission, **Réjean Prévost** (voix Roland
  Lescalde) **dedans**, à son bureau de l'usine (`point:prevost`, un point de plus dans la pièce : aucune tuile de
  la ville ne bouge) — fiches, visages, repos.
  - ⚠️ **Écarts à la fiche, et pourquoi** : Ti-Loup n'a pas de cour à lui — son compacteur est au lot de Gilles
    (la cour à scrap de la gare existe depuis le 28 sept., mais en faire un lieu de mission élargirait le devant de
    sa porte, et la bande du nord glisserait) ; s10 mène Raymonde **à l'hôtel** et non à la villa (un lieu de bloc
    ne se rejoint pas avec quelqu'un qui te suit, et l'usine n'est jamais un `lieu`) — le maire y dort, e06 l'a
    montré ; les gardiens de Prévost sont des `gardien` du lot (`tuer` `pieton: gardien`, Prévost les loue).
  - **Juges** (`tests/test_arc_s_js.py`, sept ; quatre mutations, toutes rouges) : chaque mission de l'appel à la
    prime ; s11 ratée pistolet au poing dans le coin des Boulonneux, puis gagnée les mains vides ; et La Shop libre
    dans le monde (« La Shop » sous la mini-carte, le gang hors jeu) — **cinq districts** libérés.
  - **Ce que M13 attend** : les quatre districts de M16 (et le Faubourg de m5) se libèrent en jouant. _Le Boss_
    demande **aussi quatre propriétés**, et la quatrième, l'hôtel, n'est en vente nulle part (`phase: 2`) : c'est
    `q07` et `a_vendre`, en brouillon sous `refs/wip/m16-q07` — la dernière marche avant m98.
- **29 sept. 2026 : vague 5 — la quatrième propriété. L'hôtel est à vendre.** Le brouillon `refs/wip/m16-q07`
  repris, fini et joué : `q07` (Norbert, _La chambre 12_ : un comptable de Prévost mort dans la chambre douze ; de
  nuit, le « colis » dans le camion de la buanderie, à la fourrière sans une étoile, et Gilles s'occupe du reste —
  500 $, **`donne.a_vendre: hotel`**). L'Hôtel Bandini, `phase: 2` et vendu nulle part, se met en vente
  (`partie.enVente`, gardée par la sauvegarde) : il s'achète 10 000 $ au comptoir du hall (`Missions.aVendre`), et
  le BILAN compte les propriétés qu'on peut avoir, hôtel compris une fois en vente. 11 voix (Norbert, et Gilles à la
  poignée de main).
  - **Juge** (`tests/test_q07_hotel_a_vendre_js.py` ; trois mutations, toutes rouges) : q07 de l'appel à la prime,
    l'hôtel qui n'est à vendre nulle part avant et l'est après, la sauvegarde (une partie abîmée repart à vide), puis
    l'hôtel **acheté au comptoir du hall** : quatre propriétés, `exigeTenu({proprietes: 4})`.
  - ⚠️ Le brouillon livrait le colis « à la cour de Ti-Loup », un lieu qui n'existe pas : il va à la fourrière, chez
    Gilles — c'est aussi là que Ti-Loup compacte (s02).
  - **Ce que M13 attend** : les **quatre districts** (vagues 1 à 4) et les **quatre propriétés** (celle-ci) se
    gagnent en jouant. Reste à écrire _Le Boss_ lui-même — m98, son générique, la ville qui change de couleur.
- **30 sept. 2026 : M. Bilodeau change de voix, et le pont coûte cinquante piastres** (Martin : « les voix de Roméo
  Bilodeau sont pas bonnes, et 2 $ pour passer sur le pont, c'est vraiment pas assez cher »). Bill est une voix
  **américaine** (`verified_languages` : « standard » en multilingue v2 seulement) ; en v3 il sonnait anglais.
  Audition de la même réplique (l'appel de p02) par trois Québécois de la bibliothèque — **Santa** (le seul « old »
  / `quebec`), Pascal (ex-animateur radio), Mathieu — et Martin a pris **Santa - Gentle and Heartwarming**.
  - ⚠️ Une voix de bibliothèque se dit **par son identifiant** sans être au compte, mais le script la cherche **par
    son nom dans le compte** : l'ajouter d'abord (`POST /v1/voices/add/<public_owner_id>/<voice_id>`, droit
    `voices_write` donné à la clé par Martin le 30 sept.). Les voix de bibliothèque ne prennent pas de place.
  - « Deux piastres » devient **« Cinquante piastres »** (texte et `jeu=`) ; les 11 voix de Bilodeau refaites
    (`bilodeau-p02-1…10`, `bilodeau-repos-2`, ≈ 970 crédits), le dictionnaire (`piastres`) les étiquette.
- **30 sept. 2026 : vague 6a — l'arc D, la dette de Rocco a un visage.** Quatre missions : `d01` (Sal, _Le barbier_ :
  il te fait asseoir au terminus, puis veut voir sa garantie — on le mène au garage, `proteger` — 100 $), `d02` (Sal,
  _Le premier versement_ : Momo le taxi lui doit cinq cents, on le rattrape — le fuyard en taxi, parti de devant le
  terminus —, on sème la police, on rapporte l'enveloppe — 100 $, **`dette: -500`**), `d03` (Sal, _Les Ciseaux_ :
  trois faux Ciseaux et leur chef collectent en son nom devant l'Hôtel Bandini, on les couche, on sème deux étoiles —
  300 $, `dette: -300`), `d04` (Sal, _La collecte du barbier_ : Ti-Paul, Lulu et Ovila lui doivent aussi — chacun paie
  à sa façon à la poignée de main, et Ovila avec la montre de son père — 400 $, `dette: -800`). Un personnage neuf,
  **Salvatore « Sal » Ferraro** (voix Pascal — Voix québécoise chaleureuse, libre ; fiche, visage), **dedans**, à sa
  chaise au milieu du terminus (`point:sal` : un point de plus dans la pièce, aucune tuile de la ville ne bouge), et
  seulement après m6 (`arrive_apres`). 44 voix (≈ 4 500 caractères).
  - ⚠️ **Écarts à la fiche, et pourquoi.** Le « Salon Ferraro » n'existe pas comme lieu : un lieu neuf élargirait le
    devant d'une porte et la ville glisserait (la mémoire « reprendre une porte de commerce ») — Sal tient sa chaise au
    terminus, un endroit où l'on coupe les cheveux des chauffeurs. `acheter` n'accepte que des armes : la coupe de d01
    se dit dans l'intro, et la mission devient la visite du garage (ce qui prépare `d05`, Sal qui veut le saisir).
    Momo passe de d03 à d02 (l'enveloppe de Momo **est** le premier versement : un `payer` de 500 $ tout de suite ne se
    jouait pas) ; d03 devient les faux Ciseaux ; la collecte (d04) ne propose pas de payer pour les trois — un
    objectif facultatif n'existe pas.
  - Sal est **dedans** (`point:`) : pas de `retourner` (il ne se règle qu'avec un donneur dans la rue) — d02 à d04
    finissent par un `parler` à Sal, au terminus. Chaque job **efface** un bout de la dette (`donne.dette`) : 1 600 $
    pour la vague, et le carnet le montre.
  - **Juges** (`tests/test_arc_d_js.py`, six) : Sal absent du terminus avant m6, là après, et il donne d01 ; d01 de la
    poignée de main au garage, et Sal couché en chemin qui fait rater ; d02 (Momo né à moins de 40 tuiles du terminus —
    le piège de m50 —, la police semée, la dette à 14 500) ; d03 (les faux Ciseaux et leur chef devant l'hôtel, la
    dette à 14 700) ; d04 (les trois poignées de main dites, la dette à 14 200).
  - **Ce qui reste de l'arc (vague 6b)** : `d05` (l'avocat du Carré — Sal veut saisir le garage ; ⚠️ Me Desjardins est
    un piéton du Brouillard avec son menu, pas un PERSONNAGE : un donneur `point:avocat` doublerait l'homme à la table),
    `d06` (Sal perd patience : ses Ciseaux au garage), puis le choix — `d07` (le coffre de Sal, avec Josée ; `ferme
    d08`) ou `d08` (la dernière coupe, `exige: dette 0` ; `ferme d07`). ⚠️ Vider « le salon » ne peut pas se jouer
    dans la pièce du terminus (`majObjectif` dort dedans) : le coffre sort par la ruelle, ou dort dans son char.
- **30 sept. 2026 : le reste de M16 — le point, et l'ordre** (Martin : « le reste de M16 »). 81 missions au
  catalogue (dont 77 d'histoire). Ce qui reste de la fiche, arc par arc, avec qui donne :

  | Arc | Reste | Donneurs | Ce qui manque au monde |
  |---|---|---|---|
  | H — l'hôpital | `h03`–`h07` ; `h08` (l'île) | Dr Lachance, Ginette — **existent** | rien : `boulots` ambulance, `proteger`, `obtenir` suffisent |
  | D — la dette | `d05`–`d08` ; `d09` (l'île) | Sal, Marco, Josée — **existent** | Me Desjardins est un piéton à menu, pas un donneur ; le coffre de Sal sort par la rue |
  | C — le Clairon | `c01`–`c06` de la fiche | Louise — **existe** (`porte:kiosque`) | ⚠️ les slugs `c01`–`c08` sont pris (Irène, le vieux maître) : l'arc s'écrit **`l01`–`l06`** (Louise) ; son bureau, c'est la façade peinte « LE CLAIRON » (`boutique:clairon`), aucune porte neuve |
  | R — Roy contre Bouchard | `r02`–`r08` | Bouchard existe ; **Roy est à créer** (un point de plus dans le poste : aucune tuile ne bouge) | le choix `r03`/`r04` (`ferme`) |
  | I — l'île | `i01`–`i08` | Bérubé, Sœur Jeanne, Léo — **existent** | `q08` d'abord (le moteur de la chaloupe) |
  | X — le casse | `x01`–`x04` | Josée, Rosa — **existent** | ⚠️ la caisse populaire serait un lieu neuf (la ville glisse) : à poser sur une façade existante |
  | T — les petites jobs | `t01`–`t15` | des **archétypes**, pas des personnages | le moteur ne sait pas encore faire donner une mission par un passant : un type de donneur neuf |
  | Q, E, S, P (hors libérations) | `q08`, `q09`, `q12`, `q14` ; `e03`, `e05`, `e08`, `e09`, `e11`, `e13`, `e14` ; `s04`, `s07`, `s12`, `s13`, `s14` ; `p03`, `p06`, `p07`, `p08`, `p12` | presque tous existent (Maude et Mme Beaulieu, non ; Jo est parti après `e04`) | Biscuit, le chien de `e03` |

  **L'ordre** : d'abord les arcs dont les donneurs existent et qui ferment quelque chose — **H** (vague 7),
  puis la fin de **D** (vague 8, le choix `d07`/`d08` : payer Sal ou le vider), puis **C** (vague 9, Louise et
  ses manchettes), puis **R** (vague 10, Roy, le choix de sa police), puis l'île et le casse. Chaque vague
  atterrit seule, verte, avec ses voix et un juge de banc qui JOUE chaque mission au bouton.
  - ⚠️ **En missions, pas en chapitres.** [Des missions en chapitres](des-missions-en-chapitres.md) (tranché le
    30 sept.) veut que les arcs qui restent s'écrivent directement en chapitres, mais son moteur (`acte`, la
    reprise) n'est pas livré. Ces vagues s'écrivent en missions de quatre à six étapes, chacune un acte tout
    prêt : le jour où l'arc passe en chapitre, `remplace` les reprend, et une partie qui les a faites garde ses
    actes.
- **30 sept. 2026 : vague 7 — l'arc H, l'hôpital.** Cinq missions : `h03` (Lachance, _Le docteur a une dette_ : son
  secret — il joue aux cartes la nuit chez Sal ; on l'escorte au terminus avec mille piasses dans son sarrau, deux
  Cravates veulent l'enveloppe, il paie, il nous attend à la porte — 250 $), `h04` (Lachance, _Le cœur_ : l'ambulance,
  une glacière de pêcheur posée devant le terminus par l'autobus de nuit, l'urgence en 90 s — 400 $), `h05` (Ginette,
  _Le patient qui s'est sauvé_ : le chef des Cravates de m5, recousu, file avec l'ambulance et la trousse de morphine,
  ses deux gars viennent le chercher — 200 $), `h06` (Lachance, _Les ordonnances_ : le reste de sa dette, Sal le veut
  en pilules — trois fausses ordonnances à trois comptoirs, sans une étoile, les sacs à Sal, puis le docteur, qui n'est
  pas fier — 350 $), `h07` (Lachance, _La nuit des urgences_ : deux districts libérés, et ceux qui les ont perdus se
  vengent dans les ruelles ; cinq blessés en ambulance, trois Cravates à la porte de l'urgence, les clés à Ginette au
  petit matin — 500 $). Aucun personnage neuf, aucune pièce neuve.
  - ⚠️ **Écarts à la fiche** : les prérequis s'enchaînent (h03 après h02 et d01, puis h04, h05, h06, h07) pour que le
    téléphone n'appelle pas cinq fois ; `h05` — un fuyard ne court jamais à pied (`poserLeFuyard` pose toujours un
    char) : le patient vole l'ambulance ; `h06` — les « trois pharmacies » sont trois ENSEIGNES (la pharmacie Tang, la
    Mission du port, le dentiste) : une `course` sur `boutique:<mot>`, que `Histoire.resoudre` connaissait et que le
    juge des points de course n'acceptait pas (il l'apprend, et vérifie que le mot est peint quelque part) — aucune
    porte ne devient lieu de mission, la ville ne glisse pas ; `h07` demande **deux** districts libérés (le Faubourg de
    m5 en fait déjà un, `liberes: 1` serait toujours vrai) ; « un séjour à l'hôpital gratuit » n'a aucune clé de `donne`
    qui le lise (la facture ne passe pas par `rabais`) : la prime seule.
  - **Juges** (`tests/test_arc_h_js.py`, sept) : chaque mission de l'appel à la prime, prise au bouton chez son donneur
    (dedans pour Lachance) ; le docteur qui nous suit encore au retour ; la glacière qu'on ne ramasse pas au volant, et
    le cœur perdu au chrono ; le patient parti de devant l'hôpital ; les trois enseignes dans l'ordre, et une étoile qui
    fait tout rater ; la nuit des urgences fermée avec un seul district.
  - ⚠️ **Le paquet** : `missions` 4 028 → 4 240 octets gzip (42 par mission) ; mais le BRUT des définitions est à
    239 890 pour un plafond de 241 000 — ≈ 200 octets bruts par mission : cinq de plus et il cède.
- **30 sept. 2026 : vague 8 — la fin de l'arc D, et son choix.** Quatre missions : `d05` (Josée, _L'avocat du Carré_ :
  Sal a mis un huissier sur le garage ; l'acte de Rocco, caché dans une boîte à outils devant la baie, deux Ciseaux à
  bagues, et Me Desjardins au fond du Brouillard — 150 $, `casier: -2`), `d06` (Gus, _Sal perd patience_ : les Ciseaux
  viennent casser le garage à la nuit, trois puis leur contremaître aux vrais ciseaux — 250 $), puis le **choix** :
  `d07` (Josée, _Le coffre de Sal_ : la recette de la semaine dans la valise de sa berline, dans la ruelle du terminus,
  deux étoiles, livrée au Brouillard — 2 000 $, **ferme `d08`**) ou `d08` (Sal, _La dernière coupe_ : la dette payée
  jusqu'au dernier vingt, `exige.dette: 0` ; une coupe gratis, la planque de Rocco, un verre au Brouillard, et la bague
  de Rocco gardée en gage dix ans — **ferme `d07`**). Aucun personnage neuf.
  - ⚠️ **Écarts à la fiche** : `d05` ne se donne pas par Me Desjardins (un piéton à menu, pas un personnage — un
    `parler` ne vise qu'un personnage) mais par Josée, dans le bar où il tient sa table ; `d06` par Gus et non Ti-Guy
    (parti après m1) ni Marco (parti après m97, qu'on peut jouer avant l'arc D) ; `d07` vole la berline et non « le
    salon » (un objectif ne se joue pas dans une pièce) ; « Sal ennemi — des Ciseaux toutes les nuits » n'a aucune clé
    de `donne` qui le lise : après `d07`, Sal reste à sa chaise et ne dit que son repos (à trancher). `d09` attend l'île.
  - **Le paquet** : le brut des définitions passait son plafond (241 433 pour 241 000) — `"echec":["mort","arrete"]`
    et `"phase":1` se répétaient dans chaque mission. Ils ne voyagent plus quand ils valent leur défaut
    (`missions.PAR_DEFAUT_AU_NAVIGATEUR`, `Histoire.echecsDe`) : **239 189** bruts, 54 549 gzip. ⚠️ La marge brute ne
    tient plus qu'une vague : après, relever le plafond brut (qui n'est qu'un indicateur, le fil est le gzip) est la
    décision de Martin.
  - **Juges** (`tests/test_arc_d_js.py`, cinq de plus ; une mutation, rouge) : chaque mission de l'appel à la prime (le
    casier qui perd deux pages, les bagues des Ciseaux, le contremaître au couteau, la berline semée puis livrée) ; les
    deux côtés du choix offerts la dette payée, et chacun ferme l'autre ; la dernière coupe fermée tant que la dette
    court ; mourir fait rater une mission dont le paquet ne porte plus l'échec. Et `test_missions.py` : le paquet ne
    porte ni l'échec ni la phase qui valent leur défaut, et garde ceux qui n'en sont pas (m3).
- **30 sept. 2026 : vague 9 — l'arc C, le Clairon de Louise.** Six missions, en `l` (les slugs `c01`–`c08` sont pris
  par Irène et le vieux maître) : `l01` (_Une photo pour la une_ : Louise sans chauffeur, Bouchard « la bedaine au
  soleil » devant son poste, ses agents à semer, la lumière du soir au port — 150 $), `l02` (_La manchette sur toi_ :
  trois étoiles devant le poste, semées en 90 s — 200 $, la une _Bandini l'insaisissable_), `l03` (_La source_ : sa
  source, c'est Norbert ; de nuit, de l'hôtel au kiosque, deux hommes le suivaient — 300 $), `l04` (_Le scoop du
  maire_ : le dossier de la villa (e07) à la rédaction, les hommes du maire — 800 $, la une _Le maire dort à
  l'hôtel_), `l05` (_Le Clairon brûle_ : un bidon d'essence contre la rédaction, l'extincteur de Louise, les
  incendiaires — 400 $), `l06` (_L'entrevue_ : trois districts libérés ; Louise au pied du phare, trois questions —
  100 $, la une _Le neveu parle_). Aucun personnage neuf ; trois manchettes au Clairon (`journal.SPECIALES`), lues
  par le narrateur.
  - ⚠️ **Écarts à la fiche** : la rédaction du Clairon n'a pas de porte (la façade « LE CLAIRON » est peinte) — une
    `course` d'un point sur son enseigne (`boutique:clairon`) et un feu sur la façade la plus proche : aucune porte ne
    devient lieu de mission ; « survivre à l'intérieur » (c05) devient éteindre la façade, un objectif ne se jouant pas
    dans une pièce ; la source (c03) est Norbert, pas un commis du poste ; le scoop (c02) vient après e07 — e11 (vendre
    le dossier au maire) n'existe pas, le maire ne se tient en ville qu'entre m97 et m98 ; l'entrevue (c06) n'a pas de
    réponses au choix (aucun choix dans un dialogue) ; `l06` demande trois districts libérés, comme la fiche.
  - **Le paquet** : le catalogue passait son budget (4 523 gzip pour 4 450) et le brut son plafond. Le message de la
    fin (`donne.message`) voyage maintenant avec la mission (`/api/mission/<slug>`, `missions._sans_le_message`) —
    il ne se lit qu'à la fin : `missions` 4 523 → **2 779** gzip, le brut 241 302 → **237 378**. Budget recalculé.
  - **Juges** (`tests/test_arc_c_js.py`, sept ; une mutation, rouge) : chaque mission de l'appel à la prime, prise au
    bouton chez Louise ; les trois étoiles trop lentes, c'est raté ; Norbert qui parle en chemin ; les hommes du maire
    (des gardiens loués) ; l'extincteur que Louise met dans les mains et le feu près de l'enseigne ; l'entrevue fermée
    avec deux districts ; et les trois manchettes du lendemain. Plus : le message de la fin arrive avec la mission
    (`test_mission_a_la_demande_js.py`), le paquet ne le porte plus (`test_missions.py`).
- **30 sept. 2026 : vague 10 — l'arc R, Roy contre Bouchard (première moitié).** Un personnage neuf, **l'inspectrice
  Claudine Roy** (sa fiche, son visage ; dedans, au milieu du poste — `point:roy`, un point de plus dans la pièce,
  aucune tuile ne bouge —, après r01 ; voix **Kasandra**, québécoise, partagée avec Gisèle des puces qui ne parle dans
  aucune mission — auditionnée contre Marie Line et Luna : `captures/audition-roy-*.mp3`, à écouter). Quatre
  missions : `r02` (Roy, _Roy te convoque_ : son carnet au coffre de l'hôtel, Norbert l'ouvre, et le marché — 150 $),
  puis le **choix** : `r03` (Roy, _Le stool, c'est toi_ : Mado paie le sergent chaque midi ; on file son char jusqu'à
  l'hôtel — l'argent va au maire — 500 $, `casier: -5`, **ferme `r04`**) ou `r04` (Bouchard, _Le sergent
  contre-attaque_ : l'auto-patrouille de Roy volée dans la ruelle du poste, semée, laissée au lot sous un faux nom —
  500 $, `sergent_ami`, **ferme `r03`**) ; et `r05` (Bouchard, _La salle des pièces_ : le camion des pièces à conviction
  qui part pour Québec, volé, semé, mené au garage de l'oncle — 250 $).
  - ⚠️ **Écarts à la fiche** : r03 ne demande pas « midi » (`exige.heure` n'est lu qu'au téléphone, et l'objectif ne
    sait pas attendre une heure) — on fait jaser Mado, puis on file ; « le sergent n'est plus ton ami » n'a aucune clé
    de `donne` qui le défasse (`sergent_ami` ne sait que monter) ; r05 vole le camion au lieu de « ramasser trois armes
    dedans » (un objectif ne se joue pas dans une pièce), et aucune clé ne rend des armes confisquées ; r04 livre au
    lot (l'eau n'avale pas encore un char de mission).
  - **Juges** (`tests/test_arc_r_js.py`, quatre) : Roy absente avant r01 ; r02, la poignée de main de Norbert, le choix
    qui s'ouvre ; r03, une vraie filature jusqu'à l'hôtel, cinq pages de moins, r04 fermée ; r04 et r05, le char volé,
    semé caché dedans, livré — r03 fermée par r04.
  - ⚠️ **Au passage** : le point de Sal (arc D) touchait le comptoir des emplettes du terminus (`test_deux_points_ne_se_marchent_pas_dessus`, rouge sur `dev`) — il passe entre les deux rangées de bancs, `(5, 4)`. Le même juge reste rouge pour le garage (`reparer` et `ascenseur`, le garage souterrain d'une autre session).
  - **Ce qui reste de l'arc R** : `r06` (les affiches, avec Roy), `r07` (l'auto banalisée, avec Bouchard), `r08` (la
    patrouille de Roy, le boulot `patrouille`).
- **30 sept. 2026 : vague 11 — la fin de l'arc R.** Trois missions, une de chaque bord du choix et une de plus du côté
  de Roy : `r06` (Roy, _Une affiche de moins_ : Bouchard a fait coller ta face — RECHERCHÉ — sur cinq portes du
  Faubourg ; trois minutes, dans l'ordre — 100 $, `casier: -3`), `r07` (Bouchard, _L'auto banalisée_ : « policier en
  civil » dans son auto grise, trois Ciseaux de Sal, l'auto ramenée au poste — 400 $), `r08` (Roy, _La patrouille de
  Roy_ : une auto-patrouille prêtée, trois suspects au klaxon — le boulot `patrouille` —, les clés rendues — 250 $,
  `casier: -2`). L'arc R de la fiche est au complet.
  - ⚠️ **Écarts à la fiche** : les affiches de r06 s'arrachent en passant à chaque porte (`course`) — celles de la rue
    sont du décor tiré au hasard, qu'une mission ne sait pas poser ; r07 ne suspend pas les étoiles « tant que tu es
    au volant » (aucune option ne le dit) ; r08 compte trois suspects en une mission, pas cinq « en une semaine »
    (`boulots` ne compte que pendant la mission).
  - **Juges** (`tests/test_arc_r_js.py`, trois de plus) : les cinq portes dans l'ordre (hors d'ordre, rien ne compte),
    trois pages de moins ; l'auto grise devant le poste, trois Ciseaux, l'auto ramenée ; trois suspects en
    auto-patrouille, deux pages de moins.
- **30 sept. 2026 : vague 12 — ce qui restait des districts, avec des donneurs qui existent.** Six missions : `s07`
  (Prévost, _Le camion de Prévost_ : La Shop libre, un contrat avec Rimouski, le camion de pièces au quai en 150 s —
  « vous avez travaillé contre moi, vous travaillez pour moi » — 350 $), `s12` (Gilles, _Le dernier char du lot_ : sa
  retraite, cinq remorquages « comme dans le temps », et sa vieille remorqueuse garée à la planque, `donne.vehicule` —
  150 $), `s14` (Ti-Loup, _La casse à Ti-Loup_ : trois autos-patrouilles devant le poste, la même nuit, trois fois
  voler-semer-livrer au compacteur — 450 $), `e13` (Diane, _Le char de Diane_ : remorquée par les hommes du maire, sa
  berline reprise au lot sans payer, semée, garée devant le dépanneur — 300 $), `q12` (Josée, _La Chef a un cœur_ :
  sa mère fait une crise aux Érables ; l'ambulance, le dépanneur, l'urgence en deux minutes — 300 $), `q09` (Gégé, _La
  course des débardeurs_ : le perdant paie la bière ; trois points autour des Quais en camion, 2 min 30 — 300 $).
  - ⚠️ **Écarts à la fiche** : `s07` vient après `s11` (La Shop libérée : Prévost rembauche) et non après `s04` (Bob
    Sauvé n'est pas un personnage) ; il livre devant la cantine, au bord du quai, sans « sans bosse » (la prime
    `sans_degats` ne vaut que pour `livrer` d'un char prêté) ; `q09` se court contre la montre, `contre` n'étant lu
    par personne ; `q12` ne donne pas « Josée amie, le bar à +10 % » (aucune clé de `donne` ne le lit) ; `s13`
    (le prototype livré « à l'usine ») attend — l'usine n'est jamais un lieu de mission (barrière d'heure).
  - **Juges** (`tests/test_districts_suite_js.py`, sept) : chaque mission de l'appel à la prime, prise au bouton ; les
    trois tours de s14 aux étapes 1, 4, 7, chacun semé caché dedans ; la remorqueuse de Gilles à la planque ; la mère
    de Josée trop lente, c'est raté ; les trois points de Gégé dans l'ordre.
- **30 sept. 2026 : vague 13 — l'arc I, l'Île-aux-Corneilles (première moitié).** Cinq missions : `q08` (Bérubé, _Le
  moteur du capitaine_ : deux jeunes filent avec le Johnson de cinquante-huit dans un pick-up — 200 $), `i01` (Bérubé,
  _Le moteur tourne_ : sa chaloupe, la baie traversée jusqu'au hangar, et Léo à pied — « j'ai rien vu pis rien reçu »
  — 120 $), `i02` (Sœur Jeanne, _La cloche de Sœur Jeanne_ : volée l'hiver passé, rachetée deux cents piastres à
  Ti-Loup, ramenée par l'eau — 150 $), `i03` (Josée, _Le hangar sans nom_ : de nuit, sans une étoile, deux caisses de
  Sven derrière le hangar, ramenées au Brouillard par l'eau — 400 $), `i05` (Sœur Jeanne, _L'usine à poisson_ : la
  conserverie brûle près du hangar, l'extincteur de la chapelle, trois matelots de Sven — 200 $). Aucun personnage
  neuf : Bérubé, Sœur Jeanne et Léo attendaient leur arc.
  - ⚠️ **L'île ne se rejoint pas à pied** (`test_barrieres.py`) : aucun `lieu` sur l'île ; la chaloupe se prend et se
    livre à un `amarrage:<lieu>` (le patron de m52, m53), et l'on marche jusqu'à Léo ou la sœur. Au banc, la chaloupe
    est menée d'un amarrage à l'autre (la traversée elle-même a ses juges, m52 et m53).
  - ⚠️ **Écarts à la fiche** : `i02` ne laisse pas « la reprendre » à la place de payer (aucun objectif facultatif),
    et « on dort à la chapelle » (une deuxième sauvegarde) n'est pas écrit ; `i02` attend aussi `s02` (Ti-Loup n'est
    au lot qu'après s01) ; Sœur Jeanne appelle « du téléphone du quai de l'île » (sa fiche dit qu'elle n'a pas le
    téléphone : l'île n'a qu'une ligne, au quai). **Restent de l'arc** : `i04` (laisser refroidir un char chaud sur
    l'île — aucun char n'y va : pas de pont, et le traversier ne la dessert pas), `i06` (le bateau de Sven détruit),
    `i07` (la course en bateau — `course` ne connaît pas encore un `amarrage:` en point), `i08` (la cache de Rocco),
    et `h08`, `d09`, `p12` qui passent par l'île.
  - **Le paquet** : tout ce que `donne` accorde voyage maintenant avec la mission (`/api/mission/<slug>`, lu en la
    réussissant) — `missions` 3 073 → 2 631 gzip, le brut 239 833 → 237 693.
  - **Juges** (`tests/test_arc_i_js.py`, cinq ; une mutation, rouge) : chaque mission de l'appel à la prime, prise au
    bouton — la chaloupe née sur l'eau, accostée sous le hangar et la chapelle, la poignée de main de Léo et de
    Ti-Loup, deux cents piastres payées, les caisses posées devant le hangar, le feu près du hangar et trois matelots.
- **30 sept. 2026 : vague 14 — l'île, deuxième moitié.** Trois missions : `i06` (Josée, _Le dernier bateau du
  Norvégien_ : le chalutier de Sven coulé à quai au pistolet qu'elle met dans les mains, trois étoiles sur l'eau —
  500 $), `i08` (Josée, _La cache de Rocco_ : « sous le troisième banc de la chapelle » — les papiers de l'oncle (d05)
  parlaient d'une île ; deux matelots la cherchaient aussi ; mille deux cents piastres et une photo de Rocco jeune —
  1 200 $), `h08` (Lachance, _La traverse de l'urgence_ : un pêcheur de l'île, la jambe ouverte ; la chaloupe de
  l'hôpital, Sœur Jeanne qui le confie, l'urgence en deux cents secondes — 250 $).
  - ⚠️ **Écarts à la fiche** : `i08` se donne par Josée (Ti-Guy est parti après m1) ; `h08` se fait en chaloupe — le
    traversier ne dessert pas l'île ; `i06` coule le bateau au pistolet (`remet`), pas « 3★ sur l'eau » au départ : les
    étoiles viennent du coup de feu, et `semer` les pose à trois.
  - ⚠️ **Le banc des fins** (`test_missions_en_scene_js.py`, `versLaFin`) posait le joueur au `lieu` du dernier objectif par `Histoire.lieu`, qui ne connaît pas un `amarrage:` — h08 finit sous l'urgence : il le cherche aussi par `resoudre`.
  - **Ce qui reste de l'arc I** : `i04` (aucun char ne va sur l'île) et `i07` (la course en bateau : `course` ne prend
    pas encore un `amarrage:` en point) ; et `d09`, `p12` qui passent par l'île.
  - **Juges** (`tests/test_arc_i_js.py`, trois de plus) : le chalutier posé sur l'eau, coulé, trois étoiles semées ;
    la cache posée devant la chapelle, deux matelots, le retour par l'eau ; la traverse, la poignée de main de Sœur
    Jeanne, le retour à l'urgence.
- **30 sept. 2026 : ce qui reste de M16, après les vagues 7 à 14** (36 missions livrées ce jour-là ; 111 au catalogue, La Pointe comptée pour un chapitre) :
  - **Le casse (arc X, `x01`–`x04`)** : la caisse populaire serait un **lieu neuf** (la fiche le dit : « un cinquième
    lieu spécial, qui se paie ») — une porte neuve élargit son devant et la ville glisse ; et « ce qu'on a préparé change
    le coup » demande au moteur un objectif qui lit les préparatifs (moins d'étoiles avec la tenue, un char qui tient la
    poursuite). **À trancher avec Martin** : un lieu neuf posé en dernier, ou une façade peinte (`boutique:`).
  - **Les petites jobs (arc T, `t01`–`t15`)** : leur donneur est un **passant** (`pieton:<slug>@district:<slug>`, un
    par jour, avec la bulle « Hé! ») — le moteur ne sait pas encore faire donner une mission par un archétype.
  - **L'île** : `i04` (aucun char ne va sur l'île), `i07` (une `course` dont les points seraient des amarrages).
  - **Les districts** : `e03` (Mme Beaulieu et Biscuit, le chien — personnage et bête neufs), `e05` et `e14` (la piscine
    de la villa, dans un bloc), `e08` (Jo est parti après e04), `e09` (des poutines en vélo — remisé l'hiver), `e11` (le
    maire n'est en ville qu'entre m97 et m98), `s04` (Bob Sauvé n'est pas un personnage), `s13` (livré « à l'usine », qui
    n'est jamais un lieu), `q14` (la liste du quai, une activité), `p03` (Maude, personnage neuf), `p06`–`p08`, `p12`
    (La Pointe est devenue un chapitre : ses missions s'y ajouteraient en actes), `d09` (un choix dans un dialogue).
  - **Des chapitres** : [Des missions en chapitres](des-missions-en-chapitres.md) veut que les arcs s'écrivent en
    chapitres une fois le pilote joué par Martin ; les vagues 7 à 14 sont des missions de trois à dix étapes, chacune un
    acte tout prêt (`remplace`).
  - ⚠️ **Le paquet** : ce qui servait à jouer une mission voyage maintenant avec elle — l'échec et la phase qui valent
    leur défaut, puis tout `donne` (message compris) : le catalogue pèse **≈ 25 octets gzip par mission** ; le brut des
    définitions est à 239 439 pour un plafond de 241 000 (les autres sessions y ajoutent aussi) : une dizaine de missions
    de marge. Relever le plafond brut reste la décision de Martin.
- **1er oct. 2026 : en cours — un choix dans un dialogue, puis un passant qui donne une job** (Martin). Le choix :
  pendant une réplique, deux ou trois réponses au clavier et à la manette, et la mission bifurque (objectifs, fin,
  récompense) ; gardé par la sauvegarde ; déclaré dans le fichier de la mission. Puis `d09`. Le passant donneur :
  un passant ordinaire interpelle le joueur et propose une courte job (né à l'empreinte, sans dé ni identifiant
  qui décale la ville), une à la fois, jamais pendant une mission ; puis le plus possible de `t01`–`t15`.
  - ✅ **Vague 18 : un choix dans un dialogue, et `d09`.** Une réplique pose une question (`choix=[(clé, texte), …]`
    sur `_l`/`_p`/`_a`), le joueur répond dans la boîte **TA RÉPONSE**, posée au-dessus de la boîte de dialogue
    (clavier, manette, doigt ; obligatoire, sourde 12 images), et la mission bifurque : répliques et objectifs
    `branche`, ce que la fin paie `branches[clé]` ; gardé par `partie.mission.branche` puis `partie.choix`, exigible
    (`exige.choix`), reposé s'il a été sauté. Recette : `docs/comment-monter-les-missions.md` § 5 bis. `d09` (Sal,
    _Un compte sur l'île_, après d04 et i01) : la chaloupe du capitaine, Léo devant son hangar — « TOUT DE SUITE »
    (deux matelots, Léo paie, 250 $) ou « JE PAIE TES 800 $ » (de ta poche ; Sal les enlève de la dette, pas de
    prime). 17 voix (≈ 1 650 crédits).
    - ⚠️ **Écarts à la fiche** : on ne couche pas Léo lui-même (un personnage est intouchable, et il donne encore
      i04, i07) — ses deux matelots s'en mêlent ; la branche « payer » coûte 800 $ et rend 800 de dette (Sal ne
      refuse jamais l'argent) : à la dette déjà payée (d08), elle ne rend rien.
    - **Juges** : `tests/test_choix.py` (la forme, sept), `tests/test_choix_js.py` (huit : chaque côté joué au
      bouton, la question qui tient contre ACTION/PAUSE/RETOUR/FRAPPE/CARTE et le temps, la manette de Martin, le
      doigt, la sauvegarde, la question reposée, `exige.choix`, une question sous une scène) ; huit mutations,
      rouges.
  - ✅ **Vague 19 : un passant qui donne une job, et douze petites jobs.** Un passant ORDINAIRE de la rue (un archétype
    et un district, la clé `passant` de la mission) se présente — à pied, dehors, jamais pendant une mission, une offre
    par demi-journée au plus (`partie.jobOfferte`), une minute et demie après la dernière mission —, marche jusqu'à toi
    et te hèle (sa bulle, sa voix de passant : la partie `hele`, comptée en dernier) ; ACTION à côté de lui : son intro,
    puis la job, sans téléphone. Il naît à l'empreinte (`static/js/jobs.js` : un dé prêté, un numéro hors de la suite,
    sa tenue tirée de la garde-robe de son archétype, sa place d'une spirale sans dé) ; laissé en plan, il dit « Laisse
    faire. » et redevient passant. Deux rôles, `passant` (Felix) et `passante` (Amélie) — les voix des passants —,
    sans portrait ni présentation ; tout se dit en personne, l'échec compris. Recette : `docs/comment-monter-les-missions.md`
    § 5 ter. Les jobs (après m6) : `t01` _Mon char est au lot_ (le banlieusard des Érables : son auto au lot, Gilles
    qui appelle la police, le dépanneur — 80 $), `t02` _Le lunch des gars_ (le débardeur : trois hot-dogs à la cantine,
    rapportés chauds en 90 s — 30 $), `t03` _Un lift au terminus_ (la dame à la valise et ses œufs, 90 s — 40 $),
    `t04` _Mon BMX_ (l'ado de La Pointe, un Skateux qui le promène en janvier — 25 $), `t05` _La sacoche_ (reprise
    par-derrière à l'itinérant — 50 $), `t06` _La commande de la taverne_ (le camion du gérant, deux caisses à la
    cantine — 90 $), `t09` _La tournée du Clairon_ (six portes dans l'ordre, deux minutes et
    demie — 60 $), `t11` _Le feu de camp_ (l'extincteur que le promeneur traîne depuis neuf ans — 50 $), `t12` _Une
    gageure avec le livreur_ (l'hôpital en 75 s — 70 $), `t13` _La pelle du vieux_ (une Morue, et il te la laisse —
    20 $ et la pelle), `t14` _Les mariés_ (la berline de l'oncle, la mariée au phare — 120 $), `t15` _L'autobus manqué_
    (la fourrière avant le quart, 100 s — 40 $). 83 voix.
    - ⚠️ **Écarts à la fiche** : une offre par demi-journée (la fiche disait « un par jour ») ; le donneur est un rôle
      (`passant`/`passante`) qui porte l'archétype, pas `pieton:<slug>@district:<slug>` ; `t02` à la cantine, pas au
      kiosque ; `t03`, `t15` sans « sans un choc » (aucune option ne le lit hors de `livrer`) ; `t10` (l'usine n'est
      jamais un lieu de mission) et `t15` vont à la fourrière ; `t12` court contre la montre (`contre` n'est lu par
      personne) ; `t09` à pied ou en char (le vélo est remisé l'hiver) ; `t04` un BMX en janvier. Restent `t07` (le p'tit perdu : rien ne pose un enfant qui se cache), `t08` (des boîtes à
      porter dans l'usine), `t10`.
    - **Le paquet** : le casse (x01-x04) venait de remplir la clé `missions` et le plafond brut, la suite était pleine.
      Les jobs voyagent donc PLIÉES (`jobs`, une liste par job — 797 bruts, 363 gzip ; `missions.jobs_pour_le_navigateur`)
      et le navigateur les déplie dans le catalogue (`Jobs.deplier`) ; leur passant n'y est qu'« archétype@district »,
      les deux rôles n'y portent pas de couleurs. ⚠️ Le brut des définitions est à 241 947 pour 242 000 : la prochaine
      clé qui grossit le passe — relever ou plier autre chose, c'est la décision de Martin.
    - **Juges** : `tests/test_jobs.py` (la forme, cinq), `tests/test_jobs_js.py` (dix-huit : il se présente, hèle et vient ;
      né sans dé ni numéro, la même tenue ; la cadence — trop tôt, en mission, au volant, une par demi-journée ; jamais
      au téléphone ; les douze jobs jouées au bouton ; l'échec dit en personne, le dépliage du paquet) ; huit mutations, rouges (une huitième —
      la garde « pendant une mission » — ne rougit pas : la cadence la double, `B.jobRepos` repart à chaque image de
      mission).
- **1er oct. 2026 : en cours — le casse, un char sur l'île, une course sur l'eau** (Martin). Trois vagues, chacune
  atterrie seule : (15) une **caisse populaire** neuve — la CAISSE POP d'origine est devenue l'ÉCOLE LA MANTE —, posée
  en dernier sur la ville finie, sans un dé, la ville d'avant identique (comparée en JSON), son intérieur (comptoir,
  coffre, bureau du gérant), puis `x01`–`x04` ; (16) un char qui embarque sur le traversier jusqu'à l'île et y roule,
  puis `i04` ; (17) des bouées sur la baie que `course` sait lire en bateau, puis `i07`.
- **1er oct. 2026 : vague 15 — le casse de la caisse populaire (arc X, `x01`–`x04`).** Un lieu neuf, **la caisse
  populaire de La Shop** (`app/caisse.py`) — la caisse des ouvriers, où le fourgon dépose la paie de l'usine Prévost :
  la pièce d'un commerce ordinaire (LIQUIDATION, à la vraie graine) reprise **en dernier** sur la ville finie, sans un
  dé — après les devants (son devant de mission est déjà dégagé, sur quatre graines), avant les étages (une pièce
  faite main n'en monte pas). **La ville d'avant est la même, clé par clé** (`test_caisse.py` : une porte renommée,
  une enseigne repeinte, la pièce redessinée, un point d'intérêt au bout — rien d'autre). Dedans, son habit `caisse`
  (boiserie brune, plâtre crème, prélart) : le comptoir des guichets d'un mur à l'autre et sa porte battante, la
  **voûte** d'acier au fond (un bloc de deux sur deux, sa porte ronde à minuterie), le **bureau du gérant** derrière
  une cloison (monsieur Lemire), la salle d'attente ; deux caissières, **Fernand** le vigile, des clients ; la porte
  d'en arrière, peinte sur le mur. Quatre missions : `x01` (Josée, _Repérer la caisse_ : la voûte regardée de près, le
  fourgon filé jusqu'au casse-croûte de Mado, où ses gars dînent avec Bouchard — 100 $), `x02` (Gus, _Le char qui
  part vite_ : le coupé d'un touriste de l'hôtel, refusé à la planque tant qu'il n'est pas **repeint** — 150 $),
  `x03` (Rosa, _Le linge propre_ : l'uniforme de livreur oublié chez elle, un colis de carnets de chèques signé par
  Lemire, et Fernand qui salue — 100 $), `x04` (Josée, _Le coup_ : la minuterie de la voûte, l'alarme, une minute à
  tenir pendant que trois vagues de gardes du fourgon entrent par l'arrière, les sacs de la paie, quatre étoiles à
  semer, le Brouillard — 2 500 $, **ferme `d08`**, et les préparatifs qu'on n'a plus à faire).
  - **Ce qu'on a préparé change le coup** — sans un type neuf : deux clés de données, `si` / `sauf` (une mission
    faite / pas faite), sur un objectif (il se SAUTE) ou une réplique `pendant` (dite ou tue) — `Histoire.tenu`. Le
    coupé du x02 attend dans la ruelle (`monter`, `si: x02`) ; Josée dit ce qui est prêt et ce qui manque au premier
    objectif. Sans l'uniforme, Fernand te reconnaît en entrant (deux étoiles, et il te saute dessus) ; sans arme à
    feu, la minute se fait aux poings. Le juge joue les deux combinaisons extrêmes, de la porte du bar à Josée.
  - **Dans une pièce, `majObjectif` dort** : le casse se joue DEDANS par `static/js/caisse.js` — un objectif
    `obtenir` dont la `table` est la caisse, et l'OBJET dit quoi faire (`caisse.OBJETS` : le repérage, la livraison,
    le coup) ; l'objet entre au sac dedans, l'objectif avance à la sortie. L'alarme sonne tant qu'on est dans la caisse
    (les étoiles ne tombent pas, comme elles tomberaient dans une pièce). Un piéton ne cherche pas son chemin : qui
    doit changer de côté du comptoir passe par la porte battante (vu en capture : Fernand et les gardes restaient
    collés au comptoir, la minute ne coûtait rien). Les gardes naissent à l'empreinte de leur vague, jamais `B.rng()`.
  - **Deux clés de plus au moteur** : `livrer` + `repeint` (le char ne se livre qu'une fois repeint — `Missions.repeindre`
    le marque), et `ferme` accepte une liste. Un uniforme de plus (`magasins.TENUES`, `livreur`, qui ne se vend pas) ;
    deux gens de pièce (`gerant`, `vigile` : le corps du commis et celui du garde, aucun archétype neuf).
  - ⚠️ **Écarts à la fiche** : la caisse est à **La Shop**, pas au Faubourg (il n'y reste aucune porte de commerce) ;
    `x02` se donne par **Gus**, pas Josée (un donneur donne la PREMIÈRE mission disponible de sa liste : Josée aurait
    offert le coupé avant le coup, à tout jamais, et le coup ne se serait jamais joué sans lui) ; `x01` ne demande pas
    « trois heures différentes » (un objectif ne sait pas attendre une heure : on regarde la voûte, on file le fourgon) ;
    les préparatifs paient un peu (le juge des missions veut une prime) ; et « chaque préparatif manquant se dit à
    l'intro » se dit au premier objectif, juste après elle (les scènes d'intro choisissent leurs répliques par leur rang).
  - ⚠️ « Le repérage » était déjà le titre de m52 : le saut de mission (triches) choisit par le titre, et lançait m52.
    `x01` s'appelle _Repérer la caisse_, et `test_missions.py` refuse deux titres pareils.
  - **Juges** : `test_caisse.py` (neuf : la ville d'avant clé par clé et sa mutation, La Shop, la mesure et le filtre
    des noms que les missions lisent — mutés, rouges —, la pièce à la mesure de son bâtiment, toutes les mesures, le
    devant sur quatre graines, la liste des objets) ; `test_casse_js.py` (six : x01, x02, x03 jouées au bouton, x04 tout
    préparé et rien de préparé, et la porte battante — mutée, rouge) ; `test_missions.py` (la table `caisse`, `si`/`sauf`
    jamais au départ ni hors `pendant`).
- **1er oct. 2026 : vague 16 — un char sur l'île, et `i04`.** La **navette de l'île** (le deuxième bateau des Quais,
  `navette.py`) prenait déjà les chars sur son pont, comme le traversier ; ce qui manquait, c'était **le chemin d'un
  joueur** et de quoi l'écrire dans une mission. Le juge part de la rue des Quais (une voie qui descend vers le quai),
  monte sur le pont au bouton, traverse, sort de la vieille jetée de l'île — par la friche, entre les barils de
  l'usine et l'eau —, roule jusqu'au hangar de Léo par la gravelle et l'herbe sans couler, revient attendre la navette
  au bout de la jetée, remonte, et redescend en ville (`tests/test_ile_en_char_js.py`, un pilote au bouton sur un
  chemin trouvé dans la carte : `tests/outils_ile_en_char.py`). **Rien n'a bougé dans la carte** : l'île roulait déjà.
  - **Au moteur** (en données, aucun slug) : `embarquer` + `bateau: navette` (la navette au lieu du traversier), les
    lieux `navette:<escale>` (le bout de son quai) et `ile:<lieu>` (un lieu de l'île qu'on rejoint par l'eau — les
    juges des barrières le savent, et `poserLeChar` y cherche de la terre, pas une rue : l'île n'en a aucune) ; un type
    neuf, `attendre` (`heures` de JEU depuis le début de l'étape — vivre ou dormir les fait passer ; le départ est gardé
    dans la partie, une partie rouverte attend toujours) ; et `livrer` + `rentre` (livré, le char quitte la rue).
  - **`i04`** (Léo, _Laisser refroidir_ — 100 $) : une berline chaude derrière la cantine, trois étoiles ; la navette
    aux heures impaires (la police n'y monte pas, l'île est un refuge) ; le hangar par la gravelle, où Léo la rentre ;
    une journée de jeu ; une berline « jamais vue de sa vie » devant le hangar ; la navette du retour ; la planque.
  - ⚠️ **Une heure de jeu, c'est vingt secondes** : du hangar à la jetée, il faut près d'une heure de route, et la navette
    ne reste à quai que vingt minutes — on l'attend au bout de la jetée (le juge le fait, comme un joueur). Et en
    tournant de la rue sur le pont des Quais (deux rangées), un coin de roue mord le bord de l'eau : le char ne coule
    pas (trois secondes, `coule_s`), le juge tolère moins d'une seconde. ✅ Corrigé le jour même (Martin : « IL COULE —
    SORS » s'affichait) : près d'une coque à quai, le char tient tant qu'une roue touche le pont ou le quai.
  - ⚠️ **Écarts à la fiche** : « par le traversier » — c'est la navette, le deuxième traversier de la baie (le premier
    ne dessert pas l'île) ; « le char repeint, les plaques changées » : Léo rend une berline neuve (`monter` sur
    `ile:hangar_ile`) — pas une clé de `donne` ; la prime est de 100 $ (le juge des missions en veut une).
  - ⚠️ **Le paquet** : le brut des définitions n'avait plus que 33 octets de marge (241 967 pour 242 000) — `i04` le
    passait. **Un seul prérequis voyage nu** (`"i01"`, pas `["i01"]`, `missions._au_catalogue`) : quatre octets sur
    soixante-dix missions ; le navigateur remet la liste en arrivant (`Jobs.deplier`). Juge : `test_missions.py`
    (muté, rouge). Martin a relevé le plafond brut le même jour (255 000) ; la compaction reste.
  - **Juges** : `test_ile_en_char_js.py` (deux : l'aller-retour au bouton, de la rue au hangar et retour ; i04 jouée
    de l'appel à la prime — trois mutations rouges : `attendre` qui ne compte pas, la navette prise pour le traversier,
    le char qui ne rentre pas) ; `test_missions.py` et `test_barrieres.py` apprennent `ile:` et `navette:`.
- **1er oct. 2026 : vague 17 — une course sur l'eau, et `i07`.** Six **bouées de course** autour de
  l'Île-aux-Corneilles (`app/regate.py`), dans le sens des aiguilles d'une montre depuis le sud-est (le hangar de
  Léo) : à sept tuiles de la rive, sur de l'eau profonde, loin des amarrages, et chaque bord du parcours est de l'eau
  libre d'une bouée à l'autre. **Ni tuile ni décor** (un décor de plus au chargement décale l'identifiant de tout ce
  qui naît après) : une liste de points posée en tout dernier, sans un dé (`ville["regate"]` ; la ville d'avant est la
  même, clé par clé), que le navigateur PEINT (`static/js/regate.js` : la bouée orange à bande blanche, son mât, son
  fanion, qui danse avec la houle ; la prochaine a son halo et son numéro).
  - **Au moteur** : `course` lit `bouee:<n>` (`Histoire.resoudre`) ; `vehicule` (la course se court dans ce véhicule —
    en chaloupe, pas à la nage) ; et **`contre`, enfin lu** (déclaré depuis la v1) : un RIVAL court les mêmes points,
    droit d'une bouée à l'autre, à son `allure` (une VITESSE : au-dessus d'`allure` × sa pointe, il lève les gaz — à 0,82
    « de gaz », la coque finissait quand même à sa pointe, et il faisait le tour en trente secondes) ; arrivé avant
    toi, c'est raté (l'échec neuf `battu`) ; battu, il dérive. Léo se voit à la barre (`cavalierDe`, le conducteur
    `regate`).
  - ⚠️ **Une coque à un amarrage (`amarrage:<lieu>`) naissait par-dessus la chaloupe de décor du même amarrage** :
    `poserLeChar` la faisait passer par `tuileDeRue`, et sur l'île — aucune rue — deux coques soudées, aucune ne
    bougeait. Une coque prend maintenant la chaloupe amarrée (comme `mouillage:` et l'amarrage de Sven).
  - **`i07`** (Léo, _Le tour de l'île_ — 200 $) : la vieille chaloupe de l'usine sous le hangar, « à trois, on part »,
    les six bouées et retour à la première contre Léo dans le bateau de son père (`allure` 0,75 : un tour de trente-deux
    secondes, mesuré ; le pilote du juge, à fond et sans freiner aux bouées, en fait vingt-sept), la chaloupe
    ramenée sous le hangar. Immobile au départ, Léo fait le tour et c'est raté.
  - ⚠️ **Écarts à la fiche** : pas de « repli à la nage » (la course se court en chaloupe : `vehicule`) ; sept points
    (les six bouées, puis la première : la ligne d'arrivée) ; le donneur est au hangar ET à la barre — sa réplique de
    départ se disait au combiné (✅ corrigé le jour même : `present` reconnaît le rival à la barre).
  - **Juges** : `test_regate.py` (quatre : la ville d'avant clé par clé, six bouées sur l'eau profonde autour de l'île,
    chaque bord de l'eau libre — le juge lit l'eau lui-même : muté, rouge —, et sans place, rien ne se pose) ;
    `test_regate_js.py` (trois : les bouées se lisent et se peignent ; i07 gagnée au bouton ; immobile, Léo gagne —
    deux mutations rouges : sans `battu`, sans rival qui court).
- **1er oct. 2026 : deux défauts des vagues 16 et 17** (Martin, en jouant).
  - **Le coin de roue au quai des Quais** : en tournant de la rue sur le pont de la navette (deux rangées), le char
    coupe le coin du quai — son CENTRE passe au-dessus de l'eau qui borde le pont, ses roues arrière sur le quai,
    l'avant sur l'acier. `majNoyade` ne lisait que la tuile du centre : « IL COULE — SORS », le char freinait dans ses
    remous, et il ne coulait pas. Près d'une coque à quai (`Traversier.aQuaiPres`/`Navette.aQuaiPres`, deux tuiles), le
    char tient tant qu'une de ses quatre roues touche du sol (`Vehicules`, `tenuAuQuai`) ; ailleurs, rien ne change (au
    bord de n'importe quel quai, un char posé le nez dans l'eau resterait perché pour toujours). Juge :
    `test_monter_sur_la_navette_en_coupant_le_coin_ne_dit_pas_il_coule` (trois virages de joueur, de la rue au pont, au
    bouton : le coin d'eau est coupé, le message ne vient jamais, le char part à bord — muté, rouge) ; le juge de
    l'aller-retour ne tolère plus une seconde d'eau.
  - **Léo au téléphone dans `i07`** : « À trois, on part » se disait au combiné alors qu'il est à la barre, à trente
    pixels — `present` ne cherchait que le piéton resté devant le hangar. Le rival d'une course (`contre.qui`) est
    aussi lui : à portée de voix, il parle en personne. Juge : `test_i07_le_tour_de_l_ile_on_bat_leo` lit le combiné
    réplique par réplique (muté, rouge).
- **1er oct. 2026 : vague 20 — La Pointe après sa paix** (Martin : « continuer M16 »). Quatre missions, des donneurs
  qui existent, aucune tuile ni porte neuve :
  - `p06` (Ovila, _Ovila voit des lumières_ — 300 $) : la nuit au phare, une chaloupe sans feux, deux matelots de Sven
    et une caisse dans un camion ; on le file (`suivre`) jusqu'à la cantine des Quais, on couche les deux matelots,
    on prend la caisse à pied (`obtenir`) et on la porte à Josée (`parler`) — des moteurs hors-bord à l'étampe de Sven.
  - `p07` (M. Bilodeau, _Le souper dansant_ — 250 $, 375 sans un choc) : l'autobus du club de l'âge d'or devant le
    phare, les voisins du bout aux Souvenirs, aux Planches et au pied du pont (`course`), l'Hôtel Bandini sans les
    brasser (`livrer`, `sans_degats`).
  - `p08` (Zed, _Le party du stationnement_ — 200 $, 300 sans une bosse) : le camion de Lulu, deux caisses de bière au
    stationnement du phare, la police à semer, le party.
  - `p12` (Zed, _La flotte de Zed_ — 150 $) : la vieille chaloupe de Lulu menée par la baie au quai de La Pointe
    (`amarrage:phare`), et Zed qui avoue qu'il ne sait pas nager.
  - ⚠️ **Écarts à la fiche** : `p06` — la « cabane » des matelots est la ruelle de la cantine, et ils roulent (on ne
    file pas un piéton) ; `p07` — un souper dansant plutôt qu'un déménagement, trois arrêts (La Pointe n'a que deux
    enseignes et un pont), à huit tuiles (les enseignes sont à six et sept tuiles de la rue ; l'autobus ne monte pas
    sur le trottoir, le banc l'a vu) ; `p12` — le quai de La Pointe est l'amarrage le plus proche du phare, au nord du
    district.
  - ⚠️ **Le banc des scènes ne savait pas qu'un chapitre fait a fait ses actes** : `faites()` de
    `test_missions_en_scene_js.py` marquait `la_pointe` sans `p02` — or Zed n'arrive qu'après `p02` (`arrive_apres`),
    et `Chapitres` marque les missions remplacées à la réussite. Les scènes de `p08` et `p12` tombaient sur un donneur
    absent (14 rouges) ; `faites()` marque maintenant ce qu'un chapitre remplace.
  - **Juges** : `tests/test_pointe_apres_js.py` (sept, au bouton de la poignée de main à la prime : chaque mission ;
    `p06` collé au camion, qui nous voit ; `p07` un choc, pas de prime ; `p12` la chaloupe en épave) ; mutations : le
    rayon des arrêts de `p07` remis à trois (rouge), `sans_degats` retiré (rouge).
  - **Voix** : 43 (≈ 3 900 caractères), générées et mesurées, pas écoutées.
- **1er oct. 2026 : vague 21 — les Érables et La Shop, la suite.** Cinq missions, des donneurs qui existent :
  - `e08` (Diane, _La cachette de Jo_ — 250 $) : sa mère a trouvé un plan dans la chambre de Jo ; son coupé, un paquet
    au pied de la rampe des Skateux sous le chrono (200 s), l'autre sous le phare, et retour chez elle avec un char des
    Skateux collé derrière (`poursuite`).
  - `e09` (Ti-Paul, _Le barbecue de janvier_ — 150 $) : trois poutines chaudes, en camion, à la quincaillerie, au
    lave-auto et chez Prestige Autos, en deux minutes (`course`, `chrono_s`) ; puis le barbecue.
  - `e11` (le maire, _Le maire te reçoit_ — un CHOIX) : dans sa chambre de l'hôtel (il n'y est qu'entre m97 et m98),
    il rachète le dossier de la villa mille piastres. « VENDU, MONSIEUR LE MAIRE. » : la planque, puis sa chambre —
    1 000 $. « IL EST PAS À VENDRE. » : la planque, Louise au kiosque, deux gardes du maire trop tard, et on remonte lui
    dire non en pleine face — 300 $. La fin se dit dans sa chambre, d'un bord comme de l'autre.
  - ⚠️ **La question se pose à la poignée de main** (`accueil` d'un `parler`, le patron de d09), pas dans l'intro : une
    scène d'intro se joue seule au banc (`test_missions_en_scene_js`), et une question l'arrête jusqu'à ce qu'on
    réponde — cinq rouges. Et le banc ne savait pas aller voir un donneur dans une chambre d'ÉTAGE (pas de porte en
    ville) : `allerVoir` entre par la pièce dont l'escalier y monte, comme `versLaFin`.
  - `s04` (Raymonde, _Le quart de nuit_ — 300 $) : la paie du quart de nuit en argent comptant à la caisse pop ; trois
    Cravates et deux vagues de renforts, leur chef au couteau ; l'enveloppe à Raymonde.
  - `s13` (Prévost, _Le prototype_ — 400 $, 600 sans une égratignure) : le coupé de Détroit chez les Skateux, la rampe
    (30 px), la fourrière de Gilles avec un char des Chevreuils collé derrière.
  - **Au moteur** : `obtenir` pose son objet à toute forme de lieu (`rampe:`, `zone:`, `boutique:`) — `Histoire.lieu`
    ne lisait qu'un nom de porte, et un paquet « au pied de la rampe » ne se posait jamais.
  - ⚠️ **Écarts à la fiche** : `e08` — Jo est parti après e04 : c'est sa mère qui donne la job ; `e09` — le vélo est remisé
    l'hiver (une partie commence en janvier) : le camion, aux enseignes de la rue (à huit tuiles : elles sont loin de la
    chaussée) ; `e11` — « c02 s'ouvre » : le slug est pris (Irène), Louise publie et paie ; `s04` — Bob Sauvé n'est pas
    un personnage (et il a vendu le syndicat, s06) : Raymonde ; on porte la paie au lieu de « survivre » à la porte de
    l'usine (jamais un lieu de mission) ; `s13` — livré à la fourrière, pas à l'usine.
  - ⚠️ **Six balises que v3 ne connaît pas** (`hesitantly`, `seriously`, `urgently`) — `test_interpretation` les a
    prises après la génération : refaites (≈ 550 caractères). Lancer `test_les_balises_sont_celles_que_v3_comprend`
    AVANT de générer.
  - **Juges** : `tests/test_erables_shop_suite_js.py` (neuf, au bouton de la poignée de main à la prime : chaque
    mission ; `e08` et `e09` trop lents ; `e11` des deux côtés de la question ; `s13` une égratignure, pas de prime) ;
    mutations : `obtenir` qui ne lit que les noms de porte (rouge), la prime de `s13` retirée (rouge).
  - **Voix** : 58 (≈ 6 000 caractères, six refaites pour leurs balises, trois pour la question déplacée), générées et
    mesurées, pas écoutées.
- **1er oct. 2026 : vague 22 — le p'tit perdu : quelqu'un qui se cache, et `t07`.** Le type neuf `chercher` (Martin :
  « construis la mécanique manquante si elle est simple et sûre ») : quelqu'un (`qui`, un archétype) se cache à quatre
  à `rayon` tuiles de `ou` (le donneur, par défaut) — un trottoir collé à un mur ou à un décor, jamais la chaussée,
  l'eau ni le pas d'une porte. Sa place vient de l'empreinte (le jour, la mission), parmi celles d'une spirale ; il naît
  avec un dé PRÊTÉ et hors de la suite des numéros (`Histoire.poserLaCachette`, le patron du passant de `jobs.js`) : la
  ville ne glisse pas. Caché, on ne le voit pas ; la flèche mène au coin, puis se tait ; la ligne d'objectif dit FROID,
  TIÈDE, CHAUD, BRÛLANT. Trouvé (à pied, à deux pas), il te suit comme un escorté (`majProtege`) ; le `retourner` qui
  suit ne se fait pas sans lui (« IL EST PAS AVEC TOI »). Recette : `docs/comment-monter-les-missions.md` § 4.
  - `t07` (la mère inquiète, de partout, _Le p'tit est perdu_ — 60 $) : son p'tit joue à la cachette depuis vingt
    minutes ; on le trouve, il nous suit, elle le chicane comme du monde.
  - **Restent `t08` et `t10`** : tous deux finissent DANS l'usine (trois boîtes à porter, le machiniste avant son
    quart), qui n'est jamais un lieu de mission — sa cour ferme la nuit (`carte.BARRIERES`), et une petite job ne sait
    ni attendre une heure ni s'offrir seulement de jour (ni `exige`, ni barrière ouverte). La mécanique manquante :
    une job qui ne s'offre qu'aux heures où son lieu est ouvert, et le juge des barrières qui l'accepte — à trancher
    avec Martin. `e03` (Biscuit) veut un chien (aucun sprite d'animal) et Mme Beaulieu (personnage, voix, fiche).
  - **Juges** : `tests/test_cachette_js.py` (deux : t07 jouée au bouton — caché et invisible, à quatre à onze tuiles,
    ni l'eau ni la chaussée, FROID → BRÛLANT, trouvé à pied, il suit, sans lui le retour attend, avec lui la mère
    paie ; il se cache sans un dé de la ville ni un de ses numéros, au même endroit la même journée) ; mutations : la
    règle « pas sans lui » retirée (rouge), le dé prêté retiré (rouge). `test_missions.py` : `qui` est un archétype.
