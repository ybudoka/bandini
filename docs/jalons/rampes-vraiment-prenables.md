# Rampes vraiment prenables

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Une rampe qu'on peut vraiment prendre (**correctif**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « les défis de rampe doivent vraiment être réalisables, avec assez
d'élan et assez de place pour atterrir sans frapper un mur. »

Les rampes se mesurent maintenant avant d'être posées — `ELAN_RAMPE = 10` tuiles devant,
`RECEPTION_RAMPE = 6` derrière, et rien ne se pose sans les deux. ⚠️ **Mais ces deux nombres
sont choisis en tuiles, alors que la portée d'un saut est de la physique** : elle vaut
`vitesse² × 2 × impulsion / gravité`, donc elle est **quadratique en vitesse** et différente
pour chaque char. Le calcul, avec les constantes d'aujourd'hui :

| Char | Vitesse max | Portée du saut | Réception exigée |
|---|---|---|---|
| **Moto** | 5,2 | **126 px** (7,9 tuiles) | 96 px — **il en manque 30** |
| Auto-patrouille | 4,4 | 90 px | 96 px, juste |
| Berline | 4,0 | 75 px | ça va |
| Camion | 2,8 | 37 px | ça va |

⚠️ **Et la moto est justement le char du défi.** _Le Grand Saut_ exige `vehicule: "moto"` et
60 px de vol. Le seul char que le défi demande est le seul que la règle de placement ne sait
pas recevoir.

**Les deux hypothèses sont fausses en même temps, et en sens contraire** : l'élan est mesuré
comme si l'on partait d'un arrêt (dix tuiles suffisent alors à peine), et la réception comme
si l'on ne dépassait jamais cet élan — alors que le code encourage exactement le contraire,
et il a raison : « l'élan n'a pas à tenir dans le terrain : il continue dans la rue, on arrive
lancé au lieu de partir d'arrêt ».

**Trois longueurs, pas deux, et toutes les trois se calculent :**

1. **L'élan** = la distance qu'il faut pour atteindre la vitesse que le défi demande. Elle
   sort de l'accélération et de la friction de la fiche — Python les a déjà.
2. **La portée** = `vitesse² × 2 × impulsion / gravité`, plus la longueur du char.
3. ⚠️ **Le freinage**, qu'on oublie et qui est le vrai mur : atterrir à 5,2 px/image et
   s'arrêter demande encore **75 px**, cinq tuiles de plus. La réception n'est pas le point de
   chute, c'est le point de chute **plus de quoi s'arrêter**.

- **Donc `RECEPTION_RAMPE` cesse d'être un nombre écrit à la main** : `carte.py` le calcule
  depuis `vehicules.PHYSIQUE` et le catalogue, pour le char le plus rapide qui peut arriver
  là. Un réglage de physique change, la ville se replace toute seule — et un test vérifie que
  les deux restent d'accord.
- ⚠️ **En l'air, on survole les murs**, et c'est voulu : `bloqueParLesTuiles` rend faux
  au-dessus de `z > 6`. Ce qui doit être dégagé n'est donc pas tout le trajet, mais la **zone
  d'atterrissage** et ce qui la suit. Un saut par-dessus un mur est un bon saut ; un saut qui
  finit **dans** un mur est un défi qu'on ne peut pas gagner.
- **Juges** : pour chaque rampe posée, et pour chaque char capable d'y arriver, la chute **et**
  le freinage tombent sur du roulable — le test rejoue la trajectoire, il ne la devine pas ;
  la rampe du _Grand Saut_ est validée **pour la moto**, pas pour un char moyen ; et l'élan
  disponible permet vraiment d'atteindre les 60 px de vol exigés, en partant de la rue.

## Notes

demande de Martin : `ELAN` et `RECEPTION` sont des nombres de tuiles, alors que la portée
d'un saut est **quadratique en vitesse**. La moto vole **126 px** pour 96 px de réception
exigée — et c'est le char du _Grand Saut_. Il manque aussi le **freinage** (75 px de plus)
