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

### Vague 2 — les missions (28 sept. 2026, en cours)

Martin : « fais des missions d'infiltration ». Trois, jouables de bout en bout, sur un seul bâtiment
grand et labyrinthique : **la villa du maire Tanguay**, que le plan de M16 attendait comme lieu spécial.

- ⚠️ **Un BLOC, pas un lieu de la ville** (`app/blocs/villa.py`) : une pièce de la taille voulue en
  ville la ferait glisser, et une PIÈCE arrête tout — `Histoire.majObjectif` et `Police.maj` ne
  tournent pas dedans. Dans un bloc (`B.interieur` nul), les objectifs, les gardes et les étoiles
  tournent. Le passage : au bout de la rue est-ouest du bord ouest des Érables. Le terrain, la
  villa à pièces, un étage et un sous-sol reliés par des escaliers (un fondu, dans le même bloc).
- **Des lieux de bloc** : un bloc déclare ses `lieux` (ses `points_interet`) ; une mission peut les
  nommer ; en ville le GPS vise le passage, dans le bloc il vise le lieu.
- **Les gardes du domaine** : le bloc déclare leurs rondes ; ils naissent quand on y entre
  (`Police.creerAgent(…, 'garde')`), marchent leur ronde, et un garde qui te voit sur le terrain
  privé donne l'alerte (une étoile, il te court après) — `sans_etoile` fait le reste.
- **La serrure** : la porte de service est une barrière `objet` du bloc (`cle_villa`) ; la clé se
  vole dans la poche d'un garde (un objectif `obtenir`, qui met un objet dans le sac).
- **Les missions** : Josée (la clé de la porte de service), le sergent Bouchard (son dossier, dans le
  bureau d'en haut), Sven (la chambre forte du sous-sol, au piratage). Chacune a son juge de banc qui
  la JOUE au bouton.
