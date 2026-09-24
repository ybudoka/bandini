# M4 : l'auto-patrouille attend au poste, et Ti-Guy suit derrière

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « la mission de Bouchard ne fonctionne pas toujours, le
véhicule de police n'apparaît pas toujours et celui qui doit nous suivre apparaît en avant. »

**Livré** (17 sept. 2026). Deux causes, mesurées au banc sur 8 graines et trois arrivées (à
pied ; en char arrêté devant la porte ; en char un peu en retrait) :

- **L'auto-patrouille naissait dans notre char.** Arrivé au poste en char, on s'arrête sur la
  tuile de rue la plus proche de la porte — celle-là même où `Histoire.poser` posait
  l'auto-patrouille : aux mêmes x et y, cachée dessous, et ACTION nous remettait dans le
  nôtre (8 graines sur 8). `poser` prend maintenant la tuile de rue la plus proche **sans char
  à moins de 32 px ni joueur dessus** (`sansChar`). Le taxi de Marco (M3), qui naît par le même
  chemin devant le garage, en profite.
- **Ti-Guy naissait devant.** L'escorte prenait la tuile de rue la plus proche du joueur :
  28 px devant le nez de l'auto-patrouille, dans sa voie (24 essais sur 24). Elle s'arrête à
  70 px du joueur, donc elle bouchait la rue : 42 px parcourus en 90 images. `placeDerriere`
  la pose derrière, dans une voie du même sens (≈ 64 px) : on roule 316 px, il en suit 227.
- ⚠️ Fausse piste : au banc, une mission dont `B.mission` est vide saute « prends
  l'auto-patrouille » (`monter` sans char avance). Mais `Jeu.commencer` annule la mission au
  rechargement : ce chemin n'arrive pas en jeu, et il n'est pas touché.
- ⚠️ Pour « Le poste a son stationnement » (en cours) : si l'auto-patrouille de M4 va dormir
  dans ce stationnement, `sansChar` reste la garde — les autos du décor y occupent justement
  les places.
- Juges (`tests/test_histoire_js.py`) : `test_le_char_de_la_mission_ne_nait_pas_sous_celui_du_joueur`
  (M4 et M3) et `test_ti_guy_nait_derriere_l_auto_patrouille_et_la_suit`. Trois mutations
  (sans `sansChar` ; l'escorte à la tuile la plus proche ; la voie à contresens préférée) font
  chacune rougir la sienne, M3 et M4 séparément.
