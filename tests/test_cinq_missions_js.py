"""Les cinq missions de « Cinq missions de plus, dans la lignée de m50 », JOUÉES au bouton.

Les juges de structure (`verifier_missions.py`, `test_mise_en_scene.py`) disent qu'une mission a ses
objectifs, ses répliques et ses scènes ; ils ne la jouent pas. m50 était « finie » sur le papier et son
fuyard naissait au coin de la carte (20 sept. 2026) : ici, chacune se joue de l'appel à la prime, avec
ce que le jeu fait vraiment — les hommes qui arrivent de loin, le char qui dort dans sa ruelle, la
poignée de main dite, l'argent encaissé.
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function boite(L) {
    const c = L.B.cinema;
    return c ? { partie: c.partie, qui: c.lignes[0].qui, slug: c.lignes[0].slug, telephone: c.lignes[0].telephone } : null;
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function heure(L, nuit) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && L.Monde.estNuit(h) !== nuit; k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h;
  }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push({ montant: montant, raison: raison || null }); return vrai.apply(null, arguments); };
    return liste;
  }
  function hommes(L, etape) {
    const j = L.B.joueur;
    return L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === etape; })
      .map(function (e) { return { e: e, d: Math.round(Math.hypot(e.x - j.x, e.y - j.y)) }; });
  }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) o.frame(1); passer(L, o); }
"""


def test_f01_les_cravates_arrivent_de_loin_la_nuit_puis_leur_chef_puis_marco_paie(banc):
    """Marco, au garage : de jour on attend la noirceur ; trois Cravates de rue (bâton, 90 PV — leur fiche
    ne bouge pas) arrivent alors de loin et courent sur nous ; les coucher fait sortir leur chef ; Marco
    paie 300 $ quand on revient à lui."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50']);
        const argent = paiements(L);
        heure(L, false);
        const marco = L.Histoire.donneur('marco');
        j.x = marco.x - 16; j.y = marco.y; L.Entites.indexer();
        const parle = L.Histoire.parler('marco');
        const scene = !!B.scene;
        passer(L, o);
        const debut = { parle: parle, scene: scene, slug: B.partie.mission && B.partie.mission.slug,
                        objectif: L.Histoire.ligneObjectif() };
        o.frame(3);
        const attend = B.mission.attend, etapeJour = etape(L);
        heure(L, true);
        o.frame(3);
        const etapeNuit = etape(L);
        const trois = hommes(L, 1);
        const arrivent = trois.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme, vie: h.e.vieMax }; });
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const etapeChef = etape(L);
        const chef = B.mission.entites.find(function (e) { return e.chef; });
        const chefFiche = chef ? { vie: chef.vieMax, arme: chef.arme } : null;   // avant : un homme K.-O. lâche son arme
        const pendant = boite(L);
        fermer(L);
        // On se bat à la porte de Marco : `retourner` se ferait dans la même image. On s'écarte d'abord.
        j.x = marco.x + 300; j.y = marco.y; L.Entites.indexer();
        if (chef) L.Entites.assommer(chef);
        o.frame(2);
        const etapeRetour = etape(L), ligneRetour = L.Histoire.ligneObjectif();
        const m2 = L.Histoire.donneur('marco');
        j.x = m2.x - 16; j.y = m2.y; L.Entites.indexer();
        finir(L, o);
        return { debut: debut, attend: attend, etapeJour: etapeJour, etapeNuit: etapeNuit, arrivent: arrivent,
                 etapeChef: etapeChef, chef: chefFiche, pendant: pendant,
                 etapeRetour: etapeRetour, ligneRetour: ligneRetour, fait: !!B.partie.missionsFaites.f01,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"]["parle"] is True and r["debut"]["scene"] is True and r["debut"]["slug"] == "f01", r["debut"]
    assert r["debut"]["objectif"].startswith("ATTENDS LA NUIT")
    assert r["attend"] == "ATTENDS LA NUIT" and r["etapeJour"] == 0, "de jour, on attend la noirceur"
    assert r["etapeNuit"] == 1, "la nuit venue, les Cravates arrivent"
    assert len(r["arrivent"]) == 3
    for h in r["arrivent"]:
        assert 100 <= h["d"] <= 260, f"ils arrivent de loin, ni sur nous ni hors de portée ({h['d']} px)"
        assert h["etat"] == "attaque_joueur", "à la course, sur le joueur"
        assert h["arme"] == "batte" and h["vie"] == 90, "la Cravate de rue reste ce qu'elle est"
    assert r["etapeChef"] == 2 and r["chef"] == {"vie": 160, "arme": "batte"}, "leur chef sort quand ils sont tombés"
    assert r["pendant"] == {"partie": "pendant", "qui": "marco", "slug": "marco-f01-7", "telephone": False} \
        or (r["pendant"] and r["pendant"]["slug"] == "marco-f01-7"), r["pendant"]
    assert r["etapeRetour"] == 3 and r["ligneRetour"].startswith("RETOURNE VOIR MARCO")
    assert r["fait"] is True and r["argent"] == [300], "Marco paie la mission"


def test_e01_les_chevreuils_arrivent_les_poings_nus_et_ti_paul_paie(banc):
    """Ti-Paul, au dépanneur : la nuit, trois Chevreuils à 60 PV et les poings nus arrivent de loin (des
    ados, pas des Cravates) ; on les couche, on revient à Ti-Paul, 150 $."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        const ti = L.Histoire.donneur('tipaul');
        j.x = ti.x - 16; j.y = ti.y; L.Entites.indexer();
        const parle = L.Histoire.parler('tipaul');
        passer(L, o);
        const debut = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        heure(L, true);       // ⚠️ APRES l'intro : la scène fait avancer l'horloge
        o.frame(3);
        const etapeNuit = etape(L);
        const trois = hommes(L, 1);
        const arrivent = trois.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme || null, vie: h.e.vieMax }; });
        const pendant = boite(L);
        fermer(L);
        // On se bat à la porte de Ti-Paul : `retourner` se ferait dans la même image. On s'écarte d'abord.
        j.x = ti.x + 300; j.y = ti.y; L.Entites.indexer();
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const etapeRetour = etape(L);
        const t2 = L.Histoire.donneur('tipaul');
        j.x = t2.x - 16; j.y = t2.y; L.Entites.indexer();
        finir(L, o);
        return { debut: debut, etapeNuit: etapeNuit, arrivent: arrivent, pendant: pendant, etapeRetour: etapeRetour,
                 fait: !!B.partie.missionsFaites.e01, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"] == {"parle": True, "slug": "e01"}
    assert r["etapeNuit"] == 1 and len(r["arrivent"]) == 3, "la nuit : trois Chevreuils"
    for h in r["arrivent"]:
        assert 100 <= h["d"] <= 260, f"ils arrivent de loin ({h['d']} px)"
        assert h["etat"] == "attaque_joueur"
        assert h["arme"] is None and h["vie"] == 60, "les poings nus, 60 PV : des ados"
    assert r["pendant"] and r["pendant"]["slug"] == "tipaul-e01-7", "Ti-Paul les voit venir"
    assert r["etapeRetour"] == 2
    assert r["fait"] is True and r["argent"] == [150]


def test_q02_le_camion_de_poisson_dort_dans_sa_ruelle_et_se_livre_sans_bosse(banc):
    """Lulu : le camion dort dans une ruelle des Quais dès le début (l'intro le filme), on le prend, on le
    livre au casse-croûte. Sans bosse, la mission paie la moitié en plus ; avec une bosse, non."""
    JEU = """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        L.Histoire.commencer('q02'); B.cinema = null; B.scene = null;
        const v = B.mission.vehicule, cantine = L.Histoire.lieu('cantine');
        const camion = v ? { slug: v.slug, etat: v.etat, d: Math.round(Math.hypot(v.x - cantine.x, v.y - cantine.y)) } : null;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2);
        const etapeCourante = etape(L), ligne = L.Histoire.ligneObjectif();
        const pendant = boite(L);
        fermer(L);
        BOSSE
        const l = L.Histoire.lieuDeLivraison('casse_croute');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { camion: camion, etape: etapeCourante, ligne: ligne, pendant: pendant, fait: !!B.partie.missionsFaites.q02,
                 argent: argent.map(function (a) { return a.montant; }) };
    }"""
    propre = banc("function (L, o) {" + OUTILS + JEU.replace("BOSSE", ""))
    cabosse = banc("function (L, o) {" + OUTILS + JEU.replace("BOSSE", "v.chocs = (v.chocs || 0) + 1;"))
    c = propre["camion"]
    assert c and c["slug"] == "camion" and c["etat"] == "stationne", "le camion de poisson dort là avant qu'on en parle"
    assert c["d"] >= 100, f"il faut le chercher, pas le trouver à la porte ({c['d']} px de la cantine)"
    assert propre["etape"] == 1 and propre["ligne"].startswith("LIVRE LE POISSON"), "monté, on livre"
    assert propre["pendant"] == {"partie": "pendant", "qui": "lulu", "slug": "lulu-q02-7", "telephone": True}, \
        "Lulu le dit au combiné : elle est à sa cantine"
    assert propre["fait"] is True and propre["argent"] == [375], "250 $ et la prime sans bosse (+50 %)"
    assert cabosse["fait"] is True and cabosse["argent"] == [250], "une bosse, et la prime s'en va"


def test_s03_le_camion_de_paie_deux_etoiles_puis_le_syndicat(banc):
    """Raymonde : le camion de paie dort près de l'hôtel ; le prendre met la police (2★) aux fesses, on la
    sème, on livre au bar de Josée (l'usine ferme la nuit, un lieu de mission ne peut pas l'être) : 450 $ — sans prime de bosse, la mission n'en demande pas."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02']);
        const argent = paiements(L);
        L.Histoire.commencer('s03'); B.cinema = null; B.scene = null;
        const v = B.mission.vehicule, hotel = L.Histoire.lieu('hotel');
        const camion = v ? { slug: v.slug, d: Math.round(Math.hypot(v.x - hotel.x, v.y - hotel.y)) } : null;
        const etoiles0 = B.recherche.etoiles;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2);
        const etapeSemer = etape(L), etoiles = B.recherche.etoiles;
        const pendant = boite(L);
        fermer(L);
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        o.frame(3);
        const etapeLivrer = etape(L), ligne = L.Histoire.ligneObjectif();
        const l = L.Histoire.lieuDeLivraison('bar');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { camion: camion, etoiles0: etoiles0, etapeSemer: etapeSemer, etoiles: etoiles, pendant: pendant,
                 etapeLivrer: etapeLivrer, ligne: ligne, fait: !!B.partie.missionsFaites.s03,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["camion"] and r["camion"]["slug"] == "camion" and r["camion"]["d"] >= 100, r["camion"]
    assert r["etoiles0"] == 0, "la police ne sait rien tant qu'on n'a pas pris le camion"
    assert r["etapeSemer"] == 1 and r["etoiles"] >= 2, "monté dans le camion de paie : deux étoiles"
    assert r["pendant"] == {"partie": "pendant", "qui": "raymonde", "slug": "raymonde-s03-7", "telephone": True}
    assert r["etapeLivrer"] == 2 and r["ligne"].startswith("LIVRE LA PAIE AU BAR"), "semée, on livre"
    assert r["fait"] is True and r["argent"] == [450]


def test_s03_le_camion_de_paie_a_fond_seme_l_agent_a_pied_et_les_etoiles_tombent(banc):
    """⚠️ Le juge d'au-dessus SAUTE l'étape « sème la police » (`etoiles = 0`) — et c'est elle que Martin n'a
    jamais passée (21 sept. 2026 : « presque impossible, le camion va trop lentement pour les policiers »). Le
    camion plafonnait à 1,97 px/image au lieu des 2,8 de sa fiche, un agent à pied court à 2,0 : il le suivait
    à 40 px, le voyait à chaque image, et les deux étoiles ne tombaient jamais.

    Ici on la joue : le camion de paie, gaz tenu au bouton, sur la plus longue ligne droite de la ville, un
    agent en chasse à 40 px derrière. Le camion prend sa vitesse, l'agent le perd de vue, et la première
    étoile tombe. Le reste de la ville est coupé — les passants qu'on renverserait feraient monter la chaleur,
    les autres agents naissent au hasard (`peuplerAgents`) : ce n'est pas ce qu'on juge. L'agent regarde à
    chaque image, pas une sur trois : c'est l'`id` de l'agent qui choisissait lesquelles."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, TT = L.TT, c = L.Monde.carte; j.invincible = 1e6;
        B.defs.conduite.trafic.vehicules_max = 0; B.defs.conduite.trafic.stationnes_max = 0;
        B.defs.recherche.police.regarde_toutes_les_images = 1;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02']);
        L.Histoire.commencer('s03'); B.cinema = null; B.scene = null;
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2); fermer(L);
        const debut = { etape: etape(L), etoiles: B.recherche.etoiles };
        // La plus longue ligne droite vers l'est où passe un camion (trois rangées libres).
        let route = null;
        for (let ty = 2; ty < c.h - 2; ty++) {
            let x0 = null;
            for (let tx = 1; tx < c.w - 1; tx++) {
                const libre = L.Monde.estRoute(tx, ty) && [-1, 0, 1].every(function (d) {
                    return !L.Monde.bloque(tx, ty + d, L.Monde.MASQUE_VEHICULE) && !L.Monde.estEau(tx, ty + d);
                });
                if (!libre) { x0 = null; continue; }
                if (x0 === null) x0 = tx;
                if (!route || tx - x0 > route.l) route = { x: x0, y: ty, l: tx - x0 };
            }
        }
        const xa = (route.x + 2) * TT + 8, ya = route.y * TT + 8, fin = (route.x + route.l - 4) * TT;
        v.x = xa; v.y = ya; v.angle = 0; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
        L.Monde.centrerCamera(v.x, v.y);
        const agent = L.Police.creerAgent(xa - 40, ya, 'poursuit'); agent.angle = 0; agent.vuT = 0;
        B.recherche.vu = 0; B.recherche.dernierVu = { x: xa, y: ya, t: B.t };
        function vider() {
            B.entites.filter(function (e) {
                return e !== j && e !== v && e !== agent && (e.type === 'vehicule' || e.type === 'pieton');
            }).forEach(function (e) { L.Entites.retirer(e); });
            L.Entites.indexer();
        }
        vider();
        let pointe = 0, perdu = null, tombe = null, i = 0;
        o.touche('KeyW');
        for (; i < 60 * 45 && v.x < fin && tombe === null; i++) {
            o.frame(1);
            if (i % 10 === 0) vider();
            pointe = Math.max(pointe, Math.abs(v.vitesse));
            if (perdu === null && B.recherche.vu > 60) perdu = { s: +(i / 60).toFixed(1), d: Math.round(Math.hypot(agent.x - v.x, agent.y - v.y)) };
            if (B.recherche.etoiles < 2) tombe = +(i / 60).toFixed(1);
        }
        o.relacher('KeyW');
        return { debut: debut, route: route, pointe: +pointe.toFixed(2), fiche: v.def.vitesse_max, perdu: perdu, tombe: tombe,
                 s: +(i / 60).toFixed(1), d: Math.round(Math.hypot(agent.x - v.x, agent.y - v.y)),
                 etoiles: B.recherche.etoiles, etape: etape(L), dans: j.dansVehicule === v };
    }""")
    assert r["debut"] == {"etape": 1, "etoiles": 2}, r["debut"]
    assert r["route"]["l"] >= 200, f"pas de ligne droite assez longue pour juger : {r['route']}"
    assert r["dans"], "on est sorti du camion en route"
    assert r["pointe"] >= 0.95 * r["fiche"], f"le camion plafonne sous sa fiche : {r}"
    assert r["perdu"] is not None, f"l'agent à pied ne lâche pas le camion : {r}"
    assert r["tombe"] is not None, f"les deux étoiles ne tombent jamais : {r}"
    assert r["etape"] == 1 and r["etoiles"] == 1, r


def test_m51_la_tournee_du_sergent_trois_poignees_de_main_dites_puis_le_casse_croute(banc):
    """Bouchard : Thibodeau, Lulu et Ti-Paul disent chacun leur mot en personne (leur voix demandée), et
    l'objectif n'avance qu'une fois la boîte fermée ; puis on rapporte les enveloppes au casse-croûte."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02']);
        const argent = paiements(L);
        L.Histoire.commencer('m51'); B.cinema = null; B.scene = null;
        const d0 = L.Son.Voix.demandees.length;
        const vus = [];
        for (const slug of ['thibodeau', 'lulu', 'tipaul']) {
            const avant = etape(L);
            const rendu = L.Histoire.parler(slug);
            const b = boite(L), pendantBoite = etape(L);
            fermer(L);
            vus.push({ rendu: rendu, avant: avant, pendant: pendantBoite, apres: etape(L), boite: b });
        }
        const voix = L.Son.Voix.demandees.slice(d0);
        const etapeCourante = etape(L), ligne = L.Histoire.ligneObjectif();
        const dernier = boite(L);
        const l = L.Histoire.lieu('casse_croute');
        j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { vus: vus, voix: voix, etape: etapeCourante, ligne: ligne, dernier: dernier,
                 fait: !!B.partie.missionsFaites.m51, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    attendus = [("thibodeau", "thibodeau-m51-8"), ("lulu", "lulu-m51-9"), ("tipaul", "tipaul-m51-10")]
    assert len(r["vus"]) == 3
    for i, (v, (qui, slug)) in enumerate(zip(r["vus"], attendus)):
        assert v["rendu"] is True, f"contact {i} : parler() ne rend pas true"
        assert v["boite"] == {"partie": "accueil", "qui": qui, "slug": slug, "telephone": False}, (i, v["boite"])
        assert v["avant"] == i and v["pendant"] == i, f"contact {i} : l'objectif avance PENDANT sa réplique"
        assert v["apres"] == i + 1, f"contact {i} : l'objectif n'avance pas après sa réplique ({v['apres']})"
    assert [s for s in r["voix"] if "-m51-" in s][:3] == [s for _, s in attendus], "chacun demande sa voix"
    assert r["etape"] == 3 and r["ligne"].startswith("RAPPORTE LES ENVELOPPES")
    assert r["fait"] is True and r["argent"] == [350]
