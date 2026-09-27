# Les autobus ne s'empilent plus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (27 sept. 2026), capture à l'appui : devant la Cantine des Quais, sur la
11e Rue, les **quatre autobus de la ligne 2**, un camion, deux chars, tous enfoncés les uns
dans les autres, un autobus de travers sur le trottoir. Rejoué au banc : une file bloquée
derrière une tête qui ne bouge pas suffit.

- ⚠️ **Forcer le passage dans celui qu'on suit** : coincé plus de `patience_images` (le
  trafic) ou le double (l'autobus), un char passe en `force` et avance à 25 % **sans regarder
  devant**. Derrière un char lui-même arrêté, ça ne dégage rien : chaque char de la file force
  dans le précédent, la séparation (`heurterVehicules`) ne défait qu'un contact par char et
  par image, et la file se tasse jusqu'à 16 px de chevauchement (deux autobus confondus).
- ⚠️ **Un voleur qui emporte un char dans un carrefour plante le jeu** : `emporterLeChar`
  copie le glyphe de la tuile dans `v.sens`, soit `'+'` dans une boîte ; `cibleDeLaVoie`
  lit `PAS_FLECHE['+']` (indéfini) et lève une exception à chaque image. La boucle redemande
  l'image AVANT `maj()` : l'écran reste figé. Au banc, c'est l'autobus en `force` qui avait
  poussé le char garé jusque dans le carrefour.
