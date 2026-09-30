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

### La suite (30 sept. 2026 — Martin choisit l'ordre)

1. **La carte plus visible l'hiver** (petit, d'abord) : la carte blanche se perd sur la neige — un contour,
   une couleur ou un éclat d'hiver, regardé en capture sur la neige, le jour ET la nuit.
2. **Les bebelles** (vague 3) : douze curiosités québécoises cachées, posées sur une étagère de la planque
   une fois trouvées ; même règle de pose que les cartes, sans dé.
3. **Les sauts** (vague 4) : vingt rampes au volant à découvrir ; un saut réussi se compte (vitesse,
   distance, atterrissage), une prime et un compte au carnet.
4. **Le marché aux puces du dimanche** ([sa fiche](le-marche-aux-puces-du-dimanche.md#fiche)).

⚠️ Le paquet des définitions n'a plus de marge (7 octets gzip au 30 sept.) : rien de neuf n'y entre, ni dans
la carte — tout passe par `/api/collections`.

## Notes

### Vague 1 — les cartes de hockey (✅ livrée le 30 sept. 2026)

- **Le catalogue** : `app/collectionner.py` — quarante cartes (`CARTES`), cinq par district de terre, chacune
  un numéro stable (le nom qu'en garde la sauvegarde), un joueur, une position, deux lignes de dos. La n° 1
  est Gilles « La Toque » Bouchard (la statue du parc), la n° 23 le petit-fils du buste d'Omer Gauthier, la
  n° 32 le neveu d'Irène Lam, la n° 40 l'organiste de l'aréna. Huit équipes et leurs deux couleurs
  (`EQUIPES`).
- **Les places** : `collectionner.poser`, appelé tout au bout de `carte.generer` (après les frénésies), sans
  un dé. Dans chaque district : un recoin (ruelle, friche, herbe, quai) d'au moins trois murs sur huit — un
  cran de moins s'il en manque —, à dix tuiles au moins des autres cartes et à six des paquets et des
  frénésies, jamais dans une cour de gang ni autour d'un chantier, rejoint à pied depuis la planque **toutes
  barrières piétonnes fermées**. Les plus encaissés d'abord, puis le plus loin possible des cartes déjà
  posées ; l'égalité en ordre de lecture. Ce que ça donne : le fond des ruelles d'herbe entre deux toits du
  Faubourg et du Canton, les coins de friche derrière les grillages de la Shop et des Friches, le bout des
  quais, et la friche entre deux cabanes du bidonville de la Gare. La ville d'avant la bande nord n'en a que
  vingt-cinq.
- **Le poids** : presque rien dans les définitions (l'empreinte : 58 990 gzip sur 59 000) et rien dans la
  carte — tout part sur `/api/collections` (8 249 bruts / 3 218 gzip), **sons compris** : les définitions
  étaient à 27 octets gzip de leur plafond sans rien de nous, et les deux bruitages et leur lieu y pesaient
  35 octets. Ils voyagent donc avec le catalogue (`audio.LIEUX_A_PART`, `audio.echantillons_a_part`) et
  `Son.Lieu.declarer` les remet au paquet à l'arrivée. Le catalogue est demandé juste après les définitions,
  redemandé toutes les dix secondes s'il rate, gardé dans la coquille hors ligne (`hors_ligne._ADRESSES`),
  servi par le banc (`collections_panne`).
- **En jeu** : `static/js/collections.js` — la carte se PEINT par terre (7 × 9 pixels aux couleurs de
  l'équipe, aucune entité au chargement), un éclat de quatorze images toutes les trois secondes, décalé par
  le numéro. À pied seulement, en ville seulement. 25 $, le son `carte_hockey`, « CARTE 12/40 — GASTON
  OUELLET », une ligne au journal du carnet ; aux paliers (10, 25, 40) : 250 $, 500 $, 1 000 $, l'orgue
  d'aréna (`orgue_arena`) et le bandeau des primes. `donner(numero, source)` est la seule porte de l'album :
  la rue, les triches, et demain le marché aux puces.
- **Le carnet** : LE CARNET > COLLECTIONS (« CARTES n / 40 ») ouvre l'album par équipe — « LES CASTORS DU
  FAUBOURG 2 / 5 », c'est l'indice —, « ??? » pour celles qui manquent ; une carte trouvée ouvre sa fiche,
  son dos et la carte en grand. Le BILAN compte « CARTES DE HOCKEY n / 40 ».
- **La sauvegarde** : `partie.collections.cartes[numero] = { jour, source }` ; une partie d'avant, ou
  abîmée, repart avec un album vide (`Sauvegarde.completer`).
- **Les triches** : TRICHES > ALLER > COLLECTIONS… (la plus proche, puis chacune : on se pose à deux ou trois
  tuiles, pour la voir sans la ramasser) et LE JOUEUR > TOUTES LES CARTES (l'album rempli, sans prime).
- **Les sons** (ElevenLabs, `app/audio.py`) : `carte_hockey` (le carton pincé et une étincelle, 0,8 s) et
  `orgue_arena` (la charge de l'orgue, 2,2 s) ; la synthèse reste le filet. ⚠️ À écouter par Martin. Ce sont
  des sons **de lieu** (`audio.LIEUX["collections"]`) : chargés quand une carte qui manque est à moins d'un
  écran, jamais au démarrage (le premier écran n'avait plus que six Ko de marge). ⚠️ **Recompressés à
  64 kbit/s** (le crissement du dérapage est arrivé le même jour dans le même budget : 1 357 733 pour
  1 350 000 — « la prochaine fois, on compresse avant de relever ») : 6 940 + 18 016 octets, les sons de lieu
  à 1 345 297. Un `--refaire` les rendrait à 96 kbit/s : recompresser après.
- **Juges** : `tests/test_collections.py` (douze) et `tests/test_collections_js.py` (dix), mutations vues
  rouges ; `test_debug_js` (l'onglet TRICHES), `test_hors_ligne` (la coquille), `test_definitions` (le
  plafond du paquet).

### Vague 2 — la planque qu'on décore (✅ livrée le 30 sept. 2026)

- **Le catalogue** : `app/decoration.py` — trois **trophées** (le cadre des dix cartes, le grand cadre doré des
  vingt-cinq, la coupe de la Ligue à l'album complet), qui se posent d'eux-mêmes au palier ; six **meubles** du
  catalogue Beausoleil (le juke-box 1 500 $, l'aquarium et Gérald 600 $, le sofa à carreaux 400 $, le téléviseur
  à oreilles de lapin 350 $, la lampe à lave 150 $, le tapis tressé 90 $), chacun sa ligne de catalogue et `ou`
  il se vend (`catalogue`, et déjà `puces` pour quatre d'entre eux : le marché aux puces n'aura qu'à les lire).
- **Les places** : une tuile écrite par objet **et par pièce** (`PLACES`) — la planque de Rocco et le chalet du
  rang, le même mécanisme ; une pose par objet (`POSES` : au mur, sur la table, debout, à plat). Les cadres
  au-dessus du lit, la coupe et la lampe sur la table, le coin salon (le téléviseur contre le mur, le sofa en
  face), l'aquarium à côté du coffre, le juke-box sous les fenêtres, le tapis tressé devant la porte ; au chalet,
  les cadres sur les rondins de part et d'autre de la cheminée. Rien au dé.
- **En jeu** : `static/js/decoration.js` — les neuf dessins (posés dans `DECORS` : le juke-box et ses lumières,
  Gérald qui fait ses longueurs, la lave qui monte, l'écran qui grésille — animés comme la grande roue) ; en
  entrant dans une planque (`Jeu.chargerPiece`), `meubler` fait naître ce qui s'y tient, **numéroté à part**
  (`Entites.enDehorsDeLaSuite`) — une planque vide ne crée rien. Le catalogue est un point de la table
  (`catalogue`, dans les deux pièces) : payé tout de suite, **livré le lendemain** (`partie.meubles[pièce][meuble]
  = { jour }`), annoncé au lever du jour et noté au carnet. Le chalet qui n'est pas encore à toi n'offre, à son
  catalogue, que de l'acheter.
- **Le juke-box** se touche (ACTION : la station suivante de la radio, puis le silence) et se tait quand on sort.
- **Le poids** : le catalogue voyage avec les collections (`/api/collections` : 10 050 bruts / 3 822 gzip) ; la
  carte gagne les deux points `catalogue` (+9 gzip).
- **Captures** : la planque vide, la planque pleine, le chalet plein, le catalogue.
- **Juges** : `tests/test_decoration.py` (sept) et `tests/test_decoration_js.py` (sept), mutations vues rouges.
- **Ce qui reste pour les vagues d'après** : les bebelles (vague 3) se poseront sur une étagère de la planque par
  le même `PLACES` ; le marché aux puces lira `ou: puces`.

### La carte plus visible l'hiver, et la nuit (✅ livrée le 30 sept. 2026)

- **Ce qui se perdait** (capture sur la neige, jour 5) : le carton crème sur la neige, c'est du blanc sur du blanc
  — on ne voyait plus que la photo, un point de couleur ; et l'éclat blanc disparaissait. **La nuit n'avait jamais
  été regardée** : la nuit se pose par-dessus la ville (`Base.fin`), la carte et son éclat s'y éteignaient, l'été
  comme l'hiver.
- **L'hiver** (`Saisons.enHiver`, tant que la neige tient — la même règle que les capotes relevées) : un cadre
  sombre d'un pixel autour du carton (le petit creux qu'elle fait dans la neige), et l'éclat passe du blanc à
  l'or (`HIVER` dans `collections.js`). L'été ne change pas.
- **La nuit** (`Monde.ambianceVue().alpha` au-dessus de 0,2) : le temps de l'éclat, une petite lampe de 16 px
  (`Collections.lampes`, donnée à la nuit par `Jeu.rendre` comme les citrouilles) — un éclat dans le noir toutes
  les trois secondes, rien entre deux : pas une carte qui luit.
- **Captures** (`captures/collections/`) : `hiver-jour-avant.png` / `hiver-jour.png`, `hiver-jour-eclat.png`,
  `hiver-nuit-eclat-avant.png` / `hiver-nuit-eclat.png`, `ete-nuit-eclat.png`.
- **Juges** : deux de plus dans `tests/test_collections_js.py` (le contour et l'éclat d'or l'hiver, pas l'été ; la
  lampe la nuit, ni le jour ni entre deux éclats, et donnée au rendu) — sept mutations vues rouges.

### Vague 3 — les bebelles (✅ livrée le 30 sept. 2026)

- **Le catalogue** : `collectionner.BEBELLES` — douze curiosités, chacune un SLUG stable (le nom qu'en garde la
  sauvegarde, `partie.collections.bebelles[slug]`), deux lignes de carnet, un dessin 6 × 7 et sa palette (le même peint
  par terre, sur l'étagère et en grand au carnet), et `ou` elle dort. L'**ordre** du catalogue est sa place sur
  l'étagère : une treizième s'ajouterait au bout. Le ton de [écrire drôle](../ecrire-drole.md) — on frappe le proprio
  du ciné-parc, le zonage des Érables, l'équipe partie à Hartford, jamais le petit monde :
  la bouteille à la mer (« dix cennes de consigne »), le cendrier de l'Expo 67 (« pris au pavillon de l'URSS »), la
  raquette en babiche (« l'autre est partie en 1971 avec le beau-frère »), les lunettes 3D en carton (« le film était
  en deux dimensions »), le Bonhomme en plastique, le calendrier du garage resté sur février 1982, la lanterne du
  serre-frein (« elle attend le train de 19 h 12 »), le chat qui salue, la boîte de biscuits danois pleine de
  boutons, le flamant rose de parterre (« article 12, alinéa "voyons donc" »), la tuque des Marsouins, le chien du
  tableau de bord (« on l'a nommé au conseil municipal »).
- **Les places, sans un dé** : dans sa zone, la cachette (ruelle, friche, herbe, quai, allée de pierre, sable) **la
  plus loin à pied** — de la planque, d'un amarrage pour l'île (on y va en chaloupe), du bout du pont pour l'aéroport
  (on saute le trou du pont, puis la guérite du laissez-passer, a02 : le cendrier est DANS la clôture). Les barrières
  qu'une mission ouvre comptent ouvertes ; celles d'une heure ou d'un prix, fermées. Jamais au bord de la carte, dans
  son coin nord-ouest (la mini-carte le couvre quand la caméra s'y arrête) ni à trois rangées de la voie du train
  (ses rails se peignent sur l'herbe) — deux défauts vus **à la capture**, pas par un juge. Loin des paquets, des
  frénésies, des cartes et des autres bebelles. Les deux des **blocs** (le fond du rang, derrière l'écran du
  ciné-parc) : la plus loin de l'arrivée du bloc, ses arbres comptés comme des murs, en tuiles du bloc (jamais dans
  la ville : la bande nord les décalerait). Posées après les cartes : les cartes n'ont pas bougé d'une tuile.
- **En jeu** (`collections.js`) : peintes par terre (aucune entité), leur éclat (décalé par leur rang), l'hiver leur
  silhouette cernée de sombre (le Bonhomme blanc sur la neige), la nuit la lampe de l'éclat ; ramassées à pied :
  100 $, le son `bebelle`, « BEBELLE 3/12 — LE CHAT QUI SALUE », une ligne au carnet ; aux paliers (six, douze) :
  500 $ et 2 500 $, le reel (`reel_bebelles`) et le bandeau. Celles d'un bloc ne se voient que dans leur bloc.
- **L'étagère** (`decoration.py`, `etagere_bebelles`) : le trophée de la PREMIÈRE bebelle, deux tuiles (`l: 2`) en pin
  foncé, trois tablettes de quatre — contre le mur du bas entre le poêle et la porte dans la planque de Rocco, derrière
  le sofa au chalet (la table de pin ferme le coin de gauche). Sa **pose** est l'ensemble des bebelles trouvées, un bit
  chacune (`Collections.masqueBebelles`) : chaque étagère différente se cuit une fois, comme une pose de manège.
- **Le carnet** : LE CARNET > BEBELLES (« n / 12 ») — celles qu'on a par leur nom (leur fiche : leurs deux lignes, le
  jour, le lieu, et elle en grand), les autres « ??? » et **le lieu où elles dorment** (« L'ÎLE-AUX-CORNEILLES », « LE
  RANG ») : l'indice, et c'est tout. Le BILAN compte « BEBELLES n / 12 ».
- **Les triches** : TRICHES > ALLER > COLLECTIONS a une section BEBELLES (celles d'un bloc passent son fondu d'abord),
  LE JOUEUR > TOUTES LES BEBELLES.
- **Les sons** (ElevenLabs, 150 crédits environ) : `bebelle` (un tintement de verre et de tôle, trois notes de boîte à
  musique, 1,4 s) et `reel_bebelles` (un violon et la podorythmie, 2,8 s) — ⚠️ **à écouter par Martin**. Sons du lieu
  `collections` (chargés à un écran d'une trouvaille). ⚠️ **Le plafond des sons de lieu (1,35 Mo) n'avait que 4,7 Ko
  de marge** : les deux sont à 64 kbit/s, ET `jackpot` et `roulette_bille` (le casino, à ~97 kbit/s) ont été
  **recompressés à 64 kbit/s** pour leur faire de la place (60 858 → 40 586 et 55 529 → 37 033 octets) : les lieux à
  1 341 306. Martin : si le casino sonne moins bien, c'est ça.
- **Le poids** : rien dans les définitions ni la carte ; `/api/collections` passe à 14 354 bruts / 5 429 gzip, son
  plafond relevé à 18 000 / 7 000 (c'est le paquet qui arrive après, en arrière-plan) pour les sauts.
- **Captures** (`captures/collections/`) : `bebelles-planque.png` (l'étagère pleine), `bebelles-planque-cinq.png`,
  `bebelles-chalet.png`, `bebelle-bonhomme-hiver.png`, `bebelle-chat-hiver.png`, `bebelle-cendrier.png`,
  `bebelle-raquette-rang.png`, `bebelle-lanterne-nuit.png`, `carnet-bebelles.png`, `carnet-bebelle.png`.
- **Juges** : `tests/test_bebelles.py` (onze) et `tests/test_bebelles_js.py` (neuf) ; dix-sept mutations vues rouges
  — dont trois qui ne mordaient pas au premier passage (le coin de la mini-carte, couvert sur la graine livrée par la
  voie du train ; les arbres du bloc ; la guérite de l'aéroport) : un pré synthétique, un faux rang coupé par une
  rangée de sapins, et le cendrier jugé DANS la clôture les séparent.
