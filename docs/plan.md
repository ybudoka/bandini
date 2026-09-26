# Bandini — ce qu'il reste à faire

Ce fichier ne porte que **le travail qui reste** : la table des lignes à faire ou en cours, leur ordre, et les dettes. La fiche de chaque ligne, et tout le reste, ont leur fichier — voir « Où est le reste ». Une ligne **livrée** quitte ce fichier pour [jalons/README.md](jalons/README.md).

Pour reprendre le travail (les commandes, l'audio, la mise en ligne) : [reprendre-le-travail.md](reprendre-le-travail.md).

## Où est le reste

| Pour savoir… | Lire |
|---|---|
| ce qu'une ligne ci-dessous **prévoit** (sa fiche) ou a **déjà livré** (ses notes) | son fichier dans [jalons/](jalons/README.md), lié depuis la table |
| ce qui est **livré** (242 jalons) | [jalons/README.md](jalons/README.md) |
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
| Le décor, les bêtes et les gens répondent — deuxième vague | ⬜ **en cours** (livrés : manger au barbecue, caresser le chat, vider un parcomètre ; le buisson est annulé ; restent l'affiche arrachée, le caddie, le panneau) | 22 sept. 2026 | **P4** | ajout | [fiche](jalons/le-decor-les-betes-et-les-gens-repondent.md#fiche-de-la-deuxième-vague) |
| M14 Meta | ⬜ **en cours** (6 vagues livrées : le compte, la session longue, les parties sur le serveur, le jeu qui se synchronise, le NIP, effacer son compte, le défi du jour, et le mode photo ; la coop locale à **deux vrais joueurs** (un clavier, une manette, chacun sur sa source d'entrées : ses coups portent, il suit dans les pièces et monte en passager, portes, missions et volant restent au joueur 1 — la porte reste ouverte à une coop en ligne) ; reste le verdict de Martin, manette en main) | 17 sept. 2026 | **P4** | ajout | [fiche](jalons/m14-meta.md#fiche) · [notes](jalons/m14-meta.md#notes) |
| Des blocs de carte en extensions | ⬜ **en cours** (✅ vagues 1 à 3 livrées : à pied, au volant, à deux, la police qui reprend au bord, et le premier vrai bloc — le chalet du rang, la deuxième planque ; reste « un vrai dehors », avec le bloc qui en aura besoin) | 25 sept. 2026 | **P3** | ajout | [fiche](jalons/des-blocs-de-carte-en-extensions.md#fiche) |
| Le dojo du quartier : apprendre les techniques | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-dojo-du-quartier.md#fiche) |
| Le quartier chinois : un 7e district | ⬜ **à faire** (à trancher par Martin : le nom, la place, la taille) | — | **P3** | ajout | [fiche](jalons/le-quartier-chinois.md#fiche) |
| L'école rivale : un gang qui sait se battre | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/l-ecole-rivale.md#fiche) |
| L'Île-aux-Corneilles — deuxième vague | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/l-ile-aux-corneilles.md#fiche) · [notes](jalons/l-ile-aux-corneilles-deuxieme-vague.md#notes) |
| Quatre activités que le jeu n'a pas | ⬜ **en cours** (2 des 4 livrées : les paliers de boulot, le pompier volontaire ; restent la patrouille, la liste du quai et les frénésies) | 15 sept. 2026 | **P4** | ajout | [fiche](jalons/quatre-activites-que-le-jeu-n-a-pas.md#fiche) · [notes](jalons/quatre-activites-que-le-jeu-n-a-pas.md#notes) |
| La réputation et la lecture des passants | ⬜ **à faire** (à trancher par Martin) | — | **P4** | ajout | [fiche](jalons/la-reputation-et-la-lecture-des-passants.md#fiche) |
| M16 Cent missions | ⬜ **en cours** (la tranche 1 « le moteur » avance : dix missions de plus livrées — `f04`, `f05`, `f06`, `f07`, `f09`, `f11`, `h01`, `p01`, `q03`, `e12` — avec le premier juge de banc joué pour huit des neuf types neufs ; ✅ **tout ce qui sert à JOUER une mission est sorti du paquet** — répliques, scènes, voix et objectifs, par `/api/mission/<slug>` avec son ETag : 369 224 → **220 367** octets bruts, 75 138 → **48 971** gzip, le juge est vert et le catalogue passe de 170 à 53 octets gzip par mission (**94 missions de marge** au lieu de cinq) ; ✅ **quatre missions de plus** — `q01` (Lulu), `q10`/`q11` (le premier choix du catalogue, Sven ou Josée), `s08` (Gilles) ; restent `eteindre` (pas de feu qu'une mission puisse allumer elle-même), le téléphone qui trie, et le reste de l'arc F) | 18 sept. 2026 | **P4** | ajout | [fiche](jalons/m16-cent-missions.md#fiche) · [notes](jalons/m16-cent-missions.md#notes) |
| M13 Les deux fins | ⬜ **en cours** (vague 1 livrée : le générique, et _Sacrer son camp_ — m99, le capitaine Bérubé, `embarquer` ; reste _Le Boss_, qui attend les districts libérés de M16) | 25 sept. 2026 | **P4** | ajout | [fiche](jalons/m13-les-deux-fins.md#fiche) · [notes](jalons/m13-les-deux-fins.md#notes) |
| Infiltration : portes verrouillées et gardes privés | ⬜ **en cours** | 22 sept. 2026 | **P4** | ajout | [fiche](jalons/infiltration-portes-verrouillees-et-gardes-prives.md#fiche) |
| Générer les bruitages qui n'ont aucun équivalent payé | ⬜ **à faire** (⚠️ le quota n'est plus l'obstacle — **nouveau forfait le 24 sept. 2026** ; à trancher par Martin, c'est sa dépense) | — | **P4** | ajout | [fiche](jalons/les-bruitages-qui-n-ont-aucun-equivalent-paye.md#fiche) |
| Des choses à collectionner, et la planque qu'on décore | ⬜ **à faire** (à trancher par Martin : les familles, leur nombre, les meubles) | — | **P4** | ajout | [fiche](jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md#fiche) |
| La cabane à sucre : un événement de printemps | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/la-cabane-a-sucre.md#fiche) |
| Le brouillard de Baie-des-Brumes | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-brouillard-de-baie-des-brumes.md#fiche) |
| Des photos pour le Clairon | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/des-photos-pour-le-clairon.md#fiche) |
| Le garage qui modifie les chars | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-garage-qui-modifie-les-chars.md#fiche) |
| Le hockey de ruelle | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-hockey-de-ruelle.md#fiche) |
| Les territoires des gangs bougent | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/les-territoires-des-gangs-bougent.md#fiche) |
| Le marché aux puces du dimanche | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-marche-aux-puces-du-dimanche.md#fiche) |
| Le 1er juillet, jour du déménagement | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-1er-juillet-jour-du-demenagement.md#fiche) |
| La Saint-Jean sur la baie | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/la-saint-jean-sur-la-baie.md#fiche) |
| La tempête de verglas | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/la-tempete-de-verglas.md#fiche) |
| Braquer un commerce | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/braquer-un-commerce.md#fiche) |
| Les nids-de-poule qui mordent | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/les-nids-de-poule-qui-mordent.md#fiche) |
| Le derby de démolition à la foire | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-derby-de-demolition-a-la-foire.md#fiche) |
| Les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/les-enseignes-qui-ouvrent-pour-vrai.md#fiche) |
| Le pont de glace | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-pont-de-glace.md#fiche) |
| La motoneige | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/la-motoneige.md#fiche) |
| Le centre d'achat hanté | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-centre-d-achat-hante.md#fiche) |
| Le temps des Fêtes | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-temps-des-fetes.md#fiche) |
| Le camion de crème glacée | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-camion-de-creme-glacee.md#fiche) |
| L'orignal de La Pointe | ⬜ **en cours** | 26 sept. 2026 | **P4** | ajout | [fiche](jalons/l-orignal-de-la-pointe.md#fiche) |
| Le ciné-parc | ⬜ **à faire** | — | **P4** | ajout | [fiche](jalons/le-cine-parc.md#fiche) |
| Une amélioration générale des toits | ⬜ **à faire** (à trancher par Martin : la liste, et par où commencer) | — | **P4** | ajout | [fiche](jalons/une-amelioration-generale-des-toits.md#fiche) |

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
| **P3** | ajout | Des blocs de carte en extensions | 3 | ⚠️ **porte** la deuxième planque, la cabane à sucre, le centre d'achat hanté et le ciné-parc ; une carte à part derrière un fondu au noir (Martin) — le mécanisme des pièces, en plein air et au volant ; l'île et l'aéroport ne bougent pas |
| **P3** | ajout | Le quartier chinois : un 7e district | 4 | ⚠️ **porte** l'école rivale ; redessine la ville — donc à côté de la trame, posé en dernier et sans dé (la recette de l'aéroport) ; touche aux frontières des gangs, donc à voir avec « Les territoires des gangs bougent » |
| **P4** | ajout | Le dojo du quartier : apprendre les techniques | 3 | le répertoire des techniques (livré) d'abord ; n'attend rien d'autre |
| **P4** | ajout | L'école rivale : un gang qui sait se battre | 3 | le quartier chinois d'abord (Martin, 26 sept. 2026 : un gang neuf, dans un quartier chinois) |
| **P4** | ajout | M14 Meta | 4 | de l'**infrastructure** (serveur, BD, comptes, sessions, NIP) : un autre métier que le reste. ⚠️ Rien n'en dépend, et rien n'en doit dépendre : un compte est un **confort**, le jeu se joue serveur éteint |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | Quatre activités que le jeu n'a pas | 2 | ⚠️ la **refonte des véhicules** d'abord (les deux boulots neufs ne demandent aucun char de plus, mais la liste du quai fait regarder le parc de près) |
| **P4** | ajout | M16 Cent missions | 8 (4 × 2) | le **carnet** d'abord (c'est lui qui rend cent missions lisibles) et **les missions mises en scène** (chaque mission porte ses scènes et ses dialogues) ; ⚠️ les dialogues et les scènes sortent du paquet ; M13 en est la dernière tranche |
| **P4** | ajout | M13 Les deux fins | 4 | **M8** pour les districts, et ça gagne à suivre **M10** : la dette de Rocco est le fil des deux fins. C'est la fin — elle se pose en dernier |
| **P4** | ajout | Des choses à collectionner, et la planque qu'on décore | 3 | rien ne l'attend ; ⚠️ poser les objets **en dernier, sans dé** (sinon la ville glisse) ; le décor conditionnel de la planque sert aussi à la deuxième |
| **P4** | ajout | La cabane à sucre : un événement de printemps | 3 | une pièce neuve posée sans dé ; la saison est une fenêtre de jours, calculée comme la neige |
| **P4** | ajout | Le brouillard de Baie-des-Brumes | 2 | reprend le mécanisme de la neige (M12) ; ⚠️ la dette du rythme sur le vrai téléphone avant de l'allumer |
| **P4** | ajout | Des photos pour le Clairon | 2 | le **personnage de Louise** d'abord (M16, arc C) ; le mode photo existe |
| **P4** | ajout | Le garage qui modifie les chars | 2 | ⚠️ la vitesse d'un moteur neuf se juge au bouton (la friction) |
| **P4** | ajout | Le hockey de ruelle | 3 | de la physique neuve : la plus chère du lot |
| **P4** | ajout | Les territoires des gangs bougent | 3 | `libere` et `calme` de M16 d'abord ; à trancher avec « La réputation et la lecture des passants » |
| **P4** | ajout | Le marché aux puces du dimanche | 2 | après **les collections** (il vend leurs meubles et leurs cartes) |
| **P4** | ajout | Le 1er juillet, jour du déménagement | 2 | gagne à suivre **les collections** (les meubles du trottoir vont à la planque) |
| **P4** | ajout | La Saint-Jean sur la baie | 3 | les barrières ferment les rues du défilé ; ⚠️ la foule et le rendu sur le vrai téléphone |
| **P4** | ajout | La tempête de verglas | 3 | reprend la neige de M12 et l'éclairage de nuit ; tout doit se rallumer après |
| **P4** | ajout | Braquer un commerce | 2 | rien ne l'attend ; ⚠️ ne jamais rapporter plus qu'un boulot, chaleur comptée |
| **P4** | ajout | Les nids-de-poule qui mordent | 2 | les nids sont déjà dessinés ; ⚠️ le trafic ne doit pas perdre ses virages |
| **P4** | ajout | Le derby de démolition à la foire | 3 | une conduite neuve (des chars qui en visent d'autres) |
| **P4** | ajout | Les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto | 3 | quatre intérieurs ; ⚠️ la ville promet déjà ces enseignes — le plus proche d'un mensonge du lot |
| **P4** | ajout | Le pont de glace | 3 | la neige de M12 ; ⚠️ l'eau est une couche que beaucoup de juges tiennent |
| **P4** | ajout | La motoneige | 2 | gagne à suivre **le pont de glace** ; un sprite de plus |
| **P4** | ajout | Le centre d'achat hanté | 2 | la voix existe déjà (« annonceur centre d'achat 2 », libre) ; une audition de Martin |
| **P4** | ajout | Le temps des Fêtes | 2 | la neige de M12 ; la musique de Noël est une dépense à trancher |
| **P4** | ajout | Le camion de crème glacée | 2 | les enfants à vélo existent ; une sorte de boulot de plus |
| **P4** | ajout | L'orignal de La Pointe | 1 | les bêtes existent ; ⚠️ une règle d'horaire, jamais `B.rng()` |
| **P4** | ajout | Le ciné-parc | 3 | un grand terrain en bord de ville : poser en dernier, sans dé |
| **P4** | ajout | Une amélioration générale des toits | 3 | rien ne l'attend ; la moitié de l'écran, c'est des toits ; ⚠️ le cache des morceaux et le rythme sur le téléphone, et rien au dé (l'empreinte du bâtiment) ; le chalet du rang comme banc d'essai |

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
| Les **districts chargés autour du joueur** (⚠️ `/api/carte` et son ETag sont **livrés** le 16 sept. 2026 : la carte voyage à part, mais entière) | 43 Ko gzip aujourd'hui (370 Ko bruts ; plafond brut relevé à 600 le 13 sept. 2026, parce qu'il n'est qu'un indicateur : le fil et `JSON.parse` sont les vraies bornes) : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin |

⚠️ Et une **fausse** dette, pour qu'on arrête de la reprendre : `tests/test_navigateur.py` est
exclu de la commande de tous les jours ci-dessous parce qu'il monte un Chromium et prend des
minutes — mais il fait partie de **la suite de livraison** (la deuxième commande), qu'on fait
tourner en local avant chaque mise en ligne. Il n'est pas oublié, il est ailleurs.
