"""Les sauts de Rocco (P4, des choses à collectionner, vague 4) au banc : un tremplin neuf fait décoller comme une
rampe, un saut réussi se compte (le vol, la vitesse, l'atterrissage), un saut raté se dit — et la prime, les paliers,
le carnet, la sauvegarde et les triches.

⚠️ On pilote par la physique elle-même (`majPhysique` + `avancer`, gaz à fond, droit devant) et on appelle
`Collections.majSauts` à chaque image : la boucle entière ferait braquer le char et passer les gens.
"""

LANCER = """
    function lancer(L, o, slug, recul, gaz, images, apres, modele) {
        const q = L.Collections.saut(slug);
        if (!L.Hud.messages) { L.Hud.messages = []; const vrai = L.Hud.message; L.Hud.message = function (t) { L.Hud.messages.push(t); return vrai.apply(this, arguments); }; }
        const j = L.B.joueur;
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return (e.type === 'pieton' && !e.personnage) || (e.type === 'vehicule' && e !== j.dansVehicule); })
            .forEach(L.Entites.retirer);
        const a = Math.atan2(q.dy, q.dx);
        const x = (q.x - q.dx * (recul || 6)) * 16 + 8, y = (q.y - q.dy * (recul || 6)) * 16 + 8;
        const v = L.Vehicules.creer(modele || (q.quatre_roues ? 'quatre_roues' : 'auto'), x, y, a, { couleur: '#888888' });
        v.etat = 'roule'; v.conducteur = j; j.dansVehicule = v; j.x = x; j.y = y;
        let zMax = 0, decolle = false;
        for (let k = 0; k < (images || 200); k++) {
            L.Vehicules.majPhysique(v, { gaz: gaz === undefined ? 1 : gaz, frein: 0, direction: 0 });
            L.Vehicules.avancer(v);
            if (apres) apres(v, k);
            j.x = v.x; j.y = v.y;
            L.Collections.majSauts(j);
            if (v.z > 0) decolle = true;
            zMax = Math.max(zMax, v.z);
            if (decolle && !L.Collections.vol) break;
        }
        L.Entites.retirer(v); j.dansVehicule = null;
        return { q: q, v: v, zMax: zMax, decolle: decolle, dit: L.Hud.messages.slice(-3).join(' / ') };
    }
"""


def test_un_tremplin_neuf_fait_decoller_comme_une_rampe(banc):
    r = banc("function (L, o) {" + LANCER + """
        L.Jeu.commencer();
        const neufs = L.Collections.sauts().filter(function (q) { return !q.rampe; });
        const q = neufs[0];
        const sur = [L.Collections.estTremplin(q.x, q.y), L.Collections.estTremplin(q.x + q.dx, q.y + q.dy)];
        const a_cote = L.Collections.estTremplin(q.x + q.dy + 3, q.y + q.dx + 3);
        const dansLaCarte = L.Monde.estRampe(q.x, q.y);
        const vrai = L.B.bloc; L.B.bloc = { slug: 'rang' };
        const enBloc = L.Collections.estTremplin(q.x, q.y);
        L.B.bloc = vrai;
        const s = lancer(L, o, q.slug);
        return { neufs: neufs.length, total: L.Collections.totalSauts(), sur: sur, a_cote: a_cote, dansLaCarte: dansLaCarte,
                 enBloc: enBloc, zMax: s.zMax, decolle: s.decolle };
    }""")
    assert r["total"] == 20 and r["neufs"] == 12, r
    assert r["sur"] == [True, True] and r["a_cote"] is False, r
    assert r["dansLaCarte"] is False, "le tremplin est dans la carte : il devait voyager à part"
    assert r["enBloc"] is False, "un tremplin de la ville fait décoller dans un bloc"
    assert r["decolle"] and r["zMax"] > 6, f"le char lancé ne décolle pas du tremplin : {r}"


def test_un_saut_reussi_se_compte_une_fois_et_paie(banc):
    r = banc("function (L, o) {" + LANCER + """
        L.Jeu.commencer();
        const q = L.Collections.sauts().filter(function (s) { return !s.rampe; })[1];
        let son = 0; const vrai = L.Son.SFX.saut_reussi; L.Son.SFX.saut_reussi = function () { son++; };
        const argent = L.B.partie.argent;
        const s1 = lancer(L, o, q.slug, 7);
        const premier = JSON.parse(JSON.stringify(L.B.partie.collections.sauts[q.slug] || null));
        const msg = s1.dit, gain = L.B.partie.argent - argent;
        const journal = L.B.partie.carnet[L.B.partie.carnet.length - 1];
        const argent2 = L.B.partie.argent;
        lancer(L, o, q.slug, 7);
        const encore = L.Collections.donnerSaut(q.slug, 'puces', false, 99, 99);   // par la porte d'à côté
        L.Son.SFX.saut_reussi = vrai;
        return { premier: premier, msg: msg, gain: gain, son: son, journal: journal && journal.t, nom: q.nom,
                 deuxieme: L.B.partie.argent - argent2, encore: encore, n: L.Collections.nombreSauts(),
                 carnet: L.Hud.menuCarnet().items.filter(function (i) { return i.cle === 'sauts'; })[0].detail,
                 bilan: L.Hud.menuBilan().items.filter(function (i) { return i.libelle === 'SAUTS'; })[0].detail };
    }""")
    p = r["premier"]
    assert p and p["px"] >= 40 and p["kmh"] > 0 and p["source"] == "rue", r
    assert r["gain"] == 150 and r["son"] == 1, r
    assert "SAUT 1/20 — " + r["nom"] + " : " + str(p["px"]) + " PX · " in r["msg"], r["msg"]
    assert r["journal"].startswith("SAUT : " + r["nom"]), r["journal"]
    assert r["deuxieme"] == 0 and r["n"] == 1 and r["encore"] is False, "le même saut paie deux fois"
    assert r["carnet"] == "1 / 20" and r["bilan"] == "1 / 20"


def test_trop_court_ou_dans_le_mur_ne_compte_pas(banc):
    r = banc("function (L, o) {" + LANCER + """
        L.Jeu.commencer();
        const q = L.Collections.sauts().filter(function (s) { return !s.rampe; })[1];
        // Trop court : le vol coupé net (le char retombe dès sa deuxième image en l'air).
        const c = lancer(L, o, q.slug, 7, 1, 200, function (v) { v.enLAir = (v.enLAir || 0) + (v.z > 0 ? 1 : 0); if (v.enLAir === 2) { v.z = 0; v.vz = 0; } });
        const court = { n: L.Collections.nombreSauts(), msg: c.dit };
        // Dans le mur : un choc pendant le vol (le compteur de chocs du char bouge).
        const m = lancer(L, o, q.slug, 7, 1, 200, function (v) { v.enLAir = (v.enLAir || 0) + (v.z > 0 ? 1 : 0); if (v.enLAir === 3) v.chocs++; });
        const mur = { n: L.Collections.nombreSauts(), msg: m.dit };
        return { court: court, mur: mur };
    }""")
    assert r["court"]["n"] == 0 and "TROP COURT" in r["court"]["msg"], r
    assert r["mur"]["n"] == 0 and "ATTERRISSAGE RATÉ" in r["mur"]["msg"], r


def test_un_record_se_note_sans_repayer(banc):
    r = banc("function (L, o) {" + LANCER + """
        L.Jeu.commencer();
        const q = L.Collections.sauts().filter(function (s) { return !s.rampe; })[1];
        L.Collections.donnerSaut(q.slug, 'rue', true, 41, 60);
        const argent = L.B.partie.argent;
        const s = lancer(L, o, q.slug, 9);
        return { rec: L.B.partie.collections.sauts[q.slug].px, gain: L.B.partie.argent - argent, msg: s.dit };
    }""")
    assert r["rec"] > 45 and r["gain"] == 0 and "RECORD — " in r["msg"], r


def test_les_paliers_paient(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const tous = L.Collections.sauts();
        tous.slice(0, 9).forEach(function (q) { L.Collections.donnerSaut(q.slug, 'debug', true); });
        let orgue = 0; const vrai = L.Son.SFX.orgue_arena; L.Son.SFX.orgue_arena = function () { orgue++; };
        const a = L.B.partie.argent;
        L.Collections.donnerSaut(tous[9].slug, 'rue', false, 60, 80);
        const dix = L.B.partie.argent - a;
        tous.slice(10, 19).forEach(function (q) { L.Collections.donnerSaut(q.slug, 'debug', true); });
        const b = L.B.partie.argent;
        L.Collections.donnerSaut(tous[19].slug, 'rue', false, 60, 80);
        L.Son.SFX.orgue_arena = vrai;
        return { dix: dix, vingt: L.B.partie.argent - b, orgue: orgue };
    }""")
    assert r["dix"] == 150 + 750 and r["vingt"] == 150 + 2500 and r["orgue"] == 2, r


def test_le_carnet_des_sauts_la_sauvegarde_et_les_triches(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const q = L.Collections.sauts()[0];
        L.Collections.donnerSaut(q.slug, 'rue', true, 77, 91);
        const m = L.Hud.menuCarnetSauts();
        L.Missions.sauvegarderPartie();
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.Sauvegarde.lire(L.Sauvegarde.emplacement()))), L.B.defs);
        const vieille = L.Sauvegarde.completer({ argent: 1 }, L.B.defs);
        const abimee = L.Sauvegarde.completer({ argent: 1, collections: { sauts: [3] } }, L.B.defs);
        const page = L.Hud.menuDebugCollections();
        const ligne = page.items.filter(function (i) { return i.saut; })[0];
        const rendu = ligne.faire(ligne);
        const s = L.Collections.saut(ligne.saut), j = L.B.joueur;
        const tuiles = Math.max(Math.abs(Math.floor(j.x / 16) - s.x), Math.abs(Math.floor(j.y / 16) - s.y));
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const tous = L.B.menu.items.filter(function (i) { return i.libelle === 'TOUS LES SAUTS'; })[0];
        const argent = L.B.partie.argent;
        tous.faire(tous);
        return { lignes: m.items.map(function (i) { return (i.entete || i.libelle) + '|' + (i.detail || ''); }), nom: q.nom,
                 relue: relue.collections.sauts[q.slug], vieille: vieille.collections.sauts, abimee: abimee.collections.sauts, rendu: rendu, tuiles: tuiles,
                 aller: page.items.filter(function (i) { return i.saut; }).length, n: L.Collections.nombreSauts(),
                 gain: L.B.partie.argent - argent };
    }""")
    assert r["nom"] + "|77 PX · 91 KM/H" in r["lignes"], r["lignes"]
    assert sum(1 for x in r["lignes"] if x.startswith("???")) == 19
    assert "???|EN 4 ROUES" in r["lignes"] and "???|" in r["lignes"], r["lignes"]
    assert "LE FAUBOURG|" in r["lignes"] and "LA POINTE|" in r["lignes"], r["lignes"]
    assert r["relue"]["px"] == 77 and r["vieille"] == {} and r["abimee"] == {}
    assert r["aller"] == 19 and r["rendu"] is True and r["tuiles"] <= 10, r
    assert r["n"] == 20 and r["gain"] == 0, "TOUS LES SAUTS paie (ou n'en donne pas tous)"


def test_le_tremplin_se_peint_la_ou_il_fait_decoller(banc):
    """Le dessin et la physique lisent le même tremplin : les rectangles du dessin couvrent ses deux tuiles."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const q = L.Collections.sauts().filter(function (s) { return !s.rampe; })[0];
        const cam = { x: q.x * 16 - 200, y: q.y * 16 - 120 };
        let n = 0; const ctx = { fillRect: function () { n++; }, set fillStyle(v) {}, save: function () {}, restore: function () {},
                                 translate: function () {}, rotate: function () {} };
        L.Collections.dessiner(ctx, cam);
        const ici = n; n = 0;
        L.Collections.dessiner(ctx, { x: cam.x + 4000, y: cam.y + 4000 });
        return { ici: ici, loin: n };
    }""")
    assert r["ici"] >= 12, r


def test_chaque_saut_se_prend(banc):
    """⚠️ Le juge qui compte : chacun des vingt se prend depuis son élan garanti (sept tuiles), droit devant, et vole
    assez pour compter — en auto, en 4 roues pour ceux des Friches ; une rampe de la ville qu'une auto ne prend pas
    (le Grand Saut exige la moto) doit se prendre en moto."""
    r = banc("function (L, o) {" + LANCER + """
        L.Jeu.commencer();
        const min = L.Collections.regleSauts().vol_min_px, out = {};
        for (const q of L.Collections.sauts()) {
            L.B.partie.collections.sauts = {};
            lancer(L, o, q.slug, 7);
            let ok = !!L.B.partie.collections.sauts[q.slug];
            if (!ok && q.rampe) { L.B.partie.collections.sauts = {}; lancer(L, o, q.slug, 7, 1, 200, null, 'moto'); ok = !!L.B.partie.collections.sauts[q.slug]; }
            out[q.slug] = ok;
        }
        return out;
    }""")
    assert all(r.values()) and len(r) == 20, {k: v for k, v in r.items() if not v}
