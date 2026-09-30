"""Le marché aux puces du dimanche (P4, docs/jalons/le-marche-aux-puces-du-dimanche.md).

Le dimanche, de l'aube à midi, deux étals se montent sur le terrain vague le plus proche de la planque : **Ti-Rhéal**
vend les cartes de hockey de la Ligue (quatre numéros par semaine, plus cher que ce qu'une carte paie par terre) et
**Gisèle** les meubles qui portent `ou: puces` (moins cher qu'au catalogue Beausoleil, livrés le lendemain). On y
marchande : offrir moins, et le marchand accepte ou refuse selon son humeur — calculée, comme le reste.

⚠️ **RIEN AU DÉ, RIEN DANS LA VILLE** : le terrain se choisit par une règle sur la ville finie (après les cartes, les
bebelles et les sauts), les étals se PEIGNENT (aucune entité, aucun passant de plus : rien ne s'empile), et ce qui se
vend cette semaine-là est une fonction de la semaine (`Puces.stock`, dans le navigateur) — le même dimanche, le même
étal pour tout le monde. Tout voyage sur `/api/collections`.

⚠️ **UN DIMANCHE** : le jour de partie divisible par sept (le jour 7, le 14…) ; « la semaine » est `(jour - 1) // 7`.
"""

from __future__ import annotations

from . import frenesies

#: Les étals, de gauche à droite. `marchand` : qui tient l'étal (son nom, ses couleurs ; `qui`, le slug de ses voix —
#: `REPLIQUES`). `vend` : `cartes` ou `meubles`. Ce qu'il dit en ouvrant, c'est sa réplique `accueil-<n>` de la semaine
#: (le ton de docs/ecrire-drole.md : le marchand se vante, et c'est lui qui a tort).
ETALS: tuple[dict, ...] = (
    {"slug": "cartes", "nom": "LES CARTES DE TI-RHÉAL", "vend": "cartes", "nappe": "#2a4a9a",
     "marchand": {"nom": "TI-RHÉAL", "qui": "ti_rheal", "chandail": "#b02a22", "peau": "#e0b08a", "cheveux": "#d8d8d8"}},
    {"slug": "meubles", "nom": "LES MEUBLES DE GISÈLE", "vend": "meubles", "nappe": "#7a4a2a",
     "marchand": {"nom": "GISÈLE", "qui": "gisele", "chandail": "#5e8a3a", "peau": "#f0c8a0", "cheveux": "#8a4a2a"}},
)

#: LES VOIX DES MARCHANDS (la deuxième vague, 30 sept. 2026) : une voix ElevenLabs par marchand, québécoise, choisie
#: à l'audition contre deux autres (docs/personnages/ti-rheal.md, gisele.md). Elles ne sont qu'au marché : personne
#: d'autre ne parle avec elles.
VOIX: dict[str, dict] = {
    "ti_rheal": {"voix": "Christian Page - Narrative and Deep", "genre": "homme"},
    "gisele": {"voix": "Kasandra - Natural Quebecer UGC ad", "genre": "femme"},
}

#: CE QUE LES MARCHANDS DISENT, à voix haute (Martin, 30 sept. 2026 : « des voix aux marchands »). Le slug de la voix :
#: `<qui>-puces-<cle>` ; le texte, en casse naturelle (le menu l'écrit en capitales) ; `jeu`, collé à la réplique
#: (docs/jeu-d-acteur.md) — ⚠️ il ne part jamais au navigateur. ⚠️ Chacun se nomme UNE fois, dans `salut`, la première
#: fois qu'on s'arrête à son étal (« Qui parle se nomme », § 3.11) ; ensuite, son `accueil-<n>` de la semaine.
#: ⚠️ Une réplique neuve s'ajoute AU BOUT de sa clé (`accueil-4`) : les mp3 payés portent le slug.
#: ⚠️ Le bandeau du HUD ne tient qu'une quarantaine de lettres : il ne montre que la PREMIÈRE phrase d'un refus ou d'un
#: au revoir (« T'es drôle, toi. ») — la réplique entière s'entend, et s'écrit au pied du menu.
REPLIQUES: tuple[dict, ...] = (
    # Ti-Rhéal Bergeron : trente ans sur la surfaceuse de l'aréna, il a tout vu et presque rien compris.
    {"qui": "ti_rheal", "cle": "salut",
     "texte": "Ti-Rhéal Bergeron, trente ans sur la zamboni de l'aréna. Des cartes de hockey, j'en ai vu passer.",
     "jeu": "[smugly] Ti-Rhéal Bergeron, trente ans sur la zamboni de l'aréna. Des cartes de hockey, j'en ai vu passer."},
    {"qui": "ti_rheal", "cle": "accueil-1", "texte": "J'ai toute la Ligue. Presque. Des fois.",
     "jeu": "[confident] J'ai toute la Ligue. Presque… des fois."},
    {"qui": "ti_rheal", "cle": "accueil-2", "texte": "La Toque, je l'ai connu. Il m'a pas connu.",
     "jeu": "[knowingly] La Toque, je l'ai connu. [sighs] Il m'a pas connu."},
    {"qui": "ti_rheal", "cle": "accueil-3", "texte": "C'est pas cher, c'est de la nostalgie.",
     "jeu": "[warmly] C'est pas cher, c'est de la nostalgie."},
    {"qui": "ti_rheal", "cle": "vente", "texte": "Vendue! Mets-la dans une pochette, pis touche pas aux coins.",
     "jeu": "[cheerful] Vendue! Mets-la dans une pochette, pis touche pas aux coins."},
    {"qui": "ti_rheal", "cle": "accepte", "texte": "Correct, correct. C'est parce que t'as une face honnête.",
     "jeu": "[amused] Correct, correct… C'est parce que t'as une face honnête."},
    {"qui": "ti_rheal", "cle": "refuse", "texte": "T'es drôle, toi. Une recrue de même, ça se marchande pas.",
     "jeu": "[sarcastic] T'es drôle, toi. Une recrue de même, ça se marchande pas."},
    {"qui": "ti_rheal", "cle": "rien", "texte": "Tu les as toutes, mes cartes de la semaine. Reviens dimanche, j'en remonte de la cave.",
     "jeu": "[impressed] Tu les as toutes, mes cartes de la semaine. Reviens dimanche, j'en remonte de la cave."},
    {"qui": "ti_rheal", "cle": "aurevoir", "texte": "Bon dimanche, là! Garde tes cartes au sec.",
     "jeu": "[warmly] Bon dimanche, là! Garde tes cartes au sec."},
    # Gisèle Lachapelle : brocanteuse, trente ans de ventes de garage, le beau-frère et son pick-up.
    {"qui": "gisele", "cle": "salut", "texte": "Gisèle Lachapelle, brocanteuse. Regarde avec tes yeux, pis touche avec ton argent.",
     "jeu": "[confident] Gisèle Lachapelle, brocanteuse. Regarde avec tes yeux, pis touche avec ton argent."},
    {"qui": "gisele", "cle": "accueil-1", "texte": "Tout a appartenu à un curé. Tout.",
     "jeu": "[matter-of-fact] Tout a appartenu à un curé. Tout."},
    {"qui": "gisele", "cle": "accueil-2", "texte": "Le sofa a une tache. Elle est à carreaux.",
     "jeu": "[deadpan] Le sofa a une tache. Elle est à carreaux."},
    {"qui": "gisele", "cle": "accueil-3", "texte": "Je livre demain. Le beau-frère a un pick-up.",
     "jeu": "[casually] Je livre demain. Le beau-frère a un pick-up."},
    {"qui": "gisele", "cle": "vente", "texte": "Vendu! Le beau-frère te livre ça demain, s'il se lève.",
     "jeu": "[cheerful] Vendu! Le beau-frère te livre ça demain… s'il se lève."},
    {"qui": "gisele", "cle": "accepte", "texte": "Tu me voles, mais t'as de beaux yeux. Marché conclu.",
     "jeu": "[playfully] Tu me voles, mais t'as de beaux yeux. Marché conclu."},
    {"qui": "gisele", "cle": "refuse", "texte": "Voyons donc! À ce prix-là, je le garde pour moi.",
     "jeu": "[firmly] Voyons donc! À ce prix-là, je le garde pour moi."},
    {"qui": "gisele", "cle": "rien", "texte": "T'as déjà toute ma table chez vous. Viens me vendre quelque chose, d'abord!",
     "jeu": "[amused] T'as déjà toute ma table chez vous. Viens me vendre quelque chose, d'abord!"},
    {"qui": "gisele", "cle": "aurevoir", "texte": "Bonne semaine! Pis dis pas au curé où t'as eu ça.",
     "jeu": "[teasing] Bonne semaine! Pis dis pas au curé où t'as eu ça."},
    # La vente à Gisèle (on lui vend un meuble de la planque) : elle rachète, et on peut lui demander plus.
    {"qui": "gisele", "cle": "rachat", "texte": "Un meuble à vendre? Je paie comptant, mais je paie pas cher.",
     "jeu": "[curious] Un meuble à vendre? Je paie comptant, mais je paie pas cher."},
    {"qui": "gisele", "cle": "rachat-conclu", "texte": "Marché conclu. Le beau-frère passe le chercher avant le souper.",
     "jeu": "[satisfied] Marché conclu. Le beau-frère passe le chercher avant le souper."},
    {"qui": "gisele", "cle": "plus-accepte", "texte": "T'es dur en affaires, toi. Correct, je monte.",
     "jeu": "[impressed] T'es dur en affaires, toi. Correct, je monte."},
    {"qui": "gisele", "cle": "plus-refuse", "texte": "Plus cher? Je suis brocanteuse, pas la Caisse populaire.",
     "jeu": "[wryly] Plus cher? Je suis brocanteuse, pas la Caisse populaire."},
)

#: Ce qui se vend, et comment. `ouvre_h`/`ferme_h` : l'aube à midi. `cartes_par_semaine` : combien de numéros au
#: stand de Ti-Rhéal. `prix_carte` : ⚠️ plus cher que la prime d'une carte trouvée par terre (25 $) — l'acheter,
#: c'est payer pour ne pas chercher. `rabais_meubles` : la part du prix du catalogue qu'on paie aux puces.
#: `offre` : la part du prix qu'on offre en marchandant ; `humeur` : sous tant (sur cent), le marchand accepte.
#:
#: LA VENTE À GISÈLE (la deuxième vague) : `rachat`, la part du prix du catalogue qu'elle paie un meuble de la planque ;
#: `demande`, ce qu'on lui demande de plus en marchandant à l'envers (× son prix), accepté sous `humeur_rachat`.
#: ⚠️ **UN CHOIX, PAS UNE POMPE À ARGENT** : le plus qu'on puisse en tirer (`rachat` × `demande`, 32,5 %) reste sous le
#: moins qu'un meuble coûte (`rabais_meubles` × `offre`, 42 %) — acheter pour revendre perd toujours (jugé).
REGLE: dict = {"ouvre_h": 6, "ferme_h": 12, "cartes_par_semaine": 4, "prix_carte": 120, "rabais_meubles": 0.6,
               "offre": 0.7, "humeur": 45, "rachat": 0.25, "demande": 1.3, "humeur_rachat": 40}

#: LA RUMEUR DU MARCHÉ (`audio.LIEUX["puces"]`, chargée en approchant, un dimanche matin) : pleine sur le terrain,
#: elle s'éteint à `portee_px` de son bord ; elle glisse vers ce volume en `glisse_s` secondes (on arrive, midi sonne).
#: LE CHIEN (30 sept. 2026) : un aboiement à `chien_px` du milieu du terrain, entre `chien_s[0]` et `chien_s[1]` secondes
#: d'écart — à l'horloge, jamais au dé — tant qu'on entend le marché.
RUMEUR: dict = {"portee_px": 320, "glisse_s": 2.5, "chien_s": [35, 70], "chien_px": 224}

#: Le terrain : tant de tuiles de large et de haut, tout d'herbe ou de friche, libre.
LARGEUR, HAUTEUR = 8, 4
TERRAIN = (",", ";")


def poser(ville: dict, dist: dict, loin_de: list[tuple[int, int]]) -> dict | None:
    """⚠️ Une RÈGLE, pas un tirage : le terrain vague (`LARGEUR` × `HAUTEUR` d'herbe ou de friche) le plus près de la
    planque À PIED (`dist`), rien de posé dessus ni autour (`frenesies._prises`), hors d'une cour de gang ou d'un
    chantier, à six tuiles au moins de toute trouvaille (`loin_de`) ; l'égalité en ordre de lecture. Les étals sur la
    deuxième rangée, deux tuiles chacun, deux tuiles d'allée entre eux."""
    sol = ville["sol"]
    prises = frenesies._prises(ville)
    zones = ville.get("zones") or []
    cours = [z for z in zones if z.get("gang")]
    chantiers = ville.get("chantiers") or []

    def libre(x, y):
        return (0 <= y < len(sol) and 0 <= x < len(sol[y]) and sol[y][x] in TERRAIN and (x, y) not in prises
                and not any(frenesies._dans(c, x, y) for c in cours)
                and not any(frenesies._dans(c, x, y, 2) for c in chantiers))

    for (x, y), _ in sorted(dist.items(), key=lambda t: (t[1], t[0][1], t[0][0])):
        if not all(libre(x + i, y + j) for i in range(LARGEUR) for j in range(HAUTEUR)):
            continue
        if any(x - 6 <= a < x + LARGEUR + 6 and y - 6 <= b < y + HAUTEUR + 6 for a, b in loin_de):
            continue
        etals = [{"slug": e["slug"], "x": x + 1 + i * 4, "y": y + 1} for i, e in enumerate(ETALS)]
        return {"x": x, "y": y, "l": LARGEUR, "h": HAUTEUR, "etals": etals}
    return None


def repliques() -> list[dict]:
    """Les répliques des marchands, comme `audio` les lit : une banque (`mission: "puces"`), une série par marchand."""
    return [{"slug": f"{r['qui']}-puces-{r['cle']}", "qui": r["qui"], "cle": r["cle"], "texte": r["texte"],
             "mission": "puces", "partie": "puces", "telephone": False} for r in REPLIQUES]


def exporter(place: dict | None) -> dict:
    """Ce que `/api/collections` sert du marché : les étals (qui vend quoi), la règle, le terrain — et, hors des
    définitions (⚠️ rien de neuf n'y entre), ce que disent les marchands, les séries de leurs voix et la rumeur."""
    from . import audio
    ou = {e["slug"]: e for e in (place or {}).get("etals", [])}
    etals = [{**{k: v for k, v in e.items() if k != "marchand"}, "marchand": dict(e["marchand"]),
              **({"x": ou[e["slug"]]["x"], "y": ou[e["slug"]]["y"]} if e["slug"] in ou else {})} for e in ETALS]
    dits: dict[str, dict[str, str]] = {}
    for r in REPLIQUES:
        dits.setdefault(r["qui"], {})[r["cle"]] = r["texte"]
    voix = audio.voix_puces()
    return {"titre": "LE MARCHÉ AUX PUCES", "etals": etals, "regle": dict(REGLE), "rumeur": dict(RUMEUR),
            "terrain": {k: place[k] for k in ("x", "y", "l", "h")} if place else None,
            "repliques": dits,
            "voix": [audio.serie_de_voix(f"{qui}-puces-", [v for v in voix if v["qui"] == qui]) for qui in VOIX],
            "sons": audio.echantillons_a_part("puces")}
