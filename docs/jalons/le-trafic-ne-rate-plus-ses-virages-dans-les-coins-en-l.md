# Le trafic ne rate plus ses virages dans les coins en L

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (capture du coin en L des Quais, 149,189 : la route à quatre voies du nord
tourne vers une route à deux voies, l'eau à une tuile) : « améliore les virages pour les
situations complexes comme ça » — c'est le trafic. Mesuré au banc : sur 2 238 entrées de
boîte, 24 font TROIS virages, toutes dans les onze coins en L de la ville. `prochaineCible`
tire sa sortie (tout droit, à droite, à gauche) sans savoir si la boîte l'a : un char qui
descend du nord et voulait « tout droit » traverse la boîte jusqu'à la rangée du bord de
l'eau, n'y trouve rien, puis zigzague (ouest, nord, ouest) :
`149,188v 149,189v 149,190v 148,190< 148,189^ 147,189<`.

- ⚠️ Le correctif : la sortie voulue est la première de la liste qui PART DE LA BOÎTE, tout
  droit devant — sinon la suivante ; et une fois tourné, on ne change plus d'avis. Le tirage
  « tout droit » devient « tout droit, sinon à gauche » pour que les T gardent le partage
  qu'ils avaient (77 % à gauche depuis le pied du T).
- ⚠️ Un juge : de chaque entrée de chaque boîte, avec les trois préférences et en poursuite,
  UN virage au plus, pris à la première tuile d'où il mène — rouge avant (24 zigzags).
