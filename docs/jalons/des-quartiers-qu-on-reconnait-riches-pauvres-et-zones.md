# Des quartiers qu'on reconnaît : riches, pauvres, et zonés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des quartiers qu'on reconnaît : riches, pauvres, et zonés (**ajout**, taille 4)_

_Demande de Martin (16 sept. 2026) :_ « je veux des cartiers plus reconnaissable, plus riche et
propre avec des commerce plus riche, des cartiers plus pauvre et sale. commercial, indistriel,
résidentiel, parc, etc.. »

⚠️ **Mesuré d'abord (graine de la ville, 16 sept. 2026) : le zonage existe, le standing
n'existe pas — et la rue ne dit ni l'un ni l'autre.**

- **L'usage est déjà décidé, au bloc.** Chaque lettre du `plan` d'un district est un zonage :
  `c` commerces, `h` maisons, `m` banlieue, `w` hangars, `i` industriel, `g` cour de gang,
  `p`/`k` parc, `n` bois, `o` place, `q`/`j` quai. On n'invente donc pas de zonage : on le
  **rend visible**.
- **Le standing n'existe nulle part.** Ni « riche », ni « pauvre », ni rien qui en tienne lieu
  dans `app/`. Ce qui ressemble à un contraste est un **accident de genre** : la friche tombe
  dans l'industriel parce que `_contenu` y tire plus de terrains vagues, pas parce que
  quelqu'un a décidé que La Shop était pauvre.
- **Le contraste entre districts est réel, mais flou.** Sacs, pneus, barils et débris (131
  dans la ville) : Les Érables **4**, Le Faubourg **25**, Les Quais **41**, La Shop **61**,
  La Pointe **0** — 0,3 par mille tuiles en banlieue, 3,7 à La Shop.
- **À l'intérieur d'un district, rien ne change.** Un bloc `c` du Faubourg ressemble au bloc
  `c` d'à côté : la rue commerçante et le coin derrière la cour des Cravates ont le même
  trottoir, les mêmes lampadaires, des enseignes tirées dans la même liste.
- **La rue ne dit pas la zone.** Un seul trottoir (`.`) et un seul abord (`_`) pour toute la
  ville. La Shop a **22 arbres** et 6 bancs ; les Quais ont **plus de poubelles (41) que le
  centre-ville (40)** ; la banlieue a **autant de nids-de-poule (21) que le Faubourg**.

**Deux axes, et ils ne se confondent pas.** L'**usage** (commercial, résidentiel, industriel,
parc, port) dit _ce qu'on fait là_ ; le **standing** (`cossu`, `ordinaire`, `pauvre`) dit _qui
en a les moyens_. Une rue commerçante peut être cossue (bijouterie, bistro, bacs à fleurs) ou
pauvre (prêteur sur gages, vitrines placardées) ; un résidentiel peut être la banlieue des
Érables ou les plex derrière le port. C'est le croisement des deux qui fait qu'on reconnaît un
coin de ville sans lire son nom.

### 1re vague — le standing se déclare, et la saleté se déplace (taille 1) — **livrée le 17 sept. 2026**

✅ **Ce qui est livré, et où ça s'écarte de la proposition ci-dessous :**

- **La grille** vit dans `DISTRICTS[].standing`, de la forme du `plan`. `_assembler_le_standing`
  refuse une grille sans la forme de son plan, un bloc bâti qui ne déclare rien, un bloc d'eau
  qui déclare quelque chose (`~` obligé), et un bloc avalé (`<`, `^`) qui ne dit pas ce que dit
  son maître — un superbloc est UN lot. ⚠️ **Un district neuf doit la déclarer**, sinon la ville
  ne se charge pas : c'est voulu, un quartier oublié serait ordinaire sans que personne l'ait décidé.
- **La proposition est tenue**, avec une précision : La Shop n'a pas de rangée commerçante au
  nord — son seul bloc de commerces est au sud-est. Sont ordinaires là-bas ce bloc-là, le parc
  et la fourrière municipale ; le reste est pauvre. Au Faubourg, la rue chic va du Terminus à la
  place par le parc (et la Boutique Rosa) ; le coin pauvre tient le garage, la planque, le bar, la
  cour des Cravates et le casse-croûte, plus les deux quais.
- **Une rue se coupe en deux** (`_Chantier.standing_en`, la coupe de `rect_district`) : chaque
  trottoir est du standing du bloc qu'il borde. **Le paquet la porte en douze lignes**
  (`grille.standing`), douze lignes de glyphes et pas un rectangle par bloc : 171 octets gzip. `Monde.standingA(tx, ty)` la relit avec la même coupe, **sur la carte et pas dans le
  module** — une pièce recharge le module et `restaurer` ne rend que la carte.
- **`app/salete.py` déplace, après les lignes d'autobus et avant le mobilier.** Ce qui part se
  lit à la POSITION (le `hash2` de base.js), pas au dé : changer un bloc de standing ne rebat pas
  la saleté du reste de la ville. Ce qui se repose tire dans son propre dé. Trois sortes : les
  déchets **semés par le terrain vague** (`dechets_semes` — une caisse de quai est de la
  cargaison, un pneu de grève une défense), les tags, les nids-de-poule.
- ⚠️ **L'ordinaire garde une saleté sur deux (`salete.GARDE`), pas toute.** Mesuré : 30 saletés
  en cossu, 40 en ordinaire, 159 en pauvre ; vider le cossu seul laissait le pauvre à **4,1 fois**
  l'ordinaire par tuile, sous le juge. Livré : **0, 16 et 213** — 11,5 fois, total inchangé (234).
- **Les déchets reposés vont au pied des murs** d'un abord pauvre (sacs, gravats, un pneu, un
  **matelas** couché, un **caddie renversé** — deux dessins neufs), avec la règle des arbres de
  rue (`mobilier._place_libre`) et loin des coins, du parvis, des chantiers et des amuseurs. Pas
  sur la friche : les terrains vagues pauvres en ont déjà assez. **La poubelle déborde** en pauvre
  (`poubelle_pleine`, la même : 65 sur 145), elle ne s'ajoute pas.
- **Le propre** : `mobilier.ARBRES_PAR_STANDING` passe par-dessus le rythme du district — une rue
  cossue plantée au pas de 6 à 8, une rue pauvre pas du tout. Les **bacs à fleurs** (cossu) vont
  au milieu des intervalles d'un bord, bouts compris : un bord cossu fait huit tuiles en moyenne
  et porte un seul arbre, « entre deux arbres » n'en posait que trois. Livré : 31 bacs, 0 arbre de
  rue en pauvre, la rue chic du Faubourg 2,5 fois plus plantée que ses rues ordinaires.
- **Comparée en JSON à la ville d'avant, clé par clé** : seuls `decor` (saleté, poubelles, arbres,
  bancs et bacs de rue), `decor_solide`, `graffitis`, `nids_de_poule` et `grille.standing`
  changent. Pas un paquet, pas une porte, pas une tuile.
- **Juges** (`test_quartiers.py`, 18) : la grille (chaque bloc, les grilles fautives, trois
  districts à deux standings, la coupe de rue), zéro saleté en cossu et cinq fois l'ordinaire en
  pauvre, aucune sorte ne monte, hors de la saleté la ville ne bouge pas, ce qui se pose est au
  pied d'un mur pauvre et ne ferme rien à pied — **aussi sur une ville où toute la saleté part**
  (sur la ville livrée, huit poses ne mettaient pas `_place_libre` à l'épreuve : la mutation
  restait verte) —, la poubelle qui déborde, les nids qui restent des nids, la rue plantée par
  standing (**au Faubourg** : Les Érables sont plantés serré par leur district, et sans le bonus
  cossu le juge restait vert), et le moteur qui lit la même grille, ressorti d'une pièce.

- ⚠️ **Le chien de garde du trafic mentait, et la ville neuve l'a montré.** `test_trace_js` est
  tombé sur sa graine 5 : un taxi resté 600 images au feu derrière une moto qui attendait la boîte
  repartait, et le contrôle « sur place » (la position d'il y a dix secondes) tombait juste après —
  téléporté au milieu de la voie. Rien à voir avec la saleté : les dés des entités ont changé et
  sont tombés sur la course. Mesuré : 0 graine sur 80 à la base (dont 40 avec une caisse lointaine),
  2 sur 40 avec la ville neuve. `Vehicules.debloquer` remet maintenant l'ancrage à zéro pendant une
  attente légitime : 40 sur 40. **Même leçon que le juge de la panne** : ce qui tombe à côté n'est
  pas forcément à soi, mais ce n'est pas forcément de la malchance non plus — il faut le tracer.

_La proposition d'origine :_

- Une **grille de standing** à côté du `plan`, une lettre par bloc (`+` cossu, `=` ordinaire,
  `-` pauvre), **écrite à la main, pas tirée** : c'est une décision de ville, et elle doit se
  lire dans `DISTRICTS` d'un coup d'œil comme le plan se lit. Elle descend dans le paquet
  (`zones`) — Python décide, JS calcule.
- Le standing **ne suit pas le district**. Proposition, à trancher par Martin au moment de
  dessiner : Les Érables cossus, sauf leur rangée commerçante contre la cour des Chevreuils ;
  le Faubourg avec sa rue chic entre le Terminus et la place, et son coin pauvre autour de la
  cour des Cravates — là où Rocco a sa planque ; les Quais et La Shop pauvres presque partout,
  avec leur rangée commerçante du nord ordinaire ; La Pointe ordinaire.
- ⚠️ **La saleté se DÉPLACE, elle ne s'ajoute pas.** Martin a renvoyé « trop de saleté
  partout » le 16 sept. (303 objets → 166) : le total de déchets, de graffitis et de
  nids-de-poule **ne monte pas d'un objet**. Il se concentre : **zéro** en cossu, la densité
  d'aujourd'hui en ordinaire, tout le reste en pauvre — trottoir compris (sacs au pied des
  plex, un matelas, un caddie renversé).
- **Le propre se voit aussi** : en cossu, des arbres de rue alignés, des bacs à fleurs, des
  poubelles vidées ; en pauvre, des poubelles qui débordent et pas un arbre. ⚠️ C'est le semis
  des **bancs et des arbres de rue**, en cours dans une autre session : cette vague passe
  **après** sa livraison et règle ses densités par standing, elle ne le refait pas.

### 2e vague — le zonage se lit (taille 1) — **livrée le 17 sept. 2026**

✅ **Ce qui est livré, et où ça s'écarte de la table ci-dessous :**

- **L'usage se DÉDUIT du plan, il ne s'écrit pas.** `carte.USAGE_DU_PLAN` traduit chaque lettre
  (la cour de gang est **industrielle** — barbelé, asphalte, ferraille ; la place et la foire
  sont des parcs), `USAGE_DU_GENRE` traduit les lieux garantis par le genre d'îlot qui les
  bâtit (le phare est bâti en banlieue, l'usine en industriel, le reste en commerces). Un
  superbloc prend l'usage de son maître. `carte.USAGES` ne porte que ce qui ne se déduit pas :
  la lettre de la grille, la couleur du calque et le mot de la légende. La grille voyage avec
  la carte (`grille.usage`, douze lignes), `Monde.usageA` la relit avec la coupe du standing.
- **Le sol, en couche peinte** : `Monde.varianteDeSol` (trottoir) et `Monde.varianteDAbord`
  (abord) portent l'usage et le standing au-dessus de l'usure ; `.` et `_` restent `.` et `_`.
  Le trottoir d'une rue chic est un granit lavé sans fissure, celui d'une usine un béton sombre
  taché d'huile, celui d'une rue pauvre a **plus de fissures — pas plus de rapiéçages** : vu dans
  Chromium, une dalle rapiécée sur deux se lisait comme un damier. L'abord : des pavés devant les
  commerces (plus chauds en cossu, des trous en pauvre), une **bande de gazon** devant les maisons
  (tondue en rayures en cossu, brûlée par plaques en pauvre), de l'asphalte devant les entrepôts
  (l'huile rare et à peine plus sombre : seize usures, donc seize places de tache — fréquente, elle
  s'alignait en pointillé). ⚠️ L'abord tirait `hash2 % 4` et son peintre lisait `(v >> 2) + 1`,
  toujours 1 : tous les abords de la ville avaient le même grain.
- **Le mobilier de l'usage** (`mobilier.MEUBLES_PAR_USAGE`, son propre dé, après les bacs à
  fleurs) : **40 parcomètres** devant les commerces, **21 boîtes aux lettres** et **12 bacs de
  recyclage** devant les maisons, **39 palettes** et **17 bennes** devant les entrepôts. Les palettes
  et la benne arrêtent un piéton (`DECOR_SOLIDE`, la benne arrête un char) ; le parcomètre, la boîte
  aux lettres et le bac se frôlent.
- **La carte plein écran porte le calque** (`Monde.calqueDeZonage`, cuit une fois comme la
  mini-carte) : les blocs se teignent de leur usage, la chaussée et le trottoir restent gris. Sa
  légende tient une rangée sous le titre — le bandeau du bas porte déjà les familles de lieux.
- ⚠️ **Les légendes de la carte étaient dans l'ordre ALPHABÉTIQUE, celle des lieux depuis
  toujours.** Le paquet trie ses clés (`definitions._json`), `Object.keys` rendait l'alphabet —
  MAGASINS, MANGER, REPÈRES — et le juge « la légende suit l'ordre de la table » relisait la table
  dans ce même paquet trié. Vu sur la capture, pas par un test. Un `rang` voyage maintenant avec
  `familles` et `zonage`, et les juges comparent à l'ordre **écrit en Python**.
- ⚠️ **Un vélo poussait l'autobus dans le carrefour, et ce n'était pas la vague.**
  `test_autobus_js` (« le nez hors du carrefour ») est tombé avec la ville neuve. Mesuré sur
  20 graines : **3 échecs à la base**, 1 avec la vague — le juge tenait par sa graine. Tracé :
  l'autobus attend son feu une tuile avant la ligne d'arrêt, son nez à **deux pixels** du
  carrefour ; un vélo du trafic, derrière, perd patience (`force`) et le pousse. Deux chars du
  trafic ne se poussent pas (« sur des rails »), mais l'autobus d'une ligne n'y était pas compté.
  `Vehicules.heurterVehicules` range maintenant la ligne avec le trafic : 20 sur 20 à la base
  comme avec la vague.
- **Reportés, et pourquoi** : les lampadaires rapprochés (c'est la redistribution des lampes de
  la 3e vague), la haie taillée (les rayures de tondeuse disent la même chose sans un décor de
  plus), et tout le côté pauvre du mobilier — vitrines placardées, grillage troué, char sur des
  blocs, ferraille et barils : c'est la 3e vague (les façades) et la 4e (ce qui est garé).
- **Juges** (`test_quartiers.py`, 7 de plus, chacun vu rouge sans sa règle) : l'usage se déduit du
  plan (La Shop et Les Érables écrites en toutes lettres), chaque lieu garanti a un usage, le
  mobilier dit l'usage, **sans le mobilier de l'usage la ville est la même glyphe pour glyphe et
  arbre pour arbre**, le sol se peint selon le quartier (le peintre appelé sur un faux contexte),
  la carte peint le zonage et pas la chaussée, et le moteur lit la même grille d'usages.

_La proposition d'origine :_

Chaque usage a sa signature au sol et dans son mobilier, croisée avec le standing :

| Usage | Sol (trottoir et abord) | Mobilier | Cossu ↔ pauvre |
|---|---|---|---|
| commercial | pavés, dalles | bancs, poubelles, parcomètres, lampadaires rapprochés | pavé propre et bacs à fleurs ↔ dalles cassées, vitrines placardées |
| résidentiel | trottoir et bande de gazon | arbres, boîtes aux lettres, bacs de recyclage, cordes à linge | haie taillée ↔ gazon brûlé, grillage troué, char sur des blocs |
| industriel | asphalte taché, pas de gazon | conteneurs, palettes, bennes, barbelé, pas un arbre | cour rangée ↔ ferraille, barils, flaques d'huile |
| parc | gazon, sentier | déjà lisible (parcs de quartier, livrés le 16 sept.) | fontaine et plates-bandes ↔ gazon pelé, bancs tagués |
| port | planches, béton | bornes, cargaison (livrés) | — |

- ⚠️ **Le sol neuf est une couche peinte, pas un glyphe.** Le peintre de morceau lit l'usage et
  le standing du bloc et choisit la texture ; `.` et `_` restent `.` et `_`. Aucun juge de
  circulation ne le voit passer — c'est la règle des devantures, et elle a tenu.
- **La carte plein écran peint le zonage** en calque (commercial, résidentiel, industriel,
  parc, eau), légende dérivée de la table des couleurs comme pour les lieux. C'est la seule
  façon de voir le zonage **avant** d'y marcher.

### 3e vague — les commerces montent et descendent (taille 1) — **livrée le 17 sept. 2026**

✅ **Ce qui est livré, et où ça s'écarte de la proposition ci-dessous :**

- **Tout se fait sur la ville FINIE** (`app/vitrines.py`, après le métro, avant la saleté). ⚠️ Le
  premier essai tirait les enseignes dans des catalogues par standing pendant la construction :
  un nom plus long élargit le bandeau (`poser_devanture` l'étire jusqu'à ce qu'il tienne), change
  la tuile de la porte peinte, le nombre de tirages de la pancarte et la famille qui ouvre sa
  porte la première — **dix juges tombés**, rampes et barrière du cargo comprises, sans qu'un seul
  parle d'enseigne. La passe finale ne tire aucun dé et ne touche aucune tuile ; un juge le tient
  (sans elle, la ville est la même hors des noms, des planches et des standings).
- **Les enseignes** : `devantures.COMMERCES_COSSUS` (seize) et `COMMERCES_PAUVRES` (douze). Une
  devanture d'un bloc cossu ou pauvre prend un nom de la **même famille** (la pièce derrière la porte
  reste la bonne) qui **tient dans le même bandeau**, loin de son double ; la porte qui s'ouvre prend
  le nouveau nom. Une famille sans nom de son standing garde le sien : le port garde sa poissonnerie,
  La Shop ses ateliers. Mesuré : 19 renommées.
- **À LOUER** : un commerce **fermé** sur cinq d'une rue pauvre (`vitrines.PART_A_LOUER`) — toutes
  ses vitrines placardées, sa lampe de vitrine retirée. Offert à la seule famille « commerce », il
  ne tombait jamais ; à toutes, il remplaçait chaque criée (huit locaux vides). Mesuré : 3.
- **La façade** : chaque devanture et chaque logement d'un bloc cossu ou pauvre porte `standing`
  (`+` ou `-`). En pauvre, une vitrine sur trois devient le motif `B`, tirée à la position
  (`carte.empreinte_de_tuile`) et **jamais au-dessus d'un guichet ou d'une machine** (ils sont
  encastrés dans la vitrine) ; le sol reste `W`. Le peintre : lettrage doré et auvent uni en cossu ;
  néon à moitié éteint, auvent déchiré, planches en pauvre ; jardinières, ou fenêtres placardées,
  drap et escalier rouillé pour les logements.
- **La nuit** (`mobilier.eclairer`) : un lampadaire sur trois **en panne** en pauvre (29 sur 69),
  et ceux des rues cossues **portent plus loin** (`PORTEE_COSSUE`, 60 px au lieu de 44).
  ⚠️ **Pas de poteaux « plus rapprochés »** : vingt-neuf lampadaires neufs au milieu des bords
  cossus changeaient le décor, donc les entités et les dés, et un juge d'autobus déjà fragile est
  tombé (voir « Qui attend l'autobus monte dedans »).
- **Les pièces** : `piece_de_commerce(standing=…)` — le comptoir d'un commerce pauvre barre les
  trois quarts de la pièce ; un commerce cossu a une plante de chaque côté de la porte, un pauvre
  aucune. Le contenu seul : ses mesures ne changent pas.
- **Reportés** : la grille de fer baissée la nuit et la vitrine cossue allumée toute la nuit —
  une devanture se peint UNE fois dans son morceau, et la faire changer avec l'heure demande de
  repeindre les morceaux à la brune.
- **Juges** (`test_quartiers.py`, 8 de plus, quatorze mutations toutes rouges) : aucune enseigne
  cossue en pauvre ni l'inverse, la façade suit le standing (une vitrine sur trois, jamais sur une
  machine), le local à louer ne s'ouvre ni ne s'allume, **les commerces montent sans rien déplacer**,
  la nuit se redistribue sans un poteau de plus, la pièce suit le standing, la façade se peint selon
  le standing, un lampadaire en panne n'éclaire pas. Et regardé dans Chromium.

_La proposition d'origine :_

- **Des enseignes par standing**, pas seulement par district (`devantures.COMMERCES`) : en
  cossu, BIJOUTERIE, FLEURISTE, BISTRO, GALERIE, TAILLEUR, CHOCOLATIER, BOUTIQUE DE VIN ; en
  pauvre, PRÊT SUR GAGES, ENCAISSEMENT DE CHÈQUES, BINGO, DÉPANNEUR 24 H, À LOUER. ⚠️ Le juge
  qui interdit de mélanger les noms entre districts s'étend au standing : aucune enseigne
  cossue dans un bloc pauvre, et l'inverse.
- **La façade suit** : en cossu, lettrage doré, auvent uni, vitrine éclairée toute la nuit ; en
  pauvre, néon à moitié éteint, auvent déchiré, une vitrine sur trois placardée (le motif `d`,
  condamnée, existe déjà), grille de fer baissée la nuit.
- **Les logements aussi** (`residences`) : balcons fleuris et fenêtres allumées ↔ fenêtres
  placardées, escalier de fer rouillé, drap tendu en guise de rideau.
- **La nuit dit le standing** : en pauvre, un lampadaire sur trois éteint ; en cossu, tous
  allumés et plus rapprochés. ⚠️ Le compte de lampes ne monte pas (361 aujourd'hui) : il se
  redistribue, comme la saleté.
- **Les commerces qui s'ouvrent** (un sur cinq) prennent une pièce selon le standing : un bistro
  n'a pas le comptoir d'un prêteur sur gages.

### 4e vague — le standing se vit (taille 1) — **livrée le 17 sept. 2026, reposée le 21 sept. 2026**

✅ **Ce qui est livré, et où ça s'écarte de la proposition ci-dessous :**

- ⚠️ **LIVRÉE, PUIS EFFACÉE, PUIS REPOSÉE.** Livrée le 17 sept. 2026 à 15 h 47 (`cde28f9`) ; 53
  minutes plus tard, un commit fait depuis l'éditeur, au message générique (`a5027b9`, « feat:
  Implement score tracking feature… »), a été fait depuis un arbre **plus vieux** : il a ramené le
  tableau des scores que Martin venait de retirer, et **effacé toute la vague** — le code, les
  juges et sa note du plan. Le tableau des scores est reparti le soir même (`d54c809`) ; la vague,
  personne ne l'a vue partir, et la table du plan disait « 3 vagues livrées » pendant quatre jours.
  Seule `Missions.gainDeFouille` avait survécu, qui lisait une table que le paquet ne portait plus
  (donc des tiroirs pareils partout). Reposée le 21 sept. 2026 sur le `dev` du jour, **le même
  code** : deux conflits seulement, résolus en gardant les deux côtés (le `au_volant` du cabriolet
  rose, né entre-temps, ne se gare toujours pas, et ce qui se gare lit le standing).
- **Qui marche** : `pietons.Pieton.standings` (une sorte sans standing va partout) se croise avec
  `districts` — touriste et joggeuse en cossu et ordinaire, ivrogne et pickpocket en pauvre.
  ⚠️ Le district se lit au JOUEUR (c'est sa bulle), le standing à la TUILE où la sorte se pose :
  deux blocs voisins n'ont pas le même. Et un juge exige que le croisement des deux existe
  quelque part — une sorte qui ne peut naître nulle part est une sorte morte (le premier essai
  mettait le touriste en cossu seul : ses quartiers sont les Quais et La Pointe, il n'y serait
  jamais né).
- **Ce qui est garé** : `vehicules.STANDING_DU_PARC` — `rares` (le haut de gamme peut-il naître
  ici ?) et `usure` (la carrosserie qu'il lui reste). Pas un char rare dans une rue pauvre ; les
  chars qui y naissent gardent 60 % de leur tôle, et le char porte sa marque (`usure`), ce qui
  distingue un char né minoune d'un char défoncé depuis. La fumée commence sous 50 % : une
  minoune ne fume pas en naissant, elle casse plus vite.
- **La police** : `recherche.STANDING` — `patrouille` multiplie ce que la zone veut d'agents
  (1,5 en cossu, 0,6 en pauvre), `depeche` le délai au bout duquel un témoin qui ne trouve pas
  d'agent téléphone (0,6 en cossu, 1,7 en pauvre).
- **L'argent** : `economie.FOUILLE_PAR_STANDING` — les tiroirs d'un logement rapportent 2,2 fois
  plus en cossu, 0,4 fois en pauvre. Le standing se lit DEHORS (`B.exterieur`) : dedans, on est
  dans une pièce, et une pièce n'a pas de quartier.
- ⚠️ **Pas d'épave sur des blocs** : une épave s'efface au bout de quarante secondes
  (`PHYSIQUE["epave_secondes"]`), elle ne peut pas décorer une rue. La minoune dit la même chose.
- **Reporté** : « la gang tient la rue ». Le territoire des gangs est une carte à part
  (`pietons.frontieres`) ; décider qui gagne entre elle et le standing vaut sa propre ligne.
- ⚠️ **QUATRE JUGES VOISINS NE TENAIENT QUE PAR LES DÉS**, et changer qui marche dans la rue les a
  fait tomber. Aucun ne parlait de standing, et chacun avait un vrai défaut :
  - « les cinq qui viennent avec » posait le témoin **par rapport au joueur** alors que son propre
    commentaire dit « à côté de l'ivrogne » — l'ivrogne venait de marcher cent soixante pas, il
    était à 191 px, hors du rayon de peur (sept tuiles). Il le pose maintenant à côté de l'ivrogne.
  - « une rixe qu'on ne voit pas ne s'entend pas » laissait la bagarre sept secondes hors champ :
    **un camp entier y passait**, et le juge mesurait le silence d'une bagarre finie. Cent
    cinquante images, et il écoute jusqu'à entendre.
  - « les cinq qui viennent avec » encore : il donnait 180 images à l'ivrogne pour tomber — mais un
    flâneur s'arrête tout seul une fois sur trois, pour 50 à 209 images, et `majIvrogne` ne regarde
    qu'un ivrogne **qui flâne**. Le juge le remet debout quand il s'arrête.
  - « le pont arrête les chars » conduisait à fond dans une ville vivante : **une seule caisse
    lointaine** le faisait rougir à la base. Il dégage son corridor, et il exige que la fiche de
    dégâts coûte quelque chose.
- ⚠️ **Et un cinquième, à la reprise** : « les tiroirs d'un logement ne se fouillent qu'une fois »
  (`test_interieurs_js`, refait le 20 sept. pour « on agit sur ce qu'on regarde ») bornait le gain
  à la fourchette d'avant la vague. Son premier logement est cossu : 120 $ pour un plafond de 60. Il
  lit maintenant le standing de l'adresse, dehors, et borne par la part du quartier.
- **Juges** (`test_quartiers.py`, 7 de plus) : qui marche dit le standing (et peut naître quelque
  part), l'ivrogne ne dort pas dans la rue chic, pas un char rare dans une rue pauvre, une minoune a
  moins de carrosserie (et le char cossu toute la sienne), la police arrive plus vite chez les riches,
  **le témoin téléphone plus vite chez les riches**, les tiroirs disent le quartier. ⚠️ Le septième
  est né de la reprise : sur dix mutations rejouées le 21 sept., neuf rougissaient, et **la dixième
  restait verte** — `police.js` pouvait oublier le `depeche` du témoin, le juge de la police ne
  lisait que la table Python et la patrouille. Il fait maintenant téléphoner un témoin par
  `Police.maj` sur une tuile cossue, une ordinaire et une pauvre, au même âge du crime.

_La proposition d'origine :_

Celle qui peut attendre : les trois premières font déjà ce que Martin a demandé. Celle-ci donne
au standing une **conséquence de jeu**.

- **Qui marche dans la rue** : touristes et joggers en cossu ; ivrognes en pauvre (et le
  pickpocket quand M12 le fera). Les sortes ont déjà leurs `districts` : elles gagnent un
  standing.
- **Ce qui est garé** : les `rares` passent du district au standing — une décapotable dans la
  rue chic du Faubourg, pas devant le prêteur sur gages ; en pauvre, des chars bosselés et une
  épave sur des blocs.
- **La police et l'argent** : en cossu, la police arrive plus vite et la fouille d'un logement
  rapporte plus ; en pauvre, la police tarde, la gang tient la rue et il n'y a presque rien à
  prendre. Voler chez les riches paie, et ça se paie.

⚠️ **Les leçons à relire avant d'y toucher** — toutes payées cher dans ce fichier :

- **Chaque semis dans son propre dé.** Un semis de saleté qui tire un dé de plus dans le dé
  commun rebat toute la ville (le 16 sept., dix juges sont tombés sans qu'un seul parle de
  terrain vague — voir `des_dechet` et `Des.brule`). Le standing, lui, est **écrit** : il ne
  consomme aucun dé.
- **Comparer les deux villes en JSON, clé par clé**, avant et après : hors des objets semés par
  standing, **rien** ne doit bouger. Une tuile réservée de plus fait glisser la ville.
- **Un décor solide passe par `DECOR_SOLIDE` et `degager_le_decor`** : un trottoir pauvre plein
  de sacs reste un trottoir qu'on marche, et un bac à fleurs ne ferme pas une porte.
- **Une devanture reste une couche peinte** : zéro solidité touchée.

**Juges** : chaque bloc bâtissable déclare son standing (pas de défaut silencieux) ; le
Faubourg, les Quais et La Shop ont chacun au moins deux standings ; **zéro** déchet, graffiti
et nid-de-poule en cossu, et en pauvre au moins cinq fois la densité de l'ordinaire ; le
**total** de saleté et de lampes ne dépasse pas celui d'avant ; aucune enseigne cossue en
pauvre, ni l'inverse ; la grille de glyphes est identique avant et après la 2e vague ; hors des
objets semés par standing, la ville est la même tuile pour tuile ; aucune poche fermée à pied ;
et le paquet reste sous son plafond.

## Notes

demande de Martin : « je veux des cartiers plus reconnaissable, plus riche et propre avec
des commerce plus riche, des cartiers plus pauvre et sale. commercial, indistriel,
résidentiel, parc, etc.. ».

- ⚠️ **Mesuré (16 sept. 2026) : le zonage existe, le standing n'existe pas, et la rue ne dit
  ni l'un ni l'autre.** L'usage est déjà décidé au bloc par les lettres du `plan` (`c`
  commerces, `h` maisons, `m` banlieue, `w` hangars, `i` industriel, `p`/`k` parc, `q`/`j`
  quai) ; mais « riche » ou « pauvre » n'apparaît **nulle part** dans `app/`, et le
  contraste qu'on voit est un accident de genre : 131 sacs, pneus, barils et débris, dont
  **4** aux Érables et **61** à La Shop — uniformes à l'intérieur d'un district. **Un seul
  trottoir et un seul abord pour toute la ville** ; La Shop a 22 arbres, les Quais plus de
  poubelles que le centre-ville, la banlieue autant de nids-de-poule que le Faubourg. Deux
  axes qui se croisent : l'**usage** (ce qu'on fait là) et le **standing** (`cossu`,
  `ordinaire`, `pauvre` — qui en a les moyens). Quatre vagues : **le standing se déclare**
  (une grille écrite à la main à côté du `plan`) **et la saleté se déplace** — ⚠️ **sans que
  son total monte** : Martin a renvoyé « trop de saleté partout » le jour même ; **le zonage
  se lit** (sol et mobilier par usage en couche peinte, calque sur la carte) ; **les
  commerces montent et descendent** (enseignes, façades, logements et lampes par standing) ;
  **le standing se vit** (qui marche, ce qui est garé, la police et l'argent).
- ⚠️ Passe **après les bancs et les arbres de rue** (en cours) : c'est le même semis. Détail
  dans « Des quartiers qu'on reconnaît » plus bas.

✅ **1re vague livrée** (17 sept. 2026) : une **grille de standing** écrite à la main à côté
de chaque `plan` (`+` cossu, `=` ordinaire, `-` pauvre, `~` l'eau), validée au chargement
(un bloc avalé dit ce que dit son maître, pas de défaut silencieux) et portée par le paquet
(`grille.standing`, douze lignes — le gzip est à mille octets de son plafond), lue par
`Monde.standingA`. **`app/salete.py`** déplace la saleté après les lignes d'autobus et avant
le mobilier : **cossu 30 → 0, ordinaire 40 → 16, pauvre 159 → 213**, total inchangé (234) —
les déchets reposés vont au pied des murs (sacs, gravats, pneu, **matelas**, **caddie
renversé**), la **poubelle déborde** en pauvre (la même, 65 sur 145).

- ⚠️ **L'ordinaire garde une saleté sur deux, pas toutes** : vider le cossu seul laissait le
  pauvre à 4,1 fois l'ordinaire par tuile ; il est à 11,5. **Le propre se voit** : pas un
  arbre de rue en pauvre, la rue chic du Faubourg plantée 2,5 fois plus serré que ses rues
  ordinaires, **31 bacs à fleurs** en cossu. Comparée en JSON clé par clé à la ville
  d'avant : rien d'autre ne bouge.
- ⚠️ **Un district neuf doit déclarer son standing** (`DISTRICTS[].standing`), sinon la
  ville ne se charge pas. 18 juges (`test_quartiers.py`), chacun vu rouge sans sa règle.
- ⚠️ **Et un faux positif du chien de garde du trafic, corrigé en passant** : un char resté
  600 images au feu (légitimement) repartait, et la comparaison « dix secondes au même
  endroit » tombait juste après — téléporté au milieu de la voie. La ville neuve le faisait
  tomber sur la graine 5 de `test_trace_js` (2 graines sur 40, 0 sur 80 à la base) ; une
  attente légitime remet maintenant l'ancrage à zéro (`Vehicules.debloquer`), 40 graines sur 40.

✅ **2e vague livrée** (17 sept. 2026) : l'usage de chaque bloc **se déduit du plan**
(`carte.USAGES`, `grille.usage`) ; le trottoir et l'abord se peignent selon l'usage et le
standing (granit lavé en rue chic, béton d'usine taché, **bande de gazon** tondue ou brûlée
devant les maisons, asphalte devant les entrepôts) — une couche peinte, pas une tuile ne
change ; **129 meubles d'usage** (40 parcomètres, 21 boîtes aux lettres, 12 bacs de recyclage,
39 palettes, 17 bennes) ; la carte plein écran porte le **calque de zonage** et sa légende.

- ⚠️ **Les légendes de la carte s'affichaient dans l'ordre alphabétique** : le paquet trie
  ses clés, et le juge des familles relisait ce paquet trié — un `rang` voyage maintenant
  avec chaque table.
- ⚠️ **Un vélo poussait l'autobus dans le carrefour.** Le trafic qui perd patience force le
  passage ; entre deux chars du trafic rien ne bouge (« sur des rails »), mais l'autobus d'une
  ligne n'y était pas compté, et un vélo impatient le poussait pendant qu'il attendait le feu.
  `test_autobus_js` tombait sur 3 graines sur 20 **à la base** (le nez dans le carrefour, ou
  hors du tracé), et la ville neuve l'a fait tomber sur la sienne. Ligne et trafic ne se
  poussent plus : 20 sur 20, à la base comme avec la vague.
- Restent la 3e vague (les commerces montent et descendent) et la 4e (le standing se vit).

✅ **3e vague livrée** (17 sept. 2026) : **sur la ville finie**, `app/vitrines.py` renomme
les enseignes des blocs cossus et pauvres — seize noms cossus, douze pauvres, toujours de la même
famille et dans le même bandeau —, placarde **43 vitrines** et vide **3 locaux À LOUER** ; les
façades portent leur standing (lettrage doré et auvent uni ↔ néon à moitié éteint, auvent déchiré,
planches ; jardinières ↔ fenêtres placardées, drap, escalier rouillé). **29 lampadaires en panne**
en pauvre, et ceux des rues cossues **portent plus loin** (60 px au lieu de 44). Un commerce pauvre
qui s'ouvre a un comptoir qui barre la pièce, un cossu deux plantes à l'entrée.

- ⚠️ **Tirer les noms pendant la construction a fait tomber dix juges** : un nom plus long élargit
  le bandeau, déplace la porte peinte et décale le dé des devantures — rampes perdues, barrière du
  cargo déplacée. D'où la passe finale, qui ne touche ni une tuile ni un dé.
- ⚠️ **Et pas un poteau de plus** : vingt-neuf lampadaires neufs en cossu décalaient les dés de la
  ville, et le juge d'autobus « qui attend monte » est tombé — il ne tient que par sa graine
  (voir « Qui attend l'autobus monte dedans »).
- Reste la 4e vague : le standing se vit (qui marche, ce qui est garé, la police et l'argent).

✅ **4e vague livrée — le jalon est complet** (livrée le 17 sept. 2026, effacée le jour même par un
commit d'éditeur, reposée le 21 sept. 2026) : le standing a des conséquences de jeu. **Qui marche** :
touristes et joggeuses en cossu et ordinaire, ivrognes et pickpockets en pauvre
(`pietons.Pieton.standings`, croisé avec `districts`, lu à la TUILE où la sorte se pose). **Ce qui
est garé** : pas un char rare dans une rue pauvre, et les chars qui y naissent sont des minounes
(60 % de carrosserie — ça se sent au premier poteau). **La police et l'argent** : une patrouille et
demie en cossu contre six dixièmes en pauvre, un témoin qui téléphone presque deux fois plus tard
en pauvre, et les tiroirs d'un logement qui rapportent 2,2 fois plus en cossu, 0,4 fois en pauvre.
Voler chez les riches paie, et ça se paie.

- ⚠️ **Un commit d'éditeur fait depuis un arbre périmé efface sans bruit** : `a5027b9` (17 sept.,
  16 h 40) a emporté la vague 53 minutes après sa livraison, et rien n'a rougi — ses juges
  partaient avec elle. Le témoin qui l'a dit, quatre jours plus tard : `git log -S` sur un nom de
  la vague (`STANDING_DU_PARC`) rendait deux commits, l'ajout et la suppression. Avant de refaire
  une vague « à faire », chercher si elle n'a pas déjà existé.
- **Pas d'épave sur des blocs** (une épave s'efface en quarante secondes) ; **reporté** : « la
  gang tient la rue » en pauvre, qui vaut sa propre ligne.
