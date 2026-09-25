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

_Rien de livré._
