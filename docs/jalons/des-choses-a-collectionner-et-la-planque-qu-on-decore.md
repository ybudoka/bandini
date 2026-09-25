# Des choses à collectionner, et la planque qu'on décore

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 25 sept. 2026 : « des choses à collectionner et décorer la planque »._

_Ce que ça donne :_ une raison de fouiller chaque coin de la ville entre deux missions, et une planque
qui raconte la partie — on y voit ce qu'on a trouvé, gagné et acheté.

**Aujourd'hui**, la planque de Rocco (`carte.py`, `_piece("planque")`) a trois points — le lit (la
sauvegarde), le coffre, la garde-robe — et son décor ne bouge jamais. Rien ne se collectionne : les trois
paquets de Rocco de `f04` se ramassent, mais ne se comptent nulle part.

**Les collections** — trois familles, une par façon de jouer (à trancher par Martin, les noms comme le
nombre) :

- **Les cartes de hockey de Rocco** (à pied) : cinquante cartes cachées dans des recoins — derrière une
  benne, sur un toit de garage, au bout d'un quai. Le Clairon publie un indice le matin (le journal existe
  déjà).
- **Les sauts de Rocco** (au volant) : vingt rampes qui comptent une fois chacune, vol mesuré (le type
  `sauter` et le juge du Grand Saut existent déjà).
- **Les enseignes** (en passant) : un néon, une plaque ou une affiche par commerce du jeu, qu'on dévisse la
  nuit — le décor qui répond (« le décor, les bêtes et les gens répondent ») sait déjà arracher une affiche.

**La planque qu'on décore** : chaque collection complétée par paliers (10, 25, toutes) pose un objet dans
la planque — le cadre de cartes au mur, la maquette d'un char, l'enseigne du Brouillard au-dessus du lit.
Et des meubles **à acheter** (un juke-box qui joue les stations de la radio, un aquarium, un sofa à
carreaux), chez Rosa ou au marché aux puces. Une planque vide au début, pleine à la fin : c'est le bilan
de la partie, qu'on regarde.

⚠️ **Ce qui coûte, et ce qui guette :**

- **Poser, pas tirer.** Cent objets cachés dans la ville, c'est cent tuiles réservées : tirés au dé, ils
  déplaceraient toute la ville (« grossir un lieu garanti déplace la ville », 26 juges rouges la dernière
  fois). Ils se posent **en dernier, sans dé**, sur un plan écrit — comme l'aéroport et `devants.py`.
- **Le paquet** : la position de cent objets pèse quelques Ko ; à faire voyager avec la carte
  (`/api/carte`), pas dans les définitions (4 864 octets de marge gzip).
- **La planque se dessine selon la partie** : les pièces sont un plan fixe aujourd'hui. Il faut des
  points de décor **conditionnels** (un objet présent si un palier est atteint) — le même mécanisme
  servira à la deuxième planque.
- **Le carnet** compte chaque collection (un onglet de plus, ou une ligne du BILAN).
- **La sauvegarde** garde ce qui est trouvé (une liste d'identifiants stables, jamais un index).

**Juges** : chaque objet caché est atteignable à pied depuis la planque (le juge des barrières sait déjà le
faire) ; aucun n'est posé au dé ; la ville ne bouge pas d'une tuile quand on les ajoute ; une collection
complète pose son objet dans la planque, et il survit à une sauvegarde.

## Notes

_Rien de livré._
