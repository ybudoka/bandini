"""Les foyers de l'hiver (docs/jalons/la-foire-fermee-l-hiver.md, vague 3 ; `static/js/foyers.js`).

Martin (30 sept. 2026) : « à la place : jongleur de feu, des foyers centraux et des vendeurs de chocolat
chaud ». Tranché : sur chaque place publique, un brasero de part et d'autre de la fontaine à sec, où des
passants se chauffent les mains et où le joueur reprend son souffle plus vite ; une roulotte de chocolat
chaud au sud de la fontaine ; et le jongleur du Faubourg jongle avec trois torches. Rien ne naît : tout
se peint, sans un dé. Chaque juge regarde janvier (`jour = 2`) ET juillet (`jour = 22`).
"""

from app import economie, foyers

OUTILS = """
    function moment(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h === undefined ? 0.5 : h; }
    function alaPlace(L, k) {
      const p = L.Foyers.places()[k || 0], f = p.fontaine, j = L.B.joueur;
      j.x = f.x * L.TT + 8; j.y = (f.y + 5) * L.TT + 8; j.invincible = 1e9;
      L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
      return p;
    }
"""


def test_chaque_place_a_deux_braseros_et_une_roulotte_hors_de_tout(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, def = M.carte.def;
        const places = L.Foyers.places(), fautes = [];
        const decor = def.decor.map(function (d) { return [d.x * TT + 8, d.y * TT + 15, d.type]; });
        places.forEach(function (p) {
          p.braseros.concat([p.roulotte]).forEach(function (q) {
            if (!q) { fautes.push('manque'); return; }
            if (M.estRoute(q.tx, q.ty) || M.devantDUnePorte(q.tx, q.ty) || !M.marchablePieton(q.tx, q.ty)) fautes.push('mal pose ' + q.tx + ',' + q.ty);
            // ⚠️ Sur toute la hauteur du dessin (la roulotte monte de deux tuiles : elle couvrait un banc).
            decor.forEach(function (d) { if (Math.abs(d[0] - q.x) < 16 && d[1] > q.y - 30 && d[1] < q.y + 12) fautes.push('sur ' + d[2]); });
          });
        });
        return { n: places.length, braseros: places.map(function (p) { return p.braseros.length; }),
                 roulottes: places.filter(function (p) { return p.roulotte; }).length, fautes: fautes,
                 fontaines: def.decor.filter(function (d) { return d.type === 'fontaine'; }).length };
    }""")
    assert r["n"] == r["fontaines"] >= 1, r
    assert all(n == 2 for n in r["braseros"]), r["braseros"]
    assert r["roulottes"] == r["n"], r
    assert r["fautes"] == [], r["fautes"][:5]


def test_l_hiver_les_braseros_brulent_et_l_ete_il_n_y_a_rien(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, F = L.Foyers;
        const p = alaPlace(L), b = p.braseros[0];
        function mesure(jour) {
          moment(L, jour, 0.9);
          const vis = []; F.ajouterVisibles(vis, B.cam.x, B.cam.y);
          // Un passant plante au milieu du brasero : le feu le repousse.
          const q = { type: 'pieton', x: b.x + 1, y: b.y, r: 5 };
          F.bloquer(q);
          return { braseros: F.braseros().length, peints: vis.length, pousse: Math.round(Math.hypot(q.x - b.x, q.y - b.y)),
                   lueurs: F.lampes(B.cam.x, B.cam.y).length, lampes: L.Monde.lampesVisibles(B.cam).length };
        }
        return { hiver: mesure(2), ete: mesure(22) };
    }""")
    h, e = r["hiver"], r["ete"]
    assert h["braseros"] >= 2 and h["peints"] >= 3, h
    assert h["pousse"] >= 10, f"un passant tient dans le brasero : {h['pousse']} px"
    assert h["lueurs"] >= 2, h
    assert e["braseros"] == 0 and e["peints"] == 0 and e["pousse"] <= 1 and e["lueurs"] == 0, e


def test_l_hiver_une_tasse_de_chocolat_chaud_a_la_roulotte(banc):
    prix = economie.TARIFS["chocolat_chaud"]
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        const p = alaPlace(L), q = p.roulotte;
        function devant() { j.x = q.x; j.y = q.y + 16; j.face = 'haut'; j.angle = -Math.PI / 2; j.vx = 0; j.vy = 0; L.Entites.indexer(); }
        if (L.B.menu) L.Hud.fermerMenu();
        moment(L, 22); devant(); L.Missions.majInvite(j);
        const ete = B.invite;
        moment(L, 2); devant(); L.Missions.majInvite(j);
        const hiver = B.invite;
        B.partie.argent = 50; j.endurance = 10;
        o.tape('KeyE', 2);
        return { ete: ete, hiver: hiver, argent: B.partie.argent, souffle: j.endurance };
    }""")
    assert r["hiver"] == f"CHOCOLAT CHAUD — {prix} $", r
    assert not (r["ete"] or "").startswith("CHOCOLAT"), r
    assert r["argent"] == 50 - prix and r["souffle"] > 10, r


def test_l_hiver_des_passants_se_chauffent_les_mains(banc):
    """⚠️ DÉTERMINISTE : cinq passants posés à la main près d'un brasero, qui flânent, un jour d'hiver
    où la règle les choisit tous (à l'empreinte, `part`) — au plus `par_feu` y vont, chacun à SA place,
    et personne n'entre dans personne. Attendre qu'un flâneur passe par hasard tenait à la foule du moment."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, E = L.Entites, F = L.Foyers, r = B.defs.foyers;
        moment(L, 2);
        const p = alaPlace(L), f = p.braseros[0];
        B.joueur.x = f.x + 60; B.joueur.y = f.y + 60; L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        const arch = E.archetype('passant') || B.defs.pietons.catalogue.find(function (a) { return a.frequence > 0; });
        const gens = [];
        for (let k = 0; k < 5; k++) {
          const q = E.creerPieton(f.x - 40 + k * 20, f.y + 50, arch);
          q.etat = 'flane'; gens.push(q);
        }
        // Un jour d'hiver ou la regle les choisit tous (ou le plus possible) : `hash2(id * 40503 + jour)`.
        let jour = 2, meilleur = -1;
        for (let d = 1; d <= 10; d++) {
          const n = gens.filter(function (q) { return L.hash2(q.id * 40503 + d, 0xF0E2) % r.part === 0; }).length;
          if (n > meilleur) { meilleur = n; jour = d; }
        }
        moment(L, jour);
        let max = 0, colles = 0;
        for (let i = 0; i < 900; i++) {
          gens.forEach(function (q) { if (q.etat === 'flane' && !q.versLeFoyer && !q.auFoyer) { q.vx = 0; q.vy = 0; } });
          o.frame(1);
          const la = gens.filter(function (q) { return q.auFoyer === f && q.etat === 'arret'; });
          max = Math.max(max, la.length);
          for (let a = 0; a < la.length; a++) for (let b2 = a + 1; b2 < la.length; b2++) {
            if (Math.hypot(la[a].x - la[b2].x, la[a].y - la[b2].y) < 9.5) colles++;
          }
        }
        // L'ete, la meme scene : personne.
        gens.forEach(function (q) { q.auFoyer = null; q.versLeFoyer = null; q.chauffeJour = null; q.etat = 'flane'; });
        moment(L, 22);
        let ete = 0;
        for (let i = 0; i < 300; i++) { o.frame(1); ete = Math.max(ete, gens.filter(function (q) { return q.versLeFoyer || q.auFoyer; }).length); }
        return { choisis: meilleur, max: max, colles: colles, parFeu: r.par_feu, ete: ete };
    }""")
    assert r["choisis"] >= 2, f"aucun jour d'hiver ne choisit ces passants : {r}"
    assert 1 <= r["max"] <= r["parFeu"], f"en janvier, {r['max']} passants au feu ({r})"
    assert r["colles"] == 0, f"deux passants à la même place au feu : {r}"
    assert r["ete"] == 0, r


def test_l_hiver_le_joueur_reprend_son_souffle_pres_du_feu(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, F = L.Foyers;
        const p = alaPlace(L), b = p.braseros[0];
        function souffle(jour, x, y) {
          moment(L, jour);
          j.x = x; j.y = y; j.vx = 0; j.vy = 0; j.endurance = 5;
          for (let i = 0; i < 20; i++) F.maj();
          return j.endurance;
        }
        return { pres: souffle(2, b.x, b.y + 14), loin: souffle(2, b.x + 200, b.y + 14), ete: souffle(22, b.x, b.y + 14),
                 bonus: B.defs.foyers.chaleur_souffle };
    }""")
    assert r["pres"] > 5 and r["loin"] == 5 and r["ete"] == 5, r


def test_l_hiver_le_jongleur_jongle_avec_trois_torches(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const S = L.SPRITES.jongleur;
        function lettres(fiche) {
          const vues = {};
          for (const nom in fiche.poses) if (nom !== 'couche') fiche.poses[nom].forEach(function (img) { img.forEach(function (rang) { for (const c of rang) vues[c] = 1; }); });
          return Object.keys(vues).join('');
        }
        moment(L, 2); const hiver = L.Saisons.ficheDuMoment('jongleur', S);
        moment(L, 22); const ete = L.Saisons.ficheDuMoment('jongleur', S);
        return { hiver: [hiver[0], lettres(hiver[1])], ete: [ete[0], lettres(ete[1])],
                 memeTaille: hiver[1].w === S.w && hiver[1].h === S.h };
    }""")
    nom, lettres = r["hiver"]
    assert nom == "jongleur~hiver" and r["memeTaille"], r
    assert "y" in lettres and "f" in lettres and not set("jvr") & set(lettres), lettres
    assert r["ete"][0] == "jongleur" and set("jvr") <= set(r["ete"][1]), r["ete"]


def test_les_foyers_ne_tirent_aucun_de(banc):
    """⚠️ Rien ne naît et rien ne se tire : une heure d'hiver sur la place laisse `B.rng` là où la même heure
    le laisse sans les foyers (on les éteint en retirant leurs règles)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, F = L.Foyers;
        moment(L, 2); alaPlace(L);
        let appels = 0;
        const vrai = B.rng;
        B.rng = function () { appels++; return vrai(); };
        for (let i = 0; i < 20; i++) { F.maj(); F.ajouterVisibles([], B.cam.x, B.cam.y); F.lampes(B.cam.x, B.cam.y); L.Entites.majLesFoyers(); B.t += 15; }
        B.rng = vrai;
        return { appels: appels };
    }""")
    assert r["appels"] == 0, f"{r['appels']} dés tirés par les foyers"


def test_le_chocolat_tient_la_regle_du_trottoir():
    t = economie.TARIFS
    points = (t["chocolat_chaud_pv"] + t["chocolat_chaud_souffle"]) / t["chocolat_chaud"]
    hotdog = (t["hotdog_pv"] + t["hotdog_souffle"]) / t["hotdog"]
    assert points <= hotdog, f"le chocolat vaut {points:.2f} points au dollar, le hot-dog {hotdog:.2f}"
    assert foyers.FOYERS["chocolat"]["tarif"] == "chocolat_chaud"
    # ⚠️ Pas la tablette des distributrices : le 30 sept. 2026, la cle `chocolat` doublee ecrasait le chocolat chaud.
    assert t["chocolat_chaud"] != t["chocolat"] or t["chocolat_chaud_souffle"] != t["chocolat_souffle"]
