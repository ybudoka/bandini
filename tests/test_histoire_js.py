"""M6 — l'histoire : donneurs, dialogues dits a voix haute, telephone, missions, defis, GPS.

Le texte vient de `missions.py` ; ici on verifie que le navigateur le JOUE :
qu'un objectif atteint passe au suivant, qu'une arrestation fait rater la
mission, que le donneur suivant appelle, que chaque replique demande sa voix.
"""


def test_les_donneurs_attendent_devant_leur_porte_et_ti_guy_parle(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const t = L.Histoire.donneur('ti_guy');
        const terminus = L.Histoire.lieu('terminus');
        const pres = Math.hypot(t.x - terminus.x, t.y - terminus.y);
        const invite0 = (L.Missions.majInvite(j), L.B.invite);
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        const parle = L.Missions.interagir(j);
        const cinema = L.B.cinema;
        return { pres: pres, invite0: invite0, invite: invite, parle: parle, scene: !!L.B.scene,
                 lignes: cinema ? cinema.lignes.length : 0, qui: cinema ? cinema.lignes[0].qui : null,
                 slug: cinema ? cinema.lignes[0].slug : null, dialogue: L.B.dialogue && L.B.dialogue.qui,
                 demandee: L.Son.Voix.demandees[0], fige: (function () { const x = j.x; o.tape('KeyD', 10); return j.x === x; })(),
                 marco: !!L.Histoire.donneur('marco'), thibodeau: !!L.Histoire.donneur('thibodeau'), bouchard: !!L.Histoire.donneur('bouchard') };
    }""")
    assert 24 <= r["pres"] <= 80, "Ti-Guy attend a cote de la porte du terminus"
    assert r["invite0"] != "PARLER À TI-GUY", "au pas de la porte, ACTION ne saute pas sur Ti-Guy"
    assert r["invite"] == "PARLER À TI-GUY"
    # ⚠️ Depuis la 2e vague des scènes, parler joue la SCENE d'intro : ses répliques
    # se disent en deux temps, sous ses plans (`missions.py`, `scenes.intro`).
    assert r["parle"] is True and r["scene"] is True and 1 <= r["lignes"] <= len(paquet["missions"][0]["dialogue"]["intro"])
    assert r["qui"] == "ti_guy" and r["slug"] == "ti_guy-m1-1" and r["dialogue"] == "Ti-Guy"
    assert r["demandee"] == "ti_guy-m1-1", "la replique demande sa voix"
    assert r["fige"] is True, "pendant qu'on lui parle, le joueur ecoute"
    assert r["marco"] and r["thibodeau"], "les autres donneurs sont chez eux"
    assert r["bouchard"] is False, "le sergent est dedans, au casse-croute"


def test_la_premiere_mission_de_bout_en_bout(banc, paquet):
    m1 = paquet["missions"][0]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const j = L.B.joueur;
        // ⚠️ ON ECOUTE CE QUE LA MISSION PAIE, pas ce que le portefeuille
        // gagne. Le juge mesurait `argent - argent0` et appelait ca « la prime
        // de la mission » : tout ce qui entre dans les poches pendant le trajet
        // y entrait aussi. En route vers le garage, le cousin renverse
        // quelqu'un une fois sur deux et lui fait les poches — cinquante et une
        // piastres, et le juge accusait la recompense. C'est de la que venait
        // une CI a pile ou face, jusqu'a ce que la ville redevienne
        // reproductible et que ce cote-la tombe tout le temps.
        const paiements = [];
        const vraiEncaisser = L.Missions.encaisser;
        L.Missions.encaisser = function (montant, raison) {
            paiements.push({ montant: montant, raison: raison || null });
            return vraiEncaisser.apply(null, arguments);
        };
        const t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        L.Missions.interagir(j);
        // On passe les repliques a ACTION, une a une — et la SCENE, qui continue
        // apres ses mots, a PAUSE (2e vague des scenes).
        let passes = 0;
        const ecouter = function (max) {
            while ((L.B.cinema || L.B.scene) && passes < max) { o.tape(L.B.cinema ? 'KeyE' : 'Escape', 2); passes++; }
        };
        ecouter(10);
        const commencee = L.B.partie.mission && L.B.partie.mission.slug;
        const etape0 = L.B.partie.mission.etape;
        const objectif0 = L.Histoire.ligneObjectif();
        const gps0 = L.Histoire.cible();
        // 1. Au garage.
        const garage = L.Histoire.lieu('garage');
        j.x = garage.x; j.y = garage.y; L.Entites.indexer();
        o.frame(2);
        const etape1 = L.B.partie.mission.etape;
        const v = L.B.mission.vehicule;
        const ruelle = v ? L.Monde.glyphe(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)) : null;
        // 2. Le char de la ruelle.
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v);
        o.frame(2);
        const etape2 = L.B.partie.mission.etape;
        const objectif2 = L.Histoire.ligneObjectif();
        // Au volant, Ti-Guy appelle : la replique PENDANT de l'objectif, au combine
        // (il est au terminus). On l'ecoute.
        const pendant = L.B.cinema ? { partie: L.B.cinema.partie, slug: L.B.cinema.lignes[0].slug,
                                       telephone: L.B.cinema.lignes[0].telephone } : null;
        ecouter(20);
        // 3. Au garage, sans bosse, a l'arret.
        v.x = garage.x; v.y = garage.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
        o.frame(2);
        const finie = !!L.B.partie.missionsFaites.m1;
        // La fin est une SCENE : Ti-Guy sort du garage et marche jusqu'a toi avant
        // de parler. On la laisse jouer jusqu'a sa premiere replique.
        const finJouee = !!L.B.scene;
        let attente = 0;
        while (L.B.scene && !L.B.cinema && attente < 300) { o.frame(1); attente++; }
        const finDite = !!L.B.cinema;
        const voixFin = L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1];
        ecouter(40);
        return { passes: passes, commencee: commencee, etape0: etape0, objectif0: objectif0, gps0: gps0 && gps0.nom,
                 etape1: etape1, ruelle: ruelle, etape2: etape2, objectif2: objectif2, finie: finie, finDite: finDite,
                 finJouee: finJouee, voixFin: voixFin, mission: L.B.partie.mission, pendant: pendant,
                 tiGuy: !!L.Histoire.donneur('ti_guy'),
                 missions: L.B.partie.stats.missions, paiements: paiements };
    }""")
    assert r["commencee"] == "m1" and r["etape0"] == 0
    assert r["objectif0"] == m1["objectifs"][0]["texte"] and r["gps0"] == "Garage Rocco Bandini"
    assert r["etape1"] == 1, "arrive au garage, l'objectif suivant"
    assert r["ruelle"] == "x", "le char de Ti-Guy dort dans une ruelle"
    assert r["etape2"] == 2 and r["objectif2"] == m1["objectifs"][2]["texte"]
    assert r["pendant"] == {"partie": "pendant", "slug": "ti_guy-m1-8", "telephone": True}, \
        "au volant, Ti-Guy appelle : sa replique pendant, au combine"
    assert r["finie"] is True and r["finJouee"] is True and r["finDite"] is True, "la mission finie, Ti-Guy conclut"
    assert r["voixFin"] == "ti_guy-m1-5", "la replique de fin demande sa voix (n continue apres l'intro)"
    # ⚠️ La prime de la MISSION, retrouvee par son libelle : c'est elle qu'on
    # juge, pas la somme de tout ce qui est entre dans les poches en chemin.
    prime = [p for p in r["paiements"] if p["raison"] == m1["titre"].upper()]
    assert len(prime) == 1, "la mission n'a pas paye une fois et une seule : %s" % r["paiements"]
    assert prime[0]["montant"] == m1["recompense"] + m1["recompense"] // 2, (
        "sans bosse : la prime et demie (%s)" % prime[0]
    )
    assert r["mission"] is None and r["missions"] == 1
    # ⚠️ Plus un `if (m.slug === 'm1')` dans `reussir()` : c'est la scène de fin qui
    # fait entrer Ti-Guy au garage, et il quitte la ville avec elle.
    assert r["tiGuy"] is False, "Ti-Guy s'en va une fois le cousin lance"


def test_une_arrestation_fait_rater_la_mission_et_on_peut_recommencer(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Histoire.commencer('m1');
        const enCours = !!L.B.partie.mission;
        L.B.partie.argent = 100;
        L.Missions.prison(null);
        const rate = L.B.partie.mission === null;
        const echecDit = L.B.cinema && L.B.cinema.partie === 'echec';
        const echecs = L.B.partie.stats.echecs;
        L.Histoire.finir();
        o.frame(120);
        const encore = L.Histoire.disponibleDe('ti_guy');
        return { enCours: enCours, rate: rate, echecDit: echecDit, echecs: echecs, encore: encore && encore.slug };
    }""")
    assert r["enCours"] and r["rate"] and r["echecDit"] and r["echecs"] == 1
    assert r["encore"] == "m1", "ratee, la mission se redonne"


def test_le_donneur_suivant_appelle_au_telephone(banc, paquet):
    m2 = paquet["missions"][1]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.missionsFaites.m1 = 1;
        let quand = -1;
        for (let i = 0; i < 900 && quand < 0; i++) { o.frame(1); if (L.B.cinema) quand = i; }
        const c = L.B.cinema;
        const ligne = c ? c.lignes[0] : null;
        const gpsPendant = L.Histoire.cible();
        L.Histoire.finir();
        const gps = L.Histoire.cible();
        const t = L.Histoire.donneur('thibodeau');
        return { quand: quand, partie: c && c.partie, qui: ligne && ligne.qui, telephone: ligne && ligne.telephone,
                 slug: ligne && ligne.slug, dialogueQui: gpsPendant && gpsPendant.nom, gps: gps && gps.nom,
                 versThibodeau: gps && t && Math.hypot(gps.x - t.x, gps.y - t.y) < 4, appels: L.B.partie.appels };
    }""")
    assert 0 <= r["quand"] < 900, "Madame Thibodeau appelle quelques secondes apres M1"
    assert r["partie"] == "appel" and r["qui"] == "thibodeau" and r["telephone"] is True
    assert r["slug"] == "thibodeau-m2-1"
    assert r["gps"] == "Madame Thibodeau" and r["versThibodeau"], "le GPS pointe vers celle qui a appele"
    assert r["appels"] == {"m2": True}
    assert m2["dialogue"]["appel"][0]["qui"] == "thibodeau"


def test_les_cravates_de_madame_thibodeau_et_le_fuyard(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(6);
        const j = L.B.joueur;
        L.B.partie.missionsFaites.m1 = 1;
        const t = L.Histoire.donneur('thibodeau');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        L.Histoire.commencer('m2');
        const cibles = L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible; });
        const pres = cibles.every(function (e) { return Math.hypot(e.x - t.x, e.y - t.y) < 160; });
        const ligne0 = L.Histoire.ligneObjectif();
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        o.frame(2);
        const etape1 = L.B.partie.mission.etape;
        // Le fuyard file : Mme Thibodeau crie (sa replique PENDANT), et a pied ca fige
        // la rue le temps de l'entendre. Elle est a deux pas : pas au combine.
        const pendant = L.B.cinema ? { partie: L.B.cinema.partie, telephone: L.B.cinema.lignes[0].telephone } : null;
        while (L.B.cinema) L.Histoire.suivante();
        const moto = L.B.mission.fuyard;
        const fuit = moto && moto.fuite && moto.conducteur === 'trafic' && moto.slug === 'moto';
        let dMax = 0;
        for (let i = 0; i < 120; i++) { o.frame(1); if (moto) dMax = Math.max(dMax, Math.hypot(moto.x - j.x, moto.y - j.y)); }
        // On le rattrape : la moto casse.
        L.Vehicules.endommager(moto, 999, j);
        o.frame(2);
        const porteur = L.B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        const tombe = L.B.mission.fuyardTombe;
        L.Entites.assommer(porteur);
        o.frame(2);
        const caisse = L.B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        j.x = caisse.x; j.y = caisse.y; L.Entites.indexer();
        o.frame(2);
        const etape2 = L.B.partie.mission.etape;
        j.x = t.x - 14; j.y = t.y; L.Entites.indexer();
        o.frame(2);
        const finie = !!L.B.partie.missionsFaites.m2;
        return { n: cibles.length, pres: pres, ligne0: ligne0, etape1: etape1, pendant: pendant, fuit: fuit, dMax: dMax, tombe: tombe,
                 porteur: !!porteur, caisse: !!caisse, etape2: etape2, finie: finie,
                 batte: !!L.B.partie.armes.batte, rabais: L.B.partie.rabais };
    }""")
    assert r["n"] == 2 and r["pres"], "deux Cravates rodent pres du kiosque"
    assert r["ligne0"].endswith(" 0/2")
    assert r["etape1"] == 1, "les deux K.-O., le fuyard file"
    assert r["pendant"] == {"partie": "pendant", "telephone": False}, "elle crie apres le fuyard, a deux pas de toi"
    assert r["fuit"] is True and r["dMax"] > 60, "la moto s'eloigne sur les rails"
    assert r["tombe"] and r["porteur"] and r["caisse"], "la moto cassee, le Cravate tombe, la caisse aussi"
    assert r["etape2"] == 2 and r["finie"] is True
    assert r["batte"] is True and r["rabais"] == {"kiosque": 0.75}, "le baton, et le kiosque moins cher"


def test_le_sergent_ami_et_le_faubourg_libere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        ['m1', 'm2', 'm3'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        L.Histoire.commencer('m4');
        const nuit = L.Monde.estNuit();
        o.frame(2);
        const attend = L.Histoire.ligneObjectif();
        L.B.partie.mission.etape = 3;                       // on saute a la livraison, deja faite ailleurs
        L.B.mission.vehicule = null;
        L.Histoire.reussir();
        const ami = L.B.partie.sergentAmi;
        L.Histoire.finir();
        L.Histoire.commencer('m5');
        L.B.partie.mission.etape = 3;
        L.Histoire.reussir();
        L.Histoire.finir();
        return { nuit: nuit, attend: attend, ami: ami, libere: L.B.partie.faubourgLibere, bar: !!L.B.partie.proprietes.bar,
                 manchette: L.B.partie.manchetteForcee, faites: Object.keys(L.B.partie.missionsFaites).sort() };
    }""")
    assert r["nuit"] is False and r["attend"] == "ATTENDS LA NUIT", "M4 commence de jour : on attend la nuit"
    assert r["ami"] is True and r["libere"] is True and r["bar"] is True
    assert r["manchette"] == "cravates_chassees", "la une de demain, par son slug (journal.SPECIALES)"
    assert r["faites"] == ["m1", "m2", "m3", "m4", "m5"]


def test_les_defis_ont_un_panneau_et_un_chrono(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const panneaux = L.B.entites.filter(function (e) { return e.type === 'panneau'; }).map(function (e) { return e.defi; }).sort();
        const p = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'tour'; });
        j.x = p.x; j.y = p.y + 8; L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.Missions.interagir(j);
        const menu = L.B.menu && L.B.menu.titre;
        L.B.menu.items[0].faire(); L.Hud.fermerMenu();
        const defi = L.B.defi && L.B.defi.slug;
        const ligne = L.Histoire.ligneObjectif();
        const gps = L.Histoire.cible();
        // ⚠️ Sans char, le defi rate A L'INSTANT — pas au bout du chrono. Le
        // juge laissait filer les deux minutes et lisait le DERNIER message du
        // HUD : le jour ou un facteur en colere a trouve le joueur plante la,
        // c'est la facture de l'hopital qu'il a lue. On lit le verdict tout
        // de suite, et on ne mesure que lui.
        o.frame(30);
        return { panneaux: panneaux, invite: invite, menu: menu, defi: defi, ligne: ligne, gps: gps && gps.nom,
                 apres: L.B.defi, msg: L.B.msg };
    }""")
    assert r["panneaux"] == ["livraison", "saut", "tour"]
    assert r["invite"] == "DÉFI" and r["menu"] == "TOUR DU FAUBOURG"
    assert r["defi"] == "tour" and r["ligne"].startswith("TOUR DU FAUBOURG 2:00 TOUR 1/3")
    assert r["gps"] == "Terminus Baie-des-Brumes" or r["gps"]
    assert r["apres"] is None and "RATÉ" in r["msg"], "sans char, le tour rate"


def test_le_narrateur_lit_la_manchette_et_josee_ouvre_le_marche_noir(banc, paquet):
    mn = paquet["marche_noir"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.stats.tues = 2;
        L.Missions.nouveauJour();
        const lue = L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1];
        const titre = L.B.dialogue && L.B.dialogue.lignes[0];
        // La manchette de M5, imposee : par son slug, et lue elle aussi.
        L.B.partie.manchetteForcee = 'cravates_chassees';
        L.Missions.nouveauJour();
        const forcee = L.B.dialogue && L.B.dialogue.lignes[0];
        const forceeLue = L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1];
        // Josee, avant et apres M5.
        const avant = L.Histoire.parler('josee');
        const menuAvant = L.B.menu && L.B.menu.titre;
        L.B.dialogue = null;
        ['m1', 'm2', 'm3', 'm4', 'm5'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        L.B.partie.argent = 1000;
        L.Histoire.parler('josee');
        const menu = L.B.menu;
        const pistolet = menu.items.find(function (i) { return i.libelle === 'PISTOLET'; });
        pistolet.faire(pistolet);
        return { lue: lue, titre: titre, forcee: forcee, forceeLue: forceeLue, avant: avant, menuAvant: menuAvant,
                 menu: menu.titre, prix: pistolet.detail, argent: L.B.partie.argent, arme: !!L.B.partie.armes.pistolet };
    }""")
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    prix = round(pistolet["prix"] * mn["rabais"])
    assert r["titre"] == "UN MORT DANS LA RUE" and r["lue"] == "narrateur-journal-un_mort"
    assert r["forcee"] == "LES CRAVATES CHASSEES DU FAUBOURG" and r["forceeLue"] == "narrateur-journal-cravates_chassees"
    assert r["avant"] is True and r["menuAvant"] is None, "avant M5, Josee ne vend rien"
    assert r["menu"] == "MARCHÉ NOIR" and r["prix"] == f"{prix} $"
    assert r["argent"] == 1000 - prix and r["arme"] is True


def test_la_carte_de_la_ville_s_ouvre_et_se_ferme(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.tape('KeyN', 2);
        const ouverte = L.B.etat;
        L.Jeu.rendre();                                   // (rendre remet les compteurs a zero au debut)
        const dessine = L.B.stats.rects;
        const t0 = L.B.t;
        o.frame(10);
        const fige = L.B.t === t0;
        o.tape('KeyN', 2);
        const fermee = L.B.etat;
        L.Jeu.pause();
        const item = L.B.menu.items.find(function (i) { return i.libelle === 'CARTE DE LA VILLE'; });
        item.faire(item);
        const parLeMenu = L.B.etat;
        o.tape('Escape', 2);
        return { ouverte: ouverte, dessine: dessine, fige: fige, fermee: fermee, parLeMenu: parLeMenu, fin: L.B.etat };
    }""")
    assert r["ouverte"] == "carte" and r["dessine"] > 10, "N ouvre la carte, qui se dessine"
    assert r["fige"] is True, "la carte ouverte, le temps s'arrete"
    assert r["fermee"] == "jeu" and r["parLeMenu"] == "carte" and r["fin"] == "jeu"


def test_le_sergent_et_josee_se_voient_dans_leur_piece(banc):
    """⚠️ LE juge du retour de Martin : « je vais à la cantine, mais je ne vois
    pas quoi faire ». Bouchard et Josee sont les deux seuls donneurs qui se
    tiennent DEDANS (`ou: point:...`), et `creerDonneurs` ne posait que ceux de
    la rue : on poussait la porte du casse-croute et la salle etait vide — le
    sergent n'etait qu'un point invisible au fond a droite. Ici on entre, et il
    faut trouver quelqu'un, a portee de son point, qui parle quand on l'aborde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        function visite(lieu, type, slug) {
            const porte = c.portes.find(function (p) { return p.lieu === lieu; });
            o.entrer(porte);
            const piece = L.B.interieur;
            const point = piece.points.find(function (p) { return p.type === type; });
            const e = L.Histoire.donneur(slug);
            const dit = { la: !!e, sur_meuble: e ? L.Monde.estMeuble(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)) : null,
                          du_point: e ? Math.hypot(e.x / L.TT - 0.5 - point.x, e.y / L.TT - 0.5 - point.y) : null,
                          gens: L.B.entites.filter(function (q) { return q.type === 'pieton'; }).length };
            if (e) {
                j.x = e.x - 14; j.y = e.y; L.Entites.indexer();
                L.Missions.majInvite(j);
                dit.invite = L.B.invite;
                dit.parle = L.Missions.utiliserPoint(j);
                dit.qui = L.B.cinema ? L.B.cinema.lignes[0].qui : (L.B.dialogue ? L.B.dialogue.qui : null);
                L.Scenes.passer();                     // l'intro de Josee est une scene (2e vague)
                L.B.cinema = null; L.B.dialogue = null;
            }
            o.sortir();
            dit.dehors = !!L.Histoire.donneur(slug);
            return dit;
        }
        const sergent = visite('casse_croute', 'sergent', 'bouchard');
        ['m1', 'm2', 'm3', 'm4'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        const josee = visite('bar', 'contact', 'josee');
        return { sergent: sergent, josee: josee };
    }""")
    for qui, personne in (("bouchard", r["sergent"]), ("josee", r["josee"])):
        assert personne["la"] is True, f"{qui} : on entre chez lui et la piece est vide"
        assert personne["sur_meuble"] is False, f"{qui} se tient debout sur un meuble"
        assert personne["du_point"] <= 1.5, f"{qui} : loin de son point, l'ancien comptoir ne sert plus de filet"
        assert personne["gens"] >= 3, "le commis et les clients de la piece sont encore la"
        assert personne["dehors"] is False, "il est reste dans sa piece, il n'a pas suivi dans la rue"
    assert r["sergent"]["invite"] == "PARLER À SERGENT BOUCHARD", "le HUD nomme celui qu'on voit"
    assert r["sergent"]["qui"] == "Sergent Bouchard", \
        "sans M3 il n'a pas de job, mais il repond : c'est la boite de dialogue qui le nomme"
    assert r["josee"]["invite"] == "PARLER À JOSÉE"
    assert r["josee"]["qui"] == "josee", "M4 faite : Josee donne M5"


def test_le_donneur_qui_a_une_job_pour_toi_t_interpelle(banc, paquet):
    """⚠️ Une bulle qui ne s'eteint jamais ne veut plus rien dire : elle doit
    dire « celui-la attend apres toi », et personne d'autre."""
    heler = {p["slug"]: p["heler"] for p in paquet["personnages"]}
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        function bulleDe(slug) { const e = L.Histoire.donneur(slug); return e && e.bulle ? e.bulle.texte : null; }
        o.frame(2);
        const debut = { tiguy: bulleDe('ti_guy'), marco: bulleDe('marco') };
        // Ti-Guy donne M1 : sa bulle s'eteint pendant, et pour de bon apres.
        const t = L.Histoire.donneur('ti_guy');
        L.Histoire.commencer('m1');
        o.frame(2);
        const pendant = bulleDe('ti_guy');
        L.B.partie.mission.etape = 2; L.B.mission.vehicule = null;
        L.Histoire.reussir(); L.Scenes.passer(); L.Histoire.finir();
        o.frame(2);
        const apres = bulleDe('ti_guy');
        // M1 faite : c'est Mme Thibodeau (M2) qui attend, maintenant.
        const thibodeau = bulleDe('thibodeau');
        // Et le sergent, dans sa piece, une fois M3 faite.
        ['m2', 'm3'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'casse_croute'; });
        o.entrer(porte);
        o.frame(2);
        const sergent = bulleDe('bouchard');
        const b = L.Histoire.donneur('bouchard').bulle;
        // Elle vit : elle ne repart pas a zero a chaque image, et elle se dessine.
        const t0 = b.t; o.frame(10); const bouge = L.Histoire.donneur('bouchard').bulle.t > t0;
        const rects = L.B.stats.rects;
        L.Entites.dessinerBulle(o.ctx, L.Histoire.donneur('bouchard'), 0, 0);
        return { debut: debut, pendant: pendant, apres: apres, thibodeau: thibodeau,
                 sergent: sergent, bouge: bouge, dessine: L.B.stats.rects > rects };
    }""")
    assert r["debut"]["tiguy"] == heler["ti_guy"], "Ti-Guy a M1 pour toi : il t'interpelle"
    assert r["debut"]["marco"] is None, "Marco n'a rien pour toi avant M2 : il se tait"
    assert r["pendant"] is None, "pendant sa propre mission, le donneur n'appelle plus"
    assert r["apres"] is None, "M1 faite, Ti-Guy n'a plus rien a dire"
    assert r["thibodeau"] == heler["thibodeau"], "M1 faite : c'est Mme Thibodeau qui attend"
    assert r["sergent"] == heler["bouchard"], "M3 faite : le sergent t'attend dans sa piece"
    assert r["bouge"] is True, "une bulle reposee chaque image resterait figee a sa premiere image"
    assert r["dessine"] is True, "la bulle ne pose aucun pixel"


def test_la_premiere_bagarre_se_gagne_aux_poings(banc, paquet):
    """M2 est la PREMIERE bagarre du jeu, et elle doit se gagner aux poings.

    ⚠️ **Rouge avant le correctif, deux fois** : les deux Cravates sortaient de
    l'archetype avec le BATON (18 de degats, `renverse`) et 90 PV, contre 100 PV
    et des poings a 8 — et le joueur qui les laisse cogner tombait en **2,8 s**,
    la ou ce juge en demande plus de quatre. Le dialogue promet pourtant le
    contraire (« Avec tes poings, pas plus »), et le baton est la RECOMPENSE de
    cette mission-ci : on le rencontrait avant de l'avoir.

    ⚠️ **La moitie « il gagne » est un garde-fou, pas une mesure** — elle etait
    VERTE avant, et il faut le dire : un banc qui cogne toutes les dix images
    sans jamais rater ni tourner le dos chancelle ses deux hommes en continu
    (`recul`), et gagnait deja. Ce que le banc ne sait pas jouer, c'est le
    joueur qui se deplace, qui en a un dans le dos, qui rate — celui-la
    encaissait 18 par coup. Cette moitie tient l'autre bord : deux hommes
    qu'on peut ignorer ne seraient plus une bagarre.
    """
    r = banc("""function (L, o) {
        function bagarre(riposte) {
            L.Jeu.commencer();
            L.graine(6);
            const j = L.B.joueur;
            L.B.partie.missionsFaites.m1 = 1;
            const t = L.Histoire.donneur('thibodeau');
            j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
            L.Histoire.commencer('m2');
            L.B.cinema = null; L.B.dialogue = null;      // on a raccroche : la bagarre commence
            const cibles = L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible; });
            const fiches = cibles.map(function (e) { return { vie: e.vie, arme: e.arme }; });
            let i = 0, mort = false, creux = j.vie;
            for (; i < 1800; i++) {
                const debout = cibles.filter(function (e) { return e.vivant && e.etat !== 'assomme'; });
                if (!debout.length) break;
                if (j.vie <= 0 || L.B.transition) { mort = true; break; }   // l'hopital l'a repris
                creux = Math.min(creux, j.vie);
                // ⚠️ UN COUP SUR DIX IMAGES, pas un par image : le juge doit
                // mesurer une bagarre jouable, pas un joueur parfait. C'est
                // justement le jeu parfait qu'on ne veut plus exiger.
                if (riposte && i % 10 === 0) {
                    let c = debout[0], d = 1e9;
                    debout.forEach(function (e) { const q = Math.hypot(e.x - j.x, e.y - j.y); if (q < d) { d = q; c = e; } });
                    j.angle = Math.atan2(c.y - j.y, c.x - j.x);
                    L.Combat.frapper(j);
                }
                o.frame(1);
            }
            return { fiches: fiches, s: i / 60, mort: mort, restant: mort ? 0 : creux };
        }
        const bat = bagarre(true), subit = bagarre(false);
        // L'archetype, lui, n'a pas bouge : une Cravate de rue garde son baton.
        const arch = L.Entites.archetype('cravate');
        return { fiches: bat.fiches, gagne: bat, subit: subit,
                 arch: { vie: arch.vie, arme: arch.arme } };
    }""")
    objectif = paquet["missions"][1]["objectifs"][0]
    assert objectif["arme"] == "" and objectif["vie"] == 55, "la fiche des deux hommes vit dans missions.py"
    assert r["fiches"] == [{"vie": 55, "arme": None}] * 2, "ils arrivent les mains vides, avec la vie de la fiche"
    assert r["gagne"]["mort"] is False, "un joueur qui riposte gagne la premiere bagarre"
    assert r["gagne"]["s"] < 5, f"{r['gagne']['s']:.1f} s : la bagarre doit se conclure"
    assert r["gagne"]["restant"] >= 20, f"il reste {r['gagne']['restant']} PV : trop juste pour une premiere"
    assert r["subit"]["mort"] is True, "mais deux hommes qu'on laisse cogner ont encore raison de toi"
    assert r["subit"]["s"] > 4, f"{r['subit']['s']:.1f} s a encaisser : moins, et on n'a pas le temps de reagir"
    assert r["arch"] == {"vie": 90, "arme": "batte"}, "la Cravate de rue, elle, garde son baton (M5, la dette)"


def test_ceux_qu_on_a_couches_restent_couches_quand_la_mission_rate(banc):
    """Retour de Martin : « quand on meurt ou est arrete lors d'une mission, ceux
    qu'on a tues sont resettes ». Ratee a l'hopital ou en prison, la mission se
    retente — mais les Cravates deja couches ne se relevent pas pour autant, et
    un coin qu'on a vide reste vide."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        ['m1', 'm2', 'm3', 'm4'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        L.B.partie.argent = 5000;
        const dehors = { x: j.x, y: j.y };
        function debout() {
            return L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.vivant; });
        }
        function prendre() {
            L.Histoire.commencer('m5');
            L.B.cinema = null; L.B.dialogue = null;
            j.invincible = 1e6;                        // on mesure la reprise, pas la bagarre
            o.frame(2);
        }
        function reprendre() {
            L.Histoire.finir();                        // la replique d'echec
            o.frame(200);                              // le fondu : lit d'hopital ou poste
            if (L.B.interieur) L.Jeu.quitterLaPiece();
            j.x = dehors.x; j.y = dehors.y; L.Entites.dansLaCarte(j); L.Entites.indexer();
            prendre();
        }
        prendre();
        const six = debout();
        const survivants = six.slice(4).map(function (e) { return { x: e.x, y: e.y }; });
        six.slice(0, 4).forEach(function (e) { L.Entites.tuer(e); });
        o.frame(2);
        const lue = L.Histoire.ligneObjectif();
        L.Missions.hopital();
        const rateeMort = L.B.partie.mission === null;
        reprendre();
        const relue = L.Histoire.ligneObjectif();
        const reposes = debout();
        const dansLeurCoin = reposes.every(function (e) {
            return survivants.some(function (s) { return Math.hypot(e.x - s.x, e.y - s.y) < 100; });
        });
        reposes.forEach(function (e) { L.Entites.tuer(e); });
        o.frame(30);
        const chef = L.B.mission.entites.find(function (e) { return e.chef; });
        const etapeDuChef = L.B.partie.mission.etape;
        const chefDebout = !!chef && chef.vivant;
        L.Missions.prison(null);
        const rateePrison = L.B.partie.mission === null;
        reprendre();
        const etapeReprise = L.B.partie.mission.etape;
        const deboutReprise = debout().map(function (e) { return !!e.chef; });
        // ⚠️ Le chef debout, Josee appelle (sa replique PENDANT) : a pied, ca fige la
        // rue comme tout dialogue. On raccroche.
        L.B.cinema = null; L.B.dialogue = null;
        debout().forEach(function (e) { L.Entites.tuer(e); });
        o.frame(2);
        const etapeApres = L.B.partie.mission.etape;
        L.Histoire.reussir();
        L.Histoire.finir();
        return { n: six.length, lue: lue, rateeMort: rateeMort, relue: relue, reposes: reposes.length,
                 dansLeurCoin: dansLeurCoin, etapeDuChef: etapeDuChef, chefDebout: chefDebout,
                 rateePrison: rateePrison, etapeReprise: etapeReprise, deboutReprise: deboutReprise,
                 etapeApres: etapeApres, oubliees: !(L.B.partie.tombes || {}).m5 };
    }""")
    assert r["n"] == 6 and r["lue"].endswith(" 4/6")
    assert r["rateeMort"] is True, "a l'hopital, la mission rate"
    assert r["relue"].endswith(" 4/6"), f"la reprise repart de {r['relue']!r} : les morts se sont releves"
    assert r["reposes"] == 2, f"{r['reposes']} Cravates reposes : seuls les deux survivants reviennent"
    assert r["dansLeurCoin"] is True, "un coin qu'on a vide reste vide"
    assert r["etapeDuChef"] == 1 and r["chefDebout"] is True, (
        "les six au sol, le chef sort — et les corps du premier objectif ne le couchent pas a sa place")
    assert r["rateePrison"] is True, "en prison, la mission rate aussi"
    assert r["etapeReprise"] == 1 and r["deboutReprise"] == [True], (
        "les trois coins sont vides : la reprise va droit au chef, seul debout")
    assert r["etapeApres"] == 2, "le chef couche, on seme la police"
    assert r["oubliees"] is True, "la mission reussie, il n'y a plus d'essai a retenir"
