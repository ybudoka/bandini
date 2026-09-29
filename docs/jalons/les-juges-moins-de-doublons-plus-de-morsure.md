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

**Vague B livrée le 28 sept. 2026** — la ville partagée. `tests/villes.py` génère chaque ville
(`generer(plan, graine, nord)`, `exporter()`, `assembler()`) **une fois par processus** et la rend
**en copie** à chaque appel (0,02 s contre 6 à 7) : un juge qui salit sa ville ne salit pas celle
du suivant. `test_villes.py` le juge (la même ville que le jeu, une copie par juge, la graine et
la bande nord dans la clé — mutation « la clé oublie `nord` » : rouge). La fixture `app` et le
`serveur` reprennent le paquet de la session (`conftest._creer_app`) au lieu de rebâtir
`construire()` à chaque juge.

- 73 fichiers migrés : les villes bâties **à la collecte** (payées même par un `-k` ailleurs)
  deviennent des fixtures de module ; `_villes_de_la_rue()` de `test_chantiers`, les graines de
  `test_carte` et de `test_devantures` passent par le cache.
- **Mesure appariée** (les 73 fichiers en quatre lots, l'ancienne base et la nouvelle lancées EN MÊME
  TEMPS, même charge) : **2 057 s → 1 519 s** (−26 %), mêmes verts et mêmes rouges des deux côtés.
  Les plus gros : `test_chantiers` 140 → 49 s, `test_nord` 47 → 13, `test_carte` 79 → 42,
  `test_devantures` 52 → 18, `test_routes` 30 → 0.
- ⚠️ **Restent en génération directe, avec un ⚠️ qui dit pourquoi** : tout juge qui patche le jeu avant
  de bâtir (le cache ne voit pas le patch — la ville « avec », bâtie avant le patch, passe par le
  cache), les juges de déterminisme (`generer() == generer()` doit en bâtir deux), les sous-processus,
  les espions (`test_terrains_vagues`, `test_commerce_a_la_mesure`), et
  `test_aeroport::…l_aerogare…`, qui exige `is` (une copie n'est jamais le même objet).
- ⚠️ Deux fichiers ont déjà une fixture `villes` (mobilier, quartiers) : le module y est importé
  `villes as villes_gardees`.
- Ce que la vague B ne règle pas : le coût vient maintenant surtout des **bancs** (Node) —
  `test_missions_en_scene_js` (≈ 1 000 s), `test_interpretation` (ffmpeg), `test_moteur_js` :
  c'est la vague C.

Rouges sur `dev` au moment d'atterrir, tous rejoués sur la base d'avant (aucun de cette vague) :
`test_interieurs::…lieux_des_missions…` (`villa_chemin`), `test_rang::…trois_blocs…` (la villa),
`test_quai_se_marche` (friche enfermée), `test_missions_en_scene_js` ×10 (v01, v02),
`test_parole::…la_rue_se_tait…`, `test_velos_js[23]` (HORS VOIE autobus), et les deux du ciné-parc.

**Vague C livrée le 29 sept. 2026** — les doublons retirés, les bancs fusionnés. Cinq lots, 48 commits,
75 fichiers de juges. Deux gestes, deux preuves : **un retrait** nomme le juge qui tient encore la règle
(et ce qui était propre au retiré y est déplacé d'abord) ; **une fusion** garde chaque assertion et son
message, remet l'état entre les scénarios, et se prouve par une mutation du jeu qui casse un scénario qui
n'est PAS le premier — le juge fusionné rougit avec le bon message. Les noms des juges restent quand ils
disent des règles différentes : une fixture de module joue le banc une fois, chaque juge lit sa part.

- **Mesure appariée** (les 75 fichiers, `dev` d'avant et d'après lancés EN MÊME TEMPS) : **3 344 s →
  2 576 s** (−23 %), les trois mêmes rouges des deux côtés ; 7 243 cas → 4 899.
- **Les scènes** (`test_missions_en_scene_js`, le goulot) : un banc par mission au lieu d'un par cas —
  **482 bancs → 58**, 930 s → 346 s. Chaque scénario repart d'une partie neuve (`neuve()`). Relevé
  comparé de ce que voyaient les 423 juges avant et après : identique (à ±2 images près sur la durée
  d'une scène, le pas fixe du banc).
- **Le son** : une passe ffmpeg par fichier, lue par les quatre juges (`test_audio` ≈ 600 → 216
  sous-processus, `test_interpretation` ≈ 3 300 → 2 310, et 4 081 cas → 1 774). ⚠️ Un graphe ffmpeg à
  trois branches dont une coupée (`atrim`) figeait ffmpeg 8 environ 4 fois sur 2 200 : le niveau reste
  une passe à part, les graphes gardés ont un délai de 60 s et une relance.
- **Les défis** : `test_defis_graduels_js` 75 → 43 bancs (364 → 215 s) ; les trois joueurs d'une épreuve
  dans un banc. ⚠️ Fusionnés, les essais tombaient pour une autre raison (« PAS SANS CHAR ») : mille images
  plus tard, le trafic arrivait sur la piste — il est retiré à chaque image, et la raison du raté se lit.
- **Le moteur** : `test_moteur_js` 185 → 179 juges, ≈ 181 → 163 bancs ; le sprint devient du Python pur,
  la borne-fontaine passe dans `test_carte` (une aide `_coins_des_feux` commune avec les lampadaires).
- ⚠️ **Deux juges verts par chance de graine, démasqués par la fusion** : les prises des techniques
  (la graine 2 donnait un enfant, qu'on ne saisit pas — le corps est maintenant nommé, une graine posée
  par scénario, dix graines passent) ; et le paramètre `raison` du frein pile, jamais lu.
- **Refusés après mesure** (l'audit se trompait) : `greve()` du banc de la plage coûte 2 ms ; les sondes
  de rythme du navigateur 0,4 s ; `magasins` (24 lettres = 95 px, plus strict que la bulle) ; `port`
  (l'autre juge ignore les petits quais) ; le chrono du hockey et le mode photo (raccourcir changerait la
  règle) ; `…laisse_finir_ses_repliques` (seul à exiger trois voix et leurs mp3).

Rouges au moment d'atterrir, les mêmes avant et après : `test_debug_js::…portes_des_blocs…` (ciné-parc),
`test_defis_graduels_js::test_l_esquive_se_gagne_sans_frapper` (« IL T'A SONNÉ » après 46 roulades),
`test_velos_js[23]` (HORS VOIE autobus).

**Vague D livrée le 29 sept. 2026** — le rangement. Un juge déplacé reste le même juge : **6 647 noms
collectés avant, 6 647 après, `diff` vide** ; chaque fichier touché passe (1 255 verts, le seul rouge
est celui du ciné-parc, d'avant).

- **`test_moteur_js.py` découpé** (8 960 lignes, 179 juges ; ses sections mentaient) : il garde le socle
  (10 juges : API, sprites, ville reçue, sauvegarde, singe, son sans audio, cache) ; neuf fichiers neufs —
  `test_conduite_js` (25), `test_trafic_js` (21), `test_boulots_js` (9), `test_commerces_js` (21),
  `test_pietons_js` (14), `test_combat_js` (13), `test_hud_js` (24), `test_coop_js` (12), `test_monde_js`
  (13) — et des juges rendus à leur fichier : la police (+7), les portes et fondus (`test_interieurs_js`,
  +8), la musique (`test_son_js`, +2), les lampes (`test_la_nuit`, +2). Un script a retrouvé les 189
  définitions, texte pour texte ; chaque fixture de module est partie avec tous ses juges.
- **Les petites paires** : `test_garage`, `test_brouillard`, `test_canton_js`, `test_saint_jean`, `test_loto`
  rejoignent leur jumeau ; `test_viser_a_la_gachette_js` → `test_manette_js` ; `test_trois_defauts_js`
  dispersé (histoire, interactions) ; les nids-de-poule de `test_ville_vit` → `test_nids_de_poule_js` ;
  l'hôpital sort des distributrices (`test_hopital.py`, `test_hopital_js.py`).
- **Les outils des missions** : `tests/outils_missions.py` (`outils(*noms, plafond=100)`, `OUTILS`,
  `PLUS_LONGUES`) — les aides identiques mot pour mot dans au moins deux fichiers ; celles qui avaient
  divergé (`boite`, `hommes`, `chemin`, deux `paiements`…) restent locales : les aligner changerait ce que
  les juges regardent. Les deux fichiers du tronc n'en font qu'un (`test_tronc_plus_long_js`).
- ⚠️ Le garde d'écriture de Claude Code lit la carte du dépôt PRINCIPAL, pas celle du worktree : un
  fichier neuf créé dans un worktree peut être refusé alors que sa carte est à jour. Le vérificateur lancé
  DANS le worktree fait foi.

**Le jalon est livré.** Ce qui reste — les deux rouges honnêtes de la vague A (le kiosque sur l'allée,
l'empreinte des chars) — a sa ligne au plan : « Les juges : deux rouges honnêtes à trancher ».

