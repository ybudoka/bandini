# Une partie rechargée ne réapparaît plus dans un bâtiment

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (21 sept. 2026, capture : le cousin debout sur le toit du garage Bandini, Marco
qui hèle devant la porte) : « l'apparition n'est pas correcte, j'ai apparu dans le bâtiment ».
Sa partie (emplacement 1, jour 277) est sauvegardée à 2549, 763 : la tuile 159, 47, deux rangées
de toit au-dessus de la porte du garage (159, 49), sur la carte d'aujourd'hui (même empreinte).
`commencer` pose le joueur à `p.x`, `p.y` sans regarder ce qu'il y a dessous, et rien ne le sort
d'un mur ensuite : il y reste pris.

La position sauvegardée est celle du joueur à la dernière sauvegarde (toutes les dix secondes), et
au volant c'est celle du char. Un char sous le toit d'un garage (la baie du rideau, livrée ce
matin), un bateau sur l'eau, un corps passé dans une façade : tout ça s'écrit tel quel, et la
partie se rouvre dedans.

- ⚠️ Le correctif est au CHARGEMENT, pas à la sauvegarde : c'est lui qui répare les parties déjà
  écrites, celle de Martin comprise. Une position où un piéton ne tient pas (mur, eau, grillage,
  barbelé) glisse sur la tuile à pied la plus proche, hors chaussée et hors meuble, au pixel près ;
  une position où l'on tient ne bouge pas d'un pixel.
- ⚠️ Un juge : la position de Martin, rechargée, réapparaît sur le trottoir devant le garage — rouge
  avant (le joueur reste sur le toit) ; et une position libre revient exactement où elle était.
