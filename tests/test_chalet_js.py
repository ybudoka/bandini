"""Le chalet du rang : la deuxième planque, dans un bloc de carte (vague 3 des blocs). Il
s'achète, on y dort, une partie s'y réveille, son char revient avec elle, et le bloc se
souvient de ce qu'on y laisse. Voir `app/blocs/chalet.py`."""

OUTILS = """
  const TT = 16;
  async function laisser(L, o, n) { for (let i = 0; i < (n || 6); i++) { o.frame(1); await o.attendre(); } }
  function fermer(L) { if (L.B.menu) L.Hud.fermerMenu(); }
  // Au passage de l'ouest des Quais, on pousse vers la gauche : le chalet.
  async function auChalet(L, o) {
    const B = L.B, j = B.joueur;
    fermer(L);
    j.x = 20; j.y = 166 * TT + 8; L.Entites.indexer();
    await laisser(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.bloc; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 80; i++) o.frame(1);
    return B.bloc && B.bloc.slug;
  }
  function entrerDansLeChalet(L, o) {
    const B = L.B, j = B.joueur, porte = L.Monde.carte.def.portes[0];
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10; L.Entites.indexer();
    L.Jeu.entrer(porte);
    for (let i = 0; i < 80 && (B.transition || !B.interieur); i++) o.frame(1);
    for (let i = 0; i < 30; i++) o.frame(1);
    return B.interieur && B.interieur.slug;
  }
  function menuDu(L, type) {
    const pt = L.B.interieur.points.find(function (q) { return q.type === type; });
    return L.Missions.menuDuPoint(pt);
  }
  function libelles(menu) { return menu.items.map(function (i) { return i.libelle; }); }
  // Rouvrir la partie telle qu'elle est sauvegardée, comme au titre : JOUER.
  async function rouvrir(L, o) {
    const p = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.B.partie)), L.B.defs);
    L.B.partie = p;
    L.Jeu.commencer();
    for (let i = 0; i < 60; i++) { o.frame(1); if (i % 5 === 0) await o.attendre(); }
    fermer(L);
  }
"""


def test_le_chalet_s_achete_avant_de_servir(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie;
        const bloc = await auChalet(L, o);
        const piece = entrerDansLeChalet(L, o);
        p.argent = 1000;
        const pauvre = menuDu(L, 'lit');
        const avant = { lit: libelles(pauvre), actif: pauvre.items[0].actif, coffre: libelles(menuDu(L, 'coffre')) };
        p.argent = 3000;
        const menu = menuDu(L, 'lit');
        menu.items[0].faire();
        const apres = { planques: p.planques.slice(), argent: p.argent, lit: libelles(menuDu(L, 'lit')) };
        return { bloc: bloc, piece: piece, avant: avant, apres: apres };
    }""")
    assert r["bloc"] == "chalet" and r["piece"] == "chalet", r
    assert r["avant"]["lit"] == ["ACHETER LE CHALET DU RANG"] and r["avant"]["actif"] is False, r["avant"]
    assert r["avant"]["coffre"] == ["ACHETER LE CHALET DU RANG"], "le coffre d'un chalet qui n'est pas à toi"
    assert r["apres"]["planques"] == ["chalet"] and r["apres"]["argent"] == 500, r["apres"]
    assert "DORMIR JUSQU’AU MATIN" in r["apres"]["lit"], r["apres"]


def test_on_dort_au_chalet_et_la_partie_s_y_reveille_avec_son_char(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, j = B.joueur;
        await auChalet(L, o);
        p.planques.push('chalet');
        const place = B.bloc.def.bloc.planque.char;
        const v = L.Vehicules.creer('cabriolet', place.x * TT + 8, place.y * TT + 8, 0, { etat: 'stationne' });
        v.couleur = '#ff77cc';
        entrerDansLeChalet(L, o);
        L.Missions.sauvegarderPartie();
        const sauve = { bloc: p.bloc, char: p.charsDesPlanques.chalet, x: p.x, y: p.y };
        await rouvrir(L, o);
        // ⚠️ `commencer` crée un joueur NEUF : on relit `B.joueur`.
        const k = B.joueur;
        const w = B.entites.find(function (e) { return e.type === 'vehicule' && e.slug === 'cabriolet'; });
        const porte = L.Monde.carte.def.portes[0];
        return { sauve: sauve, bloc: B.bloc && B.bloc.slug, noir: !!B.transition,
                 pres: Math.round(Math.hypot(k.x - (porte.x * TT + 8), k.y - (porte.y + 1) * TT) / TT),
                 char: w ? { couleur: w.couleur, d: Math.round(Math.hypot(w.x - v.x, w.y - v.y)) } : null };
    }""")
    s = r["sauve"]
    assert s["bloc"] and s["bloc"]["slug"] == "chalet", f"la sauvegarde ne sait pas qu'on dort au chalet : {s}"
    assert s["x"] < 40 and 160 * 16 < s["y"] < 172 * 16, f"le repli reste le passage en ville : {s}"
    assert s["char"] and s["char"]["slug"] == "cabriolet", s
    assert r["bloc"] == "chalet" and r["noir"] is False, f"rouverte, la partie se réveille au chalet : {r}"
    assert r["pres"] <= 2, f"devant la porte du chalet : {r}"
    assert r["char"] == {"couleur": "#ff77cc", "d": 0}, f"le char de la planque revient : {r}"


def test_hors_ligne_le_reveil_retombe_au_passage_en_ville_sans_rester_au_noir(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, j = B.joueur;
        await auChalet(L, o);
        p.planques.push('chalet');
        L.Missions.sauvegarderPartie();
        const passage = { x: p.x, y: p.y };
        // Une autre page : le navigateur n'a pas la carte du chalet, et le réseau est mort.
        delete L.Blocs.cartes.chalet;
        await rouvrir(L, o);
        for (let i = 0; i < 700; i++) o.frame(1);
        return { bloc: !!B.bloc, noir: !!B.transition, d: Math.round(Math.hypot(j.x - passage.x, j.y - passage.y)) };
    }""", blocs_panne=99)
    assert r["noir"] is False, "un réseau mort a laissé l'écran noir"
    assert r["bloc"] is False and r["d"] < 24, f"on se réveille au passage en ville : {r}"


def test_le_bloc_se_souvient_du_char_qu_on_y_laisse(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        await auChalet(L, o);
        const v = L.Vehicules.creer('auto', 22 * TT + 8, 21 * TT + 8, 0, { etat: 'stationne' });
        // On repart à pied par le rang, et on revient.
        const r0 = B.bloc.def.bloc.retour;
        j.x = (L.Monde.carte.w - 2) * TT; j.y = (r0.de + 1) * TT + 8; L.Entites.indexer();
        o.touche('KeyD'); for (let i = 0; i < 120 && B.bloc; i++) o.frame(1); o.relacher('KeyD');
        for (let i = 0; i < 80; i++) o.frame(1);
        const sorti = !B.bloc && B.entites.indexOf(v) < 0;
        await auChalet(L, o);
        return { sorti: sorti, revenu: !!B.bloc, meme: B.entites.indexOf(v) >= 0,
                 arbres: B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'arbre'; }).length };
    }""")
    assert r["sorti"] is True
    assert r["revenu"] is True and r["meme"] is True, f"le char laissé au chalet a disparu : {r}"
    assert r["arbres"] > 100, "les arbres une fois, pas deux"


def test_sauvegarder_au_chalet_n_oublie_pas_le_char_de_la_planque_de_rocco(banc):
    """⚠️ La porte de la planque de Rocco se cherchait dans la carte COURANTE : au chalet,
    elle n'y était pas, et le char qui l'attendait était oublié à chaque sauvegarde."""
    # ⚠️ On entre dans le bloc SANS s'éloigner de la planque : la ville oublie un char garé
    # loin du joueur (chalet ou pas), et le juge ne jugerait que cet oubli-là.
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, j = B.joueur;
        fermer(L);
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'planque'; });
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10; L.Entites.indexer();
        L.Vehicules.creer('taxi', porte.x * TT + 8, (porte.y + 2) * TT + 8, 0, { etat: 'stationne' });
        L.Missions.sauvegarderPartie();
        const enVille = p.planque.vehicule && p.planque.vehicule.slug;
        L.Blocs.charger('chalet'); await laisser(L, o);
        const b = L.Blocs.liste().find(function (q) { return q.slug === 'chalet'; });
        L.Jeu.passerDansLeBloc(b, L.Blocs.cartes.chalet, { x: j.x, y: j.y }, null);
        L.Missions.sauvegarderPartie();
        return { enVille: enVille, auChalet: p.planque.vehicule && p.planque.vehicule.slug };
    }""")
    assert r == {"enVille": "taxi", "auChalet": "taxi"}, r


def test_tombe_au_chalet_on_va_a_l_hopital_et_le_chalet_garde_le_char(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await auChalet(L, o);
        const v = L.Vehicules.creer('auto', 22 * TT + 8, 21 * TT + 8, 0, { etat: 'stationne' });
        entrerDansLeChalet(L, o);
        L.Missions.hopital('test');
        for (let i = 0; i < 400 && B.transition; i++) o.frame(1);
        const hopital = B.interieur && B.interieur.slug;
        return { hopital: hopital, bloc: !!B.bloc, garde: (L.Blocs.enMemoire('chalet') || []).indexOf(v) >= 0 };
    }""")
    assert r == {"hopital": "hopital", "bloc": False, "garde": True}, r


def test_au_reveil_le_noir_attend_la_carte_du_chalet(banc):
    """Une page neuve n'a pas la carte du chalet : le réveil la demande, et le noir TIENT
    le temps qu'elle arrive — sans quoi on se réveillait au passage en ville."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie;
        await auChalet(L, o);
        p.planques.push('chalet');
        L.Missions.sauvegarderPartie();
        delete L.Blocs.cartes.chalet;
        const p2 = L.Sauvegarde.completer(JSON.parse(JSON.stringify(B.partie)), B.defs);
        B.partie = p2;
        L.Jeu.commencer();
        o.frame(1); o.frame(1);
        const noirTenu = !!B.transition && !B.bloc;
        for (let i = 0; i < 60; i++) { o.frame(1); if (i % 5 === 0) await o.attendre(); }
        return { noirTenu: noirTenu, bloc: B.bloc && B.bloc.slug };
    }""")
    assert r == {"noirTenu": True, "bloc": "chalet"}, r
