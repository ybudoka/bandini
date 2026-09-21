# Ce qui se dit destructible l'est

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

un lampadaire portait `casse: 0.7` depuis toujours et encaissait un chargeur de carabine
sans broncher : `Entites.briser` n'avait qu'**un seul appelant**, le char lancé. La balle
traversait le décor (`majProjectiles` ne s'arrêtait que sur une façade), l'explosion d'un
char ne filtrait que `q.vivant` — ce que le décor n'est pas — et le brasier d'un molotov non
plus. Deuxième moitié, plus vieille : `buisson` et `corde_a_linge` déclaraient `casse` avec
`solide: false`, et l'index du décor ne prenait que le solide — deux fiches destructibles
sur le papier que **rien au monde** ne pouvait toucher ; la règle existait en **deux
exemplaires** (`reindexerDecor` et `creerDecor`), si bien que le premier correctif n'en a
réparé qu'un et qu'il a fallu un juge qui tire sur un buisson de la **vraie carte** pour
voir la copie oubliée. La fiche gagne `pv` (l'échelle se lit en balles de pistolet :
poubelle 25, lampadaire 60, kiosque 90) et `Entites.endommagerDecor` est le second chemin
vers `briser` — balle, explosion, feu. Ce qui porte `arrete` (arbre, fontaine,
camion-restaurant) n'a **pas** de `pv` : il encaisse et ne tombe jamais, c'est ce qui fait
un abri. Trois pièges réglés en chemin : la balle jugée sur son **trajet** et non son point
d'arrivée (10 px par image, un poteau en fait 8 — elle le traversait une fois sur deux) ; la
cible visée à **hauteur de canon** (`y - 6`) plutôt qu'élargie de 7 px, sans quoi un banc
devenait un gilet pare-balles plus large qu'un passant ; et **une balle, une morsure**,
sinon ce qui ne l'arrête pas se faisait mordre à chaque image.
`scripts/verifier_ce_qui_casse.py` tient le catalogue et le câblage, branché en **garde
Claude Code** à l'écriture et avant `git commit` comme ses deux voisins ;
`tests/test_ce_qui_casse.py` : 6 juges de forme + 6 de banc qui tirent pour de vrai
