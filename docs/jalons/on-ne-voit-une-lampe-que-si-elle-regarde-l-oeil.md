# On ne voit une lampe que si elle regarde l'œil

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026), deux captures à l'appui — un char qui monte l'écran et un qui le
descend, et les deux montrent leurs phares ET leurs feux arrière : « les phares devraient logiquement
être visibles ou non selon la direction (toutes les directions) ».

La ville se voit de trois quarts : on voit les faces tournées vers le bas de l'écran. Un char qui
monte montre son arrière — ses feux rouges ; ses phares sont sur la face d'en avant, cachés par la
caisse, et ce qu'on voit d'eux, c'est la flaque de lumière au sol devant lui. Un char qui descend,
l'inverse. De profil, ce qu'on devine du coin des lampes.

- La **lueur** d'une lampe ne s'allume que si la lampe SE VOIT à ce cap — et c'est la machine qui le
  sait déjà : sa projection décide point par point ce qui est caché (`Atlas.projeter`, le plus près
  de l'œil gagne). Une lampe se voit si son dessin, à ce cap, montre ses pixels de lampe ; sa lueur
  vaut ce qu'on en voit.
- Le **faisceau** au sol ne change pas : il éclaire la chaussée devant le char, qu'on voie le phare
  ou non.
- ⚠️ Toutes les directions : les 32 caps, pour chaque silhouette qui a des lampes.
