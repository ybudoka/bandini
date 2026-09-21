# Trottoir et traverses de deux tuiles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le trottoir et les traverses font deux tuiles, ils devraient en faire une (**correctif**, taille 2)_

_Demande de Martin :_ « les trottoirs ne devraient être que d'une tuile de large », et
« les traverses de piéton devraient aussi être d'une tuile ».

`TROTTOIR = 2` depuis M1, et il se voit : 32 px de trottoir contre une rue de deux voies, ce
n'est pas une proportion de ville, c'est une promenade. ⚠️ **Mais cette constante ne décore
rien — elle construit.** `_coupe()` la lit pour découper _chaque_ rue, et tout le reste en
découle. Il faut donc dire d'avance ce que ça déplace, parce que ça déplace la ville entière.

**Le choix à faire, et il n'y en a que deux.** Une rue fait `largeur - 2 × TROTTOIR` voies.
Passer le trottoir à 1 sans rien d'autre transforme une **rue de 6 en quatre voies** et un
boulevard de 8 en six. Donc :

- soit **les rues rétrécissent de deux tuiles** (rue 6 → 4, boulevard 8 → 6) et le nombre de
  voies ne bouge pas — la ville perd environ 10 % de sa largeur et de sa hauteur, et c'est
  l'option qui respecte la demande sans toucher au trafic ;
- soit **on garde les largeurs** et chaque rue gagne deux voies — ce qui refait le trafic, le
  déport dans la voie d'à côté, les feux et les lignes d'arrêt. Ce n'est pas ce qui a été
  demandé.

**Les traverses suivent toutes seules — c'est la même constante.** Au croisement, la bande
de passage piéton fait exactement `TROTTOIR` tuiles de profond : c'est l'endroit où la
chaussée traverse la ligne du trottoir. La demande de Martin sur les traverses n'est donc pas
un deuxième chantier, c'est la **preuve que le premier est le bon** — le trottoir et sa
traverse sont le même nombre, et ils doivent le rester.

- ⚠️ **Mais le 2 est écrit en dur dans le JS**, et c'est le piège qui mordra. `monde.js` range
  les tuiles d'un croisement avec `inter.y - 2` et `inter.x - 2` — deux littéraux — « pour
  inclure les passages piétons, deux tuiles de chaque côté ». Le paquet transporte pourtant
  déjà `grille.trottoir`. Le jour où `TROTTOIR` passe à 1, Python dessinera des traverses
  d'une tuile et le JS continuera d'en réclamer deux : un piéton demanderait à quel feu obéir
  en se tenant sur la chaussée, et un char lirait un croisement là où il n'y en a plus. **Ce
  littéral doit lire le paquet avant qu'on touche à la constante.**
- ⚠️ **Une traverse d'une tuile est une porte de 16 px pour tout un coin de rue.** Les piétons
  ne traversent qu'aux passages, et un char cède à celui qui est engagé dessus
  (`priorite_pieton_px`). En file indienne, à un coin passant, ça peut faire attendre un char
  pour chaque piéton, l'un après l'autre. C'est la même question que la foule sur un trottoir
  d'une tuile, et elle se tranche en même temps.

⚠️ **Ce qui vivait sur le trottoir doit déménager**, parce qu'il n'y aura plus qu'une tuile et
que tout s'y bouscule déjà : les lampadaires, les bornes-fontaines, les kiosques et roulottes
(`_places_ambulantes` cherche du `.`), les enseignes qui pendent au-dessus, et surtout la
**réserve de deux tuiles devant chaque porte** posée par `poser_porte` — avec un trottoir
d'une tuile, la deuxième réservée tombe sur la chaussée. Chacun a besoin d'un chez-soi
explicite : contre le mur pour les lampadaires et les bornes, dans un élargissement de coin
ou sur une place pour les ambulants, et une seule tuile réservée devant les portes.

⚠️ **Et la foule.** Un personnage fait 12 px de large ; une tuile en fait 16. Deux piétons ne
se croisent donc plus sur un trottoir d'une tuile — or la règle du jeu est qu'**un piéton ne
pose pas le pied sur la chaussée**. Il faut trancher : ou bien les piétons acceptent de se
frôler (la foule se démêle déjà, `demeler()`), ou bien le trottoir s'élargit là où il y a du
monde. Sans décision, on obtient des bouchons de piétons devant chaque commerce.

- ⚠️ **Toutes les graines changent.** Ce n'est pas un réglage : c'est une ville redessinée.
  Les positions sauvegardées se rattrapent déjà par l'empreinte du catalogue (M8 l'a fait une
  fois), et tous les juges de géométrie se rejouent — connexité forte des voies, un seul îlot
  marchable, les croisements, les lignes d'arrêt. **C'est exactement à ça qu'ils servent**, et
  c'est ce qui rend ce changement possible sans y passer la semaine.
**⚠️ Essayé le 14 sept. 2026, et ANNULÉ par Martin en cours de route.** Ce que la tentative
a appris — et qui vaut plus que le code qu'elle a produit :

- **Les deux questions ouvertes de la fiche sont tranchées**, par Martin, pendant l'essai :
  1. « on laisse les gens se **croiser** » — pas d'élargissement du trottoir pour la foule ;
  2. « on **agrandit les terrains et non les rues** ; les gens peuvent passer sur le nouveau
     terrain ainsi créé » — ⚠️ **c'est une troisième option, que la fiche n'avait pas vue** :
     les deux tuiles libérées par chaque rue ne reviennent ni aux voies ni au néant, elles
     vont au **bloc**, et sa bordure devient un abord **marchable**. La ville garde sa taille,
     le nombre de voies ne bouge pas, et la largeur où l'on marche reste la même (1 trottoir +
     1 abord) — ce qui règle du même coup les bouchons de piétons ;
  3. « mais **priorité de marcher sur le trottoir** » — l'abord est un débordement, pas un
     deuxième trottoir : le flâneur préfère la dalle.
- **Le littéral du JS est un vrai prérequis, et il se corrige seul.** `monde.js` rangeait les
  tuiles d'un croisement avec `inter.y - 2` / `inter.x - 2` alors que le paquet transporte
  `grille.trottoir`. Ça se change en cinq lignes, **avant** de toucher à la constante, et ça
  ne casse rien — c'est le premier pas de la prochaine tentative.
- **Le coût réel, mesuré** : avec `TROTTOIR = 1` et les rues rétrécies, **neuf juges rougissent
  d'un coup** — poches de barbelé, ossature d'une autre graine, arbres dans les sentiers,
  enseignes des lieux garantis, foule qui se traverse, passages piétons, vélo du cycliste,
  homme-sandwich à son poste. ⚠️ Ce n'est pas un défaut des juges : **c'est exactement à ça
  qu'ils servent**, et c'est la mesure honnête de ce que « redessiner la ville » veut dire.
  La prochaine tentative doit prévoir de les rejouer **un par un**, pas de tout faire passer
  d'un coup.

- **Juges** : la largeur de la ville suit toujours sa trame (`somme(COLONNES) + somme(RUES)`) ;
  une rue garde deux voies et un boulevard quatre ; aucune tuile réservée ne tombe sur la
  chaussée ; aucun kiosque, aucune borne et aucun lampadaire ne bouche la seule tuile de
  trottoir devant une porte ; et **aucune largeur de trottoir n'est écrite en dur** — ni en
  Python ni en JS, le paquet est la seule source (un test lit les deux).

## Notes

demande de Martin : `TROTTOIR = 2` construit chaque rue **et la profondeur des passages
piétons** — une seule constante pour les deux. Le passer à 1 demande de rétrécir les rues de
deux tuiles (sinon elles gagnent deux voies), de reloger lampadaires, bornes, kiosques et la
réserve devant les portes, de trancher sur la foule, et ⚠️ de sortir le **2 écrit en dur**
dans `monde.js`. ✅ **Le prérequis est payé** (15 sept. 2026) : `monde.js` lit
`grille.trottoir`, et trois juges le tiennent — dont un qui donne au navigateur un paquet à
une tuile et compte ce qu'il range comme croisement, et un qui mesure que **toutes les
traverses font exactement la largeur du trottoir**. Il rougira le jour où la constante
bougera sans elles. Les trois questions ouvertes sont tranchées par Martin : on se croise,
les tuiles libérées vont **aux terrains** (dont la bordure devient marchable), et la dalle
reste prioritaire. ✅ **Le gros œuvre est livré** (15 sept. 2026, 2e tentative — la première
avait été annulée) : `TROTTOIR = 1` ; chaque rue perd deux tuiles (`RUES_V`/`RUES_H`) et
chaque bloc les gagne (`COLONNES`/`RANGEES`) — mêmes voies, même ville, ⚠️ sauf la rangée du
chenal, gardée telle quelle pour que le pont reste le seul lien carrossable. La couronne
extérieure de chaque bloc bâti (commerces, logements, gangs, industrie, lieux garantis,
fourrière — pas les parcs, les places ni les quais) devient un **abord** (`_`, pavé,
marchable, sol nu) où déménagent les **lampadaires** des coins de croisement, les
**kiosques** et les **postes** des hommes-sandwichs ; le trottoir reste la **dalle
prioritaire** : un flâneur qui passerait de la dalle à l'abord fait demi-tour trois fois sur
quatre (`REACTIONS.abord_renonce`, dans la fiche), sauf s'il va vers une porte.

- ⚠️ Les sentiers de banlieue, l'allée vers la rue et la réserve devant les portes
  traversent l'abord en le **pavant** (`_` → `.`), sinon une porte donnait sur un anneau de
  pavés. **Les neuf juges rejoués un par un** : les lampadaires (près d'une rue à plus de 80
  %, aucun sur la dalle), les kiosques (sur l'abord, la dalle devant), la banlieue, la
  fourrière, le chenal, la traverse (pleine, sans déborder), le toit (« un bord ne se peint
  pas COMME un plein », pas « plus » — il tenait par chance sur le premier toit venu), le
  témoin des cinq, la foule qui se creuse, l'amuseur (le juge le pose sur sa scène comme le
  moteur le fait, au lieu de parier qu'il naîtra hors champ en 400 images) et
  l'homme-sandwich — ⚠️ dont le juge de banc tombait pour une raison à lui : `retirer` ôte
  de la liste, pas de la **grille**, et `placeLibre` voyait encore le crieur qu'on venait
  d'ôter ; il tenait tant que le poste 0 était hors de la bulle du départ. 6 juges neufs
  dans `test_trottoir.py`, rouge-avant prouvé pour `abord_renonce` ; 1547 tests. Aperçu :
  l'artefact « La rue d'une tuile »
