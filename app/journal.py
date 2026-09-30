"""Le Clairon de la Baie — la manchette du matin, selon ce qu'on a fait hier.

Le navigateur compare les statistiques d'aujourd'hui a celles d'hier et prend
la PREMIERE regle qui passe : l'ordre est donc du plus grave au plus banal, et
la derniere regle sert de repli (rien a signaler).
"""

from __future__ import annotations

from typing import TypedDict


class Regle(TypedDict):
    slug: str
    cle: str
    min: int
    titre: str
    texte: str
    lu: str      # ce que le narrateur DIT : en casse naturelle, sinon le TTS epelle les majuscules


REGLES: list[Regle] = [
    {"slug": "nuit_rouge", "cle": "tues", "min": 3, "titre": "NUIT ROUGE AU FAUBOURG",
     "texte": "TROIS CORPS EN UNE NUIT. LA POLICE PROMET DES RENFORTS.",
     "lu": "Nuit rouge au Faubourg. Trois corps en une nuit ; la police promet des renforts."},
    {"slug": "un_mort", "cle": "tues", "min": 1, "titre": "UN MORT DANS LA RUE",
     "texte": "UN PASSANT RETROUVÉ SANS VIE. TÉMOINS RECHERCHÉS.",
     "lu": "Un mort dans la rue. Un passant retrouvé sans vie ; témoins recherchés."},
    # ⚠️ Trois manchettes du 30 sept. 2026 (« le Clairon a plus à dire ») sur des statistiques déjà comptées et
    # jamais lues : `braquages`, `arrestations`, `bateauxVoles`. Elles sont gardées dans l'instantané de la veille
    # (`p.journal`, `Missions.manchetteDuJour`) — sans lui, le total depuis le début passerait tous les matins.
    {"slug": "un_braquage", "cle": "braquages", "min": 1, "titre": "UN COMMERCE BRAQUÉ",
     "texte": "LE COMMIS A LEVÉ LES MAINS. LA CAISSE EST PARTIE AVEC LE VOLEUR.",
     "lu": "Un commerce braqué. Le commis a levé les mains, et la caisse est partie avec le voleur. « Il avait l'air poli », dit-il."},
    {"slug": "un_blesse", "cle": "hospitalisations", "min": 1, "titre": "UN BLESSÉ À L'HÔPITAL",
     "texte": "LE DR LACHANCE PARLE D'UNE NUIT AGITÉE AUX URGENCES.",
     "lu": "Un blessé à l'hôpital. Le docteur Lachance parle d'une nuit agitée aux urgences."},
    {"slug": "une_arrestation", "cle": "arrestations", "min": 1, "titre": "UN SUSPECT AU POSTE",
     "texte": "LE SERGENT PARLE D'UN VISAGE CONNU ET D'UNE AMENDE SALÉE.",
     "lu": "Un suspect au poste. Le sergent parle d'un visage connu, et d'une amende salée. Il est ressorti au matin, les poches plus légères."},
    {"slug": "vague_de_vols", "cle": "volees", "min": 3, "titre": "VAGUE DE VOLS D'AUTOS",
     "texte": "TROIS VÉHICULES DISPARUS. « ON A NOS SOUPÇONS », DIT LE SERGENT.",
     "lu": "Vague de vols d'autos. Trois véhicules disparus. « On a nos soupçons », dit le sergent."},
    {"slug": "un_bateau_vole", "cle": "bateauxVoles", "min": 1, "titre": "UN BATEAU DISPARU AU QUAI",
     "texte": "SON PROPRIÉTAIRE CHERCHE ENCORE SES AMARRES.",
     "lu": "Un bateau disparu au quai. Son propriétaire cherche encore ses amarres. « Il reviendra quand il aura faim », dit un pêcheur."},
    {"slug": "un_char_vole", "cle": "volees", "min": 1, "titre": "UN CHAR VOLÉ AU FAUBOURG",
     "texte": "ON L'A VU DISPARAÎTRE EN PLEINE RUE. IL EST REPARTI EN PLEIN VOL.",
     "lu": "Un char volé au Faubourg. On l'a vu disparaître en pleine rue. Il est reparti en plein vol."},
    {"slug": "taxi_qui_ne_dort_pas", "cle": "courses", "min": 3, "titre": "LE TAXI QUI NE DORT PAS",
     "texte": "UN CHAUFFEUR ENCHAÎNE LES COURSES. LES CLIENTS PARLENT DE BROUILLARD.",
     "lu": "Le taxi qui ne dort pas. Un chauffeur enchaîne les courses ; les clients parlent de brouillard."},
    {"slug": "faubourg_inquiet", "cle": "crimes", "min": 5, "titre": "LE FAUBOURG S'INQUIÈTE",
     "texte": "LES COMMERÇANTS DEMANDENT PLUS DE PATROUILLES.",
     "lu": "Le Faubourg s'inquiète. Les commerçants demandent plus de patrouilles."},
    {"slug": "brume", "cle": "crimes", "min": 0, "titre": "BRUME SUR LE BASSIN",
     "texte": "LE TRAVERSIER A PRIS DU RETARD. RIEN À SIGNALER.",
     "lu": "Brume sur le bassin. Le traversier a pris du retard. Rien à signaler."},
]

#: LES MATINS CALMES — ce que le Clairon lit quand il ne s'est RIEN passé.
#:
#: ⚠️ « Brume sur le bassin » (le repli, ci-dessus) était le SEUL matin normal :
#: chaque matin où la ville dormait se lisait mot pour mot pareil. Ces dix-sept-là
#: s'ajoutent au bassin : le narrateur en tire un, sans jamais redire le
#: précédent (même règle que les répliques de la rue), et le repli reste le
#: filet — il n'y a rien de plus grave à dire.
#:
#: ⚠️ Chacun porte la même forme que les manchettes (`slug`, `titre`, `texte`
#: en casse de manchette, `lu` en casse naturelle) : c'est ce qui les fait lire
#: par le narrateur (`audio.voix_journal`) sans une ligne de plus, et c'est ce
#: qui les fait juger par les mêmes juges qu'elle. Ils ne sont PAS dans
#: `REGLES` : ils ne portent aucune gravité, ce ne sont pas des règles qui
#: passent, ce sont des replis qui VARIENT.
MATINS: list[Regle] = [
    {"slug": "matin_maree", "cle": "crimes", "min": 0, "titre": "LA MARÉE EST HAUTE",
     "texte": "LES QUAIS S'ÉVEILLENT. LES CORDAGES CRAQUENT DANS LA BRISE.",
     "lu": "La marée est haute. Les quais s'éveillent, les cordages craquent dans la brise."},
    {"slug": "matin_mouettes", "cle": "crimes", "min": 0, "titre": "LES MOUETTES CRIENT TÔT",
     "texte": "ELLES TOURNENT AU-DESSUS DU QUAI, PUIS ELLES SE TAISENT.",
     "lu": "Les mouettes crient tôt. Elles tournent au-dessus du quai, puis elles se taisent."},
    {"slug": "matin_boulanger", "cle": "crimes", "min": 0, "titre": "ÇA SENT LE PAIN CHAUD",
     "texte": "LE BOULANGER DU FAUBOURG SORT SES FOURNÉES. LA RUE MARCHE LE NEZ EN L'AIR.",
     "lu": "Ça sent le pain chaud. Le boulanger du Faubourg sort ses fournées, la rue marche le nez en l'air."},
    {"slug": "matin_laitier", "cle": "crimes", "min": 0, "titre": "LE LAITIER PASSE À L'AUBE",
     "texte": "LES BOUTEILLES S'ALIGNENT SUR LES PERRONS. LE FAUBOURG DORT ENCORE, PRESQUE.",
     "lu": "Le laitier passe à l'aube. Les bouteilles s'alignent sur les perrons, le Faubourg dort encore, presque."},
    {"slug": "matin_peche", "cle": "crimes", "min": 0, "titre": "LA PÊCHE A ÉTÉ BONNE",
     "texte": "LES BATEAUX RENTRENT AU QUAI, LES COFFRES PLEINS.",
     "lu": "La pêche a été bonne. Les bateaux rentrent au quai, les coffres pleins."},
    {"slug": "matin_volets", "cle": "crimes", "min": 0, "titre": "LA VILLE OUVRE LES VOLETS",
     "texte": "ILS SE LÈVENT UN À UN. BAIE-DES-BRUMES S'ÉTIRE AU SOLEIL.",
     "lu": "La ville ouvre les volets. Ils se lèvent un à un, Baie-des-Brumes s'étire au soleil."},
    {"slug": "matin_silence", "cle": "crimes", "min": 0, "titre": "UN MATIN TRANQUILLE",
     "texte": "RIEN À SIGNALER À BAIE-DES-BRUMES. LE MEILLEUR GENRE DE MATIN.",
     "lu": "Un matin tranquille. Rien à signaler à Baie-des-Brumes, le meilleur genre de matin."},
    # Dix matins de plus (30 sept. 2026) : sans saison — une partie commence en janvier —, et chacun avec sa chute.
    {"slug": "matin_traversier", "cle": "crimes", "min": 0, "titre": "LE TRAVERSIER PART À L'HEURE",
     "texte": "UNE PREMIÈRE DEPUIS DES MOIS. LE CAPITAINE N'EN REVIENT PAS.",
     "lu": "Le traversier part à l'heure. Une première depuis des mois ; le capitaine Bérubé n'en revient pas."},
    {"slug": "matin_bingo", "cle": "crimes", "min": 0, "titre": "LE BINGO FAIT SALLE COMBLE",
     "texte": "UNE PAROISSIENNE A CRIÉ BINGO DEUX FOIS. ON VÉRIFIE SES CARTES.",
     "lu": "Le bingo fait salle comble. Une paroissienne a crié bingo deux fois ; le curé vérifie ses cartes."},
    {"slug": "matin_chat", "cle": "crimes", "min": 0, "titre": "LE CHAT DU DÉPANNEUR EST REVENU",
     "texte": "PLUS GRAS QU'AVANT. PERSONNE NE POSE DE QUESTIONS.",
     "lu": "Le chat du dépanneur est revenu de sa fugue. Plus gras qu'avant ; personne ne pose de questions."},
    {"slug": "matin_horloge", "cle": "crimes", "min": 0, "titre": "L'HORLOGE DE LA VILLE RETARDE",
     "texte": "DE SEPT MINUTES. LE CONSEIL EN DÉBATTRA JEUDI.",
     "lu": "L'horloge de l'hôtel de ville retarde de sept minutes. Le conseil en débattra jeudi, si tout le monde arrive à l'heure."},
    {"slug": "matin_autre_rive", "cle": "crimes", "min": 0, "titre": "ON VOIT L'AUTRE RIVE",
     "texte": "LA BRUME S'EST LEVÉE SUR LA BAIE. CERTAINS AURAIENT PRÉFÉRÉ PAS.",
     "lu": "On voit l'autre rive. La brume s'est levée sur la baie, pour une fois ; certains auraient préféré pas."},
    {"slug": "matin_casse_croute", "cle": "crimes", "min": 0, "titre": "UNE FILE AU CASSE-CROÛTE",
     "texte": "SIX HEURES DU MATIN, ET DÉJÀ DES FRITES. ON NE JUGE PERSONNE.",
     "lu": "Une file au casse-croûte. Six heures du matin, et déjà des frites ; on ne juge personne."},
    {"slug": "matin_cloches", "cle": "crimes", "min": 0, "titre": "LES CLOCHES SONNENT SEPT HEURES",
     "texte": "TOUTE LA VILLE LES ENTEND. PERSONNE NE SE LÈVE.",
     "lu": "Les cloches sonnent sept heures. Toute la ville les entend ; personne ne se lève."},
    {"slug": "matin_mots_croises", "cle": "crimes", "min": 0, "titre": "LES MOTS CROISÉS EN PAGE HUIT",
     "texte": "LE DOUZE HORIZONTAL, C'EST « BRUME ». COMME D'HABITUDE.",
     "lu": "Les mots croisés sont en page huit. Le douze horizontal, c'est « brume », comme d'habitude."},
    {"slug": "matin_facteur", "cle": "crimes", "min": 0, "titre": "LE FACTEUR A FINI AVANT MIDI",
     "texte": "ON SOUPÇONNE UN RACCOURCI PAR LES COURS ARRIÈRE.",
     "lu": "Le facteur a fini sa tournée avant midi. On soupçonne un raccourci par les cours arrière."},
    {"slug": "matin_toune", "cle": "crimes", "min": 0, "titre": "LA RADIO JOUE LA MÊME TOUNE",
     "texte": "POUR LA TROISIÈME FOIS CE MATIN. TOUT LE MONDE FREDONNE.",
     "lu": "La radio joue la même toune, pour la troisième fois ce matin. Personne n'appelle pour se plaindre ; tout le monde fredonne."},
]

#: CE QUE LE JEU T'APPREND, un matin a la fois.
#:
#: ⚠️ Le jeu a des boulots au klaxon, une fourriere, un marche noir, des
#: proprietes, trois defis — et RIEN N'EXPLIQUE RIEN. M1 apprend a marcher et a
#: voler un char, et apres ca le joueur est tout seul. Le repli du Clairon
#: (« rien a signaler ») etait la place libre : un matin ou il ne s'est rien
#: passe, le journal enseigne une chose. Sans une seule fenetre de plus.
#:
#: ⚠️ `cle` est la statistique qui PROUVE qu'on sait deja : on n'enseigne que ce
#: que le joueur n'a pas encore fait. Un jeu qui explique le taxi a quelqu'un
#: qui a fait trente courses n'explique rien, il agace.
#:
#: ⚠️ Et jamais deux fois la meme : la partie retient ce qui a ete lu. Quand il
#: n'y a plus rien a apprendre, le repli redevient « rien a signaler » — et
#: c'est une bonne nouvelle.
LECONS: list[dict] = [
    {"slug": "lecon_klaxon", "cle": "courses", "titre": "LE SAVIEZ-VOUS?",
     "texte": "UN COUP DE KLAXON DANS UN TAXI VOUS TROUVE UN CLIENT.",
     "lu": "Le saviez-vous ? Un coup de klaxon dans un taxi vous trouve un client. Ça marche aussi avec la pizza, l'ambulance et la remorqueuse."},
    {"slug": "lecon_fourriere", "cle": "saisies", "titre": "VOTRE CHAR A DISPARU?",
     "texte": "MAL GARÉ, IL EST À LA FOURRIÈRE. ON PEUT L'Y RACHETER.",
     "lu": "Votre char a disparu ? Mal garé, il est à la fourrière municipale. On peut l'y racheter, à un prix qui dépend de ce qu'il vaut."},
    {"slug": "lecon_cafe", "cle": "cafes", "titre": "LE CAFÉ DU MATIN",
     "texte": "UN CAFÉ, ET VOUS COUREZ DEUX FOIS PLUS LONGTEMPS.",
     "lu": "Le café du matin. Un café au comptoir, et vous sprintez deux fois plus longtemps pendant une minute et demie."},
    {"slug": "lecon_garage", "cle": "reparations", "titre": "LE GARAGE DE ROCCO",
     "texte": "ON Y RÉPARE, ON Y REPEINT — ET UNE PEINTURE FAIT OUBLIER UN CHAR.",
     "lu": "Le garage de Rocco. On y répare, on y repeint — et une peinture neuve fait oublier un char que la police cherche."},
    {"slug": "lecon_proprietes", "cle": "proprietes", "titre": "DEVENIR PROPRIÉTAIRE",
     "texte": "CERTAINS COMMERCES SE VENDENT. ILS RAPPORTENT CHAQUE JOUR.",
     "lu": "Devenir propriétaire. Certains commerces de la ville se vendent, et ils rapportent tous les jours, que vous y soyez ou non."},
    {"slug": "lecon_cloture", "cle": "clotures", "titre": "LES RACCOURCIS DU FAUBOURG",
     "texte": "UNE CLÔTURE S'ENJAMBE. LA POLICE AUSSI, MAIS ELLE Y PERD LE MÊME TEMPS.",
     "lu": "Les raccourcis du Faubourg. Une clôture se franchit à pied — la police aussi, mais elle y perd le même temps que vous."},
    # Six leçons de plus (30 sept. 2026), chacune vérifiée dans le code avant d'être écrite : le lit de la planque
    # (sauvegarde, toute la vie), la coupe de couleur (12 $, la recherche à zéro), le 6/49 (2 $ chez Ti-Paul), le
    # camion d'asphalte (devant la fourrière, au klaxon), Me Desjardins (au Brouillard, une page par jour), et les
    # photos de Louise — la dernière : Louise n'arrive qu'avec l'histoire. ⚠️ Leur `cle` n'est comptée nulle part,
    # comme celles d'avant sauf `courses` : chaque leçon se lit une fois, et c'est tout.
    {"slug": "lecon_dormir", "cle": "nuits", "titre": "UNE BONNE NUIT À LA PLANQUE",
     "texte": "ON SE RÉVEILLE EN PLEINE FORME, ET LA JOURNÉE EST MISE DE CÔTÉ.",
     "lu": "Une bonne nuit à la planque. Un lit, et on se réveille en pleine forme ; la journée, elle, est mise de côté."},
    {"slug": "lecon_barbier", "cle": "coupes", "titre": "RECHERCHÉ? PASSEZ CHEZ LE BARBIER",
     "texte": "UNE COUPE DE COULEUR, ET LA POLICE NE VOUS RECONNAÎT PLUS.",
     "lu": "Recherché? Passez chez le barbier. Une coupe de couleur, douze piastres, et la police ne vous reconnaît plus. Le stool non plus."},
    {"slug": "lecon_loto", "cle": "billets", "titre": "LE 6/49 DU DÉPANNEUR",
     "texte": "DEUX PIASTRES LE BILLET CHEZ TI-PAUL. LE TIRAGE, C'EST LA NUIT.",
     "lu": "Le six-quarante-neuf du dépanneur. Deux piastres le billet, chez Ti-Paul ; le tirage se fait la nuit, et les numéros sont dans le journal du matin. On peut gagner. Ça arrive."},
    {"slug": "lecon_nids", "cle": "nids", "titre": "LES NIDS-DE-POULE SE BOUCHENT",
     "texte": "LE CAMION D'ASPHALTE, DEVANT LA FOURRIÈRE, ATTEND UN CHAUFFEUR.",
     "lu": "Les nids-de-poule se bouchent. Le camion d'asphalte, garé devant la fourrière, attend un chauffeur ; un coup de klaxon, et la ville vous paie chaque trou."},
    {"slug": "lecon_avocat", "cle": "avocat", "titre": "UN CASIER TROP ÉPAIS?",
     "texte": "ME DESJARDINS, AU BROUILLARD, EN EFFACE UNE PAGE PAR JOUR.",
     "lu": "Un casier trop épais? Maître Desjardins, au Brouillard, en efface une page par jour. Ce n'est pas donné ; la prison non plus."},
    {"slug": "lecon_photos", "cle": "photos", "titre": "LE CLAIRON ACHÈTE VOS PHOTOS",
     "texte": "LOUISE PAIE BIEN UNE BELLE POURSUITE. UNE PAR JOUR.",
     "lu": "Le Clairon achète vos photos. Louise paie bien une belle poursuite, une par jour. Conseil d'ami : évitez d'être dessus."},
]


#: Les manchettes que l'histoire impose (une mission finie fait la une, une fois).
SPECIALES: list[dict] = [
    {"slug": "cravates_chassees", "titre": "LES CRAVATES CHASSÉES DU FAUBOURG",
     "texte": "TROIS COINS DE RUE LIBÉRÉS EN UNE NUIT. TOUTE LA VILLE EN PARLE.",
     "lu": "Les Cravates chassées du Faubourg. Trois coins de rue libérés en une nuit ; toute la ville en parle."},
    # L'orignal de La Pointe (`Vehicules.heurterDecor`) : le lendemain du choc, si c'etait toi. La
    # lecon du klaxon est celle d'Ovila, le gardien du phare, que le Clairon cite.
    {"slug": "orignal", "titre": "UN ORIGNAL GAGNE CONTRE UN CHAR",
     "texte": "LA BÊTE EST REPARTIE DANS LE BOIS. LE CHAR EST AU GARAGE.",
     "lu": "Un orignal gagne contre un char. La bête est repartie dans le bois de La Pointe ; le char est au garage. "
           "Ovila, au phare, le rappelle : un coup de klaxon, et ils s'en vont."},
    # La chute du Pouce (c04, 29 sept. 2026) : le lendemain, le Petit-Canton fait la une. Le Clairon ne sait pas
    # tout — il ne dit ni barbotte ni dés pipés, seulement ce que le quartier raconte.
    {"slug": "pouce_parti", "titre": "LE POUCE PLIE BAGAGE",
     "texte": "LE PETIT-CANTON RETROUVE SA PAYE. LA CAVE DU DRAGON D'OR CHANGE DE MAINS.",
     "lu": "Le Pouce plie bagage. Le Petit-Canton retrouve sa paye, et la cave du Dragon d'or change de mains. "
           "On l'aurait vu monter dans l'autobus de Sorel, sans ses valises."},
    # L'école rouvre (c08, 29 sept. 2026) : le lendemain des portes ouvertes, le Clairon est là pour le premier cours.
    {"slug": "ecole_rouverte", "titre": "L'ÉCOLE LA MANTE ROUVRE",
     "texte": "LE VIEUX MAÎTRE EST REVENU DE FLORIDE. SES ÉLÈVES AUSSI, UN PAR UN.",
     "lu": "L'École La Mante rouvre ses portes. Son vieux maître est revenu de Floride, bronzé, et ses élèves aussi, "
           "un par un. Premier cours à sept heures : les parents sont invités, les frimeurs aussi."},
    # La nuit des Morues (q13, 29 sept. 2026) : la première libération de M16. Le Clairon ne dit ni Josée ni
    # Sven — il dit ce que le port a vu.
    {"slug": "quais_liberes", "titre": "NUIT BLANCHE À L'HÔTEL BANDINI",
     "texte": "LES MATELOTS REPARTIS À LA RAME. LES QUAIS DORMENT TRANQUILLES.",
     "lu": "Nuit blanche à l'Hôtel Bandini. Les matelots du cargo norvégien sont repartis à la rame, "
           "et les Quais dorment tranquilles. Les débardeurs, eux, parlent d'une paix qui tiendra."},
    # Les Érables libérés (e10, 29 sept. 2026) : le Clairon ne nomme pas Jo — il nomme la conseillère.
    {"slug": "erables_liberes", "titre": "PLUS UN DRIFT DANS LES ÉRABLES",
     "texte": "LES CHEVREUILS RANGENT LEURS CHARS. LE CONSEIL VOTE LA PAIX.",
     "lu": "Plus un drift dans les Érables. Les Chevreuils rangent leurs chars, et le conseil vote la paix jeudi. "
           "La conseillère Larivière n'a pas voulu commenter."},
    # Le phare a tenu (p09) et La Pointe libérée (p11), 29 sept. 2026.
    {"slug": "phare_a_tenu", "titre": "LE PHARE A TENU",
     "texte": "UN CHALUTIER ÉVITE LES RÉCIFS DE JUSTESSE. LE GARDIEN REMERCIE UN INCONNU.",
     "lu": "Le phare a tenu. Un chalutier a évité les récifs de justesse, cette nuit ; le gardien Saint-Onge remercie "
           "un inconnu, et ne veut pas en dire plus."},
    {"slug": "pointe_liberee", "titre": "LA POINTE SIGNE LA PAIX",
     "texte": "LES SKATEUX RANGENT LEURS PLANCHES. LE PONT RESTE OUVERT.",
     "lu": "La Pointe signe la paix. Les Skateux rangent leurs planches, le pont reste ouvert, et monsieur Bilodeau "
           "dit qu'il ira enfin à la messe."},
    # La Shop libérée (s11, 29 sept. 2026) : le Clairon parle de l'usine, pas des Boulonneux.
    {"slug": "prevost_rembauche", "titre": "LA PRÉVOST REMBAUCHE",
     "texte": "CENT CINQUANTE POSTES AU SALAIRE D'AVANT. LA SHOP RESPIRE.",
     "lu": "La Prévost rembauche. Cent cinquante postes au salaire d'avant, dès lundi, et La Shop respire. "
           "Monsieur Prévost parle d'une décision d'affaires ; ses employés, d'un miracle."},
    # _Le Boss_ (m98, M13, 29 sept. 2026) : le maire démissionne, et la ville a un nouveau boss. Le Clairon écrit le
    # nom de Rocco une dernière fois — et, pour une fois, il n'y a pas de dette à côté.
    {"slug": "le_boss", "titre": "LE MAIRE TANGUAY DÉMISSIONNE",
     "texte": "LE NEVEU DE ROCCO BANDINI TIENT LA VILLE. PAS UN COIN DE RUE NE LUI ÉCHAPPE.",
     "lu": "Le maire Tanguay démissionne, en robe de chambre, à l'Hôtel Bandini. Le neveu de Rocco tient la ville, "
           "et pas un coin de rue ne lui échappe. Ceux qui le connaissent disent qu'il salue tout le monde."},
]


def speciale(slug: str) -> dict | None:
    for m in SPECIALES:
        if m["slug"] == slug:
            return m
    return None


def manchette(hier: dict, aujourd_hui: dict) -> Regle:
    """La premiere regle dont le delta depasse le minimum ; la derniere sinon."""
    for regle in REGLES:
        if aujourd_hui.get(regle["cle"], 0) - hier.get(regle["cle"], 0) >= regle["min"]:
            return regle
    return REGLES[-1]
