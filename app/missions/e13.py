"""La mission e13 — voir app/missions/__init__.py pour le moteur.

Le char de Diane (M16, arc E, 30 sept. 2026). Les Érables sont libres (e10), et la conseillère se prépare à la
mairie ; mais sa berline dort au lot de la fourrière — un stationnement « interdit aux citoyens » devant l'hôtel de
ville, posé par les hommes du maire. Elle ne paiera pas une amende de Tanguay. On la reprend au lot sans payer, on
sème la police que Gilles appelle « par principe », et on la gare devant le dépanneur, sans une bosse.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e13",
    "titre": "Le char de Diane",
    "donneur": "diane",
    "prerequis": ["e10"],
    "recompense": 300,
    "donne": {"message": "LA BERLINE DE DIANE EST DEVANT LE DÉPANNEUR — SANS AMENDE"},

    # ⚠️ La berline se prend au lot (`porte:fourriere`, le patron de f08) ; on la livre devant le dépanneur, où Diane
    # se tient (`porte:depanneur`) : la fin se dit devant elle, sans `retourner`.
    "objectifs": [
        {"type": "monter", "texte": "SA BERLINE DORT AU LOT : REPRENDS-LA SANS PAYER",
         "vehicule": "luxe", "ou": "porte:fourriere"},

        {"type": "semer", "texte": "GILLES APPELLE LA POLICE, PAR PRINCIPE : SÈME-LA", "etoiles": 1},

        {"type": "livrer", "texte": "LA BERLINE DEVANT LE DÉPANNEUR, SANS UNE BOSSE",
         "lieu": "depanneur", "rayon": 6},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:fourriere", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Diane : la politicienne qui vouvoie, un sourire dans la voix ; elle parle
    # des « citoyens » pour ne pas parler d'elle.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Le maire m'a fait remorquer. Venez me voir au dépanneur, j'ai un service.",
               jeu="[confident] Diane Larivière. [wryly] Le maire m'a fait remorquer. [calm] Venez me voir au dépanneur, j'ai un service.")
        ],
        "intro": [
            _l("diane", "Un stationnement « interdit aux citoyens » devant l'hôtel de ville. Posé hier, par ses hommes.",
               jeu="[wryly] Un stationnement « interdit aux citoyens » devant l'hôtel de ville. [knowingly] Posé hier, par ses hommes."),
            _l("diane", "Ma berline est au lot. Je ne paierai pas une amende signée Tanguay, par principe.",
               jeu="[calm] Ma berline est au lot. [confident] Je ne paierai pas une amende signée Tanguay, par principe."),
            _l("diane", "Ramenez-la ici, sans une bosse. Les citoyens me regardent conduire, maintenant.",
               jeu="[firmly] Ramenez-la ici, sans une bosse. [wryly] Les citoyens me regardent conduire, maintenant.")
        ],
        "pendant": [
            _p("diane", "Gilles est un homme honnête. Ne lui faites pas de peine, prenez-la, c'est tout.", 0,
               jeu="[calm] Gilles est un homme honnête. [knowingly] Ne lui faites pas de peine, prenez-la, c'est tout."),
            _p("diane", "Il a appelé la police, évidemment. Par principe, lui aussi.", 1,
               jeu="[wryly] Il a appelé la police, évidemment. [calm] Par principe, lui aussi."),
            _p("diane", "Devant le dépanneur, en face des pompes. C'est là qu'on me voit le mieux.", 2,
               jeu="[confident] Devant le dépanneur, en face des pompes. [wryly] C'est là qu'on me voit le mieux.")
        ],
        "fin": [
            _l("diane", "Pas une bosse. Vous conduisez mieux que mon chauffeur, et vous parlez moins.",
               jeu="[satisfied] Pas une bosse. [wryly] Vous conduisez mieux que mon chauffeur, et vous parlez moins."),
            _l("diane", "Pour votre peine. Et quand je serai mairesse, le lot aura un nouveau règlement.",
               jeu="[calm] Pour votre peine. [confident] Et quand je serai mairesse, le lot aura un nouveau règlement.")
        ],
        "echec": [
            _l("diane", "Ma berline est encore au lot. Je vais devoir payer l'amende. Quelle humiliation.",
               jeu="[disappointed] Ma berline est encore au lot. Je vais devoir payer l'amende. [coldly] Quelle humiliation.")
        ]
    }
}
