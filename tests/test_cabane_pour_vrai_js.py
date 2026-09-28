"""La cabane à sucre, pour vrai, au banc (docs/jalons/la-cabane-a-sucre-pour-vrai.md) : la calèche qu'on prend à
son arrêt et qui fait le tour de l'érablière, ses chevaux qui trottent, les gens de la cabane au temps des sucres
(et personne l'hiver), la vapeur de l'évaporateur, la tubulure, la table de tire qui lance le défi — sans un dé."""

OUTILS = """
  const TT = 16;
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  async function auRang(L, o, jour, heure) {
    const B = L.B, j = B.joueur, p = B.defs.blocs.find(function (b) { return b.slug === 'rang'; }).passage;
    B.partie.jour = jour; B.partie.heure = heure / 24;
    if (B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 1) * TT + 8; L.Entites.indexer();
    await laisserArriver(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 100; i++) o.frame(1);
    await laisserArriver(L, o);
    for (let i = 0; i < 20; i++) o.frame(1);
    if (B.menu) L.Hud.fermerMenu();
  }
  function poser(L, x, y) { const j = L.B.joueur; j.x = x; j.y = y; j.vx = 0; j.vy = 0; L.Entites.indexer(); }
"""


def test_on_monte_dans_la_caleche_elle_fait_le_tour_et_nous_redepose(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        await auRang(L, o, 12, 13);
        const c0 = C.caleche();
        // Derrière la calèche arrêtée (elle regarde l'ouest) : l'invite, puis ACTION.
        poser(L, c0.x + C.CAISSE.l + 10, c0.y);
        o.frame(1);
        const invite = B.invite;
        o.tape('KeyE', 1);
        const aBord = !!(B.joueur.manege && B.joueur.manege.quoi === 'caleche');
        let yMax = 0, xMin = 1e9, k = 0, bouge = false;
        for (; k < 2600 && B.joueur.manege; k++) {
            o.frame(1);
            yMax = Math.max(yMax, B.joueur.y); xMin = Math.min(xMin, B.joueur.x);
            if (C.caleche().roule) bouge = true;
        }
        const j = B.joueur;
        return { invite: invite, aBord: aBord, images: k, yMax: yMax, xMin: xMin, bouge: bouge, descendu: !j.manege,
                 dessine: j.dessine, fin: { x: j.x, y: j.y }, arret: { x: c0.x, y: c0.y }, msg: B.msg,
                 L: C.chemin.longueur, v: C.chemin.def.vitesse };
    }""")
    assert r["invite"] == "UN TOUR DE CALÈCHE", r
    assert r["aBord"], "ACTION derrière la calèche ne fait pas monter"
    assert r["bouge"] and r["descendu"] and r["dessine"], r
    assert r["images"] >= r["L"] / r["v"], f"descendu avant la fin du tour : {r}"
    assert r["yMax"] >= 44 * 16 - 8 and r["xMin"] <= 48 * 16 + 8, f"le tour ne passe pas par le fond de l'érablière : {r}"
    assert abs(r["fin"]["x"] - r["arret"]["x"]) < 24 and abs(r["fin"]["y"] - r["arret"]["y"]) < 32, r
    assert "MERCI" in (r["msg"] or ""), r


def test_les_chevaux_trottent_quand_elle_roule_et_rien_n_est_tire_au_de(banc):
    """Deux images de trot, deux dessins ; arrêtés, deux images pareilles. Et un tour complet de la calèche (et la
    naissance des gens de la cabane) ne prend pas un seul tirage de `B.rng()`."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        await auRang(L, o, 12, 13);
        // Les images qu'on peint (`drawImage`), chacune par son numéro : l'attelage en volume a une image par pas.
        const numeros = new Map();
        function traces() {
            const c = C.caleche(), ctx = L.Base.nouveauCanvas(600, 400).getContext('2d'), vis = [], peintes = [];
            ctx.drawImage = function (img) { if (!numeros.has(img)) numeros.set(img, numeros.size); peintes.push(numeros.get(img)); };
            C.ajouterVisibles(vis, c.chevaux.x - 300, c.chevaux.y - 200);
            vis.filter(function (v) { return v.id === 910000001; }).forEach(function (v) { v.peindreFoire(ctx); });
            return JSON.stringify(peintes);
        }
        const e = C.etat;
        e.attente = 500; const arret1 = traces(); e.s = 0; const arret2 = traces();
        e.attente = 0; e.s = 30; const trot1 = traces(); e.s = 36; const trot2 = traces();
        // Le dé : un tour complet, et la naissance des gens, entre deux tirages.
        C.gens().forEach(function (g) { L.Entites.retirer(g); }); e.gens = false;
        L.graine(9); const temoin = [B.rng(), B.rng()]; L.graine(9);
        e.s = 0; e.attente = 1;
        for (let k = 0; k < 2200; k++) C.maj();
        const apres = [B.rng(), B.rng()];
        return { arret: arret1 === arret2, trot: trot1 !== trot2, vide: trot1 === '[]', temoin: temoin, apres: apres,
                 tours: e.tours, gens: C.gens().length };
    }""")
    assert not r["vide"], "les chevaux ne sont pas peints"
    assert r["trot"], "les chevaux ne trottent pas : deux pas, un seul dessin"
    assert r["arret"], "arrêtés, les chevaux bougent quand même"
    assert r["tours"] >= 1, r
    assert r["gens"] > 0, r
    assert r["apres"] == r["temoin"], "la calèche ou les gens de la cabane ont tiré au dé du jeu"


def test_les_gens_de_la_cabane_au_temps_des_sucres_et_personne_l_hiver(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        await auRang(L, o, 12, 13);
        const printemps = C.gens().map(function (e) { return e.cabane; });
        const musicien = C.gens().find(function (e) { return e.cabane === 'musicien'; });
        const fige = C.gens().every(function (e) { return e.etat === 'fige'; });
        // La fermeture : ils rentrent — mais pas sous nos yeux.
        B.partie.heure = 23 / 24;
        const vu = C.gens().filter(function (e) { return L.Entites.visibleAEcran(e.x, e.y, 24); }).length;
        o.frame(1);
        const restent = C.gens().length;
        poser(L, 20 * TT, 40 * TT); L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        o.frame(2);
        const nuit = C.gens().length;
        return { printemps: printemps, toune: musicien && musicien.toune, fige: fige, vu: vu, restent: restent, nuit: nuit };
    }""")
    assert "tireur" in r["printemps"] and "musicien" in r["printemps"] and r["printemps"].count("client") >= 4, r
    assert r["toune"] == "cabane_violon", "le musicien de la cabane n'est pas le violoneux (28 sept. 2026)"
    assert r["fige"], "les gens de la cabane flânent (ils tireraient au dé à chaque pas)"
    assert r["vu"] > 0 and r["restent"] >= r["vu"], "à la fermeture, des gens se sont évaporés sous nos yeux"
    assert r["nuit"] == 0, "la cabane fermée, ses gens sont encore là"
    hiver = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        await auRang(L, o, 2, 13);
        for (let k = 0; k < 30; k++) o.frame(1);
        return { gens: L.Cabane.gens().length, table: L.B.entites.filter(function (e) { return e.decor === 'table_tire'; })
                 .map(function (e) { return e.poseManuelle; }) };
    }""")
    assert hiver["gens"] == 0, "l'hiver, il y a du monde à la cabane"
    assert hiver["table"] == [0], f"hors saison, des rubans de tire sur la neige : {hiver}"


def test_la_vapeur_ne_sort_qu_au_temps_des_sucres_et_la_tubulure_est_bleue(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await auRang(L, o, 12, 13);
        const ch = L.Blocs.cheminees();
        const lanterneau = ch.find(function (c) { return c.genre === 'lanterneau'; }), tole = ch.find(function (c) { return c.genre === 'tole'; });
        const chalet = ch.find(function (c) { return !c.genre; });
        function fument() { return [L.Blocs.fume(lanterneau), L.Blocs.fume(tole), L.Blocs.fume(chalet)]; }
        const sucres = fument();
        B.partie.heure = 23 / 24; const nuit = fument();
        B.partie.jour = 2; B.partie.heure = 13 / 24; const hiver = fument();
        B.partie.jour = 12;
        // La tubulure : du bleu, d'érable en érable, et le tuyau maître jusqu'au toit.
        const ctx = L.Base.nouveauCanvas(900, 400).getContext('2d'); ctx.traces = [];
        L.Cabane.dessinerSol(ctx, { x: 50 * TT, y: 2 * TT });
        const bleus = ctx.traces.filter(function (q) { return q[4] === '#2f86d6'; }).length;
        const maitre = ctx.traces.filter(function (q) { return q[4] === '#1c2e44'; }).map(function (q) { return q[1]; });
        return { sucres: sucres, nuit: nuit, hiver: hiver, bleus: bleus, maitre: maitre.length,
                 maitreBas: maitre.length ? Math.max.apply(null, maitre) + 2 * TT : 0,
                 toit: 11 * TT };
    }""")
    assert r["sucres"] == [True, True, True], r
    assert r["nuit"] == [False, False, True], "la nuit, l'évaporateur bout encore"
    assert r["hiver"] == [False, False, True], "l'hiver, l'évaporateur bout"
    assert r["bleus"] > 200, "la tubulure bleue n'est pas peinte"
    assert r["maitre"] > 0, "le tuyau maître n'est pas peint"
    assert r["maitreBas"] >= r["toit"], "le tuyau maître n'arrive pas à la cabane"


def test_la_table_de_tire_propose_le_defi_au_temps_des_sucres(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, t = B.defs.blocs && L.Monde;
        L.Histoire.ouvrirDefi(B.defs.defis.find(function (q) { return q.slug === 'tire'; }), true);
        await auRang(L, o, 12, 13);
        const table = L.Monde.carte.def.bloc.cabane.table;
        poser(L, table.x * TT + 8, (table.y + 1) * TT + 8);
        o.frame(1);
        const invite = B.invite;
        o.tape('KeyE', 1);
        const menu = B.menu && B.menu.titre;
        if (B.menu) L.Hud.fermerMenu();
        B.partie.jour = 22; o.frame(1);
        B.msg = null; o.tape('KeyE', 1);
        return { invite: invite, menu: menu, ete: B.msg, menuEte: !!B.menu };
    }""")
    assert r["invite"] == "LA TIRE SUR LA NEIGE", r
    assert r["menu"] and "TIRE" in r["menu"], f"ACTION à la table ne propose pas le défi : {r}"
    assert not r["menuEte"] and "FERMÉ" in (r["ete"] or ""), r


def test_la_pancarte_a_ses_poteaux_dans_l_herbe_au_bord_du_sentier(banc):
    """Martin (28 sept. 2026) : « la pancarte est pas alignée au chemin » — centrée sur sa tuile, son poteau de
    gauche tombait dans le passage qui descend de la cabane. Ses deux poteaux sont dans l'herbe, et leurs pieds
    touchent le sentier de la calèche."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane, M = L.Monde;
        await auRang(L, o, 12, 13);
        const p = C.pancarte();
        return { p: p, sous: p.poteaux.map(function (x) { return M.glyphe(Math.floor(x / TT), Math.floor(p.y / TT)); }),
                 pieds: p.poteaux.map(function (x) { return M.glyphe(Math.floor(x / TT), Math.floor((p.y + 1) / TT)); }),
                 sentier: M.glyphe(60, 30) };
    }""")
    assert r["sentier"] == "g", r
    assert all(g != r["sentier"] for g in r["sous"]), f"un poteau de la pancarte est planté dans le chemin : {r}"
    assert all(g == r["sentier"] for g in r["pieds"]), f"la pancarte ne se tient pas au bord du sentier : {r}"


def test_la_caleche_tourne_comme_un_vrai_vehicule(banc):
    """Martin (28 sept. 2026) : « je veux que les virages soient mieux, comme un vrai véhicule ». Sur tout le tour :
    le cap de la caisse et celui des chevaux ne sautent jamais d'un coup (au plus un cran des 32 d'une image à
    l'autre) ; dans un coin, les chevaux tournent D'ABORD et la caisse suit ; et jamais l'attelage ne se met en
    travers de la caisse."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane, V = L.Vehicules;
        await auRang(L, o, 12, 13);
        const e = C.etat, L0 = C.chemin.longueur, v = C.chemin.def.vitesse;
        const ecart = function (a, b) { let d = Math.abs(a - b) % 32; return Math.min(d, 32 - d); };
        const angle = function (a, b) { let d = Math.abs(a - b) % (2 * Math.PI); return Math.min(d, 2 * Math.PI - d); };
        let sautCaisse = 0, sautChevaux = 0, travers = 0, avant = null, chevauxDabord = false, caisseApres = false;
        e.attente = 0;
        for (let s = 0; s < L0; s += v) {
            e.s = s;
            const c = C.caleche(), cap = V.capDe(c.a), capC = V.capDe(c.chevaux.a);
            if (avant) {
                sautCaisse = Math.max(sautCaisse, ecart(cap, avant.cap));
                sautChevaux = Math.max(sautChevaux, ecart(capC, avant.capC));
                // Au premier coin (vers le sud) : les chevaux descendent pendant que la caisse regarde encore l'ouest.
                if (angle(c.chevaux.a, Math.PI / 2) < 0.2 && angle(c.a, Math.PI) < 0.5) chevauxDabord = true;
                if (chevauxDabord && angle(c.a, Math.PI * 3 / 4) < 0.2) caisseApres = true;
            }
            travers = Math.max(travers, angle(c.a, c.chevaux.a));
            avant = { cap: cap, capC: capC };
        }
        return { sautCaisse: sautCaisse, sautChevaux: sautChevaux, travers: travers, chevauxDabord: chevauxDabord,
                 caisseApres: caisseApres };
    }""")
    assert r["sautCaisse"] <= 1, f"la caisse vire d'un coup : {r}"
    assert r["sautChevaux"] <= 1, f"les chevaux virent d'un coup : {r}"
    assert r["chevauxDabord"] and r["caisseApres"], f"la caisse ne suit pas ses chevaux dans le virage : {r}"
    assert r["travers"] < 1.75, f"l'attelage se met en travers de la caisse : {r}"


def test_on_monte_de_n_importe_quel_cote_meme_pres_des_chevaux(banc):
    """Martin (28 sept. 2026) : « je ne peux plus embarquer » — il se tenait au-dessus des chevaux, et on ne montait
    qu'à 30 px de l'arrière. À côté de la caisse, de n'importe quel côté, ou à côté des chevaux : l'invite, et ACTION
    fait monter."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane, j = B.joueur;
        await auRang(L, o, 12, 13);
        const c0 = C.caleche(), n = -Math.sin(c0.a), m = Math.cos(c0.a);
        const places = {
            chevaux: [c0.chevaux.x - n * (C.CHEVAUX.w + 6), c0.chevaux.y - m * (C.CHEVAUX.w + 6)],
            flanc_nord: [c0.x - n * (C.CAISSE.w + 8), c0.y - m * (C.CAISSE.w + 8)],
            flanc_sud: [c0.x + n * (C.CAISSE.w + 8), c0.y + m * (C.CAISSE.w + 8)],
        };
        const vu = {};
        for (const k of Object.keys(places)) {
            if (j.manege) C.descendre(j, true);
            C.etat.s = 0; C.etat.attente = 400;
            poser(L, places[k][0], places[k][1]);
            o.frame(1);
            const invite = B.invite;
            o.tape('KeyE', 1);
            vu[k] = { invite: invite, aBord: !!(j.manege && j.manege.quoi === 'caleche') };
        }
        return vu;
    }""")
    for place, v in r.items():
        assert v["invite"] == "UN TOUR DE CALÈCHE" and v["aBord"], f"on ne monte pas depuis {place} : {r}"


def test_la_cabane_fermee_pas_de_caleche_et_le_cocher_dit_quand_il_attelle(banc):
    """Martin (28 sept. 2026) : « la calèche devrait être absente si fermée ». La nuit, et hors du temps des sucres :
    pas de calèche, et à sa pancarte, l'invite dit quand le cocher attelle. Elle ne s'évapore pas sous nos yeux : on
    la regarde à la fermeture, elle reste ; on s'en va, elle part ; on revient à l'ouverture, elle est là."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane, j = B.joueur;
        const vu = {};
        const aLaPancarte = function () {
            const p = C.pancarte();
            poser(L, p.x0 + p.large / 2, p.y - 12);
            o.frame(1);
            const invite = B.invite;
            o.tape('KeyE', 1);
            return { la: !!C.caleche(), invite: invite, msg: String((B.msg && B.msg.texte) || B.msg || ''),
                     aBord: !!j.manege };
        };
        await auRang(L, o, 12, 2.9);
        vu.nuit = aLaPancarte();
        // Le jour : on la regarde quand la cabane ferme, elle reste ; on s'en va, elle part ; on revient, elle est là.
        B.partie.heure = 13 / 24;
        poser(L, 4 * TT, 46 * TT); for (let i = 0; i < 60; i++) o.frame(1);
        poser(L, 60 * TT, 28 * TT); for (let i = 0; i < 60; i++) o.frame(1);
        vu.jour = !!C.caleche();
        B.partie.heure = 23 / 24; for (let i = 0; i < 5; i++) o.frame(1);
        vu.sousNosYeux = !!C.caleche();
        poser(L, 4 * TT, 46 * TT); for (let i = 0; i < 60; i++) o.frame(1);
        vu.partie = !C.caleche();
        B.partie.heure = 13 / 24; for (let i = 0; i < 5; i++) o.frame(1);
        vu.revenue = !!C.caleche();
        return vu;
    }""")
    hiver = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        await auRang(L, o, 2, 13);
        const p = C.pancarte();
        poser(L, p.x0 + p.large / 2, p.y - 12);
        o.frame(1);
        return { la: !!C.caleche(), invite: B.invite };
    }""")
    nuit = r["nuit"]
    assert not nuit["la"], f"la nuit, la calèche est là : {r}"
    assert nuit["invite"] == "PAS DE CALÈCHE — LE COCHER ATTELLE À 7 H", r
    assert "LE COCHER ATTELLE" in nuit["msg"] and not nuit["aBord"], r
    assert r["jour"], f"le jour, pas de calèche : {r}"
    assert r["sousNosYeux"], f"la calèche s'évapore sous nos yeux à la fermeture : {r}"
    assert r["partie"], f"la cabane fermée, la calèche est encore là quand on ne la regarde plus : {r}"
    assert r["revenue"], f"la calèche ne revient pas à l'ouverture : {r}"
    assert not hiver["la"] and hiver["invite"] == "PAS DE CALÈCHE — ON ATTELLE AU TEMPS DES SUCRES", hiver
