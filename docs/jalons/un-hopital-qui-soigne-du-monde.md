# Un hôpital qui soigne du monde

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « l'hôpital devrait être plus grand et avec des malades, une salle
d'attente, des solutés, machines de santé ».

- ⚠️ **Mesuré avant** : 11 × 8 tuiles (54 de plancher), deux lits de bois, trois chaises, un
  comptoir — et **pas un malade**. **Livré** : **deux étages de 14 × 10** reliés par un
  escalier (192 tuiles de plancher, 3,5 fois plus). En bas, **l'urgence** : le triage et sa
  soignante en blouse, un lit d'examen occupé, une **salle d'attente** de seize chaises où
  **six patients attendent assis**, et deux distributrices (café, grignotines). En haut,
  **l'étage des soins** : **six malades couchés** dans six lits d'hôpital, chacun entre son
  **soluté** et son **moniteur** (le pic du tracé tombe ailleurs d'un écran à l'autre), et
  le poste des infirmières. Quatre glyphes de meuble — `r` lit d'hôpital (un bloc d'une
  place), `i` soluté, `q` moniteur, `b` distributrice — : ⚠️ ce sont **les quatre dernières
  minuscules libres** de la légende. Deux archétypes (`soignante`, `malade` en jaquette,
  fréquence 0) et deux sortes de gens dedans, jugées au chargement du plan : le `patient`
  naît **sur une chaise**, le `malade` **dans la tuile de tête** d'un lit
  (`ASSIS_OU_COUCHE`) — ailleurs, `_piece` lève. Ils tiennent leur place comme un donneur
  (`fige`) ; qu'on frappe un malade, il redevient un passant et se sauve en jaquette.
- ⚠️ **Plus grand en profondeur et par un étage, pas en largeur** : l'îlot de l'hôpital fait
  douze tuiles de large, et une pièce a exactement les mesures de son bâtiment
  (`test_la_piece_a_les_mesures_de_son_batiment`, cinq graines) — le bâtiment est passé de 9
  × 6 à 12 × 8 sans qu'un autre juge de la ville bouge.
- ⚠️ **Mais le tirage de la ville, lui, glisse** : un bâtiment plus grand consomme le dé
  autrement, et tout ce qui se pose après change de place. Deux juges prenaient « la
  première borne » et « la première voie de la colonne 14 » — la borne est tombée au coin
  nord-est de la carte (on ne pouvait plus s'en éloigner de 900 px) et, au nouvel endroit du
  pickpocket, le **joueur se tenait entre le voleur et sa victime** et les poussait tous les
  deux vers l'est ; et la rumeur de la foule devait « crier plus fort que le murmure voulu »
  alors que ce voulu plafonne à 1 dès dix passants — il y en avait plus au départ. Trois
  juges verts par chance de tirage, durcis sans changer ce qu'ils mesurent, et vérifiés
  verts sur l'ancienne ville comme sur la nouvelle. `tests/test_distributrices.py` (le
  matériel au chevet, la salle d'attente, le plan qui refuse un malade au pied du lit) et
  `test_distributrices_js.py` (trois cents images plus tard, personne ne s'est levé)
