# Clôtures nord-sud couchées

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les clôtures nord-sud sont couchées (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Bug signalé par Martin :_ « les clôtures qui sont nord-sud ne sont pas dans le bon sens. »

Les trois clôtures venaient d'être livrées, et leurs trois peintres ne savaient dessiner
qu'**un seul sens** : est-ouest. Les lisses traversaient la tuile sur toute sa largeur, les
poteaux étaient à `x = 2` et `x = 13`, et les planches du bois se tenaient côte à côte en
travers. Une clôture qui descend du nord au sud était donc une **pile de panneaux vus de
face** — d'où l'impression, juste, qu'elle était couchée.

⚠️ **Et le remède était déjà écrit trois fois dans le dépôt.** `varianteDeTuile()` sait
demander à une tuile ce que ses voisines lui apprennent : les passages piétons, les cases de
stationnement et les rampes s'en servent. Les clôtures tombaient dans le repli et ne
recevaient qu'un bruit stable. Elles ont maintenant `varianteDeCloture()` — **un masque des
quatre côtés où la clôture continue** (1 nord, 2 est, 4 sud, 8 ouest).

- **Le dessin se fait en BRAS** : un brin du centre vers chaque côté où ça continue. Tout
  passe par `bloc`/`trait`, qui **échangent les deux axes** selon le sens — c'est tout le
  correctif, et c'est ce qui garantit qu'un nord-sud est un est-ouest tourné.
- **Un coin et un bout comptent** : un poteau se pose au centre dès que ce n'est pas une ligne
  droite. Sans lui, une clôture qui s'arrête a l'air coupée au couteau et la maille flotte au
  tournant.
- ⚠️ **Les trois partagent la géométrie** et ne diffèrent que par leur palette et ce qu'elles
  portent (la maille du grillage, les planches du bois, les trois fils et les épines du
  barbelé) — sinon on corrige un sens sur une clôture et on recommence à la prochaine. Et les
  trois se **continuent l'une l'autre** : un grillage qui se poursuit en barbelé est une seule
  ligne, parce qu'ici c'est la géométrie qui compte, pas la matière.
- ⚠️ **La hauteur des planches se tire sur un seul axe** : le même brin tourné doit donner le
  même dessin tourné, sinon le juge ne peut plus rien comparer.
- **Juges** : pour **chacun des trois glyphes**, le nord-sud n'est pas le même dessin que
  l'est-ouest, il en est le **tourné trait par trait**, un bout de course porte son poteau
  central, un coin aussi, et une ligne droite ne l'a pas. ⚠️ Le banc sait maintenant
  **enregistrer les `fillRect`** d'une cuisson (`ctx.traces`) : sans ça, on ne peut pas juger
  un dessin sous Node — le canevas du banc ne garde aucun pixel.

## Notes

bug de Martin : les trois peintres ne dessinaient que l'est-ouest, donc une clôture
verticale était une pile de panneaux vus de face. Elles lisent maintenant leurs voisines
(`varianteDeCloture` : un masque des quatre côtés où la clôture continue) et se peignent en
**bras** — le même code pour les trois, avec les deux axes échangés en nord-sud, un poteau
au centre à chaque coin et à chaque bout. Le juge compare les **deux cuissons trait par
trait** : le nord-sud doit être l'est-ouest tourné
