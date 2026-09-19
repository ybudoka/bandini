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

from typing import NotRequired, TypedDict

TYPES_OBJECTIFS = (
    "aller",       # atteindre un lieu (rayon en tuiles) ; `nuit` : attendre la nuit
    "parler",      # toucher un personnage — `cible` : de qui il s'agit (`personnages:`
                   # ou `arch:`), l'objectif s'accomplit en lui parlant
    "monter",      # monter dans le vehicule de la mission (`vehicule`, `ou`) ;
                   # `prete` : a QUI il est — un char prete ne se vend pas ;
                   # `ou: ruelle:<lieu>:<n>` : la ruelle la plus proche a n tuiles au moins
    "livrer",      # amener le vehicule de la mission a un lieu ; `sans_degats` : prime
    "ramasser",    # ramasser un objet — `cible: fuyard` : le rattraper d'abord
    "tuer",        # mettre KO (ou pire) `n` membres d'un `groupe`, `chef` pour le boss ;
                   # `arme` et `vie` remplacent la fiche de l'archetype (voir ci-dessous)
    "survivre",    # tenir `secondes`
    "course",      # passer des points de passage dans l'ordre, chrono
    "courses",     # `n` courses de taxi (le klaxon prend un client)
    "semer",       # redescendre a 0 etoile (`etoiles` posees au depart)
    "retourner",   # revenir au donneur
    # --- M16 : les neuf types de plus (docs/plan.md, « Ce que le moteur apprend »).
    # ⚠️ Chacun porte un juge de banc avant de servir une mission, et chacun
    # s'écrit en DONNÉES, jamais en `if (slug === '…')`. Les clés se déclarent
    # ici pour rester lisibles au carnet et au GPS comme au navigateur.
    "suivre",      # filer un piéton ou un char sans être vu : trop près ou trop
                   # loin, c'est raté (`cible`)
    "proteger",    # un personnage te suit à pied ou monte avec toi ; s'il meurt,
                   # échec `protege_mort` (`cible`)
    "pickpocket",  # les poches d'un piéton PRÉCIS, par-derrière (le jet de m2) `cible`
    "payer",       # donner un montant (`montant`)
    "acheter",     # un article à un comptoir (`article`, `ou`)
    "detruire",    # un véhicule de la mission (`vehicule_val` : ce qu'on lui enveie)
    "sauter",      # une rampe (`vol_px` : le juge du Grand Saut)
    "eteindre",    # un feu à l'extincteur (le jet existe, le feu de char aussi)
    "boulots",     # `n` boulots d'une `sorte` (généralise `courses`, qui reste au taxi)
)

#: ⚠️ **CE QUE PORTE UN HOMME DE MISSION SE DECLARE ICI.** Un objectif `tuer`
#: pose des membres d'un `groupe` : ils sortent de l'archetype (`pietons.py`),
#: avec sa vie et son arme. Deux cles facultatives passent par-dessus, et
#: seulement pour CES hommes-la :
#:
#:   `arme` — ce qu'ils tiennent ; `""` veut dire les poings. ⚠️ Un homme sans
#:            arme ne peut pas non plus en LACHER une en tombant.
#:   `vie`  — leurs points de vie.
#:
#: ⚠️ **On ne touche pas a l'archetype pour regler une bagarre.** Une Cravate de
#: rue doit rester ce qu'elle est : c'est elle qui tient le Faubourg (M5), c'est
#: elle qui vient encaisser la dette de Rocco, et l'affaiblir pour arranger M2
#: rendrait tout le reste du jeu mou. Ce qui change, c'est QUI on envoie.
# ⚠️ `etoile` (les missions discrètes, `sans_etoile`) et `protege_mort`
# (`proteger`, sa cible est tombée) sont les deux échecs que M16 ajoute aux
# quatre de la v1. Ils vivent ICI, lus par `histoire.js` comme le reste.
ECHECS = ("mort", "arrete", "vehicule_detruit", "chrono", "etoile", "protege_mort")

#: Les quatre options qui TRAVERSENT les types d'objectifs (M16). Une clé
#: d'objectif, pas un type : `chrono_s` sur n'importe lequel (le défi l'avait),
#: `sans_etoile` (échec `etoile` dès qu'on est vu), `sans_arme` (en territoire
#: de gang les mains vides), `contre` (des adversaires sur une `course`).
OPTIONS_OBJECTIFS = ("chrono_s", "sans_etoile", "sans_arme", "contre")


class Personnage(TypedDict):
    slug: str
    nom: str
    genre: str
    voix: str          # le nom exact de la voix dans le compte ElevenLabs
    couleurs: dict     # les permutations du sprite `joueur` : c chandail, h cheveux, s peau, p pantalon
    ou: str            # ou il se tient : `porte:<lieu>` (dehors, a cote de la porte) ou `point:<type>` (dedans)
    heler: str         # le mot de sa BULLE quand il a une job pour toi (voir `Entites.bulle`)
    # La mission apres laquelle il n'est plus a sa place (Ti-Guy quitte le terminus
    # apres M1 : sa scene de fin le fait entrer au garage). ⚠️ Dans les donnees, pas
    # dans `histoire.js` : un juge y interdit tout slug de mission.
    parti_apres: NotRequired[str]


#: ⚠️ La bulle est lue a l'ecran, en police 3x5 : plus long que ca et le mot
#: deborde de la tete de celui qui le dit. C'est court par force, pas par style.
HELER_MAX = 16


#: ⚠️ Les voix sont celles que Martin a ajoutees a son compte le 13 sept. 2026
#: (voir docs/plan.md, « Les voix de l'histoire »). Si un nom change,
#: `scripts/audio_elevenlabs.py --voix` le dit : il ne devine jamais.
PERSONNAGES: list[Personnage] = [
    {"slug": "ti_guy", "nom": "Ti-Guy", "genre": "homme", "voix": "Felix Tabarnak - Confident and Witty",
     "couleurs": {"c": "#2e8b57", "h": "#3a2a1a", "s": "#e8b088", "p": "#3a3a4a"}, "ou": "porte:terminus",
     "heler": "Hé! Le cousin!", "parti_apres": "m1"},
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

    # --- M16 : les quatre contacts que Josée te présente (m6, « Le tour du
    # propriétaire »). Un par district, un par monde : deux se tiennent DEHORS
    # devant leur porte, deux DEDANS sur un point de piece pose exprès.
    # ⚠️ Les trois voix quebecoises de femme (Jeanne Mance, Julia, Amélie) sont
    # TOUTES prises. Le 18 sept. 2026, Martin a ajoute deux quebecoises
    # d'origine au compte : Lulu prend donc Claudia (jeune, confiante), et
    # Raymonde garde Nadine, la voix rauque — ici l'accent FAIT le personnage,
    # une presidente de syndicat qui a roule sa bosse. Martin les auditonna a la
    # prochaine generation.
    {"slug": "tipaul", "nom": "Ti-Paul Gagnon", "genre": "homme", "voix": "Québec Tremblay - Confident and Measured",
     "couleurs": {"c": "#c0392b", "h": "#7a2a1a", "s": "#e8b088", "p": "#3a3a4a"}, "ou": "porte:depanneur",
     "heler": "Salut, l'ami!"},
    {"slug": "lulu", "nom": "Lucienne « Lulu » Pelletier", "genre": "femme", "voix": "Claudia - Warm, Energetic and Confident",
     "couleurs": {"c": "#f1c40f", "h": "#101018", "s": "#f0c098", "p": "#4a3a5a"}, "ou": "point:lulu",
     "heler": "Viens manger!"},
    {"slug": "raymonde", "nom": "Raymonde Fortin", "genre": "femme", "voix": "Nadine",
     "couleurs": {"c": "#8e44ad", "h": "#d0d0d0", "s": "#e8b088", "p": "#2a2a3a"}, "ou": "porte:usine",
     "heler": "Le syndicat!"},
    {"slug": "ovila", "nom": "Ovila Saint-Onge", "genre": "homme", "voix": "annonceur centre d'achat 1",
     "couleurs": {"c": "#2e8b57", "h": "#8a8a8a", "s": "#e8b088", "p": "#16264a"}, "ou": "point:ovila",
     "heler": "Les lumières..."},
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
    scenes: dict       # `intro` et `fin` : des listes de plans (voir `TYPES_PLANS`)
    phase: int
    # --- M16 : les deux cles qui font les choix et les conditions d'etat.
    # ⚠️ Facultatives, lues par le navigateur (voir `histoire.js` `exigeTenu`,
    # `estFermee`) et par le carnet.
    exige: NotRequired[dict]   # ce qu'il faut AVOIR en plus des prerequis
    ferme: NotRequired[str]    # le slug de la mission que celle-ci ferme


from ._commun import _l, _p


#: Ce que dit un personnage qui n'a rien pour toi. ⚠️ Ici et pas dans
#: `histoire.js` : « le Faubourg est tranquille » ne se dit qu'apres M5.
REPOS = {"texte": "REVIENS ME VOIR PLUS TARD.", "apres": "m5", "texte_apres": "LE FAUBOURG EST TRANQUILLE. MERCI."}


#: L'OUVERTURE — ce que le narrateur dit pendant que le car arrive au terminus.
#:
#: ⚠️ **Elle est ICI, avec les repliques de mission, et pas dans `histoire.js`.**
#: Le texte est la source de la boite de dialogue ET de la voix generee : une
#: premisse ecrite en JS ne se relit pas, ne se regenere pas a la ligne, et
#: n'apparait dans aucun juge. C'est la meme regle que partout — la replique est
#: la source.
#:
#: ⚠️ **Quatre phrases, pas dix.** On la passe (ACTION saute une ligne, PAUSE
#: saute tout), mais la premiere partie de quelqu'un ne doit pas commencer par
#: une minute ou il ne joue pas. Elles disent exactement ce que le jeu ne dit
#: NULLE PART ailleurs : qui est mort, ce dont on herite, ce qu'on doit, et avec
#: combien on debarque. Le reste, la ville le raconte toute seule.
#:
#: ⚠️ **Le narrateur est celui du Clairon**, et c'est voulu : c'est la meme voix
#: qui lira la manchette du lendemain matin et, un jour, le generique de fin.
#: Un homme qui ouvre le jeu et le ferme en fait une ligne ; deux voix en
#: feraient deux animations.
OUVERTURE: list[dict] = [
    _l("narrateur", "Baie-des-Brumes. Un port, du brouillard, pis du monde qui se mêle de ses affaires."),
    _l("narrateur", "Ton oncle Rocco est mort le mois passé. Il te laisse son garage, sa planque, pis son nom."),
    _l("narrateur", "Il te laisse sa dette avec. Quinze mille piastres à Sal le Barbier, qui compte les jours."),
    _l("narrateur", "T'arrives avec cinquante piastres pis un billet aller simple. Bonne chance, le jeune."),
]


# --- Les scènes : un vocabulaire de plans ----------------------------------------------------
#
# Décision du 16 sept. 2026 (« Les missions mises en scène », docs/plan.md) : une
# scène est une LISTE DE PLANS, typés comme les objectifs, et `static/js/scenes.js`
# les joue sans connaître aucune scène par son nom. Si une scène ne s'écrit pas
# avec ces types, on ajoute UN TYPE — jamais un `if (slug === 'q07')`.
#
# ⚠️ Les plans se jouent l'un après l'autre : chacun attend que le précédent soit
# fini, SAUF s'il porte `ensemble` — il part alors, et le suivant part avec lui.
# ⚠️ `fond` : un plan qui ne retient pas la scène. Elle se termine quand ses autres
# plans ET ses répliques sont finis, même s'il joue encore (le titre de l'ouverture
# s'éteint avec elle).
# ⚠️ Un lieu : un nom que la scène reçoit (`arret`, `quai`), un acteur (sa
# position), ou tout ce que `Histoire.resoudre` connaît (`porte:garage`,
# `ruelle:garage`, `donneur`). Un plan dont le lieu ou l'acteur ne se trouve pas
# est SAUTÉ, jamais attendu : une scène se termine toujours.

#: Les types de plan, et les clés que chacun accepte (les deux dernières, partout).
#: `courbe` : `droite`, `freine` (l'approche ralentit) ou `accelere` (le départ).
TYPES_PLANS: dict[str, tuple[str, ...]] = {
    # Aller voir un lieu. Sans `duree` ni `lissage`, la caméra y SAUTE ; avec
    # `duree`, elle y va ; avec `lissage`, elle le suit jusqu'au plan caméra suivant.
    # `recul` : tant de pixels en amont de la rue du lieu (il faut qu'il en ait une).
    "camera": ("vers", "recul", "duree", "courbe", "lissage"),
    # Un acteur va à un lieu, à pied, les jambes animées, en `duree` images.
    # `pres` : s'arrêter à tant de pixels du lieu (on va VERS quelqu'un, pas sur lui).
    "marcher": ("acteur", "vers", "duree", "pres"),
    # Un char de la scène : il ENTRE par la rue (`vehicule` le crée, `depuis` pixels
    # en amont de `vers`), ou il PART (`part` pixels en aval). `fumee` : les bouffées
    # du pot, `portiere` : le claquement à l'arrêt et au départ, `retirer` : il
    # quitte la ville au bout du plan.
    "conduire": ("acteur", "vehicule", "couleur", "vers", "depuis", "part", "duree", "courbe",
                 "fumee", "portiere", "retirer"),
    # Un geste dessiné sur le sprite que partagent tous les personnages.
    "geste": ("acteur", "geste", "duree", "vers"),
    # Un acteur passe une porte : `entrer` y marche puis disparaît ; `sortir` en
    # apparaît — d'une porte, ou du côté trottoir d'un char de la scène (`de`),
    # tourné vers `vers`.
    "entrer": ("acteur", "dans", "duree"),
    "sortir": ("acteur", "de", "vers"),
    # Le noir : `ferme` images pour y tomber, la caméra saute à `vers`, `ouvre`
    # images pour en sortir, `tient` images là-bas. ⚠️ Son PROPRE noir : un fondu de
    # porte fige la boucle, et la scène doit continuer pendant.
    "coupe": ("vers", "ferme", "ouvre", "tient"),
    # Des répliques de la scène (`repliques`, comptées à partir de 1 ; toutes par
    # défaut). La scène se joue SOUS elles.
    "dire": ("repliques",),
    # Le carton : `logo` (celui de l'accueil) ou `texte`, `sous` en petit.
    "titre": ("texte", "sous", "logo", "monte", "tenu", "descend"),
    # Un bruitage du catalogue (`sfx`), un morceau (`musique`), une boucle (`boucle`).
    "son": ("sfx", "musique", "boucle"),
    "attendre": ("duree",),
}
CLES_DE_TOUS_LES_PLANS = ("type", "ensemble", "fond")
COURBES = ("droite", "freine", "accelere")
GESTES = ("montrer", "donner", "prendre", "bras_croises", "hausser", "telephone")

#: L'OUVERTURE, MISE EN SCÈNE : le car de six heures entre au terminus, le
#: bonhomme en descend et marche jusqu'au quai, le car repart, le titre s'inscrit
#: — et le narrateur dit ses quatre phrases par-dessus. ⚠️ Elle était écrite EN DUR
#: dans `histoire.js` (265 lignes) ; la réécrire dans le vocabulaire, sans toucher
#: un seul de ses treize juges, est la preuve que les plans suffisent.
#:
#: `arret` (la rue devant le terminus, avec son sens) et `quai` (où l'on descend)
#: sont les deux lieux que `Histoire.ouverture` lui donne. Les temps sont ceux de
#: l'ancienne scène, en images (60 = une seconde) : 170 d'arrivée, 70 d'arrêt,
#: 130 de départ, et le titre 30 + 150 + 30.
SCENE_OUVERTURE: list[dict] = [
    {"type": "coupe", "ferme": 0, "ouvre": 45, "ensemble": True},
    {"type": "son", "musique": "ouverture"},
    {"type": "dire", "ensemble": True},
    {"type": "camera", "vers": "arret", "recul": 80},
    {"type": "conduire", "acteur": "car", "vehicule": "autobus", "vers": "arret", "depuis": 330,
     "duree": 170, "courbe": "freine", "fumee": 6, "portiere": True, "ensemble": True},
    {"type": "camera", "vers": "arret", "duree": 170, "courbe": "freine"},
    {"type": "attendre", "duree": 15},
    {"type": "sortir", "acteur": "joueur", "de": "car", "vers": "quai"},
    {"type": "marcher", "acteur": "joueur", "vers": "quai", "duree": 56, "ensemble": True},
    {"type": "camera", "vers": "quai", "lissage": 0.06},
    {"type": "attendre", "duree": 55},
    {"type": "conduire", "acteur": "car", "part": 330, "duree": 130, "courbe": "accelere",
     "fumee": 10, "portiere": True, "retirer": True},
    {"type": "camera", "vers": "quai", "lissage": 0.08},
    {"type": "titre", "logo": True, "sous": "BAIE-DES-BRUMES", "monte": 30, "tenu": 150, "descend": 30,
     "fond": True},
]


def erreurs_de_scene(scene: list[dict]) -> list[str]:
    """Ce qui ne va pas dans une scène, en clair (vide si elle se joue)."""
    erreurs = []
    if not scene:
        return ["scène vide"]
    for i, plan in enumerate(scene):
        genre = plan.get("type")
        if genre not in TYPES_PLANS:
            erreurs.append(f"plan {i} : type inconnu {genre!r}")
            continue
        inconnues = set(plan) - set(TYPES_PLANS[genre]) - set(CLES_DE_TOUS_LES_PLANS)
        if inconnues:
            erreurs.append(f"plan {i} ({genre}) : clés inconnues {sorted(inconnues)}")
        for cle in ("duree", "ferme", "ouvre", "tient", "monte", "tenu", "descend", "depuis", "part", "recul", "fumee",
                    "pres"):
            if cle in plan and (not isinstance(plan[cle], int) or plan[cle] < 0):
                erreurs.append(f"plan {i} ({genre}) : {cle} doit être un entier positif")
        if "lissage" in plan and not (isinstance(plan["lissage"], float) and 0 < plan["lissage"] <= 1):
            erreurs.append(f"plan {i} ({genre}) : lissage entre 0 et 1")
        if "courbe" in plan and plan["courbe"] not in COURBES:
            erreurs.append(f"plan {i} ({genre}) : courbe inconnue {plan['courbe']!r}")
        if genre == "geste" and plan.get("geste") not in GESTES:
            erreurs.append(f"plan {i} : geste inconnu {plan.get('geste')!r}")
        if genre in ("marcher", "geste", "entrer", "sortir", "conduire") and not plan.get("acteur"):
            erreurs.append(f"plan {i} ({genre}) : sans acteur")
        if genre == "conduire" and ("vers" in plan) == ("part" in plan):
            erreurs.append(f"plan {i} : un char ENTRE (`vers`) ou PART (`part`), pas les deux")
        if genre == "son" and sum(k in plan for k in ("sfx", "musique", "boucle")) != 1:
            erreurs.append(f"plan {i} : un son, et un seul")
        if genre == "titre" and not (plan.get("logo") or plan.get("texte")):
            erreurs.append(f"plan {i} : un titre sans texte ni logo")
    return erreurs

# --- Les missions, une par fichier ----------------------------------------
# ⚠️ Chaque mission vit dans `m1.py`, `m2.py`, … sous la forme `MISSION = {…}`
# (répliques écrites avec `_l`/`_p` de `_commun.py`). Ce fichier les réunit
# dans `CATALOGUE` : ajouter une mission = créer son fichier et l'ajouter
# aux deux listes ci-dessous, rien d'autre.
from . import m1, m2, m3, m4, m5, m6, m50, m97

CATALOGUE: list[Mission] = [m1.MISSION, m2.MISSION, m3.MISSION, m4.MISSION, m5.MISSION, m6.MISSION, m50.MISSION, m97.MISSION]


#: Les defis : un panneau en ville, un chrono, une prime — une seule fois.
DEFIS: list[dict] = [
    {"slug": "saut", "titre": "Le Grand Saut", "ou": "rampe", "vehicule": "moto", "vol_px": 60,
     "prime": 250, "texte": "SAUTE LA RAMPE EN MOTO : 60 PX DE VOL"},
    {"slug": "tour", "titre": "Tour du Faubourg", "ou": "porte:terminus", "tours": 3, "chrono_s": 120,
     "points": ["terminus", "garage", "hopital", "poste"], "prime": 250,
     "texte": "TROIS TOURS PAR LE GARAGE, L'HÔPITAL ET LE POSTE EN MOINS DE 2:00"},
    {"slug": "livraison", "titre": "Livraison sans bosse", "ou": "porte:garage", "lieu": "bar", "chrono_s": 90,
     "etoiles": 1, "prime": 250, "texte": "LIVRE TON CHAR AU BAR EN 90 S, SANS UNE BOSSE, AVEC LA POLICE AUX FESSES"},

    # --- LES TROIS JEUX D'ADRESSE DE LA FOIRE (bord de l'eau, 4e vague) -------
    #
    # ⚠️ **UN JEU D'ADRESSE EST UN DEFI, PAS UN MOTEUR**, et c'est la fiche du
    # plan qui l'ecrit en majuscules. Ils tiennent donc sur les rails de la v1 —
    # un lieu, un compte, un chrono, une prime, un texte en majuscules — et tout
    # ce qu'ils ajoutent au moteur est `a_pied` : on les joue debout devant un
    # comptoir, pas au volant.
    #
    # ⚠️ `ou` : `foire:<jeu>`, et AUCUN PANNEAU ne se plante (`creerPanneaux` ne
    # connait que `rampe` et `porte:`). C'est le COMPTOIR qu'on lit : un panneau
    # de defi au milieu d'une allee de foire, entre deux kiosques a trois tuiles
    # l'un de l'autre, serait un poteau de plus dans le seul endroit dense du
    # jeu — et la baraque dit deja ce qu'elle vend.
    #
    # ⚠️ **LA PRIME EST PETITE, ET C'EST LA REGLE DES PALIERS DE BOULOT** : un
    # defi de foire ne paie pas mieux a l'heure qu'un boulot honnete (juge :
    # `prime / chrono_s` sous le taux du taxi). Les trois ensemble rapportent
    # dix fois le billet d'entree — de quoi jouer, pas de quoi vivre. Ce qu'on
    # vient chercher au troisieme, c'est la CASQUETTE (`CASQUETTE_DE_LA_FOIRE`).
    {"slug": "tir", "titre": "La galerie de tir", "ou": "foire:galerie_tir", "a_pied": True,
     # ⚠️ **LE FORAIN PRÊTE SA CARABINE À BOUCHON** (`armes.carabine_foire`).
     # Avant, on crevait les cibles avec sa PROPRE arme à feu : la foule fuyait,
     # la police rappliquait, et un joueur sans arme à feu ne pouvait pas jouer
     # du tout (les poings n'atteignent pas les décors). `Histoire.commencerDefi`
     # prête la carabine — inoffensive, `foire` — et la reprend à la fin.
     "foire": True, "cibles": 3, "chrono_s": 30, "rayon_px": 120, "prime": 60,
     "consigne": "FRAPPE POUR TIRER",
     "texte": "LE FORAIN TE PRÊTE SA CARABINE : TIRE LES TROIS CIBLES EN 30 S"},
    # ⚠️ « Marteler ACTION contre un chrono : aucune statistique neuve, c'est le
    # BOUTON qui fait la force. » Le compte est en coups, pas en muscles.
    {"slug": "marteau", "titre": "Le marteau de force", "ou": "foire:marteau_force", "a_pied": True,
     # ⚠️ `rayon_px` : on a les mains dessus, mais on se tient DANS L'ALLEE —
     # deux tuiles et demie du comptoir, mesure au banc. A une tuile et demie,
     # on ne pouvait pas jouer sans monter sur la baraque.
     "foire": True, "coups": 25, "chrono_s": 10, "rayon_px": 44, "prime": 25,
     "consigne": "MARTÈLE ACTION",
     "texte": "MARTÈLE ACTION : 25 COUPS EN 10 S, ET LA CLOCHE SONNE"},
    # ⚠️ **ON LA GAGNE, ON NE LA VOLE PAS** : le canard ne s'accroche que quand
    # il passe sous le crochet, et un comptoir defonce ne rend pas un lot — il
    # met fin au jeu (`vole_pas`).
    {"slug": "canards", "titre": "La pêche aux canards", "ou": "foire:peche_canards", "a_pied": True,
     # ⚠️ `pose` : la FENETRE, c'est la pose du bassin ou le canard passe sous le
     # crochet — pas un chrono invente. Le dessin du kiosque (`peche_canards`,
     # `anime` + `variantes`) et la regle du jeu disent donc la MEME chose, et
     # un juge de banc le prouve en regardant la couche peinte : a cette
     # pose-la, un canard est sous la canne.
     "foire": True, "canards": 5, "chrono_s": 40, "rayon_px": 44, "prime": 90,
     "pose": 0, "vole_pas": True,
     "consigne": "ACTION QUAND IL PASSE SOUS LE CROCHET",
     "texte": "PÊCHE CINQ CANARDS : ACTION QUAND IL PASSE SOUS LE CROCHET"},
]

#: ⚠️ **LE LOT DU TROISIEME PALIER**, et rien d'autre ne la donne : la casquette
#: de la foire (`magasins.TENUES`) tombe quand les TROIS jeux d'adresse sont
#: gagnes. Le vestiaire existait deja et ne demande rien a personne — une tenue
#: de plus, c'est une ligne de catalogue, pas un moteur.
CASQUETTE_DE_LA_FOIRE = "casquette_foire"


def defis_de_foire() -> list[dict]:
    """Les jeux d'adresse de la foire, dans l'ordre du catalogue."""
    return [d for d in DEFIS if d.get("foire")]

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


#: L'ordre dans lequel se comptent les répliques d'une mission (le `n` du slug de voix).
PARTIES = ("appel", "intro", "client", "fin", "echec", "pendant")


def repliques() -> list[dict]:
    """Toutes les repliques de l'histoire, dans l'ordre, avec leur slug de voix.

    Le slug : `<qui>-<mission>-<n>` (n compte a travers appel, intro, client,
    fin, echec). Il ne depend que de la place de la replique : on peut changer
    un mot et regenerer une seule ligne avec `--refaire`.
    """
    sortie = []
    for mission in CATALOGUE:
        n = 0
        # ⚠️ `pendant` se compte APRES `echec` : insérée avant `fin`, elle renommerait
        # les voix de fin et d'échec déjà générées, et des mp3 payés deviendraient
        # des 404.
        for partie in PARTIES:
            for ligne in mission["dialogue"].get(partie, []):
                n += 1
                sortie.append({"slug": f"{ligne['qui']}-{mission['slug']}-{n}", "qui": ligne["qui"],
                               "texte": ligne["texte"], "mission": mission["slug"], "partie": partie,
                               "telephone": partie in ("appel", "echec")})
    return sortie


def repliques_ouverture() -> list[dict]:
    """Les repliques de l'ouverture, avec leur slug de voix.

    Meme forme que `repliques()`, et meme regle : le slug (`narrateur-ouverture-2`)
    ne depend que de la PLACE de la ligne, donc changer un mot se regenere a la
    ligne pres (`--refaire narrateur-ouverture-2`) sans toucher aux trois autres.

    ⚠️ `mission` vaut `"ouverture"` : c'est ce qui la range avec le journal du
    matin plutot qu'avec une mission, et ce qui permet au navigateur de charger
    ses quatre voix d'un coup (`Son.Voix.chargerHistoire('ouverture')`).
    """
    return [{"slug": f"{ligne['qui']}-ouverture-{i}", "qui": ligne["qui"], "texte": ligne["texte"],
             "mission": "ouverture", "partie": "ouverture", "telephone": False}
            for i, ligne in enumerate(OUVERTURE, start=1)]


#: Les acteurs qu'une scène de mission peut nommer, en plus des personnages : ce que
#: la mission pose (`vehicule`, la première `cible`, le `fuyard`) et le joueur.
ACTEURS_DE_MISSION = ("joueur", "donneur", "vehicule", "cible", "fuyard")
#: Les formes de lieu : un acteur, `place:<acteur>` (où il était au début de la
#: scène), et ce que `Histoire.resoudre` connaît — plus `chez:<personnage>`, la
#: porte de là où il se tient.
FORMES_DE_LIEU = ("place", "porte", "ruelle", "zone", "chez")


def _lieux_du_plan(plan: dict) -> list[str]:
    return [plan[cle] for cle in ("vers", "dans", "de") if isinstance(plan.get(cle), str)]


def erreurs_de_mise_en_scene(mission: dict) -> list[str]:
    """Ce qui manque à une mission pour être FINIE : ses scènes, ses répliques à
    chaque temps, et une fin qui ne parle pas par la bouche d'un absent."""
    slug, erreurs = mission["slug"], []
    scenes, dialogue = mission.get("scenes") or {}, mission["dialogue"]
    personnages = {p["slug"] for p in PERSONNAGES}
    for partie in ("intro", "fin", "echec"):
        if not dialogue.get(partie):
            erreurs.append(f"{slug} : pas de répliques {partie}")
    pendant = dialogue.get("pendant", []) + dialogue.get("client", [])
    if not pendant:
        erreurs.append(f"{slug} : aucune réplique pendant la mission")
    for ligne in dialogue.get("pendant", []):
        if not 0 <= ligne.get("objectif", -1) < len(mission["objectifs"]):
            erreurs.append(f"{slug} : une réplique pendant accrochée à un objectif qui n'existe pas")
    for partie in ("intro", "fin"):
        scene = scenes.get(partie)
        if not scene:
            erreurs.append(f"{slug} : pas de scène {partie}")
            continue
        erreurs += [f"{slug} {partie} : {e}" for e in erreurs_de_scene(scene)]
        acteurs = set(ACTEURS_DE_MISSION) | personnages
        for plan in scene:
            if plan.get("acteur") and plan["acteur"] not in acteurs:
                erreurs.append(f"{slug} {partie} : acteur inconnu {plan['acteur']!r}")
            for nom in _lieux_du_plan(plan):
                forme = nom.split(":", 1)[0] if ":" in nom else None
                if forme is None and nom not in acteurs:
                    erreurs.append(f"{slug} {partie} : lieu inconnu {nom!r}")
                elif forme is not None and forme not in FORMES_DE_LIEU:
                    erreurs.append(f"{slug} {partie} : forme de lieu inconnue {nom!r}")
                elif forme in ("place",) and nom[6:] not in acteurs:
                    erreurs.append(f"{slug} {partie} : {nom!r} n'est la place de personne")
                elif forme == "chez" and nom[5:] not in personnages:
                    erreurs.append(f"{slug} {partie} : {nom!r} n'est chez personne")
        # Chaque réplique de la partie est dite, et une seule fois.
        dites: list[int] = []
        for plan in scene:
            if plan["type"] == "dire":
                dites += plan.get("repliques") or list(range(1, len(dialogue.get(partie, [])) + 1))
        if sorted(dites) != list(range(1, len(dialogue.get(partie, [])) + 1)):
            erreurs.append(f"{slug} {partie} : les répliques dites {sorted(dites)} ne sont pas toutes, une fois")
    # ⚠️ UNE FIN QUI SE JOUE LOIN DU DONNEUR le fait venir (`sortir`, `marcher`) ou
    # va le voir chez lui (`coupe`) — sinon on entend quelqu'un qui n'est pas là.
    donneur = personnage(mission["donneur"])
    dernier = mission["objectifs"][-1] if mission["objectifs"] else {}
    chez_lui = donneur["ou"][6:] if donneur and donneur["ou"].startswith("porte:") else None
    loin = dernier.get("type") != "retourner" and dernier.get("lieu") != chez_lui
    if loin and scenes.get("fin"):
        noms = {"donneur", mission["donneur"]}
        vient = any(p["type"] in ("sortir", "marcher") and p.get("acteur") in noms for p in scenes["fin"])
        va_chez_lui = any(p["type"] == "coupe" and p.get("vers") in {"chez:" + mission["donneur"], "donneur"}
                          for p in scenes["fin"])
        if not (vient or va_chez_lui):
            erreurs.append(f"{slug} : la fin se joue loin de {mission['donneur']} et personne ne va le voir")
    return erreurs


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
