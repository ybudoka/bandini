# Les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ quatre façades que la ville affiche déjà deviennent des endroits où l'on entre.

**Aujourd'hui** `app/devantures.py` peint `BINGO`, `SALLE DE QUILLES`, `LAVE-AUTO` et `CINÉMA RIALTO` sur des
façades — des enseignes sans pièce derrière. La ville promet, et on ne peut pas entrer : c'est presque un
mensonge (P4 tant qu'aucune porte ne l'invite).

- **Le bingo** : une pièce du sous-sol, une carte de bingo à l'écran, le narrateur qui crie les boules
  (« B-7! ») ; les madames te regardent de travers si tu gagnes. Tirage calculé, jamais `B.rng()`.
- **La salle de quilles** : un jeu d'adresse (viser, la force, l'effet), dix carreaux, un défi du rail.
- **Le lave-auto** : on y entre en char ; un char lavé est **moins reconnaissable** — la chaleur baisse d'un
  cran (moins fort que repeindre au garage, et moins cher).
- **Le Rialto** : un film le soir (un écran qui scintille, une salle sombre) ; une mission de filature dans la
  salle (`suivre` existe).

⚠️ **Ce qui guette** : quatre pièces de plus — des intérieurs (`carte.py`, `_piece`), posés sans déplacer
la ville ; chaque intérieur doit « donner quelque chose à faire » (le juge `test_une_piece_donne…`).

**Juges** : chacune des quatre a une porte et un point qui sert ; le bingo et les quilles ne tirent aucun
`B.rng()` ; un char lavé perd un cran de chaleur, une fois par passage.

## Notes

**Livré le 26 sept. 2026.** `app/enseignes.py`, `static/js/enseignes.js`, deux épreuves de plus dans
`adresse.js` (`quilles`, `bingo`), quatre comptoirs dans `magasins.COMPTOIRS` (`enseigne`), deux glyphes
(`[` l'allée de quilles, `]` la toile), le défi `quilles` ; juges `tests/test_enseignes.py` et
`tests/test_enseignes_js.py`. Les juges « ne déplace rien » du dojo et des carrosseries neutralisent les
enseignes des deux côtés (sans le dojo, le Rialto prenait sa porte) ; le plafond gzip de la carte passe
de 53 000 à 55 000 (mesures dans `test_definitions`).

- **Où elles ouvrent.** Sur la ville finie, sans dé, comme le dojo : chacune reprend la porte d'un commerce
  ordinaire (sa pièce redessinée, son enseigne repeinte, sa porte et son lieu renommés, un point au bout de
  la carte). ⚠️ La mesure du jour : **aucune** des trois autres enseignes n'était peinte dans la ville (le
  catalogue les propose, le tirage ne les avait pas posées) ; seul le BINGO l'était — deux fois, dont une
  porte, et c'est elle qui ouvre. ⚠️ **Le Faubourg n'a que deux portes de commerce** (le dojo en a pris une ;
  l'autre, la GALERIE D'ART, est la SEULE porte de sa famille « savoir » — un juge veut que chaque famille en
  garde une — et son plancher fait 5 × 4) : le Rialto et la salle de quilles sont à La Shop (des hangars ;
  « SALLE DE QUILLES » tient sur une façade de cinq tuiles, sinon elle s'écrit « QUILLES »), le lave-auto
  aux Érables. Le district est une préférence, pas une condition.
- **Les pièces sont à la mesure de leur bâtiment** (le juge `la pièce a les mesures de son bâtiment`) :
  chacune se dessine dans le plancher de la pièce qu'elle remplace, comme le dojo, avec un minimum
  (`MESURES_MIN` : un cinéma de 5 × 4 n'en est pas un). Le premier jet, quatre plans dessinés à la main,
  rougissait ce juge sur cinq graines.
- **Le bingo** : une carte à 3 $ au comptoir, gros lot 20 $. Une boule toutes les 3,2 s ; ACTION la marque
  pendant 2,6 s si elle est sur ta carte. Trois madames jouent sans rien rater, et crient à la FIN de la
  fenêtre — marquer à temps bat une madame à égalité. Carte et ordre des boules : un `mulberry` à la graine
  du jour et du numéro de la carte (`B.partie.bingos`). Joué comme une épreuve d'`Adresse` hors catalogue
  (l'épreuve porte maintenant sa fiche, `def`). ⚠️ Les boules ne sont pas **dites** : 75 voix
  (« B-7! ») n'ont pas été générées — le texte et le ding du micro seulement.
- **La salle de quilles** : la ligue du mardi, un défi du comptoir (comme la tire) — cinq carreaux, une
  boule chacun, 32 quilles pour gagner (prime 60 $), ouvert après trois défis (comme la tire : une partie
  neuve n'a que les dix défis de la v1). La visée part du dalot ; les quilles se calculent de
  l'écart au milieu et de la force. ⚠️ Le banc a trouvé un piège : la visée gardait sa valeur d'avant au
  carreau suivant, et une boule lancée à la première image partait avec — remise à zéro.
- **Le Rialto** : le maïs soufflé le jour ; le soir (18 h à 23 h 30), un billet de 5 $ assoit le joueur au
  milieu de la salle, qui s'éteint, et le film muet du ciné-parc joue sur la toile (`Cineparc.film`, sur
  deux tuiles de haut). 45 s de film, +20 PV en sortant. ⚠️ **La mission de filature dans la salle n'est
  pas faite** (le moteur `suivre` le permet ; il faut l'écrire, et ses voix).
- **Le lave-auto** : la baie est peinte sur les deux premières rangées de chaussée sous sa porte, sur trois
  tuiles (des brosses bleues qui tournent, un portique) ; rien n'y est solide. Au pas (sous 1,2) pendant
  1,5 s : 12 $, et une étoile de moins (`Police.unCranDeMoins` — la chaleur repart de zéro). Une fois par
  passage ; à pleine vitesse, on traverse sans être lavé. La pièce derrière la porte est le bureau (un
  café, une liqueur, et le prix du lavage).
- ⚠️ **Deux rouges de la suite complète, corrigés le soir même** : la clé du comptoir qui dit ce qu'il fait
  jouer s'appelait `jeu` — le mot du jeu d'acteur, qui ne part jamais au navigateur
  (`test_interpretation`) : elle s'appelle `joue`. Et la façade reprise GARDE sa famille (`genre`) : la
  distributrice adossée à côté vend selon elle (`magasins.sortes_devant`) — le Rialto repeint « nuit »
  avait une machine à café. Les brosses du lave-auto réclamaient un échantillon qui n'existe pas.
- Captures regardées : les quatre façades, les pièces, la partie de bingo, la ligue, le film, la baie.
