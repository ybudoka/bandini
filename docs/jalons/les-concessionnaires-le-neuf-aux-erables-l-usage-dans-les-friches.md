# Les concessionnaires : le neuf aux Érables, l'usagé dans les Friches

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un vendeur de voitures neuves dans un quartier riche avec plusieurs
voitures dans le stationnement et un vendeur de voitures usagées dans un quartier plus pauvre ou industriel ».

**Tranché avec Martin le même jour** :

- **On achète ET on vole.** Un vendeur au comptoir vend les chars du lot ; le char payé est à toi (`aToi`) et y
  monter n'est pas un vol. Le prendre sans payer en est un.
- **Les lieux** : le neuf aux **Érables** (le cossu), l'usagé dans les **Friches** (la bande nord, pauvre et
  industrielle).
- **Les noms** : **Prestige Automobiles** (le neuf) et **Chez Ti-Pout — Autos usagées** (l'usagé).

### Ce que ça donne

**Prestige Automobiles, aux Érables.**
- ⚠️ **Pas la quincaillerie**, pourtant proposée d'abord (et acceptée) : c'est la SEULE porte `artisan` de la ville
  d'avant, et `f04` (le couteau) et `p01` (la batte) y envoient acheter ; `test_chaque_famille_de_commerce_ouvre_une_porte`
  la garde. Et la rangée commerçante des Érables n'a que deux portes (la quincaillerie, le lave-auto), toutes deux
  uniques ; le troisième îlot est la cour des Chevreuils.
- **La place** : le **stationnement de l'îlot `mm<mm`** (rangée 3, tout cossu), deux rangées de neuf cases (`^` au
  nord, `v` au sud, îlots `I`) avec leur allée — mesuré le 28 sept. 2026 à x 56-66, y 168-174 de la ville finie.
  Le salon se **bâtit sur la moitié sud** (les cases `v`), sa façade vitrée sur la rue du sud ; la moitié nord
  reste le **lot d'exposition** (neuf places, l'allée comprise). Le lot se trouve par une MESURE (le plus grand
  stationnement d'un îlot cossu des Érables), jamais par un tirage ni par des coordonnées écrites en dur.
- **Dedans** : des vitrines, un char en montre si la pièce le permet (sinon un podium vide et une plante), un
  bureau, et le vendeur en complet derrière son comptoir. La pièce à la mesure du bâtiment.
- **L'enseigne** cossue (lettres dorées, `COMMERCES_COSSUS`).
- **Le stock** : berline neuve, sport, cabriolet, luxe, au prix du catalogue (`vehicules.CATALOGUE`, 600 à 5 200 $),
  pleine vie ; l'**alarme** sur TOUS les chars du lot, la berline comprise.

**Chez Ti-Pout, dans les Friches.**
- **La place** : une cour de gravier grillagée **contre une rue** (les terrains vagues des Friches sont au milieu
  de l'herbe, loin du trottoir), avec une trouée dans le grillage pour sortir ; mesurée comme au Salon.
- **Une roulotte-bureau** (une petite pièce : un bureau, une chaise, la cafetière, Ti-Pout en chemise), des
  fanions, une pancarte « FINANCEMENT FACILE ».
- **Le stock** : compacte, familiale, camionnette, un vieux camion, en couleurs délavées, **60 % de vie**, environ
  **40 % du prix du catalogue** ; aucune alarme.

**Acheter.** Au comptoir, un menu liste les chars du lot (modèle, couleur, prix). Payer (`payer`) rend le char
dehors `aToi` ; on sort, on embarque. Le garder d'une partie à l'autre, c'est le garer à la planque
(`sauvegarderPartie`, déjà là). La place vidée se remplit **le lendemain** ; le stock du jour se calcule par
empreinte (le jour et la place), sans dé.

**Voler.** Monter dans un char du lot sans payer = `vol_vehicule` ; l'alarme chez le neuf, rien chez l'usagé.

### Les vagues

1. **Les deux lots et leurs chars** : le Salon bâti, la roulotte posée, les chars du lot qui naissent et se
   volent (l'alarme au neuf). Jouable seul : Martin voit les lots et peut voler.
2. **Le comptoir et l'achat** : les deux menus, `aToi`, le lot qui se remplit le lendemain.

### ⚠️ Ce que ça touche (à relire avant de coder)

- **Poser sur la ville finie, en dernier, sans dé** — la recette du lot du poste (`poser_les_lots_et_les_rideaux`)
  et du dojo : un module `app/concessionnaires.py`, appelé par `carte.generer` après `enseignes.poser` pour le
  Salon, et après `canton.poser` (dans `nord.poser`) pour les Friches. Ce qui s'y était posé (décor, lampe) s'en
  va ; `ville["sol"]` réécrit sur les seules rangées touchées. La clé neuve de `ville` va dans `nord.DECALAGES`
  (mémoire « La carte descend sous la bande nord »).
- **Bâtir un bâtiment neuf** (le Salon) sur la ville finie : toit, façade, porte, `toits`, `portes`,
  `devantures`, `points_interet`, et la pièce dans `interieurs`. La pièce à la mesure du bâtiment
  (`test_la_piece_a_les_mesures_de_son_batiment`).
- **Les juges « ne déplace rien »** (dojo, enseignes, carrosseries, canton, aéroport, relief…) : les comparer sans
  le module, un dé par choix (mémoire « Juges ce module ne déplace rien »).
- **Les chars du lot en JS** : le modèle de `majGaresDeService` — couleur donnée (sinon `B.rng` décale tout),
  silhouette forcée (`options.sprite`), nés dans la bulle, un marqueur à eux, et **exclus du compte des chars
  garés** (sinon les dés de `peupler` glissent ; `test_poste_et_garage_js`, `test_cabriolet_js`, `test_la_nuit_js`).
- **Les Friches touchent la bulle de naissance du terminus** (le Petit-Canton y est) : les juges qui tiennent par
  une graine (mémoire « Juge vert par chance de graine »).
- **Le poids du paquet** (`test_le_paquet_reste_leger`, `test_definitions`).
- **Voir avant de livrer** : une capture du Salon et de la cour (mémoire « Regarder une couche peinte »), et un
  juge joué au banc (acheter puis embarquer ; voler et entendre l'alarme).

### Plan d'exécution — vague 1 (les deux lots et leurs chars)

**But** : Prestige Automobiles bâti sur la moitié sud du stationnement cossu des Érables, Chez Ti-Pout posé contre le
boulevard au pied des Friches, et leurs chars qui naissent dans la bulle, se volent, et sonnent chez le neuf.

**Architecture** : un module `app/concessionnaires.py` à deux entrées — `poser_le_salon(chantier, ville)` (appelé par
`carte.generer` après `ouvrir_les_rues`, AVANT `nord.poser` : le Salon est dans la ville d'avant et descend avec
elle) et `poser_ti_pout(ville)` (appelé APRÈS `nord.poser` : la cour est dans la bande). Chacun MESURE sa place sur
la ville finie, sans un dé, écrit ses tuiles dans `ville["sol"]`, et ajoute un lot à `ville["concessionnaires"]`
(liste). Côté JS, `Vehicules.majLotsDeConcession()` fait naître les chars du lot sur le modèle de
`majGaresDeService`.

**La donnée d'un lot** (Python décide, JS calcule) :
```python
{"slug": "prestige", "nom": "Prestige Automobiles", "genre": "neuf",
 "places": [{"x": 56, "y": 168, "sens": "N"}, ...],   # y = la tuile du NEZ, comme au poste
 "garees": [0, 1, 2, 3, 5, 6, 7, 8],                    # la place devant la porte reste libre
 "stock": [{"slug": "sport", "sprite": "sport"}, ...],  # un par place, même ordre
 "usure": 1.0, "alarme": True,
 "cour": {"x": 56, "y": 168, "l": 9, "h": 9}}           # le rectangle touché, pour les juges
```

**Constantes** (`app/concessionnaires.py`) :
- `SALON_SLUG = "prestige"`, `SALON_NOM = "Prestige Automobiles"`, `SALON_ENSEIGNES = ("PRESTIGE AUTOMOBILES",
  "PRESTIGE AUTOS", "PRESTIGE")` (la première qui `tient_en` le bandeau), `SALON_CASES_MIN = 6`,
  `SALON_PROFONDEUR = 4` (trois rangées de toit d'ardoise `E`, une de façade).
- `NEUFS = (("sport", "sport"), ("luxe", "luxe"), ("auto", "auto"), ("luxe", "luxe_vus"), ("auto", "auto_familiale"))`
  — ⚠️ pas le cabriolet : il a sa conductrice (`au_volant`).
- `TI_POUT_SLUG = "ti_pout"`, `TI_POUT_NOM = "Chez Ti-Pout — Autos usagées"`, `TI_POUT_ENSEIGNES = ("TI-POUT AUTOS",
  "TI-POUT")`, cour `TI_POUT_L, TI_POUT_H = 16, 8`, `USURE_USAGEE = 0.6`.
- `USAGES = (("auto", "auto_compacte"), ("auto", "auto_familiale"), ("camion", "camion"), ("auto", "auto_camionnette"),
  ("auto", "auto"))`.

**Global** : aucun `Des` dans le module (juge) ; `uv run ruff check .` avant tout commit ; pytest avec
`UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv` ; commits dans le worktree, rangés sous
`refs/wip/concessionnaires`.

**Ce qui guette** (les juges à ajouter, chacun dans sa tâche) :
1. Une ville (une autre graine) sans stationnement qui convient : pas de Salon, et rien ne plante (tâche 1).
2. Un char du lot compté comme char garé de la rue : les dés de `peupler` glissent (tâche 3).
3. Un char du lot qui naît sous les yeux du joueur (tâche 3).
4. Le lot volé puis abandonné : il ne se regarnit pas tant que le char existe, et ne double pas (tâche 3).
5. La porte du Salon ou de la roulotte qui s'ouvre sur un mur ou un char (tâche 1, 2 : le devant marchable et libre).

#### Tâche 1 — Prestige Automobiles, bâti sur le stationnement des Érables

**Fichiers** : créer `app/concessionnaires.py`, `tests/test_concessionnaires.py` ; modifier `app/carte.py` (l'appel
dans `generer`, juste après `ouvrir_les_rues(ville)`, avant le bloc `if nord`), `app/nord.py` (`DECALAGES` :
`"concessionnaires": _y` — `_y` descend à toute profondeur).

- [ ] **Juges d'abord** (`tests/test_concessionnaires.py`) :
  - `test_le_salon_est_aux_erables_en_cossu` : `ville = carte.generer()` ; le lot `prestige` existe ; sa porte
    (`interieur == "prestige"`) est dans `erables` et `cossu` par `nord.LECTEUR.district_en/standing_en` ; la pièce
    `prestige` est dans `ville["interieurs"]` avec un `commis`.
  - `test_le_lot_du_salon_est_garni` : `len(garees) >= 6` ; chaque place est un `^` ET la tuile sous elle aussi
    (`sol[y][x] == sol[y + 1][x] == "^"`) ; aucune place devant la porte n'est garnie.
  - `test_le_stock_du_neuf` : chaque `stock[i]["slug"]` est dans `{"sport", "luxe", "auto"}`, `usure == 1.0`,
    `alarme is True`.
  - `test_le_salon_ne_tire_aucun_de` : comme `test_devants.test_le_deplacement_ne_tire_aucun_de` —
    `mock.patch.object(carte.Des, "suivant"/"chance"/"entier", side_effect=AssertionError)` pendant
    `concessionnaires.poser_le_salon`.
  - `test_le_salon_ne_deplace_rien` : `avec = carte.generer(nord=False)`, puis `poser_le_salon` neutralisé,
    `sans = carte.generer(nord=False)` ; toutes les clés égales en JSON sauf `sol`, `portes`, `devantures`,
    `interieurs`, `points_interet`, `concessionnaires`, `decor`, `lampes` ; `avec["portes"][:len(sans["portes"])] ==
    sans["portes"]` (on AJOUTE au bout) ; les rangées de `sol` qui diffèrent sont toutes dans `cour`.
  - `test_sans_stationnement_pas_de_salon` : `monkeypatch.setattr(concessionnaires, "SALON_CASES_MIN", 99)` →
    aucun lot `prestige`, aucune porte `prestige`, et `generer` passe.
- [ ] Les lancer : rouges (`ModuleNotFoundError`).
- [ ] **`trouver_le_salon(chantier, ville)`** : parcourir `ville["sol"]` ; une rangée de `^` d'au moins
  `SALON_CASES_MIN`, dont la rangée du dessus N'EST PAS `^` (c'est le nez) et celle du dessous l'est (la case fait
  deux) ; sous elle, `ALLEE` rangées ou plus de `p` sur toute la largeur (l'allée) ; sous l'allée, `SALON_PROFONDEUR`
  rangées sans rien de solide (`carte.solidite(g) == 0`, pas de porte) — là se bâtit le Salon ; la rangée d'après
  marchable sur toute la largeur (`_`, `.` ou `,`) — c'est le devant. District `erables` et standing `cossu` par
  `chantier.district_en` / `chantier.standing_en` au milieu de la rangée. Clé de choix : `(-largeur, y, x)` — la
  plus longue rangée, puis la plus au nord, puis la plus à l'ouest.
- [ ] **`poser_le_salon(chantier, ville)`** : rien trouvé → `return`. Sinon, sur `largeur` colonnes à partir de `x0` :
  trois rangées `E`, puis la façade `F` + `W…` + `D` + `W…` + `F`, porte au milieu (`px = x0 + largeur // 2`) ;
  retirer de `ville["decor"]` et de `ville["lampes"]` ce qui tombe dans le bâtiment ou sur la tuile devant la porte ;
  ajouter la porte `{"x": px, "y": yf, "interieur": "prestige", "lieu": "prestige", "nom": SALON_NOM, "vitrine":
  [x0, largeur]}`, la devanture `{"x": x0, "y": yf, "l": largeur, "genre": devantures.genre_index("commerce"),
  "texte": <première de SALON_ENSEIGNES qui tient_en>, "pancarte": -1, "motifs": <la façade>, "porte": px - x0}`,
  le point `{"type": "prestige", "slug": "prestige", "nom": SALON_NOM, "x": px, "y": yf + 1, "famille":
  "magasin"}`, la pièce `piece_de_salon("prestige", largeur, SALON_PROFONDEUR, px - x0)`, et le lot (places sur la
  rangée de `^`, `garees` = toutes sauf celle en face de `px`, `stock[i] = NEUFS[i % len(NEUFS)]`).
- [ ] **`piece_de_salon(slug, largeur, hauteur, porte)`** sur le modèle de `carte.piece_de_dojo` : le fond en
  vitrines de montre (`n` plantes aux coins), un bureau (`a`) et sa chaise (`h`) du côté opposé à la porte, le
  comptoir (`c`, trois tuiles) à l'avant-dernière rangée, le `commis` derrière (`carte._quelqu_un`),
  `carte._plan_de(grille, porte)`, `carte._piece(slug, SALON_NOM, …, sol="t")`.
- [ ] Brancher dans `carte.generer` (`if plan == PLAN: concessionnaires.poser_le_salon(chantier, ville)`, après
  `ouvrir_les_rues`) ; `ville.setdefault("concessionnaires", [])` avant ; `DECALAGES`.
- [ ] Verts : `pytest tests/test_concessionnaires.py tests/test_carte.py -k "salon or piece_a_les_mesures or
  concession" tests/test_nord.py tests/test_dojo.py tests/test_enseignes.py tests/test_devantures.py` ; ruff.
- [ ] Commit `feat: Prestige Automobiles — le salon des Érables et son lot (concessionnaires, vague 1)`.

#### Tâche 2 — Chez Ti-Pout, contre le boulevard au pied des Friches

**Fichiers** : `app/concessionnaires.py`, `tests/test_concessionnaires.py`, `app/carte.py` (l'appel juste après
`nord_mod.poser(ville)`).

- [ ] **Juges** :
  - `test_ti_pout_est_dans_les_friches` : le lot `ti_pout` existe ; sa porte est dans `friches` et `pauvre`.
  - `test_la_cour_de_ti_pout` : le tour de la cour est du grillage `f`, sauf une trouée de cinq tuiles au sud qui
    donne sur du marchable ; chaque place est sur `g` (les deux tuiles de la case) ; `len(garees) >= 5` ;
    `stock` dans `{"auto", "camion"}`, `usure == 0.6`, `alarme is False`.
  - `test_ti_pout_ne_tire_aucun_de` et `test_ti_pout_ne_deplace_rien` (comme à la tâche 1, sur `generer()` avec la
    bande, en neutralisant `poser_ti_pout`) ; ⚠️ la cour se choisit SANS décor ni lampe dedans : `decor` et `lampes`
    doivent être égaux, eux aussi.
  - `test_la_ville_d_avant_n_a_pas_ti_pout` : `generer(nord=False)` → aucun lot `ti_pout`.
- [ ] **`poser_ti_pout(ville)`** : `n = ville["decalage_nord"]`, la zone `friches` de `ville["zones"]` ; la cour
  fait `TI_POUT_L × TI_POUT_H`, sa dernière rangée est `n - 1` (contre le trottoir du boulevard, rangée `n`) ;
  candidats : chaque `x` de la zone où tout le rectangle est de l'herbe `,`, sans décor ni lampe dedans ; clé
  `abs(milieu de la cour - milieu de la zone)`, puis `x`. Dessin (rangées `r0` à `r7` depuis le haut) : le sol en
  `g` ; le tour en `f` (haut, deux côtés, bas) sauf la trouée `x0 + 9 .. x0 + 13` en bas ; la roulotte en `x0 + 1 ..
  x0 + 5`, `r1-r2` toit de tôle `B`, `r3` façade `FWDWF` (porte en `x0 + 3`) ; places nez au sud en `r1-r2` à
  `x0 + 8, 10, 12, 14` (`y = r2`, `sens "S"`) et nez au nord en `r5-r6` à `x0 + 2, 4, 6` (`y = r5`, `sens "N"`).
  Porte, devanture (`genre_index("industrie")`), point (`famille: "magasin"`), pièce `piece_de_roulotte` (le bureau,
  la chaise, la cafetière en `z`, Ti-Pout en `commis`), lot (`garees` = toutes, `stock[i] = USAGES[i % len]`,
  `usure: USURE_USAGEE`, `alarme: False`).
- [ ] Brancher après `nord_mod.poser(ville)` ; verts (+ `tests/test_canton.py tests/test_nord.py
  tests/test_devants.py`) ; ruff ; commit `feat: Chez Ti-Pout — la cour d'usagés des Friches (concessionnaires,
  vague 1)`.

#### Tâche 3 — Les chars du lot, au banc

**Fichiers** : `static/js/vehicules.js` ; créer `tests/test_concessionnaires_js.py`.

- [ ] **Juges** (modèle : `tests/test_poste_et_garage_js.py`, fixtures `banc` et `paquet`) :
  - `test_les_chars_du_salon_naissent_hors_champ_sans_de` : le joueur devant le lot (sous les yeux) → aucun char
    après 80 images ; à 330 px de côté (hors champ) → `majLotsDeConcession()` en comptant `B.rng` → `des == 0` et
    `nees == garees.length` ; chaque char : le slug et la silhouette du stock, `etat 'stationne'`, pas de
    conducteur, à cheval sur sa case.
  - `test_les_chars_du_lot_ne_comptent_pas_comme_gares` : après `peupler` avec le lot garni, le compte de
    `stationnes` est celui d'une ville sans lot (le juge compte les chars sans `placeDeLot`).
  - `test_voler_un_neuf_sonne_voler_un_usage_non` : `Vehicules.monter(j, v)` sur la berline du Salon →
    `v.alarme > 0` et `v.vole` ; sur une minoune de Ti-Pout → `v.alarme === 0`, `v.vole`, `v.vie ≈ 0.6 × vieMax`.
  - `test_un_char_pris_ne_se_double_pas` : on monte, on roule 200 px, `majLotsDeConcession()` → 0 né pour cette
    place tant que le char existe.
- [ ] **`majLotsDeConcession()`** à côté de `majGaresDeService` : pour chaque lot de `Monde.carte.def.concessionnaires`,
  chaque place de `garees` dans la portée (`trafic().oubli_px - GAREES_MARGE`), sans char `placeDeLot === place`,
  hors champ (`Entites.visibleAEcran(x, y, 24)`) et libre (`libreAutour(x, y, 12)`) : `creer(stock.slug, x, y,
  angle, { etat: 'stationne', couleur, sprite: stock.sprite })` ; `v.placeDeLot = place` ; `lot.usure < 1` → `v.usure`
  et `v.vie` comme `user()` ; `lot.alarme` → `v.alarmeDuLot = true`. La couleur SANS DÉ : `def.couleurs[(i * 3 + 1) %
  n]`, et chez l'usagé délavée (mêlée à `#9a968a`, 40 %) par une petite fonction `delaver(hex)`.
- [ ] `peupler` : `if (v.placeDeLot && v.etat === 'stationne' && !v.laisse) continue;` à côté de `gareDeService`, et
  l'appel `majLotsDeConcession()` après `majGaresDeService()` ; `monter` : `(v.def.alarme || v.alarmeDuLot) &&
  declencherAlarme(v)` ; l'export.
- [ ] Verts : `tests/test_concessionnaires_js.py tests/test_poste_et_garage_js.py tests/test_cabriolet_js.py
  tests/test_la_nuit_js.py` ; `node --check` ; commit `feat: les chars des concessionnaires naissent, se volent, et le
  neuf sonne`.

#### Tâche 4 — Voir, puis atterrir

- [ ] Capture Playwright du Salon et de la cour (mémoire « Capturer une pièce du jeu ») ; la regarder ; l'ouvrir pour
  Martin dans Aperçu (`captures/`).
- [ ] `docs/carte.md` (l'inventaire : les deux lieux), `docs/architecture.md` (`app/concessionnaires.py` dans la carte
  du dépôt), la note de la vague 1 sous « Notes ».
- [ ] Juges ciblés + ruff verts → atterrir (`cherry-pick` sur `dev` à jour, `merge --ff-only`), pousser ; puis la
  suite complète (mémoire « Atterrir avant la suite complète »).

## Notes

### Les deux vagues ensemble (28 sept. 2026)

Livrées d'un coup : `test_interieurs` refuse une pièce dont le comptoir ne donne rien (« une porte qu'on ouvre pour
rien »), et le Salon sans son comptoir en était une. Le plan de la vague 1 a tenu, avec ces écarts :

- **La devanture fait 5 tuiles**, centrée sur la porte, sur les vitrines seulement (`ENSEIGNE_ETIREE`,
  `MOTIFS_CONNUS` : pas les coins `F` de la façade) ; elle porte le `standing` du bloc et sa **lampe de
  vitrine** (`test_devantures`, `test_quartiers`). L'enseigne du Salon se raccourcit donc d'elle-même
  (`SALON_ENSEIGNES`, la première qui tient).
- **Les îlots `I` des cases `v`** qu'on a bâties redeviennent de la pelouse : un îlot ne se tient qu'au bout d'une
  rangée (`test_carte`). La `cour` du Salon déborde d'une colonne de chaque côté pour eux.
- **La roulotte a une façade toute vitrée** (`WWDWB`, la dernière placardée : les Friches sont pauvres) — c'est
  toute sa devanture.
- **Le comptoir du Salon est au fond**, loin de la porte : devant elle, il lui volait ACTION (`RAYON_POINT`).
- **Dedans, `Monde.carte` est la pièce** : le menu lit les lots dans `B.exterieur.carte` (mémoire « Monde.carte
  est le bloc »).
- **Un char acheté quitte son lot** (`placeDeLot = null`) : la place vendue reste vide le jour même
  (`partie.concession`, sauvegardé avec la partie) et se regarnit le lendemain, même s'il roule encore.
- **Les juges « ce module ne déplace rien »** de l'aéroport et des enseignes veulent LEURS ajouts au bout des
  listes : le Salon (posé après eux) y est neutralisé des deux côtés.

- **Huit juges de banc rougissaient avec le build seul** (la suite contre la base, rejoués un par un) — deux causes,
  deux leçons :
  - **Le décor ne se retire pas** : le Salon retirait le banc planté devant sa porte, et l'identifiant de tout le
    décor qui suit glissait (la police, les passants). La porte se pose maintenant sur la colonne la plus proche du
    milieu dont le devant est DÉJÀ libre ; le décor est identique à la base, au JSON près. En repli seulement,
    `devants._deplacer_le_decor`.
  - **Une porte au sol est un tirage** : `Monde.charger` relève les `d`/`D` dans l'ordre de lecture dans
    `portesFermees`, et un passant y tire sa porte par index (`entites.js`). La porte de Ti-Pout, en haut de la
    carte, décalait tous les tirages — même au terminus, à 1 200 px de là. Les portes des lots (`lot.porte`) n'y
    entrent pas : personne ne sort d'un concessionnaire, et la ville se tire comme avant.

Juges : `test_concessionnaires.py` (13), `test_concessionnaires_js.py` (8) — dont quatre mutations vues rouges (la
place libre devant la porte, `alarmeDuLot`, `compteCommeGare`, les portes tirées).

### Relecture finale (agent neuf) et ce qui reste

Corrigés, chacun par un juge vu rouge : un char payé garé à la planque redevenait un vol au rechargement (la
sauvegarde gardait `vole`, pas `aToi` — la fourrière avait le même trou) ; un passant pouvait voler le char qu'on
venait de payer, et les neufs du lot sans alarme (`majVolDeChar`) ; une façade de six tuiles faisait planter
l'enseigne (`min()` vide).

**À trancher par Martin :**
- **Un char payé s'oublie** comme tout char laissé loin (`peupler` ne protège que celui qu'on conduit) : payer
  5 200 $ puis s'éloigner de 560 px, et il disparaît — la place vendue ne se regarnit que le lendemain. Le
  protéger (`aToi` dans `peupler`), ou le dire au comptoir ?
- **Voler au lot puis revendre chez Ti-Guy** : une place volée se regarnit dès que le char est oublié, sans
  attendre le lendemain — une source de luxe à 5 200 $, freinée seulement par `vente_malus_doublon`.

**Reportés (mineurs)** : un char de la rue peut se garer sur une case vide du lot du Salon (`placeStationnee`
lit ses `^`) ; la place « en face de la porte » ne sert à rien, la porte donne au sud et le lot est au nord ;
un char cabossé ou poussé se vend plein prix ; le camion de Ti-Pout (40 px) mord de 4 px dans le grillage nord ;
`x0 - 1` hors bornes si un lot touchait le bord ouest ; le stock est fixe par place (la fiche le voulait « du
jour », à l'empreinte).

**Et une ligne d'une autre session s'y branche** : « les 4 roues » veut en vendre chez le concessionnaire.
