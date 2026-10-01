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

### Vague 5 — les enseignes qu'on dévisse la nuit (1er oct. 2026 — Martin : « la collection des enseignes »)

La fiche d'origine la laissait « à trancher » : elle doublait l'affiche arrachée du décor qui répond. Ce qui
est proposé, et livré :

**Quoi : douze enseignes-drapeaux.** Pas le bandeau du commerce (c'est la façade : il garde sa place et son
nom), mais **l'enseigne qui pend au bout, au-dessus du trottoir** — celle qu'on appelle une enseigne depuis
le Moyen Âge, et la seule qu'on dévisse d'une main, debout sur le trottoir. Aujourd'hui chaque commerce a là
une pancarte muette ; les douze qui ont du caractère y portent **un néon à leur emblème** (une petite grille
de 5 × 7 et sa palette, comme les bebelles), qui luit la nuit. Une ou deux par district de commerces :

| District | Enseigne | L'emblème | Au carnet (le ton d'[écrire drôle](../ecrire-drole.md) : on frappe le proprio, jamais le client) |
|---|---|---|---|
| le Faubourg | **BINGO** (le sous-sol) | la boule « B » | « Le conseil de fabrique la cherchera. Il cherche encore la quête de 1971. » |
| le Faubourg | **LE CLAIRON** | le clairon | « Louise en fera sa une. Pour une fois, c'est vrai. » |
| les Érables | **CHEZ TI-PAUL** | la bouteille de liqueur | « Ouvert sept jours, vingt-quatre heures. L'enseigne, elle, a pris congé. » |
| les Érables | **LAVE-AUTO** | les bulles | « Garantie sans égratignures. On a pris l'enseigne avec des gants. » |
| La Shop | **CINÉMA RIALTO** | la bobine | « Le proprio dit que c'est un monument historique. Le monument est chez nous. » |
| La Shop | **SALLE DE QUILLES** | la quille | « La ligue du mardi ne s'en est pas aperçue : elle ne regarde que le tableau. » |
| les Quais | **CANTINE** | le hot-dog | « Deux steamés, une frite, une enseigne. Le reste de la commande, on l'a payé. » |
| les Quais | **TAVERNE DU PORT** | la bock | « La draft à trente-cinq cennes. L'enseigne, gratis. » |
| La Pointe | **SOUVENIRS** | le phare | « Le seul souvenir de La Pointe qu'on n'a pas payé 4,99 $. » |
| le Petit-Canton | **CLUB MAH-JONG** | la tuile | « Le club a voté : la police ne sera pas appelée. Le vote était serré. » |
| le Petit-Canton | **DRAGON D'OR** | la pièce d'or porte-bonheur | « Irène l'a remarqué. Irène remarque tout. » |
| les Friches | **TI-POUT AUTOS** | le pneu | « Garantie trente jours ou trente pieds. L'enseigne n'a fait ni l'un ni l'autre. » |

La Gare n'a aucun commerce sur la graine livrée : elle n'en a pas. ⚠️ **Où, sans un dé** : chaque enseigne nomme
ses noms de devanture (`BINGO`, `CANTINE`…) ; la règle prend, sur la ville FINIE, la devanture qui porte ce nom
et une pancarte, dans son district d'abord, la première en ordre de lecture. La ville ne bouge pas d'un octet :
rien n'est posé, tout se peint. Un nom qu'une ville n'a pas : l'enseigne reste au catalogue, sans place.

**Le geste — LE TOURNEVIS.** La nuit seulement (`Monde.estNuit`, la règle des barrières et de la police), à pied,
debout sous l'enseigne : ACTION ouvre une épreuve d'adresse (la boîte du bingo et du crochetage). **Quatre vis,
et chacune se dévisse d'un tour complet dans le sens contraire des aiguilles** : HAUT, GAUCHE, BAS, DROITE — au
stick, à la croix ou aux flèches (`Entree.axe`, le même axe que le piratage). ⚠️ **Aucune fenêtre de rythme et
aucun échec** (la leçon du dojo) : on tourne à son rythme ; un cran dans le mauvais sens ne défait rien, il est
seulement commenté (« DANS L'AUTRE SENS, TU LA REVISSES ») ; ESQUIVE abandonne, l'enseigne reste. Le jour, rien
(aucune invite, le bouton reste à la porte et aux poches).

**Le risque — un témoin.** Quand l'enseigne tombe, c'est une **effraction** (`recherche.DELITS["effraction"]`,
une étoile, qui attendait son premier usage) : un policier qui voit → l'étoile tout de suite ; un passant qui
a vu → il court le raconter, et on peut lui acheter son silence comme d'habitude. La nuit, les passants voient
moins loin : c'est pour ça que ça se fait la nuit.

**Ce qui change.**
- **La façade** : à la place du néon, la potence vide, un fil qui pend et les deux trous de vis ; la lampe du néon
  s'éteint. Peint dans le morceau (`Monde.peindreDevantures`, recuit quand le compte change) — la façade garde sa
  place, son bandeau et son nom.
- **La planque** : un trophée de plus, **LE MUR DES ENSEIGNES** — un panneau perforé de deux tuiles accroché sous
  les fenêtres (palier 1, comme l'étagère des bebelles), trois rangées de quatre crochets ; chaque enseigne
  dévissée y pend, la même qu'on a vue sur la rue. Sa pose est l'ensemble des enseignes dévissées (un bit
  chacune). Au chalet du rang aussi, s'il y a la place.

**Ce qu'elles rapportent.** 200 $ l'enseigne (la prime de collection, comme les cartes, les bebelles et les sauts —
plus cher : la nuit, un témoin), et aux paliers : **six** → 1 000 $, **douze** → 3 000 $. Un son ElevenLabs court au
dévissage d'une vis (le tournevis, le grincement, la vis qui tombe), le reel des bebelles aux paliers. Au carnet,
LE CARNET > ENSEIGNES (« n / 12 ») : par district, celles qu'on a — leur nom, leurs deux lignes, la nuit du vol
et l'emblème en grand —, les autres « ??? » et le district où elles pendent encore. Le BILAN compte
« ENSEIGNES n / 12 ». La sauvegarde : `partie.collections.enseignes[slug] = { jour, source }`.

**Le poids** : rien dans les définitions ni dans la carte — le catalogue, les emblèmes et les places voyagent sur
`/api/collections` ; le son est un son de lieu (`audio.LIEUX["collections"]`, chargé à un écran d'une enseigne).

**Le debug** : TRICHES > ALLER > COLLECTIONS a une section ENSEIGNES (on se pose sous l'enseigne, à la nuit
tombée), et LE JOUEUR > TOUTES LES ENSEIGNES.

⚠️ **À valider par Martin** : le geste (un tour par vis, quatre vis), le prix (200 $), et le propriétaire — **pas
fait** : le patron qui sort de la taverne ouverte la nuit serait la vague d'après.

### Vague 6 — le propriétaire qui sort (1er oct. 2026 — Martin : « le propriétaire qui sort de son commerce quand on dévisse »)

Martin a validé le geste (quatre vis), le prix (200 $) et le mur de la planque. Ce qui vient : **pendant qu'on
dévisse (ou quand l'enseigne tombe), le propriétaire du commerce sort par sa porte, en pyjama ou en robe de
chambre.** Il crie (une ou deux répliques en bulle, une voix générique si c'est bon marché), puis, selon son
**tempérament** — tiré à l'empreinte du commerce, jamais au dé —, il te court après ou il appelle la police. Il
naît hors de la suite des identifiants de la ville, avec un dé prêté (comme les passants donneurs), et rentre
chez lui après. On peut l'assommer (un délit de plus) ou se sauver. Pas toutes les enseignes : certaines sont
muettes la nuit (fermé, personne en haut), à l'empreinte. Le ton d'[écrire drôle](../ecrire-drole.md) : jamais
méchant.

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
- **Les sons** (ElevenLabs, une cinquantaine de crédits) : `bebelle` (un tintement de verre et de tôle, trois notes de boîte à
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

### Vague 4 — les sauts de Rocco (✅ livrée le 30 sept. 2026)

- **Vingt sauts** (`collectionner.SAUTS_PAR_DISTRICT`, `poser_sauts`) : les **huit rampes** de la ville (celles du Grand
  Saut et des missions) et **douze tremplins neufs** en contreplaqué, aux chevrons rouges peints à la main. Par
  district, son compte (trois au Faubourg, aux Érables, à la Shop, aux Quais et à La Pointe, deux aux Friches et à la
  Gare, un au Petit-Canton), ses rampes d'abord, puis ses tremplins ; un SLUG par saut (`erables_2`), un nom (« LE SAUT
  DU NOTAIRE », « LE SAUT DU 19 H 12 »…). Le numéro du saut dans son district est son nom : `partie.collections.sauts`.
- ⚠️ **Les tremplins ne sont PAS dans la carte** : ils voyagent sur `/api/collections`, se **peignent** par-dessus le
  sol (`Collections.dessiner`, aucune entité) et font **décoller comme une rampe** — `Collections.estTremplin`, lu par
  `Vehicules.avancer` à côté de `Monde.estRampe` (en ville seulement).
- **Où, sans un dé** : un pied et une lèvre hors d'une voie de circulation et d'un trottoir, **sept tuiles d'élan**
  derrière et **dix de réception** devant (`carte.ELAN_RAMPE`, `carte.RECEPTION_RAMPE`), une piste **large** (ni décor ni
  mur sur ses deux bords), jamais sur la voie du train, au bord de la carte ni dans son coin nord-ouest ; le plus loin
  possible des rampes et des autres tremplins, jamais à moins de vingt tuiles. L'élan sur un sol **rapide** :
  l'asphalte, le stationnement, le quai — pas l'abord ni les planches d'un pont (« un couloir, pas un élan », la
  leçon des rampes d'avant), pas la terre (mesuré au banc : une auto plafonne à 2,2 px/image sur l'herbe, sous les
  2,7 qu'il faut pour décoller). Un district qui n'en a pas prend ses ruelles, puis sa terre : **un saut en 4 roues**
  (plein régime sur la terre ; les Friches en ont trois) — le carnet le dit (« EN 4 ROUES »). Sur la graine livrée :
  **sept tremplins sur douze se prennent en 4 roues** (les deux des Friches, de La Pointe, de la Gare, un des Érables).
  ⚠️ À Martin de dire si c'est trop.
- **Un saut réussi** (`Collections.majSauts`) : le char du joueur décolle d'une rampe ou d'un tremplin, vole au moins
  **40 px** (la distance parcourue en l'air — une auto lancée sur ses sept tuiles d'élan vole 45 px, une moto ou un 4 roues
  bien plus), et **atterrit propre** : trente images après avoir touché le sol, pas un choc, pas l'eau, le char entier.
  Le premier : **150 $**, le son `saut_reussi` (la bande de chums qui fait « ohhh ! » et applaudit), « SAUT 3/20 — LE SAUT
  DU PHARE : 84 PX · 97 KM/H », une ligne au carnet ; aux paliers (dix, vingt) : 750 $ et 2 500 $, l'orgue et le
  bandeau. Ensuite, un **record** se note sans repayer. Raté, ça se dit : « TROP COURT (40) », « ATTERRISSAGE RATÉ ».
- **Le carnet** : LE CARNET > SAUTS (« n / 20 »), par district — ceux qu'on a réussis avec leur record (vol et vitesse
  au décollage), les autres « ??? ». Le BILAN compte « SAUTS n / 20 ». **Triches** : ALLER > COLLECTIONS a une section
  SAUTS (on se pose au bout de l'élan) ; LE JOUEUR > TOUS LES SAUTS.
- **Le son** (ElevenLabs ; les trois bruitages des vagues 3 et 4 ont coûté **70 crédits** en tout, 69 190 restants) : `saut_reussi`, 2 s, à 64 kbit/s — ⚠️ à écouter par Martin. ⚠️ **Les sons de
  lieu** : pour lui faire de la place, `tonnerre-1` et `tonnerre-2` (la pluie, ~98 kbit/s) sont recompressés à 64 kbit/s
  (40 482 → 27 002 et 42 363 → 28 256) : les lieux à 1 326 510 sur 1 350 000.
- **Le poids** : `/api/collections` à 16 987 bruts / 5 964 gzip (plafond 18 000 / 7 000) ; rien dans les définitions ni
  la carte (le juge le vérifie : aucun tremplin n'est une rampe de la carte).
- **Captures** (`captures/collections/`) : `saut-tremplin-quai.png`, `saut-tremplin-hiver.png`,
  `saut-tremplin-4-roues.png` (un 4 roues en l'air à côté), `saut-tremplin-ruelle.png`, `carnet-sauts.png`.
- **Juges** : `tests/test_sauts.py` (sept) et `tests/test_sauts_js.py` (huit, dont **chacun des vingt se prend** depuis
  son élan, au banc — c'est ce juge qui a trouvé les six premiers tremplins injouables : un toit d'à côté, une poubelle,
  une caisse du quai) ; vingt mutations vues rouges, dont cinq qui ne mordaient pas au premier passage (deux
  règles doublées retirées du code, un terrain synthétique pour l'écart, une sauvegarde abîmée, un don en double).

### Vague 5 — les enseignes qu'on dévisse la nuit (✅ livrée le 1er oct. 2026)

- **Le catalogue** : `app/devisser.py` — douze enseignes-drapeaux (`ENSEIGNES`), chacune un SLUG stable
  (`partie.collections.enseignes[slug]`), les noms de devanture qu'elle peut prendre, deux lignes de carnet et un
  emblème de 5 × 7 en couleurs de néon ; l'ordre du catalogue est sa place sur le mur de la planque. Le Dragon d'or
  porte une pièce porte-bonheur (un dragon ne tient pas dans 5 × 7), Ti-Pout un pneu orange.
- **Les places, sans un dé** : `devisser.poser`, appelé au bout de `collectionner.poser` — la devanture qui porte un
  de ses noms ET une pancarte, son district d'abord, puis l'ordre de lecture. Elle LIT la ville et n'y pose rien
  (juge : un espion pendant la génération, la ville avant et après à l'octet). Sur la graine livrée, les douze ont
  leur place, chacune dans son district (le Rialto est à La Shop, où `enseignes.py` l'a ouvert).
- **La façade** : le néon pend à la place de la pancarte (`Devisser.peindreDrapeau`, appelé par
  `Monde.peindreDevantures` ; `FACADES.devanture` saute alors sa pancarte), une lueur de sa couleur la nuit, qui
  grésille à l'empreinte de son rang. Dévissée : la potence vide, la barre et ses deux crochets, le fil coupé et
  son bout de cuivre. Les morceaux de la ville se recuisent quand `Devisser.cle()` change (le catalogue qui arrive,
  une enseigne qui tombe) — jamais à chaque image.
- **Le geste** : la nuit (`Monde.estNuit`), à pied, debout sous le néon (16 px), ACTION — dans `Missions.interagir`
  après la grue, avant le bouclier humain ; la porte d'abord (le néon se tait devant une porte). L'invite :
  « DÉVISSER : LE CINÉMA RIALTO ». Le tournevis est une épreuve d'`Adresse` (`Adresse.EPREUVES.tournevis`,
  posée par `devisser.js`) : le néon en grand et ses quatre vis, la tête de vis qu'on tourne et ses quarts, H/G/B/D
  autour — la direction qui vient, allumée. Le premier cran pose la lame ; chaque pas dans le sens contraire des
  aiguilles fait un quart ; quatre quarts, une vis (le son `devisser`) ; quatre vis, « ELLE LÂCHE ! ». Le mauvais
  sens est dit (« DANS L'AUTRE SENS, TU LA REVISSES »), un saut de deux crans aussi (« UN QUART À LA FOIS ») —
  rien ne se défait, aucun temps ne presse. Au stick on roule le pouce ; au clavier et à la croix, on tape les quatre
  directions dans l'ordre. ESQUIVE abandonne : « L'ENSEIGNE RESTE ».
- **Le risque** : l'enseigne tombe → `Police.signalerCrime('effraction', …, Police.quelqu_un_voit(…))` — le délit
  existait (une étoile, il faut un témoin) et n'avait jamais servi. Un agent qui voit chauffe ; un passant qui a vu
  court le raconter, et son silence s'achète. Le propriétaire : **pas fait**.
- **Ce qu'elles rapportent** : 200 $, une ligne au journal (« ENSEIGNE : LE CINÉMA RIALTO — AU MUR DE LA
  PLANQUE »), et aux paliers six et douze 1 000 $ et 3 000 $, le reel des bebelles et le bandeau.
- **La planque** : `LE MUR DES ENSEIGNES` (`decoration.py`, palier 1, `sol`, deux tuiles) — un panneau perforé de
  trois rangées de quatre crochets, chaque enseigne dévissée y pend (le même néon que sur la rue). Dans la planque de
  Rocco, appuyé au mur sous les fenêtres, à côté du juke-box (4, 1) ; au chalet, dans le coin du bas (1, 6) —
  ⚠️ **le juke-box du chalet s'est déplacé d'une tuile** pour lui laisser le coin (3, 6), toujours à gauche de la
  porte. Sa pose est l'ensemble des enseignes dévissées, un bit chacune (`Devisser.masque`).
- **Le carnet et le BILAN** : LE CARNET > ENSEIGNES (« n / 12 »), par district — celles qu'on a par leur nom (leurs
  deux lignes, la nuit du vol, le district, le néon en grand), les autres « ??? · LA NUIT ». Le BILAN compte
  « ENSEIGNES n / 12 ». La sauvegarde : une partie d'avant (ou abîmée) repart avec un mur vide.
- **Les triches** : TRICHES > ALLER > COLLECTIONS a une section ENSEIGNES (`Devisser.allerA` : debout sous le néon,
  et la nuit tombée si c'était le jour) ; LE JOUEUR > TOUTES LES ENSEIGNES.
- **Le son** (ElevenLabs, ≈ 40 crédits) : `devisser` (la vis rouillée qui grince et tombe en tintant sur le trottoir,
  0,9 s), recompressé à 64 kbit/s (7 567 octets), son du lieu `collections` (chargé à un écran d'une enseigne, la
  nuit) ; la synthèse reste le filet. ⚠️ À écouter par Martin.
- **Le poids** : rien dans les définitions ni dans la carte ; `/api/collections` passe à 23 947 bruts / 8 533 gzip
  (3 790 / 1 430 pour les enseignes), son plafond relevé à 26 000 / 9 500.
- **Captures** (`captures/enseignes/`) : `zoom-rialto-jour-avant.png`, `zoom-rialto-nuit-avant.png` (le néon rose
  qui luit), `zoom-rialto-nuit-apres.png` / `zoom-rialto-jour-apres.png` (la potence vide), `zoom-dragon_or-nuit-avant.png`
  (sous la plaque à idéogrammes), `zoom-bingo-jour-avant.png`, `zoom-ti_pout-jour-avant.png`, `tournevis.png`,
  `tournevis-autre-sens.png`, `zoom-planque-mur-quelques.png`, `zoom-planque-mur-plein.png`, `carnet-enseignes.png`,
  `carnet-rialto.png`.
- **Juges** : `tests/test_enseignes_devissees.py` (huit) et `tests/test_enseignes_devissees_js.py` (douze, PAR LE
  BOUTON : chacune des douze s’atteint par ACTION sous son néon) ; seize mutations vues rouges — dont deux qui
  ne mordaient pas au premier passage : la ville du cache était déjà passée par la règle (le juge espionne
  maintenant la génération), et la sauvegarde d'une partie abîmée.

### Vague 6 — le propriétaire qui sort (✅ livrée le 1er oct. 2026)

- **Qui sort, à l'empreinte du commerce** (`devisser.proprio`, `crc32("réveillé:" + slug)`, jamais un dé) : personne
  (une fois sur trois : il n'y a personne en haut), ou quelqu'un qui **court** ou qui **appelle** ; homme ou femme ; en
  pyjama rayé ou en robe de chambre à carreaux (le pyjama dépasse aux chevilles), toujours en pantoufles ; et la vis
  qui le réveille (la deuxième, la troisième, ou la dernière, quand elle lâche). ⚠️ **Personne ne sort d'une porte
  tenue** (`PORTE_TENUE`) : chez Ti-Paul, c'est Ti-Paul (un personnage, avec sa voix) ; au Dragon d'or, le portier du
  casino, ouvert toute la nuit. Les Souvenirs n'ont pas de porte. Sur la ville livrée :

  | Commerce | Qui | Il se réveille | Habit |
  |---|---|---|---|
  | le Bingo | elle **court** | à la 3e vis | pyjama |
  | le Clairon | elle **appelle** | quand elle tombe | pyjama |
  | le Lave-auto | elle **appelle** | à la 3e vis | pyjama |
  | les Quilles | il **court** | à la 2e vis | robe de chambre |
  | la Cantine | il **appelle** | à la 2e vis | robe de chambre |
  | le Mah-jong | il **appelle** | à la 2e vis | robe de chambre |
  | Ti-Pout Autos | elle **court** | à la 2e vis | robe de chambre |
  | Chez Ti-Paul, le Rialto, la Taverne du port, les Souvenirs, le Dragon d'or | personne | — | — |

- **Il sort par la porte** de sa devanture (la vraie `D`, sinon la condamnée `d` : il habite en haut), né DANS la porte
  comme un passant qui sort (`e.sortie`, `majPorte` : invisible tant qu'elle s'ouvre). Il naît **hors de la suite des
  numéros** (`Entites.enDehorsDeLaSuite`) avec un **dé prêté** (`sansLeDe`, la règle des jobs et du portier) : sa
  naissance ne tire rien du jeu. Il est `metier: 'proprio'` (ni costume d'Halloween, ni compté dans la foule, ni témoin
  ordinaire) et `horsSaison` : en janvier, la ville ne lui enfile pas de manteau (`Entites.imageDe`) — c'est la blague.
- **Il crie** (sa bulle, sa voix de passant — Felix pour lui, Amélie pour elle, `audio.VOIX_PAR_GENRE`), tourné vers
  toi, le temps de le lire ; puis son tempérament :
  - **il court** (« Attends que j'te pogne! J'cours vite, en pantoufles! » / « Reviens icitte! J'ai des bigoudis, pas
    des béquilles! ») : il te colle aux talons — ⚠️ **sans frapper** (`coupsDictes`) : au banc, ses poings
    t'envoyaient à l'hôpital en neuf secondes, ce n'est pas un monsieur en pantoufles. Arrivé sur toi (26 px), **le
    tournevis te tombe des mains** (« L'ENSEIGNE RESTE — LE PROPRIO ! »). Il lâche au bout de douze secondes, ou à deux
    cents pixels de sa porte : « Pfff… Reviens demain, j'vas être habillé! » / « Reviens aux heures d'ouverture, comme
    tout le monde! », et il rentre.
  - **il appelle** (« Bouge pas! J'appelle la police… dès que j'trouve mes lunettes! » / « J'appelle la police! Pis ma
    belle-sœur, a va le savoir avant eux! ») : planté sur son perron le temps qu'on le lise, il rentre ; cinq secondes
    plus tard, si l'enseigne est tombée, **l'effraction est rapportée** (`Police.rapporter`, comme un témoin qui
    téléphone : la chaleur d'une étoile ; « LE PROPRIO A APPELÉ LA POLICE »). Elle pend encore : il attend en ligne
    qu'elle tombe, une minute au plus.
- **On peut l'assommer** : c'est un `coup_pieton` de plus (le délit ordinaire d'un coup sur un passant) ; assommé, il
  n'appelle personne — relevé, il rentre, la tête lui tourne. Ou **se sauver**.
- **Une fois par nuit et par commerce** (la nuit va de la tombée du jour à l'aube) ; la nuit d'après, il ressort.
- **Le poids** : rien dans les définitions ni dans la carte ; qui sort, ses répliques et ses deux séries de voix
  voyagent sur `/api/collections` (26 336 octets bruts : plafond relevé de 26 000 à 27 000).
- **Les voix** (ElevenLabs v3, ≈ 500 crédits, deux passes : la première portait des balises que v3 ne connaît pas) :
  huit `histoire-proprio-<h|f>-<sort|court|appelle|lache>.mp3`, −19,5 LUFS, relues par Scribe (tous les mots y sont,
  aucune balise lue). ⚠️ À écouter par Martin.
- **Captures** (`captures/enseignes/`) : `planche-proprios.png` (les sept, tels que le jeu les cuit),
  `zoom-quilles-porte.png` (il sort), `zoom-quilles-crie.png` (la robe de chambre, la nuit), `proprio-bingo-crie.png`
  (le pyjama rayé), `zoom-cantine-janvier-crie.png` (en robe de chambre dans la neige), `proprio-quilles-ensuite.png`.
- **Juges** : `tests/test_proprio_des_enseignes.py` (cinq : la table écrite en toutes lettres, les portes tenues, une
  vraie porte, aucun dé, ce qui voyage) et `tests/test_proprio_des_enseignes_js.py` (neuf, au bouton : sa vis, hors de la
  suite et sans un dé ; le pyjama en janvier ; il crie, colle sans frapper et le tournevis tombe ; il appelle et la
  police l'apprend ; assommé au bouton, il n'appelle personne ; il lâche au bout de sa poursuite ; il ne court pas loin
  de chez lui ; une fois par nuit ; ceux qui ne sortent jamais) — seize mutations vues rouges.

### Ce qui reste

- **Les enseignes qu'on dévisse la nuit** : livrées le 1er oct. 2026 (la vague 5), et le propriétaire qui sort (la
  vague 6). Reste, si Martin le veut : le mur des enseignes ailleurs que dans les deux planques.
- **Le marché aux puces du dimanche** ([sa fiche](le-marche-aux-puces-du-dimanche.md#fiche)) : il vendra les cartes qui
  manquent par `Collections.donner(numero, 'puces')` et les meubles `ou: puces`.
