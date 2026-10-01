"""Les enseignes qu'on dévisse la nuit (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md),
la cinquième famille des collections.

Douze **enseignes-drapeaux** — pas le bandeau du commerce (c'est la façade : il garde sa place et son nom), mais
l'enseigne qui pend au bout, au-dessus du trottoir, là où les autres commerces ont une pancarte muette. Les douze
qui ont du caractère y portent un NÉON à leur emblème (une grille de 5 × 7 et sa palette, comme les bebelles), qui
luit la nuit. On la dévisse la nuit, à pied, au tournevis (`static/js/devisser.js`) ; elle monte au mur de la
planque (`decoration.py`, `mur_enseignes`).

⚠️ **SUR LA VILLE FINIE ET SANS UN DÉ** : rien ne se pose, tout se PEINT. La règle LIT `ville["devantures"]` : pour
chaque enseigne, la devanture qui porte un de ses noms ET une pancarte, dans son district d'abord, la première en
ordre de lecture. Elle ne touche à aucune liste — la ville est la même à l'octet (`test_enseignes_devissees`).

⚠️ **LE SLUG EST LE NOM** : la sauvegarde garde `partie.collections.enseignes[slug]`, jamais un index ; l'ORDRE du
catalogue est la place sur le mur de la planque (trois rangées de quatre).

⚠️ **LE POIDS** : rien dans les définitions ni dans la carte — tout voyage sur `/api/collections`.
"""

from __future__ import annotations

import zlib

from . import garderobe


def _e(slug: str, nom: str, district: str, textes: tuple[str, ...], lignes: tuple[str, str],
       grille: str, palette: dict) -> dict:
    return {"slug": slug, "nom": nom, "district": district, "textes": textes, "lignes": lignes,
            "grille": grille.strip().split(), "palette": palette}


#: Les douze, dans l'ordre du mur de la planque. `textes` : les noms de devanture qu'elle peut prendre, dans
#: l'ordre de préférence ; `grille` : l'emblème du néon, 5 × 7, une lettre par couleur de `palette` (`.` = le fond
#: sombre du néon). Le ton de docs/ecrire-drole.md : on frappe le proprio, jamais le client.
ENSEIGNES: tuple[dict, ...] = (
    _e("bingo", "LE BINGO DU SOUS-SOL", "faubourg", ("BINGO",),
       ("LE CONSEIL DE FABRIQUE LA CHERCHERA.", "IL CHERCHE ENCORE LA QUÊTE DE 1971."), """
.rrr.
rrwrr
rwbwr
rwwwr
rwbwr
rrwrr
.rrr.
""", {"r": "#e8443a", "w": "#fff4e0", "b": "#2a2a6a"}),
    _e("clairon", "LE CLAIRON", "faubourg", ("LE CLAIRON",),
       ("LOUISE EN FERA SA UNE.", "POUR UNE FOIS, C’EST VRAI."), """
.....
...yy
y.yyy
yyyyy
y.yyy
...yy
.....
""", {"y": "#f0c040"}),
    _e("tipaul", "CHEZ TI-PAUL", "erables", ("CHEZ TI-PAUL",),
       ("OUVERT SEPT JOURS, VINGT-QUATRE HEURES.", "L’ENSEIGNE, ELLE, A PRIS CONGÉ."), """
..g..
..g..
.ggg.
.rrr.
.rwr.
.rrr.
.ggg.
""", {"g": "#4ab84a", "r": "#e8443a", "w": "#fff4e0"}),
    _e("lave_auto", "LE LAVE-AUTO", "erables", ("LAVE-AUTO",),
       ("GARANTIE SANS ÉGRATIGNURES.", "ON A PRIS L’ENSEIGNE AVEC DES GANTS."), """
.c...
cwc..
.c.c.
..cwc
.c.c.
cwc..
.c...
""", {"c": "#6ac8ff", "w": "#ffffff"}),
    _e("rialto", "LE CINÉMA RIALTO", "shop", ("CINÉMA RIALTO",),
       ("LE PROPRIO DIT QUE C’EST UN MONUMENT.", "LE MONUMENT EST CHEZ NOUS."), """
.sss.
sdsds
sssss
sdsds
.sss.
..s..
.sss.
""", {"s": "#ff5aa8", "d": "#3a1030"}),
    _e("quilles", "LA SALLE DE QUILLES", "shop", ("SALLE DE QUILLES", "QUILLES"),
       ("LA LIGUE DU MARDI NE S’EN EST PAS APERÇUE :", "ELLE NE REGARDE QUE LE TABLEAU."), """
..w..
.www.
..r..
.www.
wwwww
wwwww
.www.
""", {"w": "#f4f0e8", "r": "#e02a2a"}),
    _e("cantine", "LA CANTINE", "quais", ("CANTINE", "CANTINE DU PARC", "CANTINE MOBILE"),
       ("DEUX STEAMÉS, UNE FRITE, UNE ENSEIGNE.", "LE RESTE DE LA COMMANDE, ON L’A PAYÉ."), """
y.y.y
yyyyy
yyyyy
rrrrr
.rrr.
.rwr.
..r..
""", {"y": "#ffd23a", "r": "#e8443a", "w": "#fff4e0"}),
    _e("taverne_port", "LA TAVERNE DU PORT", "quais", ("TAVERNE DU PORT",),
       ("LA DRAFT À TRENTE-CINQ CENNES.", "L’ENSEIGNE, GRATIS."), """
wwww.
yyyy.
yyyyg
yyyyg
yyyyg
yyyy.
gggg.
""", {"w": "#fff8e0", "y": "#f0a020", "g": "#b8d8e8"}),
    _e("souvenirs", "LES SOUVENIRS DE LA POINTE", "pointe", ("SOUVENIRS", "PHOTO SOUVENIR"),
       ("LE SEUL SOUVENIR DE LA POINTE", "QU’ON N’A PAS PAYÉ 4,99 $."), """
..y..
.rrr.
..w..
..r..
.www.
.rrr.
wwwww
""", {"y": "#ffe060", "r": "#e8443a", "w": "#f4f0e8"}),
    _e("mah_jong", "LE CLUB MAH-JONG", "canton", ("CLUB MAH-JONG",),
       ("LE CLUB A VOTÉ : LA POLICE NE SERA PAS APPELÉE.", "LE VOTE ÉTAIT SERRÉ."), """
wwwww
wgwgw
wwwww
wrwrw
wwwww
wgwgw
wwwww
""", {"w": "#f0ead8", "g": "#2a9a4a", "r": "#d02a2a"}),
    _e("dragon_or", "LE DRAGON D’OR", "canton", ("DRAGON D'OR",),
       ("IRÈNE L’A REMARQUÉ.", "IRÈNE REMARQUE TOUT."), """
.yyy.
yyyyy
yy.yy
yyyyy
.yyy.
..r..
.rrr.
""", {"y": "#ffc830", "r": "#e8302a"}),
    _e("ti_pout", "TI-POUT AUTOS", "friches", ("TI-POUT AUTOS",),
       ("GARANTIE TRENTE JOURS OU TRENTE PIEDS.", "L’ENSEIGNE N’A FAIT NI L’UN NI L’AUTRE."), """
.ddd.
ddddd
ddgdd
dgggd
ddgdd
ddddd
.ddd.
""", {"d": "#ff8a2a", "g": "#ffe0a0"}),
)

#: Ce que le navigateur suit. `portee_px` : à quelle distance du néon on se tient pour l'atteindre (debout sous
#: lui, sur le trottoir) ; `vis` : les vis à défaire ; `crans` : les quarts de tour d'une vis (un tour complet,
#: dans le sens contraire des aiguilles) ; `delit` : ce que la police en fait (`recherche.DELITS`) — une
#: effraction, une étoile, et il faut un témoin ; `prime` et `paliers` : comme les autres familles.
REGLE: dict = {
    "portee_px": 16,
    "vis": 4,
    "crans": 4,
    "delit": "effraction",
    "prime": 200,
    "paliers": {"6": 1000, "12": 3000},
}

# --- Le propriétaire qui sort (vague 6, 1er oct. 2026 — Martin : « le propriétaire qui sort de son commerce ») ---

#: ⚠️ QUI SORT, ET COMMENT, À L'EMPREINTE DU COMMERCE — jamais un dé : `crc32(SEL + ":" + slug)` décide s'il y a
#: quelqu'un en haut (`humeur`), s'il te court après (`court`) ou s'il rentre appeler la police (`appelle`), homme ou
#: femme, pyjama ou robe de chambre, ses couleurs, et à quelle vis il se réveille (`reveil` : la deuxième, la
#: troisième, ou seulement quand l'enseigne tombe). Le même commerce sort la même personne dans toutes les parties.
SEL_PROPRIO = "réveillé"

#: ⚠️ PERSONNE NE SORT de ces commerces-là, et l'empreinte n'y est pour rien : leur porte est déjà tenue. Chez Ti-Paul,
#: c'est Ti-Paul (un personnage, avec sa voix à lui) ; au Dragon d'or, le portier du casino, ouvert toute la nuit.
#: Et une devanture sans porte (les Souvenirs) n'a personne à faire sortir.
PORTE_TENUE: dict[str, str] = {
    "tipaul": "Ti-Paul tient son dépanneur : c'est un personnage, pas un passant en pyjama",
    "dragon_or": "le casino est ouvert toute la nuit, et son portier garde la porte",
}

#: Les habits de nuit. `pyjama` : la chemise rayée et le pantalon de la même couleur ; `robe` : la robe de chambre
#: par-dessus (le pyjama dépasse aux chevilles). Les pantoufles, toujours — même en janvier (c'est la blague).
HABITS_DE_NUIT: dict[str, tuple[str, ...]] = {
    "pyjama": ("#9ec5e8", "#f2b8c6", "#c9e4a8", "#e8dca8"),
    "robe": ("#a8323e", "#3a5aa8", "#7a4a8a", "#4a7a4a"),
}

#: Ce que le navigateur suit. `allure` : en pantoufles, il court moins vite que toi (le joueur court à 2,0, un passant
#: à 1,35 × son allure) ; `cri_images` : le temps de sa bulle, de son cri au tempérament ; `chasse_s` : au bout de ça,
#: il lâche et rentre ; `rattrape_px` : à cette distance, le tournevis tombe des mains (il arrive sur toi) ;
#: `appel_s` : rentré, le temps de trouver ses lunettes et de composer ; `attente_s` : au téléphone, il attend qu'elle
#: tombe — au-delà, la police ne vient pas pour une enseigne qui pend encore.
PROPRIO: dict = {
    "allure": 0.8,
    "cri_images": 110,
    "chasse_s": 12,
    "rattrape_px": 26,
    "appel_s": 5,
    "attente_s": 60,
}

#: CE QU'IL CRIE (le ton de docs/ecrire-drole.md : il est en pantoufles, à trois heures du matin — on rit de la
#: situation, jamais de lui). Une voix de passant par genre (`audio.VOIX_PAR_GENRE`), le slug `proprio-<h|f>-<cle>`.
#: `sort` : en sortant ; `court` / `appelle` : son tempérament ; `lache` : il abandonne la poursuite. ⚠️ Une réplique
#: neuve s'ajoute AU BOUT : les mp3 payés portent le slug.
REPLIQUES_PROPRIO: tuple[dict, ...] = (
    {"qui": "h", "cle": "sort", "texte": "Heille! Ça fait trente ans qu'a pend là, mon enseigne!",
     "jeu": "[shouting] [angry] Heille! Ça fait trente ans qu'a pend là, mon enseigne!"},
    {"qui": "h", "cle": "court", "texte": "Attends que j'te pogne! J'cours vite, en pantoufles!",
     "jeu": "[angry] Attends que j'te pogne! J'cours vite, en pantoufles!"},
    {"qui": "h", "cle": "appelle", "texte": "Bouge pas! J'appelle la police… dès que j'trouve mes lunettes!",
     "jeu": "[nervously] Bouge pas! J'appelle la police… dès que j'trouve mes lunettes!"},
    {"qui": "h", "cle": "lache", "texte": "Pfff… Reviens demain, j'vas être habillé!",
     "jeu": "[sighs] [annoyed] Pfff… Reviens demain, j'vas être habillé!"},
    {"qui": "f", "cle": "sort", "texte": "Heille! J'ai payé quatre cents piastres pour c't'enseigne-là!",
     "jeu": "[shouting] [angry] Heille! J'ai payé quatre cents piastres pour c't'enseigne-là!"},
    {"qui": "f", "cle": "court", "texte": "Reviens icitte! J'ai des bigoudis, pas des béquilles!",
     "jeu": "[angry] Reviens icitte! J'ai des bigoudis, pas des béquilles!"},
    {"qui": "f", "cle": "appelle", "texte": "J'appelle la police! Pis ma belle-sœur, a va le savoir avant eux!",
     "jeu": "[firmly] J'appelle la police! Pis ma belle-sœur, a va le savoir avant eux!"},
    {"qui": "f", "cle": "lache", "texte": "Reviens aux heures d'ouverture, comme tout le monde!",
     "jeu": "[annoyed] Reviens aux heures d'ouverture, comme tout le monde!"},
)

#: Les deux voix : celles des passants (`audio.VOIX_PAR_GENRE`), la même pour chaque proprio de son genre.
GENRES_PROPRIO = {"h": "homme", "f": "femme"}


def repliques_du_proprio() -> list[dict]:
    """Ses répliques, comme `audio` les lit : une banque (`mission: "proprio"`), une série par genre."""
    return [{"slug": f"proprio-{r['qui']}-{r['cle']}", "qui": f"proprio_{r['qui']}", "genre": GENRES_PROPRIO[r["qui"]],
             "texte": r["texte"], "mission": "proprio", "partie": "proprio", "telephone": False}
            for r in REPLIQUES_PROPRIO]


def _porte(ville: dict, d: dict) -> list[int] | None:
    """La porte de la devanture : la vraie (`D`) d'abord, sinon la condamnée (`d`) — il habite en haut, il sort par où
    il peut. Aucune : personne ne sort. ⚠️ Une ville sans `sol` (un juge synthétique) n'en a pas."""
    sol = ville.get("sol")
    if not sol or not (0 <= d["y"] < len(sol)):
        return None
    rang = sol[d["y"]]
    for lettre in ("D", "d"):
        for x in range(d["x"], d["x"] + d["l"]):
            if 0 <= x < len(rang) and rang[x] == lettre:
                return [x, d["y"]]
    return None


def proprio(slug: str, porte: list[int] | None) -> dict | None:
    """Qui sort de ce commerce, à l'empreinte de son slug — ou None : la porte est tenue, il n'y en a pas, ou personne
    n'est en haut (une sur trois). Rend `{porte, humeur, genre, reveil, tenue}` ; la tenue est un descripteur (l'habit,
    sa couleur, la peau, les cheveux, la coiffure, le corps) que `devisser.js` enfile."""
    if porte is None or slug in PORTE_TENUE:
        return None
    h = zlib.crc32(f"{SEL_PROPRIO}:{slug}".encode())
    humeur = (None, "court", "appelle")[h % 3]
    if humeur is None:
        return None
    genre = "hf"[(h >> 8) & 1]
    habit = ("pyjama", "robe")[(h >> 10) & 1]
    couleurs = HABITS_DE_NUIT[habit]
    corps = ("vieux", "costaud", "homme") if genre == "h" else ("femme",)
    coiffures = ("degarnie", "chauve", "courte") if genre == "h" else ("bouclee", "chignon")
    cheveux = garderobe.GRIS + garderobe.CHEVEUX[:4]
    tenue = {"habit": habit, "couleur": couleurs[(h >> 16) % len(couleurs)],
             "peau": garderobe.PEAUX[(h >> 4) % len(garderobe.PEAUX)], "cheveux": cheveux[(h >> 20) % len(cheveux)],
             "coiffure": coiffures[(h >> 24) % len(coiffures)], "squelette": corps[(h >> 27) % len(corps)]}
    return {"porte": list(porte), "humeur": humeur, "genre": genre, "reveil": 2 + (h >> 13) % 3, "tenue": tenue}


def _district(ville: dict, x: int, y: int) -> str | None:
    for z in ville.get("zones") or []:
        if z.get("gang"):
            continue
        if z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]:
            return z["slug"]
    return None


def poser(ville: dict) -> list[dict]:
    """Les places des enseignes, sur la ville FINIE. ⚠️ Aucun dé, rien de posé : la règle lit les devantures.

    Pour chaque enseigne : la devanture qui porte un de ses noms ET une pancarte (le néon pend là où pendait la
    pancarte), dans son district d'abord, le premier nom de sa liste d'abord, puis la première en ordre de lecture.
    Une devanture ne porte qu'une enseigne. Rend `[{slug, x, y, l, pancarte, district, porte}]` — la devanture, en
    tuiles, et sa porte (`[x, y]`, ou None : d'où le propriétaire sort, vague 6)."""
    devantures = ville.get("devantures") or []
    prises: set[tuple[int, int]] = set()
    out: list[dict] = []
    for e in ENSEIGNES:
        candidates = []
        for d in devantures:
            if d.get("texte") not in e["textes"] or not d.get("pancarte") or (d["x"], d["y"]) in prises:
                continue
            ici = _district(ville, d["x"], d["y"])
            candidates.append((ici != e["district"], e["textes"].index(d["texte"]), d["y"], d["x"], d, ici))
        if not candidates:
            continue
        *_, d, ici = min(candidates, key=lambda c: c[:4])
        prises.add((d["x"], d["y"]))
        out.append({"slug": e["slug"], "x": d["x"], "y": d["y"], "l": d["l"], "pancarte": d["pancarte"],
                    "district": ici or e["district"], "porte": _porte(ville, d)})
    return out


def exporter(places: list[dict] | None) -> dict:
    """Ce que `/api/collections` sert : le catalogue (dans l'ordre du mur), la règle, et la place de celles que la
    ville porte. Une enseigne sans place reste au catalogue, sans place (le carnet la montre quand même). Et le
    propriétaire (vague 6) : qui sort de chacune (`proprio`, absent si personne), ce qu'il crie et ses voix."""
    ou = {p["slug"]: p for p in places or []}
    liste = []
    for e in ENSEIGNES:
        fiche = {k: e[k] for k in ("slug", "nom", "district", "grille", "palette")}
        fiche["lignes"] = list(e["lignes"])
        if e["slug"] in ou:
            fiche.update({k: v for k, v in ou[e["slug"]].items() if k not in ("slug", "porte")})
            qui = proprio(e["slug"], ou[e["slug"]].get("porte"))
            if qui:
                fiche["proprio"] = qui
        liste.append(fiche)
    from . import audio
    dits: dict[str, dict[str, str]] = {}
    for r in REPLIQUES_PROPRIO:
        dits.setdefault(r["qui"], {})[r["cle"]] = r["texte"]
    voix = audio.voix_proprio()
    return {"titre": "ENSEIGNES", "liste": liste, "regle": {**REGLE, "paliers": dict(REGLE["paliers"])},
            "proprio": {**PROPRIO, "repliques": dits,
                        "voix": [audio.serie_de_voix(f"proprio-{g}-", [v for v in voix if v["qui"] == f"proprio_{g}"])
                                 for g in GENRES_PROPRIO]}}
