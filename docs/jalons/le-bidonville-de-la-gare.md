# Le bidonville de la gare : l'est de la Gare de triage

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « dans le quartier des trains, je veux plus un bidonville et des maisons
pauvres pour la partie est ».

**Ce que ça donne** : la Gare de triage (`nord.py`, district `gare`) garde ses voies sur ses quatre colonnes
d'îlots de l'ouest (le poste d'aiguillage ne bouge pas) et ses hangars au sud ; ses trois colonnes de l'est
changent de vocation.

- **Le bidonville** (lettre de plan `t`, les trois rangées du nord de l'est, un seul lot) : des cabanes de tôle
  serrées, des sentiers de terre battue entre elles, des barils où brûle un feu, des cordes à linge, des bâches
  et des pneus sur les toits pour tenir la tôle. Aucune porte qu'on pousse.
- **Les maisons pauvres** (`h`, standing `-`, les deux rangées sous le bidonville) : les maisons de la ville,
  en pauvre — les planches aux fenêtres, le fer rouillé, les lampadaires en panne, les poubelles qui débordent.
- ⚠️ **Les dés** : chaque îlot neuf se bâtit avec les SIENS (la recette du Petit-Canton, `_a_ses_des`) ; les
  Friches et le Petit-Canton ne doivent pas bouger d'une tuile.
- La gare garde sa règle « une seule pièce, le poste d'aiguillage » : on n'entre ni dans les cabanes ni dans
  les maisons pauvres.

## Fiche de la deuxième vague

_Martin (29 sept. 2026), à « tu veux pouvoir entrer dans les maisons pauvres ? » :_ « Oui ».

Les logements des maisons pauvres de la gare se visitent, comme ceux du reste de la ville (une porte `D` sur
quelques-unes, la pièce à la mesure du bâtiment, en pauvre). ⚠️ Le logement visitable se décidait sur un état
COMMUN à toute la bande (`premiere_du_genre`, le compteur `visites`) : la gare doit tenir le sien, sinon le
Petit-Canton décide encore quelles portes de la gare s'ouvrent (`test_canton`, le témoin). Les cabanes du
bidonville restent fermées.

## Notes

**Livré le 28 sept. 2026.** `app/nord.py` (`_bidonville`, `_cabane`, `_salir_les_maisons`), `app/carte.py`
(la lettre `t`, les tuiles `{` et `}`, `TOITS_DE_CABANE`), `static/js/sprites.js`, `monde.js`, `son.js`.

- **Le plan de la gare** : `v<<<t<<` sur trois rangées, `^<<<hhh` sur deux, les hangars dessous inchangés.
  Le poste d'aiguillage ne bouge pas. Le district passe de 3 à 9 passants, de 2 à 3 chars.
- **Le bidonville** : une cinquantaine de cabanes en rangées qui ne s'alignent jamais (hauteur et recul inégaux),
  trois tuiles d'allée devant chaque porte (`devants.DEVANT`). **Deux tuiles neuves** : `{` la tôle de cabane
  (une plaque par tuile — galvanisée, rouillée, verte délavée — et le bord de tous les toits) et `}` le mur de
  planches. La porte reste un `d` — un logement : les passants y entrent et en sortent — peinte en planches
  quand elle est dans un mur `}` (`varianteDeTuile`). Sur la tôle, `pneus`, `bache`, `tole` (des
  `EQUIPEMENTS_DE_TOIT` du genre `cabane`, jamais tirés ; le juge des toits les laisse toucher le bord de la
  tôle, jamais se coller). Entre les cabanes, du bric-à-brac (`BRIC_A_BRAC`), et le **baril en feu**
  (`baril_feu`, trois poses de flamme, sa lueur orange la nuit : `SORTES_DE_LAMPE.feu`).
- **Les maisons pauvres** : les maisons de la ville en standing `-`. ⚠️ **La bande ne marquait jamais le
  standing de ses logements** (`vitrines.monter_et_descendre` ne voit que la ville d'avant) : c'est fait dans
  `batir_la_bande` — le fer rouillé des maisons pauvres, et au Petit-Canton aussi (ses blocs `-` et `+`), sans
  toucher ses enseignes. Et la saleté que `salete.py` pose au pied des murs pauvres de la ville d'avant — il
  passe avant la bande —, posée ici, peu (`SALETE_PAR_CENT_TUILES`), jamais devant une porte ; la poubelle
  y déborde.
- ⚠️ **On n'entre pas dans les maisons de la gare** (`_ChantierNord.poser_la_piece`) : le logement visitable se
  décide sur un état COMMUN à toute la bande (`premiere_du_genre`, le compteur `visites`), et le témoin de
  `test_canton` l'a vu — le Petit-Canton décidait quelles portes de la gare s'ouvraient.
- ⚠️ **Le dé d'un LCG** : `Des.entier(0, 1)` puis `Des.entier(2, 3)` à la suite donnaient toujours la même
  somme (les bits faibles alternent) — toutes les façades d'une rangée tombaient sur la même ligne. Le
  bidonville tire par les bits forts (`_entre`, `_parmi`).
- ⚠️ **Les bornes-fontaines de la bande ont bougé** (une fois) : elles se tirent coin par coin, et la gare a
  des croisements de plus. Rien d'autre des Friches ni du Petit-Canton ne bouge. Le bidonville tire SES dés
  (`_a_ses_des`) : le mettre au goût du jour ne les rebattra plus (`test_le_bidonville_tire_ses_des_a_part`).
- Juges : `tests/test_nord.py` (cabanes, feux, rien devant une porte, maisons pauvres, dés à part),
  `test_carte` (le juge des toits, celui des lampadaires) ; mutations rouges pour chacun.
