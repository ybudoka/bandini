"""Le chapitre de l'ambulance de nuit — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague H). L'hôpital
commence par deux missions qui se suivent : h01 (le Dr Lachance, trois transports de nuit et le gardien du phare)
et h02 (Ginette, le commis qui vide la pharmacie) — six et cinq étapes. Deux ACTES d'une même nuit à l'urgence :
on rend les clés à Ginette, et c'est elle qui a la suite. Rien d'ajouté pour faire durer : la nuit à attendre, trois
transports et une filature tiennent déjà la visée (6 à 8 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de h01
  restent ceux du chapitre ; sa fin (le Dr Lachance) se dit à l'ouverture de l'acte 2, suivie de l'appel et de
  l'intro de Ginette ; la fin de h02 reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : Ginette se nomme en rendant les clés (« Moi, c'est Ginette ») ; son
  appel de h02 perd « C'est Ginette, de l'hôpital » — la même voix, coupée au silence ;
- l'échec `vehicule_detruit` de h01 (l'ambulance) vaut pour le chapitre : la filature de h02 ne prend aucun char ;
- la scène d'intro de h01 reste celle du chapitre.
- h03 attend h02 (le dernier acte) : le chapitre suivant, _La dette du docteur_, l'attend.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "ambulance_de_nuit",
    "titre": "L'ambulance de nuit",
    "donneur": "lachance",
    "prerequis": ["m6"],
    "remplace": ["h01", "h02"],
    "recompense": 250,
    "donne": {"message": "LA PHARMACIE EST AU COMPLET"},
    "echec": ["mort", "arrete", "vehicule_detruit"],

    "objectifs": [
        # --- Acte 1 (h01, « L'ambulance de nuit »).
        {"type": "acte", "texte": "ACTE 1 — L'AMBULANCE DE NUIT", "donneur": "lachance"},  # 0
        {"type": "aller", "texte": "VA À L'HÔPITAL ET ATTENDS LA NUIT", "lieu": "hopital", "rayon": 6, "nuit": True},  # 1
        {"type": "monter", "texte": "MONTE DANS L'AMBULANCE", "vehicule": "ambulance", "ou": "porte:hopital"},  # 2
        {"type": "boulots", "texte": "FAIS TROIS TRANSPORTS, DE NUIT", "n": 3, "sorte": "ambulance"},  # 3
        {"type": "aller", "texte": "URGENCE AU PHARE DE LA POINTE — FONCE", "lieu": "phare", "rayon": 5},  # 4
        {"type": "livrer", "texte": "RAMÈNE LE GARDIEN À L'URGENCE", "lieu": "hopital", "rayon": 5},  # 5
        {"type": "parler", "texte": "RENDS LES CLÉS À GINETTE, À L'ENTRÉE", "cible": "ginette", "donne": {"message": "LE BOULOT AMBULANCE, AU KLAXON", "prime": 300}},  # 6
        # --- Acte 2 (h02, « Les pilules »).
        {"type": "acte", "texte": "ACTE 2 — LES PILULES", "donneur": "ginette"},  # 7
        {"type": "suivre", "texte": "SUIS-LE SANS TE FAIRE REPÉRER", "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "depanneur"},  # 8
        {"type": "parler", "texte": "FAIS JASER TI-PAUL SUR LE COMMIS", "cible": "tipaul"},  # 9
        {"type": "pickpocket", "texte": "REPRENDS LES PILULES, PAR-DERRIÈRE", "cible": "pickpocket"},  # 10
        {"type": "semer", "texte": "IL CRIE AU VOLEUR — SÈME LA POLICE", "etoiles": 1},  # 11
        {"type": "retourner", "texte": "RAPPORTE-LES À GINETTE"},  # 12
    ],

    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # h01 — Le jeu de chaque réplique (`jeu=`) — Dr Lachance : clinique et posé, jamais de
    # panique dans la voix, même fatigué — le ton d'une salle d'urgence qui roule
    # depuis trop longtemps.
    # h02 — Le jeu de chaque réplique (`jeu=`) — Ginette : sèche, elle sait tout ce qui se
    # passe dans son hôpital et n'a pas de patience pour ceux qui en profitent.
    "dialogue": {
        "appel": [
            _l("lachance", "Ici le docteur Lachance, de l'hôpital. J'ai besoin d'une ambulance en état de rouler, cette nuit.", jeu="[calm] Ici le docteur Lachance, de l'hôpital. [gravely] J'ai besoin d'une ambulance en état de rouler… cette nuit."),
        ],
        "intro": [
            _l("lachance", "L'urgence manque de bras entre minuit et six heures. Trois transports, pas plus.", jeu="[matter-of-fact] L'urgence manque de bras entre minuit et six heures. [firmly] Trois transports… pas plus."),
            _l("lachance", "Klaxonne pour prendre chaque blessé. Conduis vite, mais conduis droit.", jeu="[gravely] Klaxonne pour prendre chaque blessé. [firmly] Conduis vite, mais conduis droit."),
        ],
        "fin": [
            _l("ginette", "Toutes là. Ce commis-là ne remettra plus les pieds dans ma pharmacie.", jeu="[satisfied] Toutes là. [firmly] Ce commis-là ne remettra plus les pieds dans ma pharmacie."),
            _l("ginette", "Bon travail. L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin.", jeu="[matter-of-fact] Bon travail. [warmly] L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin."),
            _l("ginette", "Pis si Ti-Paul dort mal, dis-y que ses vitrines, c'est pas mon département.", jeu="[wryly] Pis si Ti-Paul dort mal, dis-y que ses vitrines… [matter-of-fact] c'est pas mon département."),
        ],
        "echec": [
            _e("lachance", "On fera avec ce qu'on a... Reviens si tu peux, une autre nuit.", 0, jeu="[somber] On fera avec ce qu'on a… [calm] Reviens si tu peux, une autre nuit."),
            _e("ginette", "Perdues... Il va continuer à vider mes tablettes. Reviens quand t'es prêt.", 7, jeu="[disappointed] Perdues… [annoyed] Il va continuer à vider mes tablettes. Reviens quand t'es prêt."),
        ],
        "pendant": [
            _p("lachance", "Un blessé qui attend trop longtemps, on ne le récupère pas au triage.", 3, jeu="[gravely] Un blessé qui attend trop longtemps… [serious] on ne le récupère pas au triage."),
            _p("lachance", "Je sais, j'avais dit trois. Le gardien du phare a déboulé son escalier, lui, il compte pas.", 4, jeu="[wryly] Je sais, j'avais dit trois. [matter-of-fact] Le gardien du phare a déboulé son escalier… lui, il compte pas."),
            _p("lachance", "Il a une jambe cassée, pas besoin de lui casser l'autre. Évite les nids-de-poule.", 5, jeu="[deadpan] Il a une jambe cassée, pas besoin de lui casser l'autre. [firmly] Évite les nids-de-poule."),
            # Acte 2 : la fin de h01, en personne ; puis l'appel et l'intro de h02.
            _p("lachance", "Trois de plus qui dorment dans un vrai lit, cette nuit. Ça compte.", 7, jeu="[relieved] Trois de plus qui dorment dans un vrai lit, cette nuit. [calm] Ça compte.", cloture=True),
            _p("lachance", "L'hôpital te doit une faveur. Reviens si tu en as besoin.", 7, jeu="[matter-of-fact] L'hôpital te doit une faveur. [warmly] Reviens si tu en as besoin.", cloture=True),
            _p("lachance", "Le gardien du phare te fait dire merci. Il boite, mais il le dit.", 7, jeu="[matter-of-fact] Le gardien du phare te fait dire merci. [wryly] Il boite… mais il le dit.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Ginette, de l'hôpital. » — elle s'est nommée en prenant les clés.
            _p("ginette", "Un commis vide notre pharmacie depuis des semaines. J'ai besoin de toi.", 7, jeu="[annoyed] Un commis vide notre pharmacie depuis des semaines. [firmly] J'ai besoin de toi."),
            _p("ginette", "Il sort dans dix minutes. Suis-le sans qu'il te voie, il va vendre ça au dépanneur.", 7, jeu="[matter-of-fact] Il sort dans dix minutes. [firmly] Suis-le sans qu'il te voie… il va vendre ça au dépanneur."),
            _p("ginette", "Une fois la vente faite, reprends nos pilules par-derrière. Discret, comme toujours.", 7, jeu="[knowingly] Une fois la vente faite, reprends nos pilules par-derrière. [quietly] Discret, comme toujours."),
            _p("ginette", "S'il crie au voleur, cours pas. Cache-toi, pis attends que ça passe.", 7, jeu="[firmly] S'il crie au voleur, cours pas. [quietly] Cache-toi… pis attends que ça passe."),
            _p("ginette", "Il regarde dans son rétroviseur souvent. Garde tes distances.", 8, jeu="[gravely] Il regarde dans son rétroviseur souvent. [firmly] Garde tes distances."),
            _p("ginette", "Il est rentré chez Ti-Paul. Va voir ce qu'il lui vend, l'air de rien.", 9, jeu="[knowingly] Il est rentré chez Ti-Paul. [quietly] Va voir ce qu'il lui vend… l'air de rien."),
            _p("ginette", "Il crie au voleur, lui? Ça prend du front. Perds la police, pis reviens.", 11, jeu="[annoyed] Il crie au voleur, lui? [sarcastic] Ça prend du front. [firmly] Perds la police, pis reviens."),
        ],
        "accueil": [
            _a("ginette", "Moi, c'est Ginette, l'infirmière-chef. Les clés, pis va dormir, t'as une face de garde de nuit.", 6, jeu="[matter-of-fact] Moi, c'est Ginette, l'infirmière-chef. [firmly] Les clés… pis va dormir, [wryly] t'as une face de garde de nuit."),
            _a("tipaul", "Ton commis? Y m'offre des pilules pour dormir, l'ami. Avec mes vitrines, je dors pas pareil!", 9, jeu="[knowingly] Ton commis? Y m'offre des pilules pour dormir, l'ami. [cheerful] Avec mes vitrines… je dors pas pareil!"),
        ],
    },
}
