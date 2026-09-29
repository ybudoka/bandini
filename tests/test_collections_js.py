"""Les cartes de hockey (P4, des choses à collectionner, vague 1) au banc : on marche dessus, elle entre dans
l'album — le compte, la prime, le son, le carnet, les paliers, la sauvegarde, et les triches.

⚠️ Chaque juge vide la rue autour de la carte avant de marcher dessus : un passant qui pousse le joueur ou un
char qui passe feraient juger autre chose que la carte.
"""

AMENER = """
    function amener(L, o, numero) {
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        const c = L.Collections.fiche(numero);
        const p = L.Collections.pixels(c);
        const j = L.B.joueur;
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
        j.x = p.x + 60; j.y = p.y; L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        return { c: c, p: p, j: j };
    }
    function surLaCarte(L, o, a, n) {
        for (let i = 0; i < (n || 2); i++) { a.j.x = a.p.x; a.j.y = a.p.y; a.j.vx = 0; a.j.vy = 0; o.frame(1); }
    }
"""


def test_le_catalogue_arrive_a_part_et_chaque_carte_a_sa_place(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const cartes = L.Collections.cartes();
        return { etat: L.Collections.etatDeLaDemande(), total: L.Collections.total(), nombre: L.Collections.nombre(),
                 placees: cartes.filter(function (c) { return typeof c.x === 'number'; }).length,
                 dansLaCarte: 'collections' in L.B.defs.carte, dansLesDefs: 'collections' in L.B.defs };
    }""")
    assert r["etat"] == "arrive", r
    assert r["total"] == 40 and r["placees"] == 40 and r["nombre"] == 0, r
    assert r["dansLaCarte"] is False and r["dansLesDefs"] is False, "les collections pèsent sur un paquet"


def test_marcher_sur_une_carte_la_met_dans_l_album(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 12);
        let son = 0; const avant = L.Son.SFX.carte_hockey; L.Son.SFX.carte_hockey = function () { son++; };
        const argent = L.B.partie.argent;
        const loin = L.Collections.trouvee(12);
        surLaCarte(L, o, a, 3);
        L.Son.SFX.carte_hockey = avant;
        const journal = L.B.partie.carnet[L.B.partie.carnet.length - 1];
        return { loin: loin, album: L.B.partie.collections.cartes[12] || null, gain: L.B.partie.argent - argent, son: son,
                 msg: L.B.msg, journal: journal && journal.t, restantes: L.Collections.aTrouver().length,
                 bilan: L.Hud.menuBilan().items.filter(function (i) { return i.libelle === 'CARTES DE HOCKEY'; })[0].detail };
    }""")
    assert r["loin"] is False, "la carte entre dans l'album sans qu'on marche dessus"
    assert r["album"] and r["album"]["source"] == "rue" and r["album"]["jour"] >= 1, r
    assert r["gain"] == 25, "une carte paie 25 $, une fois"
    assert r["son"] == 1, "la carte se ramasse sans son (ou deux fois)"
    assert r["msg"].startswith("CARTE 1/40 — GASTON OUELLET"), r["msg"]
    assert r["journal"] == "CARTE DE HOCKEY N° 12 : GASTON OUELLET", r["journal"]
    assert r["restantes"] == 39
    assert r["bilan"] == "1 / 40"


def test_ni_au_volant_ni_d_une_piece(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 1);
        const v = L.Vehicules.creer('auto', a.p.x, a.p.y, 0, { couleur: '#888888' });
        L.Vehicules.monter(a.j, v);
        for (let i = 0; i < 3; i++) { v.x = a.p.x; v.y = a.p.y; v.vx = 0; v.vy = 0; a.j.x = a.p.x; a.j.y = a.p.y; o.frame(1); }
        const auVolant = L.Collections.trouvee(1);
        L.Vehicules.descendre(a.j);
        v.x = a.p.x + 400;
        L.B.interieur = { bidon: true };
        const dansUnePiece = L.Collections.aTrouver().length;
        L.B.interieur = null;
        surLaCarte(L, o, a, 3);
        return { auVolant: auVolant, dansUnePiece: dansUnePiece, aPied: L.Collections.trouvee(1) };
    }""")
    assert r["auVolant"] is False, "une carte se ramasse au volant"
    assert r["dansUnePiece"] == 0, "une carte de la rue se voit dans une pièce"
    assert r["aPied"] is True


def test_les_paliers_paient_et_jouent_l_orgue(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 40);
        let orgue = 0; L.Son.SFX.orgue_arena = function () { orgue++; };
        const primes = []; const vraie = L.Hud.prime; L.Hud.prime = function (p) { primes.push(p.montant + ' ' + p.titre); };
        // Neuf cartes d'avance, données comme au marché aux puces : la dixième, ramassée, fait le palier.
        for (let n = 1; n <= 9; n++) L.Collections.donner(n, 'puces', true);
        const argent = L.B.partie.argent;
        surLaCarte(L, o, a, 3);
        const dixieme = { gain: L.B.partie.argent - argent, orgue: orgue, primes: primes.slice() };
        // Jusqu'à trente-neuf, puis la dernière : l'album complet. ⚠️ La n° 40 est celle qu'on vient de
        // ramasser (la dixième) : on la retire de l'album pour qu'elle soit la quarantième.
        for (let n = 10; n <= 39; n++) L.Collections.donner(n, 'debug', true);
        delete L.B.partie.collections.cartes[40];
        const avant = L.B.partie.argent;
        const donnee = L.Collections.donner(40, 'rue');
        const deuxFois = L.Collections.donner(40, 'rue');
        L.Hud.prime = vraie;
        return { dixieme: dixieme, derniere: L.B.partie.argent - avant, orgue: orgue, primes: primes, donnee: donnee, deuxFois: deuxFois,
                 jalon: L.B.partie.carnet.filter(function (e) { return e.jalon; }).map(function (e) { return e.t; }) };
    }""")
    assert r["dixieme"]["gain"] == 25 + 250, r["dixieme"]
    assert r["dixieme"]["orgue"] == 1 and r["dixieme"]["primes"] == ["250 10 CARTES DE HOCKEY"], r["dixieme"]
    assert r["donnee"] is True and r["deuxFois"] is False
    assert r["derniere"] == 25 + 1000, "l'album complet ne paie pas sa prime"
    assert r["orgue"] == 2 and r["primes"][-1] == "1000 L’ALBUM EST COMPLET", r
    assert "L’ALBUM DE LA LIGUE EST COMPLET — 1000 $" in r["jalon"], r["jalon"]


def test_l_album_survit_a_la_sauvegarde_et_une_vieille_partie_repart_vide(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 7);
        surLaCarte(L, o, a, 3);
        L.Missions.sauvegarderPartie();
        const n = L.Sauvegarde.emplacement();
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.Sauvegarde.lire(n))), L.B.defs);
        const vieille = L.Sauvegarde.completer({ argent: 10, jour: 3 }, L.B.defs);
        const abimee = L.Sauvegarde.completer({ argent: 10, collections: { cartes: [3, 4] } }, L.B.defs);
        const texte = L.Sauvegarde.completer({ argent: 10, collections: 'rien' }, L.B.defs);
        return { relue: relue.collections, vieille: vieille.collections, abimee: abimee.collections, texte: texte.collections };
    }""")
    assert r["relue"]["cartes"]["7"]["source"] == "rue", r["relue"]
    assert r["vieille"] == {"cartes": {}}
    assert r["abimee"] == {"cartes": {}} and r["texte"] == {"cartes": {}}


def test_le_carnet_range_l_album_par_equipe(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 23);
        surLaCarte(L, o, a, 3);
        const carnet = L.Hud.menuCarnet().items.filter(function (i) { return i.cle === 'collections'; })[0];
        const album = L.Hud.menuCarnetCollections();
        const entetes = album.items.filter(function (i) { return i.entete; }).map(function (i) { return i.entete; });
        const lignes = album.items.filter(function (i) { return !i.entete; }).map(function (i) { return i.libelle; });
        const carte = L.Hud.menuCarnetCarte(23);
        return { carnet: carnet && carnet.detail, entetes: entetes, lignes: lignes, titre: album.titre, sur: album.sur,
                 carte: carte.items.map(function (i) { return i.libelle + '|' + (i.detail || ''); }), titreCarte: carte.titre };
    }""")
    assert r["carnet"] == "CARTES 1 / 40"
    assert r["titre"] == "CARTES DE HOCKEY" and r["sur"] == "1 / 40"
    assert len(r["entetes"]) == 8 and "LES PHOQUES DE LA POINTE 1 / 5" in r["entetes"], r["entetes"]
    assert "LES CASTORS DU FAUBOURG 0 / 5" in r["entetes"]
    assert "N° 23  BRUNO GAUTHIER" in r["lignes"] and "N° 1  ???" in r["lignes"], r["lignes"][:8]
    assert sum(1 for x in r["lignes"] if x.endswith("???")) == 39
    assert r["titreCarte"] == "BRUNO GAUTHIER"
    assert "PETIT-FILS D’OMER GAUTHIER, L’INVENTEUR.|" in r["carte"] and "DÉFENSEUR|" in r["carte"], r["carte"]


def test_les_triches_vont_voir_une_carte_sans_la_ramasser_et_remplissent_l_album(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const debug = L.Hud.menuDebug();
        const aller = debug.items.filter(function (i) { return i.libelle === 'COLLECTIONS'; })[0];
        L.Hud.ouvrirMenu(debug);
        aller.faire(aller);
        const page = L.B.menu;
        const ligne = page.items.filter(function (i) { return i.carte === 33; })[0];
        const rendu = ligne.faire(ligne);
        const j = L.B.joueur, c = L.Collections.fiche(33), p = L.Collections.pixels(c);
        const tuiles = Math.max(Math.abs(Math.floor(j.x / 16) - c.x), Math.abs(Math.floor(j.y / 16) - c.y));
        o.frame(3);
        const apres = L.Collections.trouvee(33);
        const argent = L.B.partie.argent;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const toutes = L.B.menu.items.filter(function (i) { return i.libelle === 'TOUTES LES CARTES'; })[0];
        toutes.faire(toutes);
        return { titre: page.titre, premiere: page.items[0].libelle, lignes: page.items.length, rendu: rendu, tuiles: tuiles,
                 menu: !!L.B.menu && L.B.menu.titre, apres: apres, nombre: L.Collections.nombre(), gain: L.B.partie.argent - argent };
    }""")
    assert r["titre"] == "COLLECTIONS" and r["premiere"] == "LA PLUS PROCHE"
    assert r["lignes"] == 1 + 40 + 1, r
    assert r["rendu"] is True and 2 <= r["tuiles"] <= 5, r
    assert r["apres"] is False, "le saut de debug ramasse la carte"
    assert r["nombre"] == 40 and r["gain"] == 0, "TOUTES LES CARTES paie (ou n'en donne pas toutes)"


def test_une_demande_ratee_se_refait(banc):
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const avant = L.Collections.etatDeLaDemande(), total = L.Collections.total();
        L.B.t += 601;
        L.Collections.reclamer();
        await o.attendre(); await o.attendre();
        return { avant: avant, total: total, apres: L.Collections.etatDeLaDemande(), totalApres: L.Collections.total() };
    }""", collections_panne=1)
    assert r["avant"] == "ratee" and r["total"] == 0, r
    assert r["apres"] == "arrive" and r["totalApres"] == 40, r


def test_le_scintillement_est_bref_et_jamais_ensemble(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 12);
        a.j.x = a.p.x + 40;
        const periode = L.Collections.regle().scintille_s * 60;
        const vus = [];
        const ctx = { fillRect: function () { n++; }, set fillStyle(v) {} };
        let n = 0;
        for (let t = 0; t < periode; t++) {
            L.B.t = t; n = 0;
            L.Collections.dessiner(ctx, { x: a.p.x - 240, y: a.p.y - 135 });
            vus.push(n);
        }
        const base = Math.min.apply(null, vus);
        return { eclats: vus.filter(function (k) { return k > base; }).length, base: base, periode: periode };
    }""")
    assert r["base"] > 0, "la carte ne se peint pas"
    # 14 images d'éclat par carte à l'écran, sur trois secondes : discret.
    assert 0 < r["eclats"] <= 14 * 3, r


def test_les_sons_des_cartes_se_chargent_a_l_approche(banc):
    """⚠️ Pas au démarrage (le premier écran n'a plus de marge) : quand une carte qui manque est à moins d'un
    écran — `audio.LIEUX["collections"]`."""
    r = banc("function (L, o) {" + AMENER + """
        const lieux = []; const vrai = L.Son.Lieu.charger; L.Son.Lieu.charger = function (l) { lieux.push(l); };
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const c = L.Collections.fiche(36), p = L.Collections.pixels(c), j = L.B.joueur;
        j.x = p.x + 2000; j.y = p.y; L.Monde.centrerCamera(j.x, j.y);
        L.B.t = 29; o.frame(2);
        const loin = lieux.indexOf('collections') >= 0;
        j.x = p.x + 300; L.B.t = 59; o.frame(2);
        L.Son.Lieu.charger = vrai;
        const defs = L.B.defs.audio.echantillons.filter(function (e) { return e.slug === 'orgue_arena'; });
        return { loin: loin, pres: lieux.indexOf('collections') >= 0, declares: L.B.defs.audio.lieux.collections,
                 orgue: defs.length && defs[0].fichiers };
    }""")
    assert r["loin"] is False, "les sons des cartes se chargent loin de toute carte"
    assert r["pres"] is True, "à un écran d'une carte, ses sons ne se chargent pas"
    assert r["declares"] == ["carte_hockey", "orgue_arena"], "les sons des cartes n'ont pas rejoint le paquet"
    assert r["orgue"] == ["orgue_arena-1.mp3"], "l'orgue n'est pas déclaré une fois, avec son fichier"
