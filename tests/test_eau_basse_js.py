"""L'eau basse : la première tuile ne coûte rien et ne noie pas.

_Demande de Martin (16 sept. 2026) :_ « la premiere case de l eau ne prend pas
d'énergie nie ne noie. »

L'eau n'avait qu'une seule profondeur. Le souffle partait au premier pixel
mouillé (0,5 par image), et immobile les pieds dans l'eau au bord de la grève on
coulait en 3,3 s — réveil à l'hôpital, facture comprise. « L'eau n'est plus un
mur » (14 sept. 2026) l'écrivait pourtant noir sur blanc : « **il faut un bord**
— on ne doit pas passer d'un pas de la terre ferme à la noyade. » C'est le seul
point de cette fiche qui était resté ouvert, et la grève meublée l'a rendu
criant : un enfant y barbote sans rien risquer, à côté d'un joueur qui s'y noie.

⚠️ **La règle se LIT dans la carte** (`Monde.eauBasse`) : de l'eau qui touche la
terre par une de ses quatre voisines. Pas de glyphe de haut-fond — ce serait une
deuxième vérité à tenir à jour, et la côte bouge à chaque graine.

⚠️ Et elle ne doit pas ouvrir un abri : l'eau basse est un liséré d'une tuile, à
un pas du sable. Le juge de l'au-large tient l'autre bout — une tuile plus loin,
le souffle part et l'on coule comme avant.
"""

import pytest

#: Une rive : une tuile qu'on foule, avec seize tuiles d'eau plein est sur trois
#: rangées. ⚠️ Trois rangées et pas une : sur un filet d'une tuile de haut,
#: TOUTE l'eau touche la terre et le juge de l'au-large n'aurait rien à mesurer.
RIVE = """
        let rive = null;
        for (let y = 4; y < c.h - 4 && !rive; y++) {
            for (let x = 4; x < c.w - 17; x++) {
                if (!L.Monde.marchablePieton(x, y) || L.Monde.estEau(x, y)) continue;
                let eau = true;
                for (let k = 1; k <= 16; k++) {
                    for (const dy of [-1, 0, 1]) if (!L.Monde.estEau(x + k, y + dy)) eau = false;
                }
                if (eau) { rive = { x: x, y: y }; break; }
            }
        }
        if (!rive) throw new Error('aucune rive : la carte n\\'a plus d\\'eau ?');
"""


@pytest.fixture
def rive(banc):
    """Fait tourner `corps` avec le joueur posé sur une tuile d'eau, au choix.

    `tuile` dit à combien de tuiles de la berge on le pose : 1 = l'eau basse,
    3 = le large.
    """
    def lancer(corps, tuile=1):
        return banc("""function (L, o) {
            L.Jeu.commencer();
            L.graine(31);
            const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};
            """ + RIVE + """
            const tx = rive.x + """ + str(tuile) + """, ty = rive.y;
            j.x = tx * TT + 8; j.y = ty * TT + 8;
            L.Monde.centrerCamera(j.x, j.y);
            j.endurance = 100; j.surplus = 0; j.cafeine = 0;
            o.frame(1);
            out.basse = L.Monde.eauBasse(tx, ty);
            out.nage = !!j.nage;
            (""" + corps + """)(L, o, j, rive, TT, out);
            return out;
        }""")
    return lancer


def test_la_premiere_tuile_est_de_l_eau_basse_et_pas_la_troisieme(rive):
    """⚠️ Le juge qui tient les deux autres : si la carte devenait un filet
    d'eau d'une tuile, « le large » n'existerait plus et les mesures d'à côté
    diraient n'importe quoi sans rougir."""
    bord = rive("""function (L, o, j, rive, TT, out) {}""", tuile=1)
    large = rive("""function (L, o, j, rive, TT, out) {}""", tuile=3)
    assert bord["nage"] is True and large["nage"] is True, (bord, large)
    assert bord["basse"] is True, "la tuile collée à la berge n'est pas de l'eau basse : %s" % bord
    assert large["basse"] is False, "trois tuiles au large touchent encore la terre : %s" % large


def test_les_pieds_dans_l_eau_le_souffle_ne_part_pas(rive):
    """LE juge de la demande. Rouge avant : 300 images à 0,5 point, c'est toute
    la barre — et bien plus, puisqu'on coule à 200.

    ⚠️ **La noyade se guette PENDANT la boucle, jamais à la fin.** Lue après
    coup, `B.transition` est déjà retombée : le fondu a joué, on s'est réveillé à
    l'hôpital avec 100 points de souffle tout neufs, et le juge aurait félicité
    le code d'avant pour une noyade complète."""
    r = rive("""function (L, o, j, rive, TT, out) {
        let noye = -1;
        for (let i = 0; i < 300 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        out.noye = noye >= 0;
        out.souffle = Math.round(j.endurance);
        out.encore = !!j.nage;
    }""")
    assert r["basse"] is True, "le juge ne mesure pas de l'eau basse : il ne prouve rien"
    assert r["noye"] is False, "on se noie les pieds dans l'eau : %s" % r
    assert r["encore"] is True, "on n'a plus les pieds dans l'eau : %s" % r
    assert r["souffle"] == 100, "le premier pas dans l'eau coûte du souffle : %s" % r


def test_a_bout_de_souffle_on_ne_se_noie_pas_au_bord_et_on_se_refait(rive):
    """Un point de souffle, dix secondes debout dans dix centimètres d'eau : on
    ne coule pas, et la barre remonte comme sur le sable — l'eau basse est de la
    terre ferme pour le souffle, pas un purgatoire où il resterait figé."""
    r = rive("""function (L, o, j, rive, TT, out) {
        j.endurance = 1; j.surplus = 0;
        let noye = -1;
        for (let i = 0; i < 600 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        out.noye = noye >= 0;
        out.souffle = Math.round(j.endurance);
        out.encore = !!j.nage;
    }""")
    assert r["noye"] is False, "à bout de souffle, on coule au bord de la grève : %s" % r
    assert r["encore"] is True, "on n'est plus dans l'eau : le juge ne prouve rien (%s)" % r
    assert r["souffle"] > 50, "le souffle ne revient pas les pieds dans l'eau : %s" % r


def test_une_tuile_plus_loin_le_souffle_part_et_l_on_coule(rive, paquet):
    """⚠️ L'autre bout de la règle, et il compte autant : le bord ne devient pas
    un abri. Une tuile au large, la baie reprend son dû — sinon le chenal du
    pont cesse d'être un pari et la géographie de M8 ne veut plus rien dire."""
    r = rive("""function (L, o, j, rive, TT, out) {
        for (let i = 0; i < 60; i++) o.frame(1);
        out.souffle = Math.round(j.endurance);
        j.endurance = 2; j.surplus = 0;
        let noye = -1;
        for (let i = 0; i < 120 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        out.noye = noye >= 0;
    }""", tuile=3)
    attendu = paquet["recherche"]["nage"]["souffle_par_image"] * 60
    assert r["basse"] is False, "le juge mesure de l'eau basse : il ne prouve rien"
    assert 100 - r["souffle"] >= attendu * 0.8, (
        "nager au large ne coûte presque rien : %s (attendu ~%s en une seconde)" % (r, attendu)
    )
    assert r["noye"] is True, "à bout de souffle au large, on ne coule pas : %s" % r


def test_on_revient_au_bord_sans_couler(rive):
    """L'histoire que la règle doit rendre possible : on nage, on est à bout, on
    revient — et le dernier mètre ne doit pas tuer. ⚠️ Rouge avant sur la
    dernière ligne : huit pixels d'eau profonde puis la tuile du bord, c'est
    douze points de souffle dans le code d'avant — on n'en a que six, et l'on
    coulait à un pas du sable."""
    r = rive("""function (L, o, j, rive, TT, out) {
        j.endurance = 6; j.surplus = 0;       // douze images de nage : huit pixels d'eau profonde
        o.touche('KeyA');                      // plein ouest : la berge
        let noye = -1;
        for (let i = 0; i < 240 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        o.relacher('KeyA');
        out.noye = noye >= 0;
        out.auSec = !L.Entites.dansLEau(j);
        out.souffle = Math.round(j.endurance);
    }""", tuile=2)
    assert r["noye"] is False, "on coule à un pas du sable : %s" % r
    assert r["auSec"] is True, "on n'a pas regagné la berge : le juge ne prouve rien (%s)" % r
    assert r["souffle"] > 10, "le souffle n'est pas revenu une fois au sec : %s" % r
