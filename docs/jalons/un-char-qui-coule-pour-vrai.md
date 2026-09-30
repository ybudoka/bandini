# Un char qui coule pour vrai

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin : « améliore l'animation des véhicules qui coulent ». Mesuré : `majNoyade` laisse le
char entier et en pleines couleurs pendant `coule_s` (3 s), avec quelques remous, puis
`Entites.retirer` le fait disparaître d'un coup — le dessin (`dessinerUn`) ne lit jamais
`v.coule`. Tranché par Martin, les quatre :

- **il s'enfonce peu à peu** : il pâlit vers l'eau, rapetisse un peu, son ombre s'efface ;
- **le nez en premier** : une ligne de flottaison court de l'avant vers l'arrière, ce qui
  est devant est sous l'eau (presque transparent), un liseré d'écume la suit ;
- **des ronds dans l'eau et un gros glouglou** : des anneaux autour de la coque pendant
  qu'il coule, au fond une grosse bulle qui crève et des cercles qui s'élargissent ;
- **une tache d'huile qui reste** : irisée, quelques secondes, une bulle qui remonte.

⚠️ Sans un dé de plus (tout à l'empreinte : `v.id`, l'âge de la trace) ; la logique ne
change pas (même durée, même perte, même éjection) ; rien ne se dessine dans une pièce ni
sur un bloc. Juges : l'état du naufrage en fonction pure, la trace posée au fond qui
expire, les tirages de `B.rng` identiques ; capture Chromium avant de livrer.
