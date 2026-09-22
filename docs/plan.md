# Bandini — ce qu'il reste à faire

Ce fichier ne porte que **le travail qui reste** : la table des lignes à faire ou en cours, leur ordre, et les dettes. La fiche de chaque ligne, et tout le reste, ont leur fichier — voir « Où est le reste ». Une ligne **livrée** quitte ce fichier pour [jalons/README.md](jalons/README.md).

Pour reprendre le travail (les commandes, l'audio, la mise en ligne) : [reprendre-le-travail.md](reprendre-le-travail.md).

## Où est le reste

| Pour savoir… | Lire |
|---|---|
| ce qu'une ligne ci-dessous **prévoit** (sa fiche) ou a **déjà livré** (ses notes) | son fichier dans [jalons/](jalons/README.md), lié depuis la table |
| ce qui est **livré** (205 jalons) | [jalons/README.md](jalons/README.md) |
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
| La ligne d'histoire : une ouverture et un générique | ⬜ **en cours** (l'ouverture livrée) | 16 sept. 2026 | **P2** | ajout | [fiche](jalons/la-ligne-d-histoire-une-ouverture-et-un-generique.md#fiche) · [notes](jalons/la-ligne-d-histoire-une-ouverture-et-un-generique.md#notes) |
| On ne voit une lampe que si elle regarde l'œil (les phares selon la direction) | ⬜ **en cours** | 22 sept. 2026 | **P2** | **correctif** | [fiche](jalons/on-ne-voit-une-lampe-que-si-elle-regarde-l-oeil.md#fiche) |
| M15 La ville te parle — deuxième vague | ⬜ **en cours** (déjà livrés : la rue qui se tait, les leçons du Clairon, la radio qui parle vraiment, la police à la radio, le souffle du joueur, les bruits de quartier ; restent le bulletin de nouvelles et les répliques par contexte) | 21 sept. 2026 | **P4** | ajout | [fiche](jalons/m15-la-ville-te-parle.md#fiche-de-la-deuxième-vague) |
| Le décor, les bêtes et les gens répondent — deuxième vague | ⬜ **en cours** (livrés : manger au barbecue, caresser le chat, vider un parcomètre ; le buisson est annulé ; restent l'affiche arrachée, le caddie, le panneau) | 22 sept. 2026 | **P4** | ajout | [fiche](jalons/le-decor-les-betes-et-les-gens-repondent.md#fiche-de-la-deuxième-vague) |
| M14 Meta | ⬜ **en cours** (6 vagues livrées : le compte, la session longue, les parties sur le serveur, le jeu qui se synchronise, le NIP, effacer son compte, le défi du jour, et le mode photo ; la coop locale a son essai (un clavier, une manette) — reste le verdict de Martin) | 17 sept. 2026 | **P4** | ajout | [fiche](jalons/m14-meta.md#fiche) · [notes](jalons/m14-meta.md#notes) |
| L'Île-aux-Corneilles — deuxième vague | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/l-ile-aux-corneilles.md#fiche) · [notes](jalons/l-ile-aux-corneilles-deuxieme-vague.md#notes) |
| Quatre activités que le jeu n'a pas | ⬜ **en cours** (2 des 4 livrées : les paliers de boulot, le pompier volontaire ; restent la patrouille, la liste du quai et les frénésies) | 15 sept. 2026 | **P4** | ajout | [fiche](jalons/quatre-activites-que-le-jeu-n-a-pas.md#fiche) · [notes](jalons/quatre-activites-que-le-jeu-n-a-pas.md#notes) |
| La réputation et la lecture des passants | ⬜ **à faire** (à trancher par Martin) | — | **P4** | ajout | [fiche](jalons/la-reputation-et-la-lecture-des-passants.md#fiche) |
| M16 Cent missions | ⬜ **en cours** (la tranche 1 « le moteur » avance : dix missions de plus livrées — `f04`, `f05`, `f06`, `f07`, `f09`, `f11`, `h01`, `p01`, `q03`, `e12` — avec le premier juge de banc joué pour huit des neuf types neufs ; restent `eteindre` (pas de feu qu'une mission puisse allumer elle-même), le téléphone qui trie, et le reste de l'arc F) | 18 sept. 2026 | **P4** | ajout | [fiche](jalons/m16-cent-missions.md#fiche) · [notes](jalons/m16-cent-missions.md#notes) |
| M13 Les deux fins | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/m13-les-deux-fins.md#fiche) · [notes](jalons/m13-les-deux-fins.md#notes) |
| Infiltration : portes verrouillées et gardes privés | ⬜ **en cours** | 22 sept. 2026 | **P4** | ajout | [fiche](jalons/infiltration-portes-verrouillees-et-gardes-prives.md#fiche) |
| Rien de collé devant chez Ti-Paul | ⬜ **en cours** | 22 sept. 2026 | **P2** | **correctif** | [fiche](jalons/rien-de-colle-devant-chez-ti-paul.md#fiche) |
| Le large de l'aéroport se refuse : on vire de bord avant de voir l'île | ⬜ **en cours** | 22 sept. 2026 | **P2** | **correctif** | [fiche](jalons/le-large-de-l-aeroport-se-refuse-on-vire-de-bord-avant-de-voir-l-ile.md#fiche) |
| Plus de temps pour les courses aux flèches | ⬜ **en cours** | 22 sept. 2026 | **P2** | **correctif** | [fiche](jalons/plus-de-temps-pour-les-courses-aux-fleches.md#fiche) |
| Des menus à onglets, et la téléportation vers les défis | ⬜ **en cours** | 22 sept. 2026 | **P2** | ajout | [fiche](jalons/des-menus-a-onglets-et-la-teleportation-vers-les-defis.md#fiche) |

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
| **P2** | ajout | La ligne d'histoire : une ouverture et un générique | 3 | ⚠️ **l'ouverture est livrée** (16 sept. 2026) — elle ne dépendait de rien ; le **générique**, lui, attend **M13** : il n'y a pas de fin à filmer avant |
| **P4** | ajout | M15 La ville te parle | 4 | le narrateur, le journal et les voix existent ; ⚠️ contient un correctif (les passants se répètent) |
| **P4** | ajout | M14 Meta | 4 | de l'**infrastructure** (serveur, BD, comptes, sessions, NIP) : un autre métier que le reste. ⚠️ Rien n'en dépend, et rien n'en doit dépendre : un compte est un **confort**, le jeu se joue serveur éteint |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | Quatre activités que le jeu n'a pas | 2 | ⚠️ la **refonte des véhicules** d'abord (les deux boulots neufs ne demandent aucun char de plus, mais la liste du quai fait regarder le parc de près) |
| **P4** | ajout | M16 Cent missions | 8 (4 × 2) | le **carnet** d'abord (c'est lui qui rend cent missions lisibles) et **les missions mises en scène** (chaque mission porte ses scènes et ses dialogues) ; ⚠️ les dialogues et les scènes sortent du paquet ; M13 en est la dernière tranche |
| **P4** | ajout | M13 Les deux fins | 4 | **M8** pour les districts, et ça gagne à suivre **M10** : la dette de Rocco est le fil des deux fins. C'est la fin — elle se pose en dernier |

M8 porte tout le reste (les gangs, les fins, le traversier, la fourrière ont besoin de la
ville complète) ; il est livré. Rien n'oblige à suivre la liste à la lettre : à l'intérieur
d'un niveau de priorité, on prend ce dont on a envie. Mais **on ne descend pas d'un niveau
tant qu'il en reste au-dessus** — c'est tout ce que le tri veut dire.

Ce que la suite **ne fait pas**, pour que le plan tienne : pas de multijoueur en ligne, pas
de 3D, pas d'histoire à plus de deux fins, pas de génération de sprites par IA. Le jeu
reste un GTA 1 québécois en pixels, joué au téléphone.

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
| Les **districts chargés autour du joueur** (⚠️ `/api/carte` et son ETag sont **livrés** le 16 sept. 2026 : la carte voyage à part, mais entière) | 43 Ko gzip aujourd'hui (370 Ko bruts ; plafond brut relevé à 600 le 13 sept. 2026, parce qu'il n'est qu'un indicateur : le fil et `JSON.parse` sont les vraies bornes) : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin |
| **Aucune limite d'essais** à la connexion par mot de passe (M14) | scrypt coûte un moment par essai et deux workers n'en font que quelques-uns à la fois ; et bloquer un pseudo après N échecs laisserait n'importe qui verrouiller le compte d'un autre — la raison même pour laquelle le NIP ne bloque pas le compte | La **2e vague de M14** : le jour où le jeu montre l'écran de connexion à tout le monde (une limite par adresse, pas par pseudo). ⚠️ **Échue** : l'écran est en ligne depuis le 17 sept. 2026, et la confirmation d'effacement (4e vague) est un second endroit où l'on devine un mot de passe |

⚠️ Et une **fausse** dette, pour qu'on arrête de la reprendre : `tests/test_navigateur.py` est
exclu de la commande de tous les jours ci-dessous parce qu'il monte un Chromium et prend des
minutes — mais il fait partie de **la suite de livraison** (la deuxième commande), qu'on fait
tourner en local avant chaque mise en ligne. Il n'est pas oublié, il est ailleurs.
