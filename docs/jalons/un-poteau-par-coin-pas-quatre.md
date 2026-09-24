# Un poteau par coin, pas quatre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Un poteau par coin, pas quatre (**correctif**, taille 1) — **livré le 14 sept. 2026**_

_Retour de Martin, une fois les feux visibles :_ « refais une passe de validation visuelle des
feux, car il y en a trop, il faut que ce soit plus réaliste. »

Il avait raison, et la mesure a trouvé pire que « trop ».

- ⚠️ **Les 124 feux de chars étaient plantés DANS un poteau piéton** — à la tuile près, 124 sur
  124, pas un seul qui ne le soit. `coinLibre` vise le coin **nord-est** et le coin **sud-ouest**
  du croisement ; `carte.py` pose ses feux piétons au **bout de chaque traverse**, ce qui est
  exactement ces coins-là. Et `coinLibre` ne les voyait pas : il n'écarte que le décor **solide**
  (`decorAutour` lit `grilleFixe`), où un feu n'entre jamais — il n'est pas solide. Tant que les
  lanternes n'étaient pas peintes, deux poteaux noirs l'un dans l'autre ne se voyaient pas ; le
  correctif d'avant les a rendus visibles, et le défaut avec.
- ⚠️ **Et il ne fallait surtout pas les écarter d'une tuile.** Ça aurait fait un poteau **de
  plus** à regarder, au lieu d'un de moins. La mesure suivante dit quoi faire à la place : en
  groupant les poteaux d'un croisement par proximité, **chaque croisement en donne exactement
  trois grappes**, et sur 186 grappes il y en a **174 de deux poteaux — tous à UNE tuile d'écart,
  pas un seul à deux**. Une tuile, c'est deux mètres et demi. Ce ne sont pas deux endroits, c'est
  **un coin de rue**, et dans la vraie vie ces deux têtes-là sont sur le même mât.
- **Un mât par coin, jusqu'à trois têtes.** Les feux des chars se posent **d'abord** ; chaque
  traverse cherche ensuite le mât de son coin (la tuile même, puis l'anneau d'une tuile) et lui
  accroche sa tête — au plus deux, celles des deux rues qui s'y croisent. Ce qui ne trouve pas de
  mât en plante un.
- **484 poteaux → 186**, soit **3 par croisement au lieu de 8** (124 mâts de chars, 62 poteaux
  seuls). ⚠️ **Et les 360 traverses sont toujours montrées** : un juge compare le nombre de têtes
  peintes au nombre de traverses que la carte pose. On a retiré des **poteaux**, pas de
  l'**information** — c'est toute la différence entre alléger et amputer.
- ⚠️ **À deux têtes, les ampoules rétrécissent à trois pixels** et se posent aux **mêmes colonnes**
  que celles des chars, juste au-dessus. Deux raisons, et la seconde n'est pas du goût : à quatre
  pixels chacune elles se **toucheraient**, et deux rouges qui se touchent font un seul rectangle
  rouge. L'alignement, lui, est ce qui fait lire le mât comme **un** poteau plutôt que comme deux
  collés — un empilement de boîtiers dont les feux tombent sur la même verticale.
- ⚠️ **Deux rangées de vide entre la tête des chars et celle des piétons.** Collées, les deux ne
  font qu'un bloc noir et on ne voit plus qu'il y en a deux. Et la tête est à la **hauteur du
  poteau isolé**, à un pixel près : la même tête au même niveau, qu'elle ait son mât ou qu'elle le
  partage.
- **Juges (2 neufs)** : aucun poteau planté dans un autre, aucune paire de mâts du **même
  croisement** à une tuile, aucun mât à plus de deux traverses, **autant de têtes que de traverses
  posées par la carte**, et le compte borné à trois par croisement — sans cette borne-là, un jour
  ou l'autre on en remet. Le premier est **rouge sur le code d'avant** : « 124 poteaux plantés
  dans un autre ».
- **Ce qui reste ouvert** : un croisement n'a de poteau qu'à **trois** coins — le quatrième est
  refusé par `carte.py` quand le trottoir y est déjà pris. Ça se voit peu, et ça se corrigerait
  côté carte, pas côté dessin.

## Notes

retour de Martin, une fois les feux visibles : « il y en a trop, il faut que ce soit plus
réaliste ». Mesuré, et c'était pire que trop : **les 124 feux de chars étaient plantés DANS
un poteau piéton**, à la tuile près — 124 sur 124. `coinLibre` vise les coins nord-est et
sud-ouest du croisement, exactement les bouts de traverse où `carte.py` pose ses poteaux, et
il ne les voyait pas : il n'écarte que le décor **solide** (`grilleFixe`), où un feu n'entre
jamais.

- ⚠️ **Et les écarter d'une tuile aurait fait un poteau de PLUS.** Le reste se groupait par
  deux à **une tuile** d'écart — 174 paires, pas une seule à deux : c'est le même coin de
  rue, et un vrai carrefour met ces têtes-là sur **le même mât**. Un mât porte donc la tête
  des chars **et** jusqu'à deux têtes de traverse, alignées sous elle. **484 poteaux → 186**
  (−61 %), **3 par croisement au lieu de 8**, et **les 360 traverses sont toujours
  montrées** : on a retiré des poteaux, pas de l'information. 2 juges neufs
