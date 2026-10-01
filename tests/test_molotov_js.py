"""Le Molotov en mieux (`docs/jalons/les-explosifs.md`, vague 2, lot 2a) : il s'allume d'abord, on voit la bouteille
voler, et sa flaque est plus grosse et plus visible — la nuit, elle éclaire le sol."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur;
    j.intouchable = true;
    function donner(slug, n) { L.B.partie.armes[slug] = { mun: n === undefined ? 3 : n, usure: 0 }; j.arme = slug; L.B.partie.arme = slug; }
    function bouteilles() { return L.B.entites.filter(function (e) { return e.type === 'projectile' && e.feu_s; }); }
    function appuyer() { o.touche('KeyJ'); o.frame(2); o.relacher('KeyJ'); o.frame(2); }
    const ligne = o.ligneDroite(); j.x = ligne.x; j.y = ligne.y; L.Monde.centrerCamera(j.x, j.y);
"""


def test_au_bouton_on_allume_puis_on_lance(banc):
    """Le premier appui allume le chiffon (rien ne part, rien ne sort du sac) ; le suivant lance la bouteille."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('molotov');
        o.frame(2);
        appuyer();
        const allume = { chiffon: !!j.chiffon, parties: bouteilles().length, mun: L.B.partie.armes.molotov.mun };
        o.frame(30);
        appuyer();
        return { allume: allume, chiffon: !!j.chiffon, parties: bouteilles().length, mun: L.B.partie.armes.molotov.mun };
    }""")
    assert r["allume"] == {"chiffon": True, "parties": 0, "mun": 3}, r
    assert r["chiffon"] is False and r["parties"] == 1 and r["mun"] == 2, r


def test_sans_bouteille_rien_ne_s_allume(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('molotov', 0);
        o.frame(2);
        appuyer();
        return { chiffon: !!j.chiffon, parties: bouteilles().length };
    }""")
    assert r == {"chiffon": False, "parties": 0}, r


def test_le_chiffon_s_eteint_si_on_range_la_bouteille_monte_dans_un_char_ou_passe_une_porte(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('molotov');
        o.frame(2);
        appuyer();
        const allume = !!j.chiffon;
        j.arme = 'poings'; L.B.partie.arme = 'poings'; o.frame(2);
        const range = !!j.chiffon;
        donner('molotov'); o.frame(2); appuyer();
        const v = o.char('auto', 0, 20); j.dansVehicule = v; o.frame(2);
        const auVolant = !!j.chiffon;
        j.dansVehicule = null; L.Entites.retirer(v);
        const c = L.Monde.carte, porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; o.frame(2);
        appuyer();
        const devant = !!j.chiffon;
        o.entrer(porte);
        return { allume: allume, range: range, auVolant: auVolant, devant: devant, dedans: !!L.B.interieur, porte: !!j.chiffon };
    }""")
    assert r == {"allume": True, "range": False, "auVolant": False, "devant": True, "dedans": True, "porte": False}, r


def test_on_voit_la_bouteille_voler_avec_son_ombre_et_sa_trainee(banc):
    """Elle se dessine (`Entites.dessiner` passe la main à `Combat.dessinerLance`), au-dessus de son ombre, elle
    tourne, et son chiffon laisse des flammes derrière elle."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('molotov');
        L.Combat.tirer(j, L.Combat.armeDef('molotov'));
        const b = bouteilles()[0];
        const avant = L.B.particules.length;
        for (let i = 0; i < 6; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majProjectiles(); }
        const trainee = L.B.particules.length - avant;
        let peinte = 0; const d = L.Combat.dessinerLance;
        L.Combat.dessinerLance = function (ctx, e) { if (e === b) peinte++; return d.apply(this, arguments); };
        L.Jeu.rendre();
        L.Combat.dessinerLance = d;
        const ctx = o.ctx, poses = [];
        ctx.drawImage = function (img, x, y) { poses.push(y); };
        ctx.translate = function (x, y) { poses.push(y); };
        L.Combat.dessinerLance(ctx, b, L.B.cam.x, L.B.cam.y);
        return { peinte: peinte, z: b.z, tour: b.tour, trainee: trainee, poses: poses };
    }""")
    assert r["peinte"] == 1, "la bouteille vole invisible"
    assert r["z"] > 4 and r["tour"] > 1, r
    assert r["trainee"] >= 6, f"pas de traînée de flammes : {r}"
    assert min(r["poses"]) < max(r["poses"]) - 4, f"la bouteille doit être peinte au-dessus de son ombre : {r}"


def test_la_flaque_est_plus_grosse_et_eclaire_la_nuit(banc):
    """30 px et 8 s (au lieu de 20 et 5) ; la nuit, la flaque et le chiffon allumé éclairent le sol
    (`Monde.lampesVisibles`)."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('molotov');
        L.B.partie.jour = 22; L.B.partie.heure = 23 / 24;
        const f = L.Combat.allumer(j.x + 40, j.y, { arme: 'molotov', tireur: j, feu_s: L.Combat.armeDef('molotov').feu_s });
        const reste = f.reste;
        appuyer(); L.Monde.centrerCamera(j.x, j.y);
        const cam = L.B.cam, lampes = L.Monde.lampesVisibles(cam);
        const pres = function (x, y) { return lampes.filter(function (l) { return Math.hypot(l.x + cam.x - x, l.y + cam.y - y) < 20; }).length; };
        return { r: f.r, reste: reste, feu: pres(f.x, f.y), chiffon: pres(j.x, j.y - 12), allume: !!j.chiffon, nuit: lampes.length };
    }""")
    assert r["r"] >= 30 and r["reste"] >= 8 * 60, r
    assert r["allume"] and r["feu"] >= 1 and r["chiffon"] >= 1, f"la nuit, le feu n'éclaire pas : {r}"
