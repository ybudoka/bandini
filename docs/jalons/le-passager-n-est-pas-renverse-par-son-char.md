# Le passager n'est pas renversé par son char

← [le plan](../plan.md)

## Fiche

Vu par Martin dans « Une photo pour la une » (l01, 30 sept. 2026) : dès que Louise monte dans l'auto,
ça cogne sans arrêt, avec du bruit, et la police monte à cinq étoiles, même après un passage à la
peinture.

Un `proteger` assis dans le char (`c.dansVehicule`) reste un piéton de `B.entites`, collé au centre du
char à chaque image. `Vehicules.heurterPietons` écarte le joueur assis, pas le passager : au-delà de la
vitesse de renverse, le char « renverse » son passager à chaque image. `blesser` refuse bien le coup
(qui est dedans ne se blesse pas), mais le reste du choc passe : le coup sourd, la secousse, le char
freiné, et un crime `renversement` signalé à chaque image — les étoiles remontent aussitôt effacées.

- ⚠️ Le char ne heurte que ceux qui marchent : un piéton assis dans un char (le passager d'une
  escorte, Marco de f09, Louise de l01, Zed de p11) est hors du choc, comme le joueur.
