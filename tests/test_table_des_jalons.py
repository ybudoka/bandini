"""Les tables des jalons — six colonnes, deux fichiers, et un juge qui les tient.

Le detecteur vit dans `scripts/verifier_table_des_jalons.py`. Le premier juge lit
les VRAIES tables (`docs/plan.md` pour ce qui reste a faire, `docs/jalons/README.md`
pour ce qui est livre) ; les autres jugent le detecteur lui-meme sur un plan d'essai,
parce qu'un juge qui passe parce que le detecteur ne detecte rien serait pire
qu'aucun.

Ce qui l'a fait naitre : la table a ete divisee en `Jalon | Etat | Date | Prio |
Genre | Notes` le 14 sept. 2026, et une session qui n'avait pas vu passer le
changement a rajoute sa ligne dans l'ancienne forme a trois colonnes. Markdown
ne s'en plaint pas — il avale la ligne et la rend de travers.

Le plan a ete fragmente le 20 sept. 2026 : il ne garde que ce qui reste a faire, et
chaque jalon livre a son fichier dans `docs/jalons/`. Le detecteur juge donc aussi
que chaque ligne est dans SA table, et que ses liens mènent quelque part.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "scripts" / "verifier_table_des_jalons.py"


def _charger():
    spec = importlib.util.spec_from_file_location("verifier_table_des_jalons", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


juges = _charger()
PLAN, LIVRES = juges.PLAN, juges.LIVRES


def _doc(fichier: str, *lignes: str) -> str:
    """Un fichier minimal. Une cellule Notes qui vaut « notes » devient le lien vers sa fiche."""
    titre = juges.TABLES[fichier][0]
    rangees, fiches = [], []
    for ligne in lignes:
        cols = juges.cellules(ligne)
        if cols and cols[-1] == "notes":
            coupe = ligne.rstrip().rstrip("|").rstrip()
            ligne = f"{coupe[: -len('notes')]}[fiche](#{juges.ancre(cols[0])}) |"
            fiches += [f"### {cols[0]}", "", "ce qu'il y a dedans", ""]
        rangees.append(ligne)
    return "\n".join(
        [
            "# Doc",
            "",
            titre,
            "",
            "Un paragraphe de légende.",
            "",
            juges.ENTETE,
            "|---|---|---|---|---|---|",
            *rangees,
            "",
            "## Dettes",
            "",
            "## Les fiches",
            "",
            *fiches,
        ]
    )


def _juge(*lignes: str, fichier: str = PLAN, lire=None) -> list[str]:
    return juges.juger(_doc(fichier, *lignes), fichier, lire)


BONNE = "| M9 Le parc | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | notes |"
LIVREE = "| M9 Le parc | ✅ **livré** | 13 sept. 2026 | **P1** | ajout | notes |"


# --- les vraies tables ------------------------------------------------------


def test_les_vraies_tables_tiennent_leur_forme():
    lire = juges._lecteur_disque(RACINE)
    fichiers = {f: lire(f) for f in juges.TABLES}
    assert all(c is not None for c in fichiers.values()), "une des deux tables manque"
    assert juges.juger_tout(fichiers, lire) == []


def test_les_jalons_livres_ont_des_lignes_a_juger():
    """Sinon le juge ci-dessus passerait sur une table vide."""
    corps = (RACINE / LIVRES).read_text(encoding="utf-8")
    lignes = juges.table(corps, juges.TABLES[LIVRES][0])
    assert len(lignes) > 80, f"{len(lignes)} lignes : la table des jalons livrés a fondu"


def test_le_plan_a_sa_table_meme_quand_il_ne_reste_plus_rien_a_faire():
    """L'en-tête et le séparateur suffisent : une table vide est une bonne nouvelle, pas une absence."""
    corps = (RACINE / PLAN).read_text(encoding="utf-8")
    assert len(juges.table(corps, juges.TABLES[PLAN][0])) >= 2


# --- le detecteur, sur un fichier d'essai -------------------------------------


def test_une_ligne_bien_formee_ne_reproche_rien():
    assert _juge(BONNE) == []
    assert _juge(LIVREE, fichier=LIVRES) == []


def test_l_ancienne_forme_a_trois_colonnes_est_attrapee():
    """Le cas qui a coute la division : l'etat, la date, la prio et le genre en un."""
    vieille = (
        "| Un poteau par coin | **P2** **correctif**, ⬜ **en cours** (14 sept. 2026) | les notes |"
    )
    reproches = _juge(BONNE, vieille)
    assert len(reproches) == 1
    assert "3 colonnes" in reproches[0]
    assert "Un poteau par coin" in reproches[0]


def test_une_colonne_de_trop_est_attrapee():
    trop = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | notes | de trop |"
    reproches = _juge(trop)
    assert len(reproches) == 1
    assert "7 colonnes" in reproches[0]


def test_la_date_restee_collee_dans_l_etat_est_attrapee():
    """Une ligne peut mériter deux reproches ; celui-là doit y être."""
    collee = "| M11 | ⬜ **en cours** (14 sept. 2026) | 14 sept. 2026 | **P4** | ajout | notes |"
    reproches = _juge(collee)
    assert len(reproches) == 1
    assert "garde sa date dans l'état" in reproches[0]


def test_un_etat_qui_ne_commence_pas_par_l_etat_est_attrape_deux_fois():
    """« **1re vague livrée** (14 sept.) » : l'état n'est pas lisible, et la date traîne."""
    collee = (
        "| M11 | ✅ **1re vague livrée** (14 sept. 2026) | 14 sept. 2026 | **P4** | ajout | notes |"
    )
    reproches = _juge(collee, fichier=LIVRES)
    assert len(reproches) == 2
    assert any("Les états connus" in r for r in reproches)
    assert any("garde sa date dans l'état" in r for r in reproches)


def test_un_etat_sans_son_icone_est_attrape():
    nue = "| M9 | **en cours** | 13 sept. 2026 | **P1** | ajout | notes |"
    reproches = _juge(nue)
    assert len(reproches) == 1
    assert "sans son icône" in reproches[0]
    assert "⬜ **en cours**" in reproches[0]


def test_le_message_nomme_l_etat_tel_qu_il_est_ecrit():
    nue = "| **v1 complète** | **livrée** | 13 sept. 2026 | — | — | notes |"
    reproches = _juge(nue, fichier=LIVRES)
    assert len(reproches) == 1
    assert "✅ **livrée**" in reproches[0]


def test_une_icone_qui_ment_est_attrapee():
    """Le crochet sur une ligne en cours, la case vide sur une ligne livrée."""
    for fichier, ligne, attendue in (
        (PLAN, "| M16 | ✅ **en cours** | 17 sept. 2026 | **P4** | ajout | notes |", "⬜ **en cours**"),
        (
            LIVRES,
            "| M9 | ⬜ **livré** (1re vague) | 13 sept. 2026 | **P1** | ajout | notes |",
            "✅ **livré**",
        ),
    ):
        reproches = _juge(ligne, fichier=fichier)
        assert len(reproches) == 1, ligne
        assert "mauvaise icône" in reproches[0]
        assert attendue in reproches[0]


def test_la_case_vide_va_devant_tout_ce_qui_n_est_pas_livre():
    a_faire = "| M13 | ⬜ **à faire** | — | **P4** | ajout | notes |"
    en_cours = (
        "| M12 | ⬜ **en cours** (huit vagues livrées) | 15 sept. 2026 | **P4** | ajout | notes |"
    )
    livree = "| **v1 complète** | ✅ **livrée** | 13 sept. 2026 | — | — | notes |"
    assert _juge(a_faire, en_cours) == []
    assert _juge(livree, fichier=LIVRES) == []


def test_un_etat_inconnu_est_attrape():
    inconnu = "| M9 | ⬜ **peut-être** | 13 sept. 2026 | **P1** | ajout | notes |"
    reproches = _juge(inconnu)
    assert len(reproches) == 1
    assert "état" in reproches[0]


def test_une_date_mal_ecrite_est_attrapee():
    mauvaise = "| M9 | ⬜ **en cours** | 2026-09-13 | **P1** | ajout | notes |"
    reproches = _juge(mauvaise)
    assert len(reproches) == 1
    assert "date" in reproches[0]


def test_le_tiret_est_une_date_une_prio_et_un_genre_valables():
    vide = "| M13 Les deux fins | ⬜ **à faire** | — | — | — | notes |"
    assert _juge(vide) == []


def test_une_prio_hors_echelle_est_attrapee():
    hors = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P5** | ajout | notes |"
    reproches = _juge(hors)
    assert len(reproches) == 1
    assert "prio" in reproches[0]


def test_un_genre_invente_est_attrape():
    invente = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | amélioration | notes |"
    reproches = _juge(invente)
    assert len(reproches) == 1
    assert "genre" in reproches[0]


def test_un_entete_change_est_attrape():
    corps = _doc(PLAN, BONNE).replace(juges.ENTETE, "| Jalon | État | Notes |")
    reproches = juges.juger(corps, PLAN)
    assert any("l'en-tête de la table a changé" in r for r in reproches)


def test_une_table_absente_est_attrapee():
    assert juges.juger("# Plan\n\n## Dettes\n", PLAN) != []
    assert juges.juger("# Jalons\n", LIVRES) != []


def test_la_table_s_arrete_a_la_premiere_ligne_qui_n_est_pas_une_ligne():
    """Les autres tables du fichier (les dettes, l'ordre) ne sont pas jugées."""
    corps = _doc(PLAN, BONNE) + "\n| Dette | Pourquoi | Déclencheur |\n|---|---|---|\n"
    assert juges.juger(corps, PLAN) == []


# --- une ligne dans SA table ----------------------------------------------------


def test_une_ligne_livree_restee_dans_le_plan_est_attrapee():
    """Livrer une ligne, c'est la faire passer du plan aux jalons livrés."""
    reproches = _juge(LIVREE)
    assert len(reproches) == 1
    assert "M9 Le parc" in reproches[0]
    assert "jalons/README.md" in reproches[0]


def test_une_ligne_a_faire_passee_dans_les_jalons_livres_est_attrapee():
    reproches = _juge(BONNE, fichier=LIVRES)
    assert len(reproches) == 1
    assert "docs/plan.md" in reproches[0]


def test_un_jalon_dans_les_deux_tables_est_attrape():
    fichiers = {PLAN: _doc(PLAN, BONNE), LIVRES: _doc(LIVRES, LIVREE)}
    reproches = [r for r in juges.juger_tout(fichiers) if "ET dans" in r]
    assert len(reproches) == 1
    assert "M9 Le parc" in reproches[0]


def test_deux_jalons_de_noms_differents_ne_se_gênent_pas():
    autre = "| M10 L'argent | ✅ **livré** | 13 sept. 2026 | **P4** | ajout | notes |"
    fichiers = {PLAN: _doc(PLAN, BONNE), LIVRES: _doc(LIVRES, autre)}
    assert juges.juger_tout(fichiers) == []


# --- les notes : des liens dans la table, le detail dans un fichier --------------

NOTE_LONGUE = (
    "demande de Martin (« des feux qu'on voit ») : il n'y en avait pas. Le poteau est posé. "
    "⚠️ **Un poteau par coin** : quatre, c'était une forêt. "
    "⚠️ Et le dessin suit le feu — (⚠️ jamais l'inverse) — **3.** ⚠️ **Le troisième point** tient. "
    "✅ **2e vague livrée** (15 sept. 2026) — *le clignotant*. La nuit, ça clignote. "
    "⚠️ **Mesuré** : 0,2 ms. 3 juges ; 1611 tests."
)


def _normaliser(texte: str) -> str:
    return " ".join(texte.split())


def _lecteur(fichiers: dict[str, str]):
    return lambda chemin: fichiers.get(chemin)


def test_une_note_restee_dans_la_table_est_attrapee():
    """Le cas qui a fait naitre la regle : 22 000 caracteres sur une ligne de table."""
    longue = f"| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |"
    reproches = _juge(longue)
    assert len(reproches) == 1
    assert "garde ses notes dans la table" in reproches[0]
    assert "--ranger" in reproches[0]


def test_un_lien_qui_ne_mene_nulle_part_est_attrape():
    perdu = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | [fiche](#m-neuf) |"
    reproches = _juge(perdu)
    assert len(reproches) == 1
    assert "#m-neuf" in reproches[0]


def test_un_lien_vers_un_titre_du_fichier_tient():
    """N'importe quel titre du fichier est une ancre : la fiche d'une ligne est un titre ### ordinaire."""
    ailleurs = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | [fiche](#dettes) |"
    assert _juge(ailleurs) == []


def test_un_lien_vers_un_fichier_de_jalon_qui_existe_tient():
    ligne = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | [notes](jalons/m9.md) |"
    lire = _lecteur({"docs/jalons/m9.md": "# M9\n"})
    assert _juge(ligne, lire=lire) == []


def test_un_lien_vers_un_fichier_qui_n_existe_pas_est_attrape():
    ligne = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | [notes](jalons/m9.md) |"
    reproches = _juge(ligne, lire=_lecteur({}))
    assert len(reproches) == 1
    assert "docs/jalons/m9.md n'existe pas" in reproches[0]


def test_les_liens_des_jalons_livres_se_lisent_depuis_leur_dossier():
    ligne = "| M9 | ✅ **livré** | 13 sept. 2026 | **P1** | ajout | [notes](m9.md) |"
    assert _juge(ligne, fichier=LIVRES, lire=_lecteur({"docs/jalons/m9.md": "# M9\n"})) == []
    reproches = _juge(ligne, fichier=LIVRES, lire=_lecteur({"docs/m9.md": "# M9\n"}))
    assert len(reproches) == 1
    assert "docs/jalons/m9.md n'existe pas" in reproches[0]


def test_une_ancre_dans_un_autre_fichier_doit_y_etre():
    ligne = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | [notes](jalons/m9.md#notes) |"
    assert _juge(ligne, lire=_lecteur({"docs/jalons/m9.md": "# M9\n\n## Notes\n"})) == []
    reproches = _juge(ligne, lire=_lecteur({"docs/jalons/m9.md": "# M9\n"}))
    assert len(reproches) == 1
    assert "#notes" in reproches[0]


def test_une_fiche_et_des_notes_ensemble_tiennent():
    ligne = (
        "| M9 Le parc | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | "
        "[fiche](#m9-le-parc) · [notes](jalons/m9.md) |"
    )
    corps = _doc(PLAN, ligne) + "\n### M9 Le parc\n"
    assert juges.juger(corps, PLAN, _lecteur({"docs/jalons/m9.md": "# M9\n"})) == []


def test_la_fiche_et_les_notes_se_lisent_dans_le_fichier_du_jalon():
    """La forme du plan : [fiche](jalons/x.md#fiche) · [notes](jalons/x.md#notes)."""
    ligne = (
        "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | "
        "[fiche](jalons/m9.md#fiche) · [notes](jalons/m9.md#notes) |"
    )
    complet = "# M9\n\n## Fiche\n\nle plan\n\n## Notes\n\nle livré\n"
    assert _juge(ligne, lire=_lecteur({"docs/jalons/m9.md": complet})) == []
    sans_notes = "# M9\n\n## Fiche\n\nle plan\n"
    reproches = _juge(ligne, lire=_lecteur({"docs/jalons/m9.md": sans_notes}))
    assert len(reproches) == 1
    assert "#notes" in reproches[0]


def test_du_texte_autour_des_liens_est_attrape():
    ligne = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | voir [fiche](#dettes) |"
    reproches = _juge(ligne)
    assert len(reproches) == 1
    assert "garde ses notes dans la table" in reproches[0]


def test_l_ancre_est_celle_de_github():
    assert juges.ancre("Le char abrite, l'appel fige") == "le-char-abrite-lappel-fige"
    assert juges.ancre("La fourrière : remorquage") == "la-fourrière--remorquage"
    assert (
        juges.ancre("L'Île-aux-Corneilles — deuxième vague")
        == "lîle-aux-corneilles--deuxième-vague"
    )
    assert juges.ancre("**v1 complète**") == "v1-complète"
    assert juges.ancre("Se réveiller dans un lit d’hôpital") == "se-réveiller-dans-un-lit-dhôpital"


def test_deux_titres_pareils_ont_deux_ancres():
    lignes = ["# Plan", "## Le métro", "```", "## Le métro", "```", "### Le métro"]
    assert [nom for *_, nom in juges.titres(lignes)] == ["plan", "le-métro", "le-métro-1"]


def test_le_nom_de_fichier_d_un_jalon():
    assert juges.slug("Le char abrite, l'appel fige") == "le-char-abrite-l-appel-fige"
    assert juges.slug("« Mal garé » veut enfin dire quelque chose") == "mal-gare-veut-enfin-dire-quelque-chose"
    assert juges.slug("**v1 complète**") == "v1-complete"
    assert len(juges.slug("un " * 60)) <= 72


# --- ranger : la note de la cellule devient le fichier du jalon -------------------


def test_ranger_ecrit_le_fichier_du_jalon_et_pose_le_lien():
    corps = _doc(PLAN, f"| M9 Le parc | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |")
    range_, ecrits = juges.ranger(PLAN, corps, _lecteur({}))
    assert list(ecrits) == ["docs/jalons/m9-le-parc.md"]
    assert "| [fiche](jalons/m9-le-parc.md#fiche) |" in range_
    assert ecrits["docs/jalons/m9-le-parc.md"].startswith("# M9 Le parc\n")
    assert "\n## Fiche\n" in ecrits["docs/jalons/m9-le-parc.md"]
    fichiers = {"docs/jalons/m9-le-parc.md": ecrits["docs/jalons/m9-le-parc.md"]}
    assert juges.juger(range_, PLAN, _lecteur(fichiers)) == []


def test_ranger_dans_les_jalons_livres_pose_un_lien_court():
    corps = _doc(LIVRES, f"| M9 Le parc | ✅ **livré** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |")
    range_, ecrits = juges.ranger(LIVRES, corps, _lecteur({}))
    assert "| [notes](m9-le-parc.md#notes) |" in range_
    assert list(ecrits) == ["docs/jalons/m9-le-parc.md"]
    assert "\n## Notes\n" in ecrits["docs/jalons/m9-le-parc.md"]


def test_ranger_ne_perd_pas_un_mot():
    corps = _doc(PLAN, f"| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |")
    _, ecrits = juges.ranger(PLAN, corps, _lecteur({}))
    lignes = ecrits["docs/jalons/m9.md"].split("\n")
    depart = lignes.index("## Fiche") + 1
    dedans = [x[2:] if x.startswith("- ") else x for x in lignes[depart:]]
    assert _normaliser(" ".join(dedans)) == _normaliser(NOTE_LONGUE)


def test_ranger_se_rejoue_sans_rien_changer():
    corps = _doc(
        PLAN,
        f"| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |",
        "| M10 | ⬜ **à faire** | — | **P3** | ajout | notes |",
    )
    une_fois, ecrits = juges.ranger(PLAN, corps, _lecteur({}))
    deux_fois, encore = juges.ranger(PLAN, une_fois, _lecteur(ecrits))
    assert deux_fois == une_fois
    assert encore == {}


def test_ranger_ne_ecrase_pas_le_fichier_d_un_autre_jalon():
    corps = _doc(PLAN, f"| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |")
    _, ecrits = juges.ranger(PLAN, corps, _lecteur({"docs/jalons/m9.md": "# un autre M9\n"}))
    assert list(ecrits) == ["docs/jalons/m9-2.md"]


def test_ranger_laisse_une_cellule_vide_au_juge():
    vide = "| M9 | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout |  |"
    corps = _doc(PLAN, vide)
    range_, ecrits = juges.ranger(PLAN, corps, _lecteur({}))
    assert range_ == corps
    assert ecrits == {}
    assert _juge(vide)


def test_une_puce_par_alerte_qui_ouvre_une_phrase():
    lignes = juges.mettre_en_forme(NOTE_LONGUE)
    puces = [x for x in lignes if x.startswith("- ")]
    assert puces[0].startswith("- ⚠️ **Un poteau par coin**")
    assert puces[1].startswith("- ⚠️ Et le dessin suit le feu")
    # au milieu d'une phrase (« — (⚠️ ») ou apres « **3.** », le ⚠️ ne coupe pas
    assert len(puces) == 3
    assert any("**3.** ⚠️ **Le troisième point**" in x for x in lignes)


def test_une_vague_ouvre_un_paragraphe():
    lignes = juges.mettre_en_forme(NOTE_LONGUE)
    assert any(x.startswith("✅ **2e vague livrée** (15 sept. 2026)") for x in lignes)
    vague = next(i for i, x in enumerate(lignes) if x.startswith("✅ **2e vague"))
    assert lignes[vague - 1] == ""


def test_une_ligne_repliee_ne_devient_jamais_une_liste_ni_un_titre():
    """Replier au mauvais endroit ferait une puce d'un tiret, ou un titre d'un dièse."""
    for piege in ("- suite", "1. suite", "# suite", "> suite"):
        texte = "a" * (juges.LARGEUR - 1) + " " + piege + " " + "b " * 60
        for premier, suivants in (("", ""), ("- ", "  ")):
            lignes = juges._envelopper(texte, premier, suivants)
            for ligne in lignes[1:]:
                assert not juges.DANGER.match(ligne[len(suivants) :]), (piege, ligne)
            assert _normaliser(
                " ".join(x[len(premier) :] if i == 0 else x for i, x in enumerate(lignes))
            ) == _normaliser(texte)


# --- la ligne de commande -----------------------------------------------------


def _depot_d_essai(tmp_path: Path, plan: str, livres: str) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "docs" / "jalons").mkdir(parents=True)
    (tmp_path / PLAN).write_text(plan, encoding="utf-8")
    (tmp_path / LIVRES).write_text(livres, encoding="utf-8")
    return tmp_path


def _lancer(depot: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--cwd", str(depot), *args], capture_output=True, text=True
    )


def test_la_ligne_de_commande_range_puis_juge(tmp_path):
    plan = _doc(PLAN, f"| M9 Le parc | ⬜ **en cours** | 13 sept. 2026 | **P1** | ajout | {NOTE_LONGUE} |")
    depot = _depot_d_essai(tmp_path, plan, _doc(LIVRES))
    assert _lancer(depot).returncode == 1  # la note est encore dans la cellule
    sortie = _lancer(depot, "--ranger")
    assert sortie.returncode == 0, sortie.stderr
    assert (depot / "docs" / "jalons" / "m9-le-parc.md").is_file()
    assert "[fiche](jalons/m9-le-parc.md#fiche)" in (depot / PLAN).read_text(encoding="utf-8")
    assert _lancer(depot).returncode == 0


def test_la_ligne_de_commande_attrape_une_ligne_dans_la_mauvaise_table(tmp_path):
    depot = _depot_d_essai(tmp_path, _doc(PLAN, LIVREE), _doc(LIVRES))
    sortie = _lancer(depot)
    assert sortie.returncode == 1
    assert "jalons/README.md" in sortie.stderr


def test_la_garde_a_l_ecriture_ne_juge_que_les_tables_et_les_jalons(tmp_path):
    depot = _depot_d_essai(tmp_path, _doc(PLAN, LIVREE), _doc(LIVRES))  # le plan est faux
    (depot / "docs" / "carte.md").write_text("# Carte\n", encoding="utf-8")
    assert _lancer(depot, "--fichier", str(depot / "docs" / "carte.md")).returncode == 0
    assert _lancer(depot, "--fichier", str(depot / PLAN)).returncode == 1
    (depot / "docs" / "jalons" / "m9.md").write_text("# M9\n", encoding="utf-8")
    assert _lancer(depot, "--fichier", str(depot / "docs" / "jalons" / "m9.md")).returncode == 1
    assert _lancer(depot, "--fichier", "/tmp/ailleurs.md").returncode == 0
