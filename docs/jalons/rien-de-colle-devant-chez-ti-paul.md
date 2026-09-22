# Rien de collé devant chez Ti-Paul

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026, capture) : « trop de choses collé devant chez Ti-Paul,
étale-les plus sur le pâté de maison ». Sur huit tuiles devant la porte : l'édicule du
métro, Ti-Paul, le guichet, la pancarte, l'abribus et son banc — et Xavier, invisible, posé
sur le même pixel que Ti-Paul (les deux bulles empilées). Deux causes, toutes deux
générales. (1) La ligne 2 s'arrête « devant » le dépanneur : l'arrêt prend la place la plus
proche de la porte, c'est-à-dire deux tuiles de côté — la place même du donneur, qui se
rabat entre l'édicule et le guichet. Mesuré : cinq arrêts sont dans ce cas (dépanneur,
planque de Rocco, poste, casse-croûte, hôpital). Remède : `devants.py` fait glisser l'arrêt
le long de SA voie, après coup et sans dé, jusqu'à laisser de l'air au donneur ; l'abri et
le banc suivent, le tracé ne bouge pas (seul l'indice de l'arrêt dans la boucle change). (2)
`placeVisible` pose chaque donneur sans regarder les autres : Ti-Paul et Xavier au
dépanneur, Ti-Guy, Mo et Fern au terminus, tous sur la même tuile. Remède : une place déjà
tenue par un autre personnage (ou collée à lui) passe à la suivante, dans le même ordre
fixe. Juges : aucun arrêt dans l'air d'un donneur, la ville ne bouge que ces arrêts, deux
donneurs jamais à moins de deux tuiles ; mutations ; et une capture du dépanneur.
