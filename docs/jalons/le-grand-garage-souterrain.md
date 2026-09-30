# Le grand garage souterrain

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des véhicules que nous pourrons reprendre après
dans un grand garage souterrain ». Tranché avec lui, question par question : on **descend en char** dans un vrai
sous-sol (pas un simple menu) ; il s'ouvre **quand on possède le garage** ; **deux niveaux de dix cases**, le
deuxième à acheter **10 000 $** ; un char volé **reste volé** et on ne descend pas avec des étoiles ; on entre
**par le rideau** du Garage Rocco Bandini, et **à pied par un ascenseur** dans la pièce du garage.

### Ce qui existe

- **Le Garage Rocco Bandini** (`SPECIAUX["G"]`, `app/carte.py`) : une propriété à 4 500 $ (`app/economie.py`,
  `p.proprietes.garage`), un rideau où l'on entre au volant (`missions.js` `majGarage`/`majAtelier`, phases
  `baisse → menu → leve → sortie`, REPARTIR en tête du menu), et une pièce à pied de 10 × 7 avec le commis
  (`carte.py`, l'intérieur `garage`).
- **Aucun parc de chars.** Seulement des places à un char : `planque.vehicule`, `charsDesPlanques`, la fourrière
  (`p.fourriere`, six places). La ville **oublie** un char garé loin (`Vehicules.peupler` retire tout char hors de
  la bulle, `aToi` compris) : un stockage doit vivre **en données**, pas en entités.
- **La fiche d'un char sauvegardé** : `{ slug, sprite, couleur, vie, vole, aToi, mods }`, recréée par
  `recreerLeChar` (`jeu.js`) et `Garage.poser`. La fourrière fait déjà « données → chars sur des places »
  (`garnirLaFourriere`), sans dé.
- **Un char ne roule jamais dans une pièce**, seulement dans un **bloc** (`B.bloc`, `Jeu.passerDansLeBloc`). La
  villa (`app/blocs/villa.py`) est un bloc à plusieurs niveaux, un `CADRE` par niveau, reliés par des escaliers
  **à pied seulement**.

### Ce que ça donne

**Le lieu : le bloc `souterrain`**, dessiné à la main, **sans un dé** (`app/blocs/souterrain.py`). Deux cadres,
chacun plus grand que l'écran (30 × 17) :

- **Niveau −1** : la rampe vers la rue, une allée, **dix cases numérotées P1 à P10** peintes au sol, l'ascenseur,
  des piliers, des néons.
- **Niveau −2** : la rampe intérieure qui monte au −1, dix cases **P11 à P20**, l'ascenseur. **Une grille** ferme
  la rampe tant qu'il n'est pas acheté (une barrière du bloc, sa condition lue dans la partie).

**Entrer et sortir :**

- **En char** : sous le rideau du Garage Bandini, le menu gagne **DESCENDRE AU SOUS-SOL** (REPARTIR reste en tête).
  Au noir, on est au bas de la rampe du −1, au volant (`Blocs.sauter`). Refusé, avec sa raison à l'écran : garage
  pas acheté, une étoile ou plus, un char de mission, un bateau, une remorque, ou **plus aucune case libre**
  (« SOUS-SOL PLEIN — 10/10 »).
- **À pied** : un **ascenseur** dans la pièce du garage (un point, comme un escalier). Au noir, on arrive devant
  l'ascenseur du −1. En bas, l'ascenseur remonte à la pièce du garage, et dessert les deux niveaux.
- **Entre les niveaux, au volant** : la rampe intérieure se franchit **en char** — c'est neuf (les escaliers de la
  villa sont à pied) : le char et son conducteur passent au noir d'un cadre à l'autre, cap conservé.
- **Ressortir** : monter la rampe du −1 au volant. On réapparaît **devant le rideau du Garage Bandini**, le nez vers
  la rue — pas au passage d'un bord de carte comme les autres blocs (le retour se pose à la main).

**La mémoire : `p.souterrain`**, dans la partie :

```js
souterrain: { niveaux: 1, cases: [ /* 20 × (null | { slug, sprite, couleur, vie, vole, aToi, mods }) */ ] }
```

- **Ranger** : un char immobile sur une case y est écrit **quand on quitte le sous-sol** (rampe ou ascenseur) et à
  chaque sauvegarde. Un char laissé dans l'allée est **garé par Ti-Guy** sur la première case libre ouverte.
- **Le plein ne se dépasse jamais** : la descente en char est refusée quand toutes les cases ouvertes sont prises,
  donc il y a toujours au plus autant de chars en bas que de cases. À pied, on descend toujours.
- **Reprendre** : à chaque descente, les chars rangés sont **recréés sur leur case**, couleur donnée (aucun dé),
  comme la fourrière. Monter la rampe au volant de l'un d'eux le **retire** de la liste : il redevient un char de
  la ville.
- **Un char volé reste volé** : le sous-sol cache, il ne lave pas — REPEINDRE reste le seul blanchiment.
- **Ni passant, ni trafic, ni police** en bas.
- **Recharger** ne perd rien : les cases sont des données, pas des positions en ville. Environ 3 Ko pour vingt chars,
  loin des 48 Ko d'une partie.

**Agrandir** : le comptoir du commis gagne **AGRANDIR LE SOUS-SOL — 10 000 $** (seulement si le garage est à toi et
le −2 pas encore ouvert). La grille du −2 s'ouvre.

**Le son** (ElevenLabs) : le ding et le moteur de l'ascenseur, les pneus qui crissent en écho sur le béton de la
rampe, le bourdonnement des néons.

### Deux vagues

1. **Le −1** : le bloc et son cadre, DESCENDRE AU SOUS-SOL au rideau, la rampe de sortie devant le garage,
   l'ascenseur dans les deux sens, `p.souterrain` (ranger, reprendre, Ti-Guy qui gare, le plein, recharger).
2. **Le −2** : la rampe intérieure au volant, la grille, AGRANDIR LE SOUS-SOL, et les sons.

### Ce qui guette

- ⚠️ **La ville ne doit pas bouger** : aucune tuile neuve dans la rue. Seul un point `ascenseur` s'ajoute dans la
  pièce du garage — une pièce du catalogue, pas la ville ; les juges « ce module ne déplace rien » le confirment.
- ⚠️ **`Vehicules.creer` sans couleur tire un dé** : chaque char recréé reçoit la sienne.
- ⚠️ **`Sauvegarde.completer`** initialise `souterrain` (les vieilles parties n'en ont pas), et la migration de la
  bande nord ne touche pas les cases (pas de `x`/`y` dedans).
- ⚠️ **Le retour d'un bloc** se fait par défaut à son `passage`, sur un bord de la carte : ici il se pose devant le
  rideau, cap vers la rue, et le rideau ne doit pas se rouvrir aussitôt (il faut relâcher puis réappuyer).
- ⚠️ **Une sauvegarde prise en bas** : la partie se réveille dans le bloc (`partie.bloc`, comme au chalet), ou devant
  le garage si la carte du bloc n'arrive pas — jamais un char perdu.
- ⚠️ **La rampe intérieure au volant** : l'arrivée est un refuge, le cap est gardé, et un char trop long (l'autobus,
  une remorque) n'y passe pas — la remorque est déjà refusée à la descente.
- ⚠️ **Le poids du paquet** : le bloc voyage à part (`/api/blocs/<slug>`), mais un son neuf va dans `audio.LIEUX`
  (plafond du premier écran plein) ; `test_definitions` dans les juges ciblés.

### Les juges

- Python : deux cadres plus grands que l'écran, vingt cases, la grille sur la rampe du −2, les arrivées (rampe,
  ascenseur) en refuge, `erreurs(bloc)` vide, la ville identique avec et sans le jalon.
- JS au banc, **au bouton** : ranger un char, recharger la partie, le reprendre (couleur, modifs, vie) ; le refus au
  plein, avec des étoiles, pour un char de mission et pour un bateau ; l'ascenseur dans les deux sens ; un char
  laissé dans l'allée rangé par Ti-Guy ; un char volé toujours volé en ressortant ; l'achat du −2 ouvre la grille ;
  la rampe intérieure au volant.
- Chaque juge vu rougir, sa règle retirée ; une capture Chromium du −1 et du −2 avant de livrer.
