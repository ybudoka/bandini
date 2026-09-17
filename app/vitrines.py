"""Les commerces montent et descendent — des quartiers qu'on reconnaît, 3e vague.

Demande de Martin (16 sept. 2026) : « des cartiers plus riche et propre avec des
commerce plus riche, des cartiers plus pauvre et sale ».

Dans un bloc cossu, la rue vend des bijoux et du vin ; dans un bloc pauvre, on
prête sur gages et une vitrine sur trois est placardée. Ce module le fait sur la
ville FINIE, après le métro :

- il **renomme** les enseignes (`devantures.COMMERCES_COSSUS`, `COMMERCES_PAUVRES`)
  — un nom de la MÊME famille, pour que la pièce derrière la porte reste la bonne,
  et qui tient dans le MÊME bandeau, pour que le mur ne bouge pas ;
- il **placarde** une vitrine sur trois en pauvre (le motif `B`), jamais au-dessus
  d'un guichet ou d'une machine, et toutes celles d'un local À LOUER ;
- il **marque** le standing des façades (`standing` : `+` ou `-`), que le peintre lit.

⚠️ **Pourquoi après coup, et pas en choisissant l'enseigne.** Tiré pendant la
construction, un nom plus long élargissait le bandeau, déplaçait la porte peinte,
décalait le dé des devantures et changeait qui ouvre sa porte : rampes perdues,
barrière du cargo déplacée, et dix juges tombés sans qu'un seul parle d'enseigne.
Ici, rien ne tire un dé et rien ne touche une tuile : ce qui change se lit à la
position (`carte.empreinte_de_tuile`).
"""

from __future__ import annotations

#: La part des commerces FERMÉS d'une rue pauvre qui sont des locaux vides.
#: ⚠️ Offert à la seule famille « commerce », À LOUER ne tombait jamais (deux
#: commerces fermés de cette famille dans toute la ville) ; offert à tous, il
#: remplaçait chaque criée qui n'avait pas de nom pauvre (huit locaux vides).
PART_A_LOUER = 0.2


def _loin(places: dict[str, list[tuple[int, int]]], texte: str, x: int, y: int) -> bool:
    """Aucune enseigne de ce nom à moins de `DISTANCE_DOUBLON` tuiles."""
    from . import devantures

    return all(max(abs(px - x), abs(py - y)) >= devantures.DISTANCE_DOUBLON
               for px, py in places.get(texte, ()))


def _renommer(chantier, d: dict, nouveau: str, places: dict) -> None:
    ancien = d["texte"]
    places[ancien].remove((d["x"], d["y"]))
    places.setdefault(nouveau, []).append((d["x"], d["y"]))
    d["texte"] = nouveau
    # ⚠️ La porte qui s'ouvre porte le nom de SON enseigne : on entre dans la pièce
    # sous le bandeau qu'on vient de lire (`Monde.entrer`).
    for porte in chantier.portes:
        if porte["y"] == d["y"] and d["x"] <= porte["x"] < d["x"] + d["l"] and porte.get("nom") == ancien:
            porte["nom"] = nouveau


def monter_et_descendre(chantier, ville: dict) -> dict[str, int]:
    """Renomme, placarde et marque. Rend les comptes."""
    from . import carte, devantures, magasins

    speciaux = {texte for texte, _ in devantures.ENSEIGNES.values()}
    cossus = {nom for nom, _ in devantures.COMMERCES_COSSUS}
    pauvres = {nom for nom, _ in devantures.COMMERCES_PAUVRES}
    machines = {"guichet"} | {fiche["decor"] for fiche in magasins.DISTRIBUTRICES.values()}
    sous_une_machine = {(d["x"], d["y"] - 1) for d in chantier.decor if d["type"] in machines}
    places: dict[str, list[tuple[int, int]]] = {}
    for d in chantier.devantures:
        places.setdefault(d["texte"], []).append((d["x"], d["y"]))
    comptes = {"renommees": 0, "placardees": 0, "a_louer": 0}

    for d in chantier.devantures:
        standing = chantier.standing_en(d["x"], d["y"])
        if standing not in carte.STANDING_LETTRE or (d["texte"] in speciaux and d.get("porte")):
            continue
        d["standing"] = carte.STANDING_LETTRE[standing]
        famille = devantures.GENRES[d["genre"]]["slug"]
        visitable = "D" in d["motifs"]
        liste = devantures.COMMERCES_COSSUS if standing == "cossu" else devantures.COMMERCES_PAUVRES
        interdits = pauvres if standing == "cossu" else cossus

        def convient(nom: str) -> bool:
            return (devantures.tient_en(nom, d["l"], carte.TUILE_PX) and nom not in interdits
                    and _loin(places, nom, d["x"], d["y"]))

        # ⚠️ À LOUER n'est offert qu'à un commerce qui ne s'ouvre PAS : une enseigne
        # « à louer » derrière laquelle on trouve un magasin meublé ment deux fois.
        # Et seulement à sa famille : offert à toutes, il remplaçait chaque criée et
        # chaque atelier qui n'avait pas de nom pauvre — le port perdait sa poissonnerie.
        voulus = [nom for nom, f in liste if f == famille and convient(nom)
                  and not (nom == devantures.A_LOUER and visitable)]
        # ... sauf un commerce fermé sur cinq, de toute famille : le local vide.
        a_louer_ici = (standing == "pauvre" and not visitable and convient(devantures.A_LOUER)
                       and carte.empreinte_de_tuile(d["x"] + 1, d["y"]) < PART_A_LOUER)
        if not voulus and d["texte"] in interdits:
            # Un nom du district qui n'a rien à faire ici (la BIJOUTERIE tombée en
            # pauvre) : n'importe quel nom ordinaire de sa famille qui tient.
            voulus = [nom for nom, f in devantures.commerces_du_district(chantier.district_en(d["x"], d["y"]))
                      if f == famille and convient(nom) and nom not in cossus | pauvres]
        deja = cossus if standing == "cossu" else pauvres
        if a_louer_ici:
            _renommer(chantier, d, devantures.A_LOUER, places)
            comptes["renommees"] += 1
        elif voulus and d["texte"] not in deja:
            nouveau = voulus[int(carte.empreinte_de_tuile(d["x"], d["y"]) * len(voulus))]
            _renommer(chantier, d, nouveau, places)
            comptes["renommees"] += 1
        if standing != "pauvre":
            continue
        a_louer = d["texte"] == devantures.A_LOUER
        motifs = []
        for i, m in enumerate(d["motifs"]):
            tuile = (d["x"] + i, d["y"])
            if m == "W" and tuile not in sous_une_machine and (
                    a_louer or carte.empreinte_de_tuile(*tuile) < devantures.PART_PLACARDEE):
                motifs.append("B")
                comptes["placardees"] += 1
            else:
                motifs.append(m)
        d["motifs"] = "".join(motifs)
        if a_louer:
            comptes["a_louer"] += 1
            # Sa vitrine ne s'allume pas : il n'y a personne.
            lampe = next((lampe for lampe in chantier.lampes if lampe.get("c") == "vitrine"
                          and (lampe["x"], lampe["y"]) == (d["x"] + d["l"] // 2, d["y"] + 1)), None)
            if lampe is not None:
                chantier.lampes.remove(lampe)

    for r in chantier.residences:
        standing = chantier.standing_en(r["x"], r["y"])
        if standing in carte.STANDING_LETTRE:
            r["standing"] = carte.STANDING_LETTRE[standing]
    return comptes
