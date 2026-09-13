import gzip
import json

from app import definitions


def test_le_paquet_est_deterministe():
    a, b = definitions.construire(), definitions.construire()
    assert a.corps == b.corps
    assert a.etag == b.etag
    assert len(a.etag) == 16


def test_le_paquet_reste_leger():
    """⚠️ Budget releve a 400 Ko bruts pour les cinq districts (M8).

    Mesure du 13 sept. 2026, avant M8 : 101 Ko bruts / 17 Ko gzip, dont 64 Ko
    de carte pour 17 584 tuiles. La ville complete en fait 89 673 — d'ou les
    ~315 Ko bruts d'aujourd'hui, et toujours moins de 70 Ko sur le fil, parce
    que `sol` et `voie` sont des suites de glyphes que gzip adore.

    C'est le gzip qui voyage : c'est donc lui qui a le budget serre. Si le brut
    approche des 400 Ko, la carte sort du paquet (`/api/carte`, districts
    charges autour du joueur) — pas avant : personne n'a encore prouve le
    besoin de cette machinerie.
    """
    paquet = definitions.construire()
    assert paquet.taille < 400_000, f"{paquet.taille} octets : la carte enfle"
    sur_le_fil = len(gzip.compress(paquet.corps, 6))
    assert sur_le_fil < 70_000, f"{sur_le_fil} octets gzip : le telephone va sentir passer"


def test_l_empreinte_change_avec_le_contenu(monkeypatch):
    avant = definitions.construire().etag
    monkeypatch.setattr(definitions.economie, "ARGENT_DEPART", 51)
    assert definitions.construire().etag != avant


def test_le_paquet_contient_tout(paquet):
    for cle in ("version", "empreinte", "tuile_px", "vehicules", "armes", "ordre_armes", "economie",
                "recherche", "carte", "missions", "defis", "types_objectifs", "magasins", "tenues"):
        assert cle in paquet, cle
    assert json.dumps(paquet)  # serialisable
