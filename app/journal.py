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
    {"slug": "un_blesse", "cle": "hospitalisations", "min": 1, "titre": "UN BLESSÉ À L'HÔPITAL",
     "texte": "LE DR LACHANCE PARLE D'UNE NUIT AGITÉE AUX URGENCES.",
     "lu": "Un blessé à l'hôpital. Le docteur Lachance parle d'une nuit agitée aux urgences."},
    {"slug": "vague_de_vols", "cle": "volees", "min": 3, "titre": "VAGUE DE VOLS D'AUTOS",
     "texte": "TROIS VÉHICULES DISPARUS. « ON A NOS SOUPÇONS », DIT LE SERGENT.",
     "lu": "Vague de vols d'autos. Trois véhicules disparus. « On a nos soupçons », dit le sergent."},
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
#: chaque matin où la ville dormait se lisait mot pour mot pareil. Ces sept-là
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
]


#: Les manchettes que l'histoire impose (une mission finie fait la une, une fois).
SPECIALES: list[dict] = [
    {"slug": "cravates_chassees", "titre": "LES CRAVATES CHASSÉES DU FAUBOURG",
     "texte": "TROIS COINS DE RUE LIBÉRÉS EN UNE NUIT. TOUTE LA VILLE EN PARLE.",
     "lu": "Les Cravates chassées du Faubourg. Trois coins de rue libérés en une nuit ; toute la ville en parle."},
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
