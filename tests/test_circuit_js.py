"""Le labyrinthe électrifié du piratage (`static/js/circuit.js`, Martin, 27 sept. 2026 :
« je veux un jeu de labyrinthe électrifié ») — le module seul, sans mission : le tracé tiré
à l'empreinte, le pas de l'étincelle au stick, le zap contre un fil, le relais, le port.

⚠️ Aucun `B.rng` : le même labyrinthe à chaque essai (on l'apprend), et la ville ne bouge pas
parce qu'on a ouvert un terminal."""

# Un stick poussé à fond dans une direction, comme `Entree.axe` le rend au clavier.
AXES = """
    const AXE = { haut: { x: 0, y: -1, mag: 1 }, bas: { x: 0, y: 1, mag: 1 },
                  gauche: { x: -1, y: 0, mag: 1 }, droite: { x: 1, y: 0, mag: 1 },
                  rien: { x: 0, y: 0, mag: 0 } };
    const C = L.Circuit, CASE = C.CASE;
    const centre = function (c, r) { return { x: (c + 0.5) * CASE, y: (r + 0.5) * CASE }; };
"""


def test_le_trace_vient_de_l_empreinte_et_pas_du_hasard_de_la_ville(banc):
    r = banc("""function (L, o) {""" + AXES + """
        const avant = L.B.rng.etat ? L.B.rng.etat() : null;
        const tire = []; const vrai = L.B.rng; L.B.rng = function () { tire.push(1); return vrai(); };
        const a = C.generer('m53:2', 7, 4), b = C.generer('m53:2', 7, 4), c = C.generer('m53:4', 7, 4);
        L.B.rng = vrai;
        return { memes: JSON.stringify(a) === JSON.stringify(b), autre: JSON.stringify(a) !== JSON.stringify(c),
                 des: tire.length, taille: [a.cols, a.rangs] };
    }""")
    assert r["memes"], "la même empreinte ne redonne pas le même labyrinthe"
    assert r["autre"], "deux terminaux différents ont le même labyrinthe"
    assert r["des"] == 0, "le labyrinthe a tiré dans B.rng : la ville glisserait"
    assert r["taille"] == [7, 4]


def test_le_labyrinthe_est_parfait_et_la_solution_va_de_la_prise_au_port(banc):
    """Toutes les cases atteintes depuis la prise (un labyrinthe parfait : cols × rangs − 1
    passages), et la solution passe case à case par des passages OUVERTS."""
    r = banc("""function (L, o) {""" + AXES + """
        const sortie = [];
        ['m53:2', 'm53:4', 'm54:0', 'm54:3', 'm54:6'].forEach(function (emp) {
            const cols = emp.indexOf('m54') === 0 ? 8 : 7, p = C.generer(emp, cols, 4);
            const ouvert = function (a, b) {
                if (a.r === b.r && Math.abs(a.c - b.c) === 1) return p.est[a.r * p.cols + Math.min(a.c, b.c)];
                if (a.c === b.c && Math.abs(a.r - b.r) === 1) return p.sud[Math.min(a.r, b.r) * p.cols + a.c];
                return false;
            };
            let passages = 0;
            p.est.forEach(function (v) { if (v) passages++; }); p.sud.forEach(function (v) { if (v) passages++; });
            const s = p.solution, bout = s[s.length - 1];
            let suit = true;
            for (let i = 1; i < s.length; i++) if (!ouvert(s[i - 1], s[i])) suit = false;
            sortie.push({ emp: emp, passages: passages, attendu: p.cols * p.rangs - 1,
                          depart: s[0].c === 0 && s[0].r === p.entree, arrivee: bout.c === p.cols - 1 && bout.r === p.sortie,
                          suit: suit, relaisSurLeChemin: s.some(function (q) { return q.c === p.relais.c && q.r === p.relais.r; }) });
        });
        return sortie;
    }""")
    for p in r:
        assert p["passages"] == p["attendu"], f"{p['emp']} : pas un labyrinthe parfait ({p['passages']} passages)"
        assert p["depart"] and p["arrivee"], f"{p['emp']} : la solution ne va pas de la prise au port"
        assert p["suit"], f"{p['emp']} : la solution traverse un fil"
        assert p["relaisSurLeChemin"], f"{p['emp']} : le relais n'est pas sur le chemin"


def test_un_couloir_est_libre_et_un_fil_ou_un_poteau_touche(banc):
    r = banc("""function (L, o) {""" + AXES + """
        const p = C.generer('m53:2', 7, 4);
        const libres = [];
        for (let rr = 0; rr < p.rangs; rr++) for (let c = 0; c < p.cols; c++) {
            const m = centre(c, rr); libres.push(C.touche(p, m.x, m.y));
        }
        // Un fil : la bordure nord de la boîte, au-dessus de n'importe quelle case.
        const m = centre(3, 0);
        // Un poteau : le coin haut-gauche de la case (1, 1), même si ses deux côtés sont ouverts.
        return { libres: libres.some(Boolean), fil: C.touche(p, m.x, 1), poteau: C.touche(p, CASE, CASE),
                 largeur: CASE - C.FIL - 2 * C.RAYON };
    }""")
    assert not r["libres"], "le centre d'une case touche un fil"
    assert r["fil"], "la bordure de la boîte ne touche pas"
    assert r["poteau"], "un poteau au croisement ne touche pas"
    assert r["largeur"] >= 6, f"le couloir laisse {r['largeur']} px de jeu à l'étincelle : injouable au doigt"


def test_le_stick_pousse_l_etincelle_et_un_fil_la_zappe_au_relais(banc):
    r = banc("""function (L, o) {""" + AXES + """
        const p = C.generer('m53:2', 7, 4), e = C.ouvrir(p, 0);
        const depart = { x: e.x, y: e.y };
        // Au neutre, rien ne bouge.
        C.maj(e, AXE.rien);
        const neutre = e.x === depart.x && e.y === depart.y;
        // Tout droit vers le haut, au milieu du couloir : au pire la bordure de la boîte, quatre
        // cases plus haut — on finit toujours sur un fil.
        let res = null, n = 0;
        while (res !== 'zap' && n < 200) { res = C.maj(e, AXE.haut); n++; }
        const apres = { x: e.x, y: e.y, zaps: e.zaps };
        // Pendant l'immunité, collé ou pas, on ne recompte pas — et on ne bouge pas.
        let recompte = 0;
        for (let i = 0; i < C.IMMUNITE; i++) if (C.maj(e, AXE.haut) === 'zap') recompte++;
        return { neutre: neutre, res: res, n: n, retour: apres.x === depart.x && apres.y === depart.y,
                 zaps: apres.zaps, recompte: recompte, fige: e.x === depart.x && e.y === depart.y };
    }""")
    assert r["neutre"], "l'étincelle bouge au neutre"
    assert r["res"] == "zap" and r["n"] < 60, f"pousser tout droit vers le haut ne zappe pas ({r['n']} images)"
    assert r["retour"], "le zap ne ramène pas l'étincelle à la prise"
    assert r["zaps"] == 1
    assert r["recompte"] == 0, "un zap recompte pendant l'immunité"
    assert r["fige"], "l'étincelle bouge pendant l'immunité"


def test_suivre_la_solution_passe_le_relais_et_atteint_le_port(banc):
    """Le pilote du banc : un axe à la fois, du centre d'une case au centre de la suivante, comme
    le clavier le ferait. Un zap en chemin et on recommence depuis le relais."""
    r = banc("""function (L, o) {""" + AXES + """
        const p = C.generer('m54:3', 8, 4), e = C.ouvrir(p, 0);
        const vus = [];
        let fin = null, images = 0, relaisVu = false;
        for (let i = 1; i < p.solution.length && !fin; i++) {
            const cible = centre(p.solution[i].c, p.solution[i].r);
            for (let k = 0; k < 40 && !fin; k++) {
                const dx = cible.x - e.x, dy = cible.y - e.y;
                if (Math.abs(dx) < C.VITESSE / 2 + 0.05 && Math.abs(dy) < C.VITESSE / 2 + 0.05) break;
                const axe = Math.abs(dx) >= C.VITESSE / 2 + 0.05 ? (dx > 0 ? AXE.droite : AXE.gauche) : (dy > 0 ? AXE.bas : AXE.haut);
                const res = C.maj(e, axe); images++;
                if (res) vus.push(res);
                if (res === 'fini') fin = res;
            }
            if (e.relais) relaisVu = true;
        }
        // Le port est à droite de la dernière case : on pousse jusqu'à lui.
        for (let k = 0; k < 40 && !fin; k++) { const res = C.maj(e, AXE.droite); images++; if (res === 'fini') fin = res; }
        return { fin: fin, zaps: vus.filter(function (v) { return v === 'zap'; }).length, relaisVu: relaisVu, images: images };
    }""")
    assert r["zaps"] == 0, "suivre la solution au centre des couloirs a touché un fil"
    assert r["relaisVu"], "le relais n'a pas été retenu en passant"
    assert r["fin"] == "fini", f"l'étincelle n'atteint pas le port ({r['images']} images)"


def test_un_zap_apres_le_relais_ramene_au_relais(banc):
    r = banc("""function (L, o) {""" + AXES + """
        const p = C.generer('m53:2', 7, 4), e = C.ouvrir(p, 2);
        const m = centre(p.relais.c, p.relais.r);
        e.x = m.x; e.y = m.y; C.maj(e, AXE.rien);          // on y est : il est retenu,
        // …puis collé au poteau du coin haut-gauche de sa case (un poteau touche toujours).
        e.x = p.relais.c * CASE + 1; e.y = p.relais.r * CASE + 1;
        const vu = C.touche(p, e.x, e.y);
        const res = C.maj(e, AXE.rien);
        return { retenu: !!e.relais, vu: vu, res: res, zaps: e.zaps, x: e.x, y: e.y, m: m };
    }""")
    assert r["retenu"], "le relais n'est pas retenu"
    assert r["zaps"] == 3 and r["res"] == "zap", "les zaps repris à l'ouverture ne s'additionnent pas"
    assert (r["x"], r["y"]) == (r["m"]["x"], r["m"]["y"]), "le zap ne ramène pas au relais"
