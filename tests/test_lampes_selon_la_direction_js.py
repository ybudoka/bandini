"""On ne voit une lampe que si elle regarde l'œil — les phares selon la direction.

Retour de Martin (22 sept. 2026), deux captures : un char qui monte l'écran et un qui le
descend montraient tous deux leurs phares ET leurs feux arrière. La ville se voit de trois
quarts : on voit les faces tournées vers le bas de l'écran.

⚠️ Par le RENDU : les lueurs sont ramassées en dessinant ; on lit ce qu'une image vraie a
allumé pour le char. Et les sens sont écrits ici en toutes lettres.
"""

import re

import pytest

NUIT = 0.9

#: Un char mené, seul dans la rue, la nuit, dessiné une fois au cap voulu.
UN_CHAR = """
    function lueurs(L, slug, angle) {
      L.Jeu.commencer();
      const t = L.B.defs.conduite.trafic;
      t.vehicules_max = 0; t.stationnes_max = 0; t.garer_la_nuit.max = 0;
      L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
      L.B.partie.heure = %s;
      const j = L.B.joueur;
      const v = L.Vehicules.creer(slug, j.x + 60, j.y, angle, { conducteur: 'trafic', etat: 'roule' });
      v.vitesse = 0; v.vx = 0; v.vy = 0; v.angle = angle;
      L.Monde.centrerCamera(v.x, v.y);
      L.Jeu.rendre();
      const out = { phare: [], arriere: [], faisceau: 0 };
      for (const l of L.Vehicules.lampesDesPhares()) {
        if (l.phare === v) out.phare.push(l.c);
        if (l.arriere === v) out.arriere.push(l.c);
        if (l.faisceau === v) out.faisceau++;
      }
      L.Entites.retirer(v);
      return out;
    }
""" % NUIT

NORD, EST, SUD, OUEST = "-Math.PI / 2", "0", "Math.PI / 2", "Math.PI"


def _alpha(c):
    return float(re.search(r"rgba\([^)]*,\s*([\d.]+)\)", c).group(1))


@pytest.mark.parametrize("slug", ["auto", "camion"])
def test_qui_monte_montre_ses_feux_arriere_et_qui_descend_ses_phares(banc, paquet, slug):
    """Il monte l'écran : on voit son arrière — ses feux rouges ; ses phares sont sur la face
    d'en avant, cachés par la caisse. Il descend : ses phares, pas ses feux arrière. ⚠️ Le
    faisceau au sol, lui, éclaire devant lui dans les deux cas."""
    r = banc("""function (L, o) {
        %s
        return { nord: lueurs(L, '%s', %s), sud: lueurs(L, '%s', %s) };
    }""" % (UN_CHAR, slug, NORD, slug, SUD))
    assert r["nord"]["phare"] == [], "%s monte l'écran et on voit ses phares : %s" % (slug, r["nord"])
    assert r["nord"]["arriere"], "%s monte l'écran et on ne voit pas ses feux arrière" % slug
    assert r["sud"]["phare"], "%s descend l'écran et on ne voit pas ses phares" % slug
    assert r["sud"]["arriere"] == [], "%s descend l'écran et on voit ses feux arrière : %s" % (slug, r["sud"])
    assert r["nord"]["faisceau"] == 1 and r["sud"]["faisceau"] == 1, "le faisceau au sol a disparu : %s" % r


@pytest.mark.parametrize("slug", ["auto", "camion"])
def test_de_profil_on_devine_les_deux_et_moins_que_de_face(banc, paquet, slug):
    """De profil (vers l'est comme vers l'ouest), on devine le coin des phares ET des feux
    arrière — plus faiblement que de face : on n'en voit qu'une part."""
    r = banc("""function (L, o) {
        %s
        return { est: lueurs(L, '%s', %s), ouest: lueurs(L, '%s', %s), sud: lueurs(L, '%s', %s),
                 nord: lueurs(L, '%s', %s) };
    }""" % (UN_CHAR, slug, EST, slug, OUEST, slug, SUD, slug, NORD))
    for cote in ("est", "ouest"):
        assert r[cote]["phare"] and r[cote]["arriere"], "%s de profil (%s) : %s" % (slug, cote, r[cote])
    de_face = sum(_alpha(c) for c in r["sud"]["phare"])
    de_profil = max(sum(_alpha(c) for c in r[cote]["phare"]) for cote in ("est", "ouest"))
    assert de_profil < de_face, "%s : ses phares luisent autant de profil (%.2f) que de face (%.2f)" % (
        slug, de_profil, de_face)
    # Et les feux arrière : pleins quand il monte (ils nous regardent), plus faibles de profil.
    dos = sum(_alpha(c) for c in r["nord"]["arriere"])
    flanc = max(sum(_alpha(c) for c in r[cote]["arriere"]) for cote in ("est", "ouest"))
    assert flanc < dos, "%s : ses feux arrière luisent autant de profil (%.2f) que de dos (%.2f)" % (slug, flanc, dos)
