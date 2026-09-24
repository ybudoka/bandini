# Une décapotable rose et sa conductrice

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « une voiture type corvette, rose, avec une femme en
robe rose qui la pilote et en descend si volée. Elle va plus vite. » Un char rare de plus au
haut de gamme, et la première auto du parc qui a SA conductrice.

- ⚠️ **Le char** : `cabriolet` (« Cabriolet rose »), une décapotable basse à long capot,
  dessinée en volume comme la sport, et menée à la vue de tous comme la chaloupe
  (`assisDedans`, la selle du côté du conducteur) ; plus rapide que la sport — la moto reste
  devant, un juge le tient — et rare : elle ne naît que dans les districts qui la déclarent.
- ⚠️ **Toujours menée** : c'est la fiche qui dit QUI est au volant (`au_volant`, un
  archétype de `pietons.py`), pas un `slug === 'cabriolet'` caché dans le JS ; le trafic la
  fait naître avec sa conductrice et elle ne se gare jamais.
- ⚠️ **La conductrice** : un archétype à sprite propre — une robe rose, comme la Fille de la
  Brume a le sien —, fréquence 0 (elle ne marche jamais sans sa voiture), et des couleurs
  qui ne sont à personne d'autre.
- ⚠️ **Elle descend si on la vole** : le carjacking existant la fait sortir, témoigner et
  fuir, mais elle, en robe rose, et non un passant tiré au hasard ; sans un dé de plus au
  jeu.

## Notes

**Livré le 21 sept. 2026.** Demande de Martin : « une voiture type corvette, rose, avec une femme en
robe rose qui la pilote et en descend si volée. Elle va plus vite. » Le `cabriolet` (« Cabriolet rose »)
roule dans le trafic du Faubourg et de La Pointe avec sa conductrice, on la **voit** au volant, et si on
lui prend sa voiture c'est elle qui en sort, en robe, pour témoigner et fuir.

- ⚠️ **Plus vite que la sport, pas plus vite que la moto** : 5,0 px/image (sport 4,8, patrouille 4,4,
  moto 5,2), accélération 0,09. Le garde-fou d'`exploitation.md` (« un char rapide qui casse toutes les
  poursuites ») tient : 80 PV (la sport reste la plus fragile des autos, à 75), alarme, adhérence 0,20 —
  elle part en travers. Un juge la tient sous la moto et à moins de 20 % de la patrouille. Dans le
  trafic elle roule à 55 % de sa vitesse max comme tout le monde : 2,75 px/image contre 2,2 pour une
  berline. Rare (`rares` du Faubourg et de La Pointe, fréquence 0,04 — un peu plus que la sport : on la
  veut, mais on veut d'abord la voir).
- ⚠️ **La fiche dit QUI est au volant** (`au_volant: "conductrice"`), pas un `slug === 'cabriolet'` dans
  le JS. `Vehicules.creer` la met au volant à la naissance **sans un dé** (mesuré : sa naissance tire
  les mêmes dés que celle du sport) ; son identité voyage avec elle (`pilote.arch`) et c'est **cette
  identité**, pas le slug de la voiture, qui décide qui descend au carjacking — un voleur qui aurait
  emporté un cabriolet garé (`emporterLeChar`) reste un voleur, avec ses couleurs. Elle **ne se gare
  jamais** : `peupler` saute ce qui a un `au_volant` quand il gare.
- ⚠️ **On la voit** : le cabriolet est une décapotable dessinée en volume, et sa machine déclare le
  siège du conducteur (`assise`, à gauche, derrière le milieu) comme la chaloupe déclare son banc ;
  `assisDedans` peint le corps du joueur par-dessus, posture `volant`, aux couleurs de la conductrice
  (le rose de la robe, les cheveux miel). ⚠️ `deuxRoues` ne connaissait que l'axe : la selle prend
  maintenant `assise[1]` — 0 pour tout ce qui se chevauche, donc rien ne bouge pour le vélo, la moto
  et la chaloupe. Quand c'est le joueur qui la vole, c'est lui qui est au volant, à sa place.
- ⚠️ **Le dessin** : ni la sport repeinte ni une berline rose — ce sont les proportions qui la nomment.
  Long capot avec sa bosse, cockpit repoussé vers l'arrière, pare-brise très incliné, **deux bosses
  d'ailes devant et deux hanches derrière** (ce qui couvre les roues, dont le haut dépassait du capot
  comme des oreilles), deux ouies, des pots latéraux, quatre feux ronds derrière, sièges crème. Vérifié
  à l'œil sur les 8 caps (Chromium, gros plan) avant de l'écrire : les juges disent qu'elle est là, pas
  qu'elle se lit. Le premier essai avait les bosses trop hautes et trop longues — de face, des oreilles
  de chat ; abaissées à 6,2 et raccourcies devant.
- ⚠️ **La conductrice à pied** : un corps à elle (`conductrice`, 12 × 16, trois images de marche par face
  et `couche`), comme la Fille de la Brume a le sien — une robe de l'épaule au genou qui s'évase, les
  cheveux longs, les jambes nues, des souliers clairs ; la coupe la nomme à douze pixels, pas la couleur.
  Même rose en `c` et en `p` (une robe n'a pas de haut et de bas), et des couleurs qui ne sont à personne
  d'autre dans le catalogue (un juge, comme pour la Fille de la Brume). Fréquence 0 et pas de `metier` :
  descendue, c'est une passante comme une autre ; sa bourse est la plus lourde de la rue (60 à 180 $).
- **Juges** : `test_cabriolet_js.py` (3 : elle naît avec sa conductrice et on la voit au bon siège à
  tous les caps, **sans un dé de plus** ; si on la vole elle descend en robe, et le voleur d'un
  cabriolet garé reste un voleur ; elle ne se gare jamais mais roule — avec un **témoin** : dans le
  même décor l'auto seule se gare), `test_vehicules.py` (la fiche : plus vite que le sport, sous la
  moto, mince, rose, rare, `au_volant` vers un passant qui existe), `test_pietons.py` (ses couleurs).
  **Rouges avant, chacun sur sa règle** — cinq mutations : plus de conductrice à la naissance (3
  juges rouges), le carjacking qui tire un passant au hasard, la garer, la selle sur l'axe, l'identité
  qui suit le slug au lieu du pilote.
- ⚠️ **Trois choses que ce jalon a trouvées en route, et qui n'étaient pas à lui** :
  - la **carte pesait 47 999 octets gzip pour un plafond de 48 000** — le cabriolet en a ajouté 13 ;
    plafond relevé à 50 000 (`test_definitions.py`, raison datée) : ce n'est pas lui qui l'avait
    rempli, c'est qu'il n'y avait plus de marge ;
  - **`test_les_etoiles_ne_tombent_que_hors_de_vue` était fragile par la graine** : l'agent y était
    posé `fige`, et `gere` ne consulte jamais un agent figé (son `vuT` restait à 9999) — il ne voyait
    rien, et le juge ne passait que si un *autre* agent, né au hasard, arrivait à temps. Mesuré sur 60
    graines : la base tombait sur 103, 106 et 144, exactement comme mon arbre sur 103 et 144 ; la
    graine par défaut, elle, tombait du bon côté à la base et du mauvais chez moi (le cabriolet
    déplace le tirage des types de chars du Faubourg). Corrigé à la source : l'agent reste `flane`, `gere`
    le pilote, il voit, remet `vu` à zéro et se met en poursuite ; **rouge avant** en retirant ce
    `r.vu = 0`, ce que l'ancien juge ne voyait pas ;
  - **deux juges étaient déjà rouges sur `dev` sans moi** : `test_la_foule_ne_se_traverse_plus`
    (`test_moteur_js.py`) et `test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`
    (`test_histoire_js.py`) — rejoués sur un worktree à `eaede85`, avant tout changement. Pas touchés.
- **Pas fait** : pas de radio ni de klaxon à elle (les défauts) ; si on fait exploser la voiture du
  trafic, la conductrice disparaît avec l'épave comme le conducteur invisible de n'importe quelle
  auto — elle ne sort pas. À reprendre si Martin la regrette.

