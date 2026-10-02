"""La pause baisse le son, et tombe en veille.

Demande de Martin (3 oct. 2026) : « affaiblis le son sur pause, et je voudrais un
style de screen saver ». Il a choisi la camera qui flane, a 20 s.

⚠️ Juge PAR LE BOUTON : la pause s'ouvre et se referme a ECHAP, la veille se
reveille a la touche, a la souris, au stick — jamais en appelant `majVeille`.
"""

import pytest

#: Le son du maitre, image par image, en pause puis a la reprise. ⚠️ Les reglages
#: sont ceux du JUGE (`pause: 0.5`, durees doublees) : un `0.3` ecrit en dur dans le
#: JS donnerait la meme courbe que le paquet et ne rougirait jamais.
_SON = """async function (L, o) {
    L.Jeu.commencer();
    o.brancherAudio(true);
    L.Son.reveiller();
    await o.attendre(); await o.attendre();
    o.frame(2);
    const plein = L.Son.volumeMaitre;
    Object.assign(L.B.defs.audio.musique, { pause: 0.5, baisse_s: 0.6, remonte_s: 2.4 });
    o.tape('Escape', 1);
    const etat = L.B.etat;
    const descente = [L.Son.volumeMaitre];
    for (let k = 0; k < 150; k++) { o.frame(1); descente.push(L.Son.volumeMaitre); }
    o.tape('Escape', 1);
    const apres = L.B.etat;
    const montee = [L.Son.volumeMaitre];
    for (let k = 0; k < 420; k++) { o.frame(1); montee.push(L.Son.volumeMaitre); }
    // Le muet reste une coupure franche, pause ou pas.
    o.tape('Escape', 30);
    L.B.options.muet = true; L.Son.majVolume();
    const muet = L.Son.volumeMaitre;
    L.B.options.muet = false; L.Son.majVolume();
    return { plein: plein, etat: etat, apres: apres, descente: descente, montee: montee, muet: muet };
}"""


@pytest.fixture(scope="module")
def son(banc):
    return banc(_SON)


def _monotone_sans_saut(serie, depart, arrivee, quoi):
    sens = 1 if arrivee > depart else -1
    pas = [(b - a) * sens for a, b in zip(serie, serie[1:])]
    assert all(p >= -1e-9 for p in pas), "%s : le volume repart en arriere : %s" % (quoi, serie[:20])
    assert max(pas) < 0.25 * abs(arrivee - depart), "%s : un coup sec : %s" % (quoi, serie[:8])
    assert abs(serie[-1] - arrivee) < 1e-9, "%s : arrive a %s au lieu de %s" % (quoi, serie[-1], arrivee)


def test_la_pause_baisse_tout_le_son_graduellement(son):
    assert son["etat"] == "pause"
    assert son["plein"] > 0
    _monotone_sans_saut(son["descente"], son["plein"], son["plein"] * 0.5, "la descente")
    assert sum(1 for v in son["descente"] if v > son["plein"] * 0.5 + 1e-9) >= 9, \
        "le son tombe en moins de 0,15 s : c'est un saut, pas une descente"


def test_la_reprise_remonte_le_son_plus_lentement(son):
    assert son["apres"] == "jeu"
    _monotone_sans_saut(son["montee"], son["plein"] * 0.5, son["plein"], "la remontee")
    n_bas = sum(1 for v in son["descente"] if v > son["plein"] * 0.5 + 1e-9)
    n_haut = sum(1 for v in son["montee"] if v < son["plein"] - 1e-9)
    assert n_haut > 2 * n_bas, "il remonte en %d images et baisse en %d" % (n_haut, n_bas)


def test_le_muet_coupe_net_meme_en_pause(son):
    assert son["muet"] == 0


#: La veille, au bouton. `etat()` : ou on en est, et ou regarde la camera.
_VEILLE = """
    function etat(L) {
        const v = L.B.veille;
        return { etat: L.B.etat, actif: !!(v && v.actif), part: v ? v.part : null,
                 dx: v ? v.dx : null, dy: v ? v.dy : null,
                 menu: L.B.menu ? (L.B.menu.classeur ? L.B.menu.classeur.onglet : L.B.menu.titre) : null,
                 curseur: L.B.menu ? L.B.menu.curseur : null };
    }
"""


@pytest.fixture(scope="module")
def veille(banc):
    return banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _VEILLE + """
        const N = L.Jeu.VEILLE_IMAGES;
        o.tape('Escape', 1);
        o.frame(N - 30);
        const avant = etat(L);
        o.frame(60);
        const endormie = etat(L);
        o.frame(600);
        const flane = etat(L);
        // Ce que l'oeil voit : la vue que recoit le sol, moins la camera du jeu.
        let vue = null;
        const sol = L.Monde.dessinerSol;
        L.Monde.dessinerSol = function (ctx, v) { vue = { x: v.x - L.B.cam.x, y: v.y - L.B.cam.y }; return sol.apply(this, arguments); };
        o.frame(1);
        L.Monde.dessinerSol = sol;
        flane.vue = vue; flane.dxVu = L.B.veille.dx; flane.dyVu = L.B.veille.dy;
        // START (ECHAP) reveille : la pause reste, le menu revient.
        o.tape('Escape', 1);
        const reveil = etat(L);
        o.frame(30);
        const revenue = etat(L);
        // Un deuxieme appui, lui, reprend.
        o.tape('Escape', 1);
        const reprise = etat(L);
        return { N: N, avant: avant, endormie: endormie, flane: flane, reveil: reveil, revenue: revenue, reprise: reprise };
    }""")


def test_vingt_secondes_sans_toucher_endorment_la_pause(veille):
    assert veille["N"] == 20 * 60
    assert veille["avant"]["etat"] == "pause" and not veille["avant"]["actif"], veille["avant"]
    assert veille["endormie"]["actif"], "20 s sans toucher, et la pause ne s'endort pas : %s" % veille["endormie"]


def test_endormie_la_camera_flane_doucement(veille):
    f = veille["flane"]
    assert f["part"] == 1
    assert abs(f["dx"]) > 40 or abs(f["dy"]) > 40, "la camera ne bouge pas : %s" % f
    assert f["vue"] is not None, "le sol n'a pas ete peint"
    assert abs(f["vue"]["x"] - f["dxVu"]) < 1e-6 and abs(f["vue"]["y"] - f["dyVu"]) < 1e-6, \
        "la veille derive, mais l'ecran ne la montre pas : %s" % f


def test_l_appui_qui_reveille_ne_reprend_pas_la_partie(veille):
    r = veille["reveil"]
    assert r["etat"] == "pause", "START a reveille ET repris : %s" % r
    assert not r["actif"]
    assert r["menu"] == "pause"
    v = veille["revenue"]
    assert v["part"] == 0 and v["dx"] == 0 and v["dy"] == 0, "le menu et la camera ne sont pas revenus : %s" % v
    assert veille["reprise"]["etat"] == "jeu"


def test_un_appui_remet_le_compte_a_zero(banc):
    """Lire le carnet n'endort pas la pause : chaque touche recommence les 20 s."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _VEILLE + """
        const N = L.Jeu.VEILLE_IMAGES;
        o.tape('Escape', 1);
        o.frame(N - 60);
        o.tape('ArrowRight', 1);
        o.frame(N - 60);
        return etat(L);
    }""")
    assert r["etat"] == "pause" and not r["actif"], r
    assert r["menu"] == "carnet"


@pytest.mark.parametrize("geste", ["souris", "stick", "doigt"])
def test_la_souris_le_stick_et_le_doigt_reveillent_aussi(banc, geste):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _VEILLE + """
        const curseur = function () { return L.B.menu ? L.B.menu.curseur : null; };
        o.tape('Escape', 1);
        o.frame(L.Jeu.VEILLE_IMAGES + 120);
        const endormie = etat(L);
        const avant = curseur();
        const geste = '""" + geste + """';
        if (geste === 'souris') { o.fenetreEvenement('pointermove', { movementX: 3, movementY: 0 }); o.frame(1); }
        if (geste === 'stick') { o.pad([0, 0.9], []); o.frame(2); o.pad(null); o.frame(1); }
        if (geste === 'doigt') { o.pointeur('pointerdown', 90, 520); o.frame(2); o.pointeur('pointerup', 90, 520); o.frame(1); }
        return { endormie: endormie, apres: etat(L), avant: avant, curseur: curseur() };
    }""")
    assert r["endormie"]["actif"]
    assert r["apres"]["etat"] == "pause" and not r["apres"]["actif"], r["apres"]
    assert r["curseur"] == r["avant"], "le geste qui reveille a aussi bouge le curseur du menu"
