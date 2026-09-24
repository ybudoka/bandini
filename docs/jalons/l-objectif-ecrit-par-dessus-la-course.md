# L'objectif écrit par-dessus la course

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

bug de Martin, capture à l'appui (« bug de hoverlap en haut ») : en taxi, « COURSE : POSTE
DE POLICE 51M » et « FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT 0/3 » étaient écrits l'un
**dans** l'autre, tous les deux dorés, à un pixel de hauteur près.

- ⚠️ Rien n'était cassé : chaque ligne était à sa place. La ligne de boulot est collée sous
  le compteur (x 70, y 16) et la ligne d'objectif tombait sous les étoiles (4 + 11 + 2 = y 17)
  — mais elle est **centrée**, et une phrase de soixante-dix caractères centrée commence
  bien avant le milieu de l'écran (x 144 pour la course de Marco, en plein dans une ligne de
  boulot qui court de 70 à 181). Deux mises en page qui ne se connaissaient pas. La ligne de
  boulot, l'argent et l'heure **rendent leur boîte** au lieu de s'écrire et de s'oublier (et
  le boulot devient une ancre, donc le juge tactile de `test_navigateur.py` le voit aussi) ;
  à la place d'un `y` fixe, **une seule règle** : toute boîte du bandeau du haut que la
  ligne d'objectif chevauche **en largeur** la pousse d'une rangée vers le bas. C'est
  toujours elle qui cède, comme elle cédait déjà aux étoiles. 1 juge — la règle entière, pas
  le seul cas de la capture : la ligne d'objectif ne chevauche **aucune** autre ancre du HUD
