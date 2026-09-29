# Les juges : deux rouges honnêtes à trancher

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Deux juges réécrits pendant « Les juges : moins de doublons, plus de morsure » (vague A, 28
sept. 2026) rougissent sur le JEU et sont gardés hors de dev en attendant la décision de
Martin. 1) Le sentier de parc : lu enfin dans le bon repère, il trouve le kiosque de Madame
Thibodeau posé sur l'allée est (`carte._parc` le bâtit après les allées : six tuiles de
sentier sous un toit) — déplacer le kiosque, ou accepter. Le juge :
`refs/wip/vagueA-sentier`. 2) L'empreinte des chars : mesurés sur la projection, cinq
dessins dépassent leur collision — la pelleteuse de 9 px (son godet, que `sprites.js` promet
replié), le bateau 3, la motoneige et la remorqueuse 2, le cabriolet 1,5 — corriger les
dessins, ou tolérer un débord. Le patch : le blob `refs/wip/vagueA-empreinte` (le sortir par
`git cat-file -p`, puis `git apply`).

- ⚠️ Un juge qui rougit sur le jeu ne se relâche pas pour passer : on répare le jeu, ou on
  écrit pourquoi le débord est voulu.
