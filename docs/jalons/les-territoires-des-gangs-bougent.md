# Les territoires des gangs bougent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ la carte des gangs vit — quand tu affaiblis un gang, son voisin grignote son
territoire, et une mission peut le renverser.

**Aujourd'hui** chaque gang a sa zone fixe (`pietons.GANGS`, `carte.zones`), et M16 prévoit `libere` (un
district libéré : le gang devient des passants) et `calme` (l'hostilité tombe). Rien ne bouge entre les
deux.

- **La force d'un gang** : un nombre par gang, dans la partie. Coucher ses membres la fait baisser, le temps
  la fait remonter lentement.
- **La frontière** : chaque nuit, un gang plus fort que son voisin lui prend un coin de rue (un bloc de la
  zone) ; les couleurs de la carte et les graffitis suivent (les devantures et graffitis existent).
- **Les missions** : « reprendre le coin » (un `tuer` sur le bloc disputé) rend le coin à qui tu veux.
- **Le lien avec `libere`** : un district libéré sort du jeu ; ses voisins ne peuvent plus le grignoter.

⚠️ **Ce qui guette** : les zones servent partout (piétons, hostilité, missions `zone:`) — une zone qui
bouge doit rester un **calcul** (la force + le jour), jamais une simulation qui dérive ; et la ligne « La
réputation et la lecture des passants » touche au même sujet : à trancher ensemble.

**Juges** : un gang qu'on affaiblit perd un coin la nuit suivante ; le coin repris change de couleur et de
piétons ; une zone `libere` ne bouge plus ; tout survit à une sauvegarde.

## Notes

_Rien de livré._
