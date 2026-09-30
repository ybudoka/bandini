# Bandini — ce qu'il reste à faire

Ce fichier ne porte que **le travail qui reste** : la table des lignes à faire ou en cours, leur ordre, et les dettes. La fiche de chaque ligne, et tout le reste, ont leur fichier — voir « Où est le reste ». Une ligne **livrée** quitte ce fichier pour [jalons/README.md](jalons/README.md).

Pour reprendre le travail (les commandes, l'audio, la mise en ligne) : [reprendre-le-travail.md](reprendre-le-travail.md).

## Où est le reste

| Pour savoir… | Lire |
|---|---|
| ce qu'une ligne ci-dessous **prévoit** (sa fiche) ou a **déjà livré** (ses notes) | son fichier dans [jalons/](jalons/README.md), lié depuis la table |
| ce qui est **livré** (298 jalons) | [jalons/README.md](jalons/README.md) |
| comment lancer le jeu, régénérer l'audio, mettre en ligne, lire la trace | [reprendre-le-travail.md](reprendre-le-travail.md) |
| le contexte, les décisions prises avec Martin, la vision | [vision.md](vision.md) |
| l'architecture, et **la carte du dépôt** (arborescence, modules Python, scripts JS) | [architecture.md](architecture.md) |
| le serveur, les tests et la CI, la vérification de bout en bout, les risques | [exploitation.md](exploitation.md) |
| les voix de l'histoire (une voix par personnage) | [voix-de-l-histoire.md](voix-de-l-histoire.md) |
| qui sont les personnages : leur histoire, leur personnalité, comment ils parlent et se présentent | [personnages/](personnages/README.md) |
| les missions mises en scène, et le jeu d'acteur | [missions-en-scene.md](missions-en-scene.md), [jeu-d-acteur.md](jeu-d-acteur.md), [comment-monter-les-missions.md](comment-monter-les-missions.md) |
| écrire drôle, et l'inventaire des textes du jeu | [ecrire-drole.md](ecrire-drole.md) |
| l'inventaire de la ville (districts, bâtiments, véhicules, personnages…) | [carte.md](carte.md) |

Les sections que ce plan avait avant d'être fragmenté (20 sept. 2026), et où elles sont :

| Section d'avant | Maintenant |
|---|---|
| Les répliques disent le bon moment | ⬜ **en cours** | 30 sept. 2026 | **P2** | **correctif** | [fiche](jalons/les-repliques-disent-le-bon-moment.md#fiche) |
| « État des jalons » | ⬜ dans « À faire », ci-dessous ; ✅ dans [jalons/README.md](jalons/README.md) |
| « Notes des jalons » | sous « Notes » dans le fichier de chaque jalon, [jalons/](jalons/README.md) |
| « La suite » | l'ordre : « L'ordre », ci-dessous ; les fiches : sous « Fiche » dans le fichier de chaque jalon |
| « Dettes » | ci-dessous |
| « Reprendre le travail » | [reprendre-le-travail.md](reprendre-le-travail.md) |
| « Contexte », « La vision » | [vision.md](vision.md) |
| « Les voix de l'histoire » | [voix-de-l-histoire.md](voix-de-l-histoire.md) |
| « Les missions mises en scène », « Le jeu d'acteur » | [missions-en-scene.md](missions-en-scene.md) |
| « Architecture », « Arborescence du dépôt » | [architecture.md](architecture.md) |
| « Serveur », « Tests et CI », « Vérification de bout en bout », « Risques et parades » | [exploitation.md](exploitation.md) |
| « Jalons (chacun jouable, testé, déployé) » | [jalons/les-jalons-de-la-v1.md](jalons/les-jalons-de-la-v1.md) |

## À faire

Les lignes **à faire** et **en cours**, **par priorité**, prérequis devant : l'ordre et ses règles sont
dans « L'ordre » plus bas. Une ligne **livrée** ne reste pas ici : elle passe dans
[docs/jalons/README.md](jalons/README.md).

⚠️ **Une colonne, une question** — chaque ligne se lit en quatre coups d'œil avant d'ouvrir sa fiche :

- **État** — ⬜ `à faire` ou `en cours` (le ✅ `livré` n'existe que dans les jalons livrés). L'icône va
  **devant** l'état, et le juge de la table la refuse absente ou fausse. Une seule chose s'y lit d'un
  balayage : ce qui bouge en ce moment. ⚠️ **On passe une ligne à `en cours` et on la pousse _avant_
  d'écrire le code** — plusieurs sessions travaillent dans le même arbre, et cette colonne est le seul
  endroit où elles se voient.
- **Date** — pour une ligne `en cours`, le jour où elle a commencé ; `—` tant que rien n'a commencé.
- **Prio** — « qu'est-ce qui coûte le plus cher à ne pas faire ? » : **P1** le jeu ment, **P2** ça se
  sent à chaque partie, **P3** ça porte le reste, **P4** ça enrichit ; l'échelle est détaillée dans
  « L'ordre ».
- **Genre** — un **correctif** répare une promesse que le jeu fait déjà et ne tient pas ; un **ajout**
  en fait une nouvelle. Il suit les préfixes de commit du dépôt (`fix:` et `feat:`).
- **Notes** — un ou deux liens, et rien d'autre, tous vers **le fichier du jalon** dans `docs/jalons/` :
  `[fiche](jalons/….md#fiche)` mène à ce qui est **prévu** (la fiche : la demande, le pourquoi, ce que ça
  coûte), `[notes](jalons/….md#notes)` à ce qui est **déjà livré**. ⚠️ Une ligne de table ne se replie pas :
  le 17 sept. 2026 la plus longue faisait 22 000 caractères, et plus personne ne lisait la table. On peut
  encore écrire son plan dans la cellule, puis le ranger — la commande crée le fichier du jalon, y met
  le texte en forme sous « Fiche » (un paragraphe par vague, une puce par ⚠️) et pose le lien ; le juge
  refuse un texte resté dans la table : `uv run python scripts/verifier_table_des_jalons.py --ranger`

⚠️ **Livrer une ligne** ne déplace que la ligne : elle **quitte** cette table et s'ajoute en bas de
[docs/jalons/README.md](jalons/README.md), en `✅ **livré**` avec sa date. Son fichier ne bouge pas — sa
fiche y est déjà, et la note de livraison s'écrit dessous, sous « Notes ». Le juge refuse une ligne ✅
restée ici et une ligne ⬜ passée là-bas.

⚠️ **Prendre une ligne neuve** : sa ligne ici, et son fichier `docs/jalons/<jalon>.md` (sous « Fiche », ce
qu'on veut faire et pourquoi) — `--ranger` le crée depuis le texte écrit dans la cellule Notes.

⚠️ **Toute ligne à faire doit porter sa prio et son genre** : ce sont eux qui décident de l'ordre.

⚠️ Les numéros de jalon sont des **noms**, pas un ordre : tout le dépôt y renvoie, alors ils ne bougent
pas quand l'ordre de travail change.

| Jalon | État | Date | Prio | Genre | Notes |
|---|---|---|---|---|---|
| La foire fermée l'hiver, et le tour de ce qui ferme | ⬜ **en cours** (tranché par Martin : fermée tant que la neige tient, cadenassée, les missions du Bonimenteur attendent ; le tour — derby, crème glacée, fruits de mer, amuseurs, piscines, fontaine, BBQ, chaloupes ; et l'hiver amène le jongleur de feu, les foyers, le chocolat chaud ; trois vagues) | 30 sept. 2026 | **P2** | **correctif** | [fiche](jalons/la-foire-fermee-l-hiver.md#fiche) |
| La plage l'hiver | ⬜ **en cours** | 30 sept. 2026 | **P2** | **correctif** | [fiche](jalons/la-plage-l-hiver.md#fiche) |
| Des chocs qui sonnent ce qu'ils frappent, et des pas qui sonnent le sol | ⬜ **en cours** | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/des-chocs-qui-sonnent-ce-qu-ils-frappent-et-des-pas-qui-sonnent-le-sol.md#fiche) |
| Les bateaux ne sont pas des chars | ⬜ **en cours** (tranché par Martin : tout, en cinq vagues — la conduite, les règles de char, le plongeon et la police de terre, la vedette de police, l'habillage et l'hiver ; ✅ vague 1 livrée : la conduite — la poupe chasse, la machine arrière au lieu du frein, la météo reste sur la rue ; ✅ vague 2 livrée : ni fourrière, ni remorqueuse, ni garage, ni place de stationnement pour une coque, BATEAUX VOLÉS au carnet, et le traversier n'accoste plus sur une coque ; ensuite la vague 3, le plongeon et la police de terre) | 30 sept. 2026 | **P2** | **correctif** | [fiche](jalons/les-bateaux-ne-sont-pas-des-chars.md#fiche) · [notes](jalons/les-bateaux-ne-sont-pas-des-chars.md#notes) |
| Une route en lacets vers le chalet | ⬜ **en cours** (tranché par Martin le 30 sept. 2026 : la première route courbe, dans le rang — des lacets dans le bois, le chalet au bout du chemin, du gravier qui ralentit, un tracé lisse sur la grille) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/une-route-en-lacets-vers-le-chalet.md#fiche) |
| Des bagarres de gangs vivantes, et armées | ⬜ **en cours** (tranché par Martin le 30 sept. 2026 : un seul cerveau pour la rixe et le gang contre toi, un arsenal par gang porté par un membre sur trois, quatre vagues — le contact, la fusillade, le moral, les renforts) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/des-bagarres-de-gangs-vivantes-et-armees.md#fiche) |
| Des intérieurs fidèles à l'extérieur : la revue complète | ⬜ **en cours** (✅ vague 1 livrée : le mur de la porte harmonisé, un seul plâtre dans toutes les pièces ; ensuite la revue, et les logements selon le standing) | 29 sept. 2026 | **P2** | **correctif** | [fiche](jalons/des-interieurs-fideles-a-l-exterieur.md#fiche) |
| Le décor, les bêtes et les gens répondent — deuxième vague | ⬜ **en cours** (livrés : manger au barbecue, caresser le chat, vider un parcomètre, arracher une affiche ; le buisson est annulé ; restent le caddie et le panneau, à préciser par Martin) | 22 sept. 2026 | **P4** | ajout | [fiche](jalons/le-decor-les-betes-et-les-gens-repondent.md#fiche-de-la-deuxième-vague) |
| Des blocs de carte en extensions | ⬜ **en cours** (✅ vagues 1 à 3 livrées : à pied, au volant, à deux, la police qui reprend au bord, et le premier vrai bloc — le chalet du rang, la deuxième planque ; reste « un vrai dehors », avec le bloc qui en aura besoin) | 25 sept. 2026 | **P3** | ajout | [fiche](jalons/des-blocs-de-carte-en-extensions.md#fiche) |
| Charger les districts autour du joueur | ⬜ **en cours** (✅ vague 1 livrée : la carte voyage pliée, 70 538 → 52 129 octets gzip, plafond 55 000, une garde par clé ; ✅ vague 2 livrée : le serveur compresse les paquets une fois au niveau 9, la carte à 50 Ko sur le fil au lieu de 98 derrière nginx ; les vagues : la carte voyage pliée, le fil compressé une fois au plus fort, les pièces à part, le squelette et les morceaux par district ; la suite attend le téléphone de Martin) | 30 sept. 2026 | **P3** | **correctif** | [fiche](jalons/charger-les-districts-autour-du-joueur.md#fiche) · [notes](jalons/charger-les-districts-autour-du-joueur.md#notes) |
| Des étages pour vrai, des maisons de luxe et des terrains clôturés | ⬜ **en cours** (demandé par Martin le 30 sept. 2026 ; trois vagues : les étages, les terrains clôturés, les maisons de luxe ; ✅ vague 1, les étages : les logements et les commerces ; ✅ vague 2, les terrains clôturés) | 30 sept. 2026 | **P2** | ajout | [fiche](jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md#fiche) |
| Des étages dedans aussi | ⬜ **en cours** (demandé par Martin le 30 sept. 2026 : autant de niveaux dedans que la façade en peint ; en haut d'un commerce, le logement du commerçant ; Python compte, le JS peint) | 30 sept. 2026 | **P2** | ajout | [fiche](jalons/des-etages-dedans-aussi.md#fiche) |
| La réputation et la lecture des passants | ⬜ **à faire** (à trancher par Martin) | — | **P4** | ajout | [fiche](jalons/la-reputation-et-la-lecture-des-passants.md#fiche) |
| M16 Cent missions | ⬜ **en cours** (la tranche 1 « le moteur » avance : dix missions de plus livrées — `f04`, `f05`, `f06`, `f07`, `f09`, `f11`, `h01`, `p01`, `q03`, `e12` — avec le premier juge de banc joué pour huit des neuf types neufs ; ✅ **tout ce qui sert à JOUER une mission est sorti du paquet** — répliques, scènes, voix et objectifs, par `/api/mission/<slug>` avec son ETag : 369 224 → **220 367** octets bruts, 75 138 → **48 971** gzip, le juge est vert et le catalogue passe de 170 à 53 octets gzip par mission (**94 missions de marge** au lieu de cinq) ; ✅ **quatre missions de plus** — `q01` (Lulu), `q10`/`q11` (le premier choix du catalogue, Sven ou Josée), `s08` (Gilles) ; ✅ **28 sept. : `eteindre` allume son feu, le téléphone trie, l'arc F est au complet** — `f13` (Mado, trois feux), `f10` (Rosa, la chemise, Norbert), `f12` (les cinq enveloppes) ; et la rue lit enfin `libere` et `calme` (un district libéré se vide de son gang, un gang calmé ne te saute plus dessus) ; restent les arcs Q, E, S, P, H, D, C, R, T, I, X (≈ 70 missions) ; ⬜ **29 sept. : en cours, le chemin vers les quatre libérations** qu'attend _Le Boss_ — 19 missions par vagues, un arc à la fois ; ✅ **vague 1 : les Quais sont libres** (`q05` Cindy, `q06` le Beau Denis à mains nues, `q13` la nuit des Morues — `libere: quais`) ; ✅ **vague 2 : les Érables sont libres** (`e04` Jo, `e06`/`e07` Diane, le maire et son dossier, `e10` — c'était Jo — `libere: erables` ; trois districts : _Marco te vend_ s'ouvre) ; ✅ **vague 3 : La Pointe est libre** (`p02`, `p05`, `p04` — la première `course` —, `p09`, `p10`, `p11` — `libere: pointe` ; quatre districts : ce que _Le Boss_ demande) ; ✅ **vague 4 : La Shop est libre** (`s02`, `s06`, `s05`, `s09`, `s10`, `s11` — l'accord porté sans arme, `libere: shop`) — **les quatre libérations sont livrées** ; ✅ **vague 5 : l'hôtel est à vendre** (`q07`, Norbert et la chambre 12 — `donne.a_vendre`, la quatrième propriété de _Le Boss_) ; ⬜ **30 sept. : en cours, vague 6 — l'arc D, la dette de Rocco** (`d01`–`d08` : Sal le barbier, ses Ciseaux, Me Desjardins ; la dette du carnet bouge enfin, et `d07`/`d08` se ferment l'une l'autre)) | 18 sept. 2026 | **P4** | ajout | [fiche](jalons/m16-cent-missions.md#fiche) · [notes](jalons/m16-cent-missions.md#notes) |
| Des missions en chapitres, de cinq à dix minutes | ⬜ **en cours** | 30 sept. 2026 | **P2** | ajout | [fiche](jalons/des-missions-en-chapitres.md#fiche) |
| Générer les bruitages qui n'ont aucun équivalent payé | ⬜ **en cours** (Martin, 30 sept. 2026 : on les génère) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/les-bruitages-qui-n-ont-aucun-equivalent-paye.md#fiche) |
| Les territoires des gangs bougent | ⬜ **en cours** (✅ vague 1 livrée : la force de chaque gang, un coin par nuit à la frontière, jamais le cœur, l'îlot pris qui se peuple de son nouveau gang, le Clairon et la carte ; ✅ vague 2 livrée : reprendre un coin, le nom sous la mini-carte, la légende ; ✅ vague 3 livrée : les graffitis suivent la frontière — les tags de qui tient le coin, ceux du perdant barrés ; reste : les Mantes) | 29 sept. 2026 | **P4** | ajout | [fiche](jalons/les-territoires-des-gangs-bougent.md#fiche) |
| Le marché aux puces du dimanche | ⬜ **en cours** (après les bebelles et les sauts des collections : les cartes qui manquent et les meubles `ou: puces`) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/le-marche-aux-puces-du-dimanche.md#fiche) |
| Les quatre saisons, réalistes | ⬜ **en cours** (tranché par Martin : six lots, l'Halloween et la pluie compris ; ✅ lot 1 livré : le paysage des quatre saisons, la neige l'hiver seulement, la longueur du jour, la triche « mois suivant » ; ✅ lot 2 livré : la pluie, les orages, les flaques, la gadoue d'avril, les feuilles d'octobre ; ✅ lot 3 livré : l'Halloween — citrouilles, lumières, déguisés, enfants, la maison hantée, la musique ; ✅ lot 4 livré : les gens et la rue — la garde-robe des saisons (manteau, tuque et bottes l'hiver, t-shirt et short l'été) et le parapluie, puis la rue des saisons : bancs de neige, abris Tempo, cheminées qui fument, terrasses de l'été ; ✅ lot 5 livré : le son des saisons — le vent et la charrue l'hiver, la fonte et les merles, les cigales et la tondeuse, les feuilles et les outardes, en fondu enchaîné ; ✅ vague 4c livrée : les restes tranchés par Martin — les personnages et le joueur habillés dehors, les enfants en habit de neige, des manteaux d'hiver de vraies couleurs, terrasses et Tempo solides, les bornes-fontaines ouvertes de la canicule et leurs enfants ; lot 6 en cours : la glace et le vrai dérapage — ✅ vague 6a livrée, le dérapage (sous-virage, survirage, contre-braquage, roues bloquées, traces et crissement) ; vague 6b à faire, la glace) | 29 sept. 2026 | **P4** | ajout | [fiche](jalons/les-quatre-saisons-realistes.md#fiche) · [notes](jalons/les-quatre-saisons-realistes.md#notes) |
| Les explosifs : grenades, dynamite, C4, roquettes — et le Molotov en mieux | ⬜ **en cours** (✅ vague 1 livrée : l'explosion commune, la grenade et la dynamite ; reste la vague 2, le Molotov en mieux ; puis les murs fissurés et le C4, le char piégé et le lance-roquettes) | 28 sept. 2026 | **P4** | ajout | [fiche](jalons/les-explosifs.md#fiche) · [notes](jalons/les-explosifs.md#notes) |
| Le train : au sol, sur le viaduc, dans le tunnel | ⬜ **en cours** (✅ vague 1 livrée : le train passe — au sol dans les Friches, sur son viaduc au-dessus du Petit-Canton, à la gare centrale, dans son tunnel ; les passages à niveau, il écrase et il klaxonne ; restent : on monte (vague 2), on s'assoit (vague 3)) | 29 sept. 2026 | **P4** | ajout | [fiche](jalons/le-train.md#fiche) · [notes](jalons/le-train.md#notes) |

## L'ordre

Règle inchangée : **chaque vague reste jouable, testée, déployée**.

⚠️ **Le tri est un tri de PRIORITÉ, pas de taille.** Quatre niveaux, et ils répondent à une
seule question : qu'est-ce qui coûte le plus cher à ne pas faire ?

- **P1 — le jeu ment.** Quelque chose est promis et pas tenu : un catalogue qui annonce des
  chars que rien ne dessine, un défi affiché qu'on ne peut pas gagner. C'est ce qui coûte le
  plus cher, parce que ça se paie en confiance et qu'aucun ajout ne la rachète.
- **P2 — ça se sent à chaque partie**, et ça coûte une bouchée. Un défaut qu'on rencontre à
  chaque mort, à chaque parc, à chaque nouvelle partie — et dont le mécanisme existe déjà.
- **P3 — ça porte le reste.** Ce qui redessine la ville ou débloque d'autres fiches. À faire
  avant ce qui s'appuie dessus, sinon on ajuste deux fois.
- **P4 — ça enrichit**, du plus utile au moins.

À l'intérieur d'un niveau : le moins cher d'abord, le correctif avant l'ajout, et les
prérequis toujours devant.

Ce que chaque ligne à faire attend (la table de tri du 13 sept. 2026, réduite à ce qui reste ; la table entière est dans [jalons/le-tri-du-13-sept-2026.md](jalons/le-tri-du-13-sept-2026.md)) :

| P | Genre | Ce qu'il y a à faire | Taille | Pourquoi là, et ce qu'il attend |
|---|---|---|---|---|
| **P2** | **correctif** | Des intérieurs fidèles à l'extérieur : la revue complète | 4 | Martin (29 sept. 2026) : « des intérieurs toujours représentatifs de l'extérieur » — on pousse des portes à chaque partie ; la taille est déjà tenue, reste le contenu (standing, district, genre du bâtiment) ; rien au dé, un juge par règle sur toutes les portes, et une capture dedans et dehors |
| **P2** | ajout | Des missions en chapitres, de cinq à dix minutes | 6 | Martin (30 sept. 2026) : « au moins 5 à 10 minutes chacune » — chaque mission se joue, donc ça se sent à chaque partie ; le moteur (actes, reprises, chronomètre, options et types neufs) et le pilote de La Pointe d'abord, puis un arc à la fois ; remplace le compte de M16 |
| **P3** | ajout | Des blocs de carte en extensions | 3 | ⚠️ **porte** la deuxième planque, la cabane à sucre, le centre d'achat hanté et le ciné-parc ; une carte à part derrière un fondu au noir (Martin) — le mécanisme des pièces, en plein air et au volant ; l'île et l'aéroport ne bougent pas |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | M16 Cent missions | 8 (4 × 2) | le **carnet** d'abord (c'est lui qui rend cent missions lisibles) et **les missions mises en scène** (chaque mission porte ses scènes et ses dialogues) ; ⚠️ les dialogues et les scènes sortent du paquet ; M13 en est la dernière tranche |
| **P4** | ajout | Les territoires des gangs bougent | 3 | `libere` et `calme` de M16 d'abord ; à trancher avec « La réputation et la lecture des passants » |
| **P4** | ajout | Le marché aux puces du dimanche | 2 | après **les collections** (il vend leurs meubles et leurs cartes) |
| **P4** | ajout | Les quatre saisons, réalistes | 4 | le **calendrier** est livré (`calendrier.py`) ; ⚠️ touche au rendu de toute la ville **et** à la physique : la sonde de performance et le rythme sur le vrai téléphone ; ce qui se pose, en dernier et sans dé ; gagne à suivre **les toits** (la neige sur les toits) |
| **P4** | ajout | Les explosifs : grenades, dynamite, C4, roquettes — et le Molotov en mieux | 4 | rien ne l'attend ; ⚠️ les murs fissurés posés **en dernier, sans dé** (sinon la ville glisse), et seulement là où il y a du sol des deux côtés ; le feu du Molotov borné (le rythme sur le téléphone) |

M8 porte tout le reste (les gangs, les fins, le traversier, la fourrière ont besoin de la
ville complète) ; il est livré. Rien n'oblige à suivre la liste à la lettre : à l'intérieur
d'un niveau de priorité, on prend ce dont on a envie. Mais **on ne descend pas d'un niveau
tant qu'il en reste au-dessus** — c'est tout ce que le tri veut dire.

Ce que la suite **ne fait pas**, pour que le plan tienne : pas de multijoueur en ligne, pas
de 3D, pas d'histoire à plus de deux fins, pas de génération de sprites par IA. Le jeu
reste un GTA 1 québécois en pixels, joué au téléphone.

⚠️ **La coop EN LIGNE n'est pas promise — mais la porte lui reste ouverte** (Martin,
22 sept. 2026 : « il faut laisser la possibilité d'avoir un mode coop online »). Rien de
réseau n'est écrit et rien n'est prévu ; ce qui existe, c'est le *joint* : chaque joueur
porte sa **source d'entrées** (`Entree.SOURCE1`/`SOURCE2`, `j.entree`), et tout ce qui le
fait bouger, frapper ou agir lit cette source-là plutôt que le clavier. Une source remplie
depuis le réseau se brancherait au même endroit. Le jour où ça se décide, ça devient un
jalon à part — avec son serveur, sa latence et ses tricheurs.

⚠️ **Un compte (M14) n'est pas du multijoueur.** Deux joueurs ne se voient jamais dans la
même ville ; le serveur ne fait que garder une partie et un classement. La ligne ci-dessus
tient : c'est une sauvegarde qui voyage, pas une partie partagée — et le jeu continue de
tourner entièrement dans le navigateur, compte ou pas.

## Dettes

⚠️ Ce qui est **sciemment pas fait**. Ça vivait éparpillé dans les notes de jalons, là où on
ne relit jamais — et une dette qu'on ne relit pas devient un oubli. Chacune porte donc son
**déclencheur** : la chose qui dit qu'il est temps de la payer. Une dette sans déclencheur
est un oubli avec du style.

| Dette | Pourquoi pas fait | Déclencheur |
|---|---|---|
| Le **rythme mesuré sur le vrai téléphone** de Martin (reporté de M7) | Les chiffres du banc (0,29 ms/image de nuit à 5★) sont ceux d'une machine de développement | Avant M12 : la neige touche à la physique **et** au rendu, c'est là que le budget casse |
| Les **districts chargés autour du joueur** (⚠️ `/api/carte` et son ETag sont **livrés** le 16 sept. 2026 : la carte voyage à part, mais entière ; ⚠️ **en cours** depuis le 30 sept. 2026 : [fiche](jalons/charger-les-districts-autour-du-joueur.md#fiche) ; la carte voyage pliée, 52 Ko gzip) | 43 Ko gzip aujourd'hui (370 Ko bruts ; plafond brut relevé à 600 le 13 sept. 2026, parce qu'il n'est qu'un indicateur : le fil et `JSON.parse` sont les vraies bornes) : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin |

⚠️ Et une **fausse** dette, pour qu'on arrête de la reprendre : `tests/test_navigateur.py` est
exclu de la commande de tous les jours ci-dessous parce qu'il monte un Chromium et prend des
minutes — mais il fait partie de **la suite de livraison** (la deuxième commande), qu'on fait
tourner en local avant chaque mise en ligne. Il n'est pas oublié, il est ailleurs.
