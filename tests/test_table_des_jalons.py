"""La table des jalons — six colonnes, et un juge qui le tient.

Le detecteur vit dans `scripts/verifier_table_des_jalons.py`. Le premier juge lit
le VRAI plan ; les autres jugent le detecteur lui-meme sur un plan d'essai, parce
qu'un juge qui passe parce que le detecteur ne detecte rien serait pire qu'aucun.

Ce qui l'a fait naitre : la table a ete divisee en `Jalon | Etat | Date | Prio |
Genre | Notes` le 14 sept. 2026, et une session qui n'avait pas vu passer le
changement a rajoute sa ligne dans l'ancienne forme a trois colonnes. Markdown
ne s'en plaint pas — il avale la ligne et la rend de travers.
"""

import importlib.util
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "scripts" / "verifier_table_des_jalons.py"


def _charger():
    spec = importlib.util.spec_from_file_location("verifier_table_des_jalons", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


juges = _charger()


def _plan_d_essai(*lignes: str) -> str:
    return "\n".join(
        [
            "# Plan",
            "",
            "## État des jalons",
            "",
            "Un paragraphe de légende.",
            "",
            juges.ENTETE,
            "|---|---|---|---|---|---|",
            *lignes,
            "",
            "## Dettes",
            "",
        ]
    )


BONNE = "| M9 Le parc | ✅ **livré** | 13 sept. 2026 | **P1** | ajout | ce qu'il y a dedans |"


# --- le vrai plan ---------------------------------------------------------


def test_le_vrai_plan_tient_sa_division():
    corps = (RACINE / "docs" / "plan.md").read_text(encoding="utf-8")
    assert juges.juger(corps) == []


def test_le_vrai_plan_a_des_lignes_a_juger():
    """Sinon le juge ci-dessus passerait sur une table vide."""
    corps = (RACINE / "docs" / "plan.md").read_text(encoding="utf-8")
    lignes = juges.table(corps)
    assert len(lignes) > 80, f"{len(lignes)} lignes : la table a fondu"


# --- le detecteur, sur un plan d'essai ------------------------------------


def test_une_ligne_bien_formee_ne_reproche_rien():
    assert juges.juger(_plan_d_essai(BONNE)) == []


def test_l_ancienne_forme_a_trois_colonnes_est_attrapee():
    """Le cas qui a coute la division : l'etat, la date, la prio et le genre en un."""
    vieille = (
        "| Un poteau par coin | **P2** **correctif**, ⬜ **en cours** (14 sept. 2026) | les notes |"
    )
    reproches = juges.juger(_plan_d_essai(BONNE, vieille))
    assert len(reproches) == 1
    assert "3 colonnes" in reproches[0]
    assert "Un poteau par coin" in reproches[0]


def test_une_colonne_de_trop_est_attrapee():
    trop = "| M9 | ✅ **livré** | 13 sept. 2026 | **P1** | ajout | notes | de trop |"
    reproches = juges.juger(_plan_d_essai(trop))
    assert len(reproches) == 1
    assert "7 colonnes" in reproches[0]


def test_la_date_restee_collee_dans_l_etat_est_attrapee():
    """Une ligne peut mériter deux reproches ; celui-là doit y être."""
    collee = "| M11 | ✅ **livré** (14 sept. 2026) | 14 sept. 2026 | **P4** | ajout | notes |"
    reproches = juges.juger(_plan_d_essai(collee))
    assert len(reproches) == 1
    assert "garde sa date dans l'état" in reproches[0]


def test_un_etat_qui_ne_commence_pas_par_l_etat_est_attrape_deux_fois():
    """« **1re vague livrée** (14 sept.) » : l'état n'est pas lisible, et la date traîne."""
    collee = (
        "| M11 | ✅ **1re vague livrée** (14 sept. 2026) | 14 sept. 2026 | **P4** | ajout | notes |"
    )
    reproches = juges.juger(_plan_d_essai(collee))
    assert len(reproches) == 2
    assert any("Les états connus" in r for r in reproches)
    assert any("garde sa date dans l'état" in r for r in reproches)


def test_un_etat_sans_son_icone_est_attrape():
    nue = "| M9 | **livré** | 13 sept. 2026 | **P1** | ajout | notes |"
    reproches = juges.juger(_plan_d_essai(nue))
    assert len(reproches) == 1
    assert "sans son icône" in reproches[0]
    assert "✅ **livré**" in reproches[0]


def test_le_message_nomme_l_etat_tel_qu_il_est_ecrit():
    nue = "| **v1 complète** | **livrée** | 13 sept. 2026 | — | — | notes |"
    reproches = juges.juger(_plan_d_essai(nue))
    assert len(reproches) == 1
    assert "✅ **livrée**" in reproches[0]


def test_une_icone_qui_ment_est_attrapee():
    """Le crochet sur une ligne en cours, la case vide sur une ligne livrée."""
    for ligne, attendue in (
        ("| M16 | ✅ **en cours** | 17 sept. 2026 | **P4** | ajout | notes |", "⬜ **en cours**"),
        (
            "| M9 | ⬜ **livré** (1re vague) | 13 sept. 2026 | **P1** | ajout | notes |",
            "✅ **livré**",
        ),
    ):
        reproches = juges.juger(_plan_d_essai(ligne))
        assert len(reproches) == 1, ligne
        assert "mauvaise icône" in reproches[0]
        assert attendue in reproches[0]


def test_la_case_vide_va_devant_tout_ce_qui_n_est_pas_livre():
    a_faire = "| M13 | ⬜ **à faire** | — | **P4** | ajout | notes |"
    en_cours = (
        "| M12 | ⬜ **en cours** (huit vagues livrées) | 15 sept. 2026 | **P4** | ajout | notes |"
    )
    livree = "| **v1 complète** | ✅ **livrée** | 13 sept. 2026 | — | — | notes |"
    assert juges.juger(_plan_d_essai(a_faire, en_cours, livree)) == []


def test_un_etat_inconnu_est_attrape():
    inconnu = "| M9 | ⬜ **peut-être** | 13 sept. 2026 | **P1** | ajout | notes |"
    reproches = juges.juger(_plan_d_essai(inconnu))
    assert len(reproches) == 1
    assert "état" in reproches[0]


def test_une_date_mal_ecrite_est_attrapee():
    mauvaise = "| M9 | ✅ **livré** | 2026-09-13 | **P1** | ajout | notes |"
    reproches = juges.juger(_plan_d_essai(mauvaise))
    assert len(reproches) == 1
    assert "date" in reproches[0]


def test_le_tiret_est_une_date_une_prio_et_un_genre_valables():
    vide = "| M13 Les deux fins | ⬜ **à faire** | — | — | — | notes |"
    assert juges.juger(_plan_d_essai(vide)) == []


def test_une_prio_hors_echelle_est_attrapee():
    hors = "| M9 | ✅ **livré** | 13 sept. 2026 | **P5** | ajout | notes |"
    reproches = juges.juger(_plan_d_essai(hors))
    assert len(reproches) == 1
    assert "prio" in reproches[0]


def test_un_genre_invente_est_attrape():
    invente = "| M9 | ✅ **livré** | 13 sept. 2026 | **P1** | amélioration | notes |"
    reproches = juges.juger(_plan_d_essai(invente))
    assert len(reproches) == 1
    assert "genre" in reproches[0]


def test_un_entete_change_est_attrape():
    corps = _plan_d_essai(BONNE).replace(juges.ENTETE, "| Jalon | État | Notes |")
    reproches = juges.juger(corps)
    assert any("l'en-tête de la table a changé" in r for r in reproches)


def test_une_table_absente_est_attrapee():
    assert juges.juger("# Plan\n\n## Dettes\n") != []


def test_la_table_s_arrete_a_la_premiere_ligne_qui_n_est_pas_une_ligne():
    """Les autres tables du plan (les dettes, l'architecture) ne sont pas jugées."""
    corps = _plan_d_essai(BONNE) + "\n| Dette | Pourquoi | Déclencheur |\n|---|---|---|\n"
    assert juges.juger(corps) == []
