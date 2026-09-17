"""Le mobilier de rue : des arbres de temps à autre, bien placés, et des bancs.

Demande de Martin (16 sept. 2026) : « je veux des bancs sur le bord de la rue,
des arbres de temps à autre bien positionnés ».

⚠️ Les juges lisent ce que `mobilier.semer` AJOUTE à la ville — la même ville
bâtie sans lui, comparée à elle-même avec lui. Un arbre de parc ou un banc de
terrain vague n'a rien à voir ici.
"""

import pytest

from app import autobus, carte, mobilier


@pytest.fixture(scope="module")
def villes():
    avec = carte.generer()
    original = mobilier.semer
    mobilier.semer = lambda chantier, ville, graine: {}
    try:
        sans = carte.generer()
    finally:
        mobilier.semer = original
    ajoutes = avec["decor"][len(sans["decor"]):]
    return avec, sans, ajoutes


#: Le banc selon le côté du trottoir. ⚠️ En toutes lettres, pas relu dans
#: `mobilier.BANCS_PAR_COTE` : un juge qui relit la table qu'il juge ne rougit pas.
REGARDE = {(0, 1): "banc", (0, -1): "banc_nord", (1, 0): "banc_est", (-1, 0): "banc_ouest"}

#: Le coin d'un croisement, en tuiles autour de la boîte — le chiffre de la règle,
#: pas la constante du code.
COIN = 3


def cote_du_trottoir(ville, x, y):
    sol, voie = ville["sol"], ville["voie"]
    cotes = [(dx, dy) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
             if sol[y + dy][x + dx] == "." and voie[y + 2 * dy][x + 2 * dx] != "."]
    return cotes[0] if len(cotes) == 1 else None


def test_la_rue_se_plante_et_se_meuble(villes):
    _avec, _sans, ajoutes = villes
    arbres = [d for d in ajoutes if d["type"] == "arbre"]
    bancs = [d for d in ajoutes if d["type"] in mobilier.BANCS_PAR_COTE.values()]
    # ⚠️ Le bac à fleurs est du mobilier de rue cossue (`test_quartiers`).
    assert {d["type"] for d in ajoutes} <= {"arbre", "bac_fleurs", *mobilier.BANCS_PAR_COTE.values()}
    assert 120 <= len(arbres) <= 400, f"{len(arbres)} arbres de rue"
    assert 25 <= len(bancs) <= 200, f"{len(bancs)} bancs de rue"


def test_chaque_meuble_borde_un_trottoir_et_le_banc_regarde_la_rue(villes):
    avec, _sans, ajoutes = villes
    for d in ajoutes:
        x, y = d["x"], d["y"]
        assert avec["sol"][y][x] in ("_", ","), f"{d['type']} en {(x, y)} sur « {avec['sol'][y][x]} »"
        cote = cote_du_trottoir(avec, x, y)
        assert cote is not None, f"{d['type']} en {(x, y)} ne borde pas UN trottoir"
        if d["type"].startswith("banc"):
            assert d["type"] == REGARDE[cote], f"{d['type']} en {(x, y)} tourne le dos à la rue"


def test_rien_au_coin_d_un_croisement(villes):
    """Le coin est au feu, au lampadaire et à la vue de qui traverse."""
    avec, _sans, ajoutes = villes
    for d in ajoutes:
        for i in avec["intersections"]:
            dedans = (i["x"] - COIN - 1 <= d["x"] < i["x"] + i["l"] + COIN + 1
                      and i["y"] - COIN - 1 <= d["y"] < i["y"] + i["h"] + COIN + 1)
            assert not dedans, f"{d['type']} en {(d['x'], d['y'])} au coin du croisement {i['x'], i['y']}"


def test_le_parvis_du_terminus_reste_nu(villes):
    """⚠️ Le car de l'ouverture y dépose le cousin, qui marche jusqu'à la porte :
    ni abribus, ni banc, ni arbre neuf sur ce trajet."""
    avec, sans, _ajoutes = villes
    nus = autobus.parvis(avec)
    avant = {(d["x"], d["y"]) for d in sans["decor"]}
    for d in avec["decor"]:
        if (d["x"], d["y"]) in nus and (d["x"], d["y"]) not in avant:
            raise AssertionError(f"{d['type']} en {(d['x'], d['y'])} sur le parvis du terminus")


def test_rien_devant_une_porte_ni_juste_a_cote(villes):
    avec, _sans, ajoutes = villes
    devant = {(p["x"] + i, p["y"] + j) for p in avec["portes"] for j in (1, 2, 3) for i in (-1, 0, 1)}
    for d in ajoutes:
        assert (d["x"], d["y"]) not in devant, f"{d['type']} en {(d['x'], d['y'])} devant une porte"


def test_rien_au_bout_d_une_sortie_de_char(villes):
    avec, _sans, ajoutes = villes
    for d in ajoutes:
        dx, dy = cote_du_trottoir(avec, d["x"], d["y"])
        derriere = avec["sol"][d["y"] - dy][d["x"] - dx]
        assert derriere not in mobilier.SORTIES_DE_CHAR, f"{d['type']} en {(d['x'], d['y'])} ferme une sortie ({derriere})"


def test_un_meuble_ne_colle_a_aucun_autre(villes):
    avec, _sans, ajoutes = villes
    for d in ajoutes:
        voisins = [e for e in avec["decor"] if e is not d
                   and abs(e["x"] - d["x"]) <= 1 and abs(e["y"] - d["y"]) <= 1]
        assert not voisins, f"{d['type']} en {(d['x'], d['y'])} collé à {voisins[0]['type']}"


def test_le_mobilier_ne_ferme_aucun_passage(villes):
    """⚠️ Un arbre est SOLIDE pour un piéton. Tout ce qu'on atteignait à pied sans
    le mobilier s'atteint encore avec — moins les tuiles qu'il occupe."""
    avec, sans, ajoutes = villes

    def atteignables(ville):
        sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
        bloque = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
        depart = tuple(autobus.detail(ville, 0)["quai"])
        vus, pile = {depart}, [depart]
        while pile:
            x, y = pile.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (0 <= n[0] < largeur and 0 <= n[1] < hauteur and n not in vus
                        and carte.marchable(sol[n[1]][n[0]]) and n not in bloque):
                    vus.add(n)
                    pile.append(n)
        return vus

    pris = {(d["x"], d["y"]) for d in ajoutes}
    perdus = (atteignables(sans) - pris) - atteignables(avec)
    assert not perdus, f"{len(perdus)} tuiles qu'on n'atteint plus à pied, dont {sorted(perdus)[:4]}"


def test_les_arbres_suivent_un_pas_et_le_quartier(villes):
    """Une rangée, pas une poignée : deux arbres d'un même bord ne se touchent
    pas, et Les Érables sont plus plantés que La Shop."""
    avec, _sans, ajoutes = villes
    arbres = sorted((d["y"], d["x"]) for d in ajoutes if d["type"] == "arbre")
    for (y1, x1), (y2, x2) in zip(arbres, arbres[1:]):
        if y1 == y2:
            assert x2 - x1 >= 4, f"deux arbres de rue collés en {(x1, y1)} et {(x2, y2)}"
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    par_quartier: dict[str, int] = {}
    for y, x in arbres:
        q = chantier.district_en(x, y)
        par_quartier[q] = par_quartier.get(q, 0) + 1
    assert par_quartier.get("erables", 0) > 2 * par_quartier.get("shop", 0), par_quartier


def test_les_abribus_ont_leur_banc_qui_regarde_la_rue(villes):
    """Le banc d'un abribus est posé par la ligne, pas par le semis — mais il
    obéit à la même règle : il regarde la rue."""
    avec, _sans, _ajoutes = villes
    decor = {(d["x"], d["y"]): d["type"] for d in avec["decor"]}
    avec_banc = 0
    arrets = [autobus.detail(avec, rang) for rang in range(len(avec["autobus"]["arrets"]))]
    for a in arrets:
        dx, dy = autobus.PAS[a["sens"]]
        for k in (-1, 1):
            t = decor.get((a["abri"][0] + dx * k, a["abri"][1] + dy * k))
            if t and t.startswith("banc"):
                assert t == autobus.BANCS[a["sens"]], f"le banc de {a['nom']} tourne le dos à la rue"
                avec_banc += 1
    assert avec_banc >= len(arrets) * 0.8
