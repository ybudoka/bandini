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
    posée au bon endroit sur un dessin qui flotte ne vaut rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.SPRITES.auto;
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


def test_un_char_debout_se_dessine_a_sa_ligne_de_sol(banc):
    """Le dessin, pas seulement la fiche : on regarde **où l'image est posée**.
    ⚠️ `v.y` reste le centre physique — c'est là que les pneus touchent, et le
    tri du nord au sud s'y retrouve sans rien changer."""
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
        return { auSol: auSol, enVol: poses[0], ancre: L.SPRITES.auto.ancre,
                 x: v.x, y: v.y };
    }""")
    ax, ay = r["ancre"]
    assert r["auSol"][0] == r["x"] - ax, "le char n'est pas centré sur son axe : %s" % r
    assert r["auSol"][1] == r["y"] - ay, (
        "le char n'est pas posé à sa ligne de sol : %s" % r
    )
    # ⚠️ Et en vol il MONTE, il ne grandit pas : `z` sort du dessin, pas de l'ancre.
    assert r["enVol"][1] == r["auSol"][1] - 20, "le saut ne lève pas le char : %s" % r


def test_l_atlas_du_parc_a_maigri(banc):
    """⚠️ Le chiffre que la fiche promet : 32 caps par véhicule pesaient
    1 024 canevas et 6 Mo pour trois pour cent du temps (94,5 % des chars en
    marche sont à moins de 2° d'un cap cardinal). Trois poses en pèsent trois.

    On mesure les canevas d'une carrosserie convertie contre ceux d'une qui
    tient encore ses rotations : le rapport est ce qui compte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const compter = function (slug) {
            const def = L.SPRITES[slug];
            if (def.rotations) {
                return L.Atlas.cuireRotations(slug, def, null, L.Vehicules.ROTATIONS).images.length;
            }
            const p = L.Atlas.cuire(slug, def, null).poses;
            let n = 0;
            for (const nom in p) n += p[nom].length;
            return n;
        };
        // ⚠️ Le temoin en caps est la MOTO : elle porte son conducteur cuit
        // dans le dessin, donc elle attend la vague du passant assis. Le jour
        // ou elle passera debout, ce juge devra prendre un autre temoin — ou
        // disparaitre, parce qu'il n'y aura plus rien a comparer.
        return { debout: compter('auto'), caps: compter('moto') };
    }""")
    assert r["caps"] == 32, "le décor du juge est faux : %s" % r
    # Cinq noms de pose, mais `droite` est le MÊME canevas que `cote` : trois
    # dessins cuits, pas cinq. C'est ça, l'économie.
    assert r["debout"] <= 5, "une carrosserie debout cuit %s canevas" % r["debout"]
    assert r["debout"] * 6 <= r["caps"], (
        "l'atlas n'a pas maigri : %s canevas debout contre %s en caps" % (r["debout"], r["caps"])
    )
