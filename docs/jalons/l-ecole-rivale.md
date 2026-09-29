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

**Reste (une vague 2, à trancher avec Martin)** : une mission des Mantes et son donneur — la fiche ne la prévoyait pas.
Deux pistes : **Irène** (« je gage cinq piasses que tu te fais mettre sur le dos par un gamin de dix-neuf ans en
pyjama vert ») qui en a assez de les voir racketter la boulangerie de la rue ; ou le **vieux maître** revenu de
Floride, qui veut qu'on lui ramène la plaque de son école et ses élèves à la raison — un nouveau personnage, sa fiche
et sa voix. Et, si Martin le veut : que les Mantes provoquent un joueur à mains nues (aujourd'hui, comme les autres
gangs, ils n'attaquent que si tu sors une arme ou que tu frappes).
