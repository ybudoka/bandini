"""Le marché aux puces du dimanche : où il se monte, ce qu'il vend, ce qu'il pèse — et la ville qui ne bouge pas.

⚠️ Les règles sont écrites ICI (un terrain de 8 × 4 d'herbe ou de friche, libre, loin des trouvailles et des pistes
des sauts) : un juge qui relirait `puces.TERRAIN` changerait avec la constante qu'il garde.
"""

import json

import pytest

from app import carte, collectionner, decoration, puces


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_le_terrain_est_un_terrain_vague_libre(ville):
    m = ville["collections"]["puces"]
    assert m and (m["l"], m["h"]) == (8, 4)
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    for j in range(4):
        for i in range(8):
            x, y = m["x"] + i, m["y"] + j
            assert ville["sol"][y][x] in (",", ";"), f"({x},{y}) : « {ville['sol'][y][x]} »"
            assert (x, y) not in decor, f"un décor sur le marché en ({x},{y})"
    for e in m["etals"]:
        assert m["x"] <= e["x"] and e["x"] + 1 < m["x"] + 8 and m["y"] <= e["y"] < m["y"] + 4, e
    # Loin des trouvailles et de la piste de chaque saut.
    col = ville["collections"]
    for q in col["cartes"] + col["bebelles"]:
        assert not (m["x"] - 6 <= q["x"] < m["x"] + 14 and m["y"] - 6 <= q["y"] < m["y"] + 10), q
    for s in col["sauts"]:
        for k in range(-7, 12):
            x, y = s["x"] + s["dx"] * k, s["y"] + s["dy"] * k
            assert not (m["x"] <= x < m["x"] + 8 and m["y"] <= y < m["y"] + 4), f"la piste de {s['slug']} traverse le marché"


def test_le_plus_proche_de_la_planque(ville):
    """Il n'existe pas de terrain libre de 8 × 4 plus près de la planque, à pied : on déplace le marché d'une rangée
    en y posant un décor — il part ailleurs, jamais plus près."""
    m = ville["collections"]["puces"]
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    v["decor"] = v["decor"] + [{"type": "buisson", "x": m["x"] + 3, "y": m["y"] + 1}]
    autre = collectionner.poser(v)["puces"]
    assert autre and (autre["x"], autre["y"]) != (m["x"], m["y"]), "un décor sur le terrain n'a pas déplacé le marché"


def test_rien_d_autre_n_a_bouge(ville):
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    assert collectionner.poser(v) == ville["collections"], "la pose varie"


def test_ce_qu_il_vend(paquets):
    col = json.loads(paquets.collections.corps)
    p = col["puces"]
    assert [e["vend"] for e in p["etals"]] == ["cartes", "meubles"]
    assert all("x" in e and e["marchand"]["qui"] in p["repliques"] for e in p["etals"])
    r = p["regle"]
    assert r["prix_carte"] > collectionner.REGLE["prime"], "une carte des puces coûte moins que ce qu'elle rapporte"
    assert 0 < r["rabais_meubles"] < 1 and 0 < r["offre"] < 1 and 0 < r["humeur"] < 100
    assert {m["slug"] for m in decoration.MEUBLES if "puces" in m["ou"]} == {"jukebox", "sofa", "televiseur", "tapis_tresse"}
    assert "puces" not in json.loads(paquets.definitions.corps)


def test_jamais_sur_une_trouvaille():
    """⚠️ Sur la graine livrée, le terrain le plus proche est déjà loin de tout : un pré synthétique de 30 × 12, une carte
    au coin d'où l'on part — le marché se pose à six tuiles d'elle au moins."""
    sol = ["," * 30 for _ in range(12)]
    dist = {(x, y): x + y for y in range(12) for x in range(30)}
    m = puces.poser({"sol": sol}, dist, [(2, 2)])
    assert m and not (m["x"] - 6 <= 2 < m["x"] + 14 and m["y"] - 6 <= 2 < m["y"] + 10), m


# --- La deuxième vague : des voix, la rumeur, et on y vend ------------------------------------------------------------

#: Ce que chacun doit pouvoir dire (Martin, 30 sept. 2026) : l'accueil, le marchandage accepté ou refusé, la vente,
#: rien à vendre cette semaine, au revoir — et, chez Gisèle, le rachat.
COMMUNES = {"salut", "accueil-1", "accueil-2", "accueil-3", "vente", "accepte", "refuse", "rien", "aurevoir"}
NOMS = {"ti_rheal": ("Ti-Rhéal", "Bergeron"), "gisele": ("Gisèle", "Lachapelle")}


def test_chaque_marchand_a_toutes_ses_repliques():
    par_qui = {}
    for r in puces.REPLIQUES:
        par_qui.setdefault(r["qui"], set()).add(r["cle"])
    assert set(par_qui) == set(puces.VOIX) == {e["marchand"]["qui"] for e in puces.ETALS}
    for qui, cles in par_qui.items():
        assert COMMUNES <= cles, f"{qui} : il manque {sorted(COMMUNES - cles)}"
    assert {"rachat", "rachat-conclu", "plus-accepte", "plus-refuse"} <= par_qui["gisele"]
    assert len({(r["qui"], r["cle"]) for r in puces.REPLIQUES}) == len(puces.REPLIQUES), "deux répliques, une clé"


def test_chacun_se_nomme_une_fois_dans_sa_salutation():
    """« Qui parle se nomme » (docs/jeu-d-acteur.md § 3.11) : le nom dans `salut`, et nulle part ailleurs."""
    for r in puces.REPLIQUES:
        prenom, nom = NOMS[r["qui"]]
        if r["cle"] == "salut":
            assert r["texte"].startswith(prenom + " " + nom), r
        else:
            assert prenom not in r["texte"] and nom not in r["texte"], f"{r['qui']} se renomme dans « {r['cle']} »"


def test_chaque_marchand_a_sa_voix_a_lui():
    from app import audio
    usages = audio.usages_des_voix()
    for qui, v in puces.VOIX.items():
        assert usages[v["voix"]] == {qui}, f"la voix de {qui} sert aussi à {usages[v['voix']] - {qui}}"
    assert {v["voix"] for v in audio.voix_puces() if v["qui"] == "gisele"} == {puces.VOIX["gisele"]["voix"]}


def test_les_voix_et_la_rumeur_voyagent_avec_le_marche_pas_dans_les_definitions(paquets):
    from app import audio
    defs = paquets.definitions.corps.decode("utf-8")
    assert "puces-" not in defs and "rumeur_puces" not in defs, "le marché a mis un octet de plus dans les définitions"
    assert "puces" in audio.LIEUX_A_PART and audio.LIEUX["puces"] == ["rumeur_puces"]
    p = json.loads(paquets.collections.corps)["puces"]
    assert p["sons"]["lieu"] == "puces" and [e["slug"] for e in p["sons"]["echantillons"]] == ["rumeur_puces"]
    series = {s["prefixe"]: s for s in p["voix"]}
    assert set(series) == {"ti_rheal-puces-", "gisele-puces-"}
    for qui, s in (("ti_rheal", series["ti_rheal-puces-"]), ("gisele", series["gisele-puces-"])):
        assert s["mission"] == "puces" and s["qui"] == qui
        assert sorted(s["noms"]) == sorted(r["cle"] for r in puces.REPLIQUES if r["qui"] == qui)
    assert p["repliques"]["gisele"]["salut"].startswith("Gisèle")
    assert '"jeu"' not in paquets.collections.corps.decode("utf-8"), "le jeu d'acteur est parti au navigateur"


def test_revendre_a_gisele_ne_paie_jamais_plus_qu_acheter():
    """⚠️ Un choix, pas une pompe à argent : le plus qu'on tire d'un meuble (son prix de rachat, demandé plus haut)
    reste sous le moins qu'il coûte — au catalogue, ou chez Gisèle à l'offre acceptée."""
    r = puces.REGLE
    for m in decoration.MEUBLES:
        plus_haut = round(round(m["prix"] * r["rachat"]) * r["demande"])
        moins_cher = min([m["prix"]] + ([round(round(m["prix"] * r["rabais_meubles"]) * r["offre"])] if "puces" in m["ou"] else []))
        assert 0 < round(m["prix"] * r["rachat"]) < plus_haut < moins_cher, (m["slug"], plus_haut, moins_cher)
    assert 0 < r["humeur_rachat"] < 100
