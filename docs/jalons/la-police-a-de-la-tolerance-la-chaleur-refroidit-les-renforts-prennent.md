# La police a de la tolérance : la chaleur refroidit, les renforts prennent le temps de venir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin en jouant (22 sept. 2026) : « la police arrive trop rapidement et les
étoiles aussi. il faut plus de tolérance ». Trois causes lues dans police.js.

- ⚠️ La chaleur ne refroidit JAMAIS : trois petits délits espacés de vingt minutes font une
  étoile, pour toute la partie.
- ⚠️ Un carambolage compte chaque accrochage : trois chars touchés devant un passant, c'est
  une étoile d'un coup, sans témoin à convaincre.
- ⚠️ Les renforts d'un palier naissent à l'instant où l'étoile tombe, à moins de 420 px d'où
  l'on t'a vu (parfois d'une porte à l'écran), et courent à 1,6 px/image : trois secondes et
  demie plus tard, ils sont là. Le correctif, en données dans app/recherche.py : la chaleur
  refroidit après un répit sans nouveau délit compté (les étoiles, elles, ne tombent
  toujours que hors de vue) ; un même délit de conduite répété dans la foulée ne compte
  qu'une fois ; les renforts d'une étoile neuve arrivent après un délai, jamais d'une porte
  à l'écran — les agents déjà sur place réagissent tout de suite. Des juges pour chacune des
  trois, et une mutation pour chacun.

## Notes

**Livré le 22 sept. 2026.** Trois règles, toutes en données dans `app/recherche.py`, et une
quatrième trouvée en chemin.

- **La chaleur refroidit** (`CHALEUR_REPIT_S`, `CHALEUR_REFROIDIT_PAR_S`, `refroidir` dans
  `police.js`). Elle ne redescendait JAMAIS : la jauge d'un délit pesait jusqu'à la fin de la
  partie, et trois petits délits espacés de vingt minutes faisaient une étoile. Elle tient
  maintenant 30 s après le dernier délit compté, puis perd 5 points à la seconde — un délit de
  gravité 1 (35) est oublié 37 s plus tard. ⚠️ La JAUGE seulement : les étoiles, elles, ne
  tombent qu'hors de vue (`decroissance_s`), et trois délits coup sur coup font toujours leur
  étoile.
- **Un carambolage est un délit, pas trois** (`DELITS["conduite_dangereuse"]["repit_s"]`, 20 s).
  Chaque accrochage à plus de 2 px/image et chaque clôture défoncée chauffait : trois chars
  touchés, une étoile d'un coup. Le répit part du dernier délit qui a CHAUFFÉ, il ne glisse pas
  — conduire comme un fou sans arrêt coûte quand même, une fois par répit.
- **Un accrochage a un témoin** (`temoin: True`). Il était BRUYANT : n'importe quel passant qui
  le voyait le faisait compter tout de suite, comme un coup de feu. Sa fiche disait pourtant
  déjà le contraire (« casser est un délit, avec son témoin qui rapporte ») : il faut maintenant
  qu'un agent le voie, ou qu'un passant aille le raconter — et d'ici là on peut lui acheter son
  silence. C'était la dernière raison pour laquelle les étoiles montaient en conduisant.
- **Les renforts prennent le temps de venir** (`POLICE.renfort_s`, 20 s ; `majRenforts`,
  `palierDesRenforts`). Ceux d'un palier — ses agents à pied, ses autos, l'hélico, les barrages —
  naissaient à l'image où l'étoile tombait, à moins de 420 px d'où l'on t'avait vu, parfois par
  une porte à l'écran, et couraient à 1,6 px/image : trois secondes et demie plus tard, ils
  étaient là. ⚠️ Les agents DÉJÀ sur place ne sont pas des renforts : ils te voient et te
  poursuivent dans la seconde (c'est le poste qui attend, pas l'agent). ⚠️ Et un renfort n'arrive
  plus par une porte : `placeDeNaissance` fait sortir un passant sur trois d'un pas de porte,
  parfois à deux pas du joueur.
- **Le témoin qui téléphone attend 15 s** (`TEMOINS["delai_depeche_s"]`, 8 s avant) : le temps de
  lui acheter son silence, ou de partir.

**Les juges** (`tests/test_police_js.py`) : un par règle — la jauge qui refroidit et l'étoile qui
ne refroidit pas ; le carambolage compté une fois et pas sans témoin ; les renforts qui prennent
le temps de venir pendant que l'agent déjà là poursuit dans la seconde ; le renfort qui ne sort
jamais d'une porte. Chacun rougit quand on retire sa règle (quatre mutations, chacune sur la
bonne assertion).

⚠️ **Trois juges d'avant supposaient des renforts instantanés.** Deux ne jugent pas le délai
(`renfort_s = 0` chez eux, avec la raison) : l'auto sans équipage qui ne retient plus les
renforts, et le scanner qui saute le temps à la main. Le troisième —
`test_deux_dehors_l_auto_reste_immobile…` — tenait par chance de foule **sur la base aussi** : le
joueur avançait par `j.x - 2`, l'équipage se tenait entre lui et le bout de la rue, et depuis que
la foule ne se traverse plus il restait collé derrière ; il ne passait que si un agent né ailleurs
venait le décoincer. Il avance maintenant par son propre compteur. ⚠️ En le jouant sur la base
avec ce correctif, l'auto garée bouge de 0,5 px sous la poussée des agents : c'est là depuis
avant, et ça n'est pas de ce jalon.

**Deux passes.** La première (répit 20 s, 3 points/s, `renfort_s` 12 s, conduite dangereuse
bruyante avec un répit de 10 s) n'a jamais atterri : la session a été coupée pendant la suite, le
code est resté dans `refs/wip/tolerance-police`, et Martin a rejoué l'ancienne police — « ça me
semble ENCORE trop rapide ». Les chiffres livrés sont ceux de la deuxième passe.
