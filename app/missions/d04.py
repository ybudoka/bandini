"""La mission d04 — voir app/missions/__init__.py pour le moteur.

La collecte du barbier (M16, arc D, 30 sept. 2026). Sal te confie sa tournée : trois débiteurs dans trois
districts — Ti-Paul (les Érables), Lulu (les Quais), Ovila (La Pointe). Les trois que Josée t'a présentés au
tour du propriétaire (m6), et que tu croyais connaître : chacun cache une dette chez le barbier (leurs fiches, dans
`docs/personnages/`). On passe les voir, ils paient chacun à leur façon, et on rapporte le tout au terminus.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "d04",
    "titre": "La collecte du barbier",
    "donneur": "sal",
    "prerequis": ["d03"],
    "recompense": 400,
    "donne": {"dette": -800, "message": "LA COLLECTE EST FAITE — SAL EFFACE 800 $"},

    # ⚠️ Trois `parler` de suite (le patron de m6 et m51) : Ti-Paul dehors (`porte:depanneur`), Lulu et Ovila dedans
    # (`point:lulu`, `point:ovila`). Chacun dit son mot à la poignée de main (`accueil`), déjà connu : pas de nom
    # (docs/jeu-d-acteur.md § 3.11). Puis on revient PARLER à Sal (dedans : pas de `retourner`).
    "objectifs": [
        {"type": "parler", "texte": "TI-PAUL DOIT À SAL : VA COLLECTER AU DÉPANNEUR", "cible": "tipaul"},

        {"type": "parler", "texte": "LULU AUSSI : VA COLLECTER À LA CANTINE", "cible": "lulu"},

        {"type": "parler", "texte": "PIS OVILA : VA COLLECTER AU PHARE", "cible": "ovila"},

        {"type": "parler", "texte": "RAPPORTE LA COLLECTE À SAL, AU TERMINUS", "cible": "sal"},
    ],

    # Intention (intro) : Sal parle en coupant les cheveux — un geste, puis chaque réplique tient la scène (la voix
    # retient le plan ; l'intro par défaut les disait en `ensemble`, et la suivante coupait la première).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": ["porte:depanneur", "porte:cantine", "porte:phare"], "ferme": 20, "ouvre": 20, "tient": 100, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : il donne sa tournée comme on donne les clés de la maison, et il
    # connaît chaque débiteur par sa faiblesse. Ti-Paul paie en jasant (gêné, il ne parle jamais de lui) ; Lulu paie
    # en te grondant, pour se donner une contenance ; Ovila paie en vouvoyant, avec ce qu'il a. À la fin, Sal compte
    # et comprend que tu as vu les visages — il te le reproche doucement.
    "dialogue": {
        "appel": [
            _l("sal", "Ici Sal. J'ai une tournée pour toi, le neveu. Trois clients, trois quartiers.",
               jeu="[calm] Ici Sal. [warmly] J'ai une tournée pour toi, le neveu. [matter-of-fact] Trois clients, trois quartiers.")
        ],
        "intro": [
            _l("sal", "Ti-Paul au dépanneur, Lulu à la cantine, Ovila au phare. Tu les connais, je pense.",
               jeu="[knowingly] Ti-Paul au dépanneur, Lulu à la cantine, Ovila au phare. [wryly] Tu les connais, je pense."),
            _l("sal", "Tout le monde doit quelque chose à quelqu'un, dans cette ville. Moi, j'ai juste un meilleur livre.",
               jeu="[amused] Tout le monde doit quelque chose à quelqu'un, dans cette ville. [smugly] Moi, j'ai juste un meilleur livre."),
            _l("sal", "Sois poli. Un client qui paie, ça se garde comme un client qui se fait couper les cheveux.",
               jeu="[softly] Sois poli. [calm] Un client qui paie, ça se garde comme un client qui se fait couper les cheveux.")
        ],
        "pendant": [
            _p("sal", "Ti-Paul va te parler de la température. Laisse-le faire, il finit toujours par payer.", 0,
               jeu="[amused] Ti-Paul va te parler de la température. [knowingly] Laisse-le faire… il finit toujours par payer."),
            _p("sal", "Lulu va te chicaner. C'est sa façon de dire qu'elle a honte.", 1,
               jeu="[knowingly] Lulu va te chicaner. [softly] C'est sa façon de dire qu'elle a honte."),
            _p("sal", "Le vieux au phare, lui, prends ce qu'il te donne. Il a jamais rien de plus.", 2,
               jeu="[calm] Le vieux au phare, lui, prends ce qu'il te donne. [serious] Il a jamais rien de plus."),
            _p("sal", "Reviens avec tout, le neveu. Je compte, moi, le soir, avant de dormir.", 3,
               jeu="[matter-of-fact] Reviens avec tout, le neveu. [softly] Je compte, moi… le soir, avant de dormir.")
        ],
        "accueil": [
            _a("tipaul", "Sal t'envoie? Eh ben, tiens, l'ami, trois cents. Pis tu diras rien à Josée, hein?", 0,
               jeu="[nervously] Sal t'envoie? Eh ben… [knowingly] tiens, l'ami, trois cents. [worried] Pis tu diras rien à Josée, hein?"),
            _a("lulu", "Toi, collecteur pour Sal? Mon grand, t'as pas honte? Tiens, prends, pis va-t'en.", 1,
               jeu="[annoyed] Toi, collecteur pour Sal? [teasing] Mon grand, t'as pas honte? [softly] Tiens, prends… pis va-t'en."),
            _a("ovila", "Je n'ai que ceci. La montre de mon père. Dites-lui qu'elle retarde un peu.", 2,
               jeu="[softly] Je n'ai que ceci. La montre de mon père. [calm] Dites-lui qu'elle retarde un peu.")
        ],
        "fin": [
            _l("sal", "Trois cents, trois cents, pis une montre. Le vieux Ovila, toujours le même.",
               jeu="[amused] Trois cents, trois cents, pis une montre. [softly] Le vieux Ovila… toujours le même."),
            _l("sal", "T'as vu leurs faces, hein? C'est pour ça que j'envoie pas mes Ciseaux chez les amis.",
               jeu="[knowingly] T'as vu leurs faces, hein? [serious] C'est pour ça que j'envoie pas mes Ciseaux chez les amis."),
            _l("sal", "Huit cents de moins sur ta dette, tu vois? Chez nous, tout se paie. Même la gêne.",
               jeu="[warmly] Huit cents de moins sur ta dette, tu vois? [smugly] Chez nous, tout se paie. Même la gêne.")
        ],
        "echec": [
            _l("sal", "Une collecte à moitié faite, c'est une collecte que je fais moi-même. Pis ça, personne aime ça.",
               jeu="[coldly] Une collecte à moitié faite, c'est une collecte que je fais moi-même. [menacingly] Pis ça, personne aime ça.")
        ]
    }
}
