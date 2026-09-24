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
  // Entrer chez quelqu'un qui se tient DEDANS et se planter sur son point, comme un joueur.
  function dedans(L, o, lieu, point) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; L.Entites.indexer();
    o.frame(2);
    return B.interieur.slug;
  }
  function sortir(L, o) {
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
    return !L.B.interieur;
  }
  // ACTION au bouton (la poignée de main passe par `Missions.interagir`, comme au jeu).
  function action(L, o) { o.tape('KeyE', 2); o.frame(2); }
  // Dehors : se planter à côté de quelqu'un, un pas vers lui (on le REGARDE : `faceA`), puis ACTION.
  function serrerLaMain(L, o, slug) {
    const j = L.B.joueur, e = L.Histoire.donneur(slug);
    j.x = e.x - 20; j.y = e.y; L.Entites.indexer();
    o.touche('KeyD'); o.frame(2); o.relacher('KeyD'); o.frame(1);
    action(L, o);
  }
  // Le fuyard d'un `ramasser` : le char casse, le porteur tombe, on ramasse la caisse à pied.
  function rattraper(L, o) {
    const B = L.B, j = B.joueur, f = B.mission.fuyard;
    const d = f ? Math.round(Math.hypot(f.x - j.x, f.y - j.y)) : null;
    L.Vehicules.endommager(f, 999, j); o.frame(2);
    const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
    L.Entites.assommer(porteur); o.frame(2);
    const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
    j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); o.frame(2);
    return d;
  }
  // Semer comme un joueur : entrer dans `lieu` et y attendre que les étoiles tombent (la police ne
  // voit pas dedans : 1★ ≈ 20 s, 2★ ≈ 40 s) ; `majObjectif` ne tourne pas dedans, l'objectif avance
  // à la sortie. Rien n'est remis à zéro à la main.
  function semerDedans(L, o, lieu) {
    const B = L.B, j = B.joueur, M = L.Monde, avant = etape(L), etoiles = B.recherche.etoiles;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    let n = 0;
    for (; n < 9000 && B.recherche.etoiles > 0; n++) o.frame(1);
    const pendantQuOnSeCache = etape(L);
    sortir(L, o); o.frame(3);
    return { avant: avant, etoiles: etoiles, secondes: Math.round(n / 60), cache: pendantQuOnSeCache,
             apres: etape(L), ligne: L.Histoire.ligneObjectif() };
  }
"""


def test_f01_les_cravates_arrivent_de_loin_puis_leur_chef_leur_comptable_la_police_et_ovila(banc):
    """Marco, au garage : de jour on attend la noirceur ; trois Cravates de rue (bâton, 90 PV — leur fiche
    ne bouge pas) arrivent alors de loin et courent sur nous ; les coucher fait sortir leur chef.

    « Des missions plus longues » (22 sept. 2026) : leur chef couché, leur comptable file en char avec le
    livre de dettes ; on le rattrape, deux étoiles tombent sur nous (on se cache dans le garage jusqu'à ce
    qu'elles tombent) ; Ovila, au phare — l'autre bout de la ville —, prend le livre en disant son mot ;
    et Marco paie 300 $ quand on revient à lui."""
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
        if (chef) L.Entites.assommer(chef);
        o.frame(2);
        // Le comptable file avec le livre.
        const comptable = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L),
                            fuyard: !!B.mission.fuyard };
        fermer(L);
        comptable.d = rattraper(L, o);
        // La police : deux étoiles, qu'on laisse tomber cachés dans le garage.
        const police = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles, boite: boite(L) };
        fermer(L);
        const seme = semerDedans(L, o, 'garage');
        const versOvila = { ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        // Ovila, au phare : la poignée de main se dit, puis l'objectif avance.
        const garage = L.Histoire.lieu('garage'), phare = L.Histoire.lieu('phare');
        const loin = Math.round(Math.hypot(phare.x - garage.x, phare.y - garage.y) / 16);
        const piece = dedans(L, o, 'phare', 'ovila');
        const avantOvila = etape(L);
        action(L, o);
        const ovila = { piece: piece, avant: avantOvila, boite: boite(L), pendantBoite: etape(L) };
        fermer(L); o.frame(2);
        ovila.apres = etape(L); ovila.ligne = L.Histoire.ligneObjectif();
        sortir(L, o);
        const m2 = L.Histoire.donneur('marco');
        j.x = m2.x - 16; j.y = m2.y; L.Entites.indexer();
        finir(L, o);
        return { debut: debut, attend: attend, etapeJour: etapeJour, etapeNuit: etapeNuit, arrivent: arrivent,
                 etapeChef: etapeChef, chef: chefFiche, pendant: pendant, comptable: comptable, police: police,
                 seme: seme, versOvila: versOvila, loin: loin, ovila: ovila,
                 fait: !!B.partie.missionsFaites.f01, argent: argent.map(function (a) { return a.montant; }) };
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
    assert r["pendant"] and r["pendant"]["slug"] == "marco-f01-9" and r["pendant"]["qui"] == "marco", r["pendant"]
    c = r["comptable"]
    assert c["etape"] == 3 and c["ligne"].startswith("RATTRAPE LE COMPTABLE") and c["fuyard"], c
    assert c["boite"] and c["boite"]["slug"] == "marco-f01-10", "Marco le voit filer"
    assert c["d"] is not None and c["d"] <= 200, f"le comptable file devant nous, pas au bout de la ville ({c['d']} px)"
    p = r["police"]
    assert p["etape"] == 4 and p["ligne"].startswith("SÈME LA POLICE") and p["etoiles"] >= 2, p
    assert p["boite"] and p["boite"]["slug"] == "marco-f01-11"
    s = r["seme"]
    assert s["cache"] == 4 and s["apres"] == 5 and 0 < s["secondes"] < 150, f"cachés au garage, les étoiles tombent : {s}"
    assert r["versOvila"]["ligne"].startswith("DONNE LE LIVRE À OVILA")
    assert r["versOvila"]["boite"] and r["versOvila"]["boite"]["slug"] == "marco-f01-12"
    assert r["loin"] >= 200, f"le phare est à l'autre bout de la ville ({r['loin']} tuiles du garage)"
    o = r["ovila"]
    assert o["piece"] == "phare" and o["avant"] == 5
    assert o["boite"] == {"partie": "accueil", "qui": "ovila", "slug": "ovila-f01-13", "telephone": False}, o
    assert o["pendantBoite"] == 5 and o["apres"] == 6, "l'objectif avance une fois qu'Ovila a dit son mot"
    assert o["ligne"].startswith("RETOURNE VOIR MARCO")
    assert r["fait"] is True and r["argent"] == [300], "Marco paie la mission"


def test_e01_les_chevreuils_leur_grand_frere_la_police_puis_bouchard_et_ti_paul_paie(banc):
    """Ti-Paul, au dépanneur : la nuit, trois Chevreuils à 60 PV et les poings nus arrivent de loin (des
    ados, pas des Cravates) ; on les couche.

    « Des missions plus longues » (22 sept. 2026) : leur grand frère sort (le chef : 160 PV, un bâton) ;
    les voisins appellent la police (on se cache dans le dépanneur) ; Ti-Paul nous envoie demander une
    patrouille à Bouchard, au casse-croûte — l'autre bout de la ville —, qui répond en personne ; on
    revient à Ti-Paul, 150 $."""
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
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        // Le grand frère.
        const chef = B.mission.entites.find(function (e) { return e.chef; });
        const frere = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L),
                        fiche: chef ? { vie: chef.vieMax, arme: chef.arme, gang: chef.gang || null } : null,
                        d: chef ? Math.round(Math.hypot(chef.x - j.x, chef.y - j.y)) : null };
        fermer(L);
        if (chef) L.Entites.assommer(chef);
        o.frame(2);
        const police = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles, boite: boite(L) };
        fermer(L);
        const seme = semerDedans(L, o, 'depanneur');
        const versBouchard = { ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const depanneur = L.Histoire.lieu('depanneur'), cc = L.Histoire.lieu('casse_croute');
        const loin = Math.round(Math.hypot(cc.x - depanneur.x, cc.y - depanneur.y) / 16);
        const piece = dedans(L, o, 'casse_croute', 'sergent');
        const avantB = etape(L);
        action(L, o);
        const bouchard = { piece: piece, avant: avantB, boite: boite(L), pendantBoite: etape(L) };
        fermer(L); o.frame(2);
        bouchard.apres = etape(L); bouchard.ligne = L.Histoire.ligneObjectif();
        sortir(L, o);
        const t2 = L.Histoire.donneur('tipaul');
        j.x = t2.x - 16; j.y = t2.y; L.Entites.indexer();
        finir(L, o);
        return { debut: debut, etapeNuit: etapeNuit, arrivent: arrivent, pendant: pendant, frere: frere,
                 police: police, seme: seme, versBouchard: versBouchard, loin: loin, bouchard: bouchard,
                 fait: !!B.partie.missionsFaites.e01, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"] == {"parle": True, "slug": "e01"}
    assert r["etapeNuit"] == 1 and len(r["arrivent"]) == 3, "la nuit : trois Chevreuils"
    for h in r["arrivent"]:
        assert 100 <= h["d"] <= 260, f"ils arrivent de loin ({h['d']} px)"
        assert h["etat"] == "attaque_joueur"
        assert h["arme"] is None and h["vie"] == 60, "les poings nus, 60 PV : des ados"
    assert r["pendant"] and r["pendant"]["slug"] == "tipaul-e01-9", "Ti-Paul les voit venir"
    f = r["frere"]
    assert f["etape"] == 2 and f["ligne"].startswith("LEUR GRAND FRÈRE"), f
    assert f["fiche"] and f["fiche"]["vie"] == 160 and f["fiche"]["arme"] == "batte", "le grand frère a un bâton"
    assert f["d"] is not None and f["d"] < 200, "il sort près de nous"
    assert f["boite"] and f["boite"]["slug"] == "tipaul-e01-10"
    p = r["police"]
    assert p["etape"] == 3 and p["ligne"].startswith("SÈME LA POLICE") and p["etoiles"] >= 1, p
    assert p["boite"] and p["boite"]["slug"] == "tipaul-e01-11"
    s = r["seme"]
    assert s["cache"] == 3 and s["apres"] == 4 and 0 < s["secondes"] < 150, f"cachés au dépanneur, l'étoile tombe : {s}"
    assert r["versBouchard"]["ligne"].startswith("DEMANDE UNE PATROUILLE À BOUCHARD")
    assert r["versBouchard"]["boite"] and r["versBouchard"]["boite"]["slug"] == "tipaul-e01-12"
    assert r["loin"] >= 100, f"le casse-croûte est loin du dépanneur ({r['loin']} tuiles)"
    b = r["bouchard"]
    assert b["piece"] == "casse_croute" and b["avant"] == 4
    assert b["boite"] == {"partie": "accueil", "qui": "bouchard", "slug": "bouchard-e01-13", "telephone": False}, b
    assert b["pendantBoite"] == 4 and b["apres"] == 5 and b["ligne"].startswith("RETOURNE VOIR TI-PAUL")
    assert r["fait"] is True and r["argent"] == [150]


def test_q02_le_camion_de_poisson_la_glace_de_ti_paul_le_sergent_paie_et_lulu_encaisse(banc):
    """Lulu : le camion dort dans une ruelle des Quais dès le début (l'intro le filme), on le prend.

    « Des missions plus longues » (22 sept. 2026) : détour aux Érables — on descend chez Ti-Paul pour la
    glace (sa poignée de main se dit), on remonte dans LE MÊME camion ; on livre au casse-croûte ; le
    sergent paie en personne (dedans) ; on rapporte l'argent à la cantine. Sans bosse, la mission paie la
    moitié en plus ; avec une bosse, non — la prime se décide à la livraison et tient jusqu'à la fin."""
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
        // Aux Érables : le camion garé dans la rue, on descend, on va serrer la main de Ti-Paul. ⚠️ Pas
        // collé à lui : à 36 px, ACTION remonte dans le camion au lieu de lui parler (le char passe
        // avant le personnage dans la chaîne d'ACTION) — on se gare à quatre tuiles et on marche.
        const ti = L.Histoire.donneur('tipaul');
        const loin = Math.round(Math.hypot(ti.x - cantine.x, ti.y - cantine.y) / 16);
        const rue = L.Histoire.tuileDeRue(ti.x, ti.y, 12, function (q) { return Math.hypot(q.x - ti.x, q.y - ti.y) >= 64; });
        v.x = rue.x; v.y = rue.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); o.frame(1);
        L.Vehicules.descendre(j); L.Entites.indexer(); o.frame(2);
        const avantGlace = etape(L);
        serrerLaMain(L, o, 'tipaul');
        const glace = { avant: avantGlace, boite: boite(L), pendantBoite: etape(L), dansLeCamion: j.dansVehicule === v };
        fermer(L); o.frame(2);
        glace.apres = etape(L); glace.ligne = L.Histoire.ligneObjectif(); glace.suite = boite(L);
        fermer(L);
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer(); o.frame(2);
        BOSSE
        const l = L.Histoire.lieuDeLivraison('casse_croute');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        o.frame(3);
        const livre = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L), aPied: !j.dansVehicule };
        fermer(L);
        // Le sergent, dedans : il paie, pour une fois.
        const piece = dedans(L, o, 'casse_croute', 'sergent');
        const avantS = etape(L);
        action(L, o);
        const sergent = { piece: piece, avant: avantS, boite: boite(L), pendantBoite: etape(L) };
        fermer(L); o.frame(2);
        sergent.apres = etape(L); sergent.ligne = L.Histoire.ligneObjectif(); sergent.suite = boite(L);
        fermer(L);
        sortir(L, o);
        const argentAvant = argent.length;
        const c = L.Histoire.lieu('cantine');
        j.x = c.x; j.y = c.y; L.Entites.indexer();
        finir(L, o);
        return { camion: camion, etape: etapeCourante, ligne: ligne, pendant: pendant, loin: loin, glace: glace,
                 livre: livre, sergent: sergent, argentAvant: argentAvant, fait: !!B.partie.missionsFaites.q02,
                 argent: argent.map(function (a) { return a.montant; }) };
    }"""
    propre = banc("function (L, o) {" + OUTILS + JEU.replace("BOSSE", ""))
    cabosse = banc("function (L, o) {" + OUTILS + JEU.replace("BOSSE", "v.chocs = (v.chocs || 0) + 1;"))
    c = propre["camion"]
    assert c and c["slug"] == "camion" and c["etat"] == "stationne", "le camion de poisson dort là avant qu'on en parle"
    assert c["d"] >= 100, f"il faut le chercher, pas le trouver à la porte ({c['d']} px de la cantine)"
    assert propre["etape"] == 1 and propre["ligne"].startswith("ARRÊTE CHERCHER DE LA GLACE"), "monté, on va chercher la glace"
    assert propre["pendant"] == {"partie": "pendant", "qui": "lulu", "slug": "lulu-q02-8", "telephone": True}, \
        "Lulu le dit au combiné : elle est à sa cantine"
    assert propre["loin"] >= 100, f"le dépanneur est à l'autre bout de la ville ({propre['loin']} tuiles de la cantine)"
    g = propre["glace"]
    assert g["avant"] == 1 and not g["dansLeCamion"]
    assert g["boite"] == {"partie": "accueil", "qui": "tipaul", "slug": "tipaul-q02-12", "telephone": False}, g
    assert g["pendantBoite"] == 1 and g["apres"] == 2 and g["ligne"].startswith("LIVRE LE POISSON"), g
    assert g["suite"] and g["suite"]["slug"] == "lulu-q02-9", "Lulu : doucement dans les tournants"
    lv = propre["livre"]
    assert lv["etape"] == 3 and lv["ligne"].startswith("FAIS PAYER LE SERGENT") and lv["aPied"], lv
    assert lv["boite"] and lv["boite"]["slug"] == "lulu-q02-10"
    s = propre["sergent"]
    assert s["piece"] == "casse_croute" and s["avant"] == 3
    assert s["boite"] == {"partie": "accueil", "qui": "bouchard", "slug": "bouchard-q02-13", "telephone": False}, s
    assert s["pendantBoite"] == 3 and s["apres"] == 4 and s["ligne"].startswith("RAPPORTE L'ARGENT À LULU"), s
    assert s["suite"] and s["suite"]["slug"] == "lulu-q02-11"
    assert propre["argentAvant"] == 0, "rien n'est payé avant d'avoir rapporté l'argent à Lulu"
    assert propre["fait"] is True and propre["argent"] == [375], "250 $ et la prime sans bosse (+50 %)"
    assert cabosse["fait"] is True and cabosse["argent"] == [250], "une bosse, et la prime s'en va"


def test_s03_les_gardiens_le_camion_de_paie_deux_etoiles_le_bar_tenu_puis_josee(banc):
    """Raymonde : le camion de paie dort près de l'hôtel ; le prendre met la police (2★) aux fesses, on la
    sème, on livre au bar de Josée (l'usine ferme la nuit, un lieu de mission ne peut pas l'être) : 450 $ —
    sans prime de bosse, la mission n'en demande pas.

    « Des missions plus longues » (22 sept. 2026) : deux Boulonneux gardent le camion — ils sortent de
    l'hôtel quand on monte, arrivent de loin sur nous, on les couche ; la paie livrée, Prévost en envoie trois autres au bar — ils arrivent de
    loin ; puis Josée reçoit la paie en personne (dedans), et sa poignée de main se dit.

    ⚠️ Ici l'étape « sème la police » est remise à zéro à la main : on ne se cache pas dans une pièce avec
    un camion. C'est le juge d'en dessous qui la JOUE, camion à fond, un agent derrière."""
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
        // Les gardiens sortent : ils arrivent de loin, sur nous.
        const gardes = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L), dans: j.dansVehicule === v,
                         hommes: hommes(L, 1).map(function (h) { return { d: h.d, etat: h.e.etat }; }) };
        fermer(L);
        hommes(L, 1).forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const etapeSemer = etape(L), etoiles = B.recherche.etoiles;
        const pendant = boite(L);
        fermer(L);
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        o.frame(3);
        const etapeLivrer = etape(L), ligne = L.Histoire.ligneObjectif();
        const l = L.Histoire.lieuDeLivraison('bar');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        o.frame(3);
        // Prévost envoie ses Boulonneux : ils arrivent de loin sur nous.
        const renforts = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L), aPied: !j.dansVehicule,
                           hommes: hommes(L, 4).map(function (h) { return { d: h.d, etat: h.e.etat }; }) };
        fermer(L);
        hommes(L, 4).forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const versJosee = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const piece = dedans(L, o, 'bar', 'contact');
        const avantJ = etape(L), paye = argent.length;
        action(L, o);
        const josee = { piece: piece, avant: avantJ, boite: boite(L), pendantBoite: etape(L), paye: paye };
        finir(L, o);
        return { camion: camion, etoiles0: etoiles0, gardes: gardes,
                 etapeSemer: etapeSemer, etoiles: etoiles, pendant: pendant,
                 etapeLivrer: etapeLivrer, ligne: ligne, renforts: renforts, versJosee: versJosee, josee: josee,
                 fait: !!B.partie.missionsFaites.s03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["camion"] and r["camion"]["slug"] == "camion" and r["camion"]["d"] >= 100, r["camion"]
    assert r["etoiles0"] == 0, "la police ne sait rien tant qu'on n'a pas pris le camion"
    g = r["gardes"]
    assert g["etape"] == 1 and g["ligne"].startswith("LES GARDIENS DE PRÉVOST") and g["dans"], g
    assert g["boite"] and g["boite"]["slug"] == "raymonde-s03-9" and g["boite"]["telephone"] is True
    assert len(g["hommes"]) == 2, g["hommes"]
    for h in g["hommes"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"les gardiens arrivent sur nous : {h}"
    assert r["etapeSemer"] == 2 and r["etoiles"] >= 2, "monté dans le camion de paie : deux étoiles"
    assert r["pendant"] == {"partie": "pendant", "qui": "raymonde", "slug": "raymonde-s03-10", "telephone": True}
    assert r["etapeLivrer"] == 3 and r["ligne"].startswith("LIVRE LA PAIE AU BAR"), "semée, on livre"
    rf = r["renforts"]
    assert rf["etape"] == 4 and rf["ligne"].startswith("PRÉVOST ENVOIE SES BOULONNEUX") and rf["aPied"], rf
    assert rf["boite"] and rf["boite"]["slug"] == "raymonde-s03-11"
    assert len(rf["hommes"]) == 3, rf["hommes"]
    for h in rf["hommes"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous : {h}"
    assert r["versJosee"]["etape"] == 5 and r["versJosee"]["ligne"].startswith("REMETS LA PAIE À JOSÉE")
    j = r["josee"]
    assert j["piece"] == "bar" and j["avant"] == 5 and j["paye"] == 0, j
    assert j["boite"] == {"partie": "accueil", "qui": "josee", "slug": "josee-s03-12", "telephone": False}, j
    assert j["pendantBoite"] == 5
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
        // Les deux gardiens (22 sept. 2026) : couchés, la police arrive.
        B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === 1; })
          .forEach(function (e) { L.Entites.assommer(e); });
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
    assert r["debut"] == {"etape": 2, "etoiles": 2}, r["debut"]
    assert r["route"]["l"] >= 200, f"pas de ligne droite assez longue pour juger : {r['route']}"
    assert r["dans"], "on est sorti du camion en route"
    assert r["pointe"] >= 0.95 * r["fiche"], f"le camion plafonne sous sa fiche : {r}"
    assert r["perdu"] is not None, f"l'agent à pied ne lâche pas le camion : {r}"
    assert r["tombe"] is not None, f"les deux étoiles ne tombent jamais : {r}"
    assert r["etape"] == 2 and r["etoiles"] == 1, r


def test_m51_la_tournee_du_sergent_trois_enveloppes_un_agent_honnete_josee_puis_le_casse_croute(banc):
    """Bouchard : Thibodeau, Lulu et Ti-Paul disent chacun leur mot en personne (leur voix demandée), et
    l'objectif n'avance qu'une fois la boîte fermée.

    « Des missions plus longues » (22 sept. 2026) : un agent honnête a vu l'enveloppe de Ti-Paul — une
    étoile, qu'on laisse tomber caché au dépanneur (DEHORS : elle se pose quand on sort de chez Ti-Paul) ;
    Josée, au bar, refuse en personne ; puis on rapporte les enveloppes au casse-croûte."""
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
            if (slug === 'tipaul') serrerLaMain(L, o, 'tipaul'); else L.Histoire.parler(slug);
            const b = boite(L), pendantBoite = etape(L);
            fermer(L);
            vus.push({ avant: avant, pendant: pendantBoite, apres: etape(L), boite: b });
        }
        const voix = L.Son.Voix.demandees.slice(d0);
        o.frame(2);
        const agent = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles, boite: boite(L) };
        fermer(L);
        const seme = semerDedans(L, o, 'depanneur');
        const versJosee = { ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const piece = dedans(L, o, 'bar', 'contact');
        const avantJ = etape(L);
        action(L, o);
        const josee = { piece: piece, avant: avantJ, boite: boite(L), pendantBoite: etape(L) };
        fermer(L); o.frame(2);
        josee.apres = etape(L); josee.ligne = L.Histoire.ligneObjectif(); josee.suite = boite(L);
        fermer(L);
        sortir(L, o);
        const l = L.Histoire.lieu('casse_croute');
        j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { vus: vus, voix: voix, agent: agent, seme: seme, versJosee: versJosee, josee: josee,
                 fait: !!B.partie.missionsFaites.m51, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    attendus = [("thibodeau", "thibodeau-m51-11"), ("lulu", "lulu-m51-12"), ("tipaul", "tipaul-m51-13")]
    assert len(r["vus"]) == 3
    for i, (v, (qui, slug)) in enumerate(zip(r["vus"], attendus)):
        assert v["boite"] == {"partie": "accueil", "qui": qui, "slug": slug, "telephone": False}, (i, v["boite"])
        assert v["avant"] == i and v["pendant"] == i, f"contact {i} : l'objectif avance PENDANT sa réplique"
        assert v["apres"] == i + 1, f"contact {i} : l'objectif n'avance pas après sa réplique ({v['apres']})"
    assert [s for s in r["voix"] if "-m51-" in s][:3] == [s for _, s in attendus], "chacun demande sa voix"
    a = r["agent"]
    assert a["etape"] == 3 and a["ligne"].startswith("UN AGENT HONNÊTE") and a["etoiles"] >= 1, a
    assert a["boite"] and a["boite"]["slug"] == "bouchard-m51-9" and a["boite"]["telephone"] is True, a
    s = r["seme"]
    assert s["cache"] == 3 and s["apres"] == 4 and 0 < s["secondes"] < 150, f"caché au dépanneur, l'étoile tombe : {s}"
    assert r["versJosee"]["ligne"].startswith("PASSE SALUER JOSÉE")
    assert r["versJosee"]["boite"] and r["versJosee"]["boite"]["slug"] == "bouchard-m51-10"
    j = r["josee"]
    assert j["piece"] == "bar" and j["avant"] == 4
    assert j["boite"] == {"partie": "accueil", "qui": "josee", "slug": "josee-m51-14", "telephone": False}, j
    assert j["pendantBoite"] == 4 and j["apres"] == 5 and j["ligne"].startswith("RAPPORTE LES ENVELOPPES")
    assert j["suite"] and j["suite"]["slug"] == "bouchard-m51-8", "trois enveloppes? rapporte-les-moi"
    assert r["fait"] is True and r["argent"] == [350]
