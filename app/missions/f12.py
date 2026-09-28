"""La mission f12 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "f12",
    "titre": "Le Faubourg te dit merci",
    "donneur": "thibodeau",
    "prerequis": ["f08", "f09", "f10"],
    "recompense": 500,
    "echec": ["mort", "arrete", "etoile"],
    "donne": {"rabais": {"casse_croute": 0.90}, "message": "LE FAUBOURG TE NOURRIT MOINS CHER"},

    # ⚠️ La fin de l'arc F — une tournée, pas une bagarre. Cinq commerçants ont mis une
    # enveloppe : on va la chercher chez chacun (`parler`, sa poignée de main dite en
    # `accueil`), tous DEHORS à leur porte (`porte:`), donc vivants en ville et pointés par
    # la flèche. `sans_etoile` sur chaque tournée : on ne paie pas un gars recherché — une
    # étoile et c'est raté (`etoile`), ce qui fait de la plus douce mission de l'arc la
    # seule où l'on ne peut pas voler un char pour aller plus vite.
    #
    # Aucun lieu neuf : les cinq portes sont déjà des lieux de mission (la ville ne glisse
    # pas). Le rabais va au casse-croûte (−10 %) : c'est le comptoir qu'aucune mission ne
    # rabattait encore — l'armurerie et Rosa ont déjà les leurs (f02, f03), plus gros.
    "objectifs": [
        {"type": "parler", "texte": "L'ENVELOPPE DE GUS, À L'ARMURERIE",
         "cible": "gus", "sans_etoile": True},

        {"type": "parler", "texte": "CELLE DE ROSA, À LA BOUTIQUE",
         "cible": "rosa", "sans_etoile": True},

        {"type": "parler", "texte": "CELLE DE MADO, AU CASSE-CROÛTE",
         "cible": "mado", "sans_etoile": True},

        {"type": "parler", "texte": "CELLE DE FERN, AU TERMINUS",
         "cible": "fern", "sans_etoile": True},

        {"type": "parler", "texte": "CELLE DE MARCO, AU GARAGE",
         "cible": "marco", "sans_etoile": True},

        {"type": "retourner", "texte": "RAPPORTE LES ENVELOPPES AU KIOSQUE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Madame Thibodeau : la fierté émue de celle qui a
    # vu le Faubourg à genoux (m2) et qui organise la quête comme un bingo paroissial ; les
    # cinq commerçants, chacun dans son registre — Gus bourru qui ne sait pas dire merci,
    # Rosa ironique, Mado qui nourrit, Fern chronométré, Marco qui compte encore.
    "dialogue": {
        "appel": [
            _l("thibodeau", "C'est Madame Thibodeau, du kiosque. Les commerçants ont fait une petite quête pour toi, veux-tu passer?",
               jeu="[warmly] C'est Madame Thibodeau, du kiosque. [tenderly] Les commerçants ont fait une petite quête pour toi… veux-tu passer?")
        ],
        "intro": [
            _l("thibodeau", "Cinq enveloppes, mon p'tit. Gus, Rosa, Mado, Fern pis ton cousin Marco.",
               jeu="[cheerful] Cinq enveloppes, mon p'tit. [warmly] Gus, Rosa, Mado, Fern… pis ton cousin Marco."),
            _l("thibodeau", "Fais le tour à pied, comme un honnête homme. Personne va donner une cenne à un gars que la police cherche.",
               jeu="[firmly] Fais le tour à pied, comme un honnête homme. [concerned] Personne va donner une cenne à un gars que la police cherche.")
        ],
        "pendant": [
            _p("thibodeau", "Commence par Gus. Il te dira pas merci, mais son enveloppe est la plus épaisse.", 0,
               jeu="[amused] Commence par Gus. [knowingly] Il te dira pas merci… mais son enveloppe est la plus épaisse."),
            _p("thibodeau", "Rosa, astheure. Elle a mis un ruban sur la sienne, fais attention.", 1,
               jeu="[warmly] Rosa, astheure. [amused] Elle a mis un ruban sur la sienne, fais attention."),
            _p("thibodeau", "Mado t'attend au casse-croûte. Mange quelque chose, t'as les joues creuses.", 2,
               jeu="[tenderly] Mado t'attend au casse-croûte. [concerned] Mange quelque chose… t'as les joues creuses."),
            _p("thibodeau", "Fern est au terminus entre deux autobus. Il te laisse une minute, pas deux.", 3,
               jeu="[matter-of-fact] Fern est au terminus entre deux autobus. [amused] Il te laisse une minute… pas deux."),
            _p("thibodeau", "Marco a hésité longtemps. Va voir s'il a fini de compter.", 4,
               jeu="[wryly] Marco a hésité longtemps. [knowingly] Va voir s'il a fini de compter."),
            _p("thibodeau", "Reviens au kiosque, mon p'tit. J'ai mis le café sur le feu.", 5,
               jeu="[warmly] Reviens au kiosque, mon p'tit. [cheerful] J'ai mis le café sur le feu.")
        ],
        "accueil": [
            _a("gus", "Tiens, jeune. Compte-la pas devant moi, ça me gêne.", 0,
               jeu="[gruffly] Tiens, jeune. [annoyed] Compte-la pas devant moi… ça me gêne."),
            _a("rosa", "Une enveloppe cousue main. Le ruban, c'est pour la classe.", 1,
               jeu="[wryly] Une enveloppe cousue main. [amused] Le ruban, c'est pour la classe."),
            _a("mado", "La mienne, pis une poutine pour la route. Pas de discussion, mon grand.", 2,
               jeu="[warmly] La mienne, pis une poutine pour la route. [firmly] Pas de discussion, mon grand."),
            _a("fern", "Deux minutes d'avance sur l'horaire, c'est grâce à toi. Tiens, monte pas, c'est tout.", 3,
               jeu="[matter-of-fact] Deux minutes d'avance sur l'horaire, c'est grâce à toi. [amused] Tiens… monte pas, c'est tout."),
            _a("marco", "Je l'ai recomptée trois fois, cousin. Elle est juste, c'est ça qui me fait mal.", 4,
               jeu="[wryly] Je l'ai recomptée trois fois, cousin. [sighs] Elle est juste… c'est ça qui me fait mal.")
        ],
        "fin": [
            _l("thibodeau", "Cinq enveloppes. Y a deux ans, on avait même pas de quoi payer les Cravates.",
               jeu="[tenderly] Cinq enveloppes. [somber] Y a deux ans… on avait même pas de quoi payer les Cravates."),
            _l("thibodeau", "Merci, mon p'tit. Le Faubourg respire, pis c'est un peu grâce à toi.",
               jeu="[warmly] Merci, mon p'tit. [tenderly] Le Faubourg respire… pis c'est un peu grâce à toi.")
        ],
        "echec": [
            _l("thibodeau", "Ils t'ont vu avec la police aux trousses, hein? Laisse retomber la poussière, pis reviens.",
               jeu="[concerned] Ils t'ont vu avec la police aux trousses, hein? [softly] Laisse retomber la poussière… pis reviens.")
        ]
    }
}
