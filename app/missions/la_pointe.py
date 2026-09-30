"""Le chapitre de La Pointe — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ LE PREMIER CHAPITRE (30 sept. 2026, docs/jalons/des-missions-en-chapitres.md). Martin : « les missions doivent
durer au moins 5 à 10 minutes chacune ». Les six missions de La Pointe (p02, p05, p04, p10, p09, p11 — deux à trois
étapes chacune, moins de deux minutes) deviennent six ACTES d'une seule histoire, du pont bloqué à la paix signée
au Brouillard. Chaque acte s'ouvre par un marqueur `acte` (son carton, son donneur, le point de reprise) ; mourir
ou se faire pogner fait reprendre à l'acte, pas au pont.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées MOT POUR MOT (et leurs voix payées, renommées) : l'appel et l'intro de p02
  restent l'appel et l'intro du chapitre ; l'appel et l'intro des cinq autres se disent à l'ouverture de LEUR acte
  (un `pendant` sur le marqueur : le donneur suivant appelle) ; leur fin se dit à l'ouverture de l'acte SUIVANT,
  en personne, juste après le `retourner` ; la fin de p11 reste la fin du chapitre ;
- chaque acte donne ce que sa mission donnait (`donne` sur l'objectif qui le finit), sa PRIME comprise : la fronde
  du Trappeur, le respect des Skateux, la manchette du phare ; la libération de La Pointe reste celle du chapitre ;
- ce qui fait durer : des renforts au pont, le phare à TENIR 90 s contre trois vagues, une auto de Skateux qui
  vous colle jusqu'au Brouillard ;
- l'appel de p10 perd « Yo, c'est Zed » (il est à côté de toi, il vient de courir) ; l'échec est neuf (celui du
  pont n'allait pas au phare) ; `frontiere: pointe` de p05 tombe (l'acte 6 va au Brouillard) ; les scènes d'intro
  écrites de p09 et p11 aussi (leurs intros se disent au téléphone, à l'ouverture de l'acte).
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "la_pointe",   # ⚠️ pas « pointe » : c'est le nom du district, que le code nomme
    "titre": "La Pointe",
    "donneur": "bilodeau",
    # ⚠️ Après p01 : M. Bilodeau n'est devant le phare qu'une fois la lampe réparée (`arrive_apres`).
    "prerequis": ["p01"],
    "remplace": ["p02", "p05", "p04", "p10", "p09", "p11"],
    # La prime de p11 : chaque acte d'avant paie la sienne en finissant (`donne.prime`) — une vieille partie qui avait
    # fait p02 ne la touche pas deux fois.
    "recompense": 500,
    "donne": {"libere": "pointe", "manchette": "pointe_liberee", "message": "LA POINTE EST LIBRE"},

    "objectifs": [
        # --- Acte 1 (p02) : le pont bloqué.
        {"type": "acte", "texte": "ACTE 1 — LE PONT EST BLOQUÉ", "donneur": "bilodeau"},                      # 0
        {"type": "tuer", "texte": "LES SKATEUX BLOQUENT LE PONT — DÉGAGE-LES",
         "groupe": "skateux", "n": 3, "ou": "pont", "renforts": {"vagues": 1, "n": 2}},                        # 1
        {"type": "tuer", "texte": "LEUR GRAND ARRIVE AVEC UN CÔNE — COUCHE-LE",
         "groupe": "skateux", "n": 1, "chef": True, "arme": "cone"},                                           # 2
        {"type": "retourner", "texte": "RETOURNE VOIR M. BILODEAU, AU PHARE",
         "donne": {"prime": 150, "message": "LE PONT DE LA POINTE EST OUVERT"}},                                             # 3

        # --- Acte 2 (p05) : les collets du Trappeur, de nuit.
        {"type": "acte", "texte": "ACTE 2 — LES COLLETS DU TRAPPEUR", "donneur": "trappeur",
         "sur_place": {"lieu": "phare", "heure": "nuit"}},                                                     # 4
        {"type": "aller", "texte": "ATTENDS LA NUIT PRÈS DU PHARE",
         "lieu": "phare", "rayon": 6, "nuit": True},                                                           # 5
        # ⚠️ Pas `ou: bois` (la carte n'a plus le glyphe du bois : ils naissaient sur le joueur) — voir p05.
        {"type": "tuer", "texte": "DEUX SKATEUX RELÈVENT SES COLLETS — COUCHE-LES",
         "groupe": "skateux", "n": 2, "ou": "zone:skateux"},                                                   # 6
        {"type": "retourner", "texte": "RETOURNE VOIR LE TRAPPEUR",
         "donne": {"prime": 120, "arme": "fronde", "message": "LA FRONDE DU TRAPPEUR, ET SES BILLES"}},                       # 7

        # --- Acte 3 (p04) : la course de Zed, à pied, contre son temps.
        {"type": "acte", "texte": "ACTE 3 — ZED VEUT UN DÉFI", "donneur": "zed"},                              # 8
        {"type": "course", "texte": "BATS LE TEMPS DE ZED, À PIED",
         "points": ["zone:skateux", "foire", "pont", "phare"], "a_pied": True, "chrono_s": 80},                # 9
        {"type": "retourner", "texte": "RETOURNE VOIR ZED, DEVANT LE PHARE",
         "donne": {"prime": 200, "calme": "skateux", "message": "LES SKATEUX TE RESPECTENT"}},                               # 10

        # --- Acte 4 (p10) : le saut, sur la machine de Zed (une motoneige l'hiver).
        {"type": "acte", "texte": "ACTE 4 — LE SAUT DE LA POINTE", "donneur": "zed"},                          # 11
        {"type": "monter", "texte": "MONTE SUR LA MACHINE DE ZED", "vehicule": "moto", "ou": "porte:phare"},   # 12
        {"type": "sauter", "texte": "SAUTE LA RAMPE DES SKATEUX — 80 PX DE VOL",
         "ou": "rampe:pointe", "vol_px": 80},                                                                  # 13
        {"type": "retourner", "texte": "RAMÈNE SA MACHINE À ZED",
         "donne": {"prime": 250, "message": "LES SKATEUX PARLENT DE TON SAUT"}},                                             # 14

        # --- Acte 5 (p09) : le phare s'éteint — le TENIR, puis rallumer avec Ovila.
        {"type": "acte", "texte": "ACTE 5 — LE PHARE S'ÉTEINT", "donneur": "ovila"},                           # 15
        {"type": "tenir", "texte": "DES SKATEUX ONT ÉTEINT LE PHARE — TIENS BON",
         "lieu": "phare", "rayon": 6, "secondes": 90,
         "groupe": "skateux", "n": 3, "renforts": {"vagues": 2, "n": 2}},                                      # 16
        {"type": "parler", "texte": "MONTE RALLUMER LA LAMPE AVEC OVILA", "cible": "ovila",
         "donne": {"prime": 300, "manchette": "phare_a_tenu", "message": "LE PHARE A TENU"}},                                # 17

        # --- Acte 6 (p11) : Zed au Brouillard, une auto de Skateux au pare-chocs ; la paix signée.
        {"type": "acte", "texte": "ACTE 6 — ZED ET LA CHEF", "donneur": "josee"},                              # 18
        {"type": "proteger", "texte": "AMÈNE ZED AU BROUILLARD, SAIN ET SAUF",
         "cible": "zed", "lieu": "bar", "rayon": 5, "poursuite": {"groupe": "skateux", "chars": 1}},           # 19
        {"type": "tuer", "texte": "LES SKATEUX QUI REFUSENT LA PAIX — COUCHE-LES",
         "groupe": "skateux", "n": 3, "ou": "bar", "loin": 10},                                                # 20
    ],

    # Le jeu de chaque réplique (`jeu=`) — celui de sa mission d'origine :
    # - M. Bilodeau : un vieux monsieur poli qui s'emporte contre « la jeunesse », puis a honte ; il vouvoie.
    # - Armand, le Trappeur : l'ermite qui parle bas, parce que le bois écoute ; des phrases de conteur.
    # - Zed : le rieur ; il dit « man », il ricane en finissant ses phrases ; il perd bien.
    # - Ovila : pour une fois, l'urgence ; il ne crie pas, mais il presse.
    # - Josée : elle prend au sérieux un gamin qui rit trop — c'est sa politesse.
    "dialogue": {
        "appel": [
            _l("bilodeau", "Roméo Bilodeau, du bout de La Pointe. Les jeunes ont fermé le pont, monsieur. Avec des cônes!",
               jeu="[annoyed] Roméo Bilodeau, du bout de La Pointe. [gruffly] Les jeunes ont fermé le pont, monsieur. Avec des cônes!"),
        ],
        "intro": [
            _l("bilodeau", "C'est le seul pont. Ma femme a son rendez-vous chez le docteur jeudi.",
               jeu="[worried] C'est le seul pont. [softly] Ma femme a son rendez-vous chez le docteur jeudi."),
            _l("bilodeau", "Ils demandent deux piastres pour passer. Deux piastres! Pour un pont municipal!",
               jeu="[angry] Ils demandent deux piastres pour passer. [shouting] Deux piastres! [gruffly] Pour un pont municipal!"),
            _l("bilodeau", "Pardon. Je m'emporte. Allez leur parler, vous, vous avez l'âge.",
               jeu="[sighs] Pardon. Je m'emporte. [warmly] Allez leur parler, vous… vous avez l'âge."),
        ],
        "fin": [
            _l("josee", "Zed a signé. La Pointe est aux gens de La Pointe, astheure.",
               jeu="[satisfied] Zed a signé. [confident] La Pointe est aux gens de La Pointe, astheure."),
            _l("josee", "Il voulait te dire merci. Il a ri, à la place. C'est pareil, chez lui.",
               jeu="[amused] Il voulait te dire merci. Il a ri, à la place. [warmly] C'est pareil, chez lui."),
        ],
        # Neuf : l'échec de p02 parlait du pont, et un chapitre rate aussi au phare ou au Brouillard.
        "echec": [
            _l("bilodeau", "Ça s'est mal passé, monsieur. Reposez-vous. La Pointe va vous attendre.",
               jeu="[worried] Ça s'est mal passé, monsieur. [softly] Reposez-vous. [warmly] La Pointe va vous attendre."),
        ],
        "pendant": [
            # Acte 1.
            _p("bilodeau", "Les voyez-vous? Trois, sur le pont, avec leurs planches à roulettes.", 1,
               jeu="[nervously] Les voyez-vous? [annoyed] Trois, sur le pont, avec leurs planches à roulettes."),
            # Neuf : les renforts du pont.
            _p("bilodeau", "Il en arrive d'autres par le chemin! Combien sont-ils, cette jeunesse-là?", 1,
               jeu="[worried] Il en arrive d'autres par le chemin! [exasperated] Combien sont-ils, cette jeunesse-là?"),
            _p("bilodeau", "Le grand arrive! Il a un cône, monsieur, faites attention!", 2,
               jeu="[worried] Le grand arrive! [shouting] Il a un cône, monsieur, faites attention!"),
            _p("bilodeau", "Revenez au phare. J'ai du café, pis des biscuits de ma femme.", 3,
               jeu="[relieved] Revenez au phare. [warmly] J'ai du café, pis des biscuits de ma femme."),
            # Acte 2 : la fin de p02, en personne ; puis le Trappeur appelle.
            _p("bilodeau", "Le pont est ouvert. Ma femme va pouvoir aller chez son docteur.", 4,
               jeu="[relieved] Le pont est ouvert. [tenderly] Ma femme va pouvoir aller chez son docteur."),
            _p("bilodeau", "Prenez un biscuit. Deux. Vous les avez gagnés, monsieur.", 4,
               jeu="[warmly] Prenez un biscuit. Deux. [amused] Vous les avez gagnés, monsieur."),
            _p("trappeur", "C'est Armand. Le Trappeur, qu'ils disent en ville. Quelqu'un vole mes collets.", 4,
               jeu="[quietly] C'est Armand. [wryly] Le Trappeur, qu'ils disent en ville… [serious] Quelqu'un vole mes collets."),
            _p("trappeur", "Chaque matin, mes collets sont vides, pis coupés. C'est pas un renard qui a un couteau.", 4,
               jeu="[gravely] Chaque matin, mes collets sont vides, pis coupés. [wryly] C'est pas un renard qui a un couteau."),
            _p("trappeur", "Ils viennent la nuit. Attends la noirceur, pis va voir dans le bois.", 4,
               jeu="[quietly] Ils viennent la nuit. [calm] Attends la noirceur… pis va voir dans le bois."),
            _p("trappeur", "Pas de police. La police, ça fait peur au gibier.", 4,
               jeu="[deadpan] Pas de police. [amused] La police, ça fait peur au gibier."),
            _p("trappeur", "La nuit tombe. Écoute : le bois devient plus fort que la ville.", 5,
               jeu="[softly] La nuit tombe. [mysteriously] Écoute… le bois devient plus fort que la ville."),
            _p("trappeur", "Deux lampes de poche dans le bois. C'est eux. Vas-y doucement.", 6,
               jeu="[quietly] Deux lampes de poche dans le bois. C'est eux. [calm] Vas-y doucement."),
            _p("trappeur", "Reviens au phare. J'ai quelque chose pour toi.", 7,
               jeu="[warmly] Reviens au phare. [mysteriously] J'ai quelque chose pour toi."),
            # Acte 3 : la fin de p05 ; puis Zed appelle.
            _p("trappeur", "Des Skateux. Des enfants de la ville qui jouent aux coureurs des bois.", 8,
               jeu="[wryly] Des Skateux. [bitterly] Des enfants de la ville… qui jouent aux coureurs des bois."),
            _p("trappeur", "Tiens, ma fronde. Elle fait pas de bruit, pis la police l'entend pas.", 8,
               jeu="[warmly] Tiens, ma fronde. [knowingly] Elle fait pas de bruit… pis la police l'entend pas."),
            _p("zed", "Yo, c'est Zed, des Skateux. Paraît que t'as nettoyé le pont. Viens voir si tu cours aussi vite que tu frappes.", 8,
               jeu="[playfully] Yo, c'est Zed, des Skateux. [amused] Paraît que t'as nettoyé le pont… Viens voir si tu cours aussi vite que tu frappes."),
            _p("zed", "Notre parcours : le stationnement, la foire, le pont, pis retour au phare. À pied, man.", 8,
               jeu="[excited] Notre parcours : le stationnement, la foire, le pont, pis retour au phare. [teasing] À pied, man."),
            _p("zed", "Mon record, c'est une minute vingt. Personne l'a jamais battu.", 8,
               jeu="[smugly] Mon record, c'est une minute vingt. [laughs] Personne l'a jamais battu."),
            _p("zed", "Tu le bats, les Skateux te laissent tranquille. Go!", 8,
               jeu="[mischievously] Tu le bats, les Skateux te laissent tranquille. [shouting] Go!"),
            _p("zed", "Cours, man! Le chrono attend personne!", 9,
               jeu="[excited] Cours, man! [laughs] Le chrono attend personne!"),
            _p("zed", "Non! T'as battu mon temps? Reviens au phare, faut que je voie ta face.", 10,
               jeu="[surprised] Non! T'as battu mon temps? [amused] Reviens au phare, faut que je voie ta face."),
            # Acte 4 : la fin de p04, puis Zed, qui est là, remet ça (son appel, sans se nommer : il est à côté).
            _p("zed", "Ha! Un vieux qui court. Les gars vont rire de moi une semaine.", 11,
               jeu="[laughs] [amused] Ha! Un vieux qui court. Les gars vont rire de moi une semaine."),
            _p("zed", "Correct, man. Les Skateux te toucheront plus. Parole de Skateux.", 11,
               jeu="[warmly] Correct, man. [confident] Les Skateux te toucheront plus. Parole de Skateux."),
            _p("zed", "T'as battu mon temps, correct. Mais sauter, man, ça s'apprend pas en courant.", 11,
               jeu="[amused] T'as battu mon temps, correct. [mischievously] Mais sauter, man… ça s'apprend pas en courant."),
            _p("zed", "Ma machine est devant le phare. La rampe est au stationnement, tu la connais.", 11,
               jeu="[casually] Ma machine est devant le phare. [confident] La rampe est au stationnement, tu la connais."),
            _p("zed", "Quatre-vingts pixels de vol, man. Moins que ça, c'est un trottoir.", 11,
               jeu="[smugly] Quatre-vingts pixels de vol, man. [laughs] Moins que ça, c'est un trottoir."),
            _p("zed", "Prends ton élan. Le plus loin possible, pis lâche rien.", 13,
               jeu="[excited] Prends ton élan. [shouting] Le plus loin possible, pis lâche rien!"),
            _p("zed", "Malade! Ramène-moi ma machine avant que tu la brises, man.", 14,
               jeu="[impressed] Malade! [laughs] Ramène-moi ma machine avant que tu la brises, man."),
            # Acte 5 : la fin de p10 ; puis Ovila appelle, la lampe éteinte.
            _p("zed", "Quatre-vingts pixels. Les gars l'ont filmé, t'es sur toutes les cassettes.", 15,
               jeu="[impressed] Quatre-vingts pixels. [amused] Les gars l'ont filmé… t'es sur toutes les cassettes."),
            _p("zed", "La Chef veut me voir, paraît. Si tu y vas, je viens.", 15,
               jeu="[nervously] La Chef veut me voir, paraît. [warmly] Si tu y vas… je viens."),
            _p("ovila", "Bonsoir. Ici Ovila, au phare. La lampe est éteinte, et il y a un bateau dans la brume.", 15,
               jeu="[worried] Bonsoir. Ici Ovila, au phare. [gravely] La lampe est éteinte… et il y a un bateau dans la brume."),
            _p("ovila", "Des Skateux sont montés à la lampe. Ils ont tout coupé, pour rire.", 15,
               jeu="[somber] Des Skateux sont montés à la lampe. [bitterly] Ils ont tout coupé… pour rire."),
            _p("ovila", "Ce bateau-là ne voit pas les récifs sans nous. Vous avez une minute et demie, peut-être moins.", 15,
               jeu="[worried] Ce bateau-là ne voit pas les récifs sans nous. [firmly] Vous avez une minute et demie… peut-être moins."),
            _p("ovila", "Ils sont encore autour du phare. Je vous en prie, dépêchez-vous.", 16,
               jeu="[worried] Ils sont encore autour du phare. [gravely] Je vous en prie… dépêchez-vous."),
            # Neuf : le phare à tenir, pendant qu'il remonte à la lampe.
            _p("ovila", "Tenez la porte, je remonte à la lampe. Qu'ils ne repassent pas!", 16,
               jeu="[urgently] Tenez la porte, je remonte à la lampe. [firmly] Qu'ils ne repassent pas!"),
            # Acte 6 : la fin de p09, en personne ; puis Josée appelle.
            _p("ovila", "Il est passé. Il ne saura jamais qu'il a failli ne pas passer.", 18,
               jeu="[relieved] Il est passé. [softly] Il ne saura jamais… qu'il a failli ne pas passer."),
            _p("ovila", "Demain, le Clairon dira que le phare a tenu. Il aura raison, grâce à vous.", 18,
               jeu="[warmly] Demain, le Clairon dira que le phare a tenu. [tenderly] Il aura raison… grâce à vous."),
            _p("josee", "Josée. Le chef des Skateux veut me parler. Amène-le-moi, entier.", 18,
               jeu="[calm] Josée. [matter-of-fact] Le chef des Skateux veut me parler. [firmly] Amène-le-moi… entier."),
            _p("josee", "Il attend devant le phare. Il a peur de traverser la ville tout seul, et il a raison.", 18,
               jeu="[knowingly] Il attend devant le phare. [calm] Il a peur de traverser la ville tout seul… et il a raison."),
            _p("josee", "Ses gars ne veulent pas tous la paix. Ceux qui la refusent vont vous suivre.", 18,
               jeu="[serious] Ses gars ne veulent pas tous la paix. [coldly] Ceux qui la refusent… vont vous suivre."),
            _p("josee", "Au Brouillard, je lui offre La Pointe. Sans guerre, sans nous.", 18,
               jeu="[confident] Au Brouillard, je lui offre La Pointe. [quietly] Sans guerre… sans nous."),
            _p("zed", "Man, j'ai jamais passé le pont à pied. C'est grand, la ville.", 19,
               jeu="[nervously] Man, j'ai jamais passé le pont à pied. [quietly] C'est grand, la ville."),
            # Neuf : l'auto des Skateux qui vous colle.
            _p("zed", "Une auto nous colle, man! Ils vont pas me laisser signer tranquille.", 19,
               jeu="[worried] Une auto nous colle, man! [nervously] Ils vont pas me laisser signer tranquille."),
            _p("zed", "C'est Ti-Kid pis sa bande. Ils veulent pas que je signe. Couche-les, man!", 20,
               jeu="[worried] C'est Ti-Kid pis sa bande. Ils veulent pas que je signe. [shouting] Couche-les, man!"),
        ],
        "accueil": [
            _a("ovila", "Tournez la manette, là. La lampe revient. Le bateau tourne.", 17,
               jeu="[quietly] Tournez la manette, là. [relieved] La lampe revient… Le bateau tourne."),
        ],
    },
}
