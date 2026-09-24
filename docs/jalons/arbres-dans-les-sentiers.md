# Arbres dans les sentiers

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des arbres plantés au milieu des sentiers (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « les arbres ne devraient pas être dans les sentiers. »

⚠️ **Et ce n'est pas qu'une question de vue : un arbre est SOLIDE.** `_parc()` trace ses
allées en baïonnette, puis sème ses arbres, ses bancs et ses buissons **sur tout le rectangle
du parc**, au hasard. `poser_decor()` refuse ce qui est solide, routier, occupé ou réservé —
mais une allée est du pavé `.` (ou de la terre battue `s`) : marchable, pas routière. Rien ne
la protège. Un arbre tombe donc dans l'allée, et comme il a un rayon de 5 px et qu'une allée
fait deux tuiles, il la bouche à moitié. **Un sentier barré par ses propres arbres est pire
qu'un parc sans sentier** : on l'a dessiné pour dire « passe par ici ».

**Le mécanisme du remède existe déjà** : `self.reserve` — les tuiles qu'on garde libres, dont
`poser_decor` ne veut pas. C'est ce qui tient le devant des portes depuis M1. Il suffit
qu'une allée **se réserve en se traçant**.

- ⚠️ Ça vaut pour **tout ce qui se pose après** : les bancs et les buissons tombent dans les
  allées par le même chemin, et le banc est solide lui aussi. La réserve les règle tous d'un
  coup — c'est pour ça qu'on corrige là plutôt que dans le tirage des arbres.
- ⚠️ Et ça vaut pour **le sentier de banlieue** que la fiche des terrains prévoit : de la
  porte à la rue, réservé, sinon on y replantera un arbre le jour où on le dessinera.
- Un banc **à côté** d'une allée, en revanche, est exactement ce qu'on veut : la réserve
  couvre l'allée, pas ses bords.
- **Juges** : aucun décor solide sur une tuile d'allée, dans aucun parc, sur cinq graines ;
  et de l'entrée d'un parc jusqu'à son cœur, le chemin reste franchissable à pied sans
  contourner un tronc.

## Notes

demande de Martin : `_parc()` sème arbres, bancs et buissons sur tout le rectangle, et une
allée n'est ni solide ni routière — rien ne la protège. Or un arbre est **solide** : il
barre le sentier qu'on a dessiné pour y passer
