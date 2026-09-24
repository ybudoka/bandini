# Un saut qu'on ne voit pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Un saut qu'on ne voit pas (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Bug signalé par Martin :_ « les rampes n'ont pas l'air de fonctionner, et s'il marche, il
faut qu'on voie une ombre pour bien imager le saut. »

⚠️ **Elles fonctionnent. Le saut mesure sept pixels et dure un tiers de seconde.** C'est pour
ça qu'il n'a pas l'air d'exister : `vz` vaut `vitesse × 0,42`, la gravité vaut 0,18, et la
hauteur d'un saut est donc `vz² / 2g` :

| Char | Vitesse max | Hauteur du saut | Durée |
|---|---|---|---|
| Berline | 4,0 | **7,8 px** | 0,31 s |
| Moto | 5,2 | **13,2 px** | 0,40 s |
| Auto-patrouille | 4,4 | 9,5 px | 0,34 s |
| Camion | 2,8 | 3,8 px | 0,22 s |
| **Vélo** | 2,0 | **2,0 px** | 0,16 s |

**Une tuile fait 16 px et un char est dessiné 32 × 16.** Un char qui monte de sept pixels
pendant un tiers de seconde, ce n'est pas un saut : c'est une bosse. Le joueur passe sur le
tremplin, entend le moteur, et ne voit rien — il en conclut, raisonnablement, que la rampe ne
marche pas.

- **Il faut que ça décolle pour de vrai.** L'impulsion et la gravité sont deux nombres dans
  `PHYSIQUE`, et ils se règlent ensemble : on veut un char qui monte assez haut pour passer
  **par-dessus quelque chose** et qui reste en l'air assez longtemps pour qu'on le voie
  partir. ⚠️ Et ça se règle **avec** la fiche de la réception : plus le saut est haut, plus il
  est long, et plus il faut de place pour retomber. Les deux se décident ensemble ou pas du
  tout.
- ⚠️ **Le vélo ne devrait pas sauter.** À 2 px/image il monte de deux pixels — moins que
  l'épaisseur de son ombre. Un vélo qui « saute » sans que rien ne bouge est pire qu'un vélo
  qui refuse la rampe. Soit il passe le seuil, soit il ne le passe pas ; à deux pixels, il ne
  le passe pas.

**L'ombre existe déjà, et elle ne dit rien.** `dessinerUn()` pose un rectangle noir de
**20 × 10 px, fixe**, dès que `z > 2` :

- elle a **la même taille pour tout le monde** — l'autobus fait 48 px de long et projette la
  même tache qu'une moto ;
- elle ne **bouge pas avec la hauteur** : elle ne rétrécit pas, ne s'écarte pas, ne pâlit pas.
  Or c'est exactement ça qui dit « il est haut » — une ombre qui reste collée sous le char ne
  raconte aucune altitude ;
- elle est **rectangulaire et non orientée**, alors que le char tourne sur 32 caps.

Ce qu'il faut : une ombre **à la taille du char**, qui **s'éloigne** et **rétrécit** à mesure
qu'il monte, et qui s'éclaircit avec l'altitude. Le jeu sait déjà faire ça — l'hélicoptère de
M7 a son ombre au sol depuis le premier jour.

- **Juges** : la hauteur d'un saut se voit (elle dépasse la hauteur d'un char dessiné) ; un
  vélo ne décolle jamais ; l'ombre existe pendant **tout** le vol, pas seulement au-dessus
  d'un seuil ; sa taille suit celle du char ; et la hauteur du saut reste cohérente avec la
  réception exigée par le générateur — le même calcul, une seule fois.

## Notes

bug de Martin (« les rampes n'ont pas l'air de fonctionner »).

- ⚠️ Elles fonctionnent : le saut mesure **7,8 px** pour une berline (2,0 px pour un vélo)
  et dure **0,3 s**, sur des tuiles de 16 px. Et l'ombre est un rectangle **fixe** de 20 ×
  10 qui ne rétrécit ni ne s'éloigne — elle ne raconte aucune hauteur
