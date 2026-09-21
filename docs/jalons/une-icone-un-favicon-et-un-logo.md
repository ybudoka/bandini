# Une icône, un favicon et un logo

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « fait moi un favicon et icone pour webapp », puis « et un beau logo en
pixel art pour l'accueil ».

- ⚠️ **Mesuré avant** : un seul `favicon.svg` 16 × 16 — qu'iOS ne lit pas (il colle une
  capture floue sur l'écran d'accueil), aucun manifeste, et `/favicon.ico` que tout
  navigateur demande tombait sur la page « Cul-de-sac ». **Livré** : tout se dessine en code
  dans `scripts/icones.py`, comme les sprites, **sans rien installer** (il écrit lui-même
  ses PNG et son .ico). **L'icône** (24 × 24) : Bandini — **le sprite du jeu recopié tel
  quel**, `SPRITES.joueur` pose `bas` — debout devant une lune d'or et la ville la nuit,
  fenêtres allumées ; en 180 (`apple-touch-icon`), 192 et 512. **Le favicon** (16 × 16) : la
  même lune, Bandini sur toute la hauteur, en SVG et en `.ico` 16/32/48 servi à la racine.
  **Le manifeste** : une route (`/manifest.webmanifest`, `no-cache`) et pas un fichier de
  `static/` — le nom et la devise viennent de la config, et nginx garde `/static/` sept
  jours. **Le logo** : « BANDINI » en lettres penchées, l'or « chrome » des titres d'arcade
  (clair, un trait blanc à l'horizon, plus sombre dessous), contour brun, ombre portée, un
  éclat sur le dernier I ; il remplace le `<h1>` en texte **à la même hauteur**
  (`clamp(34px, 8vw, 72px)`), `alt="Bandini"`.
- ⚠️ **La 512 sert aussi de « maskable »** : Bandini tient entier dans le cercle de 80 %
  qu'Android découpe — un juge le vérifie pixel par pixel.
- ⚠️ **`--verifier` compare les PIXELS, pas les octets** : deux zlib (macOS, la CI) ne
  compriment pas pareil la même image.
- ⚠️ Mesuré au passage, **pas causé ici** : sur un téléphone **debout** (390 × 844), l'écran
  fait 320 × 180 et l'accueil déborde par le haut — le titre en texte était coupé exactement
  pareil (mêmes boîtes avant et après). Juges : `tests/test_icones.py` (les fichiers sont
  ceux que le script dessine, Bandini est encore celui de `sprites.js`, le masque, le
  manifeste et ses tailles, les liens de la page, le logo dans le `<h1>`).
