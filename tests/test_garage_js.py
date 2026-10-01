"""Le garage qui modifie les chars, au banc (docs/jalons/le-garage-qui-modifie-les-chars.md) : chaque pièce
change ce qu'elle promet, mesuré au bouton ; elle survit à la sauvegarde et à la fourrière (qui la fait
payer) ; Ti-Guy la commente ; le klaxon joue son air — le début du refrain de « Gens du pays », tel que la
partition l'écrit."""

from app import garage

EFFETS = {p["slug"]: p["effet"] for p in garage.PIECES}
PRIX = {p["slug"]: p["prix"] for p in garage.PIECES}

OUTILS = """
  const TT = 16;
  function vider(L) {
    const B = L.B, j = B.joueur;
    B.entites = B.entites.filter(function (e) { return e === j || !(e.type === 'vehicule' || e.type === 'pieton' || e.type === 'police'); });
    L.Entites.indexer();
  }
  function char(L, x, y, mods) {
    const v = L.Vehicules.creer('auto', x, y, 0, { etat: 'stationne', couleur: '#c0392b' });
    L.Garage.poser(v, mods);
    return v;
  }
  /** Pied au plancher sur un boulevard : la pointe atteinte. `pendant(v, k)` : ce qu'on fait a l'image k. */
  function pointe(L, o, rue, mods, pendant) {
    const B = L.B, j = B.joueur, V = L.Vehicules;
    vider(L);
    const v = char(L, rue.x, rue.y, mods);
    V.monter(j, v); L.Entites.indexer();
    o.touche('KeyW');
    let max = 0;
    for (let k = 0; k < 420; k++) {
      if (pendant) pendant(v, k);
      o.frame(1); max = Math.max(max, v.vitesse); if (v.x > rue.x + 150) v.x = rue.x; v.y = rue.y; v.angle = 0;
    }
    o.relacher('KeyW'); V.descendre(j, true); B.entites.splice(B.entites.indexOf(v), 1);
    return +max.toFixed(3);
  }
"""


def test_le_moteur_atteint_la_pointe_qu_il_promet_et_la_nitro_la_depasse(banc):
    """⚠️ Au BOUTON, pas à la fiche : la pointe est un équilibre entre l'accélération et la friction."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, rue = o.boulevard(true);
        const def = B.defs.vehicules.find(function (q) { return q.slug === 'auto'; });
        const base = pointe(L, o, rue, null), moteur = pointe(L, o, rue, { moteur: true });
        // La nitro : SAISIR a pleine vitesse pousse au-dela ; tout de suite apres, elle recharge.
        let pousse = 0, recharge = null;
        pointe(L, o, rue, { nitro: true }, function (v, k) {
            if (k === 200 || k === 340) o.touche('KeyU');
            if (k === 201 || k === 341) o.relacher('KeyU');
            if (k > 200 && k < 290) pousse = Math.max(pousse, v.vitesse);
            if (k === 345) recharge = v.nitroT;
        });
        return { base: base, moteur: moteur, pousse: pousse, recharge: recharge, vmax: def.vitesse_max };
    }""")
    k = EFFETS["moteur"]["vitesse"]
    assert r["base"] > r["vmax"] * 0.9, r
    assert r["moteur"] >= r["base"] * (k - 0.05), f"le moteur n'atteint pas ce qu'il promet : {r}"
    assert r["pousse"] > r["vmax"] * 1.15, f"la nitro ne pousse pas : {r}"
    assert r["recharge"] == 0, f"la nitro repart sans recharger : {r}"


def test_le_blindage_et_les_pneus_d_hiver(banc):
    """Le blindage : la vie pleine. Les pneus : sur le verglas, on s'arrête plus court."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, rue = o.boulevard(true);
        const def = B.defs.vehicules.find(function (q) { return q.slug === 'auto'; });
        const blinde = char(L, rue.x, rue.y, { blindage: true }), vie = blinde.vieMax;
        B.entites.splice(B.entites.indexOf(blinde), 1);
        // La glace partout : le frein n'y mord plus qu'a 20 %.
        const frein = L.Neige.frein;
        L.Neige.frein = function () { return 0.2; };
        function freinage(mods) {
            vider(L);
            const v = char(L, rue.x, rue.y, mods);
            V.monter(j, v); L.Entites.indexer();
            v.vitesse = 3; v.vx = 3; v.vy = 0;
            o.touche('KeyS');
            let n = 0;
            for (; n < 600 && v.vitesse > 0.2; n++) { o.frame(1); v.y = rue.y; v.angle = 0; if (v.x > rue.x + 150) v.x = rue.x; }
            o.relacher('KeyS'); V.descendre(j, true); B.entites.splice(B.entites.indexOf(v), 1);
            return n;
        }
        const sans = freinage(null), avec = freinage({ pneus: true });
        L.Neige.frein = frein;
        return { vie: vie, base: def.vie, sans: sans, avec: avec };
    }""")
    assert r["vie"] == round(r["base"] * EFFETS["blindage"]["vie"]), r
    assert r["avec"] < r["sans"] * 0.6, f"les pneus d'hiver ne freinent pas mieux sur la glace : {r}"


def test_ti_guy_pose_la_piece_la_commente_et_ne_la_pose_qu_une_fois(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, V = L.Son.Voix;
        p.argent = 5000;
        const v = char(L, B.joueur.x + 40, B.joueur.y, null);
        function menu() {
            B.exterieur = { entites: [v], x: v.x, y: v.y };
            const items = L.Missions.menuGarage([], v).items;
            B.exterieur = null;
            return items;
        }
        const ligne = menu().find(function (i) { return i.libelle === 'POSER : MOTEUR GONFLÉ'; });
        V.demandees.length = 0;
        const avant = p.argent;
        ligne.faire();
        const apres = menu().find(function (i) { return i.libelle === 'POSER : MOTEUR GONFLÉ'; });
        const velo = L.Vehicules.creer('velo', v.x + 40, v.y, 0, { etat: 'stationne', couleur: '#ffffff' });
        return { paye: avant - p.argent, mods: v.mods, voix: V.demandees.slice(), apres: { detail: apres.detail, actif: apres.actif },
                 vmax: v.def.vitesse_max, catalogue: L.Vehicules.vehiculeDef('auto').vitesse_max,
                 velo: L.Garage.items(velo, L.Missions.payer).length };
    }""")
    assert r["paye"] == PRIX["moteur"] and r["mods"] == {"moteur": True}, r
    assert "ti_guy-garage-moteur" in r["voix"], r
    assert r["apres"] == {"detail": "POSÉ", "actif": False}, r
    assert abs(r["vmax"] - r["catalogue"] * EFFETS["moteur"]["vitesse"]) < 1e-9, "la fiche du char, pas celle du catalogue"
    assert r["velo"] == 0, "un vélo n'a pas de moteur à gonfler"


def test_les_pieces_survivent_a_la_sauvegarde_et_a_la_fourriere(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, M = L.Missions;
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu === 'planque'; });
        const v = char(L, porte.x * TT + 8, (porte.y + 1) * TT + 8, { moteur: true, blindage: true });
        L.Entites.indexer();
        M.sauvegarderPartie();
        const ecrite = JSON.parse(o.store['bandini-partie-v1']);
        // On recharge : la ville se repose, le char revient devant la planque.
        B.partie = ecrite;
        L.Jeu.commencer();
        const revenu = B.entites.find(function (e) { return e.type === 'vehicule' && e.mods && e.mods.moteur; });
        // Au lot, et racheté : modifié, et plus cher.
        const prixNu = M.prixRachat('auto');
        M.saisir(revenu);
        const fiche = B.partie.fourriere[B.partie.fourriere.length - 1];
        const prixMod = M.prixRachat('auto', fiche.mods);
        B.entites = B.entites.filter(function (e) { return e.saisi === null || e.saisi === undefined; });
        M.garnirLaFourriere();
        const auLot = B.entites.find(function (e) { return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined && e.mods; });
        return { ecrite: ecrite.planque.vehicule && ecrite.planque.vehicule.mods, revenu: revenu && revenu.mods,
                 vie: revenu && revenu.vieMax, fiche: fiche.mods, prixNu: prixNu, prixMod: prixMod,
                 auLot: auLot && auLot.mods, vmax: auLot && auLot.def.vitesse_max };
    }""")
    attendu = {"moteur": True, "blindage": True}
    assert r["ecrite"] == attendu and r["revenu"] == attendu, r
    assert r["fiche"] == attendu and r["auLot"] == attendu, r
    assert r["prixMod"] - r["prixNu"] == round((PRIX["moteur"] + PRIX["blindage"]) * garage.RACHAT_PART), r


# Le klaxon au bouton — chacun joue le sien, « Gens du pays » compris : tests/test_klaxons_de_ti_guy_js.py.


# --- Le klaxon, côté catalogue : la partition -------------------------------------------------------

#: La partition (Choralies, chant 1, mesures 5 à 8), en noms de notes : trois noires, une blanche pointée.
REFRAIN = [("A4", 1), ("G4", 1), ("F4", 1), ("C5", 3), ("A4", 1), ("G4", 1), ("F4", 1), ("D5", 3)]

DEMI_TONS = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def frequence(nom: str) -> float:
    """Le tempérament égal, la 440."""
    return 440.0 * 2 ** ((DEMI_TONS[nom[0]] + 12 * (int(nom[1]) - 4)) / 12)


def test_le_klaxon_joue_gens_du_pays():
    assert len(garage.KLAXON_AIR) == len(REFRAIN)
    for (hz, duree), (nom, temps) in zip(garage.KLAXON_AIR, REFRAIN, strict=True):
        assert abs(hz - frequence(nom)) < 0.05, (hz, nom)
        assert abs(duree - temps * garage.NOIRE) < 1e-9, (duree, nom)


#: « La Soirée du hockey » : la partition que Martin a fournie le 1er oct. 2026 (« Hockey Night in Canada », Dolores
#: Claman, version facile), main droite, en croches : l'intro (mesures 2 à 4) puis la cadence (mesures 11 et 12).
#: Les liaisons fondent (do~do : trois croches) ; le soupir du bout de la mesure 4 tombe ; le demi-soupir de la
#: mesure 11 reste (« R »).
HOCKEY = [("G3", 2), ("G3", 1), ("C4", 2), ("C4", 1), ("Bb3", 2),       # mesure 2
          ("G4", 2), ("G4", 1), ("C5", 2), ("C5", 1), ("Bb4", 2),       # mesure 3 : la même, une octave plus haut
          ("G4", 1), ("G3", 1), ("G3", 1), ("G3", 1), ("C4", 2),        # mesure 4
          ("G4", 1), ("R", 1), ("G4", 1), ("Bb4", 2), ("Bb4", 1), ("B4", 2),   # mesure 11
          ("C5", 2)]                                                    # mesure 12 : la tonique

BEMOLS = {"Bb3": 233.08, "Bb4": 466.16}


def test_le_klaxon_joue_la_soiree_du_hockey():
    air = garage.AIR_HOCKEY
    assert len(air) == len(HOCKEY)
    for (hz, duree), (nom, croches) in zip(air, HOCKEY, strict=True):
        attendu = 0.0 if nom == "R" else BEMOLS.get(nom) or frequence(nom)
        assert abs(hz - attendu) < 0.05, (hz, nom)
        assert abs(duree - croches * 0.14) < 1e-9, (duree, nom)        # Martin : « un peu moins vite » que 0,11

