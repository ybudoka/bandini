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
- **16 juges Python + 8 de banc, 28 mutations, chaque règle vue rouge sans elle.** Reste : le
  signaleur (LENTEMENT d'un côté, ARRÊT de l'autre — une sorte de gens qui **arrête le trafic**,
  toi aussi), le conteneur qu'on pousse, le tas de terre qui fait rampe, de nouveaux chantiers
  quand les premiers sont finis ; et l'étage 2 — la pelle conduisible, après la refonte des
  véhicules. À écouter par Martin : le claquement de la plaque n'a pas de fichier ElevenLabs,
  et le filet synthétisé est ce qu'on entend.
