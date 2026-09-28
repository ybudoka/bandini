# La calèche : sa pancarte dans l'axe, des virages de vrai véhicule

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 28 sept. 2026 : « la pancarte est pas alignée au chemin et je veux que les virages
soient mieux, comme un vrai véhicule ». La pancarte à l'arrêt, dans l'axe du sentier ; le
sentier arrondi aux coins, les chevaux tournent d'abord et la caisse suit au bout du timon,
avec des caps en diagonale.

## Notes

**Livré le 28 sept. 2026.**

- **La pancarte** (`Cabane.pancarte`) : son poteau de GAUCHE est planté dans la tuile `pancarte` du rang
  (`app/blocs/rang.py`), l'écriteau s'étend vers l'est. Centrée sur sa tuile, elle débordait d'une
  demi-largeur et son poteau tombait dans le passage qui descend de la cabane (colonnes 61-62). Les deux
  poteaux sont dans l'herbe, les pieds au bord du sentier ; les deux qui attendent la calèche reculent
  d'une case (66 et 67) pour ne pas se tenir derrière.
- **Le sentier arrondi** : `construireChemin` coupe chaque coin d'un arc de `RAYON` (40 px), un point tous
  les deux pixels. La boucle raccourcit un peu ; l'arrêt, au milieu d'un tronçon droit, ne bouge pas.
- **La caisse tirée** : ses deux essieux (`ESSIEUX`, 12 px de part et d'autre) roulent sur le sentier, et
  son cap va de l'un à l'autre (`tire`) — les chevaux entrent dans la courbe, la caisse pivote après eux et
  coupe un peu le virage, comme une voiture attelée. Les chevaux de même, d'un bout à l'autre de leur
  longueur. Rien d'autre ne change : sans un dé, sans état (on peut poser `etat.s` n'importe où).
- **En volume, à 32 caps** (`CABANE_EN_VOLUME` dans `sprites.js`, comme le petit train de la foire) : la
  caisse — roues de bois aux rayons qui tournent (deux phases), ridelles rouges et filet doré, trois bancs,
  le siège haut du cocher — et l'attelage — un bai et un alezan côte à côte, avec un jour entre eux (collés,
  ils se lisaient comme une seule bête), la tête longue et sa liste blanche, le harnais, les traits vers la
  caisse, le trot sur quatre images et l'arrêt. Les gens assis sont des passants posés sur les `bancs` par
  `Vehicules.imageDuCavalier`, un peu plus haut que dans un char ; le joueur à la première place, le cocher
  à son siège. Les dessins à la main (profil, dos, face) sont retirés.
- **Juges** (`tests/test_cabane_pour_vrai_js.py`) : `test_la_pancarte_a_ses_poteaux_dans_l_herbe…` (rougit
  quand la pancarte est recentrée sur sa tuile), `test_la_caleche_tourne_comme_un_vrai_vehicule` (aucun saut
  de plus d'un cran de cap d'une image à l'autre, les chevaux d'abord, jamais en travers ; rougit sur l'ancien
  comportement, sentier à angle droit et caisse sans essieux : 8 crans d'un coup). Le juge du trot lit
  maintenant les images peintes (une par pas) au lieu des sabots peints à la main.
