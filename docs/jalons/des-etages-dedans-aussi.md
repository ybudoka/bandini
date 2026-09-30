# Des étages dedans aussi

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demandé par Martin le 30 sept. 2026_, après [les étages pour vrai](des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md#fiche)
(vague 1, les façades) : « il faut que les commerces et résidences qui ont plusieurs étages aient aussi plusieurs
étages à l'intérieur ».

**Aujourd'hui** : un logement de 2 ou 3 étages a au plus **une** pièce en haut (`poser_la_piece`, `_haut`) — un
triplex a deux niveaux dedans. Un commerce n'en a aucune, alors que 129 devantures sur 135 peignent 2 ou 3 étages de
logements au-dessus de l'enseigne. Et le nombre d'étages **peint** se décide dans le JS (`logementElargi`,
`etagesDuCommerce` : la profondeur du toit, une rangée de toit toujours visible) sans que Python, qui fait les
pièces, le connaisse.

**La règle** : une porte qui s'ouvre donne sur **autant de niveaux que la façade en peint** — le rez, plus `hauts`.
Ce qu'on voit de la rue fait foi.

**Tranché avec Martin (30 sept. 2026)** :

- **En haut d'un commerce, le logement du commerçant** : un escalier au fond de la boutique, et des logements meublés
  comme l'étage d'un plex (la façade y peint des fenêtres de logement).
- **Python compte, le JS peint** : une seule source pour le dehors et le dedans.

**Le design** :

1. **Le compte, en Python** — `app/etages.py`, à la toute fin de `generer` (après la bande nord : le Petit-Canton
   compris), sur la ville finie, **sans un dé et sans une tuile** : le portage du calcul du JS (les toits d'une même
   matière reliés, `teintesDesToits().qui` ; le mur étendu, `murDuBatiment` et `murDesLogements` ; la profondeur ;
   `2 + hash2(x, y) % 2` pour un commerce ; `ETAGES_MAX`). Il écrit `hauts` sur chaque `residences[]` et
   `devantures[]`. ⚠️ **Avant de brancher quoi que ce soit** : une sonde sous Node compare l'ancien calcul JS au
   compte Python sur toutes les façades — toutes égales, ou le portage est faux.
2. **Le JS peint la donnée** : `logementElargi` et `etagesDuCommerce` lisent `hauts` au lieu de le recalculer.
3. **Les pièces** : pour chaque porte qui s'ouvre, `1 + hauts` niveaux, chaînés par des escaliers (le point
   `escalier`, `vers`, `descend` : `Jeu.changerEtage` sait déjà faire).
   - Logement : `slug`, `slug_haut`, `slug_haut2`… ; un étage du milieu a **deux** escaliers, MONTER et DESCENDRE.
   - Commerce : un escalier au fond de la boutique monte au logement du commerçant (`piece_de_logement(haut=True)`),
     et au-dessus s'il y en a trois.
   - L'escalier prend une tuile libre hors de portée de la porte ; s'il n'y en a pas, la place du meuble le plus
     éloigné de la porte — jamais un coin de lit.
   - ⚠️ **Les escaliers dans les deux sens, ou aucun étage** : personne ne reste pris en haut.
   - ⚠️ **Un logement peu profond qui ne peint aucun étage perd sa pièce du haut** : il devient fidèle à sa façade.
   - La pièce du haut que `poser_la_piece` fait aujourd'hui se fait à la fin, avec les autres. ⚠️ Le tirage
     d'`etages` (`des_devanture`) reste où il est : l'enlever ferait glisser la ville.
4. **Les juges** (chacun rougit quand on retire sa règle) :
   - pour **toutes** les portes de la ville, la suite de pièces compte `1 + hauts` niveaux ;
   - sous Node, le JS peint exactement `hauts`, pour toutes les façades ;
   - chaque étage est rejoignable à pied depuis la porte, en montant et en redescendant ;
   - les juges « ce module ne déplace rien » : le même sol, le même hasard ;
   - le poids du paquet (`test_definitions`).
   - Et **se regarde** : une capture dedans et dehors d'un triplex et d'un commerce à trois étages.

## Notes
