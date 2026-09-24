# La dernière Cravate de M5 ne disparaît plus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (21 sept. 2026) : « la mission de libérer les trois coins des Cravates, la
dernière cravate à trouver n'apparaît pas ». Au banc, deux causes, chacune suffit à bloquer
M5 (Josée) à 5/6. (1) Un flâneur qui passe sous une porte y entre une fois sur douze
(`entites.js`, « Une porte juste au nord ? ») sans regarder s'il est une cible de mission :
au coin 2, sur un trottoir le long d'une façade à porte (207, 61), une Cravate rentre en une
minute sur 2 graines sur 8 ; elle quitte la ville, reste comptée debout, et la flèche montre
la porte, où il n'y a personne. (2) Une Cravate K.-O. (poings, poing américain) se relève 5
s plus tard et s'enfuit : le compteur repasse de 1/6 à 0/6, et il faudrait coucher les six
en 5 s sur trois coins.

- ⚠️ Le correctif : une cible de mission n'entre dans aucune porte, et un homme de mission
  couché reste couché tant que la mission dure (le « 4/6 » lu à l'écran ne recule plus).
  Juges rouges avant, verts après.

## Notes

**Livré le 21 sept. 2026.**

- **La porte** (`entites.js`, le flâneur) : « une porte juste au nord ? une fois sur douze, on
  rentre » écarte maintenant les hommes de mission (`!e.mission`), comme le font déjà `peupler`,
  `quelquUnRentre` et le vol de char. ⚠️ Le test vient APRÈS le dé : il se tire comme avant, et la
  ville d'une mission ne bouge pas. Au banc (la ville d'aujourd'hui ; sa partie est restée en M5, à
  l'étape 0), la Cravate du coin 2 flâne sur le trottoir d'une tuile sous la porte (207, 61), et
  y entrait en 57 s à la graine 1, en 70 s à la graine 8 ; avec le correctif, aucune des six ne
  quitte la ville en 10 minutes de jeu sur ces deux graines.
- **Le K.-O.** : une cible de mission (`e.cible`) couchée reste couchée tant que la mission dure ;
  sa minuterie ne tourne plus. `nettoyer` lui retire `cible` à la fin (réussie, ratée ou
  abandonnée), et elle se relève alors, 5 s plus tard, comme tout le monde. C'est ce que disait
  déjà `retenirLesTombes` (« K.-O. compte comme mort ») : le compteur ne recule plus. Ça vaut
  aussi pour les deux Cravates de M2, le porteur de la caisse et le chef de M5.
- Les juges (`test_histoire_js`) : une Cravate de M5 plantée sous une porte, le dé forcé à
  « rentre » une fois sur deux, n'entre pas — et un TÉMOIN (la même, sans mission) entre, pour que
  le juge morde encore si la règle de la porte change ; une Cravate K.-O. reste au sol 600 images
  (compteur à 1/6), puis se relève quand la mission s'arrête. Mutations : sans `!e.mission`, la
  Cravate rentre ; sans `!e.cible`, le compteur retombe à 0/6. Rouge les deux fois.
- ⚠️ **Ce qui reste** : les Cravates flânent loin de leur coin (deux du même coin à 1 100 px l'une
  de l'autre après 8 minutes) ; la flèche les suit, donc on les trouve, mais « vide les trois
  coins » ne dit plus vraiment où elles sont. Et après la mission, `nettoyer` laisse `e.mission`
  aux survivantes : `peupler` ne les oublie jamais, elles errent jusqu'au rechargement (d'avant,
  non touché).
- La suite complète : 3 753 verts, 14 sautés, 3 rouges — les trois aussi rouges sans ce correctif
  (rejoués sur `75f6485`) : les Cravates de M2 (« ils arrivent de hors de l'écran »), la foule, et
  le poids du paquet (44 075 octets gzip sur la base).
