"""L'Halloween au banc (`static/js/halloween.js`) : des citrouilles sur les perrons tout octobre, allumées
la nuit ; des lumières orange et violettes le soir du 31 ; le Clairon la veille. Rien de posé, aucun dé."""


def test_les_citrouilles_d_octobre_sur_les_perrons(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, res = L.B.defs.carte.residences;
        const cs = H.citrouilles();
        const encore = JSON.stringify(H.citrouilles()) === JSON.stringify(cs);
        return { n: cs.length, residences: res.length, encore: encore,
                 octobre: [30, 31, 32, 33, 34].map(function (j) { return H.octobreA(j); }),
                 an2: H.octobreA(33 + 40), part: L.B.defs.halloween.citrouilles.part };
    }""")
    assert r["octobre"] == [False, True, True, True, False]
    assert r["an2"] is True
    assert r["encore"], "les citrouilles changent de place d'un appel à l'autre"
    assert abs(r["n"] / r["residences"] - r["part"]) < 0.1, r


def test_une_citrouille_se_peint_en_octobre_et_s_allume_la_nuit(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, c = H.citrouilles()[0], j = B.joueur;
        j.x = c.x; j.y = c.y + 40; L.Monde.centrerCamera(j.x, j.y);
        const cx = B.cam.x, cy = B.cam.y;
        function peindre(jour, heure) {
            B.partie.jour = jour; B.partie.heure = heure / 24;
            const v = []; H.ajouterVisibles(v, cx, cy);
            const ctx = { fillStyle: '', couleurs: [], fillRect: function () { this.couleurs.push(this.fillStyle); } };
            v.forEach(function (e) { e.peindreFoire(ctx); });
            return { n: v.length, couleurs: ctx.couleurs, lampes: H.lampes({ x: cx, y: cy }).length };
        }
        return { jour: peindre(32, 12), nuit: peindre(32, 22), juillet: peindre(21, 22) };
    }""")
    assert r["jour"]["n"] >= 1 and "#e07b1a" in r["jour"]["couleurs"], r["jour"]
    assert "#ffd84a" not in r["jour"]["couleurs"] and r["jour"]["lampes"] == 0, "la citrouille est allumée en plein jour"
    assert "#ffd84a" in r["nuit"]["couleurs"] and r["nuit"]["lampes"] >= 1, "la citrouille ne s'allume pas la nuit"
    assert r["juillet"]["n"] == 0 and r["juillet"]["lampes"] == 0


def test_les_lumieres_du_31_et_le_clairon_de_la_veille(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, d = B.defs.halloween;
        const l = { sorte: 'fenetre', tx: 40, ty: 50 }, v = { sorte: 'lampadaire', tx: 40, ty: 50 };
        function a(jour, heure) { B.partie.jour = jour; B.partie.heure = heure / 24; return [H.couleur(l), H.couleur(v), H.ligneDuClairon()]; }
        return { soir31: a(33, 21), midi31: a(33, 12), soir30: a(32, 21), veille: a(32, 8), couleurs: d.lumieres.couleurs };
    }""")
    c, _, _ = r["soir31"]
    assert c and any(("%d,%d,%d" % tuple(x)) in c for x in r["couleurs"]), r
    assert r["soir31"][1] is None, "un lampadaire se déguise"
    assert r["midi31"][0] is None and r["soir30"][0] is None
    assert r["veille"][2] and "HALLOWEEN" in r["veille"][2] and r["soir31"][2] is None


def test_un_passant_sur_trois_sort_deguise_le_31_au_soir(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, A = L.Entites.archetypeDeRue();
        const gens = [];
        for (let k = 0; k < 300; k++) { const e = L.Entites.creerPieton(B.joueur.x + (k % 30) * 20, B.joueur.y + Math.floor(k / 30) * 20, A); if (e.tenue) gens.push(e); }
        function costumes(jour, heure) {
            B.partie.jour = jour; B.partie.heure = heure / 24;
            const par = {}; let n = 0;
            gens.forEach(function (e) { const c = H.costumeDe(e); if (c) { n++; par[c] = (par[c] || 0) + 1; } });
            return { n: n, par: par };
        }
        const soir = costumes(33, 19), encore = costumes(33, 20);
        const e = gens.find(function (g) { return H.costumeDe(g); });
        const tenue = H.tenueDe(e), memeObjet = H.tenueDe(e) === tenue;
        return { total: gens.length, soir: soir, encore: encore, apresMidi: costumes(33, 14).n, veille: costumes(32, 19).n,
                 lendemain: costumes(34, 19).n, part: B.defs.halloween.deguises.part, memeObjet: memeObjet,
                 autre: tenue !== e.tenue };
    }""")
    assert r["total"] >= 250
    assert abs(r["soir"]["n"] / r["total"] - r["part"]) < 0.08, r["soir"]
    assert len(r["soir"]["par"]) == 4, f"des costumes manquent : {r['soir']['par']}"
    assert r["encore"] == r["soir"], "un passant change de costume d'une heure à l'autre"
    assert r["apresMidi"] == 0 and r["veille"] == 0 and r["lendemain"] == 0
    assert r["memeObjet"] and r["autre"], "la tenue du costume se recalcule à chaque image"


def test_la_sorciere_a_son_chapeau_pointu_et_le_squelette_ses_os(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, G = L.Garderobe;
        const base = { squelette: 'homme', peau: '#e8b088', cheveux: '#3a2a1a', coiffure: 'courte', chapeau: 'aucun',
                       couleur_chapeau: '#c0392b', haut: 'chandail', couleur_haut: '#2980b9', motif: 'uni', bas: 'pantalon',
                       couleur_bas: '#2a2a3a', souliers: 'souliers', couleur_souliers: '#1a1a1a', accessoires: [], accent: '#e8b33c' };
        const out = {};
        ['sorciere', 'fantome', 'squelette', 'citrouille'].forEach(function (c) {
            const t = H.habillerEn(base, c);
            out[c] = { t: t, bas: G.grille(t, 'bas', 0).join('\\n'), cote: G.grille(t, 'cote', 0).join('\\n'), cuit: !!G.cuire(t) };
        });
        out.nu = G.grille(base, 'bas', 0).join('\\n');
        return out;
    }""")
    def hauteur(g):
        return len(g.split("\n"))

    def tete(g):
        return next(i for i, rangee in enumerate(g.split("\n")) if rangee.strip("."))

    def pointe(g):
        return next(rangee for rangee in g.split("\n") if rangee.strip(".")).replace(".", "")

    assert tete(r["sorciere"]["bas"]) <= tete(r["nu"]) - 3 and len(pointe(r["sorciere"]["bas"])) <= 2, "le chapeau de sorcière n'est pas pointu"
    assert "W" in r["squelette"]["bas"], "le squelette n'a pas ses os"
    assert r["fantome"]["t"]["peau"] == r["fantome"]["t"]["couleur_haut"], "le fantôme a la peau d'un vivant"
    assert r["citrouille"]["t"]["couleur_haut"] == "#e07b1a"
    assert all(r[c]["cuit"] for c in ("sorciere", "fantome", "squelette", "citrouille"))
    assert hauteur(r["sorciere"]["bas"]) == hauteur(r["nu"])


#: Le joueur dans un quartier de maisons, à côté d'une citrouille.
QUARTIER = """
    function dansLeQuartier(L) {
        const H = L.Halloween, M = L.Monde, d = L.B.defs.halloween.enfants, j = L.B.joueur;
        // La citrouille la mieux entouree (les bandes naissent au pied d'une citrouille de 220 a 480 px).
        const ici = H.citrouilles().filter(function (p) { const z = M.zoneA(p.x, p.y); return z && d.districts.indexOf(z.district) >= 0; });
        let c = null, mieux = -1;
        for (const p of ici) {
            const n = ici.filter(function (q) { const dd = Math.hypot(q.x - p.x, q.y - p.y); return dd >= 260 && dd <= 440; }).length;
            if (n > mieux) { mieux = n; c = p; }
        }
        j.x = c.x; j.y = c.y + 30; M.centrerCamera(j.x, j.y); L.Entites.indexer();
        return c;
    }
"""


def test_des_bandes_d_enfants_le_31_au_soir_seulement(banc):
    r = banc("function (L, o) {" + QUARTIER + """
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, d = B.defs.halloween.enfants;
        dansLeQuartier(L);
        function tourner(jour, heure, n) { B.partie.jour = jour; B.partie.heure = heure / 24; for (let k = 0; k < n; k++) { B.t++; H.maj(); } return H.bandes().length; }
        const avant = tourner(33, 15, 900), veille = tourner(32, 19, 900);
        const soir = tourner(33, 18.5, 2400);
        const bandes = H.bandes().map(function (b) {
            return { n: b.enfants.length, archs: b.enfants.map(function (e) { return e.arch; }),
                     suivent: b.enfants.slice(1).every(function (e) { return e.suit === b.enfants[0]; }),
                     deguises: b.enfants.every(function (e) { return !!e.costume; }) };
        });
        return { avant: avant, veille: veille, soir: soir, bandes: bandes, max: d.bandes_max, taille: d.taille };
    }""")
    assert r["avant"] == 0 and r["veille"] == 0, "des enfants passent l'Halloween hors du 31 au soir"
    assert 1 <= r["soir"] <= r["max"], r
    for b in r["bandes"]:
        assert r["taille"][0] <= b["n"] <= r["taille"][1] and set(b["archs"]) == {"enfant"}, b
        assert b["suivent"] and b["deguises"], b


def test_le_chef_de_bande_dit_des_bonbons_a_une_porte_a_citrouille(banc):
    r = banc("function (L, o) {" + QUARTIER + """
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B;
        const c = dansLeQuartier(L);
        B.partie.jour = 33; B.partie.heure = 18.5 / 24;
        for (let k = 0; k < 2400 && !H.bandes().length; k++) { B.t++; H.maj(); }
        const b = H.bandes()[0], chef = b.enfants[0];
        chef.x = b.cible.x; chef.y = b.cible.y;
        for (let k = 0; k < 30; k++) { B.t++; H.maj(); }
        return { mot: chef.bulle ? chef.bulle.texte : null, mots: B.defs.halloween.enfants.mots,
                 surUneCitrouille: H.citrouilles().some(function (p) { return Math.abs(p.x - b.faites[0].x) < 1 && Math.abs(p.y - b.faites[0].y) < 1; }) };
    }""")
    assert r["mot"] in r["mots"], r
    assert r["surUneCitrouille"], "la bande s'arrête à une porte sans citrouille"


def test_apres_l_heure_les_enfants_rentrent(banc):
    r = banc("function (L, o) {" + QUARTIER + """
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, d = B.defs.halloween.enfants;
        dansLeQuartier(L);
        B.partie.jour = 33; B.partie.heure = 18.5 / 24;
        for (let k = 0; k < 2400 && !H.bandes().length; k++) { B.t++; H.maj(); }
        const n = H.bandes().length;
        B.partie.heure = (d.jusqu_h + 0.5) / 24;
        B.joueur.x += 5000; L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        for (let k = 0; k < 60; k++) { B.t++; H.maj(); }
        return { avant: n, apres: H.bandes().length };
    }""")
    assert r["avant"] >= 1 and r["apres"] == 0, r


#: Entrer dans la maison hantée (un logement des Érables), à l'heure dite.
MAISON = """
    function entrerALaMaison(L, o, jour, heure) {
        const B = L.B, j = B.joueur, porte = L.Halloween.maisonPorte();
        if (B.interieur) { L.Jeu.sortir(); o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1); }
        B.partie.jour = jour; B.partie.heure = heure / 24;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
        L.Jeu.entrer(porte); o.fondu();
        for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
        B.partie.jour = jour; B.partie.heure = heure / 24;
        return porte;
    }
"""


def test_la_maison_hantee_est_un_logement_des_erables(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.Halloween.maisonPorte(), z = L.Monde.zoneA(p.x * 16 + 8, p.y * 16 + 8);
        return { interieur: String(p.interieur || p.lieu || ''), district: z && z.district, encore: L.Halloween.maisonPorte() === p };
    }""")
    assert r["interieur"].startswith("logement") and r["district"] == "erables" and r["encore"], r


def test_la_maison_n_est_hantee_que_le_31_au_soir(banc):
    r = banc("function (L, o) {" + MAISON + """
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const H = L.Halloween, d = L.B.defs.halloween.maison;
        function hantee(jour, heure) {
            entrerALaMaison(L, o, jour, heure);
            for (let k = 0; k < 60 * d.lumiere_s * 3; k++) { L.B.partie.heure = heure / 24; o.frame(1); }
            const v = H.visite();
            return v ? { eteintes: v.eteintes, fantome: !!v.fantome } : null;
        }
        return { soir: hantee(33, 20), apresMidi: hantee(33, 15), veille: hantee(32, 20) };
    }""")
    assert r["soir"] and r["soir"]["eteintes"] >= 2 and r["soir"]["fantome"], r
    assert r["apresMidi"] is None and r["veille"] is None, r


def test_le_sac_de_bonbons_paie_une_fois_par_annee(banc):
    r = banc("function (L, o) {" + MAISON + """
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const H = L.Halloween, B = L.B, j = B.joueur;
        function prendre(jour) {
            entrerALaMaison(L, o, jour, 20); o.frame(2);
            const s = H.sac(); if (!s) return null;
            const avant = B.partie.argent;
            j.x = s.x; j.y = s.y; L.Entites.indexer(); o.frame(2);
            o.tape('KeyE', 1); o.frame(2);
            return B.partie.argent - avant;
        }
        return { premier: prendre(33), encore: prendre(33), anDApres: prendre(73), prime: B.defs.halloween.maison.prime };
    }""")
    assert r["premier"] == r["prime"], r
    assert r["encore"] in (None, 0), "le sac paie deux fois la même année"
    assert r["anDApres"] == r["prime"], "le sac ne revient pas l'année suivante"


def test_la_musique_d_halloween_joue_dehors_le_31_au_soir(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const B = L.B, C = L.Son.Chef;
        function morceau(jour, heure) { B.partie.jour = jour; B.partie.heure = heure / 24; const v = C.voulu(); return v ? v.slug : null; }
        return { soir: morceau(33, 19), apresMidi: morceau(33, 14), veille: morceau(32, 19) };
    }""")
    assert r["soir"] == "halloween", r
    assert r["apresMidi"] != "halloween" and r["veille"] != "halloween", r


def test_les_sons_d_halloween_se_chargent_le_31_et_la_maison_parle(banc):
    r = banc("function (L, o) {" + MAISON + """
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const S = L.Son, appels = { lieux: [], sfx: [], voix: [], histoires: [] };
        S.Lieu.charger = function (l) { appels.lieux.push(l); };
        S.SFX.porte_grince = function () { appels.sfx.push('porte_grince'); };
        S.Voix.parler = function (slug) { appels.voix.push(slug); };
        S.Voix.chargerHistoire = function (p) { appels.histoires.push(p); };
        L.B.partie.jour = 32; L.B.partie.heure = 19 / 24; for (let k = 0; k < 400; k++) { L.B.t++; L.Halloween.maj(); }
        const veille = appels.lieux.length;
        entrerALaMaison(L, o, 33, 20);
        for (let k = 0; k < 30; k++) { L.B.partie.heure = 20 / 24; o.frame(1); }
        return { veille: veille, appels: appels };
    }""")
    a = r["appels"]
    assert r["veille"] == 0, "les sons d'Halloween se chargent la veille"
    assert "halloween" in a["lieux"], a
    assert "porte_grince" in a["sfx"], "la porte de la maison hantée ne grince pas"
    assert "halloween" in a["histoires"] and "halloween-entree" in a["voix"], a


def test_ni_la_police_ni_les_gangs_ni_les_commis_ne_se_deguisent(banc):
    """La relecture : un agent sur trois poursuivait le joueur en sorcière. On doit reconnaître la police,
    les gangs, les commis et les gens d'une mission."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, A = L.Entites.archetypeDeRue();
        B.partie.jour = 33; B.partie.heure = 19 / 24;
        const gens = [];
        for (let k = 0; k < 60; k++) { const e = L.Entites.creerPieton(B.joueur.x + k * 12, B.joueur.y, A); if (H.costumeDe(e)) gens.push(e); }
        const marques = [['agent', true], ['gang', 'chevreuils'], ['commerce', 'depanneur'], ['mission', 'm1'], ['metier', 'facteur']];
        const encore = marques.map(function (m, i) { const e = gens[i]; e[m[0]] = m[1]; return [m[0], H.costumeDe(e)]; });
        return { n: gens.length, encore: encore };
    }""")
    assert r["n"] >= 5
    for champ, costume in r["encore"]:
        assert costume is None, f"un passant marqué « {champ} » se déguise"


def test_une_bande_retiree_de_la_ville_libere_sa_place(banc):
    r = banc("function (L, o) {" + QUARTIER + """
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B;
        dansLeQuartier(L);
        B.partie.jour = 33; B.partie.heure = 18.5 / 24;
        for (let k = 0; k < 2400 && !H.bandes().length; k++) { B.t++; H.maj(); }
        const b = H.bandes()[0];
        b.enfants.forEach(L.Entites.retirer);           // `peupler` l'a retiree, loin de l'ecran
        for (let k = 0; k < 30; k++) { B.t++; H.maj(); }
        return { encore: H.bandes().indexOf(b) >= 0 };
    }""")
    assert r["encore"] is False, "une bande retirée de la ville garde sa place"


def test_l_invite_du_sac_se_lit_et_la_maison_n_est_pas_hantee_a_l_etage(banc):
    r = banc("function (L, o) {" + MAISON + """
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const H = L.Halloween, B = L.B, j = B.joueur;
        entrerALaMaison(L, o, 33, 20); o.frame(2);
        const s = H.sac(); j.x = s.x; j.y = s.y; L.Entites.indexer(); o.frame(2);
        const msg = JSON.stringify(B.msg);
        const vrai = B.interieur; B.interieur = Object.assign({}, vrai, { slug: vrai.slug + '_haut' });
        const etage = H.dansLaMaison(); B.interieur = vrai;
        return { msg: msg, etage: etage, ici: H.dansLaMaison() };
    }""")
    assert "ACTION" in r["msg"], f"l'invite du sac est écrasée : {r['msg']}"
    assert r["ici"] is True and r["etage"] is False, r


def test_le_passant_deguise_se_dessine_en_costume(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const H = L.Halloween, B = L.B, A = L.Entites.archetypeDeRue(), j = B.joueur;
        B.partie.jour = 33; B.partie.heure = 19 / 24;
        let e = null;
        for (let k = 0; k < 40 && !e; k++) { const q = L.Entites.creerPieton(j.x + 20, j.y + 10, A); if (H.costumeDe(q)) e = q; else L.Entites.retirer(q); }
        const voulu = H.tenueDe(e), cuire = L.Garderobe.cuire; let vu = false;
        L.Garderobe.cuire = function (tn) { if (tn === voulu) vu = true; return cuire(tn); };
        L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer(); L.Jeu.rendre();
        L.Garderobe.cuire = cuire;
        return { vu: vu };
    }""")
    assert r["vu"], "le passant déguisé se dessine dans sa tenue de tous les jours"


def test_le_decor_et_les_costumes_ne_tirent_aucun_de(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const H = L.Halloween, B = L.B, j = B.joueur, A = L.Entites.archetypeDeRue();
        const gens = []; for (let k = 0; k < 20; k++) gens.push(L.Entites.creerPieton(j.x + k * 9, j.y, A));
        B.partie.jour = 33; B.partie.heure = 21 / 24;
        L.graine(3); const tirage = B.rng; let des = 0;
        B.rng = function () { if (String(new Error().stack).indexOf('halloween.js') >= 0) des++; return tirage(); };
        const v = []; H.ajouterVisibles(v, B.cam.x, B.cam.y); H.lampes(B.cam); H.citrouilles();
        gens.forEach(function (e) { H.tenueDe(e); });
        H.couleur({ sorte: 'fenetre', tx: 3, ty: 4 }); H.ligneDuClairon();
        B.rng = tirage;
        return { des: des };
    }""")
    assert r["des"] == 0
