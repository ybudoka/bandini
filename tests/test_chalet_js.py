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


def test_dedans_c_est_un_chalet_et_le_foyer_brule(banc):
    """Martin, 26 sept. 2026 : « Remanie l'intérieur et ajoute un foyer au chalet. Je veux que ça
    ait vraiment l'air d'être un chalet. » Avant : la planque de Rocco en plus petit — murs de
    brique, classeur de bureau, cuisinière blanche, plantes en pot. Maintenant : des rondins, le
    foyer de pierre sous sa cheminée, la corde de bois, la peau d'ours, les berçantes, le panache
    et les raquettes au mur ; les meubles de la ville repeints en camp (`materiaux`) — chacun a son
    peintre. Et le FEU danse : deux images, deux feux (il ne se cuit pas dans la tuile)."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await auChalet(L, o);
        const piece = entrerDansLeChalet(L, o);
        const c = L.Monde.carte, sol = c.sol.join('\\n');
        const mats = c.materiaux || {};
        const sansPeintre = Object.keys(mats).filter(function (g) { return !L.TUILES[g + '@' + mats[g]]; });
        function feu(t) {
            B.t = t;
            const ctx = L.Base.nouveauCanvas(400, 400).getContext('2d'); ctx.traces = [];
            L.Monde.dessinerFoyers(ctx, { x: 0, y: 0 });
            return ctx.traces.filter(function (q) { return q[4] === '#c8401e'; }).map(function (q) { return q[3]; }).join(',');
        }
        return { piece: piece, sol: sol, mats: mats, sansPeintre: sansPeintre,
                 foyers: (c.foyers || []).length ? c.foyers : (feu(0), c.foyers),
                 feu1: feu(10), feu2: feu(37),
                 points: B.interieur.points.map(function (q) { return [q.type, c.sol[q.y][q.x]]; }) };
    }""")
    assert r["piece"] == "chalet", r
    sol = r["sol"]
    lignes = sol.split("\n")
    for g, quoi in (("Y", "le foyer"), ("K", "la cheminée"), ("L", "la corde de bois"), ("U", "la peau d'ours"),
                    ("V", "la berçante"), ("N", "le panache"), ("&", "les raquettes")):
        assert g in sol, f"{quoi} manque au chalet"
    for g, quoi in (("n", "une plante en pot"), ("j", "un frigo"), ("S", "un vidéopoker")):
        assert g not in sol, f"{quoi} dans un camp en bois rond"
    y = next(i for i, ligne in enumerate(lignes) if "YY" in ligne)
    x = lignes[y].index("YY")
    assert lignes[y - 1][x:x + 2] == "KK", "la cheminée monte au-dessus du foyer, dans le mur"
    assert r["mats"]["B"] == r["mats"]["W"] == r["mats"]["D"] == "bois_rond", "dedans aussi, des rondins"
    assert r["sansPeintre"] == [], f"un meuble repeint sans peintre : {r['sansPeintre']}"
    assert dict(r["points"]) == {"lit": "l", "coffre": "k", "garde_robe": "e"}, "la planque sert encore"
    assert r["foyers"] == [{"x": x, "y": y, "l": 2}], r["foyers"]
    assert r["feu1"] and r["feu2"] and r["feu1"] != r["feu2"], "le feu danse : deux images, deux feux"


def test_de_dehors_la_cheminee_fume(banc):
    """« Va plus loin » (Martin, 26 sept. 2026) : sur le rang, on sait de loin que le feu est
    allumé. La souche de pierre sort du toit au-dessus du foyer, et la fumée monte, grossit et
    dérive — d'après l'heure du jeu, jamais un dé : deux images, deux fumées."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await auChalet(L, o);
        const c = L.Blocs.cheminees();
        const vue = { x: c[0].x * TT - 120, y: c[0].y * TT - 120 };
        function peindre(quoi, t) {
            B.t = t;
            const ctx = L.Base.nouveauCanvas(400, 400).getContext('2d'); ctx.traces = [];
            quoi(ctx, vue);
            return ctx.traces;
        }
        const souche = peindre(L.Blocs.dessiner, 5).filter(function (q) { return q[4] === '#6e685e'; }).length;
        const f1 = peindre(L.Blocs.dessinerFumees, 10), f2 = peindre(L.Blocs.dessinerFumees, 60);
        const toit = L.Monde.carte.sol[c[0].y].slice(c[0].x, c[0].x + c[0].l);
        return { cheminees: c, souche: souche, toit: toit, f1: f1.length, pareil: JSON.stringify(f1) === JSON.stringify(f2),
                 monte: f1.every(function (q) { return q[1] < 120 + 8; }) };
    }""")
    assert len(r["cheminees"]) == 1, r
    assert r["toit"] == "PP", f"la souche sort du toit, pas du pré : {r['toit']}"
    assert r["souche"] >= 1, "la souche de pierre n'est pas peinte"
    assert r["f1"] > 0 and not r["pareil"], "la fumée ne bouge pas"
    assert r["monte"], "la fumée monte au-dessus de la souche"


def test_dedans_le_feu_crepite_plus_fort_pres_de_l_atre(banc):
    """Le crépitement (`foyer`, une boucle ElevenLabs) : on l'entend en entrant, plus fort à
    l'âtre qu'à la porte, et il s'éteint quand on ressort."""
    r = banc("async function (L, o) {" + OUTILS + """
        o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        const B = L.B;
        await auChalet(L, o);
        await o.attendre(); await o.attendre(); await o.attendre();
        entrerDansLeChalet(L, o);
        const j = B.joueur, f = L.Monde.foyersDeLaPiece()[0];
        function la(x, y) { j.x = x; j.y = y; L.Entites.indexer(); for (let i = 0; i < 4; i++) o.frame(1); return L.Son.volumeBoucle('foyer'); }
        const porte = L.Monde.carte.def.portes[0];
        const loin = la(porte.x * TT + 8, (porte.y - 1) * TT + 8);
        const pres = la((f.x + 1) * TT, (f.y + 1) * TT + 10);
        const charge = L.Son.estCharge('foyer');
        L.Jeu.sortir();
        for (let i = 0; i < 90; i++) o.frame(1);
        return { charge: charge, loin: loin, pres: pres, dehors: L.Son.boucleActive('foyer'), interieur: !!B.interieur };
    }""")
    assert r["charge"], "le fichier du feu ne se charge pas"
    assert r["loin"] and r["pres"] and r["pres"] > r["loin"], f"plus fort près de l'âtre : {r}"
    assert r["interieur"] is False and r["dehors"] is False, f"dehors, le feu se tait : {r}"
