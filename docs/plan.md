# Bandini — ce qu'il reste à faire

Ce fichier ne porte que **le travail qui reste** : la table des lignes à faire ou en cours, leur ordre, et les dettes. La fiche de chaque ligne, et tout le reste, ont leur fichier — voir « Où est le reste ». Une ligne **livrée** quitte ce fichier pour [jalons/README.md](jalons/README.md).

Pour reprendre le travail (les commandes, l'audio, la mise en ligne) : [reprendre-le-travail.md](reprendre-le-travail.md).

## Où est le reste

| Pour savoir… | Lire |
|---|---|
| ce qu'une ligne ci-dessous **prévoit** (sa fiche) ou a **déjà livré** (ses notes) | son fichier dans [jalons/](jalons/README.md), lié depuis la table |
| ce qui est **livré** (308 jalons) | [jalons/README.md](jalons/README.md) |
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
| Le lave-auto qu'on traverse, en vitre | ⬜ **en cours** (tranché par Martin : de la rue à la ruelle, sous un toit de verre, un convoyeur qui tire le char, la police voit sans entrer, l'étoile tombe à la sortie) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/le-lave-auto-qu-on-traverse.md#fiche) |
| Des blocs de carte en extensions | ⬜ **en cours** (✅ vagues 1 à 3 livrées : à pied, au volant, à deux, la police qui reprend au bord, et le premier vrai bloc — le chalet du rang, la deuxième planque ; reste « un vrai dehors », avec le bloc qui en aura besoin) | 25 sept. 2026 | **P3** | ajout | [fiche](jalons/des-blocs-de-carte-en-extensions.md#fiche) |
| Charger les districts autour du joueur | ⬜ **en cours** (✅ vague 1 livrée : la carte voyage pliée, 70 538 → 52 129 octets gzip, une garde par clé ; ✅ vague 2 livrée : le serveur compresse les paquets une fois au niveau 9 ; le découpage révisé le 1er oct. 2026 après la remesure — ce sont les SCRIPTS qui faisaient attendre, 1,56 Mo sur 1,68 en 3G rapide, et une mise en ligne les faisait tous repartir : ✅ vague 3 livrée, les scripts à l'empreinte de leur contenu ; ✅ vague 4 livrée, les scripts maigrissent, 1 535 → 750 Ko sur le fil ; ✅ vague 5 livrée, les paquets partent avec les scripts — l'écran titre en 3G rapide de 12,6 à 7,7 s à la première visite, de 2,6 à 2,1 s aux suivantes ; restent les pièces à part et le squelette par district, le second attend une décision de Martin) | 30 sept. 2026 | **P3** | **correctif** | [fiche](jalons/charger-les-districts-autour-du-joueur.md#fiche) · [notes](jalons/charger-les-districts-autour-du-joueur.md#notes) |
| Le grand garage souterrain | ⬜ **en cours** (tranché par Martin : on descend en char par le rideau du Garage Bandini, ou à pied par un ascenseur ; ouvert quand le garage est à toi ; deux niveaux de dix cases, le −2 à 10 000 $ ; un char volé reste volé, pas de descente avec des étoiles ; deux vagues — le −1, puis le −2 ; ✅ vague 1 livrée : le −1, dix cases, le rideau et l'ascenseur, les chars rangés dans la partie, à l'abri du ciel ; reste la vague 2, le −2 et les sons) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/le-grand-garage-souterrain.md#fiche) |
| Des missions en chapitres, de cinq à dix minutes | ⬜ **en cours** (✅ tranche 1 livrée : le moteur — actes, REPRENDRE L'ACTE, chronomètre, renforts, poursuite, tenir, relais — et La Pointe en six actes ; Martin l'a joué, « on y va » : les autres arcs, un par vague, dans l'ordre de la fiche — D, H, L, R, S, E, Q, I ; ✅ vagues D, H, L, R, S, E, Q et I livrées : dix-neuf chapitres, 49 missions devenues des actes ; reste Léo ; Martin a tranché pour C, F et V : les trois arcs passent en chapitres, ⬜ en cours) | 30 sept. 2026 | **P2** | ajout | [fiche](jalons/des-missions-en-chapitres.md#fiche) · [notes](jalons/des-missions-en-chapitres.md#notes) |
| Générer les bruitages qui n'ont aucun équivalent payé | ⬜ **en cours** (Martin, 30 sept. 2026 : on les génère ; ✅ vague 1 livrée : les quatorze sons synthétisés ont leur fichier, chacun dans un lieu chargé au premier geste ; reste : les gestes muets) | 30 sept. 2026 | **P4** | ajout | [fiche](jalons/les-bruitages-qui-n-ont-aucun-equivalent-paye.md#fiche) |
| Les territoires des gangs bougent | ⬜ **en cours** (✅ vague 1 livrée : la force de chaque gang, un coin par nuit à la frontière, jamais le cœur, l'îlot pris qui se peuple de son nouveau gang, le Clairon et la carte ; ✅ vague 2 livrée : reprendre un coin, le nom sous la mini-carte, la légende ; ✅ vague 3 livrée : les graffitis suivent la frontière — les tags de qui tient le coin, ceux du perdant barrés ; reste : les Mantes) | 29 sept. 2026 | **P4** | ajout | [fiche](jalons/les-territoires-des-gangs-bougent.md#fiche) |
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
| **P2** | ajout | Des missions en chapitres, de cinq à dix minutes | 6 | Martin (30 sept. 2026) : « au moins 5 à 10 minutes chacune » — chaque mission se joue, donc ça se sent à chaque partie ; le moteur (actes, reprises, chronomètre, options et types neufs) et le pilote de La Pointe d'abord, puis un arc à la fois ; remplace le compte de M16 |
| **P3** | ajout | Des blocs de carte en extensions | 3 | ⚠️ **porte** la deuxième planque, la cabane à sucre, le centre d'achat hanté et le ciné-parc ; une carte à part derrière un fondu au noir (Martin) — le mécanisme des pièces, en plein air et au volant ; l'île et l'aéroport ne bougent pas |
| **P4** | ajout | Le grand garage souterrain | 3 | Martin (30 sept. 2026) : ranger ses chars et les reprendre plus tard ; le rideau du garage et les blocs à cadres existent ; ⚠️ la ville ne bouge pas (un bloc à part, un point d'ascenseur dans la pièce), les chars rangés vivent en données comme la fourrière, recréés avec leur couleur |
| **P4** | ajout | Le lave-auto qu'on traverse, en vitre | 2 | rien ne l'attend ; la mécanique du rideau de garage existe ; ⚠️ le tunnel se pose **sur la ville finie, sans dé**, et le bureau des piétons se remesure |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | Les territoires des gangs bougent | 3 | `libere` et `calme` de M16 d'abord ; à trancher avec « La réputation et la lecture des passants » |

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
| **Semer le client de la police de m3 tient par la graine** (`test_tronc_plus_long_js`, 30 sept. 2026) : sur huit graines, la 3 et la 4 ratent sur `dev` même — le char roule toute la route et l'étoile ne tombe jamais | Hors du jalon des bagarres, qui ne faisait que déplacer le dé ; le juge est passé de la graine 6 à la 1 | Martin se plaint de ne pas pouvoir semer une étoile en char, ou un autre juge de `semer` flanche d'une graine à l'autre |
| Le **rythme mesuré sur le vrai téléphone** de Martin (reporté de M7) | Les chiffres du banc (0,29 ms/image de nuit à 5★) sont ceux d'une machine de développement | Avant M12 : la neige touche à la physique **et** au rendu, c'est là que le budget casse |
| Les **districts chargés autour du joueur** (⚠️ `/api/carte` et son ETag sont **livrés** le 16 sept. 2026 : la carte voyage à part, mais entière ; ⚠️ **en cours** depuis le 30 sept. 2026 : [fiche](jalons/charger-les-districts-autour-du-joueur.md#fiche) ; la carte voyage pliée, 52 Ko gzip) | 43 Ko gzip aujourd'hui (370 Ko bruts ; plafond brut relevé à 600 le 13 sept. 2026, parce qu'il n'est qu'un indicateur : le fil et `JSON.parse` sont les vraies bornes) : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin. ⚠️ Remesuré le 1er oct. 2026 : JOUER → la ville prend 0,3 s (processeur ×4) ; l'attente est AVANT le titre, et ce sont les scripts (vagues 3 à 5 de la fiche). Nouveau déclencheur du découpage par district : le plafond de la carte pliée (55 000) qui cède |

⚠️ Et une **fausse** dette, pour qu'on arrête de la reprendre : `tests/test_navigateur.py` est
exclu de la commande de tous les jours ci-dessous parce qu'il monte un Chromium et prend des
minutes — mais il fait partie de **la suite de livraison** (la deuxième commande), qu'on fait
tourner en local avant chaque mise en ligne. Il n'est pas oublié, il est ailleurs.
