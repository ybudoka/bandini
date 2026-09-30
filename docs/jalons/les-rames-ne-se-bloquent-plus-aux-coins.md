# Les rames ne se bloquent plus aux coins

← [le plan](../plan.md)

## Fiche

Retour de Martin (30 sept. 2026), capture à l'appui : « il y a des bouchons aux tram et bus » —
deux rames et un autobus enfoncés les uns dans les autres dans une boîte du Faubourg.

**Rejoué au banc**, boîte (25, 196) où la ligne T tourne : les rames sont espacées de 207 tuiles
sur une boucle de 622, l'aller passe la boîte à l'index 104 et le retour à 515 (= 104 + 2 × 207 − 3)
— **deux rames s'y croisent à presque chaque passage**. Celle qui tourne à droite coupe le coin
comme le trafic (elle vise la tuile suivante à 6 px du centre) : au bout de la boîte, son nez de
48 px pointe encore de 18° dans la voie d'en face, où l'autre rame attend au rouge. Elle la voit
comme un obstacle et s'arrête ; l'autre attend que la boîte soit rendue : **1 400 images
d'impasse**, l'autobus de la ligne 2 derrière, puis tout le monde force et les caisses se
recouvrent de 15 px.

- ⚠️ Une rame pivote AU CENTRE de sa tuile, sur ses rails — elle ne coupe pas les coins.

## Notes

Quatre causes, trouvées une à une au banc (sept boîtes de la ligne T, trois horaires chacune,
8 000 images, le joueur à côté), toutes du même genre : **deux véhicules qui s'attendent l'un
l'autre**.

- ⚠️ **Le coin coupé** (`Autobus.conduire`) : un véhicule de ligne visait la tuile suivante à 6 px
  du centre. Une caisse de 48 px sortait du virage le nez de biais — dans la voie d'en face (la
  rame qui y attendait la boîte qu'elle tenait : impasse), ou sur l'auto arrêtée à la ligne d'à
  côté, qui attendait « légitimement » et la repoussait d'autant qu'elle avançait (l'autobus
  figé 600 images à vitesse 1,1, donc invisible pour son chien de garde). Tout véhicule de ligne
  pivote maintenant au centre de la tuile.
- ⚠️ **Celui d'en face qui attend dans sa voie** (`Vehicules.obstacleDevant`) : seul un char d'en
  face qui ROULAIT comptait « dans sa voie ». Arrêté, il arrêtait qui sortait de la boîte le nez
  de biais. `arreteDansSaVoie` : sur une flèche (ou une ligne d'arrêt, `Monde.sensArret`) de son
  sens, à contresens du nôtre, et notre centre hors de son couloir — l'écart se juge à SON axe.
  À contresens dans notre voie, il reste un obstacle.
- ⚠️ **La rame arrêtée qui gelait la boîte** (`Vehicules.croisementLibre`) : le trafic cédait à
  toute rame tournée vers la boîte, même arrêtée au rouge (toute la phase verte de la rue qui la
  croise perdue) ou derrière une auto à la ligne (l'auto lui cédait, elle attendait l'auto). Il ne
  cède plus qu'à une rame qui roule ; elle réserve la boîte en s'y engageant, comme tout le monde.
- ⚠️ **La rame poussée hors de ses rails** (`Vehicules.heurterVehicules`) : deux rames se croisent
  sur deux voies voisines à 16 px, deux demi-largeurs pile. Celle qui roulait, poussée par celle
  qui attendait au rouge, glissait, braquait vers sa cible (donc vers l'autre) et finissait de
  travers — jusqu'à 45 px hors des rails, 3 000 images plantée. Une rame ne se pousse plus :
  contre elle, l'autre encaisse ; entre deux rames, personne.
- Mesuré (plus longue attente sans feu ni arrêt, près de la boîte ; écart aux rails) : base
  **819 / 2 059 / 3 109 / 3 843 / 2 681 images**, rames jusqu'à **45 px** hors des rails ; après,
  rien au-dessus d'une file au rouge (≤ 530), **0,4 px** hors des rails. Juges dans
  `test_tramway_js.py` : le coin où deux rames se croisent, la rame arrêtée qui ne gèle pas la
  boîte, celui d'en face dans sa voie, la rame qu'on ne pousse pas — les quatre rougissent sur la base.
