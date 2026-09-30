# Une revue des façades des résidences et des appartements

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (29 sept. 2026)_, dans la foulée de
[la revue des intérieurs](des-interieurs-fideles-a-l-exterieur.md#fiche) : « aussi une revue des façades de
résidences et appartements ».

**Pourquoi avec les intérieurs** : c'est la façade qui dit ce que l'intérieur doit être. Si deux maisons se
ressemblent dehors alors qu'elles sont l'une cossue et l'autre pauvre, aucun intérieur ne peut rattraper ça.
La revue des façades passe donc **devant** celle des intérieurs, ou au plus tard avec elle.

**Ce qui est dessiné aujourd'hui** (à vérifier par la revue) : chaque logement est une `residence` du paquet
(`carte.py` la pose, `FACADES.residence` la peint dans `sprites.js`), avec sa largeur, ses étages, ses
motifs (fenêtre, porte, porte peinte), son escalier, son balcon, son mur et son standing. Le standing change
déjà un peu le dessin : le fer rouille chez les pauvres, une jardinière fleurit chez les cossus, des planches
couvrent une fenêtre sur trois. Les genres de bâtiment : les plex du Faubourg et des quartiers (`maisons`), les
bungalows des Érables (`banlieue`, toits à deux versants), les logements du Petit-Canton, les maisons pauvres
de la gare, et les cabanes du bidonville (tuiles à part).

**La revue** :

- Un **inventaire** de toutes les façades d'habitation, par genre × standing × district, avec une capture de
  chacune.
- Pour chacune, trois questions :
  1. **Elle se lit** : on devine le standing, le quartier et le genre sans lire la carte.
  2. **Elle est variée** : pas une rangée de façades identiques (couleur de brique, portes, fenêtres, balcons,
     escaliers).
  3. **Elle est cohérente** : le nombre d'étages et de fenêtres, la porte et l'escalier correspondent à ce qu'on
     trouvera dedans ; ce que la façade promet, l'intérieur le tient.
- La liste des écarts, puis des corrections par vagues, chacune jouable, jugée et regardée.

- ⚠️ **Rien au dé** : ce qui change sur une façade se décide à ce qu'on lit (standing, district, genre, position
  par `empreinte_de_tuile`), sinon la ville glisse.
- ⚠️ **Se regarde avant de livrer** : une capture par genre ; les juges ne voient ni une rangée monotone ni un
  damier.
- ⚠️ **À préciser par Martin** : ce qui le gêne aujourd'hui dans les façades, s'il a quelque chose en tête (une
  rue, un genre de bâtiment, une capture).

## Notes

### L'inventaire (30 sept. 2026)

Martin : « l'inventaire d'abord, montré avant de corriger ». Mesuré sur la ville livrée (graine du jeu, 183
façades d'habitation `residences`), et un représentant capturé par quartier et par standing (la planche :
`captures/planche-facades-2026-09-30.png`, hors du dépôt).

| Quartier | Cossu | Ordinaire | Pauvre |
|---|---|---|---|
| Faubourg | 1 | 27 | 1 |
| Érables (bungalows) | 37 | 1 | — |
| Petit-Canton | 14 | 40 | 24 |
| Gare | — | — | 14 |
| Quais | — | 13 | — |
| La Pointe · La Shop | — | 4 | — |
| Île (maisons de pêcheur, bois à clin) | — | 7 | — |

Ce qu'une façade peut varier aujourd'hui : le mur (trois : brique rouge, brique jaune, bardeau gris), les étages
(1 à 3 — une rangée de fenêtres par étage au-dessus du rez), le balcon, le côté de l'escalier de fer, la place et le
genre de la porte ; et le standing (cossu : des jardinières fleuries ; pauvre : le fer rouillé, une fenêtre sur trois
placardée, une sur cinq tendue d'un drap ; ordinaire : rien).

### Les écarts, sur les trois questions de la fiche

1. **Le mur tiré ne se voit pas** (varier). `residence()` (`sprites.js`) ne peint jamais `m.brique` : la façade
   est la tuile de mur de la ville, en brique rouge partout. Deux maisons sur trois ont tiré la brique jaune (51)
   ou le bardeau gris (67), et n'en montrent que la couleur des cadres et de la porte. **Toute la ville est en
   brique rouge.**
2. **Une porte sur deux est condamnée** (se lire). 94 façades sur 183 (51 %) ont leur porte condamnée (`d`),
   dessinée avec deux planches clouées — **dont 33 des 52 maisons cossues** (63 %). Dans une rue riche, on lit
   une maison abandonnée.
3. **Le Petit-Canton n'a pas de maisons à lui** (se lire). Ses 78 façades sont les plex du Faubourg, trait pour
   trait : rien de ce qui fait le quartier (les lanternes, les enseignes bilingues, les balcons à linge, les
   couleurs) n'arrive jusqu'aux logements — il est dans les commerces et dans la rue seulement.
4. **Le bungalow est un plex d'un étage** (se lire). Les 37 maisons cossues des Érables portent la même rangée de
   brique rouge et les mêmes fenêtres que les plex : pas de revêtement de banlieue, pas de porte de garage, pas de
   perron.
5. **La même fenêtre partout** (varier). Deux fenêtres par tuile et par étage, toutes de la même taille, du
   bungalow au triplex : pas une fenêtre en saillie, pas une corniche ornée, pas une galerie — ce qui distingue un
   triplex de Montréal, c'est sa galerie et son escalier ; il a l'escalier, pas la galerie.
6. **L'ordinaire ne porte aucun signe** (se lire). Cossu et pauvre ont leurs détails ; l'ordinaire est le dessin
   nu. Le Faubourg, le centre, est ordinaire à 27 sur 29 : c'est le quartier le plus uniforme de la ville.
7. **Ce qui va bien** : les voisins identiques sont rares (1 paire sur 20 façades mitoyennes) ; le pauvre se lit
   (fer rouillé, planches, draps) ; les maisons de pêcheur de l'île ont leur bois à clin ; les escaliers et les
   balcons varient.

⚠️ **La troisième question** (ce que la façade promet, l'intérieur le tient) est à la revue des intérieurs, en
cours dans une autre session ([des intérieurs fidèles](des-interieurs-fideles-a-l-exterieur.md#fiche)) ; les
32 logements visitables (`D`) y passent.

**Rien n'est corrigé** : la liste attend le mot de Martin sur l'ordre des vagues.
