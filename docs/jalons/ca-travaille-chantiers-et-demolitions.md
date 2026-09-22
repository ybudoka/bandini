# Ça travaille : chantiers et démolitions

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Ça travaille : maisons, commerces et rues en chantier (**ajout**, taille 3)_

_Demande de Martin (15 sept. 2026) :_ « je veux des zones comme des maisons ou commerces ou
des rues soit en construction avec des pelles, des boules de démolition, des… » puis, tout de
suite après : « des grues ».

**Ce qui existe déjà, et c'est presque tout** — la fiche est courte parce que le dépôt a fait
le gros du travail sans le savoir :

- le **terrain vague** est un genre de parcelle depuis M1 : ceinturé de grillage (de barbelé
  dans La Shop), ouvert au nord sur la ruelle, avec du décor semé dedans. Une parcelle sur
  vingt au centre, une sur huit ailleurs ;
- les **entraves** de M12 font déjà la rue : une voie fermée, des cônes, un détour, tirés par
  la graine du jour ;
- le **décor se brise** (20 fiches `DECORS` avec leur `pv`), et `reparerLeDecor()` remet tout
  au matin ;
- et surtout : **une tuile se change en cours de partie**, avec ses morceaux voisins recuits —
  c'est le chemin qu'emprunte une clôture qu'on défonce.

Ce qui manque n'est donc pas la mécanique. C'est qu'**aucun endroit de la ville ne dit
« ça travaille ici »**.

**La règle : un chantier est un état de parcelle, pas un dessin.** `carte` déclare des
`CHANTIERS` — une parcelle, un genre (démolition, construction, réfection de rue), et une
**phase**. Le reste en découle, et voici la seule idée qui compte :

⚠️ **Un chantier est une HORLOGE, pas un décor.** La partie compte les jours (`p.jour`) et
personne ne s'en sert pour changer la ville. Un chantier avance :

| Phase | Ce qu'on voit | Ce que ça change |
|---|---|---|
| 0 | la maison debout, des pancartes, des fenêtres placardées | la porte est condamnée |
| 1 | la **boule de démolition**, la moitié du mur par terre, la poussière | le bâtiment devient franchissable en partie |
| 2 | le terrain rasé, la **pelle** qui charge un camion, un tas de terre | un terrain vague… qui n'était pas là hier |
| 3 | la dalle, l'**échafaudage**, la **grue** qui tourne | on peut y grimper (la clôture s'enjambe déjà) |
| 4 | un bâtiment neuf, propre, une devanture qui n'existait pas | une porte de plus dans la ville |

Deux ou trois chantiers par partie, chacun avançant d'une phase tous les trois ou quatre
jours. Au bout d'une vingtaine de jours, **la ville n'est plus celle du premier matin** — et
c'est la seule façon honnête de faire sentir le temps dans un jeu où il ne se passe rien
entre deux missions.

**Les machines** — et ⚠️ **c'est là que le plan se mord la queue** : une pelle et une grue
sont des véhicules, et la fiche de la refonte des véhicules (plus haut) dit noir sur blanc
qu'on n'ajoute **aucun char** avant qu'elle soit faite. Deux étages, donc :

- **Étage 1, sans un seul véhicule neuf** : la pelle, la grue et la boule sont du **décor
  animé**. Elles ne roulent pas — elles **travaillent** : le bras de la pelle monte et
  descend, la flèche de la grue tourne lentement, la boule se balance et **casse ce qu'elle
  touche** (`endommagerDecor` existe). ⚠️ Une articulation, pas dix : le feu de circulation
  fait déjà exactement ça — un poteau cuit une fois, des lanternes peintes par-dessus à
  chaque image.
- **Étage 2, après la refonte** : la pelle se conduit. Et elle est drôle pour une raison
  précise, déjà écrite dans les fiches : `defonce`. Elle roule à 12 km/h et **passe à
  travers** ce qu'aucun autre char ne défonce. La grue, elle, ne roulera jamais — on monte
  dans la cabine, on tourne la flèche, et c'est tout ce qu'on lui demande.

**Le réservoir** (la phrase de Martin s'arrête sur « des… » : voici de quoi la finir). Chaque
idée porte ce qu'elle **fait**, parce qu'un chantier qui ne fait rien est un fond d'écran :

- **La boule de démolition** — elle se balance sur son câble, et ⚠️ **elle frappe pour vrai** :
  passer dessous en char, c'est un choc et une carcasse. Le seul décor du jeu qui attaque.
- **La grue à tour** — sa flèche tourne, son contrepoids suit, et elle se voit **de l'autre
  bout du district**. C'est un point de repère, donc un lieu de mission gratuit.
- **La pelle et le bulldozer** — le godet levé fait une **rampe** (les rampes sont livrées),
  et une pelle garée à côté d'un mur est une façon d'entrer dans une cour.
- **Le tas de terre ou de gravier** — une rampe naturelle, en plus doux. ⚠️ C'est le décor le
  plus rentable de la liste : il ne coûte qu'un dessin et il change la carte.
- **Le conteneur à déchets** — il se pousse (la physique des chars pousse déjà), donc il se
  place. Et il cache ce qu'on veut y cacher.
- **La tranchée et ses plaques d'acier** — rouler dessus **claque** : un son, une secousse, et
  la rue cesse d'être lisse.
- **L'échafaudage** et ses planches — on passe dessous, et la clôture orange qui le ceinture
  s'enjambe comme les autres.
- **La roulotte de chantier**, les **toilettes portatives** (le gag, et un abri d'une tuile),
  les **palettes de briques**, les **poutres d'acier**, le **rouleau compresseur**, la
  **bétonnière**, le **camion à benne** (⚠️ celui-là est un vrai véhicule : étage 2).
- **Le signaleur** — pancarte LENTEMENT d'un côté, ARRÊT de l'autre. ⚠️ C'est une **sorte de
  gens**, pas du décor : il va au réservoir de la fiche des sortes, et il fait ce que personne
  ne fait encore — **arrêter le trafic**, donc te bloquer, toi aussi.
- **L'ouvrier au marteau-piqueur** — il s'arrête quand tu t'approches et te regarde passer.
- **La maison condamnée** (planches en croix sur les fenêtres), **la façade seule** qu'on a
  gardée en démolissant le reste, **le trou de fondation** plein d'eau boueuse — ⚠️ de l'eau
  **basse**, exactement comme la piscine de banlieue : on y barbote, on ne s'y noie pas.
- **La rue neuve** : un carré d'asphalte plus noir que le reste, et des lignes fraîches. Ça ne
  fait rien du tout, et c'est ce qui rend le reste crédible.

**⚠️ Les cinq pièges, et ils sont tous du même genre : une ville qui change casse ce qui
comptait sur elle.**

1. ⚠️ **Jamais un lieu qui sert.** Aucun `SPECIAUX`, aucun commerce, aucune porte de donneur
   de mission ne passe en chantier — sinon on démolit la quincaillerie le jour où une mission
   y envoie. Les chantiers se tirent **parmi les parcelles qui ne portent rien**, et le juge
   le vérifie à chaque phase.
2. ⚠️ **Une porte en chantier ne mène nulle part.** Si un bâtiment est démoli, sa porte doit
   **disparaître** de `portes`, pas rester ouverte sur un intérieur qui flotte. Et en phase 4,
   la porte neuve doit avoir une pièce à la bonne taille — le correctif « une pièce plus
   grande que sa maison » est livré, il s'applique ici aussi.
3. ⚠️ **Les juges de géométrie se rejouent à CHAQUE phase**, pas seulement à la génération :
   un seul îlot marchable, aucune poche murée, les sentiers qui rejoignent la rue. C'est
   exactement ce que la tentative du trottoir a appris — neuf juges rougissent d'un coup quand
   la ville bouge, et c'est à ça qu'ils servent.
4. ⚠️ **Le cache de morceaux se vide au changement de JOUR**, jamais en pleine image : une
   phase qui avance change des tuiles, et recuire en plein jeu se voit. Le chemin existe (une
   clôture cassée oublie son morceau **et les huit voisins**) ; ici on l'appelle au matin,
   pendant le fondu qui existe déjà.
5. ⚠️ **La phase voyage dans la sauvegarde**, une ligne par chantier — et une vieille partie
   repart avec tout à zéro (`completer()` sait déjà faire ça). Sinon deux appareils voient deux
   villes différentes, et la fiche des sauvegardes sur le serveur devient un mensonge.

**Et ça s'entend.** Un chantier sans bruit n'existe pas : le marteau-piqueur, le godet qui
racle, et ⚠️ **le bip de recul** — c'est LE son d'un chantier, celui qu'on reconnaît sans
regarder. Trois échantillons, joués à la distance (`Son.jouerA` existe), et **ça se tait la
nuit**, sauf le chantier de nuit qui fait râler le quartier — une manchette pour le journal
de M15.

**Juges** : aucun chantier ne tombe sur un lieu spécial, un commerce ou une porte de donneur ;
à chaque phase, la ville garde un seul îlot marchable et aucune poche murée ; une porte
démolie disparaît de `portes` et une porte neuve a une pièce qui tient dans son bâtiment ; la
boule de démolition endommage ce qu'elle touche et rien d'autre ; le cache de morceaux ne se
vide qu'au changement de jour ; les phases sont dans la sauvegarde et une vieille partie
repart à zéro sans planter ; et le chantier se tait entre minuit et six heures.

## Notes

demande de Martin : « des maisons ou commerces ou des rues en construction, avec des pelles,
des boules de démolition, des grues ».

- ⚠️ Un chantier est une **horloge**, pas un décor : cinq phases (condamné → boule de
  démolition → terrain rasé → grue et échafaudage → bâtiment neuf), une phase tous les trois
  ou quatre jours, et au bout de vingt jours **la ville n'est plus celle du premier matin**.
  La pelle, la grue et la boule sont d'abord du **décor animé** (une articulation, comme les
  lanternes d'un feu) ⚠️ parce que la refonte des véhicules interdit d'ajouter un char avant
  elle ; conduisibles ensuite. Plus un réservoir : tas de terre qui fait rampe, conteneur
  qu'on pousse, plaques d'acier qui claquent, signaleur qui arrête le trafic, trou de
  fondation en eau basse

⚠️ **1re vague livrée le 16 sept. 2026 — l'horloge et les cinq phases.** Trois chantiers par
ville (`app/chantiers.py`), tirés dans **leur propre dé, après toute la ville** : un juge
compare la ville avec et sans chantiers, et pas un arbre ne bouge. Ils ne tombent que sur ce
qui ne SERT à rien — ni porte vers un intérieur, ni enseigne, ni point d'intérêt, ni
logement qu'on visite, ni cour de gang. Mesuré : **58 bâtiments sur 199** passent le filtre,
parce qu'une résidence sans intérieur n'est qu'une façade peinte — c'est-à-dire exactement
« la maison debout » de la phase 0. **Python calcule les tuiles des cinq phases** et toute
la géométrie s'y juge phase par phase : la ville reste d'un seul tenant à chaque phase de
chaque chantier, machines comptées comme des murs, et la démolition coupe **dans la
largeur** pour que la moitié debout garde ses façades (coupée dans la profondeur, on verrait
le dos d'un toit). Le neuf reprend exactement l'empreinte : toit plat de gravier, une porte
**peinte** et fermée, « À LOUER » — pas d'intérieur, donc pas de promesse. **Au premier
matin, les trois chantiers sont à des stades différents** (condamné, démolition, rasé) :
sinon il fallait trois jours de jeu avant la première machine. Une phase tous les trois ou
quatre jours, et au vingt et unième jour la ville est neuve. `static/js/chantiers.js`
**pose** la phase du jour, et ⚠️ **jamais sous les yeux ni sur quelqu'un** : elle attend que
le chantier soit hors de vue (la marge nord est plus haute, pour la flèche de la grue) et
que personne ne se tienne dans l'empreinte — le neuf remonte des murs là où l'on marchait la
veille. Ce qui appartenait à la maison tombe avec elle (façade de logement, équipement de
toit, tag, fenêtre allumée) ; les portes par où les gens rentrent chez eux suivent le sol ;
un objet par terre ressort devant la porte du neuf ; un joueur sauvegardé sur un terrain
devenu mur reparaît devant elle. Le cache ne se recuit **qu'autour** du chantier. La phase
voyage dans la sauvegarde par un seul nombre (`partie.chantiers.debut`) : deux appareils
voient la même ville, et une partie d'avant les chantiers repart de son propre jour. Les
machines sont du **décor animé** (`anime`) dans `DECORS` — la grue à boule qui se balance,
la pelle qui racle, le tas de terre, la grue à tour dont la flèche tourne en seize poses —
et elles **arrêtent** un char sans jamais tomber (le juge des décors les lit).

- ⚠️ Deux gardes que la graine livrée n'exerce jamais (une moitié démolie murée, une machine
  en travers d'un couloir) ont chacune leur carte écrite à la main : sans elle, on pouvait
  les retirer sans qu'aucun juge ne rougisse. **30 juges Python + 14 de banc, chaque règle
  vue rouge sans elle.**

⚠️ **2e vague livrée le 16 sept. 2026 — le chantier qui travaille** (Martin : « bar ouvert
pour ElevenLabs »). **La boule frappe pour vrai** : Python ne pose la grue à boule qu'à
**deux tuiles** de la moitié debout, tournée vers elle, avec du mur sur sa rangée ET sur
celle du dessus — la boule pend une tuile plus haut à l'écran (`chantiers.FRAPPE`,
`PORTEE_BOULE`). Mesuré sur sept graines : la place existe **364 fois sur 374** ; un
bâtiment qui ne l'a pas ne se démolit pas, donc la règle est toujours vraie et les trois
chantiers de la graine livrée n'ont pas bougé. La boule recule, part, cogne et rebondit
(seize poses) ; **au coup, son dernier pixel touche le premier pixel du mur** et à aucune
autre pose elle n'y entre — un juge le mesure des deux côtés, la grue tournée vers l'ouest
étant un **miroir** peint par `miroirX` (pas de `scale(-1, 1)` : le banc voit ce que voit le
navigateur). Au coup : le son, la poussière et les briques au bord du mur, la rue qui
tremble à deux pas, et le mur frappé porte un trou et ses fissures.

- ⚠️ Les éclats ne tirent pas `B.rng` (un coup toutes les 2,7 s décalerait tout ce que la
  ville tire au sort) — et le premier essai lisait `hash2` avec `>>` : l'entier sans signe
  relu signé envoyait la poussière **en colonne vers le ciel**, comme un feu (la capture l'a
  montré ; les gravats peints de la 1re vague avaient le même défaut). **Le chantier
  s'entend** : six sons ElevenLabs (neuf fichiers, 216 Ko) — la boule, le marteau-piqueur,
  le godet, le marteau, la scie circulaire et une **rumeur** de chantier en boucle dont le
  volume suit la distance. Chacun part d'un geste qu'on VOIT quand il y en a un (la boule à
  la première image de sa pose de coup, le godet quand la pelle racle) ; le reste revient
  sur une horloge.
- ⚠️ **Pas de bip de recul ElevenLabs** : trois générations (« evenly spaced beeps », puis
  les durées en toutes lettres, puis « dry, no reverb », à 1000 Hz) ont rendu trois
  **sifflements continus** — à l'enveloppe par tranches de 10 ms, pas un silence entre deux
  bips. Un bip de recul est un ton électronique : il est synthétisé, et chaque son garde son
  repli synthétisé (`REPLI_CHANTIER`). **Et il se tait la nuit** : les machines portent
  `travaille: 'jour'`, s'arrêtent à leur pose de repos (`Entites.poseDuDecor`, la même
  fonction pour le dessin et pour le coup), et plus un son ne part — ni dans une pièce. **La
  grue se voit de loin** : un décor sort de la liste de dessin par son DESSIN et non plus
  par son pied (la grue fait 112 px de large et monte à 90 px au-dessus de sa tuile ; la
  marge fixe la faisait surgir en montant la rue), et une phase attend aussi que la flèche
  d'une machine soit hors de l'écran. **6 juges de banc, 2 Python (5 cas) et 1 d'audio,
  chaque règle vue rouge sans elle (21 mutations).**
- ⚠️ À écouter par Martin : aucun juge ne dit qu'un son est le bon.

⚠️ **3e vague livrée le 20 sept. 2026 — la tranchée et l'équipe.** Un chantier qui travaille
sans un homme dessus est un décor, et il s'arrête net à sa palissade : la vague lui donne
**du monde** et **la rue d'en face**.

- ⚠️ **La tranchée** (`chantiers._tranchee`) : deux tuiles d'**asphalte nu** sous la façade, sur
  la première chaussée qui les offre (5 à 8 rangées plus bas sur la graine livrée), couvertes de
  **plaques d'acier** boulonnées au ruban jaune et noir tant qu'on travaille (phases 2 et 3),
  puis **rapiécées** — un carré plus sombre, joints scellés — quand le neuf est debout. Elle ne
  change **aucune tuile** : elle se peint et se sent, donc les juges de géométrie de chaque phase
  n'ont pas bougé d'une ligne. Jamais dans un croisement, sur une ligne d'arrêt, un nid, une
  entrave, une fermeture, un pont, une barrière, ni à trois tuiles d'un bris d'aqueduc — chaque
  exclusion a sa carte écrite à la main. **Facultative** : quand une fermeture couvre la rue
  d'en face (graines 7 et 2026, un chantier sur trois), le chantier n'en a pas et n'en est pas
  refusé ; le juge exige les trois de la graine livrée et deux sur trois ailleurs, pour qu'une
  règle qui ne trouve jamais rien ne passe pas inaperçue.
- ⚠️ **Elle claque** (`Vehicules.majPlaque`) : la roue avant, la plaque qui résonne, la roue
  arrière — un son **synthétisé** (`REPLI_CHANTIER.plaque`, pas de fichier : un cahot n'en a pas
  besoin), une secousse plus douce que le nid-de-poule (`plaque_secousse` 0,28 contre 0,35) et
  **aucun point de carrosserie** : un nid est un accident, une plaque est un décor qu'on sent.
  Même répit que les nids, rien à l'arrêt ni en l'air. **Le trafic claque aussi**, posé là où il
  roule et entendu à la distance — mais la caméra ne tremble que pour le char du joueur. L'index
  (`carte.plaques`) vit **sur la carte**, comme celui des nids : une porte franchie ne l'efface pas.
- ⚠️ **L'équipe** (`chantiers._postes`, `Entites.naitreLEquipe`) : personne sur la maison
  condamnée ni sur le neuf, **un homme** à la démolition, **deux** quand la pelle puis la grue
  travaillent. Python choisit les **postes** : une tuile du terrain libéré aux quatre voisines
  libres (jamais dans un couloir — un homme planté y ferait bouchon), à deux ou quatre tuiles de
  la machine, à deux tuiles l'un de l'autre. Ils naissent **hors de l'écran et dans la bulle**,
  intouchables comme les ouvriers de la voie fermée, **hors de la foule** (`metier`), plantés,
  et **regardent passer** : à moins de 90 px le visage vers le joueur, sinon vers leur machine. La
  nuit ils rentrent — hors de l'écran seulement. ⚠️ Ils portent `equipeDe` et `posteDe`, **pas**
  `chantier` : `naitreLesOuvriers` compte « qui travaille » avec `q.chantier`, et une équipe de
  chantier marquée pareil faisait ne plus naître celle de la voie fermée (le piège de la grue,
  déjà payé une fois). Et au changement de phase l'équipe d'hier **s'en va** : un poste pris par
  son homme reste « pris », il serait resté planté là où la grue se pose.
- ⚠️ **Leur propre dé, un par chantier** : les trois chantiers de la graine livrée sont restés
  où ils étaient, avec les mêmes machines et les mêmes tuiles — un juge rejoue `tirer` avec les
  annexes retirées et compare.
- ⚠️ **Deux juges verts qui ne mordaient pas**, trouvés à la mutation : le recuit du morceau de la
  tranchée (sur la graine livrée, elle tombe **toujours** dans le même morceau que la marge du
  bâtiment — le cache vidé par la marge cachait celui qu'on avait retiré : un cas synthétique, à
  32 tuiles de là, et un cache **rempli** avant de le vider) et « personne sur une maison
  condamnée » (le juge relisait la constante qu'on mutait). Et la tranchée, à cinq ou huit
  tuiles de la façade, n'est pas dans le rectangle que la phase attend hors de l'écran : elle a
  **son propre test** (`enVue`), et le juge met la caméra sur elle, l'immeuble au-dessus de
  l'écran.
- ⚠️ **Regardé dans Chromium avant de livrer** (les juges verts ont déjà laissé passer un
  damier) : la plaque se lit, le ruban aussi, les hommes en gilet orange entourent la pelle ; la
  rue rapiécée était trop noire — on aurait dit un trou — et a été éclaircie d'un cran.
- **16 juges Python + 8 de banc, 28 mutations, chaque règle vue rouge sans elle.** Restait : le
  signaleur (livré à la 4e vague), le conteneur qu'on pousse, le tas de terre qui fait rampe,
  de nouveaux chantiers quand les premiers sont finis ; et l'étage 2 — la pelle conduisible,
  après la refonte des véhicules. À écouter par Martin : le claquement de la plaque n'a pas de
  fichier ElevenLabs, et le filet synthétisé est ce qu'on entend.

⚠️ **4e vague livrée le 20 sept. 2026 — le signaleur qui arrête le trafic.** Sur le trottoir, au
bout amont de la tranchée, un homme tient une palette : ARRÊT (l'octogone rouge) trois
secondes, puis LENTEMENT (le losange orange) trois secondes. Le trafic de sa voie obéit — et la
file qui s'arrête devant lui est ce qui te bloque, toi aussi : le joueur, lui, peut passer, comme
devant un feu.

- ⚠️ **Il se tient sur le TROTTOIR, jamais dans la chaussée** : un homme planté dans la voie, le
  trafic le contourne (`changerDeVoie`), il ne l'écoute pas. Python le pose (`chantiers._signaleur`)
  sur la tuile au nord de la tranchée, **du bout d'où l'on vient** (à l'est d'une voie qui va vers
  l'ouest). Refusé — et le chantier n'en est pas refusé — sur une voie nord-sud, sur deux tuiles
  qui ne vont pas dans le même sens, sur un trottoir qui est une chaussée ou déjà pris par un
  meuble ; chaque refus a sa carte. **Il ne sert que pendant les plaques** (phases 2 et 3).
  Mesuré : les trois tranchées de la graine livrée en ont un, et tous sont à l'est d'une voie
  « < » — l'autre bout (voie « > ») n'est jugé que sur une carte écrite à la main.
- ⚠️ **Branché dans `obstacleDevant`, pas dans les feux** : la ligne d'arrêt du trafic est liée
  aux croisements (`attendFeu`, `prochaineCible`) et l'y greffer aurait touché la partie la plus
  jugée de la conduite. `Chantiers.signalDevant` rend la distance de son nez à l'homme quand la
  palette dit ARRÊT, sinon l'infini ; la conduite ordinaire fait le reste, **au même freinage que
  pour un piéton planté sur la voie**. Il ne parle qu'à SA voie (la rangée de la tranchée, dans son
  sens), à six tuiles au plus, pas à qui l'a déjà dépassé, **jamais à une poursuite ni à une
  rame**. Un vrai char de trafic est posé cinq tuiles derrière lui : il s'arrête sans jamais passer
  l'homme, sans forcer le passage, et repart au LENTEMENT.
- ⚠️ **Trois secondes d'ARRÊT, pas plus** : la patience du trafic est de 200 images (3,3 s), au-delà
  il force le passage. Un ARRÊT plus long ne serait pas obéi ; un juge compare les deux constantes
  (`anime` de la palette, `patience_images` de la fiche).
- ⚠️ **Une seule source : la POSE de la palette** (`Entites.poseDuDecor(f, t, false)`, comme
  `feuDeCirculation` pour un feu) décide à la fois du dessin et de l'obéissance. Sans `travaille`,
  donc **jamais de pose de repos la nuit** : le premier essai en avait une, et un homme resté à
  l'écran à la tombée du jour aurait montré ARRÊT pendant que le trafic passait. (Aucun juge ne le
  voyait : la mutation, oui.) Un juge lit les deux poses la nuit.
- ⚠️ **La palette naît et rentre avec son homme**, jamais seule sur le trottoir : posée dans sa
  main à sa naissance, retirée quand il rentre la nuit, quand la phase change, ou quand la
  distance l'oublie. Son poste s'appelle `'signal'` (`posteDe`), pas un numéro : sinon il se
  confondait avec le poste 0 de l'équipe du terrain et ne naissait pas. Il naît hors de l'écran,
  intouchable, hors de la foule, tourné vers la route — les mêmes règles que l'équipe.
- ⚠️ **Le paquet de la carte est à SEC** : `test_le_paquet_reste_leger` a rougi (48 045 octets
  gzip pour un plafond de 48 000 ; la base en pesait 47 976). Le signaleur voyageait avec un
  drapeau par phase et une clé par champ ; il ne voyage plus que sa tuile `[x, y]` — la voie est
  la rangée dessous, son sens se lit sur le calque `voie`, et « sert pendant les plaques » se lit
  dans `tranchee` de la phase, qui y est déjà. Résultat : **47 999 octets, un de marge**. Le
  prochain ajout à la carte, de n'importe quelle session, doit se serrer de même ou relever le
  plafond (`test_definitions`) en le disant — c'est le budget de Martin, je n'y ai pas touché.
- ⚠️ **Regardé dans Chromium** : l'octogone se lit dans sa main, deux chars s'arrêtent en file
  avant la plaque ; au LENTEMENT le losange orange et la file repart.
- **9 juges Python + 3 de banc (dont un char de trafic qui s'arrête et repart), 21 mutations, chaque
  règle vue rouge sans elle.** Reste : le conteneur qu'on pousse, le tas de terre qui fait
  rampe, de nouveaux chantiers quand les premiers sont finis ; et l'étage 2 — la pelle
  conduisible, après la refonte des véhicules.

⚠️ **5e vague livrée le 21 sept. 2026 — le tas de terre fait rampe.** Le tas de la phase « rasé »,
à côté de la pelle, n'arrête plus personne : un char qui roule dessus **décolle**, doucement,
et retombe plus loin sans avoir rien perdu.

- ⚠️ **Ni un mur ni un obstacle qui cède** : `Vehicules.decorDevant` ignore toute fiche qui déclare
  `rampe` (le rayon, en px, où les roues sentent le tas). Avant, la berline butait sur le tas
  (masse 1,0 < `arrete` 3,0) et l'autobus le **déracinait** (3,2 ≥ 3,0). `arrete` ne sert plus qu'aux
  balles — la fiche le garde pour ça.
- ⚠️ **Plafonné, pas mesuré** : contrairement aux rampes des défis (élan, portée et freinage calculés
  pour chaque char), le saut du tas est borné d'avance — `tas_impulsion` 0,38, vitesse comptée
  jusqu'à 4, jamais plus haut que `tas_hauteur_max` = **6 px**, le seuil au-delà duquel un char passe
  AU-DESSUS des tuiles (`v.z > 6`). Un mur retient donc toujours ce qui retombe, et un tas au bord
  d'un lot ne lance personne dans une façade. **Le juge de banc a attrapé ma première valeur** : à
  0,42 la moto montait à 6,3 px, parce que l'intégration est discrète (`z += vz ; vz -= g` monte de
  `vz / 2` de plus que la formule continue) et que mon juge Python l'avait calculée en continu. Il
  **rejoue maintenant le saut** image par image, comme `majPhysique`.
- Même répit que les nids (30 images) ; sous 1,2 px/image on monte dessus sans décoller ; ni vitesse
  ni carrosserie perdues ; de la poussière au départ, une secousse plus douce que celle d'une plaque
  (0,18), un son synthétisé — un coup sourd, du gravier, un atterrissage mou.
- **1 juge Python + 3 de banc, 7 mutations, chaque règle vue rouge sans elle.**

⚠️ **6e vague livrée le 21 sept. 2026 — la benne qu'on pousse.** Devant chaque chantier, du début de
la démolition à la dalle, une **benne à gravats** verte au ruban jaune et noir que les chars
**poussent** : elle avance sous une berline lancée dessus, la ralentit, et s'arrête à sa portée ou
au premier mur.

- ⚠️ **Elle ne bouge que d'une fraction de tuile** : `portee` 24 px de chez elle (`d.chez`), moins
  que le bloc de sol libre que Python lui garantit — cinq tuiles de large, trois de profondeur, tout
  de l'espace piéton, milieu compris. Poussée au bout, sa boîte reste dans le bloc. À chaque phase
  elle est retirée et **reposée chez elle** (elle ne se tient pas dans `machines`, la pelle ne
  travaille pas avec elle) ; ni sur la maison condamnée ni sur le neuf.
- ⚠️ **Le décor ne bougeait JAMAIS** : l'index fixe était bâti une fois. `Entites.pousserDecor` est
  le seul à le faire bouger, et il tient l'index à jour LUI-MÊME — sans quoi les piétons buteraient
  sur l'endroit qu'elle a quitté. Les chars la sentent par sa **boîte** (`sol`), pas par un cercle.
- ⚠️ **Elle se paie à la masse** : `poussee_frein` x la masse de la benne / celle du char, borné par
  `poussee_frein_max`. `decorDevant` sortait tout de suite pour un char lent (< 1 px/image), or la
  poussée ralentit sous ce seuil : la poussée passe avant ce raccourci.
- ⚠️ **Le parcmètre dans le bloc, et ce qu'il disait des vagues d'avant.** Le mobilier de rue, les
  abribus et la saleté sont posés APRÈS `tirer` et ne retirent rien aux chantiers : un parcmètre est
  tombé dans le bloc d'une benne, et la tranchée du premier chantier de la graine livrée **était
  déjà sur quelque chose** — les juges des 3e et 4e vagues passaient sur leurs quatre graines par
  chance. Les annexes (tranchée, équipe, signaleur, benne) se calculent maintenant dans
  `chantiers.completer`, appelée **tout à la fin de `carte.generer`**, sur la ville finie.
- **11 juges Python + 8 de banc, 22 mutations, chaque règle vue rouge sans elle.**

⚠️ **7e vague livrée le 21 sept. 2026 — de nouveaux chantiers quand les premiers sont finis.** Au
vingtième jour, la ville ne s'arrête plus de changer : trois chantiers **dorment** au premier matin
(la maison reste telle quelle) et ouvrent à mesure que les premiers finissent — aux jours 8, 13 et 18
— pour finir au plus tard au trente-quatrième.

- ⚠️ **Six chantiers par ville, jamais plus de trois qui travaillent à la fois** : `OUVERTS` = 3 (ceux
  d'avant, inchangés), `NOMBRE` = 6. Un chantier **DORMANT** est une maison : `phase_du_jour` rend
  `DORMANT` (-1) avant son jour, la ville est celle du générateur, et le jeu ne pose rien. Il s'éveille
  hors de vue, comme toute autre phase.
- ⚠️ **Le piège du -1** : `phases[-1]` est le **NEUF**. `appliquer` (Python) lisait un dormant comme
  le dernier indice de la liste — la mutation « appliquer(-1) lit le neuf » le montre.
- ⚠️ **Un couplage vieux de la 3e vague, vu à l'atterrissage** : les postes de l'équipe partageaient
  le dé de la tranchée, qui tire UNE fois quand elle trouve une place et PAS DU TOUT sinon — un
  meuble sur la rue d'en face changeait donc les ouvriers du TERRAIN. Ils ont leur dé.
- **9 juges Python + 2 de banc, 14 mutations, chaque règle vue rouge sans elle.**

⚠️ **8e et 9e vagues livrées le 21 sept. 2026 — la pelle et la grue qu'on conduit (l'étage 2).** La
refonte des véhicules était livrée entre-temps par une autre session : rien n'interdisait plus
d'ajouter un char. Devant la pelle qui travaille, l'invite dit **MONTER : PELLETEUSE** ; devant la
grue, **MONTER : GRUE**.

- ⚠️ **La pelle sort de son décor, elle ne naît pas dans la rue** (`frequence` 0). Monter la retire du
  chantier (le godet ne racle plus) et un vrai char naît à sa place — voler la pelle est un délit,
  l'équipe plantée autour est témoin. Le seuil de vitesse pour défoncer une clôture se règle sur SA
  vitesse (trois quarts de la vitesse max) : à 1,4 fixe, jamais assez vite pour ses 12 km/h.
- ⚠️ **La grue ne roule pas : c'est un MODE**, pas un char. `j.manege` (le nom que la foire utilise
  déjà) porte la cabine ; gauche et droite tournent la flèche (le stick dose la vitesse), ACTION
  redescend. `Foire.majPassager` éjectait aussitôt quiconque n'était pas dans un de SES manèges —
  une garde la laisse tranquille. La grue prend la pose qu'on lui donne tant qu'on la pilote, et
  **reprend son travail** dès qu'on redescend, y compris si le pilote disparaît par un autre chemin
  (la mort, une pièce).
- **12 juges de banc, 28 mutations, chaque règle vue rouge sans elle.**

⚠️ **L'atterrissage sur `dev`, après un redémarrage** (21 sept. 2026 au soir) — les cinq derniers
commits de cette fiche n'existaient que sur `origin/dev`, qui porte l'ancien plan monolithique ; le
`dev` local, fragmenté depuis, avait continué sans eux (véhicules lourds qui atteignent leur vitesse,
phares par classe, virages en L, cabriolet, chalutier, porte-conteneurs, aéroport, M15…). Réconcilié
à trois voies (base commune, mes 5 commits, `dev` courant) sur chaque fichier touché des deux côtés :
zéro conflit textuel sur `entites.js`, `sprites.js`, `missions.js`, `son.js` et `app/vehicules.py`
malgré des centaines de lignes ajoutées de chaque bord ; trois petits (une liste d'export dans
`vehicules.js`, un import, un ensemble de slugs) résolus à la main.

- ⚠️ **Deux prétentions à des records, fausses une fois le parc au complet** : « la pelle est le char
  le plus lourd » ne tenait plus devant le porte-conteneurs (masse 12, mais hors trafic — `eau`) ; « la
  pelle est le char le plus large » pareil (elle a été resserrée à 16 px, comme le camion, plus tôt
  dans la même journée, pour ne pas frôler un bac d'éboueur). Les deux juges se limitent maintenant
  À LA RUE. Le porte-conteneurs, lui, se disait « le plus lent » dans l'inventaire — plus vrai depuis
  que la pelle existe (1,3 contre 1,9) : corrigé.
- ⚠️ **Une pelle à 12 km/h « distance un agent à pied » selon un juge écrit avant elle.** Elle roule
  sous la vitesse minimale que ce juge exige de tout ce qui a un moteur — et c'est voulu, pas un bug :
  on ne vole pas une pelleteuse pour fuir la police, on la vole pour la farce, et un agent qui la
  rattrape à la course est le gag. Exemptée avec sa raison écrite dans le juge, pas désarmée en
  silence.
- ⚠️ **Le budget des définitions était déjà rouge avant que j'y touche** — 202 902 octets bruts pour
  un plafond de 200 000 (45 796 gzip pour 44 000), le temps que d'autres sessions ajoutent du contenu
  pendant que ce plafond dormait. La pelleteuse du catalogue y ajoute 794 octets bruts et 111 gzip.
  Plafond relevé à 215 000 / 48 000. Le budget de la carte, lui, avait encore de la marge : les six
  chantiers (contre trois) et leurs annexes ajoutent 3 209 octets bruts et 451 gzip, sans toucher au
  plafond fixé par l'aéroport la même journée.
- Les annexes des chantiers (tranchée, équipe, signaleur, benne) se calculent maintenant tout à la
  toute fin de `carte.generer`, après l'aéroport et les grands bateaux — pas seulement après le
  mobilier de rue : rien de plus récent ne doit leur retirer une tuile.
- ⚠️ **La benne posée au démarrage décalait des identifiants d'entités, et ça a fait rougir un juge
  de policiers.** `poserLaBenne` naissait dans `poserLesMachines` (donc dès `appliquer`, au tout
  premier chargement pour chaque chantier « ouvert » — visité ou non). Or `police.js` étale ses
  vérifications de vue sur `(B.t + a.id) % N` (le budget d'un agent, pas du hasard) : les quelques
  identifiants de plus décalaient le cran auquel un agent perd de vue le fuyard, retardant son
  abandon de poursuite (image ~400, puis 1419 avec les bennes en plus) — assez pour qu'un juge à
  cadence fixe (`test_deux_dehors_l_auto_reste_immobile_jusqu_a_ce_qu_un_agent_reprenne_le_volant`,
  800 images) le rate. Élargir la cadence du juge a masqué le symptôme et en a montré un pire
  (l'agent, parti bien plus loin, se perdait en revenant) — pas la bonne piste. La benne est passée
  en pose PARESSEUSE, exactement comme l'équipe et le signaleur : `poserLaBenneSiBesoin`, appelée
  par `equiper()`, gardée par la même bulle (`Entites.BULLE_OUBLI`) et `visibleAEcran`. Cohérent
  avec « jamais sous les yeux », et corrige la cause plutôt que la tolérance du juge — celui-ci
  repasse tel quel, inchangé, à sa cadence d'origine. Les cinq juges de banc qui posaient la benne
  directement (`appliquerSeule` et un test à sa propre boucle) ont dû apprendre à poser le joueur
  dans la bulle et appeler `equiper()`, comme tout juge d'équipe le fait déjà.
- ⚠️ **La pelleteuse allumait 9 lampes pour une place gardée de 7** (`LAMPES_PAR_CHAR_MAX`,
  `vehicules.js`) : quatre feux arrière sur le contrepoids (deux hauteurs empilées de chaque côté),
  en plus des quatre phares et du faisceau du camion. Les deux paires empilées fusionnées en un
  seul bloc par côté (même portée verticale, une seule lueur) : six lampes + le faisceau = sept,
  pile la place gardée — `test_chaque_char_du_parc_allume_les_lampes_que_sa_machine_peint` le dit.

**Le jalon est livré au complet.** Les deux étages du plan sont faits (le décor animé, puis les
chars qu'on conduit) ; ce qui reste du réservoir d'origine — le rouleau compresseur, la bétonnière,
la roulotte de chantier, les toilettes portatives, le camion à benne — est resté au stade de
brainstorm dans la Fiche : jamais promis comme livrable, à reprendre si Martin en veut un jour.
