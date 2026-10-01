"""Les Mantes : l'école rivale du Petit-Canton et le gang de ses élèves (docs/jalons/l-ecole-rivale.md).

⚠️ Le ton : le quartier est à ses habitants, l'école est UNE adresse, et le gang, ce sont ses élèves — le
territoire est le coin de l'école, jamais la rue principale.
"""

import json

import pytest
import villes

from app import carte, devantures, etages, garderobe, mantes, nord, pietons, techniques


@pytest.fixture(scope="module")
def ville():
    return villes.generer()


def _ecole(ville):
    portes = [p for p in ville["portes"] if p.get("interieur") == mantes.SLUG]
    assert len(portes) == 1, portes
    return portes[0]


def _zone(ville):
    zones = [z for z in ville["zones"] if z.get("gang") == "mantes"]
    assert len(zones) == 1, zones
    return zones[0]


def test_l_ecole_est_une_adresse_du_petit_canton_hors_de_la_rue_principale(ville):
    p = _ecole(ville)
    assert nord.LECTEUR.district_en(p["x"], p["y"]) == "canton"
    ch = nord._bande()
    x_rue, _ = __import__("app.canton", fromlist=["rue_principale"]).rue_principale(ch, nord.district("canton"))
    assert p["x"] < x_rue, "l'école est sur la rue principale : la rue commerçante est aux gens du quartier"
    assert p["nom"] == mantes.ENSEIGNE and p["lieu"] == mantes.SLUG
    dev = [d for d in ville["devantures"] if d["y"] == p["y"] and d["x"] <= p["x"] < d["x"] + d["l"]]
    assert len(dev) == 1 and dev[0]["texte"] == mantes.ENSEIGNE
    assert devantures.tient_en(mantes.ENSEIGNE, dev[0]["l"])
    points = [q for q in ville["points_interet"] if q["type"] == mantes.SLUG]
    assert points == [{"type": mantes.SLUG, "slug": mantes.SLUG, "nom": mantes.NOM, "x": p["x"], "y": p["y"] + 1,
                       "famille": "service"}]


def test_l_ecole_a_ses_mannequins_son_sac_et_ses_eleves(ville):
    piece = ville["interieurs"][mantes.SLUG]
    sol = "".join(piece["sol"])
    assert sol.count("%") == 2 and "@" in sol, piece["sol"]
    assert "A" not in sol, "un kwoon a un plancher de bois, pas le tatami du DOJO DION"
    assert [(q["type"], q.get("garde")) for q in piece["points"]] == [("fouiller", "mantes"), ("maitre", None)], \
        piece["points"]
    qui = [g["qui"] for g in piece["gens"]]
    assert qui and set(qui) == {"mante"} and len(qui) >= 2, qui
    # Le vieux maître (vague 2) se tient devant le sac, face à la salle — sur le plancher, et personne sous lui.
    maitre = next(q for q in piece["points"] if q["type"] == mantes.POINT_DU_MAITRE)
    assert piece["sol"][maitre["y"]][maitre["x"]] == "t", "le maître se tient sur le plancher, pas dans un meuble"
    assert (maitre["x"], maitre["y"]) not in {(g["x"], g["y"]) for g in piece["gens"]}, "un élève sous ses sandales"
    assert "mante" in carte.QUI_DEDANS


def test_le_territoire_est_le_coin_de_l_ecole(ville):
    """Autour de l'école, dans le Petit-Canton, à l'ouest de la rue principale — et le DERNIER rectangle qui
    contient la porte de l'école (`Monde.zoneA` garde la dernière zone qui contient un point)."""
    z = _zone(ville)
    p = _ecole(ville)
    assert z["x"] <= p["x"] < z["x"] + z["l"] and z["y"] <= p["y"] < z["y"] + z["h"]
    canton = next(q for q in ville["zones"] if q["slug"] == "canton")
    assert canton["x"] <= z["x"] and z["x"] + z["l"] <= canton["x"] + canton["l"]
    assert canton["y"] <= z["y"] and z["y"] + z["h"] <= canton["y"] + canton["h"]
    x_rue = nord._bande().xr[nord.district("canton")["bx"] + 4]
    assert z["x"] + z["l"] <= x_rue, "leur territoire mange la rue principale"
    dernieres = [q for q in ville["zones"] if q["x"] <= p["x"] < q["x"] + q["l"] and q["y"] <= p["y"] < q["y"] + q["h"]]
    assert dernieres[-1] is not None and dernieres[-1]["slug"] == "mantes"
    # Loin de la couture : une partie neuve, née au terminus, n'est pas sur leur territoire.
    app = ville["apparition"]["joueur"]
    assert not (z["x"] <= app["x"] < z["x"] + z["l"] and z["y"] <= app["y"] < z["y"] + z["h"])


def test_leur_frontiere_est_la_couture_face_aux_cravates(ville):
    lignes = [f for f in pietons.frontieres(ville) if "mantes" in (f["a"], f["b"])]
    assert len(lignes) == 1, lignes
    f = lignes[0]
    # ⚠️ `a` est la gang du petit côté (le nord) : les Mantes, au-dessus de la couture.
    assert (f["a"], f["b"], f["axe"], f["y"]) == ("mantes", "cravates", "h", nord.DECALAGE_NORD), f


def test_l_ecole_ne_deplace_rien(monkeypatch):
    """La ville, identique : seules la porte, la devanture, la pièce, le point, les zones (le territoire au bout)
    et le gang du district changent — et la pièce de commerce reprise disparaît."""
    avec = carte.generer()
    monkeypatch.setattr(mantes, "poser", lambda ville, ch, district, n: None)
    sans = carte.generer()
    for cle in avec:
        if cle in ("portes", "devantures", "interieurs", "points_interet", "zones", "frenesies"):
            continue
        assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    # La frénésie du quartier vise les Mantes : son crâne se cache près de LEUR cour (`frenesies.cachette`), et
    # seulement lui bouge.
    bouge = [(a, b) for a, b in zip(avec["frenesies"], sans["frenesies"]) if a != b]
    assert [a["slug"] for a, _ in bouge] in ([], ["canton"]), bouge
    portes = [(a, b) for a, b in zip(avec["portes"], sans["portes"]) if a != b]
    assert len(portes) == 1 and portes[0][0]["interieur"] == mantes.SLUG, portes
    enseignes = [(a, b) for a, b in zip(avec["devantures"], sans["devantures"]) if a != b]
    assert len(enseignes) == 1 and enseignes[0][0]["texte"] == mantes.ENSEIGNE, enseignes
    assert set(avec["interieurs"]) - set(sans["interieurs"]) == {mantes.SLUG}
    # ⚠️ Avec ses étages (`etages.monter`) : le logement du commerçant s'en va avec sa boutique.
    assert set(sans["interieurs"]) - set(avec["interieurs"]) == set(etages.suite(sans["interieurs"],
                                                                                portes[0][1]["interieur"]))
    assert [q for q in avec["points_interet"] if q["type"] != mantes.SLUG] == sans["points_interet"]
    assert len(avec["points_interet"]) == len(sans["points_interet"]) + 1
    neuves = [z for z in avec["zones"] if z not in sans["zones"]]
    assert [z for z in avec["zones"] if z.get("gang") != "mantes"] == sans["zones"]
    assert len(neuves) == 1 and neuves[0]["gang"] == "mantes"


def test_sans_facade_qui_convient_pas_d_ecole_et_rien_ne_plante(monkeypatch):
    monkeypatch.setattr(mantes, "MESURES_MIN", (99, 99))
    ville = carte.generer()
    assert mantes.SLUG not in ville["interieurs"]
    assert not [p for p in ville["portes"] if p.get("interieur") == mantes.SLUG]
    # Le territoire reste : le gang a son coin même sans enseigne.
    assert [z for z in ville["zones"] if z.get("gang") == "mantes"]


def test_un_gang_qui_sait_se_battre_et_pas_a_la_batte():
    """Le Mante : pas d'arme, le répertoire. Plus de vie et de courage que tous les autres gangs, et au moins
    aussi vite."""
    m = pietons.par_slug("mante")
    gang = next(g for g in pietons.GANGS if g["slug"] == "mantes")
    assert gang["pieton"] == "mante" and gang["district"] == "canton" and gang["zone"] == "mantes"
    assert m["gang"] == "mantes" and m["arme"] is None and m["frequence"] == 0.0
    catalogue = {t["slug"]: t for t in techniques.CATALOGUE}
    assert m["techniques"] and all(s in catalogue and not catalogue[s]["gratuite"] for s in m["techniques"])
    gestes = {catalogue[s]["geste"] for s in m["techniques"]}
    assert {"prise_avant", "prise_vers_soi", "contre"} <= gestes, "ni projection ni parade"
    assert any(catalogue[s]["style"] == "karate" for s in m["techniques"]), "pas un seul pied"
    autres = [pietons.par_slug(g["pieton"]) for g in pietons.GANGS if g["slug"] != "mantes"]
    assert all(m["vie"] > a["vie"] and m["courage"] >= a["courage"] for a in autres)
    assert all("techniques" not in a for a in pietons.CATALOGUE if a["slug"] != "mante"), \
        "un champ `techniques` vide sur les autres archétypes alourdit le paquet"


def test_leur_combat_frappe_de_plus_loin_et_tient_le_temps_d_une_roulade():
    c = mantes.COMBAT
    assert c["portee_px"] > 18 and c["cadence_images"] < 40, "pas plus durs que les autres"
    assert c["saisie_px"] <= techniques.par_slug("projection_hanche")["portee"] + 2
    # La prise tient assez pour qu'on la voie venir et qu'on roule (ESQUIVE) — quatre images, on ne voyait rien.
    assert c["saisie_images"] >= 18
    assert 0 < c["part_projection"] + c["part_pieds"] <= 100
    assert 0 < c["parade_chance"] < 1 and c["parade_repos_images"] >= 60
    assert 0 < c["au_sol_images"] <= 90


def test_leur_garde_robe_est_la_veste_de_kungfu_vert_mante():
    robe = garderobe.exporter()["garde_robes"]["mante"]
    assert robe["hauts"] == ["veste_kungfu"] and robe["haut_fixe"] == pietons.par_slug("mante")["couleurs"]["c"]
    assert "veste_kungfu" in garderobe.HAUTS
