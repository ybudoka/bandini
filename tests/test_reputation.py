"""La réputation par quartier (`recherche.REPUTATION`, `docs/jalons/la-reputation-et-la-lecture-des-passants.md`,
vague 2) : une jauge par quartier, qui ne change QUE la délation."""

import pathlib
import re

from app import recherche
from tests import villes

RACINE = pathlib.Path(__file__).resolve().parent.parent
JS = RACINE / "static" / "js"


def test_la_regle_voyage_avec_la_police():
    r = recherche.exporter()["reputation"]
    assert r == recherche.REPUTATION
    assert r["min"] < r["mal_vu"] < 0 < r["bien_vu"] < r["max"]
    assert r["mission"] > r["job"] > 0 and r["par_etoile"] > 0 and r["retour_par_jour"] > 0


def test_chaque_quartier_est_un_district_de_la_ville():
    districts = {z.get("district") or z["slug"] for z in villes.exporter()["zones"]}
    q = recherche.REPUTATION["quartiers"]
    assert len(set(q)) == len(q) and set(q) <= districts, set(q) - districts


def test_elle_ne_change_que_la_delation():
    """Une seule décision la lit : `Reputation.denonce`, là où un passant devient témoin. Le reste ne fait que
    l'ÉCRIRE (un crime vu, une mission, une job, le matin) ou la MONTRER (le carnet, la carte)."""
    lecteurs, decideurs = {}, {}
    for f in JS.glob("*.js"):
        if f.name == "reputation.js":
            continue
        texte = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\bReputation\.(\w+)", texte):
            lecteurs.setdefault(m.group(1), set()).add(f.name)
        if "Reputation.denonce" in texte:
            decideurs[f.name] = texte.count("Reputation.denonce")
    permis = {"quartierA", "quartierDeLaVille", "denonce", "crime", "mission", "job", "reussite", "nouveauJour", "oublier",
              "de", "etat", "quartiers", "dessinerJauge", "dessinerSurLaCarte"}
    assert set(lecteurs) <= permis, set(lecteurs) - permis
    assert set(decideurs) <= {"police.js", "entites.js"}, decideurs
    # Lire sa valeur, c'est la montrer : le carnet et la carte, rien d'autre.
    for nom in ("de", "etat"):
        assert lecteurs.get(nom, set()) <= {"hud.js"}, (nom, lecteurs.get(nom))
