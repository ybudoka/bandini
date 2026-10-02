# Les corps couchés à l'image des debout

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (2 oct. 2026) : « améliore les glyphes des personnes mortes ou tombées,
elles ne sont pas équivalentes au personnage debout ». La planche (debout contre couché, à
l'ancre) : le gabarit couché commun fait 12 px de long contre 16 debout, et il perd la tenue
— la robe, la salopette, le short, les bottes, la coiffure, la barbe, les lunettes, la
carrure du costaud ou du grand ; l'enfant n'en a pas du tout. Ce qu'on fait : la pose
`couche` ne se dessine plus à la main, elle se CUIT depuis la pose debout de face, habillée,
tournée d'un quart de tour (la tête à droite), les yeux fermés — pour la garde-robe comme
pour les dessins à la main, qui gardent ce qui les nomme debout (les balles, les échasses,
la pancarte). Même longueur que debout, même tenue.

## Notes

✅ **Livré** (2 oct. 2026).

- **La planche d'abord** (debout de face, de profil, couché, à l'ancre, ×7 ; un script Playwright du
  scratchpad) : neuf tenues de la garde-robe choisies pour leurs pièces (robe, jupe, salopette, short,
  bottes, crête, barbe, casque, feutre, enfant) et les dix-neuf dessins à la main. Elle a montré le
  gabarit de 12 px, la tenue perdue, l'enfant sans pose couchée (il serait mort debout), puis — avec un
  prototype qui tournait simplement le canevas debout — que le quart de tour se lit.
- **`Atlas.coucher`** : la grille `bas` tournée (la tête à droite), les yeux fermés — les `o` **seuls**
  de la première rangée qui en a deviennent `k` : plus bas, un `o` est la chemise de l'avocat, et le fard
  du mime est tout en `o`. **`Atlas.ancreCouchee`** : le corps est centré sur ses pieds et repose juste
  au-dessus, comme l'ancien. La pose `couche` est un getter paresseux (`Atlas.cuire`, `Garderobe.cuire`)
  avec **son ancre** (`cuit.ancres.couche`) : sa grille n'a pas la forme de la debout. `imageDe` la lit.
- **La garde-robe** : `grille(tn, 'couche')` habille la pose debout de face, sans le chapeau, qui
  **roule** à plat à côté de la tête (un pixel d'air, deux colonnes de côté) ; la capuche reste. Ce
  qu'il faut de rangées au chapeau s'ajoute au-dessus de la tête debout : couché, à droite, l'ancre ne
  bouge pas.
- **Les dessins à la main** perdent leur pose `couche` (19 grilles retirées, dont celle du joueur) : à
  terre, ils sont leur corps debout — les balles du jongleur, les échasses (26 px), la pancarte de
  l'homme-sandwich, la mascotte entière. Ce que l'ancien dessin faisait **tomber à côté** (les lettres du
  facteur, la bouteille de l'ivrogne, le seau du laveur) ne tombe plus : ils le portent. La conductrice
  l'hiver garde sa tuque, tricotée dans le dessin.
- **Juges** : `test_corps_qui_tombent_js.py` — chaque passant du catalogue, couché, est sa grille debout
  tournée, pixel pour pixel, sauf deux yeux fermés ; centré sur ses pieds ; `coucher` sur des grilles
  écrites à la main. `test_garderobe_js.py` : le chapeau tombe à côté de la tête sans la toucher.
  `test_decapotable_l_hiver_js.py` : la conductrice couchée l'hiver a sa tuque. **Cinq mutations, toutes
  rouges** (l'ancre propre, les yeux, la tenue, le chapeau resté sur la tête, les `o` collés fermés).
