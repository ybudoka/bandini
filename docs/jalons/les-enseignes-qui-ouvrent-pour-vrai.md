# Les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ quatre façades que la ville affiche déjà deviennent des endroits où l'on entre.

**Aujourd'hui** `app/devantures.py` peint `BINGO`, `SALLE DE QUILLES`, `LAVE-AUTO` et `CINÉMA RIALTO` sur des
façades — des enseignes sans pièce derrière. La ville promet, et on ne peut pas entrer : c'est presque un
mensonge (P4 tant qu'aucune porte ne l'invite).

- **Le bingo** : une pièce du sous-sol, une carte de bingo à l'écran, le narrateur qui crie les boules
  (« B-7! ») ; les madames te regardent de travers si tu gagnes. Tirage calculé, jamais `B.rng()`.
- **La salle de quilles** : un jeu d'adresse (viser, la force, l'effet), dix carreaux, un défi du rail.
- **Le lave-auto** : on y entre en char ; un char lavé est **moins reconnaissable** — la chaleur baisse d'un
  cran (moins fort que repeindre au garage, et moins cher).
- **Le Rialto** : un film le soir (un écran qui scintille, une salle sombre) ; une mission de filature dans la
  salle (`suivre` existe).

⚠️ **Ce qui guette** : quatre pièces de plus — des intérieurs (`carte.py`, `_piece`), posés sans déplacer
la ville ; chaque intérieur doit « donner quelque chose à faire » (le juge `test_une_piece_donne…`).

**Juges** : chacune des quatre a une porte et un point qui sert ; le bingo et les quilles ne tirent aucun
`B.rng()` ; un char lavé perd un cran de chaleur, une fois par passage.

## Notes

_Rien de livré._
