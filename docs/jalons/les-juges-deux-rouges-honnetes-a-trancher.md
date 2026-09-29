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

## Notes

Livré le 29 sept. 2026. **Martin : « 1 et 2 on tolère ».** Tolérer ne veut pas dire relâcher : chaque
tolérance est ÉCRITE dans son juge, au plus juste, et le juge garde toute sa morsure pour le reste.

- **Le sentier de parc** (`test_carte::test_un_sentier_de_parc_se_traverse_de_bout_en_bout`) : il lit la
  ville d'avant (le repère du chantier), les allées que `_allee` réserve (espionnées), et n'excuse que les
  tuiles du **bâtiment du kiosque**, retrouvé depuis sa porte (`interieur == "kiosque"`) — pas des
  coordonnées : si le kiosque bouge, l'excuse le suit. Mord : l'étang posé sur les allées rougit (19
  tuiles) ; sans l'excuse, il nomme les six tuiles du kiosque, et elles seules.
- **L'empreinte des chars** (`test_poses_vehicules::test_le_char_tourne_autour_de_son_empreinte`) : les
  deux bouts mesurés sur la projection de profil ; `DEBORDS_TOLERES` porte les cinq débords à leur valeur
  mesurée (pelleteuse 9, bateau 3, motoneige 2, remorqueuse 2, cabriolet 1,5). Mord : sans la table, les
  cinq rougissent ; la pelleteuse à 8, elle rougit. Un sixième char qui déborde rougit.

