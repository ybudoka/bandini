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

_Rien de livré._
