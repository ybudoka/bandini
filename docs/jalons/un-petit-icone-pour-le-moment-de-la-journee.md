# Un petit icône pour le moment de la journée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « ajoute un petit icône pour indiquer quel moment de la journée on
est ». Une icône de 7 pixels devant « JOUR N HH:MM », en haut à droite du HUD : un soleil le
jour, une lune la nuit, un soleil à moitié couché à l'aube et au crépuscule. Les quatre
périodes suivent les teintes de `Monde.ambiance` (la même horloge que le ciel), mais se
lisent à l'heure DEHORS : dans une pièce, l'icône dit encore la nuit qu'il fait. Cuite une
fois par période (`Atlas.cuirePeintre`), comme l'étoile.

## Notes

**Livré le 22 sept. 2026.** Une icône de 7 × 7 devant « JOUR N HH:MM » (`MOMENTS` dans
`sprites.js`, `dessinerMoment` dans `hud.js`) : un soleil orange le jour, une lune en croissant
la nuit, un soleil à moitié levé sur l'horizon à l'aube (doré sur bleu pâle) et au crépuscule
(rouge sur mauve). Chaque moment est cuit une fois, avec son ombre d'un pixel comme le texte du HUD.

- `Monde.periode(heure)` lit l'opacité du ciel (`ambiance`) : `nuit` au-delà de 0,4 — pile la règle
  d'`estNuit`, celle des barrières et des fenêtres —, `aube` ou `crepuscule` au-delà de 0,1 (le ciel
  orange), sinon `jour`. Soit la nuit de 19 h 53 à 6 h 24, l'aube jusque vers 8 h 15, le crépuscule
  à partir de 18 h. ⚠️ C'est l'heure DEHORS : dans une pièce éclairée, l'icône dit encore la lune.
- ⚠️ Le soleil est ORANGE, pas jaune : le jaune est à l'étoile de recherche et le doré à l'argent,
  juste au-dessus (voir `ETOILE_ALLUMEE`).
- La boîte `heure` du HUD englobe l'icône : la ligne d'objectif passe dessous comme sous l'heure.
  L'ancre `moment` porte sa `periode`, pour les juges.
- Juges : `test_le_moment_de_la_journee_suit_le_ciel` (les quatre moments dans l'ordre, une fois
  chacun, et `nuit` ⇔ `estNuit` minute par minute) et `test_l_icone_du_moment_se_dessine_devant_l_heure`
  (devant l'heure, à sa hauteur, et la nuit dehors vue d'une pièce). Deux mutations les font rougir
  (seuil de nuit décalé, heure lue à travers les murs).
- ⚠️ Regardé à la capture avant de livrer : la première lune, avec une étoile dedans, se lisait « E »,
  et le premier soleil couchant, avec son reflet, comme une couronne.
