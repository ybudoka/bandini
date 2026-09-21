"""La mission m6 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "m6", "titre": "Le tour du propriétaire", "donneur": "josee", "prerequis": ["m5"],
    "recompense": 300, "phase": 1, "echec": ["mort", "arrete"],
    "donne": {"message": "QUATRE CONTACTS AU TÉLÉPHONE",
              "contacts": ["tipaul", "lulu", "raymonde", "ovila"]},
    # Le tour de Josée : quatre districts, quatre portes, du dépanneur au
    # phare. Chaque objectif `parler` nomme sa CIBLE — ce qu'on accomplit en
    # lui parlant, jamais en s'approchant de sa tuile (`Histoire` lit la cible).
    "objectifs": [
        {"type": "parler", "cible": "tipaul", "texte": "PARLE À TI-PAUL, AU DÉPANNEUR"},
        {"type": "parler", "cible": "lulu", "texte": "PARLE À LULU, À LA CANTINE"},
        {"type": "parler", "cible": "raymonde", "texte": "PARLE À RAYMONDE, À L'USINE"},
        {"type": "parler", "cible": "ovila", "texte": "PARLE À OVILA, AU PHARE"},
    ],
    # Josée parle dedans, et la caméra sort voir LES QUATRE PORTES du tour, chacune
    # quand elle la nomme. Il n'y a pas d'objectif `retourner` — la mission se clôt
    # après le dernier contact, et Josée est loin : la fin se dit donc au combiné.
    # ⚠️ Elle n'écrit QUE son intro. Sa fin — une coupe chez Josée, qui est loin : elle
    # parle au combiné — est celle que `scene_par_defaut` bâtit, mot pour mot, et elle
    # est effacée.
    #
    # ⚠️ **LES TEMPS SONT CEUX DES VOIX** (mesurés le 20 sept. 2026 sur `josee-m6-2` et
    # `-3`, 60 images = 1 s) : la réplique 1 dure 362 images, Ti-Paul y est nommé à
    # l'image 141 et Lulu à la 242 ; la 2 dure 282, Raymonde y est nommé d'entrée et Ovila
    # à la 164. Chaque coupe vit donc SOUS sa réplique — et lui survit de quelques images :
    # c'est la coupe qui retient la scène, et une réplique qui a besoin de plus de temps
    # que la coupe est COUPÉE par la suivante (elle l'était : l'ancienne coupe, 230 images
    # pour une réplique de 362). D'où les deux `attendre` : ils laissent finir la phrase, avec
    # de quoi absorber une voix qui met du temps à arriver.
    # Un tronçon d'une coupe = `ferme` + `ouvre` + `tient` ; deux lieux + le retour = 2 × le
    # tronçon + `ferme` + `ouvre`, soit 258 images pour la première coupe, 304 pour la seconde.
    # ⚠️ Si une voix change de durée, c'est ici qu'on recale — et `test_le_tour_du_proprietaire_
    # montre_ses_quatre_contacts` dit quand la caméra n'est plus sur la bonne porte.
    "scenes": {
        "intro": [
            # « Quatre coins, quatre personnes » : Josée parle dans le bar, on la voit.
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "attendre", "duree": 100},
            # « Ti-Paul au dépanneur » (image 141), puis « ma sœur Lulu à la cantine » (242).
            {"type": "coupe", "vers": ["chez:tipaul", "chez:lulu"], "ferme": 14, "ouvre": 14, "tient": 87},
            {"type": "attendre", "duree": 70},
            # « Raymonde à l'usine » (0), puis « Ovila garde le phare » (164).
            {"type": "dire", "repliques": [2], "ensemble": True},
            {"type": "coupe", "vers": ["chez:raymonde", "chez:ovila"], "ferme": 14, "ouvre": 14, "tient": 110},
            {"type": "attendre", "duree": 60},
            # « Va leur serrer la main » : Josée, de retour dans le bar, montre la sortie.
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
    },
    "dialogue": {
        "appel": [_l("josee", "Josée. Le Faubourg est à nous. Viens au bar, je te présente la ville.")],
        "intro": [
            _l("josee", "Quatre coins, quatre personnes. Ti-Paul au dépanneur, ma sœur Lulu à la cantine."),
            _l("josee", "Raymonde tient le syndicat à l'usine, pis Ovila garde le phare."),
            _l("josee", "Va leur serrer la main. Dans cette ville, tout commence par là."),
        ],
        "fin": [
            _l("josee", "Quatre poignées de main. Le monde va t'appeler par ton nom, astheure."),
            _l("josee", "Garde l'œil ouvert. Il se passe plus de choses que t'en penses."),
        ],
        "echec": [_l("josee", "Tu reviendras quand tu auras le temps de faire le tour.")],
        "pendant": [_p("josee", "Le dépanneur d'abord. Ti-Paul en sait plus qu'il en a l'air.", 0)],
        # La poignée de main, dite : un mot de chacun, dans son registre — le bavard (il « en sait plus »),
        # la sœur qui materne, la syndicaliste qui jauge, le gardien qui guette. Elles se comptent APRÈS
        # `pendant` (`PARTIES`) : `tipaul-m6-9`, `lulu-m6-10`, `raymonde-m6-11`, `ovila-m6-12`.
        "accueil": [
            _a("tipaul", "Ah, c'est toi, le nouveau de Josée! Ici, rien passe sans que je le sache.", 0),
            _a("lulu", "Josée m'a parlé de toi. Assis-toi, mange un peu, t'as l'air d'un fantôme.", 1),
            _a("raymonde", "Le syndicat, c'est moi. Josée se porte garante de toi, ça reste à voir.", 2),
            _a("ovila", "Les lumières du port, c'est moi. Depuis ici, je vois tout ce qui entre.", 3),
        ],
    },
}
