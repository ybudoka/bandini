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

### Le découpage (30 sept. 2026 — Martin : « on y va »)

Martin avait laissé à trancher les familles, leur nombre et les meubles. Ce qui est proposé, et livré
vague par vague — chacune jouable et livrée seule :

**Vague 1 — Les cartes de hockey de la Ligue de Baie-des-Brumes, saison 1974-75** (à pied). Quarante
cartes, cinq par district de terre (le Faubourg, les Érables, la Shop, les Quais, La Pointe, les Friches, le
Petit-Canton, la Gare) — cinq joueurs de l'équipe du coin : les Castors du Faubourg, les Seigneurs des
Érables, les Boulons de la Shop, les Goélands des Quais, les Phoques de La Pointe, les Chardons des Friches,
les Dragons du Canton, les Aiguilleurs de la Gare. Chaque carte a son numéro (stable : c'est lui que la
sauvegarde garde, et que le marché aux puces vendra), son joueur, sa position, et **un dos** qu'on lit au
carnet — une fiche de hockeyeur de garage, une ligne qui tombe à plat exprès (le ton de
[écrire drôle](../ecrire-drole.md) : on frappe en haut, le propriétaire d'équipe, jamais le petit joueur).
La carte n° 1, c'est Gilles « La Toque » Bouchard — celui de la statue du parc.

- **Où** : une par recoin — le fond d'une ruelle, un coin entre deux murs, le bout d'un quai, une friche
  derrière une clôture —, posée **sur la ville finie, après la bande nord, sans un dé** (comme les
  frénésies) : une règle écrite choisit, dans chaque district, les recoins les plus encaissés (le plus de
  murs autour), les plus loin les uns des autres, jamais sur un décor, un paquet, une frénésie ou le pas
  d'une porte, et toujours rejoignables à pied depuis la rue. La ville d'avant ne bouge pas d'un octet
  (juge : la ville en JSON avant et après la pose).
- **Comment on les trouve** : une carte par terre, et **un scintillement discret** toutes les trois
  secondes — assez pour l'œil qui fouille, trop peu pour une carte au trésor. L'indice, c'est le carnet :
  « LES CASTORS DU FAUBOURG 2 / 5 » dit où il en reste. On la ramasse en marchant dessus, à pied.
- **Ce qu'elles rapportent** : 25 $ la carte, une prime à 10, à 25 et à 40 (l'album complet), un son
  ElevenLabs au ramassage et l'orgue d'aréna aux paliers ; le carnet les range (COLLECTIONS), le BILAN
  compte « CARTES DE HOCKEY n / 40 ». La sauvegarde garde les numéros trouvés (`partie.collections`).
- **Le poids** : les dos et les noms ne voyagent **ni dans les définitions ni dans la carte** (les deux
  sont au ras de leur plafond) : ils partent sur `/api/collections`, demandé en arrière-plan après les
  définitions et gardé hors ligne, comme les notes de la musique.
- **Le debug** : TRICHES > ALLER > COLLECTIONS… (aller à une carte qui manque), et une ligne pour toutes
  les avoir.

**Vague 2 — La planque qu'on décore.** Des points de décor **conditionnels** dans une pièce (un objet
présent si la partie le dit), le mécanisme qui servira aussi au chalet du rang : les trophées des paliers
de cartes (le cadre de dix cartes au mur, le cadre de vingt-cinq, l'album et sa coupe sur le bureau) et
**des meubles à acheter** — un catalogue sur la table de la planque (« le catalogue de chez Beausoleil »,
livré le lendemain) : le juke-box qui joue les stations de la radio, l'aquarium, le sofa à carreaux, la
lampe à lave, le tapis tressé, le téléviseur à oreilles de lapin. Gardés dans la sauvegarde
(`partie.meubles`), posés à une place écrite dans le plan de la pièce, jamais au dé.

**Vague 3 — Les bebelles** : douze curiosités québécoises cachées dans les endroits durs (le bout de
l'île, l'aéroport, le fond du rang, un toit qu'on atteint par une rampe) — un cendrier de l'Expo 67, une
tuque d'équipe disparue, un Bonhomme en plastique, un calendrier de garage de 1982… **Chaque bebelle
trouvée se pose elle-même dans la planque** (l'étagère des bebelles) : l'objet est le trophée.

**Vague 4 — Les sauts de Rocco** (au volant) : vingt rampes qui comptent une fois chacune, vol mesuré,
comme le Grand Saut. (Les enseignes qu'on dévisse la nuit, troisième famille de la fiche d'origine,
restent à trancher : elles doublent l'affiche arrachée du décor qui répond.)

**Le marché aux puces du dimanche vient APRÈS** (sa ligne) et s'appuie sur ce qui précède sans qu'on le
fasse ici : les cartes ont un numéro stable (il vendra celle qui manque par `Collections.donner`, pas par
un index), et chaque meuble du catalogue porte `ou` (`catalogue`, `puces`) — les puces vendront ceux qu'on
ne commande pas.

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
