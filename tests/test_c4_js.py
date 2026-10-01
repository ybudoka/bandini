"""Le C4 (`docs/jalons/les-explosifs.md`, vague 3, lot 3a) : on le pose — au sol, contre un mur, sur un char qu'il
suit —, trois au plus, et on tient le bouton pour tout faire sauter."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur;
    j.intouchable = true;
    const booms = [];
    const f = L.Explosions.faire;
    L.Explosions.faire = function (x, y, o) { booms.push({ x: x, y: y, coupable: o.coupable === j, rayon: o.rayon }); return f.apply(this, arguments); };
    function donner(n) { L.B.partie.armes.plastic = { mun: n === undefined ? 6 : n, usure: 0 }; j.arme = 'plastic'; L.B.partie.arme = 'plastic'; }
    function charges() { return L.B.entites.filter(function (e) { return e.type === 'charge'; }); }
    function poser() { o.touche('KeyJ'); o.frame(3); o.relacher('KeyJ'); o.frame(2); }
    function tenir() { o.touche('KeyJ'); o.frame(L.B.defs.armes_regles.c4.tenir_images + 5); o.relacher('KeyJ'); o.frame(2); }
    const ligne = o.ligneDroite(); j.x = ligne.x; j.y = ligne.y; j.angle = 0; L.Monde.centrerCamera(j.x, j.y);
    for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.hypot(e.x - j.x, e.y - j.y) < 120) L.Entites.retirer(e);
"""


def test_un_appui_pose_tenir_fait_tout_sauter(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(6);
        o.frame(2);
        poser(); j.x += 30; o.frame(2); poser();
        const posees = { n: charges().length, mun: L.B.partie.armes.plastic.mun, booms: booms.length };
        j.x += 60; o.frame(2);
        tenir();
        return { posees: posees, apres: charges().length, booms: booms.length, coupable: booms.every(function (b) { return b.coupable; }) };
    }""")
    assert r["posees"] == {"n": 2, "mun": 4, "booms": 0}, r
    assert r["apres"] == 0 and r["booms"] == 2 and r["coupable"], r


def test_trois_au_plus_et_sans_c4_rien(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(6);
        o.frame(2);
        for (let k = 0; k < 4; k++) { poser(); j.x += 24; o.frame(1); }
        const quatre = { n: charges().length, mun: L.B.partie.armes.plastic.mun };
        for (const c of charges()) L.Entites.retirer(c);
        donner(0); o.frame(2); poser();
        return { quatre: quatre, vide: charges().length };
    }""")
    assert r == {"quatre": {"n": 3, "mun": 3}, "vide": 0}, r


def test_pose_sur_un_char_il_le_suit_quand_il_roule(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3);
        const v = o.char('auto', 22, 0);
        o.frame(2);
        poser();
        const c = charges()[0];
        const avant = { x: c.x - v.x, y: c.y - v.y, sur: c.sur === v };
        v.x += 80; v.y += 10; v.angle += 0.6;
        L.Combat.majCharges();
        const d = Math.hypot(c.x - v.x, c.y - v.y), d0 = Math.hypot(avant.x, avant.y);
        tenir();
        return { sur: avant.sur, ecart: Math.abs(d - d0), booms: booms.length, pres: booms.length && Math.hypot(booms[0].x - v.x, booms[0].y - v.y) < d0 + 2 };
    }""")
    assert r["sur"] and r["ecart"] < 1, f"la charge ne suit pas le char : {r}"
    assert r["booms"] >= 1 and r["pres"], f"la charge saute sur le char (et le char saute avec) : {r}"


def test_au_noir_d_une_porte_les_charges_restent_hors_champ(banc):
    """On les pose, on passe une porte : elles ne sautent plus — ni dehors en notre absence, ni au retour."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3);
        const c = L.Monde.carte, porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 2) * L.TT + 10; o.frame(2);
        poser();
        const posees = charges().length;
        j.y = (porte.y + 1) * L.TT + 10; o.frame(1);
        o.entrer(porte);
        tenir();
        o.sortir();
        o.frame(60); tenir();
        return { posees: posees, booms: booms.length, dehors: charges().length };
    }""")
    assert r == {"posees": 1, "booms": 0, "dehors": 0}, r


def test_la_charge_se_dessine_et_clignote(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3); o.frame(2); poser();
        const c = charges()[0];
        let peinte = 0; const d = L.Combat.dessinerCharge;
        L.Combat.dessinerCharge = function (ctx, e) { if (e === c) peinte++; return d.apply(this, arguments); };
        L.Jeu.rendre();
        return { peinte: peinte };
    }""")
    assert r["peinte"] == 1


def test_le_char_piege_saute_quand_un_voleur_le_demarre(banc):
    """Lot 4a : posé sur un char garé et vide, le C4 est un piège ; un passant le vole (il prend le volant) — boum,
    et le coupable est le poseur."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3);
        const v = o.char('auto', 22, 0); v.conducteur = null; v.etat = 'stationne';
        o.frame(2);
        poser();
        const c = charges()[0];
        const piege = !!(c && c.piege);
        j.x -= 120; o.frame(2);
        L.Combat.majCharges(); const avant = booms.length;
        v.conducteur = 'trafic';                     // un voleur ouvre la portiere et demarre
        L.Combat.majCharges();
        return { piege: piege, avant: avant, booms: booms.length, coupable: booms.length > 0 && booms[0].coupable,
                 restantes: charges().length };
    }""")
    assert r["piege"] and r["avant"] == 0, r
    assert r["booms"] >= 1 and r["coupable"] and r["restantes"] == 0, r


def test_le_joueur_qui_monte_dans_son_char_piege_saute_aussi(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3);
        const v = o.char('auto', 22, 0); v.conducteur = null; v.etat = 'stationne';
        o.frame(2); poser();
        const vie = j.vie; j.intouchable = false; j.invincible = 0;
        L.Vehicules.monter(j, v);
        L.Combat.majCharges();
        o.frame(5);                                  // le char saute a son tour, a l'image suivante (la chaine)
        return { booms: booms.length, blesse: j.vie < vie || !j.vivant, epave: v.etat === 'epave' };
    }""")
    assert r["booms"] >= 1 and r["epave"] and r["blesse"], r


def test_sur_un_char_qui_roule_ce_n_est_pas_un_piege(banc):
    """Un char du trafic qui a son conducteur : la charge s'y colle et le suit, mais ne saute qu'au bouton."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner(3);
        const v = o.char('auto', 22, 0); v.conducteur = 'trafic';
        o.frame(1); poser();
        const c = charges()[0];
        L.Combat.majCharges(); L.Combat.majCharges();
        return { colle: !!(c && c.sur === v), piege: !!(c && c.piege), booms: booms.length };
    }""")
    assert r == {"colle": True, "piege": False, "booms": 0}, r
