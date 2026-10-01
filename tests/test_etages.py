"""Des étages dedans aussi (docs/jalons/des-etages-dedans-aussi.md) : autant de niveaux derrière une porte que sa
façade en peint — le compte vit en Python (`app/etages.py`), le navigateur le peint."""
import json
import re

from app import carte, etages
from tests import villes


def test_hash2_est_celui_du_navigateur(banc):
    """⚠️ La deuxième multiplication de `hash2` est un FLOTTANT en JS : un entier Python exact s'en écarterait."""
    paires = [(0, 0), (3, 4), (120, 57), (411, 389), (-1, 7), (65535, 2)]
    attendu = banc("function (L) { return %s.map(function (p) { return L.hash2(p[0], p[1]); }); }"
                   % json.dumps([list(p) for p in paires]))
    assert [etages.hash2(x, y) for x, y in paires] == attendu


def test_chaque_facade_sait_combien_d_etages_elle_peint():
    v = villes.generer()
    for q in v["residences"] + v["devantures"]:
        assert type(q["au_dessus"]) is int and 0 <= q["au_dessus"] <= etages.ETAGES_MAX, q
    for r in v["residences"]:
        assert r["au_dessus"] <= r["etages"] - 1, r
    montes = sum(1 for d in v["devantures"] if d["au_dessus"])
    assert montes >= 120, f"{montes} devantures portent des étages (129 sur 135 le 30 sept.)"


GENEREE = re.compile(r"^(?:nord_)?[a-z_]+?_\d+$")


def _portes_generees(v):
    for p in v["portes"]:
        s = p.get("interieur")
        if s and GENEREE.match(s) and s in v["interieurs"]:
            q = etages.facade_de(v, p)
            if q is not None:
                yield p, q


def test_autant_de_niveaux_dedans_que_la_facade_en_peint():
    v = villes.generer()
    fautes, montes, commerces = [], 0, 0
    for p, q in _portes_generees(v):
        n = len(etages.suite(v["interieurs"], p["interieur"]))
        if n != 1 + q["au_dessus"]:
            fautes.append((p["interieur"], n, 1 + q["au_dessus"]))
        montes += n >= 3
        commerces += n >= 2 and q in v["devantures"]
    assert fautes == [], fautes[:10]
    assert montes >= 5 and commerces >= 10, (montes, commerces)


def test_chaque_etage_monte_et_redescend():
    v = villes.generer()
    for p, _ in _portes_generees(v):
        suite = etages.suite(v["interieurs"], p["interieur"])
        for k, slug in enumerate(suite):
            piece = v["interieurs"][slug]
            carte._verifier_piece(piece)
            esc = {(q["vers"], bool(q.get("descend"))) for q in piece["points"] if q["type"] == "escalier"}
            attendu = ({(suite[k - 1], True)} if k else set()) | ({(suite[k + 1], False)} if k + 1 < len(suite) else set())
            assert esc == attendu, (slug, esc, attendu)
            pts = piece["points"]
            for i, a in enumerate(pts):
                for b in pts[i + 1:]:
                    # Deux escaliers peuvent se toucher (on se tient DESSUS) ; un autre point, jamais.
                    assez = 1 if a["type"] == b["type"] == "escalier" else 2
                    assert max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"])) >= assez, (slug, a, b)


def test_la_bande_nord_monte_aussi():
    v = villes.generer()
    assert any(len(etages.suite(v["interieurs"], p["interieur"])) >= 2
               for p, _ in _portes_generees(v) if p["interieur"].startswith("nord_"))


def test_en_haut_d_un_commerce_le_logement_du_commercant():
    v = villes.generer()
    for p, q in _portes_generees(v):
        if q in v["devantures"]:
            for slug in etages.suite(v["interieurs"], p["interieur"])[1:]:
                assert v["interieurs"][slug]["nom"] == "Le logement du commerçant", slug


def test_les_etages_ne_deplacent_rien(monkeypatch):
    """⚠️ Pas `villes` : on compare une ville bâtie SANS le module (le monkeypatch ne se voit pas du cache)."""
    avec = carte.generer()
    monkeypatch.setattr(etages, "compter", lambda ville: None)
    monkeypatch.setattr(etages, "monter", lambda ville: None)
    sans = carte.generer()
    for cle in avec:
        if cle not in ("interieurs", "residences", "devantures"):
            assert avec[cle] == sans[cle], cle
    for cle in ("residences", "devantures"):
        assert [{k: x for k, x in q.items() if k != "au_dessus"} for q in avec[cle]] == sans[cle], cle
    posees = re.compile(r"^(?:nord_)?[a-z_]+?_\d+(?:_haut\d*)?$")   # une pièce posée, ou l'un de ses étages
    for slug, piece in sans["interieurs"].items():
        if not posees.match(slug):
            assert avec["interieurs"][slug] == piece, slug


def test_une_facade_qui_ne_peint_plus_d_etage_perd_ses_pieces_du_haut():
    """Le chemin du retrait (aucune porte de la ville d'aujourd'hui ne le prend) : le rez redevient une pièce seule, et
    la marche de son escalier redevient du plancher."""
    v = villes.generer()
    porte, facade = next((p, q) for p, q in _portes_generees(v)
                         if len(etages.suite(v["interieurs"], p["interieur"])) == 3)
    facade["au_dessus"] = 0
    etages.monter(v)
    rez = v["interieurs"][porte["interieur"]]
    assert etages.suite(v["interieurs"], porte["interieur"]) == [porte["interieur"]]
    assert not any(q["type"] == "escalier" for q in rez["points"]), rez["points"]
    assert "/" not in "".join(rez["sol"])
    carte._verifier_piece(rez)


def test_faute_de_plancher_un_petit_meuble_cede_sa_place():
    piece = carte._piece("essai_meuble", "Essai", """
BBBBBBB
BlllllB
BnllllB
B     B
BBBDBBB""", porte="maison")
    assert etages.ajouter_un_escalier(piece, "ailleurs")
    assert piece["sol"][2][1] == "/" and piece["points"][-1] == {"type": "escalier", "x": 1, "y": 2, "vers": "ailleurs"}


def test_faute_de_toute_place_le_point_fouiller_qui_gene_s_en_va():
    piece = carte._piece("essai_fouille", "Essai", """
BBBBBBB
BlllllB
B llllB
B     B
BBBDBBB""", porte="maison", points=({"type": "fouiller", "x": 1, "y": 1},))
    assert etages.ajouter_un_escalier(piece, "ailleurs")
    assert piece["sol"][2][1] == "/"
    assert [q["type"] for q in piece["points"]] == ["escalier"], piece["points"]
