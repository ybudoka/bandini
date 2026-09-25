"""Les visages des dialogues : un portrait dessiné à gauche de la boîte, pour qui parle.

Demande de Martin (22 sept. 2026) : « je veux des visages dessinés pour chaque dialogue ».

Python décide (quels traits, quelle humeur), JS dessine (`static/js/visages.js`) — comme les
devantures. Un visage est une FICHE de traits pris dans des listes fermées ; les couleurs sont
celles que le personnage a déjà dans la rue (`PERSONNAGES[...]["couleurs"]`) : le portrait et
le bonhomme de seize pixels sont la même personne.

L'HUMEUR suit le jeu d'acteur. `jeu=` (ce qu'ElevenLabs dit) ne va jamais au navigateur
(`missions.pour_le_navigateur`) ; ce qui y va à sa place, c'est un mot : l'humeur de sa
première balise connue. `[warmly]` sourit, `[worried]` fronce, `[coldly]` ne bouge pas un cil.
"""

from __future__ import annotations

import re

#: Les formes de tête (demi-largeurs rangée par rangée : `visages.js`, `TETES`).
TETES = ("ronde", "carree", "longue", "fine", "large")

COIFFURES = ("courte", "brosse", "degarnie", "chauve", "gominee", "meche", "longue", "queue",
             "chignon", "permanente", "bouclee", "carre", "hirsute")

PILOSITES = ("aucune", "moustache", "moustache_epaisse", "barbe", "barbe_courte", "mal_rase", "bouc")

LUNETTES = ("aucunes", "rondes", "carrees", "demi", "epaisses")

CHAPEAUX = ("aucun", "police", "casquette", "tuque", "canotier", "marin", "coiffe")

#: Ce qu'il porte sous le menton — la couleur est son `c` de rue.
HABITS = ("chandail", "chemise_police", "sarrau", "veston", "veste", "uniforme", "tablier",
          "blouse", "col_roule", "gilet")

#: Les petits signes qui font la personne. Une liste, dans n'importe quel ordre.
SIGNES = ("rides", "cernes", "rousseur", "cicatrice", "boucles", "rouge", "fard", "grain",
          "megot", "nez_rouge", "sourcils_epais", "yeux_plisses", "yeux_voiles", "crayon",
          "cure_dent", "noeud_pap", "insigne", "stetho")

#: Les humeurs que le dessin connaît : des sourcils, des yeux et une bouche chacune.
HUMEURS = ("neutre", "content", "rire", "fache", "serieux", "triste", "inquiet", "surpris",
           "malin", "froid")

#: Balise du jeu d'acteur → humeur du visage. ⚠️ Une balise qui ne dit rien du VISAGE
#: (`[quietly]`, `[whispers]`) va à `neutre` — c'est une façon de parler, pas une mine.
#: Un juge refuse toute balise de `interpretation.BALISES` (la liste fermée du jeu d'acteur)
#: qui n'est pas ici : une balise qu'on y ajoute se range aussi dans cette table.
BALISES = {
    "neutre": ("matter-of-fact", "calm", "calmly", "quietly", "casually", "softly", "whispers",
               "whispering", "slowly", "pause", "short pause", "long pause", "clears throat",
               "sincere", "sincerely", "curious", "thoughtful", "hesitant", "hesitantly"),
    "content": ("warmly", "satisfied", "relieved", "cheerful", "cheerfully", "happy", "tenderly",
                "enthusiastic", "excited", "impressed", "confident", "proud", "proudly",
                "grateful", "gently", "friendly", "hopeful"),
    "rire": ("laughs", "laughing", "amused", "chuckles", "giggles", "playfully"),
    "fache": ("annoyed", "angry", "angrily", "bitterly", "frustrated", "irritated", "shouting",
              "shouts", "furious", "exasperated", "impatient", "impatiently"),
    "serieux": ("firmly", "gravely", "serious", "seriously", "gruffly", "deadpan", "stern",
                "sternly", "urgent", "urgently", "determined", "commanding"),
    "triste": ("disappointed", "somber", "sombre", "sighs", "sadly", "sad", "groans", "tired",
               "wearily", "melancholic", "nostalgic", "resigned"),
    "inquiet": ("worried", "nervously", "nervous", "concerned", "anxious", "anxiously",
                "scared", "afraid", "fearful"),
    "surpris": ("surprised", "shocked", "gasps", "dramatic", "dramatically", "astonished"),
    "malin": ("wryly", "knowingly", "teasing", "teasingly", "mischievously", "smugly", "smug",
              "sarcastic", "sarcastically", "mysteriously", "conspiratorially", "slyly", "ironic",
              "ironically"),
    "froid": ("coldly", "menacingly", "threatening", "icy", "flatly", "dryly"),
}

HUMEUR_DE = {balise: humeur for humeur, balises in BALISES.items() for balise in balises}


def connue(balise: str) -> bool:
    """Une balise que le visage sait lire. Un ACCENT (`[norwegian accent]`, Sven) est une
    façon de parler : il est connu, et il ne dit aucune mine."""
    return balise in HUMEUR_DE or balise.endswith(" accent")

_BALISE = re.compile(r"\[([^\]]+)\]")


def balises(jeu: str | None) -> list[str]:
    """Les balises d'un jeu d'acteur, dans l'ordre, en minuscules."""
    return [b.strip().lower() for b in _BALISE.findall(jeu or "")]


def humeur(jeu: str | None) -> str:
    """L'humeur du visage pour une réplique : celle de sa PREMIÈRE balise qui en dit une.

    La première, parce que c'est la mine qu'il a en ouvrant la bouche ; une balise de
    silence (`[pause]`) ne compte pas, sinon « [pause] [angry] » resterait de marbre.
    """
    for b in balises(jeu):
        h = HUMEUR_DE.get(b)
        if h and h != "neutre":
            return h
    return "neutre"


def _v(tete, coiffure, habit, pilosite="aucune", lunettes="aucunes", chapeau="aucun", signes=(),
       **couleurs):
    """Une fiche de visage. `couleurs` ajoute ce que la rue n'a pas : `b` barbe (sinon les
    cheveux), `t` chapeau, `l` lèvres, `y` iris."""
    return {"tete": tete, "coiffure": coiffure, "habit": habit, "pilosite": pilosite,
            "lunettes": lunettes, "chapeau": chapeau, "signes": list(signes), "extra": couleurs}


#: Qui a quelle tête. Les traits viennent des fiches (`docs/personnages/`) : l'âge, le métier,
#: ce qu'on dit d'eux. ⚠️ Les couleurs de base viennent de `PERSONNAGES` — on ne les répète pas.
VISAGES: dict[str, dict] = {
    # Le receleur, chum de Rocco : la cinquantaine joviale, moustache de garagiste, crayon à l'oreille.
    "ti_guy": _v("ronde", "courte", "chandail", "moustache", signes=("rides", "crayon")),
    # La dame du kiosque : chignon gris, petites lunettes, la mine de celle qui a vu passer la rue.
    "thibodeau": _v("fine", "chignon", "gilet", lunettes="demi", signes=("rides", "fard", "boucles")),
    # Le chauffeur de taxi, cousin de toujours : les cheveux gominés, pas rasé depuis hier.
    "marco": _v("carree", "gominee", "chandail", "mal_rase", signes=("cure_dent",)),
    # Le sergent : képi, moustache de flic, les joues de dix ans de casse-croûte gratuit.
    "bouchard": _v("large", "courte", "chemise_police", "moustache_epaisse", chapeau="police",
                   signes=("rides", "insigne"), t="#16264a"),
    # La Chef des Quais : cheveux noirs tirés, le regard qui ne baisse pas, une cicatrice.
    "josee": _v("fine", "queue", "col_roule", signes=("cicatrice", "rouge")),
    # Le client du taxi : un policier en civil qui fait semblant d'être personne.
    "civil": _v("carree", "courte", "veston"),
    # Le Clairon de la Baie : la voix du journal, lunettes carrées et nœud papillon.
    "narrateur": _v("longue", "degarnie", "veston", "moustache", "carrees", signes=("noeud_pap",)),
    # Le dépanneur des Érables : roux, taches de rousseur, bouclé, la cinquantaine.
    "tipaul": _v("ronde", "bouclee", "chandail", "barbe_courte", signes=("rousseur",)),
    # La cantine des Quais : le carré noir, le tablier, les joues rouges de la friteuse.
    "lulu": _v("ronde", "carre", "tablier", signes=("fard", "rouge", "boucles")),
    # La présidente du syndicat : permanente grise, trente ans d'usine dans les yeux.
    "raymonde": _v("carree", "permanente", "chandail", lunettes="carrees", signes=("rides",)),
    # Le gardien du phare : presque aveugle, barbe de marin, les yeux voilés.
    "ovila": _v("longue", "degarnie", "col_roule", "barbe", signes=("rides", "yeux_voiles")),
    # L'itinérant du terminus : tuque, barbe hirsute, le nez de la bière.
    "mo": _v("large", "hirsute", "gilet", "barbe", chapeau="tuque", signes=("nez_rouge", "cernes"),
             t="#8e3a2a"),
    # Le chauffeur du dernier autobus : casquette d'uniforme, moustache, lunettes.
    "fern": _v("longue", "courte", "uniforme", "moustache", "rondes", chapeau="casquette",
               signes=("rides",), t="#1a3a5a"),
    # Le casse-croûte du Faubourg : permanente auburn, tablier, maternelle.
    "mado": _v("ronde", "permanente", "tablier", signes=("fard", "rouge", "grain")),
    # Le chef des débardeurs : tuque de quai, brosse, sourcils épais, pas un sourire de trop.
    "gege": _v("carree", "brosse", "veste", "mal_rase", chapeau="tuque",
               signes=("sourcils_epais", "cicatrice"), t="#2a3a5a"),
    # L'ado du dépanneur : la mèche dans les yeux, un bouton sur le menton.
    "xavier": _v("fine", "meche", "chandail", signes=("rousseur",)),
    # L'urgentologue : sarrau, stéthoscope, cernes de garde.
    "lachance": _v("longue", "degarnie", "sarrau", lunettes="rondes", signes=("cernes", "stetho")),
    # L'armurier : chauve, moustache épaisse, le mégot au coin de la bouche.
    "gus": _v("carree", "chauve", "gilet", "moustache_epaisse",
              signes=("sourcils_epais", "megot", "yeux_plisses", "cicatrice")),
    # La couturière, ancienne blonde de Rocco : longs cheveux foncés, rouge à lèvres.
    "rosa": _v("fine", "longue", "blouse", signes=("rouge", "boucles", "grain")),
    # L'infirmière-chef : coiffe, chignon châtain, le regard qui sait.
    "ginette": _v("ronde", "chignon", "blouse", chapeau="coiffe", signes=("cernes",), t="#ffffff"),
    # Le gardien du lot, bientôt à la retraite : casquette, moustache grise, rides.
    "gilles": _v("longue", "degarnie", "uniforme", "moustache", chapeau="casquette",
                 signes=("rides", "cernes"), t="#4a5a3a"),
    # Le Bonimenteur de la foire : canotier, moustache cirée, nœud papillon.
    "bonimenteur": _v("longue", "gominee", "veston", "moustache", chapeau="canotier",
                      signes=("noeud_pap",), t="#e8d8a0"),
    # Le contrebandier : casquette de marin, barbe grise courte, yeux pâles.
    "sven": _v("carree", "courte", "col_roule", "barbe_courte", chapeau="marin",
               signes=("yeux_plisses", "rides"), t="#1a1a2a", y="#6a9ac8"),
    # Le vieux capitaine du traversier (M13) : la casquette de marin, l'uniforme bleu nuit, une
    # barbe blanche pleine — là où Sven la porte courte et grise.
    "berube": _v("large", "degarnie", "uniforme", "barbe", chapeau="marin",
                 signes=("rides", "sourcils_epais", "yeux_plisses"), t="#16263a", y="#5a7a9a"),
}

#: Ceux qui parlent sans être des PERSONNAGES : l'agent qui t'interpelle dans la rue.
AUTRES: dict[str, dict] = {
    "agent": dict(_v("carree", "courte", "chemise_police", chapeau="police", signes=("insigne",),
                     t="#16264a"),
                  couleurs={"c": "#1f3a6e", "h": "#3a2a1a", "s": "#e8b088", "p": "#16264a"}),
}


#: Ce qui ne voyage pas : le paquet est déjà serré (`test_definitions`), et `visages.js`
#: lit une clé absente comme « rien » (pas de lunettes, pas de chapeau, pas de signes).
_PAR_DEFAUT = {"pilosite": "aucune", "lunettes": "aucunes", "chapeau": "aucun", "signes": [], "extra": {}}


def _leger(v: dict) -> dict:
    return {k: val for k, val in v.items() if _PAR_DEFAUT.get(k, object()) != val}


def complet(v: dict) -> dict:
    """Une fiche du paquet avec ses valeurs par défaut remises (pour les juges)."""
    return {**_PAR_DEFAUT, **v}


def pour_le_navigateur() -> dict[str, dict]:
    """Les visages tels que `visages.js` les lit : la fiche, avec les couleurs de la rue,
    sans ce qui vaut « rien »."""
    # ⚠️ Importé ICI : `missions.pour_le_navigateur` appelle `humeur`, et les deux modules
    # se liraient l'un l'autre au chargement.
    from . import missions
    sortie = {}
    for p in missions.PERSONNAGES:
        v = VISAGES.get(p["slug"])
        if v:
            sortie[p["slug"]] = _leger(dict(v, couleurs=dict(p["couleurs"])))
    for slug, v in AUTRES.items():
        sortie[slug] = _leger(dict(v))
    return sortie
