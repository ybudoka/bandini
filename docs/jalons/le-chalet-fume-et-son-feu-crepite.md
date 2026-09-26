# Le chalet fume, et son feu crépite

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 26 sept. 2026, après [le vrai chalet dedans](un-vrai-chalet-dedans-et-son-foyer.md) : « Oui va plus
loin ». Les deux suites proposées : **la cheminée vue de dehors**, en pierre sur le toit de bardeaux, et
**la fumée** qui en sort (on sait de loin, sur le rang, que le feu est allumé) ; et **le crépitement du feu**
quand on est dedans — un bruitage ElevenLabs en boucle, plus fort près du foyer.

## Notes

Livré le 26 sept. 2026.

- **La cheminée** : le bloc la déclare (`BLOC["cheminees"]`, `app/blocs/chalet.py`), au-dessus du foyer de
  la pièce, une rangée sous le faîte nord — sur le faîte même, on ne la voyait pas depuis la porte (cachée
  sous le HUD à la première capture). `carte_du_bloc` la passe au navigateur (`def.bloc.cheminees`). La
  souche de pierre, son chapeau et son ombre se peignent PAR-DESSUS le toit (`Blocs.dessiner`) : une tuile
  de plus au milieu des `P` couperait le versant que le toit calcule d'après ses voisines.
- **La fumée** (`Blocs.dessinerFumees`, `FUMEE`) : huit bouffées qui montent, grossissent, dérivent vers
  l'est et s'effacent, d'après `B.t` (jamais un dé), peintes au-dessus des toits ET des gens.
- **Le crépitement** : `audio.py` gagne `foyer` (une boucle ElevenLabs de 8 s, générée le 26 sept. 2026 —
  enveloppe mesurée : fond régulier vers −29 dB, craquements brefs jusqu'à −1,6 dBFS, début et fin au même
  niveau). `Monde.majFeuDeFoyer` l'allume dans une pièce qui a un foyer (`foyersDeLaPiece`), plus fort à
  l'âtre qu'à la porte (`FEU_SON`), et l'éteint en fondu en ressortant. ⚠️ Pas de synthèse de repli :
  sans fichier, le feu se tait, comme le vent de la tempête.
- Juges (`test_chalet_js.py`) : `test_de_dehors_la_cheminee_fume` (la souche sur le toit, la fumée qui
  monte et change d'une image à l'autre — rouge si on la fige) et
  `test_dedans_le_feu_crepite_plus_fort_pres_de_l_atre` (rouge sans `majFeuDeFoyer`).
