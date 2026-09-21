# On fait un tour dans le petit train, la montagne russe et la grande roue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux aussi que le petit train soit dans le même style que les
véhicules et qu'on puisse y faire un tour. pareil pour la montagne russe et la grande roue
». Les wagons et les chariots étaient des grilles plates de 11 à 15 px tournées par
seizièmes de tour (`foire.js`), les nacelles des rectangles peints dans le décor de la roue,
et la 4e vague de la foire avait tranché « on n'y monte pas ». **Les trois sont maintenant
des machines comme les chars** (`FOIRE_EN_VOLUME`, `sprites.js`) — mêmes pièces, même biais
du sol, contour et arrondi — cuites au cap par `Atlas.cuireCap`, et **on fait un tour dans
chacun** : ACTION à côté d'un siège, un tour complet, on descend là où l'on est monté.
Gratuit une fois dans l'enceinte : le billet du jour paie la foire.

- ⚠️ **Pas dans `SPRITES`** : ce ne sont pas des chars du catalogue, et les juges du parc
  (`test_poses_vehicules.py` : phare et feu à 24 caps sur 32, deux roues au sol) les
  prendraient pour des autos ratées. `Foire` est le seul à les lire.
- **Le petit train** : une locomotive de 20 px (chaudière, cheminée, cabine ouverte et son
  machiniste) et quatre wagons de 16 px où les voyageurs s'assoient comme le barreur de la
  chaloupe (`Vehicules.imageDuCavalier`, posture `volant`). **Sa gare** (`carte.py`) : la
  locomotive s'arrête six secondes à 9 tuiles à l'ouest de l'arche, le dernier wagon hors de
  l'allée d'entrée ; le **quai** est une allée de pierre le long de la voie, raccordée à
  l'allée d'entrée, sous une pancarte PETIT TRAIN. `ecart_px` 15 → 20 (les wagons se
  chevauchaient), `regard_px` 26 → 34.
- **La montagne russe** : des chariots de 14 px et leurs deux passagers DANS la machine. ⚠️
  Un chariot PENCHE : `Atlas.projeter` apprend le **tangage** (un cran sur 32, comme le cap)
  — il grimpe la chaîne le nez en l'air, plonge, et passe le looping **la tête en bas**,
  passagers compris ; dans le looping il garde le cap de l'entrée, puisque celui de la voie
  au sol retourne au sommet. `ecart_px` 13 → 16. On monte depuis les planches de la gare, et
  la caméra suit le chariot en hauteur, pas le sol sous lui (`Monde.majCamera`).
- **La grande roue** : ses nacelles sortent du décor — des baquets pendus à leur attache,
  peints par `Foire` au cran même des rayons (`moyeu`, `rayon`, `nacelles` sur la fiche du
  décor). Une roue ne s'arrête pas : on s'assoit dans la nacelle du bas, un tour dure
  `nacelles × variantes` crans (26 s), et on descend devant le portique.
- ⚠️ **Assis, on est À PIED ET PORTÉ** (`j.manege`), comme à bord du traversier : ni dans un
  véhicule (rien à conduire, la police ne sort personne), ni libre — pas de marche, de coup,
  de roue d'armes ni de portière, et pas d'invite. **On ne monte pas recherché** : un manège
  où la police ne suit pas serait la meilleure cachette du jeu.
- Juges neufs (`test_foire.py`), chacun vu rouge sans sa règle (douze mutations) : la gare
  et son quai, l'arrêt à chaque tour, un tour de petit train, rien d'autre à faire assis ni
  recherché, le train en volume, la descente sur un sol libre, un tour de montagne russe, le
  chariot la tête en bas au looping, un tour de grande roue, les nacelles au bout de leurs
  rayons.
