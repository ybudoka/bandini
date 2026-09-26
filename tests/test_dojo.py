"""Le dojo du quartier (docs/jalons/le-dojo-du-quartier.md)."""

import json

from app import carte, devantures


def test_un_seul_dojo_et_il_est_au_faubourg():
    ville = carte.generer()
    portes = [p for p in ville["portes"] if p.get("interieur") == "dojo"]
    assert len(portes) == 1, portes
    p = portes[0]
    assert p["nom"] == "DOJO DION"
    assert carte._Chantier(carte.PLAN, carte.GRAINE).district_en(p["x"], p["y"]) == "faubourg"
    piece = ville["interieurs"]["dojo"]
    assert [pt["type"] for pt in piece["points"]] == ["cours"]
    assert [g["qui"] for g in piece["gens"]] == ["eleve"]
    sol = "".join(piece["sol"])
    assert "A" in sol and "@" in sol and "%" in sol


def test_le_dojo_ne_deplace_rien(monkeypatch):
    """La ville d'avant, identique : seules la porte, la devanture, la pièce et le point
    du dojo changent — et la pièce de commerce qu'il a reprise disparaît.
    ⚠️ Les ENSEIGNES qui ouvrent pour vrai (`enseignes.poser`) sont posées juste après, sur la même
    règle : sans le dojo, le Rialto prenait sa porte. Neutralisées des DEUX côtés."""
    from app import enseignes
    monkeypatch.setattr(enseignes, "poser", lambda chantier, ville: [])
    avec = carte.generer()
    monkeypatch.setattr(carte._Chantier, "poser_le_dojo", lambda self, ville: None)
    sans = carte.generer()
    for cle in avec:
        if cle in ("portes", "devantures", "interieurs", "points_interet"):
            continue
        assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    portes = [(a, b) for a, b in zip(avec["portes"], sans["portes"]) if a != b]
    assert len(portes) == 1 and portes[0][0]["interieur"] == "dojo", portes
    enseignes = [(a, b) for a, b in zip(avec["devantures"], sans["devantures"]) if a != b]
    assert len(enseignes) == 1 and enseignes[0][0]["texte"] == "DOJO DION", enseignes
    assert set(avec["interieurs"]) - set(sans["interieurs"]) == {"dojo"}
    reprise = set(sans["interieurs"]) - set(avec["interieurs"])
    assert reprise == {portes[0][1]["interieur"]}, reprise
    assert len(avec["points_interet"]) == len(sans["points_interet"]) + 1


def test_sans_facade_qui_convient_pas_de_dojo_et_rien_ne_plante(monkeypatch):
    """À surveiller no 1 : une ville où aucune pièce du Faubourg n'est assez grande."""
    monkeypatch.setattr(carte._Chantier, "DOJO_MESURES_MIN", (99, 99))
    ville = carte.generer()
    assert "dojo" not in ville["interieurs"]
    assert not [p for p in ville["portes"] if p.get("interieur") == "dojo"]


def test_plus_de_salon_mireille():
    assert all(nom != "SALON MIREILLE" for noms in devantures.COMMERCES.values() for nom, _ in noms)


# --- Mireille Dion, et les règles de la leçon (tâche 2) ----------------------------------

from app import audio, dojo, missions, techniques  # noqa: E402


def test_mireille_tient_le_comptoir_du_dojo():
    m = missions.personnage("mireille")
    assert m and m["ou"] == "point:cours" and m["nom"] == "Mireille Dion"


def test_chaque_cours_a_sa_lecon_et_son_annonce():
    cles = {r["cle"] for r in dojo.REPLIQUES}
    for t in techniques.CATALOGUE:
        if t["gratuite"]:
            continue
        assert dojo.lecon(t["slug"]) in dojo.DISTANCES, t["slug"]
        assert f"annonce_{t['slug']}" in cles, t["slug"]
    assert set(dojo.LECONS) <= {t["slug"] for t in techniques.CATALOGUE}


def test_mireille_ne_dit_pas_son_repos():
    """ACTION ouvre ses cours, toujours : un repos qu'on n'entend jamais ne se paie pas."""
    assert not [r for r in missions.repliques_de_repos() if r["qui"] == "mireille"]


def test_les_voix_du_dojo_sont_declarees():
    slugs = {v["slug"] for v in audio.toutes_les_voix()}
    assert {f"mireille-dojo-{r['cle']}" for r in dojo.REPLIQUES} <= slugs


def test_elle_se_nomme_une_fois():
    """« Qui parle se nomme » : dans sa salutation, et nulle part ailleurs."""
    nomment = [r["cle"] for r in dojo.REPLIQUES if "Mireille" in r["texte"]]
    assert nomment == ["salut"], nomment
