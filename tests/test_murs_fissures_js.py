"""Le mur fissuré cède à une explosion, et lui seul (`Monde.ceder`, `Explosions.faire`)."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur, c = L.Monde.carte;
    j.intouchable = true;
    // Un mur plein de la ville, devenu fissuré pour le juge : un mur de facade avec du sol devant.
    let mur = null;
    for (let y = 2; y < c.h - 2 && !mur; y++) for (let x = 2; x < c.w - 2; x++) {
        if (c.sol[y][x] === 'F' && c.sol[y][x + 1] === 'F' && L.Monde.solidite(x, y + 1) === 0 && L.Monde.solidite(x + 1, y + 1) === 0) { mur = [x, y]; break; }
    }
    function poser(x, y, g) {
        c.sol[y] = c.sol[y].slice(0, x) + g + c.sol[y].slice(x + 1);
        c.solide[y * c.w + x] = c.legende[g].solide || 0;
    }
    poser(mur[0], mur[1], '0');
    const voisin = [mur[0] + 1, mur[1]];
"""


def test_une_explosion_fait_ceder_le_mur_fissure_et_pas_son_voisin(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const avant = L.Monde.solidite(mur[0], mur[1]);
        L.Explosions.faire(mur[0] * 16 + 8, (mur[1] + 1) * 16 + 4, { rayon: 30, degats: 50, coupable: null });
        return { avant: avant, glyphe: c.sol[mur[1]][mur[0]], apres: L.Monde.solidite(mur[0], mur[1]),
                 voisin: c.sol[voisin[1]][voisin[0]], voisinSolide: L.Monde.solidite(voisin[0], voisin[1]) };
    }""")
    assert r == {"avant": 1, "glyphe": "g", "apres": 0, "voisin": "F", "voisinSolide": 1}, r


def test_seul_le_mur_fissure_cede(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        return { fissure: L.Monde.ceder(mur[0], mur[1]), plein: L.Monde.ceder(voisin[0], voisin[1]),
                 rue: L.Monde.ceder(mur[0], mur[1] + 1) };
    }""")
    assert r == {"fissure": True, "plein": False, "rue": False}, r


def test_le_c4_pose_contre_le_mur_l_ouvre(banc):
    """Le geste entier : la charge posée face au mur, on tient le bouton, et on passe."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.armes.plastic = { mun: 3, usure: 0 }; j.arme = 'plastic'; L.B.partie.arme = 'plastic';
        j.x = mur[0] * 16 + 8; j.y = (mur[1] + 1) * 16 + 10; j.angle = -Math.PI / 2; L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        o.touche('KeyJ'); o.frame(3); o.relacher('KeyJ'); o.frame(2);
        const posee = L.B.entites.filter(function (e) { return e.type === 'charge'; }).length;
        j.y += 40; o.frame(2);
        o.touche('KeyJ'); o.frame(L.B.defs.armes_regles.c4.tenir_images + 5); o.relacher('KeyJ'); o.frame(2);
        return { posee: posee, glyphe: c.sol[mur[1]][mur[0]], passe: L.Monde.solidite(mur[0], mur[1]) };
    }""")
    assert r == {"posee": 1, "glyphe": "g", "passe": 0}, r


def test_le_mur_fissure_se_peint_fissure(banc):
    r = banc("""function (L, o) {
        function traces(cle) { const k = o.doc.createElement('canvas').getContext('2d'); k.traces = []; L.TUILES[cle](k, 0, 16); return k.traces.length; }
        return { mur: traces('B'), fissure: traces('0'), piece: traces('B@piece'), fissurePiece: traces('0@piece') };
    }""")
    assert r["fissure"] > r["mur"] and r["fissurePiece"] > r["piece"], r
