# Infiltration : portes verrouillées et gardes privés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin veut des missions d'infiltration dans des bâtiments grands et labyrinthiques : ne pas
être vu, déverrouiller des portes, trouver des clés. Le moteur a déjà presque tout — les
cônes de vision et les paliers d'alerte (`app/recherche.py`, `static/js/police.js`), les
intérieurs à étages (`app/ile.py`, `app/aeroport.py`), les objectifs `sans_etoile` et
`suivre` (`static/js/histoire.js`), et le mini-jeu de piratage (m53). Il manque deux briques
réutilisables, avant d'écrire une vraie mission dessus : ⚠️ une VRAIE serrure —
`carte.BARRIERES` (« une porte, une condition, un prix ») sait déjà fermer un lieu tant
qu'une mission n'est pas faite ou tant qu'on n'a pas payé ; elle apprend une troisième
condition, `objet`, fermée tant que `partie.objets[slug]` n'est pas possédé — la clé qu'on
trouve ou qu'on vole devient une vraie clé.

- ⚠️ Un genre `garde` (vigile privé) — `recherche.VISION` lui donne son propre cône, et
  `police.js` généralise ses deux appels à `voit(..., 'policier', ...)` (dans `gere()` et
  `signalerCrime()`) en `a.genreVision`, avec `'policier'` en défaut, pour que N'IMPORTE
  QUEL genre déclaré compte, pas seulement la police ; un archétype `garde` dans
  `app/pietons.py` (même moule que `policier` : `frequence: 0`, ne naît jamais au hasard) et
  `Police.creerAgent(x, y, etat, genre)` sait désormais fabriquer l'un ou l'autre. Se faire
  voir par un garde compte exactement comme se faire voir par un policier — patrouille,
  poursuite, arrestation : c'est le même moteur, un cône et une palette différents. La
  mission elle-même (le bâtiment, ses pièces, où poser le garde et la clé) reste à écrire
  par-dessus ces deux briques.
