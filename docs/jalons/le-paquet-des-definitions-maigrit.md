# Le paquet des définitions maigrit

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé le 29 sept. 2026 : le plafond de `test_le_paquet_reste_leger` a été relevé presque chaque jour
(60 → 62 → 64 → 67 Ko gzip, 270 → 300 Ko bruts), et chaque relève écrivait « le remède reste celui d'en
haut »._ Mesure du jour : 296 109 octets bruts, 66 090 gzip.

_Ce que ça donne :_ le paquet que le téléphone télécharge au démarrage (`/api/definitions`) perd ce qu'il
n'a pas besoin de lire pour ouvrir le menu, et ses plafonds **redescendent**.

**Première cure : les notes de la musique** (`audio.musiques`, les partitions de secours de `musique.py`,
≈ 45 Ko bruts / 8,7 Ko gzip). Elles sont le FILET : un mp3 absent ou un réseau coupé fait jouer le
séquenceur. ⚠️ Un filet qui dépendrait du réseau n'en serait plus un :

- ce qui joue avant tout réseau (le thème du menu, `titre`) garde ses notes dans le paquet ;
- le reste voyage sur `/api/musiques` (ETag, `?e=` comme la carte), demandé **tout de suite après** les
  définitions, en arrière-plan — jamais au moment où un mp3 rate (c'est souvent que le réseau vient de
  tomber) ;
- l'adresse est dans la **coquille** du travailleur : hors ligne, les notes sont déjà gardées ;
- les métadonnées (slug, nom, fichier, tempo) restent au paquet : `Mus.def`, le jukebox, la radio et les
  musiciens de rue les lisent sans attendre.

**Ensuite** : mesurer le paquet clé par clé et sortir, si c'est aussi sûr, ce que le navigateur ne lit
jamais ou ce qui ne sert qu'à un endroit.

**Juges** : le paquet ne porte plus les notes (sauf le menu) ; `/api/musiques` se revalide et se demande
par son empreinte ; au banc, un morceau sans mp3 dont les notes arrivent après le démarrage joue quand
même ; un réseau qui tombe une fois ne tue pas le filet ; les plafonds baissés à la nouvelle mesure.

## Fiche de la deuxième cure

_Demandé le 30 sept. 2026 (Martin : « Cure 2 maintenant »)._ En un jour, d'autres ajouts ont remangé la marge
rendue par la première cure : **7 octets** sous le plafond de 59 000 gzip.

- **Mesurer le paquet clé par clé** (brut et gzip), et comparer à la mesure de la première cure : ce qui a
  grossi, et qui.
- **Sortir le journal du matin** (`journal*`, ≈ 4,4 Ko gzip). ⚠️ Un texte n'a pas de repli : il se demande au
  démarrage, en arrière-plan, et la coquille du travailleur le garde hors ligne, comme `/api/musiques`.
- **`types_plans` / `types_objectifs`** sortent si aucun script ne les lit ; les deux juges qui en font un
  contrat jugent la même chose ailleurs (côté Python).
- **D'autres sorties sûres** : ce que le navigateur ne lit jamais, ou ce qui ne sert qu'à un endroit ou à un
  moment — chacune prouvée (pas lue au démarrage, ou arrivée avant qu'on en ait besoin).
- **Une garde** qui rend visible QUI fait grossir le paquet : la prochaine session qui déborde sait où
  couper, au lieu de relever le plafond.
- **Les plafonds redescendent** à la nouvelle mesure, avec au moins 4 Ko gzip de marge.

## Notes

**Livré le 29 sept. 2026.** Mesure : **296 109 octets bruts / 66 090 gzip** sur `dev`, **246 381 / 56 345**
après deux sorties. Les plafonds de `test_le_paquet_reste_leger` **descendent** : 300 000 → **256 000** bruts,
67 000 → **59 000** gzip ; les notes ont le leur (50 000 / 10 000 pour 43 775 / 8 382).

- **Les notes de la musique** (−43 504 bruts / −8 783 gzip) : `definitions.sortir_les_notes` retire les
  `voix` de chaque morceau, sauf celles du thème du menu (`musique.NOTES_DANS_LE_PAQUET`) ; elles voyagent
  sur `/api/musiques` (ETag, `?e=`, `musiques_empreinte` dans les définitions). Le navigateur les demande
  juste après les définitions, pendant que la ville se bâtit (`Son.Notes.charger`), et les remet à leur
  morceau. Un morceau qui doit jouer en notes avant leur arrivée se tait, comme pendant le téléchargement
  d'un mp3 ; si la demande a raté, il la refait une fois toutes les dix secondes. La coquille du travailleur
  les garde : le filet tient hors ligne (juge dans Chromium, réseau coupé). `Radio.estProcedurale` ne lit
  plus « le morceau porte ses notes » (la station du camion aurait été prise pour un mp3 de radio).
- **Les bruitages** (−6 224 bruts / −961 gzip) : le nom, la catégorie et `boucle`, qu'aucun script ne lit.
  ⚠️ Et une réparation : la cure du 28 sept. avait emporté `duree_s`, que `Son.SFX.telephone()` lit — l'appel
  parlait 0,37 s après le premier coup d'une sonnerie de deux secondes. Elle revient pour la seule sonnerie
  (`audio.DUREES_LUES`).
- ⚠️ **Ce que ça n'achète pas** : au premier chargement, presque autant d'octets arrivent, en une requête de
  plus, après les définitions au lieu de dedans. Ce que ça achète : un `JSON.parse` plus petit avant le
  menu, des notes qui revalident en 304 quand un catalogue change, et dix Ko gzip de marge rendus au paquet.

**Les prochaines sorties possibles** (mesurées le 29 sept., pas faites ce jour-là — le journal et
`types_*` sont sortis avec la deuxième cure, plus bas) :

- `journal`, `journal_speciales`, `journal_lecons`, `journal_matins` (≈ 4,4 Ko gzip) : ils ne servent qu'au
  journal du matin (sa manchette et sa voix). ⚠️ Un texte n'a pas de repli : il faudrait les demander au démarrage comme les notes
  (et les garder dans la coquille), pas au lever du jour.
- `types_plans` et `types_objectifs` (≈ 750 bruts) : aucun script ne les lit, mais deux juges en font un
  contrat (`test_le_paquet_porte_les_scenes`, `test_le_paquet_contient_tout`) — à trancher.
- `defis` (4 Ko gzip), `personnages` et `visages` (4,8 Ko), `garderobe` (3,4 Ko) : lus au démarrage ou
  à chaque image ; ils ne sortiraient qu'avec la dette des districts chargés autour du joueur.

**Deuxième cure, livrée le 30 sept. 2026.** Mesure sur `dev` : **255 021 octets bruts / 58 992 gzip** — sept
octets sous le plafond, un jour après la première. **Qui avait remangé la marge** (mesuré commit par commit
depuis `a185aaed`, +8 640 bruts / +2 644 gzip) : les quatre saisons **+1 275 gzip** (l'Halloween +570 avec sa
clé neuve, les vagues 4a/4b/4c +541, le son des saisons +148), les photos du Clairon **+697** (clé neuve),
Le Boss **+542** (une manchette, des personnages, la dernière nuit), le reste en miettes. Après :
**233 247 / 53 017** (−21 774 / −5 975). Les plafonds de `test_le_paquet_reste_leger` descendent :
256 000 → **240 000** bruts, 59 000 → **57 500** gzip (**4 483 octets de marge**).

- **La suite du paquet** (`/api/suite`, `definitions.DANS_LA_SUITE`, `static/js/suite.js`) : le Clairon
  (`journal*` et `photos`) et la hantise des Galeries (`galeries`) — −4 444 gzip. Ce que le navigateur ne lit
  jamais avant d'avoir quitté l'écran titre, demandé juste après les définitions en arrière-plan, gardé dans
  la coquille du travailleur (le juge Chromium, réseau coupé, le voit arriver), et remis dans `B.defs` sous
  les mêmes clés (`Suite.poser`) : aucun lecteur ne sait d'où il vient. ⚠️ **Un texte n'a pas de repli** :
  un jour qui se lève avant la suite ne perd pas sa une — le Clairon l'ATTEND (`Suite.quand`, dans
  `Missions.nouveauJour`), puis s'affiche et se dit ; si un autre matin s'est levé entre-temps, seule la une
  du dernier paraît. Ce qui lit une de ces clés se tait sans elle (le déclic de la photo, Louise, les Galeries
  la nuit, le bulletin de la radio) — jamais une exception dans `maj()`. Une demande ratée se refait une fois
  par dix secondes. La suite a son plafond (10 562 bruts / 4 884 gzip ; 13 000 / 6 000).
- **Ce qu'aucun script ne lisait** — −971 gzip : `types_plans` et `types_objectifs` (leurs deux juges jugent
  ailleurs ce qu'ils tenaient : l'ouverture ne joue que des plans que `scenes.js` connaît, clés comprises ;
  chaque objectif de chaque `/api/mission/<slug>` est d'un type de `TYPES_OBJECTIFS`), et la voix ElevenLabs
  de chaque personnage (`CHAMPS_HORS_DU_PAQUET` : elle ne sert qu'à générer ses mp3, en Python).
- **Les voix du journal et des repos en séries** (`audio.series_des_repos`, comme le 6/49) — −542 gzip :
  `histoire` ne garde que l'ouverture ; `audio.deplier_les_series` est le jumeau Python de `Son.Voix.histoire`
  pour les juges.
- ⚠️ **La garde** (`MESURE_DU_PAQUET`, `tests/test_definitions.py`) : chaque clé des définitions, son poids
  gzip seul à la mesure du 30 sept., et son **budget** (mesure + 10 % + 100). Une clé qui dépasse le sien
  rougit **en se nommant** (`test_chaque_cle_du_paquet_tient_son_budget`) ; une **clé neuve** doit s'y écrire
  avec son poids (hier, `photos` et `halloween` sont arrivées sans un mot) ; et le plafond global, s'il cède,
  **nomme les trois clés qui ont le plus grossi** depuis la mesure. Le prochain qui déborde sait où couper
  avant de relever quoi que ce soit.

**Les prochaines sorties possibles** (mesurées le 30 sept., gain dans le paquet, pas faites) :

- les **textes des défis** (`texte`, `regles`, `consigne` : ≈ 2,5 Ko gzip) : lus quand on en prend un ou
  qu'on ouvre le carnet — la carte et les panneaux ne lisent que le titre et le lieu ;
- les **comptoirs** (≈ 1,4 Ko) : leurs menus ne s'ouvrent qu'à un comptoir ; `menuComptoir` rend `null`
  sans eux (ACTION ne ferait rien, sans un mot) — il lui faudrait un message ou `Suite.quand` ;
- les **jeux du casino** (`tables_de_jeu`, `machine_a_sous`, `videopoker` : ≈ 1,2 Ko) : ⚠️ `Casino.maj` →
  `majSecurite` → `dossier()` lit `tables_de_jeu.surveillance` sans garde, dans la boucle d'images ;
- `economie.paliers` (≈ 880) et le **repos** des personnages (≈ 690) : à regarder, lecteur par lecteur.

