#!/usr/bin/env python3
"""La table des jalons — six colonnes, et personne ne la reduit a trois en passant.

`docs/plan.md` ouvre sur « Etat des jalons » : une ligne par morceau de travail,
divisee en `Jalon | Etat | Date | Prio | Genre | Notes`. C'est le tableau de bord
des sessions — plusieurs Claude ecrivent dans le meme arbre, et cette table est le
seul endroit ou elles se voient.

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
3. une date `JJ mois AAAA` ou `—`, et jamais une date restee collee dans l'etat ;
4. une prio `P1` a `P4` ou `—` ;
5. un genre `ajout`, `correctif` ou `—` ;
6. des notes qui ne sont qu'un lien, `[notes](#ancre)`, vers un titre de la
   section « Notes des jalons » en bas du plan.

La 6e regle date du 17 sept. 2026 : les notes vivaient dans la cellule, et une
ligne de table ne se replie pas — la plus longue faisait 22 000 caracteres, et la
table entiere 320 Ko. `--ranger` fait le travail : il sort chaque note restee dans
sa cellule, la met en forme (un paragraphe, une puce par ⚠️, une vague par
paragraphe, replie a 92 colonnes) et pose le lien. On peut donc continuer
d'ecrire la note dans la cellule, et ranger avant de committer.

Appele de quatre facons, comme son voisin `verifier_carte_du_depot.py` :

    python scripts/verifier_table_des_jalons.py              # tout le plan
    python scripts/verifier_table_des_jalons.py --fichier F  # ne dit rien si F n'est pas le plan
    python scripts/verifier_table_des_jalons.py --commit     # ce qui part au commit
    python scripts/verifier_table_des_jalons.py --ranger     # sort les notes de la table, puis juge
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
import unicodedata
from pathlib import Path

PLAN = "docs/plan.md"
TITRE = "## État des jalons"
ENTETE = "| Jalon | État | Date | Prio | Genre | Notes |"
TITRE_NOTES = "## Notes des jalons"
INTRO_NOTES = (
    "Le détail de chaque ligne de la table « État des jalons », dans le même ordre : ce qui a "
    "été demandé, mesuré, livré, et pourquoi. La table n'y renvoie que par un lien ; une note "
    "écrite dans sa cellule se range ici avec `--ranger` (voir la légende de la table)."
)

COLONNES = 6

ETATS = ("livré", "livrée", "en cours", "à faire")
# L'icone devant l'etat (demande de Martin, 17 sept. 2026) : un crochet pour ce qui
# est livre, une case vide pour le reste — la colonne se lit d'un coup d'oeil.
ICONE_LIVRE = "✅"
ICONE_AUTRE = "⬜"
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
LIEN_NOTES = re.compile(r"\[notes\]\(#([^)\s]+)\)")

# La mise en forme d'une note. Les lignes du plan sont repliees a cette largeur.
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


def _dedans(texte: str) -> str:
    """Le corps d'une cellule, sans le gras ni les espaces."""
    return texte.strip().strip("*").strip()


def _icone(etat: str) -> tuple[str | None, str]:
    """L'icone en tete de la cellule d'etat (ou None), et ce qui la suit."""
    for icone in (ICONE_LIVRE, ICONE_AUTRE):
        if etat.startswith(icone):
            return icone, etat[len(icone) :].strip()
    return None, etat


def table(corps: str) -> list[tuple[int, str]]:
    """Les lignes de la table des jalons, numerotees (1-based) comme dans le fichier.

    La table est celle qui suit `## État des jalons` : elle commence a la premiere
    ligne qui ouvre sur `|` et finit a la premiere qui ne le fait plus.
    """
    lignes = corps.split("\n")
    depart = next((i for i, x in enumerate(lignes) if x.strip() == TITRE), None)
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


def _bornes_notes(lignes: list[str]) -> tuple[int, int] | None:
    """La ligne `## Notes des jalons` et la premiere ligne apres sa section."""
    debut = next((i for i, x in enumerate(lignes) if x.strip() == TITRE_NOTES), None)
    if debut is None:
        return None
    fin = next((j for j in range(debut + 1, len(lignes)) if lignes[j].startswith("## ")), None)
    return debut, len(lignes) if fin is None else fin


def ancres_des_notes(corps: str) -> set[str]:
    """Les ancres des notes : les titres `###` de la section « Notes des jalons »."""
    lignes = corps.split("\n")
    bornes = _bornes_notes(lignes)
    if bornes is None:
        return set()
    debut, fin = bornes
    return {nom for i, niveau, _, nom in titres(lignes) if debut < i < fin and niveau == 3}


# --- le juge ---------------------------------------------------------------


def juger(corps: str) -> list[str]:
    """Les reproches, un par ligne fautive. Vide = la table tient."""
    lignes = table(corps)
    if not lignes:
        return [f"{PLAN} : pas de section « {TITRE.lstrip('# ')} », ou pas de table dessous."]

    reproches = []
    numero_entete, entete = lignes[0]
    if entete.strip() != ENTETE:
        reproches.append(
            f"{PLAN}:{numero_entete} : l'en-tête de la table a changé.\n"
            f"  attendu : {ENTETE}\n"
            f"  trouvé  : {entete.strip()}"
        )

    notes_connues = ancres_des_notes(corps)
    for numero, ligne in lignes[2:]:  # [0] l'en-tete, [1] le separateur
        cols = cellules(ligne)
        jalon = cols[0] if cols else "?"
        if len(cols) != COLONNES:
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a {len(cols)} colonnes, il en faut {COLONNES}.\n"
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
                f"{PLAN}:{numero} : « {jalon} » a l'état « {etat} ».\n"
                f"  Les états connus : {', '.join(ETATS)}."
            )
        else:
            attendue = ICONE_LIVRE if connu.startswith("livr") else ICONE_AUTRE
            if icone != attendue:
                manque = "sans son icône" if icone is None else "avec la mauvaise icône"
                reproches.append(
                    f"{PLAN}:{numero} : « {jalon} » a l'état « {etat} », {manque}.\n"
                    f"  {ICONE_LIVRE} devant « livré », {ICONE_AUTRE} devant « en cours » et « à faire » :"
                    f" « {attendue} **{connu}** »."
                )
        if DATE_COLLEE.search(etat):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » garde sa date dans l'état (« {etat} »).\n"
                "  La date a sa colonne depuis qu'elle est divisée — mets-la là, pas ici."
            )
        if date != "—" and not DATE.match(date):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a la date « {date} ».\n"
                "  Il faut « 14 sept. 2026 » (jour, mois abrégé, année) ou « — »."
            )
        if prio != "—" and not PRIO.match(prio):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a la prio « {prio} ».\n"
                "  Il faut **P1** à **P4**, ou « — » pour une ligne livrée avant M9."
            )
        if genre != "—" and not GENRE.match(genre):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a le genre « {genre} ».\n"
                "  Il faut « ajout » ou « **correctif** » (le préfixe du commit décide)."
            )
        lien = LIEN_NOTES.fullmatch(notes)
        if lien is None:
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » garde ses notes dans la table"
                f" ({len(notes)} caractères).\n"
                f"  La cellule Notes n'est qu'un lien, [notes](#ancre), vers « {TITRE_NOTES[3:]} »\n"
                "  en bas du plan. Pour y déplacer la note et poser le lien :\n"
                "  uv run python scripts/verifier_table_des_jalons.py --ranger"
            )
        elif lien.group(1) not in notes_connues:
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » renvoie à #{lien.group(1)}, qui n'est le titre"
                " d'aucune note.\n"
                f"  Les notes sont les titres ### de « {TITRE_NOTES[3:]} ». Si le titre porte le\n"
                "  nom du jalon, --ranger recolle le lien."
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


def _titre_de_note(jalon: str) -> str:
    # « » n'ont pas la meme ancre chez GitHub et dans l'apercu de VS Code ; “ ” si
    return re.sub(r"«\s*", "“", re.sub(r"\s*»", "”", jalon))


def _sans_blancs_aux_bords(lignes: list[str]) -> list[str]:
    debut = 0
    while debut < len(lignes) and not lignes[debut].strip():
        debut += 1
    fin = len(lignes)
    while fin > debut and not lignes[fin - 1].strip():
        fin -= 1
    return lignes[debut:fin]


def ranger(corps: str) -> str:
    """Sort les notes restees dans la table, et range la section dans l'ordre de la table.

    Une note deja rangee ne bouge que de place ; un lien casse est recolle si une note
    porte le nom du jalon ; une note que plus aucune ligne ne cite reste, a la fin.
    Se rejoue sans rien changer.
    """
    lignes = corps.split("\n")
    rangs = table(corps)
    if len(rangs) < 3:
        return corps

    ancres_avant = {i: nom for i, _, _, nom in titres(lignes)}
    bornes = _bornes_notes(lignes)
    notes: list[dict] = []  # {"titre", "corps", "ancre"} dans l'ordre du fichier
    if bornes is None:
        intro = _envelopper(INTRO_NOTES)
        avant, apres = lignes[:], []
        while avant and not avant[-1].strip():
            avant.pop()
    else:
        debut, fin = bornes
        avant, apres = lignes[:debut], lignes[fin:]
        while avant and not avant[-1].strip():
            avant.pop()
        courante = None
        intro_brute: list[str] = []
        for i in range(debut + 1, fin):
            if lignes[i].startswith("### "):
                courante = {
                    "titre": lignes[i][4:].strip(),
                    "corps": [],
                    "ancre": ancres_avant.get(i),
                }
                notes.append(courante)
            elif courante is None:
                intro_brute.append(lignes[i])
            else:
                courante["corps"].append(lignes[i])
        intro = _sans_blancs_aux_bords(intro_brute)
        for note in notes:
            note["corps"] = _sans_blancs_aux_bords(note["corps"])

    if rangs[-1][0] > len(avant):
        return corps  # la section des notes est au-dessus de la table : on ne touche a rien

    par_ancre = {n["ancre"]: n for n in notes if n["ancre"]}
    ordre: list[dict] = []
    liens: list[tuple[int, dict]] = []  # (index de la ligne de table, note visee)
    for numero, ligne in rangs[2:]:
        cols = cellules(ligne)
        if len(cols) != COLONNES:
            continue
        jalon, texte = cols[0], cols[5]
        titre = _titre_de_note(jalon)
        lien = LIEN_NOTES.fullmatch(texte)
        if lien is not None:
            note = par_ancre.get(lien.group(1)) or next(
                (n for n in notes if n["titre"] == titre), None
            )
            if note is None:
                continue  # un lien qui ne mene nulle part : le juge le dira
        else:
            note = next((n for n in notes if n["titre"] == titre), None)
            if note is None:
                note = {"titre": titre, "corps": [], "ancre": None}
                notes.append(note)
            if note["corps"]:
                note["corps"].append("")
            note["corps"] += mettre_en_forme(texte)
        liens.append((numero - 1, note))
        if all(note is not n for n in ordre):
            ordre.append(note)
    ordre += [n for n in notes if all(n is not m for m in ordre)]

    section = [TITRE_NOTES, "", *intro]
    positions = []
    for note in ordre:
        section.append("")
        positions.append((len(avant) + 1 + len(section), note))
        section += [f"### {note['titre']}", "", *note["corps"]]
    if apres:
        section.append("")
    nouvelles = [*avant, "", *section, *apres]
    if not apres:
        nouvelles.append("")

    ancres_apres = {i: nom for i, _, _, nom in titres(nouvelles)}
    ancre_de = {id(note): ancres_apres[i] for i, note in positions}
    for index, note in liens:
        parts = nouvelles[index].split("|")
        parts[-2] = f" [notes](#{ancre_de[id(note)]}) "
        nouvelles[index] = "|".join(parts)
    return "\n".join(nouvelles)


# --- la ligne de commande --------------------------------------------------


def _racine(depart: Path) -> Path:
    sortie = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=depart,
        capture_output=True,
        text=True,
    )
    return Path(sortie.stdout.strip()) if sortie.returncode == 0 else depart


def _corps_au_commit(racine: Path) -> str | None:
    """Le plan tel qu'il partirait au commit (l'index), ou None s'il n'y est pas."""
    sortie = subprocess.run(
        ["git", "show", f":{PLAN}"],
        cwd=racine,
        capture_output=True,
        text=True,
    )
    return sortie.stdout if sortie.returncode == 0 else None


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fichier", help="ne juge que si ce fichier est le plan")
    analyseur.add_argument("--commit", action="store_true", help="juge l'index, pas le disque")
    analyseur.add_argument(
        "--ranger", action="store_true", help="sort les notes de la table, puis juge"
    )
    analyseur.add_argument("--cwd", default=".", help="où chercher le dépôt")
    args = analyseur.parse_args()

    racine = _racine(Path(args.cwd).resolve())

    if args.fichier:
        vise = Path(args.fichier).resolve()
        if vise != (racine / PLAN).resolve():
            return 0

    if args.commit:
        corps = _corps_au_commit(racine)
        if corps is None:  # le plan n'est pas dans ce commit : rien a juger
            return 0
    else:
        plan = racine / PLAN
        if not plan.exists():
            return 0
        corps = plan.read_text(encoding="utf-8")
        if args.ranger:
            range_ = ranger(corps)
            if range_ != corps:
                plan.write_text(range_, encoding="utf-8")
                print(f"{PLAN} : notes rangées sous « {TITRE_NOTES[3:]} ».")
            corps = range_

    reproches = juger(corps)
    if not reproches:
        return 0

    print("La table des jalons a perdu sa division :\n", file=sys.stderr)
    for reproche in reproches:
        print(f"  {reproche}\n", file=sys.stderr)
    print(
        "  La légende au-dessus de la table dit ce que chaque colonne porte.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
