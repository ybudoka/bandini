# Le crieur ne se plante plus devant une porte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (30 sept. 2026, capture du Garage Bandini) : « il y a encore des personnes
qui bloquent les portes et qui ne bougent pas ». Le crieur de journaux (`vitesse: 0`) naît
par `placeDeNaissance`, qui pose un passant sur le pas d'une porte une fois sur trois —
normal pour qui marche, il s'en va ; mais le crieur est figé et plante sa place là où il
naît : il tenait la tuile sous la porte du garage toute la matinée.

- ⚠️ Ce qui naît en cours de partie et tient un poste ne se pose jamais sur un devant de
  porte (`Monde.devantDUnePorte`) : on le glisse sur la tuile voisine la plus proche, sans
  dé, ou il ne naît pas.

## Notes

Livré le 30 sept. 2026.

- **La cause, lue dans la partie de Martin** (jour 580, 14 h 30, joueur à 2 534, 2 575) : la casquette
  rouge de la capture n'était pas un donneur — Marco, qui hèle « Hé! Viens ici! », se tient à droite du
  guichet, hors cadre. C'était le crieur, qui criait la manchette du matin (« LA VILLE OUVRE LES
  VOLETS ») sur la tuile (159, 160), pile sous la porte du garage.
- `Entites.horsDuDevant` : ce qui naît par `naitreLesSortes` et tient un poste (`vitesse: 0`) passe par
  lui. Sa place tirée, si elle est sur un devant, glisse à la tuile voisine la plus proche qui ne l'est
  pas (spirale, rayon 3), marchable, hors de la rue, hors de l'écran, libre — **sans aucun dé** : la
  place a déjà tiré les siens. À défaut, il ne naît pas cette fois-ci. Qui marche ne change pas.
- Juge `test_qui_tient_un_poste_ne_nait_pas_devant_une_porte` (`tests/test_devants_js.py`) : les sortes
  du matin nées autour de chaque porte du Faubourg et de La Shop. Avant le correctif : 5 crieurs sur
  un devant sur 73 naissances figées.
