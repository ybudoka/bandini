"""Le crime d'autrui (M12), jugé en Python : la méprise est rare, bornée et bon marché.

« Un crime qu'on n'a pas commis peut te tomber dessus si tu es au mauvais endroit. C'est
risqué, donc c'est rare et lisible, et un juge vérifie qu'aucune étoile ne tombe sur un
joueur immobile à plus de N tuiles. »
"""

from __future__ import annotations

import re
from pathlib import Path

from app import recherche

RACINE = Path(__file__).resolve().parent.parent


def test_la_meprise_est_rare_et_se_tient_pres_de_la_scene():
    a = recherche.AUTRUI
    assert 0 < a["chance"] <= 0.5, "une méprise sur deux crimes n'est plus rare"
    assert a["rayon_px"] <= 5 * recherche.TUILE_PX, "on te confond de trop loin"
    assert a["temoin_px"] >= a["rayon_px"]
    assert a["repos_s"] >= 60, "deux méprises coup sur coup"
    assert a["cri"] and a["cri"] == a["cri"].upper()
    assert recherche.exporter()["autrui"] == a


def test_chaque_crime_d_autrui_a_son_temoin_et_ne_coute_qu_une_etoile():
    """⚠️ Les trois routines de la ville qui commettent un crime (le pickpocket, le voleur
    de char, la rixe) appellent la méprise avec un délit du catalogue — et chacun ne vaut
    qu'UNE étoile et exige un TÉMOIN : il faut qu'il coure le dire, et on peut lui
    acheter le silence. Une méprise bruyante (sans témoin) serait une étoile sans recours."""
    source = (RACINE / "static" / "js" / "entites.js").read_text(encoding="utf-8")
    types = re.findall(r"Police\.crimeDAutrui\('([a-z_]+)'", source)
    assert sorted(types) == ["coup_pieton", "pickpocket", "vol_vehicule"], types
    for t in types:
        delit = recherche.DELITS[t]
        assert delit["etoiles"] == 1 and delit["temoin"] is True, (t, delit)
