# M12 La ville vit

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M12 — La ville vit (**ajout**, taille 4)_

_Ce que ça donne :_ une ville qui bouge toute seule, avec ou sans toi.

- **Le chantier** (demande de Martin) : rien ne dit « Québec » comme une voie barrée depuis
  trois ans — et ce n'est pas qu'une farce. C'est une **surcouche** au champ `voie`, tirée
  par la graine du jour : une voie fermée, des cônes orange (le sprite `cone` existe déjà
  dans `OBJETS`), un détour. Le trafic sait déjà se déporter dans la voie d'à côté ; ici il
  n'a plus le choix. La ville devient différente d'un jour à l'autre **sans regénérer une
  seule tuile**, et la police a enfin un endroit où se tenir sans raison.
  - **Pas un chantier : une famille d'entraves** (demande de Martin : « des réparations,
    des blocages de route aléatoires, des détours »). Le même mécanisme — une surcouche au
    champ `voie`, tirée par la graine du jour — porte plusieurs visages, et c'est la
    variété qui fait qu'on ne s'y habitue pas :
    - **la réparation** : une voie fermée, des cônes, un ouvrier ou deux (des piétons
      `intouchables`, comme les enfants) et une pelle mécanique — le trafic se déporte ;
    - **la fermeture** : la rue entière barrée par une barricade et un panneau **DÉTOUR** avec
      sa flèche, et un itinéraire de rechange que le trafic **suit** ;
    - **le bris d'aqueduc** : la rue inondée sur trois tuiles, roulable au ralenti — il
      manque au Faubourg un printemps où la rue est un lac ;
    - **le camion de déménagement** ou l'**autobus en panne** : une entrave qui n'a pas de
      cônes parce qu'elle n'était pas prévue, et qui dure une heure de jeu, pas un jour.
  - ⚠️ **Une entrave ne coupe jamais la ville en deux — et une FERMETURE le pourrait.** Une
    voie fermée sur un boulevard laisse l'autre ; une rue entière barrée change le champ de
    direction lui-même, et une fermeture tirée au hasard peut isoler un quartier. Le juge est
    celui de M1 (`voies_bloquees` : fortement connexes), mais il ne peut pas tourner dans le
    navigateur à chaque jour de jeu. La sortie est celle de tout le dépôt : **Python décide,
    JS calcule**. `carte.py` calcule une fois, avec le juge, la liste des **segments qui
    peuvent se fermer** sans casser la connexité — et le paquet la transporte. La graine du
    jour ne tire que dans cette liste. Un pont n'y est jamais, ni la seule approche d'un
    croisement, ni une rue à voie unique.
  - ⚠️ **Deux entraves ne se combinent pas sans juge.** Deux fermetures prises séparément
    dans la liste peuvent, ENSEMBLE, isoler un bloc. Soit on n'en tire qu'une par jour, soit
    la liste est faite de **paires** validées — jamais de tirages indépendants.
  - **Le détour se lit.** Un panneau DÉTOUR avec une flèche à chaque coin de l'itinéraire de
    rechange, pour le joueur autant que pour le trafic : une fermeture sans détour affiché
    n'est pas une entrave, c'est un piège.
  - **Nid-de-poule** : une tuile qui secoue la caméra et coûte deux points de carrosserie.
    Deux lignes, et toute la ville prend un accent. Jamais dans un croisement (on y freine
    déjà), jamais deux côte à côte.

- **Tramway** : une ligne sur rails du Faubourg aux Quais, des arrêts, des portes — et il
  ne s'arrête pas pour toi. ⚠️ C'est un véhicule qui **ignore** le champ de direction : il
  a ses propres rails, et le trafic doit lui céder.
- **Traversier** : Les Quais ↔ La Pointe, à l'heure, quatre chars à bord, il part sans toi.
- **Tempête de neige** (risqué) : visibilité réduite, adhérence divisée, **charrue** qui
  pousse la neige et les chars mal garés ; la police glisse aussi.
- ⚠️ La neige touche à la physique **et** au rendu : elle arrive derrière une option, et la
  sonde de performance Playwright la mesure avant qu'elle soit allumée par défaut.
- **La nuit de déneigement** — et c'est ce qui donne enfin à la fourrière une raison d'être.
  À Québec, la veille d'une opération, un **feu orange clignote** sur le panneau de la rue :
  interdiction de stationner cette nuit-là, et ce qui reste dans la rue part au lot. Le jeu a
  déjà les trois morceaux — la fourrière (M9), la charrue (ci-dessus), le rythme de nuit — il
  ne manque que le panneau qui clignote **la veille**, pour qu'on ait eu le temps de lire.
  Laisse ton char dans la mauvaise rue, et le lendemain il est au lot : c'est la meilleure
  façon d'apprendre ce que « mal garé » veut dire, parce que ce n'est pas une punition, c'est
  la ville.
- **Les feux passent au clignotant la nuit.** Vrai partout au Québec, et presque gratuit ici :
  `feuVert()` est une pure fonction de l'heure, et la nuit vide maintenant la ville. À partir
  d'une heure, plus de cycle — l'artère clignote orange, la rue secondaire clignote rouge (un
  STOP), et le trafic de nuit, qui n'a plus personne à croiser, cesse d'attendre devant un
  feu rouge pour rien. Ça se voit de loin sur une ville déserte, et c'est exactement le
  genre de détail qui dit « c'est la nuit » mieux qu'un voile bleu.
- **Les heures de pointe ont une direction.** Le rythme (nuit, matin, soir) règle _combien_
  de chars roulent ; il ne dit pas _où ils vont_. Le matin, le trafic devrait **converger**
  vers le Faubourg et les Quais, et le soir se **disperser** vers les Érables. ⚠️ Pas en
  touchant au champ de direction, qui est fixe et jugé : en **pondérant le choix de sortie**
  aux croisements selon l'heure. C'est trois lignes dans `prochaineCible`, et le matin a
  soudain un sens.
- **La ville est coupable d'elle-même.** GTA 2 le faisait déjà : des pickpockets qui
  travaillent la foule, un vol de char sous tes yeux, deux gangs qui se battent à leur
  frontière — **sans toi**. Le jeu a tout ce qu'il faut : le pickpocket, le carjacking, les
  témoins, les gangs et leurs territoires. Il manque que ça arrive à d'autres qu'au joueur.
  - ⚠️ Et ça change la police : un crime qu'on n'a pas commis peut te tomber dessus si tu es
    au mauvais endroit — un témoin qui te confond, un agent qui arrive sur une bagarre où tu
    passais. C'est risqué, donc c'est **rare** et **lisible** (on voit le vrai coupable), et
    un juge vérifie qu'aucune étoile ne tombe sur un joueur immobile à plus de N tuiles.
- **On attend l'autobus.** GTA 2 avait des piétons à l'arrêt ; ici il y a un autobus (M9) et
  bientôt un tramway. Des gens qui attendent à l'arrêt, montent quand il s'arrête, et
  descendent trois arrêts plus loin : c'est de la vie qui a un **but**, et c'est aussi la
  façon la moins chère de faire entrer et sortir des piétons sans qu'ils naissent hors écran.
- **Les éboueurs.** Un camion à bras mécanique — Québec ramasse les bacs comme ça — qui
  s'arrête tous les vingt mètres, lève un bac, repart. Un obstacle qui **bouge** dans la
  rue, une raison de le dépasser, et le camion de M9 qui sert à autre chose qu'à défoncer.
- **Les goélands et les chats.** La vie qui n'est pas humaine : un goéland qui s'envole quand
  tu passes aux Quais, un chat qui file dans une ruelle du Faubourg. Ils ne comptent pour
  rien — ni témoins, ni victimes — et c'est précisément ce qui les rend vivants : ils ne sont
  là que pour être là.
- **Juges** : toute entrave du jour vient de la liste calculée par Python, jamais d'un
  tirage libre ; la ville reste fortement connexe **avec** les entraves du jour posées (sur
  cinq graines) ; un détour affiché mène bien de l'autre côté ; la nuit de déneigement
  s'annonce la **veille** ou n'arrive pas ; un feu au
  clignotant ne fait plus attendre personne pour rien ; le trafic de pointe converge et se
  disperse (on compte les sorties choisies à un croisement, matin contre soir) ; aucun crime
  d'autrui ne vaut une étoile à un joueur qui n'y est pour rien ; et un autobus qui s'arrête
  fait vraiment monter quelqu'un.

## Notes

tramway, traversier à l'heure, tempête de neige et charrue, **une famille d'entraves**
(réparations, fermetures avec DÉTOUR, bris d'aqueduc, pannes) tirées d'une liste que Python
valide, nids-de-poule, nuit de déneigement qui envoie les chars au lot, feux au clignotant
la nuit, heures de pointe qui ont une direction, la ville coupable d'elle-même, l'arrêt
d'autobus, les éboueurs, goélands et chats

✅ **1re vague livrée** (15 sept. 2026) — *le rythme de la ville*, trois choses qui la font
changer d'une heure à l'autre **sans regénérer une seule tuile**.

- ⚠️ **Les feux passent au clignotant la nuit** : de 20 h 40 à 6 h, l'**artère** (la rue la
  plus large du croisement) clignote jaune et la rue secondaire clignote rouge.
  `feuDeCirculation` reste **la seule source** — le dessin de la lanterne en découle,
  `feuVert` en découle, et le trafic obéit à `feuVert` : un clignotant ne peut donc pas
  montrer une couleur que le char ne respecte pas.
- ⚠️ Le rouge qui bat est un **STOP**, pas un mur : on s'immobilise puis on passe — sans
  cette ligne, le trafic de nuit attendait la fin des temps. Le bonhomme s'éteint avec le
  cycle (on traverse à vue). La lentille pulse : la douille reste, la lumière part.
- ⚠️ **Les heures de pointe ont une direction** : le matin (6 h 30 → 10 h) le trafic
  converge vers le Faubourg, le soir (16 h 20 → 20 h) il s'en disperse — en **pondérant le
  choix de sortie** aux croisements, jamais en touchant au champ de direction, qui est fixe
  et jugé. `penchant` est la **part** des chars qui suivent le mouvement (0,45) : le reste
  tire au sort comme toujours, sinon la ville entière roule dans le même sens et ce n'est
  plus une heure de pointe, c'est une évacuation.
- ⚠️ **Les nids-de-poule** : 30 à 90 tuiles de chaussée qui secouent la caméra et coûtent
  deux points de carrosserie — **jamais dans un croisement** (on y freine déjà, et une
  secousse au milieu d'un virage se lit comme un bogue de collision), jamais sur une ligne
  d'arrêt, jamais deux collés, et un **répit** de 30 images pour qu'un char lent ne le paie
  pas à chaque image. Un char à l'arrêt n'y tombe pas. Son bruit est synthétisé (le
  talonnage, le gravier, la tôle qui résonne).
- ⚠️ **Un vrai trou dans les barrières, trouvé au passage** : une barrière fermée n'était
  consultée que sur les **voies** — un char qui abordait le pont *depuis la boîte* d'un
  croisement en sortait dessus sans que rien ne le lui demande, et une fois sur le tablier
  il était **dedans**, donc exempté, et il traversait tout du long. Une sortie barrée n'est
  plus une sortie (`peutSortir`). Le juge du demi-tour l'a attrapé le jour où les dés ont
  changé la route d'un char ; le trou, lui, était là depuis le premier jour des barrières.
- ⚠️ Et deux juges des lanternes testaient « la nuit » **à minuit** — heure où les feux
  clignotent désormais : ils visent l'heure qui est sombre sans être clignotante. 7 juges
  neufs (`test_ville_vit.py`), rouge-avant prouvé sur les trois règles ; 1611 tests.

✅ **2e vague livrée** (15 sept. 2026) — *les entraves du jour*. Python calcule **une fois**
la liste des voies qu'on peut fermer, le paquet la transporte, et la **graine du jour** en
tire une : la ville change d'un jour à l'autre sans qu'on regénère une seule tuile.

- ⚠️ `hash2(jour, …)`, jamais `B.rng()` — un décor qui change la ville ne consomme pas un dé
  du jeu.
- ⚠️ **Une entrave ne coupe jamais la ville en deux, et elle ne le peut pas PAR
  CONSTRUCTION** : elle ferme **une voie** d'une rue qui en a deux dans le même sens, donc
  le champ de direction ne bouge pas d'une flèche et `voies_bloquees` rend exactement ce
  qu'il rendait. C'est ce qui permet de se passer du juge de connexité à la construction —
  il coûte 14 ms, et en valider cent doublerait le temps de bâtir la ville ; la rue
  **entière** barrée, elle, l'exigera, et viendra avec son panneau DÉTOUR. Hors croisement,
  hors ligne d'arrêt, espacées de 20 tuiles.
- ⚠️ Le chantier est une **barrière comme les autres** — rien de neuf dans le mécanisme,
  seulement dans le choix : il arrête les chars et pas les jambes, il se force en poussant
  les cônes (8 points), il se voit, et le carnet le liste.
- ⚠️ **Et le trafic se DÉPORTE avant de faire demi-tour** : une voie fermée laisse sa
  voisine ouverte, y rebrousser chemin pour trois cônes serait absurde — c'est la voie d'à
  côté qui tranche, pas le genre de la barrière. Une voie barrée n'est pas non plus une voie
  où se déporter. 3 juges de plus, rouge-avant prouvé ; 1614 tests.

✅ **3e vague livrée** (15 sept. 2026) — *la rue barrée*.

- ⚠️ **Mesuré, et c'est ce qui a tout décidé** : barrer la MOITIÉ d'un tronçon laisse
  l'autre moitié en **cul-de-sac dans les deux sens** — la voie qui monte n'a plus d'entrée,
  celle qui descend n'a plus de sortie. Le juge de connexité de M1 a refusé les **vingt-six
  premières candidates**, toutes pour cette raison. Une rue barrée couvre donc **tout son
  tronçon, d'un croisement à l'autre** : fermée en entier, elle disparaît du graphe et la
  grille route autour — c'est d'ailleurs ce que « rue barrée » veut dire. `voies_bloquees`
  tranche à la construction, une fois, sur 20 candidates au plus (il coûte 14 ms pièce).
  Jamais sur le pont.
- ⚠️ Elle bloque **tout son rectangle** et pas sa seule couronne : une chaussée de quatre
  tuiles de large aurait laissé passer le monde par le milieu — les cours, elles, gardent
  leur couronne. Sa **barricade** se peint aux deux bouts seulement : on ferme une rue par
  ses extrémités, on ne la clôture pas. Elle coûte 14 points à forcer contre 8 pour des
  cônes.
- ⚠️ **Une seule entrave par jour**, tirée dans les deux listes réunies : c'est ce qui évite
  d'avoir à juger les **combinaisons** — deux fermetures valides séparément peuvent,
  ensemble, isoler un bloc. Et le trafic n'y entre jamais : une sortie barrée n'est pas une
  sortie, donc les chars tournent **avant**, au croisement, comme devant un vrai détour. 1
  juge de plus et deux rouverts aux deux genres ; 1615 tests.

✅ **4e vague livrée** (15 sept. 2026) — *l'entrave se lit*.

- ⚠️ **Une fermeture sans détour affiché n'est pas une entrave, c'est un piège** : on
  arrive, on ne passe pas, et rien ne dit par où aller. Le **panneau DÉTOUR** se pose
  au-dessus de la barricade, aux deux bouts, et sa flèche montre le côté où la rue continue.
  Il a coûté deux défauts avant de dire vrai : il cherchait la rue de rechange **dans l'axe
  de la rue barrée** (elle n'y est pas — le détour croise la rue barrée à son bout, pas à
  son milieu), puis, une fois qu'il regardait au bon endroit, il **se taisait aux
  carrefours** parce que les deux côtés se valent. Il sort donc du rectangle par le bon
  bout, et quand les deux mènent quelque part il montre la **droite** : une flèche qui
  hésite est un panneau pour rien.
- ⚠️ **Les ouvriers au chantier** : un ou deux, plantés sur la voie fermée, et
  **intouchables comme les enfants** — un chantier où l'on fauche l'équipe au premier
  passage n'est pas un chantier, c'est une cible. C'est une propriété de l'**entité**, pas
  de l'archétype : un ouvrier qui rentre chez lui reste un passant comme un autre, et un
  juge le vérifie. Ils ne comptent pas dans la foule : ils ont un poste, comme
  l'homme-sandwich. 2 juges de plus ; 1617 tests.
- ⚠️ Rouge-avant prouvé pour les ouvriers ; celui du panneau ne l'est pas — il affirme une
  vérité utile (chaque bout parle, et montre une chaussée qui n'est pas la voie barrée
  elle-même) et il a attrapé les deux défauts ci-dessus en cours de route, mais la
  neutralisation évidente lui échappe.

✅ **5e vague livrée** (15 sept. 2026) — *le char en panne*, une entrave qu'on n'a **pas**
vue venir : ni cônes, ni panneau, ni liste validée par Python. Un camion s'arrête en travers
d'une voie, ses **feux de détresse** battent aux quatre coins de sa caisse, et il repart au
bout de quarante minutes de jeu — une entrave du jour change la ville, une panne ne fait que
la contrarier. Le trafic sait déjà quoi en faire : il se déporte (`obstacleDevant` voit les
chars à l'arrêt), exactement comme devant un piéton planté sur la chaussée.

- ⚠️ Elle a coûté **deux leçons, et les deux étaient déjà écrites dans le dépôt**. (1) **Un
  décor ne tire pas dans le dé du jeu** : la panne prenait sa couleur et sa place au hasard
  commun, et **quatre juges sont tombés d'un coup** — aucun ne parlait de pannes. Sa couleur
  et sa place se tirent maintenant par `hash2` du jour et de l'heure, `creer` n'appelle plus
  le dé quand on lui donne une couleur, et un juge compte les dés sur six cents images pour
  le tenir. (2) **`laisse` veut dire « le JOUEUR l'a abandonné ici »** — marquer la panne
  ainsi la faisait suivre par la fourrière, et le HUD nageait dans « la fourrière va
  passer » pendant qu'un camion battait ses feux. Elle ne compte pas non plus dans les
  places de stationnement de la ville.
- ⚠️ Et un juge d'amuseurs a été **resserré sur ce qu'il dit mesurer** : il annonçait
  mesurer le GESTE, mais il le mesurait dans une ville vivante — il a suffi qu'un camion
  tombe en panne au bout de la rue pour que le jongleur devienne témoin, s'en aille, et ne
  montre plus que deux dessins. Il tient maintenant l'amuseur sur sa scène. 3 juges neufs ;
  1620 tests.
- ⚠️ Jugé dans un **worktree isolé** : deux autres sessions écrivaient dans l'arbre. 🔧
  **Réparé après coup** (15 sept. 2026) — *une panne ne s'efface pas sous celui qui la
  tient*. Monter dans la remorqueuse en panne et la voir disparaître : l'heure finie, le
  compte à rebours retirait le char de la ville **sans regarder qui était dedans**, et le
  joueur restait accroché (`dansVehicule`) à une entité absente de `B.entites` — plus mise à
  jour ni dessinée, donc invisible et immobile, et rien ne le lui disait. La charge sur la
  fourche et un char de mission partaient pareil. Tenu, le char cesse simplement d'**être en
  panne** (ses feux s'éteignent) et redevient un char ordinaire : c'est `peupler` qui
  l'oubliera, loin et hors champ. La liste est **exactement la sienne**, et ce n'est pas un
  hasard — « qui tient ce char ? » n'a pas deux réponses selon qui pose la question. 1 juge
  neuf, rouge-avant prouvé ; 1645 tests.

✅ **6e vague livrée** (15 sept. 2026) — *la ville est coupable d'elle-même*, première
moitié : **un vol de char sous tes yeux**.

- ⚠️ Le **vol à la tire entre passants existait déjà** (`majPickpocket`, livré avec les
  sortes de gens) — vérifié avant de risquer de le réécrire. Voici l'autre : un passant
  ordinaire repère un char garé, marche dessus d'un pas pressé, ouvre la portière et s'en va
  avec ; la rue crie **AU VOLEUR** et s'écarte.
- ⚠️ **Il se voit, ou il n'a pas lieu** : on ne déclenche un vol que sur un char **à
  l'écran** — un vol hors champ est du travail qu'on fait pour personne.
- ⚠️ **Et ce n'est PAS le joueur qui le paie** : la police du jeu est centrée sur lui, et
  signaler le geste d'un autre lui mettrait une étoile — un juge vérifie qu'il n'en écope
  aucune. (« Ça peut te tomber dessus » reste à faire, avec son propre juge.)
- ⚠️ Le voleur ne touche **ni au char du joueur, ni à celui qu'il a laissé** : un char
  abandonné appartient à la fourrière, pas aux voleurs — deux systèmes qui se disputent le
  même char, c'est l'un des deux qui ment, et le juge de la fourrière est justement tombé le
  jour où un voleur lui a pris le sien.
- ⚠️ Et **pas de réplique neuve** : un juge exige que chaque parole soit le métier de
  quelqu'un, et « AU VOLEUR » existait déjà chez le pickpocket — c'est la rue qui parle, pas
  le voleur. Le tirage se fait à l'empreinte de la minute, jamais au dé du jeu. 3 juges
  neufs, rouge-avant prouvé deux fois ; 1625 tests.
- ⚠️ Jugé dans un **worktree isolé** : une autre session écrivait dans l'arbre. Restent,
  pour les vagues suivantes : la **bagarre de gangs à leur frontière** (elle demande un état
  d'attaque qui vise quelqu'un d'autre que le joueur — aujourd'hui `attaque_joueur` ne sait
  viser que lui), le bris d'aqueduc (il demande `carte.py`, occupé), le tramway, le
  traversier, la neige et la charrue, la nuit de déneigement, la ville coupable d'elle-même,
  l'arrêt d'autobus, les éboueurs, les goélands et les chats

✅ **7e vague livrée** (15 sept. 2026) — *la bagarre de gangs à leur frontière*, deuxième
moitié de « la ville est coupable d'elle-même ». Le vol de char se passait **de travers** du
joueur ; celle-ci se passe **sans lui**. Deux gangs se tombent dessus là où leurs districts
se touchent — cinq frontières sur toute la carte, que `pietons.frontieres()` calcule des
**deux** fiches : les rectangles viennent de `carte`, qui ne sait pas qui tient quoi ; les
gangs viennent de `pietons`, qui ne sait pas où sont les rectangles. C'est
`definitions.assembler` qui les marie, une fois, au démarrage — « une fiche que le
navigateur ne lisait pas » a son symétrique, **« un calcul que Python ne pouvait pas
juger »**.

- ⚠️ **Ce qui a coûté cher n'est pas la rixe : c'est que `attaque_joueur` est le SEUL état
  d'attaque du jeu, et que TROIS mécanismes y ramenaient tout le monde.** `alerter`
  retournait contre le joueur toute gang à portée d'un coup, `blesser` faisait de même du
  blessé, et `majAttaque` y ramenait tout piéton qui finissait son geste : six hommes qui se
  tapaient dessus se retournaient contre lui au premier poing — et il n'avait rien fait, il
  passait par là. Les trois sont corrigés, **chacun sous son rouge-avant** (115, 30 et 184
  images de rixe retournée contre lui).
- ⚠️ **Et un quatrième, trouvé au passage et plus vieux que la vague** : un piéton en plein
  coup n'avait pas de branche à lui dans la machine à états et tombait dans le DERNIER
  `else`, celui qui flâne — il pouvait donc décider de s'arrêter au milieu de son geste.
  `majAttaque` refuse alors de continuer (l'état n'est plus `attaque`), le coup reste **en
  suspens pour toujours**, et l'homme repart faire autre chose. Une gang qui attaquait le
  joueur le faisait déjà ; ça ne se voyait pas, parce qu'elle y revenait toute seule.
- ⚠️ **`stats.tues` était le compteur de la VILLE, pas celui du joueur** : toute mort de
  piéton y entrait, y compris les passants fauchés par un char du trafic. Il tire la
  manchette du Clairon (« UN MORT DANS LA RUE », « NUIT ROUGE AU FAUBOURG ») et le bilan de
  fin de mission — créditer le joueur d'une rixe qu'il a regardée de loin est un **mensonge
  imprimé**.
- ⚠️ **La seule inimitié que la ville connaisse** s'écrit dans `arcDeMelee` et pas dans
  l'état `bagarre` : c'est le même test qui empêche un coup perdu de faucher le badaud venu
  regarder.
- ⚠️ **La fenêtre est mesurée, pas choisie** : sous 300 px on serait à l'ÉCRAN (la vue fait
  480 × 270, donc tout ce qui est à plus de 276 px du joueur est forcément dehors) et on
  verrait six hommes se matérialiser ; au-delà de 500 px on serait hors de la BULLE D'OUBLI
  (520) et ils naîtraient pour être effacés à l'image suivante.
- ⚠️ Le tirage se fait à l'**empreinte de la minute**, jamais au dé du jeu (la leçon du char
  en panne, qui avait fait tomber quatre juges sans rapport), et un juge le tient en
  comptant les dés sur six cents images.
- ⚠️ Ils **ne sont pas la foule** : ils sont venus pour ça, comme l'ouvrier à son chantier —
  sans cette marque, six hommes de plus passent par-dessus le plafond de passants, faute que
  le juge de la foule a déjà attrapée une fois.
- ⚠️ Et **l'autre moitié de la règle compte autant** : on a appris à la rixe à ignorer le
  joueur, il ne faut pas qu'elle l'ignore quand il ENTRE dedans — un coup de sa part, et la
  gang lui tombe dessus comme chez elle. **Pas de réplique neuve** (le `cri` et les coups
  suffisent) : un juge exige que chaque parole soit le métier de quelqu'un. 14 juges neufs
  (`test_bagarre.py`, `test_bagarre_js.py`), rouge-avant prouvé **six fois** ; 1644 tests.

✅ **8e vague livrée** (16 sept. 2026) — *le bris d'aqueduc*, troisième visage de l'entrave
et le seul que personne n'a posé : une conduite lâche sous la chaussée, la rue gicle, et la
ville met presque une heure à trouver la vanne.

- ⚠️ **Il arrive à une HEURE, pas à l'aube** : l'entrave du jour et la rue barrée se tirent
  au lever du jour et tiennent la journée ; celui-ci est de la famille du char en panne — on
  roulait, la rue était libre, elle ne l'est plus. Ni cônes, ni panneau DÉTOUR.
- ⚠️ **Rien n'a été écrit pour l'eau** : la gerbe est le `jet_eau` de la borne-fontaine
  défoncée, tel quel — il crache ses gouttes et **tient** son souffle (`Son.SFX.borne_jet`,
  une fois par image, à distance). Un bris d'aqueduc est cette gerbe-là, en pleine rue et
  pour une heure de jeu.
- ⚠️ **Et le trafic n'a rien demandé non plus** : un bris est une barrière comme les autres,
  et `peutSortir` les consulte déjà depuis la 1re vague. Sans elle, mesuré, le char roule
  sept images **dans le trou**.
- ⚠️ **Le juge qu'il a fallu jeter, et ce qu'il a appris.** La tentation était d'appliquer
  le standard de la **rue barrée** : effacer la flèche et redemander à `voies_bloquees` si
  les rues sont encore fortement connexes. Mesuré : les **trente** candidates échouent — et
  ce n'est pas un défaut, c'est la leçon de la 3e vague relue à l'envers. Une voie est un
  couloir dirigé d'une tuile de large : boucher une tuile laisse toujours le reste du
  tronçon en cul-de-sac dans les deux sens, jusqu'au croisement suivant. C'est exactement
  **pourquoi** une rue barrée doit couvrir tout son tronçon. Un bris, lui, ne touche pas au
  champ de direction : ce qui le rend franchissable n'est pas le graphe des flèches, c'est
  **le changement de voie**. Le juge mesure donc la manœuvre — se déporter une tuile avant,
  passer, continuer — sur les trois tuiles qu'elle emprunte, et il exige que la voie d'à
  côté mène quelque part **des deux bouts** : une voisine qui commence ou finit pile au trou
  n'est pas un détour, c'est une impasse d'une tuile.
- ⚠️ **Et la première version de ce juge-là ne mesurait rien du tout** : elle lisait un
  `_Chantier` neuf, qui est une toile **vide** — `voies_bloquees` y rend deux ensembles
  vides quoi qu'on fasse. Les juges lisent maintenant la ville **bâtie**, celle du paquet,
  c'est-à-dire exactement ce que le navigateur reçoit.
- ⚠️ Il arrête les **chars** et pas les **jambes** — la règle du pont de La Pointe : on
  traverse la gerbe à pied, on se mouille, on passe ; un trou d'eau qui arrêterait tout le
  monde serait un mur, et la ville n'en a pas.
- ⚠️ **Un bris ne déborde jamais sur l'heure suivante**, et c'est la fiche qui le garantit
  (`minutes` < 60, sous son juge) : cette borne a permis de **supprimer** une branche du
  navigateur qui, écrite pour ce cas, ne pouvait jamais s'exécuter.
- ⚠️ Le tirage se fait à l'**empreinte de l'heure**, jamais au dé du jeu — rouge-avant
  prouvé en faisant tirer la tuile au dé (715 dés d'écart sur six cents images).
- ⚠️ Et un juge qui plantait le joueur au **milieu de la chaussée** à côté du bris le
  faisait faucher par le trafic : l'hôpital le renvoyait à deux mille pixels de là, la gerbe
  sortait de la bulle, et le juge mesurait un oubli par distance en croyant mesurer une
  minuterie. Il se tient sur le trottoir.
- ⚠️ Note honnête : le **renouvellement** de la gerbe n'a pas de rouge-avant — la branche
  d'à côté en refait une à l'image même où l'autre meurt, et un juge qui regarde chaque
  image ne voit aucun creux sans elle ; elle évite de jeter et refaire une entité toutes les
  dix secondes, rien de plus. 10 juges neufs (`test_aqueduc.py`, `test_aqueduc_js.py`),
  rouge-avant prouvé **cinq fois** ; 1652 tests.
- ⚠️ Jugé dans un **worktree isolé** : une autre session écrivait dans l'arbre.

✅ **9e vague livrée** (16 sept. 2026) — *les goélands et les chats*. « La vie qui n'est pas
humaine : un goéland qui s'envole quand tu passes aux Quais, un chat qui file dans une
ruelle du Faubourg. Ils ne comptent pour rien — ni témoins, ni victimes — et c'est
précisément ce qui les rend vivants : ils ne sont là que pour être là. »

- ⚠️ **Et « ne compter pour rien » a fini par vouloir dire quelque chose de très précis : ne
  pas être dans `B.entites`.** Les sortir de l'index des gens ne suffisait pas — mesure, un
  juge du trottoir qui compte un TAUX sur cent essais tombait de 75 % à 2 % rien qu'en les
  laissant vivre dans la liste du monde, **sans qu'aucune ne tire un seul dé** (vérifié par
  attribution de pile d'appel, puis en neutralisant l'oubli, puis le semis). Elles ont leur
  liste : ni parcourues, ni démêlées, ni oubliées, ni indexées avec le reste.
- ⚠️ **`blesser` acceptait n'importe quoi de vivant** : `creer` donne `vivant: true` à TOUT
  ce qu'il fabrique, si bien qu'un goéland — ou un ballon, ou une gerbe d'eau — se laissait
  « blesser » de 99 points. Un goéland qu'on peut tuer est une **cible**, et une cible
  demande un score, un crime, un juge.
- ⚠️ Elles partent **avant** qu'on les touche : leur distance de fuite est plus grande que
  la portée de tout ce qui pourrait les atteindre, et c'est ce qui évite d'avoir à répondre
  à « que se passe-t-il si je lui roule dessus » — on n'y arrive pas. Un char qui fonce
  compte double.
- ⚠️ Chacune chez soi (le goéland au bord de l'eau, le chat dans les ruelles), et rien ne se
  tire au dé : le semis balaie la bulle en anneaux, l'humeur se tire à l'empreinte.
- ⚠️ **Et une heure perdue avant de comprendre** : trois des juges qui tombaient
  appartenaient à une autre session en vol (`carte.py`, `test_trottoir.py`). La leçon du
  dossier partagé, apprise deux fois en deux vagues : **avant d'accuser son propre code,
  vérifier à qui appartient le diff**. 4 juges neufs, rouge-avant prouvé trois fois ; 1716
  tests. Restent ensuite : le tramway, le traversier, la neige et la charrue, la nuit de
  déneigement, l'arrêt d'autobus, les éboueurs.

✅ **10e vague livrée** (17 sept. 2026) — *on attend l'autobus*. Des passants attendent à
l'abribus, montent quand l'autobus s'arrête et descendent deux à quatre arrêts plus loin :
de la vie qui a un **but**, et la façon la moins chère de faire entrer et sortir du monde
sans qu'il naisse sous les yeux. Python règle (`autobus.ATTENTE`), `autobus.js` joue.

- ⚠️ **Qui attend se tire à l'empreinte de l'arrêt et du quart d'heure, jamais au dé du
  jeu** — et `creerPieton`, qui en tire deux, joue avec un **dé prêté** (`sansLeDe`) : la
  file du jeu ne bouge pas d'un tirage, et le juge des autobus, qui compte les dés par pile
  d'appel, compte aussi ceux-là.
- ⚠️ **Personne ne naît sous les yeux** : entre 300 et 480 px du joueur (la vue fait 480 ×
  270, donc au-delà de 276 px on est dehors ; la bulle d'oubli est à 520) — **et pas à
  l'écran quand la caméra a pris de l'avance** au volant, cas qu'un juge force en posant la
  caméra sur l'abribus. Ils ne sont pas la foule (`metier: 'autobus'`), et un abribus que
  l'autobus vient de servir ne se remplit pas derrière lui dans le même quart d'heure.
- ⚠️ **L'autobus s'arrête pour qui attend, vu ou pas** ; avec le joueur à bord, seulement
  pour qui descend (une demande d'arrêt comme la sienne) — qui attend prendra le suivant.
  Ceux qui descendent redeviennent des passants, là où ils voulaient aller.
- ⚠️ **Un défaut trouvé par un juge d'une autre vague** : un voyageur qui s'avançait à 4 px
  de la caisse la chevauchait, et la résolution des collisions **poussait l'autobus hors de
  sa voie** — 29 relevés sur 1 175 hors du tracé. Le pas de la porte est à 9 px (plus qu'un
  rayon de passant), et c'est ce juge-là qui le garde.
- ⚠️ **Et un défaut vu par le juge de la foule** : un voyageur **naissait dans le passant**
  qui longeait le trottoir à ce moment-là (7,4 px d'enfoncement, l'image d'après sa
  naissance). On ne naît plus dans quelqu'un, et on ne descend pas dans quelqu'un : un pas
  de porte occupé fait descendre à l'arrêt suivant.
- ⚠️ **Deux gardes qu'aucun juge n'exerçait** : la place d'attente sur un mur (les 106
  places des 53 abribus sont bonnes sur cette ville — un juge pose un mur exprès) et
  l'abribus qui se remplit derrière l'autobus (le premier juge passait **par chance** : le
  quart d'heure avait changé pendant l'attente, et le nouveau ne voulait personne). 9 juges
  neufs (`test_on_attend_l_autobus.py`, `test_on_attend_l_autobus_js.py`), **13 mutations
  toutes rouges**.

✅ **11e vague livrée** (17 sept. 2026) — *les éboueurs*. Un camion-benne fait sa tournée du
matin dans Les Érables : il s'arrête à chaque bac vert sorti au bord du trottoir, le lève,
le vide au-dessus de la benne, le repose **exactement** où il était et repart — un obstacle
qui bouge dans la rue, et une raison de le dépasser.

- ⚠️ **Python trace, le navigateur roule — avec la machinerie des autobus** (`eboueurs.py`
  appelle `autobus._Reseau` et `autobus._boucle`) : la tournée passe par les quatre coins
  des maisons du quartier, obéit aux flèches, ne tourne qu'une fois par boîte et ne passe
  jamais où la ville peut fermer. Sur la graine livrée : **576 tuiles et 71 bacs**, un tous
  les cinq pas au plus, jamais à moins de trois tuiles d'une boîte, ni sur un meuble, un
  abribus ou le pas d'une porte.
- ⚠️ **Rien ne se pose dans la ville** : la tournée se calcule en tout dernier sur la ville
  finie, ne tire aucun dé et ne touche pas à ce qu'elle lit — un juge compare la ville avec
  et sans. Les bacs naissent dans le navigateur : sortis de 5 h à 15 h, **hors de l'écran**
  (même quand la caméra a pris de l'avance), jamais sur un passant, et rentrés hors de vue
  l'après-midi.
- ⚠️ **Le camion roule comme un autobus de ligne** (`conducteur: 'ligne'`, marqué
  `collecte`) : il hérite des feux, des boîtes, du déport du trafic et de tout ce que le jeu
  fait déjà pour un autobus, et seuls les gestes de l'autobus l'excluent (on n'y monte pas).
  Sa place est une fonction de l'heure ; il naît de 6 h à midi, hors de l'écran, avec sa
  silhouette et sa couleur **données** — `creer` ne tire alors aucun dé. ⚠️ Il s'appelait
  d'abord `tournee`, **comme le champ du facteur** (la liste de ses portes) : le juge de
  l'après-midi a pris un facteur pour un camion.
- ⚠️ **Un bac ne barre rien.** Solide, il faisait du trottoir d'une tuile de la banlieue une
  suite de cages : deux juges des passants sans rapport sont tombés (le musicien seul devant
  personne, le passant témoin de l'ivrogne qui ne marchait plus). On le traverse à pied
  comme un buisson ; un char le défonce, et le camion ne s'arrête pas devant un bac défoncé.
  Et son pied est à **quatorze pixels** au moins du centre de la voie : posé au bas de la
  tuile, un bac de trottoir nord était à onze, et le camion (rayon 8) touche un bac (rayon
  4) à douze.
- Le son du bras est ElevenLabs (`benne`), avec son repli synthétisé. **11 juges neufs**
  (`test_eboueurs.py`, `test_eboueurs_js.py`), **19 mutations toutes rouges** — deux d'entre
  elles restaient vertes avant qu'on ajoute la caméra en avance et le camion de l'après-midi
  là où l'horaire le mettrait.

✅ **12e vague livrée** (17 sept. 2026) — *le traversier*. Les Quais ↔ La Pointe, à l'heure :
départ des Quais aux heures paires, de La Pointe aux impaires, douze secondes de traversée
au nord de l'île et sept à quai. On y monte **en roulant** — en char ou à pied, par le bout
de rue qui touche le pont — et à l'heure dite, tout ce qui est sur le pont part avec lui. Ce
qui n'y est pas reste à quai : il part sans toi.

- ⚠️ **Python trouve les quais, le navigateur traverse** (`traversier.py`, `traversier.js`)
  : sur la ville finie, une coque de 8 × 3 tuiles (deux voies de pont, la cabine au sud)
  cherche où accoster — de l'eau profonde dessous, au moins deux tuiles de rive carrossables
  qui touchent le PONT (jamais la cabine), une rue à côté, le quartier à trois tuiles — puis
  la traversée la plus courte dont le couloir est de l'eau libre, hors de la ceinture de
  l'île et à plus d'une tuile d'un amarrage. Sur la graine livrée : **(154, 117) → (278,
  121)**, 124 tuiles, et une chaloupe amarrée à La Pointe a repoussé le quai de trois
  rangées. Aucun dé ; la ville est la même avec ou sans (un juge compare).
- ⚠️ **À quai, le pont est une vraie tuile.** `poser` marque la coque dans la carte (le pont
  sol carrossable ET chaussée — un flâneur de la rive n'y descend pas se promener —, la
  cabine un mur), `lever` rend chaque octet noté : un juge compare `solide`, `route` et
  `passage` avant et après deux allers-retours. Au départ, les chars et le joueur sur le
  pont passent **à bord** (`aBord`) : `Vehicules.maj` et `Entites.majJoueur` les sautent, la
  coque les porte au pixel — le char ne coule pas, le joueur ne nage pas. Un passant égaré
  sur le pont est remis sur le quai. Une pièce où l'on entre pendant le départ ne laisse pas
  de pont fantôme sur l'eau.
- À bord, **Radio-Traversier** joue enfin — la station qui attendait le traversier depuis
  M9, « sa musique de pont » ; descendu à pied, elle se tait, au volant, la radio du char
  reprend. La corne (ElevenLabs, `corne`, avec son repli synthétisé) sonne au départ et à
  l'arrivée, de loin sur l'eau. Au bout du quai, un panneau bleu et la ligne du bas : «
  TRAVERSIER POUR LA POINTE · DÉPART 14:00 », « DÉPART DANS 5 S » à quai, « LA POINTE DANS
  12 S » à bord ; la grande carte trace la traversée en pointillé.
- ⚠️ **Il ne double pas les chars** : la vitesse de pointe (un trapèze — il prend de l'élan
  et freine en arrivant) est jugée sous celle d'une berline. ⚠️ Et le banc avance à **pas
  fixe** : une image du banc peut n'en faire aucun, et le juge lisait la carte d'avant le
  départ — deux images après chaque réglage d'heure. ⚠️ Le filtre « la coque dans l'eau »
  est redondant avec le couloir mais c'est celui de la vitesse (20 ms au lieu de 3 min 30) :
  un juge de durée le tient.
- **Ce qu'il ne fait pas encore** : il ne s'arrête pas à L'Île-aux-Corneilles (c'est la 2e
  vague de l'île), pas de billet, et le pont ne porte que ce qu'on y amène — aucun char du
  trafic ne prend le traversier. **15 juges neufs** (`test_traversier.py`,
  `test_traversier_js.py`), **22 mutations toutes rouges** — celle de la coque posée sur la
  terre ne l'est que par le juge de durée.

✅ **13e vague livrée** (17 sept. 2026) — *le tramway*. La ligne **T**, du Casse-croûte du
Faubourg au Quai du traversier : trois rames crème à bande rouge sur une voie double, douze
arrêts marqués d'un poteau rouge. Elles n'attendent personne, ne s'arrêtent pas pour toi —
elles sonnent —, et le trafic leur cède.

- ⚠️ **Double voie, jamais à contresens** (`tramway.py`) : une recherche sur les voies, qui
  ne tourne que dans les boîtes (de n'importe quelle voie : c'est ce qu'elle ignore du champ
  de direction) et n'avance que si la voie d'EN FACE existe aussi ; le retour est l'aller
  décalé d'une tuile à gauche (un coin se décale de ses deux gauches — intérieur à gauche,
  extérieur à droite). Aux deux terminus, la rame passe d'une voie à l'autre là où elle est
  : c'est une rame à deux cabines. Sur la graine livrée : **516 tuiles, 8 coins**,
  contournement de la baie par l'ouest. Rien de fermable, aucun dé, la ville identique avec
  ou sans (un juge compare).
- ⚠️ **Le tramway est une LIGNE** (`autobus.js`) : ses rames sont des autobus marqués
  `rails` sur la ligne `T`, avec l'horaire, l'invite, le passager, la ligne du HUD et le
  tracé de la grande carte des autobus. Ce qui change : sa place vient de SON horaire (1,4
  px/image) ; il s'arrête à chaque arrêt le temps des portes, ni plus ni moins
  (`dureeDArret`) ; `obstacleDevant` ne voit ni le joueur ni son char — il sonne
  (`cloche_tram`, ElevenLabs) ; un char ne s'engage pas dans une boîte vers laquelle roule
  une rame à quatre tuiles (`croisementLibre`), mais deux rames qui s'y croisent ne se
  cèdent pas le passage. On ne vole pas une rame ; on y monte à l'arrêt, 3 $.
- ⚠️ **Une silhouette donnée se déclare** : `Vehicules.creer` refusait tout ce qui n'était
  pas une variante tirée au sort, et la rame naissait… autobus scolaire. `SPRITES.tramway.de
  = 'autobus'` : une silhouette de la fiche qui ne se tire jamais. La machine est celle de
  l'autobus sans roues visibles, un pare-brise à chaque bout, deux portes, la livrée et le
  pantographe ; les rails sont peints sous la ville (`dessinerRails`), deux filets d'acier
  dans le sens de la voie.
- ⚠️ **Le banc compte les jours** : `tempsDeLaPartie` ajoute les jours d'avant, et le juge
  qui posait une rame « au deuxième jour » la faisait naître à 949 px de sa place — un tour
  et demi de boucle. **15 juges neufs** (`test_tramway.py`, `test_tramway_js.py`), **19
  mutations toutes rouges** — cinq restaient vertes avant qu'on croise deux rames, qu'on
  regarde le sens des rails, qu'on mesure la place à l'heure, et qu'on salisse une copie de
  la ville (un meuble, un abribus) là où la graine n'en mettait pas.

✅ **14e vague livrée** (17 sept. 2026) — *la tempête de neige et la charrue*, **derrière une
option** (OPTIONS › TEMPÊTES DE NEIGE, NON par défaut). Un soir sur trois à partir du
deuxième, de 17 h à 23 h 30 : la ville blanchit, la neige tombe en biais, les chars glissent
et freinent mal — la police aussi —, le trafic lève le pied, et une charrue orange sort
déblayer sa tournée en poussant les chars mal garés.

- ⚠️ **Python règle, le navigateur neige** (`neige.py`, `neige.js`) : l'intensité est une
  fonction du jour et de l'heure (elle monte et retombe en trois quarts d'heure) ; la
  charrue suit une boucle d'autobus par le terminus, l'hôpital, l'usine et le garage (510
  tuiles). Aucun dé, rien de posé, la ville identique avec ou sans (un juge compare). **Sans
  l'option, 0 ne change rien** : l'adhérence est multipliée par 1, rien ne se peint, la
  charrue ne sort pas — un juge le vérifie un soir de tempête.
- ⚠️ **La neige déblayée est la seule mémoire** : la charrue note les tuiles qu'elle passe
  (sa voie et une de chaque côté) ; sur une tuile déblayée, l'adhérence revient aux trois
  quarts et le freinage en entier, et la tuile se recouvre au bout de trois heures de jeu.
  Rien ne se sauvegarde : une partie rechargée trouve la rue blanche. La charrue est une
  ligne sans arrêt qui ne voit pas les chars sans conducteur — elle les pousse.
- ⚠️ **La sonde d'abord** : `test_navigateur` mesure le pire cas ordinaire (au volant, trois
  étoiles) un soir de pleine tempête, à côté de la sonde de nuit — **1,3 ms** contre 1,2 ms
  sur la machine de développement. La neige au sol se peint **par plages** d'une rangée (une
  cinquantaine de rectangles, pas cinq cents), les flocons sont une fonction de l'image. ⚠️
  La mesure sur le vrai téléphone de Martin reste à faire avant de mettre l'option à OUI
  (voir « Dettes »).
- La charrue a sa silhouette (`camion_charrue`, déclarée `de: 'camion'` comme le tramway) :
  ⚠️ sa lame posée au sol soudait la roue avant à la route, et de profil la machine ne
  montrait plus qu'une roue — relevée, comme en transit. Le vent de tempête est une boucle
  ElevenLabs dont le volume suit l'intensité. **12 juges neufs** (`test_neige.py`,
  `test_neige_js.py`, la sonde), **15 mutations toutes rouges** — celle du premier soir
  restait verte tant que le juge ne posait pas un rythme où le jour 1 tombait pile.

✅ **15e vague livrée** (17 sept. 2026) — *la nuit de déneigement*, avec la neige (même
option). Le lendemain d'une tempête, dès midi, les panneaux d'un secteur clignotent orange —
« DÉNEIGEMENT CETTE NUIT · STATIONNEMENT INTERDIT DÈS 23:00 » — et de 23 h à 7 h, un char
laissé dans ses rues part au lot. Les secteurs se suivent, un par tempête, et la charrue
sort cette nuit-là aussi.

- ⚠️ **Elle s'annonce ou elle n'arrive pas** — le juge du plan : l'opération est une
  fonction du jour et de l'heure (`Neige.operationA`) ; un juge la parcourt minute par
  minute sur trois cycles de tempête et vérifie que chaque nuit est précédée, le même jour,
  d'au moins six heures d'annonce (onze, avec les réglages livrés). Python garde les bornes
  : l'annonce le jour même, bien avant la nuit, et jamais un soir de tempête.
- ⚠️ **Ce qui part au lot, c'est ce qui était permis le reste du temps** : un char `laissé`
  hors d'une case, dans le secteur — une ruelle, par exemple, où `Missions.malGare` ne le
  remorque jamais. Il part par `Missions.saisir` (on le rachète au comptoir), jamais sous
  les yeux, jamais celui de la planque, jamais dans sa case, jamais dans un autre secteur.
  ⚠️ Et le juge lit le LOT, pas la disparition : au-delà d'`oubli_px`, un char garé s'oublie
  de toute façon — le char de l'autre secteur « disparaissait » sans être remorqué, et la
  règle du secteur passait pour tenue.
- Les panneaux (`neige.panneaux`) : un au coin de chaque boîte du quartier, sur le trottoir
  — de 14 (La Pointe) à 54 (Le Faubourg) ; blancs, un P barré, un feu orange qui clignote.
  Entre la tempête et la fin de l'opération, la neige reste au sol à 60 % (`couverture`), et
  la physique la sent : la ville ne redevient grise que derrière la charrue. **7 juges
  neufs** (`test_deneigement.py`, `test_deneigement_js.py`), **14 mutations toutes rouges**
  — celle du secteur restait verte tant que le juge regardait si le char avait disparu
  plutôt que s'il était au lot.

✅ **16e vague livrée** (17 sept. 2026) — *le crime d'autrui*, et M12 est livré. La ville
volait, cognait et partait avec des chars toute seule (le pickpocket, la rixe, le voleur de
char) sans jamais te regarder ; maintenant, **rarement**, un passant qui a vu la scène de
loin te désigne — « C'EST LUI! » — si tu te tenais tout près. Il porte le crime, il court le
dire à un agent ou il téléphone, et on peut lui acheter le silence.

- ⚠️ **Le juge du plan : aucune étoile à un joueur qui n'y est pour rien.** Un VRAI vol à la
  tire (la routine du pickpocket, pas un appel à la main), la méprise forcée à coup sûr, le
  joueur immobile à 112 px de la victime : ni crime à son nom, ni chaleur, sur toute la
  machine des témoins. À 24 px, le badaud le désigne et la chaleur monte. Le rayon
  (`autrui.rayon_px`, 72) est la seule distance qui compte, et Python le borne à cinq
  tuiles.
- ⚠️ **Rare** : une chance sur trois (`autrui.chance`), tirée à l'EMPREINTE de l'image et du
  coupable — aucun dé, mesurée entre 20 et 50 % sur 400 images —, et pas deux méprises en
  une minute et demie. **Lisible** : la scène doit être à l'écran (le vrai coupable avec) ;
  le témoin doit voir le JOUEUR ; au volant, on passe. Et chaque méprise ne vaut qu'un délit
  à UNE étoile qui exige un témoin : on peut toujours lui acheter le silence.
- ⚠️ **La victime ne se trompe pas de coupable** : la plus proche de la scène, c'était elle
  — et elle te montrait du doigt au lieu de crier « AU VOLEUR! » après celui qui fuyait. Qui
  fuit le vrai coupable est écarté. ⚠️ Et le premier juge lisait des étoiles : un vol à la
  tire rapporté vaut le tiers d'une (35 de chaleur sur 100) — il lit la chaleur, comme le
  juge des témoins. Les trois juges qui tenaient « le joueur ne paie jamais le crime d'un
  autre » fixent la chance à 0 : ils mesurent le crime, pas la méprise. **6 juges neufs**
  (`test_crime_d_autrui.py`, `test_crime_d_autrui_js.py`), **13 mutations toutes rouges**.
