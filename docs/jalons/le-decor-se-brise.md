# Le décor se brise

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le décor se brise (**correctif**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « une interaction réaliste avec le décor — les bris de poteau, de banc
de parc et d'arbre, tout ce qui se brise. »

⚠️ **Le décor est solide pour les piétons et fantôme pour les chars.** `bloquerParDecor`
repousse un passant hors d'un arbre, d'un banc, d'une poubelle ; côté véhicules, le seul
appel à `decorAutour` sert à choisir une place de stationnement. Un autobus traverse donc un
arbre, un kiosque à hot-dogs et une fontaine sans ralentir — et **le lampadaire est fantôme
pour tout le monde** (`solide: false`), on le traverse à pied comme en char. Le défonçage
de M9 ne casse que des **tuiles** (clôtures, bornes) : le décor, lui, n'est ni un obstacle
ni une chose qui casse. C'est la moitié d'un monde.

**Deux familles, et c'est la fiche qui décide** (`DECORS`, comme `vehicules.py` décide ce
qu'un char sait faire) :

- **ce qui ARRÊTE un char** : un arbre, une fontaine, une borne — le char prend des dégâts
  comme contre un mur, et la chose ne cède qu'au-dessus d'un poids (le `defonce` de la fiche
  existe déjà : un camion déracine un arbre, une berline s'y écrase) ;
- **ce qui CASSE sous un char** : un banc, une poubelle, un kiosque à journaux, un cône, un
  lampadaire — le char ralentit d'une fraction (`defonce`) et continue, la chose est par
  terre.

**Le bris a un après, sinon ce n'est qu'une disparition :**

- des **débris** (le décor `debris` existe) là où c'était, et un banc cassé, un arbre couché
  ou un poteau à terre deviennent des obstacles **bas** — solidité 3, comme une clôture : on
  les enjambe à pied, un char les évite ou les défonce ;
- ⚠️ **un lampadaire à terre ne s'allume plus.** Sa lumière vit dans `carte.lampes`, à part
  de son poteau ; casser l'un sans éteindre l'autre donnerait un halo qui flotte au-dessus
  de rien — exactement le genre de chose qu'on ne voit qu'en jouant, la nuit ;
- **la ville se souvient jusqu'au lendemain** : rien ne repousse dans la minute. Ce qu'on a
  cassé reste cassé jusqu'à `nouveauJour()`, et le quartier porte ses blessures — c'est ce
  qui fait qu'une nuit de folie **se voit** le matin.

- ⚠️ **Le décor est bâti une fois.** `grilleFixe` est l'index « qui ne bouge jamais », et
  c'est ce qui le rend gratuit par image. Casser un décor, c'est le sortir de cet index :
  `reindexerDecor` existe, il est rare, et il doit le rester — on réindexe au bris, jamais
  par image. Rien à repeindre dans les morceaux : le décor est une entité, pas une tuile.
- ⚠️ **Casser, c'est un délit.** La taxonomie a déjà « conduite dangereuse +1 » et un témoin
  qui rapporte. Un lampadaire couché en pleine rue, un arbre déraciné dans le parc : la même
  étoile, le même témoin. Sans ça, défoncer devient gratuit, et un char lourd vaut plus
  qu'un char rapide.
- ⚠️ **Le budget.** Les débris sont des entités, donc ils comptent dans le plafond. Un
  plafond de débris par jour, les plus vieux disparaissent en premier — et un test rejoue une
  nuit à tout casser pour vérifier que le rythme tient.
- **Si ça coûte peu** : un poteau qui tombe peut renverser un piéton (la réaction `renverse`
  existe). Sinon, il tombe sans toucher personne, et ce n'est pas grave.
- **Juges** : chaque décor solide déclare s'il arrête ou s'il casse, et sous quel poids ; un
  banc n'arrête jamais un camion, un arbre arrête toujours une berline ; un lampadaire à
  terre a sa lumière éteinte ; un décor cassé est **enjambable** et pas fantôme ; tout est
  debout le lendemain ; et les débris ne dépassent jamais leur plafond.

**Livré le 13 sept. 2026 :**

- **La fiche décide**, comme `vehicules.py` décide ce qu'un char sait faire : `arrete: n` est
  la **masse** au-delà de laquelle ça cède (l'arbre à 2,0 — une berline de 1,0 s'y écrase, un
  camion de 3,0 le déracine), `casse: f` la **fraction de vitesse** qu'on garde en passant au
  travers. Un décor sans l'un ni l'autre reste ce qu'il était : ⚠️ **les feux et les panneaux
  ne se renversent pas**, sinon un croisement se démonte au premier virage raté.
- **Le lampadaire devient solide.** Il était `solide: false` — fantôme pour tout le monde,
  traversé à pied comme en char. Un poteau de deux pixels de rayon qu'on traverse, c'est la
  moitié d'un monde ; un juge qui affirmait le contraire a été retourné.
- ⚠️ **Le rebond se pose dans l'appelant, pas dans `heurterMur`.** Celui-ci ne touche qu'à
  `v.vitesse` — pour les tuiles, c'est `avancer()` qui renverse `vx`/`vy`, axe par axe. Sans
  ça, la berline s'écrasait sur l'arbre **en gardant sa vitesse réelle** et le traversait
  quand même. Ça ne se voit qu'en mesurant la position finale, pas la collision.
- ⚠️ **`debris: true` et `ne: B.t` séparés.** L'image de naissance vaut **zéro** au premier
  instant d'une partie, et `if (e.debris)` laissait alors passer le tout premier morceau
  cassé du jeu. Le genre de bogue qui ne se montre qu'une fois par partie, au pire moment.
- ⚠️ **La ville pose déjà 88 débris à la main** (cour de la fourrière, terrains vagues) : le
  plafond et les juges ne comptent que ceux **nés d'un bris**.
- **La lampe s'éteint avec son poteau** : sa lumière vit dans `carte.lampes`, à part du
  poteau ; casser l'un sans éteindre l'autre donnerait un halo qui flotte au-dessus de rien.
- **Casser est un délit** (`conduite_dangereuse`, avec son témoin) : sans ça, défoncer est
  gratuit et un char lourd vaut plus qu'un char rapide.
- **Le lendemain, tout est debout** — par `nouveauJour()`, pas par un appel à la main : c'est
  le lever du jour qui répare, et c'est ce lien-là que le juge tient.
- ⚠️ **Ce qui n'est PAS fait, et c'est une décision** : un décor cassé n'est pas
  _enjambable_ — il est **traversable**. La fiche voulait de la solidité 3 (comme une
  clôture), mais `enjamber` est une machine à **tuiles** et le décor est une **entité** : lui
  donner l'enjambement demanderait de porter cette machine sur les entités, pour un banc
  couché. Les débris sont donc du décor qu'on foule.
- **Juges (1 neuf, 1 retourné)** : une berline s'arrête sur un arbre et ne passe pas, un
  camion le déracine et passe, un banc cède sous une berline ; le bris laisse des débris et
  n'est plus solide ; déraciner au camion compte un délit ; un lampadaire à terre a sa lumière
  éteinte ; tout casser d'un coup ne dépasse jamais le plafond de débris ; et `nouveauJour()`
  remet **exactement** ce qui était cassé, déblaie et rallume.

## Notes

demande de Martin (« les bris de poteau, de banc de parc et d'arbre ») : le décor était
**solide pour les piétons et fantôme pour les chars** — un autobus traversait un arbre, un
kiosque et une fontaine sans ralentir, et le **lampadaire était fantôme pour tout le
monde**. La **fiche décide** maintenant : `arrete` (un arbre stoppe une berline, un camion
le déracine) ou `casse` (un banc, un poteau, un cône cèdent sous n'importe quoi lancé). Le
bris laisse des **débris** plafonnés, **éteint la lampe** du poteau tombé, compte une
**conduite dangereuse**, et la ville se **répare au lever du jour** — pas dans la minute :
le quartier porte ses blessures
