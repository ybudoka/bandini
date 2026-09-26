"""Le brouillard de Baie-des-Brumes, au banc (docs/jalons/le-brouillard-de-baie-des-brumes.md) : le même
brouillard le même matin pour tout le monde, la vue de la police qui baisse et revient, aucun dé, et le
Clairon qui l'annonce la veille. Derrière son option : éteinte, il n'existe pas."""

from app import brouillard

#: Un matin de brouillard, à 8 h, aux Quais (là où il est entier).
MATIN = """
  function unMatinDeBrouillard(L) {
    const B = L.B, p = B.partie;
    let jour = 1;
    while (!L.Brouillard.matinDeBrouillard(jour)) jour++;
    p.jour = jour; p.heure = 8 / 24;
    const q = L.Monde.carte.zones.find(function (z) { return z.district === 'quais'; });
    B.joueur.x = (q.x + q.l / 2) * 16; B.joueur.y = (q.y + q.h / 2) * 16;
    return jour;
  }
"""


def test_le_meme_brouillard_le_meme_matin_pour_tout_le_monde(banc):
    """Deux graines, les mêmes matins de brouillard ; un matin sur quatre, environ ; il monte à
    l'aube, tient, et se lève avant midi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const Br = L.Brouillard, matins = [];
        for (const g of [1, 777]) { L.graine(g); const m = []; for (let j = 1; j <= 400; j++) if (Br.matinDeBrouillard(j)) m.push(j); matins.push(m); }
        const j = matins[0][0];
        return { matins: matins, courbe: [3, 5, 7, 9, 11, 13].map(function (h) { return +Br.intensiteA(j, h / 24).toFixed(2); }) };
    }""")
    assert r["matins"][0] == r["matins"][1]
    assert 60 < len(r["matins"][0]) < 140, len(r["matins"][0])
    avant, montee, plein, plein2, levee, apres = r["courbe"]
    assert avant == 0 and apres == 0 and 0 < montee < 1 and plein == plein2 == 1 and 0 < levee < 1, r["courbe"]


def test_eteint_il_n_existe_pas(banc):
    """⚠️ L'option est éteinte par défaut : un matin de brouillard, rien ne change — ni la vue, ni le
    voile, ni l'annonce."""
    r = banc("function (L, o) {" + MATIN + """
        L.Jeu.commencer();
        unMatinDeBrouillard(L);
        return { option: L.B.options.brouillard, i: L.Brouillard.intensite(), vision: L.Brouillard.vision(),
                 annonce: L.Brouillard.annonceDeDemain() };
    }""")
    assert r == {"option": False, "i": 0, "vision": 1, "annonce": None}, r


def test_la_police_voit_moins_loin_dans_le_brouillard_et_de_nouveau_a_midi(banc):
    """Un agent qui regarde droit devant : le joueur à mi-portée de jour est vu par temps clair, pas
    dans le brouillard du matin ; à midi, le brouillard levé, il l'est de nouveau."""
    r = banc("function (L, o) {" + MATIN + """
        L.Jeu.commencer();
        const B = L.B, P = L.Police;
        B.options.brouillard = true;
        unMatinDeBrouillard(L);
        const j = B.joueur, portee = B.defs.recherche.vision.policier.jour * 16, M = L.Monde;
        // Une rue des Quais, et un agent a 70 % de sa portee dans une direction degagee, qui regarde
        // le joueur (toujours aux Quais : c'est la que le brouillard est entier).
        const q = M.carte.zones.find(function (z) { return z.district === 'quais'; });
        let agent = null;
        for (let ty = q.y; ty < q.y + q.h && !agent; ty += 2) {
            for (let tx = q.x; tx < q.x + q.l && !agent; tx += 2) {
                if (!M.estChaussee(tx, ty)) continue;
                const px = tx * 16 + 8, py = ty * 16 + 8;
                for (let k = 0; k < 4 && !agent; k++) {
                    const a = k * Math.PI / 2, x = px - Math.cos(a) * portee * 0.7, y = py - Math.sin(a) * portee * 0.7;
                    const z = M.zoneA(x, y);
                    if (z && z.district === 'quais' && M.ligneLibre(x, y, px, py)) { agent = { x: x, y: y, angle: a }; j.x = px; j.y = py; }
                }
            }
        }
        const libre = !!agent;
        if (!agent) return { libre: false };
        const brume = P.voit(agent, j.x, j.y, 'policier');
        const i = L.Brouillard.intensite();
        B.partie.heure = 12.5 / 24;
        const midi = P.voit(agent, j.x, j.y, 'policier');
        return { libre: libre, brume: brume, midi: midi, i: i };
    }""")
    assert r["libre"], "aucune direction dégagée autour du joueur : le juge ne mesure rien"
    assert r["i"] == 1, r
    assert r["brume"] is False and r["midi"] is True, r


def test_le_brouillard_ne_tire_aucun_de_et_le_clairon_l_annonce_la_veille(banc):
    """Cent images du brouillard (la corne, le voile) entre deux tirages de `B.rng()` : le tirage
    suivant ne change pas. Et la veille d'un matin de brouillard, le Clairon l'écrit sous la une."""
    r = banc("function (L, o) {" + MATIN + """
        L.Jeu.commencer();
        const B = L.B, Br = L.Brouillard;
        B.options.brouillard = true;
        const jour = unMatinDeBrouillard(L);
        L.graine(9);
        const temoin = [B.rng(), B.rng()];
        L.graine(9);
        for (let k = 0; k < 100; k++) { B.t++; Br.maj(); Br.vision(); }
        const apres = [B.rng(), B.rng()];
        // Le matin de la veille : le jour change, et le Clairon parle.
        B.partie.jour = jour - 1; B.partie.heure = 0.3;
        const annonce = Br.annonceDeDemain();
        L.Missions.nouveauJour();
        const veille = B.dialogue ? JSON.stringify(B.dialogue) : '';
        // Le matin du brouillard lui-meme : il ne s'annonce pas pour le lendemain (sauf s'il revient).
        B.partie.jour = jour;
        const lendemain = L.Brouillard.matinDeBrouillard(jour + 1);
        L.Missions.nouveauJour();
        const jourJ = B.dialogue ? JSON.stringify(B.dialogue) : '';
        return { temoin: temoin, apres: apres, annonce: annonce, veille: veille, jourJ: jourJ, lendemain: lendemain };
    }""")
    assert r["apres"] == r["temoin"], "le brouillard a tiré au dé du jeu"
    assert r["annonce"] == brouillard.ANNONCE
    assert brouillard.ANNONCE in r["veille"], "la veille, le Clairon ne l'annonce pas"
    assert (brouillard.ANNONCE in r["jourJ"]) == r["lendemain"], "il annonce un brouillard qui ne vient pas"
