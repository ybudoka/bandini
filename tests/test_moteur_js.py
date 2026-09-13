"""Le moteur JS sous Node, contre le paquet que le serveur sert VRAIMENT.

Chaque test passe une fonction `(L, o) => resultat` au banc (tests/banc.js) :
L = window.BANDINI, o = outils (frame, touche, pad, pointeur, singe...).
"""

import json

import pytest

from app import economie


def test_le_moteur_charge_et_expose_son_api(banc):
    r = banc("""function (L, o) {
        return { etat: L.B.etat, cles: Object.keys(L).sort(), version: L.B.defs.version,
                 carte: [L.Monde.carte.w, L.Monde.carte.h], fetchs: o.fetchs.length };
    }""")
    assert r["etat"] == "titre"
    for cle in ("B", "Base", "Atlas", "Entree", "Son", "Monde", "Entites", "Combat", "Vehicules",
                "Police", "Missions", "Hud", "Jeu", "Sauvegarde", "SPRITES", "TUILES"):
        assert cle in r["cles"], cle
    assert r["carte"] == [60, 34]
    assert r["fetchs"] == 1


def test_les_sprites_sont_integres(banc):
    r = banc("""function (L, o) {
        const problemes = [];
        for (const nom in L.SPRITES) problemes.push.apply(problemes, L.Atlas.valider(nom, L.SPRITES[nom]));
        for (const ch in L.POLICE_PIXEL) if (L.POLICE_PIXEL[ch].length !== 15) problemes.push('police ' + ch);
        const legende = L.B.defs.carte.legende;
        for (const g in legende) if (!L.TUILES[g]) problemes.push('tuile sans peintre : ' + g);
        return problemes;
    }""")
    assert r == []


def test_le_joueur_marche_et_ne_traverse_pas_les_murs(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const x0 = j.x;
        o.touche('KeyD'); o.frame(60); o.relacher('KeyD');
        const x1 = j.x;
        o.touche('ShiftLeft'); o.touche('KeyD'); o.frame(60); o.relacher('KeyD'); o.relacher('ShiftLeft');
        const x2 = j.x;
        // Vers le haut, un batiment se trouve sur le chemin : on doit s'arreter dessus.
        o.touche('KeyW'); o.frame(900); o.relacher('KeyW');
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { x0: x0, x1: x1, x2: x2, sol: L.Monde.solidite(tx, ty), y: j.y, etat: L.B.etat,
                 dataEtat: o.elements.bandini.dataset.etat };
    }""")
    assert r["x1"] > r["x0"] + 50
    assert r["x2"] - r["x1"] > (r["x1"] - r["x0"]) * 1.4, "le sprint doit etre nettement plus rapide"
    assert r["sol"] == 0, "le joueur a fini dans un mur"
    assert r["y"] > 0
    assert r["etat"] == "jeu" and r["dataEtat"] == "jeu"


def test_la_manette_a_une_zone_morte_radiale(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0.1, 0.05]); o.frame(2);
        const morte = Object.assign({}, L.Entree.axe);
        o.pad([0.6, 0]); o.frame(2);
        const demi = Object.assign({}, L.Entree.axe);
        o.pad([0, -1]); o.frame(2);
        const plein = Object.assign({}, L.Entree.axe);
        o.pad([0, 0], [0, 1]); o.frame(2);
        const bouton = L.entree('esquive');
        o.pad(null); o.frame(2);
        return { morte: morte, demi: demi, plein: plein, bouton: bouton.pad, apres: L.Entree.axe.source };
    }""")
    assert r["morte"]["mag"] == 0
    assert r["demi"]["source"] == "manette" and 0.45 < r["demi"]["mag"] < 0.6 and r["demi"]["y"] == 0
    assert r["plein"]["mag"] == 1 and r["plein"]["y"] == -1
    assert r["bouton"] is True
    assert r["apres"] == "clavier"


def test_le_joystick_tactile_deplace_le_joueur(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, x0 = j.x;
        // Le centre de #croix est en (90, 570) d'apres son faux rectangle.
        o.pointeur('pointerdown', 90, 570, 1);
        o.pointeur('pointermove', 150, 570, 1);
        o.frame(60);
        const pendant = Object.assign({}, L.Entree.axe);
        o.pointeur('pointerup', 150, 570, 1);
        o.frame(2);
        o.bouton('esquive', 'pointerdown');
        o.frame(1);
        const tenu = L.entree('esquive').tactile;
        o.bouton('esquive', 'pointerup');
        return { dx: j.x - x0, pendant: pendant, tenu: tenu, apres: L.Entree.axe.mag,
                 tactile: o.doc.body.classList.contains('tactile') };
    }""")
    assert r["pendant"]["source"] == "tactile" and r["pendant"]["x"] > 0.9
    assert r["dx"] > 40
    assert r["tenu"] is True
    assert r["apres"] == 0
    assert r["tactile"] is True


def test_la_recherche_monte_puis_retombe(banc, paquet):
    palier1 = paquet["recherche"]["paliers"][1]["decroissance_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Police.signalerCrime('mort_policier', 100, 100, true);
        const apres = L.B.recherche.etoiles;
        o.frame(%d * 60 - 5);
        const avantDecroissance = L.B.recherche.etoiles;
        o.frame(10);
        return { apres: apres, avant: avantDecroissance, fin: L.B.recherche.etoiles,
                 nonVu: (function () { L.Police.signalerCrime('pickpocket', 0, 0, false); return L.B.recherche.etoiles; })() };
    }""" % palier1)
    assert r["apres"] == 1
    assert r["avant"] == 1
    assert r["fin"] == 0
    assert r["nonVu"] == 0, "un crime non vu ne donne pas d'etoile"


def test_le_cone_de_vision(banc):
    r = banc("""function (L, o) {
        const c = L.Police.dansLeCone;
        const demi = 45 * Math.PI / 180;
        return [c(0, 0, 0, demi, 100, 80, 0), c(0, 0, 0, demi, 100, -80, 0), c(0, 0, 0, demi, 100, 60, 70),
                c(0, 0, 0, demi, 100, 200, 0), c(0, 0, Math.PI, demi, 100, -80, 0)];
    }""")
    assert r == [True, False, False, False, True]


def test_les_amendes_du_navigateur_sont_celles_de_python(banc):
    cas = [(1000, 1, 0), (1000, 2, 3), (50, 5, 20), (100000, 3, 7), (0, 1, 0)]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return %s.map(function (c) { return [L.Missions.amende(c[0], c[1], c[2]), L.Missions.potDeVin(c[1], c[2]),
                                              L.Missions.factureHopital(c[0])]; });
    }""" % json.dumps(cas))
    for (argent, etoiles, casier), (amende, pot, hopital) in zip(cas, r):
        assert amende == economie.amende(argent, etoiles, casier)
        assert pot == economie.pot_de_vin(etoiles, casier)
        assert hopital == economie.facture_hopital(argent)


def test_la_sauvegarde_fait_l_aller_retour_et_complete_un_vieux_blob(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.argent = 1234; L.B.partie.casier = 2;
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        const vieux = L.Sauvegarde.completer({ argent: 7 }, L.B.defs);
        return { argent: brut.argent, casier: brut.casier, x: brut.x, vieux: vieux,
                 cles: Object.keys(L.etatInitial(L.B.defs)).sort() };
    }""")
    assert r["argent"] == 1234 and r["casier"] == 2 and isinstance(r["x"], int)
    assert r["vieux"]["argent"] == 7
    assert sorted(r["vieux"].keys()) == r["cles"]
    assert r["vieux"]["armes"]["poings"] == {"mun": None}


@pytest.mark.parametrize("graine", [1, 2])
def test_le_singe_ne_casse_rien(banc, graine):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.singe(3000, %d);
        const j = L.B.joueur, c = L.Monde.carte;
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { etat: L.B.etat, dedans: j.x >= 0 && j.y >= 0 && j.x <= c.pxW && j.y <= c.pxH,
                 sol: L.Monde.solidite(tx, ty), t: L.B.t, argent: L.B.partie.argent, nan: isNaN(j.x) || isNaN(j.y) };
    }""" % graine)
    assert r["etat"] in ("jeu", "pause")
    assert r["dedans"] and r["sol"] in (0, 3) and not r["nan"]
    assert r["argent"] >= 0
    assert r["t"] > 1000
