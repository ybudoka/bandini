# La carte d'un bloc à étages : un étage à la fois

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (30 sept. 2026), capture de la grande carte dans la villa du maire à l'appui : « je ne
veux pas voir tous les étages d'un coup — et valide toutes les missions qui se passent là, pour que ça ne
soit pas incohérent ».

La villa (`app/blocs/villa.py`) tient ses trois étages dans une seule carte : le terrain et le
rez-de-chaussée en haut, l'étage et la cave dessous. La caméra ne sort jamais du **cadre** du joueur
(`Monde.cibleCamera`), mais la grande carte (`Hud.dessinerCarte`) dessinait la carte entière — on y voyait
l'étage et la cave collés sous le terrain, avec les lieux et les marqueurs de tous les étages.

- La grande carte d'un bloc à `cadres` ne montre que **le cadre où se tient le joueur**, à sa propre
  échelle ; ce qui est hors du cadre (lieux, défis, agents) ne se dessine pas.
- Le titre nomme l'étage.
- L'objectif sur un autre étage : le repère va à l'escalier qui y mène, pas dans le vide.
- Puis les missions de la villa (`v01`, `v02`, `v03`, `e07`) rejouées au banc, la carte ouverte à chaque étape.
