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
    frequence: float
    phase: int


def _p(slug, nom, chandail, cheveux, peau, pantalon, *, sprite="joueur", vitesse=1.0,
       courage=0.0, temoin=0.3, vie=60, argent=(2, 20), arme=None, gang=None,
       intouchable=False, accompagne=None, metier=None, heures=None, frequence=1.0,
       phase=1) -> Pieton:
    return Pieton(
        slug=slug, nom=nom, sprite=sprite,
        couleurs={"c": chandail, "h": cheveux, "s": peau, "p": pantalon},
        vitesse=vitesse, courage=courage, temoin=temoin, vie=vie, argent=argent,
        arme=arme, gang=gang, intouchable=intouchable, accompagne=accompagne,
        metier=metier, heures=heures, frequence=frequence, phase=phase,
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
]

#: Les gangs : leur archetype, leur territoire (zone de la carte), leur humeur.
GANGS: list[dict] = [
    {"slug": "cravates", "nom": "Les Cravates", "pieton": "cravate", "zone": "cravates",
     "membres": 8, "hostile_si_arme": True, "hostile_toujours": False, "phase": 1},
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


def ordinaires() -> list[Pieton]:
    """Ceux qui peuplent la rue (gangs et metiers apparaissent autrement)."""
    return [p for p in CATALOGUE if p["frequence"] > 0 and p["gang"] is None]


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
