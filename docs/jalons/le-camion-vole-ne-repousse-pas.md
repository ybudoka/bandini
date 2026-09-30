# Le camion volé ne repousse pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (30 sept. 2026, capture du 1er juillet) : « quand on vole un camion de
déménagement, un autre apparaît ». `Demenagement.maj` oublie l'étiquette `demenageur` du
camion qu'on prend (il est à nous, il survit au lendemain) ; mais c'est la même étiquette
qui disait « cette place a son camion » : à la vérification suivante, la place paraît vide
et un camion neuf y naît, par-dessus celui qu'on vient de voler. On descend, on remonte,
on repart : un camion de plus à chaque fois.

- ⚠️ Une place dont on a pris le camion reste vide jusqu'au lendemain : le jeu se souvient
  des places prises, pour le jour qu'on les a prises.

## Notes

✅ Livré le 30 sept. 2026. `Demenagement.maj` retient les places dont on a pris le camion
(`prises`, clé partie + jour) : l'étiquette `demenageur` s'oublie toujours sur le camion volé
(il est à nous, il survit au lendemain), mais sa place ne fait plus naître de camion neuf
avant le lendemain, ni en montant, ni en descendant, ni en remontant. Une partie neuve
repart à zéro.

Juge : `test_le_camion_vole_ne_repousse_pas_a_sa_place` (tests/test_demenagement_js.py) —
rouge avant le correctif (deux camions blancs à la place prise dès qu'on monte).
