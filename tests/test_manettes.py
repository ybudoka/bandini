"""Les dispositions de manette : ce qu'on propose au joueur doit tenir debout.

⚠️ Ces juges ne peuvent pas verifier qu'une disposition correspond a la manette
de quelqu'un — ca, seul le DESSIN de l'ecran MANETTE le dit, en allumant le
bouton qu'on appuie. Ils verifient qu'aucune disposition n'est incoherente :
pas d'action orpheline, pas un bouton pour deux choses, pas un chapeau tordu.
"""

import re
from pathlib import Path

import pytest

from app import manettes

RACINE = Path(__file__).resolve().parent.parent

#: Un bouton fait UNE chose — sauf celui de droite, qui sert aussi de RETOUR.
PAIRE_TOLEREE = {"esquive", "annuler"}


def test_le_javascript_connait_les_memes_actions():
    """⚠️ `entree.js` a ses propres defauts : si les deux listes derivent, une
    action du catalogue ne serait jamais lue, sans que rien ne rougisse."""
    source = (RACINE / "static" / "js" / "entree.js").read_text(encoding="utf-8")
    bloc = re.search(r"const MANETTE_DEFAUT = \{(.*?)\n  \};", source, re.S)
    assert bloc, "MANETTE_DEFAUT introuvable dans entree.js"
    actions_js = set(re.findall(r"(\w+): \[", bloc.group(1)))
    for profil in manettes.PROFILS:
        assert set(profil["boutons"]) == actions_js, profil["slug"]


@pytest.mark.parametrize("profil", manettes.PROFILS, ids=lambda p: p["slug"])
def test_une_disposition_est_coherente(profil):
    assert profil["nom"] and profil["detail"]
    assert profil["nom"] == profil["nom"].upper(), "le HUD ecrit en majuscules"
    # Un bouton pour une action, sauf la paire toleree.
    proprietaires: dict[int, set[str]] = {}
    for action, indices in profil["boutons"].items():
        for i in indices:
            proprietaires.setdefault(i, set()).add(action)
    for i, actions in proprietaires.items():
        assert len(actions) == 1 or actions == PAIRE_TOLEREE, f"bouton {i} : {actions}"
    # De quoi jouer : agir, frapper, mettre en pause, et une direction.
    for indispensable in ("action", "attaque", "pause", "carte"):
        assert profil["boutons"][indispensable], f"{profil['slug']} : pas de {indispensable}"
    assert profil["gaz"] != profil["frein"], "le gaz et le frein sur la meme chose"
    assert len(profil["axes"]) == 2 and profil["axes"][0] != profil["axes"][1]


@pytest.mark.parametrize("profil", manettes.PROFILS, ids=lambda p: p["slug"])
def test_la_croix_est_completement_dite(profil):
    """Quatre boutons, ou un chapeau — jamais un melange, jamais rien."""
    cotes = ["haut", "bas", "gauche", "droite"]
    boutons = [profil["boutons"][c] for c in cotes]
    if profil["croix"] is None:
        assert all(len(b) == 1 for b in boutons), f"{profil['slug']} : croix incomplete"
        assert len({b[0] for b in boutons}) == 4
    else:
        assert all(b == [] for b in boutons), "une croix-chapeau n'a pas de boutons"
        assert profil["croix"]["i"] >= 0
        assert set(profil["croix"]["valeurs"]) == {"haut", "droite"}, \
            "HAUT et DROITE suffisent : le navigateur deduit le tour"


def test_le_tour_du_chapeau_donne_huit_positions_distinctes():
    """⚠️ Le tour se deduit de HAUT et DROITE : si le pas est faux, deux
    directions tombent au meme endroit et la croix ment."""
    for profil in manettes.PROFILS:
        if not profil["croix"]:
            continue
        haut = profil["croix"]["valeurs"]["haut"]
        droite = profil["croix"]["valeurs"]["droite"]
        pas = (droite - haut) / 2
        positions = [haut + k * pas for k in range(8)]
        assert len({round(v, 4) for v in positions}) == 8, profil["slug"]
        assert min(positions) >= -1.001 and max(positions) <= 1.001, \
            "les huit positions tiennent dans l'axe ; le repos, lui, tombe dehors"


def test_deux_dispositions_ne_sont_jamais_les_memes():
    """Une ligne de plus dans la liste doit valoir une ligne de plus."""
    vues = {}
    for profil in manettes.PROFILS:
        signature = (tuple(sorted((a, tuple(b)) for a, b in profil["boutons"].items())),
                     profil["gaz"]["i"], profil["frein"]["i"], bool(profil["croix"]))
        assert signature not in vues, f"{profil['slug']} = {vues.get(signature)}"
        vues[signature] = profil["slug"]


def test_la_disposition_directinput_dit_ce_que_martin_a_mesure():
    """⚠️ Mesure en jeu, 13 sept. 2026 : sur sa 8BitDo en Bluetooth, les
    GACHETTES ouvraient la carte et la pause. Or carte et pause sont 8 et 9 sur
    une manette reconnue : ses gachettes sont donc 8 et 9, et toute la
    numerotation DirectInput suit (epaules 6-7, SELECT/START 10-11). Ce test
    garde le fait ; si quelqu'un « corrige » ces numeros, c'est ce retour-la
    qu'il efface."""
    profil = manettes.par_slug("bt_dinput")
    assert profil["frein"] == {"type": "bouton", "i": 8}
    assert profil["gaz"] == {"type": "bouton", "i": 9}
    assert profil["boutons"]["carte"] == [10] and profil["boutons"]["pause"] == [11]
    assert profil["boutons"]["attaque"][1] == 7 and profil["boutons"]["arme"][1] == 6
    assert profil["croix"], "et sa croix est un axe"


def test_le_defaut_existe_et_c_est_la_manette_reconnue():
    assert manettes.par_slug(manettes.DEFAUT)
    assert manettes.DEFAUT == "standard"
    assert manettes.par_slug("inconnue") is None


def test_le_paquet_sert_les_dispositions(paquet):
    bloc = paquet["manettes"]
    assert [p["slug"] for p in bloc["profils"]] == [p["slug"] for p in manettes.PROFILS]
    assert bloc["defaut"] in {p["slug"] for p in bloc["profils"]}
