# Le quartier chinois : un 7e district

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Idée de Martin (26 sept. 2026), en tranchant [l'école rivale](l-ecole-rivale.md#fiche) : « ça pourrait être un
quartier chinois ». Choisi parmi trois places (un coin du Faubourg, un bloc de carte à part, un district de la
trame) : **un 7e district de la trame** — un vrai quartier, avec ses rues, ses frontières et ses bagarres.

_Ce que ça donne :_ un quartier vivant — l'arche à l'entrée, les enseignes bilingues, les lanternes au-dessus
de la rue, les restos, les épiceries, la boulangerie, le marché le dimanche, la fête de la lune à l'automne —
et, à l'une de ses adresses, **l'école de kung-fu** dont les élèves ont mal tourné : le gang neuf de l'école
rivale, qui se bat avec les techniques du [répertoire](les-techniques-d-arts-martiaux.md#fiche).

- ⚠️ **Le ton** : le gang n'est pas « les Chinois ». Le quartier est à ses habitants (passants, commerçants,
  une foule comme ailleurs), l'école est UNE adresse, et le gang ce sont ses élèves dévoyés — le même
  traitement que les Cravates au Faubourg. Drôle comme le reste du jeu (voir `ecrire-drole.md`), jamais aux
  dépens de l'accent ou de l'origine.
- ⚠️ **La place — la recette de l'aéroport, pas une rangée de la trame** : changer une rangée de la trame
  re-tire toute la ville (26 juges rouges, voir « Grossir un lieu garanti déplace la ville »). Le quartier se
  pose **à côté** de la trame, en **tout dernier** dans `generer`, **sans un dé** : la carte s'allonge (comme
  pour l'aéroport, `aeroport.py` — 419 × 224 → 419 × 304), un plan dessiné, et une ou deux rues qui
  prolongent des rues de la trame. La ville d'avant reste identique à la tuile près.
- ⚠️ **Ce qu'un district de plus touche** (à relire avant de coder) : `DISTRICTS` et leurs rectangles
  (`carte.py`), les **frontières de gangs** (`pietons.frontieres`, mariées aux districts dans
  `definitions.py` — un district dessiné hors trame n'a peut-être pas de rectangle), les **bagarres** à la
  frontière, le **standing** (`standing_en`, borné à la trame), `Monde.lettreDuBloc`, la carte du jeu (la
  touche N), les blips, et les juges qui supposaient la carte = la trame (`test_carte`, `test_districts`,
  `test_trottoir`, `composantes_par_terre`…) — la liste de l'aéroport.
- **Ce qui s'y pose** : les devantures (restos, épicerie, boulangerie, herboristerie, l'école de kung-fu), le
  décor (lanternes, l'arche, étals), une garde-robe d'archétype pour le gang neuf (`garderobe.py`), sa
  couleur, sa musique de quartier peut-être (`une-seule-musique-pour-toute-la-ville` a tranché : à revoir
  avec Martin).
- **Prérequis et voisins** : il **porte** l'école rivale ; il touche « Les territoires des gangs bougent »
  (la même mécanique de territoires) ; le dojo du quartier (jalon 2) n'en dépend pas.

**À trancher avec Martin** (le brainstorming du jalon) : le nom du quartier et celui du gang ; où il se pose
(au nord du Faubourg ? à l'est, entre la Shop et les Quais ?) ; sa taille ; ce qui s'y ouvre au joueur
(missions, un donneur, le marché).

**Juges** : la ville d'avant identique à la tuile près (comparer les deux villes en JSON, clé par clé) ; le
quartier atteignable à pied et au volant ; le gang naît chez lui et se bat à sa frontière ; aucun dé consommé
par la pose ; les juges de la carte à la nouvelle taille.

## Notes

_Rien de livré._
