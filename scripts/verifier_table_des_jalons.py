#!/usr/bin/env python3
"""Les tables des jalons — six colonnes, et personne ne les reduit a trois en passant.

Le plan ne garde que ce qui reste a faire. Deux tables, deux fichiers :

- `docs/plan.md`, section `## À faire` : les lignes ⬜ (`à faire`, `en cours`) ;
- `docs/jalons/README.md`, section `## Jalons livrés` : les lignes ✅ (`livré`, `livrée`).

Chacune est divisee en `Jalon | Etat | Date | Prio | Genre | Notes`. C'est le
tableau de bord des sessions — plusieurs Claude ecrivent dans le meme arbre, et la
table du plan est le seul endroit ou elles se voient.

Une session qui ajoute sa ligne recopie souvent la forme qu'elle a en tete, pas
celle du fichier : elle ecrit `| Mon jalon | **P2** **correctif**, **en cours**
(14 sept.) | ... |` — trois colonnes dans une table qui en compte six. Markdown
ne s'en plaint pas, il avale la ligne et la rend de travers ; la table perd sa
division sans qu'un test rougisse. Ce detecteur l'attrape.

Il juge la FORME, jamais le fond : ni l'ordre des lignes, ni les dates, ni qui a
raison sur une priorite. Ce qu'il exige :

1. six colonnes par ligne, pas une de plus, pas une de moins ;
2. un etat connu (`livré`, `livrée`, `en cours`, `à faire`), precede de son icone :
   ✅ pour ce qui est livre, ⬜ pour tout le reste ;
3. **la ligne dans sa table** : ⬜ dans le plan, ✅ dans les jalons livres — livrer
   une ligne, c'est la faire passer de l'une a l'autre ;
4. une date `JJ mois AAAA` ou `—`, et jamais une date restee collee dans l'etat ;
5. une prio `P1` a `P4` ou `—` ;
6. un genre `ajout`, `correctif` ou `—` ;
7. des notes qui ne sont que des liens (un ou deux, separes par ` · `), vers le
   fichier du jalon dans `docs/jalons/` : `[fiche](jalons/x.md#fiche)` pour ce qui
   est prevu, `[notes](jalons/x.md#notes)` pour ce qui est livre. Le fichier (et
   l'ancre, s'il y en a une) doit exister ;
8. un jalon dans une seule des deux tables.

La 7e regle date du 17 sept. 2026 (les notes vivaient dans la cellule, et une ligne
de table ne se replie pas : la plus longue faisait 22 000 caracteres). Depuis le
20 sept. 2026 le plan est fragmente : les notes vivent chacune dans son fichier.
`--ranger` fait le travail : il sort chaque note restee dans sa cellule, la met en
forme (un paragraphe, une puce par ⚠️, une vague par paragraphe, replie a 92
colonnes), l'ecrit dans `docs/jalons/<jalon>.md` — sous « Fiche » pour une ligne du
plan (ce qui est prevu), sous « Notes » pour une ligne livree — et pose le lien. On peut donc
continuer d'ecrire la note dans la cellule, et ranger avant de committer.

Appele de quatre facons, comme son voisin `verifier_carte_du_depot.py` :

    python scripts/verifier_table_des_jalons.py              # les deux tables
    python scripts/verifier_table_des_jalons.py --fichier F  # ne dit rien si F n'est pas une des deux, ni un jalon
    python scripts/verifier_table_des_jalons.py --commit     # ce qui part au commit
    python scripts/verifier_table_des_jalons.py --ranger     # sort les notes des tables, puis juge
"""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
import textwrap
import unicodedata
from collections.abc import Callable
from pathlib import Path

PLAN = "docs/plan.md"
LIVRES = "docs/jalons/README.md"
DOSSIER_JALONS = "docs/jalons"
ENTETE = "| Jalon | État | Date | Prio | Genre | Notes |"

COLONNES = 6

ETATS = ("livré", "livrée", "en cours", "à faire")
# L'icone devant l'etat (demande de Martin, 17 sept. 2026) : un crochet pour ce qui
# est livre, une case vide pour le reste — la colonne se lit d'un coup d'oeil.
ICONE_LIVRE = "✅"
ICONE_AUTRE = "⬜"
#: fichier -> (titre de la section, icone de ses lignes, comment on le nomme). Une ligne
#: livree va dans les jalons livres, tout le reste reste dans le plan.
TABLES = {
    PLAN: ("## À faire", ICONE_AUTRE, "le plan"),
    LIVRES: ("## Jalons livrés", ICONE_LIVRE, "les jalons livrés"),
}
MOIS = (
    "janv.",
    "févr.",
    "mars",
    "avril",
    "mai",
    "juin",
    "juill.",
    "août",
    "sept.",
    "oct.",
    "nov.",
    "déc.",
)
DATE = re.compile(r"^\d{1,2} (?:" + "|".join(map(re.escape, MOIS)) + r") \d{4}$")
PRIO = re.compile(r"^\*\*P[1-4]\*\*$")
GENRE = re.compile(r"^(?:ajout|\*\*correctif\*\*)$")
# une date entre parentheses, la ou elle ne devrait plus etre depuis qu'il y a
# une colonne Date : « **livré** (14 sept. 2026) »
DATE_COLLEE = re.compile(r"\(\s*\d{1,2} (?:" + "|".join(map(re.escape, MOIS)) + r")")
_LIEN = r"\[(?:notes|fiche)\]\([^)\s]+\)"
LIENS = re.compile(rf"{_LIEN}(?: · {_LIEN})*")
UN_LIEN = re.compile(r"\[(notes|fiche)\]\(([^)\s]+)\)")

# La mise en forme d'une note. Les lignes sont repliees a cette largeur.
LARGEUR = 92
ALERTE = "⚠️"
# « ✅ **2e vague livrée** (15 sept. 2026) — ... » : chaque vague ouvre un paragraphe
VAGUE = re.compile(r"\s+(?=(?:✅|🔨|⬜|⚠️) \*\*(?:\d+(?:re|e) vague|Refaite)\b)")
# des espaces ou l'on ne coupe pas la ligne : dans un bout de code, contre un
# guillemet ou une ponctuation double, et au milieu d'un nombre (« 2 507 »)
COLLE = re.compile(r"`[^`\n]*`|« | »| [:;!?%$](?=\s|$)|\d (?=\d{3}(?!\d))")
# une ligne repliee qui commencerait ainsi deviendrait une liste, un titre ou une citation
DANGER = re.compile(
    r"[-+*](?:\s|$)|[-=]+\s*$|>|#{1,6}(?:\s|$)|\d{1,9}[.)](?:\s|$)|\||`{3}|~{3}|<[A-Za-z/!?]"
)

#: Comment lire un fichier du depot : son chemin depuis la racine -> son texte, ou None s'il n'existe pas.
Lecteur = Callable[[str], "str | None"]


def _dedans(texte: str) -> str:
    """Le corps d'une cellule, sans le gras ni les espaces."""
    return texte.strip().strip("*").strip()


def _icone(etat: str) -> tuple[str | None, str]:
    """L'icone en tete de la cellule d'etat (ou None), et ce qui la suit."""
    for icone in (ICONE_LIVRE, ICONE_AUTRE):
        if etat.startswith(icone):
            return icone, etat[len(icone) :].strip()
    return None, etat


def table(corps: str, titre: str = TABLES[PLAN][0]) -> list[tuple[int, str]]:
    """Les lignes de la table qui suit `titre`, numerotees (1-based) comme dans le fichier.

    La table commence a la premiere ligne qui ouvre sur `|` et finit a la premiere
    qui ne le fait plus.
    """
    lignes = corps.split("\n")
    depart = next((i for i, x in enumerate(lignes) if x.strip() == titre), None)
    if depart is None:
        return []
    dedans = False
    trouvees = []
    for i in range(depart + 1, len(lignes)):
        ligne = lignes[i]
        if ligne.startswith("|"):
            dedans = True
            trouvees.append((i + 1, ligne))
        elif dedans:
            break
        elif ligne.startswith("## "):
            break
    return trouvees


def cellules(ligne: str) -> list[str]:
    parts = ligne.split("|")
    # `| a | b |` se coupe en ['', ' a ', ' b ', ''] : les bords ne comptent pas
    return [c.strip() for c in parts[1:-1]]


# --- les ancres ------------------------------------------------------------


def ancre(titre: str) -> str:
    """L'ancre que GitHub donne a un titre (github-slugger), avant le suffixe des doublons.

    Minuscules ; on garde les lettres (accents compris), les chiffres, `-` et `_` ;
    chaque espace devient `-`. « La fourrière : remorquage » donne donc
    `la-fourrière--remorquage` — l'espace de chaque cote du deux-points reste.
    """
    garde = []
    for c in titre.strip().lower():
        if c in " -_":
            garde.append(c)
        elif unicodedata.category(c)[0] in "LN":
            garde.append(c)
        elif unicodedata.category(c)[0] == "M" and not 0xFE00 <= ord(c) <= 0xFE0F:
            garde.append(c)
    return "".join(garde).replace(" ", "-")


def titres(lignes: list[str]) -> list[tuple[int, int, str, str]]:
    """Les titres du document : (index de ligne, niveau, texte, ancre), doublons suffixes."""
    vues: dict[str, int] = {}
    trouves = []
    dans_code = False
    for i, ligne in enumerate(lignes):
        if ligne.lstrip().startswith(("```", "~~~")):
            dans_code = not dans_code
            continue
        if dans_code:
            continue
        m = re.match(r"^(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$", ligne)
        if m is None:
            continue
        base = ancre(m.group(2))
        nom = base
        while nom in vues:
            vues[base] += 1
            nom = f"{base}-{vues[base]}"
        vues[nom] = 0
        trouves.append((i, len(m.group(1)), m.group(2), nom))
    return trouves


def ancres(corps: str) -> set[str]:
    """Les ancres de tous les titres d'un document."""
    return {nom for *_, nom in titres(corps.split("\n"))}


def slug(jalon: str) -> str:
    """Le nom de fichier d'un jalon : « Le char abrite, l'appel fige » -> `le-char-abrite-l-appel-fige`."""
    s = jalon.replace("**", "").replace("œ", "oe").replace("Œ", "oe")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > 72:
        s = s[:72].rsplit("-", 1)[0]
    return s or "jalon"


# --- le juge ---------------------------------------------------------------


def _cible(fichier: str, lien: str) -> tuple[str, str]:
    """Un lien relatif, vu depuis `fichier` : (chemin depuis la racine, ancre ou « »)."""
    chemin, _, ancre_ = lien.partition("#")
    if not chemin:
        return fichier, ancre_
    return posixpath.normpath(posixpath.join(posixpath.dirname(fichier), chemin)), ancre_


def juger(corps: str, fichier: str = PLAN, lire: Lecteur | None = None) -> list[str]:
    """Les reproches pour UNE table (celle de `fichier`), un par ligne fautive. Vide = elle tient.

    `lire` dit ce que contiennent les autres fichiers du depot (pour verifier qu'un lien
    mene quelque part) ; sans lui, seuls les liens `#ancre` du fichier sont verifies.
    """
    titre, icone_attendue, nom_du_fichier = TABLES[fichier]
    lignes = table(corps, titre)
    if not lignes:
        return [f"{fichier} : pas de section « {titre.lstrip('# ')} », ou pas de table dessous."]

    reproches = []
    numero_entete, entete = lignes[0]
    if entete.strip() != ENTETE:
        reproches.append(
            f"{fichier}:{numero_entete} : l'en-tête de la table a changé.\n"
            f"  attendu : {ENTETE}\n"
            f"  trouvé  : {entete.strip()}"
        )

    ancres_ici = ancres(corps)
    for numero, ligne in lignes[2:]:  # [0] l'en-tete, [1] le separateur
        cols = cellules(ligne)
        jalon = cols[0] if cols else "?"
        if len(cols) != COLONNES:
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » a {len(cols)} colonnes, il en faut {COLONNES}.\n"
                f"  La table est « {ENTETE.strip('|').strip()} ».\n"
                "  Une ligne comme « | Mon jalon | **P2** **correctif**, **en cours** (14 sept.\n"
                "  2026) | … | » est l'ANCIENNE forme : sépare l'état, la date, la prio et le\n"
                "  genre en quatre cellules."
            )
            continue

        _, etat, date, prio, genre, notes = cols

        icone, sans_icone = _icone(etat)
        # le plus long d'abord : « livrée » commence aussi par « livré »
        connu = next(
            (e for e in sorted(ETATS, key=len, reverse=True) if _dedans(sans_icone).startswith(e)),
            None,
        )
        if connu is None:
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » a l'état « {etat} ».\n"
                f"  Les états connus : {', '.join(ETATS)}."
            )
        else:
            attendue = ICONE_LIVRE if connu.startswith("livr") else ICONE_AUTRE
            if icone != attendue:
                manque = "sans son icône" if icone is None else "avec la mauvaise icône"
                reproches.append(
                    f"{fichier}:{numero} : « {jalon} » a l'état « {etat} », {manque}.\n"
                    f"  {ICONE_LIVRE} devant « livré », {ICONE_AUTRE} devant « en cours » et « à faire » :"
                    f" « {attendue} **{connu}** »."
                )
            if attendue != icone_attendue:
                ou = TABLES[LIVRES if attendue == ICONE_LIVRE else PLAN]
                reproches.append(
                    f"{fichier}:{numero} : « {jalon} » est « {connu} », mais cette table est celle de"
                    f" {nom_du_fichier}.\n"
                    f"  Une ligne {attendue} va dans « {ou[0][3:]} » "
                    f"({LIVRES if attendue == ICONE_LIVRE else PLAN}) : livrer une ligne, c'est la\n"
                    "  faire passer du plan aux jalons livrés (voir la légende du plan)."
                )
        if DATE_COLLEE.search(etat):
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » garde sa date dans l'état (« {etat} »).\n"
                "  La date a sa colonne depuis qu'elle est divisée — mets-la là, pas ici."
            )
        if date != "—" and not DATE.match(date):
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » a la date « {date} ».\n"
                "  Il faut « 14 sept. 2026 » (jour, mois abrégé, année) ou « — »."
            )
        if prio != "—" and not PRIO.match(prio):
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » a la prio « {prio} ».\n"
                "  Il faut **P1** à **P4**, ou « — » pour une ligne livrée avant M9."
            )
        if genre != "—" and not GENRE.match(genre):
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » a le genre « {genre} ».\n"
                "  Il faut « ajout » ou « **correctif** » (le préfixe du commit décide)."
            )
        if LIENS.fullmatch(notes) is None:
            reproches.append(
                f"{fichier}:{numero} : « {jalon} » garde ses notes dans la table"
                f" ({len(notes)} caractères).\n"
                "  La cellule Notes n'est que des liens : [fiche](jalons/x.md#fiche) pour ce qui\n"
                "  est prévu, [notes](jalons/x.md#notes) pour ce qui est livré — le fichier du\n"
                f"  jalon, dans {DOSSIER_JALONS}/. Pour y ranger la note et poser le lien :\n"
                "  uv run python scripts/verifier_table_des_jalons.py --ranger"
            )
            continue
        for _, lien in UN_LIEN.findall(notes):
            reproches += _juger_lien(fichier, numero, jalon, lien, ancres_ici, lire)

    return reproches


def _juger_lien(
    fichier: str, numero: int, jalon: str, lien: str, ancres_ici: set[str], lire: Lecteur | None
) -> list[str]:
    chemin, ancre_ = _cible(fichier, lien)
    if chemin == fichier:
        if ancre_ in ancres_ici:
            return []
        return [
            f"{fichier}:{numero} : « {jalon} » renvoie à #{ancre_}, qui n'est le titre d'aucune\n"
            "  section de ce fichier. Les fiches et les notes sont dans le fichier du jalon\n"
            f"  ({DOSSIER_JALONS}/x.md#fiche, #notes) : le lien y va, pas ici."
        ]
    if lire is None:
        return []
    texte = lire(chemin)
    if texte is None:
        return [
            f"{fichier}:{numero} : « {jalon} » renvoie à {lien}, et {chemin} n'existe pas.\n"
            f"  Le fichier d'un jalon est {DOSSIER_JALONS}/<jalon>.md ; --ranger le crée depuis\n"
            "  une note écrite dans la cellule."
        ]
    if ancre_ and ancre_ not in ancres(texte):
        return [
            f"{fichier}:{numero} : « {jalon} » renvoie à {lien}, et {chemin} n'a pas de titre #{ancre_}."
        ]
    return []


def juger_tout(fichiers: dict[str, str], lire: Lecteur | None = None) -> list[str]:
    """Les deux tables, et ce qui les lie : un jalon dans une seule des deux."""
    reproches: list[str] = []
    noms: dict[str, str] = {}
    for fichier, corps in fichiers.items():
        reproches += juger(corps, fichier, lire)
        for _, ligne in table(corps, TABLES[fichier][0])[2:]:
            cols = cellules(ligne)
            if not cols:
                continue
            ailleurs = noms.setdefault(cols[0], fichier)
            if ailleurs != fichier:
                reproches.append(
                    f"« {cols[0]} » est dans {ailleurs} ET dans {fichier}.\n"
                    "  Un jalon a une seule ligne : ⬜ dans le plan tant qu'il reste à faire, ✅ dans les\n"
                    "  jalons livrés quand il l'est."
                )
    return reproches


# --- ranger ----------------------------------------------------------------


def _envelopper(texte: str, premier: str = "", suivants: str = "") -> list[str]:
    """Replie un paragraphe a LARGEUR sans qu'une ligne devienne une liste ou un titre."""
    colle = COLLE.sub(lambda m: m.group(0).replace(" ", "\0"), texte.strip())
    if not premier and DANGER.match(colle):
        colle = re.sub(r"^(\d+)([.)])", r"\1\\\2", colle) if colle[0].isdigit() else "\\" + colle
    lignes = textwrap.wrap(
        colle,
        width=LARGEUR,
        initial_indent=premier,
        subsequent_indent=suivants,
        break_long_words=False,
        break_on_hyphens=False,
    )
    i = 1
    while i < len(lignes):
        reste = lignes[i][len(suivants) :]
        if DANGER.match(reste):
            # le premier mot remonte sur la ligne d'avant : elle deborde un peu, le sens tient
            mot, _, suite = reste.partition(" ")
            lignes[i - 1] += " " + mot
            if suite:
                lignes[i] = suivants + suite
            else:
                del lignes[i]
            continue
        i += 1
    return [x.replace("\0", " ") for x in lignes]


def _coupe_ici(avant: str, apres: str) -> bool:
    """Un ⚠️ ouvre-t-il une nouvelle puce ? Seulement s'il commence une phrase."""
    avant = avant.rstrip()
    if not avant:
        return False
    if re.search(r"\*\*\d+\.\*\*$", avant):  # « **3.** ⚠️ » : une enumeration
        return False
    if avant.rstrip('*)»" ')[-1:] in (".", "!", "?", "…"):
        return True
    # « (`--refaire batte`) ⚠️ **Correctif, 15 sept. » : le point a ete oublie
    return avant.endswith(")") and re.match(r"\*\*[A-ZÀ-Ý0-9]", apres) is not None


def _segments(bloc: str) -> list[str]:
    morceaux = []
    depart = 0
    for m in re.finditer(ALERTE, bloc):
        if m.start() > depart and _coupe_ici(bloc[depart : m.start()], bloc[m.end() :].lstrip()):
            morceaux.append(bloc[depart : m.start()].strip())
            depart = m.start()
    morceaux.append(bloc[depart:].strip())
    return [x for x in morceaux if x]


def mettre_en_forme(note: str) -> list[str]:
    """Une note d'une seule ligne devient des paragraphes : une vague par paragraphe,
    une puce par ⚠️ qui ouvre une phrase. Pas un mot ne change."""
    lignes: list[str] = []
    for bloc in VAGUE.split(note.strip()):
        segments = _segments(bloc)
        if not segments:
            continue
        if lignes:
            lignes.append("")
        lignes += _envelopper(segments[0])
        if len(segments) > 1:
            lignes.append("")
            for segment in segments[1:]:
                lignes += _envelopper(segment, "- ", "  ")
    return lignes


def ranger(fichier: str, corps: str, lire: Lecteur) -> tuple[str, dict[str, str]]:
    """Sort les notes restees dans la table de `fichier` : chacune devient le fichier de son jalon.

    Rend le fichier corrige et les fichiers a ecrire (chemin depuis la racine -> texte).
    Une cellule qui n'est deja que des liens ne bouge pas ; une cellule vide non plus (le
    juge la reprochera). Se rejoue sans rien changer.
    """
    titre = TABLES[fichier][0]
    nouvelles = corps.split("\n")
    ecrits: dict[str, str] = {}
    dossier = posixpath.dirname(fichier)
    for numero, ligne in table(corps, titre)[2:]:
        cols = cellules(ligne)
        if len(cols) != COLONNES or not cols[5] or LIENS.fullmatch(cols[5]):
            continue
        jalon, texte = cols[0], cols[5]
        base = slug(jalon)
        nom, n = base, 2
        while lire(f"{DOSSIER_JALONS}/{nom}.md") is not None or f"{DOSSIER_JALONS}/{nom}.md" in ecrits:
            nom = f"{base}-{n}"
            n += 1
        chemin = f"{DOSSIER_JALONS}/{nom}.md"
        # dans le plan, une cellule dit ce qui est prévu (la fiche) ; dans les jalons livrés, ce qui l'est (les notes)
        rubrique = "Fiche" if fichier == PLAN else "Notes"
        ecrits[chemin] = (
            "\n".join(
                [
                    f"# {jalon.replace('**', '')}",
                    "",
                    "← [les jalons livrés](README.md) · [le plan](../plan.md)",
                    "",
                    f"## {rubrique}",
                    "",
                    *mettre_en_forme(texte),
                ]
            )
            + "\n"
        )
        lien = posixpath.relpath(chemin, dossier or ".")
        parts = nouvelles[numero - 1].split("|")
        parts[-2] = f" [{rubrique.lower()}]({lien}#{rubrique.lower()}) "
        nouvelles[numero - 1] = "|".join(parts)
    return "\n".join(nouvelles), ecrits


# --- la ligne de commande --------------------------------------------------


def _racine(depart: Path) -> Path:
    sortie = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=depart,
        capture_output=True,
        text=True,
    )
    return Path(sortie.stdout.strip()) if sortie.returncode == 0 else depart


def _lecteur_disque(racine: Path) -> Lecteur:
    def lire(chemin: str) -> str | None:
        cible = racine / chemin
        return cible.read_text(encoding="utf-8") if cible.is_file() else None

    return lire


def _lecteur_index(racine: Path) -> Lecteur:
    """Ce que le commit emporterait : l'index (`git show :chemin`), pas l'arbre de travail."""

    def lire(chemin: str) -> str | None:
        sortie = subprocess.run(
            ["git", "show", f":{chemin}"], cwd=racine, capture_output=True, text=True
        )
        return sortie.stdout if sortie.returncode == 0 else None

    return lire


def _concerne(racine: Path, vise: str) -> bool:
    """Ce fichier est-il une des deux tables, ou un fichier de jalon (dont une ancre peut servir) ?"""
    chemin = Path(vise).resolve()
    try:
        relatif = chemin.relative_to(racine.resolve()).as_posix()
    except ValueError:
        return False
    return relatif in TABLES or (
        relatif.startswith(f"{DOSSIER_JALONS}/") and relatif.endswith(".md")
    )


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fichier", help="ne juge que si ce fichier est une table ou un jalon")
    analyseur.add_argument("--commit", action="store_true", help="juge l'index, pas le disque")
    analyseur.add_argument(
        "--ranger", action="store_true", help="sort les notes des tables, puis juge"
    )
    analyseur.add_argument("--cwd", default=".", help="où chercher le dépôt")
    args = analyseur.parse_args()

    racine = _racine(Path(args.cwd).resolve())

    if args.fichier and not _concerne(racine, args.fichier):
        return 0

    lire = _lecteur_index(racine) if args.commit else _lecteur_disque(racine)
    fichiers = {f: lire(f) for f in TABLES}
    fichiers = {f: c for f, c in fichiers.items() if c is not None}
    if not fichiers:  # ni le plan ni les jalons livres : rien a juger
        return 0

    if args.ranger and not args.commit:
        for fichier, corps in list(fichiers.items()):
            range_, ecrits = ranger(fichier, corps, lire)
            for chemin, texte in ecrits.items():
                cible = racine / chemin
                cible.parent.mkdir(parents=True, exist_ok=True)
                cible.write_text(texte, encoding="utf-8")
                print(f"{chemin} : note rangée.")
            if range_ != corps:
                (racine / fichier).write_text(range_, encoding="utf-8")
                fichiers[fichier] = range_

    reproches = juger_tout(fichiers, lire)
    if not reproches:
        return 0

    print("Les tables des jalons ont perdu leur forme :\n", file=sys.stderr)
    for reproche in reproches:
        print(f"  {reproche}\n", file=sys.stderr)
    print(
        f"  La légende de « À faire » ({PLAN}) dit ce que chaque colonne porte.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
