# Les phares ne passent pas à travers un autre char

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « les phares éclairent encore au travers des véhicules eux-mêmes ». Le
faisceau (voir [[des-phares-a-la-mesure-de-chaque-char]]) s'arrêtait déjà devant un mur ou un toit,
mais traversait un autre char sans s'en apercevoir — une auto garée juste devant restait éclairée à
travers sa caisse.

## Notes

**Livré le 22 sept. 2026.** Chaque char visible pose son empreinte (`lampesPhares.corps`, un
rectangle dans son propre repère, en VRAI monde) ; le faisceau y marche par quarts de tuile — la
même méthode que pour un mur (`porteeLibreDesChars`, jumelle de `porteeLibre`) — et s'arrête devant
le premier char qui n'est pas le sien.

- ⚠️ **La finalisation se fait dans `lampesDesPhares`, pas dans `allumerLesPhares`.** Les chars se
  dessinent dans l'ordre de `Entites`, pas dans celui où ils se gênent : un char plus loin dans la
  liste — donc pas encore dessiné — peut déjà se trouver devant celui qui s'allume, et son empreinte
  n'existe pas encore. `lampesDesPhares` n'est appelée qu'UNE FOIS par image, par `jeu.js`, après que
  tous les chars visibles sont passés par `dessinerUn` : c'est le seul moment où `corps` est complet.
  Le juge dédié pose exprès le char MENÉ en premier — le cas qui piège une garde posée trop tôt.
- **L'empreinte se pose pour tout char visible, mené ou non** : un char garé, ou en panne, bloque un
  faisceau tout autant que celui qui roule — c'est sa caisse qui arrête la lumière, pas son moteur.
- ⚠️ **Un char ne se bloque jamais lui-même** (`sansCe`) — mais le juge sur l'auto ne le prouvait
  pas : son phare est presque à son nez (13,4 px sur 14 de demi-longueur), et le premier pas de
  marche (4 px) le sort déjà de sa propre caisse même sans la garde. Le juge utilise la moto (phare à
  5,8 px sur 10) : sans `sansCe`, deux pas y suffisent encore, et le faisceau s'éteindrait tout court.
- **Le cône rétrécit dans la même proportion** que le raccourcissement, comme pour un mur.
- **Juges** : cinq neufs dans `test_la_nuit_js.py`. Quatre mutations, une par règle, toutes rouges —
  dont une resserrée à une égalité stricte (12 px pile, géométrie pure) après qu'une empreinte deux
  fois trop étroite ait d'abord passé sous des bornes trop larges.
- **Regardé dans Chromium** : une auto menée, un camion garé 60 px devant elle — comparé à la même
  scène, la garde retirée : sans elle, le faisceau atteint et éclaire le dessous du camion ; avec
  elle, rien ne dépasse le nez de l'auto.
- ⚠️ **Un chevauchement avec un autre jalon en cours** (« un char sous le toit d'un garage n'éclaire
  rien ») : son mécanisme (`corpsDesPhares`/`decouperLesCorps`, un découpage du cône dessiné dans
  `Base.fin`) couvre — en plus du toit d'un garage, son vrai sujet — le même cas que ce jalon-ci, par
  une autre méthode (une découpe à l'écran plutôt qu'un raccourcissement de la portée en vrai monde).
  Les deux ne se contredisent pas — ils préviennent la même chose, chacun à sa manière — mais une
  fois l'autre jalon livré, sa part « char devant char » sera redondante avec celle-ci. À simplifier
  à ce moment-là, pas avant : ce jalon-ci répond à la demande de Martin dès maintenant, testé et
  vérifié, sans attendre un jalon voisin encore en cours.
