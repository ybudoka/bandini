"""Le serveur de dev ne redemarre que pour ce qui le change.

Sans `watchdog`, le rechargeur de Werkzeug surveille chaque `.py` sous
`sys.path`, et la racine du depot y est. Un juge sauve dans `tests/` par une
autre session redemarrait Flask — 104 des 129 fichiers surveilles ne
changeaient rien au serveur. `run.py` passe `ce_que_le_rechargeur_ignore()` a
`app.run`, et ces juges le lisent avec la fonction meme de Werkzeug.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import dotenv
import flask
from werkzeug._reloader import _find_stat_paths

from config import CE_QUI_REDEMARRE_LE_SERVEUR, RACINE, ce_que_le_rechargeur_ignore


def _sous(racine: Path, chemins) -> set[Path]:
    """Les chemins sous `racine`, relatifs a elle."""
    return {Path(p).relative_to(racine) for p in chemins if Path(p).is_relative_to(racine)}


def test_run_py_ne_surveille_que_ce_qui_change_le_serveur(monkeypatch):
    """⚠️ Le juge qui compte : il lance `run.py` comme `uv run python run.py`, sans serveur.

    Il garde ce que `app.run` recoit, et demande a Werkzeug ce qu'il surveillerait.
    """
    recu = {}
    monkeypatch.setattr(flask.Flask, "run", lambda _app, **options: recu.update(options))
    # run.py charge le .env en ecrasant l'environnement : pas dans le processus des juges.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda **_k: False)
    monkeypatch.syspath_prepend(str(RACINE))  # `python run.py` y met le dossier du script
    runpy.run_path(str(RACINE / "run.py"), run_name="__main__")
    assert recu["use_reloader"]

    extra = set(recu.get("extra_files") or ())
    sans_motifs = _sous(RACINE, _find_stat_paths(extra, set()))
    surveilles = _sous(RACINE, _find_stat_paths(extra, set(recu.get("exclude_patterns") or ())))

    # Le temoin : sans les motifs, tests/ et scripts/ sont bien surveilles.
    assert any(p.parts[0] == "tests" for p in sans_motifs)
    assert any(p.parts[0] == "scripts" for p in sans_motifs)

    etrangers = sorted(str(p) for p in surveilles if p.parts[0] not in CE_QUI_REDEMARRE_LE_SERVEUR)
    assert etrangers == [], f"redemarreraient le serveur sans le changer : {etrangers[:5]}"
    assert {Path("run.py"), Path("config.py"), Path("app/__init__.py")} <= surveilles
    assert {p for p in sans_motifs if p.parts[0] == "app"} <= surveilles


def test_un_dossier_neuf_a_la_racine_ne_redemarre_rien(tmp_path, monkeypatch):
    """La liste est celle de ce qui compte : un `outils/` d'apres-demain est ignore aussi.

    Le `[` du nom du depot verifie qu'un chemin n'est pas lu comme un motif.
    """
    racine = tmp_path / "bandini [copie]"
    for chemin in (
        "app/__init__.py",
        "app/salle/sieges.py",
        "config.py",
        "run.py",
        "tests/test_x.py",
        "outils/y.py",
        "z.py",
    ):
        (racine / chemin).parent.mkdir(parents=True, exist_ok=True)
        (racine / chemin).write_text("", encoding="utf-8")
    monkeypatch.syspath_prepend(str(racine))

    surveilles = _sous(racine, _find_stat_paths(set(), ce_que_le_rechargeur_ignore(racine)))
    assert surveilles == {
        Path("app/__init__.py"),
        Path("app/salle/sieges.py"),
        Path("config.py"),
        Path("run.py"),
    }
