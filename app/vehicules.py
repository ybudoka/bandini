"""Le parc automobile de Baie-des-Brumes — source unique des stats.

Le navigateur ne connait aucune de ces valeurs : il recoit ce catalogue et
conduit avec. Les unites sont celles du moteur : pixels par image (60 images
par seconde), radians par image pour le braquage, points de vie.

`phase` : 1 = present dans la premiere version (le navigateur a son sprite),
2 = vague suivante. Un test verifie que chaque vehicule de phase 1 a un sprite.
"""

from __future__ import annotations

from typing import TypedDict


class Vehicule(TypedDict):
    slug: str
    nom: str
    classe: str
    longueur: int
    largeur: int
    vitesse_max: float
    vitesse_recul: float
    acceleration: float
    frein: float
    friction: float
    braquage: float
    adherence: float
    adherence_frein: float
    masse: float
    vie: int
    places: int
    prix: int
    frequence: float
    couleurs: list[str]
    sprite: str
    police: bool
    sirene: bool
    alarme: bool
    ejecte: bool
    eau: bool
    phase: int


def _v(slug, nom, classe, lon, lat, vmax, accel, braquage, vie, places, prix, freq, couleurs,
       sprite, *, police=False, sirene=False, alarme=False, ejecte=False, eau=False,
       masse=1.0, phase=1) -> Vehicule:
    return Vehicule(
        slug=slug, nom=nom, classe=classe, longueur=lon, largeur=lat,
        vitesse_max=vmax, vitesse_recul=round(vmax * 0.33, 2), acceleration=accel,
        frein=round(accel * 2, 3), friction=0.995 if eau else 0.985,
        braquage=braquage, adherence=0.12 if not eau else 0.05, adherence_frein=0.035,
        masse=masse, vie=vie, places=places, prix=prix, frequence=freq,
        couleurs=couleurs, sprite=sprite, police=police, sirene=sirene, alarme=alarme,
        ejecte=ejecte, eau=eau, phase=phase,
    )


#: ⚠️ L'auto est la reference (vitesse 100 %). Les prix sont ceux du garage
#: clandestin de Ti-Guy pour un vehicule PROPRE ; la revente d'un vehicule vole
#: rapporte `economie.VENTE_FRACTION` de ce prix.
CATALOGUE: list[Vehicule] = [
    _v("auto", "Berline", "auto", 28, 14, 4.0, 0.06, 0.045, 100, 4, 600, 0.40,
       ["#c0392b", "#2c3e50", "#ecf0f1", "#27ae60", "#8e44ad", "#d35400"], "auto",
       alarme=False),
    _v("taxi", "Taxi", "auto", 28, 14, 3.8, 0.058, 0.047, 110, 4, 700, 0.12,
       ["#f1c40f"], "taxi"),
    _v("moto", "Moto", "moto", 20, 8, 5.2, 0.09, 0.07, 40, 2, 450, 0.15,
       ["#1a1a1a", "#c0392b", "#2980b9"], "moto", ejecte=True),
    _v("police", "Auto-patrouille", "auto", 28, 14, 4.4, 0.07, 0.05, 150, 4, 2500, 0.0,
       ["#ffffff"], "police", police=True, sirene=True, alarme=True),
    _v("camion", "Camion", "camion", 40, 16, 2.8, 0.03, 0.03, 300, 2, 1200, 0.10,
       ["#7f8c8d", "#c0392b", "#2c3e50"], "camion", masse=3.0, phase=2),
    _v("autobus", "Autobus", "camion", 48, 16, 2.6, 0.028, 0.025, 250, 12, 1500, 0.06,
       ["#2980b9"], "autobus", masse=3.0, phase=2),
    _v("ambulance", "Ambulance", "auto", 32, 15, 3.6, 0.05, 0.04, 180, 3, 1400, 0.04,
       ["#ffffff"], "ambulance", sirene=True, alarme=True, phase=2),
    _v("bateau", "Chaloupe", "bateau", 30, 12, 3.2, 0.02, 0.025, 120, 4, 2000, 0.05,
       ["#ecf0f1", "#2c3e50"], "bateau", eau=True, phase=2),
]

CLASSES = ("auto", "moto", "camion", "bateau")


def par_slug(slug: str) -> Vehicule | None:
    for vehicule in CATALOGUE:
        if vehicule["slug"] == slug:
            return vehicule
    return None


def de_phase(phase: int) -> list[Vehicule]:
    return [v for v in CATALOGUE if v["phase"] <= phase]
