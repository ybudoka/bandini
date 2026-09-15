"""M10, 2e vague, cote navigateur : le camion ouvre le guichet et la berline
s'y arrete ; la caisse tombe en liasses qu'on ramasse en passant ; le skimmer
se pose, lit la nuit et se vide ; l'assurance paie le char disparu, et
l'assureur enquete a la troisieme reclamation."""

from app import economie, vehicules


def test_le_camion_defonce_le_guichet_et_l_auto_s_y_arrete(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        const j = L.B.joueur;
        const g = L.B.entites.find(function (e) { return e.type === 'decor' && e.decor === 'guichet'; });
        if (!g) return { pasDeGuichet: true };
        // Le joueur regarde de loin : personne ne doit etre dans le souffle.
        j.x = g.x + 200; j.y = g.y + 200; L.Monde.centrerCamera(j.x, j.y);
        function devant(slug) {
            const v = L.Vehicules.creer(slug, g.x, g.y + 6, -Math.PI / 2, { etat: 'stationne' });
            v.vitesse = 4; v.vx = 0; v.vy = -4;
            L.Entites.indexer();
            return v;
        }
        const auto = devant('auto');
        const rAuto = L.Vehicules.decorDevant(auto, auto.x, auto.y);
        const passeAuto = L.Vehicules.heurterDecor(auto, auto.x, auto.y);
        const briseParAuto = !!g.brise;
        L.Entites.retirer(auto);
        const camion = devant('camion');
        const rCamion = L.Vehicules.decorDevant(camion, camion.x, camion.y);
        const passeCamion = L.Vehicules.heurterDecor(camion, camion.x, camion.y);
        const liasses = L.B.entites.filter(function (e) { return e.type === 'ramassage' && e.objet === 'billets'; });
        const total = liasses.reduce(function (s, e) { return s + e.montant; }, 0);
        const crime = L.B.crimes.filter(function (c) { return c.type === 'guichet'; }).length;
        // On passe sur une liasse : elle se ramasse.
        const avant = L.B.partie.argent;
        j.x = liasses[0] ? liasses[0].x : j.x; j.y = liasses[0] ? liasses[0].y : j.y;
        L.Entites.indexer();
        L.Missions.maj();
        const parTerre = L.B.entites.filter(function (e) { return e.type === 'ramassage' && e.objet === 'billets'; });
        const resteTotal = parTerre.reduce(function (s, e) { return s + e.montant; }, 0);
        return { rAuto: rAuto && rAuto.quoi, passeAuto: passeAuto, briseParAuto: briseParAuto,
                 rCamion: rCamion && rCamion.quoi, passeCamion: passeCamion, brise: !!g.brise,
                 liasses: liasses.length, total: total, crime: crime,
                 ramasse: L.B.partie.argent - avant, restent: parTerre.length, resteTotal: resteTotal };
    }""")
    assert not r.get("pasDeGuichet"), "la ville n'a pas de guichet"
    fiche = economie.GUICHET
    assert r["rAuto"] == "arrete" and r["passeAuto"] is False and r["briseParAuto"] is False, r
    assert r["rCamion"] == "casse" and r["passeCamion"] is True and r["brise"] is True, r
    assert r["liasses"] == fiche["liasses"]
    assert fiche["caisse"][0] <= r["total"] <= fiche["caisse"][1], r["total"]
    assert r["crime"] == 1, "defoncer un guichet est un delit"
    # Les liasses tombent serrees : on en ramasse une ou plusieurs d'un pas, et
    # ce qui reste par terre plus ce qu'on a en poche fait toujours la caisse.
    assert r["ramasse"] > 0 and r["restent"] < fiche["liasses"]
    assert r["ramasse"] + r["resteTotal"] == r["total"]


def test_le_skimmer_se_pose_lit_la_nuit_et_se_vide(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        const j = L.B.joueur, p = L.B.partie;
        // Un guichet sans kiosque ni homme-sandwich a portee : ACTION ne doit
        // parler qu'a lui.
        const g = L.B.entites.find(function (e) {
            return e.type === 'decor' && e.decor === 'guichet'
                && !L.Entites.autour(e.x, e.y, 60, function (q) { return q.type === 'ambulant' || q.metier; }).length;
        });
        if (!g) return { pasDeGuichet: true };
        j.x = g.x; j.y = g.y + 14; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        L.Missions.majInvite(j);
        const sansSkimmer = L.B.invite;
        p.objets.skimmer = 2;
        L.Missions.majInvite(j);
        const invitePose = L.B.invite;
        const pose = L.Missions.interagir(j);
        const n1 = p.skimmers.length, reste = p.objets.skimmer;
        L.Missions.majInvite(j);
        const inviteAttend = L.B.invite;
        const deuxieme = L.Missions.interagir(j);        // deja un ici : on attend
        const n2 = p.skimmers.length;
        // La nuit : on force le de pour lire les deux issues.
        const rng = L.B.rng;
        L.B.rng = function () { return 0.9; };            // pas trouve, et un bon rendement
        L.Missions.nuitDesSkimmers();
        L.B.rng = rng;
        const s = p.skimmers[0];
        L.Missions.majInvite(j);
        const inviteVide = L.B.invite;
        const avant = p.argent;
        L.Missions.interagir(j);
        const gagne = p.argent - avant, n3 = p.skimmers.length;
        // Et celui qu'on trouve : il disparait sans rien rendre.
        p.objets.skimmer = 1; L.Missions.interagir(j);
        L.B.rng = function () { return 0.1; };
        const trouves = L.Missions.nuitDesSkimmers();
        L.B.rng = rng;
        return { sansSkimmer: sansSkimmer, invitePose: invitePose, pose: pose, n1: n1, reste: reste, inviteAttend: inviteAttend,
                 deuxieme: deuxieme, n2: n2, pret: s && s.pret, monte: s ? s.monte : 0, inviteVide: inviteVide,
                 gagne: gagne, n3: n3, trouves: trouves, n4: p.skimmers.length };
    }""")
    assert not r.get("pasDeGuichet")
    s = economie.GUICHET["skimmer"]
    assert r["sansSkimmer"] != "POSER UN SKIMMER", "sans skimmer en poche, rien a poser"
    assert r["invitePose"] == "POSER UN SKIMMER"
    assert r["pose"] is True and r["n1"] == 1 and r["reste"] == 1
    assert r["inviteAttend"] == "SKIMMER POSÉ — REVIENS DEMAIN"
    assert r["deuxieme"] is True and r["n2"] == 1, "deux skimmers sur le meme guichet"
    assert r["pret"] is True
    assert s["rendement"][0] <= r["monte"] <= s["rendement"][1]
    assert r["inviteVide"] == "VIDER LE SKIMMER — %d $" % r["monte"]
    assert r["gagne"] == r["monte"] and r["n3"] == 0
    assert r["trouves"] == 1 and r["n4"] == 0, "un skimmer trouve disparait"


def test_l_assurance_paie_le_char_disparu_et_l_assureur_enquete_a_la_troisieme(banc, paquet):
    auto = next(v for v in vehicules.CATALOGUE if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(3);
        const j = L.B.joueur, p = L.B.partie, a = L.B.defs.economie.assurance;
        p.argent = 5000; p.casier = 0;
        const out = { primes: [], valeurs: [], reclames: [] };
        for (let k = 0; k < a.reclamations_max; k++) {
            const v = o.char('auto', 160, 0, 0);
            function menu() {
                L.B.exterieur = { entites: [v], x: v.x, y: v.y };
                const items = L.Missions.menuGarage([]).items;
                L.B.exterieur = null;
                return items.map(function (i) { return i.libelle + ' | ' + (i.detail || '') + ' | ' + !!i.actif; });
            }
            if (k === 0) out.menuAvant = menu();          // le garage le propose, avec sa prime
            const avant = p.argent;
            L.Missions.assurer(v);
            out.primes.push(avant - p.argent); out.valeurs.push(v.assure ? v.assure.valeur : 0);
            if (k === 0) {
                out.menuApres = menu();                   // ... et pas deux fois
                out.deuxFois = L.Missions.assurer(v);
            }
            L.Vehicules.exploser(v);
            out.reclames.push(p.assurance.reclamations);
        }
        out.du = p.assurance.du; out.enquete = p.assurance.enquete; out.casier = p.casier; out.jour = p.jour;
        const v4 = o.char('auto', 200, 0, 0);
        out.refuse = !L.Missions.assurer(v4) && !v4.assure;
        const avant = p.argent;
        L.Missions.encaisserAssurance();
        out.encaisse = p.argent - avant; out.duApres = p.assurance.du;
        // L'enquete se classe quand son jour arrive.
        p.jour = p.assurance.enquete; L.Missions.nouveauJour();
        out.classe = p.assurance.enquete === 0 && p.assurance.reclamations === 0;
        const v5 = o.char('auto', 240, 0, 0);
        out.reprend = L.Missions.assurer(v5);
        return out;
    }""")
    a = economie.ASSURANCE
    prime, valeur = economie.prime_assurance(auto["prix"]), economie.valeur_assuree(auto["prix"])
    assert r["primes"] == [prime] * a["reclamations_max"], r["primes"]
    assert r["valeurs"] == [valeur] * a["reclamations_max"]
    assert r["deuxFois"] is False, "on assure deux fois le meme char"
    nom = auto["nom"].upper()
    assert "ASSURER %s | %d $ / COUVRE %d $ | true" % (nom, prime, valeur) in r["menuAvant"], r["menuAvant"]
    assert "ASSURER %s | DÉJÀ ASSURÉ | false" % nom in r["menuApres"], r["menuApres"]
    assert r["reclames"] == list(range(1, a["reclamations_max"] + 1))
    assert r["du"] == valeur * a["reclamations_max"]
    assert r["enquete"] == r["jour"] + a["enquete_jours"], "la troisieme ouvre l'enquete"
    assert r["casier"] == a["enquete_pages"]
    assert r["refuse"] is True, "on assure encore pendant l'enquete"
    assert r["encaisse"] == r["du"] and r["duApres"] == 0
    assert r["classe"] is True and r["reprend"] is True


def test_le_marche_noir_vend_le_skimmer_et_la_partie_le_garde(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.argent = 1000;
        const menu = L.Missions.menuMarcheNoir();
        const item = menu.items.find(function (i) { return i.libelle === 'SKIMMER'; });
        if (!item) return { pasDItem: true, libelles: menu.items.map(function (i) { return i.libelle; }) };
        item.faire();
        const apres = L.Missions.menuMarcheNoir().items.find(function (i) { return i.libelle === 'SKIMMER'; });
        // Une vieille sauvegarde n'a ni poches ni dossier d'assurance : `completer` les ajoute.
        const vieille = L.Sauvegarde.completer({ argent: 12 }, L.B.defs);
        return { prix: 1000 - p.argent, enPoche: p.objets.skimmer, detail: apres.detail,
                 vieille: { objets: vieille.objets, skimmers: vieille.skimmers, assurance: vieille.assurance } };
    }""")
    assert not r.get("pasDItem"), r
    s = economie.GUICHET["skimmer"]
    assert r["prix"] == s["prix"] and r["enPoche"] == 1
    assert "(1 EN POCHE)" in r["detail"]
    assert r["vieille"] == {"objets": {}, "skimmers": [], "assurance": {"du": 0, "reclamations": 0, "enquete": 0}}
