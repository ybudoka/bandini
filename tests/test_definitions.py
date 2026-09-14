import gzip
import json

from app import definitions


def test_le_paquet_est_deterministe():
    a, b = definitions.construire(), definitions.construire()
    assert a.corps == b.corps
    assert a.etag == b.etag
    assert len(a.etag) == 16


def test_le_paquet_reste_leger():
    """⚠️ Budget releve a 600 Ko bruts le 13 sept. 2026 (demande de Martin).

    Mesure du 13 sept. 2026 : 370 Ko bruts / 43 Ko gzip, dont 306 Ko de carte
    pour 89 673 tuiles — et la carte ne pese que 26 Ko sur le fil, parce que
    `sol` et `voie` sont des suites de glyphes que gzip adore.

    Le brut n'est qu'un INDICATEUR : ce qui coute, c'est le gzip qui voyage
    et le temps de JSON.parse sur le telephone. Le plafond de 400 Ko etait a
    30 Ko d'etre touche par n'importe quel ajout ; il ne mesurait plus rien.
    Le gzip garde ses 70 Ko, et c'est lui le juge. Si le fil deborde, la
    carte sort du paquet (`/api/carte`, districts charges autour du joueur)
    — pas avant : personne n'a encore prouve le besoin de cette machinerie.
    Et ce qui n'est pas de la geographie (les dialogues de M16) n'entre pas
    ici du tout : une requete par mission, quand le telephone sonne.
    """
    paquet = definitions.construire()
    assert paquet.taille < 600_000, f"{paquet.taille} octets : le paquet enfle"
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
