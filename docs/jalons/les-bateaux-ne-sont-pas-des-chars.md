# Les bateaux ne sont pas des chars

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026 : « révise les bateaux car ils sont trop comme des véhicules et ce n'est pas toujours
cohérent ». Tout ce qu'il a vu : la conduite, la police et la descente, les règles de char, l'habillage. Tranché
par Martin : tout corriger, en vagues ; erre et gouvernail ; une vedette de police ; descendre au large = plonger ;
les chaloupes remisées l'hiver.

Un bateau est un `vehicule` ordinaire marqué `eau: true` (`app/vehicules.py`, la chaloupe, le chalutier, le
porte-conteneurs). Six endroits seulement le traitent à part (`tuileInterdite`, `majNoyade`, `majConducteur`,
`majVolDeChar`, `Derapage.exempt`, le moteur et les phares) ; tout le reste — police, fourrière, météo, sons,
statistiques — le prend pour une auto.

**Vague 1 — la conduite : erre et gouvernail.** Une branche `eau` dans `majPhysique` : la coque pivote au tiers
avant (la poupe chasse, le nez ne balaie plus comme un train arrière) ; pas de frein sec — l'arrière met la
machine en arrière, qui ralentit doucement puis recule lentement ; lâcher le gaz laisse filer sur l'erre. La
neige, le verglas, la pluie et les pneus d'hiver (`Neige`, `Verglas`, `Pluie`, `Garage.hiver`) ne jouent plus sur
l'eau, et les feuilles d'octobre ne se lèvent plus d'une coque.

**Vague 2 — ce qui n'est pas une règle de bateau.** Ni « mal garé » ni fourrière pour une coque
(`malGare`, `charSaisissable` — le porte-conteneurs saisi renaissait sur la terre ferme du lot) ; la remorqueuse
ne l'accroche pas (`aCrocher`) ; le garage de Ti-Guy la refuse (`Garage.accepte`, `charDevant`) ; une coque
amarrée ne compte plus comme une auto garée (`compteCommeGare`) ; le carnet a sa ligne **BATEAUX VOLÉS** ; la
frénésie « chars » ne compte plus les bateaux ; le traversier n'accoste pas sur une coque (`traversier.js`
`poser`, comme `Pont.poser`).

**Vague 3 — le plongeon, et la police de terre.** Descendre au large = plonger : une éclaboussure, on nage ; la
coque file sur son erre et s'arrête, elle n'est pas « laissée » (la fourrière l'ignore). Les agents à la nage ne
sortent plus personne d'une coque (« SORS DU CHAR ! » en pleine eau) — ils attrapent encore un joueur qui nage.
Les autos-patrouilles ne foncent plus en ligne droite dans la baie (`police.js` `commandes`, la ligne de vue
traverse l'eau) : elles s'arrêtent au bord. Pas de barrage routier tant que le joueur est sur l'eau.

**Vague 4 — la vedette de police.** Une fiche `vedette` (police, sirène, eau) et son sprite. Le premier pilote
sur l'eau (aucun n'existe : `docs/exploitation.md` en annonce un qui n'est pas là) : un chemin sur les tuiles
d'eau, au grain grossier, recalculé chaque seconde. Elle naît hors champ, dans la même étendue d'eau que le
joueur — une dès une étoile, deux dès trois. Elle aborde bord à bord ; coque du joueur presque arrêtée à côté
d'elle : **« ARRAISONNÉ ! »**, qui vaut l'arrestation.

**Vague 5 — l'habillage et l'hiver.** Le compteur en **NŒUDS** ; le bouton **CORNE** quand la fiche a la
corne ; monter à bord fait des pas sur un pont (pas la béquille du vélo) ; le chalutier et le cargo ont un diesel
grave (ElevenLabs), la chaloupe garde son hors-bord ; les feux de navigation — rouge et vert aux flancs, blanc à
la poupe ; l'épave **coule** en quelques secondes, avec ses bulles, puis s'efface. De décembre à mars, les
chaloupes de plaisance sont sur des bers à quai ; la chaloupe de Sven (m52), le chalutier et le cargo restent à
l'eau.

- ⚠️ **L'ordre compte** : la vague 3 retire l'arrestation par les nageurs, la vague 4 la remplace — entre les deux,
  sur l'eau, la police ne peut que suivre jusqu'au quai.
- ⚠️ **Les amarrages sont un tirage** (`carte.amarrages`, `majAmarrages`) : la remise d'hiver MARQUE l'amarrage et
  peint le ber sans entité, elle n'en retire aucun — sinon les identifiants et le hasard de la ville glissent.
- ⚠️ **L'épave qui coule** : une cible de mission détruite reste comptée détruite (m52 à m54) — s'effacer ne doit
  pas la faire revenir « debout ».
- ⚠️ Chaque règle neuve a son juge, et chaque juge est vu rougir, règle retirée.

## Plan de la vague 1

> Écrit avec superpowers:writing-plans (30 sept. 2026) ; exécuté dans la session, test d'abord.

**But** : une coque se pilote comme une coque — la poupe chasse, pas de frein sec, l'erre, et la météo de la rue ne
touche pas l'eau. **Architecture** : une branche `eau` dans `Vehicules.majPhysique` (`static/js/vehicules.js`), deux
nombres neufs dans `PHYSIQUE` (`app/vehicules.py`) — `pivot_eau` et `machine_arriere` —, un garde dans
`Pluie.majChar`. Aucune fiche de bateau ne change, aucune tuile, aucun dé : la ville ne bouge pas.

**Ce qui mord le plus probablement, et son juge** : (1) une coque qui chasse de la poupe contre un quai — le pivot
reste refusé dans un mur (`bloqueParLesTuiles`), comme celui des chars ; (2) le virage automatique du large
(`virerDeBord`) garde son pivot au centre — `tests/test_aeroport_js.py` rejoué ; (3) la vedette de la vague 4
héritera de la branche — elle passe par `majPhysique` comme la police ; (4) les chars ne changent pas d'un pixel —
`tests/test_derapage_js.py` et `tests/test_conduite_js.py` rejoués ; (5) le frein à main ne fait rien sur l'eau.

**Tâche 1 — les deux nombres.** `app/vehicules.py`, `PHYSIQUE`, sous `pivot_arriere` :
`"pivot_eau": -0.17` (la coque pivote au tiers avant : un sixième de la longueur DEVANT le centre, la poupe
chasse) et `"machine_arriere": 0.8` (l'arrière pousse à 0,8 × l'accélération, à toute vitesse : pas de frein).
Juge dans `tests/test_vehicules.py`, à côté de celui de `pivot_arriere` :
`assert -0.5 < ph["pivot_eau"] < 0` et `assert 0 < ph["machine_arriere"] <= 1`.

**Tâche 2 — la poupe chasse.** `pivoterSurLArriere(v, ancien)` devient `pivoter(v, ancien, fraction)` (la
fraction de longueur DERRIÈRE le centre ; négative, devant) ; `majPhysique` passe `ph.pivot_eau` pour une coque,
`ph.pivot_arriere` sinon. Juge `test_la_poupe_chasse_le_nez_tient` (`tests/test_bateaux_conduite_js.py`) : une
chaloupe au plein large, lancée à 2 px/image, le même état joué dix images droit puis dix images barre à fond
(`v.volant = 1`) ; on mesure de combien l'étrave et la poupe s'écartent entre les deux. Coque : la poupe s'écarte
plus que l'étrave ; auto (même mesure sur une chaussée) : l'inverse.

**Tâche 3 — la machine arrière, pas de frein à main.** Dans `majPhysique`, pour une coque : `cmd.frein` retire
`d.acceleration * ph.machine_arriere * cmd.frein` à chaque image, à toute vitesse (pas de seuil de 0,15, pas de
`d.frein`), et `cmd.freinMain` ne fait rien (ni 0,965, ni 1,35 au volant, ni `adherence_frein`). Juge
`test_la_machine_arriere_ralentit_sans_frein_sec` : une chaloupe à 3 px/image, arrière à fond — plus de 100
images pour passer sous 0 (le frein de char le faisait en 64), la vitesse descend à chaque image sans saut, puis
recule jusqu'à `-vitesse_recul` ; et `test_sur_l_eau_le_frein_a_main_ne_fait_rien` : la même trajectoire au pixel
avec et sans `freinMain`.

**Tâche 4 — la météo reste sur la rue.** Pour une coque, `g = 1` (ni `Neige`, ni `Verglas`, ni `Pluie`, ni
`Monde.adherenceMouillee`, ni `Garage.hiver`) et le frein n'existe plus (tâche 3). Juge
`test_la_neige_et_la_pluie_ne_touchent_pas_l_eau` : les cinq coefficients bouchés à 0,3 et des pneus d'hiver ;
la trajectoire d'une chaloupe (gaz, barre, arrière) est la même au pixel qu'au sec — et celle d'une auto change
(sinon le bouchon ne mord pas).

**Tâche 5 — pas de feuilles sous une coque.** `Pluie.majChar` : `if (v.def && v.def.eau) return;` en tête.
Juge `test_en_octobre_une_coque_ne_souleve_pas_de_feuilles` : jour 32, une chaloupe lancée au plein large sous la
caméra, quarante images de `majChar` — aucune particule ; une auto sur la rue, le même jour, en soulève (le
juge d'octobre existant).

**Atterrir** : juges ciblés (`test_bateaux_conduite_js`, `test_vehicules`, `test_bateau`, `test_derapage_js`,
`test_conduite_js`, `test_aeroport_js`, `test_pluie_js`, `test_navires_js`, `test_monde_js`, `test_definitions`)
+ `uv run ruff check .`, chaque juge neuf vu rougir règle retirée ; commit `fix:`, cherry-pick sur `dev`,
`merge --ff-only`. La ligne du plan dit « ✅ vague 1 livrée ». Martin essaie avant la vague 2.

## Notes

- **Vague 1 livrée le 30 sept. 2026 — la conduite.** Deux nombres dans `PHYSIQUE` (`app/vehicules.py`) :
  `pivot_eau` −0,17 (le pivot un sixième de la longueur DEVANT le centre) et `machine_arriere` 0,8 (l'arrière pousse
  à 0,8 × l'accélération, à toute vitesse). `pivoterSurLArriere` devient `pivoter(v, ancien, fraction)`, toujours
  refusé dans un mur. Pour une coque, `majPhysique` n'a ni frein sec ni frein à main, et `g = 1` : ni neige, ni
  verglas, ni pluie, ni rue mouillée, ni pneus d'hiver. `Pluie.majChar` ne fait rien pour une coque. Les chars ne
  changent pas d'un pixel (leur branche est la même, relue).
- Mesuré : la chaloupe à 3 px/image, arrière à fond, s'arrête en plus de 100 images (68 avec le frein de char) ;
  barre à fond, la poupe s'écarte plus de 1,5 fois plus que l'étrave (l'inverse avant : 2,5 contre 8,7 px).
- **Les juges** : `tests/test_bateaux_conduite_js.py` (cinq, chacun vu rougir avant la règle) et les deux bornes
  dans `test_vehicules.py::test_le_trafic_et_la_physique_sont_bornes`.
- ⚠️ Le porte-conteneurs met environ 5 s à s'arrêter depuis sa pointe (0,004/image de machine arrière) : c'est
  voulu, à confirmer par Martin à quai. L'aide des commandes dit encore « FREIN À MAIN » en bateau (`hud.js`) :
  vague 5.
