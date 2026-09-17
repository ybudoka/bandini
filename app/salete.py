"""La saleté se déplace, elle ne s'ajoute pas.

Demande de Martin (16 sept. 2026) : « je veux des cartiers plus reconnaissable,
plus riche et propre avec des commerce plus riche, des cartiers plus pauvre et
sale ».

⚠️ **Le total ne monte pas d'un objet.** Martin a renvoyé « trop de saleté
partout » le jour même (303 objets → 166) : ce qu'il demande, c'est que la
saleté se LISE, pas qu'il y en ait plus. Ce module prend la ville déjà semée,
enlève la saleté des quartiers qui en ont les moyens et la repose chez ceux qui
ne les ont pas — au plus autant qu'il en a enlevé.

Trois saletés, les trois que la ville sème déjà : les **déchets** d'un terrain
vague (`carte.DECHETS`, et seulement ceux-là — une caisse de quai est de la
cargaison), les **tags** et les **nids-de-poule**. Et une quatrième chose qui
n'en ajoute pas : en pauvre, la **poubelle déborde**.

⚠️ **Son propre dé, après les lignes d'autobus et avant le mobilier** : ce qu'il
enlève et ce qu'il pose ne déplace ni un abribus, ni un chantier, ni un paquet.
Et **qui part** ne se tire pas au dé : il se lit à la position (`_reste`), pour
qu'un bloc qu'on change de standing ne rebatte pas la saleté du reste de la ville.
"""

from __future__ import annotations

#: La part de la saleté d'aujourd'hui qui RESTE où elle est ; le reste part
#: chez les pauvres. ⚠️ **Une sur deux en ordinaire, pas toute.** Le plan
#: proposait « la densité d'aujourd'hui en ordinaire, tout le reste en pauvre » ;
#: mesuré sur la ville (16 sept. 2026) : 30 saletés en cossu, 40 en ordinaire,
#: 159 en pauvre, et vider le cossu seul laisse le pauvre à **4,1 fois**
#: l'ordinaire par tuile. Il faut cinq fois pour qu'on le voie en changeant de
#: rue ; une sur deux en donne onze et demi (16 en ordinaire, 213 en pauvre).
GARDE: dict[str, float] = {"cossu": 0.0, "ordinaire": 0.5, "pauvre": 1.0}

#: Ce qui traîne au pied des immeubles d'un quartier pauvre. ⚠️ Pas la liste du
#: terrain vague : sur un trottoir, on ne jette ni baril ni caisse, on sort ses
#: sacs, et un matelas le jour du déménagement.
AU_PIED_DES_MURS = ("ordures", "ordures", "ordures", "debris", "debris", "pneu", "matelas", "caddie")

#: L'écart, en tuiles, entre deux déchets qu'on repose — et entre deux tags.
#: Sinon le dé les empile dans la même ruelle, et la saleté se lit comme un
#: dépôt au lieu d'un quartier.
ECART_DECHET = 5
ECART_TAG = 4


def _reste(x: int, y: int, standing: str | None) -> bool:
    """Cette saleté reste-t-elle ? Sur l'eau et en pauvre, toujours."""
    garde = 1.0 if standing is None else GARDE[standing]
    if garde >= 1.0:
        return True
    # Le `hash2` de base.js, en 32 bits : un XOR de deux produits laissait
    # six déchets sur sept dans les lots ordinaires.
    h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 0x100000000 < garde


def _evitees(chantier, ville: dict) -> set[tuple[int, int]]:
    """Ce qui reste nu : les coins de croisement, le parvis du terminus, les
    chantiers, les plages, la foire et le rond des amuseurs."""
    from . import autobus, mobilier

    evitees = set(autobus.parvis(ville))
    for inter in chantier.intersections:
        for y in range(inter["y"] - mobilier.COIN - 1, inter["y"] + inter["h"] + mobilier.COIN + 1):
            for x in range(inter["x"] - mobilier.COIN - 1, inter["x"] + inter["l"] + mobilier.COIN + 1):
                evitees.add((x, y))
    rectangles = list(ville.get("chantiers") or []) + list(ville.get("plages") or [])
    if ville.get("foire"):
        rectangles.append(ville["foire"])
    marge = chantier.SCENE_DEGAGEMENT
    rectangles += [{"x": s["x"] - marge, "y": s["y"] - marge, "l": 2 * marge + 1, "h": 2 * marge + 1}
                   for s in ville.get("scenes") or []]
    for r in rectangles:
        for y in range(r["y"] - 1, r["y"] + r["h"] + 1):
            for x in range(r["x"] - 1, r["x"] + r["l"] + 1):
                evitees.add((x, y))
    return evitees


def _contre_un_mur(chantier, x: int, y: int) -> bool:
    """Au pied d'un bâtiment : un mur, une vitrine ou un toit touche la tuile.
    ⚠️ Pas une porte : on ne sort pas ses sacs devant l'entrée."""
    from . import carte

    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        glyphe = chantier.sol[y + dy][x + dx]
        fiche = carte.LEGENDE[glyphe]
        if fiche.get("solide") == 1 and not fiche.get("porte") and not fiche.get("garage"):
            return True
    return False


def _deplacer_les_dechets(chantier, ville: dict, des) -> tuple[int, int]:
    from . import carte, mobilier

    partent = sorted((d["x"], d["y"]) for d in chantier.decor
                     if (d["x"], d["y"]) in chantier.dechets_semes and d["type"] in carte.DECHETS
                     and not _reste(d["x"], d["y"], chantier.standing_en(d["x"], d["y"])))
    for x, y in partent:
        chantier.retirer_decor(x, y)
        chantier.dechets_semes.discard((x, y))
    if not partent:
        return 0, 0
    evitees = _evitees(chantier, ville)
    candidats = [(x, y) for y in range(1, chantier.hauteur - 1) for x in range(1, chantier.largeur - 1)
                 if chantier.sol[y][x] == "_" and (x, y) not in evitees
                 and chantier.standing_en(x, y) == "pauvre" and _contre_un_mur(chantier, x, y)]
    solides = {(d["x"], d["y"]) for d in chantier.decor if d["type"] in carte.DECOR_SOLIDE}
    poses: list[tuple[int, int]] = []
    for _essai in range(60 * len(partent)):
        if len(poses) >= len(partent) or not candidats:
            break
        # ⚠️ La sorte ET la place à chaque essai, refusé ou non : un refus ne
        # décale pas le tirage des suivants selon ce qu'il a rencontré.
        quoi = AU_PIED_DES_MURS[des.suivant() % len(AU_PIED_DES_MURS)]
        x, y = candidats[des.suivant() % len(candidats)]
        if any(abs(px - x) + abs(py - y) < ECART_DECHET for px, py in poses):
            continue
        # ⚠️ La règle des arbres de rue, telle quelle : ni devant une porte ni
        # juste à côté, collé à rien, et la tuile prise ne coupe aucun passage.
        if not mobilier._place_libre(chantier, x, y, solides) or not chantier.poser_decor(quoi, x, y):
            continue
        if quoi in carte.DECOR_SOLIDE:
            solides.add((x, y))
        chantier.dechets_semes.add((x, y))
        poses.append((x, y))
    return len(partent), len(poses)


def _deplacer_les_tags(chantier, des) -> tuple[int, int]:
    from . import devantures as devantures_mod

    partent = [g for g in chantier.graffitis
               if not _reste(g["x"], g["y"], chantier.standing_en(g["x"], g["y"]))]
    for g in partent:
        chantier.graffitis.remove(g)
        chantier.murs_tagges.discard((g["x"], g["y"]))
    if not partent:
        return 0, 0
    murs = [(x, y) for y in range(chantier.hauteur - 1) for x in range(chantier.largeur)
            if chantier.standing_en(x, y) == "pauvre" and chantier.mur_taggable(x, y)]
    poses: list[tuple[int, int]] = [(g["x"], g["y"]) for g in chantier.graffitis]
    # ⚠️ Le gang signe PRÈS DE SA COUR, pas dans tout son district : c'est la
    # règle de `graffitis_sur_les_murs`, et le tag dit le territoire.
    cours = [(z["x"], z["y"], z["l"], z["h"], z["gang"]) for z in chantier.zones() if z.get("gang")]
    ajoutes = 0
    for _essai in range(60 * len(partent)):
        if ajoutes >= len(partent) or not murs:
            break
        x, y = murs[des.suivant() % len(murs)]
        # Au pied d'une cour, son gang signe une fois sur deux.
        gang = next((g for zx, zy, zl, zh, g in cours
                     if zx - 6 <= x < zx + zl + 6 and zy - 6 <= y < zy + zh + 6), None)
        signe = des.chance(0.5)
        if not chantier.mur_taggable(x, y) or any(abs(px - x) + abs(py - y) < ECART_TAG for px, py in poses):
            continue
        mots = devantures_mod.TAGS_GANG.get(gang, devantures_mod.TAGS_LIBRES) if gang and signe \
            else devantures_mod.TAGS_LIBRES
        if chantier.taguer(x, y, mots, des):
            poses.append((x, y))
            ajoutes += 1
    return len(partent), ajoutes


def _deplacer_les_nids(chantier, ville: dict, des) -> tuple[int, int]:
    from . import carte

    nids = ville["nids_de_poule"]
    restent = [(n["x"], n["y"]) for n in nids if _reste(n["x"], n["y"], chantier.standing_en(n["x"], n["y"]))]
    partis = len(nids) - len(restent)
    if not partis:
        return 0, 0
    candidats = [t for t in chantier.chaussee_a_nids() if chantier.standing_en(*t) == "pauvre"]
    poses = list(restent)
    for _essai in range(60 * partis):
        if len(poses) - len(restent) >= partis or not candidats:
            break
        x, y = candidats[des.suivant() % len(candidats)]
        if any(abs(px - x) + abs(py - y) < carte.NIDS_DE_POULE["ecart"] for px, py in poses):
            continue
        poses.append((x, y))
    nids[:] = [{"x": x, "y": y} for x, y in sorted(poses)]
    return partis, len(poses) - len(restent)


def deplacer(chantier, ville: dict, graine: int) -> dict[str, tuple[int, int]]:
    """Déplace la saleté vers les quartiers pauvres. Rend, par sorte, combien
    sont partis et combien ont été reposés (jamais plus)."""
    from . import carte

    des = carte.Des(graine ^ 0x5A1E7E)
    comptes = {
        "dechets": _deplacer_les_dechets(chantier, ville, des),
        "tags": _deplacer_les_tags(chantier, des),
        "nids": _deplacer_les_nids(chantier, ville, des),
    }
    # ⚠️ La poubelle ne s'ajoute pas non plus : c'est la MÊME, qui déborde.
    for d in chantier.decor:
        if d["type"] == "poubelle" and chantier.standing_en(d["x"], d["y"]) == "pauvre":
            d["type"] = "poubelle_pleine"
    return comptes
