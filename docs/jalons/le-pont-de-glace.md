# Le pont de glace

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ l'hiver, la baie gèle, et on roule jusqu'à l'Île-aux-Corneilles — qu'on ne rejoint
aujourd'hui qu'en bateau.

**Aujourd'hui** l'île (`ile.py`) ne se rejoint pas à pied (c'est pour ça qu'aucun lieu de mission n'y est
posé, `test_barrieres.py`) ; la neige de M12 (`neige.js`) a son intensité calculée du jour et de l'heure.

- **Quand** : les jours les plus froids de l'hiver du jeu, calculés — un chemin balisé de sapins sur la
  glace, de la Pointe à l'île.
- **Ce qu'il change** : l'eau du chemin devient roulable (le masque des véhicules), l'adhérence est
  minimale ; au dégel, la glace craque — un char arrêté trop longtemps passe au travers (drôle, et
  dangereux).
- **Ce qu'il ouvre** : des missions sur l'île par la route, l'hiver seulement.

⚠️ **Ce qui guette** : l'eau est une couche que beaucoup de juges tiennent (la baie, les bateaux, les
nageurs) — rendre des tuiles d'eau roulables pour quelques jours touche à tout ça ; les bateaux amarrés ne
doivent pas se retrouver pris dans la glace au milieu du chemin.

**Juges** : le chemin n'existe que les jours froids ; un char y roule, un bateau ne le traverse pas ; au
dégel, rien ne reste coincé dans une glace disparue.

## Notes

_Livré le 26 sept. 2026._ ⚠️ **Derrière l'option « NEIGE (ESSAI) »** : c'est l'hiver du jeu.

- **L'année du jeu** (`app/calendrier.py`, `static/js/calendrier.js`) : le jeu n'avait pas de saisons, et
  cinq idées du plan en demandent (le pont, la motoneige, la cabane à sucre, la Saint-Jean, le ciné-parc,
  les Fêtes). Martin a dit « fais tout le reste » : une seule année les porte — **quarante jours, douze
  mois de trois ou quatre jours, le jour 1 est le premier janvier**, une pure fonction du jour. Rien de ce
  qui existe n'en dépend (la neige tombe toujours tous les trois jours, le verglas garde ses jours 9 à 11,
  la fin de mars). Le HUD et la pause écrivent le mois : « JOUR 3 · JANVIER ».
- **Le grand froid** : les jours 3 à 6 de l'année (fin janvier, début février), revenant chaque hiver. Le
  dernier, à partir de midi, c'est le dégel.
- **Le chemin** (`app/pont_de_glace.py`) : les trois rangées d'eau les plus courtes entre la VRAIE rive
  est de l'île (sa boîte déborde sur l'eau : on recule d'abord jusqu'à la terre) et une terre qui mène à
  une route — 29 tuiles de long, de l'herbe de l'île au sable de La Pointe, la route à huit tuiles. LU sur
  la ville finie : la ville garde son eau (`test_eau`, `test_ile` le tiennent).
- **La glace** (`static/js/pont.js`) : le navigateur rend les tuiles du chemin praticables (`solide`,
  `route`, `passage` sauvés, comme la passerelle du traversier) et les rend à l'eau après, exactement. Un
  char y roule sans couler ; une coque s'y bute, et la baie ne prend pas tant qu'une coque est sur le
  chemin. Au dégel, un char arrêté plus de trois secondes fait craquer la glace sous lui (neuf tuiles) et
  coule ; après le froid, ce qui est resté dessus tombe à l'eau. Peinte : claire et rayée, fendue au
  dégel, une glace mince PEINTE de chaque côté (c'est de l'eau : on y coule — un chemin de glace sur une
  eau d'été ne faisait pas froid, vu à la capture), et des sapins de balise.
- **Le Clairon** : la veille, « GRAND FROID DEMAIN : LA BAIE VA PRENDRE… » ; le premier matin, « LE PONT
  DE GLACE EST OUVERT : SUIVEZ LES SAPINS… ».
- **Juges** : `test_calendrier.py`, `test_pont_de_glace.py` (de l'eau, de l'île à une route, la ville
  intacte, le froid en hiver) et `test_pont_de_glace_js.py` (la baie ne prend que les jours de grand froid
  avec la neige, rend toute son eau après et revient l'hiver suivant ; un char traverse sans couler ; une
  coque ne se fait pas prendre et ne passe pas ; au dégel un char arrêté passe au travers, pas avant ; le
  Clairon). Chaque juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : des **missions sur l'île par la route** (M16 : l'île n'a toujours aucun lieu de
  mission) ; la mini-carte ne montre pas le chemin ; pas de son de glace qui craque à lui (le choc).
