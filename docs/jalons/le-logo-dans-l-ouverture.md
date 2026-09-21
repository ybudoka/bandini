# Le logo dans l'ouverture

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « les nouveau logo d'intro n'a pas été placé après l'animation d'intro ».
Le logo n'était que sur l'accueil (le `<h1>`) : le titre qui monte quand le car repart
s'écrivait encore « BANDINI » en police du HUD (`Hud.dessinerOuverture`). **Livré** :
l'ouverture dessine **la même image** que l'accueil — l'élément `#voile-titre .logo` que la
page a déjà chargé, pas une seconde copie du dessin qui divergerait à la première retouche
de `scripts/icones.py` — à **×3** (`Hud.LOGO_ECHELLE`) : un multiple entier, le logo garde
le grain de la ville derrière. La bande sombre s'élargit (50 à 118) pour tenir le logo et
« BAIE-DES-BRUMES », qui reste en lettres dessous.

- ⚠️ **Le repli en lettres reste** tant que l'image n'a pas fini de charger, et au banc
  Node, qui n'a pas de page : une ouverture sans nom de jeu serait pire. Juge :
  `test_le_titre_de_l_ouverture_est_le_logo` (navigateur) lit les **pixels** de l'écran —
  l'éclat blanc du dernier I et l'or du haut du B ; logo retiré, il lit le gris de la rue.
