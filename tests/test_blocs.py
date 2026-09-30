"""Les blocs de carte (vague 1) : un morceau de monde à part, servi à part, qui ne change
pas un octet de la ville. Voir `app/blocs/` et `docs/jalons/des-blocs-de-carte-en-extensions.md`."""

import json

import pytest

from app import blocs, definitions, hors_ligne


@pytest.mark.parametrize("bloc", blocs.BLOCS, ids=lambda b: b["slug"])
def test_chaque_bloc_tient_debout(bloc, paquet):
    """Son plan, ses glyphes, son retour qui se marche et qu'on rejoint à pied depuis
    l'arrivée — et son passage, dans la VILLE, sur une tuile qui se marche, au bout d'une rue qui rejoint
    celles de la ville (`blocs.sortie_sans_rue`)."""
    assert blocs.erreurs(bloc, paquet["carte"]) == []


def test_un_bloc_mal_fait_se_voit():
    """Le juge mord : un retour muré et un passage en pleine façade."""
    mauvais = dict(blocs.BLOCS[0], retour={"bord": "sud", "de": 0, "l": 3}, passage={"bord": "nord", "de": 0, "l": 1})
    ville = {"largeur": 3, "hauteur": 1, "sol": ["FFF"]}
    fautes = blocs.erreurs(mauvais, ville)
    assert any("retour ne se marche pas" in f for f in fautes), fautes
    assert any("passage en ville ne se marche pas" in f for f in fautes), fautes


def test_une_sortie_de_la_ville_sans_rue_se_voit():
    """Martin (30 sept. 2026) : « toutes les sorties de la ville [doivent avoir] une rue ou une voie qui permette
    de sortir ». Le juge mord : un trottoir au bord, une seule tuile de chaussée, une rue qui ne mène à rien, et
    une rue barrée entre la sortie et la ville (docs/jalons/chaque-sortie-de-la-ville-a-sa-rue.md)."""
    passage = {"bord": "ouest", "de": 0, "l": 4}
    trottoir = {"largeur": 6, "hauteur": 4, "sol": [".#####"] * 4}
    assert "n'a pas de rue" in " ".join(blocs.sortie_sans_rue("x", passage, trottoir))
    une_tuile = {"largeur": 6, "hauteur": 4, "sol": [".#####", "######", ".#####", ".#####"]}
    assert "n'a pas de rue" in " ".join(blocs.sortie_sans_rue("x", passage, une_tuile))
    isolee = {"largeur": 7, "hauteur": 4, "sol": ["##.####", "##.####", "..,####", "..,####"]}
    assert "ne rejoint pas" in " ".join(blocs.sortie_sans_rue("x", passage, isolee))
    barree = {"largeur": 6, "hauteur": 4, "sol": ["######"] * 4, "fermetures": [{"x": 1, "y": 0, "l": 1, "h": 4}]}
    assert "ne rejoint pas" in " ".join(blocs.sortie_sans_rue("x", passage, barree))
    assert blocs.sortie_sans_rue("x", passage, dict(barree, fermetures=[])) == []


def test_un_bloc_ne_change_pas_un_octet_de_la_ville(monkeypatch, paquets):
    """⚠️ LA PROMESSE DES BLOCS : la ville n'en sait rien. Bâtie sans aucun bloc, sa carte
    a exactement la même empreinte."""
    monkeypatch.setattr(blocs, "BLOCS", [])
    monkeypatch.setattr(blocs, "SOUS_SOLS", [])
    sans = definitions.construire()  # ⚠️ sous le patch : pas la fixture `paquets`
    assert sans.carte.etag == paquets.carte.etag
    assert sans.blocs == {}


def test_la_carte_d_un_bloc_se_sert_a_part_et_se_revalide(client):
    for bloc in blocs.BLOCS:
        r = client.get(f"/api/carte/bloc/{bloc['slug']}")
        assert r.status_code == 200 and r.headers["ETag"]
        corps = r.get_json()
        assert corps["bloc"]["slug"] == bloc["slug"] and corps["largeur"] == len(bloc["plan"][0])
        assert client.get(f"/api/carte/bloc/{bloc['slug']}",
                          headers={"If-None-Match": r.headers["ETag"]}).status_code == 304
    assert client.get("/api/carte/bloc/nulle-part").status_code == 404


def test_le_paquet_nomme_les_passages_et_pas_les_cartes(paquet):
    """Le paquet dit OÙ passer ; la carte du bloc voyage à part, à la demande. Seules ses
    PORTES voyagent avec lui (x, y, nom de la pièce) : la triche ENDROITS CLÉS les liste. Un
    bloc qui a des lieux de mission (la villa) n'en envoie que les NOMS, pas les pixels ; un bloc
    qui a une planque (le chalet) le dit d'un booléen : la triche TOUTES LES PROPRIÉTÉS la donne."""
    tous = blocs.BLOCS + blocs.SOUS_SOLS
    assert [b["slug"] for b in paquet["blocs"]] == [b["slug"] for b in tous]
    for b, source in zip(paquet["blocs"], tous):
        assert set(b) - {"lieux", "planque", "seuil"} == {"slug", "nom", "passage", "panneau", "portes"}
        assert (b["passage"] is None) is bool(source.get("seuil"))
        assert b.get("planque", False) is bool(source.get("planque"))
        assert all(isinstance(nom, str) for nom in b.get("lieux", []))
        for p in b["portes"]:
            assert set(p) == {"x", "y", "nom"}
    assert paquet["blocs_empreinte"]


def test_le_gabarit_des_blocs_est_dans_la_page_et_hors_de_la_coquille(client):
    page = client.get("/").get_data(as_text=True)
    assert 'data-url-bloc="/api/carte/bloc/SLUG?e=' in page
    assert not any("/api/carte/bloc/" in a for a in hors_ligne.coquille(page, "/"))


def test_la_carte_d_un_bloc_a_ce_que_monde_charger_lit():
    for bloc in blocs.BLOCS:
        c = blocs.carte_du_bloc(bloc)
        for cle in ("sol", "voie", "legende", "decor", "apparition", "portes", "lampes", "zones",
                    "points_interet", "intersections", "arrets", "interieurs", "ambulants", "bloc"):
            assert cle in c, f"{bloc['slug']} : « {cle} » manque"
        assert len(c["voie"]) == c["hauteur"] and len(c["voie"][0]) == c["largeur"]
        json.dumps(c)


def test_on_ressort_d_un_bloc_dans_le_sens_ou_l_on_est_venu():
    """⚠️ Martin, 26 sept. 2026 (les Galeries) : « on entre à l'ouest et on sort aussi à l'ouest ». On pousse
    contre le bord OUEST de la ville : on arrive donc par le côté EST du bloc, et on en ressort en poussant
    vers l'est. Le retour d'un bloc est sur le bord OPPOSÉ à son passage en ville."""
    oppose = {"nord": "sud", "sud": "nord", "ouest": "est", "est": "ouest"}
    for bloc in blocs.BLOCS:
        assert bloc["retour"]["bord"] == oppose[bloc["passage"]["bord"]], (
            f"{bloc['slug']} : passage au {bloc['passage']['bord']}, retour au {bloc['retour']['bord']}")


def test_chaque_mission_de_la_villa_a_sa_cle_avant_la_maison():
    """Martin (30 sept. 2026) : « assure-toi que les prérequis des missions soient bien respectés ». Une
    mission qui va DANS la maison de la villa (la porte de service, le bureau, la cave) a la clé avant :
    un de ses objectifs d'avant la met au sac, ou une mission de ses prérequis (de proche en proche)."""
    from app import missions
    from app.blocs import villa
    par_slug = {m["slug"]: m for m in missions.CATALOGUE}
    donnent = set(missions.cles_des_serrures(blocs.BLOCS)["cle_villa"])
    dedans = {"villa_service", "villa_bureau", "villa_terminal", "villa_voute"}
    assert dedans <= set(villa.LIEUX)

    def avant(slug, vus=None):
        vus = set() if vus is None else vus
        for p in par_slug[slug]["prerequis"]:
            if p not in vus:
                vus.add(p)
                avant(p, vus)
        return vus

    vues = []
    for m in missions.CATALOGUE:
        etapes = [i for i, o in enumerate(m["objectifs"]) if (o.get("lieu") or o.get("ou")) in dedans]
        if not etapes:
            continue
        vues.append(m["slug"])
        soi = any(o.get("objet") == "cle_villa" for o in m["objectifs"][:etapes[0]])
        assert soi or avant(m["slug"]) & donnent, f"{m['slug']} entre dans la villa sans que rien ne lui donne la clé"
    assert sorted(vues) == ["e07", "v02", "v03"], vues
