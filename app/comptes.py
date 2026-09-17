"""Les comptes, leurs appareils et leurs parties sur le serveur (M14).

**La regle : le local joue, le serveur se souvient.** Le `localStorage` reste la
verite pendant qu'on joue ; le serveur recoit des INSTANTANES, et un compte n'est
qu'une synchronisation — jamais une condition pour jouer.

Ce qu'on demande, et rien d'autre : un pseudo (les regles du tableau des scores),
un mot de passe, et un courriel FACULTATIF qui ne servira qu'a reprendre un mot
de passe perdu.

**La session longue est un jeton d'appareil**, pas un mot de passe qu'on retape :
32 octets aleatoires en cookie `httpOnly`, dont la base ne garde que l'EMPREINTE
— une base volee n'ouvre pas les comptes. Le mot de passe ne sert qu'a LIER un
appareil, une fois.

⚠️ **Le jeton tourne a l'OUVERTURE, pas a chaque requete.** Un jeton qui revient
apres que son successeur a servi, c'est deux appareils qui portent la meme
session : on coupe tous les appareils du compte. Mais un jeu envoie des requetes
qui se croisent — une sauvegarde lente partie avant la rotation, un `sendBeacon`
dont personne ne lit la reponse — et chacune de ces retardataires, avec une
rotation par requete, passerait pour un vol et deconnecterait tout le monde. Le
jeu tourne donc son jeton une fois par chargement (`/api/compte/ouvrir`) et
attend la reponse avant tout autre appel de compte.

⚠️ **Et une reponse peut se perdre** (l'autobus, le tunnel) : tant que le nouveau
jeton n'a JAMAIS servi, l'ancien reste accepte. Pendant `GRACE_S` il est pris tel
quel — le nouveau est peut-etre encore en route, ou deux onglets s'ouvrent
ensemble — ; passe ce delai, l'ouverture en emet un autre. L'ancien ne devient
une preuve de vol qu'une fois son successeur vu.

⚠️ **Le conflit de parties se regle par un compteur, jamais par une horloge** :
deux appareils n'ont pas la meme heure. Le serveur refuse un instantane dont le
compteur n'avance pas, rend le sien, et ne fusionne jamais rien — c'est le jeu
qui pose la question au joueur.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

from werkzeug.security import check_password_hash, generate_password_hash

from . import bd
from .scores import PSEUDO_MAX, pseudo_propre

#: Les trois cases de `Sauvegarde` (base.js) : le serveur les reflete, il ne les invente pas.
EMPLACEMENTS = 3

MOT_DE_PASSE_MIN = 8
#: ⚠️ Une borne haute aussi : scrypt sur un tres long mot de passe occupe un worker.
MOT_DE_PASSE_MAX = 128
COURRIEL_MAX = 254
NOM_APPAREIL_MAX = 32

COOKIE = "bandini-appareil"
#: Le cookie ne part qu'avec les appels de compte : ni la page, ni les definitions,
#: ni les scores ne le portent.
CHEMIN_COOKIE = "/api/compte"
JETON_OCTETS = 32
DUREE_JETON_S = 365 * 24 * 3600
GRACE_S = 120

#: Une partie bien avancee pese 4,5 Ko : dix fois plus, et le reste est un abus.
#: ⚠️ Sous le `client_max_body_size 64k` de nginx, sinon c'est nginx qui refuse,
#: avec une page HTML au lieu d'une reponse JSON.
PARTIE_MAX_OCTETS = 48 * 1024
#: La requete entiere : la partie, son compteur et son empreinte autour.
REQUETE_PARTIE_MAX_OCTETS = PARTIE_MAX_OCTETS + 4096
#: `Number.MAX_SAFE_INTEGER` : au-dela, le navigateur ne compte plus juste.
COMPTEUR_MAX = 2**53 - 1

_EMPREINTE_DEFS = re.compile(r"^[0-9a-f]{0,64}$")
_JETON = re.compile(r"^[A-Za-z0-9_\-]{16,64}$")
_COURRIEL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MAUVAIS_IDENTIFIANTS = "pseudo ou mot de passe incorrect"
APPAREIL_INCONNU = "cet appareil n'est pas lié à un compte"
SESSION_EXPIREE = "session expirée : reconnecte-toi"
SESSION_COUPEE = ("ce compte a été ouvert ailleurs avec une vieille session : "
                  "tous les appareils sont déconnectés, reconnecte-toi")


class CompteInvalide(ValueError):
    """Ce qui a ete envoye ne se prend pas."""

    statut = 400


class PseudoPris(CompteInvalide):
    statut = 409


class EmplacementInconnu(CompteInvalide):
    statut = 404


class PartieTropGrosse(CompteInvalide):
    statut = 413


class NonAutorise(Exception):
    """401. `coupe` : un jeton perime est revenu, et tous les appareils du compte sont delies."""

    def __init__(self, message: str, coupe: bool = False) -> None:
        super().__init__(message)
        self.coupe = coupe


@dataclass(frozen=True)
class Session:
    compte_id: int
    appareil_id: int
    pseudo: str
    #: Le NOUVEAU jeton a poser en cookie, quand il vient d'etre emis ; sinon None.
    jeton: str | None = None


def maintenant() -> int:
    return int(time.time())


def iso(secondes: int) -> str:
    return datetime.fromtimestamp(secondes, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def empreinte(jeton: str) -> str:
    """⚠️ sha256, pas scrypt : 256 bits aleatoires ne se devinent pas — ce qui rend un
    mot de passe lent a essayer ne protegerait rien ici — et une empreinte rapide se
    cherche par index."""
    return hashlib.sha256(jeton.encode("ascii")).hexdigest()


@lru_cache(maxsize=1)
def _leurre() -> str:
    """L'empreinte d'un mot de passe que personne n'a : un pseudo inconnu coute le meme
    temps qu'un mot de passe faux, et la duree de la reponse ne dit pas qui existe."""
    return generate_password_hash(secrets.token_hex(16))


def _objet(donnees: object) -> dict:
    if not isinstance(donnees, dict):
        raise CompteInvalide("corps attendu : un objet JSON")
    return donnees


def _nom_appareil(donnees: dict) -> str:
    nom = donnees.get("appareil")
    if not isinstance(nom, str):
        return ""
    return "".join(c for c in nom if c.isprintable()).strip()[:NOM_APPAREIL_MAX]


def _nouveau_jeton() -> str:
    return secrets.token_urlsafe(JETON_OCTETS)


def _lier(conn: sqlite3.Connection, compte_id: int, nom: str, quand: int) -> tuple[str, int]:
    jeton = _nouveau_jeton()
    curseur = conn.execute(
        "INSERT INTO appareils (compte_id, empreinte, vu, nom, cree_le, tourne_le,"
        " derniere_visite, expire_le) VALUES (?, ?, 0, ?, ?, ?, ?, ?)",
        (compte_id, empreinte(jeton), nom, quand, quand, quand, quand + DUREE_JETON_S),
    )
    return jeton, curseur.lastrowid


# --- Le compte -------------------------------------------------------------------------


def inscrire(conn: sqlite3.Connection, donnees: object, quand: int | None = None) -> Session:
    """Cree le compte ET lie l'appareil qui s'inscrit."""
    donnees = _objet(donnees)
    quand = maintenant() if quand is None else quand

    pseudo = pseudo_propre(donnees.get("pseudo"))
    if pseudo is None:
        raise CompteInvalide(f"pseudo : 1 à {PSEUDO_MAX} lettres, chiffres, espaces ou tirets")

    mot_de_passe = donnees.get("mot_de_passe")
    if not isinstance(mot_de_passe, str) or not (
        MOT_DE_PASSE_MIN <= len(mot_de_passe) <= MOT_DE_PASSE_MAX
    ):
        raise CompteInvalide(
            f"mot de passe : de {MOT_DE_PASSE_MIN} à {MOT_DE_PASSE_MAX} caractères"
        )

    courriel = donnees.get("courriel")
    if courriel in (None, ""):
        courriel = None
    elif not isinstance(courriel, str) or len(courriel) > COURRIEL_MAX or not _COURRIEL.match(
        courriel.strip()
    ):
        raise CompteInvalide("courriel : une adresse, ou rien (il est facultatif)")
    else:
        courriel = courriel.strip()

    # Hors transaction : scrypt prend un moment, et le verrou d'ecriture est a tout le monde.
    empreinte_mdp = generate_password_hash(mot_de_passe)
    with bd.transaction(conn):
        try:
            curseur = conn.execute(
                "INSERT INTO comptes (pseudo, pseudo_cle, mot_de_passe, courriel, cree_le)"
                " VALUES (?, ?, ?, ?, ?)",
                (pseudo, pseudo.casefold(), empreinte_mdp, courriel, quand),
            )
        except sqlite3.IntegrityError:
            raise PseudoPris("pseudo : déjà pris") from None
        compte_id = curseur.lastrowid
        jeton, appareil_id = _lier(conn, compte_id, _nom_appareil(donnees), quand)
    return Session(compte_id, appareil_id, pseudo, jeton)


def connecter(
    conn: sqlite3.Connection,
    donnees: object,
    jeton_actuel: str | None = None,
    quand: int | None = None,
) -> Session:
    """Le mot de passe lie cet appareil au compte.

    Le meme message pour un pseudo inconnu et un mot de passe faux. L'appareil qui
    portait deja un jeton le perd : on ne garde pas deux liens pour le meme appareil.
    """
    donnees = _objet(donnees)
    quand = maintenant() if quand is None else quand

    pseudo = pseudo_propre(donnees.get("pseudo"))
    mot_de_passe = donnees.get("mot_de_passe")
    if not isinstance(mot_de_passe, str) or len(mot_de_passe) > MOT_DE_PASSE_MAX:
        raise NonAutorise(MAUVAIS_IDENTIFIANTS)

    rang = None
    if pseudo is not None:
        rang = conn.execute(
            "SELECT id, pseudo, mot_de_passe FROM comptes WHERE pseudo_cle = ?",
            (pseudo.casefold(),),
        ).fetchone()
    if rang is None:
        check_password_hash(_leurre(), mot_de_passe)
        raise NonAutorise(MAUVAIS_IDENTIFIANTS)
    if not check_password_hash(rang["mot_de_passe"], mot_de_passe):
        raise NonAutorise(MAUVAIS_IDENTIFIANTS)

    with bd.transaction(conn):
        if isinstance(jeton_actuel, str) and _JETON.match(jeton_actuel):
            h = empreinte(jeton_actuel)
            conn.execute("DELETE FROM appareils WHERE empreinte = ? OR precedente = ?", (h, h))
        jeton, appareil_id = _lier(conn, rang["id"], _nom_appareil(donnees), quand)
    return Session(rang["id"], appareil_id, rang["pseudo"], jeton)


def _tourner(conn: sqlite3.Connection, appareil_id: int, remplace: str, quand: int) -> str:
    """Emet un nouveau jeton ; `remplace` (une empreinte) devient le precedent."""
    jeton = _nouveau_jeton()
    conn.execute(
        "UPDATE appareils SET precedente = ?, empreinte = ?, vu = 0, tourne_le = ?,"
        " expire_le = ? WHERE id = ?",
        (remplace, empreinte(jeton), quand, quand + DUREE_JETON_S, appareil_id),
    )
    # Un jeton plus vieux qu'une session entiere ne prouverait plus rien.
    conn.execute("DELETE FROM jetons_perimes WHERE perime_le < ?", (quand - DUREE_JETON_S,))
    return jeton


def authentifier(
    conn: sqlite3.Connection,
    jeton: object,
    tourner: bool = False,
    quand: int | None = None,
) -> Session:
    """La session que ce jeton ouvre, ou NonAutorise. `tourner` : l'ouverture du jeu."""
    quand = maintenant() if quand is None else quand
    if not isinstance(jeton, str) or not _JETON.match(jeton):
        raise NonAutorise(APPAREIL_INCONNU)
    h = empreinte(jeton)

    erreur: NonAutorise | None = None
    session: Session | None = None
    # ⚠️ L'erreur se leve APRES la transaction : un appareil expire ou un compte coupe
    # doit rester efface, et une exception dans le bloc annulerait l'effacement.
    with bd.transaction(conn):
        selection = (
            "SELECT a.id, a.compte_id, a.empreinte, a.precedente, a.vu, a.tourne_le,"
            " a.expire_le, c.pseudo FROM appareils a JOIN comptes c ON c.id = a.compte_id"
        )
        actuel = conn.execute(selection + " WHERE a.empreinte = ?", (h,)).fetchone()
        ancien = None if actuel else conn.execute(
            selection + " WHERE a.precedente = ?", (h,)
        ).fetchone()
        rang = actuel or ancien

        if rang is not None and rang["expire_le"] <= quand:
            conn.execute("DELETE FROM appareils WHERE id = ?", (rang["id"],))
            erreur = NonAutorise(SESSION_EXPIREE)
        elif actuel is not None:
            if not actuel["vu"] and actuel["precedente"]:
                # Le successeur sert : le jeton d'avant devient une preuve.
                conn.execute(
                    "INSERT OR IGNORE INTO jetons_perimes (empreinte, compte_id, perime_le)"
                    " VALUES (?, ?, ?)",
                    (actuel["precedente"], actuel["compte_id"], quand),
                )
            conn.execute(
                "UPDATE appareils SET vu = 1, precedente = NULL, derniere_visite = ? WHERE id = ?",
                (quand, actuel["id"]),
            )
            nouveau = _tourner(conn, actuel["id"], h, quand) if tourner else None
            session = Session(actuel["compte_id"], actuel["id"], actuel["pseudo"], nouveau)
        elif ancien is not None:
            # Le nouveau jeton n'a jamais servi : sa reponse s'est perdue, ou elle arrive.
            nouveau = None
            if tourner and quand - ancien["tourne_le"] >= GRACE_S:
                nouveau = _tourner(conn, ancien["id"], h, quand)
            conn.execute(
                "UPDATE appareils SET derniere_visite = ? WHERE id = ?", (quand, ancien["id"])
            )
            session = Session(ancien["compte_id"], ancien["id"], ancien["pseudo"], nouveau)
        else:
            perime = conn.execute(
                "SELECT compte_id FROM jetons_perimes WHERE empreinte = ?", (h,)
            ).fetchone()
            if perime is not None:
                conn.execute("DELETE FROM appareils WHERE compte_id = ?", (perime["compte_id"],))
                erreur = NonAutorise(SESSION_COUPEE, coupe=True)
            else:
                erreur = NonAutorise(APPAREIL_INCONNU)

    if erreur is not None:
        raise erreur
    return session


def deconnecter(conn: sqlite3.Connection, session: Session) -> None:
    with bd.transaction(conn):
        conn.execute("DELETE FROM appareils WHERE id = ?", (session.appareil_id,))


# --- Les parties -----------------------------------------------------------------------


def _emplacement(n: object) -> int:
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= EMPLACEMENTS:
        raise EmplacementInconnu(f"emplacement : de 1 à {EMPLACEMENTS}")
    return n


def _nombre(valeur: object, defaut: int) -> int:
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        return defaut
    return int(valeur)


def apercu(partie: object) -> dict | None:
    """Ce que le choix des parties montre : les champs de `Sauvegarde.apercu` (base.js)."""
    if not isinstance(partie, dict):
        return None
    stats = partie.get("stats") if isinstance(partie.get("stats"), dict) else {}
    faites = partie.get("missionsFaites")
    return {
        "jour": _nombre(partie.get("jour"), 1),
        "argent": _nombre(partie.get("argent"), 0),
        "secondes": _nombre(stats.get("secondes"), 0),
        "missions": len(faites) if isinstance(faites, dict) else 0,
    }


def _etat(n: int, rang: sqlite3.Row | None, avec_partie: bool) -> dict:
    partie = json.loads(rang["partie"]) if rang is not None and rang["partie"] else None
    etat = {
        "emplacement": n,
        "compteur": rang["compteur"] if rang is not None else 0,
        "sauvee_le": iso(rang["sauvee_le"]) if rang is not None else None,
    }
    if avec_partie:
        etat["partie"] = partie
        etat["empreinte"] = rang["empreinte"] if rang is not None else ""
    else:
        etat["apercu"] = apercu(partie)
    return etat


def _rang_partie(conn: sqlite3.Connection, compte_id: int, n: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT compteur, partie, empreinte, sauvee_le FROM parties"
        " WHERE compte_id = ? AND emplacement = ?",
        (compte_id, n),
    ).fetchone()


def etat_des_parties(conn: sqlite3.Connection, compte_id: int) -> list[dict]:
    """Les trois cases, avec leur compteur et leur apercu (sans la partie entiere)."""
    return [_etat(n, _rang_partie(conn, compte_id, n), avec_partie=False)
            for n in range(1, EMPLACEMENTS + 1)]


def lire_partie(conn: sqlite3.Connection, compte_id: int, n: object) -> dict:
    n = _emplacement(n)
    return _etat(n, _rang_partie(conn, compte_id, n), avec_partie=True)


def ecrire_partie(
    conn: sqlite3.Connection,
    compte_id: int,
    n: object,
    donnees: object,
    quand: int | None = None,
) -> tuple[bool, dict]:
    """(True, ce qui est ecrit) — ou (False, la partie du serveur) si le compteur n'avance pas.

    `{"compteur": 8, "partie": {...}, "empreinte": "…"}` ; `"partie": null` efface la
    case. ⚠️ Un effacement garde son compteur : sans lui, une vieille copie gardee par
    un autre appareil reviendrait remplir la case qu'on a videe.
    """
    n = _emplacement(n)
    donnees = _objet(donnees)
    quand = maintenant() if quand is None else quand

    compteur = donnees.get("compteur")
    if isinstance(compteur, bool) or not isinstance(compteur, int) or not (
        1 <= compteur <= COMPTEUR_MAX
    ):
        raise CompteInvalide("compteur : un entier positif")
    if "partie" not in donnees:
        raise CompteInvalide("partie : attendue (null pour effacer la case)")
    partie = donnees["partie"]
    if partie is not None and not isinstance(partie, dict):
        raise CompteInvalide("partie : un objet JSON, ou null")
    empreinte_defs = donnees.get("empreinte", "")
    if not isinstance(empreinte_defs, str) or not _EMPREINTE_DEFS.match(empreinte_defs):
        raise CompteInvalide("empreinte : celle des définitions, en hexadécimal")

    corps = None
    if partie is not None:
        corps = json.dumps(partie, ensure_ascii=False, separators=(",", ":"))
        if len(corps.encode("utf-8")) > PARTIE_MAX_OCTETS:
            raise PartieTropGrosse(f"partie : plus de {PARTIE_MAX_OCTETS // 1024} Ko")

    refus = None
    with bd.transaction(conn):
        rang = _rang_partie(conn, compte_id, n)
        if rang is not None and compteur <= rang["compteur"]:
            refus = _etat(n, rang, avec_partie=True)
        else:
            conn.execute(
                "INSERT INTO parties (compte_id, emplacement, compteur, partie, empreinte,"
                " sauvee_le) VALUES (?, ?, ?, ?, ?, ?)"
                " ON CONFLICT (compte_id, emplacement) DO UPDATE SET"
                " compteur = excluded.compteur, partie = excluded.partie,"
                " empreinte = excluded.empreinte, sauvee_le = excluded.sauvee_le",
                (compte_id, n, compteur, corps, empreinte_defs, quand),
            )
    if refus is not None:
        return False, refus
    return True, {"emplacement": n, "compteur": compteur, "sauvee_le": iso(quand)}
