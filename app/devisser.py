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
    Une devanture ne porte qu'une enseigne. Rend `[{slug, x, y, l, pancarte, district}]` — la devanture, en tuiles."""
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
                    "district": ici or e["district"]})
    return out


def exporter(places: list[dict] | None) -> dict:
    """Ce que `/api/collections` sert : le catalogue (dans l'ordre du mur), la règle, et la place de celles que la
    ville porte. Une enseigne sans place reste au catalogue, sans place (le carnet la montre quand même)."""
    ou = {p["slug"]: p for p in places or []}
    liste = []
    for e in ENSEIGNES:
        fiche = {k: e[k] for k in ("slug", "nom", "district", "grille", "palette")}
        fiche["lignes"] = list(e["lignes"])
        if e["slug"] in ou:
            fiche.update({k: v for k, v in ou[e["slug"]].items() if k != "slug"})
        liste.append(fiche)
    return {"titre": "ENSEIGNES", "liste": liste, "regle": {**REGLE, "paliers": dict(REGLE["paliers"])}}
