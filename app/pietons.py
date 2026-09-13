"""Qui marche dans Baie-des-Brumes — et comment chacun reagit a un coup.

Le navigateur ne connait aucune de ces valeurs : il recoit le catalogue et fait
marcher les gens avec. Les couleurs sont des ECHANGES DE PALETTE sur le sprite
du personnage (`c` chandail, `h` cheveux, `s` peau, `p` pantalon) : un seul
dessin, seize silhouettes.

`courage` decide de tout quand on frappe quelqu'un :
    0,0  il fuit toujours          (la dame, l'ado)
    0,5  il fuit ou il riposte     (l'ouvrier)
    1,0  il fonce                  (la Cravate)

`temoin` est la probabilite qu'il aille RACONTER le crime a un policier au lieu
de seulement fuir — c'est le deuxieme canal de detection de la police (M4).
"""

from __future__ import annotations

from typing import TypedDict


class Pieton(TypedDict):
    slug: str
    nom: str
    sprite: str
    couleurs: dict[str, str]
    vitesse: float
    courage: float
    temoin: float
    vie: int
    argent: tuple[int, int]
    arme: str | None
    gang: str | None
    intouchable: bool
    accompagne: str | None
    metier: str | None
    heures: tuple[float, float] | None
    districts: tuple[str, ...] | None
    frequence: float
    phase: int


def _p(slug, nom, chandail, cheveux, peau, pantalon, *, sprite="joueur", vitesse=1.0,
       courage=0.0, temoin=0.3, vie=60, argent=(2, 20), arme=None, gang=None,
       intouchable=False, accompagne=None, metier=None, heures=None, districts=None,
       frequence=1.0, phase=1) -> Pieton:
    return Pieton(
        slug=slug, nom=nom, sprite=sprite,
        couleurs={"c": chandail, "h": cheveux, "s": peau, "p": pantalon},
        vitesse=vitesse, courage=courage, temoin=temoin, vie=vie, argent=argent,
        arme=arme, gang=gang, intouchable=intouchable, accompagne=accompagne,
        metier=metier, heures=heures, districts=districts,
        frequence=frequence, phase=phase,
    )


#: ⚠️ `frequence` est un POIDS, pas une probabilite : le navigateur tire
#: dedans. La somme n'a pas besoin de faire 1, et ajouter un archetype ne
#: rend donc pas les autres faux.
CATALOGUE: list[Pieton] = [
    _p("passant", "Passant", "#3a6ea5", "#3a2a1a", "#e8b088", "#2a2a3a",
       frequence=3.0, argent=(5, 25)),
    _p("passante", "Passante", "#b2558a", "#5a3a1a", "#f0c098", "#3a3a4a",
       frequence=3.0, argent=(5, 30), temoin=0.45),
    _p("ouvrier", "Ouvrier", "#d98324", "#2a2a2a", "#c98d66", "#3f4a5a",
       courage=0.5, vie=80, vitesse=0.95, frequence=2.0, argent=(10, 40), temoin=0.2),
    _p("ado", "Ado en planche", "#27ae60", "#1a1a1a", "#e8b088", "#4a4a6a",
       vitesse=1.2, frequence=1.5, argent=(2, 12), temoin=0.15),
    _p("dame", "Dame du Faubourg", "#8e44ad", "#c9c9c9", "#f0c098", "#2a2a3a",
       vitesse=0.8, frequence=1.5, argent=(15, 60), temoin=0.6),
    _p("cravate", "Cravate", "#2c3e50", "#1a1a1a", "#e8b088", "#1f2a36",
       courage=0.9, vie=90, vitesse=1.05, argent=(20, 80), arme="batte",
       gang="cravates", frequence=0.0, temoin=0.0),
    # v2 / M8 — les quatre gangs des nouveaux districts. Meme regle que les
    # Cravates : frequence 0, ils ne naissent QUE sur leur territoire.
    _p("morue", "Une Morue", "#1d6f6f", "#3a2a1a", "#c98d66", "#2a3540",
       courage=0.85, vie=95, vitesse=0.95, argent=(15, 70), arme="batte",
       gang="morues", frequence=0.0, temoin=0.0),
    _p("chevreuil", "Un Chevreuil", "#8a5a2b", "#4a3320", "#e8b088", "#3a2f22",
       courage=0.7, vie=80, vitesse=1.1, argent=(20, 90), arme="batte",
       gang="chevreuils", frequence=0.0, temoin=0.0),
    _p("boulonneux", "Un Boulonneux", "#5a5f66", "#2a2a2a", "#c98d66", "#2f3338",
       courage=0.95, vie=105, vitesse=0.9, argent=(10, 55), arme="batte",
       gang="boulonneux", frequence=0.0, temoin=0.0),
    _p("skateux", "Un Skateux", "#9b3fa8", "#1a1a1a", "#e8b088", "#2a2a3a",
       courage=0.55, vie=70, vitesse=1.3, argent=(5, 40), arme=None,
       gang="skateux", frequence=0.0, temoin=0.0),
    # ⚠️ Les passants de quartier : `districts` les ENFERME chez eux. Un
    # debardeur aux Erables, un banlieusard sur les quais, et les cinq
    # quartiers redeviennent le meme quartier repeint.
    _p("docker", "Débardeur", "#c8842a", "#2a2a2a", "#c98d66", "#38404a",
       courage=0.6, vie=90, vitesse=0.95, argent=(15, 55), temoin=0.15,
       districts=("quais",), frequence=2.4),
    _p("banlieusard", "Banlieusard", "#7f9a4e", "#5a3a1a", "#f0c098", "#454f38",
       courage=0.2, vie=65, vitesse=0.9, argent=(20, 80), temoin=0.65,
       districts=("erables",), frequence=2.4),
    _p("machiniste", "Machiniste", "#4a5a75", "#1a1a1a", "#c98d66", "#2a3240",
       courage=0.55, vie=85, vitesse=0.95, argent=(12, 50), temoin=0.2,
       districts=("shop",), frequence=2.2),
    _p("promeneur", "Promeneur de chien", "#2f8f6a", "#6b4b2c", "#e8b088", "#3a3a4a",
       courage=0.1, vie=60, vitesse=0.85, argent=(10, 45), temoin=0.55,
       districts=("pointe",), frequence=2.2),
    _p("itinerant", "Itinérant", "#6b5a48", "#6b5a48", "#c98d66", "#4a4438",
       vitesse=0.75, courage=0.2, frequence=1.0, argent=(1, 8), temoin=0.1),
    _p("livreur", "Livreur", "#c0392b", "#3a2a1a", "#c98d66", "#2a2a3a",
       vitesse=1.1, courage=0.3, vie=70, frequence=1.2, argent=(10, 35), temoin=0.25),
    # ⚠️ L'ENFANT EST INTOUCHABLE. Le jeu est adulte : on y meurt, le sang
    # coule. Un enfant, non — aucune arme ne l'atteint, aucun char ne le
    # renverse, il detale bien avant. C'est une regle du moteur
    # (`intouchable`), pas une consigne qu'on peut oublier de suivre.
    _p("enfant", "Enfant", "#f1c40f", "#6b4b2c", "#f0c098", "#2f6b8a", sprite="enfant",
       vitesse=1.15, vie=40, argent=(0, 3), temoin=0.5, intouchable=True,
       frequence=1.2),
    _p("mere", "Mère avec son petit", "#16a085", "#4a3320", "#f0c098", "#3a3a4a",
       vitesse=0.85, vie=65, argent=(10, 45), temoin=0.7, accompagne="enfant",
       frequence=1.4),
    # La Brume, la nuit : elles travaillent pres du bar et du port. Elles
    # vendent de la COMPAGNIE (voir economie.TARIFS) et rien ne se montre.
    _p("racoleuse", "Fille de la Brume", "#e0397a", "#1a1a1a", "#f0c098", "#2a2a3a",
       vitesse=0.9, vie=60, argent=(20, 90), temoin=0.2, metier="compagnie",
       heures=(0.78, 0.28), frequence=0.0),
    _p("vendeur", "Marchand ambulant", "#ecf0f1", "#3a2a1a", "#c98d66", "#2a3a4a",
       vitesse=0.0, vie=70, argent=(20, 70), temoin=0.5, metier="ambulant",
       frequence=0.0),
    # L'agent : un pieton que la police dirige quand il poursuit. Il patrouille
    # sur les trottoirs comme tout le monde, arme au ceinturon, et ne nait
    # jamais au hasard — `police.js` en place autant que la zone en demande.
    _p("policier", "Agent", "#1f3a6e", "#101018", "#e8b088", "#16264a",
       vitesse=1.0, courage=1.0, temoin=0.0, vie=100, argent=(0, 0), arme="pistolet",
       metier="police", frequence=0.0),
]

#: Les gangs : leur archetype, leur territoire (zone de la carte), leur humeur.
GANGS: list[dict] = [
    {"slug": "cravates", "nom": "Les Cravates", "pieton": "cravate", "zone": "cravates",
     "district": "faubourg", "membres": 8, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    # v2 / M8 — une gang par district. Les Boulonneux sont les seuls a ne pas
    # attendre que tu sortes une arme : La Shop n'est a personne d'autre.
    {"slug": "morues", "nom": "Les Morues", "pieton": "morue", "zone": "morues",
     "district": "quais", "membres": 8, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    {"slug": "chevreuils", "nom": "Les Chevreuils", "pieton": "chevreuil", "zone": "chevreuils",
     "district": "erables", "membres": 6, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    {"slug": "boulonneux", "nom": "Les Boulonneux", "pieton": "boulonneux", "zone": "boulonneux",
     "district": "shop", "membres": 9, "hostile_si_arme": True,
     "hostile_toujours": True, "phase": 1},
    {"slug": "skateux", "nom": "Les Skateux", "pieton": "skateux", "zone": "skateux",
     "district": "pointe", "membres": 6, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
]

#: Ce qui arrive a un pieton qu'on frappe, en images (60 par seconde).
REACTIONS = {
    "recul_images": 12,          # il titube
    "ko_images": 300,            # assomme : il se releve apres 5 s
    "fuite_secondes": 8,         # combien de temps il court avant de se calmer
    "peur_rayon_tuiles": 7,      # qui voit le coup et prend peur
    "saignement_images": 240,    # duree max d'un saignement
    "degats_saignement": 1,      # points de vie par seconde de saignement
    "pickpocket_images": 45,     # le temps de faire les poches
    "pickpocket_dos_degres": 90, # il faut etre DERRIERE lui
    "enfant_peur_tuiles": 12,    # un enfant detale de bien plus loin
    "suite_distance_px": 26,     # a quelle distance l'enfant suit sa mere
}

#: Un piéton assomme rapporte ses poches ; un mort ne rapporte rien de plus.
SLUGS = tuple(p["slug"] for p in CATALOGUE)


def par_slug(slug: str) -> Pieton | None:
    for pieton in CATALOGUE:
        if pieton["slug"] == slug:
            return pieton
    return None


def ordinaires(district: str | None = None) -> list[Pieton]:
    """Ceux qui peuplent la rue (gangs et metiers apparaissent autrement).

    Sans district : ceux de partout. Avec : ceux de partout PLUS ceux de ce
    quartier-la — jamais ceux du quartier d'a cote.
    """
    return [p for p in CATALOGUE if p["frequence"] > 0 and p["gang"] is None
            and (p["districts"] is None or (district in (p["districts"] or ())))]


def de_metier(metier: str) -> list[Pieton]:
    return [p for p in CATALOGUE if p["metier"] == metier]


def travaille_a(pieton: Pieton, heure: float) -> bool:
    """`heures` = (debut, fin) sur 24 h ramenees a 0..1 ; peut passer minuit."""
    creneau = pieton["heures"]
    if not creneau:
        return True
    debut, fin = creneau
    return debut <= heure < fin if debut < fin else (heure >= debut or heure < fin)


def exporter() -> dict:
    return {
        "catalogue": CATALOGUE,
        "gangs": GANGS,
        "reactions": dict(REACTIONS),
        "poids_total": round(sum(p["frequence"] for p in ordinaires()), 3),
    }
