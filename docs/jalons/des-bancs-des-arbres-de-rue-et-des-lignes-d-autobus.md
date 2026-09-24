# Des bancs, des arbres de rue et des lignes d'autobus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux des bancs sur le bord de la rue, des arbres de temps à autre
bien positionnés. Aussi des arrêts d'autobus pour se déplacer réellement d'un arrêt à
l'autre selon un tracé, et des bus qui passent aux arrêts aussi ». Prend « l'arrêt
d'autobus » de M12. ✅ **Le mobilier de rue** (`mobilier.py`) : **183 arbres et 49 bancs**
plantés EN RANGÉE le long de chaque bord de rue, au pas du quartier (Les Érables bordés
d'arbres, La Shop presque nue).

- ⚠️ **Bien placé, ça se juge** : jamais à moins de trois tuiles d'une boîte de croisement
  (le feu, le lampadaire, la vue de qui traverse), ni devant une porte ni juste à côté, ni
  au bout d'une sortie de char, ni collé à un autre meuble.
- ⚠️ **Un banc regarde la rue** : quatre dessins (`banc` de face, `banc_nord` de dos,
  `banc_est` et `banc_ouest` de profil), et c'est le côté du trottoir qui choisit.
- ⚠️ Une ruelle qui court derrière toute une rangée n'est pas une entrée : la refuser
  privait d'arbres la moitié du Faubourg — seule la BOUCHE d'une allée est exclue. Son
  propre dé, en tout dernier. ✅ **Les lignes d'autobus** (`autobus.py`, `autobus.js`) :
  **trois lignes** qui partent du terminus — 1 Le Faubourg (armurerie, garage, hôpital,
  casse-croûte, poste), 2 Les Érables et les Quais (dépanneur, hôtel, cantine), 3 La Shop
  (usine, électronique, hôpital) —, **53 arrêts** avec leur abribus (verre, toit, réclame et
  poteau d'arrêt, quatre dessins qui regardent la rue) et leur banc, nommés d'après le lieu
  servi ou le coin : « 3e Rue / 5e Avenue » (les avenues se comptent d'ouest en est, les
  rues du nord au sud). On attend sur le trottoir, l'abribus dit « 2 DANS 45 S », l'autobus
  arrive, **MONTER — LIGNE 2 — 3 $**, on roule pour de vrai derrière la vitre (la caméra
  suit), ACTION demande l'arrêt, et on descend sur le trottoir de cet abribus-là. Recherché,
  le chauffeur n'ouvre pas : un autobus où la police ne suit pas serait la meilleure
  cachette du jeu. La grande carte montre les trois tracés et leurs arrêts.
- ⚠️ **Python trace, JS roule** : un autobus ne choisit jamais une rue.
- ⚠️ **Un autobus qu'on ne voit pas est une HEURE, pas une entité** : sa place sur sa boucle
  ne dépend que du jour et de l'heure de la partie ; il ne devient un char que quand elle
  entre dans la bulle, hors de l'écran, sans un dé du jeu (rouge-avant prouvé en lui en
  faisant tirer un).
- ⚠️ **Le tracé ne passe jamais où la ville peut fermer** (entraves, rues barrées, bris
  d'aqueduc, barrières, pont — d'où aucune ligne vers La Pointe).
- ⚠️ **Quatre défauts trouvés en roulant, chacun sous son juge** : (1) arrêté le centre sur
  la ligne d'arrêt comme le trafic, l'autobus dépassait de 24 px dans le carrefour, se
  faisait accrocher et restait pris 800 images — il guette le feu **une tuile avant** ; (2)
  le tracé faisait des **demi-tours dans les boîtes** pour servir un arrêt d'en face — une
  seule manœuvre par boîte, un virage là où il mène à une voie (`peutSortir`), et l'arrêt du
  lieu choisi **du bon côté** pour le sens du voyage ; (3) une entrave possible sur la voie
  de droite laissait la ligne 3 sur la voie du milieu **105 tuiles sans un arrêt** — il
  manquait le **déport** d'une voie dans la boîte ; (4) la pression qui fait monter faisait
  **redescendre dans la même image** (trois dollars pour rien).
- ⚠️ **Avec le joueur à bord, l'autobus ne s'arrête qu'aux arrêts demandés** : servant les
  vingt abribus d'une ligne, il était plus lent qu'un piéton. Sans lui, il s'arrête si
  quelqu'un attend, et pour la ville quand ça se voit.
- ⚠️ **Le passager est `dansVehicule` sans le volant** (`conducteur` reste `'ligne'`) : tout
  le jeu lit déjà « pas à pied » là-dessus, et `Vehicules.descendre` (l'hôpital, un autobus
  en feu) le pose à côté au lieu de garer l'autobus pour la fourrière.
- ⚠️ **Le parvis du terminus reste nu** (six tuiles) : c'est le trajet de l'ouverture, et un
  abribus à deux tuiles de la porte arrêtait la balle du juge du pistolet et empêchait
  Ti-Guy de revenir à son poste.
- ⚠️ **Le paquet ne porte que le nom et la tuile d'un arrêt** (le sens est la flèche, le
  trottoir et l'abri s'en déduisent) : 670 octets gzip gagnés, 73,9 Ko sous le plafond de 75.
- ⚠️ Les juges de l'ouverture comptent le **car de la scène**, plus les autobus de ligne qui
  passent au terminus. 30 juges neufs (`test_autobus.py`, `test_mobilier.py`,
  `test_autobus_js.py`) ; rouge-avant prouvé **quinze fois** — et quatre juges qui ne
  mordaient pas ont été réécrits : trois relisaient la constante qu'ils jugeaient, un
  demandait justement l'arrêt où l'autobus s'arrête de toute façon. Note honnête : la
  vérification de connexité du mobilier ne se voit pas seule sur cette ville (les autres
  précautions suffisent) ; le juge, lui, rougit dès qu'on les retire en bloc. Reste, pour
  une vague suivante : des passants qui attendent à l'abribus, montent et descendent.
