"""Le chapitre de Rosa — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague F). Martin a tranché
pour les arcs hors de la liste de M16 : les deux commissions de Rosa (f03, la robe de mariée volée par un Chevreuil ;
f10, la chemise hawaïenne et la lettre pour Norbert) deviennent deux ACTES — quatre étapes chacune, la même
boutique, le même hôtel au bout. Visée : 6 à 8 minutes, rien d'ajouté. f08 (le char de Rocco) attend f03, l'acte 1 ;
q07 et le scoop du maire attendent f10, le dernier.

Ce qui a bougé, et pourquoi (comme aux autres chapitres) :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la
  première mission restent ceux du chapitre ; la fin de la première se dit à l'ouverture de l'acte 2, suivie de
  l'appel et de l'intro de la seconde ; la fin de la seconde reste la fin du chapitre ; chacune garde son échec
  (`_e`, accroché à son acte) ;
- l'acte 1 paie sa prime et accorde ce que sa mission accordait en finissant (`donne` sur l'objectif qui le
  finit), et la mission qu'il remplace est faite à l'ouverture de l'acte 2 — ce qui l'attendait s'ouvre là ;
- la scène d'intro de la première reste celle du chapitre, la scène de fin de la seconde celle de sa fin ; les
  deux autres tombent (leurs répliques se disent au marqueur), comme au pilote.
- QUI PARLE SE NOMME une fois par chapitre : l'appel de f10 perd « Rosa, de la boutique » — la même voix, coupée au
  silence (Rosa vient de te parler en personne, à sa caisse).
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "rosa_et_ses_clients",
    "titre": "Rosa et ses clients",
    "donneur": "rosa",
    "prerequis": ["f01"],
    "remplace": ["f03", "f10"],
    "recompense": 300,
    "donne": {"contacts": ["norbert"], "message": "NORBERT TE DOIT UN SERVICE"},

    "objectifs": [
        # --- Acte 1 (f03, « La robe de Rosa »).
        {"type": "acte", "texte": "ACTE 1 — LA ROBE DE ROSA", "donneur": "rosa"},  # 0
        {"type": "ramasser", "texte": "RATTRAPE LE CHEVREUIL EN BERLINE", "cible": "fuyard", "vehicule": "auto"},  # 1
        {"type": "tuer", "texte": "SES CHUMS VEULENT LA CAISSE", "groupe": "chevreuils", "n": 2, "ou": "donneur", "loin": 10, "arme": "", "vie": 60},  # 2
        {"type": "aller", "texte": "PORTE LA ROBE DE MARIÉE À L'HÔTEL", "lieu": "hotel", "rayon": 4},  # 3
        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À ROSA", "donne": {"rabais": {"vetements": 0.75}, "message": "BOUTIQUE ROSA, MOINS CHER POUR TOI", "prime": 250}},  # 4
        # --- Acte 2 (f10, « La chemise hawaïenne »).
        {"type": "acte", "texte": "ACTE 2 — LA CHEMISE HAWAÏENNE", "donneur": "rosa"},  # 5
        {"type": "aller", "texte": "ENFILE LA CHEMISE, PUIS VA À L'HÔTEL", "lieu": "hotel", "rayon": 4, "remet": "chemise_hawai", "tenue": "chemise_hawai"},  # 6
        {"type": "parler", "texte": "DONNE LA LETTRE À NORBERT, EN CHEMISE", "cible": "norbert", "tenue": "chemise_hawai"},  # 7
        {"type": "tuer", "texte": "DEUX CRAVATES TE PRENNENT POUR UN AUTRE", "groupe": "cravates", "n": 2, "ou": "porte:hotel", "arme": "", "vie": 70},  # 8
        {"type": "retourner", "texte": "RETOURNE VOIR ROSA"},  # 9
    ],

    # f03 — Le jeu de chaque réplique (`jeu=`) — Rosa : chic, jamais surprise de rien, l'ex
    # de Rocco qui en a trop vu pour s'énerver ; un sourire en coin, pas un cri.
    # f10 — Le jeu de chaque réplique (`jeu=`) — Rosa, la chemise : amusée de bout en bout, l'ironie
    # de l'artisane qui habille un neveu de Rocco en touriste ; Norbert, le concierge, poli
    # jusqu'au vouvoiement, jamais surpris — il a tout vu passer dans ce hall. Il se nomme à
    # sa poignée de main : c'est la première fois qu'on l'entend.
    "dialogue": {
        "appel": [
            _l("rosa", "Rosa, de la boutique. Un Chevreuil vient de partir avec ma livraison, dans une belle berline. Viens me voir.", jeu="[calm] Rosa, de la boutique. Un Chevreuil vient de partir avec ma livraison… dans une belle berline. [matter-of-fact] Viens me voir."),
        ],
        "intro": [
            _l("rosa", "Une caisse de robes cousues sur mesure. Il file vers le nord, il connaît pas mon quartier.", jeu="[wryly] Une caisse de robes cousues sur mesure. [knowingly] Il file vers le nord… il connaît pas mon quartier."),
            _l("rosa", "Rattrape-le, pis ramène-moi ça propre. J'ai pas le temps de recoudre trois jours d'ouvrage.", jeu="[firmly] Rattrape-le, pis ramène-moi ça propre. [annoyed] J'ai pas le temps de recoudre trois jours d'ouvrage."),
        ],
        "fin": [
            _l("rosa", "Pas une tache, pas un bouton de parti. Tu te bats proprement, toi.", jeu="[impressed] Pas une tache, pas un bouton de parti. [amused] Tu te bats proprement, toi."),
            _l("rosa", "Garde la chemise. Pis Norbert te doit un service, ça vaut plus que mon rabais.", jeu="[warmly] Garde la chemise. [knowingly] Pis Norbert te doit un service… ça vaut plus que mon rabais."),
        ],
        "echec": [
            _e("rosa", "Trois jours d'ouvrage, envolés... Reviens quand t'auras la tête à ça.", 0, jeu="[disappointed] Trois jours d'ouvrage, envolés… [wryly] Reviens quand t'auras la tête à ça."),
            _e("rosa", "Tant pis. Une chemise, ça se recoud, une réputation, moins.", 5, jeu="[disappointed] Tant pis. [wryly] Une chemise, ça se recoud… une réputation, moins."),
        ],
        "pendant": [
            _p("rosa", "Il roule vite pour un gars qui connaît pas la ville. Reste sur lui.", 1, jeu="[amused] Il roule vite pour un gars qui connaît pas la ville. [firmly] Reste sur lui."),
            _p("rosa", "Ses petits amis veulent la caisse. Des Chevreuils en jogging, ça se couche vite.", 2, jeu="[wryly] Ses petits amis veulent la caisse. [amused] Des Chevreuils en jogging, ça se couche vite."),
            _p("rosa", "Tant qu'à y être, la robe de mariée va à l'hôtel. La mariée attend, le marié, moins.", 3, jeu="[knowingly] Tant qu'à y être, la robe de mariée va à l'hôtel. [wryly] La mariée attend… le marié, moins."),
            _p("rosa", "La mariée a appelé, elle pleure de joie. Rapporte-moi le reste de la caisse.", 4, jeu="[amused] La mariée a appelé, elle pleure de joie. [calm] Rapporte-moi le reste de la caisse."),
            # Acte 2 : la fin de f03, en personne ; puis l'appel et l'intro de f10.
            _p("rosa", "Impeccable. Pas une couture de défaite.", 5, jeu="[satisfied] Impeccable. [amused] Pas une couture de défaite.", cloture=True),
            _p("rosa", "Tiens, un rabais pour toi. Rocco payait toujours plein prix, lui. T'es différent.", 5, jeu="[knowingly] Tiens, un rabais pour toi. [softly] Rocco payait toujours plein prix, lui. T'es différent.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Rosa, de la boutique. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("rosa", "Un client a oublié une chemise hawaïenne chez nous, pis une lettre dans la poche.", 5, jeu="[knowingly] Un client a oublié une chemise hawaïenne chez nous… pis une lettre dans la poche."),
            _p("rosa", "La lettre est pour Norbert, le concierge de l'Hôtel Bandini. Il ouvre juste au gars en chemise.", 5, jeu="[knowingly] La lettre est pour Norbert, le concierge de l'Hôtel Bandini. [wryly] Il ouvre juste au gars en chemise."),
            _p("rosa", "Enfile-la, elle est à ta taille. Rocco aurait jamais porté des palmiers, toi t'as le cou pour.", 5, jeu="[amused] Enfile-la, elle est à ta taille. [wryly] Rocco aurait jamais porté des palmiers… toi t'as le cou pour."),
            _p("rosa", "Change-toi dans ma cabine si tu veux. Pis marche comme un gars en vacances.", 6, jeu="[amused] Change-toi dans ma cabine si tu veux. [teasing] Pis marche comme un gars en vacances."),
            _p("rosa", "Norbert est au bout du comptoir, dans le hall. Donne-lui la lettre, pas un mot de plus.", 7, jeu="[calm] Norbert est au bout du comptoir, dans le hall. [firmly] Donne-lui la lettre… pas un mot de plus."),
            _p("norbert", "Deux messieurs en cravate attendaient le vrai client, dehors. Je crains qu'ils vous confondent.", 8, jeu="[quietly] Deux messieurs en cravate attendaient le vrai client, dehors. [concerned] Je crains qu'ils vous confondent."),
            _p("rosa", "Norbert m'a appelée. Reviens me montrer si les palmiers ont survécu.", 9, jeu="[amused] Norbert m'a appelée. [teasing] Reviens me montrer si les palmiers ont survécu."),
        ],
        "accueil": [
            _a("norbert", "Norbert, concierge. Monsieur porte la chemise, monsieur a donc une lettre pour moi.", 7, jeu="[calm] Norbert, concierge. [knowingly] Monsieur porte la chemise… monsieur a donc une lettre pour moi."),
        ],
    },
}
