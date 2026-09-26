"""Le garage qui modifie les chars (docs/jalons/le-garage-qui-modifie-les-chars.md).

Chez Ti-Guy, au Garage Rocco Bandini, on ne fait plus que réparer, repeindre et racheter : on GARDE un
char et on l'améliore. Cinq pièces, posées une fois chacune, sur le char garé devant le rideau
(`Missions.menuGarage`, `static/js/garage.js`) :

- le MOTEUR gonflé : la vitesse de pointe ET l'accélération, du même facteur — ⚠️ la vitesse de pointe
  est un équilibre entre l'accélération et la friction (`vehicules.friction_pour`, le camion de paie de
  s03) : gonfler l'une sans l'autre, et le char n'atteint jamais ce qu'on lui a promis ;
- le BLINDAGE : des points de vie de tôle en plus ;
- les PNEUS D'HIVER : la neige et le verglas ne lui prennent qu'une part de l'adhérence et du frein ;
- la NITRO : une poussée au bouton libre du volant (SAISIR), qui se recharge ;
- le KLAXON qui joue « Gens du pays ».

⚠️ **LES PIÈCES VOYAGENT AVEC LE CHAR** (`v.mods`) : devant la planque et dans les planques des blocs
(la sauvegarde), à la fourrière — un char modifié qui y part revient modifié, et se rachète plus cher.
"""

from __future__ import annotations

#: Les pièces, dans l'ordre du menu. `effet` : ce que le navigateur applique.
PIECES: list[dict] = [
    {"slug": "moteur", "nom": "Moteur gonflé", "prix": 600, "effet": {"vitesse": 1.2}},
    {"slug": "blindage", "nom": "Blindage", "prix": 800, "effet": {"vie": 1.6}},
    {"slug": "pneus", "nom": "Pneus d'hiver", "prix": 250, "effet": {"garde": 0.6}},
    {"slug": "nitro", "nom": "Nitro", "prix": 900, "effet": {"poussee": 1.35, "duree_s": 1.5, "recharge_s": 10}},
    {"slug": "klaxon", "nom": "Klaxon « Gens du pays »", "prix": 150, "effet": {}},
]

#: Les chars qui ne se modifient pas : un vélo n'a pas de moteur à gonfler.
CLASSES_EXCLUES = ("velo",)

#: La part du prix des pièces que la fourrière ajoute au rachat d'un char modifié.
RACHAT_PART = 0.5

#: L'air du klaxon : (note en Hz, durée en secondes), joué au bouton du klaxon, au volant seulement.
#: ⚠️ **PAS ENCORE LE BON AIR** (26 sept. 2026) : la mélodie de « Gens du pays » n'a pas été transcrite
#: note pour note — ces six notes sont une fanfare de klaxon qui monte, en attendant la vraie phrase
#: (« Gens du pa-ys, c'est vo-tre tour »). C'est une DONNÉE : la remplacer ne demande aucun code.
KLAXON_AIR: list[list[float]] = [
    [392.0, 0.18], [523.3, 0.18], [659.3, 0.18], [784.0, 0.36], [659.3, 0.18], [784.0, 0.6],
]

#: Ce que Ti-Guy dit quand une pièce est posée. Le slug de la voix : `ti_guy-garage-<cle>` ; le jeu
#: d'acteur est dans `interpretation.JEU`. ⚠️ Pas de nom : c'est Ti-Guy, dans son garage, qu'on connaît.
REPLIQUES: list[dict] = [
    {"cle": "moteur", "texte": "Écoute-moi ça ronronner. Y va te décoller les plombages, mon homme."},
    {"cle": "blindage", "texte": "De la tôle de camion blindé. Les balles vont rebondir, pas toi."},
    {"cle": "pneus", "texte": "Des bons pneus d'hiver. Tu vas coller à la glace comme ta langue sur un poteau."},
    {"cle": "nitro", "texte": "La bonbonne est branchée. Appuie pas là-dessus dans un stationnement."},
    {"cle": "klaxon", "texte": "Klaxonne pour voir. Si ça te donne pas des frissons, t'es pas d'icitte."},
]


def valeur(mods: dict | None) -> int:
    """Le prix des pièces posées sur un char."""
    return sum(p["prix"] for p in PIECES if (mods or {}).get(p["slug"]))


def repliques() -> list[dict]:
    """Les voix de Ti-Guy au garage, rangées ensemble (`mission: "garage"`) : le navigateur les charge
    d'un coup (`Son.Voix.chargerHistoire('garage')`)."""
    return [{"slug": f"ti_guy-garage-{r['cle']}", "qui": "ti_guy", "texte": r["texte"],
             "mission": "garage", "partie": "garage", "telephone": False} for r in REPLIQUES]


def exporter() -> dict:
    return {"pieces": [dict(p, effet=dict(p["effet"])) for p in PIECES], "classes_exclues": list(CLASSES_EXCLUES),
            "rachat_part": RACHAT_PART, "klaxon_air": [list(n) for n in KLAXON_AIR],
            "repliques": {r["cle"]: r["texte"] for r in REPLIQUES}}
