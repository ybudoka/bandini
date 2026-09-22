# Les courses : suivre les flèches, un tour par quartier

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « pour les courses, il faut un nouveau concept de flèches
lumineuses sur la route qui trace le chemin de la course, pas des flèches avec les mètres. » Puis
(22 sept. 2026) : « je veux une side quest de course par secteur » — un **défi** par quartier, comme
le Tour du Faubourg (panneau, chrono, prime, aucun dialogue), les quatre d'un coup — et « pas besoin
de point de passage, on doit suivre les flèches lumineuses au sol. Si on quitte, on a 5 sec pour
revenir ou on doit recommencer. »

**Première vague — les flèches au sol.** Un second A*, qui ne connaît que la chaussée
(`Monde.cheminRoute`) : le tracé d'une course suit la route, jamais une ligne à vol d'oiseau. Des
flèches qui pulsent, posées sur la chaussée devant le char (`Histoire.dessinerCheminCourse`). Et la
flèche-avec-les-mètres du GPS se tait pendant une course : le tracé la remplace.

**Deuxième vague — un circuit, et un tour par quartier.** Une course n'est plus une suite de points de
passage à toucher : c'est un **circuit fermé**, calculé une fois au départ sur la chaussée, et on le
suit. Hors du tracé, un compte de 5 s part ; revenir l'annule, au bout la course est ratée (on
recommence au panneau). Quatre défis de plus : le Tour des Érables (panneau au dépanneur), de la Shop
(à la fourrière), des Quais (à l'hôtel), de la Pointe (au phare) ; trois tours chacun, prime de 250 $.
Leur circuit se tire du rectangle du quartier (`carte.zones`) : le bâtiment du panneau, puis trois
coins rentrés, dans l'ordre du tour. Le Tour du Faubourg passe à la même règle ; ses quatre bâtiments
restent son circuit.

- ⚠️ Le circuit est **fixe** : un tracé qui se recalculerait depuis le char suivrait le joueur partout,
  et on ne pourrait jamais en sortir. La progression se lit sur le tracé lui-même, dans une fenêtre
  autour du dernier point atteint — couper par une ruelle vers un autre bout du circuit, c'est sortir.
- ⚠️ Le chrono part **sur la ligne de départ**, pas au volant : le char pris au panneau est garé où il
  est garé, et le rejoindre ne se chronomètre pas.
- ⚠️ Aucun dé : le circuit ne dépend que de la carte. Les quatre bâtiments des panneaux sont déjà des
  lieux de mission (`devants.lieux_de_mission`) — les défis ne déplacent rien devant une porte. Pas
  l'usine, qui a sa barrière d'heures.
- ⚠️ Les chronos se calent sur le Tour du Faubourg : la même vitesse moyenne exigée sur la longueur
  mesurée de chaque circuit, pas une règle de trois sur la surface du quartier.

## Notes

**Livré le 22 sept. 2026 — les deux vagues d'un coup.** `Monde.cheminRoute` (un A* sur la seule
chaussée, un vrai tas, qui roule à droite et tourne le moins possible) ; `Histoire.circuit` tire le
circuit au panneau ; `majCircuit` le fait suivre ; `dessinerCheminCourse` peint les flèches au sol
(un halo, un trait, la lumière qui court vers l'avant) et `lampesDeCourse` les allume la nuit. Le
GPS (`hud.js`) garde sa flèche-et-mètres pour rejoindre la ligne de départ, et la tait sur la piste.

Les cinq circuits, mesurés au banc : Faubourg 412 points (de 16 px), Érables 306, Shop 380, Quais
392, Pointe 366 — tous 100 % sur la chaussée et 100 % dans leur quartier, tirés en moins de 3 ms.
L'étalon est le Tour du Faubourg (3 tours en 2:00, ≈ 165 px/s, 69 % de la vitesse d'une berline) ;
les autres exigent la même vitesse, arrondie en faveur du joueur : Érables 1:30, Shop 1:55, Quais
1:55, Pointe 1:50.

- ⚠️ **La cour de la fourrière et celle de l'usine sont de la chaussée SANS VOIE** (`.`), et elles
  ne touchent aucune rue : un circuit de la Shop tiré depuis la porte de la fourrière n'avait pas un
  seul tronçon. Les ancres se posent sur une vraie rue (`estVoie` : une voie, un sens) ; la ligne de
  départ de la Shop est donc à 13 tuiles de son panneau, les autres à 2-5.
- ⚠️ **Peintes au sol, les flèches s'éteignaient la nuit** avec la ville (`Base.fin` assombrit tout
  ce qui est peint avant elle) : on ne les voyait plus que dans ses phares. Vu à la capture, pas par
  un juge. Chacune pose maintenant sa lampe, poussée après les phares (si l'écran dépasse
  `LAMPES_MAX`, ce sont elles qui sautent, pas un lampadaire).
- ⚠️ Le Tour du Faubourg change de règle : plus de bâtiments à toucher dans l'ordre (5 tuiles de
  rayon, qu'on pouvait couper par un parc), un circuit par ses quatre bâtiments, qu'on suit.
- ⚠️ Au banc, `proposerDefi` + `items[0].faire()` laisse le menu ouvert — et un menu ouvert fige la
  ville : `majDefi` ne tournait jamais. Les juges ferment le menu (`Hud.fermerMenu`).
- ⚠️ Le premier juge du hors-piste posait le char « à côté » de la piste de la Pointe… dans la baie :
  le char coulait et la course se ratait « sans char ». Le juge choisit maintenant une rue.
- ⚠️ Deux juges d'autres jalons figeaient ce qui change : `test_les_defis_ont_un_panneau_et_un_chrono`
  (trois panneaux, il y en a sept) et `test_un_grand_se_fait_bronzer_sur_une_serviette_libre`. Celui-là
  prenait « le premier grand venu » ; quatre panneaux de plus décalent l'ordre des entités, et le premier
  devenait un nageur à 227 px, en pleine eau — 20 graines sur 40 rouges contre 0 sur la base. Ce que le
  juge juge, c'est RESTER sur sa serviette (il le dit) : il prend maintenant le grand le plus près d'une
  serviette libre, et tient sur les 40 graines des deux côtés.
- Juges : `tests/test_course_js.py` (sept) ; chacun rougit quand on retire sa règle (compte hors
  piste, GPS qui se tait, ancre sur une voie, contre-sens, ligne de départ, tour complet, circuit au
  panneau). `test_missions.py` compte dix défis, dont une course par quartier.
