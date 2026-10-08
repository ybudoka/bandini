# L'arroseuse qui tourne à 180°

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (8 oct. 2026) : « il y a des bugs aussi pour le camion qui lave les rues quand il
tourne à 180 ». L'arroseuse roule sur la boucle de la charrue avec le code des autobus
(`Autobus.conduire`), qui pivote au centre de la tuile ; la boucle n'a aucun demi-tour écrit
(vérifié sur la ville du 8 oct.) : le demi-tour vient donc de la conduite (un camion poussé
au-delà de sa tuile se retourne pour y revenir ?). Sans doute la même racine que l'autobus
accroché au carrefour des Quais. À faire : le reproduire au banc, le juger, le fermer.

## Notes

✅ **Livré** (8 oct. 2026), avec [l'autobus accroché au carrefour des Quais](l-autobus-accroche-au-carrefour-des-quais.md#notes) :
la même racine. La boucle de la charrue n'a aucun demi-tour ; c'est `Autobus.conduire` qui en faisait un, quand un
choc poussait le camion au-delà de la tuile qu'il visait : il ne passait à la suivante que posé pile sur son centre,
et se retournait pour y revenir. Une tuile dépassée compte maintenant pour atteinte (`Autobus.tuileAtteinte`). Le juge
`test_pousse_au_dela_de_sa_tuile_il_ne_fait_pas_demi_tour[arroseuse]` la pousse six pixels au-delà et cinq de côté,
un soir d'été à 2 h (elle ne sort qu'entre 1 h et 5 h) : sans la correction, elle se retourne (cos −0,76).
