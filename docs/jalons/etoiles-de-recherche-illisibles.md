# Étoiles de recherche illisibles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les étoiles de recherche, grosses, jaunes et au centre (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « je veux les étoiles de police plus grosses, jaunes et au centre de
l'écran. »

⚠️ **Aujourd'hui, l'argent est dessiné deux fois plus gros que le niveau de recherche.** Les
étoiles sont du **texte** — des `★` de la police 5 × 7, à l'échelle **1** — rangés dans la
colonne du coin haut-droit, sous un montant en argent tracé à l'échelle **2**. La chose la
plus importante d'une poursuite est donc le plus petit élément de l'écran, dans un coin, en
blanc. C'est à l'envers.

- **Plus grosses** : pas en agrandissant le caractère. Un `★` de 5 × 7 tiré à l'échelle 3
  donne une bouillie de blocs. Une **étoile dessinée**, cuite comme les autres sprites depuis
  sa grille de caractères, se lit à n'importe quelle taille — et l'atlas sait déjà faire
  exactement ça.
- **Jaunes.** ⚠️ Avec une nuance à trancher : le doré `#e8b33c` est **déjà** celui de
  l'argent, juste au-dessus, et celui de « ce qui est à toi » sur la carte. Deux choses
  différentes de la même couleur dans le même coin, ça ne se lit plus. Soit les étoiles
  prennent un jaune à elles, soit elles déménagent — et justement, elles déménagent.
- **Au centre.** ⚠️ Pas au milieu de l'écran : le milieu, c'est le joueur, et une rangée
  d'étoiles par-dessus l'action cacherait ce qu'on regarde. **En haut, centré** — la place des
  étoiles dans le genre. Mais ce coin-là est déjà pris : `noter('objectif', …)` y écrit la
  ligne de mission. Les étoiles passent devant (en poursuite, c'est **l'information**), et la
  ligne d'objectif descend sous elles.
- **Les étoiles éteintes ne sont pas des points.** Le code écrit `'.'` pour celles qu'on n'a
  pas — ça se voyait à l'échelle 1, ça ne tiendra pas en gros. Il faut une étoile **creuse** :
  on doit lire « trois sur cinq » d'un coup d'œil, sans compter.
- **Le clignotement rouge reste**, et c'est lui qui dit qu'un palier vient de changer. En
  jaune, il doit rester aussi visible qu'en blanc — c'est le seul signal du passage à
  l'étoile suivante, et il ne se remplace pas par « c'est plus gros ».
- ⚠️ **Le tactile** : `noter()` enregistre chaque élément du HUD, et un test vérifie
  qu'aucun ne finit sous un bouton du pouce. Les étoiles qui déménagent réenregistrent leur
  ancre, sinon le juge tactile parle encore de l'ancien coin.
- **Juges** : les étoiles sont l'élément le plus grand du HUD en poursuite ; on distingue
  allumée d'éteinte sans compter ; rien du HUD ne se chevauche au centre (étoiles et ligne
  d'objectif) ; et aucune ancre ne tombe sous un bouton tactile.

## Notes

demande de Martin : plus grosses, jaunes, au centre.

- ⚠️ Ce sont des `★` de texte à l'échelle **1** dans un coin, sous un montant d'argent à
  l'échelle **2** — la chose la plus importante d'une poursuite est le plus petit élément de
  l'écran
