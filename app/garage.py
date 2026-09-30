"""Le garage qui modifie les chars (docs/jalons/le-garage-qui-modifie-les-chars.md).

Chez Ti-Guy, au Garage Rocco Bandini, on ne fait plus que réparer, repeindre et racheter : on GARDE un
char et on l'améliore. Quatre pièces, posées une fois chacune, et un klaxon au choix, sur le char garé
devant le rideau (`Missions.menuGarage`, `static/js/garage.js`) :

- le MOTEUR gonflé : la vitesse de pointe ET l'accélération, du même facteur — ⚠️ la vitesse de pointe
  est un équilibre entre l'accélération et la friction (`vehicules.friction_pour`, le camion de paie de
  s03) : gonfler l'une sans l'autre, et le char n'atteint jamais ce qu'on lui a promis ;
- le BLINDAGE : des points de vie de tôle en plus ;
- les PNEUS D'HIVER : la neige et le verglas ne lui prennent qu'une part de l'adhérence et du frein ;
- la NITRO : une poussée au bouton libre du volant (SAISIR), qui se recharge ;
- le KLAXON (`KLAXONS`), un seul à la fois : « Gens du pays », « Le Parrain », « La Cucaracha », la corne
  à air d'un 18 roues, la voix de Ti-Guy, ou le faux whoop-whoop de police (docs/jalons/les-klaxons-de-ti-guy.md).

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
]

#: Les chars qui ne se modifient pas : un vélo n'a pas de moteur à gonfler, et une coque
#: ne passe pas la porte de Ti-Guy (les bateaux ne sont pas des chars).
CLASSES_EXCLUES = ("velo", "bateau")

#: La part du prix des pièces que la fourrière ajoute au rachat d'un char modifié.
RACHAT_PART = 0.5

#: L'air du klaxon « Gens du pays » : (note en Hz, durée en secondes), joué au bouton du klaxon, au volant
#: seulement.
#: « Gens du pa-ys, c'est vo-tre tour » — le début du refrain de Gilles Vigneault, en fa majeur, à 3/4
#: (la partition des Choralies que Martin a fournie le 27 sept. 2026, chant 1, mesures 5 à 8) : trois
#: noires qui descendent, une blanche pointée qui remonte, deux fois. La noire à 0,2 s : un klaxon ne
#: chante pas, il claironne.
NOIRE = 0.2
KLAXON_AIR: list[list[float]] = [
    [440.00, NOIRE], [392.00, NOIRE], [349.23, NOIRE], [523.25, 3 * NOIRE],     # Gens du pa-ys (la sol fa do)
    [440.00, NOIRE], [392.00, NOIRE], [349.23, NOIRE], [587.33, 3 * NOIRE],     # c'est vo-tre tour (la sol fa ré)
]

_DEMI_TONS = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def note(nom: str) -> float:
    """La fréquence d'une note (« E4 »), au tempérament égal, la 440 — arrondie au centième."""
    return round(440.0 * 2 ** ((_DEMI_TONS[nom[0]] + 12 * (int(nom[1]) - 4)) / 12), 2)


#: « Le Parrain » (le thème d'amour de Nino Rota, en la mineur) : mi la do si la do, la si la fa sol mi —
#: ce que jouent les cornes à cinq trompettes des autos de parade. Des noires égales, le mi du bout tenu.
NOIRE_PARRAIN = 0.24
AIR_PARRAIN: list[list[float]] = (
    [[note(n), NOIRE_PARRAIN] for n in ("E4", "A4", "C5", "B4", "A4", "C5", "A4", "B4", "A4", "F4", "G4")]
    + [[note("E4"), 3 * NOIRE_PARRAIN]])

#: « La Cucaracha », en fa majeur : do do do fa la, deux fois (trois croches, une noire, une blanche), puis
#: fa fa mi mi ré ré do — le classique des cornes à air.
CROCHE = 0.13
AIR_CUCARACHA: list[list[float]] = (
    2 * [[note("C4"), CROCHE], [note("C4"), CROCHE], [note("C4"), CROCHE], [note("F4"), 2 * CROCHE],
         [note("A4"), 4 * CROCHE]]
    + [[note(n), CROCHE] for n in ("F4", "F4", "E4", "E4", "D4", "D4")] + [[note("C4"), 4 * CROCHE]])

#: Ce que Ti-Guy a enregistré dans le klaxon « La voix de Ti-Guy » : une engueulade par coup, tirée à
#: l'empreinte, jamais deux fois la même de suite (`Garage.klaxonner`). Slug : `ti_guy-garage-crie-<n>`.
ENGUEULADES: list[str] = [
    "Tasse-toé!",
    "Enweye, avance!",
    "Heille, le cave! T'as-tu eu ton permis dans une boîte de Cracker Jack?",
    "Bouge de d'là!",
    "C'est vert! Ça virera pas plus vert que ça!",
]

#: LES KLAXONS (docs/jalons/les-klaxons-de-ti-guy.md, Martin, 30 sept. 2026) : UN à la fois ; en poser un
#: autre remplace le premier. `v.mods.klaxon` porte son slug — ⚠️ un vieux `true` (les sauvegardes d'avant)
#: est « Gens du pays ». Ce qu'il fait entendre, un seul des trois :
#: - `air` : des notes, claironnées par la corne synthétisée (`Son.SFX.claironner`) ;
#: - `son` : un échantillon (ElevenLabs), rangé dans le lieu `klaxons` (`audio.LIEUX`) ;
#: - `voix` : les engueulades de Ti-Guy (`ENGUEULADES`).
#: `portee` : ce que le klaxon multiplie à la portée où l'on se tasse (les passants, l'orignal).
#: `cede` : le trafic devant change de voie, comme devant une auto-patrouille. `delit` : ce qu'un vrai
#: policier à `oreille_tuiles` en pense (`recherche.DELITS`). `replique` : la clé de `REPLIQUES`, si ce n'est
#: pas son slug.
KLAXONS: list[dict] = [
    {"slug": "gens_du_pays", "nom": "Klaxon « Gens du pays »", "prix": 150, "air": KLAXON_AIR,
     "replique": "klaxon"},
    {"slug": "parrain", "nom": "Klaxon « Le Parrain »", "prix": 200, "air": AIR_PARRAIN},
    {"slug": "cucaracha", "nom": "Klaxon « La Cucaracha »", "prix": 150, "air": AIR_CUCARACHA},
    {"slug": "corne_a_air", "nom": "Corne à air de 18 roues", "prix": 300, "son": "corne_a_air", "portee": 2.0},
    {"slug": "ti_guy", "nom": "La voix de Ti-Guy", "prix": 250,
     "voix": [f"ti_guy-garage-crie-{i}" for i in range(1, len(ENGUEULADES) + 1)]},
    {"slug": "police", "nom": "Whoop-whoop de police", "prix": 400, "son": "whoop_police", "cede": True,
     "delit": "fausse_sirene", "oreille_tuiles": 12},
]


def klaxon(mods: dict | None) -> dict | None:
    """Le klaxon posé (`mods.klaxon`), ou None. Un vieux `true` : « Gens du pays »."""
    k = (mods or {}).get("klaxon")
    if not k:
        return None
    slug = "gens_du_pays" if k is True else k
    return next((q for q in KLAXONS if q["slug"] == slug), None)


#: Ce que Ti-Guy dit quand une pièce est posée. Le slug de la voix : `ti_guy-garage-<cle>` ; le jeu
#: d'acteur est dans `interpretation.JEU`. ⚠️ Pas de nom : c'est Ti-Guy, dans son garage, qu'on connaît.
REPLIQUES: list[dict] = [
    {"cle": "moteur", "texte": "Écoute-moi ça ronronner. Y va te décoller les plombages, mon homme."},
    {"cle": "blindage", "texte": "De la tôle de camion blindé. Les balles vont rebondir, pas toi."},
    {"cle": "pneus", "texte": "Des bons pneus d'hiver. Tu vas coller à la glace comme ta langue sur un poteau."},
    {"cle": "nitro", "texte": "La bonbonne est branchée. Appuie pas là-dessus dans un stationnement."},
    {"cle": "klaxon", "texte": "Klaxonne pour voir. Si ça te donne pas des frissons, t'es pas d'icitte."},
    {"cle": "parrain", "texte": "Le Parrain. Tu klaxonnes, pis le monde reçoit une offre qu'y peut pas refuser : se tasser."},
    {"cle": "cucaracha", "texte": "La Cucaracha. Mon beau-frère avait ça sur sa Camaro. Y s'est jamais remarié."},
    {"cle": "corne_a_air", "texte": "Une corne de dix-huit roues. Klaxonne pas en arrière d'une matante, a va perdre son dentier."},
    {"cle": "ti_guy", "texte": "J'ai enregistré ma voix là-dedans. Même quand chus pas là, j'engueule le monde pour toi."},
    {"cle": "police", "texte": "Un whoop-whoop de police. Les chars se tassent… mais si un vrai bœuf l'entend, t'es dans marde."},
]


def valeur(mods: dict | None) -> int:
    """Le prix des pièces posées sur un char, son klaxon compris."""
    k = klaxon(mods)
    return sum(p["prix"] for p in PIECES if (mods or {}).get(p["slug"])) + (k["prix"] if k else 0)


def repliques() -> list[dict]:
    """Les voix de Ti-Guy au garage, rangées ensemble (`mission: "garage"`) : le navigateur les charge
    d'un coup (`Son.Voix.chargerHistoire('garage')`) — ses commentaires, et ses engueulades du klaxon."""
    return ([{"slug": f"ti_guy-garage-{r['cle']}", "qui": "ti_guy", "texte": r["texte"],
              "mission": "garage", "partie": "garage", "telephone": False} for r in REPLIQUES]
            + [{"slug": f"ti_guy-garage-crie-{i}", "qui": "ti_guy", "texte": t,
                "mission": "garage", "partie": "garage", "telephone": False}
               for i, t in enumerate(ENGUEULADES, start=1)])


def exporter() -> dict:
    """Le garage du paquet : les pièces et ce que Ti-Guy en dit. ⚠️ Les klaxons n'y sont pas : ils voyagent dans
    la suite (`exporter_klaxons`, `definitions.DANS_LA_SUITE`)."""
    pieces = {p["slug"] for p in PIECES}
    return {"pieces": [dict(p, effet=dict(p["effet"])) for p in PIECES], "classes_exclues": list(CLASSES_EXCLUES),
            "rachat_part": RACHAT_PART,
            "repliques": {r["cle"]: r["texte"] for r in REPLIQUES if r["cle"] in pieces}}


def exporter_klaxons() -> list[dict]:
    """Les klaxons, avec le texte de ce que Ti-Guy en dit (`texte`). ⚠️ DANS LA SUITE DU PAQUET
    (`definitions.DANS_LA_SUITE`, 30 sept. 2026) : leurs airs ne tenaient pas sous le plafond, et personne ne
    klaxonne à l'écran titre. Tant qu'ils ne sont pas là, le klaxon ordinaire joue et le menu n'en montre aucun."""
    textes = {r["cle"]: r["texte"] for r in REPLIQUES}
    return [dict(k, texte=textes[k.get("replique", k["slug"])], **({"air": [list(n) for n in k["air"]]} if "air" in k else {}))
            for k in KLAXONS]
