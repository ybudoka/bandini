# Les nids-de-poule survivent à une porte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

vu le 16 sept. 2026 en livrant les quartiers : **après être entré dans n'importe quel
bâtiment et ressorti, plus un seul nid-de-poule ne secoue la ville** jusqu'au rechargement.
Reproduit au banc sur la base (`nidDePoule` vrai avant, faux après `Monde.entrer` puis
`Monde.restaurer`). La cause : `nids` vit dans le MODULE de `monde.js` ; `entrer` passe par
`charger`, qui le remplace par les nids de la pièce (aucun), et `restaurer` ne rend que la
carte. Même piège pour `coeur` (remis à `null`, recalculé — sans dégât). Le remède est celui
du standing : le ranger **sur la carte** (`carte.nids`), et un juge qui entre, ressort et
roule sur un nid. ✅ **Livré** (17 sept. 2026) : l'index des nids vit maintenant **sur la
carte** (`carte.nids`), et le cœur de la ville aussi (`coeurDeLaVille` lit toujours la
VILLE, même demandé depuis une pièce — il y restait au milieu de la pièce). Les deux autres
caches du module (`entraveJour`, `brisEnCours`) ont été relus : une pièce n'a ni entrave ni
aqueduc, ils sortent avant de rien retenir, ils sont sains. Un juge passe par la **vraie
porte** (`Jeu.entrer`, `Jeu.sortir`, fondus compris), puis roule sur un nid : rouge sur
l'ancien code, et chaque moitié vue rouge sans sa règle.
