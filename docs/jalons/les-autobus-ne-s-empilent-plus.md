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

## Notes

- ⚠️ **On ne force jamais dans celui qu'on suit** (`Vehicules.suitUnChar`) : `obstacleDevant`
  retient ce qu'il a vu (`v.devant`) ; si c'est un char **conduit** qui va dans notre sens
  (cos > 0,7), la patience épuisée klaxonne au lieu de passer en `force`, et une `force` déjà
  lancée ne pousse plus dedans — pour le trafic comme pour l'autobus. Celui de devant a sa
  propre patience, c'est lui qui forcera. Ce qui se pousse encore : un char sans conducteur
  (garé, épave), un char d'en face ou en travers (les interblocages de boîte), un passant.
- Mesuré au banc, sur la 11e Rue devant la Cantine des Quais, une tête de file tenue sur
  place 16 000 images : **16 px** de chevauchement (deux autobus confondus, une vingtaine de
  paires enfoncées) avant, **2 px** après. Juge : `test_une_file_arretee_ne_se_tasse_pas_dans_celui_qu_elle_suit`
  (4 chars et 3 autobus sur un tronçon droit de 34 tuiles : 14 px avant, 0 après).
- ⚠️ **Le voleur dans la boîte** : `emporterLeChar` ne prend plus que les flèches de la tuile
  (`+` et `S` n'en sont pas) ; et la boîte relit le cap de tout char dont le sens n'est pas
  une flèche, d'où qu'il vienne. Juge : `test_un_voleur_qui_emporte_un_char_arrete_dans_un_carrefour_ne_fige_pas_la_ville`.
- La boucle redemande l'image AVANT `maj()` (`Jeu.boucle`) : une exception dans `maj` se
  répète à chaque image et fige l'écran sans rien dire. Aucune remontée d'erreur au serveur :
  on ne sait pas si l'écran de Martin était figé.
