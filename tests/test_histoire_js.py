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


def test_le_dialogue_de_l_appel_attend_la_fin_de_la_sonnerie(banc):
    """Demande de Martin (17 sept. 2026) : « quand on reçoit des appels, le
    dialogue commence après la fin de la sonnerie ».

    ⚠️ Au banc, aucun mp3 n'est decode : la sonnerie est celle de la SYNTHESE
    (0,37 s, soit 22 images). C'est l'ecart qu'on mesure — pas les deux
    secondes du fichier, qui ne sont pas la."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.missionsFaites.m1 = 1;
        let sonne = -1, parle = -1, ensemble = false;
        for (let i = 0; i < 900 && parle < 0; i++) {
          o.frame(1);
          if (L.B.sonnerie && sonne < 0) sonne = i;
          if (L.B.sonnerie && L.B.cinema) ensemble = true;   // on parle pendant que ca sonne
          if (L.B.cinema) parle = i;
        }
        const c = L.B.cinema;
        return { sonne: sonne, parle: parle, ensemble: ensemble,
                 duree: L.Son.SFX.telephone(), sonnerie: L.B.sonnerie,
                 partie: c && c.partie, qui: c && c.lignes[0].qui, appels: L.B.partie.appels };
    }""")
    duree = r.get("duree") or 0
    assert duree > 0, "la sonnerie ne dit pas ce qu'elle dure : personne ne peut l'attendre"
    assert 0 <= r["sonne"] < r["parle"], "le telephone sonne, PUIS le donneur parle"
    images = round(duree * 60)                      # 60 images font une seconde
    assert r["parle"] - r["sonne"] == images, "le dialogue part a la fin de la sonnerie, ni avant ni plus tard"
    assert r["ensemble"] is False, "la voix du donneur passait par-dessus le combine"
    assert r["sonnerie"] is None, "la sonnerie se raccroche quand le dialogue part"
    assert r["partie"] == "appel" and r["qui"] == "thibodeau"
    assert r["appels"] == {"m2": True}, "l'appel n'est marque qu'au decrochage"


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


def test_le_tour_du_proprietaire_pointe_chaque_contact(banc, paquet):
    """⚠️ m6, « Le tour du propriétaire » : quatre objectifs `parler` à quatre
    personnes. `Histoire.cible()` n'avait AUCUN cas `parler` — ni flèche à
    l'écran, ni losange sur la mini-carte, ni « OÙ » dans le carnet : on
    cherchait Ti-Paul, Lulu, Raymonde et Ovila à l'aveugle. Le GPS doit pointer
    la PERSONNE quand elle est dehors (Ti-Paul au dépanneur, Raymonde à
    l'usine), et sa PORTE quand elle est dedans (Lulu à la cantine, Ovila au
    phare)."""
    m6 = next(m for m in paquet["missions"] if m["slug"] == "m6")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        ['m1', 'm2', 'm3', 'm4', 'm5'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        L.Histoire.commencer('m6');
        function vue(etape) {
            L.B.partie.mission.etape = etape;
            const g = L.Histoire.cible();
            const perso = L.B.defs.personnages.find(function (q) { return q.slug === L.Histoire.cibleDuParler(L.Histoire.courante().objectifs[etape]); });
            return { nom: g && g.nom, x: g && g.x, y: g && g.y,
                     surLePersonnage: g && perso ? (function () {
                        const e = L.Histoire.donneur(perso.slug);
                        return e && Math.hypot(g.x - e.x, g.y - e.y) < 4;
                     })() : null,
                     surLaPorte: g && perso ? (function () {
                        const l = L.Histoire.lieuDuPersonnage(perso.slug);
                        return l && Math.hypot(g.x - l.x, g.y - l.y) < 4;
                     })() : null };
        }
        return { tiPaul: vue(0), lulu: vue(1), raymonde: vue(2), ovila: vue(3) };
    }""")
    # Les quatre objectifs sont bien des `parler`, dans cet ordre.
    assert [o["cible"] for o in m6["objectifs"]] == ["tipaul", "lulu", "raymonde", "ovila"]
    assert r["tiPaul"]["nom"] == "Ti-Paul Gagnon", "le GPS nomme Ti-Paul, pas un lieu"
    assert r["tiPaul"]["surLePersonnage"] is True, "Ti-Paul est dehors : on pointe SA personne"
    assert r["lulu"]["nom"] == "Lucienne « Lulu » Pelletier", "le GPS nomme Lulu"
    assert r["lulu"]["surLaPorte"] is True, "Lulu est dedans : on pointe sa porte (la cantine)"
    assert r["raymonde"]["nom"] == "Raymonde Fortin", "le GPS nomme Raymonde"
    assert r["raymonde"]["surLePersonnage"] is True, "Raymonde est dehors : on pointe SA personne"
    assert r["ovila"]["nom"] == "Ovila Saint-Onge", "le GPS nomme Ovila"
    assert r["ovila"]["surLaPorte"] is True, "Ovila est dedans : on pointe sa porte (le phare)"


def test_les_defis_ont_un_panneau_et_un_chrono(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const panneaux = L.B.entites.filter(function (e) { return e.type === 'panneau'; }).map(function (e) { return e.defi; }).sort();
        const p = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'tour'; });
        j.x = p.x; j.y = p.y + 8; L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        o.tape('KeyE', 2);                                // le panneau, au bouton
        const menu = L.B.menu && L.B.menu.titre;
        o.tape('KeyE', 2);                                // COMMENCER
        const defi = L.B.defi && L.B.defi.slug;
        const ligne = L.Histoire.ligneObjectif();
        const gps = L.Histoire.cible();
        // ⚠️ A PIED, LE DEFI ATTEND SON CHAR. Il ratait a l'image suivante
        // (« SANS CHAR, PAS DE TOUR ») — et comme le panneau ne se lit qu'a
        // pied, le tour ne s'etait jamais gagne.
        o.frame(300);
        const attend = { defi: L.B.defi && L.B.defi.slug, ligne: L.Histoire.ligneObjectif() };
        // ⚠️ Le verdict se lit A L'IMAGE OU IL TOMBE. Le juge laissait filer le
        // temps et lisait le DERNIER message du HUD : le jour ou un facteur en
        // colere a trouve le joueur plante la, c'est la facture de l'hopital
        // qu'il a lue.
        let n = 300;
        while (L.B.defi && n < 1200) { o.frame(1); n++; }
        return { panneaux: panneaux, invite: invite, menu: menu, defi: defi, ligne: ligne, gps: gps && gps.nom,
                 attend: attend, rateA: n, apres: L.B.defi, msg: L.B.msg };
    }""")
    assert r["panneaux"] == ["livraison", "saut", "tour"]
    assert r["invite"] == "DÉFI" and r["menu"] == "TOUR DU FAUBOURG"
    assert r["defi"] == "tour" and r["ligne"] == "TOUR DU FAUBOURG 2:00 — MONTE DANS UN CHAR"
    assert r["gps"] == "Terminus Baie-des-Brumes" or r["gps"]
    assert r["attend"] == {"defi": "tour", "ligne": "TOUR DU FAUBOURG 2:00 — MONTE DANS UN CHAR"}, (
        "a pied, le defi attend son char et le chrono ne court pas : %s" % r["attend"])
    assert r["apres"] is None and r["msg"] == "DÉFI RATÉ — IL FAUT UN CHAR"
    assert 590 <= r["rateA"] <= 610, f"{r['rateA']} images : dix secondes pour monter, pas plus"


def test_la_livraison_se_commence_a_pied_et_part_au_volant(banc, paquet):
    """⚠️ Rouge avant (17 sept. 2026) : « DÉFI RATÉ — SANS CHAR, PAS DE
    LIVRAISON » a l'image qui suivait COMMENCER. Le panneau ne se lit qu'a pied
    (au volant, ACTION fait descendre) : ni le tour ni la livraison ne s'etaient
    jamais gagnes. Tout au bouton, sauf le trajet jusqu'au bar."""
    liv = next(d for d in paquet["defis"] if d["slug"] == "livraison")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde, TT = L.TT;
        function roule(tx, ty) { return !M.bloque(tx, ty, M.MASQUE_VEHICULE) && !M.estEau(tx, ty); }
        function pres(p) {
            const tx = Math.floor(p.x / TT), ty = Math.floor(p.y / TT);
            for (let r = 0; r <= 4; r++) for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
                if (Math.max(Math.abs(dx), Math.abs(dy)) === r && roule(tx + dx, ty + dy)) return { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
            }
            return null;
        }
        const p = B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'livraison'; });
        j.x = p.x; j.y = p.y + 8; L.Entites.indexer();
        const place = pres({ x: p.x, y: p.y + 40 });
        const v = L.Vehicules.creer('auto', place.x, place.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        o.tape('KeyE', 2);                                // le panneau
        o.tape('KeyE', 2);                                // COMMENCER
        const commence = B.defi && B.defi.slug;
        const aPied = { t: B.defi && B.defi.t, etoiles: B.recherche.etoiles };
        o.frame(60);                                      // on marche jusqu'au char
        const unPeuPlusTard = { t: B.defi && B.defi.t, etoiles: B.recherche.etoiles };
        const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
        for (const c of cotes) {
            j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer();
            if (L.Vehicules.vehiculeSousLaMain(j) === v) break;
        }
        o.tape('KeyE', 2);                                // on monte
        const auVolant = { dedans: j.dansVehicule === v, etoiles: B.recherche.etoiles, ligne: L.Histoire.ligneObjectif() };
        const bar = pres(L.Histoire.lieu('bar'));
        v.x = bar.x; v.y = bar.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
        L.Entites.indexer();
        let n = 0;
        while (B.defi && n < 30) { o.frame(1); n++; }
        return { commence: commence, aPied: aPied, unPeuPlusTard: unPeuPlusTard, auVolant: auVolant,
                 reussi: !!B.partie.defisFaits.livraison, msg: B.msg, encore: B.defi && B.defi.slug };
    }""")
    assert r["commence"] == "livraison"
    assert r["aPied"] == {"t": 0, "etoiles": 0} and r["unPeuPlusTard"] == {"t": 0, "etoiles": 0}, (
        "a pied, ni chrono ni police : on marche jusqu'a son char (%s)" % r["unPeuPlusTard"])
    assert r["auVolant"]["dedans"] is True
    assert r["auVolant"]["etoiles"] >= liv["etoiles"], "au volant, la police aux fesses"
    assert r["auVolant"]["ligne"].startswith("LIVRAISON SANS BOSSE 1:"), r["auVolant"]
    assert r["reussi"] is True, f"la livraison ne se gagne pas : {r['msg']} (encore : {r['encore']})"
    assert str(liv["prime"]) in r["msg"]


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
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
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
    assert r["forcee"] == "LES CRAVATES CHASSÉES DU FAUBOURG" and r["forceeLue"] == "narrateur-journal-cravates_chassees"
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


def test_la_premiere_replique_se_dit_quand_on_parle_au_bouton(banc, paquet):
    """⚠️ Rouge avant (17 sept. 2026), chez les cinq donneurs : l'appui d'ACTION
    qui ouvre la conversation etait relu par `Histoire.majCinema` dans la MEME
    image, et passait a la deuxieme replique. La voix de la premiere etait
    demandee, puis coupee. Les juges d'avant ne le voyaient pas : ils ouvraient
    la conversation par `Missions.interagir`, jamais par le bouton.

    On appuie comme un joueur (clavier, puis manette pour Ti-Guy), on laisse
    jouer l'intro — scene comprise — sans rien toucher, et on releve les
    repliques affichees."""
    premieres = {}
    for m in paquet["missions"]:
        # ⚠️ Marco donne M3 ET m97 : `disponibleDe` sert la PREMIERE dans l'ordre
        # du catalogue dont les prérequis sont faits. On garde donc la première
        # occurrence, pas la dernière.
        if m["donneur"] in premieres:
            continue
        n = len(m["dialogue"].get("appel", []))
        premieres[m["donneur"]] = f"{m['dialogue']['intro'][0]['qui']}-{m['slug']}-{n + 1}"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde, out = {};
        const avant = { ti_guy: [], thibodeau: ['m1'], marco: ['m1', 'm2'], bouchard: ['m1', 'm2', 'm3'], josee: ['m1', 'm2', 'm3', 'm4'] };
        const pieces = { bouchard: 'casse_croute', josee: 'bar' };
        function essai(slug, manette) {
            B.partie.missionsFaites = {};
            avant[slug].forEach(function (s) { B.partie.missionsFaites[s] = 1; });
            B.partie.appels = { m2: true, m3: true, m4: true, m5: true };
            if (pieces[slug]) o.entrer(M.carte.portes.find(function (p) { return p.lieu === pieces[slug]; }));
            const d = L.Histoire.donneur(slug);
            if (!d) return { absent: true };
            j.x = d.x - 14; j.y = d.y; L.Entites.indexer();
            L.Son.Voix.demandees.length = 0;
            if (manette) { o.pad([0, 0, 0, 0], [1]); o.frame(1); o.pad([0, 0, 0, 0], [0]); o.frame(1); }
            else { o.touche('KeyE'); o.frame(1); o.relacher('KeyE'); o.frame(1); }
            const vues = [];
            for (let k = 0; k < 2400 && (B.cinema || B.scene); k++) {
                const c = B.cinema;
                const s = c && c.lignes[c.i] ? c.lignes[c.i].slug : null;
                if (s && vues[vues.length - 1] !== s) vues.push(s);
                o.frame(1);
            }
            const rec = { vues: vues, voix: L.Son.Voix.demandees[0] || null, mission: B.partie.mission && B.partie.mission.slug };
            if (B.partie.mission) { L.Histoire.echouer('juge'); B.cinema = null; B.scene = null; }
            if (B.interieur) o.sortir();
            o.pad(null);
            return rec;
        }
        ['ti_guy', 'thibodeau', 'marco', 'bouchard', 'josee'].forEach(function (s) { out[s] = essai(s, false); });
        out.manette = essai('ti_guy', true);
        return out;
    }""")
    for qui, e in r.items():
        attendue = premieres["ti_guy" if qui == "manette" else qui]
        assert not e.get("absent"), f"{qui} : pas la"
        assert e["mission"], f"{qui} : parler au bouton n'a rien commence ({e})"
        assert e["vues"] and e["vues"][0] == attendue, (
            f"{qui} : la premiere replique affichee est {e['vues'][:1]}, pas {attendue} — l'appui qui ouvre l'a sautee")
        assert e["voix"] == attendue


def test_le_char_de_m1_dort_loin_du_garage(banc):
    """Demande de Martin (17 sept. 2026) : « déplacer plus loin la voiture de la
    premiere mission ». La ruelle la plus proche du garage est a six tuiles : le
    char naissait dans l'ecran, sous les yeux du joueur arrive au garage, et le
    ramener tenait en trois secondes. ⚠️ Plus loin, il doit rester un char qu'on
    peut prendre : dans la ruelle par ses deux bouts, relie au garage par la
    route, il en sort sans toucher un mur — et la coupe de l'intro, qui va le
    montrer, filme SA ruelle et pas la plus proche."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde, TT = L.TT;
        L.Histoire.commencer('m1');
        B.cinema = null;
        const garage = L.Histoire.lieu('garage');
        j.x = garage.x; j.y = garage.y; L.Entites.indexer();
        M.centrerCamera(j.x, j.y);
        o.frame(3);
        const v = B.mission.vehicule;
        M.centrerCamera(j.x, j.y);
        const vu = L.Entites.visibleAEcran(v.x, v.y, 0);
        // La coupe de l'intro va MONTRER ce char : elle doit tomber sur sa ruelle.
        const coupe = ((B.defs.missions[0].scenes || {}).intro || []).find(function (q) { return q.type === 'coupe'; });
        const filme = coupe ? L.Histoire.resoudre(coupe.vers, L.Histoire.courante()) : null;
        const ecartCoupe = filme ? Math.hypot(filme.x - v.x, filme.y - v.y) : null;
        const ca = Math.cos(v.angle), sa = Math.sin(v.angle);
        const bouts = [12, -12].map(function (d) { return M.glyphe(Math.floor((v.x + ca * d) / TT), Math.floor((v.y + sa * d) / TT)); });
        // La route, ecrite ici : du char, les tuiles ou un char roule.
        const W = M.carte.w, H = M.carte.h, vus = new Uint8Array(W * H), file = [];
        const s0 = Math.floor(v.y / TT) * W + Math.floor(v.x / TT);
        vus[s0] = 1; file.push(s0);
        for (let i = 0; i < file.length; i++) {
            const k = file[i], x = k % W, y = (k - x) / W;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
                const nx = x + d[0], ny = y + d[1], nk = ny * W + nx;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H || vus[nk]) return;
                if (M.bloque(nx, ny, M.MASQUE_VEHICULE) || M.estEau(nx, ny)) return;
                vus[nk] = 1; file.push(nk);
            });
        }
        let relie = false;
        for (let y = Math.floor(garage.y / TT) - 4; y <= Math.floor(garage.y / TT) + 4; y++) {
            for (let x = Math.floor(garage.x / TT) - 4; x <= Math.floor(garage.x / TT) + 4; x++) if (vus[y * W + x]) relie = true;
        }
        const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
        for (const c of cotes) {
            j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer();
            if (L.Vehicules.vehiculeSousLaMain(j) === v) break;
        }
        o.tape('KeyE', 2);
        const monte = j.dansVehicule === v;
        const x0 = v.x, y0 = v.y;
        o.touche('KeyW'); o.frame(50); o.relacher('KeyW'); o.frame(1);
        return { tuiles: Math.hypot(v.x - garage.x, v.y - garage.y) / TT, depart: Math.hypot(x0 - garage.x, y0 - garage.y) / TT,
                 glyphe: M.glyphe(Math.floor(x0 / TT), Math.floor(y0 / TT)), bouts: bouts, vu: vu, relie: relie, ecartCoupe: ecartCoupe,
                 monte: monte, roule: Math.hypot(v.x - x0, v.y - y0), chocs: v.chocs, etape: B.partie.mission.etape };
    }""")
    assert r["depart"] >= 20, f"le char dort a {r['depart']:.0f} tuiles du garage : pas plus loin qu'avant (6)"
    assert r["vu"] is False, "le char nait dans l'ecran, sous les yeux du joueur arrive au garage"
    assert r["ecartCoupe"] is not None and r["ecartCoupe"] < 16, (
        f"la coupe de l'intro filme une ruelle a {r['ecartCoupe']} px de celle ou dort le char")
    assert r["glyphe"] == "x" and r["bouts"] == ["x", "x"], f"le char deborde de sa ruelle : {r['bouts']}"
    assert r["relie"] is True, "aucune route ne ramene ce char au garage"
    assert r["monte"] is True and r["etape"] == 2
    assert r["roule"] > 30 and r["chocs"] == 0, f"le char ne sort pas de sa ruelle ({r['roule']:.0f} px, {r['chocs']} chocs)"


def test_le_char_de_la_mission_saute_sous_le_joueur_et_la_mission_rate(banc):
    """⚠️ Rouge avant (17 sept. 2026), deux fois. Le taxi de Marco explosait
    pendant les courses et M3 continuait a « 0/3 » ; l'auto-patrouille de M4
    sautait pendant qu'on semait et M4 attendait qu'on la livre. `descendre()`
    rendait la carcasse `stationne`, et seuls `monter` et `livrer` regardaient
    l'epave."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde;
        function monter(v) {
            const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
            for (const c of cotes) {
                j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer();
                if (L.Vehicules.vehiculeSousLaMain(j) === v) break;
            }
            o.tape('KeyE', 2);
            return j.dansVehicule === v;
        }
        function sauter(v) {
            j.invincible = 1e6;                       // on juge la mission, pas la brulure
            // ⚠️ La replique « pendant » de l'objectif d'abord, au bouton : tant
            // qu'elle se dit, l'objectif attend (`Histoire.maj`).
            for (let k = 0; k < 20 && B.cinema; k++) o.tape('KeyE', 2);
            const pret = { etape: B.partie.mission && B.partie.mission.etape, cinema: !!B.cinema };
            L.Vehicules.endommager(v, 9999, null);
            let n = 0;
            while (B.partie.mission && n < 10) { o.frame(1); n++; }
            const rec = { pret: pret, etat: v.etat, ratee: !B.partie.mission, dit: B.cinema && B.cinema.partie, msg: B.msg };
            B.cinema = null; B.dialogue = null;
            B.recherche.etoiles = 0;
            return rec;
        }
        const out = {};
        // M3, pendant les courses.
        B.partie.missionsFaites = { m1: 1, m2: 1 };
        L.Histoire.commencer('m3'); B.cinema = null;
        o.frame(2);
        const taxi = B.mission.vehicule;
        out.m3 = { monte: monter(taxi) };
        o.frame(2);
        out.m3.etape = B.partie.mission.etape;
        Object.assign(out.m3, sauter(taxi));
        // M4, pendant qu'on seme.
        B.partie.missionsFaites = { m1: 1, m2: 1, m3: 1 };
        L.Histoire.commencer('m4'); B.cinema = null;
        let h = B.partie.heure;
        for (let k = 0; k < 200 && !M.estNuit(h); k++) h = (h + 0.005) % 1;
        B.partie.heure = h;
        const poste = L.Histoire.lieu('poste');
        j.x = poste.x; j.y = poste.y; L.Entites.indexer();
        o.frame(3);
        const patrouille = B.mission.vehicule;
        out.m4 = { monte: monter(patrouille) };
        o.frame(2);
        out.m4.etape = B.partie.mission.etape;
        Object.assign(out.m4, sauter(patrouille));
        return out;
    }""")
    for slug, titre, etape in (("m3", "LE TAXI DE MARCO", 1), ("m4", "LE LUNCH DU SERGENT", 2)):
        m = r[slug]
        assert m["monte"] is True and m["etape"] == etape, m
        assert m["pret"] == {"etape": etape, "cinema": False}, m
        assert m["etat"] == "epave", f"{slug} : le char a saute sous le joueur et n'est pas une epave ({m['etat']})"
        assert m["ratee"] is True and m["dit"] == "echec", f"{slug} : le char a saute et la mission continue ({m})"
        assert m["msg"] == "MISSION RATÉE — " + titre


def test_le_char_de_la_mission_ne_nait_pas_sous_celui_du_joueur(banc):
    """⚠️ Rouge avant (17 sept. 2026), 8 graines sur 8. « L'auto-patrouille
    n'apparaît pas toujours » : arrivé au poste EN CHAR, on s'arrête dans la rue
    devant la porte — et l'auto-patrouille naissait sur cette tuile-là, aux mêmes
    x et y que notre char, cachée dessous. ACTION nous remettait dans le nôtre.
    Le taxi de Marco (M3) naît par le même chemin, devant le garage."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde;
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        function essai(slug, faites, lieu, nuit) {
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            j.invincible = 1e6;
            // On s'arrete dans la rue, devant la porte : la tuile de rue la plus
            // proche. Le taxi de M3 se pose des qu'on la prend, l'auto-patrouille
            // de M4 quand on arrive au poste : le char est la avant les deux.
            const porte = L.Histoire.lieu(lieu);
            const arret = L.Histoire.tuileDeRue(porte.x, porte.y, 8);
            const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], {});
            L.Vehicules.monter(j, mien); L.Entites.indexer();
            if (nuit) { let h = B.partie.heure; for (let k = 0; k < 400 && !M.estNuit(h); k++) h = (h + 0.005) % 1; B.partie.heure = h; }
            B.partie.missionsFaites = faites;
            L.Histoire.commencer(slug); B.cinema = null;
            for (let n = 0; n < 30 && !B.mission.vehicule; n++) o.frame(1);
            const v = B.mission.vehicule;
            if (!v) return { etape: B.partie.mission.etape };
            const ecart = Math.hypot(v.x - mien.x, v.y - mien.y);
            L.Vehicules.descendre(j, true); o.frame(2);
            const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
            for (const c of cotes) { j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer(); if (L.Vehicules.vehiculeSousLaMain(j) === v) break; }
            o.tape('KeyE', 2);
            const rec = { slug: v.slug, ecart: Math.round(ecart), monte: j.dansVehicule === v, etape: B.partie.mission.etape };
            L.Histoire.echouer('arrete'); B.cinema = null; B.dialogue = null; B.recherche.etoiles = 0;
            L.Entites.retirer(mien);
            return rec;
        }
        return { m4: essai('m4', { m1: 1, m2: 1, m3: 1 }, 'poste', true),
                 m3: essai('m3', { m1: 1, m2: 1 }, 'garage', false) };
    }""")
    # M3 monte au premier objectif, M4 au deuxième (il faut d'abord aller au poste).
    for slug, vehicule, nom, apres in (("m4", "police", "l'auto-patrouille", 2), ("m3", "taxi", "le taxi", 1)):
        m = r[slug]
        assert m.get("slug") == vehicule, f"{slug} : pas de {nom} ({m})"
        assert m["ecart"] >= 28, f"{slug} : {nom} naît dans le char du joueur ({m['ecart']} px, un char en fait 28)"
        assert m["monte"] is True and m["etape"] == apres, f"{slug} : ACTION ne fait pas monter dans {nom} ({m})"


def test_ti_guy_nait_derriere_l_auto_patrouille_et_la_suit(banc):
    """⚠️ Rouge avant (17 sept. 2026), 24 essais sur 24. « Celui qui doit nous
    suivre apparaît en avant » : Ti-Guy naissait sur la tuile de rue la plus
    proche, 28 px DEVANT l'auto-patrouille, dans sa voie. L'escorte s'arrête à
    70 px du joueur : il restait planté là, et on n'avançait que de 42 px en une
    seconde et demie, le pare-chocs dans le sien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const B = L.B, j = B.joueur, M = L.Monde;
        B.partie.missionsFaites = { m1: 1, m2: 1, m3: 1 };
        L.Histoire.commencer('m4'); B.cinema = null;
        let h = B.partie.heure;
        for (let k = 0; k < 400 && !M.estNuit(h); k++) h = (h + 0.005) % 1;
        B.partie.heure = h;
        j.invincible = 1e6;
        const poste = L.Histoire.lieu('poste');
        j.x = poste.x; j.y = poste.y + 20; L.Entites.indexer();
        for (let n = 0; n < 30 && B.partie.mission.etape < 1; n++) o.frame(1);
        const v = B.mission.vehicule;
        const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
        for (const c of cotes) { j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer(); if (L.Vehicules.vehiculeSousLaMain(j) === v) break; }
        o.tape('KeyE', 2);
        o.frame(2);
        const e = B.mission.escorte;
        const out = { monte: j.dansVehicule === v, etape: B.partie.mission.etape, escorte: !!e };
        if (!e || !out.monte) return out;
        // Devant, c'est le nez de l'auto-patrouille.
        const hx = Math.cos(v.angle), hy = Math.sin(v.angle);
        out.devant = Math.round((e.x - v.x) * hx + (e.y - v.y) * hy);
        out.cote = Math.round(Math.abs(-(e.x - v.x) * hy + (e.y - v.y) * hx));
        out.memeSens = Math.cos(e.angle - v.angle) > 0.7;
        // La replique de Ti-Guy, au bouton, puis on roule tout droit.
        for (let k = 0; k < 20 && B.cinema; k++) o.tape('KeyE', 2);
        const ex = e.x, ey = e.y, vx = v.x, vy = v.y;
        o.touche('KeyW'); o.frame(90); o.relacher('KeyW'); o.frame(60);
        out.joueur = Math.round((v.x - vx) * hx + (v.y - vy) * hy);
        out.suit = Math.round((e.x - ex) * hx + (e.y - ey) * hy);
        return out;
    }""")
    assert r["monte"] is True and r["etape"] == 2 and r["escorte"] is True, r
    assert r["devant"] <= -40, f"Ti-Guy naît devant l'auto-patrouille ({r['devant']} px devant son nez)"
    assert r["cote"] <= 24 and r["memeSens"] is True, f"Ti-Guy n'est pas dans une voie qui va où l'on va ({r})"
    assert r["joueur"] > 150, f"l'auto-patrouille n'avance que de {r['joueur']} px : quelqu'un lui bouche la rue"
    assert r["suit"] > 60, f"Ti-Guy ne suit pas ({r['suit']} px pendant qu'on en roule {r['joueur']})"
