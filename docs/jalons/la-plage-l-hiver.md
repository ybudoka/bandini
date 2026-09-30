# La plage l'hiver

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026), capture d'une plage un soir de janvier : « la plage devrait aussi être en
hiver, et les exhibitionnistes prennent une pause ». Mesuré : le sable de la grève (`s`) garde sa
couleur d'été toute l'année pendant que le gazon et les trottoirs blanchissent ; les serviettes, les
parasols, les chaises longues, les châteaux et les kayaks restent semés ; les baigneurs n'ont que
leurs heures (`PLAGE.heures`), pas de saison ; et l'homme au manteau ouvre le sien en plein janvier.

Correctif, sans un dé et sans rien déplacer :

- **Le sable sous la neige.** La tuile `s` passe par `Saisons.enneiger`, comme le trottoir : blanche
  tant que la neige tient, avec le sable qui perce ; le dégel la rend.
- **La plage rangée.** Au-dessus d'un seuil de froid (`PLAGE.froid_max`), les meubles mous de la grève
  (parasol, serviette, chaise longue, château de sable, kayak) ne se peignent plus. Aucun n'est solide :
  les ranger ne laisse pas de mur invisible. La chaise du sauveteur et les tables restent.
- **Pas de baignade hors saison.** Le même seuil garde les baigneurs : personne n'y naît, et qui y est
  encore plie bagage hors champ, comme à la fermeture du soir.
- **L'exhibitionniste prend congé.** Une sorte peut porter `froid_max` comme elle porte `heures` :
  au-dessus, elle ne naît pas et rentre hors champ. L'homme au manteau a le sien.

Juges : le sable de janvier est blanchi, celui de juillet ne l'est pas ; en janvier un parasol ne se
peint pas et aucun baigneur ne naît ; l'exhibitionniste ne naît pas en janvier et naît en juillet.

## Notes

**Livré le 30 sept. 2026.**

- **Le sable** (`sprites.js`, tuile `s`) : ses couleurs dans `SABLE`, passées par `Saisons.enneiger`
  comme le trottoir ; les galets gardent leur teinte et percent la neige. La tuile cuite se repeint au
  palier, comme le gazon.
- **La saison de la plage** (`PLAGE.froid_max` = 0,2, `pietons.py`) : ouverte l'été et en août (froid
  0 et 0,1), fermée au printemps (0,45), à l'automne (0,4), en novembre et l'hiver.
  `Entites.plageEnSaison()` la lit ; `Entites.enSaison(froidMax)` est le pendant d'`enService` pour
  l'année, sans dé.
- **La grève rangée** : `ete: true` dans la fiche du parasol, de la serviette, de la chaise longue, du
  château de sable et du kayak (aucun n'est solide). Hors saison, `Entites.dessiner` les saute. Le
  château sort de l'index fixe (`estIndexable`) pour qu'un char ne défonce pas un château invisible ;
  `rangerLaGreve` réindexe au changement de saison (vérifié toutes les 60 images), jamais par image.
  La chaise du sauveteur et les tables restent.
- **Les baigneurs** : même garde que les heures, à la naissance et dans `majPlage` (on plie bagage
  hors champ).
- **L'homme au manteau** : `froid_max` (0,75, le grand froid de `HABITS`) sur l'archétype, clé
  facultative (`NotRequired`) pour ne pas alourdir le paquet. `naitreLesSortes` ne le fait plus naître
  et `majSortes` le fait rentrer hors champ. À l'écran, il flâne sans ouvrir son manteau jusqu'à sortir
  du champ.
- **Juges** : `tests/test_plage_l_hiver_js.py` (5 juges, chacun avec son témoin de juillet ; les
  huit règles retirées une à une font rougir le bon juge). Les bancs de `test_plage_js.py`,
  `test_la_nuit_js.py` et du manteau (`test_pietons_js.py`) se jouent désormais le 22 : une partie
  commence en janvier. ⚠️ Pas le 21, le déménagement déplace le joueur. ⚠️ Sur 1 800 images, les
  hommes de Sal envoient parfois le joueur à l'hôpital, selon la graine : les bancs neufs le rendent
  invincible.
