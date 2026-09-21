# Les chars s'arrêtent avant le passage

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « valide que les véhicules n'arrêtent pas sur un passage à piéton ».

✅ **Livré** (17 sept. 2026) — *le nez à la ligne, pas le centre*.

- ⚠️ **Mesuré d'abord : ils s'y arrêtaient, à chaque feu rouge.** Depuis `TROTTOIR = 1`, la
  traverse fait UNE tuile, toute peinte, collée à la ligne d'arrêt — et le trafic attendait
  **le centre** sur la ligne : tout ce qui dépasse les huit pixels d'avant du char était
  peint sur les bandes. Au banc, graine 5, 2 000 images : **5 550 relevés**, 4,9 px de nez
  pour une berline, 10 pour une remorqueuse, 12 pour un camion, et l'autobus couvrait la
  traverse entière. 5 409 de ces relevés étaient des attentes à la ligne (feu, STOP, boîte).
- ⚠️ **La cible d'attente n'est plus le centre de la tuile : c'est le point où le NEZ touche
  la ligne** (`pointDArret`) — donc un point qui tombe d'autant plus tôt que la caisse est
  longue, et qui oblige un long char à freiner **avant** d'entrer sur la ligne d'arrêt. Ce
  n'est pas une invention : **l'autobus de M9 le faisait déjà pour lui seul**, en s'arrêtant
  au centre de la tuile d'avant — sa caisse fait pile trois tuiles, et ce centre-là lui
  posait le nez pile sur la ligne. On a généralisé la trouvaille à tout le parc, et le
  camion-benne des éboueurs, qui n'a que 40 px, y a gagné ses quatre pixels.
- ⚠️ **Jamais derrière soi** : arrivé trop vite, ou surpris par un feu qui tourne, un char
  s'arrête **où il est**. Un char qui recule devant un feu rouge n'existe pas dans la vraie
  rue, et il reculerait dans celui qui le suit.
- ⚠️ **On ne freine pas SEC, on GLISSE** : la vitesse voulue fond avec ce qui reste à
  parcourir (`approche_part` du reste, au plus `approche_vitesse`). Sans elle, un char qui
  voit le rouge une tuile avant la ligne s'arrêterait là où il l'a vu — au milieu de la rue
  —, et la file entière reculerait d'autant. Et il ne peut pas dépasser la ligne en
  glissant : `rouler` avance de `min(distance, vitesse)`, et la cible **est** le point
  d'arrêt.
- ⚠️ **Le feu se relit à CHAQUE IMAGE tant que la ligne est en vue**, et pas seulement au
  centre de chaque tuile : entre deux lectures il se passe une tuile entière, la boîte se
  fermait dans cet intervalle, et le char l'apprenait **déjà engagé** — quatre pixels de
  traverse pour une remorqueuse, mesurés. Un conducteur regarde le feu ; il ne le consulte
  pas tous les seize pixels.
- ⚠️ **Deux règles écrites, mesurées, puis JETÉES** — c'est la même leçon deux fois : une
  règle qu'aucune mutation ne rougit est une règle qu'on ne garde pas. (1) Guetter la ligne
  **deux** tuiles en avance : inutile depuis que le feu se relit à chaque image, le plus
  long du parc voyant son point d'arrêt venir dès qu'il met les roues sur la tuile d'avant.
  (2) Un garde « ne pas glisser dans le char d'en avant » : deux chars ne visent jamais le
  même point d'arrêt, la distance de sécurité les sépare d'une tuile et demie bien avant.
- ⚠️ **Le chien de garde a failli mordre un char sage, par l'autre bout.** Un char de plus
  de 32 px attend désormais sur la tuile qui **précède** la ligne : le croisement est alors
  à deux tuiles, et `attenteLegitime`, qui n'en regardait qu'une, répondait « il n'attend
  rien de légitime » — dix secondes de feu rouge (il en dure jusqu'à 480 images, plus
  l'attente de boîte), et l'autobus était téléporté au milieu de la voie. C'est exactement
  la faute réparée à M8, revenue par la porte d'à côté.
- ⚠️ **La panne loin des traverses**, l'autre moitié de la fiche : elle ne se posait déjà
  jamais sur la ligne d'arrêt ni dans le croisement (`placeDeLaPanne` exige une flèche), mais
  la voie qui **précède** un passage est une voie comme une autre — et une caisse de 48 px
  la couvre **quarante minutes de jeu**, là où un char au feu repart. Deux tuiles de
  dégagement de chaque bord (`panne.ecart_traverse_tuiles`), et un juge Python vérifie
  qu'elles couvrent bien la demi-longueur du plus long char qui tombe en panne.
- ⚠️ **Ce qui reste, et pourquoi c'en est un autre.** Sur sept graines de 2 000 images, plus
  **une seule** attente le nez dans les bandes (5 550 → 0). Deux causes subsistent, et
  aucune n'est celle-ci : un char qui **cède à un piéton déjà engagé** s'arrête forcément
  devant lui, donc sur la traverse — c'est la règle, pas le défaut ; et un char **surpris
  DANS la boîte** par la file qui se fige devant lui (jusqu'à 15 px, deux secondes et demie,
  sur deux graines de sept). Celui-là demande « on ne s'engage pas si l'on ne peut pas
  sortir », une règle de plus, qui se juge à part : on l'a écrite, mesurée, et elle ne
  changeait **pas un seul relevé** — la file qui bouche l'autre côté n'est pas encore là
  quand on est à la ligne.
- ⚠️ **Et trois juges tombés de loin, qui n'ont rien à voir avec les traverses** — la même
  fragilité chaque fois : pour mesurer sa règle, le juge s'appuyait sur une **conséquence du
  rythme** du trafic. Changer ce rythme les a fait tomber sans qu'aucune de leurs règles ait
  bougé d'une ligne. (1) `test_une_rixe_qu_on_ne_voit_pas_ne_s_entend_pas` laissait six
  hommes se battre 420 images hors champ, puis exigeait qu'il en reste **deux debout** pour
  aller les écouter : un homme de plus est tombé, et il est passé de deux à un. Il mesure ce
  qu'on **entend**, pas qui gagne — les six ont maintenant de quoi tenir tout le juge
  (vérifié : il rougit toujours si un coup hors champ se met à s'entendre). (2) Le juge du
  chantier plaçait « avoir passé les cônes » **cinq tuiles** au-delà du rectangle vers
  l'ouest et deux vers l'est : le char avait doublé le chantier dès la 75e image, puis il a
  **tourné** au croisement suivant au lieu de continuer tout droit — et le juge le déclarait
  bloqué. On mesure le bord du rectangle, et rien d'autre. (3) Celui de l'abribus comparait
  la file de la **40e image** aux montées d'un autobus arrivé un quart d'heure plus tard :
  on compte maintenant qui attend **quand il ouvre ses portes**.
- **6 juges neufs** (`test_passage_pietons.py`, 8 cas), **7 mutations toutes rouges** : la
  cible au centre, l'anticipation retirée, le feu relu à la tuile, le freinage sec, le
  dégagement de la panne, `attenteLegitime` à une tuile, et un feu qui ne passe jamais au
  vert. Le juge du **catalogue entier** est celui qui tiendra le jour où un char plus long
  arrivera — le tramway de M12, par exemple. **2 166 tests.**
