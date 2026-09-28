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


#: Ce qu'on compare d'un lancement à l'autre : ce que la sauvegarde retrouve en coordonnées.
CLES = ("sol", "decor", "portes", "paquets", "ambulants", "autobus", "metro")


def _empreintes(graine: str) -> dict:
    """UN processus par graine d'empreinte, qui hache les sept clés d'un coup (vague C, 28 sept.
    2026 : sept processus par graine refaisaient chacun toute la ville pour une seule clé). Et le
    témoin du sol : ses ruelles, comptées dans CE processus-là."""
    code = (
        "import json, hashlib;"
        "from app import carte;"
        "v = carte.exporter();"
        "e = {k: hashlib.sha256(json.dumps(v[k], sort_keys=True, ensure_ascii=False).encode()).hexdigest()"
        f" for k in {CLES!r}}};"
        "e['ruelles'] = json.dumps(v['sol']).count('x');"
        "print(json.dumps(e))"
    )
    sortie = subprocess.run(
        [sys.executable, "-c", code], cwd=RACINE, capture_output=True, text=True,
        env={"PYTHONHASHSEED": graine, "PATH": "/usr/bin:/bin"},
    )
    assert sortie.returncode == 0, sortie.stderr[-800:]
    return json.loads(sortie.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def empreintes() -> dict:
    return {g: _empreintes(g) for g in GRAINES}


@pytest.mark.parametrize("quoi", CLES)
def test_la_ville_est_la_meme_a_chaque_lancement(empreintes, quoi):
    """⚠️ On lance DEUX PROCESSUS avec deux graines d'empreinte différentes. Dans
    un seul processus, `PYTHONHASHSEED` ne bouge pas : le défaut y est invisible,
    et c'est pour ça qu'il a vécu si longtemps.

    ⚠️ Le témoin (il vivait dans `test_deux_appels_dans_le_meme_processus…`, parti le 28 sept.
    2026 — « la même ville dans un seul processus » est `test_carte::test_deterministe`) : un
    générateur cassé au point de ne rien rendre du tout passerait ce juge au vert."""
    for g in GRAINES:
        assert empreintes[g]["ruelles"] > 100, "le décor du juge est faux : plus une seule ruelle"
    assert len({empreintes[g][quoi] for g in GRAINES}) == 1, (
        f"« {quoi} » change d'un lancement à l'autre : la ville n'est pas "
        f"reproductible, et une sauvegarde ne retrouvera pas son monde"
    )
