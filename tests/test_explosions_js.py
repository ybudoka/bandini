"""L'explosion commune (`explosions.js`) : celle du char, de la grenade, de la dynamite — une seule.

⚠️ Jusqu'au 29 sept. 2026, seule `Vehicules.exploser` savait faire sauter quelque chose. Les explosifs
(`docs/jalons/les-explosifs.md`) passent par le MEME chemin : deux explosions ecrites deux fois
divergent — l'une casse le lampadaire, l'autre pas.
"""


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


def test_une_explosion_sans_coupable_ne_signale_rien(banc):
    """Un char du trafic qui brule tout seul : pas de delit, pas d'agent qui accourt."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, vus = [], entendus = [];
        L.Police.signalerCrime = function (k) { vus.push(k); };
        L.Police.entendre = function (x, y, r) { entendus.push(r); return 0; };
        L.Explosions.faire(j.x + 80, j.y, { rayon: 48, degats: 110, coupable: null, auteur: null });
        return { vus: vus, entendus: entendus };
    }""")
    assert r == {"vus": [], "entendus": []}


def test_le_char_saute_toujours_par_la_meme_explosion(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let appels = 0; const f = L.Explosions.faire;
        L.Explosions.faire = function () { appels++; return f.apply(this, arguments); };
        const v = o.char('auto', 60, 0);
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        return { appels: appels, etat: v.etat };
    }""")
    assert r == {"appels": 1, "etat": "epave"}


def test_les_chars_sautent_en_chaine_un_par_image(banc):
    """Dix chars colles : le premier saute, le suivant a l'image d'apres — jamais dans sa boucle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const chars = [];
        for (let i = 0; i < 10; i++) { const v = o.char('auto', 60 + i * 34, 0); v.vie = 1; chars.push(v); }
        let sautes = 0; const f = L.Explosions.faire;
        L.Explosions.faire = function () { sautes++; return f.apply(this, arguments); };
        L.Vehicules.endommager(chars[0], 9999, L.B.joueur);
        const apres0 = chars.filter(function (v) { return v.etat === 'epave'; }).length;
        for (let i = 0; i < 12; i++) { L.Entites.indexer(); L.Explosions.maj(); }
        return { apres0: apres0, fin: chars.filter(function (v) { return v.etat === 'epave'; }).length, sautes: sautes };
    }""")
    assert r["apres0"] == 1, "la chaine a saute dans la meme image"
    assert r["fin"] == 10 and r["sautes"] == 10, r
