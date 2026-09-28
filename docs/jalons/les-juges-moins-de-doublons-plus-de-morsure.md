# Les juges : moins de doublons, plus de morsure

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demandé par Martin le 27 sept. 2026 (« regarde si tous les tests sont toujours valides et
nécessaires, et si on pourrait en regrouper »). L'audit du 27 sept. (suite complète sur
4f978c23 : 2 669 tests, 8 292 cas, 98 min de CPU, 15 min sur 8 files ; six lecteurs sur les
230 fichiers) : presque tous valides, mais une quinzaine ne mordent pas et une quarantaine
se répètent ; le gros du coût, c'est la ville régénérée sans cache (environ 200 fois) et des
bancs qui refont la même mise en place (environ 150). Vague A — les juges qui ne mordent
pas : test_zz_smoke sans assertion (seul juge des canards), le sentier de parc lu dans le
mauvais repère depuis la bande nord, les assertions tautologiques (or True, or gps,
json.dumps, isascii, le plafond des districts), les règles calculées jamais affirmées (le
feu, la course, la trace, l'empreinte des chars), le PYTHONHASHSEED jugé dans un seul
processus, les répliques hors du paquet que test_accents ne voit plus, la variable morte de
test_version, et le chien de garde du char coincé (rouge). Vague B — une ville partagée
(fixtures de session, cache par graine) et paquet au lieu d'assembler(). Vague C — les
doublons retirés et les bancs fusionnés. Vague D — test_moteur_js découpé par thème, les
petites paires fusionnées, un module commun pour les outils des missions.

- ⚠️ Un juge retiré ou fusionné ne perd aucune règle : chaque retrait nomme le juge qui la
  tient encore.
- ⚠️ Les deux rouges du ciné-parc (test_la_nuit::comptoirs, test_debug_js::portes des blocs)
  restent à la session du cinéma.

## Notes

**Vague A livrée le 28 sept. 2026** — les juges qui ne mordaient pas. Chaque juge réparé a été
prouvé par mutation du JEU (la règle retirée, le juge rougit avec un message qui la nomme) ;
chaque retrait nomme le juge qui tient encore la règle.

- **Le char coincé** (`test_moteur_js`, rouge depuis cf4e11d9) : le jeu n'avait rien. Planté
  devant le char, le joueur se faisait renverser dans la première moitié et se réveillait à
  l'hôpital — la seconde moitié jouait dans une pièce, sans un char à surveiller. Il reste en vie
  comme dans la seconde, et un garde dit « le joueur a fini dans une pièce » si ça revient.
- **Les canards** : `test_zz_smoke.py` (aucune assertion, seul juge de la pêche) devient
  `test_foire.py::test_la_peche_aux_canards_se_joue_au_bouton_et_paie`.
- **Des règles calculées, jamais affirmées** : le feu qui ne repart pas dans l'heure, la
  traversée en courant (le joueur s'arrêtait à un feu puis finissait à l'hôpital, qui rend le
  souffle), la rumeur (mesurée vide puis pleine), l'adresse qui allume la trace, le GPS du tour
  (valeur exacte), la grève (lue dans `carte.MEUBLES_DU_BORD`).
- **Des tautologies retirées** : `or True`, `or r["gps"]`, `json.dumps(...)`, `isascii()` après
  `ensure_ascii`, `pire_nuit >= 0`, le plafond des districts (vrai par l'algèbre, juge supprimé),
  `all(v["histoire"])`, le grep de l'ouverture (`Scenes.jouer(` existe trois fois ailleurs).
- **Des juges qui regardaient à côté** : les frontières (PYTHONHASHSEED jugé dans UN processus —
  maintenant deux), `test_accents` (ne lisait plus une réplique depuis qu'elles sont sorties du
  paquet — il lit `a_jouer`), `test_version` (`crochet=False` posait une variable que le crochet ne
  lit pas), le stool (lu dans le paquet, là où `police.js` le lit), le repli réseau (simulé).
- Le code mort : `harnais_js.lire_js`, les branches mortes du trafic, de l'ombre, de l'économie.

⚠️ **À trancher par Martin — deux juges honnêtes qui rougissent sur le jeu, gardés hors de `dev`** :

1. **Le sentier de parc** : réécrit pour lire la ville dans son repère, il trouve le **kiosque de
   Madame Thibodeau posé sur l'allée est** (`_parc` le bâtit après les allées : six tuiles de
   sentier sous un toit). Le juge est sous `refs/wip/vagueA-sentier`.
2. **L'empreinte des chars** : la moitié du juge qui mesurait le nez et l'arrière ne s'exécutait
   jamais ; mesurée sur la projection, cinq dessins dépassent leur collision — la **pelleteuse
   de 9 px** (son godet, que `sprites.js` promet replié), le bateau 3, la motoneige et la
   remorqueuse 2, le cabriolet 1,5. Le patch est le blob `refs/wip/vagueA-empreinte`
   (`git cat-file -p refs/wip/vagueA-empreinte | git apply`).

Restés à voir : la borne de `test_ombre` (la « ligne de sol » depuis la vue en volume : `ecart_sud` à
10 ne rougit pas), la ligne `routes.py` de `architecture.md` qui annonce encore « scores ». Rouges
connus, pas de cette vague : `test_moteur_js::la_foule…`, `test_police_js::deux_dehors…`,
`test_carte_du_depot` (`tests/test_garage.py`), les deux du ciné-parc.
