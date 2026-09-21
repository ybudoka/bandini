"""M10, 2e vague, cote navigateur : le camion ouvre le guichet et la berline
s'y arrete ; la caisse tombe en liasses qu'on ramasse en passant ; le skimmer
se pose, lit la nuit et se vide ; l'assurance paie le char disparu, et
l'assureur enquete a la troisieme reclamation."""

from app import economie, magasins, vehicules


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
        // ⚠️ On regarde le guichet : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(g);
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


def test_le_skimmer_se_pose_sur_une_machine_sans_empecher_d_acheter(banc, paquet):
    """Le skimmer se pose aussi sur une machine distributrice DE LA RUE — mais
    dans son menu, EN PLUS des articles : poser un skimmer n'empeche pas
    d'acheter une canette dans la meme visite, et la machine d'une salle
    d'attente refuse le skimmer."""
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        const j = L.B.joueur, p = L.B.partie;
        const d = L.B.entites.find(function (e) {
            return e.type === 'decor' && e.decor.indexOf('distributrice') === 0
                && !L.Entites.autour(e.x, e.y, 60, function (q) { return q.type === 'ambulant' || q.metier; }).length;
        });
        if (!d) return { pasDeMachine: true };
        j.x = d.x; j.y = d.y + 14; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        // ⚠️ On regarde la machine : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(d);
        const m = L.Missions.distributriceSousLaMain(j);
        if (!m) return { pasDeMachine: true };
        p.objets.skimmer = 2; p.argent = 100;
        const menu = L.Missions.menuDistributrice(m);
        const libelles = menu.items.map(function (i) { return i.libelle; });
        // Les articles d'abord, le skimmer en SURPLUS : on peut encore acheter.
        const pose = menu.items.find(function (i) { return i.libelle === 'POSER UN SKIMMER'; });
        if (!pose) return { pasDePose: true, libelles: libelles };
        const avant = p.argent;
        // On pose le skimmer SANS fermer le menu, puis on achete une canette.
        const poseFait = pose.faire();
        const n1 = p.skimmers.length, reste = p.objets.skimmer;
        const achats = L.Missions.menuDistributrice(m);
        const achetable = achats.items[0].libelle;
        L.B.rng = function () { return 0.99; };                   // la canette tombe
        const servi = achats.items[0].faire();
        const apres = p.argent, n2 = p.skimmers.length;
        // Le menu redecore le skimmer deja pose : on attend, pas de deuxieme pose.
        const revu = L.Missions.menuDistributrice(m).items.map(function (i) { return i.libelle; });
        // La nuit le lit, puis on le vide au menu.
        L.B.rng = function () { return 0.9; };
        L.Missions.nuitDesSkimmers();
        const vide = L.Missions.menuDistributrice(m).items.find(function (i) { return i.libelle.indexOf('VIDER LE SKIMMER') === 0; });
        const avantVide = p.argent;
        if (vide) vide.faire();
        const n3 = p.skimmers.length, gagne = p.argent - avantVide;
        // La machine d'une salle d'attente (pas `rue:`) ne propose pas de skimmer.
        const interieur = { cle: 'piece:3,4', sorte: m.sorte, fiche: L.B.defs.distributrices[m.sorte], x: 0, y: 0 };
        const sansSkimmer = L.Missions.menuDistributrice(interieur).items.map(function (i) { return i.libelle; });
        return { libelles: libelles, poseFait: poseFait, n1: n1, reste: reste, achetable: achetable, servi: servi,
                 apres: apres, n2: n2, revu: revu, vide: vide ? vide.libelle : null, n3: n3, gagne: gagne,
                 sansSkimmer: sansSkimmer };
    }""")
    assert not r.get("pasDeMachine"), "la ville n'a pas de machine loin des kiosques"
    assert not r.get("pasDePose"), r
    s = economie.GUICHET["skimmer"]
    # Les articles d'abord, puis le skimmer : l'ordre n'empeche pas d'acheter.
    assert "POSER UN SKIMMER" in r["libelles"]
    assert r["libelles"].index("POSER UN SKIMMER") > r["libelles"].index(r["achetable"]), r["libelles"]
    assert r["poseFait"] is False and r["n1"] == 1 and r["reste"] == 1, "poser un skimmer ne ferme pas le menu"
    assert r["servi"] is False and r["apres"] < 100 and r["n2"] == 1, "on achete apres avoir pose le skimmer"
    assert "SKIMMER POSÉ — REVIENS DEMAIN" in r["revu"], r["revu"]
    assert r["vide"] is not None, "le skimmer lu la nuit se vide au menu"
    assert r["n3"] == 0, "vider le skimmer le retire"
    monte = int(r["vide"].split("— ")[1].split(" $")[0])
    assert s["rendement"][0] <= monte <= s["rendement"][1]
    assert r["gagne"] == monte
    assert "POSER UN SKIMMER" not in r["sansSkimmer"] and "SKIMMER POSÉ — REVIENS DEMAIN" not in r["sansSkimmer"], \
           "la machine d'une salle d'attente ne se skime pas"
