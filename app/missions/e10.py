"""La mission e10 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e10",
    "titre": "Diane veut la paix",
    "donneur": "diane",
    "prerequis": ["e04", "e07"],
    "recompense": 600,
    # ⚠️ LA DEUXIÈME LIBÉRATION (`libere: erables`) : les Chevreuils rangent leurs chars — plus un ne traîne dans
    # leur coin (`Entites.gangChasse`), ni ne prend ou ne perd un coin la nuit (`Territoires.horsJeu`), et ce
    # qu'ils avaient pris ailleurs revient (`Territoires.liberer`) ; leur cour redevient « Les Érables ».
    "donne": {"libere": "erables", "manchette": "erables_liberes", "message": "LES ÉRABLES SONT LIBRES"},

    # Deux coins des Chevreuils à vider (`coins: 2`, trois hommes chacun, autour de leur cour — loin du dépanneur
    # où la fin se dit), puis leur chef, qui vient à toi : c'est Jo, parti se cacher chez les siens après e04
    # (`parti_apres`). La police arrive ; on revient voir Diane, qui comprend avant qu'on parle.
    "objectifs": [
        {"type": "tuer", "texte": "VIDE LES DEUX COINS DES CHEVREUILS",
         "groupe": "chevreuils", "n": 6, "coins": 2, "ou": "zone:chevreuils"},

        {"type": "tuer", "texte": "LEUR CHEF ARRIVE — COUCHE-LE",
         "groupe": "chevreuils", "n": 1, "chef": True},

        {"type": "semer", "texte": "LES VOISINS ONT APPELÉ LA POLICE — SÈME-LA",
         "etoiles": 2},

        {"type": "retourner", "texte": "REVIENS VOIR DIANE, AU DÉPANNEUR"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Diane : la paix, et le pouvoir — jusqu'à ce que le chef couché ait un
    # nom. Elle a tout prévu sauf ça. La politicienne reste droite dans les mots ; la voix, elle, casse une fois,
    # à la fin, et se reprend tout de suite.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Le conseil vote la paix dans les Érables jeudi. Aidez-moi à la rendre vraie.",
               jeu="[confident] Diane Larivière. [serious] Le conseil vote la paix dans les Érables jeudi. [firmly] Aidez-moi à la rendre vraie.")
        ],
        "intro": [
            _l("diane", "Les Chevreuils tiennent deux coins derrière le boulevard. Je les veux vides.",
               jeu="[matter-of-fact] Les Chevreuils tiennent deux coins derrière le boulevard. [coldly] Je les veux vides."),
            _l("diane", "Ensuite, leur chef viendra. Il vient toujours quand on touche à ses gars.",
               jeu="[calm] Ensuite, leur chef viendra. [knowingly] Il vient toujours… quand on touche à ses gars."),
            _l("diane", "Ne me dites pas son nom. Je ne veux pas le savoir avant jeudi.",
               jeu="[quietly] Ne me dites pas son nom. [serious] Je ne veux pas le savoir… avant jeudi.")
        ],
        "pendant": [
            _p("diane", "Deux coins, six garçons. Des enfants de bonne famille qui jouent aux bandits.", 0,
               jeu="[coldly] Deux coins, six garçons. [bitterly] Des enfants de bonne famille… qui jouent aux bandits."),
            _p("diane", "Le voilà. Faites vite, je vous en prie.", 1,
               jeu="[nervously] Le voilà. [quietly] Faites vite… je vous en prie."),
            _p("diane", "Les voisins ont appelé la police. Évidemment, ce soir, ils sont réveillés.", 2,
               jeu="[wryly] Les voisins ont appelé la police. [annoyed] Évidemment, ce soir, ils sont réveillés."),
            _p("diane", "Revenez au dépanneur. Seul.", 3,
               jeu="[somber] Revenez au dépanneur. [quietly] Seul.")
        ],
        "fin": [
            _l("diane", "C'était Jo. Je le savais depuis le dossier. Je voulais me tromper.",
               jeu="[somber] C'était Jo. [quietly] Je le savais depuis le dossier. [sighs] Je voulais me tromper."),
            _l("diane", "Il va s'en remettre, et il va m'en vouloir. Les Érables, eux, vont dormir.",
               jeu="[softly] Il va s'en remettre… et il va m'en vouloir. [firmly] Les Érables, eux, vont dormir."),
            _l("diane", "Jeudi, je vote la paix. Personne ne saura ce qu'elle m'a coûté.",
               jeu="[confident] Jeudi, je vote la paix. [bitterly] Personne ne saura ce qu'elle m'a coûté.")
        ],
        "echec": [
            _l("diane", "Les Chevreuils tiennent encore. Jeudi, je voterai contre moi-même.",
               jeu="[disappointed] Les Chevreuils tiennent encore. [bitterly] Jeudi, je voterai contre moi-même.")
        ]
    }
}
