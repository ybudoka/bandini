# Les petits manèges à l'échelle de la grande roue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, captures à l'appui : « grossis ça pour que ce soit proportionnel avec les
autres manèges ». ⚠️ **Mesuré** : le carrousel (34 × 30 px), les tasses (30 × 26) et les
chaises volantes (34 × 34) avaient la taille d'un kiosque à limonade, posés entre la grande
roue (84 × 92) et la montagne russe. **Redessinés au double** (`sprites.js`) : le carrousel
**60 × 58** (toit rayé à frange d'ampoules, huit chevaux qui montent et descendent, fût à
miroirs), les tasses **58 × 40** (six tasses et deux têtes dans chacune, le sucrier au
milieu), les chaises volantes **72 × 70** (douze nacelles occupées sous un parasol à
frange). Chaque boucle d'animation retombe sur ses couleurs : elle ne saute pas.

- ⚠️ `r` reste à 14 — les balles et les chars ne cherchent le décor qu'à 24 et `c.r + 14`
  px. C'est la **boîte `sol`** qui suit le plancher (26 × 8 de demi-boîte pour le
  carrousel), et `PORTEE_DECOR` passe de **24 à 30** (`entites.js`) pour la couvrir :
  `test_la_portee_de_recherche_couvre_la_plus_grosse_empreinte` rougit à 24.
- **Rien ne bouge dans la ville** : les manèges gardent leurs tuiles et leur pas de 7
  tuiles. Vu en capture (Playwright, rang nord et coin sud-ouest) : les chaises volantes
  tiennent entre la montagne russe et les kiosques, et le carrousel du coin sud-ouest laisse
  encore 2 px au wagon du petit train.
- Juge neuf : `test_les_manèges_sont_a_l_echelle_de_la_grande_roue` (`test_foire.py` — 65 %
  de la largeur de la roue, 70 % de sa hauteur pour les chaises volantes, et une boîte au
  sol qui couvre le plancher), rouge sur l'ancien dessin.
