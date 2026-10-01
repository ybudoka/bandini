"""Biscuit s'est sauvé (M16, la toute fin, 1er oct. 2026) — le premier chien du jeu, et Mme Beaulieu, au banc.

- e03 jouée au bouton : la poignée de main chez Mme Beaulieu (devant le dépanneur, après m6), Biscuit qu'on VOIT au bois
  du phare ; à pied, on l'approche, il détale à l'opposé, trois fois — au volant, il ne bouge pas ; épuisé, il se couche
  et se laisse prendre ; il nous suit, on ne rentre pas sans lui, et elle paie.
- Après e03 : Biscuit est assis aux pieds de sa maîtresse ; à pied, il te suit dans les Érables ; en char, il rentre
  s'asseoir. Il naît sans un dé ni un numéro de la ville.
- Il se peint en chien : assis immobile, au trot, au galop, dans le sens où il va."""

import json

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_p_js import RECHARGER

from app import missions

AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("e03", "m97", "m98", "m99")]
                   + ["p02", "p05", "p04", "p10", "p09", "p11"])

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + """
  function partie(L, plus) { faites(L, """ + AVANT + """.concat(plus || [])); return recharger(L); }
  function tuiles(a, b) { return a && b ? Math.round(Math.hypot(a.x - b.x, a.y - b.y) / 16) : null; }
  function aCote(L, e, dx) { const j = L.B.joueur; aPied(L); j.x = e.x + dx; j.y = e.y; j.vx = 0; j.vy = 0; L.Entites.indexer(); }
  // Planté à `dx` pixels de lui (on le relance : un joueur qui s'approche ne recule pas) jusqu'à ce qu'il s'arrête.
  function laisserCourir(L, o, e) { for (let k = 0; k < 400 && e.fugue; k++) { o.frame(1); ecouter(L); } }
"""


def test_e03_biscuit_se_sauve_trois_fois_puis_se_laisse_prendre(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const beaulieu = L.Histoire.donneur('beaulieu');
        const dispo = L.Histoire.disponibleDe('beaulieu');
        serrer(L, o, 'beaulieu'); passer(L, o); ecouter(L);
        const pris = p.mission && p.mission.slug;
        jouer(L, o, 6);
        const c = B.mission.cachette, e = c && c.e, phare = L.Histoire.lieu('phare');
        const pose = { bete: e && e.bete, dessine: e && e.dessine, phare: tuiles(e, phare), eau: e ? L.Monde.estEau(Math.floor(e.x / 16), Math.floor(e.y / 16)) : null,
                       fleche: L.Histoire.ouAller ? null : null, ligne: L.Histoire.ligneObjectif() };
        // Au volant, à côté de lui : il ne bouge pas.
        const v = L.Vehicules.creer('auto', e.x + 30, e.y, 0, { etat: 'stationne', couleur: '#777777' });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 10);
        const auVolant = { fugues: e.fugues, fugue: !!e.fugue };
        L.Vehicules.descendre(j, true); L.Entites.retirer(v); L.Entites.indexer();
        // À pied : trois fois il détale, à l'opposé, à cinq tuiles au moins.
        const fugues = [];
        for (let k = 0; k < 3; k++) {
          const avant = { x: e.x, y: e.y };
          aCote(L, e, -40);
          for (let n = 0; n < 30 && !e.fugue; n++) { o.frame(1); ecouter(L); }
          jouer(L, o, 3);
          const part = { fugue: !!e.fugue, vite: Math.round(Math.hypot(e.vx, e.vy) * 10) / 10, ligne: L.Histoire.ligneObjectif(),
                         pose: L.Entites.poseDePietonBete(e).decor };
          laisserCourir(L, o, e);
          part.loin = tuiles(e, avant); part.duJoueur = tuiles(e, j); part.fugues = e.fugues; part.epuise = !!e.epuise;
          fugues.push(part);
        }
        const assis = { pose: L.Entites.poseDePietonBete(e), ligne: L.Histoire.ligneObjectif(), etape: etape(L) };
        // Épuisé : à deux pas, on l'attrape.
        aCote(L, e, -14); jouer(L, o, 4);
        const pris2 = { etape: etape(L), suit: e.suit === j || B.mission.protege === e, dessine: e.dessine };
        // Revenir sans lui : il est resté au phare.
        e.x = phare.x; e.y = phare.y + 40; e.suit = null; L.Entites.indexer();
        aCote(L, beaulieu, -14); jouer(L, o, 2);
        const sansLui = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        e.x = j.x + 12; e.y = j.y; e.suit = j; L.Entites.indexer();
        finir(L, o);
        return { dispo: dispo && dispo.slug, pris: pris, pose: pose, auVolant: auVolant, fugues: fugues, assis: assis, pris2: pris2,
                 sansLui: sansLui, dites: dites, fait: !!p.missionsFaites.e03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "e03" and r["pris"] == "e03", r
    assert r["pose"]["bete"] == "chien" and r["pose"]["dessine"] is True, r["pose"]
    assert 4 <= r["pose"]["phare"] <= 11 and r["pose"]["eau"] is False, r["pose"]
    assert "APPROCHE" in r["pose"]["ligne"], r["pose"]
    assert r["auVolant"] == {"fugues": 0, "fugue": False}, f"au volant, il ne se sauve pas : {r['auVolant']}"
    for k, f in enumerate(r["fugues"]):
        assert f["fugue"] and f["vite"] > 2.6 and "SE SAUVE" in f["ligne"], (k, f)
        assert f["pose"] == "chien_bouge", (k, f)
        assert f["loin"] >= 3 and f["duJoueur"] >= 5, f"il détale, loin du joueur : {k} {f}"
        assert f["fugues"] == k + 1 and f["epuise"] == (k == 2), (k, f)
    assert r["assis"]["pose"] == {"decor": "chien", "cle": 2} and "ÉPUISÉ" in r["assis"]["ligne"], r["assis"]
    assert r["assis"]["etape"] == 0
    assert r["pris2"] == {"etape": 1, "suit": True, "dessine": True}, r["pris2"]
    assert r["sansLui"]["etape"] == 1 and "PAS AVEC TOI" in r["sansLui"]["ligne"], r["sansLui"]
    assert "pendant:beaulieu:0" in r["dites"] and "pendant:beaulieu:1" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [80], r


def test_apres_e03_biscuit_est_a_ses_pieds_et_te_suit_dans_les_erables(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        function prochain() { const e = L.Entites.creer('decor', 0, 0); L.Entites.retirer(e); return e.id; }
        const j = partie(L, ['e03']);
        const m = L.Histoire.donneur('beaulieu');
        // Il naît sans un dé ni un numéro de la ville : on le retire, on le laisse renaître.
        jouer(L, o, 2);
        let c = B.entites.find(function (e) { return e.chienDe === 'beaulieu'; });
        const ne = !!c;
        L.Entites.retirer(c);
        L.graine(77); const de = B.rng(); const id0 = prochain();
        L.graine(77); L.Biscuit.maj(); const de2 = B.rng(); const id1 = prochain();
        c = B.entites.find(function (e) { return e.chienDe === 'beaulieu'; });
        const naissance = { ne: ne, de: de === de2, id: id1 === id0 + 1, idChien: c.id, pres: tuiles(c, m), pose: L.Entites.poseDePietonBete(c).decor };
        // Loin de lui : il reste assis.
        aCote(L, c, -16 * 8); jouer(L, o, 30);
        const reste = { suit: !!c.suit, pres: tuiles(c, m) };
        // À pied, à côté : il se lève et te suit, au trot.
        aCote(L, c, -20); jouer(L, o, 4);
        const adopte = { suit: c.suit === j && c.suiveur === true };
        let trot = null;
        // On marche vers l'est, dans la rue (le trottoir du dépanneur a son abribus, son édicule, ses donneurs) ; on y
        // descend d'abord, en deux pas.
        const rangee = L.Histoire.lieu('depanneur').y + 3 * 16;
        for (let k = 0; k < 30; k++) { j.y += (rangee - j.y) / 6; L.Entites.indexer(); o.frame(1); }
        for (let k = 0; k < 240; k++) { j.x += 1.5; j.y = rangee; L.Entites.indexer(); o.frame(1); if (!trot && Math.hypot(c.vx, c.vy) > 0.2) trot = L.Entites.poseDePietonBete(c).decor; }
        for (let k = 0; k < 90; k++) { j.y = rangee; o.frame(1); }     // on s'arrête : il nous rattrape
        const suivi = { colle: tuiles(c, j), loinDElle: tuiles(c, m), trot: trot };
        // En char : il rentre s'asseoir à ses pieds.
        const v = L.Vehicules.creer('auto', j.x, j.y, 0, { etat: 'stationne', couleur: '#777777' });
        L.Vehicules.monter(j, v); L.Entites.indexer();
        for (let k = 0; k < 900 && (c.suit || c.retour); k++) o.frame(1);
        for (let k = 0; k < 120; k++) o.frame(1);                    // il reprend sa place, à ses pieds
        const rentre = { suit: !!c.suit, pres: tuiles(c, m), etat: c.etat };
        return { naissance: naissance, reste: reste, adopte: adopte, suivi: suivi, rentre: rentre };
    }""")
    n = r["naissance"]
    assert n["ne"] and n["pres"] <= 2 and n["pose"] == "chien", n
    assert n["de"] is True and n["id"] is True and n["idChien"] >= 1e9, f"il est né d'un dé ou d'un numéro de la ville : {n}"
    assert r["reste"] == {"suit": False, "pres": r["reste"]["pres"]} and r["reste"]["pres"] <= 2, r["reste"]
    assert r["adopte"]["suit"] is True, r
    assert r["suivi"]["colle"] <= 3 and r["suivi"]["loinDElle"] >= 10 and r["suivi"]["trot"] == "chien_bouge", r["suivi"]
    assert r["rentre"]["suit"] is False and r["rentre"]["pres"] <= 2 and r["rentre"]["etat"] == "fige", r["rentre"]


def test_avant_e03_pas_de_biscuit_aux_pieds_de_mme_beaulieu(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        partie(L);
        for (let k = 0; k < 10; k++) o.frame(1);
        return { beaulieu: !!L.Histoire.donneur('beaulieu'), chien: L.B.entites.some(function (e) { return e.bete; }) };
    }""")
    assert r == {"beaulieu": True, "chien": False}, r
