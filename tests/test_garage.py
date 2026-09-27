"""Le garage de Ti-Guy, côté catalogue (docs/jalons/le-garage-qui-modifie-les-chars.md) : le klaxon joue
le début du refrain de « Gens du pays », tel que la partition l'écrit."""

from app import garage

#: La partition (Choralies, chant 1, mesures 5 à 8), en noms de notes : trois noires, une blanche pointée.
REFRAIN = [("A4", 1), ("G4", 1), ("F4", 1), ("C5", 3), ("A4", 1), ("G4", 1), ("F4", 1), ("D5", 3)]

DEMI_TONS = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def frequence(nom: str) -> float:
    """Le tempérament égal, la 440."""
    return 440.0 * 2 ** ((DEMI_TONS[nom[0]] + 12 * (int(nom[1]) - 4)) / 12)


def test_le_klaxon_joue_gens_du_pays():
    assert len(garage.KLAXON_AIR) == len(REFRAIN)
    for (hz, duree), (nom, temps) in zip(garage.KLAXON_AIR, REFRAIN, strict=True):
        assert abs(hz - frequence(nom)) < 0.05, (hz, nom)
        assert abs(duree - temps * garage.NOIRE) < 1e-9, (duree, nom)
