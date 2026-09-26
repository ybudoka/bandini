# Un vrai chalet dedans, et son foyer

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 26 sept. 2026 : « Remanie l'intérieur et ajoute un foyer au chalet. Je veux que ça ait vraiment
l'air d'être un chalet. » La pièce du chalet du rang (`app/blocs/chalet.py`) est la planque de Rocco en
plus petit, meublée avec les meubles génériques de la ville (lit, table, frigo, étagère, un poêle) : rien
ne dit « chalet ». On la redessine — murs de bois rond dedans, un **foyer** en pierre avec son feu (et sa
lueur), et ce qui fait un chalet (la corde de bois, la peau devant le feu, le trophée au mur…), sans
toucher à ce que la planque fait (lit, coffre, garde-robe, tous atteignables).

## Notes

Livré le 26 sept. 2026.

- **Le plan** (`app/blocs/chalet.py`) : même taille (11 × 8, la porte au même endroit) ; au mur du haut
  le panache d'orignal (`N`), la cheminée de pierre (`K`, deux tuiles) et les raquettes (`&`) ; dessous
  le foyer (`Y`, deux tuiles), la corde de bois (`L`), l'armoire ; la peau d'ours (`U`, deux sur deux)
  et deux berçantes (`V`) devant le feu ; le lit, le coffre au pied du lit, la table de pin et ses deux
  chaises, le poêle à bois et une seconde corde de bois. Plus de plantes, de frigo ni de classeur.
- **Les matériaux d'une pièce** : `carte._piece(…, materiaux={glyphe: matériau})`, transmis par
  `Monde.entrer` comme ceux d'une carte de bloc. Les murs `B`, `W`, `D` en bois rond (le même peintre
  que dehors), et `t`, `l`, `k`, `e`, `z`, `a`, `h` en `@chalet` : plancher de pin, lit à carreaux de
  bûcheron, coffre cerclé de fer, armoire de pin, poêle en fonte, table et chaises de pin. Chacun garde
  sa règle (on dort dans le lit, le coffre s'ouvre). Le plancher sous un meuble suit le matériau.
- **Le feu** ne se cuit pas dans la tuile : `Monde.dessinerFoyers` redessine les flammes à chaque image
  d'après `B.t` (jamais un dé) et une lueur chaude qui respire. La tuile porte la pierre, l'âtre noir,
  les bûches et la braise.
- ⚠️ Le plancher de pin était un **damier** à la première capture (chaque tuile teintait ses planches) :
  la teinte ne dépend plus que de la rangée, et les planches courent d'une tuile à l'autre.
- `table` et `chaise` de `sprites.js` prennent une palette (la ville, ou le pin du chalet).
- Juge : `test_dedans_c_est_un_chalet_et_le_foyer_brule` (`test_chalet_js.py`) — les meubles d'un camp,
  pas ceux d'une ville, la cheminée au-dessus du foyer, un peintre pour chaque meuble repeint, la planque
  qui sert encore, et le feu qui change d'une image à l'autre (rouge si on le fige). La liste des
  meubles sur plusieurs tuiles (`test_interieurs.py`) gagne le foyer et la peau d'ours.
