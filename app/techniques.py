"""Les techniques d'arts martiaux — les coups de rue et les cours du dojo.

Unités du moteur, comme `armes.py` : dégâts en points de vie, portée en pixels,
durées en images (60 par seconde). Une technique est une LIGNE DE TEMPS : une
suite d'étapes (une pose clé, sa durée, un décalage le long du regard `dx`, un
décalage vertical `dy`, une rotation `rot`, une hauteur `z`), dont UNE est
`actif` — c'est là que le coup porte, ou que la prise projette.

Les gestes (`static/js/techniques.js` choisit) :
- `tape` : FRAPPE en tapes ; `rang` est la place dans la chaîne (1, 2, 3…).
- `genou` : FRAPPE collé à la cible. `tenue` : FRAPPE tenue. `course` : FRAPPE
  en sprint. `roulade` : FRAPPE au sortir d'une roulade.
- `prise` : SAISIR relâché sans rien faire (repousser). `prise_frappe` : FRAPPE
  dans la prise. `prise_avant`, `prise_vers_soi`, `prise_cote` : le stick dans
  la prise, relatif à l'axe joueur → cible.
- `contre` : SAISIR pendant que l'ennemi arme son coup. `dos` : SAISIR tenu
  dans le dos de l'ennemi (`tenir` images).

`projete` : la distance du vol, en pixels (0 = on ne vole pas). `sans_sang` :
la victime ne saigne pas. `silencieuse` : ni cri, ni alerte autour.
"""

from __future__ import annotations

from typing import TypedDict

STYLES = ("rue", "boxe", "karate", "judo", "jiujitsu")
GESTES = ("tape", "genou", "tenue", "course", "roulade", "prise", "prise_frappe",
          "prise_avant", "prise_vers_soi", "prise_cote", "contre", "dos")
#: `debout` : la pose de marche (rien à dessiner) ; `frappe` : la pose de coup
#: qui existe déjà (`SPRITES.joueur.poses.frappe_*`). Les autres se dessinent
#: dans `sprites.js` sous `tech_<pose>_<bas|haut|cote>`.
POSES = ("debout", "frappe", "poing_arriere", "crochet", "genou", "pied_face", "pied_cote",
         "saisie", "hanche", "au_sol", "accroupi")
DESSINEES = POSES[2:]


class Etape(TypedDict):
    pose: str
    images: int
    dx: int
    dy: int
    rot: float
    z: int
    actif: bool


class Technique(TypedDict):
    slug: str
    nom: str
    style: str
    geste: str
    rang: int
    gratuite: bool
    prix: int
    degats: int
    portee: int
    arc: float
    renverse: bool
    assomme: bool
    projete: int
    tours: float
    silencieuse: bool
    sans_sang: bool
    tenir: int
    temps: list[Etape]


def _e(pose, images, *, dx=0, dy=0, rot=0.0, z=0, actif=False) -> Etape:
    return Etape(pose=pose, images=images, dx=dx, dy=dy, rot=rot, z=z, actif=actif)


def _t(slug, nom, style, geste, degats, portee, temps, *, rang=0, prix=0, arc=0.9,
       renverse=False, assomme=True, projete=0, tours=0.5, silencieuse=False,
       sans_sang=False, tenir=0) -> Technique:
    return Technique(slug=slug, nom=nom, style=style, geste=geste, rang=rang,
                     gratuite=style == "rue", prix=prix, degats=degats, portee=portee,
                     arc=arc, renverse=renverse, assomme=assomme, projete=projete,
                     tours=tours, silencieuse=silencieuse, sans_sang=sans_sang,
                     tenir=tenir, temps=temps)


CATALOGUE: list[Technique] = [
    # --- La rue : gratuite, pour tout le monde. Les poings de `armes.py` (8 de
    # dégâts, 12 px) restent la mesure : un direct EST le coup de poing d'avant.
    _t("direct_gauche", "Direct du gauche", "rue", "tape", 8, 12, rang=1, temps=[
        _e("debout", 3, dx=-1), _e("frappe", 4, dx=3, actif=True), _e("frappe", 3, dx=1), _e("debout", 2)]),
    _t("direct_droit", "Direct du droit", "rue", "tape", 8, 12, rang=2, temps=[
        _e("debout", 3, dx=-1), _e("poing_arriere", 4, dx=3, actif=True), _e("poing_arriere", 3, dx=1),
        _e("debout", 2)]),
    _t("crochet", "Crochet", "rue", "tape", 10, 12, rang=3, arc=1.4, temps=[
        _e("debout", 4, dx=-2, rot=-0.15), _e("crochet", 4, dx=2, rot=0.2, actif=True), _e("crochet", 4),
        _e("debout", 3)]),
    _t("genou", "Coup de genou", "rue", "genou", 10, 9, temps=[
        _e("debout", 3, dy=-1), _e("genou", 5, dx=2, z=2, actif=True), _e("debout", 4)]),
    _t("repousser", "Repousser", "rue", "prise", 0, 14, assomme=False, sans_sang=True, temps=[
        _e("saisie", 6, dx=3, actif=True), _e("debout", 4)]),
    _t("genoux_prise", "Genoux", "rue", "prise_frappe", 8, 14, temps=[
        _e("saisie", 2), _e("genou", 5, dx=1, z=2, actif=True), _e("saisie", 3)]),
    # --- Boxe
    _t("uppercut", "Uppercut", "boxe", "tape", 14, 12, rang=4, prix=300, renverse=True, temps=[
        _e("accroupi", 5, dy=1), _e("crochet", 4, z=3, actif=True), _e("crochet", 4, z=1), _e("debout", 4)]),
    # --- Karaté : plus loin, plus lent.
    _t("pied_circulaire", "Coup de pied circulaire", "karate", "tape", 14, 18, rang=5, prix=500,
       arc=2.4, renverse=True, temps=[
        _e("debout", 5, rot=-0.3), _e("pied_cote", 5, rot=0.6, actif=True), _e("pied_cote", 4, rot=1.2),
        _e("debout", 5)]),
    _t("pied_de_cote", "Coup de pied de côté", "karate", "tenue", 16, 20, prix=400, arc=0.8,
       renverse=True, projete=40, tours=0.0, temps=[
        _e("genou", 8, dx=-1), _e("pied_cote", 6, dx=3, actif=True), _e("pied_cote", 6, dx=2), _e("debout", 6)]),
    _t("pied_saute", "Coup de pied sauté", "karate", "course", 14, 22, prix=600, renverse=True, temps=[
        _e("accroupi", 4), _e("pied_face", 6, dx=6, z=6, actif=True), _e("pied_face", 4, dx=3, z=3),
        _e("accroupi", 5)]),
    _t("balayage", "Balayage", "karate", "roulade", 6, 16, prix=450, arc=6.3, renverse=True, temps=[
        _e("accroupi", 3, dy=2), _e("accroupi", 8, dy=2, actif=True), _e("debout", 5)]),
    # --- Judo : les projections. Pas de sang, et on assomme.
    _t("projection_hanche", "Projection de hanche", "judo", "prise_avant", 12, 14, prix=500,
       renverse=True, projete=28, sans_sang=True, temps=[
        _e("saisie", 4), _e("hanche", 10, dx=2, actif=True), _e("hanche", 6), _e("debout", 6)]),
    _t("grand_fauchage", "Grand fauchage", "judo", "prise_vers_soi", 12, 14, prix=500,
       renverse=True, projete=6, sans_sang=True, temps=[
        _e("saisie", 4), _e("pied_face", 8, dx=2, actif=True), _e("saisie", 6), _e("debout", 5)]),
    _t("sacrifice", "Sacrifice en cercle", "judo", "prise_cote", 14, 14, prix=700,
       renverse=True, projete=40, tours=1.0, sans_sang=True, temps=[
        _e("saisie", 4), _e("au_sol", 14, actif=True), _e("accroupi", 8), _e("debout", 4)]),
    # --- Jiu-jitsu
    _t("retournement_poignet", "Retournement du poignet", "jiujitsu", "contre", 12, 20, prix=800,
       renverse=True, projete=16, sans_sang=True, temps=[
        _e("saisie", 10, actif=True), _e("accroupi", 6), _e("debout", 4)]),
    _t("etranglement", "Étranglement", "jiujitsu", "dos", 999, 14, prix=900, silencieuse=True,
       sans_sang=True, tenir=90, temps=[
        _e("saisie", 90, actif=True), _e("debout", 6)]),
]


def par_slug(slug: str) -> Technique:
    return next(t for t in CATALOGUE if t["slug"] == slug)


def chaine() -> list[Technique]:
    """Les techniques de la chaîne de tapes, dans l'ordre des rangs."""
    return sorted((t for t in CATALOGUE if t["geste"] == "tape"), key=lambda t: t["rang"])
