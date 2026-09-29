# L'école rivale : les Mantes, un gang qui sait se battre

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026), troisième des trois jalons des arts martiaux — après
[le répertoire](les-techniques-d-arts-martiaux.md#fiche) et [le dojo](le-dojo-du-quartier.md#fiche).

_Ce que ça donne :_ un gang qui connaît les coups de pied et les projections — pour avoir à qui rendre ce
qu'on a appris. Les autres gangs gardent les poings de rue (variés depuis le premier jalon).

- **Où** : dans [le Petit-Canton](le-quartier-chinois.md#fiche), le quartier chinois au nord (Martin, 26 sept. 2026) —
  il doit être livré avant.
- **Qui** : **un gang neuf, les Mantes** — tranché par Martin le 26 sept. 2026. Les élèves d'un dojo concurrent, avec
  leur couleur, leur territoire et leur garde-robe (`app/garderobe.py`, une garde-robe par archétype).
- ⚠️ **Ce que coûte un gang neuf** : un archétype de plus dans `pietons.py`, sa place dans les frontières de
  gangs (`pietons.frontieres`, la bagarre), et son territoire sur la carte — or « grossir un lieu garanti
  déplace la ville » : ce qu'on ajoute se pose en dernier, sans dé, et on compare les deux villes clé par clé.
  Relire la ligne « Les territoires des gangs bougent » du plan avant de poser le sien.
- **Comment ils choisissent** : `Techniques.choisir` pour eux aussi, avec leur liste de techniques ; leurs
  choix se tirent **à l'empreinte**, jamais par `B.rng()`.
- **Ce qu'on leur répond** : la parade-contre (retournement du poignet) prend tout son sens contre eux ; une
  projection subie par le joueur le couche sans l'assommer.
- ⚠️ **Ce qui guette** : le joueur projeté passe par `e.vol` comme un passant — la caméra, le volant et la
  coop (le deuxième joueur) doivent le suivre en l'air.

**Juges** : un membre de l'école rivale finit par projeter le joueur ; le joueur projeté retombe sur une tuile
libre ; aucun dé consommé.

### Fiche de la vague 2 — le vieux maître revient de Floride (Martin, 29 sept. 2026 : « les deux »)

Martin a pris les deux pistes, tissées en une seule histoire : **Irène** appelle en Floride, et **le vieux maître**
revient reprendre ses élèves un par un.

- **Le maître : Victor Tam, « Sifu Tam »** (slug `maitre`) — soixante-quatorze ans, quarante ans à enseigner la mante
  religieuse au Petit-Canton, retraité depuis trois hivers à Hollywood Beach, en Floride. Il revient bronzé, en
  chemise fleurie, en bermudas et en chapeau de paille : un snowbird du quartier. Drôle et attachant — il compare tout
  à la Floride, et il se sent coupable : ses élèves ont mal tourné quand il est parti. ⚠️ Le ton : il est d'ici, il
  parle le joual du quartier ; le drôle vient du snowbird, jamais de l'accent ni de l'origine (`ecrire-drole.md`).
  Sa fiche : `docs/personnages/victor-tam.md` ; sa voix ElevenLabs (une voix libre, `--libres`) ; son visage
  (`visages.py`, il cligne) ; il se tient **dans son école** (`point:maitre`), **une fois revenu** (`arrive_apres`,
  une clé de donnée : il n'est pas là avant l'arc).
- **Irène le connaît depuis trente ans** : le seul qui l'ait jamais battue au mah-jong (« Madame Lam pour toi, tant
  que tu m'as pas battue » — lui l'appelle Irène).
- **L'arc, quatre missions** (c05 à c08), jamais deux fois la même mécanique :
  - **c05 (Irène)** — les Mantes veulent un « droit de table » au club de mah-jong ; Irène a appelé Victor, revenu
    hier soir. On va le voir à l'école (`parler`), et il t'envoie chercher par l'oreille les trois qui rackettent
    (`tuer`, à mains nues).
  - **c06 (le maître)** — Kenny, son meilleur élève devenu le caïd des Mantes, part s'acheter un fusil chez Gus : on
    le file (`suivre`), puis un duel à mains nues à la porte de l'armurerie (`tuer`, un chef).
  - **c07 (le maître)** — les élèves ont vendu Monsieur Bois, le mannequin de bois de l'école (1976), à la fourrière :
    on le ramène sans une égratignure (`monter`, `livrer` sans dégâts). En échange, **il t'apprend une technique**
    (le retournement du poignet, `donne.technique` — la clé est neuve, lue par `Histoire.recompenser`).
  - **c08 (le maître)** — les portes ouvertes : on escorte le vieux maître dans le quartier jusqu'au Dragon d'or, où
    Irène pose son affiche (`proteger`), et on repousse les derniers frimeurs (`tuer`).
- **Ce qui change au quartier, jugé** (`mantes.REPRISE`, `apres: c08`, comme `tripot.REPRISE`) : l'école rouvre ses
  cours — dans la salle, les élèves font face au maître et ne sont plus du gang ; dans la rue, **moins de Mantes**
  (une naissance sur deux devient une sur six sur leur territoire) ; et le gang est **calme** (`donne.calme`) : il ne
  saute plus sur qui tient une arme — ni, une fois [la provocation](les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md#fiche)
  livrée, sur qui passe à mains nues (elle lira `Entites.gangCalme`, comme la provocation à l'arme). Le Clairon en
  fait sa une.
- **Juges** : chaque mission jouée au bouton sur le banc ; le monde d'après (la salle, la rue, le calme) contre le
  même monde avant ; aucun dé de plus ; `verifier_missions.py --detail` propre ; le poids du paquet.

## Notes

### Vague 1 — l'école, le gang, et leur façon de se battre — **livrée le 29 sept. 2026**

Nommés avec Martin le 26 sept. 2026 : **les Mantes** (slug `mantes`, piéton `mante`), les élèves de l'**ÉCOLE LA
MANTE** — la mante religieuse, un vrai style de kung-fu du Sud — qui ont mal tourné. Ils se croient dans un film,
se saluent le poing dans la paume avant de te sauter dessus, et l'école ne donne plus de cours depuis que le vieux
maître a pris sa retraite en Floride. ⚠️ Le ton : l'école est UNE adresse, le gang ce sont ses élèves ; le quartier
reste à ses habitants (le territoire est le coin de l'école, jamais la rue principale). Dans l'histoire d'Irène (c01
à c04), ils n'y sont pour rien : ni c01 ni la chute du Pouce ne les nomment, et leur territoire est loin du casino.

- **L'école** (`app/mantes.py`, posée par `nord.poser` après l'arche, sur la carte finie et sans un dé — la recette
  du DOJO DION, « reprendre une porte de commerce ») : la plus au nord des portes de commerce du Petit-Canton à
  l'ouest de la rue principale, assez grande (8 × 5 dedans au moins), dont l'enseigne tient. Mesuré : c'était la
  CAISSE POP (177, 13), une pièce de 8 × 5. Enseigne **ÉCOLE LA MANTE** (quinze caractères au plus : « ÉCOLE DE LA
  MANTE » ne tient pas dans un bandeau de quatre tuiles), genre `savoir` comme le dojo, la plaque verticale gardée.
  Dedans (`piece_d_ecole`) : un plancher de bois nu (pas de tatami), deux mannequins de bois aux coins du fond, le sac,
  les **casiers des élèves** (le point `fouiller`, **gardé** : `garde: "mantes"` — les Mantes présents te voient faire
  et te tombent dessus), deux plantes, un banc de chaises le long du mur, et trois élèves — des Mantes
  (`qui: "mante"`), qui s'entraînent à leur place et ne sautent pas sur qui entre. Point `ecole_mante` (famille
  `service`). ⚠️ Toute pièce doit donner quelque chose à faire, et tout commerce a quelqu'un au comptoir
  (`test_interieurs`) : les casiers sont le « quelque chose », et l'école est tenue par ses élèves (le juge l'excuse,
  comme le DOJO DION de Mireille).
- **Le gang** (`pietons.py`) : l'archétype `mante`, vert mante (`#4c9a2a`), pantalon noir, **pas de batte** ; 110 de
  vie (le plus haut des gangs), courage 0,95, vitesse 1,15. Sa garde-robe (`garderobe.py`) : la **veste de kung-fu**
  (`veste_kungfu`, neuve : un col montant plus sombre et les boutons de corde deux par deux, une rangée sur deux), le
  pantalon noir de l'école, un bandeau une fois sur deux ; des gars et des filles. `pietons.GANGS` : `mantes`,
  district `canton`, zone `mantes`, sept membres, hostiles si tu sors une arme (comme les autres).
- **Leur territoire** (`mantes.ZONE`) : les deux colonnes d'îlots à l'ouest de la rue principale, sur les deux
  rangées du haut du quartier (148, 0, 42 × 32), ajouté AU BOUT de `ville["zones"]` (`Monde.zoneA` garde la dernière
  zone qui contient un point). Loin de la couture : une partie neuve, née au terminus, ne croise pas un Mante de plus.
  Le district `canton` passe aux Mantes (`nord.DISTRICTS_NORD` : il avait les Cravates du voisin du sud « en
  attendant »), ce qui leur donne leur **frontière** : la couture, face aux Cravates (`pietons.frontieres`, 149
  tuiles).
- **Ils se battent autrement** (`mantes.COMBAT`, `techniques.js`) — le répertoire, choisi **à l'empreinte** (le
  numéro du Mante et son compte de coups), jamais `B.rng()` :
  - ils savent (`mante.techniques`, lu par `Techniques.sait`) le coup de pied circulaire, le pied de côté, la
    projection de hanche, le grand fauchage et le retournement du poignet ;
  - ils frappent **de plus loin** (22 px contre 18) et **plus souvent** (toutes les 30 images contre 40) ; collés, trois
    coups sur dix sont une **prise** (`Techniques.saisir`) qui tient **22 images** — le temps d'une roulade — avant la
    projection ; près de la moitié sont des **pieds** (le pied de côté de loin, le circulaire de près) ;
  - **la parade** (`Techniques.parer`) : tu armes ton coup à portée — mains nues ou arme de mêlée —, et un Mante sur
    trois environ te retourne le poignet (à l'empreinte du Mante et de ton élan, `j.elans`), puis se repose quatre
    secondes. Dans une rixe, il pare la batte d'une Cravate de la même façon ;
  - **le joueur projeté** passe par `e.vol` comme un passant : la caméra le suit (elle suit `B.joueur`), il ne fait
    rien en l'air (`majGestes`), et retombe sur une tuile libre (`chute`), **couché sans être assommé** (`auSol`,
    45 images, intouchable le temps de se relever — on ne s'acharne pas sur un homme à terre), puis se relève tout
    seul ;
  - **ce qu'on leur répond** : saisi, **ESQUIVE** te dégage (la roulade suit) ; si tu connais le retournement du
    poignet, **SAISIR** renverse la prise — c'est lui qui vole ; FRAPPE et ACTION ne font rien dans la prise.
  - ⚠️ Mesuré avant de régler : contre un joueur qui cogne à la chaîne, les autres gangs tombaient sans le toucher
    (pris dans la chaîne de coups, ils ne frappent jamais) ; à la frontière, trois Cravates à la batte couchaient trois
    Mantes qui s'arrêtaient à 22 px. Les Mantes viennent maintenant au contact dans une rixe (la prise) et parent la
    batte : ils couchent les trois Cravates.
- **La frénésie du quartier** (`frenesies.py`) : « Les Cravates au Canton » devient **« Kung-fu contre carabine »**
  — huit Mantes, à la carabine, près de leur territoire.
- **Le paquet** : la carte passe 720 000 bruts (720 096 ; 70 209 gzip, sous ses 71 000) — plafond brut relevé à
  722 000 avec la mesure écrite dans `test_definitions` ; les définitions +280 gzip (60 665, sous 62 000).
- **Juges** : `tests/test_mantes.py` (l'école au Petit-Canton, hors de la rue principale, son enseigne, sa pièce et ses
  élèves ; le territoire autour d'elle, dernier rectangle, loin du terminus ; la frontière de la couture ; **l'école ne
  déplace rien** — la ville avec et sans, clé par clé ; sans façade, pas d'école et rien ne plante ; l'archétype sans
  batte, le plus dur des gangs ; leur combat ; leur garde-robe) et `tests/test_mantes_js.py` (au bouton : un Mante finit
  par projeter le joueur, qui retombe sur une tuile libre, couché sans être assommé, se relève et marche ; projeté
  contre un mur, il retombe avant ; ESQUIVE dégage la prise, FRAPPE non ; le retournement du poignet renverse la prise ;
  au même duel, un Mante tombe le dernier des six gangs et fait mal ; il pare, les autres jamais ; **aucun dé** tiré par
  `techniques.js` ; à leur frontière, ils couchent les Cravates et personne ne reste tenu ; chez eux, ce sont des
  Mantes qui naissent, en veste de kung-fu ; à l'école, les élèves sont des Mantes et ne te sautent pas dessus).
  Neuf mutations, toutes rouges. Capture regardée (Chromium) : les tenues pose par pose, la façade, la salle, le
  joueur en l'air et au sol.

**La vague 2 a été tranchée par Martin le 29 sept. 2026 (« les deux »)** : voir la fiche de la vague 2 ci-dessus et ses
notes ci-dessous. La provocation à mains nues et la musique du quartier ont été [une autre ligne](les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md#fiche).

### Les Mantes provoquent — **livré le 29 sept. 2026** (tranché par Martin)

Le dernier point du « Reste » de la vague 1 : chez elles — le coin de l'école —, les Mantes défient maintenant un
joueur à mains nues (une réplique en bulle, le salut, puis le combat) ; hors de leur territoire, rien ne change. Un
gang **calme** (`Entites.gangCalme`, ce que la vague 2 posera après c08) ne défie plus. Le détail, les garde-fous et
les juges : [les Mantes provoquent, et le Petit-Canton a sa musique](les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md#notes).

### Vague 2 — le vieux maître revient de Floride — **livrée le 29 sept. 2026**

Irène appelle en Floride, et le vieux maître reprend ses élèves un par un : une seule histoire, quatre missions, jamais
deux fois la même mécanique.

- **Victor Tam, « Sifu Tam »** (`maitre`, fiche : [`docs/personnages/victor-tam.md`](../personnages/victor-tam.md)) —
  soixante-quatorze ans, quarante à enseigner la mante religieuse, trois hivers à Hollywood Beach ; revenu bronzé, en
  chemise fleurie, en bermudas (`garderobe._BAS_DU`) et en chapeau de paille (son visage, `visages.py` : il cligne). Le
  seul qui ait jamais battu Irène au mah-jong. Il appelle le neveu « petit scarabée ». Voix : **Luca - Storyteller**
  (libre, un Français de France — permis ; en v3, à écouter). Il se tient **au milieu de sa salle** (`point:maitre`,
  `mantes.POINT_DU_MAITRE` ; au milieu parce que `placeDebout` range un personnage sur la tuile libre la plus proche du
  centre), ses trois élèves en rang entre la porte et lui ; **une fois revenu** seulement — `arrive_apres: c04`, une
  clé de donnée neuve (`Personnage`), lue par `creerDonneurs` et `creerDonneursDedans` : avant, sa salle n'a que ses
  élèves. Son premier repos ne s'entend jamais (il arrive bien après m5) : on ne le paie pas (`_vient_apres`).
- **c05, _Le droit de table_ (Irène, 500 $)** — les Mantes ont renversé la table du club de mah-jong ; Irène a appelé
  Victor. On va le voir dans sa salle (`parler`, sa poignée de main : il se nomme) ; il t'envoie chercher par l'oreille
  les trois frimeurs (`tuer`, `zone:mantes`, aux poings, 70 de vie). La fin se dit chez Irène : elle gage cinq piasses
  qu'il repart en janvier.
- **c06, _Le chemin de chez Gus_ (700 $)** — Kenny, son meilleur élève devenu le caïd, va s'acheter un fusil : on file
  son char de frime (`suivre`, une sport) jusqu'à l'armurerie, puis un duel à mains nues avec lui à la porte de Gus
  (`tuer`, `chef`). ⚠️ Deux retouches du moteur, pour tous : **le chef attend où la fiche le dit** (`ou` ; sans `ou`, il
  vient au joueur comme avant — m5, e01, f01, p14) et **il garde l'arme et la vie de la fiche** quand elle les dit
  (`arme: ""`, `vie`) — le bâton et 160 de vie restent le défaut.
- **c07, _Monsieur Bois_ (600 $, + la moitié sans une bosse)** — les élèves ont vendu le mannequin d'érable de 1976 à
  la fourrière ; Gilles te prête son camion (`monter`, `prete`), on le livre à la porte de l'école (`livrer`,
  `ecole_mante` — un lieu de la bande, accepté par le juge des lieux comme le Dragon d'or ; rayon 6 : la rue est à
  quatre tuiles en diagonale de la porte), `sans_degats`. **En échange, il t'apprend le retournement du poignet**
  (`donne.technique`, neuf, lu par `Histoire.recompenser` : comme une leçon réussie au DOJO DION, sans la payer ; déjà
  sue, rien de plus). Le camion détruit, c'est raté.
- **c08, _Les portes ouvertes_ (1 200 $)** — on escorte le vieux maître à pied jusqu'au Dragon d'or (`proteger` : un
  donneur DEDANS est posé à la porte de son école quand on sort, et suit sur nos pas), où Irène pose son affiche ; les
  quatre derniers frimeurs arrivent en courant (`tuer`, `ou: donneur`, `loin`). ⚠️ Retouche du moteur : **un personnage
  qu'une escorte a posé ne se sauve plus avec les figurants** (`Histoire.nettoyer`) — il reste planté là, et la fin se
  dit devant lui (Irène y gage cinq piasses qu'il en aura dix au cours).
- **Ce qui change au quartier** (`mantes.REPRISE`, `apres: c08`, comme `tripot.REPRISE`) : dans la salle, les élèves ne
  sont plus du gang, tiennent leur place et font face au maître, qui compte — « UN, DEUX… LA MANTE! », deux secondes
  sur quatre (`Histoire.majBulles`) ; dans la rue, sur leur territoire, **une naissance sur six** est encore un Mante au
  lieu d'une sur deux (`Entites.partDehors`, sans un dé de plus : le même tirage, un autre seuil) ; le gang est
  **calme** (`donne.calme`) ; et le lendemain, le Clairon titre **L'ÉCOLE LA MANTE ROUVRE** (`journal.SPECIALES`).
  La provocation à mains nues (l'autre ligne, livrée le même jour) lit `Entites.gangCalme` : après c08, plus aucun
  Mante ne défie personne.
- **Le paquet** : les définitions passent 62 235 → 62 874 gzip (+639 : le catalogue, le personnage, son visage, sa
  tenue, la reprise), sous les 64 000 que l'autre ligne avait posés le même soir ; le brut passe 280 599, et son
  plafond (un indicateur) 280 000 → 285 000, la mesure écrite dans `test_definitions`. Le remède d'en haut (sortir du
  paquet ce qui ne sert pas à tout le monde) reste à trancher par Martin.
- **Juges** : `tests/test_vieux_maitre_js.py` (7) — le maître absent avant c04, dans sa salle après, son repos ; c05,
  c06, c07 et c08 joués au bouton de la poignée de main à la prime (les hommes nés où il faut, avec ce qu'ils tiennent ;
  la filature ; le camion prêté, livré sans bosse, la prime et demie, la technique apprise ; l'escorte, les frimeurs,
  le maître qui ne se sauve pas, le gang calme, la une) ; le monde d'après contre le même monde avant (la salle, la
  bulle, la rue : 149 Mantes sur 280 naissances avant, 33 sur 124 après, graine 11) ; ce qu'un donneur apprend est une
  technique payante. `test_mantes` (le point du maître, sur le plancher, personne sous lui), `test_missions` (le lieu
  de l'école, son repos unique). Sept mutations, toutes rouges : le maître là avant c04, la même part de Mantes
  dehors, des élèves encore du gang, la technique jamais apprise, le maître qui se sauve, Kenny qui vient au joueur,
  Kenny à la batte. Captures regardées (Chromium) : la salle en classe, sa bulle, son portrait.
- **Les voix** : 45 fichiers générés le 29 sept. 2026 (eleven_v3) — les 32 répliques du maître (Luca) et son repos,
  les 11 d'Irène (Meera), et la une du Clairon lue par le narrateur ; ≈ 4 700 caractères, **2 938 crédits**
  (compteur ElevenLabs : 34 032 → 36 970). Luca en v3, à écouter par Martin.
