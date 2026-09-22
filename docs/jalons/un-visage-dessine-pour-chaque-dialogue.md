# Un visage dessiné pour chaque dialogue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « je veux des visages dessinés pour chaque dialogue ». Un portrait
en pixels (40×40) à gauche de la boîte de dialogue, pour chaque personnage qui parle (les 23
de `PERSONNAGES`, l'agent de police) : dessiné par du code (`static/js/visages.js`), dans
l'esprit des sprites, avec les couleurs de palette qu'il a déjà dans la rue ; ses traits
(coiffure, moustache, lunettes, casquette, rides…) sont des DONNÉES, dans sa fiche Python
(`visage`). L'expression suit le jeu d'acteur : une `humeur` tirée des balises de `jeu=`
(`[angry]` → fâché, `[warmly]` → content…) voyage vers le navigateur à la place du jeu. La
bouche bouge pendant que la voix parle, les yeux clignent. Juges : chaque personnage a un
visage valide et distinct, chaque balise a son humeur, la boîte le dessine.
