"""Le tripot du sous-sol du Dragon d'or : la BARBOTTE du Pouce (docs/jalons/le-casino-du-petit-canton.md, vague 4).

La fiche du casino : « une porte gardée, une mission pour l'ouvrir (avec le donneur du Petit-Canton), une salle
enfumée où les mises sont plus grosses et où la maison triche aussi ». Martin : « va y ».

⚠️ **LA BARBOTTE, PAS UN JEU DE PLUS DU DRAGON D'OR.** Le jeu de dés des arrière-boutiques de Montréal, des années
trente aux années soixante : deux dés, quatre coups qui gagnent (3-3, 5-5, 6-6, 5-6), quatre qui perdent (1-1,
2-2, 4-4, 1-2), et tout le reste se relance. On mise POUR ou CONTRE : les deux côtés ont la même chance, pile un
sur deux, et c'est le Pouce qui vit de sa PIASTRE — il prend cinq pour cent de chaque gain (`PIASTRE`). Honnête, la
barbotte rend donc 97,5 % : un peu mieux que la roulette d'en haut. Mais elle n'est pas honnête.

⚠️ **LA MAISON TRICHE, ET ÇA SE VOIT** (le cœur de la vague) : quand la mise grossit (`PIPES["seuil"]`), le Pouce
glisse ses DÉS PIPÉS sur le feutre — une fois sur… (`PIPES["chance"]`), et toujours contre le côté que tu as pris.
Ils se reconnaissent : de la vieille ivoire, plus JAUNE que les vrais (Irène te le dit à la fin de c01, et ça se
voit sur le feutre avant de lancer). Qui les voit a trois choix, et chacun se paie :
- **lancer quand même** : le côté du Pouce sort sept fois sur dix (mesuré au juge : la table rend 60 %) ;
- **DÉNONCER les dés** : juste, le Pouce te rend ta mise pour que la salle se taise, et te laisse tranquille
  jusqu'au lendemain — mais il s'en souvient (`MEFIANCE["denoncer"]`) ; faux (des dés honnêtes), les gros bras te
  sortent par la porte d'en arrière, et tu perds ta mise (`MEFIANCE["faux"]`) ;
- **CHANGER DE CÔTÉ** après que ses dés sont posés : ses pipés jouent pour TOI (la table te rend 135 %) — tant que
  le Pouce ne voit pas le manège (`MEFIANCE["retourner"]`, et plus si tu gagnes).
À cent de méfiance, les gros bras te raccompagnent, et le Pouce ne veut plus te voir d'une semaine
(`MEFIANCE["barre_jours"]`). Pas une étoile : dans un tripot, on n'appelle pas la police.

⚠️ **LE HASARD EST À LA TABLE** : chaque coup se tire d'un générateur semé par la graine de la partie, le numéro du
coup et le sel du tripot (`Tripot`, en JS) — jamais `B.rng()`. Ici, les fonctions prennent leurs TIRAGES en liste
(des nombres dans [0, 1)) : le navigateur a le jumeau de chacune, et un juge les compare tirage pour tirage.

⚠️ **LES MISES SONT RONDES** (`MISES`) : cinq pour cent de 100, 200, 500 ou 1 000 $ tombent sur un dollar rond.
"""

from __future__ import annotations

import random

from . import carte

#: Ce qu'on mise en bas, en dollars : dix fois ce qu'on mise en haut.
MISES = (100, 200, 500, 1000)

#: Combien de coups par jour de jeu : le Pouce ferme sa table à qui a assez joué.
COUPS_PAR_JOUR = 20

#: Les coups de la barbotte (deux dés, dans n'importe quel ordre) : ceux qui font gagner POUR, et ceux qui font
#: gagner CONTRE. Tout le reste se relance.
POUR = ((3, 3), (5, 5), (6, 6), (5, 6))
CONTRE = ((1, 1), (2, 2), (4, 4), (1, 2))
COTES = ("pour", "contre")

#: La part du Pouce sur un gain : cinq pour cent. Un coup gagné rend la mise et 95 % de la mise.
PIASTRE = 0.05

#: Au-delà de tant de relances sans coup, la main est NULLE et la mise rendue — une chance sur un milliard
#: (26/36 à la puissance 64), mais une boucle ne tourne jamais sans fin.
RELANCES = 64

#: LES DÉS PIPÉS : le poids de chaque face (du 1 au 6, sur quinze) des deux paires du Pouce — les BASSES font
#: sortir les coups de CONTRE (1, 2, 4), les HAUTES ceux de POUR (3, 5, 6). Il glisse la paire qui joue CONTRE
#: le côté que tu as pris, quand ta mise atteint `seuil`, une fois sur `1 / chance`.
PIPES: dict = {
    "seuil": 500,
    "chance": 0.6,
    "contre": (3, 3, 2, 3, 2, 2),   # les basses : ce qu'il pose quand tu mises POUR
    "pour": (2, 2, 3, 2, 3, 3),     # les hautes : ce qu'il pose quand tu mises CONTRE
}

#: CE QUE LE POUCE REMARQUE : une MÉFIANCE, de 0 à 100 (rien à voir avec la police, ni avec l'œil du Dragon d'or).
#: `retourner` : changer de côté quand ses pipés sont posés — il le voit ; `gagne` : et gagner avec ; `denoncer` :
#: le dire tout haut (il rend la mise, il s'en souvient). À `sortir`, les gros bras te raccompagnent par la porte
#: d'en arrière, et l'escalier te reste fermé `barre_jours`. Accuser des dés honnêtes (`faux`) : dehors tout de
#: suite, et jusqu'au lendemain. Elle fond de `oubli` par jour.
MEFIANCE: dict = {"retourner": 25, "gagne": 15, "denoncer": 40, "sortir": 100, "oubli": 30, "barre_jours": 7,
                  "faux_jours": 1}

#: Le retour AFFICHÉ au menu, en pour cent : celui d'une barbotte honnête (calculé : un sur deux, moins la piastre).
#: ⚠️ C'est un mensonge quand les pipés sont sur le feutre — c'est le propos.
RETOUR = 97


def face(u: float, poids: tuple[int, ...] | None) -> int:
    """La face d'un dé d'un tirage `u` dans [0, 1) : un dé honnête (`poids` à None), ou pipé."""
    if poids is None:
        return 1 + int(u * 6)
    k, total = u * sum(poids), 0
    for i, p in enumerate(poids):
        total += p
        if k < total:
            return i + 1
    return len(poids)


def coup(a: int, b: int) -> str | None:
    """Ce que deux dés disent : `pour`, `contre`, ou rien (on relance)."""
    paire = (min(a, b), max(a, b))
    if paire in POUR:
        return "pour"
    if paire in CONTRE:
        return "contre"
    return None


def jet(tirages: list[float], poids: tuple[int, ...] | None) -> tuple[str | None, list[list[int]]]:
    """Lance jusqu'au coup qui décide, deux tirages par lancer. Rend (le côté, ou None pour une main nulle ; les
    paires lancées, relances comprises)."""
    paires = []
    for k in range(RELANCES):
        a, b = face(tirages[2 * k], poids), face(tirages[2 * k + 1], poids)
        paires.append([a, b])
        c = coup(a, b)
        if c:
            return c, paires
    return None, paires


def pipe(mise: int, u: float) -> bool:
    """Le Pouce glisse-t-il ses pipés sur cette mise ? `u` : le premier tirage du coup."""
    return mise >= PIPES["seuil"] and u < PIPES["chance"]


def poids_contre(pari: str) -> tuple[int, ...]:
    """Les pipés qu'il pose contre ce pari : les basses contre POUR, les hautes contre CONTRE."""
    return PIPES["contre"] if pari == "pour" else PIPES["pour"]


def gain(pari: str, cote: str | None, mise: int) -> int:
    """Ce que la table rend, mise comprise : la mise et 95 % de la mise si le coup est de ton côté, la mise seule
    pour une main nulle, rien sinon."""
    if cote is None:
        return mise
    return mise + round(mise * (1 - PIASTRE)) if pari == cote else 0


def chance_du_cote(cote: str, poids: tuple[int, ...] | None) -> float:
    """La chance qu'un coup décidé soit de ce côté — CALCULÉE sur les trente-six (ou deux cent vingt-cinq) paires."""
    w = poids or (1, 1, 1, 1, 1, 1)
    p = [x / sum(w) for x in w]
    ou = {"pour": 0.0, "contre": 0.0}
    for a in range(1, 7):
        for b in range(1, 7):
            c = coup(a, b)
            if c:
                ou[c] += p[a - 1] * p[b - 1]
    return ou[cote] / (ou["pour"] + ou["contre"])


def retour(pari: str, poids: tuple[int, ...] | None) -> float:
    """Ce qu'un pari rend par dollar misé, calculé (la main nulle, une sur un milliard, comptée pour rien)."""
    return chance_du_cote(pari, poids) * (2 - PIASTRE)


def mefiance_apres(m: float, evenement: str) -> float:
    """La méfiance du Pouce après ce qu'il vient de voir (`MEFIANCE`)."""
    return min(150.0, m + MEFIANCE[evenement])


# --- Pour MESURER (tests/test_tripot.py) -------------------------------------------------------------------

def jouer_des_jours(rng: random.Random, jours: int, mise: int, strategie: str) -> dict:
    """Joue `jours` jours de barbotte, vingt coups par jour, toujours à `mise`, POUR, selon une stratégie :
    `naif` (il lance, quoi qu'il voie), `denonce` (il dénonce les pipés), `retourne` (il change de côté quand les
    pipés sont posés). La méfiance, les sorties et la semaine barrée comme au jeu. Rend ce qui a été misé, rendu,
    les coups joués, les sorties et les jours barrés. ⚠️ Pour MESURER : le jeu tire ses coups au hasard du
    navigateur (`Tripot`)."""
    mise_totale = rendu = coups = sorties = barres = 0
    mefiance, barre_jusqu_a = 0.0, -1
    for jour in range(jours):
        mefiance = max(0.0, mefiance - MEFIANCE["oubli"])
        if jour < barre_jusqu_a:
            barres += 1
            continue
        tranquille = False
        for _ in range(COUPS_PAR_JOUR):
            pari = "pour"
            pipes = not tranquille and pipe(mise, rng.random())
            poids = poids_contre(pari) if pipes else None
            coups += 1
            mise_totale += mise
            if pipes and strategie == "denonce":
                rendu += mise
                tranquille = True
                mefiance = mefiance_apres(mefiance, "denoncer")
            else:
                if pipes and strategie == "retourne":
                    pari = "contre"
                    mefiance = mefiance_apres(mefiance, "retourner")
                cote, _ = jet([rng.random() for _ in range(2 * RELANCES)], poids)
                g = gain(pari, cote, mise)
                rendu += g
                if pipes and strategie == "retourne" and g > mise:
                    mefiance = mefiance_apres(mefiance, "gagne")
            if mefiance >= MEFIANCE["sortir"]:
                sorties += 1
                mefiance = 0.0
                barre_jusqu_a = jour + MEFIANCE["barre_jours"]
                break
    return {"mise": mise_totale, "rendu": rendu, "coups": coups, "sorties": sorties, "barres": barres}


#: LA PREUVE (c02, _Une paire dans la manche_) : quand ses pipés sont sur le feutre, on GLISSE les siens dans sa
#: manche et on pose une paire honnête à la place — le truc du Pouce, retourné contre lui. La ligne n'apparaît au
#: menu que pendant un objectif `obtenir` dont la `table` est le tripot et l'`objet` celui-ci : c'est ce que la
#: mission dit, pas un nom de mission écrit dans le navigateur. Le coup se joue alors avec des dés honnêtes.
#: ⚠️ ENVOYÉ PAR IRÈNE, on est un gros poisson (Martin, 29 sept. 2026 : « je ne vois que peu de dés jaunes pour la
#: mission ») : tant que la preuve manque, le Pouce pipe CHAQUE mise de `PIPES["seuil"]` et plus — pas trois fois
#: sur cinq —, même après une dénonciation, et la table s'ouvre à cette mise-là.
PREUVE: dict = {"objet": "des_pipes", "nom": "LES DÉS PIPÉS DU POUCE"}

#: LE TRIPOT CHANGE DE MAINS (c04, _La barbotte change de mains_ ; Martin, 29 sept. 2026 : « on fait tomber le
#: Pouce pour de bon »). Après `apres`, le Pouce et ses gros bras ne sont plus là — ni au sous-sol, ni à la porte
#: d'en haut —, et c'est `croupier` qui tient la barbotte pour Irène : jamais de pipés, plus de méfiance ni de
#: semaine barrée, plus rien à dénoncer, et la piastre va à la caisse du quartier (`piastre`). Le retour affiché
#: (`RETOUR`, 97 %) cesse d'être un mensonge.
REPRISE: dict = {"apres": "c04", "titre": "LA BARBOTTE DU QUARTIER", "croupier": "Le vieux Chan",
                 "piastre": "5 % AU QUARTIER", "bulle": "ICI, LES DÉS SONT BLANCS."}


def pour_le_navigateur() -> dict:
    """Les règles, en chiffres : le navigateur tient le jumeau de chaque fonction (`Tripot`)."""
    return {"mises": list(MISES), "par_jour": COUPS_PAR_JOUR, "pour": [list(p) for p in POUR],
            "contre": [list(p) for p in CONTRE], "piastre": PIASTRE, "relances": RELANCES,
            "pipes": {k: list(v) if isinstance(v, tuple) else v for k, v in PIPES.items()},
            "mefiance": MEFIANCE, "retour": RETOUR, "preuve": PREUVE, "reprise": REPRISE}


# --- La salle ------------------------------------------------------------------------------------------------

#: UNE CAVE, PAS UN BUREAU (Martin, 29 sept. 2026) : les glyphes gardent leur règle, les `materiaux` de la pièce
#: changent le peintre (`TUILES['k@cave']`…) — le mur de fondation en pierre des champs, le plancher de béton, les
#: caisses de bière (`k`), les étagères de bouteilles (`e`), les tonneaux (`n`) et le feutre vert des petites tables
#: de cartes (`a`). ⚠️ Des matériaux REMPLACENT les murs de plâtre des pièces (`Monde.MATERIAUX_DE_PIECE`) : le mur
#: et la porte d'en arrière ont donc les leurs.
CAVE = {"B": "cave", "D": "cave", "t": "cave", "k": "cave", "e": "cave", "n": "cave", "a": "cave"}

#: LE TRIPOT, sous le Dragon d'or (vingt-quatre tuiles sur neuf, murs en plus). On y arrive par l'escalier du
#: coin (`/`), qui remonte à la grande salle. Au milieu, la table de la BARBOTTE (`!`, le feutre) et le Pouce
#: derrière ; au fond, le comptoir du bar et ses tabourets ; deux petites tables de cartes où jouent les habitués
#: (`a`, des chaises autour) ; des caisses de bière (`k`) et des étagères. Deux gros bras : un au pied de
#: l'escalier, un à la porte d'en arrière — ⚠️ LA PORTE `D` du bas est la sortie de secours des descentes de police
#: : elle ramène sur le trottoir du Dragon d'or, là où l'on est entré (le jeu ressort toujours par la porte d'en
#: haut, `B.exterieur`). ⚠️ À la mesure : plus petit que la grande salle (34 × 11), sinon le bâtiment du casino
#: grandirait et la ville glisserait (`carte.mesures_de_la_suite`).
PIECE = carte._piece("nord_tripot", "Le tripot du Pouce", sol="t", porte="maison", materiaux=CAVE, plan="""
BBBBBBBBBBBBBBBBBBBBBBBBBB
B/ kk  eee     ccccc  e nB
B                h h h   B
B        !!!!!           B
B        !!!!!    aa  aa B
B                 hh  hh B
Bn                       B
B  aa                    B
B  hh                  n B
Bk k                  k kB
BBBBBBBBBBBBDBBBBBBBBBBBBB
""", points=(carte._pt("escalier", 1, 1, vers="nord_casino"), carte._pt("barbotte", 11, 4)),
    gens=carte._gens(("pouce", 11, 2), ("gros_bras", 3, 2), ("gros_bras", 14, 9),
                     ("client", 19, 6), ("client", 3, 6), ("client", 17, 3)))

#: L'escalier d'en haut, dans la grande salle du Dragon d'or : le coin du sud-est, derrière une porte que garde un
#: gros bras (`casino.PIECE`). ⚠️ LA PORTE EST UNE BARRIÈRE DE LA PIÈCE, au format de `carte.BARRIERES` (comme
#: les serrures de la villa, `blocs.serrure`) : fermée tant que la mission qui l'ouvre n'est pas faite (`apres`),
#: pleine, et elle ne se force pas. `Monde.barrieres` la lit dans la carte COURANTE — la pièce.
PORTE: dict = {"slug": "tripot", "nom": "La porte du sous-sol", "x": 32, "y": 7, "l": 1, "h": 1,
               "arrete": ["pieton", "vehicule"], "condition": {"apres": "c01"}, "forcer": None,
               "raison": "LE SOUS-SOL, C'EST SUR INVITATION", "decor": "porte_tripot", "plein": True,
               "existant": False}
