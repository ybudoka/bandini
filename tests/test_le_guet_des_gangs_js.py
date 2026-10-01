"""Le guet d'un membre de gang, au banc (`Entites.guetter`, 1er oct. 2026).

La passe de qualité l'a trouvé : la règle de l'arme au poing chez un gang n'était lue qu'à la FLÂNERIE. Un Cravate
arrêté devant une vitrine (l'`arret` sort avant), ou en route vers sa porte (`majPorte` sort avant tout), laissait
passer la batte à un pas, chez lui. Les Mantes avaient été corrigées à l'arrêt, pour leur défi seulement (f1e7a44f).
Maintenant, un membre de gang à l'arrêt ou en route vers sa porte voit aussi le joueur armé — la règle elle-même ne
change pas : chez lui, à moins de six tuiles, sans mur entre eux, et jamais à mains nues (sauf le défi des Mantes).

⚠️ La rue est vidée et le trafic coupé (`PREPARER` des Mantes) ; la rangée 180 est dans la cour des Cravates, la
rangée 47 au Petit-Canton, chez personne.
"""

import pytest

from test_mantes_defi_js import PREPARER

#: Un Cravate planté devant une vitrine (`arret`, une minuterie qui ne tombe pas pendant le juge), à (dx, dy) du joueur.
ARRETE = """
    function arrete(o, arch, dx, dy) {
        const e = o.poser(arch, dx, dy);
        e.etat = 'arret'; e.minuterie = 5000; e.vx = 0; e.vy = 0;
        return e;
    }
"""


@pytest.mark.parametrize("arme", ["poings", "batte"])
def test_un_cravate_arrete_devant_une_vitrine_voit_la_batte(banc, arme):
    """Le juge de la passe de qualité. Chez les Cravates, un des leurs est planté devant une vitrine ; le joueur
    passe devant lui, d'ouest en est. La batte au poing, il laisse tomber la vitrine et attaque — sans bulle de défi ;
    à mains nues, il le laisse passer."""
    r = banc("""function (L, o) {
        %s
        %s
        const j = preparer(L, 196, 180);
        j.arme = 'ARME';
        const a = arrete(o, 'cravate', 10 * 16, -16), chez = L.Territoires.gangA(a.x, a.y);
        const out = marcher(L, o, [a], 240);
        out.gang = a.gang;
        out.chez = chez;
        out.etat = a.etat;
        return out;
    }""".replace("ARME", arme) % (PREPARER, ARRETE))
    assert r["gang"] == "cravates" and r["chez"] == "cravates", r
    assert r["proche"] <= 6 * 16, f"le joueur n'est jamais passé devant lui : {r}"
    if arme == "poings":
        assert r["defis"] == [] and r["etat"] == "arret", f"à mains nues, il a bougé : {r}"
    else:
        assert r["defis"], f"arrêté devant sa vitrine, il a laissé passer la batte : {r}"
        assert r["defis"][0]["chez"] == "cravates" and r["defis"][0]["d"] <= 6 * 16, r
        assert r["defis"][0].get("bulle") is None, f"un Cravate n'a pas de réplique de défi : {r}"


@pytest.mark.parametrize("arme", ["poings", "batte"])
def test_un_cravate_en_route_vers_sa_porte_voit_la_batte(banc, arme):
    """Il rentre souper : la marche de `majPorte`, qui sort avant tout le reste. Le joueur l'attend dans la cour ; le
    Cravate part de trois tuiles à l'est et s'éloigne vers sa porte, treize tuiles plus loin sur la même rangée. La
    batte au poing, il laisse tomber le souper et attaque ; à mains nues, il continue son chemin.

    ⚠️ La porte est posée à la main sur la rangée (`porteBut`) : la vraie la plus proche (199, 176) est derrière un
    mur, et `envoyerAUnePorte` ne cherche pas de chemin — il y piétinait 60 images et renonçait. On ne juge que la
    marche, jamais l'arrivée."""
    r = banc("""function (L, o) {
        %s
        const j = preparer(L, 196, 180);
        j.arme = 'ARME';
        const a = o.poser('cravate', 3 * 16, 0);
        a.etat = 'flane';
        a.porteBut = { x: 212, y: 179 }; a.porteT = 0; a.porteBloque = 0;
        const x0 = a.x, chez = L.Territoires.gangA(a.x, a.y);
        let attaque = null, dAttaque = null;
        for (let t = 0; t < 240 && attaque === null; t++) {
            o.frame(1);
            if (a.etat === 'attaque_joueur') { attaque = t; dAttaque = Math.round(Math.hypot(a.x - j.x, a.y - j.y)); }
        }
        return { attaque: attaque, dAttaque: dAttaque, porteBut: !!a.porteBut, chez: chez, gang: a.gang,
                 avance: Math.round(a.x - x0), etat: a.etat };
    }""".replace("ARME", arme) % PREPARER)
    assert r["gang"] == "cravates" and r["chez"] == "cravates", r
    if arme == "poings":
        assert r["attaque"] is None and r["porteBut"], f"à mains nues, il a laissé sa porte : {r}"
        assert r["avance"] > 2 * 16, f"il n'a pas marché vers sa porte : {r}"
    else:
        assert r["attaque"] is not None and r["dAttaque"] <= 6 * 16, f"en route vers sa porte, il n'a pas vu la batte : {r}"
        assert not r["porteBut"], f"il a gardé sa porte en attaquant : {r}"


def test_la_regle_ne_change_pas_pour_un_gang_arrete(banc):
    """Les garde-fous de la règle tiennent aussi à l'arrêt : hors de chez lui (au Petit-Canton, chez personne), un
    Cravate arrêté laisse passer la batte ; chez lui, un gang CALME (`partie.calmes`, M16) aussi ; dans un char, le
    joueur ne provoque personne. Et le guet ne tire pas un dé."""
    r = banc("""function (L, o) {
        %s
        %s
        const out = {};
        // Hors de chez lui.
        let j = preparer(L, 136, 47);
        j.arme = 'batte';
        let a = arrete(o, 'cravate', 10 * 16, -16);
        out.horsChez = L.Territoires.gangA(a.x, a.y);
        out.hors = marcher(L, o, [a], 420);
        // Chez lui, mais son gang est calme.
        j = preparer(L, 196, 180);
        j.arme = 'batte';
        L.B.partie.calmes = ['cravates'];
        a = arrete(o, 'cravate', 10 * 16, -16);
        out.calme = marcher(L, o, [a], 420);
        L.B.partie.calmes = [];
        // Chez lui, gang pas calme, le joueur a deux tuiles : `guetter` seul, sans un de.
        j = preparer(L, 196, 180);
        j.arme = 'batte';
        a = arrete(o, 'cravate', 32, 0);
        a.t = 15;
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng.apply(this, arguments); };
        j.dansVehicule = { id: 1 };
        out.enChar = L.Entites.guetter(a);
        j.dansVehicule = null;
        out.tic = (a.t = 16, L.Entites.guetter(a));
        out.pret = (a.t = 30, L.Entites.guetter(a));
        L.B.rng = rng;
        out.des = des;
        out.etat = a.etat;
        return out;
    }""" % (PREPARER, ARRETE))
    assert r["horsChez"] != "cravates", r
    assert r["hors"]["proche"] <= 6 * 16 and r["hors"]["defis"] == [], f"hors de chez lui, il a attaqué : {r}"
    assert r["calme"]["proche"] <= 6 * 16 and r["calme"]["defis"] == [], f"un gang calme a attaqué : {r}"
    assert r["enChar"] is False and r["tic"] is False, r
    assert r["pret"] is True and r["etat"] == "attaque_joueur", f"toutes les gardes levées, il n'attaque pas : {r}"
    assert r["des"] == 0, f"{r['des']} dés tirés par le guet"
