"""Les bateaux ne sont pas des chars, vague 1 — la conduite : erre et gouvernail.

Une coque pivote au tiers avant (la poupe chasse), n'a pas de frein (l'arrière met la machine en arrière), n'a pas
de frein à main, et la météo de la rue — neige, verglas, pluie, pneus d'hiver — ne touche pas l'eau. Les feuilles
d'octobre ne se lèvent pas d'une coque. Tout se joue dans `Vehicules.majPhysique` (et `Pluie.majChar`)."""

#: Un jour d'été sans pluie (`jour = 21`, puis le premier jour sec) : la météo ne se mêle pas de la mesure — sauf là
#: où le juge la bouche exprès. Le plein large : de l'eau sur quatre tuiles autour, pour que rien ne s'échoue.
AIDES = """
    function sec(L) { L.B.partie.jour = 21; while (L.Pluie.journee(L.B.partie.jour)) L.B.partie.jour++; L.B.partie.heure = 0.5; }
    function pleinLarge(L) {
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -4; dy <= 4 && plein; dy++) for (let dx = -4; dx <= 4 && plein; dx++) if (!L.Monde.estEau(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8 };
        }
        return null;
    }
    function pleineRue(L) {
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -2; dy <= 2 && plein; dy++) for (let dx = -2; dx <= 2 && plein; dx++) if (!L.Monde.estRoute(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8 };
        }
        return null;
    }
    /** Un char du joueur posé en `p`, cap à l'est, lancé à `vitesse`. */
    function lance(L, slug, p, vitesse) {
        const v = L.Vehicules.creer(slug, p.x, p.y, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        v.conducteur = L.B.joueur; v.vitesse = vitesse; v.vx = vitesse; v.vy = 0;
        return v;
    }
    /** `n` images de `majPhysique` (sans `avancer` : le centre ne bouge que par le pivot). */
    function jouer(L, v, script, n) {
        const traj = [];
        for (let k = 0; k < n; k++) {
            L.Vehicules.majPhysique(v, Object.assign({ gaz: 0, frein: 0, direction: 0, freinMain: false }, script(k)));
            traj.push([v.x, v.y, v.angle, v.vx, v.vy, v.vitesse]);
        }
        return traj;
    }
"""


def test_la_poupe_chasse_le_nez_tient(banc):
    """Le même état joué dix images barre droite, puis dix images barre à fond : de combien l'étrave et la poupe
    s'écartent entre les deux. Une coque pivote au tiers avant — c'est la poupe qui balaie ; un char pivote sur
    son arrière — c'est le nez."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); sec(L);
        function ecarts(slug, p) {
            const bout = function (v, s) { const l = v.def.longueur / 2; return [v.x + s * Math.cos(v.angle) * l, v.y + s * Math.sin(v.angle) * l]; };
            const a = lance(L, slug, p, 2); jouer(L, a, function () { return {}; }, 10);
            const droit = { nez: bout(a, 1), poupe: bout(a, -1) }; L.Entites.retirer(a);
            const b = lance(L, slug, p, 2); b.volant = 1; jouer(L, b, function () { return { direction: 1 }; }, 10);
            const vire = { nez: bout(b, 1), poupe: bout(b, -1) }; L.Entites.retirer(b);
            const d = function (u, w) { return Math.hypot(u[0] - w[0], u[1] - w[1]); };
            return { nez: d(droit.nez, vire.nez), poupe: d(droit.poupe, vire.poupe) };
        }
        const eau = pleinLarge(L), rue = pleineRue(L);
        if (!eau || !rue) return { trouve: false };
        L.B.joueur.x = eau.x; L.B.joueur.y = eau.y - 64;
        return { trouve: true, coque: ecarts('bateau', eau), auto: ecarts('auto', rue) };
    }""")
    assert r["trouve"], "ni plein large ni pleine rue sur la carte"
    assert r["auto"]["nez"] > r["auto"]["poupe"], f"le char ne pivote plus sur son arrière : {r['auto']}"
    assert r["coque"]["poupe"] > 1.5 * r["coque"]["nez"], f"la coque balaie du nez comme un char : {r['coque']}"


def test_la_machine_arriere_ralentit_sans_frein_sec(banc):
    """Une chaloupe à 3 px/image, l'arrière à fond : la machine en arrière la ralentit, sans le frein d'un char
    (il l'arrêtait en 64 images), la vitesse descend à chaque image, puis elle recule jusqu'à son `vitesse_recul`."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); sec(L);
        const p = pleinLarge(L); L.B.joueur.x = p.x; L.B.joueur.y = p.y - 64;
        const v = lance(L, 'bateau', p, 3);
        const traj = jouer(L, v, function () { return { frein: 1 }; }, 900);
        let arret = -1, monte = 0;
        for (let k = 0; k < traj.length; k++) {
            if (arret < 0 && traj[k][5] <= 0) arret = k;
            if (k && traj[k][5] > traj[k - 1][5] + 1e-9) monte++;
        }
        return { arret: arret, monte: monte, fin: traj[traj.length - 1][5], recul: v.def.vitesse_recul };
    }""")
    assert r["arret"] > 100, f"la coque s'arrête en {r['arret']} images : un frein de char"
    assert r["monte"] == 0, "la vitesse remonte pendant la machine arrière"
    assert abs(r["fin"] + r["recul"]) < 0.05, f"la coque ne recule pas à sa vitesse de recul : {r}"


def test_sur_l_eau_le_frein_a_main_ne_fait_rien(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); sec(L);
        const p = pleinLarge(L); L.B.joueur.x = p.x; L.B.joueur.y = p.y - 64;
        const script = function (fm) { return function (k) { return { gaz: 1, direction: k < 30 ? 1 : 0, freinMain: fm }; }; };
        const a = lance(L, 'bateau', p, 2), sans = jouer(L, a, script(false), 60); L.Entites.retirer(a);
        const b = lance(L, 'bateau', p, 2), avec = jouer(L, b, script(true), 60); L.Entites.retirer(b);
        return { pareil: JSON.stringify(sans) === JSON.stringify(avec) };
    }""")
    assert r["pareil"], "le frein à main change la conduite d'une coque"


def test_la_neige_et_la_pluie_ne_touchent_pas_l_eau(banc):
    """Les cinq coefficients de la rue bouchés à 0,3, et des pneus d'hiver : la chaloupe fait la même trajectoire
    au pixel qu'au sec. L'auto, elle, change — sinon le bouchon ne mordrait pas."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); sec(L);
        const N = L.Neige, V = L.Verglas, P = L.Pluie, M = L.Monde;
        const vrais = [N.adherence, N.frein, V.adherence, V.frein, P.adherence, P.frein, M.adherenceMouillee, M.freinMouille];
        const script = function (k) { return { gaz: k < 40 ? 1 : 0, direction: k >= 20 && k < 50 ? 1 : 0, frein: k >= 60 ? 1 : 0 }; };
        function trajet(slug, p, mouille) {
            const bas = function () { return 0.3; };
            if (mouille) { N.adherence = N.frein = V.adherence = V.frein = P.adherence = P.frein = M.adherenceMouillee = M.freinMouille = bas; }
            const v = lance(L, slug, p, 2); if (mouille) v.mods = { pneus: true };
            const t = jouer(L, v, script, 90);
            [N.adherence, N.frein, V.adherence, V.frein, P.adherence, P.frein, M.adherenceMouillee, M.freinMouille] = vrais;
            L.Entites.retirer(v);
            return JSON.stringify(t);
        }
        const eau = pleinLarge(L), rue = pleineRue(L);
        L.B.joueur.x = eau.x; L.B.joueur.y = eau.y - 64;
        return { coque: trajet('bateau', eau, false) === trajet('bateau', eau, true),
                 auto: trajet('auto', rue, false) === trajet('auto', rue, true) };
    }""")
    assert not r["auto"], "le bouchon de la météo ne mord pas sur l'auto"
    assert r["coque"], "la neige ou la pluie change la conduite d'une coque"


def test_en_octobre_une_coque_ne_souleve_pas_de_feuilles(banc):
    """`Pluie.majChar` soulève les feuilles d'octobre derrière un char lancé — pas derrière une coque. L'auto posée
    au même endroit en soulève (le juge d'octobre de la pluie) : la mesure voit bien des feuilles."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        L.B.partie.jour = 32; L.B.partie.heure = 0.5;
        const p = pleinLarge(L);
        L.B.joueur.x = p.x; L.B.joueur.y = p.y; L.Monde.centrerCamera(p.x, p.y);
        function compte(slug) {
            const v = lance(L, slug, p, 3), avant = L.B.particules.length;
            for (let k = 0; k < 40; k++) { L.B.t++; L.Pluie.majChar(v); }
            L.Entites.retirer(v);
            return L.B.particules.length - avant;
        }
        return { coque: compte('bateau'), auto: compte('auto') };
    }""")
    assert r["auto"] > 0, f"la mesure ne voit pas de feuilles : {r}"
    assert r["coque"] == 0, f"une coque soulève {r['coque']} feuilles mortes sur l'eau"
