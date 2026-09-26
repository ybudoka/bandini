"""La patrouille — la troisième des « quatre activités que le jeu n'a pas »
(docs/jalons/quatre-activites-que-le-jeu-n-a-pas.md).

Dans une auto-patrouille volée, la sirène allumée : un suspect détale ; on le rattrape — à terre,
pas mort — avant la fin du chrono. Tu fais la police avec un casier : le poste te le rend en pages.
"""

from app import economie

#: Au volant d'une auto-patrouille, la sirène allumée au bouton : la patrouille commence.
SIRENE = """
  function patrouille(L, o) {
    const B = L.B, j = B.joueur;
    const v = o.char('police', 30, 0, 0);
    L.Vehicules.monter(j, v);
    o.tape('KeyJ', 2);
    return v;
  }
"""


def test_la_sirene_lance_la_patrouille_et_le_suspect_detale(banc):
    r = banc("function (L, o) {" + SIRENE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, v = patrouille(L, o);
        const c = M.boulot.client;
        const x0 = c ? Math.hypot(c.x - v.x, c.y - v.y) : null;
        o.frame(90);
        return { sirene: v.sirene, slug: M.boulot.slug, etape: M.boulot.etape, suspect: !!(c && c.suspect),
                 etat: c && c.etat, loin: x0 !== null && x0 >= 140, fuit: c ? Math.hypot(c.x - v.x, c.y - v.y) > x0 - 5 : null,
                 cible: M.boulot.cible === c, enfant: !!(c && (c.intouchable || c.petit)) };
    }""")
    assert r["sirene"] and r["slug"] == "patrouille" and r["etape"] == "ramasse", r
    assert r["suspect"] and r["etat"] == "fuit" and r["loin"], r
    assert r["fuit"], "le suspect ne s'éloigne pas"
    assert r["cible"], "le GPS ne pointe pas le suspect"
    assert not r["enfant"], "le suspect est un enfant : intouchable, on ne l'arrête pas"


def test_a_terre_c_est_une_arrestation_sans_delit(banc):
    """Le suspect à terre, vivant : la base et la prime ; le boulot compte ; pas un délit."""
    r = banc("function (L, o) {" + SIRENE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, v = patrouille(L, o);
        const c = M.boulot.client, argent = B.partie.argent, crimes = B.partie.stats.crimes;
        L.Entites.assommer(c);
        o.frame(2);
        return { gagne: B.partie.argent - argent, fini: !M.boulot.etape, compte: B.partie.boulots.patrouille || 0,
                 crimes: B.partie.stats.crimes - crimes, suspect: c.suspect };
    }""")
    f = economie.BOULOTS["patrouille"]
    assert r["fini"] and r["compte"] == 1, r
    assert f["base"] < r["gagne"] <= f["base"] + f["prime"], r
    assert r["crimes"] == 0 and r["suspect"] is False, r


def test_mort_ca_ne_compte_pas_et_trop_tard_il_s_evapore(banc):
    r = banc("function (L, o) {" + SIRENE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        let v = patrouille(L, o);
        const argent = B.partie.argent;
        const c = M.boulot.client; c.vie = 0; c.vivant = false;
        o.frame(2);
        const mort = { fini: !M.boulot.etape, gagne: B.partie.argent - argent, compte: B.partie.boulots.patrouille || 0 };
        // Une autre : on la laisse filer.
        o.tape('KeyJ', 2); o.tape('KeyJ', 2);
        const c2 = M.boulot.client;
        for (let k = 0; k < (B.defs.economie.boulots.patrouille.chrono_s + 2) * 60 && M.boulot.etape; k++) o.frame(1);
        return { mort: mort, deuxieme: !!c2, tard: !M.boulot.etape, calme: c2 ? !c2.suspect : null };
    }""")
    assert r["mort"]["fini"] and r["mort"]["gagne"] == 0 and r["mort"]["compte"] == 0, r
    assert r["deuxieme"] and r["tard"] and r["calme"], r


def test_le_poste_rend_le_casier_en_pages(banc):
    """Le premier palier (cinq arrestations) : une page de moins au dossier — une fois."""
    premier = economie.PALIERS["patrouille"][0]
    r = banc("function (L, o) {" + SIRENE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        B.partie.casier = 4;
        patrouille(L, o);
        for (let k = 0; k < """ + str(premier["compte"]) + """; k++) {
            if (!M.boulot.etape) { o.tape('KeyJ', 2); o.tape('KeyJ', 2); }
            L.Entites.assommer(M.boulot.client); o.frame(2);
        }
        const apres = B.partie.casier;
        return { apres: apres, compte: B.partie.boulots.patrouille };
    }""")
    assert r["compte"] == premier["compte"], r
    assert r["apres"] == 4 - premier["valeur"], r


def test_le_renverser_au_volant_est_une_arrestation_pas_un_delit(banc):
    """Au volant de l'auto-patrouille, on fonce sur le suspect figé devant le capot : il tombe,
    vivant, et ce n'est pas un « renversement » — c'est une arrestation."""
    r = banc("function (L, o) {" + SIRENE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, v = patrouille(L, o);
        const c = M.boulot.client;
        c.vie = c.vieMax = 400;               // qu'il survive au choc : c'est l'arrestation qu'on juge
        // Une chaussee droite et libre sur douze tuiles vers l'est, personne autour.
        const Mo = L.Monde, j = B.joueur;
        let rue = null;
        for (let r = 0; r < 60 && !rue; r++) {
            for (let dy = -r; dy <= r && !rue; dy++) for (let dx = -r; dx <= r && !rue; dx++) {
                const tx = Math.floor(j.x / 16) + dx, ty = Math.floor(j.y / 16) + dy;
                let ok = true;
                for (let k = 0; k < 12 && ok; k++) ok = Mo.estChaussee(tx + k, ty) && !Mo.bloque(tx + k, ty, Mo.MASQUE_VEHICULE);
                if (ok) rue = { x: tx * 16 + 8, y: ty * 16 + 8 };
            }
        }
        B.entites = B.entites.filter(function (e) {
            return e === c || e === v || e === j || !((e.type === 'pieton' || e.type === 'vehicule' || e.type === 'police') && Math.hypot(e.x - rue.x, e.y - rue.y) < 300);
        });
        v.x = rue.x; v.y = rue.y; j.x = v.x; j.y = v.y;
        c.etat = 'fige'; c.minuterie = 0; c.x = v.x + 110; c.y = v.y; c.vx = 0; c.vy = 0;
        v.angle = 0; v.vitesse = v.def.vitesse_max * 0.8; v.vx = v.vitesse; v.vy = 0;
        L.Entites.indexer();
        const crimes = B.partie.stats.crimes, argent = B.partie.argent;
        o.touche('KeyW');
        for (let k = 0; k < 90 && M.boulot.etape; k++) { if (c.etat === 'fuit') { c.etat = 'fige'; c.vx = 0; c.vy = 0; } o.frame(1); }
        o.relacher('KeyW');
        return { fini: !M.boulot.etape, vivant: c.vivant, crimes: B.partie.stats.crimes - crimes, gagne: B.partie.argent - argent };
    }""")
    assert r["fini"] and r["vivant"], r
    assert r["crimes"] == 0, "renverser le suspect de la patrouille a compté pour un délit"
    assert r["gagne"] > 0, r
