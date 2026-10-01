"""La caisse populaire de La Shop (`app/caisse.py`, le casse de l'arc X — 1er oct. 2026).

Martin : « le casse dans un vrai lieu posé en dernier », « la ville d'avant identique (comparée en JSON) ». Elle reprend
la pièce d'un commerce ordinaire sur la ville finie, sans un dé ; ces juges tiennent la ville d'avant clé par clé, le
choix de la porte (une mesure), la pièce (à la mesure du bâtiment, fidèle à son quartier), et ce que le navigateur en
lit (`caisse.js`).
"""

import json
import re
from functools import lru_cache
from unittest import mock

import villes

from app import caisse, carte, devantures, devants, etages, missions, nord


@lru_cache(maxsize=None)
def _sans_la_caisse() -> str:
    """⚠️ La ville témoin se génère sous `mock.patch` : jamais par `villes` (le cache rendrait la ville d'avant)."""
    with mock.patch.object(caisse, "poser", lambda ville: None):
        return json.dumps(carte.generer(), sort_keys=True)


def _porte(v):
    return next(p for p in v["portes"] if p.get("lieu") == caisse.SLUG)


def test_la_ville_d_avant_est_la_meme_cle_par_cle():
    """Tout ce qui n'est pas la caisse est identique, clé par clé : une porte renommée, une enseigne repeinte, une pièce
    redessinée (et ses étages qui ne se montent plus), un point d'intérêt au BOUT de la liste — rien d'autre."""
    avec, sans = villes.generer(), json.loads(_sans_la_caisse())
    avec = json.loads(json.dumps(avec, sort_keys=True))
    differentes = sorted(k for k in avec if avec[k] != sans[k])
    assert differentes == ["devantures", "interieurs", "points_interet", "portes"], differentes
    p = _porte(avec)
    i = avec["portes"].index(p)
    assert [q for k, q in enumerate(avec["portes"]) if k != i] == [q for k, q in enumerate(sans["portes"]) if k != i]
    ancienne = sans["portes"][i]
    assert (ancienne["x"], ancienne["y"]) == (p["x"], p["y"]), "la caisse a pris une autre porte que celle qu'elle a renommée"
    dv = [k for k, (a, b) in enumerate(zip(avec["devantures"], sans["devantures"])) if a != b]
    assert len(dv) == 1 and avec["devantures"][dv[0]]["texte"] == caisse.ENSEIGNE, dv
    assert {k: x for k, x in avec["devantures"][dv[0]].items() if k not in ("texte", "genre")} == \
        {k: x for k, x in sans["devantures"][dv[0]].items() if k not in ("texte", "genre")}
    assert avec["points_interet"][:-1] == sans["points_interet"], "un point d'intérêt de plus, et seulement au bout"
    assert avec["points_interet"][-1]["slug"] == caisse.SLUG
    parties = set(avec["interieurs"]) ^ set(sans["interieurs"])
    assert parties == {caisse.SLUG} | set(etages.suite(sans["interieurs"], ancienne["interieur"])), parties
    assert all(avec["interieurs"][k] == sans["interieurs"][k] for k in avec["interieurs"] if k in sans["interieurs"])


def test_la_caisse_est_a_la_shop_dans_un_commerce_qui_en_garde_un_autre():
    """Le Faubourg n'a plus de porte de commerce libre (dojo, Rialto) : la plus grande pièce d'une famille qui garde une
    autre porte — à la vraie graine, LIQUIDATION, à La Shop. Son enseigne est repeinte et tient sur le bandeau."""
    v = villes.generer()
    p = _porte(v)
    assert nord.LECTEUR.district_en(p["x"], p["y"]) == "shop", (p["x"], p["y"])
    assert p["nom"] == caisse.ENSEIGNE and p["interieur"] == caisse.SLUG
    d = next(q for q in v["devantures"] if q["y"] == p["y"] and q["x"] <= p["x"] < q["x"] + q["l"])
    assert d["texte"] == caisse.ENSEIGNE and devantures.tient_en(caisse.ENSEIGNE, d["l"])
    assert d.get("standing") == "-", "La Shop est un quartier ouvrier : la caisse aussi"
    sans = json.loads(_sans_la_caisse())
    ancienne = next(q for q in sans["portes"] if (q["x"], q["y"]) == (p["x"], p["y"]))["interieur"]
    famille = ancienne.rsplit("_", 1)[0]
    assert any(q.get("interieur", "").rsplit("_", 1)[0] == famille for q in v["portes"]), \
        f"la caisse a pris la dernière porte de la famille {famille}"


def test_la_piece_a_les_mesures_de_son_batiment():
    """La pièce se dessine dans le plancher de celle qu'elle remplace : mêmes mesures, même porte."""
    v = villes.generer()
    p = _porte(v)
    sans = json.loads(_sans_la_caisse())
    vieille = sans["interieurs"][next(q for q in sans["portes"] if (q["x"], q["y"]) == (p["x"], p["y"]))["interieur"]]
    piece = v["interieurs"][caisse.SLUG]
    assert (piece["largeur"], piece["hauteur"]) == (vieille["largeur"], vieille["hauteur"])
    assert piece["sortie"] == vieille["sortie"]


def test_le_choix_est_une_mesure_sans_de():
    """Deux villes, la même caisse ; la plus grande pièce l'emporte ; jamais une façade qu'une mission lit par son nom
    (`boutique:<mot>` : à la graine 1, la plus grande, TRANSMISSION, contient MISSION — celle de h06)."""
    v = villes.generer()
    assert caisse.choisir(json.loads(_sans_la_caisse()))[0]["x"] == _porte(v)["x"]
    assert "MISSION" in caisse._mots_des_missions()
    sans = json.loads(_sans_la_caisse())
    porte, devanture, _ = caisse.choisir(sans)
    devanture["texte"] = "TRANSMISSION"
    autre = caisse.choisir(sans)
    assert autre is None or (autre[0]["x"], autre[0]["y"]) != (porte["x"], porte["y"]), \
        "une façade que h06 lit par son nom est devenue la caisse"


def test_dedans_le_comptoir_la_voute_et_le_bureau_du_gerant():
    """Ce qu'on voit dehors, on le retrouve dedans (Martin, 29 sept.) : une caisse de quartier ouvrier — le comptoir des
    guichets d'un mur à l'autre, sa porte battante ; la voûte de deux sur deux au fond ; le bureau du gérant derrière
    une cloison ; la salle d'attente. Ses gens : deux caissières, le gérant, le vigile, des clients."""
    piece = villes.generer()["interieurs"][caisse.SLUG]
    sol = piece["sol"]
    assert piece["plancher"] == "u" and piece["materiaux"]["c"] == caisse.HABIT
    comptoirs = [y for y, ligne in enumerate(sol) if ligne.count("c") >= piece["largeur"] - 3]
    assert len(comptoirs) == 1, "un comptoir de guichets qui barre la pièce"
    voute = [(x, y) for y, ligne in enumerate(sol) for x, g in enumerate(ligne) if g == "m"]
    assert len(voute) == 4 and max(y for _, y in voute) < comptoirs[0], "la voûte, deux sur deux, derrière les guichets"
    interieur = [ligne[1:-1] for ligne in sol[1:-1]]
    assert sum(ligne.count("B") for ligne in interieur) >= 2, "la cloison du bureau du gérant"
    qui = sorted(g["qui"] for g in piece["gens"])
    assert qui.count("commis") == 2 and "gerant" in qui and "vigile" in qui and "client" in qui, qui
    pt = next(q for q in piece["points"] if q["type"] == "voute")
    atteint = next(c for c in carte.composantes_marchables(piece)
                   if (piece["apparition"]["x"], piece["apparition"]["y"]) in c)
    assert any((pt["x"] + dx, pt["y"] + dy) in atteint for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
        "la voûte se touche depuis la porte (par la porte battante)"
    g = next(g for g in piece["gens"] if g["qui"] == "gerant")
    assert (g["x"], g["y"]) in atteint, "le gérant se rejoint dans son bureau"


def test_toutes_les_mesures_donnent_une_caisse():
    """Toute part assez grande donne une caisse qui se vérifie (`_verifier_piece`), porte à gauche, au milieu ou à droite."""
    for largeur in range(caisse.MESURES_MIN[0], 20):
        for hauteur in range(caisse.MESURES_MIN[1], 20):
            for porte in (1, largeur // 2 + 1, largeur):
                piece = caisse.piece_de_caisse(largeur, hauteur, porte)
                assert any(q["type"] == "voute" for q in piece["points"]), (largeur, hauteur, porte)


def test_son_devant_de_mission_est_degage_sur_quatre_graines():
    """Posée APRÈS les devants, elle ne les fait pas glisser : la porte choisie a déjà un devant de mission libre
    (sinon `test_devants` rougirait sur la graine où elle tombe mal)."""
    for g in (carte.GRAINE, 1, 2, 7):
        v = villes.generer(graine=g)
        p = _porte(v)
        zone = {(p["x"] + dx, p["y"] + dy) for dx, dy in devants.DEVANT_DE_MISSION}
        assert not [d for d in v["decor"] if d["type"] in devants.DECOR_MOBILE and (d["x"], d["y"]) in zone], g
    assert caisse.SLUG in devants.lieux_de_mission(villes.generer())


def test_les_objets_de_la_caisse_sont_ceux_des_missions():
    """Chaque objectif `obtenir` à la caisse demande un objet qu'elle sait donner, et chaque façon de donner sert."""
    vus = {o["objet"] for m in missions.CATALOGUE for o in m["objectifs"] if o.get("table") == "caisse"}
    assert vus == set(caisse.OBJETS), vus
    assert re.fullmatch(r"[a-z_]+", caisse.SLUG)


def test_le_navigateur_a_la_meme_liste(banc):
    r = banc("function (L, o) { return { objets: L.Caisse.OBJETS, slug: L.Caisse.SLUG, tenue: L.Caisse.TENUE }; }")
    assert r["objets"] == caisse.OBJETS and r["slug"] == caisse.SLUG
    from app import magasins
    assert any(t["slug"] == r["tenue"] and t["prix"] is None for t in magasins.TENUES), "l'uniforme ne se vend pas"
