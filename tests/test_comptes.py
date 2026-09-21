"""Les comptes de M14 : le mot de passe lie un appareil, le jeton tourne, le compteur tranche."""

import os
import subprocess
import sys

import pytest

from app import bd, comptes, create_app
from conftest import RACINE, ConfigTest

MDP = "la-brume-1987"
T0 = 1_800_000_000


@pytest.fixture
def conn(tmp_path):
    connexion = bd.ouvrir(tmp_path / bd.FICHIER)
    bd.migrer(connexion)
    yield connexion
    connexion.close()


def _inscrire(conn, pseudo="Rocco", quand=T0, **extra):
    return comptes.inscrire(conn, {"pseudo": pseudo, "mot_de_passe": MDP, **extra}, quand=quand)


def _appareils(conn, compte_id):
    return conn.execute("SELECT COUNT(*) FROM appareils WHERE compte_id = ?",
                        (compte_id,)).fetchone()[0]


def _tout_ce_que_la_base_contient(conn, dossier):
    """Le texte de la base (vidage SQL) ET les octets des fichiers, WAL compris."""
    texte = "\n".join(conn.iterdump())
    octets = b"".join(p.read_bytes() for p in dossier.iterdir() if p.name.startswith(bd.FICHIER))
    return texte, octets


# --- Le compte -------------------------------------------------------------------------


def test_un_mot_de_passe_n_est_jamais_garde_en_clair(conn, tmp_path):
    _inscrire(conn, courriel="rocco@example.com")
    texte, octets = _tout_ce_que_la_base_contient(conn, tmp_path)
    assert MDP not in texte and MDP.encode() not in octets
    empreinte = conn.execute("SELECT mot_de_passe FROM comptes").fetchone()[0]
    assert empreinte.startswith("scrypt:")


def test_le_jeton_n_existe_en_clair_nulle_part_dans_la_base(conn, tmp_path):
    session = _inscrire(conn)
    jetons = [session.jeton]
    for i in range(1, 4):
        session = comptes.authentifier(conn, jetons[-1], tourner=True, quand=T0 + i * 3600)
        jetons.append(session.jeton)
    assert len(set(jetons)) == 4
    texte, octets = _tout_ce_que_la_base_contient(conn, tmp_path)
    for jeton in jetons:
        assert jeton not in texte and jeton.encode() not in octets


def test_un_pseudo_pris_est_refuse_sans_egard_a_la_casse(conn):
    _inscrire(conn, "Rocco")
    with pytest.raises(comptes.PseudoPris):
        _inscrire(conn, "rOCCO")


@pytest.mark.parametrize("donnees", [
    None,
    [],
    {"pseudo": "", "mot_de_passe": MDP},
    {"pseudo": "<script>", "mot_de_passe": MDP},
    {"pseudo": "x" * 17, "mot_de_passe": MDP},
    {"pseudo": "Rocco", "mot_de_passe": "court"},
    {"pseudo": "Rocco", "mot_de_passe": "x" * 129},
    {"pseudo": "Rocco", "mot_de_passe": 12345678},
    {"pseudo": "Rocco", "mot_de_passe": MDP, "courriel": "pas-une-adresse"},
])
def test_une_inscription_invalide_est_refusee(conn, donnees):
    with pytest.raises(comptes.CompteInvalide):
        comptes.inscrire(conn, donnees)


def test_la_regle_du_pseudo(conn):
    """⚠️ La regle vivait dans `scores.py` jusqu'au retrait du tableau des scores
    (17 sept. 2026) : elle a suivi son dernier lecteur. Un pseudo est reaffiche a
    tout le monde, donc rien qui ressemble a du balisage ; et les espaces se
    reduisent avant d'entrer en base."""
    assert comptes.pseudo_propre("<b>") is None
    assert comptes.pseudo_propre("") is None
    assert comptes.pseudo_propre("x" * (comptes.PSEUDO_MAX + 1)) is None
    with pytest.raises(comptes.CompteInvalide):
        comptes.inscrire(conn, {"pseudo": "<b>", "mot_de_passe": MDP})
    assert comptes.pseudo_propre("  Léa   T ") == "Léa T"
    assert _inscrire(conn, "  Léa   T ").pseudo == "Léa T"


def test_le_courriel_est_facultatif(conn):
    _inscrire(conn, "Sans")
    _inscrire(conn, "Vide", courriel="")
    assert conn.execute("SELECT COUNT(*) FROM comptes WHERE courriel IS NULL").fetchone()[0] == 2


def test_meme_refus_pour_un_pseudo_inconnu_et_un_mot_de_passe_faux(conn):
    _inscrire(conn)
    messages = set()
    for donnees in ({"pseudo": "Personne", "mot_de_passe": MDP},
                    {"pseudo": "Rocco", "mot_de_passe": "pas-le-bon"},
                    {"pseudo": "<x>", "mot_de_passe": MDP}):
        with pytest.raises(comptes.NonAutorise) as refus:
            comptes.connecter(conn, donnees)
        messages.add(str(refus.value))
    assert messages == {comptes.MAUVAIS_IDENTIFIANTS}


def test_se_reconnecter_ne_double_pas_l_appareil(conn):
    session = _inscrire(conn)
    ailleurs = comptes.connecter(conn, {"pseudo": "rocco", "mot_de_passe": MDP}, quand=T0 + 5)
    assert _appareils(conn, session.compte_id) == 2
    # Le meme appareil (son cookie) se reconnecte : son ancien lien s'en va.
    comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP},
                      jeton_actuel=ailleurs.jeton, quand=T0 + 10)
    assert _appareils(conn, session.compte_id) == 2
    with pytest.raises(comptes.NonAutorise):
        comptes.authentifier(conn, ailleurs.jeton, quand=T0 + 20)


# --- Le jeton qui tourne ---------------------------------------------------------------


def test_l_ouverture_tourne_le_jeton_et_pas_les_autres_appels(conn):
    session = _inscrire(conn)
    assert comptes.authentifier(conn, session.jeton, quand=T0 + 1).jeton is None
    ouverte = comptes.authentifier(conn, session.jeton, tourner=True, quand=T0 + 2)
    assert ouverte.jeton and ouverte.jeton != session.jeton
    assert comptes.authentifier(conn, ouverte.jeton, quand=T0 + 3).compte_id == session.compte_id


def test_un_jeton_perime_qui_revient_coupe_tous_les_appareils_du_compte(conn):
    telephone = _inscrire(conn)
    ordi = comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP}, quand=T0 + 1)
    autre = _inscrire(conn, "Sal", quand=T0 + 1)

    nouveau = comptes.authentifier(conn, telephone.jeton, tourner=True, quand=T0 + 60).jeton
    comptes.authentifier(conn, nouveau, quand=T0 + 61)  # le successeur a servi

    # Quelqu'un d'autre porte encore l'ancien : deux appareils, une seule session.
    with pytest.raises(comptes.NonAutorise) as refus:
        comptes.authentifier(conn, telephone.jeton, quand=T0 + 3600)
    assert refus.value.coupe
    assert _appareils(conn, telephone.compte_id) == 0
    for jeton in (nouveau, ordi.jeton):
        with pytest.raises(comptes.NonAutorise):
            comptes.authentifier(conn, jeton, quand=T0 + 3601)
    # ⚠️ Le compte, lui, ne se bloque pas : le mot de passe relie un appareil.
    comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP}, quand=T0 + 3602)
    # Et les autres comptes n'ont rien vu.
    assert comptes.authentifier(conn, autre.jeton, quand=T0 + 3603).pseudo == "Sal"


def test_une_reponse_perdue_ne_coupe_personne(conn):
    """L'autobus : la reponse qui portait le nouveau jeton ne revient jamais."""
    session = _inscrire(conn)
    perdu = comptes.authentifier(conn, session.jeton, tourner=True, quand=T0 + 10).jeton

    # Deux onglets, ou la meme ouverture retentee tout de suite : l'ancien passe, sans
    # emettre un troisieme jeton — le nouveau est peut-etre encore en route.
    retente = comptes.authentifier(conn, session.jeton, tourner=True, quand=T0 + 11)
    assert retente.compte_id == session.compte_id and retente.jeton is None

    # Plus tard, l'appareil porte toujours l'ancien : l'ouverture en emet un autre.
    plus_tard = T0 + 10 + comptes.GRACE_S
    remplace = comptes.authentifier(conn, session.jeton, tourner=True, quand=plus_tard).jeton
    assert remplace not in (None, perdu)
    comptes.authentifier(conn, remplace, quand=plus_tard + 1)

    # Le jeton jamais recu n'ouvre rien, mais ne passe pas pour un vol.
    with pytest.raises(comptes.NonAutorise) as refus:
        comptes.authentifier(conn, perdu, quand=plus_tard + 2)
    assert not refus.value.coupe
    assert _appareils(conn, session.compte_id) == 1


def test_une_session_dure_un_an_depuis_sa_derniere_ouverture(conn):
    session = _inscrire(conn)
    presque = T0 + comptes.DUREE_JETON_S - 1
    nouveau = comptes.authentifier(conn, session.jeton, tourner=True, quand=presque).jeton
    # L'ouverture a repousse l'echeance : un an de plus.
    comptes.authentifier(conn, nouveau, quand=presque + comptes.DUREE_JETON_S - 1)
    with pytest.raises(comptes.NonAutorise) as refus:
        comptes.authentifier(conn, nouveau, quand=presque + comptes.DUREE_JETON_S)
    assert str(refus.value) == comptes.SESSION_EXPIREE
    assert _appareils(conn, session.compte_id) == 0


def test_se_deconnecter_delie_cet_appareil_seulement(conn):
    telephone = _inscrire(conn)
    ordi = comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP}, quand=T0 + 1)
    comptes.deconnecter(conn, comptes.authentifier(conn, telephone.jeton, quand=T0 + 2))
    with pytest.raises(comptes.NonAutorise):
        comptes.authentifier(conn, telephone.jeton, quand=T0 + 3)
    assert comptes.authentifier(conn, ordi.jeton, quand=T0 + 3).pseudo == "Rocco"


# --- Les parties -----------------------------------------------------------------------


def _partie(jour=3, argent=450):
    return {"jour": jour, "argent": argent, "stats": {"secondes": 1200},
            "missionsFaites": {"m1": True, "m2": True}}


def test_un_instantane_au_compteur_plus_petit_ou_egal_est_refuse_et_rend_celui_du_serveur(conn):
    compte = _inscrire(conn).compte_id
    ecrite, _ = comptes.ecrire_partie(conn, compte, 1, {"compteur": 8, "partie": _partie(12),
                                                         "empreinte": "ab12"}, quand=T0)
    assert ecrite
    for compteur in (8, 7, 1):
        ecrite, serveur = comptes.ecrire_partie(
            conn, compte, 1, {"compteur": compteur, "partie": _partie(2)}, quand=T0 + 5)
        assert not ecrite
        assert serveur["compteur"] == 8 and serveur["partie"]["jour"] == 12
        assert serveur["empreinte"] == "ab12"
    assert comptes.lire_partie(conn, compte, 1)["partie"]["jour"] == 12

    ecrite, etat = comptes.ecrire_partie(conn, compte, 1, {"compteur": 9, "partie": _partie(13)},
                                         quand=T0 + 6)
    assert ecrite and etat["compteur"] == 9
    assert comptes.lire_partie(conn, compte, 1)["partie"]["jour"] == 13


def test_effacer_une_case_garde_son_compteur(conn):
    """Sans lui, la vieille copie d'un autre appareil reviendrait remplir la case videe."""
    compte = _inscrire(conn).compte_id
    comptes.ecrire_partie(conn, compte, 2, {"compteur": 5, "partie": _partie()})
    assert comptes.ecrire_partie(conn, compte, 2, {"compteur": 6, "partie": None})[0]
    ecrite, serveur = comptes.ecrire_partie(conn, compte, 2, {"compteur": 5, "partie": _partie()})
    assert not ecrite and serveur["partie"] is None and serveur["compteur"] == 6
    case = comptes.etat_des_parties(conn, compte)[1]
    assert case["compteur"] == 6 and case["apercu"] is None


def test_l_apercu_des_trois_cases_montre_ce_que_montre_le_jeu(conn):
    compte = _inscrire(conn).compte_id
    comptes.ecrire_partie(conn, compte, 3, {"compteur": 1, "partie": _partie(7, 980)}, quand=T0)
    cases = comptes.etat_des_parties(conn, compte)
    assert [c["emplacement"] for c in cases] == [1, 2, 3]
    assert cases[0] == {"emplacement": 1, "compteur": 0, "sauvee_le": None, "apercu": None}
    assert cases[2]["apercu"] == {"jour": 7, "argent": 980, "secondes": 1200, "missions": 2}
    assert cases[2]["sauvee_le"] == "2027-01-15T08:00:00Z"
    assert "partie" not in cases[2]  # l'apercu voyage, pas la partie entiere


@pytest.mark.parametrize("donnees", [
    None,
    {"partie": {}},
    {"compteur": 0, "partie": {}},
    {"compteur": -3, "partie": {}},
    {"compteur": True, "partie": {}},
    {"compteur": "4", "partie": {}},
    {"compteur": 2.5, "partie": {}},
    {"compteur": 2**53, "partie": {}},
    {"compteur": 1},
    {"compteur": 1, "partie": [1, 2]},
    {"compteur": 1, "partie": "{}"},
    {"compteur": 1, "partie": {}, "empreinte": "PAS-HEX"},
])
def test_un_instantane_mal_forme_est_refuse(conn, donnees):
    compte = _inscrire(conn).compte_id
    with pytest.raises(comptes.CompteInvalide):
        comptes.ecrire_partie(conn, compte, 1, donnees)


@pytest.mark.parametrize("n", [0, 4, -1, True])
def test_trois_cases_pas_une_de_plus(conn, n):
    compte = _inscrire(conn).compte_id
    with pytest.raises(comptes.EmplacementInconnu):
        comptes.ecrire_partie(conn, compte, n, {"compteur": 1, "partie": {}})


def test_les_parties_d_un_compte_ne_se_lisent_pas_d_un_autre(conn):
    rocco = _inscrire(conn, "Rocco").compte_id
    sal = _inscrire(conn, "Sal").compte_id
    comptes.ecrire_partie(conn, rocco, 1, {"compteur": 3, "partie": _partie()})
    assert comptes.lire_partie(conn, sal, 1)["partie"] is None
    assert comptes.ecrire_partie(conn, sal, 1, {"compteur": 1, "partie": _partie(1)})[0]
    assert comptes.lire_partie(conn, rocco, 1)["compteur"] == 3


# --- Effacer son compte (M14, 4e vague) ---------------------------------------------------

TABLES_DU_COMPTE = ("appareils", "parties", "jetons_perimes")


def _tout_ce_qui_appartient_a(conn, compte_id):
    """Les lignes du compte dans CHAQUE table : `comptes` (id) et les trois qui en descendent."""
    n = conn.execute("SELECT COUNT(*) FROM comptes WHERE id = ?", (compte_id,)).fetchone()[0]
    return {"comptes": n, **{t: conn.execute(f"SELECT COUNT(*) FROM {t} WHERE compte_id = ?",
                                              (compte_id,)).fetchone()[0] for t in TABLES_DU_COMPTE}}


def _un_compte_bien_rempli(conn, pseudo="Rocco"):
    """Deux appareils, deux parties, et un jeton perime (la trace d'un vol detecte)."""
    telephone = _inscrire(conn, pseudo)
    comptes.connecter(conn, {"pseudo": pseudo, "mot_de_passe": MDP}, quand=T0 + 1)
    comptes.ecrire_partie(conn, telephone.compte_id, 1, {"compteur": 3, "partie": _partie(5)}, quand=T0)
    comptes.ecrire_partie(conn, telephone.compte_id, 2, {"compteur": 1, "partie": _partie(9)}, quand=T0)
    conn.execute("INSERT INTO jetons_perimes (empreinte, compte_id, perime_le) VALUES (?, ?, ?)",
                 (comptes.empreinte(f"perime-de-{pseudo}"), telephone.compte_id, T0))
    conn.commit()
    return telephone


def test_effacer_un_compte_efface_tout_ce_qui_lui_appartient_et_rien_d_autre(conn):
    """⚠️ Le contrat de la fiche : « les parties disparaissent, les appareils sont
    revoques ». Un seul `DELETE FROM comptes` — les trois autres tables descendent de lui en
    `ON DELETE CASCADE`, et `foreign_keys` est allume par connexion : c'est ce juge qui
    rougirait si l'un des deux lachait, avec un compte a moitie efface."""
    rocco = _un_compte_bien_rempli(conn)
    sal = _un_compte_bien_rempli(conn, "Sal")
    avant_sal = _tout_ce_qui_appartient_a(conn, sal.compte_id)
    assert avant_sal == {"comptes": 1, "appareils": 2, "parties": 2, "jetons_perimes": 1}
    assert _tout_ce_qui_appartient_a(conn, rocco.compte_id) == avant_sal

    comptes.effacer(conn, comptes.authentifier(conn, rocco.jeton), {"mot_de_passe": MDP})

    assert _tout_ce_qui_appartient_a(conn, rocco.compte_id) == {t: 0 for t in ("comptes", *TABLES_DU_COMPTE)}
    assert _tout_ce_qui_appartient_a(conn, sal.compte_id) == avant_sal, "un autre compte n'a pas bouge"


def test_apres_l_effacement_les_jetons_du_compte_ne_valent_plus_rien(conn):
    rocco = _inscrire(conn)
    ordi = comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP}, quand=T0 + 1)
    comptes.effacer(conn, comptes.authentifier(conn, rocco.jeton), {"mot_de_passe": MDP})
    for jeton in (rocco.jeton, ordi.jeton):
        with pytest.raises(comptes.NonAutorise):
            comptes.authentifier(conn, jeton)
    with pytest.raises(comptes.NonAutorise):
        comptes.connecter(conn, {"pseudo": "Rocco", "mot_de_passe": MDP})


def test_le_pseudo_efface_est_libre_et_le_nouveau_compte_repart_a_vide(conn):
    """Le pseudo se reprend aussitot — et rien de l'ancien compte ne revient avec lui."""
    ancien = _un_compte_bien_rempli(conn)
    comptes.effacer(conn, comptes.authentifier(conn, ancien.jeton), {"mot_de_passe": MDP})
    neuf = _inscrire(conn, "ROCCO", quand=T0 + 100)
    # ⚠️ SQLite REUTILISE l'id d'un compte efface (`INTEGER PRIMARY KEY`, pas d'AUTOINCREMENT) :
    # si le CASCADE lachait, les parties et appareils orphelins s'accrocheraient au NOUVEAU
    # compte. « Il repart a vide » est donc exactement la garde qui compte, et pas « l'id change ».
    assert all(p["compteur"] == 0 for p in comptes.etat_des_parties(conn, neuf.compte_id))
    assert _tout_ce_qui_appartient_a(conn, neuf.compte_id) == {"comptes": 1, "appareils": 1,
                                                                "parties": 0, "jetons_perimes": 0}


@pytest.mark.parametrize("donnees", [{}, {"mot_de_passe": None}, {"mot_de_passe": 12345678},
                                     {"mot_de_passe": "x" * (comptes.MOT_DE_PASSE_MAX + 1)},
                                     {"mot_de_passe": "un-mauvais-mot-de-passe"}, {"mot_de_passe": ""}])
def test_effacer_refuse_un_mot_de_passe_faux_ou_absent_et_ne_touche_a_rien(conn, donnees):
    """⚠️ Le mot de passe est REDEMANDE, meme sur un appareil deja lie : un cookie
    d'appareil emprunte ou vole ne doit pas suffire a detruire un compte."""
    rocco = _un_compte_bien_rempli(conn)
    avant = _tout_ce_qui_appartient_a(conn, rocco.compte_id)
    with pytest.raises(comptes.MotDePasseIncorrect):
        comptes.effacer(conn, comptes.authentifier(conn, rocco.jeton), donnees)
    assert _tout_ce_qui_appartient_a(conn, rocco.compte_id) == avant


def test_un_mot_de_passe_faux_a_l_effacement_est_un_403_et_pas_un_401():
    """⚠️ Un 401 efface le cookie (`_non_autorise`) : une faute de frappe delierait l'appareil."""
    assert comptes.MotDePasseIncorrect.statut == 403
    assert not issubclass(comptes.MotDePasseIncorrect, comptes.NonAutorise)


def test_effacer_un_compte_deja_parti_n_est_plus_une_session(conn):
    """Deux appareils l'effacent ensemble : le second arrive apres, sur un compte qui n'existe plus."""
    rocco = _inscrire(conn)
    session = comptes.authentifier(conn, rocco.jeton)
    comptes.effacer(conn, session, {"mot_de_passe": MDP})
    with pytest.raises(comptes.NonAutorise):
        comptes.effacer(conn, session, {"mot_de_passe": MDP})


# --- Par HTTP --------------------------------------------------------------------------


def _cookie(client):
    return client.get_cookie(comptes.COOKIE, path=comptes.CHEMIN_COOKIE)


def test_par_http_s_inscrire_ouvrir_sauver_et_retrouver(client):
    assert client.post("/api/compte/ouvrir").get_json() == {"compte": None}

    inscrit = client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    assert inscrit.status_code == 201
    assert [c["emplacement"] for c in inscrit.get_json()["compte"]["parties"]] == [1, 2, 3]
    premier = _cookie(client).value

    ouvert = client.post("/api/compte/ouvrir")
    assert ouvert.get_json()["compte"]["pseudo"] == "Rocco"
    assert _cookie(client).value != premier  # le jeton a tourne

    ecrit = client.post("/api/compte/parties/2", json={"compteur": 4, "partie": _partie(9)})
    assert ecrit.status_code == 200 and ecrit.get_json()["compteur"] == 4
    assert client.get("/api/compte/parties/2").get_json()["partie"]["jour"] == 9

    refus = client.post("/api/compte/parties/2", json={"compteur": 4, "partie": _partie(1)})
    assert refus.status_code == 409
    assert refus.get_json()["serveur"]["partie"]["jour"] == 9

    assert client.post("/api/compte/deconnexion").get_json() == {"compte": None}
    assert _cookie(client) is None
    assert client.get("/api/compte/parties/2").status_code == 401


def test_par_http_le_nip_rend_le_jeton_que_le_cookie_porte_deja(client):
    """M14, 3e vague : `/api/compte/nip` expose le jeton EN CLAIR, une fois — de quoi le
    chiffrer localement. ⚠️ `httpOnly` bloque le JS de la page, pas le serveur : c'est le
    MEME jeton que celui du cookie, jamais un secret different."""
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    revele = client.post("/api/compte/nip").get_json()["jeton"]
    assert revele == _cookie(client).value


def test_par_http_le_nip_refuse_sans_session(client):
    assert client.post("/api/compte/nip").status_code == 401


def test_par_http_effacer_son_compte_delie_l_appareil_et_libere_le_pseudo(client):
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    client.post("/api/compte/parties/1", json={"compteur": 4, "partie": _partie(9)})

    fait = client.post("/api/compte/effacer", json={"mot_de_passe": MDP})
    assert fait.status_code == 200 and fait.get_json() == {"compte": None}
    assert _cookie(client) is None, "le cookie s'efface avec le compte"
    assert client.get("/api/compte/parties/1").status_code == 401
    assert client.post("/api/compte/ouvrir").get_json() == {"compte": None}

    # Le pseudo est libre — et la partie de l'ancien compte n'est pas revenue avec lui.
    neuf = client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    assert neuf.status_code == 201
    assert client.get("/api/compte/parties/1").get_json()["partie"] is None


def test_par_http_un_mot_de_passe_faux_a_l_effacement_laisse_l_appareil_lie(client):
    """⚠️ 403, jamais 401 : la session survit a une faute de frappe, et rien n'est efface."""
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    client.post("/api/compte/parties/1", json={"compteur": 4, "partie": _partie(9)})
    jeton = _cookie(client).value

    refus = client.post("/api/compte/effacer", json={"mot_de_passe": "un-mauvais-mot-de-passe"})
    assert refus.status_code == 403 and "rien n'a été effacé" in refus.get_json()["erreur"]
    assert _cookie(client).value == jeton, "l'appareil reste lie"
    assert client.get("/api/compte/parties/1").get_json()["partie"]["jour"] == 9


def test_par_http_effacer_sans_session_rend_401_et_sans_corps_rend_400(client):
    assert client.post("/api/compte/effacer", json={"mot_de_passe": MDP}).status_code == 401
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    assert client.post("/api/compte/effacer", data="pas du json",
                       content_type="text/plain").status_code == 400


def test_par_http_un_pseudo_pris_rend_409(client):
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    client.delete_cookie(comptes.COOKIE, path=comptes.CHEMIN_COOKIE)
    refus = client.post("/api/compte/inscription", json={"pseudo": "ROCCO", "mot_de_passe": MDP})
    assert refus.status_code == 409 and "pris" in refus.get_json()["erreur"]


def test_par_http_un_jeton_perime_coupe_et_efface_le_cookie(client):
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    vole = _cookie(client).value
    client.post("/api/compte/ouvrir")
    assert client.get("/api/compte/parties/1").status_code == 200  # le successeur a servi

    client.set_cookie(comptes.COOKIE, vole, path=comptes.CHEMIN_COOKIE)
    refus = client.get("/api/compte/parties/1")
    assert refus.status_code == 401 and refus.get_json()["coupe"] is True
    assert _cookie(client) is None


def test_par_http_le_cookie_est_httponly_lax_et_ne_part_qu_aux_appels_de_compte(client):
    reponse = client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    entete = reponse.headers["Set-Cookie"]
    for attribut in ("HttpOnly", "SameSite=Lax", "Path=/api/compte", "Max-Age=31536000"):
        assert attribut in entete
    # ⚠️ Pas Secure hors production : le telephone du salon joue en http.
    assert "Secure" not in entete
    assert reponse.headers["Cache-Control"] == "no-store"


def test_par_http_le_cookie_est_secure_en_production(tmp_path):
    class Production(ConfigTest):
        PRODUCTION = True
        SECRET_KEY = "x" * 64
        DONNEES_DIR = str(tmp_path / "donnees")

    client = create_app(Production).test_client()
    reponse = client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    assert "Secure" in reponse.headers["Set-Cookie"]


def test_par_http_une_partie_de_40_ko_monte_et_une_de_60_ko_non(client):
    """La borne du site est de 16 Ko : la route d'une partie releve la sienne."""
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    lourde = {**_partie(), "journal": ["x" * 100] * 400}  # ~41 Ko
    assert client.post("/api/compte/parties/1", json={"compteur": 1, "partie": lourde}).status_code == 200
    trop = {**_partie(), "journal": ["x" * 100] * 600}  # ~61 Ko
    assert client.post("/api/compte/parties/1", json={"compteur": 2, "partie": trop}).status_code == 413
    # Et le reste du site garde sa borne.
    assert client.post("/api/compte/connexion", data="x" * 20_000,
                       content_type="application/json").status_code == 413


def test_par_http_emplacement_hors_des_cases_rend_404(client):
    client.post("/api/compte/inscription", json={"pseudo": "Rocco", "mot_de_passe": MDP})
    assert client.post("/api/compte/parties/4", json={"compteur": 1, "partie": {}}).status_code == 404
    assert client.get("/api/compte/parties/0").status_code == 404


# --- Le jeu sans la base ---------------------------------------------------------------


def test_le_jeu_demarre_et_se_joue_avec_la_base_eteinte(tmp_path):
    """⚠️ Un compte est un confort, jamais une condition : un dossier de donnees
    illisible coupe les comptes (503, en JSON), pas la page ni la ville."""
    bloque = tmp_path / "pas-un-dossier"
    bloque.write_text("un fichier la ou le dossier devrait etre")

    class SansBase(ConfigTest):
        DONNEES_DIR = str(bloque)

    client = create_app(SansBase).test_client()
    for chemin in ("/", "/api/definitions", "/api/carte", "/sante"):
        assert client.get(chemin).status_code == 200, chemin
    client.set_cookie(comptes.COOKIE, "x" * 43, path=comptes.CHEMIN_COOKIE)
    for chemin in ("/api/compte/ouvrir", "/api/compte/inscription"):
        reponse = client.post(chemin, json={"pseudo": "Rocco", "mot_de_passe": MDP})
        assert reponse.status_code == 503 and "indisponibles" in reponse.get_json()["erreur"]


def test_la_page_et_les_definitions_n_ouvrent_jamais_la_base(app, client):
    for chemin in ("/", "/api/definitions", "/api/carte", "/travailleur.js", "/sante"):
        client.get(chemin)
    assert not os.path.exists(os.path.join(app.config["DONNEES_DIR"], bd.FICHIER))


# --- La cle de developpement -----------------------------------------------------------


@pytest.mark.parametrize("cle", ["cle-de-developpement-a-changer", "change-cette-cle", "", "courte"])
def test_l_application_refuse_de_demarrer_en_production_avec_la_cle_de_developpement(tmp_path, cle):
    class Production(ConfigTest):
        PRODUCTION = True
        SECRET_KEY = cle
        DONNEES_DIR = str(tmp_path)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(Production)


def test_hors_production_la_cle_de_developpement_demarre(tmp_path):
    class Salon(ConfigTest):
        PRODUCTION = False
        SECRET_KEY = "cle-de-developpement-a-changer"
        DONNEES_DIR = str(tmp_path)

    assert create_app(Salon).test_client().get("/sante").status_code == 200


@pytest.mark.parametrize("url, production", [
    ("https://bandini.gestiondojo.ca", True),
    ("http://127.0.0.1:5400", False),
    ("http://192.168.1.20:5400", False),
])
def test_la_production_se_reconnait_a_son_https(url, production):
    """Dans un processus neuf : la config se lit a l'import."""
    env = {**os.environ, "APP_BASE_URL": url}
    sortie = subprocess.run(
        [sys.executable, "-c", "import config; print(config.Config.PRODUCTION)"],
        cwd=RACINE, env=env, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert sortie == str(production)
