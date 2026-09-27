# Le cinéma : maïs éclaté, films de combat et grand écran

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (27 sept. 2026) : « je veux du maïs éclaté et aussi des films de combat », « agrandis
l'écran du Rialto ». Le « Maïs soufflé » devient « Maïs éclaté » (le mot d'ici), aux deux
comptoirs. Le film unique (la poursuite, `Cineparc.film`) devient une programmation de trois
films, un par soir, choisi par le jour (le même aux deux cinémas, sans dé) : Pas de freins
(la poursuite), Le Poing de la Baie (deux karatékas dans un dojo, coups de pied sautés, POW,
l'un vole hors de l'image, l'autre salue), Le Kid des Brumes (la boxe : un ring, des
crochets, un K.-O., l'arbitre qui compte). Le billet du Rialto dit le titre ; au ciné-parc,
« CE SOIR : … » en arrivant pendant la séance. La toile du Rialto s'agrandit : toute la
largeur de la salle, une rangée de plus en hauteur.

## Notes

_Livré le 27 sept. 2026._

- **Le maïs éclaté** : « Maïs soufflé » devient « Maïs éclaté » aux deux comptoirs (`magasins._CINEMA`) ; même
  prix, mêmes effets.
- **La programmation** (`Cineparc.programme`, `Cineparc.FILMS`) : trois films, un par soir, choisi par le jour de
  la séance — après minuit, c'est encore la veille, le film ne change pas en pleine projection. Le Rialto et le
  ciné-parc passent le même film le même soir. `Cineparc.film` peint le grain et les rayures, et le film de ce
  soir entre les deux, découpé à la toile (`clip`).
  - **Pas de freins** : la poursuite d'avant, telle quelle.
  - **Le Poing de la Baie** : un dojo (le mur, la bannière et son idéogramme au premier tiers, le plancher en
    lattes) ; deux karatékas, gi blanc et gi noir, en garde, les échanges de poings, le coup de pied sauté, POW,
    le noir vole hors de l'image, le blanc salue ; carton FIN.
  - **Le Kid des Brumes** : un ring (la foule dans le noir, le tapis, les poteaux, trois câbles) ; les jabs, le
    crochet, POW, l'autre tombe au tapis, l'arbitre rayé compte un doigt par seconde jusqu'à dix, le Kid lève le
    gant ; carton FIN.
  - Les combattants (`combattant`) sont des blocs de `s` pixels, `s` à la mesure de la toile (3 au ciné-parc, 2 au
    Rialto) ; une bobine de 600 images qui boucle. Ni dé ni état.
- **Le titre du soir** : le billet du Rialto dit « UN BILLET — LE POING DE LA BAIE » ; au ciné-parc, « CE SOIR : … »
  quand on arrive pendant la séance (avec les spectateurs). Le juge « un comptoir reste ouvert » reconnaît le
  billet à son début.
- **Le grand écran du Rialto** (`enseignes.piece_de_rialto`) : la toile prend toute la largeur de la salle, sur
  les deux premières rangées (la seconde était un couloir vide devant les fauteuils), plus la rangée de mur du
  haut où le navigateur la peint — trois tuiles de haut au lieu de deux, `toile.h` lu par `Enseignes`. Le
  faisceau suit.
- **Juges** : trois soirs, trois films, le même après minuit, l'affiche du soir ; toute la bobine de chaque film
  sans un `B.rng()`, deux films jamais la même image, POW et FIN dans les deux combats ; le billet porte le titre ;
  la toile du Rialto sur toute la largeur et deux rangées, à trois tailles de salle ; le faisceau du Rialto part
  du mur du fond jusqu'au bas de la grande toile ; le menu dit MAÏS ÉCLATÉ. Onze mutations, onze rouges (une
  première mutation de l'affiche cassait la syntaxe : refaite). Regardé dans Chromium : les deux films au
  ciné-parc et au Rialto — les combattants grossis (`h / 20`) et la bannière déplacée après la première capture.
- ⚠️ En haut du ciné-parc, le HUD (étoiles, carte) recouvre le haut de la toile quand la caméra est collée au
  bord nord du bloc — c'était déjà le cas avec la poursuite.
