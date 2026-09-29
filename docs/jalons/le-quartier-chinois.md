# Le quartier chinois : le Petit-Canton, un 7e district

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

**Tranché avec Martin (26 sept. 2026)** : « un grand quartier bien défini. Au nord. Missions avec donneur. »
Les noms, il me les a laissés :

- **Le quartier : le Petit-Canton** (slug `canton`). Canton, la ville du Sud de la Chine d'où viennent bien
  des vieux quartiers chinois ; et au Québec, un canton est aussi un coin de pays (les Cantons-de-l'Est). Le
  nom joue sur les deux, sans rire de personne.
- **Le gang : les Mantes** (slug `mantes`, piéton `mante`) — les élèves de l'école de la Mante religieuse, un
  vrai style de kung-fu du Sud, qui ont mal tourné. Un nom d'animal au pluriel, comme les Morues et les
  Chevreuils ; ni « grue » (la grue des chantiers existe), ni rien qui nomme une origine.
- **La place : au NORD** de la ville — la carte s'allonge par le haut (l'aéroport l'a allongée par le bas).
  ⚠️ Tout ce qui compte en y depuis le haut de la carte (la caméra, `Monde.lettreDuBloc`, les rangées de la
  trame lues par index) se décale si on insère des rangées au-dessus : à mesurer avant de choisir entre
  décaler la trame vers le bas (une translation, pas un nouveau tirage) et un plan posé au-dessus.
- **La taille : grand, bien défini** — un vrai quartier qu'on reconnaît d'un coup d'œil : son arche aux
  entrées, ses lanternes, ses enseignes, ses couleurs de trottoir ; pas trois rues de décor.
- **Des missions, avec un donneur** : un personnage du Petit-Canton (sa fiche dans `docs/personnages/`, sa
  voix, il se nomme une fois dans sa salutation) et sa série de missions — « Une mission s'ajoute comme un
  bloc Lego ». Qui il est, et ce qu'il raconte : au brainstorming du jalon.

**Le découpage (Martin, 26 sept. 2026)** : quatre étapes, chacune livrée seule.
1. [La ville s'agrandit au nord](la-ville-s-agrandit-au-nord.md#fiche) : toute la ville descend de 110 rangées ; la
   bande libérée est une deuxième ville bâtie par le même générateur (sa trame, sa graine), avec les Friches
   au-dessus des Érables, la Gare de triage au-dessus de La Shop et, au-dessus du Faubourg, les rues du Petit-Canton
   autour de terrains à bâtir.
2. Le Petit-Canton : ses bâtiments sur ces terrains, ses devantures, ses lanternes, son arche et son bus.
3. Le donneur et ses missions.
4. [Les Mantes](l-ecole-rivale.md#fiche).

⚠️ Ce qui précède sur « la recette de l'aéroport » a été dépassé : Martin a choisi la translation et la deuxième
ville générée (l'approche A), et non un plan dessiné.

**Juges** : la ville d'avant identique à la tuile près (comparer les deux villes en JSON, clé par clé) ; le
quartier atteignable à pied et au volant ; le gang naît chez lui et se bat à sa frontière ; aucun dé consommé
par la pose ; les juges de la carte à la nouvelle taille.

## Notes

### Étape 2, vague A — les bâtiments, les enseignes et leurs plaques — **livrée le 27 sept. 2026**

Tranché avec Martin le 27 sept. 2026 : **« rue principale + place »**, des enseignes **« avec idéogrammes
stylisés »**, et l'étape 2 en **deux vagues** (A : les bâtiments et les enseignes ; B : les lanternes, l'arche et
le bus).

- **Les 56 terrains à bâtir sont bâtis** par le même générateur, avec les lettres de plan ordinaires (`c`
  commerces, `h` logements, `o<` la place) : `nord.DISTRICTS_NORD`, district `canton`. La rue principale descend
  entre la 4e et la 5e colonne d'îlots jusqu'à la couture — c'est elle que l'arche ouvrira (vague B) ; la place
  du marché est à son flanc est, au cœur du quartier. Des logements tout autour. Le standing mêle le cossu de
  la rue et le pauvre des bords (auvents déchirés, vitrines placardées).
- ⚠️ **Chaque îlot a SES dés** (`nord._ChantierNord._a_ses_des`) : tous les flux du chantier (`des`,
  `des_devanture`, `des_toit`…) sont remplacés le temps de l'îlot par un dé de `GRAINE_CANTON`, mêlé à la
  position de l'îlot et au nom du flux (`crc32`). Bâtis avec les dés de la bande, les îlots en auraient mangé
  des milliers, et tout ce qui se tire après eux dans les Friches et la Gare aurait bougé. **Mesuré : la ville
  entière, hors du rectangle du canton, est identique à l'unité près** (sol et objets, comparés en JSON), et
  un juge le tient contre une bande témoin dont le canton est resté en terrains à bâtir.
- **Ses enseignes** : `devantures.COMMERCES["canton"]`, 38 noms français avec un nom de famille cantonais en
  lettres latines — JARDIN DE JADE, DIM SUM LOTUS, MARCHÉ KAM FUNG, HERBORISTE CHAN, NOTAIRE LEUNG, SOIERIE
  MEI, CLUB MAH-JONG… Quinze caractères au plus : c'est ce qui tient dans un bandeau de quatre tuiles
  (`tient_en`), et sept noms de seize ont été raccourcis. L'école de kung-fu n'y est pas (étape 4).
- **Les plaques verticales** : chaque commerce du quartier (et lui seul) porte `ideo`, l'index d'une paire de
  `devantures.PAIRES`, choisi à la position de la devanture (aucun dé). Le peintre (`FACADES.plaqueVerticale`)
  pend une plaque rouge au cadre doré au bout de la devanture, sous l'enseigne, avec deux **vrais
  caractères** de cinq pixels sur cinq (中 山 大 米 日 月 王 : Zhongshan, le riz, le soleil et la lune, le grand
  roi) plutôt que des traits au hasard. ⚠️ Vu à la capture, grossie huit fois : collés au cadre, les
  caractères s'y fondaient — la plaque fait 9 × 15, un pixel de rouge autour de chacun.
- **Juges** : `tests/test_canton.py` (le quartier a ses commerces, ses logements et sa place ; ses enseignes
  sont les siennes et tiennent ; la plaque au canton et nulle part ailleurs ; **la bande ne bouge pas**) et
  `tests/test_canton_js.py` (le peintre pose la plaque — témoins : la même devanture sans `ideo`, et une de la
  ville d'avant). Deux mutations rouges : sans les dés propres, le décor de la bande bouge ; sans l'appel au
  peintre, pas de plaque. `test_nord` juge maintenant un canton bâti, sans une pancarte « À BÂTIR ».
- ⚠️ **Ce que la suite a trouvé** (onze fichiers rouges, départagés un à un contre `dev` nu) :
  - **Le renommage `nord_` oubliait ce que les pièces se disent entre elles** : le `slug` de chaque pièce, et
    le `vers` de ses escaliers. Un logement à étage du quartier montait à l'étage de `logement_27` de la ville
    d'avant — un 7 × 5 au-dessus d'une cabane de 3 × 3 (`test_carte`, `test_interieurs`). La bande n'avait
    encore aucune pièce à étage : le défaut dormait. `batir_la_bande` renomme les deux.
  - **Le terrain vague de la ville** peut poser sa trouée contre un coin (une clôture droite qui ne tourne
    jamais) : le quartier prend celui de la bande, et sous six tuiles de large sa trouée n'a qu'une tuile.
  - **Les portes du quartier donnent sur la couture**, où `devants.deplacer` (passé avant la bande) n'a rien
    vu : un bris d'aqueduc de la ville d'avant y tombait devant une porte (graine 1). `nord.poser` MARQUE
    (`ecartee`) ce qui tombe devant les portes de la bande ; le juge des listes tirées ôte le drapeau des deux
    côtés, puisque le témoin pose la bande lui aussi.
  - **« Les portes s'alignent »** : 29 portes dans 149 colonnes, plus serrées que la ville (21 colonnes, contre
    ~26 au hasard). Le juge de la ville garde la ville d'avant ; le quartier a le sien (deux tiers de colonnes
    distinctes, jamais plus de trois portes dans une colonne).
  - **Le Petit-Canton est dans la bulle de naissance du terminus** : dès la première image, les passants et
    les chars naissent ailleurs (compté : les appels à `B.rng` divergent à l'image 1, dans `placeDeNaissance`
    et `placeDansLeTrafic`). Deux juges qui tenaient par ce hasard sont tombés : **f09** (une remorqueuse garée
    en travers de la route du Cravate — 11 graines sur 12 passent, sur la base comme ici ; le juge ôte
    maintenant le trafic devant le char suivi) et **la course de motoneige** (la dette de la bande : graine 5,
    une des cinq sur 24 qui gagnent). ⚠️ **Chaque vague du quartier rebattra ce hasard**, la B comprise.
  - Pas de moi, rouges aussi sur `dev` nu : `test_carte_du_depot` (un `test_garage.py` d'une autre session),
    `test_passage_pietons`, `test_techniques_js`, `test_police_js`.
- **Reste, vague B** : les lanternes au-dessus des rues, l'arche aux entrées (la rue principale à la couture
  d'abord), le bus du Petit-Canton ; peut-être la couleur des trottoirs.

### Étape 2, vague B (1re partie) — l'arche et les lanternes — **livrée le 27 sept. 2026**

- **L'arche** (`app/canton.py`, posée en tout dernier par `nord.poser`, sans un dé) : au bout sud de la rue
  principale, à deux rangées de la couture — c'est elle qu'on voit en montant du terminus. Deux **piliers**
  sur les trottoirs (`pilier_arche` : un décor solide qui arrête un char et n'encaisse pas les balles), et,
  au-dessus des gens (`static/js/canton.js`, peint après les entités comme la fumée des cheminées), un
  linteau rouge, un toit de tuiles vertes aux coins relevés et un panneau d'or : 中山, Zhongshan, le nom de
  mille rues. ⚠️ Le toit n'est PAS du décor : trié à son pied, on serait passé devant lui.
- **Les lanternes** : une corde toutes les cinq rangées, d'un trottoir à l'autre de la rue principale, au-dessus
  des rangées d'îlots seulement (jamais d'un croisement, où elles cacheraient les feux) — quatorze cordes. Les
  lanternes se balancent d'après `B.t`, sans dé. La nuit, chaque corde a sa **lueur rouge** (une sorte de lampe
  neuve, `lanterne`, dans `Monde`) ; vues de nuit à la capture.
- ⚠️ **Seulement en ville** : dans un bloc, `Monde.carte` est le bloc (le piège du chalet) — `Canton.donnees`
  ne rend rien dès que `B.bloc` ou `B.interieur`.
- **Juges** : `test_canton.py` (l'arche ouvre la rue principale, ses piliers solides sur les trottoirs et hors
  du devant des portes, la chaussée libre entre eux ; les cordes au-dessus de la rue, jamais d'un croisement,
  chacune sa lueur) et `test_canton_js.py` (le toit et les lanternes se peignent quand la caméra est dessus,
  rien ailleurs ni dans une pièce — le témoin ; la lueur est rouge). Deux mutations rouges.
- **Reste** : **le bus du Petit-Canton**. ⚠️ Mesuré avant d'y toucher : une 4e ligne au bout de
  `autobus.LIGNES` garde le tracé des trois autres, mais ses abribus et ses bancs s'insèrent dans
  `ville["decor"]` avant le métro et le mobilier (tous les numéros d'entités qui suivent glissent) et les
  arrêts sont renumérotés par position (`combienAttendent`, `B.abribusServis` en dépendent). À poser hors de
  la suite (`enDehorsDeLaSuite`, comme la bande) et avec des identifiants d'arrêt stables.

### Étape 2, vague B (2e partie) — le bus, la ligne 4 — **livrée le 29 sept. 2026**

- **La ligne 4, « Le Petit-Canton »** (rouge, `app/bus_du_canton.py`) : du terminus, le long du boulevard de la
  couture (elle y prend trois arrêts qui existent), la 12e Avenue jusqu'au casino du Dragon d'or, et retour par la
  rue principale, sous l'arche. Deux autobus.
- ⚠️ **Tracée APRÈS la bande, sur la carte finie**, avec les MÊMES outils que les trois autres (`autobus._Reseau`,
  `_boucle`, `arret_possible`) : un petit adaptateur (`_SurLaVille`) leur donne ce qu'ils lisaient d'un chantier
  — le sol, ce qui occupe une tuile, le devant des portes. Rien des trois lignes d'avant ne bouge (jugé contre la
  ville sans elle) : **ses arrêts neufs prennent les numéros SUIVANTS** (51 à 55 : aucun renuméroté — le
  navigateur tire à l'empreinte d'un numéro d'arrêt), **ses abribus et ses bancs s'ajoutent au bout du décor**,
  dans la bande. Au terminus, elle prend l'arrêt qui existe.
- **Ses autobus naissent hors de la suite des numéros d'entités** (`a_part`, lu par `Autobus.faireNaitre`), et
  les voyageurs de ses abribus aussi : elle longe la couture, dans la bulle de naissance du terminus.
- ⚠️ **Ses noms** : « 3e Rue / 10e Avenue » existe aussi dans la ville d'avant ; ses arrêts se nomment dans la
  trame de la BANDE, préfixés (« Petit-Canton, 12e Avenue / 4e Rue ») — deux arrêts du même nom, c'était rouge
  (`test_autobus`).
- **Juges** : `test_bus_du_canton.py`, `test_bus_du_canton_js.py` ; une mutation rouge (les autobus nés dans la
  suite). L'étape 2 est livrée.

### Étape 3 (1re partie) — le donneur et sa première mission — **livrée le 29 sept. 2026**, avec [le tripot du casino](le-casino-du-petit-canton.md#vague-4--le-tripot-du-sous-sol--la-barbotte-du-pouce--livrée-le-29-sept-2026-martin--va-y)

Proposé par Claude (la fiche laissait le donneur au brainstorming ; Martin : « va y ») — **validé par Martin le 29 sept.
2026** (« oui », et : on fait tomber le Pouce pour de bon) :

- **Le donneur : Irène Lam** (slug `irene`), 68 ans, née au-dessus de la boulangerie de ses parents, rue principale ;
  trente ans croupière au Dragon d'or, retraitée ; la reine du mah-jong du quartier (les vieux du CLUB MAH-JONG lui
  ont interdit de miser). Joueuse ET honnête : elle gage sur tout (« je gage cinq piasses que… »), appelle le neveu
  « mon pigeon », et ne supporte pas qu'on dise « j'ai pas de chance » — « La chance, ça existe pas, y a juste du monde
  qui sait compter ». ⚠️ Le ton : elle parle le joual du quartier, elle est d'ici depuis soixante-huit ans ; le drôle
  est dans ce qu'elle dit (les gages, l'œil de croupière), jamais dans sa façon de le dire ni dans son origine. Fiche :
  [`docs/personnages/irene.md`](../personnages/irene.md).
- **Sa place : au bout du bar du Dragon d'or** (`point:irene`, dedans) — elle vient chaque soir « surveiller le
  travail des jeunes ». Dedans, et c'est voulu : un donneur de plus DEHORS naîtrait au démarrage, dans la bulle de
  naissance du terminus (un numéro d'entité de plus, le hasard du départ rebattu) ; dedans, elle naît quand on entre.
- **Sa voix : Meera - Friendly and Conversational** (libre ; vérifiée « quebec » en multilingue v2, jamais en v3 — à
  écouter). Plus aucune Québécoise d'origine n'était libre (Luna, la seule, est jeune et méditative) ; Martin a permis
  les multilingues (25 sept. 2026).
- **Le méchant : le Pouce** (Réal Vachon), qui a loué la cave du casino « pour entreposer des chaises » et y fait
  rouler une **barbotte** aux dés pipés — un escroc d'ailleurs, pas un homme du quartier ; ses rabatteurs sont des
  **Cravates** qu'il paie, ses gros bras sont à lui. Les Mantes (étape 4) n'y sont pour rien.
- **Sa mission : c01, _La barbotte du Pouce_** — elle ouvre la porte du tripot. La suite de l'étape 3 (faire tomber
  le Pouce ? les voisins plumés, le vieux Chan, la boulangère ?) reste à écrire avec Martin.
- **Les voix** : les dix répliques de c01 et les deux repos d'Irène, générées le 29 sept. 2026 (eleven_v3).

### Étape 3 (2e partie) — la chute du Pouce — **livrée le 29 sept. 2026**

Martin, 29 sept. 2026 : Irène validée (« oui »), et « on fait tomber le Pouce pour de bon ». Trois missions de plus,
chacune avec son intention — la preuve, l'argent, la chute — et jamais deux fois la même mécanique ; c01 était la
bagarre, l'arc n'en a plus qu'une petite, au bout d'une poursuite.

- **c02, _Une paire dans la manche_** (500 $, `exige` 500 $ en poche : le Pouce ne pipe pas en dessous) — Irène veut
  ses dés DANS SA MAIN. Elle te donne une paire honnête ; au sous-sol, quand le Pouce pose ses pipés, le menu offre
  **GLISSER TES DÉS** : les siens dans ta manche, les tiens sur le feutre, le coup se joue honnête. Un `obtenir` dont la
  `table` est le tripot (`tripot.PREUVE`) : l'objet ne se pose nulle part en ville (`Infiltration` le sait), et
  l'objectif avance à la sortie. Parler à Irène pendant l'objectif : elle renvoie au sous-sol (`renvoi`). Pendant la
  mission, ni la semaine barrée ni la limite du jour ne ferment la table.
- **c03, _La suite royale_** (600 $) — « un tricheur écrit tout ce qu'il gagne ». On fait jaser **Norbert** à l'hôtel
  (sa poignée de main, deux répliques : il ne dit pas le nom de son client, il vend le reste) ; on **file le comptable**
  du Pouce jusqu'au terminus (`suivre`) ; le livre (un registre) attend à la porte du terminus, **trente secondes**
  avant que les rabatteurs passent le prendre (`obtenir` + `chrono_s`). ⚠️ La suite royale, pas la chambre 12 : c'est
  celle de q07, en brouillon sous `refs/wip/m16-q07`.
- **c04, _La barbotte change de mains_** (1 500 $) — le Pouce vide la caisse (« la paye du quartier ») : son chauffeur,
  une Cravate qu'il paie mal, file EN CHAR de la porte du Dragon d'or (`ramasser`, `fuyard`) ; on l'accroche, on
  reprend la caisse, et le Pouce — qu'on entend enfin, une fois, en se sauvant — prend l'autobus de Sorel. On la
  rapporte au Dragon d'or.
- **Ce qui change dans le monde quand le Pouce tombe** (`tripot.REPRISE`, `apres: c04`) : au sous-sol, plus de Pouce
  ni de gros bras, et plus de gros bras à la porte d'en haut ; **le vieux Chan** (celui qui y avait laissé sa pension)
  tient la barbotte pour Irène — « ICI, LES DÉS SONT BLANCS. » ; le menu devient **LA BARBOTTE DU QUARTIER** : jamais de
  pipés, plus de méfiance ni de semaine barrée, plus rien à dénoncer, la piastre « AU QUARTIER ». Le lendemain matin, le
  Clairon titre **LE POUCE PLIE BAGAGE** (`donne.manchette`, `journal.SPECIALES`, lu par le narrateur).
- **Le Pouce parle** : un personnage de plus, `pouce` (Réal « le Pouce » Vachon, `ou` vide comme le client du taxi ;
  son visage, `visages.VISAGES`), voix **Callum - Husky Trickster** (libre, un français « d'ailleurs » ; en v3, à
  écouter). Fiche : [`docs/personnages/le-pouce.md`](../personnages/le-pouce.md).
- **Petit correctif en passant** : le fuyard d'un `ramasser` annonçait « LE FUYARD FILE EN MOTO ! » même en auto (m5,
  m50, m97…) ; il dit maintenant « EN CHAR » quand c'en est un.
- **Les voix** : 37 fichiers générés le 29 sept. 2026 (eleven_v3) — les 30 répliques d'Irène de c02 à c04, les deux de
  Norbert, celle du Pouce, et la manchette du narrateur ; trois refaites après le passage de la chambre 12 à la suite
  royale. ≈ 4 100 caractères, **1 930 crédits** (compteur ElevenLabs : 30 580 → 32 510).
- **Juges** : `tests/test_chute_du_pouce_js.py` (5, joués au bouton) — c02 de la poignée de main à la prime (avant la
  mission, rien à glisser ; pendant, GLISSER TES DÉS ; rien de posé en ville) ; c03 de Norbert au livre ; le chrono du
  livre qui mord ; c04 jusqu'au monde d'après (plus de Pouce ni de gros bras, le vieux Chan et sa bulle, le titre, 200
  coups à 1 000 $ sans un pipé malgré une méfiance à 150 et une semaine barrée) ; et le témoin, la même partie avant et
  après c04. Quatre mutations rouges (la reprise oubliée dans `miser`, l'objet de table posé en ville, GLISSER hors de
  la mission, le Pouce qui revient au sous-sol). Voisins : `test_missions` (un objet de table vient du tripot),
  `test_mise_en_scene` (le renvoi d'Irène compté).

### Étape 4 — les Mantes — **livrée le 29 sept. 2026**

Le gang du quartier, et l'école dont il sort : tout est dans [l'école rivale](l-ecole-rivale.md#notes). En bref :
l'**ÉCOLE LA MANTE** reprend la CAISSE POP, au nord-ouest du quartier, loin de la rue principale et du casino
(`mantes.py`, posée par `nord.poser` sans un dé) ; le district passe aux Mantes (il avait les Cravates du voisin du
sud en les attendant), leur territoire est le coin de l'école, et leur frontière la couture, face aux Cravates. Ils se
battent avec le répertoire — pieds, projections, parade —, plus durs que tous les autres gangs, et c'est jugé.
⚠️ Le ton tenu : le quartier est à ses habitants, l'école est une adresse, le gang ce sont ses élèves ; dans
l'histoire d'Irène (c01 à c04), les Mantes n'y sont pour rien.

**Les quatre étapes sont livrées.** Ce que la fiche laissait ouvert : la musique du quartier (« à revoir avec
Martin »), la couleur des trottoirs (« peut-être »), et une mission des Mantes (l'école rivale, vague 2 à trancher).

**La musique du quartier : livrée le 29 sept. 2026, demandée par Martin** — `amb_canton`, « Lanternes du
Petit-Canton », et les Mantes qui défient à mains nues chez elles : [les Mantes provoquent, et le Petit-Canton a sa
musique](les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md#notes).

### L'arc du vieux maître — c05 à c08 — **livré le 29 sept. 2026**

Martin a tranché la mission des Mantes : « les deux ». Irène appelle en Floride (c05, le droit de table au mah-jong),
et **Victor Tam**, le vieux maître de l'ÉCOLE LA MANTE, revient reprendre ses élèves un par un — Kenny chez Gus (c06),
Monsieur Bois à la fourrière et une technique en échange (c07), les portes ouvertes jusqu'au Dragon d'or (c08). Après
c08, **l'école rouvre ses cours** : les élèves font face au maître dans la salle, beaucoup moins de Mantes traînent
dans la rue, et le gang est calme. Tout est dans [l'école rivale, vague 2](l-ecole-rivale.md#vague-2--le-vieux-maître-revient-de-floride--livrée-le-29-sept-2026).

**Le Petit-Canton est livré le 29 sept. 2026** : ses quatre étapes, la musique, le défi des Mantes et l'arc du vieux
maître. Reste seulement, si Martin le veut, la couleur des trottoirs (« peut-être ») — elle n'a pas de ligne.
