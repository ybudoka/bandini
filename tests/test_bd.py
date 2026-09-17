"""La base de donnees de M14 : elle se cree, se migre une fois, tient deux workers, et se copie."""

import json
import sqlite3
import subprocess
import sys
import time
from datetime import date, timedelta

from app import bd, comptes
from conftest import RACINE

sys.path.insert(0, str(RACINE / "deploy"))
import sauvegarder_bd  # noqa: E402


def _base(tmp_path):
    conn = bd.ouvrir(tmp_path / bd.FICHIER)
    bd.migrer(conn)
    return conn


def test_une_base_vide_se_cree_toute_seule_en_wal(tmp_path):
    conn = _base(tmp_path)
    assert bd.version(conn) == len(bd.MIGRATIONS)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"comptes", "appareils", "jetons_perimes", "parties"} <= tables
    # ⚠️ Sans WAL, un lecteur bloque l'ecrivain de l'autre worker.
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    # ⚠️ Par connexion : sans elle, effacer un compte laisserait ses parties.
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_une_migration_ne_s_applique_qu_une_fois(tmp_path):
    conn = _base(tmp_path)
    conn.execute("INSERT INTO comptes (pseudo, pseudo_cle, mot_de_passe, cree_le)"
                 " VALUES ('a', 'a', 'x', 0)")
    # Une deuxieme connexion (l'autre worker) migre a son tour : rien ne se recree.
    autre = bd.ouvrir(tmp_path / bd.FICHIER)
    assert bd.migrer(autre) == len(bd.MIGRATIONS)
    assert autre.execute("SELECT COUNT(*) FROM comptes").fetchone()[0] == 1


def test_une_migration_livree_ne_change_plus():
    """⚠️ Un serveur a deja applique la migration 1 et ne la relira jamais : la modifier
    ne changerait rien la-bas, et tout ici. On en AJOUTE une."""
    migration_1 = "\n".join(bd.MIGRATIONS[0])
    for colonne in ("pseudo_cle TEXT NOT NULL UNIQUE", "precedente TEXT UNIQUE",
                    "compteur INTEGER NOT NULL", "PRIMARY KEY (compte_id, emplacement)"):
        assert colonne in migration_1


#: Un worker gunicorn, reduit a ce qui compte : il attend le signal, puis tente les
#: compteurs 1 a N sur la meme case que l'autre.
TRAVAILLEUR = """
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from app import bd, comptes
base, depart, n = Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
conn = bd.ouvrir(base)
bd.migrer(conn)
while not depart.exists():
    time.sleep(0.001)
gagnes = 0
for k in range(1, n + 1):
    ecrite, _ = comptes.ecrire_partie(conn, 1, 1, {"compteur": k, "partie": {"jour": k}})
    gagnes += ecrite
print(gagnes)
"""


def test_deux_workers_ecrivent_sans_se_barrer(tmp_path):
    """Deux PROCESSUS, comme les deux workers : chaque compteur n'est ecrit qu'une fois,
    et personne ne recoit `database is locked`.

    ⚠️ Sans `BEGIN IMMEDIATE`, les deux lisent le meme compteur puis veulent ecrire :
    SQLite refuse l'un des deux tout de suite, sans attendre son delai."""
    base = tmp_path / bd.FICHIER
    conn = _base(tmp_path)
    conn.execute("INSERT INTO comptes (id, pseudo, pseudo_cle, mot_de_passe, cree_le)"
                 " VALUES (1, 'a', 'a', 'x', 0)")
    depart = tmp_path / "depart"
    n = 150
    travailleurs = [
        subprocess.Popen([sys.executable, "-c", TRAVAILLEUR, str(RACINE), str(base),
                          str(depart), str(n)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(2)
    ]
    time.sleep(0.5)  # le temps d'importer Flask des deux cotes
    depart.touch()
    sorties = [t.communicate(timeout=60) for t in travailleurs]
    for t, (_, erreur) in zip(travailleurs, sorties):
        assert t.returncode == 0, erreur
    gagnes = [int(sortie.strip()) for sortie, _ in sorties]
    assert sum(gagnes) == n
    rang = conn.execute("SELECT compteur, partie FROM parties").fetchone()
    assert rang["compteur"] == n and json.loads(rang["partie"]) == {"jour": n}


def test_la_copie_quotidienne_emporte_ce_qui_dort_dans_le_wal(tmp_path):
    donnees, copies = tmp_path / "donnees", tmp_path / "copies"
    donnees.mkdir()
    conn = _base(donnees)
    conn.execute("PRAGMA wal_autocheckpoint = 0")  # tout reste dans le -wal
    conn.execute("INSERT INTO comptes (pseudo, pseudo_cle, mot_de_passe, cree_le)"
                 " VALUES ('Rocco', 'rocco', 'x', 0)")
    assert (donnees / (bd.FICHIER + "-wal")).stat().st_size > 0

    copie = sauvegarder_bd.sauvegarder(donnees, copies)
    lue = sqlite3.connect(copie)
    assert lue.execute("SELECT pseudo FROM comptes").fetchall() == [("Rocco",)]
    assert lue.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_la_copie_garde_les_sept_derniers_jours(tmp_path):
    donnees, copies = tmp_path / "donnees", tmp_path / "copies"
    donnees.mkdir()
    _base(donnees)
    premier = date(2026, 9, 1)
    for i in range(10):
        sauvegarder_bd.sauvegarder(donnees, copies, jour=premier + timedelta(days=i))
    restes = sorted(p.name for p in copies.iterdir())
    assert restes == [f"bandini-{(premier + timedelta(days=i)).isoformat()}.sqlite3"
                      for i in range(3, 10)]


def test_pas_de_base_pas_de_copie(tmp_path):
    assert sauvegarder_bd.sauvegarder(tmp_path / "vide", tmp_path / "copies") is None
    assert not (tmp_path / "copies").exists()


def test_la_copie_vise_le_fichier_de_l_application():
    assert sauvegarder_bd.FICHIER == bd.FICHIER


def test_l_installeur_pose_la_minuterie_du_vidage(racine):
    installeur = (racine / "deploy/installer.sh").read_text(encoding="utf-8")
    assert "enable -q --now bandini-sauvegarde-bd.timer" in installeur
    assert '"$BASE/shared/copies"' in installeur
    service = (racine / "deploy/systemd/bandini-sauvegarde-bd.service.example").read_text()
    assert "User=www-data" in service
    assert "/srv/bandini/current/deploy/sauvegarder_bd.py" in service
    assert "--copies /srv/bandini/shared/copies" in service


def test_une_partie_tient_sous_la_borne_de_nginx(racine):
    """⚠️ Au-dela de `client_max_body_size`, c'est nginx qui refuse — avec du HTML."""
    conf = (racine / "deploy/nginx/bandini-gestiondojo.conf.example").read_text()
    borne_nginx = int(conf.split("client_max_body_size")[1].split("k;")[0]) * 1024
    assert comptes.REQUETE_PARTIE_MAX_OCTETS < borne_nginx
