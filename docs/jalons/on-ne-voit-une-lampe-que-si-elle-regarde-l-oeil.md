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

## Notes

✅ **Livré** (22 sept. 2026).

- **La projection savait déjà** : `Atlas.projeter` décide point par point ce qui se voit (le plus
  près de l'œil gagne). Une auto qui monte l'écran garde 24 pixels de feux arrière et aucun de
  phare ; qui descend, l'inverse ; de profil, un peu des deux. `Atlas.grilleDuCap` (la grille que
  `cuireCap` peint, en cache) et `Atlas.ouTombe` (où tombe un point de la machine, le calcul de
  `projeter` au pixel près) donnent ça aux phares.
- **Une lueur vaut ce qu'on voit de sa lampe** (`partsVisibles`) : chaque pixel de lampe gardé
  revient à la lampe de sa sorte la PLUS PROCHE, dans le rayon de sa lueur — deux pixels, elle luit
  à plein ; un, à moitié ; aucun, elle est éteinte à l'écran. ⚠️ Premier jet : les pixels dans un
  carré de trois autour du CENTRE de la lampe — un bout de lampe peint plus loin restait sans lueur,
  et le juge de l'autre session (« chaque lampe peinte a sa lueur ») l'a vu.
- **Et selon où elle pointe** : pleine quand elle nous regarde, à 40 % de profil
  (`LUEUR_DE_PROFIL`). Sans ça, de profil, la projection gardait assez de pixels pour une lueur
  pleine — le juge l'a montré (1,10 de profil comme de face).
- **Le faisceau au sol ne change pas** : il éclaire devant le char, qu'on voie le phare ou non.
- ⚠️ **Deux juges d'autres jalons ajustés à la règle** : les phares qui montent quand le char saute
  se mesurent sur un char qui DESCEND (qui monte n'en a pas de lueur) ; « chaque lampe peinte a sa
  lueur » compte au plus grand des huit caps et non au dernier (sa docstring disait déjà « à un cap
  au moins »). Et mon témoin du toit (le char dans la rue, qui descend) n'exige plus que ses phares.
- **Juges** : `test_lampes_selon_la_direction_js.py` (auto et camion : qui monte montre ses feux
  arrière et cache ses phares, qui descend l'inverse, le faisceau reste ; de profil, les deux, plus
  faibles que de face ou de dos). **Quatre mutations, toutes rouges.**
- **Regardé dans Chromium** : l'auto et le camion sous les huit caps, la nuit.
