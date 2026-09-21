# Le motard revient sur la moto volée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « quand on vole une moto, la personne qui était dessus s'en va, mais
quand on la quitte, il y a encore une personne dessus ».

- ⚠️ **Mesuré** : descendu de la moto, on revoyait **le même** motard qu'avant le vol (mêmes
  couleurs), et le passant qui sortait n'avait pas sa tête. `Vehicules.monter` n'effaçait le
  pilote du trafic (`v.pilote = null`) que dans la branche du **vélo** ; la moto passe par
  le carjacking, qui faisait sortir un passant tiré au hasard et laissait `v.pilote` sur la
  selle — caché par le joueur tant qu'il roulait, revenu dès qu'il descendait. Le carjacking
  fait maintenant descendre **celui qui était dessus**, avec ses couleurs, comme le vélo —
  sans tirer de dé de plus.
- ⚠️ **Et la règle se tient une fois pour tous**, dans `cavalierDe` : le pilote du trafic ne
  se peint que tant que le **trafic** conduit. Le même fantôme restait assis sur la moto du
  **fuyard** quand il en tombe (`faireTomberLeFuyard` remet `conducteur` à null sans toucher
  au pilote) pendant que le Cravate s'enfuit avec la caisse.
- ⚠️ **Reste ouvert, vu en chemin** : ce motard du fuyard porte une tête **de la rue**, pas
  celle du Cravate qui en descend. 1 juge neuf (`test_poses_vehicules.py`), **rouge avant**
  sur les trois constats. 1839 tests, jugés dans un worktree isolé, et les fichiers de
  véhicules rejugés sur le HEAD de la chaloupe.
