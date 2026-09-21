# M9 Le parc et les boulots

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M9 — Le parc automobile et les boulots (**ajout**, taille 3)_

_Ce que ça donne :_ autre chose à conduire, et de quoi gagner sa vie autrement.

⚠️ **Aux deux tiers le 13 sept. 2026, et il faut être précis sur ce qui manque.**
Le **Python est commité** (`7a4d26e` pour le catalogue, les boulots, les stations ; `e49603a`
pour le lot de la fourrière) : les fiches, l'économie, la carte et leurs juges existent.

**Livré le 13 sept. 2026** — les quatre chars existent, et un vélo ne saute plus (les deux
fiches ci-dessous). **Reste à faire**, et c'est celui qui se joue :

- « **mal garé** » ne veut encore rien dire : rien ne part au lot tout seul ;
- la **radio procédurale** est dans le paquet mais `Son.Radio` ne sait pas qu'une station
  peut venir de `musiques` plutôt que d'un mp3 — le bouton RADIO du camion ne fait rien ;
- et la remorqueuse **traîne** au lieu de **lever** — elle a une corde, pas une fourche (fiche
  ci-dessous, P4).

- `vehicules.py` : les quatre chars **existent, roulent, défoncent, soignent et remorquent**
  (fiches livrées plus bas) — plus une seule ligne de fiche que le navigateur ignore.
  Le **bateau** vient en dernier : il demande une physique à part et des tuiles d'eau
  carrossables — s'il coûte plus qu'il ne donne, il tombe en v3, et le traversier de M12
  suffit pour l'eau.
- Boulots au klaxon, sur le patron du taxi : **ambulance** (un blessé quelque part, chrono,
  le sortir vivant), **pizza** (trois livraisons, la pizza refroidit — le pourboire fond),
  **remorquage** (la fourrière paie pour les épaves).
- **Fourrière** : un char mal garé, ou saisi à l'arrestation, part au lot ; on le rachète
  au comptoir, ou on le reprend par-dessus la clôture (1★, et les gars du lot ripostent).
  - ⚠️ **« Mal garé » veut dire quelque chose** — **livré le 13 sept. 2026**. La règle était
    promise par la fourrière et n'existait nulle part. Depuis que les stationnements ont de
    vraies **cases** (`^ v < >`), elle tombe toute seule et se teste : est mal garé un char
    **laissé hors d'une case ET qui gêne** — la chaussée (où personne ne s'arrête), un
    passage piéton (où les gens traversent), le devant d'une porte (où les gens sortent).
    ⚠️ On regarde **toutes les tuiles que le char couvre**, pas son centre : un autobus de
    48 px en travers d'un passage a son centre sur le trottoir et bloque quand même. Un char
    dans sa case, rangé sur une ruelle ou sur du stationnement ne se fait **jamais**
    remorquer — même mal aligné, même depuis trois jours. ⚠️ Et **jamais le trafic** : seuls
    les chars que le joueur a **laissés** (`v.laisse`, posé en descendant) sont guettés —
    remorquer le trafic viderait les rues sans que personne comprenne pourquoi. ⚠️ Et
    **jamais celui de la planque** : c'est la sauvegarde de Martin. La remorqueuse passe
    après `FOURRIERE.remorquage_s` (45 s) et **prévient** dès la première seconde — sans
    avertissement, un char qui disparaît pendant qu'on fait une course passe pour un bogue,
    pas pour une règle. **Juges (2 neufs)** : les quatre cas de la règle (chaussée et passage
    oui, case et ruelle non), le trafic jamais touché, le chrono à trois secondes près, et le
    char de la planque intact ; côté Python, le délai est borné et le rachat minimum reste
    **au-dessus d'une course de taxi** — sinon se faire remorquer ne serait pas une punition.
  - ⚠️ **Le lot de la fourrière se gare comme les autres** (**correctif**). Sa cour est aujourd'hui un
    rectangle de `p` avec des places calculées à la main — alors que `_stationnement()`
    sait maintenant poser des rangées de cases, des allées et un îlot de béton. La cour doit
    passer par lui : des chars saisis rangés de travers dans un lot municipal, c'est
    exactement ce qu'on vient de corriger partout ailleurs, et les `places` du paquet se
    lisent alors dans les cases plutôt que dans une grille inventée.
  - ⚠️ **Mais pas de tremplin dans la cour.** `_stationnement()` finit par poser un
    `_tremplin_de_stationnement` dans une allée — dans la fourrière, ce serait une sortie
    par-dessus la clôture sans payer, et toute l'idée du lot tombe. La cour demande les
    cases **sans** le tremplin.
- **Radio procédurale** : `Son.Mus` (le séquenceur trois voix, déjà là) génère une station
  par véhicule à partir d'une graine — le camion a sa toune, l'autobus n'a que son moteur.
- **Juges** : chaque char a son sprite (harnais Node) ; la remorqueuse n'en traîne qu'un à
  la fois ; l'ambulance ne ressuscite personne ; la fourrière ne peut **jamais** manger le
  char de la planque (c'est la sauvegarde de Martin) ; le sport reste **sous** la moto et
  ne dépasse l'auto-patrouille que d'un cheveu ; le luxe est la plus grosse revente et la
  plus basse fréquence du parc ; aucun des deux ne naît dans un district qui ne les veut
  pas.

### Le remorquage, et reprendre son char par-dessus la clôture (taille 2) — **livré le 13 sept. 2026**

La fourrière avait son comptoir et sa saisie ; il lui manquait ses **deux portes de sortie**
et le boulot qui la remplit.

- **Le remorquage** est le seul boulot dont ce qu'on ramasse n'est pas une personne mais ce
  qu'on a **au crochet**. ⚠️ Le bouton du klaxon accroche d'abord (`basculerCrochet`) puis
  appelle le boulot : **une seule pression** attelle l'épave et prend le contrat. Il n'y a
  pas deux gestes à apprendre, et c'est ce qu'annonçait déjà la fiche du crochet.
- ⚠️ **La fourrière ne paie que les ÉPAVES.** Traîner une berline saine au lot, ce n'est pas
  du remorquage, c'est du vol — et le refus **se dit**, sinon le bouton a l'air cassé.
- ⚠️ **On livre DANS LA COUR**, pas à 44 px d'un point comme les autres boulots : la grille
  fait quatre tuiles et une remorqueuse de 36 px avec son épave au bout ne s'arrête pas au
  pixel près dessus. L'épave part à la ferraille — le lot la prend, il ne la range pas.
- **Reprendre son char par-dessus la clôture** est l'autre moitié de la fourrière, et elle ne
  demande **aucun code de géométrie** : le grillage s'enjambe à pied et arrête les chars, il
  n'y a qu'une grille, donc sortir un char saisi de la cour suffit à tout déclencher. C'est
  `_fourriere()` qui l'avait prévu en Python ; le navigateur n'avait qu'à regarder.
- ⚠️ **Un PLANCHER d'étoiles, pas de la chaleur.** Un délit de gravité 1 pose 35 points sur
  les 100 d'une étoile : il aurait fallu voler trois fois pour que quiconque se déplace. Or
  le lot **appelle** — ce n'est pas une ambiance qui chauffe, c'est un signalement.
  `Police.etoilesAuMoins()` est la différence entre « quelqu'un a vu » et « quelqu'un a
  appelé », et elle resservira.
- **Les gars du lot ripostent** : un archétype `gardien` (batte et courage 1, ⚠️ **pas** de
  pistolet — ils ripostent, ils n'abattent pas), `frequence: 0` donc jamais dans la rue, deux
  à la grille. ⚠️ Ils se lancent **après** `Entites.alerter()` : celui-ci repasse sur tout le
  monde autour et remplace l'état de qui n'est ni en fuite ni témoin — il effaçait leur
  riposte à l'image même où on la posait.
- ⚠️ **`aToi` : un char payé au guichet n'est plus un vol.** Racheter le sien puis monter
  dedans signalait un `vol_vehicule` — et le comptoir ne servait alors plus à rien : autant
  sauter la clôture. C'est le genre de trou qui ne se voit qu'en jouant les deux chemins
  l'un après l'autre, ce que fait le juge.
- ⚠️ **Et `garnirLaFourriere` est idempotent** : `commencer()` garnit la cour, un
  rechargement la garnit encore — deux fois les gardiens, c'est quatre gars à la grille, et
  deux fois les chars, c'est un char par-dessus l'autre.
- **Ce qui reste** : « mal garé » (le remorquage automatique) et la radio du camion.
- **Juges (2 neufs, 2 Python)** : une berline saine au crochet ne lance rien et le dit, une
  épave prend le contrat en une pression, décrocher en route le fait tomber, et la livraison
  dans la cour paie base + distance ; sortir un char saisi signale `fourriere`, donne son
  étoile, vide sa ligne du lot, fait **glisser les rangs** des autres (sinon le comptoir
  libère le mauvais char), et met les deux gardiens sur toi — pendant que le même trajet,
  **racheté**, ne coûte rien. Côté Python : le délit `fourriere` est bruyant et vaut
  exactement `FOURRIERE.etoiles_vol` (deux tables, une seule vérité), et le gardien a un
  métier, du courage et une batte.

### La fourrière : on te prend ton char, tu le rachètes (taille 2) — **livré le 13 sept. 2026**

⚠️ **La fourrière existait en Python depuis M9** — une cour clôturée avec sa guérite et sa
grille, 40 cases de stationnement, un intérieur, `economie.FOURRIERE` et son juge
d'équilibrage — et **le navigateur n'en savait rien**. Le comptoir « LE LOT » avait un
libellé et **aucun menu** (il était même sur la liste des comptoirs en chantier), et rien n'y
amenait jamais un char. Une cour entière dessinée pour rien.

- **On te prend le char que tu CONDUISAIS.** ⚠️ Pas celui où tu es : la police te **sort** du
  char avant de t'embarquer, donc `j.dansVehicule` est déjà nul à l'arrestation. Sans un
  souvenir du dernier char conduit (`j.dernierVehicule`, posé au montage), on n'aurait
  **jamais rien saisi** — et le bogue aurait eu l'air d'un oubli de règle plutôt que d'une
  question d'ordre.
- ⚠️ **Jamais celui de la planque.** C'est la sauvegarde de Martin : un char qui disparaît de
  devant chez soi pendant qu'on dort n'est pas une règle de jeu, c'est une perte.
- **Le lot garde `places` chars, et c'est le plus VIEUX qui part** quand il déborde — d'où un
  **tableau** dans la sauvegarde, pas un objet : il y a un ordre, pas un sac.
- **Ils attendent dans la cour**, sur les cases du lot, posés au démarrage comme le char de la
  planque l'est devant sa porte. ⚠️ `Monde.carte` ne portait pas `fourriere` : la cour était
  dans le paquet et le navigateur ne la lisait pas — encore.
- **Le comptoir les liste et les revend**, du plus récent au plus vieux. ⚠️ Un char racheté
  **n'est plus volé** : on vient d'en payer la sortie devant un guichet municipal, avec son
  numéro au registre. Et un lot vide **le dit** au lieu de se taire.
- ⚠️ **LA règle, et elle est économique** : racheter doit coûter **plus cher que revendre** le
  même char au garage. Sinon on se fait saisir un char exprès pour le racheter moins cher
  qu'il ne se revend, et la fourrière devient une machine à argent. Le juge la vérifie sur
  **tout** le catalogue, pas sur un exemple.
- ⚠️ **Une vieille partie n'a pas le tableau.** Un tableau ne passe pas par la fusion des
  objets de `completer()` : une sauvegarde d'avant la fourrière arriverait avec `undefined`,
  et le comptoir planterait au premier clic.
- **Ce qui reste** (fiche à part) : « mal garé » qui remorque tout seul, reprendre son char
  **par-dessus la clôture** (1★, les gardiens ripostent), et le **boulot de remorquage** — il
  attendait la fourrière, il l'a maintenant.
- **Juges (1 neuf, 1 exemption levée)** : l'arrestation saisit le dernier char conduit alors
  qu'on est **dehors**, le lot déborde par le plus vieux, le comptoir vend et encaisse le bon
  prix, un lot vide le dit, les chars saisis se posent **dans la cour**, et le rachat est plus
  cher que la revente **pour chaque char du catalogue**. ⚠️ Et `fourriere` sort de la liste
  des comptoirs en chantier de `test_interieurs_js` — cette liste est pénible à garder
  **exprès** : un comptoir dessiné sans menu doit coûter quelque chose.

### Les boulots au klaxon : la pizza et l'ambulance (taille 2) — **livré le 13 sept. 2026**

⚠️ **`Missions.taxi` était le seul boulot du jeu.** Les trois autres vivaient dans
`economie.BOULOTS` — fiches complètes, juge d'équilibrage Python, exportées dans le paquet —
et le klaxon d'une moto ne faisait **rien**. Encore des fiches que le navigateur ne lisait
pas, comme `cercles`, `defonce` et `soigne` avant elles.

- **Une machine pour les quatre, pas quatre machines.** À quatre boulots, on aurait recopié
  quatre fois « va là, reviens ici, encaisse » avec quatre façons de se tromper. Ce qui
  **diffère** tient dans une table de dix lignes (`SORTES` : ce qu'on va chercher, où l'on
  va, ce qu'on affiche) ; tout le reste est commun. ⚠️ Et les **nombres** ne sont pas là non
  plus : ils viennent de `economie.BOULOTS`, où un juge Python les compare entre eux.
- **La pizza** a ce que le taxi n'a pas : **trois livraisons de suite**, et une prime qui
  **fond toute seule** (50 s). Pas de ramassage — on part avec les boîtes, et la seule
  pression du boulot est que ça refroidit. ⚠️ **La distance se paie à chaque étape** : sinon
  trois livraisons rapporteraient trois fois le premier trajet.
- **L'ambulance** va **chercher** quelqu'un. ⚠️ Le blessé est **à terre**, pas debout à héler
  — c'est ce qui le distingue d'un client de taxi à douze pixels. Et **il ne se relève pas** :
  un assommé se remet debout au bout de `ko_images` et s'enfuit, un blessé attend. Le seul
  chrono qui compte est celui du boulot, et **la prime EST sa vie** : passé les 100 s, il ne
  reste que la base. ⚠️ Sa destination n'est pas tirée au hasard comme celle du taxi : un
  blessé va **à l'hôpital**.
- ⚠️ **Un compteur par sorte**, et c'est ce qui sauve une mission de M6 : le défi « trois
  courses » compte des courses de **taxi**, et une pizza livrée n'en est pas une. Un compteur
  unique aurait laissé gagner le défi en livrant des pizzas, sans qu'aucun test ne bronche.
- **Le HUD dit lequel** : la ligne au volant affichait « TAXI : … » en dur. À quatre boulots,
  « TAXI » en tête d'une livraison de pizza ne veut plus rien dire — elle prend le nom de la
  fiche.
- **Le remorquage reste dehors**, et c'est voulu : il a besoin de la **fourrière** (où
  déposer l'épave, et qui paie). `SORTES` ne le déclare pas, donc le klaxon d'une remorqueuse
  ne promet rien — il **accroche**, ce qui est déjà son geste.
- **Juges (2 neufs)** : la pizza part sans ramassage, se livre **trois** fois, paie plus
  chaude que froide et jamais moins que la base ; l'ambulance va chercher un blessé **à
  terre** à moins de 30 % de vie, l'emmène **à l'hôpital** (pas au hasard), donne la prime
  pleine à temps et la base seule trop tard ; et dans les deux cas le compteur du **taxi**
  reste à zéro. Le juge du taxi, lui, a été rejoué à la nouvelle machine.
- ⚠️ **Corrigé le 13 sept. 2026, dans l'heure** (retour de Martin : « on ne devrait pas avoir
  de nouveaux contrats quand on arrête la sirène ; et quand un contrat est en cours, on ne
  peut pas en ravoir un autre »). Le bouton du klaxon fait **deux** choses dans une
  ambulance : il bascule la sirène **et** il prend l'appel. Le premier geste est le bon ; le
  second l'était aussi, mais **dans les deux sens** — éteindre sa sirène en sortant de
  l'hôpital rappelait aussitôt une ambulance, et on repartait sans l'avoir demandé. Un appel
  ne se prend plus que **quand on allume** : le geste inverse veut dire « j'ai fini ». Et le
  refus d'un deuxième contrat, qui était muet, **se dit** maintenant sur un char à sirène —
  le bouton vient d'allumer la sirène, il a donc l'air d'avoir fait quelque chose, et un
  refus silencieux passerait pour une panne. ⚠️ Dans un taxi, on se tait : le klaxon y sert à
  la circulation, et le répéter à chaque coup serait du harcèlement. **Juge (1 neuf)** : les
  trois états du bouton — on allume (contrat), on éteint (rien), on rallume pendant un
  contrat (rien de plus, le même client) — et il rougissait exactement sur le cas de Martin.

### Le haut de gamme : deux chars qu'on vole exprès (taille 1) — **livré le 13 sept. 2026**

_Demande de Martin._ ⚠️ **Tout le reste du parc est utilitaire** — on le prend parce qu'il
sert : un camion pour défoncer, une ambulance pour se soigner, un taxi pour gagner sa vie. Il
manquait le contraire : un char qu'on prend parce qu'on le **veut**. Deux fiches, pas dix, et
elles ne valent que si elles **s'opposent**.

- **Le sport** (coupé décapotable, 26 × 13) : le plus rapide **sur quatre roues** — la moto
  reste devant, c'est la règle du parc depuis M3 — reprise sèche (0,085 contre 0,06 pour une
  berline), et une **adhérence de 0,055** là où tout le monde est à 0,12. ⚠️ **C'est
  l'adhérence qui EST le caractère du char** : `majPhysique` fait glisser la vitesse réelle
  vers le cap à ce taux, donc le coupé part en travers là où une berline se contente de
  ralentir. Et il le paie : **75 PV**, la carrosserie la plus mince des autos — un barrage
  l'arrête pour de bon.
- **Le luxe** (grosse berline noire, 32 × 15) : lourde (masse 1,8), elle encaisse (220 PV),
  elle colle à la route (0,16) et **elle ne va pas vite** (3,6). ⚠️ Elle ne récompense pas la
  conduite, elle récompense **le vol** : c'est la **meilleure revente du jeu** (5 200 $ neuf),
  et ça tombe tout seul — `economie.prix_vente` est déjà proportionnelle au prix neuf, et le
  malus par doublon du même jour empêche d'en faire une usine. Son alarme dure **30 s** contre
  12 pour les autres (`alarme_s` en fiche) : c'est le prix de cette revente.
- ⚠️ **Ce qui les rend rares, ce n'est pas leur `frequence`, c'est LA CARTE.** Ils portent
  `rare: true`, et un char rare ne naît **que** dans un district qui le déclare (`rares` de
  `carte.DISTRICTS`) : le luxe au Faubourg (l'Hôtel Bandini) et aux Érables (les entrées de
  banlieue), le sport au Faubourg et à La Pointe (le Carré). **Ni l'un ni l'autre à La Shop** —
  on ne laisse pas une décapotable dans une cour à ferraille — ni sur la baie. Un char rare
  qu'on croise partout n'est plus rare, et c'est tout ce qui fait qu'on le veut.
- ⚠️ **Et une cour de gang hérite des rares de son district.** `Monde.zoneA` rend la zone la
  **plus précise** : sans ça, un coupé ne naîtrait jamais dans le seul coin où l'on se bat
  pour eux.
- **Les deux dessins s'opposent aussi**, sinon ce sont deux lignes de catalogue de plus. Le
  sport est le **seul char du parc dont l'habitacle est ouvert** — un trou dans le toit, deux
  sièges dedans ; le luxe est le seul dont le toit est **plein, lisse et cerné de chrome**. Vu
  d'en haut, c'est tout ce qu'on a pour les nommer, et ça suffit.
- ⚠️ **Un juge du trafic a dû être réparé, pas contourné.** `test_le_trafic_roule_3000_images`
  ne suivait que les chars présents à **une** image donnée — or le joueur ne bouge pas, donc la
  plupart s'en vont en quelques secondes, et l'échantillon tombait à deux ou trois. Le juge
  dépendait alors du tirage plutôt que du trafic, et deux entrées de catalogue de plus ont
  suffi à le faire rougir. Il suit maintenant **tous** ceux qui passent pendant les
  1 800 images. ⚠️ Un char **bloqué**, lui, reste dans la bulle et accumule des images sans
  avancer d'un pixel : élargir l'échantillon le trouve **mieux**, pas moins bien — et le juge
  élargi passe aussi sur l'ancien code, ce qui prouve qu'on n'a pas baissé la barre.
- **Juges (2 neufs)** : les deux s'opposent (le sport est le plus rapide des autos et le plus
  fragile, le luxe le plus cher, le plus lourd, le plus accrocheur, et son alarme la plus
  longue) et **aucun char non rare n'est aussi rare qu'eux** ; côté carte, tout ce qui est
  déclaré `rare` naît **quelque part**, rien d'étranger ne se déclare, La Shop et la baie n'en
  ont aucun, et une cour de gang connaît les chars de son district.

### Le camion défonce, l'ambulance soigne (taille 1) — **livré le 13 sept. 2026**

`defonce` et `soigne` étaient dans les fiches depuis M9, et **personne ne les lisait** : le
camion rebondissait sur un grillage comme une berline, et l'ambulance était une fourgonnette
blanche. Trois nombres du catalogue (0,75 · 0,7 · 0,6) et un quatrième (2 PV/s) qui ne
voulaient rien dire.

- **`Monde.defoncer(tx, ty)`** fait tomber une tuile **basse** et met à sa place le sol de ses
  voisines. ⚠️ **Le glyphe de remplacement se LIT DANS LES VOISINES** : une clôture entre un
  gazon et un trottoir laisse du gazon ou du trottoir. C'est ce qui évite un glyphe
  « décombres » de plus, avec son peintre, son entrée de légende et son octet dans le
  paquet — le trou dans une clôture, c'est la clôture qui manque, pas des gravats.
- ⚠️ **Et les morceaux voisins se repeignent, pas seulement le sien.** Une clôture lit ses
  voisines pour savoir comment se dessiner (`varianteDeCloture`, livré le matin même) : en
  casser une change le dessin des deux d'à côté, qui peuvent être dans un autre morceau.
- ⚠️ **Tout ou rien.** `defoncerDevant()` regarde **toutes** les tuiles qui bloquent avant de
  trancher : s'il y en a une seule qu'on ne casse pas, le camion s'arrête comme n'importe qui.
  Casser « celles qu'on peut » et s'arrêter sur le reste laisserait un trou dans une clôture
  **sans être passé** — le pire des deux mondes.
- ⚠️ **Jamais une façade**, jamais l'eau, jamais le barbelé, jamais un meuble. La ville tient
  par ses murs : les juges de connexité, les intérieurs et les devantures en dépendent, et un
  trou dans un mur ouvrirait sur un toit.
- **Ce qui reste de vitesse est le `defonce` de la fiche** — 0,75 pour le camion. Un mur de
  clôture coûte donc quelque chose (et `defonce_degats` à la carrosserie), sinon on le
  franchit sans le sentir.
- **L'ambulance rend `soigne` PV par seconde à qui la conduit.** ⚠️ Elle ne **ressuscite**
  personne : un mort reste mort. Sinon elle devient la sortie de secours de toutes les
  fusillades, et l'hôpital ne veut plus rien dire.
- ⚠️ **Ça ne se sauvegarde pas.** La ville se répare au rechargement : le trou dans la
  clôture vit le temps de la session. C'est une décision — la carte est le paquet, et écrire
  les tuiles cassées dans la sauvegarde ferait grossir chaque partie de tout ce qu'on a
  renversé depuis le premier jour.
- **Juges (2 neufs)** : un camion lancé traverse un grillage **et** une borne-fontaine, en
  garde 0,75 de sa vitesse mesurée **à l'image du passage**, et s'abîme ; il **ne traverse ni
  une façade ni du barbelé** ; une berline ne casse rien ; au pas (sous
  `defonce_vitesse_min`), personne ne défonce. Et l'ambulance rend bien ses PV, s'arrête au
  plafond, met la sauvegarde à jour, pendant qu'une berline n'en rend aucun.

### La dépanneuse lève les roues (**ajout**, taille 1) — **livré le 14 sept. 2026**

_Demande de Martin :_ « la dépanneuse devrait embarquer les roues avant des véhicules qu'elle
remorque, sauf les motos et vélos qu'elle embarque complètement sur sa plateforme. »

⚠️ **Aujourd'hui, c'est une corde, pas une fourche.** `majCrochet()` tire le char vers un
point derrière la remorqueuse avec `crochet_raideur`, le char pointe **vers** elle, et le
lien **lâche** si on l'étire. Autrement dit : le véhicule remorqué roule sur ses quatre roues,
à plat, au bout d'un élastique. C'est ce qu'on écrit quand on a `crochet_cable_px` sous les
yeux — et c'est ce qui fait qu'une remorqueuse ressemble encore à une auto qui tire une auto.

Ce qu'il faut, et dans cet ordre :

- **Le lien devient RIGIDE.** Une fourche ne s'étire pas : le point d'attache est fixe, et
  `crochet_raideur` ne décrit plus rien. ⚠️ **Et ça change la réponse à la seule question qui
  compte** : que se passe-t-il quand la charge est bloquée par une tuile ? Ce n'est plus le
  câble qui s'allonge, c'est **la remorqueuse qui ne passe pas**. Elle teste donc **les deux
  corps** avant d'avancer — le même « tout ou rien » que `defoncerDevant()`. Sans ça, on
  recule dans un mur avec une auto au bout de la fourche et elle le traverse.
- **L'avant est levé, et ça se voit.** ⚠️ **Ne pas inventer un sprite « nez en l'air »** : ce
  serait 32 caps de plus par char et par couleur, pour deux pixels. Trois détails suffisent,
  et le moteur sait déjà les faire :
  - le char remorqué se **colle** à la remorqueuse — plus de trou de câble entre les deux ;
  - il se dessine **deux pixels plus haut**, l'ombre restée au sol : c'est exactement ce que
    `dessinerUn()` fait déjà pour `v.z > 2` ;
  - et il est **dans l'axe** de la remorqueuse, plus « pointé vers elle ». Une fourche ne
    laisse pas de jeu, et c'est ce jeu qui trahit la corde.
- **Le plateau, pour ce qui tient dessus.** Une moto, un vélo : ça ne se lève pas par l'avant,
  ça se **charge en entier**. ⚠️ **C'est Python qui le décide** — un champ `plateau` dans la
  fiche (vrai pour la moto et le vélo), pas un `classe === 'moto'` caché dans le JS. C'est la
  leçon de `reservoir` : le jour où une trottinette arrive, elle le dit elle-même, et un juge
  vérifie que la liste n'a pas changé de sens dans notre dos.
  - À bord, le deux-roues **ne traîne plus du tout** : même décalage, même cap, zéro écart —
    il bouge avec la remorqueuse comme s'il en faisait partie.
  - Il n'est plus **bloqué par les tuiles** et ne **heurte** plus rien : c'est de la
    cargaison, pas un véhicule sur la route.
  - Le lien ne peut donc pas lâcher : on n'étire pas un plateau. Le message « LE CÂBLE A
    LÂCHÉ » n'a plus de sens pour lui.
  - ⚠️ **L'ordre de dessin** : la charge se peint **après** la remorqueuse, sinon la moto
    disparaît sous elle. C'est le genre de détail qu'on ne voit qu'une fois en jeu.
- ⚠️ **On ne monte plus dans un char remorqué.** Rien ne l'interdit aujourd'hui, et ce serait
  la façon la plus courte de casser la physique : deux conducteurs, deux volontés, un seul
  lien rigide. Le refus doit se **dire** (une invite), pas juste ne rien faire.
- **Le sprite de la remorqueuse ne change pas** : il porte déjà son bras couché et son
  plateau. C'est la charge qui se place dessus.
- **Juges** : une auto remorquée est **collée** (l'écart tombe sous ce qu'il vaut aujourd'hui)
  et **dans l'axe**, pas en biais ; une moto et un vélo montent **sur** la remorqueuse — même
  cap, même vitesse, écart nul — et se dessinent après elle ; une moto à bord ne heurte rien
  et aucune tuile ne l'arrête ; la remorqueuse **refuse d'avancer** là où sa charge ne passe
  pas au lieu de la traîner dans un mur ; on ne monte pas dans un char remorqué ; et `plateau`
  est vrai pour **exactement** la moto et le vélo.

**Livré le 14 sept. 2026.** Tout y est, et deux choses se sont apprises en chemin.

- **Le lien est rigide** : `placeDeLaCharge()` rend un point fixe, `majCrochet()` **pose** la
  charge au pixel et au cap. Elle ne suit plus — elle **est** posée. `crochet_cable_px` et
  `crochet_raideur` ont disparu de la fiche : ils ne décrivaient plus rien.
- ⚠️ **La charge se pose APRÈS que la remorqueuse a bougé**, et c'est le juge qui l'a dit.
  Placée au début de l'image, elle l'était d'après la position de l'image **précédente** :
  l'écart respirait alors de la distance parcourue dans l'image — deux pixels à vitesse de
  croisière, et c'est **exactement** le jeu qu'une corde a et qu'une fourche n'a pas.
- ⚠️ **Une charge ne conduit pas.** Elle passait encore par `majPhysique` et `avancer` : elle
  refaisait sa propre physique par-dessus le placement, se dégageait des tuiles, rebondissait
  sur les murs et repartait de biais. Exactement le jeu qu'on venait d'enlever.
- **La remorqueuse ne passe pas là où sa charge ne passe pas** (`chargeBloquee`), le même
  « tout ou rien » que `defoncerDevant`. **Mesuré sans le garde-fou : 22 px de recul dans la
  façade**, l'auto au bout traversant le mur.
- **Le plateau vient de Python** : `plateau` dans la fiche, vrai pour exactement la moto et le
  vélo, et un juge le tient. À bord, zéro dérive (mesurée sur 120 images de virage), aucune
  tuile ne les arrête, et elles se peignent **après** la remorqueuse — sinon la moto disparaît
  dessous, et c'est le genre de détail qu'on ne voit qu'une fois en jeu.
- **Décrochée, la charge redescend** (`z = 0`). Sans ça elle restait en l'air, ombre décollée —
  et au-dessus de six pixels d'altitude, `bloqueParLesTuiles` la répute en plein saut et la
  laisse **traverser les murs**.
- **On ne monte plus dans un char remorqué**, et le refus **se dit** (« IL EST SUR LA
  FOURCHE ») : une portière qui ne s'ouvre pas sans un mot se lit comme un bogue.
- ⚠️ **Deux juges ont été réécrits, pas assouplis** : ils décrivaient le câble (« il s'étire »,
  « il lâche à 400 px »), ce que la fiche demandait précisément de supprimer. Ils mesurent
  maintenant la fourche — écart **constant** à un pixel près, valeur attendue lue dans la
  fiche, biais sous 0,02 rad — ce qui est plus strict que ce qu'ils exigeaient avant.

### Le crochet de la remorqueuse (taille 1) — **livré le 13 sept. 2026**

`crochet` était la dernière ligne de fiche que personne ne lisait : la remorqueuse était un
camion orange. Elle traîne maintenant un char — **un seul**.

- **On accroche DERRIÈRE.** Un crochet est à l'arrière : il faut reculer dessus. C'est ce
  geste, et pas le catalogue, qui fait qu'une remorqueuse n'est pas un camion.
- ⚠️ **Un seul à la fois**, et ce n'est pas un détail de confort : c'est ce qui empêche le
  train de douze chars qu'on ne saurait plus arrêter. Le **même bouton** accroche et décroche.
- **Le câble** tire le char vers un point fixe derrière la remorqueuse (`crochet_cable_px`,
  `crochet_raideur`), et le char **pointe vers elle** — c'est ce qui se lit d'un coup d'œil.
- ⚠️ **Il reste bloqué par les tuiles** : on ne traîne pas une épave à travers un mur. Le
  câble s'étire alors, et **s'il s'étire trop, il lâche**. Un virage serré coûte donc quelque
  chose, sans une seule ligne de plus.
- ⚠️ **Jamais un char conduit** : on n'accroche pas une auto avec quelqu'un dedans.
- ⚠️ **Deux chars reliés ne se bousculent pas** (`heurterVehicules` saute la paire) et le
  trafic **n'oublie pas** un char qu'on traîne — sinon il disparaîtrait au bout du câble dès
  qu'il passerait la distance d'oubli. Et si la remorqueuse saute, le câble lâche : sans ça,
  un char reste accroché à une carcasse que plus personne ne met à jour.
- **Le boulot de remorquage est le même bouton** : il n'y aura pas deux gestes à apprendre
  quand la fourrière ouvrira.
- **Juge (1 neuf)** : rien ne s'accroche **devant** ; ce qui est derrière s'accroche ; un
  deuxième appui décroche au lieu d'ajouter ; un char conduit se refuse ; en roulant droit sur
  90 images le char suit sans monter dans la remorqueuse ni s'éloigner sans fin, et il pointe
  vers elle ; étiré de force à 400 px, le câble lâche.

### Un vélo ne saute plus, il se plie (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Retour de Martin :_ il part en boule de feu et donne 2★.

⚠️ **Et c'est exactement ce qui se passait.** `endommager()` appelait `exploser()` dès que
les PV tombaient à zéro, **pour tous les véhicules sans une seule exception** — et le vélo a
30 PV, le plus fragile du jeu. Deux coups de batte, et le juge du banc le mesure : quarante
particules, quatre marques au sol, une déflagration de 60 px qui blesse le passant à 18 px
**et** cabosse l'auto d'à côté, l'écran qui tremble, un délit `explosion` et son alarme de
15 tuiles. On renversait un vélo, et la police arrivait.

Ce qui a été livré :

- **La règle tient sur une ligne de fiche** : `vehicules.py` gagne `reservoir` — **ce qui n'a
  pas de réservoir ne brûle pas et n'explose pas**. ⚠️ C'est **Python** qui le décide, pas un
  `slug === 'velo'` caché dans le navigateur : le jour où une trottinette arrive, elle se plie
  toute seule, et un juge dit que le vélo est le **seul** du catalogue dans ce cas.
- **Un vélo à zéro PV se plie** : il gît de travers (un peu de cap au hasard, pour qu'on voie
  qu'il est tombé), il grisonne, son cycliste part avec — il est déjà `ejecte` —, huit
  poussières et le bruit d'un choc. Pas d'explosion, pas de secousse, pas de marque au sol.
- ⚠️ **Il ne brûle pas non plus avant.** `majEtatDuChar` mettait le feu sous 20 % des PV et
  rongeait 4 PV par seconde jusqu'à l'explosion : un vélo cabossé au bord du trottoir
  s'enflammait tout seul, puis sautait. Ni feu ni fumée sans réservoir.
- ⚠️ **Ni une fois plié.** La carcasse d'un char fume tant qu'elle est là ; celle d'un vélo,
  non — il n'avait rien à brûler. C'est le détail qu'on ne voit qu'en regardant l'épave dix
  secondes, et c'est là qu'une règle à moitié appliquée se remarque.
- ⚠️ **Ni dans la chaîne** : `exploser()` endommage les véhicules autour, donc une explosion
  en déclenche d'autres. Un vélo garé à côté d'un char qui saute se plie maintenant au lieu
  d'agrandir la déflagration gratuitement — sans une ligne de plus, parce que c'est
  `endommager()` qui tranche, et que toute la chaîne passe par lui.
- **Juges (2 neufs)** : côté Python, le vélo est le seul sans réservoir et tout ce qui n'est
  pas de la classe `velo` en a un ; côté banc, **le même décor que le juge de l'explosion**,
  au vélo près — le voisin est intact, l'auto d'à côté est intacte, l'écran n'a pas tremblé,
  zéro marque, zéro délit, zéro étoile, et **zéro particule près du vélo pendant les cent
  images qui suivent**. ⚠️ Le même test fait ensuite sauter une auto pour de vrai : il mesure
  une **différence**, pas une panne.

### Les quatre chars existent (taille 1) — **livré le 13 sept. 2026**

⚠️ **Le catalogue promettait des chars que le jeu ne montrait pas, et rien ne le disait.**
`camion`, `autobus`, `ambulance` et `remorqueuse` étaient en phase 1 : le trafic les tirait,
le garage les rachetait, la fourrière les comptait — et `SPRITES[v.sprite]` n'existait pas,
donc `dessinerUn()` sortait en silence sur son `if (!def) return`. Un char invisible qui
roule, qu'on peut heurter et voler.

Le prologue de `vehicules.py` annonçait pourtant : « phase 1 = le navigateur a son sprite. Un
test vérifie que chaque véhicule de phase 1 a un sprite. » ⚠️ **Ce test n'existait pas.**
`test_les_sprites_sont_integres` valide les sprites _déclarés_ dans `SPRITES` — il ne dit
rien du catalogue. C'est donc lui qu'on a écrit en premier, et il rougissait quatre fois.

Ce qui a été livré :

- **Le juge d'abord** : pour chaque véhicule de phase 1, `SPRITES[v.sprite]` existe, le
  sprite **couvre** la carrosserie (jamais plus court que `longueur`, jamais une affiche non
  plus : `longueur + 6` au plus) et il se cuit en 32 caps. ⚠️ Il tient aussi la liste de la
  phase 2 : le jour où le bateau y passe, le test le réclame au lieu de se taire.
- **Quatre sprites, et une règle de dessin qui vient de la vue.** ⚠️ **Vu d'en haut, un char
  est un TOIT** : à douze pixels de large, ce n'est pas le pare-brise qui nomme un véhicule,
  c'est ce qu'il porte sur le dos. D'où les **nervures** de la caisse du camion, les
  **trappes** de l'autobus, la **croix rouge** de l'ambulance, et le **bras couché avec son
  crochet qui dépasse** de la remorqueuse. La marge reste celle de l'auto (longueur + 4,
  largeur + 2) : deux pixels pour les roues, de chaque côté.
- ⚠️ **La chaîne de cercles lit enfin la fiche.** `cercles()` prenait `PHYSIQUE.cercles` — 3
  pour tout le monde, y compris pour un autobus de 48 px de long sur 16 de large. Le juge
  Python `test_la_chaine_de_cercles_ne_laisse_aucun_trou` exigeait 5 depuis M9, le catalogue
  les déclarait, et **le navigateur ne les lisait pas** : deux trous restaient entre les
  cercles, par lesquels une moto entrait dans l'autobus sans que rien ne se touche. Un
  deuxième juge mesure maintenant l'écart entre cercles voisins **au banc**, char par char.
- **Juges (2 neufs)** : celui des sprites de phase 1, et celui qui crée les cinq chars, les
  conduit vingt images, mesure la chaîne de cercles (aucun trou, le compte de la fiche) et
  dessine une image sans planter.
- ⚠️ **Corrigé le 13 sept. 2026, une heure après la mise en ligne** (bug de Martin :
  « l'autobus est transparent »). Il l'était. `s` valait `#00000030` — un noir à 19 % — copié
  des trois autos, **où il ne couvre que huit pixels de capot** : un reflet. Sur l'autobus, la
  même lettre couvrait deux trappes de toit de 66 pixels, soit **17 %** de la carrosserie, et
  le canevas de cuisson est transparent : on voyait la rue à travers l'autobus. Les quatre
  nouvelles palettes prennent des tons **opaques** (une trappe grise, une bande orange sur le
  blanc de l'ambulance), et **un troisième juge** tient la règle : un reflet est un détail,
  **au plus un pixel peint sur vingt** par sprite de véhicule. La règle n'est pas « aucune
  couleur translucide » — les trois autos en vivent très bien — c'est la **surface** qui
  décide. Il rougissait à 17 %.

## Notes

⚠️ Le Python était commité et **le JS n'existait pas** : quatre chars de phase 1 vivaient
dans le paquet, se tiraient au trafic et se revendaient au garage, mais **rien ne les
dessinait** — et aucun test ne le disait, alors que le prologue de `vehicules.py` le
promettait. **Livré** : les quatre sprites (camion, autobus, ambulance, remorqueuse), le
juge manquant (« tout char de phase 1 a son sprite »), et la **chaîne de cercles lue dans la
fiche** — elle valait 3 pour tout le monde, donc une moto entrait dans l'autobus par le
milieu. Et **un vélo ne saute plus** : il n'a pas de réservoir, donc il se **plie** — pas de
feu, pas de fumée, pas de secousse, aucun délit. Le **camion défonce** ce qui est bas et
jamais une façade, l'**ambulance soigne** qui la conduit sans ressusciter personne. La
**remorqueuse traîne** un char, un seul. Et le **haut de gamme** est là : un coupé sport et
une berline de luxe, `rare`, qui ne naissent que dans les districts qui les déclarent. La
**pizza** et l'**ambulance** se prennent au klaxon — et dans une ambulance, l'appel se prend
**quand on allume** la sirène, jamais quand on l'éteint (retour de Martin). La **fourrière**
saisit ton char à l'arrestation et te le revend. Le **remorquage** paie les épaves qu'on lui
amène au crochet, et **reprendre son char par-dessus la clôture** met le lot et ses gardiens
sur toi. **M9 est complet**
