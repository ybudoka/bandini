"""Les missions et les defis — donneur, prerequis, objectifs types, recompense, repliques.

Le texte de chaque replique vit ICI, et nulle part ailleurs : c'est la source
de la boite de dialogue ET de la voix generee (voir `audio.voix_histoire`).
Le navigateur ne decide rien : il joue les objectifs dans l'ordre, selon leur
type, et parle avec les mots d'ici.

Le fil : Ti-Guy accueille le cousin de Rocco au terminus (M1), Madame
Thibodeau a un compte a regler avec les Cravates (M2), Marco prete son taxi
(M3), le sergent Bouchard a une auto-patrouille a faire disparaitre (M4) et
Josee, la Chef des Quais, veut le Faubourg vide de Cravates (M5).
"""

from __future__ import annotations

from typing import TypedDict

TYPES_OBJECTIFS = (
    "aller",       # atteindre un lieu (rayon en tuiles) ; `nuit` : attendre la nuit
    "parler",      # toucher un personnage
    "monter",      # monter dans le vehicule de la mission (`vehicule`, `ou`)
    "livrer",      # amener le vehicule de la mission a un lieu ; `sans_degats` : prime
    "ramasser",    # ramasser un objet — `cible: fuyard` : le rattraper d'abord
    "tuer",        # mettre KO (ou pire) `n` membres d'un `groupe`, `chef` pour le boss
    "survivre",    # tenir `secondes`
    "course",      # passer des points de passage dans l'ordre, chrono
    "courses",     # `n` courses de taxi (le klaxon prend un client)
    "semer",       # redescendre a 0 etoile (`etoiles` posees au depart)
    "retourner",   # revenir au donneur
)

ECHECS = ("mort", "arrete", "vehicule_detruit", "chrono")


class Personnage(TypedDict):
    slug: str
    nom: str
    genre: str
    voix: str          # le nom exact de la voix dans le compte ElevenLabs
    couleurs: dict     # les permutations du sprite `joueur` : c chandail, h cheveux, s peau, p pantalon
    ou: str            # ou il se tient : `porte:<lieu>` (dehors, a cote de la porte) ou `point:<type>` (dedans)
    heler: str         # le mot de sa BULLE quand il a une job pour toi (voir `Entites.bulle`)


#: ⚠️ La bulle est lue a l'ecran, en police 3x5 : plus long que ca et le mot
#: deborde de la tete de celui qui le dit. C'est court par force, pas par style.
HELER_MAX = 16


#: ⚠️ Les voix sont celles que Martin a ajoutees a son compte le 13 sept. 2026
#: (voir docs/plan.md, « Les voix de l'histoire »). Si un nom change,
#: `scripts/audio_elevenlabs.py --voix` le dit : il ne devine jamais.
PERSONNAGES: list[Personnage] = [
    {"slug": "ti_guy", "nom": "Ti-Guy", "genre": "homme", "voix": "Felix Tabarnak - Confident and Witty",
     "couleurs": {"c": "#2e8b57", "h": "#3a2a1a", "s": "#e8b088", "p": "#3a3a4a"}, "ou": "porte:terminus",
     "heler": "Hé! Le cousin!"},
    {"slug": "thibodeau", "nom": "Madame Thibodeau", "genre": "femme", "voix": "Julia",
     "couleurs": {"c": "#8e44ad", "h": "#d0d0d0", "s": "#e8b088", "p": "#4a3a5a"}, "ou": "porte:kiosque",
     "heler": "Psst! Toi!"},
    {"slug": "marco", "nom": "Marco", "genre": "homme", "voix": "Québec Tremblay - Confident and Measured",
     "couleurs": {"c": "#f1c40f", "h": "#101018", "s": "#c98d66", "p": "#2a2a3a"}, "ou": "porte:garage",
     "heler": "Hé! Viens ici!"},
    {"slug": "bouchard", "nom": "Sergent Bouchard", "genre": "homme", "voix": "Khaivan - Quebec accent",
     "couleurs": {"c": "#1f3a6e", "h": "#8a8a8a", "s": "#e8b088", "p": "#16264a"}, "ou": "point:sergent",
     "heler": "Ici, le jeune!"},
    {"slug": "josee", "nom": "Josée", "genre": "femme", "voix": "Jeanne Mance - Charming, Clear and Young",
     "couleurs": {"c": "#c0392b", "h": "#101018", "s": "#f0c098", "p": "#101018"}, "ou": "point:contact",
     "heler": "Approche, toi."},
    {"slug": "civil", "nom": "Le client", "genre": "homme", "voix": "Alexandre - Authentic French Canadian",
     "couleurs": {"c": "#7f8c8d", "h": "#3a2a1a", "s": "#e8b088", "p": "#2a2a3a"}, "ou": "",
     "heler": "Taxi!"},
    # Le narrateur du Clairon : un vieil homme qui soupire, il lit la manchette du matin.
    {"slug": "narrateur", "nom": "Le Clairon de la Baie", "genre": "homme", "voix": "annonceur centre d'achat 1",
     "couleurs": {"c": "#3a3a4a", "h": "#d0d0d0", "s": "#e8b088", "p": "#2a2a3a"}, "ou": "",
     "heler": ""},
]


class Mission(TypedDict):
    slug: str
    titre: str
    donneur: str
    prerequis: list[str]
    recompense: int
    objectifs: list[dict]
    echec: list[str]
    dialogue: dict     # appel (au telephone), intro, fin, echec : listes de {qui, texte}
    donne: dict        # ce que la fin accorde, en plus de l'argent
    phase: int


def _l(qui: str, texte: str) -> dict:
    return {"qui": qui, "texte": texte}


CATALOGUE: list[Mission] = [
    {
        "slug": "m1", "titre": "Bienvenue en ville", "donneur": "ti_guy", "prerequis": [],
        "recompense": 100, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
        "donne": {"message": "LA CLÉ DE LA PLANQUE"},
        "objectifs": [
            {"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"},
            {"type": "monter", "vehicule": "auto", "ou": "ruelle:garage", "texte": "PRENDS LE CHAR DANS LA RUELLE"},
            {"type": "livrer", "lieu": "garage", "rayon": 4, "sans_degats": True, "texte": "RAMÈNE-LE AU GARAGE, SANS BOSSE"},
        ],
        "dialogue": {
            "appel": [],
            "intro": [
                _l("ti_guy", "Heille! Le cousin de Rocco! T'as fait bon voyage?"),
                _l("ti_guy", "Rocco est parti se faire oublier. Le garage, c'est toi qui le tiens, astheure."),
                _l("ti_guy", "Y a un char qui traîne dans la ruelle derrière le garage. Personne va s'en ennuyer."),
                _l("ti_guy", "Ramène-le au garage sans le bosser, pis sans que personne te voie."),
            ],
            "fin": [
                _l("ti_guy", "Pas une bosse! T'es ben le cousin de Rocco."),
                _l("ti_guy", "Tiens, la clé de la planque. Dors là, pis fais-toi pas pogner."),
            ],
            "echec": [_l("ti_guy", "Ouain... On va dire que c'était un essai. Reviens me voir.")],
        },
    },
    {
        "slug": "m2", "titre": "Le kiosque de Madame Thibodeau", "donneur": "thibodeau", "prerequis": ["m1"],
        "recompense": 150, "phase": 1, "echec": ["mort", "arrete"],
        "donne": {"arme": "batte", "rabais": {"kiosque": 0.75}, "message": "LE BÂTON, ET −25 % AU KIOSQUE"},
        "objectifs": [
            {"type": "tuer", "groupe": "cravates", "n": 2, "ou": "donneur", "texte": "METS LES DEUX CRAVATES K.-O."},
            {"type": "ramasser", "cible": "fuyard", "vehicule": "moto", "texte": "RATTRAPE LE FUYARD EN MOTO"},
            {"type": "retourner", "texte": "RAPPORTE LA CAISSE À MADAME THIBODEAU"},
        ],
        "dialogue": {
            "appel": [_l("thibodeau", "C'est Madame Thibodeau, du kiosque. Les Cravates me font des misères. Viens me voir, veux-tu?")],
            "intro": [
                _l("thibodeau", "Deux Cravates sont venus me « protéger ». Ils ont vidé ma caisse."),
                _l("thibodeau", "Ils rôdent encore au coin. Fais-leur comprendre. Avec tes poings, pas plus."),
                _l("thibodeau", "Le troisième s'est sauvé en moto avec mon argent. Rattrape-le."),
            ],
            "fin": [
                _l("thibodeau", "Mon argent! T'es un bon garçon, toi."),
                _l("thibodeau", "Tiens, le bâton de mon défunt. Pis au kiosque, c'est moins cher pour toi."),
            ],
            "echec": [_l("thibodeau", "Ils t'ont eu, hein? Repose-toi, pis reviens.")],
        },
    },
    {
        "slug": "m3", "titre": "Le taxi de Marco", "donneur": "marco", "prerequis": ["m2"],
        "recompense": 200, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
        "donne": {"message": "LE SERGENT BOUCHARD VEUT TE VOIR"},
        "objectifs": [
            {"type": "monter", "vehicule": "taxi", "ou": "porte:garage", "texte": "MONTE DANS LE TAXI DE MARCO"},
            {"type": "courses", "n": 3, "texte": "FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT"},
            {"type": "livrer", "lieu": "garage", "rayon": 4, "texte": "RAMÈNE LE TAXI AU GARAGE"},
        ],
        "dialogue": {
            "appel": [_l("marco", "Marco, le cousin. J'ai un taxi qui dort au garage. Ça te tente de faire du cash?")],
            "intro": [
                _l("marco", "Trois clients, pas plus. Pis tu me ramènes le taxi entier."),
                _l("marco", "Ouvre l'œil. Y a du monde en ville qui pose des questions sur toi."),
            ],
            "client": [_l("civil", "Roule, mon homme. Pis fais pas de folies : j'suis de la police.")],
            "fin": [
                _l("marco", "Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte."),
                _l("marco", "Y mange là tous les midis. Sois poli, c'est un ami de la famille."),
            ],
            "echec": [_l("marco", "Mon taxi... Bon. On efface, pis on recommence.")],
        },
    },
    {
        "slug": "m4", "titre": "Le lunch du sergent", "donneur": "bouchard", "prerequis": ["m3"],
        "recompense": 400, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
        "donne": {"sergent_ami": True, "message": "LE SERGENT EST TON AMI"},
        "objectifs": [
            {"type": "aller", "lieu": "poste", "rayon": 5, "nuit": True, "texte": "VA AU POSTE, DE NUIT"},
            {"type": "monter", "vehicule": "police", "ou": "porte:poste", "texte": "PRENDS L'AUTO-PATROUILLE"},
            {"type": "semer", "etoiles": 2, "escorte": "ti_guy", "texte": "SÈME LA POLICE — TI-GUY TE SUIT"},
            {"type": "livrer", "lieu": "garage", "rayon": 4, "texte": "LARGUE L'AUTO AU GARAGE"},
        ],
        "dialogue": {
            "appel": [_l("bouchard", "Bouchard. Marco m'a parlé de toi. Viens dîner au casse-croûte, j'ai une job.")],
            "intro": [
                _l("bouchard", "Y a une auto-patrouille au poste que j'aimerais voir disparaître. Papiers pas propres."),
                _l("bouchard", "Prends-la de nuit, sans témoin. Ti-Guy va te suivre en char, pour faire diversion."),
                _l("bouchard", "Largue-la au garage. Pis si mes gars te courent après, sème-les."),
            ],
            "fin": [
                _l("bouchard", "Propre. À partir d'aujourd'hui, si un de mes gars te pogne, tu dis mon nom."),
                _l("bouchard", "Un mot d'avertissement : Josée, au bar, cherche du monde comme toi. Fais attention."),
            ],
            "echec": [_l("bouchard", "J'ai rien vu, j'ai rien entendu. Reviens quand ça sera calme.")],
        },
    },
    {
        "slug": "m5", "titre": "La Chef des Quais", "donneur": "josee", "prerequis": ["m4"],
        "recompense": 800, "phase": 1, "echec": ["mort", "arrete"],
        "donne": {"propriete": "bar", "faubourg_libere": True, "manchette": "cravates_chassees",
                  "message": "LE BAR EST À TOI"},
        "objectifs": [
            {"type": "tuer", "groupe": "cravates", "n": 6, "ou": "zone:cravates", "coins": 3, "texte": "VIDE LES TROIS COINS DES CRAVATES"},
            {"type": "tuer", "groupe": "cravates", "n": 1, "chef": True, "texte": "COUCHE LE CHEF"},
            {"type": "semer", "etoiles": 3, "texte": "SÈME LA POLICE"},
            {"type": "aller", "lieu": "planque", "rayon": 4, "texte": "RENTRE À LA PLANQUE"},
        ],
        "dialogue": {
            "appel": [_l("josee", "Josée. On m'appelle la Chef. Viens au Brouillard, j'ai à te parler.")],
            "intro": [
                _l("josee", "Les Cravates tiennent trois coins de rue. Je les veux vides avant la nuit."),
                _l("josee", "Leur chef va sortir quand ses gars vont tomber. Lui, je le veux couché."),
                _l("josee", "Un témoin va appeler la police, c'est sûr. Sème-les, pis rentre à ta planque."),
            ],
            "fin": [
                _l("josee", "Le Faubourg respire. Le bar est à toi, pis toute la ville va le lire demain matin."),
                _l("josee", "On va se reparler. Y a plus grand que le Faubourg."),
            ],
            "echec": [_l("josee", "Les Cravates sont encore là. Reviens quand tu seras prêt.")],
        },
    },
]

#: Les defis : un panneau en ville, un chrono, une prime — une seule fois.
DEFIS: list[dict] = [
    {"slug": "saut", "titre": "Le Grand Saut", "ou": "rampe", "vehicule": "moto", "vol_px": 60,
     "prime": 250, "texte": "SAUTE LA RAMPE EN MOTO : 60 PX DE VOL"},
    {"slug": "tour", "titre": "Tour du Faubourg", "ou": "porte:terminus", "tours": 3, "chrono_s": 120,
     "points": ["terminus", "garage", "hopital", "poste"], "prime": 250,
     "texte": "TROIS TOURS PAR LE GARAGE, L'HÔPITAL ET LE POSTE EN MOINS DE 2:00"},
    {"slug": "livraison", "titre": "Livraison sans bosse", "ou": "porte:garage", "lieu": "bar", "chrono_s": 90,
     "etoiles": 1, "prime": 250, "texte": "LIVRE TON CHAR AU BAR EN 90 S, SANS UNE BOSSE, AVEC LA POLICE AUX FESSES"},
]

NB_MISSIONS = len(CATALOGUE)


def par_slug(slug: str) -> Mission | None:
    for mission in CATALOGUE:
        if mission["slug"] == slug:
            return mission
    return None


def personnage(slug: str) -> Personnage | None:
    for p in PERSONNAGES:
        if p["slug"] == slug:
            return p
    return None


def repliques() -> list[dict]:
    """Toutes les repliques de l'histoire, dans l'ordre, avec leur slug de voix.

    Le slug : `<qui>-<mission>-<n>` (n compte a travers appel, intro, client,
    fin, echec). Il ne depend que de la place de la replique : on peut changer
    un mot et regenerer une seule ligne avec `--refaire`.
    """
    sortie = []
    for mission in CATALOGUE:
        n = 0
        for partie in ("appel", "intro", "client", "fin", "echec"):
            for ligne in mission["dialogue"].get(partie, []):
                n += 1
                sortie.append({"slug": f"{ligne['qui']}-{mission['slug']}-{n}", "qui": ligne["qui"],
                               "texte": ligne["texte"], "mission": mission["slug"], "partie": partie,
                               "telephone": partie == "appel"})
    return sortie


def ordre_topologique() -> list[str]:
    """Les slugs dans un ordre ou chaque prerequis precede sa mission.

    Leve ValueError sur un cycle ou un prerequis inconnu.
    """
    restantes = {m["slug"]: set(m["prerequis"]) for m in CATALOGUE}
    for slug, prerequis in restantes.items():
        inconnus = prerequis - set(restantes)
        if inconnus:
            raise ValueError(f"{slug} : prerequis inconnus {sorted(inconnus)}")
    ordre: list[str] = []
    while restantes:
        pretes = sorted(s for s, p in restantes.items() if not p)
        if not pretes:
            raise ValueError(f"cycle de prerequis parmi {sorted(restantes)}")
        for slug in pretes:
            ordre.append(slug)
            del restantes[slug]
        for prerequis in restantes.values():
            prerequis.difference_update(pretes)
    return ordre
