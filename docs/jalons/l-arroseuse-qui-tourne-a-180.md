# L'arroseuse qui tourne à 180°

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (8 oct. 2026) : « il y a des bugs aussi pour le camion qui lave les rues quand il
tourne à 180 ». L'arroseuse roule sur la boucle de la charrue avec le code des autobus
(`Autobus.conduire`), qui pivote au centre de la tuile ; la boucle n'a aucun demi-tour écrit
(vérifié sur la ville du 8 oct.) : le demi-tour vient donc de la conduite (un camion poussé
au-delà de sa tuile se retourne pour y revenir ?). Sans doute la même racine que l'autobus
accroché au carrefour des Quais. À faire : le reproduire au banc, le juger, le fermer.
