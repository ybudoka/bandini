# La carte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : La carte : se trouver, lire, et voir où va la mission (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « un icône clignotant pour savoir où on est, une légende, savoir où est
la mission en cours. »

Les trois manquaient pour trois raisons différentes, et une seule des trois était un ajout.

- **Se trouver.** Le joueur _était_ dessiné — un carré blanc de 2 px sur la mini-carte, de
  4 px sur la carte plein écran. ⚠️ **Ce n'était donc pas un manque, c'était une régression** :
  ce carré était lisible sur le Faubourg de 157 × 112, et la ville a quintuplé sans qu'il
  grossisse. Il **pulse** maintenant — un anneau blanc qui s'ouvre et se referme en 40 images
  — et le point, lui, reste dessiné **à chaque image** : on ne cache pas la seule chose qu'on
  cherche. Un repère qui clignote s'efface une image sur deux ; celui-là, jamais.
- **L'objectif bat, mais pas pareil.** ⚠️ Deux choses qui clignotent au même rythme se
  confondent : l'objectif garde son battement de 16 images et devient un **losange doré**,
  contre l'anneau blanc du joueur à 40. Deux rythmes, deux formes, deux couleurs.
- ⚠️ **Une cible hors cadre était un mensonge.** Le code la _bornait_ au bord de la
  mini-carte : un objectif à deux cents tuiles s'affichait collé au coin, exactement comme un
  objectif à trois tuiles. Hors cadre, c'est maintenant une **flèche** qui pointe — une
  direction est une information, une position inventée dit le contraire de la vérité. (Elle
  ne clignote pas : une direction n'est pas une alerte.)
- **Une légende** (c'était l'ajout), en deux rangées sous la ville, sur son propre bandeau —
  sans lui elle se lisait sur du vert, du bleu et du gris à la fois. ⚠️ **Et elle ne se
  recopie pas à la main** : elle se construit depuis la table des couleurs, dans l'ordre de la
  table (sinon elle se réordonne d'une ville à l'autre et on la relit à chaque partie).
- ⚠️ **Les couleurs sont des données.** `FAMILLES_DE_LIEU` (Python) déclare 8 familles —
  tes places, magasins, manger, services, soins, transport, travail, repères — et **chaque
  lieu déclare la sienne**. La preuve que c'était nécessaire était déjà là : `COULEUR_BLIP`
  (hud.js) connaissait dix lieux, la ville en compte seize, et les six autres — dépanneur,
  hôtel, cantine, usine, phare, fourrière — tombaient tous sur le même gris par défaut. M8 en
  avait ajouté cinq, M9 un sixième, et personne n'avait touché à la table.
- **La ville entière tient au-dessus de la légende** : centrée bêtement, ses dernières rangées
  finissaient sous le bandeau — et c'est La Pointe qu'on ne voyait plus.
- **Juges (4 neufs)** : chaque lieu déclare une famille qui existe, chaque famille a une
  couleur et un libellé, et **aucune famille déclarée n'est sans lieu** (une ligne de légende
  vide) ; les blips prennent leur couleur dans les données et la légende parle des mêmes
  familles qu'eux, dans l'ordre de la table ; le repère du joueur est présent à **toutes** les
  images avec un rayon qui varie, l'objectif clignote, et les deux formes diffèrent ; une
  cible hors cadre est une flèche, deux cibles dans deux directions différentes ne pointent
  jamais au même endroit, et une cible proche redevient un losange.
- ⚠️ Les juges lisent `Hud.marqueurs()` — ce que la dernière image a dessiné pour se repérer.
  C'est la seule façon de mesurer un clignotement sans regarder l'écran, et c'est le même
  patron que les ancres du test tactile.

## Notes

demande de Martin (« un icône clignotant pour savoir où on est, une légende, savoir où est
la mission en cours ») : le joueur **était** dessiné — un carré blanc de 2 px, lisible sur
le Faubourg de 157×112 et perdu depuis que la ville fait 421×213. Il **pulse** maintenant
(un anneau qui s'ouvre et se referme, 40 images) et ne disparaît **jamais** — on ne cache
pas ce qu'on cherche ; l'objectif bat à un autre rythme (16) et dans une autre forme (un
losange doré). Hors du cadre de la mini-carte, il devient une **flèche** au lieu d'une
position bornée au coin, qui mentait. Et la **légende** se construit depuis la table des
couleurs, descendue de Python (`FAMILLES_DE_LIEU`, 8 familles) : les seize lieux ont tous
une couleur **déclarée**, là où `COULEUR_BLIP` en connaissait dix et laissait six au gris. 4
juges neufs
