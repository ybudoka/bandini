"""La ville des juges (`tests/villes.py`) : la même que celle du jeu, et à chacun la sienne.

Un cache qui rendrait une autre ville, ou la même à deux juges, ferait mentir
tous ceux qui le lisent sans qu'aucun ne rougisse : il se juge lui-même.
"""

import villes

from app import carte


def test_la_ville_gardee_est_celle_que_le_jeu_genere():
    assert villes.generer() == carte.generer()


def test_chacun_recoit_sa_copie():
    """⚠️ Un juge qui pose un char dans sa ville ne le pose pas dans celle du suivant."""
    a = villes.generer()
    a["sol"][0] = "salie par un juge"
    a["portes"].clear()
    b = villes.generer()
    assert b["sol"][0] != "salie par un juge"
    assert b["portes"], "la ville du juge suivant a perdu ses portes"


def test_la_graine_et_la_bande_nord_font_des_villes_distinctes():
    """La clé du cache porte tout ce qui change la ville : sans la bande nord,
    ce n'est pas la même carte — et le cache ne doit pas rendre l'une pour l'autre."""
    avec, sans = villes.generer(), villes.generer(nord=False)
    assert avec["hauteur"] != sans["hauteur"]
    assert sans == carte.generer(nord=False)
