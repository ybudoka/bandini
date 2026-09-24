"""Le defi du jour (M14, 5e vague) : le serveur dit quel defi est celui d'aujourd'hui.

Une rotation sur la DATE de Quebec, la meme pour tout le monde — voir le prologue de
`app/defi.py`, qui dit aussi pourquoi il n'y a ni classement ni graine.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfoNotFoundError

import pytest

from app import defi, missions

UTC = timezone.utc
#: ⚠️ Les defis qui TOURNENT : ceux qu'on a des le depart. Un defi qui se debloque (`debloque`)
#: n'entre pas dans la rotation (voir `defi.rotation`).
SLUGS = [d["slug"] for d in missions.DEFIS if not d.get("debloque")]


def _quebec(annee, mois, jour, heure=12, minute=0):
    """Un instant a l'heure de Quebec (ete ou hiver, la base des fuseaux tranche)."""
    return datetime(annee, mois, jour, heure, minute, tzinfo=defi._fuseau())


def test_le_premier_jour_de_la_rotation_est_le_premier_defi_du_catalogue():
    assert defi.defi_du(defi.EPOQUE) == SLUGS[0]


def test_chaque_defi_revient_une_fois_par_tour_et_jamais_deux_jours_de_suite():
    """La rotation est un CYCLE de la longueur du catalogue : equitable, et jamais le meme defi
    deux jours de suite — sur de longues plages, avant comme apres l'epoque."""
    n = len(SLUGS)
    jours = [defi.EPOQUE + timedelta(days=k) for k in range(-3 * n, 60 * n)]
    slugs = [defi.defi_du(j) for j in jours]
    assert all(a != b for a, b in zip(slugs, slugs[1:], strict=False))
    for debut in range(0, len(slugs) - n, 7):
        assert sorted(slugs[debut:debut + n]) == sorted(SLUGS), "n jours de suite : chaque defi une fois"


def test_le_defi_du_jour_ne_depend_que_de_la_date():
    """⚠️ Ni hasard ni `hash()` (salé par processus, le piege de `ci-pile-ou-face`) : deux
    workers gunicorn, deux redemarrages, la meme reponse."""
    jour = date(2027, 3, 14)
    assert {defi.defi_du(jour) for _ in range(50)} == {defi.defi_du(jour)}
    assert defi.aujourdhui(_quebec(2027, 3, 14, 1)) == defi.aujourdhui(_quebec(2027, 3, 14, 23))


def test_un_defi_qui_se_debloque_n_est_jamais_le_defi_du_jour():
    """Le serveur ne connait pas la partie : il designerait a un joueur neuf un defi que sa carte
    ne montre pas encore. Et la rotation d'avant les dix-huit ne bouge pas d'un jour."""
    caches = {d["slug"] for d in missions.DEFIS if d.get("debloque")}
    assert caches, "le catalogue a des defis a debloquer"
    vus = {defi.defi_du(date(2026, 1, 1) + timedelta(days=k)) for k in range(400)}
    assert not vus & caches
    assert defi.defi_du(date(2026, 9, 23)) == "tour_shop", "le 23 sept. 2026 reste celui qu'il etait"


def test_toutes_les_reponses_nomment_un_defi_qui_existe():
    for k in range(400):
        assert defi.defi_du(date(2026, 1, 1) + timedelta(days=k)) in SLUGS


@pytest.mark.parametrize("veille,lendemain", [
    # ETE (EDT, UTC-4) : minuit a Quebec = 04:00 UTC
    (datetime(2026, 9, 21, 3, 59, tzinfo=UTC), datetime(2026, 9, 21, 4, 0, tzinfo=UTC)),
    # HIVER (EST, UTC-5) : minuit a Quebec = 05:00 UTC
    (datetime(2026, 12, 21, 4, 59, tzinfo=UTC), datetime(2026, 12, 21, 5, 0, tzinfo=UTC)),
])
def test_le_jour_change_a_minuit_heure_de_quebec_ete_comme_hiver(veille, lendemain):
    """⚠️ Pas a minuit UTC (20 h en ete : un joueur du soir verrait « demain » avant la fin de sa
    soiree), et pas a une heure fixe : le changement d'heure decale minuit d'une heure UTC."""
    avant, apres = defi.aujourdhui(veille), defi.aujourdhui(lendemain)
    assert date.fromisoformat(apres["date"]) - date.fromisoformat(avant["date"]) == timedelta(days=1)
    assert avant["defi"] != apres["defi"]


def test_minuit_utc_n_est_pas_minuit_a_quebec():
    """20 h a Quebec en ete : c'est encore le soir du meme jour."""
    assert defi.aujourdhui(datetime(2026, 9, 21, 0, 0, tzinfo=UTC))["date"] == "2026-09-20"


def test_un_instant_sans_fuseau_est_refuse():
    """Un `datetime` naif ne dit pas quel jour il est : mieux vaut lever que deviner."""
    with pytest.raises(ValueError):
        defi.jour_de(datetime(2026, 9, 20, 12, 0))


def test_sans_base_de_fuseaux_le_defi_repond_quand_meme_avec_un_avertissement(monkeypatch, caplog):
    """⚠️ `tzdata` n'est pas une dependance : si le systeme n'a pas la base des fuseaux, la
    route que le titre appelle a chaque chargement ne doit pas faire un 500."""
    def introuvable(_):
        raise ZoneInfoNotFoundError("America/Toronto")

    monkeypatch.setattr(defi, "ZoneInfo", introuvable)
    with caplog.at_level("WARNING"):
        reponse = defi.aujourdhui(datetime(2026, 9, 21, 3, 30, tzinfo=UTC))
    assert reponse == {"date": "2026-09-20", "defi": defi.defi_du(date(2026, 9, 20))}
    assert "introuvable" in caplog.text
    # Le repli est UTC-5 : 04:30 UTC en ete est deja « demain » ici, une heure plus tard qu'a Quebec.
    assert defi.aujourdhui(datetime(2026, 9, 21, 5, 0, tzinfo=UTC))["date"] == "2026-09-21"


def test_par_http_le_defi_du_jour_se_lit_sans_compte_et_ne_se_garde_pas(client):
    reponse = client.get("/api/defi")
    assert reponse.status_code == 200
    corps = reponse.get_json()
    assert set(corps) == {"date", "defi"}, "un champ de plus n'aurait aucun lecteur"
    assert corps["defi"] in SLUGS
    date.fromisoformat(corps["date"])
    # ⚠️ Un defi garde par le navigateur passerait minuit sans le savoir.
    assert reponse.headers["Cache-Control"] == "no-store"
    assert "Set-Cookie" not in reponse.headers, "la route est publique : elle ne pose rien"
