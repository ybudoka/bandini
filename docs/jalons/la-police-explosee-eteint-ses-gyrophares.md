# La police explosée éteint ses gyrophares

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin : « un véhicule de police qui explose ne doit plus avoir de gyrophares en fonction ».
Mesuré : `exploser` laisse `v.sirene` allumée, et `swapsDuMoment` (qui fait battre la rampe)
ne regarde pas l'état d'épave — la carcasse calcinée clignote rouge et bleu (le SON de la
sirène, lui, saute déjà les épaves). Et même éteints, les boîtiers `a`/`b` gardent leur
rouge et leur bleu sur un char tout charbon. Correctif : une épave ne fait pas battre sa
rampe (explosée, pliée ou coulée), la sirène s'éteint à l'explosion, les boîtiers calcinés
comme le reste ; juge au banc.
