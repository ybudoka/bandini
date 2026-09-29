# Les explosifs

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux des explosifs, C4, grenades, et plus ».

**Tranché avec Martin le même jour** :

- **Les quatre** : la **grenade**, la **dynamite**, le **C4** (et le **char piégé** qu'il permet), le
  **lance-roquettes**.
- **Ce qu'une explosion ouvre** : ce que casse déjà un char qui saute (les gens, les chars, le décor
  destructible) **et certains murs** — « mais juste certains murs ». Les murs **fissurés**, qu'on voit : dedans
  entre deux pièces (la villa du maire, la banque, les planques), dehors sur les murets et les enceintes (les
  entrepôts, la cour de la prison), et là où une mission en veut un. Tout autre mur reste plein.
- **Et le Molotov, en mieux** (ajouté par Martin en cours de séance) — les quatre à la fois : **les gens prennent
  feu**, **le feu se propage**, **il s'allume d'abord**, **plus gros et plus visible** — « je veux voir la
  bouteille voler ». Aujourd'hui (`combat.js`, `allumer`/`majBrasiers`) : une flaque de 20 px qui brûle 5 s et
  mord 12 PV/s à qui reste dedans ; un char dessus finit par brûler.

**Le cœur commun : une seule explosion.** L'explosion du char (`Vehicules.exploser`, `vehicules.js`) sort dans
`Explosions.faire(x, y, puissance, coupable)`, et toutes les bombes passent par elle : elle blesse et renverse les
gens (dégâts qui baissent avec la distance, comme aujourd'hui), abîme les chars (qui sautent à leur tour — la
chaîne), casse le décor (`Entites.decorAutour`), fait céder les murs fissurés du rayon, joue le son, secoue l'écran
et signale le délit `explosion` que la police connaît déjà (`police.js`, `DELITS_ARMES`). Le rayon et les dégâts
de chaque explosif sont dans `app/armes.py`, à côté de la flaque du Molotov (`REGLES`) ; le char garde les siens
(`vehicules.PHYSIQUE` : 60 px, 90 PV).

**Les vagues**, chacune jouable, jugée et livrée seule :

1. **Ce qui se lance** — le cœur commun, puis :
   - **la grenade** (marché noir) : part en cloche comme le Molotov, **rebondit** sur les murs et roule, saute au
     bout de sa mèche (2,5 s) ; tenir le bouton la **cuit** (la mèche brûle dans la main — on la lâche plus près
     de la fin) ;
   - **la dynamite** (ramassée sur les chantiers, et au marché noir, moins chère que la grenade) : mèche de 4 s,
     une étincelle qu'on voit et qu'on entend grésiller, portée courte, rayon plus gros.
2. **Le Molotov, en mieux** :
   - **il s'allume d'abord** : un premier appui allume le chiffon — on le voit flamber dans la main, il éclaire la
     nuit — et le suivant le lance ; ranger l'arme l'éteint ;
   - **on voit la bouteille voler** : son dessin tourne en l'air, son ombre file au sol et rétrécit quand elle
     monte, le chiffon laisse une traînée de flammes et de fumée ;
   - **plus gros, plus visible** : une flaque plus large qui dure plus longtemps, des flammes hautes, de la fumée
     noire, une lueur au sol la nuit ;
   - **les gens prennent feu** : un passant touché s'enflamme, court en hurlant, brûle quelques secondes et peut
     allumer ceux qu'il frôle ; le joueur aussi (se jeter à l'eau l'éteint, l'extincteur aussi) ;
   - **le feu se propage** : la flaque s'étale, et le feu gagne l'herbe sèche, les haies, le décor en bois (bancs,
     palettes, clôtures) et les chars voisins. ⚠️ **Borné** : un nombre de brasiers au plus, et chaque brasier né
     d'un autre vit moins longtemps — un parc ne doit pas brûler jusqu'au matin, ni le téléphone ramer.
3. **Les murs, et le C4** :
   - **le mur fissuré** : une tuile neuve, pleine, dessinée fissurée, qui ne cède qu'à une explosion et devient
     des gravats où l'on passe. Posé **en dernier et sans dé** (voir ⚠️) : dedans, dehors, et pour les missions ;
   - **le C4** (marché noir) : un appui le **pose** — au sol, sur un mur, **sur un char** (il le suit s'il
     roule) ; **tenir** le bouton fait tout sauter, trois charges au plus d'un coup.
4. **Les gros jouets** :
   - **le char piégé** : du C4 posé sur un char vide ; il saute quand quelqu'un le **démarre** — un passant, un
     gangster, un policier — ou à la télécommande. Pas de garage à bombes ;
   - **le lance-roquettes** (marché noir, l'arme la plus chère) : tire droit, la roquette saute à l'impact ; une
     roquette par chargeur, les munitions chères, la portée plafonnée à l'écran comme la carabine.

**Les sons** : des bruitages ElevenLabs neufs — la mèche qui grésille, la grenade qui rebondit, le bip du C4, la
roquette qui siffle, le chiffon qu'on allume, le passant qui brûle. L'explosion existe déjà (`Son.SFX.explosion`). La synthèse reste le filet.

**Les juges** : au catalogue (Python) — les prix qui montent, aucune portée au-delà de l'écran (`test_armes`), chaque
son au catalogue audio ; au banc (JS, joués) — la grenade saute au bout de sa mèche et pas avant, la cuire la fait
sauter plus tôt, le mur fissuré cède et **son voisin plein non**, le C4 suit le char qui roule, le char piégé saute
au démarrage et le coupable est le poseur, la roquette saute à l'impact ; le Molotov qu'on lance sans l'allumer
n'existe pas (le premier appui allume), le passant touché brûle et allume son voisin, le feu gagne la haie et **s'arrête**
(le nombre de brasiers plafonne), l'eau éteint le joueur. Et des captures — le mur fissuré entier puis en gravats, la
bouteille en l'air avec son ombre — avant de livrer (mémoire « Regarder une couche peinte »).

⚠️ **Ce que ça touche** (à relire avant de coder) :
- **Changer une tuile en cours de partie existe déjà** : `Monde.defoncer` (`monde.js`, le char lourd qui casse une
  clôture) et `Chantiers.appliquer` (`chantiers.js`) — mettre à jour `sol`, `solide`, `route`, `passage`,
  invalider les morceaux cuits **avec marge** (la façade lit ses voisines, l'ombre tombe au sud) et la mini-carte.
  ⚠️ `defoncer` refuse exprès les façades (« un trou dans un mur ouvrirait sur un toit ») : c'est pourquoi seul un
  mur fissuré cède — posé **là où il y a du sol des deux côtés**, et un juge le vérifie pour chacun.
- **Les index cuits au chargement** (`devantures`, `residences`, `toits`, les lampes de fenêtre, `portesParTuile`) :
  rien ne doit être posé sur un mur fissuré, sinon une enseigne flotte sur des gravats.
- **Un mur fissuré posé dans la ville la fait glisser** s'il consomme un dé ou grossit un lieu (mémoire « Grossir un
  lieu garanti déplace la ville ») : en dernier, sans dé, et les juges « ce module ne déplace rien » à relire. Dans
  la bande nord : ses dés à elle. Dans un bloc (la villa) : `Monde.carte` est le bloc.
- **Un trou ne se sauvegarde pas** (comme une clôture défoncée) : il se referme au rechargement — c'est voulu,
  ça rend le mur à la mission suivante.
- **Les objets posés au démarrage consomment des identifiants** (mémoire « Décor eager décale les identifiants ») :
  une charge de C4 ou une grenade naît en partie, jamais au chargement.
- **Le feu de bâtiment existe à part** (`incendies.js`, tiré à l'empreinte de l'heure, éteint à l'extincteur) : le feu
  du Molotov reste un feu de **brasiers** (des entités), il ne rallume pas les façades — sinon la ville cesse d'être
  la même pour deux joueurs à la même heure.
- **Le poids du paquet** : des armes et des sons de plus → `test_definitions` dans les juges ciblés.
- **L'enfer de la chaîne** : dix chars garés côte à côte qui sautent l'un l'autre dans la même image — l'explosion
  d'un char se fait à l'image suivante, pas dans la boucle de l'autre.

### Plan de la vague 1 : l'explosion commune, la grenade, la dynamite

> **Pour qui l'exécute :** une tâche à la fois, dans l'ordre ; chaque tâche finit par ses juges verts et un commit
> dans le worktree (jamais dans `~/dev/bandini`). Les cases `- [ ]` se cochent ici.

**But :** deux armes qu'on allume, qu'on tient (la mèche brûle dans la main) et qu'on lance, qui sautent au bout de
leur mèche par une explosion commune — la même que celle du char.

**Architecture :** un type d'arme neuf, `lance`, au catalogue Python (`meche` en images, `souffle` en px, `rebond`).
Un module neuf, `static/js/explosions.js` (`Explosions.faire`), où l'explosion du char (`Vehicules.exploser`) passe
désormais. Dans `combat.js`, une entité neuve `lance` (pas un `projectile` : elle rebondit, roule, a une mèche et
se dessine), et la mèche tenue en main (`j.enMain`).

**Outils :** Python 3 (catalogue, paquet), JS sans module (IIFE, `window.BANDINI`), juges `pytest` + banc Node
(`tests/banc.js`, fixture `banc`), `uv run`, `UV_PROJECT_ENVIRONMENT=~/dev/bandini/.venv` dans le worktree.

**Ce qui vaut pour toutes les tâches :**
- Les prix des armes achetables **montent dans l'ordre du catalogue** (`test_les_prix_montent_dans_l_ordre_d_achat`).
- Aucune portée au-delà de `VW / 2` = 240 px, et ça vaut maintenant aussi pour `lance`.
- Rien ne naît au chargement (les identifiants) ; rien ne tire `B.rng()` hors de ce qui bouge déjà.
- `uv run ruff check .` avant d'atterrir ; `test_definitions` dans les juges ciblés (le poids du paquet).
- Les chiffres : **grenade** 800 $, dégâts 110, souffle 48 px, mèche 150 images (2,5 s), rebondit ; **dynamite**
  650 $, dégâts 140, souffle 64 px, mèche 240 images (4 s), ne rebondit pas (elle tombe et roule un peu).

**Ce que les tâches doivent aussi tenir** (ce qu'aucune fiche ne dit, mais qu'un joueur fera) :
1. **Monter dans un char, passer une porte ou changer d'arme avec une mèche allumée** : elle tombe aux pieds, et
   saute quand même (jugé en tâche 3).
2. **Lancer à bout portant contre un mur** : elle rebondit vers soi, on doit courir (tâche 3).
3. **Lancer dans l'eau** : la mèche s'éteint, pas d'explosion (tâche 3).
4. **Dix chars garés côte à côte** : ils sautent en chaîne, un par image, jamais dans la boucle d'un autre (tâche 2).
5. **La triche « munitions »** : allumer ne vide pas le sac, comme pour les armes à feu (tâche 3).

#### Tâche 1 : le catalogue — `lance`, la grenade, la dynamite

**Fichiers :** `app/armes.py`, `app/magasins.py` (`MARCHE_NOIR`), `tests/test_armes.py`.

**Produit :** trois clés neuves sur chaque `Arme` — `meche: int` (images, 0 = aucune), `souffle: int` (rayon de
l'explosion en px, 0 = aucune), `rebond: bool` ; `TYPES = ("melee", "tir", "jet", "lance")` ;
`REGLES["explosion"] = {"bruit_tuiles": 30, "gravite": 0.12, "rebond_amorti": 0.45, "roule_friction": 0.9}`.

- [ ] **Juges d'abord**, dans `tests/test_armes.py` :

```python
def test_ce_qui_se_lance_a_sa_meche_et_son_souffle():
    """La grenade et la dynamite : on les allume, la mèche brûle, elles sautent.
    La grenade rebondit, la dynamite non ; la dynamite coûte moins cher, souffle plus large."""
    lancees = [a for a in armes.CATALOGUE if a["type"] == "lance"]
    assert sorted(a["slug"] for a in lancees) == ["dynamite", "grenade"]
    for a in lancees:
        assert a["meche"] > 0 and a["souffle"] > 0 and a["cloche"] is True, a["slug"]
        assert a["bruit"] == 0, "le bruit est celui de l'explosion (REGLES), pas du lancer"
    g, d = armes.par_slug("grenade"), armes.par_slug("dynamite")
    assert g["rebond"] is True and d["rebond"] is False
    assert d["prix"] < g["prix"] and d["souffle"] > g["souffle"] and d["meche"] > g["meche"]
    for a in armes.CATALOGUE:
        if a["type"] != "lance":
            assert a["meche"] == 0 and a["souffle"] == 0 and a["rebond"] is False, a["slug"]
    assert armes.REGLES["explosion"]["bruit_tuiles"] > armes.par_slug("carabine")["bruit"]


def test_le_marche_noir_vend_ce_qui_saute():
    from app import magasins

    mn, gus = magasins.MARCHE_NOIR, magasins.par_slug("armurerie")
    for slug in ("grenade", "dynamite"):
        assert slug in mn["articles"] and slug in mn["munitions"], slug
        assert slug not in gus["articles"], f"{slug} : pas de vitrine chez Gus"
```

  et dans les juges existants : `test_aucune_portee_ne_depasse_ce_que_l_ecran_montre` juge
  `a["type"] in ("tir", "lance")` ; `test_les_regles_des_armes_voyagent` ajoute `"meche", "souffle", "rebond"` à sa
  liste de clés.
- [ ] **Les voir rougir** : `uv run pytest -q tests/test_armes.py` → `KeyError: 'meche'` / liste vide.
- [ ] **Le catalogue** : `_a(..., meche=0, souffle=0, rebond=False)` passés à `Arme(...)`, les trois clés dans le
  `TypedDict`, et la docstring du module dit ce qu'est `lance`. Les deux entrées, **dynamite entre le fusil
  (600) et le Molotov (700), grenade entre le Molotov et la mitraillette (900)** :

```python
    # « Ils sont derrière le mur. » Elle part en cloche, TOMBE et roule un peu —
    # elle ne rebondit pas — et saute au bout d'une mèche qu'on voit grésiller.
    # Moins chère que la grenade, plus lente, un souffle plus large. On en trouve
    # aussi sur les chantiers (`chantiers.js`). ⚠️ `bruit` 0 : ce qu'on entend,
    # c'est l'EXPLOSION (`REGLES["explosion"]`), pas le lancer.
    _a("dynamite", "Dynamite", "lance", 140, 110, 45, 650, chargeur=3, munitions_max=6,
       vproj=3.0, cloche=True, prix_munitions=90, etoiles=1, son="meche", meche=240, souffle=64),
    # « Ils sont au coin. » Elle rebondit sur les murs et roule ; la mèche
    # (2,5 s) brûle DÈS qu'on l'allume : la tenir, c'est la « cuire ».
    _a("grenade", "Grenade", "lance", 110, 150, 40, 800, chargeur=3, munitions_max=9,
       vproj=3.6, cloche=True, prix_munitions=120, etoiles=1, son="meche", meche=150, souffle=48,
       rebond=True),
```

  et `REGLES["explosion"]`, commenté (le bruit en tuiles : on entend une explosion de plus loin qu'une carabine).
  `MARCHE_NOIR["articles"]` et `["munitions"]` : ajouter `"dynamite"` et `"grenade"`.
- [ ] **Vert** : `uv run pytest -q tests/test_armes.py tests/test_magasins*.py tests/test_definitions.py`. ⚠️
  `test_chaque_arme_a_son_son` rougira (pas de son `meche`), comme `test_chaque_arme_qu_on_tient_a_son_dessin` (pas
  de dessin) : ils se règlent en tâches 4 et 5 — les marquer ici comme attendus, pas les tordre.
- [ ] **Commit** : `feat: la grenade et la dynamite au catalogue` (au moment d'atterrir, les commits de la vague
  se fondent en un seul `feat:`).

#### Tâche 2 : l'explosion commune — `static/js/explosions.js`

**Fichiers :** créer `static/js/explosions.js` ; modifier `static/js/vehicules.js` (`exploser`, `endommager`),
`templates/index.html` (le `<script>`, **après** `vehicules.js` et `combat.js`), `static/js/jeu.js` (`window.BANDINI`
et le pas de la boucle), `docs/architecture.md` (la ligne du module) ; juges dans `tests/test_explosions_js.py`.

**Consomme :** `Entites.autour`, `Entites.decorAutour`, `Entites.endommagerDecor`, `Entites.blesser`,
`Vehicules.endommager`, `Vehicules.descendre`, `Police.signalerCrime`, `Police.entendre`, `Entites.alerter`.

**Produit :**
- `Explosions.faire(x, y, o)` — `o = { rayon, degats, coupable, auteur, source }` : `coupable` (le joueur ou `null`)
  décide du délit ; `auteur` est celui que `blesser` accuse (le joueur, ou le char qui saute) ; `source` est le char
  qui saute (on ne l'abîme pas lui-même, et on fait descendre qui est dedans).
- `Explosions.differer(v)` / `Explosions.maj()` — **la chaîne** : pendant un `faire`, un char mis à zéro ne saute
  pas dans la boucle ; il attend l'image suivante.

- [ ] **Juges d'abord** (`tests/test_explosions_js.py`, fixture `banc`) :

```python
"""L'explosion commune : celle du char, de la grenade, de la dynamite — une seule."""


def test_l_explosion_blesse_dans_son_rayon_et_pas_au_dela(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const pres = o.poser(null, 30, 0), loin = o.poser(null, 120, 0);
        const v0 = pres.vie, v1 = loin.vie;
        L.Explosions.faire(j.x + 30, j.y - 30, { rayon: 48, degats: 110, coupable: j, auteur: j });
        return { pres: v0 - pres.vie, loin: v1 - loin.vie };
    }""")
    assert r["pres"] > 0 and r["loin"] == 0, r


def test_une_explosion_du_joueur_est_un_delit_et_s_entend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, vus = [], entendus = [];
        const sc = L.Police.signalerCrime, en = L.Police.entendre;
        L.Police.signalerCrime = function (k) { vus.push(k); return sc.apply(this, arguments); };
        L.Police.entendre = function (x, y, r) { entendus.push(r); return en.apply(this, arguments); };
        L.Explosions.faire(j.x + 80, j.y, { rayon: 48, degats: 110, coupable: j, auteur: j });
        return { vus: vus, entendus: entendus };
    }""")
    assert "explosion" in r["vus"] and r["entendus"], r


def test_le_char_saute_toujours_par_la_meme_explosion(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let appels = 0; const f = L.Explosions.faire;
        L.Explosions.faire = function () { appels++; return f.apply(this, arguments); };
        const v = o.char('berline', 60, 0);
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        return { appels: appels, etat: v.etat };
    }""")
    assert r == {"appels": 1, "etat": "epave"}


def test_les_chars_sautent_en_chaine_un_par_image(banc):
    """Dix chars collés : le premier saute, le suivant à l'image d'après — jamais dans sa boucle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const chars = [];
        for (let i = 0; i < 10; i++) { const v = o.char('berline', 60 + i * 34, 0); v.vie = 1; chars.push(v); }
        L.Vehicules.endommager(chars[0], 9999, L.B.joueur);
        const apres0 = chars.filter(function (v) { return v.etat === 'epave'; }).length;
        for (let i = 0; i < 12; i++) L.Explosions.maj();
        return { apres0: apres0, fin: chars.filter(function (v) { return v.etat === 'epave'; }).length };
    }""")
    assert r["apres0"] == 1, "la chaîne a sauté dans la même image"
    assert r["fin"] == 10, r
```

  (le slug `berline` est à vérifier dans `app/vehicules.py` — prendre un char à réservoir qui existe.)
- [ ] **Les voir rougir** : `uv run pytest -q tests/test_explosions_js.py` → `L.Explosions` indéfini.
- [ ] **Le module** — ce qui était dans `exploser` (particules, décalque, son, secousse, les vivants, le décor, le
  délit) passe ici, **à l'identique**, plus le bruit :

```js
/* Bandini — l'explosion commune (28 sept. 2026, « les explosifs »).

   ⚠️ UNE SEULE EXPLOSION : le char qui saute, la grenade, la dynamite passent
   tous par `faire`. Deux explosions écrites deux fois divergent — l'une
   casse le lampadaire, l'autre pas.

   ⚠️ LA CHAÎNE SE JOUE UNE IMAGE À LA FOIS. Un char mis à zéro PENDANT une
   explosion ne saute pas dans sa boucle (`differer`) : il attend l'image
   suivante (`maj`). Dix chars garés côte à côte faisaient sinon dix
   explosions imbriquées dans la même image. */

const Explosions = (function () {
  'use strict';

  let enCours = 0;
  let attente = [];

  function regles() { return (B.defs.armes_regles && B.defs.armes_regles.explosion) || { bruit_tuiles: 30 }; }

  function faire(x, y, o) {
    enCours++;
    try {
      for (let i = 0; i < 40; i++) {
        const a = B.rng() * Math.PI * 2, s = 1 + B.rng() * 3;
        Entites.particule(x, y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 30 + B.rng() * 20, i % 3 ? '#ff8c1a' : '#3a3a3a', 2 + (i % 2), 0.1);
      }
      Entites.decal(x, y, 'impact');
      Son.SFX.explosion();
      B.cam.secousse = Math.max(B.cam.secousse, 1.2);
      for (const e of Entites.autour(x, y, o.rayon, function (q) { return q !== o.source && q.vivant; })) {
        const part = 1 - Math.hypot(e.x - x, e.y - y) / o.rayon;
        if (part <= 0) continue;
        if (e.type === 'vehicule') Vehicules.endommager(e, Math.round(o.degats * part), o.coupable);
        else if (e.type === 'pieton' || e.type === 'joueur') {
          if (o.source && e.dansVehicule === o.source) Vehicules.descendre(e, true);
          Entites.blesser(e, Math.round(o.degats * part), o.auteur || o.coupable, { renverse: true, angle: angleVers(x, y, e.x, e.y), saigne: 120 });
        }
      }
      for (const d of Entites.decorAutour(x, y, o.rayon)) {
        if (d.brise) continue;
        const part = 1 - Math.hypot(d.x - x, d.y - y) / o.rayon;
        if (part > 0) Entites.endommagerDecor(d, Math.round(o.degats * part));
      }
      if (o.coupable) {
        Police.signalerCrime('explosion', x, y, true);
        Entites.alerter(x, y, o.coupable, 3);
        Police.entendre(x, y, regles().bruit_tuiles * TT);
      }
    } finally { enCours--; }
  }

  /** Vrai si le char doit attendre : on est DANS une explosion. */
  function differer(v) {
    if (!enCours) return false;
    if (attente.indexOf(v) < 0) attente.push(v);
    return true;
  }

  function maj() {
    if (!attente.length) return;
    const lot = attente; attente = [];
    for (const v of lot) Vehicules.exploser(v);
  }

  function oublier() { attente = []; enCours = 0; }

  return { faire, differer, maj, oublier };
})();
```

  ⚠️ Vérifier avant d'écrire que `Police.entendre` n'existe que pour le joueur (lire `police.js`) : une explosion
  **sans** coupable (un char du trafic qui brûle tout seul) ne doit rien signaler, comme aujourd'hui.
- [ ] **Le char y passe** : `Vehicules.exploser(v)` garde ce qui est **à lui** (l'épave, les nuances, le câble,
  `epaveT`, l'alarme, faire descendre le conducteur) et remplace le reste par
  `Explosions.faire(v.x, v.y, { rayon: ph.explosion_rayon_px, degats: ph.explosion_degats, coupable: coupable, auteur: coupable || v, source: v })`.
  Dans `endommager` : `if (v.def.reservoir === false || v.derby) plier(v); else if (!Explosions.differer(v)) exploser(v);`
  — ⚠️ l'épave doit être marquée **tout de suite** (sinon `endommager` la remet à zéro à chaque éclat) : poser
  `v.vie = 0` avant `differer`, et `exploser` ne doit pas sauter deux fois (`if (v.etat === 'epave' && v.epaveT) return;`
  en tête, à vérifier contre `perdu(v)`).
- [ ] **La boucle** : `pas('explosions', Explosions.maj)` dans `jeu.js`, juste **après** `pas('combat', Combat.maj)` ;
  `Explosions.oublier()` à côté de `Incendies.oublier()` (une partie neuve) ; `Explosions` dans `window.BANDINI`.
- [ ] **Vert, et rien de cassé** : `uv run pytest -q tests/test_explosions_js.py tests/test_vehicules_js.py tests/test_vehicules.py tests/test_ce_qui_casse.py tests/test_moteur_js.py tests/test_police*.py tests/test_frenesies_js.py`.
  Un rouge dans les anciens : le rejouer sur la base (mémoire « Un rouge est-il de moi ? ») avant de toucher.
- [ ] **Commit** : `feat: une seule explosion pour tout le jeu`.

#### Tâche 3 : allumer, tenir, lancer — la mèche

**Fichiers :** `static/js/combat.js` ; juges dans `tests/test_explosifs_js.py`.

**Consomme :** `Explosions.faire` (tâche 2) ; `meche`, `souffle`, `rebond`, `REGLES.explosion` (tâche 1).

**Produit (exporté par `Combat`) :**
- `allumerMeche(j)` → `bool` : allume l'arme `lance` en main, retire une munition (sauf triche), pose
  `j.enMain = { arme: slug, reste: meche }`.
- `lacherMeche(j, force)` → l'entité `lance` créée (ou `null`) : `force` 1 = lancer, 0 = la laisser tomber aux pieds.
- `lancer(e, arme, reste, force)` → l'entité `{ type: 'lance', arme, tireur, reste, x, y, z, vx, vy, vz, angle, tour }`.
- `majLances()` : appelé dans `maj`, après `majBrasiers()`.
- `majEnMain(j)` : la mèche tenue (appelée en tête de `majGestes`) ; et `dessinerLance(ctx, g, cx, cy)` (tâche 4).
  Les cinq s'ajoutent au `return { … }` de `Combat` — les juges les appellent par `L.Combat`.

- [ ] **Juges d'abord** (`tests/test_explosifs_js.py`) :

```python
"""La grenade et la dynamite : on allume, la mèche brûle dans la main, on lance, ça saute."""

PRELUDE = """
    L.Jeu.commencer();
    const j = L.B.joueur;
    let booms = [];
    const f = L.Explosions.faire;
    L.Explosions.faire = function (x, y, o) { booms.push({ x: x, y: y, t: L.B.t, rayon: o.rayon }); return f.apply(this, arguments); };
    function donner(slug) { L.B.partie.armes[slug] = { mun: 3, usure: 0 }; j.arme = slug; }
    function images(n) { for (let i = 0; i < n; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majLances(); L.Combat.majEnMain(j); } }
"""


def test_la_grenade_saute_au_bout_de_sa_meche_et_pas_avant(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        L.Combat.lacherMeche(j, 1);
        images(148); const avant = booms.length;
        images(4);
        return { avant: avant, apres: booms.length, mun: L.B.partie.armes.grenade.mun };
    }""")
    assert r == {"avant": 0, "apres": 1, "mun": 2}


def test_la_tenir_la_cuit(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        images(100);                       // tenue 100 images
        L.Combat.lacherMeche(j, 1);
        images(49); const avant = booms.length;
        images(3);
        return { avant: avant, apres: booms.length };
    }""")
    assert r == {"avant": 0, "apres": 1}


def test_trop_tenue_elle_saute_dans_la_main(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('dynamite');
        const vie = j.vie;
        L.Combat.allumerMeche(j);
        images(245);
        return { booms: booms.length, blesse: j.vie < vie, enMain: !!j.enMain,
                 pres: booms.length && Math.hypot(booms[0].x - j.x, booms[0].y - j.y) < 16 };
    }""")
    assert r["booms"] == 1 and r["blesse"] and not r["enMain"] and r["pres"], r


def test_changer_d_arme_la_laisse_tomber_et_elle_saute_quand_meme(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        j.arme = 'poings';
        images(160);
        return { booms: booms.length, enMain: !!j.enMain };
    }""")
    assert r == {"booms": 1, "enMain": False}


def test_dans_l_eau_la_meche_s_eteint(banc):
    """Lancée sur la baie : un remous, pas d'explosion."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        let eau = null;
        for (let y = 2; y < c.h - 2 && !eau; y++) for (let x = 2; x < c.w - 2; x++) if (L.Monde.estEau(x, y)) { eau = { x: x * L.TT + 8, y: y * L.TT + 8 }; break; }
        donner('grenade');
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 150, 0);
        g.x = eau.x; g.y = eau.y; g.z = 0; g.vz = 0;
        images(200);
        return { booms: booms.length, reste: L.B.entites.filter(function (e) { return e.type === 'lance'; }).length };
    }""")
    assert r == {"booms": 0, "reste": 0}


def test_la_grenade_rebondit_sur_le_mur_la_dynamite_non(banc):
    """Lancée droit dans une façade à bout portant : la grenade revient vers soi, la dynamite reste au pied du mur."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        function versLeMur() {                        // un mur plein à l'est, à 3 tuiles, sol libre entre
          for (let y = 3; y < c.h - 3; y++) for (let x = 3; x < c.w - 6; x++) {
            if (L.Monde.solidite(x, y) || L.Monde.solidite(x + 1, y) || L.Monde.solidite(x + 2, y)) continue;
            if (L.Monde.solidite(x + 3, y) === 1) return { x: x * L.TT + 8, y: y * L.TT + 8, mur: (x + 3) * L.TT };
          }
        }
        const p = versLeMur(); j.x = p.x; j.y = p.y; j.angle = 0;
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 999, 1);
        const d = L.Combat.lancer(j, L.Combat.armeDef('dynamite'), 999, 1);
        images(90);
        return { gx: g.x, dx: d.x, mur: p.mur, depart: p.x };
    }""")
    assert r["gx"] < r["dx"], "la grenade devait revenir plus loin du mur que la dynamite"
    assert r["gx"] < r["mur"] and r["dx"] < r["mur"], "rien ne traverse le mur"


def test_la_triche_munitions_ne_vide_pas_le_sac(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.B.triches = Object.assign(L.B.triches || {}, { munitions: true });
        L.Combat.allumerMeche(j);
        return L.B.partie.armes.grenade.mun;
    }""")
    assert r == 3
```

  (⚠️ la forme de la triche — `B.triches.munitions` — est à lire dans `combat.js`, fonction `triche`, et le
  prélude à ajuster à ce qu'elle lit vraiment ; un juge qui pose une clé que le jeu ne lit pas ne mord pas.)
- [ ] **Les voir rougir** : `uv run pytest -q tests/test_explosifs_js.py` → `allumerMeche` indéfini.
- [ ] **Le code**, dans `combat.js`, une section `// --- Ce qui se lance ---` après celle du feu :

```js
  /** Allume l'arme `lance` en main : la mèche brûle DÈS MAINTENANT, dans la main.
      Le sac perd une munition ici — une mèche allumée ne se rallume pas. */
  function allumerMeche(j) {
    const arme = armeDe(j);
    if (arme.type !== 'lance' || j.enMain) return false;
    const sac = B.partie.armes[arme.slug];
    if (!triche('munitions') && (!sac || !sac.mun)) { Son.SFX.vide(); return false; }
    if (!triche('munitions')) sac.mun--;
    j.enMain = { arme: arme.slug, reste: arme.meche };
    Son.SFX.arme(arme);                                   // le grésillement (`son: meche`)
    if (Entites.estJoueur(j)) Police.signalerCrime('arme_sortie', j.x, j.y, Police.quelqu_un_voit(j.x, j.y, j));
    return true;
  }

  /** Lâche la mèche : `force` 1 la lance devant, 0 la laisse tomber aux pieds. */
  function lacherMeche(j, force) {
    const m = j.enMain;
    if (!m) return null;
    j.enMain = null;
    return lancer(j, armeDef(m.arme), m.reste, force);
  }

  function lancer(e, arme, reste, force) {
    const angle = e === B.joueur && force ? viseeAssistee(e, e.angle) : e.angle;
    const v = arme.vitesse_projectile * force;
    return Entites.creer('lance', e.x + Math.cos(angle) * 6, e.y + Math.sin(angle) * 6, {
      r: 3, dessine: true, solide: false, arme: arme.slug, tireur: e, reste: reste,
      vx: Math.cos(angle) * v, vy: Math.sin(angle) * v, z: 6, vz: force ? 1.6 : 0, angle: angle, tour: 0,
    });
  }

  /** La mèche tenue : elle brûle, et saute DANS LA MAIN à zéro. Ce qu'on ne tient
      plus (une autre arme, un char, une porte) tombe aux pieds et saute quand même. */
  function majEnMain(j) {
    const m = j && j.enMain;
    if (!m) return;
    if (!j.vivant || j.dansVehicule || armeDe(j).slug !== m.arme) { lacherMeche(j, 0); return; }
    if (B.t % 3 === 0) Entites.particule(j.x + Math.cos(j.angle) * 6, j.y - 8, (B.rng() - 0.5) * 0.6, -0.5, 8, '#ffd23a', 1, 0.05);
    if (--m.reste <= 0) {
      j.enMain = null;
      const arme = armeDef(m.arme);
      Explosions.faire(j.x, j.y, { rayon: arme.souffle, degats: arme.degats, coupable: Entites.estJoueur(j) ? j : null, auteur: j });
    }
  }

  function majLances() {
    const R = regles().explosion || { gravite: 0.12, rebond_amorti: 0.45, roule_friction: 0.9 };
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const g = B.entites[i];
      if (g.type !== 'lance') continue;
      const arme = armeDef(g.arme);
      // Le mur : on essaie chaque axe à part — c'est ce qui fait rebondir d'équerre.
      if (g.z <= 8) {
        if (Monde.solidite(Math.floor((g.x + g.vx) / TT), Math.floor(g.y / TT)) === 1) {
          g.vx = arme.rebond ? -g.vx * R.rebond_amorti : 0;
          if (arme.rebond) Son.depuis(g, Son.SFX.rebond);
        }
        if (Monde.solidite(Math.floor(g.x / TT), Math.floor((g.y + g.vy) / TT)) === 1) {
          g.vy = arme.rebond ? -g.vy * R.rebond_amorti : 0;
          if (arme.rebond) Son.depuis(g, Son.SFX.rebond);
        }
      }
      g.x += g.vx; g.y += g.vy;
      g.z += g.vz; g.vz -= R.gravite;
      if (g.z <= 0) {
        g.z = 0;
        if (Monde.estEau && Monde.estEau(Math.floor(g.x / TT), Math.floor(g.y / TT))) {
          Entites.remous(g.x, g.y, 6); Entites.retirer(g); continue;          // la mèche s'éteint dans la baie
        }
        if (arme.rebond && g.vz < -0.8) { g.vz = -g.vz * R.rebond_amorti; Son.depuis(g, Son.SFX.rebond); }
        else g.vz = 0;
        g.vx *= R.roule_friction; g.vy *= R.roule_friction;
      }
      g.tour += Math.hypot(g.vx, g.vy) * 0.25;
      if (B.t % 3 === 0) Entites.particule(g.x, g.y - g.z - 2, (B.rng() - 0.5) * 0.5, -0.4, 8, '#ffd23a', 1, 0.05);
      if (--g.reste <= 0) {
        Entites.retirer(g);
        Explosions.faire(g.x, g.y, { rayon: arme.souffle, degats: arme.degats,
                                     coupable: Entites.estJoueur(g.tireur) ? g.tireur : null, auteur: g.tireur });
      }
    }
  }
```

  ⚠️ `regles()` a un repli sans `explosion` : l'étendre (`explosion: { bruit_tuiles: 30, gravite: 0.12, … }`).
- [ ] **Les gestes**, dans `majGestes` :
  - **tout en haut**, avant la garde qui sort pour un char, une clôture ou la roue : `majEnMain(j);` — sinon une
    mèche tenue en montant dans un char ne brûle plus jamais.
  - avec les autres armes : `else if (arme.type === 'lance') { if (ent.neuf('attaque')) allumerMeche(j); else if (!ent.bas('attaque') && j.enMain) lacherMeche(j, 1); }`
    — ⚠️ **avant** la branche `ent.neuf('attaque') && arme.type !== 'jet'`, sinon `frapper` part aussi ; et
    `frapper` lui-même refuse `lance` (`if (arme.type === 'lance') return false;`) pour que les PNJ ne tirent pas
    une grenade par la voie des balles.
  - `majLances()` dans `maj`, après `majBrasiers()`.
- [ ] **Passer une porte** : dans `Jeu.entrer` / `Jeu.sortir` (lire `jeu.js`), `Combat.lacherMeche(B.joueur, 0)`
  **avant** de changer de carte — la grenade reste dehors et y saute. Juge :

```python
def test_passer_une_porte_laisse_la_meche_dehors(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        const porte = L.Monde.carte.portes && L.Monde.carte.portes[0];
        if (!porte) return { saute: 'pas de porte' };
        o.entrer(porte);
        return { enMain: !!j.enMain, dehors: L.B.interieur ? true : false };
    }""")
    assert r.get("enMain") is False, r
```

  (la forme de `Monde.carte.portes` et de `Jeu.entrer(porte)` est à lire dans `monde.js`/`jeu.js` avant d'écrire.)
- [ ] **Vert** : `uv run pytest -q tests/test_explosifs_js.py tests/test_explosions_js.py tests/test_armes_js.py tests/test_roue_js.py tests/test_combat*_js.py`.
- [ ] **Mutation** (mémoire « Un juge qui ne mord pas ») : retirer `g.vx = -g.vx…` → le juge du rebond rougit ;
  retirer `majEnMain(j)` du haut de `majGestes` → celui de la porte rougit. Remettre, vider `__pycache__`.
- [ ] **Commit** : `feat: allumer, tenir, lancer — la mèche`.

#### Tâche 4 : les voir — dans la main, dans la roue, en l'air

**Fichiers :** `static/js/sprites.js` (`OBJETS.grenade`, `OBJETS.dynamite`), `static/js/combat.js`
(`dessinerLance`), `static/js/entites.js` (`dessiner` : la branche `lance`).

- [ ] **Juge d'abord** : `test_chaque_arme_qu_on_tient_a_son_dessin` rougit déjà (tâche 1). Ajouter, dans
  `tests/test_explosifs_js.py` :

```python
def test_on_voit_la_grenade_voler_et_son_ombre(banc):
    """Elle se dessine en l'air, et son ombre au sol : deux peintures, pas une."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 150, 1);
        images(6);
        const ctx = o.ctx; let dessins = 0; const di = ctx.drawImage;
        ctx.drawImage = function () { dessins++; return di.apply(this, arguments); };
        const avant = dessins; L.Combat.dessinerLance(ctx, g, L.B.cam.x, L.B.cam.y);
        return { z: g.z, dessins: dessins - avant };
    }""")
    assert r["z"] > 0 and r["dessins"] >= 2, r
```

- [ ] **Les dessins** (16 × 10, la même grille que `molotov`) : la grenade, un ovale vert olive quadrillé, sa
  cuillère et son anneau ; la dynamite, un bâton rouge et sa mèche blanche. Puis :

```js
  /** La grenade ou la dynamite en l'air : son ombre au sol (plus petite quand elle
      monte), puis l'objet qui TOURNE, levé de `z`. */
  function dessinerLance(ctx, g, cx, cy) {
    const def = armeDef(g.arme);
    const ombre = Math.max(0.4, 1 - g.z / 40);
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    ctx.fillRect(Math.round(g.x - 3 * ombre - cx), Math.round(g.y - 1 - cy), Math.round(6 * ombre), 2);
    const img = Atlas.cuirePeintre('objet|' + def.sprite, 16, 10, function (c, w, h) { OBJETS[def.sprite](c, w, h); });
    ctx.save();
    ctx.translate(Math.round(g.x - cx), Math.round(g.y - g.z - 4 - cy));
    ctx.rotate(g.tour);
    ctx.drawImage(img, -8, -5);
    ctx.restore();
    B.stats.images++;
  }
```

  (un `fillRect` pour l'ombre, un `drawImage` pour l'objet : si le juge compte les `drawImage`, peindre l'ombre
  par le peintre `DECORS.ombre` cuit, comme les gens — lire ce que `dessiner` fait pour eux.) Dans
  `Entites.dessiner`, avant `imageDe(e)` : `if (e.type === 'lance') { Combat.dessinerLance(ctx, e, cx, cy); continue; }`.
- [ ] **Regarder** : une capture Chromium (mémoire « Capturer une pièce du jeu ») — la grenade au sommet de sa
  cloche, avec son ombre ; la dynamite dans la roue d'armes. L'ouvrir dans Aperçu (copie dans `captures/`).
- [ ] **Vert** : `uv run pytest -q tests/test_armes.py tests/test_explosifs_js.py tests/test_roue_js.py`.
- [ ] **Commit** : `feat: on voit la grenade voler`.

#### Tâche 5 : les sons — la mèche, le rebond

**Fichiers :** `app/audio.py` (`CATALOGUE`), `static/js/son.js` (`SFX.meche`, `SFX.rebond`, et leur repli
synthétisé), `static/audio/…` (les deux mp3).

- [ ] **Juges** : `test_chaque_arme_a_son_son` (rouge depuis la tâche 1) et `tests/test_audio.py` suffisent.
- [ ] **Le catalogue**, à côté de `explosion` :

```python
    # La mèche qu'on allume : l'allumette, puis le grésillement — c'est le son de
    # la grenade ET de la dynamite (`armes.py`, `son="meche"`). Une mèche qu'on
    # n'entend pas, on ne sait pas qu'elle brûle.
    _e("meche", "Mèche allumée", duree_s=1.6, volume=0.55,
       prompt="a match struck then a short fuse catching and fizzing, crackling sparks, "
              "close-up, no explosion, no music"),
    _e("rebond", "Grenade qui rebondit", variantes=2, duree_s=0.5, volume=0.5,
       prompt="a small heavy metal object bouncing once on asphalt, a dull clank, "
              "close, no music"),
```

- [ ] **Générer** : `uv run python scripts/audio_elevenlabs.py --essai` (doit lister `meche`, `rebond-1`,
  `rebond-2` et rien d'autre), puis `uv run python scripts/audio_elevenlabs.py`. Écouter les trois fichiers (`afplay`)
  avant de garder.
- [ ] **Le navigateur** : `meche` et `rebond` dans `SFX`, chacun avec son repli (`if (!joue('meche')) { bruit(…) }`,
  sur le modèle de `molotov`).
- [ ] **Vert** : `uv run pytest -q tests/test_audio.py tests/test_armes.py tests/test_armes_js.py tests/test_definitions.py`.
- [ ] **Commit** : `feat: la mèche grésille, la grenade rebondit`.

#### Tâche 6 : la dynamite des chantiers

**Fichiers :** `static/js/chantiers.js` ; juge dans `tests/test_explosifs_js.py`.

- [ ] **Juge d'abord** :

```python
def test_un_chantier_ouvert_a_sa_dynamite_et_elle_ne_revient_pas(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const ch = L.Chantiers.ouverts && L.Chantiers.ouverts()[0];
        if (!ch) return { saute: 'aucun chantier ouvert' };
        L.Chantiers.poserLaDynamite(ch, true);             // true : ignorer la bulle et l'écran, au banc
        const b = L.B.entites.find(function (e) { return e.type === 'ramassage' && e.arme === 'dynamite'; });
        L.Entites.retirer(b); ch.dynamitePrise = true;
        L.Chantiers.poserLaDynamite(ch, true);
        return { posee: !!b, revient: L.B.entites.some(function (e) { return e.type === 'ramassage' && e.arme === 'dynamite'; }) };
    }""")
    assert r == {"posee": True, "revient": False}, r
```

  (les noms `ouverts` et la forme d'un chantier sont à lire dans `chantiers.js` et à ajuster au juge.)
- [ ] **Le code** : `poserLaDynamite(ch, forcer)` — une `ramassage` `{ objet: 'arme', arme: 'dynamite', munitions: 3 }`
  au pied de la benne (`ch.def.conteneur`, une tuile à côté), **lazy et gardée par la même bulle que la benne**
  (`poserLaBenneSiBesoin` : hors écran, dans `BULLE_OUBLI`), une seule par chantier et par partie
  (`ch.dynamitePrise`, posé quand on la ramasse — dans `Combat.ramasser`, `if (objet.chantier) objet.chantier.dynamitePrise = true`).
  Appelée à côté de `poserLaBenneSiBesoin`, retirée avec la benne.
- [ ] **Les juges « ce module ne déplace rien »** : les lancer (`uv run pytest -q -k "deplace" tests/`) — une
  ramassage neuve ne doit rien décaler (mémoire « Juges ce module ne déplace rien », « Décor eager »).
- [ ] **Vert** : `uv run pytest -q tests/test_explosifs_js.py tests/test_chantiers*.py`.
- [ ] **Commit** : `feat: la dynamite traîne sur les chantiers`.

#### Tâche 7 : livrer la vague 1

- [ ] `uv run ruff check .` ; les juges ciblés de toutes les tâches ensemble, plus `tests/test_definitions.py`,
  `tests/test_table_des_jalons.py`, `tests/test_architecture*.py` s'il existe (la carte du dépôt nomme
  `explosions.js` et les deux juges neufs).
- [ ] **Jouer au banc** une vraie partie : acheter une grenade au marché noir, la lancer sur un char garé, le voir
  sauter ; une capture.
- [ ] Les commits de la vague fondus en un `feat:` (`git reset --soft <base>` puis un commit), **atterrir tout de
  suite** (`cherry-pick` sur `dev` à jour, `merge --ff-only` depuis `~/dev/bandini`), puis la suite complète
  (mémoire « Atterrir avant la suite complète »).
- [ ] La ligne du plan : « ✅ vague 1 livrée » dans sa cellule d'état, la vague 2 (le Molotov en mieux) en cours ;
  la note de livraison sous `## Notes`.

## Notes

_Rien de livré._
