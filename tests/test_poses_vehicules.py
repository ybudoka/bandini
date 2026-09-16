"""Les véhicules debout : trois poses, choisies comme la face d'un passant.

⚠️ **Tout ce qui est debout dans Bandini est dessiné debout** — le passant ancré
à ses pieds, l'arbre, le lampadaire, le banc, le feu et son poteau, les clôtures
nord-sud vues par la tranche. Le char était la dernière chose regardée d'aplomb.

⚠️ Et le vocabulaire est celui du passant, pas un nouveau : `cote` (miroité en
`gauche` et `droite` par `Atlas.cuire`), `haut` = il s'ÉLOIGNE donc on voit son
dos, `bas` = il VIENT donc sa face. La pose se choisit avec **le même code** que
la face d'un corps — deux jeux de seuils auraient fini par diverger, et le char
aurait changé de pose à un cap où le passant à côté de lui n'en change pas.
"""

from app import vehicules


def test_l_auto_le_taxi_et_la_police_partagent_la_meme_carrosserie():
    """Ils ont toujours partagé une grille et ne différaient que par la palette.
    ⚠️ Ça reste vrai debout : trois palettes sur une carrosserie, pas trois
    dessins à tenir d'accord."""
    slugs = {"auto", "taxi", "police"}
    tailles = {(v["longueur"], v["largeur"]) for v in vehicules.CATALOGUE if v["slug"] in slugs}
    assert len(tailles) == 1, f"ils n'ont plus la même carrosserie : {tailles}"


def test_la_pose_suit_le_cap_par_la_meme_regle_que_la_face_d_un_passant(banc):
    """⚠️ LE JUGE DE LA FICHE. `regarder` porte déjà le seuil
    (`|dx| >= |dy|`) ; on vérifie qu'un char et un passant, au même cap,
    regardent dans le même sens — et donc qu'il n'y a **qu'un seul code**."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        const corps = { angle: 0, face: 'bas' };
        const desaccords = [], vus = {};
        for (let deg = 0; deg < 360; deg += 5) {
            const a = deg * Math.PI / 180;
            v.angle = a;
            const char = L.Vehicules.faceDe(v);
            L.Entites.regarder(corps, Math.cos(a), Math.sin(a));
            vus[char] = (vus[char] || 0) + 1;
            if (char !== corps.face) desaccords.push([deg, char, corps.face]);
        }
        return { desaccords: desaccords, vus: vus };
    }""")
    assert r["desaccords"] == [], (
        "le char et le passant ne regardent pas dans le même sens : %s" % r["desaccords"][:5]
    )
    # ⚠️ Et les quatre faces servent VRAIMENT : un seuil qui rendrait toujours
    # « bas » passerait l'accord ci-dessus sans rien prouver.
    assert set(r["vus"]) == {"droite", "gauche", "haut", "bas"}, r["vus"]
    assert min(r["vus"].values()) >= 10, "une face ne sert presque jamais : %s" % r["vus"]


def test_les_trois_poses_existent_et_aucune_n_est_empruntee(banc):
    """⚠️ « Aucune manquante et aucune empruntée à un autre » : deux poses
    identiques, c'est un véhicule qui n'a pas été dessiné et qui fait semblant.
    On compare les grilles, pas les canevas — un canevas se compare mal."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        ['auto', 'taxi', 'police'].forEach(function (slug) {
            const def = L.SPRITES[slug];
            const p = def.poses;
            out[slug] = {
                poses: Object.keys(p).sort(),
                cote: p.cote[0].join('|'), haut: p.haut[0].join('|'), bas: p.bas[0].join('|'),
                ancre: def.ancre, w: def.w, h: def.h,
            };
        });
        // Et la cuisson miroite `cote` en gauche/droite, comme un corps.
        const cuit = L.Atlas.cuire('auto', L.SPRITES.auto, null);
        out.cuites = Object.keys(cuit.poses).sort();
        return out;
    }""")
    assert r["cuites"] == ["bas", "cote", "droite", "gauche", "haut"], (
        "la cuisson ne miroite pas le profil comme elle le fait pour un corps : %s" % r["cuites"]
    )
    for slug, d in [(k, v) for k, v in r.items() if k != "cuites"]:
        assert d["poses"] == ["bas", "cote", "haut"], f"{slug} : {d['poses']}"
        assert d["cote"] != d["haut"] and d["cote"] != d["bas"] and d["haut"] != d["bas"], (
            f"{slug} : deux poses identiques — une d'elles n'a pas été dessinée"
        )


def test_l_ancre_est_la_ligne_de_sol_et_la_meme_pour_les_trois(banc):
    """⚠️ Un char debout ancré au centre FLOTTE au-dessus de la rue. Et l'ancre
    doit être la même pour les trois poses, sinon il saute d'un pixel en
    tournant — ce qui se voit à chaque coin de rue.

    On vérifie aussi que le bas du dessin **touche** cette ligne : une ancre
    posée au bon endroit sur un dessin qui flotte ne vaut rien.

    ⚠️ Il se juge sur la **sport**, une grille dessinée à la main : depuis le
    16 sept. 2026 la carrosserie de l'auto est EN VOLUME, ses poses sont tirées
    d'une projection centrée sur son empreinte, et elle n'a plus de ligne de sol
    à tenir (« la machine se projette au cap et suit son ombre »)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.SPRITES.sport;
        const bas = {};
        ['cote', 'haut', 'bas'].forEach(function (nom) {
            const g = def.poses[nom][0];
            let dernier = -1;
            for (let y = 0; y < g.length; y++) if (/[^.]/.test(g[y])) dernier = y;
            bas[nom] = dernier;
        });
        return { ancre: def.ancre, h: def.h, bas: bas };
    }""")
    ligne = r["ancre"][1]
    assert ligne == r["h"] - 3, (
        "l'ancre n'est pas la ligne de sol : %s pour une grille de %s" % (r["ancre"], r["h"])
    )
    for nom, dernier in r["bas"].items():
        assert dernier == ligne, (
            f"la pose « {nom} » finit à la rangée {dernier} et le sol est à {ligne} : "
            "le char flotte ou s'enfonce"
        )


def test_le_char_se_dessine_centre_sur_son_empreinte(banc):
    """Le dessin, pas seulement la fiche : on regarde **où l'image est posée**.

    ⚠️ **Un char qui tourne ne se pose plus par sa ligne de sol : il se pose par
    son MILIEU**, parce que c'est autour de son milieu qu'il tourne. Le canevas
    d'un cap est carré — la diagonale du dessin, pour qu'aucun cap ne soit rogné
    — et son centre tombe sur `v.x`, `v.y` : là où l'ombre est posée, là où les
    cercles de collision sont. Un dessin ancré ailleurs que son ombre, c'est un
    char qui ne se gare plus dans ses lignes."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        v.x = 200; v.y = 100; v.z = 0; v.angle = 0;
        const poses = [];
        const ctx = L.Base.ecran();
        ctx.drawImage = function (img, x, y) { poses.push([x, y, img.width, img.height]); };
        L.Vehicules.dessinerUn(ctx, v, 0, 0);
        const auSol = poses[0];
        v.z = 20;
        poses.length = 0;
        L.Vehicules.dessinerUn(ctx, v, 0, 0);
        return { auSol: auSol, enVol: poses[0], x: v.x, y: v.y };
    }""")
    x, y, w, h = r["auSol"]
    assert w == h, "le canevas d'un cap n'est pas carré : %s" % r
    assert x == r["x"] - w / 2, "le char n'est pas centré sur son axe : %s" % r
    assert y == r["y"] - h / 2, "le char n'est pas centré sur son empreinte : %s" % r
    # ⚠️ Et en vol il MONTE, il ne grandit pas : `z` sort du dessin, pas du centre.
    assert r["enVol"][1] == y - 20, "le saut ne lève pas le char : %s" % r


def test_le_char_tourne_comme_son_ombre(banc):
    """⚠️ **LE JUGE DE LA LIGNE.** Retour de Martin : « le pilotage des
    véhicules est vraiment impossible maintenant, il faut que le véhicule
    tourne vraiment comme l'ombre le fait, sinon impossible de conduire ».

    Le char debout n'avait que **quatre dessins** pour un cap **continu** :
    l'ombre pivotait sous lui à chaque image, la caisse attendait 45° et
    claquait. On mesure donc les deux ensemble, sur un tour complet : l'écart
    entre le cap DESSINÉ et le cap de l'ombre ne dépasse jamais un demi-cran
    (5,6°), et les 32 crans servent tous. Avec quatre poses, l'écart montait à
    45° et trois caps sur quatre étaient un mensonge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const v = o.char('auto', 0, 0, 0);
        const n = L.Vehicules.ROTATIONS;
        const vus = {}; let pire = 0;
        for (let deg = 0; deg < 720; deg++) {
            const a = deg * Math.PI / 180 - Math.PI;     // -180° a +540° : les tours negatifs aussi
            v.angle = a;
            const i = L.Vehicules.capDe(a);
            vus[i] = true;
            // Le cap dessine, ramene en radians, contre l'angle de l'ombre.
            const dessine = i * 2 * Math.PI / n - Math.PI / 2;
            let ecart = (dessine - L.Vehicules.ombreDe(v).angle) % (Math.PI * 2);
            if (ecart > Math.PI) ecart -= Math.PI * 2;
            if (ecart < -Math.PI) ecart += Math.PI * 2;
            ecart = Math.abs(ecart);
            if (ecart > pire) pire = ecart;
        }
        return { caps: Object.keys(vus).length, n: n, pire: pire * 180 / Math.PI };
    }""")
    assert r["caps"] == r["n"], (
        "le char ne se dessine qu'en %s caps sur %s : il claque au lieu de tourner" % (r["caps"], r["n"])
    )
    demi = 360 / r["n"] / 2
    assert r["pire"] <= demi + 0.01, (
        "le dessin s'écarte de son ombre de %.1f° — le volant ne se voit plus (un demi-cran fait %.1f°)"
        % (r["pire"], demi)
    )


def test_le_toit_qui_tourne_porte_les_phares_ET_les_feux(banc):
    """⚠️ `haut` et `bas` sont le **même toit lu dans l'autre sens** : l'un ne
    montre que les feux arrière (le char s'éloigne), l'autre que les phares (il
    vient). Un seul dessin qui tourne doit donc porter **les deux**, sinon un
    char qui vient vers nous roule tous phares éteints — et on ne le voit plus
    venir de nuit.

    ⚠️ Et chacun à son bout : les phares dans la moitié NEZ (le nord du
    dessin), les feux dans la moitié queue. Un retournement fait sur la grille
    plutôt que sur la caisse les décalerait d'une rangée."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        L.B.defs.vehicules.forEach(function (def) {
            const sprite = L.SPRITES[def.sprite];
            // ⚠️ Un deux-roues n'a pas de toit qui tourne : il se projette au
            // cap, et ses lampes se jugent cap par cap (plus bas, « la machine
            // se projette au cap et suit son ombre »).
            if (!sprite || out[def.sprite] || sprite.machine) return;
            const toit = L.Atlas.toitDe(def.sprite, sprite);
            let premier = -1, dernier = -1;
            toit.forEach(function (ligne, y) { if (/[^.]/.test(ligne)) { if (premier < 0) premier = y; dernier = y; } });
            const rangees = function (lettre) {
                const ys = [];
                toit.forEach(function (ligne, y) { if (ligne.indexOf(lettre) >= 0) ys.push(y); });
                return ys;
            };
            const dansBas = (sprite.poses.bas[0].join('').indexOf('l') >= 0);
            out[def.sprite] = { phares: rangees('l'), feux: rangees('t'), milieu: (premier + dernier) / 2,
                                dansBas: dansBas };
        });
        return out;
    }""")
    # ⚠️ Sept chars roulent encore sur leur toit ; la berline et les deux-roues
    # sont en volume, et leurs lampes se jugent cap par cap.
    assert len(r) >= 6, "le décor du juge est faux : %s" % list(r)
    for sprite, m in r.items():
        if not m["dansBas"]:
            continue                      # un vélo n'a pas de phare : rien à porter
        assert m["phares"], f"{sprite} : le dessin qui tourne a perdu ses phares"
        assert m["feux"], f"{sprite} : le dessin qui tourne n'a plus de feux arrière"
        assert max(m["phares"]) < m["milieu"], (
            f"{sprite} : ses phares sont posés dans sa queue ({m['phares']} pour un milieu à {m['milieu']})"
        )
        assert min(m["feux"]) > m["milieu"], (
            f"{sprite} : ses feux arrière sont posés sur son nez ({m['feux']})"
        )


def test_l_atlas_ne_cuit_que_les_caps_qu_on_a_montres(banc):
    """⚠️ **Le chiffre qui avait tué les caps, et comment on les reprend sans
    le payer.** Les 32 caps de toute la flotte, cuits d'avance, pesaient
    1 024 canevas et 6 Mo — pour trois pour cent du temps, puisque 94,5 % des
    chars en marche sont à moins de 2° d'un cap cardinal. C'est ce chiffre-là
    qui avait mis le parc debout, en trois poses.

    Sauf qu'un char qui ne tourne pas ne se conduit pas : les caps reviennent,
    mais **cuits un par un, et seulement ceux qu'on a vraiment montrés**. Un
    char du trafic roule sur des rails et n'en montre que quatre ; le joueur,
    lui, les prend tous — et c'est lui qui conduit. On mesure les deux : ce
    qu'un char à l'arrêt coûte, et ce qu'un tour complet coûte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const ctx = L.Base.ecran();
        const v = o.char('auto', 0, 0, 0);
        v.x = 200; v.y = 100; v.z = 0;
        const n = L.Vehicules.ROTATIONS;
        L.Atlas.vider();
        const vide = L.Atlas.taille;
        v.angle = 0;
        L.Vehicules.dessinerUn(ctx, v, 0, 0);
        L.Vehicules.dessinerUn(ctx, v, 0, 0);          // deux fois : la cuisson ne se refait pas
        const unCap = L.Atlas.taille - vide;
        v.angle = 2 * Math.PI / n;
        L.Vehicules.dessinerUn(ctx, v, 0, 0);
        const parCap = L.Atlas.taille - vide - unCap;
        for (let i = 0; i < n; i++) { v.angle = i * 2 * Math.PI / n; L.Vehicules.dessinerUn(ctx, v, 0, 0); }
        const tour = L.Atlas.taille - vide;
        // Et la flotte entiere, chacun a l'arret, chacun de sa couleur.
        L.Atlas.vider();
        const flotte = [];
        L.B.defs.vehicules.forEach(function (def) {
            const c = o.char(def.slug, 0, 0, 0);
            if (!c) return;
            c.x = 200; c.y = 100; c.z = 0; c.angle = 0;
            L.Vehicules.dessinerUn(ctx, c, 0, 0);
            flotte.push(def.slug);
            L.Entites.retirer(c);
        });
        return { unCap: unCap, parCap: parCap, tour: tour, n: n, flotte: L.Atlas.taille, chars: flotte.length };
    }""")
    n = r["n"]
    # Un char a l'arret : sa grille de toit, son toit peint, son cap — trois ;
    # en volume, la grille projetee de son cap et son canevas — deux.
    assert r["unCap"] <= 3, "un char à l'arrêt cuit %s entrées d'atlas" % r["unCap"]
    # ⚠️ Un cap de plus coûte un canevas (le toit tourné), ou une grille et un
    # canevas (la projection, cuite une fois par cap et peinte par couleur).
    assert 1 <= r["parCap"] <= 2, "un cap de plus cuit %s entrées" % r["parCap"]
    # Un tour complet : les 32 caps, et rien de plus.
    attendu = r["unCap"] + (n - 1) * r["parCap"]
    assert r["tour"] == attendu, "un tour complet cuit %s entrées au lieu de %s" % (r["tour"], attendu)
    assert r["chars"] >= 10, "le décor du juge est faux : %s chars" % r["chars"]
    # ⚠️ Et la flotte à l'arrêt ne paie pas les caps qu'elle ne montre pas :
    # 32 d'avance par véhicule, c'était le millier de canevas d'avant.
    assert r["flotte"] * 4 <= n * r["chars"], (
        "la flotte à l'arrêt pèse %s entrées contre %s en caps cuits d'avance"
        % (r["flotte"], n * r["chars"])
    )


# --- Le modelé : rehaut, ombre, moyeu, chrome, reflet -------------------------


def test_les_nuances_sont_les_memes_a_la_naissance_et_dans_la_palette(banc):
    """⚠️ UNE SEULE FORMULE, dans `base.js`. Les palettes de `sprites.js` en
    tirent leurs tons par défaut, et `vehicules.js` les tire pour chaque couleur
    du catalogue à la naissance d'un char. Deux formules auraient divergé : un
    taxi jaune neuf aurait eu un toit d'une autre teinte qu'un taxi jaune garé
    depuis le début. On vérifie qu'un char né avec la couleur par défaut de sa
    palette est cuit EXACTEMENT comme la palette."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const def = L.SPRITES.auto;
        // ⚠️ ON NE FORCE RIEN : `creer` tire une couleur du catalogue et pose
        // les swaps lui-meme. On verifie que CES swaps-la sortent de la formule
        // partagee, et que la palette aussi. Un juge qui poserait les swaps a
        // la main prouverait seulement que la formule existe.
        const v = o.char('auto', 0, 0, 0);
        const attendu = L.nuances(v.couleur), pal = L.nuances(def.pal.c);
        return { pal: { c: def.pal.c, C: def.pal.C, D: def.pal.D },
                 palAttendue: pal,
                 nes: v.swaps, attendu: attendu,
                 fixes: { M: def.pal.M, B: def.pal.B, G: def.pal.G, E: def.pal.E },
                 monotone: attendu.C === attendu.c && attendu.D === attendu.c };
    }""")
    assert r["nes"], "le décor du juge est faux : le char n'a pas de swaps (%s)" % r
    assert r["nes"] == r["attendu"], (
        "à la naissance, les swaps ne sortent pas de `nuances` : %s" % r
    )
    assert r["pal"] == r["palAttendue"], (
        "la palette ne tire pas ses tons de `nuances` : %s" % r
    )
    assert r["monotone"] is False, "le rehaut et l'ombre valent la couleur : il n'y a pas de modelé (%s)" % r
    for cle, val in r["fixes"].items():
        assert val, "le ton fixe « %s » manque à la palette" % cle


def test_chaque_char_debout_se_sert_de_ses_tons(banc):
    """Un ton déclaré et jamais posé n'est qu'une couleur de plus dans une
    palette. ⚠️ On regarde les GRILLES : chaque char debout doit poser un rehaut
    `C`, une ombre `D` et un moyeu `M` — sinon il est revenu au slab d'une seule
    couleur que Martin a demandé de raffiner."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        ['auto', 'sport', 'luxe', 'ambulance', 'camion', 'remorqueuse', 'autobus'].forEach(function (slug) {
            const p = L.SPRITES[slug].poses;
            const tout = p.cote[0].join('') + p.haut[0].join('') + p.bas[0].join('');
            out[slug] = { C: (tout.match(/C/g) || []).length, D: (tout.match(/D/g) || []).length,
                          M: (tout.match(/M/g) || []).length, G: (tout.match(/G/g) || []).length,
                          B: (tout.match(/B/g) || []).length };
        });
        return out;
    }""")
    for slug, n in r.items():
        for ton in ("C", "D", "M", "G", "B"):
            assert n[ton] > 0, f"{slug} ne pose jamais le ton « {ton} » : {n}"


def test_le_taxi_et_la_police_ont_retrouve_leur_livree_et_l_auto_n_en_porte_pas(banc):
    """⚠️ Les premières grilles debout avaient PERDU les bandes `x` et `y` : le
    taxi et la police se dessinaient comme une auto repeinte. La carrosserie
    commune porte maintenant une bande `y` et un damier `x` — invisibles sur
    l'auto (où ils valent la couleur de caisse), noirs sur le taxi, bleu et
    rouge sur la police.

    ⚠️ **Refait le 16 sept. 2026, la berline en volume.** « Invisibles sur
    l'auto » ne tenait que pour une auto ROUGE : la palette mettait `x` et `y`
    au rouge par défaut, et seul `c` change à la naissance — une berline bleu
    marine aurait roulé avec une bande et un damier rouges sur le flanc, le jour
    où son flanc s'est dessiné. La livrée s'AJOUTE donc à la carrosserie : le
    taxi et la police portent toutes les pièces de l'auto, plus leur livrée, et
    l'auto n'en porte pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const machine = function (slug) { return L.SPRITES[slug].machine.pieces.map(function (p) { return JSON.stringify(p); }); };
        const a = machine('auto'), t = machine('taxi'), p = machine('police');
        const dedans = function (petit, grand) { return petit.every(function (q) { return grand.indexOf(q) >= 0; }); };
        const lettres = function (slug) {
            const def = L.SPRITES[slug];
            const tout = ['cote', 'haut', 'bas'].map(function (n) { return def.poses[n][0].join(''); }).join('');
            return { x: (tout.match(/x/g) || []).length, y: (tout.match(/y/g) || []).length };
        };
        const tp = L.SPRITES.taxi.pal, pp = L.SPRITES.police.pal;
        return { carrosserie: dedans(a, t) && dedans(a, p) && t.length > a.length && t.join() === p.join(),
                 auto: lettres('auto'), taxi: lettres('taxi'), police: lettres('police'),
                 tX: tp.x, tC: tp.c, pY: pp.y, pC: pp.c };
    }""")
    assert r["carrosserie"] is True, "le taxi et la police ne sont plus la carrosserie de l'auto plus une livrée : %s" % r
    assert r["auto"] == {"x": 0, "y": 0}, "l'auto porte une livrée, qui ne suit pas sa couleur : %s" % r["auto"]
    for slug in ("taxi", "police"):
        assert r[slug]["x"] > 0 and r[slug]["y"] > 0, f"{slug} ne montre pas sa livrée : {r[slug]}"
    assert r["tX"] != r["tC"], "le taxi n'a pas de damier : %s" % r
    assert r["pY"] != r["pC"], "la police n'a pas sa bande : %s" % r



# --- Le passant assis : le conducteur n'est plus cuit dans le deux-roues -----


def test_le_velo_et_la_moto_ne_portent_plus_leur_conducteur_cuit(banc):
    """⚠️ La palette du vélo portait une peau (`s`) et des cheveux (`h`) : tous
    les cyclistes de la ville avaient la même tête pour toujours. Debout, le
    conducteur est un passant posé dessus — donc le deux-roues n'a plus AUCUN
    pixel de corps, et il déclare où sa selle est, pose par pose."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        ['velo', 'moto'].forEach(function (slug) {
            const def = L.SPRITES[slug];
            const tout = ['cote', 'haut', 'bas'].map(function (n) { return def.poses[n][0].join(''); }).join('');
            out[slug] = { corps: (tout.match(/[hsp]/g) || []).length,
                          selle: def.selle ? Object.keys(def.selle).sort() : null,
                          palette: Object.keys(def.pal).filter(function (k) { return 'hsp'.indexOf(k) >= 0; }) };
        });
        const j = L.Atlas.cuire('joueur', L.SPRITES.joueur, null).poses;
        out.assis = ['assis_bas', 'assis_cote', 'assis_droite', 'assis_gauche', 'assis_haut']
            .filter(function (n) { return !!j[n]; });
        return out;
    }""")
    for slug in ("velo", "moto"):
        assert r[slug]["corps"] == 0, f"{slug} porte encore un corps cuit dedans : {r[slug]}"
        assert r[slug]["palette"] == [], f"{slug} garde une peau ou des cheveux en palette : {r[slug]}"
        assert r[slug]["selle"] == ["0", "1"], (
            f"{slug} : la selle n'est plus une paire [dx, dy] mais {r[slug]['selle']}"
        )
    assert r["assis"] == ["assis_bas", "assis_cote", "assis_droite", "assis_gauche", "assis_haut"], (
        "la pose assise manque, ou ne se miroite pas comme la marche : %s" % r["assis"]
    )


def test_le_pilote_du_trafic_a_ses_propres_couleurs_et_un_deux_roues_gare_n_a_personne(banc):
    """⚠️ C'est le correctif des « sortes de gens » appliqué aux deux-roues :
    deux motos du trafic ne portent pas la même tête. Et un deux-roues
    STATIONNÉ n'a personne dessus — c'est ce qui le distingue d'un char qui
    roule."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(3);
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const tetes = [];
        for (let i = 0; i < 12; i++) {
            const v = L.Vehicules.creer('moto', j.x + 40 * (i + 1), j.y, 0, { conducteur: 'trafic', etat: 'roule' });
            tetes.push(JSON.stringify(L.Vehicules.cavalierDe(v)));
        }
        const gare = o.char('moto', 0, 40, 0);
        return { tetes: tetes, distinctes: new Set(tetes).size,
                 personneSurLeGare: L.Vehicules.cavalierDe(gare) === null, gareA: !!gare.pilote };
    }""")
    assert all(t != "null" for t in r["tetes"]), "une moto du trafic roule sans personne dessus : %s" % r
    assert r["distinctes"] >= 3, "tous les motards ont la même tête : %s" % r["distinctes"]
    assert r["personneSurLeGare"] is True and r["gareA"] is False, (
        "une moto stationnée a quelqu'un dessus : %s" % r
    )


def test_le_joueur_sur_sa_moto_est_peint_avec_ses_couleurs_et_en_deux_images(banc):
    """⚠️ Au volant, `j.dessine = false` : c'est le véhicule qui doit peindre
    le pilote, et avec les couleurs DU JOUEUR — sinon on change de tête en
    enfourchant. On compte les images : une moto avec quelqu'un dessus, c'est
    la machine ET le passant assis."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('moto', 0, 0, 0);
        const images = function () {
            const ctx = L.Base.ecran(); let n = 0;
            ctx.drawImage = function () { n++; };
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            return n;
        };
        const seule = images();
        L.Vehicules.monter(j, v);
        const montee = { images: images(), cavalier: L.Vehicules.cavalierDe(v) === j.swaps,
                         joueurCache: j.dessine === false };
        L.Vehicules.descendre(j, true);
        return { seule: seule, montee: montee, apres: images() };
    }""")
    assert r["seule"] == 1, "une moto stationnée se peint en %s images" % r["seule"]
    assert r["montee"]["joueurCache"] is True, "le décor du juge est faux : le joueur reste dessiné (%s)" % r
    assert r["montee"]["cavalier"] is True, "le pilote n'a pas les couleurs du joueur : %s" % r
    assert r["montee"]["images"] == 2, "le joueur sur sa moto ne se peint pas : %s" % r
    assert r["apres"] == 1, "descendu, il reste peint sur la moto : %s" % r


def test_celui_qu_on_jette_a_terre_garde_ses_couleurs(banc):
    """Voler un vélo fait tomber son cycliste. ⚠️ C'est CELUI QUI ÉTAIT DESSUS
    qui tombe : un cycliste tiré au hasard à la chute aurait changé de tête en
    touchant le sol."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('velo', j.x + 10, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        const avant = JSON.stringify(v.pilote && v.pilote.swaps);
        const gens0 = L.B.entites.filter(function (e) { return e.type === 'pieton'; }).length;
        L.Vehicules.monter(j, v);
        const tombes = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin' && e.menace === j; });
        return { avant: avant, tombe: tombes.length ? JSON.stringify(tombes[tombes.length - 1].swaps) : null,
                 pilote: v.pilote, monte: j.dansVehicule === v };
    }""")
    assert r["monte"] is True, "le décor du juge est faux : le vol n'a pas eu lieu (%s)" % r
    assert r["avant"] and r["avant"] != "null", "le vélo du trafic n'avait pas de cycliste : %s" % r
    assert r["tombe"] == r["avant"], "le cycliste jeté à terre a changé de tête : %s" % r
    assert r["pilote"] is None, "le vélo volé garde son pilote : %s" % r


def test_le_motard_qu_on_fait_descendre_ne_remonte_pas_sur_sa_moto(banc):
    """Retour de Martin : « quand on vole une moto, la personne qui était
    dessus s'en va, mais quand on la quitte, il y a encore une personne
    dessus ». ⚠️ Le vélo effaçait son cycliste en le jetant à terre ; la moto
    passait par le carjacking, qui faisait sortir un passant tiré au hasard et
    laissait le motard sur la selle — caché par le joueur tant qu'il roulait,
    revenu dès qu'il descendait. C'est aussi CELUI QUI ÉTAIT DESSUS qui sort :
    il garde ses couleurs. Et un deux-roues que son pilote du trafic a quitté
    (le fuyard qui tombe de sa moto) n'a plus personne dessus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('moto', j.x + 10, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        const avant = JSON.stringify(v.pilote && v.pilote.swaps);
        const images = function () {
            const ctx = L.Base.ecran(); let n = 0;
            ctx.drawImage = function () { n++; };
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            return n;
        };
        L.Vehicules.monter(j, v);
        const sortis = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin' && e.menace === j; });
        const monte = j.dansVehicule === v;
        v.vitesse = 0;
        L.Vehicules.descendre(j, true);
        const fuyard = L.Vehicules.creer('moto', j.x + 60, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        const fuyardA = !!(fuyard.pilote && fuyard.pilote.swaps);
        fuyard.conducteur = null; fuyard.etat = 'stationne';
        return { avant: avant, monte: monte, descendu: !j.dansVehicule,
                 sorti: sortis.length ? JSON.stringify(sortis[sortis.length - 1].swaps) : null,
                 cavalier: JSON.stringify(L.Vehicules.cavalierDe(v)), images: images(),
                 fuyardA: fuyardA, fuyardCavalier: JSON.stringify(L.Vehicules.cavalierDe(fuyard)) };
    }""")
    assert r["monte"] is True and r["descendu"] is True, "le décor du juge est faux : %s" % r
    assert r["avant"] and r["avant"] != "null", "la moto du trafic n'avait pas de motard : %s" % r
    assert r["cavalier"] == "null", "descendu de la moto volée, le motard est encore dessus : %s" % r
    assert r["images"] == 1, "la moto volée et quittée se peint en %s images" % r["images"]
    assert r["sorti"] == r["avant"], "le motard qui descend a changé de tête : %s" % r
    assert r["fuyardA"] is True, "le décor du juge est faux : la seconde moto n'a pas de motard (%s)" % r
    assert r["fuyardCavalier"] == "null", "un deux-roues quitté par son pilote a encore quelqu'un dessus : %s" % r


def test_la_sport_est_basse_et_ses_roues_sont_dans_les_ailes(banc):
    """Retour de Martin : « la voiture sport devrait être basse, les roues plus
    dans les ailes ». ⚠️ Deux mesures, pas une impression : de profil, sa
    caisse est plus courte que celle de l'auto (toit plus bas pour un même sol),
    et la rangée de bas de caisse passe PAR-DESSUS le haut des pneus — on y
    trouve du pneu là où l'auto n'a que de la tôle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ ON MESURE LE DESSIN, pas la fiche : la hauteur va du premier
        // pixel au dernier DE LA GRILLE. Mesuree depuis l'ancre declaree, une
        // grille etrangere d'une autre taille passait au travers du juge.
        const mesure = function (slug) {
            const def = L.SPRITES[slug], g = def.poses.cote[0];
            let haut = -1, sol = -1;
            for (let y = 0; y < g.length; y++) if (/[^.]/.test(g[y])) { if (haut < 0) haut = y; sol = y; }
            const large = Math.max.apply(null, g.map(function (l) { return l.replace(/[.]/g, ' ').trim().length; }));
            // La rangee du bas de caisse : la premiere rangee, en montant depuis le
            // sol, qui traverse la caisse d'un bout a l'autre.
            let bas = -1;
            for (let y = sol; y >= 0; y--) {
                const l = g[y].replace(/[.]/g, ' ').trim();
                if (l.length >= large * 0.9) { bas = y; break; }
            }
            return { hauteur: sol - haut, pneuDansLaCaisse: (g[bas].match(/r/g) || []).length, bas: bas, sol: sol };
        };
        return { sport: mesure('sport'), auto: mesure('auto') };
    }""")
    assert r["sport"]["hauteur"] < r["auto"]["hauteur"], "la sport n'est pas plus basse que l'auto : %s" % r
    assert r["sport"]["pneuDansLaCaisse"] > 0, "les roues de la sport pendent sous la caisse : %s" % r
    # ⚠️ Le décor d'avant disait « l'auto, elle, n'a pas ses roues dans les
    # ailes ». Depuis qu'elle est EN VOLUME (16 sept. 2026), ses roues sont dans
    # de vrais passages : la sport se juge sur sa propre grille, et l'auto ne
    # sert plus que de toise.


def test_de_dos_un_char_montre_sa_longueur(banc, paquet):
    """⚠️ **Retour de Martin : « les voitures de face et de dos devraient être
    vues à 45 degrés, pas de face, vu la carte » · « vue plongeante ».**

    Les poses `haut` et `bas` étaient des **élévations au ras du sol** : on
    voyait la face arrière bien à plat et presque pas de toit. Sur une carte
    qu'on regarde d'en haut, un char qui roule vers le nord ne montrait donc
    **rien de ses 28 px de longueur** — mesuré, 12 rangées peintes pour un char
    long de 28.

    À 45°, une longueur `L` se projette en `L·sin45` et une hauteur `H` en
    `H·cos45` ; pour nos proportions la somme vaut à peu près `L`. La règle est
    donc simple et elle se mesure : **de dos comme de face, un char occupe à
    l'écran sa longueur** — exactement ce que son ombre au sol annonce déjà.
    Et de profil, rien ne bouge : c'est sa hauteur qu'on y voit."""
    r = banc("""function (L, o) {
        const out = {};
        L.B.defs.vehicules.forEach(function (v) {
            const def = L.SPRITES[v.sprite];
            // ⚠️ Une machine EN VOLUME n'a pas de pose de dos dessinée : la sienne
            // est sa projection, qui montre sa longueur au biais du sol, comme son
            // ombre (« la machine se projette au cap et suit son ombre »).
            if (!def || def.rotations || def.machine) return;
            const mesure = function (nom) {
                const g = def.poses[nom][0];
                let premier = -1, dernier = -1, large = 0;
                for (let y = 0; y < g.length; y++) {
                    if (!/[^.]/.test(g[y])) continue;
                    if (premier < 0) premier = y;
                    dernier = y;
                    const peints = g[y].split('').filter(function (c) { return c !== '.'; }).length;
                    if (peints > large) large = peints;
                }
                return { haut: dernier - premier + 1, large: large };
            };
            out[v.slug] = { cote: mesure('cote'), dos: mesure('haut'), face: mesure('bas'),
                            longueur: v.longueur, largeur: v.largeur };
        });
        return out;
    }""")
    assert len(r) >= 6, "trop peu de véhicules debout : %s" % list(r)
    for slug, m in r.items():
        lon, lat = m["longueur"], m["largeur"]
        for nom, pose in (("de dos", m["dos"]), ("de face", m["face"])):
            # ⚠️ LE DÉFAUT, MESURÉ : une pose plongeante fait la LONGUEUR du
            # char, pas sa hauteur. Avant, une berline de 28 px en montrait 12.
            assert abs(pose["haut"] - lon) <= 5, (
                f"{slug} {nom} : {pose['haut']} rangées pour un char long de {lon} — "
                "il est dessiné de face, pas vu d'en haut"
            )
            # ... et sa largeur reste sa largeur : une pose plongeante ne
            # s'étale pas sur la voie d'à côté.
            assert pose["large"] <= lat + 6, f"{slug} {nom} : {pose['large']} px de large pour {lat}"
        # Le profil, lui, montre la HAUTEUR du char : il n'a pas bougé, et il
        # est forcément bien plus plat que les deux autres.
        # ⚠️ Le profil montre la HAUTEUR du char, la plongée sa LONGUEUR : la
        # seconde est donc toujours plus haute que le premier. Un vélo, court et
        # haut sur ses roues, tient de justesse — c'est pour ça que la règle se
        # dit « plus haute », et pas « deux fois plus haute ».
        assert m["cote"]["haut"] < m["dos"]["haut"], (
            f"{slug} : le profil fait {m['cote']['haut']} rangées et le dos {m['dos']['haut']} — "
            "l'un des deux ne regarde pas d'où il devrait"
        )
        assert abs(m["cote"]["large"] - lon) <= 8, f"{slug} de profil : {m['cote']['large']} px pour {lon}"


def test_le_char_tourne_autour_de_son_empreinte(banc):
    """⚠️ **Retour de Martin, capture à l'appui : « les voitures sont mal
    garré ».** Dans un stationnement, les chars débordaient par le nez sur le
    trottoir et laissaient le fond de leur case vide : la pose de dos portait la
    longueur du char mais restait posée à la ligne de sol du profil, si bien que
    tout char tourné vers le nord se dessinait **une demi-longueur devant
    lui-même**. Une case de stationnement (32 px de creux) le montrait au
    premier coup d'œil.

    ⚠️ **La règle a changé de forme avec la rotation, pas de fond.** Le dessin
    ne se pose plus par une ligne de sol qui dépend de la pose — il n'y a plus
    de poses : il TOURNE, et il tourne autour du centre de l'**empreinte du
    catalogue**. On mesure donc les deux bouts du toit depuis ce centre : une
    demi-longueur devant le nez, une demi-longueur derrière le pare-chocs. Et le
    canevas du cap se pose centré sur `v.x`, `v.y` — à tous les caps, pas
    seulement aux quatre cardinaux."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const ctx = L.Base.ecran(), vrai = ctx.drawImage;
        const out = {};
        L.B.defs.vehicules.forEach(function (def) {
            const sprite = L.SPRITES[def.sprite];
            if (!sprite) return;
            const v = o.char(def.slug, 0, 0, 0);
            if (!v) return;
            v.x = 200; v.y = 100; v.z = 0;
            const toit = L.Atlas.toitDe(def.sprite, sprite);
            let premier = -1, dernier = -1;
            toit.forEach(function (ligne, y) { if (/[^.]/.test(ligne)) { if (premier < 0) premier = y; dernier = y; } });
            const centre = L.Vehicules.centreDuToit(v);
            const poses = [];
            for (let i = 0; i < L.Vehicules.ROTATIONS; i++) {
                v.angle = i * 2 * Math.PI / L.Vehicules.ROTATIONS;
                const mises = [];
                ctx.drawImage = function (img, x, y) { mises.push([img.width, img.height, x, y]); };
                L.Vehicules.dessinerUn(ctx, v, 0, 0);
                ctx.drawImage = vrai;
                const m = mises[0];
                poses.push([m[2] + m[0] / 2 - v.x, m[3] + m[1] / 2 - v.y]);
            }
            out[def.slug] = { longueur: def.longueur, nez: centre[1] - premier,
                              cul: dernier + 1 - centre[1], poses: poses, machine: !!sprite.machine };
            L.Entites.retirer(v);
        });
        return out;
    }""")
    assert len(r) >= 10, "trop peu de véhicules : %s" % list(r)
    assert {"velo", "moto", "auto"} <= {s for s, m in r.items() if m["machine"]}, "le décor du juge est faux : %s" % r.keys()
    for slug, m in r.items():
        for i, (dx, dy) in enumerate(m["poses"]):
            assert (dx, dy) == (0, 0), (
                f"{slug} au cap {i} : son dessin est posé à ({dx}, {dy}) de son centre"
            )
        # ⚠️ Un deux-roues n'a pas de toit : ses bouts ne se mesurent pas sur
        # une grille qui tourne, mais sur sa projection (« de profil, un
        # deux-roues montre ses deux roues »). Son dessin, lui, reste centré.
        if m["machine"]:
            continue
        demi = m["longueur"] / 2
        assert abs(m["cul"] - demi) <= 1, (
            f"{slug} : du centre de rotation à son pare-chocs arrière il y a {m['cul']} px, "
            f"et sa demi-longueur en fait {demi} — il tourne à côté de sa place"
        )
        # ⚠️ Devant, le juge est plus lâche, et il faut savoir pourquoi :
        # quatre dessins sont plus COURTS que leur fiche (l'ambulance et la
        # remorqueuse de 5 px, le camion et l'autobus de 3), parce que leur
        # grille a été taillée à la longueur du char au lieu de longueur + 4.
        # Le manque se voit au nez. Ce que le juge interdit, c'est la
        # demi-longueur de décalage d'avant — un char dessiné en entier au
        # nord de son empreinte — et tout dépassement : un nez qui SORT de
        # l'empreinte, lui, est un mensonge sur ce qui bloque.
        assert demi - 5 <= m["nez"] <= demi + 1, (
            f"{slug} : son nez est à {m['nez']} px du centre de rotation pour une demi-longueur de {demi}"
        )


def test_le_cavalier_reste_assis_quand_sa_machine_tourne(banc):
    """⚠️ Le vélo et la moto portent quelqu'un, et il est dessiné à part : sa
    selle est un point **de la machine**, donc elle tourne avec elle. Posée sans
    tourner, elle laissait le cycliste assis au nord de son vélo dès qu'il
    roulait vers le sud — le même mensonge que le char qui se garait devant
    lui-même.

    On mesure, à tous les caps, l'écart entre l'ancre du cavalier et le centre
    de la machine : il vaut le recul de la selle (un ou deux pixels), il pointe
    toujours vers la QUEUE, et il ne reste jamais collé au même point de
    l'écran pendant que la machine tourne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const ctx = L.Base.ecran(), vrai = ctx.drawImage;
        const corps = L.Atlas.cuire('joueur', L.SPRITES.joueur, null);
        const out = {};
        ['velo', 'moto'].forEach(function (slug) {
            const v = L.Vehicules.creer(slug, j.x + 40, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
            if (!v || !L.Vehicules.cavalierDe(v)) return;
            v.x = 200; v.y = 100; v.z = 0;
            const selles = [];
            for (let i = 0; i < L.Vehicules.ROTATIONS; i++) {
                const a = i * 2 * Math.PI / L.Vehicules.ROTATIONS;
                v.angle = a;
                const mises = [];
                ctx.drawImage = function (img, x, y) { mises.push([img.width, img.height, x, y]); };
                L.Vehicules.dessinerUn(ctx, v, 0, 0);
                ctx.drawImage = vrai;
                const homme = mises[1];
                if (!homme) { selles.push(null); continue; }
                const dx = homme[2] + corps.ancre[0] - v.x, dy = homme[3] + corps.ancre[1] - v.y;
                selles.push([dx, dy, dx * Math.cos(a) + dy * Math.sin(a)]);
            }
            out[slug] = { selles: selles, longueur: v.def.longueur };
            L.Entites.retirer(v);
        });
        return out;
    }""")
    assert set(r) == {"velo", "moto"}, "le décor du juge est faux : %s" % list(r)
    for slug, m in r.items():
        points = set()
        for i, selle in enumerate(m["selles"]):
            assert selle is not None, f"{slug} au cap {i} : personne n'est dessiné dessus"
            dx, dy, devant = selle
            assert abs(dx) <= 3 and abs(dy) <= 3, (
                f"{slug} au cap {i} : son cavalier est assis à ({dx}, {dy}) du centre de sa machine"
            )
            # ⚠️ La selle est DERRIERE le milieu (ou dessus), jamais devant le nez.
            assert devant <= 1, f"{slug} au cap {i} : son cavalier est assis devant le guidon ({devant:.1f})"
            points.add((dx, dy))
        assert len(points) > 4, (
            f"{slug} : son cavalier reste au même point à tous les caps ({sorted(points)}) — "
            "sa selle ne tourne pas avec sa machine"
        )


# --- Le vélo et son cycliste : la machine se projette, le corps s'y tient ------


#: ⚠️ Pour juger ce qui se PEINT : le canevas du banc ne garde aucun pixel, mais
#: il écrit ses `fillRect` dans `traces` si on lui en donne. Tout canevas créé
#: après ce bout de code le fait — l'atlas est vidé pour qu'il recuise.
TRACER = """
    const fabrique = L.Base.nouveauCanvas;
    L.Base.nouveauCanvas = function (w, h) {
        const c = fabrique(w, h); c.getContext('2d').traces = []; return c;
    };
    L.Atlas.vider();
"""


def test_de_profil_une_machine_montre_ses_roues(banc):
    """⚠️ **Retour de Martin, capture à l'appui : « il faut améliorer ça ».**

    Le vélo qui roulait était son TOIT, tourné comme celui d'un char — et vu
    d'en haut, un vélo est un bâton avec une barre en travers. Vers l'est, on
    voyait un trait de trois pixels, le guidon dressé en travers, et le
    cycliste de profil posé dessus : un passant sur une échasse.

    On juge le dessin au cap de l'EST, celui qu'on voit le plus (94,5 % des
    chars en marche roulent à moins de 2° d'un cap cardinal) : sa rangée la plus
    basse — le sol — touche **deux roues séparées**, et il monte d'au moins un
    diamètre de roue. Une machine vue d'en haut n'a qu'un point au sol, là où
    finit la barre de son guidon.

    ⚠️ Et la berline (16 sept. 2026) : vers l'est, on voyait son toit couché sur
    le flanc. De profil, elle touche le sol par ses deux roues du côté qu'on
    voit."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const n = L.Vehicules.ROTATIONS, out = {};
        Object.keys(L.SPRITES).filter(function (s) { return L.SPRITES[s].machine; }).forEach(function (slug) {
            const def = L.SPRITES[slug];
            const g = L.Atlas.projeter(def.machine, L.Vehicules.capDe(0) * 2 * Math.PI / n - Math.PI / 2, def.w);
            const peintes = [];
            g.forEach(function (ligne, y) { if (/[^.]/.test(ligne)) peintes.push(y); });
            const sol = g[peintes[peintes.length - 1]];
            const touches = sol.match(/[^.]+/g) || [];
            const ecart = sol.replace(/^\\.*[^.]+/, '').match(/^\\.*/)[0].length;
            const roue = def.machine.pieces.find(function (p) { return p[0] === 'roue'; });
            out[slug] = { touches: touches.length, ecart: ecart, haut: peintes[peintes.length - 1] - peintes[0] + 1,
                          diametre: roue ? 2 * roue[2] : null, sol: sol };
        });
        return out;
    }""")
    assert {"velo", "moto", "auto", "taxi", "police"} <= set(r), "le décor du juge est faux : %s" % list(r)
    for slug, m in r.items():
        assert m["touches"] == 2, (
            f"{slug} de profil : sa rangée de sol touche {m['touches']} fois ({m['sol']!r}) — "
            "on ne voit pas deux roues, on voit une machine d'en haut"
        )
        assert m["ecart"] >= 3, f"{slug} de profil : ses deux roues se touchent ({m['sol']!r})"
        assert m["haut"] >= m["diametre"], (
            f"{slug} de profil : {m['haut']} rangées pour des roues de {m['diametre']} px"
        )


def test_la_machine_se_projette_au_cap_et_suit_son_ombre(banc, paquet):
    """⚠️ Un deux-roues ne tourne pas de toit : il se PROJETTE au cap. Ce qu'on
    tient, c'est ce qui faisait le correctif « le char tourne comme son ombre »
    — et rien ne doit en être perdu :

    - ce qui se **peint** à chaque cap est la projection à ce cap (et pas celle
      d'un cap voisin, ni un toit) ;
    - les **32 caps** sont 32 dessins : aucun cran ne claque sur le précédent ;
    - chaque dessin **pointe où il va** : là où le phare et le feu se voient
      tous les deux, le phare est devant, dans le sens du cap à l'écran ;
    - et le sol se voit du **même biais** que sous l'ombre — deux biais, c'est
      une machine qui ne se pose pas sur son ombre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + TRACER + """
        const n = L.Vehicules.ROTATIONS, out = {};
        Object.keys(L.SPRITES).filter(function (s) { return L.SPRITES[s].machine; }).forEach(function (slug) {
            const def = L.SPRITES[slug], K = def.machine.profondeur;
            const dessins = {}, faux = [], envers = [];
            let deux = 0;
            for (let i = 0; i < n; i++) {
                const a = i * 2 * Math.PI / n - Math.PI / 2;
                const g = L.Atlas.projeter(def.machine, a, def.w);
                dessins[g.join('|')] = true;
                const peints = g.join('').replace(/\\./g, '').length;
                const c = L.Atlas.cuireCap(slug, def, null, n, i, [0, 0]);
                const traces = c.getContext('2d').traces;
                const ici = {};
                traces.forEach(function (t) { ici[t[0] + ',' + t[1]] = true; });
                const pareil = traces.length === peints && g.every(function (ligne, y) {
                    return ligne.split('').every(function (ch, x) { return (ch === '.') === !ici[x + ',' + y]; });
                });
                if (!pareil) faux.push(i);
                const lampes = { l: [], t: [] };
                g.forEach(function (ligne, y) { ligne.split('').forEach(function (ch, x) { if (lampes[ch]) lampes[ch].push([x, y]); }); });
                if (!lampes.l.length || !lampes.t.length) continue;
                deux++;
                const moy = function (p, k) { return p.reduce(function (s, q) { return s + q[k]; }, 0) / p.length; };
                const avant = (moy(lampes.l, 0) - moy(lampes.t, 0)) * Math.cos(a) + (moy(lampes.l, 1) - moy(lampes.t, 1)) * Math.sin(a) * K;
                if (avant <= 0) envers.push([i, avant]);
            }
            out[slug] = { dessins: Object.keys(dessins).length, faux: faux, envers: envers, deux: deux, K: K };
        });
        out.n = n;
        return out;
    }""")
    n = r.pop("n")
    biais = paquet["conduite"]["ombre"]["profondeur"]
    assert {"velo", "moto", "auto", "taxi", "police"} <= set(r), "le décor du juge est faux : %s" % list(r)
    for slug, m in r.items():
        assert m["faux"] == [], f"{slug} : aux caps {m['faux']}, ce qui se peint n'est pas sa projection"
        assert m["dessins"] == n, f"{slug} : {m['dessins']} dessins pour {n} caps — il claque au lieu de tourner"
        assert m["envers"] == [], f"{slug} : son phare est derrière son feu aux caps {m['envers']}"
        # ⚠️ Un juge qui ne regarde rien passe : les deux lampes doivent se voir
        # ensemble à la plupart des caps (28 sur 32 le jour du correctif).
        assert m["deux"] >= n * 3 // 4, f"{slug} : phare et feu ne se voient ensemble qu'à {m['deux']} caps sur {n}"
        assert m["K"] == biais, f"{slug} : le sol se voit à {m['K']} sous la machine et à {biais} sous son ombre"


def test_le_cycliste_s_assoit_sur_la_selle_et_tient_son_guidon(banc):
    """⚠️ Le deuxième défaut de la capture : le cycliste était un passant
    ASSIS — la pose d'un banc. Les genoux devant, les mains sur les cuisses, les
    fesses à la hauteur des moyeux : posé sur une machine, il flottait à côté
    d'elle.

    La machine déclare trois points dans l'espace (`assise`, `guidon`,
    `pedales`) et on mesure le corps **tel qu'il se peint** contre leur
    projection : ses fesses sur la selle, sa main au guidon, son pied à la
    pédale. De profil pour les trois ; de dos et de face pour la main, parce
    que c'est là que le guidon change de place à l'écran (devant lui, donc plus
    haut quand il s'éloigne, plus bas quand il vient)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + TRACER + """
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        // Des couleurs qu'aucune palette n'a : chaque pixel dit ce qu'il est.
        j.swaps = { c: '#0000fe', h: '#00fe00', s: '#fe0000', p: '#fefe00' };
        const peau = '#fe0000', pantalon = '#fefe00', soulier = L.SPRITES.joueur.pal.b;
        const out = {};
        ['velo', 'moto'].forEach(function (slug) {
            const v = o.char(slug, 0, 0, 0);
            L.Vehicules.monter(j, v);
            const def = L.SPRITES[slug], M = def.machine, K = M.profondeur;
            v.x = 200; v.y = 100; v.z = 0; v.parcouru = 0;
            const ecran = function (p, a) {
                const ca = Math.cos(a), sa = Math.sin(a);
                return [v.x + p[0] * ca - p[1] * sa, v.y + (p[0] * sa + p[1] * ca) * K - p[2]];
            };
            const mesure = function (a) {
                v.angle = a;
                const cav = L.Vehicules.imageDuCavalier(def, v, L.Vehicules.cavalierDe(v));
                const x0 = Math.round(cav.x), y0 = Math.round(cav.y);
                const px = cav.canvas.getContext('2d').traces.map(function (t) { return [x0 + t[0] + 0.5, y0 + t[1] + 0.5, t[4]]; });
                const loin = function (p, q) { return Math.hypot(p[0] - q[0], p[1] - q[1]); };
                const pres = function (couleur, q) {
                    return Math.min.apply(null, px.filter(function (t) { return t[2] === couleur; }).map(function (t) { return loin(t, q); }));
                };
                // La main : de profil, le pixel de peau le plus en avant ; de dos et
                // de face, la plus proche de chaque poignee.
                const devant = Math.cos(a) >= 0 ? 1 : -1;
                const guidons = [ecran(M.guidon, a), ecran([M.guidon[0], -M.guidon[1], M.guidon[2]], a)];
                const res = {};
                if (Math.abs(Math.cos(a)) > 0.9) {
                    const peaux = px.filter(function (t) { return t[2] === peau; });
                    const main = peaux.reduce(function (m, t) { return (t[0] - m[0]) * devant > 0 ? t : m; });
                    res.main = Math.min(loin(main, guidons[0]), loin(main, guidons[1]));
                    const selle = ecran(M.assise, a);
                    const fesses = px.filter(function (t) { return t[2] === pantalon && Math.abs(t[0] - selle[0]) <= 1.5; });
                    res.fesses = Math.min.apply(null, fesses.map(function (t) { return t[1]; })) - selle[1];
                    res.pied = pres(soulier, ecran(M.pedales, a));
                } else {
                    res.main = Math.max(pres(peau, guidons[0]), pres(peau, guidons[1]));
                }
                return res;
            };
            out[slug] = { est: mesure(0), ouest: mesure(Math.PI), nord: mesure(-Math.PI / 2), sud: mesure(Math.PI / 2) };
            L.Vehicules.descendre(j, true);
            L.Entites.retirer(v);
        });
        return out;
    }""")
    for slug, faces in r.items():
        for face, m in faces.items():
            assert m["main"] <= 2.5, (
                f"{slug} vu {face} : sa main est à {m['main']:.1f} px de la poignée — il ne tient pas son guidon"
            )
            if "fesses" in m:
                assert -1.5 <= m["fesses"] <= 1.5, (
                    f"{slug} vu {face} : ses fesses sont à {m['fesses']:+.1f} px de la selle — "
                    "il flotte au-dessus ou il est assis dans ses roues"
                )
                assert m["pied"] <= 3, f"{slug} vu {face} : son pied est à {m['pied']:.1f} px de la pédale"


def test_le_cycliste_pedale_en_roulant_et_le_motard_non(banc):
    """Les pédales font un demi-tour tous les `pedale` pixels ROULÉS — la
    distance, pas la vitesse : un vélo poussé contre un mur a de la vitesse et
    ne pédale pas. ⚠️ C'est la fiche qui dit qu'on pédale : la moto n'a pas de
    `pedale`, son pilote garde les pieds sur les repose-pieds.

    On mesure les deux bouts : ce que `Vehicules.maj` compte quand la machine
    avance vraiment, et l'image du cavalier qui en suit."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const velo = o.char('velo', 0, 0, 0);
        const x0 = velo.x, y0 = velo.y;
        j.x = velo.x - 80;
        for (let i = 0; i < 30; i++) { velo.vitesse = 1.5; L.Vehicules.maj(); }
        const roule = { parcouru: velo.parcouru, bouge: Math.hypot(velo.x - x0, velo.y - y0) };
        const image = function (v, parcouru) {
            v.parcouru = parcouru;
            return L.Vehicules.imageDuCavalier(L.SPRITES[v.sprite], v, L.SPRITES.joueur.pal).canvas;
        };
        const pas = L.SPRITES.velo.pedale;
        const moto = o.char('moto', 0, 40, 0);
        return {
            roule: roule, pas: pas,
            velo: { memeDemiTour: image(velo, 0) === image(velo, pas - 1), autreDemiTour: image(velo, 0) !== image(velo, pas),
                    tourComplet: image(velo, 0) === image(velo, 2 * pas) },
            moto: { pedale: L.SPRITES.moto.pedale || null, fige: image(moto, 0) === image(moto, 7) && image(moto, 0) === image(moto, 23) },
        };
    }""")
    assert r["roule"]["bouge"] > 20, "le décor du juge est faux : le vélo n'a pas roulé (%s)" % r["roule"]
    assert abs(r["roule"]["parcouru"] - r["roule"]["bouge"]) <= 1, (
        "le vélo a roulé %.1f px et n'en compte que %.1f" % (r["roule"]["bouge"], r["roule"]["parcouru"])
    )
    assert r["pas"], "le vélo ne déclare pas ses pédales"
    v = r["velo"]
    assert v["memeDemiTour"] and v["autreDemiTour"] and v["tourComplet"], f"les pédales ne tournent pas avec la distance : {v}"
    assert r["moto"]["pedale"] is None and r["moto"]["fige"], f"le motard pédale : {r['moto']}"
