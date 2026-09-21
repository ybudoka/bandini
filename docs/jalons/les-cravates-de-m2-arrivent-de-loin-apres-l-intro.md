# Les Cravates de M2 arrivent de loin, après l'intro

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (20 sept. 2026), devant l'intro de Madame Thibodeau : « il faudrait que les
méchants apparaissent plus loin et m'attaquent, mais aussi après que la dame ait fini de
parler ».

✅ **Livré** (20 sept. 2026).

- ⚠️ **Ils naissaient trop tôt et trop près.** À la pose de la mission — avant l'intro, pour que
  la caméra les filme — à 40 px du kiosque, donc du joueur : deux hommes collés à elle pendant
  qu'elle parlait, et déjà en train de te viser.
- ⚠️ **`loin`, une clé de l'objectif `tuer`** (`m2.py`, `"loin": 15`). Le point de naissance est
  choisi à la pose — à 15 tuiles du joueur, sur un sol où l'on marche, avec une ligne droite libre
  jusqu'à lui, **hors de l'écran** d'abord —, mais les hommes n'y naissent que quand l'intro est
  finie (`annoncer` → `faireArriver`). Ils naissent alors en `attaque_joueur`, avec leur cri : au
  banc, ils touchent un joueur immobile 2,5 s plus tard. Quinze tuiles et pas plus : au-delà de
  260 px, `attaque_joueur` renonce à la première image.
- ⚠️ **La caméra de l'intro va voir un coin vide.** `cible` nomme, tant qu'ils n'existent pas, le
  point d'où ils viendront (`lieux` du contexte de `Scenes.jouer`) : la scène écrite de m2 n'a pas
  changé d'un plan, et aucun n'est sauté. Aucun dé n'est tiré : seize directions dans un ordre fixe.
- ⚠️ **Un juge mesurait la course, pas la bagarre.** `test_la_premiere_bagarre_se_gagne_aux_poings`
  passait à 7,1 s pour 4,6 s de coups : il compte maintenant depuis le premier contact. Les deux
  juges des Cravates (`test_histoire_js.py`) sont rouges sans la clé ou sans le report — vérifié.
  ⚠️ `test_la_foule_ne_se_traverse_plus` est rouge sur `ce63d7d` sans ce changement : il n'est pas
  de celui-ci.
