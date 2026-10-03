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
