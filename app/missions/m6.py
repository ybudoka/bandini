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
    #
    # « Des missions plus longues » (22 sept. 2026) : chaque coin a son épreuve, et on revient au bar.
    # Ti-Paul, qui « sait tout ce qui passe », a un pickpocket dans son parking — on lui fait goûter sa
    # médecine (l'archétype `pickpocket`, jamais un homme de gang : `Combat.pochesAPrendre` le
    # refuserait). Raymonde « verra » : trois Boulonneux viennent brasser son piquet, ils ARRIVENT
    # (`loin`), les poings nus. Ovila, lui, voit une auto sans phares rôder au Brouillard — on y
    # retourne, et Josée a la réponse (c'est la sienne). ⚠️ Pas d'objectif `lieu: "usine"` : la
    # cour ferme la nuit (`test_barrieres.py`) ; la bagarre se pose autour du joueur.
    "objectifs": [
        {"type": "parler", "cible": "tipaul", "texte": "PARLE À TI-PAUL, AU DÉPANNEUR"},
        {"type": "pickpocket", "cible": "pickpocket", "texte": "VIDE LES POCHES DU PICKPOCKET DE TI-PAUL"},
        {"type": "parler", "cible": "lulu", "texte": "PARLE À LULU, À LA CANTINE"},
        {"type": "parler", "cible": "raymonde", "texte": "PARLE À RAYMONDE, À L'USINE"},
        {"type": "tuer", "groupe": "boulonneux", "n": 3, "arme": "", "vie": 80, "loin": 12,
         "texte": "REPOUSSE LES BOULONNEUX DU PIQUET"},
        {"type": "parler", "cible": "ovila", "texte": "PARLE À OVILA, AU PHARE"},
        {"type": "aller", "lieu": "bar", "rayon": 6, "texte": "RETOURNE AU BROUILLARD"},
    ],
    # Josée parle dedans, et la caméra sort voir LES QUATRE PORTES du tour, chacune
    # quand elle la nomme. Il n'y a pas d'objectif `retourner` (Josée est dedans, `point:` :
    # il ne la trouverait jamais) — la mission se clôt à la porte du Brouillard : la fin se
    # dit au combiné, par une coupe chez elle.
    # ⚠️ Elle n'écrit QUE son intro. Sa fin — une coupe chez Josée — est celle que
    # `scene_par_defaut` bâtit, mot pour mot, et elle est effacée.
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
    # Le jeu de chaque réplique (`jeu=`) — Josee presente la ville : plus chaude qu'a M5, elle donne des noms ;
    # à la fin, froide de nouveau : l'auto sans phares est la sienne. Ti-Paul jubile, Raymonde jauge, Ovila
    # chuchote ce qu'il a « vu ».
    "dialogue": {
        "appel": [_l("josee", "Josée. Le Faubourg est à nous. Viens au bar, je te présente la ville.",
                     jeu="[confident] Josée. Le Faubourg est à nous. Viens au bar… je te présente la ville.")],
        "intro": [
            _l("josee", "Quatre coins, quatre personnes. Ti-Paul au dépanneur, ma sœur Lulu à la cantine.",
               jeu="[matter-of-fact] Quatre coins, quatre personnes. Ti-Paul au dépanneur… ma sœur Lulu à la cantine."),
            _l("josee", "Raymonde tient le syndicat à l'usine, pis Ovila garde le phare.",
               jeu="[matter-of-fact] Raymonde tient le syndicat à l'usine… pis Ovila garde le phare."),
            _l("josee", "Va leur serrer la main. Dans cette ville, tout commence par là.",
               jeu="[warmly] Va leur serrer la main… Dans cette ville, tout commence par là."),
        ],
        "fin": [
            _l("josee", "Quatre poignées de main. Le monde va t'appeler par ton nom, astheure.",
               jeu="[satisfied] Quatre poignées de main. [warmly] Le monde va t'appeler par ton nom… astheure."),
            _l("josee", "L'auto sans phares? Je sais. Elle est à moi.",
               jeu="[knowingly] L'auto sans phares? Je sais. [coldly] Elle est à moi."),
            _l("josee", "Garde l'œil ouvert. Il se passe plus de choses que t'en penses.",
               jeu="[mysteriously] Garde l'œil ouvert… Il se passe plus de choses que t'en penses."),
        ],
        "echec": [_l("josee", "Tu reviendras quand tu auras le temps de faire le tour.",
                     jeu="[disappointed] Tu reviendras… quand tu auras le temps de faire le tour.")],
        "pendant": [
            _p("josee", "Le dépanneur d'abord. Ti-Paul en sait plus qu'il en a l'air.", 0,
               jeu="[knowingly] Le dépanneur d'abord. Ti-Paul en sait plus… qu'il en a l'air."),
            _p("tipaul", "Tu vois le gars qui colle mes clients? Il travaille mon parking. Vide-lui les poches, pour voir!", 1,
               jeu="[mischievously] Tu vois le gars qui colle mes clients? Il travaille mon parking. [cheerful] Vide-lui les poches, pour voir!"),
            _p("tipaul", "T'as des doigts de fée, l'ami! Va manger chez Lulu, aux Quais : c'est le pickpocket qui paye.", 2,
               jeu="[impressed] T'as des doigts de fée, l'ami! [laughs] Va manger chez Lulu, aux Quais : c'est le pickpocket qui paye."),
            _p("raymonde", "Les Boulonneux viennent brasser mon piquet tous les soirs. Montre-moi ce que Josée voit en toi.", 4,
               jeu="[firmly] Les Boulonneux viennent brasser mon piquet tous les soirs. [wryly] Montre-moi ce que Josée voit en toi."),
            _p("raymonde", "Pas pire. Ovila, au phare, va vouloir te voir. Dis-y que le syndicat le salue.", 5,
               jeu="[matter-of-fact] Pas pire. Ovila, au phare, va vouloir te voir. [warmly] Dis-y que le syndicat le salue."),
            _p("ovila", "Pardonnez-moi. Une auto sans phares tourne autour du Brouillard depuis une heure.", 6,
               jeu="[softly] Pardonnez-moi. [mysteriously] Une auto sans phares tourne autour du Brouillard… depuis une heure."),
        ],
        # La poignée de main, dite : un mot de chacun, dans son registre — le bavard (il « en sait plus »),
        # la sœur qui materne, la syndicaliste qui jauge, le gardien qui guette. Elles se comptent APRÈS
        # `pendant` (`PARTIES`) : `tipaul-m6-15`, `lulu-m6-16`, `raymonde-m6-17`, `ovila-m6-18` depuis
        # « Des missions plus longues » (une fin et cinq `pendant` de plus devant elles ; leurs mp3
        # d'avant, `-9` à `-12`, se renomment d'après qui, mission et texte).
        "accueil": [
            _a("tipaul", "Salut, l'ami! Moi, c'est Ti-Paul, pis toi, t'es le nouveau de Josée? Ici, rien passe sans que je le sache.", 0,
               jeu="[cheerful] Salut, l'ami! Moi, c'est Ti-Paul, pis toi, t'es le nouveau de Josée? [knowingly] Ici, rien passe… sans que je le sache."),
            _a("lulu", "Allô, mon grand! Moi, c'est Lulu, la sœur de Josée. Assis-toi, mange, t'as l'air d'un fantôme.", 2,
               jeu="[warmly] Allô, mon grand! Moi, c'est Lulu, la sœur de Josée. [teasing] Assis-toi, mange… t'as l'air d'un fantôme."),
            _a("raymonde", "Raymonde Fortin, présidente du syndicat. Josée se porte garante de toi, ça reste à voir.", 3,
               jeu="[firmly] Raymonde Fortin, présidente du syndicat. Josée se porte garante de toi… ça reste à voir."),
            _a("ovila", "Ovila Saint-Onge, pour vous servir. Les lumières du port, c'est moi. D'ici, je vois tout ce qui entre.", 5,
               jeu="[calm] Ovila Saint-Onge, pour vous servir. Les lumières du port, c'est moi… D'ici, je vois tout ce qui entre."),
        ],
    },
}
