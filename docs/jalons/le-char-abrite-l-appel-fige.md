# Le char abrite, l'appel fige

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « quand on est dans un voiture ou autre, il ne faut pas que les pietons
puisse nous faire du domage » et « il faut aussi figer tout lors qu'on est au téléphone et
qu'on ne peut pas bouger ». Deux promesses que le jeu ne tenait pas, et la règle qui les
répare était **déjà écrite une fois**, pour le feu : un brasier mord le CHAR et saute qui
est dedans (`majBrasiers`). Ni le poing ni la balle ne la connaissaient — mesuré, un passant
planté à douze pixels enlevait **8 points de vie à travers la portière**, et une balle de
pistolet **30**, sans que la carrosserie perde un seul point.

- ⚠️ **La règle vit maintenant dans `Entites.blesser`** — `if (e.dansVehicule) return false`
  — c'est-à-dire au seul endroit par où passe toute blessure du jeu, plutôt qu'en trois
  exemplaires dans `Combat` (le poing, la balle, la grenaille, et le prochain qui
  s'ajoutera). Ce qui SORT du char descend AVANT de blesser — l'explosion et l'éjection
  appellent `descendre` d'abord, et le char qui renverse quelqu'un ne regarde que ceux qui
  marchent : c'est ce qui rend la ligne sans danger.
- ⚠️ **Et la tôle encaisse VRAIMENT** : la balle qui aurait touché le conducteur mord le
  char (`Vehicules.endommager`), exactement comme le brasier. Sans ça, le seul effet de
  l'abri aurait été de faire **disparaître** la balle, et la police aurait pu vider ses
  chargeurs sur une carrosserie sans jamais rien obtenir — un char serait devenu le seul
  endroit du jeu où l'on ne risque rien. (Tirer sur le capot d'un char **vide** ne fait
  toujours rien : les projectiles ne visent que les gens, c'est un autre chantier.)
- ⚠️ **Le téléphone fige la ville comme un menu** : `B.cinema` clouait le JOUEUR sur place
  (`majJoueur`, `vx = vy = 0`) pendant que le trafic, la foule et la police continuaient —
  mesuré, **26 entités bougeaient pendant qu'on écoutait**, et on encaissait des coups qu'on
  ne pouvait pas rendre. `Jeu.maj` traite désormais un dialogue comme un menu (« le temps ne
  passe pas au comptoir ») ou un fondu de porte : seul `Histoire.maj` tourne, pour que la
  réplique avance et qu'on puisse raccrocher.
- ⚠️ **Sauf au volant**, et cette moitié compte autant : là on PEUT encore bouger
  (`Vehicules.majJoueur` lit toujours le gaz pendant un dialogue), et figer un char lancé
  parce que le téléphone sonne, ce serait poser un mur au milieu de la rue.
- ⚠️ Et « ACTION > » clignote maintenant sur l'horloge de l'**œil** (`B.image`), pas sur
  celle du monde : `B.t` ne bouge plus pendant l'appel, et l'invite serait restée éteinte au
  seul moment où elle a quelque chose à dire. 4 juges neufs (`test_abri_js.py`),
  **rouge-avant prouvé trois fois** (8 points au poing, 30 à la balle, 26 entités qui
  bougeaient) ; le 4e était **vert avant** et le reste — il tient l'autre moitié (au volant,
  la ville tourne et le char répond au gaz), c'est un garde-fou, pas une mesure. 1650 tests.
- ⚠️ Jugé dans un **worktree isolé** : deux autres sessions écrivaient dans l'arbre.
