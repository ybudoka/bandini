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
