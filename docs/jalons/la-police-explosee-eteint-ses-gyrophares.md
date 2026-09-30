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

## Notes

Livré le 30 sept. 2026. Dans `Vehicules.exploser`, la sirène s'éteint et les lettres de la
rampe (`a`, `b`) passent au charbon avec le reste de la caisse ; dans `swapsDuMoment`, une
épave rend ses couleurs telles quelles, sans battement — ce qui couvre aussi le char plié ou
coulé, et la remorqueuse. La boucle de `maj` qui remet `v.sirene` pendant une chasse ne
touche pas les épaves (elle les saute avant), donc la sirène éteinte le reste.

Juge : `test_une_police_explosee_n_a_plus_de_gyrophares` (`tests/test_poses_vehicules.py`) —
une auto-patrouille en pleine chasse (trois étoiles) et une ambulance en course sautent ; la
rampe battait avant, elle est éteinte et calcinée après. Rouge avant le correctif (sirène
restée allumée), et rouge si l'on retire `a`/`b` du charbon.
