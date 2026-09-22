# Un petit icône pour le moment de la journée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « ajoute un petit icône pour indiquer quel moment de la journée on
est ». Une icône de 7 pixels devant « JOUR N HH:MM », en haut à droite du HUD : un soleil le
jour, une lune la nuit, un soleil à moitié couché à l'aube et au crépuscule. Les quatre
périodes suivent les teintes de `Monde.ambiance` (la même horloge que le ciel), mais se
lisent à l'heure DEHORS : dans une pièce, l'icône dit encore la nuit qu'il fait. Cuite une
fois par période (`Atlas.cuirePeintre`), comme l'étoile.
