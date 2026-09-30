"""Les bateaux ne sont pas des chars, vagues 3 et 4 — le plongeon, la police de terre, et la vedette.

Descendre au large, c'est plonger. Un agent à la nage ne sort personne d'une coque, une auto-patrouille ne fonce
pas dans la baie, et aucun barrage de rue n'attend une coque : c'est la VEDETTE qui te prend sur l'eau."""

AIDES = """
    function pleinLarge(L) {
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -4; dy <= 4 && plein; dy++) for (let dx = -4; dx <= 4 && plein; dx++) if (!L.Monde.estEau(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8, tx: tx, ty: ty };
        }
        return null;
    }
    /** Le joueur a la barre d'une chaloupe posee en `p`, cap `angle`, lancee a `vitesse`. */
    function aLaBarre(L, p, angle, vitesse) {
        const j = L.B.joueur, v = L.Vehicules.creer('bateau', p.x, p.y, angle || 0, { etat: 'stationne' });
        j.x = p.x; j.y = p.y; L.Monde.centrerCamera(p.x, p.y);
        L.Vehicules.monter(j, v); v.vole = true;
        v.vitesse = vitesse || 0; v.vx = Math.cos(v.angle) * v.vitesse; v.vy = Math.sin(v.angle) * v.vitesse;
        return v;
    }
    const FLECHES = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
    /** Une voie de la rue (sa fleche) et, dans l'axe `k` tuiles plus loin, de l'eau franche (3 x 3). */
    function voieFaceALEau(L, kMin, kMax, libre) {
        const c = L.Monde.carte, M = L.Monde, TT = L.TT;
        const eauFranche = function (x, y) { for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (!M.estEau(x + dx, y + dy)) return false; return true; };
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            const f = M.fleche(tx, ty);
            if (!FLECHES[f] || !M.estChaussee(tx, ty)) continue;
            for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) for (let k = kMin; k <= kMax; k++) {
                const wx = tx + d[0] * k, wy = ty + d[1] * k;
                if (wx < 2 || wy < 2 || wx >= c.w - 2 || wy >= c.h - 2 || !eauFranche(wx, wy)) continue;
                if (libre && !M.ligneLibre(tx * TT + 8, ty * TT + 8, wx * TT + 8, wy * TT + 8)) continue;
                return { rue: { x: tx * TT + 8, y: ty * TT + 8, f: f }, eau: { x: wx * TT + 8, y: wy * TT + 8 }, vers: Math.atan2(-d[1], -d[0]) };
            }
        }
        return null;
    }
"""


# --- Vague 3 : le plongeon, et la police de terre -------------------------------------------------------------


def test_descendre_au_large_c_est_plonger(banc):
    """Au plein large, lancé : on saute à l'eau par le travers, et la coque file sur son erre, sans être
    « laissée » (la fourrière n'a rien à y voir)."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, v = aLaBarre(L, p, 0, 2);
        const ok = L.Vehicules.descendre(j);
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { ok: ok, aBord: !!j.dansVehicule, aLEau: L.Monde.estEau(tx, ty), ecart: Math.hypot(j.x - v.x, j.y - v.y),
                 vitesse: v.vitesse, laisse: !!v.laisse };
    }""")
    assert r["ok"] and not r["aBord"], f"on ne descend pas d'une coque lancée : {r}"
    assert r["aLEau"], f"le plongeon ne met pas le joueur à l'eau : {r}"
    assert r["ecart"] > 8, f"le joueur plonge dans la coque : {r}"
    assert r["vitesse"] > 1.5, f"la coque s'arrête quand on plonge : {r}"
    assert not r["laisse"], "une coque quittée au large est « laissée » pour la fourrière"


def test_un_agent_a_la_nage_ne_sort_personne_d_une_coque(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, v = aLaBarre(L, p, 0, 0);
        L.B.recherche.etoiles = 1;
        const a = L.Police.creerAgent(p.x + 16, p.y + 10, 'poursuit');
        for (let k = 0; k < 60; k++) { a.vuT = 0; L.Police.gere(a); }
        return { aBord: j.dansVehicule === v, ecart: Math.hypot(a.x - v.x, a.y - v.y) };
    }""")
    assert r["aBord"], f"un agent à la nage sort le joueur de sa coque : {r}"


def test_une_auto_patrouille_ne_fonce_pas_dans_la_baie(banc):
    """Le joueur en chaloupe à moins de 140 px d'une voie du quai, à vue : l'auto-patrouille garde les rails
    au lieu de foncer tout droit dans l'eau."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const q = voieFaceALEau(L, 4, 8, true);
        if (!q) return { trouve: false };
        aLaBarre(L, q.eau, 0, 0);
        L.B.recherche.etoiles = 2;
        const pas = FLECHES[q.rue.f];
        const v = L.Vehicules.creer('police', q.rue.x, q.rue.y, Math.atan2(pas[1], pas[0]),
                                    { conducteur: 'police', etat: 'roule', sirene: true, surRails: true, poursuite: true, sens: q.rue.f });
        return { trouve: true, c: L.Police.commandes(v) };
    }""")
    assert r["trouve"], "aucune voie de rue face à l'eau à vue"
    assert r["c"] == "rails", f"l'auto-patrouille fonce dans la baie : {r['c']}"


def test_aucun_barrage_de_rue_pour_une_coque(banc):
    """Trois étoiles, une coque lancée droit sur une voie : pas de barrage (sur une auto, au même endroit, il y en a
    un — sinon le juge ne voit rien)."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const q = voieFaceALEau(L, 18, 24, false);
        if (!q) return { trouve: false };
        const j = L.B.joueur;
        L.B.recherche.etoiles = 5;
        function barrages(slug) {
            const v = L.Vehicules.creer(slug, q.eau.x, q.eau.y, q.vers, { etat: 'stationne' });
            j.x = v.x; j.y = v.y; j.dansVehicule = v; v.conducteur = j; v.vitesse = 2;
            L.Police.barrages().forEach(function (b) { L.Entites.retirer(b); });
            L.B.recherche.etoiles = 5; L.B.recherche.renforts = 5;
            L.B.t = 900 * 50; L.Police.maj();
            const n = L.Police.barrages().length;
            j.dansVehicule = null; v.conducteur = null; L.Entites.retirer(v);
            return n;
        }
        return { trouve: true, auto: barrages('auto'), coque: barrages('bateau') };
    }""")
    assert r["trouve"], "aucune voie de rue face à l'eau"
    assert r["auto"] > 0, f"même une auto n'a pas de barrage : le juge ne mesure rien ({r})"
    assert r["coque"] == 0, "un barrage de rue attend une coque"


# --- Vague 4 : la vedette de police ---------------------------------------------------------------------------

VEDETTES = """
    function vedettes(L) { return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'vedette' && e.etat !== 'epave'; }); }
    /** `n` images de la vedette seule (sa naissance et son abordage), sans faire tourner la ville. */
    function majVedette(L, n) { for (let k = 0; k < n; k++) { L.B.t++; L.Vedette.maj(); } }
"""


def test_la_vedette_est_une_coque_de_police(paquet):
    v = next((q for q in paquet["vehicules"] if q["slug"] == "vedette"), None)
    assert v is not None, "pas de vedette au parc"
    assert v["eau"] and v["police"] and v["sirene"], v
    assert v["frequence"] == 0, "la vedette naît dans le trafic de rue"
    chaloupe = next(q for q in paquet["vehicules"] if q["slug"] == "bateau")
    assert v["vitesse_max"] > chaloupe["vitesse_max"], "la vedette ne rattrape pas une chaloupe"


def test_on_veut_une_vedette_seulement_quand_on_est_recherche_sur_l_eau(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, R = L.B.recherche, V = L.Vedette;
        const res = {};
        R.etoiles = 3; j.x = p.x; j.y = p.y; res.aPied = V.voulues();
        aLaBarre(L, p, 0, 0);
        R.etoiles = 0; res.sansEtoile = V.voulues();
        R.etoiles = 1; res.une = V.voulues();
        R.etoiles = 3; res.trois = V.voulues();
        return res;
    }""")
    assert r == {"aPied": 0, "sansEtoile": 0, "une": 1, "trois": 2}, r


def test_la_vedette_nait_hors_champ_sur_l_eau_qui_mene_au_joueur(banc):
    r = banc("function (L, o) {" + AIDES + VEDETTES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), R = L.B.recherche;
        aLaBarre(L, p, 0, 0);
        R.etoiles = 1; majVedette(L, 90);
        const une = vedettes(L).map(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            return { eau: L.Monde.estEau(tx, ty), vue: L.Entites.visibleAEcran(v.x, v.y, 0), jointe: L.Vedette.distance(tx, ty) >= 0, sirene: !!v.sirene };
        });
        R.etoiles = 3; majVedette(L, 90);
        return { une: une, trois: vedettes(L).length };
    }""")
    assert len(r["une"]) == 1, f"une étoile en chaloupe : {len(r['une'])} vedettes"
    v = r["une"][0]
    assert v["eau"] and v["jointe"], f"la vedette naît hors de l'eau qui mène au joueur : {v}"
    assert not v["vue"], "la vedette naît sous les yeux du joueur"
    assert v["sirene"], "la vedette chasse sans sa sirène"
    assert r["trois"] == 2, f"trois étoiles : {r['trois']} vedettes"


def test_la_vedette_rattrape_une_chaloupe_arretee_et_l_arraisonne(banc):
    """La ville entière qui tourne, deux étoiles tenues : la vedette naît, rejoint la chaloupe par l'eau, sans
    jamais toucher la terre, et l'arraisonne en moins de vingt secondes."""
    r = banc("function (L, o) {" + AIDES + VEDETTES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, R = L.B.recherche;
        aLaBarre(L, p, 0, 0);
        let arrete = -1, aTerre = 0, vue = false, message = null;
        const hud = L.Hud.message; L.Hud.message = function (m) { if (/ARRAISONN/.test(m)) message = m; return hud.apply(this, arguments); };
        for (let k = 0; k < 1200 && arrete < 0; k++) {
            R.etoiles = 2; R.vu = 0;
            o.frame(1);
            for (const v of vedettes(L)) if (!L.Monde.estEau(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT))) aTerre++;
            if (j.arrete) arrete = k;
        }
        L.Hud.message = hud;
        return { arrete: arrete, aTerre: aTerre, message: message };
    }""")
    assert r["arrete"] >= 0, "la vedette n'a pas arraisonné la chaloupe en 20 s"
    assert r["aTerre"] == 0, f"la vedette a touché la terre {r['aTerre']} fois"
    assert r["message"], "l'arraisonnement ne se dit pas"


def test_en_fuite_on_n_est_pas_arraisonne_et_sans_etoile_la_vedette_s_efface(banc):
    r = banc("function (L, o) {" + AIDES + VEDETTES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, R = L.B.recherche;
        const c = aLaBarre(L, p, 0, 2);
        R.etoiles = 1;
        const v = L.Vehicules.creer('vedette', p.x, p.y + 18, 0, { conducteur: 'vedette', etat: 'roule', sirene: true });
        majVedette(L, 1);
        const fuite = !!j.arrete;
        c.vitesse = 0; c.vx = c.vy = 0; majVedette(L, 1);
        const arrete = !!j.arrete;
        // Plus d'etoile : elle ne s'efface que hors champ.
        j.arrete = false; R.etoiles = 0;
        const w = L.Vehicules.creer('vedette', p.x, p.y + 60, 0, { conducteur: 'vedette', etat: 'roule', sirene: true });
        majVedette(L, 60);
        const vueReste = L.B.entites.indexOf(w) >= 0;
        w.x += 3000; majVedette(L, 60);
        return { fuite: fuite, arrete: arrete, vueReste: vueReste, loinPart: L.B.entites.indexOf(w) < 0 };
    }""")
    assert not r["fuite"], "arraisonné en pleine fuite"
    assert r["arrete"], "bord à bord et arrêté, la vedette n'arraisonne pas"
    assert r["vueReste"], "la vedette disparaît sous les yeux du joueur"
    assert r["loinPart"], "sans étoile, la vedette reste pour toujours"


def test_au_refuge_de_l_ile_la_vedette_ne_vient_pas_et_n_arraisonne_pas(banc):
    """L'île est un refuge pour toute la police : la vedette n'y fait pas exception."""
    r = banc("function (L, o) {" + AIDES + VEDETTES + """
        L.Jeu.commencer();
        const z = (L.Monde.carte.zones || []).find(function (q) { return q.refuge; });
        if (!z) return { trouve: false };
        let p = null;
        for (let ty = z.y; ty < z.y + z.h && !p; ty++) for (let tx = z.x; tx < z.x + z.l && !p; tx++) {
            if (L.Monde.estEau(tx, ty)) p = { x: tx * L.TT + 8, y: ty * L.TT + 8 };
        }
        if (!p) return { trouve: false };
        const j = L.B.joueur, R = L.B.recherche;
        aLaBarre(L, p, 0, 0);
        R.etoiles = 3;
        const refuge = L.Police.auRefuge(), voulues = L.Vedette.voulues();
        L.Vehicules.creer('vedette', p.x, p.y + 16, 0, { conducteur: 'vedette', etat: 'roule', sirene: true });
        majVedette(L, 1);
        return { trouve: true, refuge: refuge, voulues: voulues, arrete: !!j.arrete };
    }""")
    assert r["trouve"], "pas d'eau dans le refuge de l'île"
    assert r["refuge"], "le juge n'est pas au refuge"
    assert r["voulues"] == 0, "la vedette chasse jusque sur l'île"
    assert not r["arrete"], "arraisonné au refuge de l'île"


def test_voler_la_vedette_est_un_crime_et_son_agent_tombe_a_l_eau(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, R = L.B.recherche;
        j.x = p.x; j.y = p.y; L.Monde.centrerCamera(p.x, p.y);
        R.etoiles = 0; R.chaleur = 0;
        const v = L.Vehicules.creer('vedette', p.x, p.y + 14, 0, { conducteur: 'vedette', etat: 'roule', sirene: true });
        v.pilote = { swaps: L.Police.paletteAgent() };
        const avant = L.Police.agents().length;
        let crime = null; const signaler = L.Police.signalerCrime;
        L.Police.signalerCrime = function (type) { crime = type; return signaler.apply(this, arguments); };
        L.Vehicules.monter(j, v);
        L.Police.signalerCrime = signaler;
        return { aBord: j.dansVehicule === v, crime: crime, agents: L.Police.agents().length - avant, pilote: v.pilote };
    }""")
    assert r["aBord"], r
    assert r["crime"], "voler la vedette n'est pas un crime"
    assert r["agents"] == 1, f"l'agent de la vedette s'évapore : {r}"
    assert not r["pilote"], "l'agent reste dessiné à la console"
