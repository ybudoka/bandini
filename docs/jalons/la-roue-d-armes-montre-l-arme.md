# La roue d'armes montre l'arme

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Un panneau à droite de la roue, pour l'arme sous le pouce : un portrait pixel 48×24 par arme
(affiché ×2, il pâlit à sec), trois barres avec leurs chiffres (dégâts, portée en mètres,
cadence en coups par seconde), les munitions et le bruit, des étiquettes (automatique, en
cloche, explose, brûle, assomme…) et un descriptif de trois lignes au plus. Les descriptifs
et les portraits vivent dans le JS : le paquet des définitions n'a plus de marge, et Python
ne les lit jamais. Juges : chaque arme du catalogue a son portrait et son descriptif, le
descriptif tient, le panneau reste dans l'écran ; capture Chromium avant de livrer.

## Notes

**Livré le 30 sept. 2026.** Martin : « avec la roue de sélection des armes, je veux une image en
plus gros des armes et des statistiques de l'arme, avec un petit descriptif ». Trois maquettes
montrées (panneau à droite en barres, à gauche, à droite chiffré) ; retenue : la chiffrée, **sans
le prix ni les étoiles**.

- **Le portrait** : `PORTRAITS` dans `sprites.js`, un dessin 48×24 par SLUG (la carabine à bouchon
  a le sien), fait de formes cernées de noir et de détails posés dessus (`peindrePortrait`).
  Affiché au double ; il pâlit à sec comme l'icône de son créneau. L'icône de `OBJETS` agrandie
  n'était pas une option : à seize pixels, le pistolet et le couteau sont deux rectangles.
- **Les chiffres** (`Hud.ficheDArme`) sont ceux du jeu : dégâts d'un coup (plombs compris,
  « 12×6 » — un glyphe `×` ajouté à la police), portée et bruit en mètres (une tuile), cadence en
  coups par seconde. Les barres se mesurent au meilleur du catalogue, sans la carabine à bouchon ;
  la cadence sans l'extincteur (un jet par image) ; les dégâts en racine, sans quoi la grenade
  écrase toutes les armes de poing à un trait. Munitions du sac, ou « SE CASSE DANS N COUPS »
  lu sur l'usure de l'arme qu'on a ; « SANS BRUIT » ou le rayon où un agent entend le coup (celui
  de l'explosion pour ce qui se lance).
- **Les étiquettes** : ce que les chiffres ne disent pas (automatique, plombs, en cloche, explose,
  rebondit, brûle, fait saigner, renverse, assomme, éteint le feu, inoffensive).
- **Le descriptif** vit dans `hud.js` (`DESCRIPTIFS_ARMES`), pas dans `app/armes.py` : Python ne le
  lit jamais, et le paquet des définitions n'avait plus qu'une centaine d'octets gzip de marge.
- ⚠️ **Au doigt, la roue glisse à gauche** (`centreDeLaRoue`) et le panneau finit avant les
  pastilles : au téléphone en paysage, SAISIR, ACTION et SPRINT couvrent le canevas dès x 415 et
  mangeaient les chiffres et le descriptif (vu à la capture). Au pouce, seule la direction choisit.
- ⚠️ La police pixel n'a pas de `;` : il se peignait en `?` dans le descriptif de la grenade. Un
  juge vérifie maintenant chaque lettre des descriptifs.

Juges (`tests/test_roue_js.py`) : chaque arme du catalogue a son portrait (un dessin à lui, dans
son cadre) et son descriptif (trois lignes au plus, lettres connues de la police) ; les chiffres
de la carabine, du fusil, de la mitraillette, des poings et de la pelle usée ; le panneau dans
l'écran, à droite de la roue, et au doigt avant les pastilles ; le portrait au double qui pâlit à
sec. Chacun a rougi à sa mutation.
