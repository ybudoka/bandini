"""Le lance-roquettes (`docs/jalons/les-explosifs.md`, vague 4b) : il tire droit, la roquette se voit voler, et elle
saute à l'impact — un mur, un char, quelqu'un — ou au bout de sa portée."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur;
    j.intouchable = true;
    const booms = [];
    const f = L.Explosions.faire;
    L.Explosions.faire = function (x, y, o) { booms.push({ x: x, y: y, coupable: o.coupable === j, rayon: o.rayon }); return f.apply(this, arguments); };
    L.B.partie.armes.lance_roquettes = { mun: 4, usure: 0 }; j.arme = 'lance_roquettes'; L.B.partie.arme = 'lance_roquettes';
    const def = L.Combat.armeDef('lance_roquettes');
    function roquettes() { return L.B.entites.filter(function (e) { return e.type === 'projectile' && e.souffle; }); }
    function voler(n) { for (let i = 0; i < n && roquettes().length; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majProjectiles(); } }
    const ligne = o.ligneDroite(); j.x = ligne.x; j.y = ligne.y; j.angle = 0; L.Monde.centrerCamera(j.x, j.y);
    for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.hypot(e.x - j.x, e.y - j.y) < 260) L.Entites.retirer(e);
    L.Entites.indexer();
"""


def test_elle_saute_au_bout_de_sa_portee_et_tire_droit(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.Combat.tirer(j, def);
        const p = roquettes()[0], z0 = p.z, x0 = j.x;
        voler(10); const z = p.z;
        voler(200);
        return { z0: z0, z: z, booms: booms.length, coupable: booms.length && booms[0].coupable,
                 loin: booms.length ? Math.round(booms[0].x - x0) : 0, portee: def.portee, mun: L.B.partie.armes.lance_roquettes.mun };
    }""")
    assert r["z"] == r["z0"], f"elle ne tire pas droit : {r}"
    assert r["booms"] == 1 and r["coupable"], r
    assert r["portee"] - 20 <= r["loin"] <= r["portee"] + 20, f"elle ne saute pas au bout de sa portée : {r}"
    assert r["mun"] == 3, r


def test_elle_saute_sur_le_char_qu_elle_touche(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const v = o.char('auto', 90, 0);
        L.Entites.indexer();
        L.Combat.tirer(j, def);
        voler(120);
        return { booms: booms.length, roquette: booms.some(function (b) { return b.rayon === def.souffle && Math.hypot(b.x - v.x, b.y - v.y) < 24; }),
                 vie: v.vie, vieMax: v.vieMax };
    }""")
    assert r["booms"] >= 1 and r["roquette"], f"la roquette ne saute pas sur le char (le char saute seul ?) : {r}"
    assert r["vie"] < r["vieMax"], f"le char n'a rien pris : {r}"


def test_elle_saute_sur_qui_elle_touche(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('ouvrier', 70, 0); p.vie = 500; p.vieMax = 500;
        L.Entites.indexer();
        L.Combat.tirer(j, def);
        voler(120);
        return { booms: booms.length, pres: booms.length && Math.hypot(booms[0].x - p.x, booms[0].y - p.y) < 16, vie: p.vie };
    }""")
    assert r["booms"] == 1 and r["pres"] and r["vie"] < 500, r


def test_on_voit_la_roquette_voler(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.Combat.tirer(j, def);
        const p = roquettes()[0];
        voler(5);
        let peinte = 0; const d = L.Combat.dessinerRoquette;
        L.Combat.dessinerRoquette = function (ctx, e) { if (e === p) peinte++; return d.apply(this, arguments); };
        L.Jeu.rendre();
        return { peinte: peinte };
    }""")
    assert r["peinte"] == 1


def test_elle_saute_contre_le_mur(banc):
    """Tirée face à une façade, deux tuiles devant : elle saute au pied du mur — pas au bout de sa portée."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        let mur = null;
        for (let y = 4; y < c.h - 4 && !mur; y++) for (let x = 4; x < c.w - 4; x++) {
            if (c.sol[y][x] === 'F' && L.Monde.solidite(x, y + 1) === 0 && L.Monde.solidite(x, y + 2) === 0 && L.Monde.solidite(x, y + 3) === 0) { mur = [x, y]; break; }
        }
        j.x = mur[0] * 16 + 8; j.y = (mur[1] + 3) * 16 + 8; j.angle = -Math.PI / 2;
        for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.hypot(e.x - j.x, e.y - j.y) < 100) L.Entites.retirer(e);
        L.Entites.indexer();
        L.Combat.tirer(j, def);
        voler(120);
        return { booms: booms.length, rayon: booms.length && booms[0].rayon, auPied: booms.length && Math.abs(booms[0].y - (mur[1] + 1) * 16) < 14 };
    }""")
    assert r["booms"] == 1 and r["rayon"] == 64 and r["auPied"], r
