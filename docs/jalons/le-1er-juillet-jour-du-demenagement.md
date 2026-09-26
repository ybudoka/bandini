# Le 1er juillet, jour du déménagement

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ un jour par partie, la moitié de la ville déménage — des camions en double file, des
sofas sur les trottoirs, des rues bouchées, et un boulot de plus.

- **Quand** : un jour fixe de la partie (le « 1er juillet » du jeu), calculé comme la neige de M12 — le même
  pour tout le monde, jamais tiré au dé.
- **La ville** : des camions de déménagement stationnés en double file (le trafic les contourne ou klaxonne),
  des meubles sur les trottoirs des quartiers pauvres et ordinaires (les quartiers existent).
- **Le boulot** : déménageur — un camion, trois adresses, des meubles à livrer sans bosse (`boulots`,
  `sans_degats` existent).
- **Le lien avec la planque** : les meubles sur le trottoir se **ramassent gratis** et vont à la planque (la
  ligne des collections et de la planque qu'on décore).

⚠️ **Ce qui guette** : des camions en double file ne doivent pas enfermer un lieu de mission ni bloquer une
rue pour de bon (le juge du trafic qui ne s'empile pas) ; les meubles se posent sans dé.

**Juges** : le jour venu, les camions sont là et le trafic passe ; le lendemain, ils sont partis ; un meuble
ramassé arrive à la planque.

## Notes

**Livré le 27 sept. 2026.** `app/demenagement.py`, `static/js/demenagement.js`, le boulot `demenagement`
(`economie.BOULOTS`, ses paliers), le camion qui le prend le jour venu (`Missions.boulotDuChar`) ; juges
`tests/test_demenagement.py` et `tests/test_demenagement_js.py` (cinq mutations, toutes mordent).

- **Le jour** : le 1er juillet du calendrier (`calendrier.DATES["demenagement"]`, le jour 21), la veille
  et le matin dans le Clairon.
- ⚠️ **À cheval sur le trottoir, pas en double file** : mesuré le 27 sept., cinq façades de logement sur
  quatre-vingt-onze donnent sur une rue à deux voies par sens — partout ailleurs, un camion arrêté dans
  l'unique voie la bouchait pour de bon (le trafic klaxonne, puis force). Les camions se garent donc sur
  le trottoir, à côté de la porte (jamais devant une autre, ni sur un décor), seize dans la ville, à dix
  tuiles l'un de l'autre, hors des rues cossues. Ils naissent à l'approche, d'une couleur donnée (aucun
  dé), et sont partis le lendemain — sauf celui qu'on conduit.
- **Les meubles** sont peints sur le trottoir de l'autre côté de la porte (sofa, matelas, boîtes,
  lampe torchère, frigo, chaise — la sorte à l'empreinte de la tuile), ni entité ni obstacle.
- **Le boulot de déménageur** : dans un camion, ce jour-là, les boîtes de trois familles à livrer ; une
  bosse mange le tiers de la prime (de la vaisselle). Le camion a trois boulots selon la saison (les
  génératrices au verglas, les boîtes le 1er juillet, les dindes en décembre).
- ⚠️ **Pas fait : ramasser les meubles pour la planque.** Ils attendent la ligne des collections et de la
  planque qu'on décore (à trancher par Martin) — sans elle, un meuble ramassé n'irait nulle part.
- Capture regardée : un camion blanc devant une maison des Érables, le sofa et le matelas à côté.
