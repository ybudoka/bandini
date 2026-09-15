"""Les adresses qu'on imprime pour le telephone de la maison.

Le serveur de developpement ecoute `0.0.0.0` par defaut : ce qui decide si on
peut jouer sur le telephone, c'est l'adresse qu'on annonce. Werkzeug en annonce
une seule, celle de la route par defaut — donc celle du VPN quand il y en a un.
"""

from __future__ import annotations

import ipaddress
import socket

import pytest

from config import adresses_du_reseau_local, hote_est_local


def test_des_adresses_ipv4_valides():
    for adresse in adresses_du_reseau_local():
        ipaddress.IPv4Address(adresse)  # leve si ce n'est pas une IPv4


def test_ni_loopback_ni_lien_local(monkeypatch):
    """127.x ne sort pas de la machine, 169.254.x est une interface sans bail."""
    monkeypatch.setattr(
        socket,
        "gethostbyname_ex",
        lambda _nom: ("mac", [], ["127.0.0.1", "169.254.3.4", "192.168.4.188"]),
    )
    assert adresses_du_reseau_local() == ["192.168.4.188"]


def test_sans_doublon(monkeypatch):
    monkeypatch.setattr(
        socket,
        "gethostbyname_ex",
        lambda _nom: ("mac", [], ["192.168.4.188", "192.168.4.188", "10.0.0.7"]),
    )
    assert adresses_du_reseau_local() == ["192.168.4.188", "10.0.0.7"]


def test_repli_quand_le_nom_ne_resout_rien(monkeypatch):
    """Docker, CI : le nom de la machine ne resout pas. On ne casse pas le demarrage."""

    def _echec(_nom):
        raise OSError("nom inconnu")

    monkeypatch.setattr(socket, "gethostbyname_ex", _echec)
    for adresse in adresses_du_reseau_local():  # le repli, ou rien du tout
        ipaddress.IPv4Address(adresse)


def test_rien_a_annoncer_ne_leve_pas(monkeypatch):
    """Aucune interface, aucune route : une liste vide, jamais une exception."""

    def _echec(_nom):
        raise OSError("nom inconnu")

    class PriseMorte:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def connect(self, _cible):
            raise OSError("pas de route")

    monkeypatch.setattr(socket, "gethostbyname_ex", _echec)
    monkeypatch.setattr(socket, "socket", lambda *_a, **_k: PriseMorte())
    assert adresses_du_reseau_local() == []


@pytest.mark.parametrize("hote", ["127.0.0.1", " localhost ", "::1", "[::1]"])
def test_la_machine_seule_est_locale(hote):
    assert hote_est_local(hote)


@pytest.mark.parametrize("hote", ["0.0.0.0", "192.168.4.188", "::", "10.14.0.2", ""])
def test_tout_ce_qui_sort_de_la_machine_ne_l_est_pas(hote):
    """⚠️ Le juge qui compte : `use_debugger` suit cette reponse dans run.py.

    Ajouter `0.0.0.0` a la liste des hotes « locaux » ouvrirait un shell Python
    a tout le reseau de la maison. Ce test rougit ce jour-la.
    """
    assert not hote_est_local(hote)
