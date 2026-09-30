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

## Notes

- `Vehicules.heurterPietons` ne regarde plus que ceux qui marchent : `!e.dansVehicule` vaut pour le
  piéton comme pour le joueur. La règle de `blesser` (« rien n'atteint qui est assis dans un char »)
  tenait déjà ; c'est le choc autour d'elle qui passait.
- Mesuré au banc (l01, graine 6, trois secondes à fond, Louise assise) : **42 coups et 42 crimes
  `renversement`** avant, le char freiné à 1,23 px/image — juste au-dessus du seuil de renverse
  (1,2) : c'était le « ça donne des coups » ; **0 et 0** après, le char monte à 3,5. Juge dédié :
  `test_l01_louise_dans_l_auto_ne_se_fait_pas_renverser`.
- Le même trou valait pour tout passager d'une escorte (`proteger` : Marco de f09, Zed de p11) : les
  juges d'avant téléportaient le char (vitesse nulle), sous le seuil — ils ne le voyaient pas.
