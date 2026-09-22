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
