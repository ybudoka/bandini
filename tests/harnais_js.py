"""Faire tourner du JavaScript du jeu sous Node — le seul endroit qui lance `node`.

Son seul appelant est la fixture `banc` de `conftest.py` : elle colle le faux
navigateur (`tests/banc.js`, qui charge `static/js/` dans l'ordre de
`templates/index.html`) au corps d'un juge `_js`, et passe en `entree` le
paquet de definitions, les missions et les blocs de carte. C'est ce qui juge le
moteur sans monter un Chromium.

⚠️ **LE HARNAIS PASSE PAR UN FICHIER, JAMAIS PAR `node -e`**, et c'est toute la
raison d'etre de ce module. Linux borne chaque argument d'`execve` a 128 Ko
(`MAX_ARG_STRLEN`, 32 pages) — macOS, lui, ne borne que le TOTAL. Un script
qui depasse cette taille (le paquet a lui seul la depasse de loin) fait echouer
les juges **sur Linux seulement**, avec un `OSError: [Errno 7] Argument list
too long` qui ne nomme ni le fichier ni la cause. Sur le Mac du developpeur,
tout reste vert.

⚠️ C'est le pire genre de panne : elle n'apparait pas la ou l'on travaille,
elle grandit toute seule avec le jeu, et elle ne se declenche pas a l'ajout
fautif mais quelques ajouts plus tard. Un fichier n'a aucune de ces limites,
et il n'en aura jamais.

⚠️ **L'entree se pose DANS le script, pas en argument** (`entree=`). Deux
raisons, et la seconde compte plus que la premiere : un argument retomberait
sous la meme borne, et surtout `process.argv[1]` ne veut pas dire la meme chose
selon qu'on lance `node -e ... payload` (c'est le payload) ou `node script.js
payload` (c'est le chemin du script). Une convention de position qu'il faut se
rappeler est une convention qu'on oublie — le harnais recoit donc une variable
`ENTREE`, deja decodee, et il n'y a plus rien a se rappeler.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest


def lancer_node(harnais: str, entree: Any = None) -> str:
    """Execute `harnais` sous Node et rend sa sortie standard.

    `entree` — n'importe quelle valeur JSON, posee dans le script sous le nom
    `ENTREE`. Le harnais la lit directement, sans `JSON.parse` ni `process.argv`.

    ⚠️ Se saute si Node manque, comme partout ailleurs : la machine d'un
    contributeur n'a pas forcement Node, et la CI, elle, l'a toujours.
    """
    node = shutil.which("node")
    if node is None:  # pragma: no cover - depend de la machine
        pytest.skip("node absent : impossible de faire tourner le module")

    if entree is not None:
        harnais = "const ENTREE = " + json.dumps(entree) + ";\n" + harnais

    with tempfile.TemporaryDirectory() as dossier:
        script = Path(dossier) / "harnais.js"
        script.write_text(harnais, encoding="utf-8")
        resultat = subprocess.run([node, str(script)], capture_output=True, text=True)
    if resultat.returncode != 0:
        # ⚠️ Sans ce message, une exception dans le JS remonte en
        # `CalledProcessError: returned non-zero exit status 1` et la pile
        # JavaScript — la seule chose utile — reste dans un tuyau ferme. On a
        # debogue une fois a l'aveugle ; une fois suffit.
        pytest.fail(
            "le harnais Node a echoue :\n"
            + (resultat.stderr or "(rien sur stderr)").strip()[-3000:]
            + (f"\n--- stdout ---\n{resultat.stdout.strip()[-1000:]}" if resultat.stdout.strip() else ""),
            pytrace=False,
        )
    return resultat.stdout
