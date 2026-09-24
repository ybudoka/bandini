#!/usr/bin/env python3
"""Les missions — la boîte de Lego, et le couvercle qui dit si le bloc s'emboîte.

Demande de Martin (20 sept. 2026) : « valide toutes les missions pour que les
animations fonctionnent. Je veux que ça soit facile d'ajouter des missions,
comme des blocs Lego. »

La recette complète est dans `docs/comment-monter-les-missions.md`. Ce script en
est le juge de poche : il dit, en clair, ce qui manque à chaque mission — et il
imprime une fiche prête à coller.

⚠️ **Ce qu'une mission reçoit sans rien demander** : ses clés par défaut
(`prerequis`, `phase`, `echec`, `donne`) et **ses deux scènes**.
`missions.scene_par_defaut` les bâtit de ce que le fichier dit déjà : qui la
donne, où il se tient, ce qu'elle demande d'abord, où elle se termine. Elle en
écrit une ? La sienne gagne. Aucune ? Les animations jouent quand même.

Trois façons de l'appeler, comme ses voisins `verifier_carte_du_depot.py` et
`verifier_table_des_jalons.py` :

    python scripts/verifier_missions.py            # juge tout le catalogue
    python scripts/verifier_missions.py --detail   # ... et dit ce que chacune porte
    python scripts/verifier_missions.py --squelette m7 --donneur josee
                                                   # un fichier prêt à coller
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from app import missions  # noqa: E402

#: Le squelette d'un fichier de mission : ce qu'il FAUT écrire, et pas une clé de
#: plus. Les quatre temps du dialogue sont là parce que le juge les exige tous les
#: quatre — une mission qui se tait à l'échec n'est pas finie. Et chaque réplique porte son
#: `jeu=` : le juge l'exige aussi (`test_interpretation.py`), et il vit dans ce fichier-ci.
SQUELETTE = '''"""La mission {slug} — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {{
    "slug": "{slug}", "titre": "À nommer", "donneur": "{donneur}", "prerequis": ["{precedente}"],
    "recompense": 300,
    "objectifs": [
        {{"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"}},
        {{"type": "retourner", "texte": "REVIENS ME VOIR"}},
    ],
    # Le jeu de chaque réplique (`jeu=`, ce qu'ElevenLabs DIT : les mêmes mots que le texte, plus des
    # balises d'émotion en anglais, des « … » et de la ponctuation) : l'arc du personnage, en une phrase.
    # Voir docs/jeu-d-acteur.md § 3.
    "dialogue": {{
        # ⚠️ On se présente UNE FOIS PAR MISSION : à l'appel (au combiné), dans SA salutation
        # (docs/personnages/<lui>.md) — et plus jamais ensuite dans la mission. Le juge refuse les deux.
        "appel": [_l("{donneur}", "Salut, c'est {nom}. Viens me voir, j'ai une job.",
                     jeu="[casually] Salut, c'est {nom}. Viens me voir… j'ai une job.")],
        "intro": [
            _l("{donneur}", "Première chose à dire.", jeu="[quietly] Première chose à dire."),
            _l("{donneur}", "Deuxième chose à dire.", jeu="[serious] Deuxième chose à dire."),
        ],
        "pendant": [_p("{donneur}", "Ça avance, ton affaire?", 1, jeu="[curious] Ça avance, ton affaire?")],
        "fin": [
            _l("{donneur}", "C'est fait. Merci.", jeu="[relieved] C'est fait. Merci."),
            _l("{donneur}", "On se reparle.", jeu="[warmly] On se reparle."),
        ],
        "echec": [_l("{donneur}", "Une autre fois. Repose-toi.", jeu="[disappointed] Une autre fois… Repose-toi.")],
    }},
}}'''


def reproches() -> list[str]:
    """Tout ce qui empêche une mission du catalogue d'être finie, en clair."""
    sortie: list[str] = []
    for mission in missions.CATALOGUE:
        sortie += missions.erreurs_de_mise_en_scene(mission)
    sortie += missions.erreurs_de_presentation()
    try:
        missions.ordre_topologique()
    except ValueError as erreur:
        sortie.append(str(erreur))
    return sortie


def _origine(mission: dict, partie: str) -> str:
    """Cette scène-là : écrite à la main, ou bâtie par le défaut ?"""
    ecrite = (mission.get("scenes") or {}).get(partie)
    return "écrite" if ecrite and ecrite != missions.scene_par_defaut(mission, partie) else "défaut"


def detail() -> list[str]:
    """Ce que chaque mission porte, deux lignes par mission."""
    lignes = []
    for slug in missions.ordre_topologique():
        mission = missions.par_slug(slug)
        combien = {p: len(mission["dialogue"].get(p) or []) for p in missions.PARTIES}
        scenes = "  ".join(f"{p} {len(mission['scenes'][p])} plans ({_origine(mission, p)})"
                           for p in ("intro", "fin"))
        lignes.append(
            f"  {slug:<6} {mission['titre'][:32]:<32} {mission['donneur']:<10}"
            f" {len(mission['objectifs'])} objectifs  "
            + " ".join(f"{p[:3]}:{n}" for p, n in combien.items() if n)
            + "\n" + " " * 8 + scenes
            + ("" if missions.fin_dite_en_personne(mission) else "  — fin au combiné"))
    return lignes


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--detail", action="store_true", help="dit ce que chaque mission porte")
    analyseur.add_argument("--squelette", metavar="SLUG", help="imprime un fichier de mission prêt à coller")
    analyseur.add_argument("--donneur", default="josee", help="le donneur du squelette")
    args = analyseur.parse_args()

    if args.squelette:
        if not missions.personnage(args.donneur):
            noms = ", ".join(p["slug"] for p in missions.PERSONNAGES if p["ou"])
            print(f"Donneur inconnu : {args.donneur!r}. Ceux qui se tiennent quelque part : {noms}",
                  file=sys.stderr)
            return 1
        ordre = missions.ordre_topologique()
        # Le nom qu'il se donne au téléphone : son surnom s'il en a un (« Lulu »), sinon son nom
        # sans les titres (« Bouchard ») — le squelette doit passer le juge « qui parle se nomme ».
        surnom = re.search(r"«\s*([^»]+?)\s*»", missions.personnage(args.donneur)["nom"])
        nom = surnom.group(1) if surnom else " ".join(missions.noms_dits(args.donneur))
        print(f"# À écrire dans app/missions/{args.squelette}.py :\n")
        print(SQUELETTE.format(slug=args.squelette, donneur=args.donneur, nom=nom,
                               precedente=ordre[-1] if ordre else ""))
        print(f"\n# Puis, dans app/missions/__init__.py, ajouter `{args.squelette}` aux DEUX listes")
        print("# (l'import, et CATALOGUE). Puis :")
        print("#   uv run python scripts/verifier_missions.py --detail")
        print("#   uv run python scripts/audio_elevenlabs.py --voix")
        return 0

    mauvais = reproches()
    if args.detail:
        print(f"{len(missions.CATALOGUE)} missions, {len(missions.DEFIS)} défis :")
        for ligne in detail():
            print(ligne)
        print()
    if not mauvais:
        print(f"Les {len(missions.CATALOGUE)} missions sont finies : "
              "objectifs, répliques aux quatre temps, et deux scènes qui jouent.")
        return 0
    print("Des missions ne sont pas finies :\n", file=sys.stderr)
    for reproche in mauvais:
        print(f"  {reproche}", file=sys.stderr)
    print(
        "\n  Une mission, c'est trois choses : ses objectifs, ses répliques (appel, intro,\n"
        "  pendant, fin, échec) et ses scènes. Les scènes, elle n'a pas à les écrire :\n"
        "  `missions.scene_par_defaut` lui en bâtit deux. Voir\n"
        "  docs/comment-monter-les-missions.md.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
