"""Des missions sur place, avec une frontière — la forme des clés, et la ville.

Demande de Martin (29 sept. 2026) : des raccourcis vers l'heure et l'endroit, et une frontière qui
garde dans la mission. `sur_place` saute le trajet et l'attente ; `frontiere` fait rater la mission
qu'on quitte plus de dix secondes.
"""

import copy

from app import blocs, missions
from tests import villes


def _mission(**cles):
    m = copy.deepcopy(next(m for m in missions.CATALOGUE if m["slug"] == "q13"))
    m.pop("sur_place", None)
    m.pop("frontiere", None)
    m.update(cles)
    return m


def test_hors_zone_est_une_raison_d_echec():
    assert "hors_zone" in missions.ECHECS


def test_une_mission_sans_les_cles_n_a_rien_a_redire():
    assert missions.erreurs_de_sur_place(_mission()) == []


def test_les_formes_refusees():
    cas = {
        "district inconnu": _mission(frontiere="atlantide"),
        "bloc inconnu": _mission(frontiere="bloc:atlantide"),
        "heure mal formée": _mission(sur_place={"lieu": "hotel", "heure": "midi"}),
        "heure hors de [0, 1)": _mission(sur_place={"lieu": "hotel", "heure": (0.5, 1.2)}),
        "lieu inconnu": _mission(sur_place={"lieu": "atlantide", "heure": "nuit"}),
        "clé inconnue": _mission(sur_place={"lieu": "hotel", "heure": "nuit", "char": True}),
    }
    for attendu, m in cas.items():
        assert any(attendu in e for e in missions.erreurs_de_sur_place(m)), (attendu, missions.erreurs_de_sur_place(m))


def test_les_formes_acceptees():
    assert missions.erreurs_de_sur_place(_mission(sur_place={"lieu": "hotel", "heure": "nuit"}, frontiere="quais")) == []
    assert missions.erreurs_de_sur_place(_mission(sur_place={"lieu": "hotel", "heure": (0.9, 0.1)})) == []
    assert missions.erreurs_de_sur_place(_mission(frontiere="bloc:villa")) == []


def test_tout_le_catalogue_a_des_cles_bien_formees():
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_sur_place(m) == [], (m["slug"], missions.erreurs_de_sur_place(m))


def _district_du_lieu(ville, lieu):
    porte = next((p for p in ville["portes"] if p.get("lieu") == lieu), None)
    if porte is None:
        return None
    trouvee = None
    for z in ville["zones"]:
        if z["x"] <= porte["x"] < z["x"] + z["l"] and z["y"] <= porte["y"] + 1 < z["y"] + z["h"]:
            trouvee = z
    return trouvee and trouvee["district"]


def _lieux_nommes(m):
    """Les lieux que la mission nomme en clair (`lieu`, `ou` sans forme) — ceux qu'on sait situer —
    jusqu'au premier `retourner` : la frontière tombe là (le butin se rapporte ailleurs)."""
    noms = [m["sur_place"]["lieu"]] if m.get("sur_place") else []
    for o in m["objectifs"]:
        if o["type"] == "retourner":
            break
        for cle in ("lieu", "ou"):
            v = o.get(cle)
            if isinstance(v, str) and ":" not in v and v != "donneur":
                noms.append(v)
    return noms


def test_chaque_lieu_nomme_est_dans_la_frontiere():
    """⚠️ Un lieu hors de sa propre frontière rend la mission impossible : on y va, et elle rate."""
    ville = villes.exporter()
    par_bloc = blocs.lieux_des_blocs()
    for m in missions.CATALOGUE:
        f = m.get("frontiere")
        if not f:
            continue
        for lieu in _lieux_nommes(m):
            if f.startswith("bloc:"):
                assert par_bloc.get(lieu) == f[5:], (m["slug"], lieu)
            elif lieu not in par_bloc:
                assert _district_du_lieu(ville, lieu) == f, (m["slug"], lieu, _district_du_lieu(ville, lieu))


def test_les_cles_arrivent_avec_la_mission_pas_dans_le_paquet(client):
    """⚠️ Le paquet a un plafond (`test_le_paquet_reste_leger`) : six clés l'ont passé de 18 octets gzip
    (30 sept. 2026). Elles servent à JOUER la mission — elles arrivent avec son texte, par
    `/api/mission/<slug>`, comme ses objectifs (M16)."""
    paquet = {m["slug"]: m for m in client.get("/api/definitions").get_json()["missions"]}
    for m in missions.CATALOGUE:
        if not (m.get("sur_place") or m.get("frontiere")):
            continue
        assert "sur_place" not in paquet[m["slug"]] and "frontiere" not in paquet[m["slug"]], m["slug"]
        jouer = client.get(f"/api/mission/{m['slug']}").get_json()
        assert jouer.get("sur_place") == m.get("sur_place") and jouer.get("frontiere") == m.get("frontiere"), m["slug"]
