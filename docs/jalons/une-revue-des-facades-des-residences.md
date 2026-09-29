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
