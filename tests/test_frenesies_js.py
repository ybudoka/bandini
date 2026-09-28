"""Les frénésies (P4) au banc : on marche sur l'icône, l'arme est prêtée, le chrono court.

⚠️ Chaque juge vide la rue autour de l'icône avant de compter : un passant ou un membre de
gang né là par hasard ferait compter (ou rater) autre chose que ce qu'on juge. Les morts se
donnent par `Entites.blesser` — le seul passage de toute blessure du jeu, celui qu'une balle
prend aussi : c'est là que l'enfant est refusé.
"""

AMENER = """
    function amener(L, o, slug) {
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        const f = L.Frenesies.toutes().find(function (q) { return q.slug === slug; });
        const p = L.Frenesies.position(f);
        const j = L.B.joueur;
        // Rien ni personne autour : on juge la frénésie, pas le quartier.
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
        j.x = p.x + 60; j.y = p.y; L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        return { f: f, p: p, j: j };
    }
    function surLIcone(L, o, a, n) {
        for (let i = 0; i < (n || 3); i++) { a.j.x = a.p.x; a.j.y = a.p.y; o.frame(1); }
    }
    function membre(L, a, gang) {
        const g = L.B.defs.pietons.gangs.find(function (q) { return q.slug === gang; });
        return L.Entites.creerPieton(a.j.x + 30, a.j.y, L.Entites.archetype(g.pieton));
    }
"""


def test_marcher_sur_l_icone_lance_la_frenesie_avec_l_arme_pretee(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cravates');
        let son = 0; const avant = L.Son.SFX.frenesie; L.Son.SFX.frenesie = function () { son++; };
        const armeAvant = a.j.arme, sacAvant = L.B.partie.armes.pistolet || null;
        const loin = !!L.B.frenesie;
        surLIcone(L, o, a);
        L.Son.SFX.frenesie = avant;
        const e = L.B.frenesie;
        // La roue ne la change pas : elle revient au poing à l'image suivante.
        a.j.arme = null; o.frame(1);
        return { loin: loin, en: e && e.slug, arme: a.j.arme, mun: L.B.partie.armes.pistolet && L.B.partie.armes.pistolet.mun,
                 armeAvant: armeAvant, sacAvant: sacAvant, son: son, ligne: L.Histoire.ligneObjectif(), msg: L.B.msg };
    }""")
    assert r["loin"] is False, "la frénésie part sans qu'on marche sur son icône"
    assert r["en"] == "cravates", r
    assert r["arme"] == "pistolet", "l'arme prêtée n'est pas au poing (ou la roue l'a changée)"
    assert r["mun"] >= 999, "l'arme prêtée tarit"
    assert r["son"] == 1, "la frénésie part sans son"
    assert r["ligne"].startswith("FRÉNÉSIE 0/10 CRAVATES"), r["ligne"]
    assert r["msg"].startswith("FRÉNÉSIE !"), r["msg"]


def test_elle_ne_part_ni_au_volant_ni_pendant_une_mission(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cravates');
        L.B.mission = { entites: [] };
        surLIcone(L, o, a);
        const pendantMission = !!L.B.frenesie, msg = L.B.msg;
        L.B.mission = null;
        // Encore sur l'icône : refusée, elle attend qu'on s'éloigne.
        surLIcone(L, o, a);
        const sansPartir = !!L.B.frenesie;
        a.j.x = a.p.x + 100; o.frame(2);
        // Au volant, on passe dessus sans la prendre.
        const v = L.Vehicules.creer('auto', a.p.x, a.p.y, 0, { couleur: '#888888' });
        L.Vehicules.monter(a.j, v);
        for (let i = 0; i < 3; i++) { v.x = a.p.x; v.y = a.p.y; a.j.x = a.p.x; a.j.y = a.p.y; o.frame(1); }
        const auVolant = !!L.B.frenesie;
        L.Vehicules.descendre(a.j);
        v.x = a.p.x + 400; v.y = a.p.y;                   // le char s'en va : il ne pousse plus personne
        a.j.x = a.p.x + 100; o.frame(2);
        surLIcone(L, o, a);
        return { pendantMission: pendantMission, msg: msg, sansPartir: sansPartir, auVolant: auVolant, apres: !!L.B.frenesie };
    }""")
    assert r["pendantMission"] is False, "une frénésie part pendant une mission"
    assert "MISSION" in r["msg"], r["msg"]
    assert r["sansPartir"] is False, "l'icône refusée repart sans qu'on s'éloigne"
    assert r["auVolant"] is False, "une frénésie se prend au volant"
    assert r["apres"] is True, "à pied, hors mission, l'icône ne part pas"


def test_les_enfants_ne_comptent_jamais_ni_les_passants(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cravates');
        surLIcone(L, o, a);
        const enfant = L.Entites.creerPieton(a.j.x + 20, a.j.y, L.Entites.archetype('enfant'));
        L.Entites.blesser(enfant, 999, a.j, {});
        const enfantVivant = enfant.vivant;
        // Même si la règle du moteur sautait : la frénésie ne compte pas un intouchable.
        L.Entites.tuer(enfant, a.j);
        const apresEnfant = L.B.frenesie.compte;
        const passant = L.Entites.creerPieton(a.j.x + 20, a.j.y + 10, L.Entites.archetype('livreur'));
        L.Entites.blesser(passant, 999, a.j, {});
        const apresPassant = L.B.frenesie.compte;
        const m = membre(L, a, 'morues');                 // une autre gang que celle visée
        L.Entites.blesser(m, 999, a.j, {});
        const apresAutreGang = L.B.frenesie.compte;
        // ⚠️ Un intouchable PORTÉ PAR LA GANG visée (un cas qui n'existe pas, écrit pour que la
        // règle se voie seule) : la frénésie ne le compte pas davantage.
        const petit = L.Entites.creerPieton(a.j.x + 20, a.j.y - 10, L.Entites.archetype('enfant'));
        petit.gang = 'cravates';
        L.Entites.tuer(petit, a.j);
        const apresPetitDeGang = L.B.frenesie.compte;
        const c = membre(L, a, 'cravates');
        L.Entites.blesser(c, 999, a.j, {});
        L.Entites.tuer(c, a.j);                          // un mort ne compte qu'une fois
        return { enfantVivant: enfantVivant, apresEnfant: apresEnfant, passantMort: !passant.vivant, apresPetitDeGang: apresPetitDeGang,
                 apresPassant: apresPassant, apresAutreGang: apresAutreGang, apresCravate: L.B.frenesie.compte };
    }""")
    assert r["enfantVivant"] is True, "un enfant est mort pendant une frénésie"
    assert r["apresEnfant"] == 0, "la frénésie a compté un enfant"
    assert r["passantMort"] is True
    assert r["apresPassant"] == 0, "la frénésie de gang compte un passant"
    assert r["apresAutreGang"] == 0, "la frénésie compte une autre gang"
    assert r["apresPetitDeGang"] == 0, "la frénésie compte un intouchable de la gang visée"
    assert r["apresCravate"] == 1, "la frénésie ne compte pas la gang visée (ou deux fois le même mort)"


def test_reussie_elle_paie_une_fois_rend_l_arme_se_sauvegarde_et_ne_revient_plus(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cravates');
        L.B.partie.armes.pistolet = { mun: 7, usure: 0 };
        a.j.arme = 'batte'; L.B.partie.armes.batte = { mun: null, usure: 0 };
        const argent = L.B.partie.argent;
        let fin = 0; const avant = L.Son.SFX.frenesie_fin; L.Son.SFX.frenesie_fin = function () { fin++; };
        surLIcone(L, o, a);
        for (let i = 0; i < 10; i++) { const c = membre(L, a, 'cravates'); L.Entites.blesser(c, 999, a.j, {}); }
        L.Son.SFX.frenesie_fin = avant;
        const gagne = L.B.partie.argent - argent;
        const carnet = L.B.partie.carnet.map(function (l) { return l.t; });
        const arme = a.j.arme, mun = L.B.partie.armes.pistolet.mun;
        L.Missions.sauvegarderPartie();
        const relue = L.Sauvegarde.lire();
        a.j.x = a.p.x + 100; o.frame(2);
        surLIcone(L, o, a);
        return { en: !!L.B.frenesie, gagne: gagne, fin: fin, arme: arme, mun: mun,
                 carnet: carnet, sauvee: !!(relue && relue.frenesies && relue.frenesies.cravates) };
    }""")
    from app import frenesies
    prime = next(f["prime"] for f in frenesies.FRENESIES if f["slug"] == "cravates")
    assert r["gagne"] == prime, f"la frénésie réussie n'a pas payé sa prime : {r['gagne']}"
    assert r["fin"] == 1, "la frénésie réussie finit sans son"
    assert r["arme"] == "batte" and r["mun"] == 7, "l'arme prêtée n'est pas rendue (ou le sac d'avant est perdu)"
    assert any("FRÉNÉSIE RÉUSSIE" in t for t in r["carnet"]), "le carnet ne dit rien de la frénésie"
    assert r["sauvee"], "la frénésie réussie ne se sauvegarde pas"
    assert r["en"] is False, "une frénésie réussie revient"


def test_le_temps_ecoule_la_rate_et_on_peut_la_reprendre(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'chevreuils');
        delete L.B.partie.armes.batte;
        a.j.arme = null;
        surLIcone(L, o, a);
        L.B.frenesie.t = a.f.chrono_s * 60;
        o.frame(2);
        const ratee = !L.B.frenesie, msg = L.B.msg;
        const garde = !!L.B.partie.armes.batte, arme = a.j.arme;
        surLIcone(L, o, a);
        const tout_de_suite = !!L.B.frenesie;
        a.j.x = a.p.x + 100; o.frame(2);
        surLIcone(L, o, a);
        return { ratee: ratee, msg: msg, garde: garde, arme: arme, tout_de_suite: tout_de_suite, reprise: !!L.B.frenesie,
                 reussie: !!L.B.partie.frenesies.chevreuils };
    }""")
    assert r["ratee"], "le chrono passé, la frénésie court encore"
    assert "TEMPS" in r["msg"], r["msg"]
    assert r["garde"] is False and r["arme"] is None, "la batte prêtée reste au joueur"
    assert r["tout_de_suite"] is False, "la frénésie ratée repart sans qu'on s'éloigne"
    assert r["reprise"] is True, "la frénésie ratée ne se reprend pas"
    assert r["reussie"] is False


def test_la_sauvegarde_pendant_la_frenesie_n_emporte_pas_l_arme(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'morues');
        delete L.B.partie.armes.fusil;
        a.j.arme = null;
        surLIcone(L, o, a);
        L.Missions.sauvegarderPartie();
        const relue = L.Sauvegarde.lire();
        return { en: !!L.B.frenesie, fusil: !!(relue.armes && relue.armes.fusil), arme: relue.arme,
                 enJeu: !!L.B.partie.armes.fusil };
    }""")
    assert r["en"] and r["enJeu"]
    assert r["fusil"] is False, "la sauvegarde écrite pendant la frénésie garde le fusil prêté"
    assert r["arme"] != "fusil"


def test_une_frenesie_de_chars_compte_ce_que_le_joueur_detruit(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'casse');
        surLIcone(L, o, a);
        const arme = a.j.arme;
        const v1 = L.Vehicules.creer('auto', a.p.x + 200, a.p.y, 0, { couleur: '#888888' });
        L.Vehicules.endommager(v1, 999, a.j);
        const parLeJoueur = L.B.frenesie.compte;
        const v2 = L.Vehicules.creer('auto', a.p.x + 200, a.p.y + 200, 0, { couleur: '#888888' });
        L.Vehicules.endommager(v2, 999, null);
        const tomber = L.B.frenesie.compte;
        const passant = L.Entites.creerPieton(a.j.x + 20, a.j.y, L.Entites.archetype('livreur'));
        L.Entites.blesser(passant, 999, a.j, {});
        return { arme: arme, parLeJoueur: parLeJoueur, tomber: tomber, passant: L.B.frenesie.compte };
    }""")
    assert r["arme"] == "molotov"
    assert r["parLeJoueur"] == 1, "le char détruit par le joueur ne compte pas"
    assert r["tomber"] == 1, "un char détruit sans le joueur compte"
    assert r["passant"] == 1, "une frénésie de chars compte un passant"


def test_la_gang_rapplique_et_l_hopital_la_rate(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'skateux');
        surLIcone(L, o, a);
        for (let i = 0; i < 400; i++) { a.j.vie = a.j.vieMax; o.frame(1); if (!L.B.frenesie) break; }
        const la = L.Entites.pietonsAutour(a.j.x, a.j.y, L.Entites.BULLE_OUBLI).filter(function (q) {
            return q.vivant && q.gang === 'skateux' && q.frenesie === 'skateux';
        }).length;
        const enCours = !!L.B.frenesie;
        L.Missions.hopital(null);
        return { la: la, enCours: enCours, apres: !!L.B.frenesie, msg: L.B.msg, couteau: !!L.B.partie.armes.couteau };
    }""")
    assert r["enCours"], "la frénésie s'est arrêtée toute seule"
    assert r["la"] >= 3, f"la gang visée ne rapplique pas pendant la frénésie : {r['la']}"
    assert r["apres"] is False, "l'hôpital ne rate pas la frénésie"


def test_le_bilan_compte_les_frenesies(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cravates');
        L.B.partie.frenesies = { cravates: { jour: 1, temps: 10 } };
        const bilan = L.Hud.menuBilan();
        const l = bilan.items.find(function (i) { return i.libelle === 'FRÉNÉSIES'; });
        return { detail: l && l.detail, n: L.Frenesies.toutes().length };
    }""")
    assert r["detail"] == f"1 / {r['n']}", r
