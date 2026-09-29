"""La planque qu'on décore (P4, des choses à collectionner, vague 2) au banc : le catalogue sur la table, la
livraison du lendemain, les trophées de l'album, le juke-box — et une planque vide qui ne crée rien.
"""

ENTRER = """
    function entrer(L, o) {
        // ⚠️ Sans `commencer` : le juge commence sa partie lui-même, une fois (sinon la ville renaît entre deux).
        if (L.B.menu) L.Hud.fermerMenu();
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.interieur === 'planque'; });
        const j = L.B.joueur;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        const piece = L.Jeu.chargerPiece(porte);
        j.x = piece.interieur.apparition.x * 16 + 8; j.y = piece.interieur.apparition.y * 16 + 8;
        return { porte: porte, piece: piece, j: j };
    }
    function ressortir(L) { L.Jeu.revenirEnVille(); }
    function deLaPlanque(L) { return L.B.entites.filter(function (e) { return e.deLaPlanque; }); }
"""


def test_une_planque_vide_ne_cree_rien(banc):
    r = banc("function (L, o) {" + ENTRER + """
        L.Jeu.commencer();
        const avant = L.Entites.creer('bidon', 0, 0, {}).id;
        const a = entrer(L, o);
        const apres = L.Entites.creer('bidon', 0, 0, {}).id;
        return { objets: deLaPlanque(L).length, ids: apres - avant, points: a.piece.interieur.points.map(function (p) { return p.type; }) };
    }""")
    assert r["objets"] == 0
    assert r["ids"] == 1, "entrer dans une planque vide a pris des numéros à la suite de la ville"
    assert "catalogue" in r["points"] and "jukebox" not in r["points"]


def test_le_catalogue_vend_et_le_meuble_arrive_le_lendemain(banc):
    r = banc("function (L, o) {" + ENTRER + """
        L.Jeu.commencer();
        let a = entrer(L, o);
        const p = L.B.partie;
        p.argent = 2000;
        const menu = L.Decoration.menuCatalogue();
        const ligne = menu.items.find(function (i) { return i.libelle === 'LE JUKE-BOX'; });
        ligne.faire(ligne);
        const apres = L.Decoration.menuCatalogue().items.find(function (i) { return i.libelle === 'LE JUKE-BOX'; });
        const jour = p.jour;
        const aujourdhui = L.Decoration.presents('planque');
        // Deux fois ? Non : déjà commandé.
        const deux = L.Decoration.commander('jukebox');
        ressortir(L);
        p.jour += 1;
        let msg = null; const vrai = L.Hud.message; L.Hud.message = function (t) { msg = msg || t; };
        L.Decoration.nouveauJour();
        L.Hud.message = vrai;
        a = entrer(L, o);
        const objets = deLaPlanque(L);
        const pts = a.piece.interieur.points.filter(function (q) { return q.type === 'jukebox'; });
        return { argent: p.argent, detail: apres.detail, commande: p.meubles.planque.jukebox, jour: jour, aujourdhui: aujourdhui,
                 deux: deux, msg: msg, objets: objets.map(function (e) { return [e.decor, e.id >= 1e9, e.solide]; }),
                 point: pts.length, aide: menu.aide, titre: menu.titre };
    }""")
    assert r["titre"] == "LE CATALOGUE BEAUSOLEIL"
    assert r["aide"], "la ligne du catalogue ne se lit pas sous le meuble"
    assert r["argent"] == 500 and r["commande"] == {"jour": r["jour"]}
    assert r["detail"] == "LIVRÉ DEMAIN" and r["aujourdhui"] == [] and r["deux"] is False
    assert r["msg"] == "LIVRAISON À LA PLANQUE : LE JUKE-BOX", r["msg"]
    assert r["objets"] == [["jukebox", True, True]], "le juke-box livré n'est pas là, à part et solide"
    assert r["point"] == 1, "le juke-box ne se touche pas"


def test_les_trophees_suivent_l_album(banc):
    r = banc("function (L, o) {" + ENTRER + """
        L.Jeu.commencer();
        for (let n = 1; n <= 10; n++) L.Collections.donner(n, 'debug', true);
        const dix = L.Decoration.presents('planque');
        for (let n = 11; n <= 25; n++) L.Collections.donner(n, 'debug', true);
        const vingtCinq = L.Decoration.presents('planque');
        L.Collections.toutes();
        const a = entrer(L, o);
        return { dix: dix, vingtCinq: vingtCinq, tout: deLaPlanque(L).map(function (e) { return e.decor; }),
                 chalet: L.Decoration.presents('chalet') };
    }""")
    assert r["dix"] == ["cadre_dix"]
    assert r["vingtCinq"] == ["cadre_dix", "cadre_vingt_cinq"]
    assert r["tout"] == ["cadre_dix", "cadre_vingt_cinq", "coupe_album"]
    assert r["chalet"] == ["cadre_dix", "cadre_vingt_cinq", "coupe_album"], "le chalet n'a pas ses trophées"


def test_le_juke_box_joue_la_radio_et_se_tait_dehors(banc):
    r = banc("function (L, o) {" + ENTRER + """
        L.Jeu.commencer();
        L.B.partie.meubles = { planque: { jukebox: { jour: L.B.partie.jour - 1 } } };
        entrer(L, o);
        const appels = [];
        const suivante = L.Son.Radio.suivante, arreter = L.Son.Radio.arreter;
        L.Son.Radio.suivante = function () { appels.push('suivante'); return (L.Son.Radio.stations()[0] || {}).slug || 'x'; };
        L.Son.Radio.arreter = function () { appels.push('arreter'); };
        L.Decoration.jukebox();
        const msg = L.B.msg;
        o.frame(1);
        const dedans = appels.slice();
        ressortir(L); L.B.interieur = null;
        L.Decoration.maj();
        L.Son.Radio.suivante = suivante; L.Son.Radio.arreter = arreter;
        return { dedans: dedans, apres: appels, msg: msg };
    }""")
    assert r["dedans"] == ["suivante"], r
    assert r["msg"].startswith("JUKE-BOX : "), r["msg"]
    assert r["apres"][-1] == "arreter", "le juke-box joue encore dehors"


def test_les_meubles_survivent_a_la_sauvegarde(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.meubles = { planque: { sofa: { jour: 3 } }, chalet: { tapis_tresse: { jour: 4 } } };
        L.Missions.sauvegarderPartie();
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.Sauvegarde.lire(L.Sauvegarde.emplacement()))), L.B.defs);
        const vieille = L.Sauvegarde.completer({ argent: 1 }, L.B.defs);
        const abimee = L.Sauvegarde.completer({ argent: 1, meubles: { planque: { sofa: 'oui' }, chalet: [1] } }, L.B.defs);
        return { relue: relue.meubles, vieille: vieille.meubles, abimee: abimee.meubles };
    }""")
    assert r["relue"] == {"planque": {"sofa": {"jour": 3}}, "chalet": {"tapis_tresse": {"jour": 4}}}
    assert r["vieille"] == {} and r["abimee"] == {"planque": {}}


def test_chaque_objet_a_son_dessin_et_ce_qui_est_debout_est_solide(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Decoration.donnees();
        const noms = Object.keys(d.poses);
        return noms.map(function (n) { const f = L.DECORS[n]; return [n, d.poses[n], !!f, !!(f && f.solide), !!(f && f.peindre)]; });
    }""")
    for nom, pose, dessin, solide, peint in r:
        assert dessin and peint, f"{nom} n'a pas de dessin"
        assert solide == (pose == "sol"), f"{nom} : posé « {pose} » mais solide={solide}"


def test_le_lever_du_jour_annonce_la_livraison(banc):
    """⚠️ Par `Missions.nouveauJour`, le vrai chemin de la nuit — pas en appelant `Decoration` à la main."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.meubles = { planque: { aquarium: { jour: p.jour } } };
        const notes = p.carnet.length;
        p.jour += 1;
        L.Missions.nouveauJour();
        return { journal: p.carnet.slice(notes).map(function (e) { return e.t; }) };
    }""")
    assert "LIVRÉ À LA PLANQUE : L’AQUARIUM" in r["journal"], r["journal"]
