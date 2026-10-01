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


#: Lot 2b : les gens prennent feu.
FEU = """
    function passant(dx, dy) { const p = o.poser('ouvrier', dx, dy); p.vie = 100; p.vieMax = 100; return p; }
    function images(n) { for (let i = 0; i < n; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majBrasiers(); L.Combat.majGensEnFeu(); } }
"""


def test_le_passant_touche_par_la_flaque_prend_feu_fuit_et_brule(banc):
    """Touché par la flaque, il s'enflamme, part en courant (`fuit`), perd de la vie, puis le feu s'éteint de
    lui-même ; et une mort dans les flammes est une mort du lanceur (`mort_pieton`)."""
    r = banc("""function (L, o) {""" + PRELUDE + FEU + """
        const crimes = [], vrai = L.Police.signalerCrime;
        L.Police.signalerCrime = function (type, x, y, vu) { crimes.push(type); return vrai(type, x, y, vu); };
        const p = passant(60, 0), q = passant(-60, 0);
        q.vie = 8;
        const def = L.Combat.armeDef('molotov');
        L.Combat.allumer(p.x, p.y, { arme: 'molotov', tireur: j, feu_s: def.feu_s });
        L.Combat.allumer(q.x, q.y, { arme: 'molotov', tireur: j, feu_s: def.feu_s });
        images(21);
        const pris = { feu: p.enFeu > 0, etat: p.etat, vie: p.vie };
        for (const f of L.B.entites.filter(function (e) { return e.type === 'brasier'; })) L.Entites.retirer(f);
        p.x += 200;                                    // loin de la flaque : il brule de lui-meme, puis s'eteint
        images(L.B.defs.armes_regles.incendie.gens.duree_s * 60 + 30);
        return { pris: pris, apres: { feu: p.enFeu > 0, vie: p.vie }, mort: !q.vivant, crimes: crimes };
    }""")
    assert r["pris"]["feu"] and r["pris"]["etat"] == "fuit", r
    assert r["apres"]["feu"] is False and r["apres"]["vie"] < r["pris"]["vie"], f"il brûle, puis le feu s'éteint : {r}"
    assert r["mort"] and "mort_pieton" in r["crimes"], f"une mort dans le feu est celle du lanceur : {r}"


def test_un_passant_en_feu_allume_son_voisin_mais_jamais_toute_la_foule(banc):
    r = banc("""function (L, o) {""" + PRELUDE + FEU + """
        const g = L.B.defs.armes_regles.incendie.gens;
        const foule = [];
        for (let k = 0; k < 12; k++) foule.push(passant(40 + (k % 4) * 6, (Math.floor(k / 4) - 1) * 6));
        for (const p of foule) { p.etat = 'assomme'; p.minuterie = 99999; }   // qu'ils restent serres
        L.Combat.enflammer(foule[0], j, null, foule[0]);
        let max = 0;
        for (let i = 0; i < 300; i++) {
            images(1);
            max = Math.max(max, L.B.entites.filter(function (e) { return e.enFeu > 0; }).length);
        }
        return { max: max, plafond: g.max, voisin: foule.filter(function (p) { return p.enFeuDe; }).length };
    }""")
    assert r["voisin"] >= 2, f"le feu ne passe à personne : {r}"
    assert r["max"] <= r["plafond"], f"toute la foule s'embrase : {r}"


def test_le_joueur_brule_aussi_et_l_eau_l_eteint(banc):
    """Le joueur prend feu (même dans son propre feu), perd de la vie, et se jeter à l'eau l'éteint."""
    r = banc("""function (L, o) {""" + PRELUDE + FEU + """
        j.intouchable = false; j.invincible = 0;
        const vie = j.vie;
        L.Combat.enflammer(j, j, null, j);
        images(41);
        const brule = { feu: j.enFeu > 0, perdu: vie - j.vie };
        const c = L.Monde.carte;
        let eau = null;
        for (let y = 0; y < c.h && !eau; y++) for (let x = 0; x < c.w; x++) if (L.Monde.estEau(x, y)) { eau = [x, y]; break; }
        j.x = eau[0] * 16 + 8; j.y = eau[1] * 16 + 8;
        images(1);
        return { brule: brule, eteint: !(j.enFeu > 0) };
    }""")
    assert r["brule"]["feu"] and r["brule"]["perdu"] > 0, f"le joueur ne brûle pas dans son propre feu : {r}"
    assert r["eteint"], "l'eau n'éteint pas le joueur"


def test_l_extincteur_eteint_les_gens_et_la_flaque(banc):
    r = banc("""function (L, o) {""" + PRELUDE + FEU + """
        const p = passant(24, 0);
        p.etat = 'assomme'; p.minuterie = 99999;
        L.Combat.enflammer(p, null, 600, p);
        const f = L.Combat.allumer(j.x + 30, j.y + 2, { arme: 'molotov', tireur: j, feu_s: 8 });
        const avant = f.reste;
        L.B.partie.armes.extincteur = { mun: 100, usure: 0 }; j.arme = 'extincteur';
        j.angle = 0; j.etat = 'attaque'; j.phase = 'actif'; j.arc = L.Combat.armeDef('extincteur');
        L.Entites.indexer();
        for (let i = 0; i < 10; i++) { L.B.t++; L.Combat.majJet(j); }
        return { passant: p.enFeu > 0, flaque: avant - f.reste };
    }""")
    assert r["passant"] is False, "l'extincteur n'éteint pas le passant"
    assert r["flaque"] >= 60, f"l'extincteur n'entame pas la flaque : {r}"


#: Lot 2c : le feu se propage, borné.
PROPAGE = """
    const c = L.Monde.carte, P = L.B.defs.armes_regles.incendie.propagation;
    function trouver(test) {
        for (let y = 3; y < c.h - 3; y++) for (let x = 3; x < c.w - 3; x++) if (test(x, y)) return [x, y];
        return null;
    }
    function pelouse(x, y) {
        for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) if (c.sol[y + dy][x + dx] !== ',') return false;
        return true;
    }
    function feu(x, y) { return L.Combat.allumer(x, y, { arme: 'molotov', tireur: j, feu_s: L.Combat.armeDef('molotov').feu_s }); }
    function brasiers() { return L.B.entites.filter(function (e) { return e.type === 'brasier'; }); }
    function vider() { for (const e of L.B.entites.slice()) if (e.type === 'pieton' || e.type === 'vehicule') L.Entites.retirer(e); }
    function laisser(n, suivre) {
        let max = 0;
        for (let i = 0; i < n; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majBrasiers(); max = Math.max(max, brasiers().length); if (suivre) suivre(); }
        return max;
    }
"""


def test_sur_l_herbe_d_ete_le_feu_gagne_puis_s_eteint_dans_sa_borne(banc):
    r = banc("""function (L, o) {""" + PRELUDE + PROPAGE + """
        L.B.partie.jour = 22;
        const ici = trouver(pelouse);
        vider();
        feu(ici[0] * 16 + 8, ici[1] * 16 + 8);
        const max = laisser(1500);
        return { ici: !!ici, max: max, plafond: P.max, fin: brasiers().length };
    }""")
    assert r["ici"], "pas de pelouse dans la ville du témoin"
    assert r["max"] >= 3, f"le feu ne gagne pas l'herbe : {r}"
    assert r["max"] <= r["plafond"] and r["fin"] == 0, f"le feu ne s'arrête pas : {r}"


def test_l_hiver_l_herbe_ne_brule_pas_et_l_asphalte_jamais(banc):
    r = banc("""function (L, o) {""" + PRELUDE + PROPAGE + """
        const ici = trouver(pelouse);
        vider();
        const hiver = L.Saisons.enHiver; L.Saisons.enHiver = function () { return true; };
        feu(ici[0] * 16 + 8, ici[1] * 16 + 8);
        const neige = laisser(300);
        L.Saisons.enHiver = hiver;
        for (const f of brasiers()) L.Entites.retirer(f);
        const route = trouver(function (x, y) { return L.Monde.estRoute(x, y) && L.Monde.estRoute(x + 2, y) && L.Monde.estRoute(x - 2, y) && L.Monde.estRoute(x, y + 2) && L.Monde.estRoute(x, y - 2); });
        feu(route[0] * 16 + 8, route[1] * 16 + 8);
        return { neige: neige, asphalte: laisser(300) };
    }""")
    assert r == {"neige": 1, "asphalte": 1}, r


def test_la_haie_et_le_banc_prennent_feu(banc):
    """La flaque gagne la haie de cèdres d'à côté, et un banc de bois ; l'hiver, pour que l'herbe ne compte pas."""
    r = banc("""function (L, o) {""" + PRELUDE + PROPAGE + """
        vider();
        const hiver = L.Saisons.enHiver; L.Saisons.enHiver = function () { return true; };
        const haie = trouver(function (x, y) { return c.sol[y][x] === '`' && !L.Monde.estRoute(x - 2, y); });
        const f = feu(haie[0] * 16 + 8 - P.pas_px, haie[1] * 16 + 8);
        laisser(P.cadence_images + 1);
        const surLaHaie = brasiers().some(function (b) { return b !== f && L.Monde.glyphe(Math.floor(b.x / 16), Math.floor(b.y / 16)) === '`'; });
        for (const b of brasiers()) L.Entites.retirer(b);
        const banc = L.B.entites.find(function (d) {
            if (d.type !== 'decor' || d.decor !== 'banc') return false;
            const tx = Math.floor(d.x / 16), ty = Math.floor(d.y / 16);
            return L.Monde.estRoute(tx, ty + 2) || L.Monde.estTrottoir(tx - 2, ty);
        });
        const g = feu(banc.x - P.pas_px, banc.y);
        laisser(P.cadence_images + 1);
        const surLeBanc = brasiers().some(function (b) { return b !== g && Math.hypot(b.x - banc.x, b.y - banc.y) < 2; });
        L.Saisons.enHiver = hiver;
        return { haie: !!haie, surLaHaie: surLaHaie, surLeBanc: surLeBanc };
    }""")
    assert r == {"haie": True, "surLaHaie": True, "surLeBanc": True}, r


def test_vingt_bouteilles_sur_un_grand_parc_restent_dans_la_borne(banc):
    """Le pire cas : vingt flaques sur une pelouse de 13 × 13. Jamais plus de `max` flaques à la fois (le compte y
    arrive : sans la borne, il la dépasse), jamais plus de `generations` générations, et tout s'éteint."""
    r = banc("""function (L, o) {""" + PRELUDE + PROPAGE + """
        L.B.partie.jour = 22;
        function grande(x, y) {
            for (let dy = -6; dy <= 6; dy++) for (let dx = -6; dx <= 6; dx++) { const g = c.sol[y + dy] && c.sol[y + dy][x + dx]; if (g !== ',') return false; }
            return true;
        }
        const ici = trouver(grande);
        vider();
        for (let k = 0; k < 20; k++) feu(ici[0] * 16 + 8 + (k % 5 - 2) * 30, ici[1] * 16 + 8 + (Math.floor(k / 5) - 1.5) * 30);
        let gen = 0;
        const max = laisser(2000, function () { for (const b of brasiers()) gen = Math.max(gen, b.generation || 0); });
        return { max: max, gen: gen, plafond: P.max, generations: P.generations, fin: brasiers().length };
    }""")
    assert r["max"] <= r["plafond"], f"plus de flaques que la borne : {r}"
    assert r["gen"] <= r["generations"], f"plus de générations que la borne : {r}"
    assert r["max"] == r["plafond"] and r["gen"] >= 2 and r["fin"] == 0, f"le témoin n'atteint pas la borne : {r}"
