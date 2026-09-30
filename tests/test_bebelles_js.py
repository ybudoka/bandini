"""Les bebelles (P4, des choses à collectionner, vague 3) au banc : on marche dessus, elle va sur l'étagère — la
prime, le son, le carnet, les paliers, la sauvegarde, les blocs, l'étagère de la planque et les triches.
"""

AMENER = """
    function amener(L, o, slug) {
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        const b = L.Collections.bebelle(slug);
        const p = L.Collections.pixels(b);
        const j = L.B.joueur;
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
        j.x = p.x + 60; j.y = p.y; L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        return { b: b, p: p, j: j };
    }
    function dessus(L, o, a, n) {
        for (let i = 0; i < (n || 2); i++) { a.j.x = a.p.x; a.j.y = a.p.y; a.j.vx = 0; a.j.vy = 0; o.frame(1); }
    }
"""


def test_marcher_sur_une_bebelle_la_pose_sur_l_etagere(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'chat_salue');
        let son = 0; const avant = L.Son.SFX.bebelle; L.Son.SFX.bebelle = function () { son++; };
        const argent = L.B.partie.argent;
        const loin = L.Collections.bebelleTrouvee('chat_salue');
        dessus(L, o, a, 3);
        L.Son.SFX.bebelle = avant;
        const journal = L.B.partie.carnet[L.B.partie.carnet.length - 1];
        return { loin: loin, etagere: L.B.partie.collections.bebelles.chat_salue || null, gain: L.B.partie.argent - argent,
                 son: son, msg: L.B.msg, journal: journal && journal.t, restantes: L.Collections.bebellesATrouver().length,
                 bilan: L.Hud.menuBilan().items.filter(function (i) { return i.libelle === 'BEBELLES'; })[0].detail,
                 carnet: L.Hud.menuCarnet().items.filter(function (i) { return i.cle === 'bebelles'; })[0].detail };
    }""")
    assert r["loin"] is False, "la bebelle se ramasse sans qu'on marche dessus"
    assert r["etagere"] and r["etagere"]["source"] == "rue", r
    assert r["gain"] == 100, "une bebelle paie 100 $, une fois"
    assert r["son"] == 1
    assert r["msg"].startswith("BEBELLE 1/12 — LE CHAT QUI SALUE"), r["msg"]
    assert r["journal"] == "BEBELLE : LE CHAT QUI SALUE — SUR L’ÉTAGÈRE DE LA PLANQUE", r["journal"]
    assert r["restantes"] == 9, "dans la ville, on voit les dix de la ville (moins celle-ci), pas celles des blocs"
    assert r["bilan"] == "1 / 12" and r["carnet"] == "1 / 12"


def test_les_paliers_paient_et_jouent_le_reel(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'flamant');
        const autres = L.Collections.bebelles().map(function (b) { return b.slug; }).filter(function (s) { return s !== 'flamant'; });
        autres.slice(0, 5).forEach(function (s) { L.Collections.donnerBebelle(s, 'debug', true); });
        let reel = 0; const avant = L.Son.SFX.reel_bebelles; L.Son.SFX.reel_bebelles = function () { reel++; };
        const argent = L.B.partie.argent;
        L.Collections.donnerBebelle(autres[5], 'rue');                  // la sixième
        const six = { gain: L.B.partie.argent - argent, reel: reel };
        autres.slice(6, 11).forEach(function (s) { L.Collections.donnerBebelle(s, 'debug', true); });
        const avantDerniere = L.B.partie.argent;
        dessus(L, o, a, 3);                                               // la douzième, par terre
        L.Son.SFX.reel_bebelles = avant;
        return { six: six, douze: L.B.partie.argent - avantDerniere, reel: reel, n: L.Collections.nombreBebelles() };
    }""")
    assert r["six"] == {"gain": 100 + 500, "reel": 1}, r
    assert r["n"] == 12 and r["douze"] == 100 + 2500 and r["reel"] == 2, r


def test_celles_des_blocs_ne_se_voient_que_dans_leur_bloc(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ville = L.Collections.bebellesATrouver().map(function (b) { return b.slug; });
        const vrai = L.B.bloc;
        L.B.bloc = { slug: 'rang' };
        const rang = L.Collections.bebellesATrouver().map(function (b) { return b.slug; });
        L.B.bloc = { slug: 'cineparc' };
        const cine = L.Collections.bebellesATrouver().map(function (b) { return b.slug; });
        L.B.bloc = vrai;
        L.B.interieur = { bidon: true };
        const piece = L.Collections.bebellesATrouver().length;
        L.B.interieur = null;
        return { ville: ville, rang: rang, cine: cine, piece: piece };
    }""")
    assert "raquette" not in r["ville"] and "lunettes_3d" not in r["ville"] and len(r["ville"]) == 10, r
    assert r["rang"] == ["raquette"] and r["cine"] == ["lunettes_3d"], r
    assert r["piece"] == 0


def test_l_etagere_arrive_a_la_premiere_et_porte_ce_qu_on_a_trouve(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        function entrer() {
            const porte = L.Monde.carte.def.portes.find(function (p) { return p.interieur === 'planque'; });
            const j = L.B.joueur; j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
            L.Jeu.chargerPiece(porte);
            const e = L.B.entites.filter(function (q) { return q.decor === 'etagere_bebelles'; });
            L.Jeu.revenirEnVille();
            return e.map(function (q) { return { v: q.v, x: q.x, solide: q.solide, horsSuite: q.id >= 1e9 }; });
        }
        const vide = entrer();
        L.Collections.donnerBebelle('bouteille', 'debug', true);    // la 1re du catalogue
        L.Collections.donnerBebelle('flamant', 'debug', true);      // la 10e
        const deux = entrer();
        const rangs = [L.Collections.rangBebelle('bouteille'), L.Collections.rangBebelle('flamant')];
        return { vide: vide, deux: deux, rangs: rangs };
    }""")
    assert r["vide"] == [], "l'étagère est là sans une bebelle"
    assert len(r["deux"]) == 1 and r["deux"][0]["solide"] and r["deux"][0]["horsSuite"], r
    assert r["rangs"] == [0, 9]
    assert r["deux"][0]["v"] == (1 << 0) | (1 << 9), "l'étagère ne porte pas les bebelles trouvées"
    # Deux tuiles : posée au milieu de (4,6) et (5,6), soit x = 5 × 16.
    assert r["deux"][0]["x"] == 80, r


def test_l_etagere_peint_chaque_bebelle_trouvee_et_rien_d_autre(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.DECORS.etagere_bebelles;
        function compte(v) { let n = 0; const ctx = { fillRect: function () { n++; }, set fillStyle(x) {} }; d.peindre(ctx, d.w, d.h, v); return n; }
        const vide = compte(0);
        const b0 = L.Collections.bebelles()[0], b3 = L.Collections.bebelles()[3];
        const pixels = function (b) { return b.grille.join('').split('').filter(function (c) { return c !== '.'; }).length; };
        return { une: compte(1) - vide, deux: compte(1 | 8) - vide, attendu1: pixels(b0), attendu2: pixels(b0) + pixels(b3) };
    }""")
    assert r["une"] == r["attendu1"] and r["deux"] == r["attendu2"], r


def test_l_etagere_survit_a_la_sauvegarde(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'tuque_marsouins');
        dessus(L, o, a, 3);
        L.Missions.sauvegarderPartie();
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.Sauvegarde.lire(L.Sauvegarde.emplacement()))), L.B.defs);
        const abimee = L.Sauvegarde.completer({ argent: 1, collections: { cartes: {}, bebelles: [1] } }, L.B.defs);
        return { relue: relue.collections.bebelles, abimee: abimee.collections.bebelles };
    }""")
    assert r["relue"]["tuque_marsouins"]["source"] == "rue", r
    assert r["abimee"] == {}


def test_le_carnet_dit_le_lieu_de_celles_qui_manquent(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Collections.donnerBebelle('raquette', 'debug', true);
        const m = L.Hud.menuCarnetBebelles();
        const f = L.Hud.menuCarnetBebelle('raquette');
        return { lignes: m.items.map(function (i) { return i.libelle + '|' + (i.detail || ''); }), sur: m.sur,
                 fiche: f.items.map(function (i) { return i.libelle + '|' + (i.detail || ''); }), titre: f.titre };
    }""")
    assert r["sur"] == "1 / 12"
    assert "???|L’ÎLE-AUX-CORNEILLES" in r["lignes"] and "???|LE CINÉ-PARC BELVÉDÈRE" in r["lignes"], r["lignes"]
    assert "LA RAQUETTE EN BABICHE|" in r["lignes"] and sum(1 for x in r["lignes"] if x.startswith("???")) == 11
    assert r["titre"] == "LA RAQUETTE EN BABICHE"
    assert any(x.startswith("TROUVÉE|JOUR") and x.endswith("· LE RANG") for x in r["fiche"]), r["fiche"]


def test_les_triches_vont_voir_une_bebelle_et_remplissent_l_etagere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const page = L.Hud.menuDebugCollections();
        const ligne = page.items.filter(function (i) { return i.bebelle === 'lanterne'; })[0];
        const rendu = ligne.faire(ligne);
        const j = L.B.joueur, b = L.Collections.bebelle('lanterne');
        const tuiles = Math.max(Math.abs(Math.floor(j.x / 16) - b.x), Math.abs(Math.floor(j.y / 16) - b.y));
        o.frame(3);
        const apres = L.Collections.bebelleTrouvee('lanterne');
        const argent = L.B.partie.argent;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const toutes = L.B.menu.items.filter(function (i) { return i.libelle === 'TOUTES LES BEBELLES'; })[0];
        toutes.faire(toutes);
        return { bebelles: page.items.filter(function (i) { return i.bebelle; }).length, rendu: rendu, tuiles: tuiles,
                 apres: apres, n: L.Collections.nombreBebelles(), gain: L.B.partie.argent - argent };
    }""")
    assert r["bebelles"] == 12
    assert r["rendu"] is True and 2 <= r["tuiles"] <= 5, r
    assert r["apres"] is False, "le saut de debug ramasse la bebelle"
    assert r["n"] == 12 and r["gain"] == 0, "TOUTES LES BEBELLES paie (ou n'en donne pas toutes)"


def test_l_hiver_la_bebelle_est_cernee(banc):
    """Le bonhomme blanc sur la neige : l'hiver, sa silhouette se peint d'abord en sombre, décalée d'un pixel dans
    les quatre sens ; l'été, non."""
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'bonhomme');
        a.j.x = a.p.x + 40;
        const b = a.b, n = b.grille.join('').split('').filter(function (c) { return c !== '.'; }).length;
        function peindre(jour) {
            L.B.partie.jour = jour; L.B.partie.heure = 0.55; L.B.t = 100;
            const vus = []; let style = null;
            const ctx = { fillRect: function () { vus.push(style); }, set fillStyle(v) { style = v; },
                          save: function () {}, restore: function () {}, translate: function () {}, rotate: function () {} };
            L.Collections.dessiner(ctx, { x: a.p.x - 240, y: a.p.y - 135 });
            return vus.filter(function (c) { return c === '#3a3442'; }).length;
        }
        return { hiver: peindre(5), ete: peindre(20), n: n };
    }""")
    assert r["hiver"] >= 4 * r["n"], r
    assert r["ete"] == 0, r
