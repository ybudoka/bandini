"""La nuit de déneigement (M12) au banc : les panneaux clignotent la veille, et ce qui reste
dans les rues du secteur part au lot.

⚠️ L'heure se règle à la main (`OPERATION`) : le lendemain de la première tempête.
"""

OPERATION = """
    function jourDeTempete(L, rang) { const t = L.Neige.donnees().tempete; return t.premier + rang * t.tous_les; }
    function regler(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h / 24; }
    function secteurDe(L, rang) { const o = L.Neige.donnees().deneigement; return o.secteurs[rang % o.secteurs.length]; }
    // Une ruelle du secteur (deux tuiles de large, droite sur cinq) : on s'y gare en toute
    // legalite le reste du temps (`Missions.malGare`).
    function ruelleDu(L, secteur, pres) {
        const c = L.Monde.carte;
        let mieux = null, dMin = Infinity;
        for (const z of c.def.zones.filter(function (q) { return q.district === secteur; })) {
            for (let y = z.y + 1; y < z.y + z.h - 1; y++) for (let x = z.x + 3; x < z.x + z.l - 3; x++) {
                let ok = true;
                for (let dy = -1; dy <= 1 && ok; dy++) for (let dx = -2; dx <= 2 && ok; dx++) {
                    const g = c.sol[y + dy][x + dx];
                    if (dy === 0 ? g !== 'x' : (L.Monde.estChaussee(x + dx, y + dy) || L.Monde.estPassage(x + dx, y + dy) || L.Monde.porteA(x + dx, y + dy + 1))) ok = false;
                }
                if (!ok) continue;
                const p = { x: x * L.TT + 8, y: y * L.TT + 8 };
                if (!pres) return p;
                const d = Math.hypot(p.x - pres.x, p.y - pres.y);
                if (d < dMin) { dMin = d; mieux = p; }
            }
        }
        return mieux;
    }
"""


def test_le_calendrier_de_l_operation(banc):
    r = banc("function (L, o) {" + OPERATION + """
        L.Jeu.commencer();
        const N = L.Neige, o2 = N.donnees().deneigement, s = jourDeTempete(L, 1);
        const a = function (jour, h) { const r = N.operationA(jour, h / 24); return r ? (r.enCours ? 'nuit:' : 'annonce:') + r.secteur : null; };
        return {
            soirDeTempete: a(s, 22), lendemainMatin: a(s + 1, o2.annonce_h - 0.5), annonce: a(s + 1, o2.annonce_h + 0.5),
            nuit: a(s + 1, o2.debut_h + 0.5), petitMatin: a(s + 2, o2.fin_h - 0.5), fini: a(s + 2, o2.fin_h + 0.5),
            secteur1: secteurDe(L, 1), secteur0: N.operationA(jourDeTempete(L, 0) + 1, (o2.debut_h + 0.5) / 24).secteur,
            sansOption: (function () { L.B.options.neige = false; regler(L, s + 1, o2.debut_h + 0.5); return N.operation(); })(),
            reste: [N.couvertureA(s, 23.8 / 24), N.couvertureA(s + 1, 10 / 24), N.couvertureA(s + 2, (o2.fin_h - 0.5) / 24), N.couvertureA(s + 2, (o2.fin_h + 0.5) / 24)],
            resteReglage: o2.reste,
        };
    }""")
    assert r["soirDeTempete"] is None and r["lendemainMatin"] is None and r["fini"] is None
    assert r["annonce"] == "annonce:" + r["secteur1"]
    assert r["nuit"] == "nuit:" + r["secteur1"] and r["petitMatin"] == "nuit:" + r["secteur1"]
    assert r["secteur0"] != r["secteur1"], "les secteurs ne se suivent pas"
    assert r["sansOption"] is None
    assert r["reste"][:3] == [r["resteReglage"]] * 3 and r["reste"][3] == 0, r["reste"]


def test_elle_s_annonce_ou_elle_n_arrive_pas(banc):
    """Sur trois cycles de tempête, minute de jeu par minute de jeu : chaque nuit
    d'opération est précédée, le même jour, d'au moins six heures d'annonce."""
    r = banc("function (L, o) {" + OPERATION + """
        L.Jeu.commencer();
        const N = L.Neige, t = N.donnees().tempete;
        let annonceDepuis = null, pire = Infinity, nuits = 0, avant = null;
        for (let jour = 1; jour < t.premier + 3 * t.tous_les + 3; jour++) {
            for (let m = 0; m < 24 * 60; m += 5) {
                const op = N.operationA(jour, m / 60 / 24), temps = jour * 24 + m / 60;
                if (op && !op.enCours && annonceDepuis === null) annonceDepuis = temps;
                if (op && op.enCours && (!avant || !avant.enCours)) {
                    nuits++;
                    pire = Math.min(pire, annonceDepuis === null ? -1 : temps - annonceDepuis);
                }
                if (!op) annonceDepuis = null;
                avant = op;
            }
        }
        return { nuits: nuits, pire: pire };
    }""")
    assert r["nuits"] >= 3, "le juge ne voit aucune nuit d'opération"
    assert r["pire"] >= 6, f"une opération annoncée {r['pire']} h avant"


def test_ce_qui_reste_dans_la_rue_part_au_lot(banc):
    """Un char laissé dans une ruelle du secteur — permis tout le reste du temps — part au
    lot pendant la nuit, pas avant ; dans sa case ou dans un autre secteur, il reste ; et
    tant qu'on le regarde, on ne le voit pas disparaître."""
    r = banc("function (L, o) {" + OPERATION + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        const s = jourDeTempete(L, 1), secteur = secteurDe(L, 1), autre = secteurDe(L, 2), o2 = L.Neige.donnees().deneigement;
        const j = L.B.joueur; j.intouchable = true;
        const dans = function (v) { return L.B.entites.indexOf(v) >= 0; };
        function garer(p, couleur) { const v = L.Vehicules.creer('auto', p.x, p.y, 0, { etat: 'stationne', couleur: couleur }); v.laisse = true; return v; }
        // ⚠️ Trois couleurs : un char loin du joueur s'OUBLIE (`peupler`), il ne part pas au
        // lot — c'est le lot qu'on lit, pas la disparition.
        const ici = garer(ruelleDu(L, secteur), '#3a6fb0');
        const loin = { x: ici.x + 380, y: ici.y };
        // Une case de stationnement du secteur.
        const c = L.Monde.carte;
        let caseP = null;
        c.def.zones.filter(function (z) { return z.district === secteur; }).forEach(function (z) {
            for (let y = z.y; y < z.y + z.h && !caseP; y++) for (let x = z.x; x < z.x + z.l && !caseP; x++) if (c.sol[y][x] === '^') caseP = { x: x * L.TT + 8, y: y * L.TT + 8 };
        });
        const enCase = caseP ? garer(caseP, '#aa3355') : null;
        L.Entites.indexer();
        // ⚠️ Hors de l'ecran mais DANS la bulle : au-dela d'`oubli_px`, un char gare
        // s'oublie de toute facon (`Vehicules.peupler`).
        j.x = loin.x; j.y = loin.y; L.Monde.centrerCamera(j.x, j.y);
        regler(L, s + 1, o2.annonce_h + 1); o.frame(130);
        const annonce = { ici: dans(ici), malGare: L.Missions.malGare(ici) };
        // Sous les yeux : il reste.
        L.Monde.centrerCamera(ici.x, ici.y); j.x = ici.x + 40; j.y = ici.y;
        regler(L, s + 1, o2.debut_h + 0.5); o.frame(130);
        const regarde = dans(ici);
        j.x = loin.x; j.y = loin.y; L.Monde.centrerCamera(j.x, j.y); o.frame(130);
        const resteEnCase = enCase ? dans(enCase) : 'pas de case';
        // Une ruelle d'un AUTRE secteur, la meme nuit, le joueur a cote — hors de l'ecran.
        const ailleurs = garer(ruelleDu(L, autre), '#2e8b57');
        L.Entites.indexer();
        j.x = ailleurs.x + 380; j.y = ailleurs.y; L.Monde.centrerCamera(j.x, j.y); o.frame(130);
        const auLot = L.B.partie.fourriere.map(function (f) { return f.couleur; });
        return { annonce: annonce, regarde: regarde, nuit: dans(ici), auLot: auLot, enCase: resteEnCase,
                 ailleursLa: dans(ailleurs) };
    }""")
    assert r["annonce"]["ici"] is True and r["annonce"]["malGare"] is False, f"le juge gare le char là où c'est interdit en temps normal : {r}"
    assert r["regarde"] is True, "le char a disparu sous les yeux"
    assert r["nuit"] is False, "la nuit de déneigement, le char est resté dans la rue"
    assert r["auLot"] == ["#3a6fb0"], f"au lot : {r['auLot']} (un char d'un autre secteur ou dans sa case ?)"
    assert r["ailleursLa"] is True, "le char de l'autre secteur a disparu : le juge ne mesure rien"
    assert r["enCase"] in (True, "pas de case"), "un char dans sa case a disparu"


def test_les_panneaux_clignotent_et_la_ligne_du_bas_le_dit(banc):
    r = banc("function (L, o) {" + OPERATION + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        const s = jourDeTempete(L, 1), secteur = secteurDe(L, 1), o2 = L.Neige.donnees().deneigement;
        const p = o2.panneaux[secteur][0], j = L.B.joueur;
        j.x = p[0] * L.TT + 8; j.y = p[1] * L.TT + 8 + 16;
        const cam = { x: j.x - L.VW / 2, y: j.y - L.VH / 2 };
        function peindre(image) {
            const ctx = { fillStyle: '', orange: 0, n: 0, fillRect: function () { this.n++; if (this.fillStyle === '#ff9f1c') this.orange++; } };
            L.B.image = image;
            L.Neige.dessinerPanneaux(ctx, cam);
            return ctx;
        }
        regler(L, s + 1, 9);
        const avant = peindre(0).n;
        regler(L, s + 1, o2.annonce_h + 1);
        const allume = peindre(5), eteint = peindre(25);
        const texte = L.Neige.texteDInfo(j);
        regler(L, s + 1, o2.debut_h + 1);
        return { avant: avant, allume: allume.orange, eteint: eteint.orange, peint: allume.n, texte: texte, nuit: L.Neige.texteDInfo(j) };
    }""")
    assert r["avant"] == 0, "des panneaux avant l'annonce"
    assert r["peint"] > 0 and r["allume"] >= 1 and r["eteint"] == 0, r
    assert r["texte"].startswith("DÉNEIGEMENT CETTE NUIT"), r["texte"]
    assert r["nuit"].startswith("DÉNEIGEMENT EN COURS"), r["nuit"]


def test_la_charrue_sort_la_nuit_de_deneigement(banc):
    r = banc("function (L, o) {" + OPERATION + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        const s = jourDeTempete(L, 1), o2 = L.Neige.donnees().deneigement;
        regler(L, s + 1, o2.debut_h + 1);
        const nuit = { dehors: L.Neige.charrueDehors(), tempete: L.Neige.intensite() };
        regler(L, s + 1, 10);
        return { nuit: nuit, jour: L.Neige.charrueDehors() };
    }""")
    assert r["nuit"]["dehors"] is True and r["nuit"]["tempete"] == 0
    assert r["jour"] is False
