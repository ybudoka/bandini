# L'autobus accroché au carrefour des Quais

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Trouvé par la passe de qualité du 2 oct. 2026 (mise en ligne de la 0.415.1) ; Martin : « plus tard ».

Au carrefour des Quais (vers la tuile 72, 283), un gros véhicule — un camion — arrêté au feu dans la voie d'en
face déborde sur celle de l'autobus. L'autobus qui passe l'accroche, pivote et reste coincé plusieurs minutes. Un
joueur peut le voir. Le juge de l'abribus (`test_autobus`, graine 4 et d'autres) coupe désormais le trafic pendant
qu'il suit l'autobus, pour juger l'abribus et non la rue : ce défaut-ci n'a donc plus de juge qui le voie.

- Cause probable : la boîte d'un long véhicule arrêté au feu n'est pas tenue dans sa voie (elle déborde sur
  l'axe), et l'autobus, qui suit son rail, pivote au contact au lieu de freiner derrière ou de passer.
- À faire : un juge qui rejoue le carrefour des Quais avec le camion au feu (sur plusieurs graines), puis tenir
  les gros véhicules arrêtés dans leur voie, ou faire attendre l'autobus au lieu de pivoter. Sans décaler le
  hasard du trafic (mémoire « Mesurer le trafic dans les boîtes »).

## Notes

✅ **Livré** (8 oct. 2026). La cause n'était pas le camion : il attendait à sa ligne d'arrêt, dans sa voie
(1188, 4520). Rejouée sur trente graines du juge de l'abribus, trafic laissé en place, la graine 19 retenait
l'autobus 2 612 images. La trace image par image : l'autobus tourne proprement de (71, 283) vers l'est, et en
sortant du virage, sa caisse (y ≥ 4 528) **frôle** celle du camion (y ≤ 4 527,5) — un reste de cap de 0,02 rad
suffit. Le choc le pousse de treize pixels vers le trottoir. Or `Autobus.conduire` ne passait à la tuile suivante
que posé **pile** sur le centre de celle qu'il visait (à un demi-pixel) : poussé, il ne l'atteignait plus. Cinq
pixels avant sa tuile et treize de côté, il la visait presque à angle droit — le nez dans la voie d'en face,
contre le même camion — et restait pris ; poussé au-delà, la cible passait derrière lui et il se retournait.
C'est aussi [l'arroseuse qui tourne à 180°](l-arroseuse-qui-tourne-a-180.md) : elle roule avec ce code.

- La correction (`Autobus.tuileAtteinte`) : la tuile visée compte pour atteinte quand il l'a **dépassée** le long
  de sa route, ou, poussé hors de son rail de plus d'un pixel, quand il en est à moins d'une tuile — il vise alors
  toujours au moins une tuile devant lui et rejoint sa voie en biais. Sur le rail, rien ne change : `rouler` le
  pose pile sur sa cible, il pivote au centre de la tuile (le retour de Martin du 30 sept. 2026 tient). Aucun dé.
- ⚠️ Le frôlement lui-même (un demi-pixel, selon le reste de cap) ne se rejoue pas dans un juge court : le juge
  des Quais (`test_pousse_hors_de_son_rail_js.py`) reprend l'autobus **dans l'état capturé** juste après le choc
  (1171, 4549, cap 5,29), le camion tenu à sa ligne d'arrêt à chaque image. ⚠️ Un camion garé laissé à lui-même
  ne rejoue rien : il se laisse pousser et s'écarte ; celui du trafic revient sur sa ligne, et c'est l'autobus qui
  cède. Rouge sans la correction (pris en (73, 284) les 900 images), vert avec.
- Le juge « poussé au-delà de sa tuile » tient l'autobus et l'arroseuse : six pixels au-delà, cinq de côté, le
  nez reste vers l'avant (cos > 0,5) ; sans la correction, les deux se retournent (cos −0,76).
