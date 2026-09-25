# Un char qui coule est détruit

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « pour la mission de détruire le camion devant l'usine, si on le fout dans l'eau ça devrait le détruire. (même hors mission) »

- ⚠️ **Mesuré avant** : `Vehicules.majNoyade` retire de la ville le char qui touche le fond, mais son `etat` reste `stationne` ou `roule`. Or tout ce qui guette un char détruit lit `etat === 'epave'` : `detruire` (q03) ne l'a jamais vu mourir, et le chrono faisait échouer la mission avec le camion au fond de la baie. Même chose pour le char d'une mission qui coule : aucun `vehicule_detruit`, la mission restait prise.
- **La règle, partout** : un char qui coule est une épave, comme un char qui explose — l'état, la vie à zéro, le câble de la remorque qui lâche.

## Notes

Livré le 25 sept. 2026, dans `Vehicules.majNoyade` (`static/js/vehicules.js`).

- **Au fond, c'est une épave** : `etat = 'epave'`, la vie à zéro, la vitesse à zéro, et le câble de la remorque lâche (des deux bouts, comme `exploser` et `plier`) — avant `perdu` et `retirer`. Rien d'autre ne change : le char disparaît toujours, et on ne le retrouve ni au fond ni à la fourrière.
- **Ce qui en profite sans une ligne de plus** : `detruire` (q03 : le camion poussé dans la baie compte), `vehicule_detruit` (le char d'une mission qui coule fait échouer la mission au lieu de la laisser prise), et un boulot dont le char coule s'abandonne.
- Juges : `test_q03_le_camion_pousse_a_l_eau_est_detruit` (`tests/test_dix_missions_js.py`, le camion posé dans l'eau la plus proche de sa ruelle, il coule, l'étape passe à 1) et `test_un_char_qui_coule_hors_mission_est_une_epave` (`tests/test_eau_son_js.py`). **Ils mordent** : sans le correctif, les deux rougissent sur `'stationne'`.
- ⚠️ Un char garé loin du joueur est oublié par `peupler` avant de couler : le juge hors mission pose le joueur sur la rive, et exige qu'il ait coulé après au moins 170 images (trois secondes d'enfoncement).
