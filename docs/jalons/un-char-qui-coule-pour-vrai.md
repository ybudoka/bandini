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

## Notes

Livré le 30 sept. 2026. `static/js/naufrage.js` (ses réglages dans le fichier, hors du paquet) ;
`Vehicules.dessinerUn` lui passe le toit d'un char qui coule, `majNoyade` pose la trace au fond, `Jeu.rendre`
dessine les traces sur l'eau, sous les gens (oubliées à chaque partie et à chaque passage de bloc).

- **La ligne court sur l'IMAGE, pas sur la caisse** : le sprite déborde la longueur du char (pare-chocs,
  hauteur vue de biais), et un coin de l'arrière restait net et sombre quand le reste avait coulé — c'est la
  capture qui l'a montré, pas les juges. Une fois la ligne passée, tout est dessiné sous l'eau.
- **L'écume en points, pas en trait** : un trait blanc continu se lisait comme une rayure sur la tôle.
- **Aucun dé** : tout se tire à l'empreinte (`v.id`, l'âge de la trace). `test_couler_ne_tire_aucun_de_de_plus`
  compare deux bancs neufs, module coupé ou non (dans le même banc, la deuxième partie ne part pas du même
  état : 178 contre 180 images, pour rien) ; il rougit si la tache tire un seul `B.rng()`.
- Juges : `tests/test_naufrage_js.py` (le nez avant l'arrière, la trace au fond qui s'efface, rien dedans ni
  dans une partie neuve, les dés).
