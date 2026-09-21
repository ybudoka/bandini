# Des chars arrondis

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « arrondit un peu (léger) les véhicules ». La berline en volume était
une boîte à angles vifs, de profil comme vue d'en haut ; les chars encore dessinés à la main
ont déjà le nez et la queue pincés. **Livré, sur la berline (l'auto, le taxi, la police)**,
en deux gestes légers dans `Atlas.projeter` : ⚠️ **le plan de la caisse se pince** au nez et
à la queue (`profil` accepte un PLAN `[[u, demi-largeur], ...]` au lieu de `[w0, w1]` : 7 px
de demi-largeur au milieu, 5,6 au bout — pare-chocs, ceinture et livrée suivent), et **un
pixel de moins à chaque coin vif** de la silhouette (`arrondi`), avant le contour.

- ⚠️ **Pas à chaque marche d'escalier** : un bord en diagonale est fait de coins, et les
  ronger amincissait tout char de trois quarts — on ne retire un coin que si ses deux bords
  continuent tout droit au-delà de lui, jugé sur la silhouette d'avant pour qu'un coin rogné
  n'en fasse pas naître un autre.
- ⚠️ **Les phares ont grossi d'un rien** : la caisse pincée les rognait, et phare et feu ne
  se voyaient plus ensemble qu'à 22 caps sur 32 (le juge des lampes l'a dit) ; 26
  maintenant. 1 juge neuf, **rouge avant sur ses deux règles** (sans arrondi : « 72 coins
  vifs sur les 32 caps » ; caisse carrée : « son bout ne rentre que de 5 sur une caisse de
  16 »).
- ⚠️ La première mesure du pincement (la seule rangée du bout) ne mordait pas — le coin
  rogné suffisait à la passer —, d'où les trois rangées. 2230 tests
