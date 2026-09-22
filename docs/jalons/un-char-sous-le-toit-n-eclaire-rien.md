# Un char sous le toit d'un garage n'éclaire rien

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026), capture à l'appui : un char entré dans une carrosserie, caché sous
le toit — et ses deux phares jaunes et ses deux feux arrière rouges brillent **par-dessus le toit et
l'enseigne**. « Corrige les feux… on devrait rien voir. »

Le toit découpe le DESSIN du char (`Entites.dessiner`, `Monde.rideauPres` : tout ce qui est au-dessus
du bas du rideau, dans le passage). Mais les lampes se composent à la fin de l'image, par-dessus
toute la scène (`Base.fin`) : la découpe ne les atteint pas.

- Ce qui est **sous le toit** ne s'allume pas à l'écran : ni les lueurs des phares et des feux
  arrière, ni le faisceau qui en partirait. Ce qui a passé le linteau (rideau levé, le nez dehors)
  éclaire, lui.
- ⚠️ La même règle que le dessin, lue au même endroit : une lampe cachée est une lampe dont le point
  est dans la zone que le dessin découpe.

## Notes

✅ **Livré** (22 sept. 2026).

- **La zone cachée vit à un seul endroit** : `Monde.sousLeToit(pg)` (les colonnes du passage, du fond
  de la baie au bas du rideau) et `Monde.cacheSousLeToit(pg, x, y)`. `Entites.dessiner` la découpe
  du dessin du char (le calcul qu'il faisait en ligne, repris tel quel) ; `Vehicules.allumerLesPhares`
  n'y pose ni lueur (une lampe dont le point dessiné y tombe) ni faisceau (celui dont le phare y est).
- **Reproduit avant de corriger** (capture Chromium, garage Bandini, 21 h 36) : deux lueurs blanches
  et deux rouges par-dessus le toit ; après, plus rien — le char droit, de biais, de jour et de nuit.
  ⚠️ La **tache sombre** entre les lueurs de la capture de Martin n'a pas été reproduite : de biais,
  rien du char ne dépasse du toit ; sans lampes, plus rien ne l'éclaire.
- **Juges** : `test_un_char_sous_le_toit_js.py` — dans la baie de CHAQUE garage, rideau baissé, trois
  caps : aucune lampe ; le même char dans la rue s'allume (le témoin) ; le nez dehors, rideau levé,
  les phares éclairent et les feux arrière restés dessous non. **Quatre mutations, toutes rouges.**
- ⚠️ **Quatorze juges sont rouges sur `dev`** à ce jour, à l'identique sur la base sans ce jalon ni
  celui des bêtes (`a438fb5`) : le paquet des définitions (270 403 octets pour 250 000), la foule et
  la course dans la foule, le poste tenu, le budget de la bagarre, les Cravates de M2, les repos dits
  à voix haute, trois scènes de mission (f04, p01, h02), l'hôpital sans rien à faire, un comptoir
  dessiné non servi, la balle dans la tôle, la voix de la police. Pas de ces jalons.
