# M1 : le char dort dans la ruelle avant qu'on l'y montre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « pour la mission du véhicule à apporter au garage, il
faut voir l'auto en place durant l'animation ».

**Livré, et généralisé (18 sept. 2026).** La règle vaut pour toutes les scènes : **une coupe
montre ce qu'elle nomme.** Un plan qui fait VOIR un élément de la mission — le char d'un
`monter`, les Cravates d'un `tuer` — doit le trouver posé à l'écran, même quand la mission
commence DANS une pièce. C'est `Histoire.poser` qui pose dans la VILLE quoi qu'il arrive, via
`dansLaVille` : quand on est dedans (`Monde.carte` = la pièce, `B.entites` = ses gens), on
remet le temps du placement la carte et la liste de la ville, on naît au bon monde, puis on
reprend les deux. m4 (Bouchard au casse-croûte) et m5 (Josée au bar) posaient leurs éléments
seulement à la sortie : leur intro coupait vers la rue et filmait le poste ou le coin des
Cravates vide.
