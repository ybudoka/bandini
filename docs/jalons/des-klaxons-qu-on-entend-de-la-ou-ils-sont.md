# Des klaxons qu'on entend de là où ils sont

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « réduit un peu les klaxon des voiture qui passe ».

- ⚠️ **Mesuré** : au bord d'une rue du centre, 1 à 6 klaxons du trafic par minute, dont les
  deux tiers viennent d'un char **hors de l'écran** — et tous partent au **plein volume**
  (`avertir`, `vehicules.js`), la règle des coups des autres ne les touchait pas.
  **Livré** : le klaxon du trafic, de l'autobus et du char heurté passe par `Son.depuis` —
  muet hors de l'écran, plus doux de loin (`audio.COUPS_DES_AUTRES`, 300 px) ; le sien, au
  volant, reste plein volume. La fréquence ne change pas. Juge :
  `test_le_klaxon_du_trafic_s_entend_de_la_ou_il_est`, qui rougit sans la règle (quatre
  chars à 0,79).
- ⚠️ L'alarme d'un char garé (`declencherAlarme`) reste au plein volume.
