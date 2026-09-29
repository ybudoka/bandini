# Des statues dans les parcs

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (28 sept. 2026) : « ajoute des statues dans les parcs ». Une statue au
centre de la place de chaque parc de ville (`_parc`, pas le bois de La Pointe), posée à la
fin de `generer` sans dé ; trois modèles tirés à l'empreinte de la tuile ; numéros d'entité
à part (`horsSuite`) pour ne rien décaler ; une plaque qu'on lit à ACTION.

## Notes

✅ **Livré le 28 sept. 2026.**

- **Trois grandes statues**, une au coeur de la place de chaque parc de ville (`_Chantier._parc`, les
  glyphes `k` et `p` du plan) : Samuel-Ovide Brumaire, le fondateur, aux Érables ; le général
  Trudel-Laflamme sur sa jument Princesse, au Faubourg ; Gilles « La Toque » Bouchard, 1971, stick en
  l'air, à la Shop. Les deux vieux sont en vert-de-gris, avec un pigeon sur la tête ; La Toque est encore
  en bronze brun. Le bois de La Pointe (`sauvage`) n'en a pas.
- **Cinq bustes** dans les grands parcs de quartier (35 tuiles et plus, `statues.SURFACE_MIN_BUSTE`) :
  la mairesse Rose-Aimée Paradis, l'abbé Côté, l'inventeur Omer Gauthier. Un sentier de parc de quartier
  ne fait qu'une tuile de large : le buste se tient sur le gazon, au bord, à mi-chemin, et collé à rien
  (un buste adossé à un banc se lisait comme un meuble de plus, vu à la capture). Les grands parcs de
  quartier sont tous aux Érables.
- **La plaque se lit à ACTION** (`interactions.LIRE`, « LIRE LA PLAQUE »), une ligne par pression — le
  toast du HUD n'en tient qu'une —, et on recommence au bout. Ça ne rapporte rien, comme le chat.
- **Rien ne bouge** : `_parc` et `_parc_de_quartier` ne font que NOTER le centre de leur place et le
  milieu de leur sentier (`places_de_parc`, `sentiers_de_parc`) ; `statues.poser` les pose sur la ville
  finie, avant la bande nord, sans un dé (le modèle suit l'ordre des parcs). La ville sans elles est la
  même clé par clé (juge). Côté navigateur, leurs fiches portent `horsSuite` : `Entites.creerDecor` les
  numérote à part, et rien de ce qui naît après elles ne glisse d'un cran (juge, vu rouge sans).
- Les dessins sont des grilles (`PAL_STATUE`, `GRILLE_STATUE_*` dans `sprites.js`), regardés en jeu
  dans Chromium avant de livrer. Solides et `arrete` : on ne traverse pas le bronze, en char non plus.
- **29 sept. 2026 — la plaque reste plus longtemps** (Martin : « affiche plus longtemps les textes ») :
  une ligne reste sept secondes à l'écran (`LIRE["duree_images"]`, 200 → 420 images) ; la pression suivante
  la remplace aussitôt.
