"""Les visages des dialogues : chaque personnage a le sien, et sa mine suit son jeu.

Demande de Martin (22 sept. 2026) : « je veux des visages dessinés pour chaque dialogue ».
Python décide (`app/visages.py`), `static/js/visages.js` dessine ; ces juges tiennent les
deux ensemble.
"""

import json
import re
from pathlib import Path

from app import interpretation, missions, visages

RACINE = Path(__file__).resolve().parent.parent
JS = (RACINE / "static" / "js" / "visages.js").read_text(encoding="utf-8")


def test_chaque_personnage_qui_parle_a_un_visage():
    slugs = {p["slug"] for p in missions.PERSONNAGES}
    assert slugs <= set(visages.VISAGES), f"sans visage : {sorted(slugs - set(visages.VISAGES))}"
    assert set(visages.VISAGES) <= slugs, "un visage pour personne : un slug mal écrit"
    # Tous ceux qui ont une réplique, ouverture comprise.
    qui = {r["qui"] for r in missions.repliques()}
    assert qui <= set(visages.pour_le_navigateur())


def test_les_traits_sont_pris_dans_les_listes_fermees():
    for slug, v in visages.pour_le_navigateur().items():
        v = visages.complet(v)
        assert v["tete"] in visages.TETES, slug
        assert v["coiffure"] in visages.COIFFURES, slug
        assert v["habit"] in visages.HABITS, slug
        assert v["pilosite"] in visages.PILOSITES, slug
        assert v["lunettes"] in visages.LUNETTES, slug
        assert v["chapeau"] in visages.CHAPEAUX, slug
        assert set(v["signes"]) <= set(visages.SIGNES), (slug, v["signes"])
        assert set(v["extra"]) <= {"b", "t", "l", "y"}, slug
        for c in list(v["couleurs"].values()) + list(v["extra"].values()):
            assert re.fullmatch(r"#[0-9a-f]{6}", c), (slug, c)


def test_les_couleurs_sont_celles_de_la_rue():
    """Le portrait et le bonhomme de seize pixels sont la même personne."""
    nav = visages.pour_le_navigateur()
    for p in missions.PERSONNAGES:
        assert nav[p["slug"]]["couleurs"] == p["couleurs"], p["slug"]


def test_deux_personnages_n_ont_pas_la_meme_tete():
    vus = {}
    for slug, v in visages.pour_le_navigateur().items():
        cle = json.dumps(v, sort_keys=True)
        assert cle not in vus, f"{slug} et {vus.get(cle)} ont le même visage"
        vus[cle] = slug


def test_le_dessin_connait_chaque_liste_de_python():
    """Une forme que Python nomme et que le JS ne dessine pas serait un visage à moitié peint."""
    for tete in visages.TETES:
        assert re.search(rf"^\s+{tete}:\s+\[", JS, re.M), f"TETES.{tete} manque dans visages.js"
    humeurs_js = re.search(r"const HUMEURS = \[([^\]]+)\]", JS).group(1)
    assert re.findall(r"'(\w+)'", humeurs_js) == list(visages.HUMEURS)
    for mot in (visages.COIFFURES + visages.HABITS + visages.PILOSITES + visages.LUNETTES
                + visages.CHAPEAUX + visages.SIGNES):
        if mot in ("aucune", "aucunes", "aucun"):
            continue
        assert re.search(rf"['.]{mot}\b", JS), f"« {mot} » : visages.js ne le dessine nulle part"


def test_chaque_balise_du_jeu_d_acteur_a_une_humeur():
    """Une balise neuve dans une mission se range d'abord dans `visages.BALISES`."""
    inconnues = {}
    for r in missions.repliques():
        for b in visages.balises(r["jeu"]):
            if not visages.connue(b):
                inconnues.setdefault(b, r["slug"])
    assert not inconnues, f"balises sans humeur : {inconnues}"
    # Et d'avance : toute balise que la liste fermée du jeu d'acteur permet.
    assert not [b for b in interpretation.BALISES if not visages.connue(b)]
    assert set(visages.BALISES) <= set(visages.HUMEURS)


def test_l_humeur_est_celle_de_la_premiere_balise_qui_dit_une_mine():
    assert visages.humeur("[warmly] Salut.") == "content"
    assert visages.humeur("[pause] [angry] Sors d'icitte.") == "fache"
    assert visages.humeur("[quietly] [worried] T'es sûr?") == "inquiet"
    assert visages.humeur("[norwegian accent] [coldly] Non.") == "froid"
    assert visages.humeur("Pas de balise.") == "neutre"
    assert visages.humeur(None) == "neutre"


def test_le_navigateur_recoit_l_humeur_et_jamais_le_jeu():
    """⚠️ Les répliques ne sont plus dans le paquet (24 sept. 2026) : elles voyagent avec
    leur mission (`/api/mission/<slug>`), et c'est là qu'il faut les lire — sinon ce juge
    ne regarderait plus une seule réplique."""
    humeurs = set()
    for fiche in missions.CATALOGUE:
        for lignes in missions.pour_jouer(fiche["slug"])["dialogue"].values():
            for ligne in lignes:
                assert "jeu" not in ligne
                if "humeur" in ligne:
                    assert ligne["humeur"] in visages.HUMEURS and ligne["humeur"] != "neutre"
                    humeurs.add(ligne["humeur"])
    # Le jeu d'acteur des missions a de quoi faire bouger les visages : pas qu'une mine.
    assert {"content", "fache", "inquiet", "triste", "malin"} <= humeurs


def test_le_paquet_porte_les_visages(paquet):
    assert set(paquet["visages"]) == set(visages.pour_le_navigateur())
