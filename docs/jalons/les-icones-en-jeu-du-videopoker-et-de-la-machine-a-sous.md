# Les icônes en jeu du vidéopoker et de la machine à sous

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (28 sept.), après [les
bornes](les-icones-du-videopoker-et-de-la-machine-a-sous.md#notes) : « améliore les icônes
en jeu aussi ». Dans l'écran de jeu, les sept symboles des rouleaux (`casino.js`, `DESSINS`,
5 × 5 d'une seule couleur) deviennent de vraies petites images en couleurs, ombrées, qu'on
reconnaît sans lire la table des gains ; les cartes du vidéopoker (`missions.js`,
`ENSEIGNES`, `dessinerVideopoker`) gagnent des enseignes plus fines, le petit rappel au coin
sous le rang, et un dos de carte dessiné. Rien ne bouge aux règles ni au hasard.

## Notes

✅ Livré le 28 sept. 2026. Du dessin seulement : ni règle, ni dé, ni table des gains ne bougent.

- **Les rouleaux** (`casino.js`) : `DESSINS` passe de sept grilles 5 × 5 d'une couleur à des
  grilles 12 × 12 (la barre 13) avec leur palette — couleur, ombre en bas à droite, reflet en
  haut à gauche —, peintes à ×4 par `peindreSymbole`. Avant, la cerise se lisait comme une
  arche, le dragon comme un X vert. Le rouleau s'assombrit en haut et en bas (un cylindre), une
  flèche rouge de chaque côté marque la ligne payante, et pendant qu'il tourne les symboles
  **glissent** dans la fenêtre (deux à la fois, sous un `clip`) au lieu de se remplacer d'un
  coup — même vitesse qu'avant, et toujours compté en images dessinées.
- **Les cartes** (`missions.js`) : `ENSEIGNES` en 7 × 7 (le pique avait l'air d'un pion, le
  trèfle d'une croix, le carreau d'un plus), la grande au milieu à ×3 et un **rappel** à ×1
  sous le rang, les coins arrondis d'un pixel, l'ombre du carton. Le dos devient un liseré
  blanc et un rouge à losanges.
- ⚠️ Premier jet du pique en `.#.#.#.` au pied : une tête de mort à l'écran. Le pied en
  `##.#.##` fait les deux lobes. Regardé dans Chromium, le menu ouvert : aucun juge ne voit un
  dessin.

