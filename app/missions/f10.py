"""La mission f10 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "f10",
    "titre": "La chemise hawaïenne",
    "donneur": "rosa",
    "prerequis": ["f03"],
    "recompense": 300,
    "donne": {"contacts": ["norbert"], "message": "NORBERT TE DOIT UN SERVICE"},

    # ⚠️ « EN LA PORTANT » (28 sept. 2026) : l'option `tenue` d'un objectif le retient tant
    # qu'on ne porte pas cette tenue-là (`B.partie.tenue`) — on arrive à l'hôtel, on parle à
    # Norbert, rien ne se passe, et la ligne d'objectif dit quoi enfiler. `remet` donne la
    # chemise (la tenue entre au sac, comme si on l'avait achetée) : on l'enfile au comptoir
    # de Rosa, à deux pas, ou à la penderie de la planque.
    #
    # Norbert se tient DEDANS (`point:norbert`, le bout du comptoir du hall) : ni `retourner`
    # vers lui ni bagarre posée près de lui (la pose relative au joueur, dedans, part au coin
    # de la ville). Les deux Cravates qui attendaient le vrai client guettent à la porte de
    # l'hôtel (`ou: porte:hotel`, sans `loin`) : on les trouve en sortant. Puis on rapporte
    # la chemise à Rosa, qui se tient dehors.
    "objectifs": [
        {"type": "aller", "texte": "ENFILE LA CHEMISE, PUIS VA À L'HÔTEL",
         "lieu": "hotel", "rayon": 4, "remet": "chemise_hawai", "tenue": "chemise_hawai"},

        {"type": "parler", "texte": "DONNE LA LETTRE À NORBERT, EN CHEMISE",
         "cible": "norbert", "tenue": "chemise_hawai"},

        {"type": "tuer", "texte": "DEUX CRAVATES TE PRENNENT POUR UN AUTRE",
         "groupe": "cravates", "n": 2, "ou": "porte:hotel", "arme": "", "vie": 70},

        {"type": "retourner", "texte": "RETOURNE VOIR ROSA"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Rosa, la chemise : amusée de bout en bout, l'ironie
    # de l'artisane qui habille un neveu de Rocco en touriste ; Norbert, le concierge, poli
    # jusqu'au vouvoiement, jamais surpris — il a tout vu passer dans ce hall. Il se nomme à
    # sa poignée de main : c'est la première fois qu'on l'entend.
    "dialogue": {
        "appel": [
            _l("rosa", "Rosa, de la boutique. Un client a oublié une chemise hawaïenne chez nous, pis une lettre dans la poche.",
               jeu="[amused] Rosa, de la boutique. [knowingly] Un client a oublié une chemise hawaïenne chez nous… pis une lettre dans la poche.")
        ],
        "intro": [
            _l("rosa", "La lettre est pour Norbert, le concierge de l'Hôtel Bandini. Il ouvre juste au gars en chemise.",
               jeu="[knowingly] La lettre est pour Norbert, le concierge de l'Hôtel Bandini. [wryly] Il ouvre juste au gars en chemise."),
            _l("rosa", "Enfile-la, elle est à ta taille. Rocco aurait jamais porté des palmiers, toi t'as le cou pour.",
               jeu="[amused] Enfile-la, elle est à ta taille. [wryly] Rocco aurait jamais porté des palmiers… toi t'as le cou pour.")
        ],
        "pendant": [
            _p("rosa", "Change-toi dans ma cabine si tu veux. Pis marche comme un gars en vacances.", 0,
               jeu="[amused] Change-toi dans ma cabine si tu veux. [teasing] Pis marche comme un gars en vacances."),
            _p("rosa", "Norbert est au bout du comptoir, dans le hall. Donne-lui la lettre, pas un mot de plus.", 1,
               jeu="[calm] Norbert est au bout du comptoir, dans le hall. [firmly] Donne-lui la lettre… pas un mot de plus."),
            _p("norbert", "Deux messieurs en cravate attendaient le vrai client, dehors. Je crains qu'ils vous confondent.", 2,
               jeu="[quietly] Deux messieurs en cravate attendaient le vrai client, dehors. [concerned] Je crains qu'ils vous confondent."),
            _p("rosa", "Norbert m'a appelée. Reviens me montrer si les palmiers ont survécu.", 3,
               jeu="[amused] Norbert m'a appelée. [teasing] Reviens me montrer si les palmiers ont survécu.")
        ],
        "accueil": [
            _a("norbert", "Norbert, concierge. Monsieur porte la chemise, monsieur a donc une lettre pour moi.", 1,
               jeu="[calm] Norbert, concierge. [knowingly] Monsieur porte la chemise… monsieur a donc une lettre pour moi.")
        ],
        "fin": [
            _l("rosa", "Pas une tache, pas un bouton de parti. Tu te bats proprement, toi.",
               jeu="[impressed] Pas une tache, pas un bouton de parti. [amused] Tu te bats proprement, toi."),
            _l("rosa", "Garde la chemise. Pis Norbert te doit un service, ça vaut plus que mon rabais.",
               jeu="[warmly] Garde la chemise. [knowingly] Pis Norbert te doit un service… ça vaut plus que mon rabais.")
        ],
        "echec": [
            _l("rosa", "Tant pis. Une chemise, ça se recoud, une réputation, moins.",
               jeu="[disappointed] Tant pis. [wryly] Une chemise, ça se recoud… une réputation, moins.")
        ]
    }
}
