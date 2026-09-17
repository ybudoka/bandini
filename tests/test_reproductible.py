"""La ville doit être la MÊME à chaque lancement — et elle ne l'était pas.

⚠️ **Ce juge est né d'une CI à pile ou face.** Trois juges du banc tombaient une
fois sur deux sans qu'aucune ligne n'ait bougé, et chaque session les mettait
sur le dos des autres. La cause était une seule ligne de `carte.py` :

    self.sol[y][x] = max(set(nus), key=nus.count)

`nus` est une liste de **glyphes**. Sur une égalité — deux voisines de glyphes
différents, une chacune — `max` rend la première que l'ensemble lui donne, et un
ensemble de CHAÎNES s'itère dans l'ordre de leurs empreintes, **que Python
randomise à chaque processus** (`PYTHONHASHSEED`). Une poignée de tuiles
changeaient donc d'un lancement à l'autre, et avec elles le décor, les kiosques,
les feux piétons et les paquets cachés.

⚠️ Une ville qui n'est pas reproductible, ce n'est pas seulement des juges
fragiles : c'est une **sauvegarde qui ne retrouve pas son monde**. La position du
joueur, son char garé devant la planque, les paquets déjà ramassés — tout ça est
rangé en coordonnées, et tout ça pointe à côté si la ville a bougé d'une tuile.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]

#: ⚠️ Deux graines d'empreinte VOLONTAIREMENT différentes. Avec la même, le juge
#: ne prouverait rien — c'est précisément la randomisation que l'on traque, et
#: elle ne se voit qu'entre deux processus qui ne hachent pas pareil.
GRAINES = ("0", "12345")


def _empreinte(graine: str, quoi: str) -> str:
    code = (
        "import json, hashlib;"
        "from app import carte;"
        f"d = carte.exporter()[{quoi!r}];"
        "print(hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False)"
        ".encode()).hexdigest())"
    )
    sortie = subprocess.run(
        [sys.executable, "-c", code], cwd=RACINE, capture_output=True, text=True,
        env={"PYTHONHASHSEED": graine, "PATH": "/usr/bin:/bin"},
    )
    assert sortie.returncode == 0, sortie.stderr[-800:]
    return sortie.stdout.strip()


@pytest.mark.parametrize("quoi", ["sol", "decor", "portes", "paquets", "ambulants", "autobus"])
def test_la_ville_est_la_meme_a_chaque_lancement(quoi):
    """⚠️ On lance DEUX PROCESSUS avec deux graines d'empreinte différentes. Dans
    un seul processus, `PYTHONHASHSEED` ne bouge pas : le défaut y est invisible,
    et c'est pour ça qu'il a vécu si longtemps."""
    empreintes = {_empreinte(g, quoi) for g in GRAINES}
    assert len(empreintes) == 1, (
        f"« {quoi} » change d'un lancement à l'autre : la ville n'est pas "
        f"reproductible, et une sauvegarde ne retrouvera pas son monde"
    )


def test_deux_appels_dans_le_meme_processus_donnent_la_meme_ville():
    """Le témoin du juge d'à côté : dans un seul processus, la ville a toujours
    été stable. ⚠️ Sans cette mesure, un générateur cassé au point de ne rien
    rendre du tout passerait le juge précédent au vert."""
    from app import carte
    a = json.dumps(carte.exporter()["sol"])
    b = json.dumps(carte.exporter()["sol"])
    assert a == b
    assert len(hashlib.sha256(a.encode()).hexdigest()) == 64
    assert a.count("x") > 100, "le décor du juge est faux : plus une seule ruelle"
