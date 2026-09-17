"""M12, 7e vague — la bagarre de gangs à leur frontière.

⚠️ **Le joueur n'est ni la cause ni la cible.** C'est la promesse que tiennent
ces juges-ci et ceux du banc : une rixe entre deux gangs se passe *sans* lui —
elle ne lui met pas d'étoile, elle ne compte pas dans ses morts, et personne ne
se retourne contre lui parce qu'elle a lieu.
"""

import math
import re
from pathlib import Path

import pytest

from app import carte, definitions, economie, pietons


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


@pytest.fixture(scope="module")
def lignes(ville):
    return pietons.frontieres(ville)


def test_la_fiche_de_la_bagarre_se_tient():
    """Des chiffres qui se contredisent font une rixe qu'on ne voit jamais."""
    f = pietons.BAGARRE
    assert 0 < f["chance_par_minute"] <= 1
    assert f["membres"] >= 2, "une bagarre à un contre un n'est pas une bagarre"
    # ⚠️ On doit la VOIR : assez loin pour que personne n'apparaisse sous les
    # yeux du joueur, assez près pour qu'il la voie se battre. Un rayon plus
    # petit que la garde serait une fenêtre vide, et la rixe n'aurait jamais lieu.
    assert 0 < f["trop_pres_px"] < f["rayon_px"]
    assert f["portee_px"] < f["rival_px"], "on cherche plus loin qu'on ne frappe"
    assert f["duree_images"] > f["cadence_images"], "elle finit avant le premier coup"
    assert f["recul_tuiles"] >= 2, "la frontière passe au milieu d'une rue : il faut en sortir"
    assert f["frontiere_min_tuiles"] > 0


def test_le_paquet_porte_la_bagarre_et_ses_frontieres():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce
    défaut huit fois. Les frontières sont le cas limite : elles ne sont *dans*
    aucune des deux fiches, c'est `definitions.assembler` qui les marie. Si
    personne ne les met dans le paquet, elles n'existent que pour Python."""
    paquet = definitions.assembler()
    assert paquet["pietons"]["bagarre"] == pietons.BAGARRE
    portees = paquet["pietons"]["frontieres"]
    assert portees, "le navigateur ne reçoit aucune frontière"
    assert portees == pietons.frontieres(paquet["carte"])


def test_il_y_a_de_vraies_frontieres_et_elles_joignent_deux_gangs(lignes):
    """⚠️ Une frontière est une LIGNE, pas un coin. Deux districts qui ne se
    touchent que par quelques tuiles n'ont pas de rue mitoyenne : on n'y ferait
    naître personne, et la rixe n'aurait jamais lieu nulle part."""
    assert len(lignes) >= 3, "la ville n'a presque aucune frontière de gang"
    slugs = {g["slug"] for g in pietons.GANGS}
    vues = set()
    for f in lignes:
        assert f["a"] in slugs and f["b"] in slugs, f
        assert f["a"] != f["b"], "une gang n'a pas de frontière avec elle-même"
        assert f["axe"] in ("v", "h")
        assert f["long"] >= pietons.BAGARRE["frontiere_min_tuiles"], f
        paire = frozenset((f["a"], f["b"]))
        assert paire not in vues, f"deux frontières pour {sorted(paire)}"
        vues.add(paire)


def test_une_frontiere_est_vraiment_la_ou_les_deux_districts_se_touchent(lignes, ville):
    """Le juge qui compte : la ligne rendue doit être exactement le bord que les
    deux rectangles partagent, et chaque camp doit être de SON côté.

    ⚠️ `a` est toujours la gang du petit côté (ouest ou nord). Sans cette
    convention, le navigateur ferait naître les deux camps du même bord de la
    rue — ils se seraient tapés dessus sans jamais traverser."""
    rects = {z["slug"]: z for z in ville["zones"] if not z.get("gang")}
    quartier = {g["slug"]: g["district"] for g in pietons.GANGS}
    for f in lignes:
        ra, rb = rects[quartier[f["a"]]], rects[quartier[f["b"]]]
        if f["axe"] == "v":
            assert ra["x"] + ra["l"] == f["x"] == rb["x"], f
            assert f["y"] >= max(ra["y"], rb["y"])
            assert f["y"] + f["long"] <= min(ra["y"] + ra["h"], rb["y"] + rb["h"])
        else:
            assert ra["y"] + ra["h"] == f["y"] == rb["y"], f
            assert f["x"] >= max(ra["x"], rb["x"])
            assert f["x"] + f["long"] <= min(ra["x"] + ra["l"], rb["x"] + rb["l"])


def test_une_frontiere_tient_dans_la_carte(lignes, ville):
    """Une ligne qui déborde de la ville ferait naître des hommes dans le vide."""
    for f in lignes:
        long_x = f["long"] if f["axe"] == "h" else 1
        long_y = f["long"] if f["axe"] == "v" else 1
        assert 0 <= f["x"] and f["x"] + long_x <= ville["largeur"], f
        assert 0 <= f["y"] and f["y"] + long_y <= ville["hauteur"], f


def test_les_frontieres_ne_dependent_pas_de_l_ordre_d_un_ensemble(ville):
    """⚠️ La leçon de PYTHONHASHSEED : un `set` de chaînes parcouru dans l'ordre
    rendait la ville différente d'un processus à l'autre, et un juge tombait à
    pile ou face. On les recalcule : c'est la même liste, dans le même ordre."""
    assert pietons.frontieres(ville) == pietons.frontieres(ville)
    # Et elle ne tient que des fiches : la même carte rend la même chose.
    assert pietons.frontieres(carte.exporter()) == pietons.frontieres(ville)


def test_une_rixe_se_fait_attendre():
    """⚠️ Retour de Martin (16 sept. 2026) : « je veux moins de bagarre de gang ».

    **« Par minute de jeu » trompe** : une journée dure `JOUR_SECONDES`, donc
    une minute de jeu dure un tiers de seconde, et `majBagarre` tire à chacun
    de ses passages. À 0,12, quatre secondes en vue d'une frontière suffisaient
    pour qu'une rixe parte. On calcule donc l'attente sur la VRAIE cadence —
    celle qu'écrit le navigateur, pas un chiffre recopié ici."""
    js = (Path(__file__).resolve().parent.parent / "static" / "js" / "entites.js").read_text(encoding="utf-8")
    passage = re.findall(r"B\.t % (\d+) === 0\) majBagarre\(\)", js)
    assert len(passage) == 1, "la cadence de `majBagarre` a changé de forme : le juge ne la lit plus"
    images_par_passage = int(passage[0])
    images_par_minute = economie.JOUR_SECONDES * 60 / (24 * 60)
    # Un passage ne tire que si la minute a changé depuis le précédent.
    images_par_tirage = images_par_passage * math.ceil(images_par_minute / images_par_passage)
    attente_s = images_par_tirage / 60 / pietons.BAGARRE["chance_par_minute"]
    assert attente_s >= 45, (
        "une rixe part après %.0f s en vue d'une frontière, en moyenne : on en croise une à chaque coin"
        % attente_s)
