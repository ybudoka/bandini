# Un char qui ne reste plus pris dans un mur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« mets un garde-fou pour éviter que mon véhicule coince dans un mur ou un
objet »).

- ⚠️ `avancer` teste les tuiles **avant** chaque pas, mais rien ne regardait où le char
  **est** : poussé par un autre char (`heurterVehicules` déplace sans lire les tuiles),
  tourné sur place contre une façade (la chaîne de cercles pivote **dans** le mur) ou
  retombé d'un saut (en l'air, les tuiles ne comptent pas), il se retrouvait dans le mur —
  et de là **chaque direction était bloquée**, même celle qui sort : pris pour toujours.
  `degager()`, à chaque image, pour tout char qui n'est pas sur ses rails : **poussé** hors
  des tuiles chevauchées (mesuré : 4,01 px pour 4 px d'enfoncement, cap gardé — pivoter
  contre un mur fait maintenant glisser le long), sinon **posé** à la place libre la plus
  proche, par anneaux de 2 px jusqu'à 96 px (posé à 48 px du milieu d'un toit, à l'arrêt :
  son élan est ce qui l'a mis là).
- ⚠️ La poussée garde la plus longue sortie par axe, pas la somme : trois cercles enfoncés
  de 4 px demandaient 12. « Un objet », c'est tout ce que `MASQUE_VEHICULE` arrête
  (borne-fontaine, clôture, meuble) ; les poteaux et les bancs ne bloquent pas encore les
  chars — c'est « Le décor se brise ». 2 juges
