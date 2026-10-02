# S'asseoir, attendre, se coucher

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (2 oct. 2026) : « il faut pouvoir s'asseoir sur les sofas et se coucher
dans les lits avant de dormir ; s'asseoir doit aussi permettre d'attendre quelques heures ».
Vague 1 — s'asseoir dedans et se coucher : les chaises (h) et la chaise berçante (V) de
toutes les pièces, le sofa à carreaux de la planque (tourné vers la télé), et les sofas des
déménagements sur le trottoir ; jamais une chaise déjà prise ; les refus du banc (police,
saigne) ; le stick lève sur un plancher libre à côté. Les lits À TOI seulement (planque de
Rocco, chambre de l'hôtel, phare, chalet du rang une fois acheté) : ACTION couche dans le
lit (la pose du lit d'hôpital), puis le menu DORMIR JUSQU'AU MATIN · JUSQU'AU SOIR ·
SAUVEGARDER · SE LEVER ; on se réveille couché, le stick lève. Vague 2 — attendre, accéléré
sous tes yeux : assis, ACTION ouvre ATTENDRE 1 H · 2 H · 3 H · SE LEVER ; l'horloge file (≈
1 h toutes les 2 s) et la ville tourne plus vite (plusieurs pas de simulation par image,
plafonnés par un budget de millisecondes) ; bandeau ATTENTE et l'heure ; s'arrête à l'heure
voulue, au stick, à un coup, à une étoile ; minuit passé = un vrai jour ; refusé avec la
police, en défi, frénésie, boulot ou chrono de mission ; pas de sauvegarde. Juges : un banc
Node (chaise, sofa, ATTENDRE 2 H, le coup qui coupe, le lever, le lit puis DORMIR) et une
capture Chromium des trois poses.

## Notes

**Vague 1 livrée (2 oct. 2026) — s'asseoir dedans, et se coucher avant de dormir.** Un module neuf,
`static/js/repos.js` (`Repos`), qui ne dit que OÙ : le corps est celui du banc (`Interactions.asseoirA`,
extrait de `sAsseoir`) et celui du lit d'hôpital (`Entites.coucher`, `seLever`).

- **Les sièges du dedans** (`interactions.ASSEOIR["dedans"]`) : la chaise `h` et la berçante `V` (la tuile
  collée droit devant, pose `assis_bas`, les pieds au bord de l'assise comme le patient), et le sofa à
  carreaux de la planque et du chalet (pose `assis_haut`, face à la télé, dessiné derrière son dossier). Une
  chaise prise (le patient, l'avocat, un passant planté) ne s'offre pas ; les refus du banc (police, saigne).
- ⚠️ **Le siège contre le point** : un comptoir attrape ACTION dans 1,6 tuile autour, une chaise se prend
  collée. `Repos.siegeAvantLePoint` donne le geste au plus PROCHE (à égalité, le point) — l'invite et
  `Missions.utiliserPoint` lisent la même fonction : à la planque, la chaise contre la table n'est plus
  volée par le catalogue.
- ⚠️ **L'assis tient dans SA pièce** : `majAssis` levait quiconque était dedans (`B.interieur`) ; il retient
  maintenant la pièce où l'on s'est assis (`assis.piece`), et en lève ailleurs.
- **Le lit à soi** (le point `lit` : planque, chambre de l'hôtel, phare, chalet acheté) couche au milieu
  de ses deux places, la tête sur l'oreiller, puis ouvre son menu, SE LEVER au bout. Fermé, on reste
  couché ; ACTION le rouvre (`Repos.majCouche`, et `utiliserPoint` couché) ; on se réveille couché.
- ⚠️ **Se lever d'un lit de deux places** : `Entites.seLever` ne cherchait que le pied de la colonne de
  tête et ses deux flancs — au chalet, le classeur bouche ce pied, et la colonne de droite est encore du
  lit : on restait debout SUR le lit. Il cherche tout le tour du lit.
- Laissés : les sofas des déménagements, peints sur le trottoir un jour par année, ni entité ni obstacle.
- Juges : `tests/test_repos_js.py` (six, au bouton ; chaque règle mutée les fait rougir) ; capture
  Chromium des trois poses (chaise, sofa, lit).

**Vague 2 livrée (2 oct. 2026) — attendre, assis, en accéléré sous tes yeux.** Assis (un banc, une chaise, la
berçante, le sofa), ACTION ouvre le menu de l'assis : ATTENDRE 1 H · 2 H · 3 H (l'heure d'arrivée en regard) et
SE LEVER ; le stick lève toujours d'un coup. Les nombres sont dans `interactions.ATTENDRE`.

- **Le temps file, il ne saute pas** : la ville fait `vitesse` (4) pas de simulation par image
  (`Repos.accelerer`, appelé par `Jeu.avancer` après les pas ordinaires — le même `maj`, plus souvent), plafonnés
  à `budget_ms` (8 ms) par image ; l'horloge avance d'une heure en `secondes_par_heure` (2) secondes
  (`Repos.majAttente`, lue par `Monde.majHeure`). Mesuré dans Chromium, dehors sur un banc : 244 pas par
  seconde, une heure toutes les 2 s, 3 h en 6 s, 8 ms par image au lieu de 3. Un appareil trop lent fait moins
  de pas : l'attente dure un peu plus, l'horloge suit les pas.
- **Le bandeau** « ATTENTE — 18:23 » (un état, pas l'ordre « ATTENDRE »), puis « IL EST 19:52 » à l'arrivée —
  pile à l'heure dite. Minuit passé, c'est un vrai jour (`nouveauJour`), comme l'horloge ordinaire.
- **Ce qui l'arrête** : le stick, un coup, SE LEVER, une étoile (son refus s'affiche). **Ce qui la refuse**
  (grisée au menu, la raison à la place de l'heure) : la police, un défi ou une épreuve, une frénésie, un boulot,
  un objectif à chrono, la villa dont la nuit tient — tout ce qui compte en images compterait au quadruple.
- ⚠️ **ACTION assis ouvrait SE LEVER** ; le juge « la pression qui nous lève n'ouvre pas la machine d'à côté »
  se juge maintenant au bouton, curseur sur SE LEVER. Le second joueur, lui, se lève toujours à ACTION : un
  menu qui change l'heure de tout le monde est au joueur 1.
- Juges : quatre de plus dans `tests/test_repos_js.py` (deux heures pile en ≈ 240 images avec ses pas de plus,
  le stick et le coup qui coupent, le boulot grisé et l'étoile qui arrête, minuit) ; mutations mordues : le
  refus du boulot, l'accélération, l'arrêt debout, l'arrêt au refus.
