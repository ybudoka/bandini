"""La mission p02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p02",
    "titre": "Le pont est bloqué",
    "donneur": "bilodeau",
    # ⚠️ Après p01 et pas m6 : M. Bilodeau n'est devant le phare qu'une fois la lampe réparée (`arrive_apres`), et
    # ça garde le téléphone calme.
    "prerequis": ["p01"],
    "recompense": 150,
    "donne": {"message": "LE PONT DE LA POINTE EST OUVERT"},

    # Les Skateux ont fermé le seul pont avec des cônes : trois gars dessus, puis leur grand, un cône à la main
    # (`arme: cone` — le cône orange est une arme du catalogue). Au pont, loin du phare où la fin se dit.
    "objectifs": [
        {"type": "tuer", "texte": "LES SKATEUX BLOQUENT LE PONT — DÉGAGE-LES",
         "groupe": "skateux", "n": 3, "ou": "pont"},

        {"type": "tuer", "texte": "LEUR GRAND ARRIVE AVEC UN CÔNE — COUCHE-LE",
         "groupe": "skateux", "n": 1, "chef": True, "arme": "cone"},

        {"type": "retourner", "texte": "RETOURNE VOIR M. BILODEAU, AU PHARE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — M. Bilodeau : un vieux monsieur poli qui s'emporte contre « la jeunesse »,
    # puis qui a honte de s'être emporté. Il vouvoie, il dit « monsieur », il parle de sa femme.
    "dialogue": {
        "appel": [
            _l("bilodeau", "Roméo Bilodeau, du bout de La Pointe. Les jeunes ont fermé le pont, monsieur. Avec des cônes!",
               jeu="[annoyed] Roméo Bilodeau, du bout de La Pointe. [gruffly] Les jeunes ont fermé le pont, monsieur. Avec des cônes!")
        ],
        "intro": [
            _l("bilodeau", "C'est le seul pont. Ma femme a son rendez-vous chez le docteur jeudi.",
               jeu="[worried] C'est le seul pont. [softly] Ma femme a son rendez-vous chez le docteur jeudi."),
            _l("bilodeau", "Ils demandent deux piastres pour passer. Deux piastres! Pour un pont municipal!",
               jeu="[angry] Ils demandent deux piastres pour passer. [shouting] Deux piastres! [gruffly] Pour un pont municipal!"),
            _l("bilodeau", "Pardon. Je m'emporte. Allez leur parler, vous, vous avez l'âge.",
               jeu="[sighs] Pardon. Je m'emporte. [warmly] Allez leur parler, vous… vous avez l'âge.")
        ],
        "pendant": [
            _p("bilodeau", "Les voyez-vous? Trois, sur le pont, avec leurs planches à roulettes.", 0,
               jeu="[nervously] Les voyez-vous? [annoyed] Trois, sur le pont, avec leurs planches à roulettes."),
            _p("bilodeau", "Le grand arrive! Il a un cône, monsieur, faites attention!", 1,
               jeu="[worried] Le grand arrive! [shouting] Il a un cône, monsieur, faites attention!"),
            _p("bilodeau", "Revenez au phare. J'ai du café, pis des biscuits de ma femme.", 2,
               jeu="[relieved] Revenez au phare. [warmly] J'ai du café, pis des biscuits de ma femme.")
        ],
        "fin": [
            _l("bilodeau", "Le pont est ouvert. Ma femme va pouvoir aller chez son docteur.",
               jeu="[relieved] Le pont est ouvert. [tenderly] Ma femme va pouvoir aller chez son docteur."),
            _l("bilodeau", "Prenez un biscuit. Deux. Vous les avez gagnés, monsieur.",
               jeu="[warmly] Prenez un biscuit. Deux. [amused] Vous les avez gagnés, monsieur.")
        ],
        "echec": [
            _l("bilodeau", "Le pont est encore fermé. Ma femme va manquer son rendez-vous.",
               jeu="[disappointed] Le pont est encore fermé. [somber] Ma femme va manquer son rendez-vous.")
        ]
    }
}
