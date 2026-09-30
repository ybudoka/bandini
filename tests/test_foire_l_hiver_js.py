"""La foire fermée l'hiver (docs/jalons/la-foire-fermee-l-hiver.md, vague 1).

Martin (30 sept. 2026) : « la foire, fermée l'hiver ». Tant que la neige tient (`Saisons.enHiver`), elle
est CADENASSÉE : l'arche ne vend plus de billet, les manèges ne tournent plus et personne n'y est assis,
les kiosques ont leurs volets baissés, les guirlandes sont éteintes, l'orgue se tait, ni foule ni mascotte,
on ne monte à rien, on ne joue à rien — et le Bonimenteur n'est pas là : ses missions attendent. Chaque
juge regarde janvier (`jour = 2`) ET juillet (`jour = 21`) : une règle qui fermerait la foire toute
l'année serait verte en janvier.
"""

#: Le moment, et la foire telle que le banc la trouve.
OUTILS = """
    function moment(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h === undefined ? 0.5 : h; }
    function arche(L) { return L.Monde.barrieres().find(function (b) { return b.slug === 'foire'; }); }
"""


def test_la_foire_est_fermee_tant_que_la_neige_tient(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const out = {};
        for (const [nom, jour, h] of [['janvier', 2], ['fevrier', 6], ['decembre', 39], ['avril', 14], ['juillet', 21], ['octobre', 31]]) {
          moment(L, jour, h); out[nom] = L.Foire.fermee();
        }
        return out;
    }""")
    assert r["janvier"] and r["fevrier"] and r["decembre"], r
    assert not r["avril"] and not r["juillet"] and not r["octobre"], r


def test_l_hiver_le_train_et_le_colosse_restent_en_gare_et_on_ne_monte_a_rien(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, F = L.Foire, j = B.joueur, TT = L.TT;
        j.invincible = 1e9;
        function mesure(jour) {
          moment(L, jour); L.Foire.demarrer();
          const t = F.train, m = F.montagne, s0 = t.s, m0 = m.s;
          let bouge = 0, bougeM = 0;
          for (let i = 0; i < 900; i++) {
            L.Foire.maj(); B.t++;
            if (Math.abs(t.s - s0) > 0.5) bouge++;
            if (Math.abs(m.s - m0) > 0.5) bougeM++;
          }
          // Debout sur le quai, face au wagon 1 du train arrete : peut-on y monter ?
          const w = F.wagons()[1];
          j.x = w.x; j.y = w.y + 10; j.face = 'haut'; j.angle = -Math.PI / 2;
          const enGare = t.attente > 0;
          return { bouge: bouge, bougeM: bougeM, enGare: enGare, sGare: t.s === t.sGare,
                   monter: enGare ? F.sousLaMain(j) : 'pas en gare',
                   cran: F.roue ? [0, 50, 500].map(function (dt) { B.t += dt; return F.attache(0); }) : null };
        }
        const hiver = mesure(2);
        return { hiver: hiver };
    }""")
    h = r["hiver"]
    assert h["enGare"] and h["sGare"], "en janvier, le petit train n'est pas en gare"
    assert h["bouge"] == 0 and h["bougeM"] == 0, f"en janvier, le train ({h['bouge']}) ou le Colosse ({h['bougeM']}) roule"
    assert h["monter"] is None, "en janvier, on monte dans le petit train"
    assert h["cran"] and h["cran"][0] == h["cran"][1] == h["cran"][2], "en janvier, la grande roue tourne"


def test_l_ete_le_train_repart_et_la_roue_tourne(banc):
    """Le pendant de celui d'avant : la même mesure en juillet ROULE — sinon le juge d'hiver ne dit rien."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, F = L.Foire;
        moment(L, 21); F.demarrer();
        const s0 = F.train.s;
        let bouge = 0;
        for (let i = 0; i < 900; i++) { F.maj(); B.t++; if (Math.abs(F.train.s - s0) > 0.5) bouge++; }
        const a = F.attache(0); B.t += 500; const b = F.attache(0);
        return { bouge: bouge, roue: a.x !== b.x || a.y !== b.y };
    }""")
    assert r["bouge"] > 100 and r["roue"], r


def test_l_hiver_les_manèges_ne_tournent_pas_et_sont_vides(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const E = L.Entites, D = L.DECORS;
        const poses = {};
        for (const nom of ['carrousel', 'tasses', 'chaises_volantes', 'grande_roue', 'marteau_force', 'peche_canards', 'portique_foire']) {
          moment(L, 2); const h = [0, 13, 29, 57, 101].map(function (t) { return E.poseDuDecor(D[nom], t); });
          moment(L, 21); const e = [0, 13, 29, 57, 101].map(function (t) { return E.poseDuDecor(D[nom], t); });
          poses[nom] = { hiver: h, ete: e };
        }
        // Qui est assis : la peau des passagers (`#e8b088`) peinte par chaque manège, ouvert et fermé.
        function peau(nom, ferme) {
          const ctx = L.Base.nouveauCanvas(D[nom].w, D[nom].h).getContext('2d'); ctx.traces = [];
          D[nom].peindre(ctx, D[nom].w, D[nom].h, 0, ferme);
          return ctx.traces.filter(function (t) { return t[4] === '#e8b088'; }).length;
        }
        function ampoules(nom, ferme) {
          const ctx = L.Base.nouveauCanvas(D[nom].w, D[nom].h).getContext('2d'); ctx.traces = [];
          [0, 1].forEach(function (v) { D[nom].peindre(ctx, D[nom].w, D[nom].h, v, ferme); });
          // ⚠️ Les lettres « FOIRE » de l'arche sont du même jaune (2 x 2) : on ne compte que ses ampoules (3 x 3).
          return ctx.traces.filter(function (t) { return t[4] === '#ffe58a' && (nom !== 'portique_foire' || (t[2] === 3 && t[3] === 3)); }).length;
        }
        const assis = {}, allume = {};
        for (const nom of ['tasses', 'chaises_volantes']) assis[nom] = [peau(nom, false), peau(nom, true)];
        for (const nom of ['carrousel', 'tasses', 'chaises_volantes', 'grande_roue', 'portique_foire']) allume[nom] = [ampoules(nom, false), ampoules(nom, true)];
        const tous = L.B.defs.carte.kiosques_de_foire.concat(L.B.defs.carte.jeux_de_foire || []).map(function (k) { return k.slug; })
          .concat(['carrousel', 'tasses', 'chaises_volantes', 'grande_roue', 'portique_foire']);
        return { poses: poses, assis: assis, allume: allume, marques: tous.filter(function (n) { return !D[n] || !D[n].fermeLHiver; }) };
    }""")
    assert r["marques"] == [], f"un décor de la foire n'est pas marqué : {r['marques']}"
    for nom, p in r["poses"].items():
        assert set(p["hiver"]) == {0}, f"{nom} tourne en janvier : {p['hiver']}"
        assert len(set(p["ete"])) > 1, f"{nom} ne tourne pas en juillet : le juge ne voit rien"
    for nom, (ouvert, ferme) in r["assis"].items():
        assert ouvert > 0 and ferme == 0, f"{nom} : {ouvert} passagers ouvert, {ferme} fermé"
    for nom, (ouvert, ferme) in r["allume"].items():
        assert ouvert > 0 and ferme == 0, f"{nom} : {ouvert} ampoules allumées ouvert, {ferme} fermé"


def test_l_hiver_les_kiosques_ont_leurs_volets_baisses_et_personne_derriere(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const D = L.DECORS, out = {};
        for (const k of L.B.defs.carte.kiosques_de_foire.concat(L.B.defs.carte.jeux_de_foire || [])) {
          const d = D[k.slug];
          function peindre(ferme) {
            const ctx = L.Base.nouveauCanvas(d.w, d.h).getContext('2d'); ctx.traces = [];
            d.peindre(ctx, d.w, d.h, 5, ferme);
            return ctx.traces;
          }
          out[k.slug] = { ouvert: peindre(false), ferme: peindre(true) };
        }
        return { kiosques: out };
    }""")
    volet = "#80868d"
    tete = [11, 8, 6, 5]                               # la tête du vendeur (`peindreKiosque`)
    for slug, p in r["kiosques"].items():
        if slug in ("marteau_force", "peche_canards"):
            continue                                   # ni comptoir ni vendeur : ampoules et bassin gelé
        couleurs = {k: {t[4] for t in p[k]} for k in ("ouvert", "ferme")}
        assert volet in couleurs["ferme"] and volet not in couleurs["ouvert"], f"{slug} : pas de volet baissé l'hiver"
        if slug != "galerie_tir":
            vendeur = {k: any(t[:4] == tete for t in p[k]) for k in ("ouvert", "ferme")}
            assert vendeur["ouvert"] and not vendeur["ferme"], f"{slug} : le vendeur est encore là l'hiver"


def test_l_hiver_les_guirlandes_sont_eteintes_et_l_orgue_se_tait(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, f = L.Monde.carte.def.foire, TT = L.TT, j = B.joueur;
        j.x = (f.x + f.l / 2) * TT; j.y = (f.y + f.h / 2) * TT; j.invincible = 1e9;
        const cam = { x: j.x - L.VW / 2, y: j.y - L.VH / 2 };
        function foire(jour) {
          moment(L, jour, 0.9);
          const lampes = L.Monde.lampesVisibles(cam).length;
          let orgue = 0, cris = 0;
          const vraiRue = L.Son.Rue.demander, vraiCris = L.Son.SFX.rumeur_foire;
          L.Son.Rue.demander = function (slug, v) { if (slug === 'foire_orgue' && v > 0) orgue++; };
          L.Son.SFX.rumeur_foire = function (v) { if (v > 0) cris++; };
          for (let i = 0; i < 10; i++) L.Foire.maj();
          L.Son.Rue.demander = vraiRue; L.Son.SFX.rumeur_foire = vraiCris;
          const guirlandes = L.Monde.carte.lampes.filter(function (l) { return l.sorte && l.sorte.indexOf('foire_') === 0; }).length;
          return { lampes: lampes, orgue: orgue, cris: cris, guirlandes: guirlandes };
        }
        return { hiver: foire(2), ete: foire(21) };
    }""")
    h, e = r["hiver"], r["ete"]
    assert e["guirlandes"] > 10, "la foire n'a pas ses guirlandes : le juge ne voit rien"
    assert e["orgue"] > 0 and e["cris"] > 0, "en juillet, l'orgue ou les cris ne jouent pas : le juge ne voit rien"
    assert h["orgue"] == 0 and h["cris"] == 0, "en janvier, la foire s'entend"
    assert e["lampes"] > h["lampes"], f"en janvier, {h['lampes']} lumières au milieu de la foire, {e['lampes']} en juillet"


def test_l_hiver_l_arche_est_cadenassee_et_ne_vend_pas_de_billet(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const b = arche(L), TT = L.TT, j = L.B.joueur, p = L.B.partie;
        function essai(jour) {
          moment(L, jour); p.argent = 100; p.billets = {}; j.bute = null; L.B.buteMsgT = -999;
          j.x = (b.x + 1) * TT + 8; j.y = (b.y + 1) * TT + 8;
          const bloque = L.Monde.barriereBloque(j, b.x + 1, b.y);
          const lu = j.bute ? L.Monde.raisonDe(j.bute) : null;
          // Avec un billet du jour pris avant la neige, l'hiver ferme quand même.
          p.billets = { foire: p.jour };
          const avecBillet = L.Monde.barriereFermee(b);
          // On ressort toujours librement.
          j.x = (b.x + 1) * TT + 8; j.y = (b.y - 1) * TT + 8;
          const sortie = L.Monde.barriereBloque(j, b.x + 1, b.y);
          return { bloque: bloque, argent: p.argent, lu: lu, avecBillet: avecBillet, sortie: sortie };
        }
        return { hiver: essai(2), ete: essai(21), hiverDef: b.hiver };
    }""")
    h, e = r["hiver"], r["ete"]
    assert h["bloque"] is True and h["argent"] == 100, "en janvier, l'arche vend un billet"
    assert h["lu"] == r["hiverDef"] and "HIVER" in h["lu"], f"en janvier, on lit {h['lu']!r}"
    assert h["avecBillet"] is True and h["sortie"] is False
    assert e["bloque"] is False and e["argent"] < 100, "en juillet, l'arche ne vend plus de billet"


def test_l_hiver_ni_foule_ni_mascotte_et_ceux_qui_restent_rentrent(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, TT = L.TT, f = L.Monde.carte.def.foire, k = L.Monde.carte.def.kiosques_de_foire;
        B.joueur.x = (f.x + 20) * TT + 8; B.joueur.y = (k[0].y + 1) * TT + 8; B.joueur.invincible = 1e9;
        L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        function gens() { return B.entites.filter(function (e) { return e.vivant && (e.metier === 'forain' || e.metier === 'mascotte'); }); }
        moment(L, 2);
        for (let i = 0; i < 600; i++) o.frame(1);
        const hiver = gens().length;
        moment(L, 21);
        for (let i = 0; i < 600; i++) o.frame(1);
        const ete = gens().length;
        // La neige arrive pendant qu'ils y sont : chacun rentre, hors de l'ecran (`rentrerHorsChamp`).
        moment(L, 2);
        const avant = gens();
        B.joueur.x -= 60 * TT; L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        for (let i = 0; i < 30; i++) o.frame(1);
        const rentres = avant.filter(function (e) { return e.etat === 'entre' || !e.vivant || B.entites.indexOf(e) < 0; }).length;
        return { hiver: hiver, ete: ete, avant: avant.length, rentres: rentres };
    }""")
    assert r["ete"] > 5, f"en juillet, {r['ete']} forains : le juge ne voit rien"
    assert r["hiver"] == 0, f"en janvier, {r['hiver']} forains dans la foire fermée"
    assert r["rentres"] == r["avant"], f"la neige venue, {r['avant'] - r['rentres']} forains sur {r['avant']} restent"


def test_l_hiver_le_bonimenteur_n_est_pas_la_et_ses_missions_attendent(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire, fait = B.partie.missionsFaites;
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { fait[s] = true; });
        function siens() { return H.disponibles().filter(function (m) { return m.donneur === 'bonimenteur'; }).map(function (m) { return m.slug; }); }
        const janvier = { pose: !!H.donneur('bonimenteur'), missions: siens() };
        moment(L, 21); H.majSaisonniers(true);
        const juillet = { pose: !!H.donneur('bonimenteur'), missions: siens() };
        // La neige revient : il repart, hors de l'ecran.
        moment(L, 39);
        const e = H.donneur('bonimenteur');
        B.joueur.x = e.x + 80 * L.TT; L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        H.majSaisonniers(true);
        return { janvier: janvier, juillet: juillet, decembre: { pose: !!H.donneur('bonimenteur'), missions: siens() } };
    }""")
    assert not r["janvier"]["pose"] and r["janvier"]["missions"] == [], r["janvier"]
    assert r["juillet"]["pose"] and "p13" in r["juillet"]["missions"], r["juillet"]
    assert not r["decembre"]["pose"] and r["decembre"]["missions"] == [], r["decembre"]


def test_l_hiver_les_jeux_de_la_foire_ne_se_jouent_pas(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, TT = L.TT, F = L.Foire;
        const q = F.comptoirs()[0];
        j.x = q.x * TT + 8; j.y = q.y * TT + 15 + 14; j.face = 'haut'; j.angle = -Math.PI / 2;
        moment(L, 21); const ete = F.jeuSousLaMain(j);
        moment(L, 2); const hiver = F.jeuSousLaMain(j);
        return { ete: ete, hiver: hiver };
    }""")
    assert r["ete"], "en juillet, aucun comptoir sous la main : le juge ne voit rien"
    assert r["hiver"] is None, "en janvier, on joue à la foire"
