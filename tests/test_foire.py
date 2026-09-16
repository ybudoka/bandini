"""Le bord de l'eau, 4e vague — la foire de La Pointe.

⚠️ **On n'agrandit pas la grille : on la DÉPENSE.** La leçon de l'île vaut ici
aussi — la ville a la place. La foire prend une des trois taches de bois du
district-parc (un glyphe `n` du plan devient `f`), et la grève est juste à côté.
"""

import pytest

from app import carte

MANEGES = ("carrousel", "tasses", "chaises_volantes")
JEUX = ("galerie_tir", "marteau_force", "peche_canards")


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def test_la_pointe_a_une_foire_et_une_seule():
    """Une foire par ville : c'est un lieu, pas un genre d'îlot."""
    pointe = next(d for d in carte.DISTRICTS if d["slug"] == "pointe")
    assert sum(ligne.count("f") for ligne in pointe["plan"]) == 1
    assert sum(ligne.count("f") for d in carte.DISTRICTS for ligne in d["plan"]) == 1
    # Et il reste du bois : la foire en a pris UNE tache, pas toutes.
    assert sum(ligne.count("n") for ligne in pointe["plan"]) >= 1


def test_la_foire_porte_sa_grande_roue_et_ses_manèges(ville):
    """⚠️ **La grande roue n'est pas un manège, c'est un belvédère qui tourne** —
    et elle est au bout de l'allée : on la voit de l'entrée, et c'est elle qui
    dit où l'on va."""
    poses = {}
    for d in ville["decor"]:
        poses[d["type"]] = poses.get(d["type"], 0) + 1
    assert poses.get("grande_roue") == 1, "la foire n'a pas sa roue (ou en a deux)"
    for quoi in MANEGES:
        assert poses.get(quoi) == 1, f"pas de {quoi}"
    for quoi in JEUX:
        assert poses.get(quoi) == 1, f"pas de {quoi}"
    assert ville["roue"], "le navigateur ne sait pas où est la roue"
    roue = next(d for d in ville["decor"] if d["type"] == "grande_roue")
    assert (roue["x"], roue["y"]) == (ville["roue"]["x"], ville["roue"]["y"])


def test_les_trois_jeux_sont_portes_par_le_paquet(ville):
    """⚠️ « Une fiche que le navigateur ne lisait pas » : sans leurs positions,
    les trois défis de foire n'auraient nulle part où poser leur panneau."""
    jeux = ville["jeux_de_foire"]
    assert {j["slug"] for j in jeux} == set(JEUX)
    for j in jeux:
        assert ville["sol"][j["y"]][j["x"]] not in ("~",), "un kiosque à l'eau"


def test_tout_ce_qui_est_de_la_foire_tient_dans_son_bloc(ville):
    """La foire n'avale aucune rue : elle tient dans la tache de bois qu'on lui
    a donnée. Le juge la mesure par l'écart entre ses pièces."""
    pieces = [d for d in ville["decor"] if d["type"] in MANEGES + JEUX + ("grande_roue",)]
    assert len(pieces) == 7
    # ⚠️ Contre le rectangle QU'ELLE DÉCLARE, pas contre un chiffre deviné :
    # ma première version supposait « une trentaine de tuiles » et accusait la
    # foire d'un débordement qui n'existait pas — le bloc en fait 69.
    f = ville["foire"]
    assert f, "la foire ne déclare pas son rectangle"
    for d in pieces:
        assert f["x"] <= d["x"] < f["x"] + f["l"], f"{d['type']} déborde à l'est/ouest"
        assert f["y"] <= d["y"] < f["y"] + f["h"], f"{d['type']} déborde au nord/sud"
    # ⚠️ Et rien n'est sur la chaussée : un manège au milieu d'une rue serait
    # un obstacle que le trafic n'a jamais appris à contourner.
    for d in pieces:
        glyphe = ville["sol"][d["y"]][d["x"]]
        assert not carte.LEGENDE[glyphe].get("route"), f"{d['type']} est sur la chaussée"


def test_deux_pieces_de_foire_ne_se_collent_pas(ville):
    """Une foire où les manèges se touchent n'est pas une foire, c'est un
    entrepôt de manèges."""
    ecart = carte.FOIRE["ecart"]
    pieces = [d for d in ville["decor"] if d["type"] in MANEGES + JEUX]
    for i, a in enumerate(pieces):
        for b in pieces[i + 1:]:
            assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= ecart, (a, b)


def test_la_foire_ne_tire_pas_dans_le_de_de_la_ville():
    """⚠️ La leçon des dés, appliquée avant qu'elle ne coûte : la foire a son
    propre dé. Un semis qui tire dans le dé principal décale toute la suite du
    hasard — douze scènes d'amuseur ont déjà disparu du Faubourg pour une
    histoire de clôture."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    for y in range(6, 30):
        for x in range(6, 40):
            chantier.sol[y][x] = ","
    avant_ville, avant_foire = chantier.des.etat, chantier.des_foire.etat
    chantier._foire(6, 6, 34, 24)
    assert chantier.des.etat == avant_ville, (
        "la foire a tiré dans le dé de la ville : tout ce qui suit est décalé")
    assert chantier.des_foire.etat != avant_foire, "la foire n'a pas tiré son propre dé"
    assert chantier.roue, "la foire n'a pas posé sa roue"


def test_les_manèges_tournent_et_on_n_y_monte_pas(banc, paquet):
    """⚠️ **Du décor animé, et on n'y monte pas.** Un manège où l'on monte et
    qui ne donne rien est un décor cher ; un manège qui tourne avec du monde
    dessus est une ville qui vit. C'est l'étage 1 des machines de chantier :
    une articulation, pas dix — chaque pose est cuite **une fois** et reste en
    cache, donc un manège qui tourne coûte quatre canevas, pas un par image."""
    r = banc("""function (L, o) {
        const out = {};
        for (const nom of %s) {
          const d = L.DECORS[nom];
          out[nom] = d ? { anime: d.anime || 0, variantes: d.variantes || 0,
                           arrete: d.arrete || 0, pv: d.pv || 0, solide: !!d.solide } : null;
        }
        return out;
    }""" % list(MANEGES + ("grande_roue",)))
    for nom, d in r.items():
        assert d, f"{nom} n'a aucun dessin"
        assert d["anime"] > 0 and d["variantes"] > 1, f"{nom} ne tourne pas"
        # ⚠️ Ce qui porte `arrete` n'a PAS de `pv` : il encaisse et ne tombe
        # jamais — c'est ce qui fait un abri, et un manège en est un.
        assert d["arrete"] > 0, f"{nom} ne retient personne"
        assert d["pv"] == 0, f"{nom} peut être démoli"
        assert d["solide"], f"{nom} se traverse"
