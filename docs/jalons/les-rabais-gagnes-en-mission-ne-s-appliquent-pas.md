# Les rabais gagnés en mission ne s'appliquent pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Trouvé le 25 sept. 2026, en préparant `q01` (Lulu promet un rabais à la cantine)._

_Ce que ça donne :_ ce qu'une mission promet en rabais se paie vraiment moins cher au comptoir.

⚠️ **Le jeu ment.** Trois missions affichent un rabais à leur récompense, et `Histoire.recompenser`
l'inscrit bien dans la partie (`partie.rabais`) — mais **un seul comptoir le lit** : le kiosque de
m2 (`Missions.rabais('kiosque')`). Les trois autres ne changent aucun prix :

- **f02** (Gus) : « GUS TE FAIT CONFIANCE, UN PEU » — `rabais.armurerie` 0,85, jamais lu par
  `menuArmurerie` ;
- **f03** (Rosa) : « BOUTIQUE ROSA, MOINS CHER POUR TOI » — `rabais.vetements` 0,75, jamais lu
  par `menuVetements` ;
- **s01** (Gilles) : « LE RACHAT AU LOT, MOINS CHER » — `rabais.fourriere` 0,80, jamais lu par
  `prixRachat`.

Le remède : **un facteur par pièce**, lu partout où un prix se calcule — armes et munitions chez
Gus, tenues chez Rosa, rachat au lot, et les comptoirs de bouffe (la cantine de `q01`). Et un juge qui
refuse une clé de `donne.rabais` que le jeu ne lit nulle part : c'est ce qui manquait pour que ça ne
se reproduise pas.

⚠️ **La fourrière garde sa règle** : racheter coûte plus cher que revendre (0,40 × 0,80 = 0,32 du
prix neuf, contre 0,25 à la revente) — à vérifier aussi avec l'avantage de palier du boulot.

## Notes

_Livré le 25 sept. 2026._

- **Un facteur par clé, lu partout où un prix se calcule** (`Missions.rabais(cle)`,
  `auRabais(prix, cle)`) : les armes **et les munitions** chez Gus (`armurerie`), les tenues chez
  Rosa (`vetements`), le rachat au lot (`fourriere`), le comptoir du casse-croûte et de la cantine
  (la clé est le slug de la pièce), et tout comptoir ordinaire (`menuComptoir` : bouchées, armes,
  tenues). Le kiosque garde le sien.
- ⚠️ **Le palier « rabais » a une clé, et elle était ignorée.** Le café du chauffeur de taxi (et
  celui du terminus) : `-25 % AUX KIOSQUES`, `cle: "kiosque"`. `avantage('rabais')` les confondait
  toutes : brancher `rabais()` chez Gus tel quel lui aurait donné le café du chauffeur.
  `rabaisDePalier(cle)` ne prend que les paliers de SA clé.
- **Le juge part du catalogue** (`tests/test_rabais_js.py`) : chaque clé de `donne.rabais` doit
  avoir un comptoir où on la voit (`OBSERVER`), et le prix y baisse du bon facteur ; une mission
  qui promettrait un rabais que personne ne lit rougit sans qu'on l'inscrive. Puis : la caisse
  prend le prix affiché, réduit ; le palier du kiosque ne suit pas le joueur chez Gus. Mutations :
  l'ancien `missions.js` rougit deux juges, le palier sans sa clé rougit le troisième.
- ⚠️ **La règle de la fourrière** (racheter coûte plus que revendre) tient avec le rabais de
  Gilles (0,40 × 0,80 = 0,32 contre 0,25) — **mais pas au dernier palier du remorquage**, qui rend
  le rachat gratuit (`valeur: 0.0`) depuis bien avant ce correctif. Le juge de la règle ne regarde
  que le tarif de base. Ce n'est pas un mensonge (le palier le dit), c'est une machine à argent
  permise : à trancher par Martin si ça le dérange.
