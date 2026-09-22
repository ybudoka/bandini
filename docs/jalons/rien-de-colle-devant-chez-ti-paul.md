# Rien de collé devant chez Ti-Paul

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026, capture) : « trop de choses collé devant chez Ti-Paul,
étale-les plus sur le pâté de maison ». Sur huit tuiles devant la porte : l'édicule du
métro, Ti-Paul, le guichet, la pancarte, l'abribus et son banc — et Xavier, invisible, posé
sur le même pixel que Ti-Paul (les deux bulles empilées). Deux causes, toutes deux
générales. (1) La ligne 2 s'arrête « devant » le dépanneur : l'arrêt prend la place la plus
proche de la porte, c'est-à-dire deux tuiles de côté — la place même du donneur, qui se
rabat entre l'édicule et le guichet. Mesuré : cinq arrêts sont dans ce cas (dépanneur,
planque de Rocco, poste, casse-croûte, hôpital). Remède : `devants.py` fait glisser l'arrêt
le long de SA voie, après coup et sans dé, jusqu'à laisser de l'air au donneur ; l'abri et
le banc suivent, le tracé ne bouge pas (seul l'indice de l'arrêt dans la boucle change). (2)
`placeVisible` pose chaque donneur sans regarder les autres : Ti-Paul et Xavier au
dépanneur, Ti-Guy, Mo et Fern au terminus, tous sur la même tuile. Remède : une place déjà
tenue par un autre personnage (ou collée à lui) passe à la suivante, dans le même ordre
fixe. Juges : aucun arrêt dans l'air d'un donneur, la ville ne bouge que ces arrêts, deux
donneurs jamais à moins de deux tuiles ; mutations ; et une capture du dépanneur.

## Notes

Livré le 22 sept. 2026. Devant chez Ti-Paul, de gauche à droite : le panneau de la course au coin,
l'édicule du métro, le guichet, la porte, la pancarte, Ti-Paul (deux tuiles de la porte), Xavier
(quatre), un arbre du parc, puis l'abribus et son banc au bout du pâté, près du passage piéton.
Avant : l'édicule, Ti-Paul **et** Xavier sur le même pixel, le guichet, la porte, la pancarte,
l'abribus, son banc et, planté SUR le banc, le panneau jaune de la course — tout sur huit tuiles,
et le parc vide à côté.

- **L'arrêt glisse le long de sa voie** (`devants._deplacer_les_arrets`, après coup et sans dé,
  comme le reste de `devants.py`). Un arrêt dont l'abri ou le banc tombe dans l'air d'un lieu de
  mission se pose à la place la plus proche, sur le **même tronçon** (aucune boîte entre les deux),
  qui obéit à tout ce que le traceur exige (`autobus.arret_possible`), à l'écart des autres arrêts de
  ses lignes (8 à 84 tuiles de boucle) et à six tuiles des quais du tramway. Le tracé ne bouge
  pas : seul l'indice de l'arrêt dans la boucle, décalé d'autant de tuiles. Faute de place, l'arrêt
  **reste**, et le banc suit ou rien ne bouge (un décor de moins décalerait les `id`).
- **L'air se compte en donneurs** (`air_d_un_arret`) : deux tuiles de côté sans donneur (le devant de
  mission), puis deux par donneur plus une d'air — trois pour Mado ou Ginette, cinq pour Ti-Paul et
  Xavier. Un air fixe de cinq tuiles laissait coincés les quatre arrêts dont la porte touche un
  carrefour.
- **Une place aérée d'abord** : l'abri et le banc ne touchent aucun autre meuble. Le premier
  glissement posait le banc du dépanneur contre un arbre du parc (17-18, l'arbre en 19) et refaisait
  un peu plus loin le paquet qu'on défaisait ; aéré, il va en 21-22.
- **Les coins de croisement ne sont pas interdits à un arrêt** (`_evitees_d_un_arret`) : le traceur y
  pose déjà les siens, et c'était souvent la seule place entre la porte et le carrefour.
- Cinq arrêts glissent sur la ville livrée : dépanneur (13 → 21), planque de Rocco (175 → 180), poste
  (122 → 121), casse-croûte (143 → 145), hôpital (252 → 250). Le terminus reste : son parvis le
  tient déjà hors du devant de mission, et il n'a nulle part où aller plus loin.
- **Les donneurs ne s'empilent plus** (`Histoire.placeVisible`) : une place qu'un autre personnage
  tient à moins de deux tuiles ne se prend pas (`placeTenue`), et le second donneur d'une porte ne se
  glisse pas contre un meuble (`colleeAUnMeuble`) — c'est entre l'édicule et le guichet que Ti-Paul
  se rabattait. Le premier donneur se tient où il s'est toujours tenu. Au terminus, Ti-Guy, Mo et
  Fern étaient trois sur la même tuile ; ils sont maintenant en 125, 119 et 128.
- **Les panneaux de défi ne se plantent ni sur un meuble ni entre deux** (`placeDePanneau(p, aere)`) :
  `tuileLibre` ne regarde que la carte, et celui des Érables tenait sur le banc de l'abribus ; l'arrêt
  parti, il se glissait entre l'édicule et le guichet. Au terminus, Ti-Guy, Mo et Fern, qui ne
  s'empilent plus, tenaient à eux trois toute la façade : le panneau du « tour » ne trouvait plus de
  place à trois tuiles d'un donneur et le défi DISPARAISSAIT (`test_les_defis_ont_un_panneau_et_un_chrono`
  et le circuit de `test_course_js` l'ont dit). Une place aérée d'abord, un pas plus loin s'il le faut
  (9, 11 tuiles), et l'ancienne règle en repli : le « tour » se pose à dix tuiles du terminus, celui
  des Érables au coin du pâté ; les cinq autres n'ont pas bougé.
- Juges : `test_devants.py` — `test_aucun_abribus_ne_colle_la_porte_d_un_lieu_de_mission` (l'air
  écrit en toutes lettres, pas relu dans `devants`), `test_le_temoin_a_bien_des_abribus_colles`,
  `test_devant_chez_ti_paul_l_arret_laisse_la_facade_aux_donneurs`, et
  `test_la_ville_ne_bouge_que_ce_qui_bouchait` qui juge maintenant ce qu'un glissement a le droit de
  changer (même voie, même nom, même tracé, l'indice décalé d'exactement `k`) ;
  `test_donneurs_visibles_js.py` — `test_deux_donneurs_ne_se_tiennent_jamais_sur_la_meme_tuile` (au
  départ, puis après m1) et `test_le_second_donneur_d_une_porte_ne_se_glisse_pas_entre_deux_meubles` ;
  `test_devants_js.py` — `test_un_panneau_de_defi_ne_se_plante_ni_sur_un_meuble_ni_entre_deux` (les
  sept panneaux existent, aucun sur un meuble, aucun entre deux).
- ⚠️ `test_mobilier::test_le_mobilier_ne_ferme_aucun_passage` compare la ville avec et sans le
  mobilier : sans les arbres, l'arrêt trouve sa place aérée plus tôt, et ses deux tuiles comptaient
  comme « passage perdu ». Elles sont occupées, pas fermées : le juge les excuse, elles seules.
- Mutations, toutes rouges : sans glissement (4 graines + le dépanneur), un air d'un seul donneur,
  sans la place aérée (le banc contre l'arbre), les donneurs empilés, le second collé aux meubles, le
  panneau sans place aérée (entre l'édicule et le guichet), le panneau à trois pas seulement (le
  « tour » disparaît).
- Suite complète sur `2cf0078` (en 12 groupes, Chromium seul après) : 5 209 verts, 13 rouges,
  hors de ce jalon, **tous rouges aussi sur la base `f5dbc7a` sans lui** —
  `test_moteur_js::test_la_foule_ne_se_traverse_plus` et `test_la_bagarre_tient_le_budget`,
  `test_definitions::test_le_paquet_reste_leger`, les cravates de M2 et
  `test_les_personnages_disent_leur_repos_a_voix_haute` (`test_histoire_js`), `test_ondes` (la voix
  de la police), les comptoirs (`test_interieurs_js`), l'hôpital (`test_interieurs`), la balle dans
  la tôle (`test_abri_js`), les intros de f04 et p01 et le dé de h02 (`test_missions_en_scene_js`),
  et l'audio de Chromium (`test_navigateur`, délais de chargement, rouge sur la base aussi).
- Hors règle, laissé tel quel : l'arrêt d'Électronique Turcotte (ligne 3) est à deux tuiles de sa
  porte, mais ce n'est pas un lieu de mission — personne n'y attend.
