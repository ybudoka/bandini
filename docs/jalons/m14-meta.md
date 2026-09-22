# M14 Meta

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M14 — Meta (**ajout**, taille 4)_

- **Un compte et une base de données** (demande de Martin, précisée le 15 sept. 2026 :
  « des sauvegardes sur le serveur dans une base de données, connexion par compte avec
  session ouverte longue durée avec option d'ouverture par NIP »). Aujourd'hui la partie vit
  dans le `localStorage` du navigateur : elle ne traverse pas. Vingt minutes au téléphone,
  puis on s'assoit à l'ordi, et on recommence. Un compte règle ça, et il porte aussi le défi
  du jour et le classement — qui ont besoin d'un serveur de toute façon. ⚠️ **Le détail de la
  sauvegarde, de la session longue et du NIP est plus bas**, dans sa propre partie : c'est
  là que se trouvent les chiffres et les pièges.
  - **`app/bd.py` + SQLite**, sous `DONNEES_DIR`. Une seule machine, deux workers gunicorn,
    quelques dizaines de joueurs : un serveur de base de données serait une pièce de plus à
    installer, à surveiller et à redémarrer pour rien. ⚠️ **WAL et un `timeout`**, sinon les
    deux workers se marchent dessus et ça donne `database is locked` — en production
    seulement, jamais en local où il n'y a qu'un worker.
  - **`app/comptes.py`** : pseudo + mot de passe haché (`generate_password_hash`, déjà là
    avec Flask), session signée. ⚠️ **`SECRET_KEY` vaut encore `cle-de-developpement-a-changer`
    par défaut** — tant qu'un compte n'existe pas, ça ne coûte rien ; le jour où une session
    vaut une partie, une clé par défaut en production laisse forger n'importe qui. Le
    `installer.sh` doit la générer et refuser de démarrer sans elle.
  - **Ce qu'on demande, et rien d'autre** : un pseudo, un mot de passe, et un courriel
    **facultatif** qui ne sert qu'à reprendre un mot de passe perdu. Sans lui, un mot de
    passe perdu est un compte perdu, et c'est écrit noir sur blanc à l'inscription. Une page
    dit ce qui est gardé et comment tout effacer — c'est un jeu pour s'amuser, pas une
    raison de tenir un fichier sur du monde.
  - ⚠️ **Le compte ne devient jamais obligatoire.** Le `localStorage` reste le défaut : on
    joue sans compte, comme avant, et le compte n'est qu'une **synchronisation**. Sinon une
    panne de serveur, une connexion coupée dans l'autobus ou un certificat expiré empêchent
    de jouer à un jeu qui tourne entièrement dans le navigateur.
  - ⚠️ **Le tableau des scores ne déménage nulle part : il n'existe plus** (17 sept. 2026,
    demande de Martin — voir « Le tableau des scores s'en va »). Ce qu'il en reste, la règle
    du pseudo, vit dans `comptes.py` ; `economie.GAIN_MAX_PAR_SECONDE` reste une borne
    d'équilibre des boulots, jugée par `test_economie`.
  - ⚠️ **On ne peut pas empêcher la triche d'un jeu qui tourne dans le navigateur** — une
    partie qu'on peut poster est une partie qu'on peut fabriquer. Ce qu'on peut faire, c'est
    que ça ne rapporte rien : le classement garde sa borne, le serveur garde la durée et la
    date de chaque partie, et une partie reprise repart avec sa durée, pas à zéro.
  - **Le schéma va changer** : la sauvegarde a déjà `version` + `empreinte` + le repli de
    `completer()`. La même discipline s'applique côté serveur — une migration par version,
    jamais une colonne ajoutée à la main sur le serveur.
  - **Une BD, c'est quelque chose à sauvegarder.** `deploy/installer.sh` pose un vidage
    quotidien (`.backup`, pas une copie du fichier à chaud) et une rétention de sept jours.
    Une base de données sans copie de sûreté est une perte de données qui attend sa date.

### Les parties vivent sur le serveur — compte, session longue, NIP (15 sept. 2026)

_Demande de Martin :_ « je veux des sauvegardes sur le serveur dans une base de données.
Connexion par compte avec session ouverte longue durée avec option d'ouverture par NIP. »

**Mesuré d'abord, parce que les chiffres tranchent la moitié des questions :**

- une partie neuve pèse **790 octets** ; une partie bien avancée (toutes les armes, vingt
  paquets, cinq missions, quarante lignes de journal, vingt personnages connus, les paliers de
  boulot) pèse **4,5 Ko**, en 39 champs. Mille joueurs avec trois parties chacune : **13 Mo**.
  SQLite n'a pas à réfléchir, et le débat « vraie base de données ou non » n'existe pas ;
- le jeu se sauvegarde **tout seul toutes les dix secondes** (`B.t % 600`, dans `Missions.maj`).
  ⚠️ **Ce chiffre-là décide du reste** : on ne poste pas six fois par minute par joueur ;
- l'installeur **génère déjà** une vraie `SECRET_KEY` (`secrets.token_hex(32)` dans le `.env`
  partagé, depuis M0). La dette qui reste n'est donc pas de la générer, c'est de **refuser de
  démarrer** avec la clé de développement quand `FLASK_DEBUG` est faux.

**La règle : le local joue, le serveur se souvient.** Le `localStorage` reste la vérité pendant
qu'on joue — c'est déjà la promesse de M14, et c'est ce qui permet de jouer dans l'autobus. Le
serveur reçoit des **instantanés**, jamais chaque image.

- **Quand un instantané monte** : à la sauvegarde volontaire (le lit de la planque, le menu),
  au changement de jour, à la fin d'une mission, quand l'onglet part en arrière-plan — et au
  plus **une fois par minute** le reste du temps. ⚠️ `beforeunload` ne se déclenche pas de
  façon fiable sur téléphone : c'est `visibilitychange` qui compte, avec `sendBeacon`, la
  seule requête qui survit à la fermeture de l'onglet.
- ⚠️ **Le conflit est la vraie question, et il se règle par un compteur, jamais par une
  horloge.** Deux appareils n'ont pas la même heure ; un compteur qui monte à chaque écriture,
  oui. Le serveur **refuse** un instantané dont le compteur est plus petit ou égal au sien et
  renvoie ce qu'il a. Le jeu pose alors la question en clair — « LA PARTIE DU SERVEUR EST PLUS
  AVANCÉE : JOUR 12, 4 300 $. GARDER CELLE-CI / PRENDRE CELLE-LÀ » — et **ne fusionne jamais
  rien** : deux parties ne se fusionnent pas, et un jeu qui tranche tout seul efface la soirée
  de quelqu'un.
- **Trois emplacements** par compte. Ça ne coûte qu'une colonne, et ça évite la question
  « j'ai fini le jeu, est-ce que je perds ma partie si j'en recommence une ? ». ⚠️ **Ils existent
  déjà dans le navigateur** (17 sept. 2026, ligne « Trois sauvegardes, et on les gère ») :
  `Sauvegarde.cle(n)`, le dernier emplacement joué, copier et effacer. Le serveur reflète ces
  trois cases, il ne les invente pas.

**La base** — quatre tables, et elles tiennent en une page :

| Table | Ce qu'elle garde |
|---|---|
| `comptes` | pseudo (unique ; la règle vit dans `comptes.py`), empreinte du mot de passe (`generate_password_hash`, scrypt), courriel **facultatif**, date de création |
| `parties` | compte, emplacement (1–3), **compteur**, le JSON de la partie (4,5 Ko), version du schéma, empreinte des définitions, date |
| `appareils` | compte, **empreinte** du jeton (jamais le jeton), nom donné par le joueur (« le téléphone »), dernière visite, date de péremption |

**La session longue durée** — c'est un **jeton d'appareil**, pas un mot de passe qu'on retape :

- 32 octets aléatoires, posés en cookie `httpOnly; Secure; SameSite=Lax; Max-Age=1 an`, et
  ⚠️ **hachés en base comme un mot de passe** : une base volée ne doit pas ouvrir les comptes.
- **Il tourne** : chaque usage en émet un nouveau et périme l'ancien. ⚠️ Et c'est ce qui donne
  la détection de vol gratuitement — si un jeton **déjà périmé** revient, c'est que deux
  appareils portent la même session : on coupe tous les appareils du compte et on redemande le
  mot de passe. C'est la seule façon simple de réagir à un vol de cookie. ⚠️ **Livré
  autrement** (17 sept. 2026) : il tourne à l'**ouverture** du jeu, pas à chaque requête — des
  requêtes qui se croisent passeraient pour un vol (voir les notes de M14).
- Le mot de passe ne sert donc qu'à **lier un appareil**, une fois. C'est tout ce qu'on tape.

**Le NIP** — et ⚠️ **il faut dire tout de suite ce qu'il n'est pas** : le NIP **n'ouvre pas un
compte**, il rouvre une session sur un appareil **déjà lié**. Quatre chiffres, c'est 10 000
possibilités : inacceptable comme secret de compte, parfait comme verrou d'écran.

- À l'ouverture, si l'appareil porte un jeton, le jeu ne demande **que le NIP**.
- Le NIP **déchiffre le jeton localement** : ce qui dort dans le navigateur est le jeton
  **chiffré** par une clé dérivée du NIP (WebCrypto, PBKDF2 — présent dans tous les
  navigateurs visés). Sans le NIP, le contenu du stockage ne vaut rien à lui seul.
- **Cinq essais**, puis le jeton chiffré est **effacé** et il faut le mot de passe. ⚠️ Le
  **compte**, lui, ne se bloque pas : bloquer un compte parce qu'un inconnu a tapé cinq fois
  sur un téléphone perdu punirait exactement la mauvaise personne.
- ⚠️ **Ce qu'un NIP promet, et rien de plus** : il arrête quelqu'un qui emprunte le téléphone
  deux minutes. Il n'arrête pas quelqu'un qui l'emporte chez lui et prend son temps — 10 000
  candidats, ça s'essaie hors ligne. La vraie protection est ailleurs et elle existe déjà : le
  jeton **tourne**, le serveur peut le révoquer, et ce qu'il y a à voler est une partie de jeu
  vidéo. C'est écrit ici pour que personne ne prenne le NIP pour ce qu'il n'est pas.
- **Facultatif**, et il ne remplace jamais le mot de passe : sans NIP, la session longue
  s'ouvre toute seule, comme sur un site où l'on reste connecté. Avec NIP, elle demande quatre
  chiffres. ⚠️ Et on refuse les vingt NIP les plus tapés de la Terre (0000, 1234, 1111,
  l'année en cours) — c'est une liste, pas un algorithme.

**Ce qui ne doit jamais arriver**, et chacun a son juge :

- ⚠️ **Le serveur en panne ne doit pas empêcher de jouer.** Toute la synchronisation est
  « au mieux » : un appel raté se retente plus tard, et rien dans la boucle de jeu n'attend une
  réponse. Un compte est un **confort**, jamais une condition.
- ⚠️ **Une partie plus vieille ne peut pas écraser une plus neuve** — c'est le compteur, et
  c'est le juge le plus important de la fiche.
- ⚠️ **Effacer un compte efface pour vrai** : les parties disparaissent, les appareils sont
  révoqués. Un bouton, une confirmation, et
  une page qui dit ce qui est gardé.
- ⚠️ **Le mot de passe perdu sans courriel est un compte perdu**, et c'est écrit à
  l'inscription, pas découvert après.

**Juges** : un instantané au compteur plus petit ou égal est refusé et rend celui du serveur ;
un jeton périmé qui revient coupe tous les appareils du compte ; cinq NIP ratés effacent le
jeton local sans toucher au compte ; les vingt NIP interdits le sont ; le jeton n'existe en
clair nulle part dans la base ; une partie de 4,5 Ko ne monte pas plus d'une fois par minute
hors des moments déclarés ; le jeu démarre et se joue avec l'API des comptes éteinte ; effacer
un compte efface ses parties et révoque ses appareils ; et l'application **refuse de démarrer**
en production avec la clé de développement.

- **Défi du jour** à graine serveur (reporté de M7) : `/api/defi` donne la graine du jour,
  le classement est celui du jour, tout le monde joue la même ville.
- **Mode photo** : le jeu se fige, la caméra se détache, quelques filtres, et l'image se
  télécharge.
- **Coop locale** (risqué) : deux manettes, une caméra qui tient les deux joueurs, zoom
  arrière quand ils s'éloignent. ⚠️ 480 × 270 n'est pas grand : à décider **après un essai**,
  pas avant.

## Notes

**un compte et une base de données** (demande de Martin, précisée le 15 sept. 2026) : **les
parties vivent sur le serveur** (SQLite, trois emplacements, un **compteur** par partie —
jamais une horloge — et le joueur tranche quand deux appareils divergent), **session longue
durée** par jeton d'appareil **tournant** (cookie d'un an, haché en base, un jeton périmé
qui revient coupe tous les appareils), et **ouverture par NIP** — ⚠️ le NIP rouvre une
session sur un appareil déjà lié, il n'ouvre **pas** un compte : il déchiffre le jeton
localement, cinq essais et le jeton s'efface, le compte ne se bloque pas. Mesuré : une
partie pèse 790 o à 4,5 Ko. Plus le défi du jour à graine serveur (reporté de M7), le mode
photo, la coop locale

**Le découpage** (17 sept. 2026) : **(1)** le compte, la session longue et les parties sur
le serveur — `app/bd.py` (SQLite, WAL, migrations par `user_version`), l'inscription, le
jeton d'appareil qui tourne, les instantanés au compteur, et le refus de démarrer en
production avec la clé de développement ; **(2)** le jeu se synchronise — les moments où un
instantané monte, `sendBeacon`, la question « garder celle-ci / prendre celle-là » ; **(3)**
le NIP ; **(4)** effacer son compte (le tableau des scores devait déménager ici : il a été
retiré du jeu le 17 sept. 2026) ; puis le défi du
jour, le mode photo et la coop.

**1re vague livrée** (17 sept. 2026) : le serveur sait tout faire, et **le jeu ne s'en sert
pas encore** — aucun écran ne crée de compte, c'est la 2e vague. `app/bd.py` (SQLite sous
`DONNEES_DIR`, WAL, `BEGIN IMMEDIATE`, migrations numérotées par `user_version`, ouverte à
la première requête de compte et jamais au démarrage) ; `app/comptes.py` (inscription,
connexion, jeton d'appareil, trois cases au compteur) ; six routes sous `/api/compte/`
(`inscription`, `connexion`, `ouvrir`, `deconnexion`, `parties/<n>` en GET et en POST) ; le
refus de démarrer avec la clé de développement ; le vidage quotidien
(`deploy/sauvegarder_bd.py` et sa minuterie systemd, sept copies gardées). Juges :
`tests/test_comptes.py` et `tests/test_bd.py`, chacun **vu rouge** en retirant sa règle (le
compteur, la preuve de vol, `BEGIN IMMEDIATE`, le refus, l'empreinte du jeton, la grâce, la
borne de la route, `foreign_keys`).

- ⚠️ **Le jeton tourne à l'OUVERTURE du jeu, pas à chaque requête** — la fiche disait «
  chaque usage ». Un jeu envoie des requêtes qui se croisent (une sauvegarde lente partie
  avant la rotation, un `sendBeacon` dont personne ne lit la réponse) : avec une rotation
  par requête, chaque retardataire arriverait avec un jeton déjà remplacé et passerait pour
  un vol — tous les appareils coupés, pour rien. `POST /api/compte/ouvrir` tourne le jeton
  une fois par chargement ; **la 2e vague doit attendre sa réponse avant tout autre appel de
  compte**.

- ⚠️ **Une réponse perdue ne coupe personne** (l'autobus) : tant que le nouveau jeton n'a
  JAMAIS servi, l'ancien reste accepté — tel quel pendant `GRACE_S` (2 min : deux onglets
  ouverts ensemble), puis l'ouverture en émet un autre. L'ancien ne devient une preuve de
  vol qu'une fois son successeur vu (`appareils.precedente` et `vu`, puis `jetons_perimes`).

- ⚠️ **Effacer une case garde son compteur** (`partie` NULL) : sans lui, la vieille copie
  d'un autre appareil reviendrait remplir la case vidée. Et les écritures passent par
  `POST`, pas `PUT` : `sendBeacon` ne sait faire que POST.

- ⚠️ **La production se reconnaît à `APP_BASE_URL` en https**, pas à `FLASK_DEBUG` :
  `.env.example` met `FLASK_DEBUG=false`, et le serveur du salon aurait refusé de démarrer
  avec `change-cette-cle`. Le même signal rend le cookie `Secure` — en http sur le wifi, un
  cookie `Secure` ne serait jamais gardé par le téléphone. **Mesuré sur le serveur** (en
  lecture) : clé de 64 caractères, `https://bandini.gestiondojo.ca`, Python 3.12.3, SQLite
  3.45.1 (l'`UPSERT` demande 3.24).

- ⚠️ **La borne du site reste de 16 Ko** (`test_corps_trop_gros`, mesurée depuis le retrait
  du tableau des scores sur l'inscription) : la route
  d'une partie relève la sienne à 52 Ko (`REQUETE_PARTIE_MAX_OCTETS`, par
  `request.max_content_length`), sous le `client_max_body_size 64k` de nginx — au-delà,
  nginx répondrait en HTML.

- ⚠️ **À faire sur le serveur, une fois** : relancer `installer.sh` (idempotent) pour poser
  `bandini-sauvegarde-bd.timer` et `shared/copies/` — `deploy.sh` ne touche pas systemd.
  Rien ne presse tant que personne ne peut créer de compte : la base n'existe qu'à la
  première requête de compte.

**2e vague livrée** (17 sept. 2026) : **le jeu se synchronise**, et le compte se voit enfin.
`static/js/compte.js` (le seul endroit du jeu qui parle à `/api/compte/`), l'**écran du
compte** au titre (une voile DOM — un mot de passe se tape, et un menu de manette sait
choisir, pas écrire ; le bouton porte le pseudo dès qu'un compte est ouvert), le **compteur
des sauvegardes** dans `Sauvegarde` (`base.js`), et le **choix entre deux versions** dans le
menu des PARTIES.

- ⚠️ **L'ouverture passe en premier, et SEULE.** Le jeton tourne à
  `POST /api/compte/ouvrir` : un appel de compte parti avant sa réponse arriverait avec un
  jeton déjà remplacé et passerait pour un vol — tous les appareils coupés, pour rien. Tout
  ce que le jeu demande attend derrière sa promesse, dans une file où deux appels ne se
  croisent jamais. C'est une **connexion** qui le prouve au banc : elle, n'attend pas d'être
  « ouvert » pour partir.

- ⚠️ **Le compteur seul ne dit pas s'il y a conflit.** « Mon local est à 41, le serveur à
  40 » ne dit pas si j'ai joué depuis SA version ou si nous avons joué chacun de notre côté.
  La réponse est dans ce que cet appareil a vu du compte la dernière fois
  (`bandini-compte-sync-v1`, rangé sous le pseudo : un autre compte repart à zéro). Sans ce
  témoin, il n'y a que deux issues et les deux sont fausses — écraser en silence, ou poser
  la question à chaque partie. `decision(n)` tranche seule les cas évidents (une case vide
  d'un côté se remplit de l'autre) et ne dérange le joueur que quand les deux ont bougé.

- ⚠️ **Une case vide qui reçoit, ce n'est pas la même chose qu'une case à zéro.** La partie
  de Martin dort dans le navigateur depuis des semaines et n'a pas de compteur : à zéro, elle
  passerait pour une case vide et la première connexion la remplacerait sans un mot. Elle
  démarre donc à 1 ; ce qui est vide reste à zéro, et c'est ça qui dit « il n'y a rien ici ».

- ⚠️ **Rien ne s'écrit sous les pieds de quelqu'un qui joue — et la garde est là où ça
  écrit**, pas avant la requête : entre la demande et la réponse il se passe une seconde, et
  une seconde suffit pour presser JOUER. La partie descendue serait alors écrasée dix
  secondes plus tard par la sauvegarde automatique de celle qu'on joue, et l'autre appareil
  aurait perdu sa soirée sans que personne ne comprenne. Elle devient une question, posée au
  retour au titre.

- **Trois moments où un instantané monte** : le repos de 90 s pendant qu'on joue (la partie
  se sauve toutes les dix secondes en local, le serveur n'a pas besoin de les voir toutes),
  le **retour au titre** (`Compte.ranger`), et le **départ de la page** — `sendBeacon`, le
  seul appel qui survit à la fermeture d'un onglet sur téléphone, avec un Blob
  `application/json` sinon Flask ne lit pas le corps. ⚠️ Le beacon ne part **jamais** sur une
  case en désaccord : personne n'en lit la réponse, il écraserait celle de l'autre appareil,
  et la question qu'on s'apprêtait à poser n'aurait plus d'objet.

- ⚠️ **Une réponse 200 sans le champ `partie` n'efface rien** (un proxy, une page d'erreur en
  JSON) : le vrai serveur en met toujours un, `null` compris. Vider une case sur une réponse
  qu'on ne comprend pas, c'est perdre une partie pour de bon.

- ⚠️ **Deux choses que le banc ne pouvait pas voir, et qu'une capture Chromium a montrées**
  (17 sept. 2026) : le formulaire restait à l'écran une fois connecté — `.score-form` est en
  `display: flex`, qui **bat l'attribut `hidden`** —, alors que le banc lisait bien
  `hidden === true` ; et « Bonjour, Martin » vivait DANS ce formulaire, donc le seul mot qui
  dit que ça a marché se cachait à la seconde où il servait. Deux juges de navigateur en
  sortent (`test_navigateur.py`) : un compte créé **de bout en bout** (l'écran, le POST,
  SQLite, le cookie `HttpOnly` que le JS de la page ne peut pas lire) et un serveur de
  comptes **en panne** qui ne barre pas le chemin de JOUER.

- **Juges** : `tests/test_comptes_js.py` (**30**) plus les deux du navigateur, et **17
  mutations toutes rouges** — la file, le compteur, le témoin, la partie posée telle quelle,
  le refus qui ne fusionne rien, la garde du joueur qui joue, le type du beacon, les deux
  choix du menu. Le banc a appris trois choses pour ça : `ENTREE.reseau` (un faux
  `/api/compte/` dont on peut **tenir** une réponse en vol, et qui distingue GET de POST sur
  la même adresse), `fenetreEvenement` (le `pagehide` joué comme le navigateur le joue —
  juger `Compte.partir()` en l'appelant soi-même ne dirait rien du jour où plus personne ne
  l'appelle) et un `innerHTML` qui vide vraiment la liste des enfants.

- ⚠️ **Deux gardes ont été retirées parce qu'aucune mutation ne les faisait rougir** : une
  question déjà posée restait posée alors que les compteurs le disaient déjà, et `jeu.js`
  revérifiait l'écran titre que `Compte` garde déjà. Une garde jamais exercée n'est pas une
  ceinture de sécurité, c'est une promesse que personne ne vérifie — et elle mentira le jour
  où l'autre tombe.

**3e vague livrée** (17 sept. 2026) : **le NIP**, un verrou d'écran sur un appareil déjà
lié — et il faut redire tout de suite ce qu'il n'est pas : il **n'ouvre pas un compte**.

- **Tout se passe en local, et le serveur ne connaît ni ne voit jamais le NIP.** Ce qui
  dort dans le navigateur est le jeton d'appareil — le MÊME que celui du cookie `httpOnly`,
  jamais un second secret —, chiffré par une clé dérivée du NIP (PBKDF2 → AES-GCM,
  WebCrypto). La seule nouveauté côté serveur est une route qui **révèle ce jeton en clair,
  une fois** : `POST /api/compte/nip` lit le cookie `httpOnly` (`httpOnly` bloque le JS de
  la page, pas le serveur) et le rend tel quel — de quoi le chiffrer localement.
- ⚠️ **Le contenu déchiffré ne sert jamais à rien d'autre qu'à prouver qu'on connaît le
  NIP.** La vraie réouverture repasse par le cookie `httpOnly`, exactement comme sans NIP —
  c'est pour ça qu'un jeton qui a tourné depuis (donc périmé côté serveur) reste un secret
  local parfaitement vérifiable : seule l'étiquette d'authentification d'AES-GCM compte,
  jamais ce qu'elle protège.
- ⚠️ **Facultatif, il ne remplace jamais le mot de passe** : sans NIP configuré sur cet
  appareil, `Compte.init()` appelle `ouvrir()` sans rien demander, exactement comme les 1re
  et 2e vagues. Avec un NIP, `init()` s'arrête à `etat = 'verrouille'` et **aucune requête
  ne part** avant `deverrouiller(nip)` — un jeu qui bavarde avec le serveur avant d'avoir vu
  le NIP ne serait pas un verrou, ce serait une case à cocher.
- ⚠️ **Rien d'autre n'en souffre** : `decision()`, `apresEcriture()`, `ranger()` et
  `partir()` se taisent déjà tous si `etat !== 'ouvert'` — verrouillé se comporte comme
  n'importe quel autre état non ouvert. JOUER reste JOUER, verrouillé ou pas : un compte est
  un confort, jamais une condition, ici comme partout ailleurs dans M14.
- ⚠️ **Le compte ne se bloque jamais, même après cinq essais ratés** — la même raison qui
  fait qu'un mot de passe n'a pas de limite d'essais côté serveur : bloquer le COMPTE parce
  qu'un inconnu a tapé cinq fois sur un téléphone perdu punirait exactement la mauvaise
  personne. Cinq échecs **effacent le jeton chiffré de cet appareil**, rien de plus, et il
  faut retaper le mot de passe pour le relier. Le compteur d'essais **vit dans le blob
  chiffré** (jamais en mémoire), donc il survit à un rechargement — sinon la limite se
  contournerait en rafraîchissant la page avant chaque essai.
- ⚠️ **La liste noire et le format se vérifient avant tout appel réseau** : les vingt NIP
  les plus tapés de la Terre (0000, 1234, 1111… et l'année en cours, calculée) sont refusés
  sans jamais exposer le jeton pour rien.
- **Se déconnecter efface aussi le NIP local** : oublier un appareil, c'est l'oublier pour
  de bon — un NIP qui survivrait rouvrirait un verrou sur un compte qui n'est plus lié à
  rien.
- **L'écran** : le formulaire du NIP est **seul** à l'écran tant qu'on n'a pas tapé les
  quatre chiffres, jamais en même temps que le mot de passe — deux portes ouvertes à la fois
  n'en protègent aucune. « Mot de passe plutôt » montre le formulaire habituel **sans**
  toucher au NIP local (un contournement d'un chargement, pas un « oublie mon NIP »). Une
  fois le compte ouvert, un formulaire propose d'ajouter un NIP à cet appareil, ou de le
  retirer s'il y en a déjà un.
- **Juges** : `tests/test_comptes_js.py` (**+13**), deux dans `test_comptes.py` (la route
  serveur), deux de bout en bout dans `test_navigateur.py` (activer un NIP puis **recharger
  la page pour de vrai** — localStorage et le cookie `httpOnly` survivent tous les deux,
  c'est justement ce que le NIP protège —, et un appareil verrouillé qui ne parle jamais au
  serveur même en jouant), et **11 mutations toutes rouges**. Le banc a appris WebCrypto
  (`node:crypto`'s `webcrypto`, aussi vraie que celle d'un navigateur), `btoa`/`atob` et
  `TextEncoder`/`TextDecoder`.

- **Reste de M14** : le mode photo et la coop locale.

**5e vague livrée** (20 sept. 2026) : **le défi du jour** — et il faut dire d'abord ce qu'on a
**tranché sans pouvoir demander**, parce que la fiche tenait en deux lignes (« `/api/defi`
donne la graine du jour, le classement est celui du jour, tout le monde joue la même ville »)
et se heurtait à un choix de Martin.

- ⚠️ **Il n'y a pas de classement.** Le tableau des scores est parti le 17 sept. 2026 à sa
  demande (« le score pourrait être complètement enlevé » — **tout** s'en va, et un juge tient
  que le mot n'est plus dans la page) : le « classement du jour » partait avec lui, et le
  rebâtir aurait défait ce choix. Ce qui reste du défi du jour est ce que personne n'a retiré :
  une date, un défi, une prime. **Si Martin veut un classement**, c'est un ajout — une table
  (compte, date, temps), une route qui reçoit un résultat, et la question de la triche que la
  fiche de M14 a déjà tranchée (« on ne peut pas l'empêcher : que ça ne rapporte rien ») — pas
  une correction de ce qui est livré.
- **Le défi du jour est l'un des six défis qui existent déjà** (le Grand Saut, le Tour du
  Faubourg, la Livraison sans bosse, et les trois jeux d'adresse de la foire), **désigné par la
  date** ; le serveur en est l'horloge, parce qu'un jeu qui tourne dans le navigateur ne décide
  pas seul du jour qu'on est. Le réussir paie **sa prime une fois par jour**, même s'il a déjà
  été fait (les six ne paient sinon qu'une fois), **en plus** de celle de la première fois — un
  seul versement, un seul message. Le titre l'annonce, et le menu du panneau dit ce qu'on va
  toucher (`DÉFI DU JOUR · 500 $`, puis `RÉUSSI AUJOURD'HUI`).
- ⚠️ **Sans réseau, il n'y a pas de défi du jour** — et le jeu ne s'en aperçoit pas : un
  bonus, jamais une condition. Pas de repli sur l'horloge du téléphone, qui est justement ce
  qu'on évite en demandant la date au serveur. Ce que le serveur dit se vérifie : une date qui
  n'en est pas une, ou un défi que **ce** catalogue ne connaît pas (version d'avant, d'après),
  est ignoré comme s'il n'y en avait pas.
- ⚠️ **La graine ne sert qu'à choisir, et la réponse n'en porte pas.** Les six défis sont
  déterministes (ni `B.rng` ni `hash2` : une rampe, un circuit, une livraison, trois jeux à
  cibles fixes) : un nombre de plus dans `/api/defi` n'aurait eu aucun lecteur. Ce que la fiche
  appelait « la graine du jour » **désigne** un défi, rien de plus — et un juge tient que la
  réponse n'a que `date` et `defi`. (Ce que la « graine du jour » du jeu pilote déjà — météo,
  entraves, prix — dépend du **jour de la partie**, pas de la date réelle ; les rendre communs à
  tous demanderait de forcer le jour de chaque partie, et n'est pas fait.)
- ⚠️ **Une rotation, pas un tirage** : `(jour − EPOQUE) % n`. Chaque défi revient tous les `n`
  jours, jamais deux fois de suite, et rien n'y dépend du processus — pas de `hash()` (salé, le
  piège de `ci-pile-ou-face`). Ajouter un défi au catalogue le fait entrer dans la rotation et
  peut **changer le défi du jour en pleine journée** au déploiement ; c'est pourquoi la prime se
  paie **par date du serveur** (`defiDuJour.date`) et jamais par slug : deux défis du jour le
  même jour ne paient pas deux fois.
- ⚠️ **Le jour bascule à minuit heure de Québec**, pas à minuit UTC (20 h en été : un joueur du
  soir verrait « demain » avant la fin de sa soirée). **À vérifier sur le serveur, une fois** :
  `python3 -c "import zoneinfo; zoneinfo.ZoneInfo('America/Toronto')"` — `tzdata` n'est pas une
  dépendance du projet et le code compte sur celui du système. S'il manque, la route ne plante
  pas : elle retombe sur UTC-5 avec un avertissement dans le journal, et le jour ne bascule
  qu'à 1 h en été.
- ⚠️ **`/api/defi` est un préfixe de `/api/definitions`** — et ça m'a coûté 102 juges rouges d'un
  coup : le faux `fetch` du banc comparait par `indexOf(…) === 0`, captait le paquet du jeu et
  répondait « réseau coupé » à tout le chargement. Le vrai code n'a pas ce défaut, mais la
  frontière se juge : l'adresse est un `data-url-defi` que la **coquille hors ligne** ne lit pas
  (un défi gardé par le travailleur passerait minuit sans le savoir), et un juge vérifie que
  `/api/definitions` y est et pas `/api/defi`.
- ⚠️ **La ligne du titre n'est pas une `.aide`** : `body.tactile .aide { display: none }` la ferait
  disparaître sur téléphone, qui est la plateforme du jeu. Et l'écran titre est un `.voile` en
  `overflow: hidden` comme l'était celui du compte : les juges vérifient en portrait
  (390×219 pour l'écran de jeu) et en paysage que ni JOUER ni COMPTE ne sortent de l'écran.
- **Une garde retirée parce qu'aucune mutation ne la faisait rougir** (encore) : le défi était
  cherché dans le catalogue à la porte **et** à chaque lecture ; c'est maintenant une seule
  fois, à la porte.
- **Juges** : `test_defi.py` (**10**), `test_defi_js.py` (**22**) et `test_navigateur.py`
  (**+5** : le vrai serveur, la route qui tombe, la page rouverte le lendemain, la place sur
  téléphone en portrait et en paysage), et **27 mutations toutes rouges** (8 serveur, 16 jeu,
  3 Chromium).

**4e vague livrée** (20 sept. 2026) : **effacer son compte**, et la page qui dit ce qui est
gardé. Le serveur efface pour vrai ; l'écran ne fait que le proposer.

- **Un seul `DELETE FROM comptes`.** Les trois autres tables descendent de lui en
  `ON DELETE CASCADE` (et `bd.ouvrir` allume `foreign_keys` par connexion — sans quoi rien ne
  partirait avec lui). Ce que ça n'efface pas : les copies de sûreté quotidiennes de la base,
  qui s'effacent d'elles-mêmes au bout de sept jours — **et la page le dit**.
- ⚠️ **Le mot de passe est redemandé**, même sur un appareil déjà lié : « un bouton, une
  confirmation », et un cookie d'appareil emprunté ou volé ne doit pas suffire à détruire un
  compte. **Un mot de passe faux rend 403, jamais 401** : un 401 efface le cookie, et une faute
  de frappe à l'effacement aurait délié l'appareil qui vient de la faire (un juge tient
  `MotDePasseIncorrect` hors de `NonAutorise`).
- ⚠️ **SQLite réutilise l'`id` d'un compte effacé** (`INTEGER PRIMARY KEY`, pas
  d'`AUTOINCREMENT`) : si le `CASCADE` lâchait, les parties et appareils orphelins
  s'accrocheraient au **nouveau** compte de même pseudo. La garde qui compte est donc « le
  nouveau compte repart à vide », pas « l'id change » — et le juge de bout en bout ajoute la
  seule preuve qu'un banc ne peut pas donner : **reprendre le même pseudo** dans Chromium.
- ⚠️ **Effacer le compte n'efface pas les parties de ce navigateur** : le `localStorage` reste
  la vérité, le compte n'est qu'une synchronisation. Ce que **cet appareil** oublie : le NIP
  et **le témoin de synchronisation** — qui doit partir avec le compte, pas seulement se ranger
  sous le pseudo : le pseudo se reprend aussitôt, et un témoin resté sur un compte neuf
  parlerait de parties qui n'ont jamais existé là-bas.
- ⚠️ **Rien ne part tant que le serveur n'a pas dit oui**, et une réponse perdue ne se
  présume pas : « rien n'a été effacé » serait un mensonge si le serveur a eu le temps d'agir,
  alors l'écran dit qu'il n'a pas pu **confirmer** (le prochain `ouvrir()` le montrera).
- **La page « Ce qu'on garde »** (un `<details>`, fermé par défaut, sauf sous le verrou du NIP
  qui montre le NIP seul) ne dit que ce qui est **vrai aujourd'hui** — la base et ses copies —
  et ne promet rien qu'aucun code ne tienne : *mot de passe perdu, compte perdu*, courriel ou
  pas, parce que rien ne permet encore de le retrouver (la fiche promettait de l'écrire « à
  l'inscription » : c'est dit ici, pas encore à l'inscription elle-même).
- ⚠️ **Deux défauts de mes vagues précédentes, trouvés en REGARDANT l'écran** (le banc et les
  juges verts les avaient laissés passer) :
  1. **Une faille du NIP (3e vague).** `.boutons` est en `display: flex`, qui bat l'attribut
     `hidden` — le piège de la 2e vague, revenu : « Retirer le NIP de cet appareil » s'affichait
     dans **les quatre états**, dont l'écran **verrouillé**, où il retirait le verrou sans le
     NIP (un emprunteur le presse, recharge, et `init()` — sans NIP — rouvre le compte avec le
     cookie encore valide). Corrigé à deux étages (commit `490c097`) : `.boutons[hidden]` et
     `desactiverNip()` qui refuse tant que `etat !== 'ouvert'`, **quoi que l'écran montre**.
     Le juge est devenu une **matrice de visibilité réelle** (`is_visible`, jamais l'attribut)
     sur les quatre états.
  2. **L'écran du compte était rogné sur téléphone (2e vague).** `.voile` centre son contenu
     dans un `.ecran` en `overflow: hidden` : ce qui déborde était coupé des deux côtés, sans
     défilement. Mesuré : en portrait (écran de jeu de 390×219), « Retour » hors écran et le
     champ du pseudo coupé en haut ; en paysage tout tenait **au pixel près** et la
     confirmation d'effacement (+130 px) l'aurait rognée. `#voile-compte` défile maintenant
     (marges `auto` : le centrage reste quand ça tient — un simple `justify-content: center`
     rend le haut inatteignable dès que ça déborde). Le juge fait défiler **à la molette**, pas
     par `scrollIntoView` ni par le `click` de Playwright, qui défilent même un conteneur
     `overflow: hidden` et laisseraient passer un bouton qu'un doigt n'atteint pas.
- **Juges** : `test_comptes.py` (**+14** : tout ce qui appartient au compte disparaît et
  rien d'un autre compte, les jetons ne valent plus rien, le pseudo repris repart à vide, le
  mot de passe faux ou absent ne touche à rien, 403 et pas 401, deux appareils qui effacent
  ensemble, dont trois par HTTP), `test_comptes_js.py` (**+10**) et `test_navigateur.py`
  (**+4** : le bout en bout avec le pseudo repris, la page, et le défilement en portrait et en
  paysage), **19 mutations toutes rouges** (6 serveur, 13 client et écran).
- ⚠️ **À faire encore, et ce n'est plus optionnel** : la dette « aucune limite d'essais » est
  **échue** (voir la table des dettes) — le formulaire de connexion est public depuis la 2e
  vague, et la confirmation d'effacement est un second endroit où l'on devine un mot de passe.

**6e vague livrée** (22 sept. 2026) : **le mode photo**. Ouvert depuis PAUSE > MODE PHOTO
(comme la carte, mais l'écran reste celui du jeu plutôt qu'un fond noir) : le monde attend
(`B.t` ne bouge plus), la caméra se **détache** du joueur et répond au stick ou aux flèches
(`B.photo.{dx,dy}`, bornée à la ville par `Monde.limitesCamera` — le même calcul que
`cibleCamera`, exposé), ARME cycle cinq filtres (aucun, noir et blanc, sépia, contraste,
froid), ACTION capture et télécharge un PNG (`Base.telecharger`, `cv.toDataURL`), ANNULER (ou
PAUSE ou CARTE) referme et rend la main au jeu.

- ⚠️ **Le filtre se pose sur l'écran, pas dans `Base.fin`.** Première version : un 4e
  paramètre `filtre` sur `Base.fin(ambiance, lampes, corps, filtre)`, appliqué au
  `ctx.filter` juste avant le dernier `drawImage`. Revenu en arrière : `Base.fin` compose
  aussi les phares des chars (`corpsPhares`, un chantier en cours dans le même fichier au
  moment d'écrire ceci) et les deux changements auraient dû se démêler ligne à ligne pour
  livrer sans emporter le travail de l'autre. La bonne coupe existait déjà : `Base.ecran()`
  rend le contexte ÉCRAN, le même que celui où `Base.fin` dessine son dernier `drawImage` —
  poser le filtre dessus AVANT d'appeler `Base.fin`, et le remettre à `'none'` juste après,
  obtient exactement le même effet sans toucher à la signature de `Base.fin` ni à un seul
  caractère de son corps. `Hud.dessiner()`, appelé juste après, n'hérite jamais du filtre.
- ⚠️ **La caméra détachée reste dans la ville.** Sans borne, le stick pousserait la vue sur
  l'eau et le vide sous la mer, jamais peints. `Monde.limitesCamera()` reprend le calcul de
  `cibleCamera` (une carte plus petite que l'écran se centre, sinon `[0, pxW-VW]`) et
  `majPhoto` clampe `B.cam.x + dx` dedans à chaque image. Vérifié en poussant dans un seul
  sens bien plus longtemps qu'il n'en faut pour traverser toute la ville, deux fois de suite :
  si la vue colle vraiment au bord, la deuxième poussée ne déplace plus rien — une mutation
  qui retire le clamp fait dériver la vue bien au-delà de `limitesCamera().xMax`, et le juge
  rougit.
- **Juges** : deux tests dans `test_moteur_js.py` —
  `test_le_mode_photo_fige_le_monde_promene_la_camera_et_capture` (l'ouverture depuis PAUSE,
  `B.t` gelé pendant que `B.image` continue d'avancer, le panoramique, les cinq filtres qui
  cyclent, la capture qui télécharge vraiment un PNG, la fermeture) et
  `test_la_vue_du_mode_photo_ne_deborde_pas_de_la_ville` (la butée, mutée pour confirmer
  qu'elle mord). Le banc (`tests/banc.js`) a appris `canvas.toDataURL` (un faux, `'data:…'`)
  et un `<a>` dont le `click()` s'enregistre dans `o.photo.telechargements` — sans ça, aucun
  juge ne peut dire si l'image est vraiment partie.
- Vérifié à l'œil (Playwright, `run.py` + Chromium headless) : le HUD de jeu disparaît, le
  bandeau du bas affiche le nom du filtre et les trois touches, les trois filtres se
  distinguent clairement les uns des autres, et le panoramique révèle bien de la ville qui
  n'était pas à l'écran avant.
- **Reste de M14** : la coop locale.
