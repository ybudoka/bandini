"""Le banc d'essai joue les scripts MAIGRES (vague 4 des districts, 1er oct. 2026 — `app/statiques.py`) : tous les
juges JS jugent ce que le téléphone reçoit. Voir `test_statiques.py` pour le maigrisseur lui-même."""

import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def test_le_banc_joue_les_scripts_maigres(banc):
    """`Jeu.demarrer` porte des commentaires dans le dépôt (des ⚠️) ; celui que le banc a chargé n'en a plus,
    et ses lignes sont celles du source (sa première ligne y est, à la même place)."""
    source = (RACINE / "static" / "js" / "jeu.js").read_text(encoding="utf-8")
    debut = source.index("  function demarrer(w, d) {")
    fin = source.index("\n  }\n", debut) + len("\n  }")
    assert "⚠️" in source[debut:fin], "le témoin : demarrer est commenté dans le dépôt"
    joue = banc("(L) => L.Jeu.demarrer.toString()")
    assert joue.startswith("function demarrer(w, d) {")
    assert "⚠️" not in joue and not re.search(r"^\s*//", joue, re.MULTILINE)
    assert joue.count("\n") == source[debut:fin].count("\n")
