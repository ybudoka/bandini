# Les chars de dos et de face, en vue plongeante

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « les voitures de face et de dos devraient être vues à 45 degrés, pas de
face, vu la carte » — « vue plongeante ». Les poses `haut` et `bas` sont des **élévations au
ras du sol** : on voit la face arrière (ou avant) bien à plat et presque pas de toit, alors
que la carte se regarde d'en haut. Un char qui roule vers le nord ne montre donc **rien de
ses 28 px de longueur** — c'est le défaut que l'ombre au sol compensait. À 45°, la longueur
se projette sur l'axe vertical (28 × sin 45° ≈ 20 px) : il faut donc **agrandir la toile**
des sprites vers le haut et remonter l'ancre, redessiner les 18 grilles (9 familles × 2
poses), replacer la selle des deux-roues, et rejouer les juges qui lisent l'ancre comme « la
hauteur du dessin ». ✅ **Livré** (15 sept. 2026) : les 18 grilles redessinées (9 familles ×
2 poses), la toile agrandie vers le haut et l'ancre remontée à la nouvelle ligne de sol.
**La règle, et elle se mesure** : de dos comme de face, un char occupe à l'écran sa
**longueur** — exactement ce que son ombre au sol annonce déjà (avant : 12 rangées peintes
pour une berline longue de 28).

- ⚠️ Ce qui fait lire une auto vue d'en haut, et qui manquait au premier jet : **une
  silhouette**. Un char n'est pas un pavé — il se pince au nez et à la queue, ses ailes
  débordent sur les roues, sa cabine est **posée en arrière du milieu** et plus étroite que
  la caisse, et son montant est l'ombre de la caisse (`D`) et non un trait noir : cerclée de
  `k`, la cabine se lit comme un trou de toit ouvrant. Le **capot reste plat et sombre**
  pour que le toit soit la seule surface haute — une arête claire sur le capot le mettait au
  même ton que le toit, et plus rien ne levait. La lumière vient du **nord-ouest** comme
  partout ailleurs : flanc gauche au jour, flanc droit dans l'ombre. Les familles dérivent
  d'un seul patron (`berline` / `camion`) et ne diffèrent que par quelques nombres — capot,
  toit, coffre, longueur de boîte, nervures : une berline, un coupé, une limousine, une
  ambulance, une remorqueuse, un camion, un autobus. Les deux-roues sont écrits à la main
  (un vélo n'a ni capot ni coffre) et leur **selle** remonte avec la toile.
- ⚠️ Trois juges rejoués, et ils ont payé : le char **flottait d'une rangée** (l'ancre
  n'était pas la dernière rangée peinte), la règle « rien n'est plus haut que long » datait
  du dessin à plat, et le juge de l'ombre prenait l'ancre pour la hauteur du char — il
  mesure maintenant ce que le **flanc** monte, sinon sa borne se relâchait de vingt pixels
  en silence. 1 juge neuf, rouge-avant prouvé (« auto de dos : 12 rangées pour un char long
  de 28 — il est dessiné de face, pas vu d'en haut ») ; 1590 tests
