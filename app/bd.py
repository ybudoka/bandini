"""La base de donnees — SQLite, un fichier sous `DONNEES_DIR` (M14).

Une seule machine, deux workers gunicorn, quelques dizaines de joueurs : un
serveur de base de donnees serait une piece de plus a installer, a surveiller et
a redemarrer pour rien. Une partie avancee pese 4,5 Ko ; mille joueurs a trois
parties, 13 Mo.

⚠️ **WAL et un delai d'attente**, sinon les deux workers se marchent dessus et
ca donne `database is locked` — en production seulement, jamais en local ou il
n'y a qu'un processus. Et toute ecriture qui LIT avant d'ecrire (le compteur
d'une partie, la rotation d'un jeton) passe par `transaction()`, qui prend le
verrou d'ecriture AVANT la lecture : sans lui, deux workers liraient le meme
compteur et ecriraient tous les deux.

⚠️ **Le schema ne se touche jamais a la main sur le serveur** : une migration par
version, numerotee par sa place dans `MIGRATIONS`, et `PRAGMA user_version` dit
ou en est le fichier. On AJOUTE une migration, on ne modifie jamais une
migration livree — un serveur l'a deja appliquee et ne la relira pas.

⚠️ **La base s'ouvre a la premiere requete qui en a besoin**, jamais au
demarrage : la page, les definitions et la carte n'y touchent pas, et une base
illisible (disque plein, droits) coupe les comptes sans couper le jeu.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import current_app, g

FICHIER = "bandini.sqlite3"

#: Combien de secondes un worker attend le verrou de l'autre avant d'abandonner.
DELAI_S = 5.0

#: Une migration = les instructions qui menent de la version `i` a `i + 1`.
MIGRATIONS: tuple[tuple[str, ...], ...] = (
    # 1 — M14, 1re vague : les comptes, leurs appareils et leurs parties.
    (
        """CREATE TABLE comptes (
            id INTEGER PRIMARY KEY,
            pseudo TEXT NOT NULL,
            -- Le pseudo plie (casefold) : « Rocco » et « rocco » sont le meme compte.
            pseudo_cle TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            courriel TEXT,
            cree_le INTEGER NOT NULL
        )""",
        # ⚠️ Un appareil lie ne garde que des EMPREINTES de jeton, jamais le jeton.
        # `precedente` : le jeton d'avant la derniere rotation, tant que le nouveau
        # n'a jamais servi (`vu` = 0) — la reponse qui le portait a pu se perdre.
        """CREATE TABLE appareils (
            id INTEGER PRIMARY KEY,
            compte_id INTEGER NOT NULL REFERENCES comptes(id) ON DELETE CASCADE,
            empreinte TEXT NOT NULL UNIQUE,
            precedente TEXT UNIQUE,
            vu INTEGER NOT NULL DEFAULT 0,
            nom TEXT NOT NULL DEFAULT '',
            cree_le INTEGER NOT NULL,
            tourne_le INTEGER NOT NULL,
            derniere_visite INTEGER NOT NULL,
            expire_le INTEGER NOT NULL
        )""",
        "CREATE INDEX appareils_compte ON appareils(compte_id)",
        # Les jetons remplaces DONT le successeur a servi : s'il en revient un, deux
        # appareils portent la meme session.
        """CREATE TABLE jetons_perimes (
            empreinte TEXT PRIMARY KEY,
            compte_id INTEGER NOT NULL REFERENCES comptes(id) ON DELETE CASCADE,
            perime_le INTEGER NOT NULL
        )""",
        # `partie` NULL : l'emplacement a ete efface, et son compteur reste — sinon
        # une vieille copie reviendrait le remplir.
        """CREATE TABLE parties (
            compte_id INTEGER NOT NULL REFERENCES comptes(id) ON DELETE CASCADE,
            emplacement INTEGER NOT NULL CHECK (emplacement BETWEEN 1 AND 3),
            compteur INTEGER NOT NULL,
            partie TEXT,
            empreinte TEXT NOT NULL DEFAULT '',
            sauvee_le INTEGER NOT NULL,
            PRIMARY KEY (compte_id, emplacement)
        )""",
    ),
    # 2 — la limite d'essais (dette de M14, payee le 25 sept. 2026) : un mot de passe
    # rate par ligne, PAR ADRESSE et jamais par compte (`comptes.ESSAIS_MAX`). Dans la
    # base et pas en memoire : deux workers gunicorn, un seul compteur.
    (
        """CREATE TABLE essais_rates (
            adresse TEXT NOT NULL,
            quand INTEGER NOT NULL
        )""",
        "CREATE INDEX essais_rates_adresse ON essais_rates(adresse, quand)",
    ),
)


def ouvrir(chemin: str | os.PathLike) -> sqlite3.Connection:
    """Une connexion en mode autocommit : les transactions se prennent a la main."""
    conn = sqlite3.connect(chemin, timeout=DELAI_S, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    # Sure en WAL : on peut perdre la toute derniere transaction a une panne de
    # courant, jamais corrompre le fichier.
    conn.execute("PRAGMA synchronous = NORMAL")
    # ⚠️ Par connexion, pas par fichier : sans elle, ON DELETE CASCADE ne fait rien.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    """`BEGIN IMMEDIATE` : le verrou d'ecriture AVANT la premiere lecture."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


def version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrer(conn: sqlite3.Connection) -> int:
    """Applique les migrations qui manquent, et rend la version atteinte.

    ⚠️ La version se RELIT une fois le verrou pris : l'autre worker a pu migrer
    entre la premiere lecture et le `BEGIN`.
    """
    if version(conn) >= len(MIGRATIONS):
        return version(conn)
    with transaction(conn):
        for i in range(version(conn), len(MIGRATIONS)):
            for instruction in MIGRATIONS[i]:
                conn.execute(instruction)
            conn.execute(f"PRAGMA user_version = {i + 1}")
    return version(conn)


class Indisponible(RuntimeError):
    """La base ne s'ouvre pas (dossier illisible, disque plein) : les comptes tombent, le jeu non."""


def connexion() -> sqlite3.Connection:
    """La connexion de la requete, ouverte a la premiere demande.

    La migration se verifie a chaque ouverture : une base a jour ne coute qu'une
    lecture de `user_version`, et un fichier efface sous un processus lance se
    recree entier au lieu de se recreer vide.
    """
    if "bd" not in g:
        dossier = Path(current_app.config["DONNEES_DIR"])
        try:
            dossier.mkdir(parents=True, exist_ok=True)
            conn = ouvrir(dossier / FICHIER)
        except (OSError, sqlite3.Error) as erreur:
            raise Indisponible(f"{dossier / FICHIER} : {erreur}") from erreur
        try:
            migrer(conn)
        except BaseException:
            conn.close()
            raise
        g.bd = conn
    return g.bd


def fermer(_erreur: BaseException | None = None) -> None:
    conn = g.pop("bd", None)
    if conn is not None:
        conn.close()
