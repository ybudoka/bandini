"""Des choses à collectionner (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md).

Vague 1 — **les cartes de hockey de la Ligue de Baie-des-Brumes, saison 1974-75.** Quarante cartes,
cinq par district de terre, cinq joueurs de l'équipe du coin. On les trouve par terre, dans un recoin —
le fond d'une ruelle, un coin entre deux murs, le bout d'un quai —, un scintillement discret les trahit,
et on les ramasse en marchant dessus. Le carnet les range, le BILAN les compte.

⚠️ **POSÉES SUR LA VILLE FINIE, SANS UN DÉ** — la leçon de `devants.py`, de l'aéroport et des frénésies :
une tuile réservée pendant la construction re-tire toute la ville (« grossir un lieu garanti déplace la
ville »). Ce module lit la ville APRÈS la bande nord et les frénésies, et choisit par une RÈGLE écrite :
dans chaque district, les recoins les plus encaissés (le plus de murs autour), les plus loin les uns des
autres. Il ne touche à aucune autre liste : la ville d'avant est la même à l'octet (`test_collections`).

⚠️ **ET RIEN AU DÉMARRAGE DU NAVIGATEUR** : une carte par terre n'est pas un décor, elle se PEINT
(`Collections.dessiner`) — un décor de plus au chargement décale le numéro de tout ce qui naît ensuite
(« décor eager décale les identifiants »).

⚠️ **LE POIDS** : les noms, les dos et les places ne voyagent ni dans les définitions ni dans la carte —
les deux sont au ras de leur plafond. `definitions.construire` sort la clé `collections` de la carte et la
sert, avec le catalogue, sur `/api/collections` (comme les notes de la musique), demandé en arrière-plan.

⚠️ **LE NUMÉRO EST LE NOM** : la sauvegarde garde les numéros trouvés (`partie.collections.cartes`), jamais
un index de liste — et le marché aux puces (sa ligne, après celle-ci) vendra la carte qui manque par son
numéro. Un numéro ne change jamais de joueur.
"""

from __future__ import annotations

from collections import deque

from . import carte, frenesies

#: Les équipes de la Ligue, une par district de terre — l'équipe du coin, et ses deux couleurs (le fond du
#: chandail, la bande) : c'est elles qu'on voit par terre, et en grand au carnet.
EQUIPES: dict[str, dict] = {
    "faubourg": {"nom": "LES CASTORS DU FAUBOURG", "couleurs": ["#7a4a2a", "#e8c890"]},
    "erables": {"nom": "LES SEIGNEURS DES ÉRABLES", "couleurs": ["#6e1e2e", "#d8b04a"]},
    "shop": {"nom": "LES BOULONS DE LA SHOP", "couleurs": ["#4e555e", "#e07a28"]},
    "quais": {"nom": "LES GOÉLANDS DES QUAIS", "couleurs": ["#1e3a6e", "#f0f0f0"]},
    "pointe": {"nom": "LES PHOQUES DE LA POINTE", "couleurs": ["#2e7a78", "#d8ece4"]},
    "friches": {"nom": "LES CHARDONS DES FRICHES", "couleurs": ["#5e3a78", "#9ac050"]},
    "canton": {"nom": "LES DRAGONS DU CANTON", "couleurs": ["#b02a22", "#f2c230"]},
    "gare": {"nom": "LES AIGUILLEURS DE LA GARE", "couleurs": ["#2a2a2e", "#e8d040"]},
}

#: Les positions telles qu'une carte de 1974 les abrège.
POSITIONS: dict[str, str] = {"C": "CENTRE", "AG": "AILIER GAUCHE", "AD": "AILIER DROIT", "D": "DÉFENSEUR",
                             "G": "GARDIEN", "ORG": "ORGANISTE"}


def _c(numero: int, district: str, nom: str, position: str, *dos: str) -> dict:
    return {"numero": numero, "district": district, "nom": nom, "position": position, "dos": list(dos)}


#: ⚠️ Le DOS d'une carte : deux lignes au plus, qui tiennent dans une ligne du carnet (`test_collections`).
#: Le ton de docs/ecrire-drole.md — on frappe en haut (le propriétaire, le fils à papa, l'arbitre beau-frère),
#: jamais le petit joueur de garage : lui, on l'aime, et c'est pour ça que sa fiche tombe à plat.
CARTES: tuple[dict, ...] = (
    # Les Castors du Faubourg. La n° 1, c'est lui : l'homme de la statue du parc (`statues.py`).
    _c(1, "faubourg", "GILLES « LA TOQUE » BOUCHARD", "C",
       "LE BUT EN PROLONGATION CONTRE SOREL.", "IL VOUS LE RACONTE ? ÇA VA ÊTRE LONG."),
    _c(2, "faubourg", "RÉAL « LE MUR » PELLETIER", "G",
       "MOYENNE : 4,80 BUTS ALLOUÉS.", "LE MUR, C’ÉTAIT CELUI DERRIÈRE LUI."),
    _c(3, "faubourg", "ARMAND TREMBLAY", "D",
       "212 MINUTES DE PUNITION.", "L’ARBITRE ÉTAIT SON BEAU-FRÈRE."),
    _c(4, "faubourg", "JEAN-GUY « PETIT PAIN » LAVOIE", "AG",
       "LIVREUR DE PAIN LE MATIN.", "IL ARRIVAIT AUX GAMES ENCORE CHAUD."),
    _c(5, "faubourg", "MAURICE « TI-MO » GAGNON", "AD",
       "LANCER FRAPPÉ : 140 KM/H.", "MESURÉ PAR SON PÈRE. SON PÈRE EST POLICIER."),
    # Les Seigneurs des Érables : l'équipe qu'un père achète à son fils.
    _c(6, "erables", "CHARLES-HENRI DE LA RUE", "C",
       "SON PÈRE A ACHETÉ L’ÉQUIPE.", "PUIS LE TROPHÉE DU MEILLEUR JOUEUR."),
    _c(7, "erables", "PHILIPPE BEAUCHEMIN III", "D",
       "PATINS EN CUIR D’ITALIE.", "NE PATINE PAS DE RECULONS. ÇA SE FAIT PAS."),
    _c(8, "erables", "ÉDOUARD « LE NOTAIRE » MARTEL", "G",
       "ARRÊTE TOUT ENTRE 9 H ET 17 H.", "APRÈS, IL FACTURE."),
    _c(9, "erables", "LOUIS-PHILIPPE CÔTÉ-RENAUD", "AG",
       "A MANQUÉ LES SÉRIES ÉLIMINATOIRES.", "LE CHALET À MAGOG ÉTAIT RÉSERVÉ."),
    _c(10, "erables", "BERTRAND « LE GÉRANT » DUMAS", "AD",
       "A DEMANDÉ À PARLER AU GÉRANT DE L’ARÉNA.", "QUARANTE-TROIS FOIS. EN UNE GAME."),
    # Les Boulons de la Shop : l'équipe du quart de jour.
    _c(11, "shop", "ROLAND « 9/16 » ROY", "D",
       "A RÉPARÉ LA SURFACEUSE ENTRE DEUX PÉRIODES.", "ELLE N’A JAMAIS SI BIEN MARCHÉ."),
    _c(12, "shop", "GASTON OUELLET", "C",
       "PUNCHAIT À 7 H, JOUAIT À 8 H.", "DORMAIT SUR LE BANC À 8 H 05."),
    _c(13, "shop", "FERNAND « GRAISSE » LEBLANC", "AG",
       "INSAISISSABLE EN ÉCHAPPÉE.", "LES MAINS PLEINES D’HUILE À MOTEUR."),
    _c(14, "shop", "NORMAND BÉLANGER", "G",
       "LE SYNDICAT A NÉGOCIÉ SA PAUSE-CAFÉ.", "EN PLEINE PÉRIODE. ILS ONT GAGNÉ."),
    _c(15, "shop", "DENIS « LE CONTREMAÎTRE » FORTIN", "AD",
       "N’A JAMAIS TOUCHÉ LA RONDELLE.", "IL DÉLÉGUAIT."),
    # Les Goélands des Quais : des pêcheurs l'été, des hockeyeurs l'hiver, du poisson toute l'année.
    _c(16, "quais", "OMER « LA MORUE » BOUDREAU", "D",
       "SENTAIT LA BOËTTE DE HOMARD.", "LES AILIERS ADVERSES RESTAIENT LOIN."),
    _c(17, "quais", "ARTHUR CHIASSON", "C",
       "PÊCHEUR L’ÉTÉ, CENTRE L’HIVER.", "A PÊCHÉ PLUS DE RONDELLES QU’IL EN A COMPTÉ."),
    _c(18, "quais", "LÉO « LE CAPITAINE » POIRIER", "AD",
       "CAPITAINE D’UN CHALUTIER.", "PAS DE L’ÉQUIPE : ILS ONT VOTÉ CONTRE."),
    _c(19, "quais", "RAYMOND « BOUÉE » LANDRY", "G",
       "FLOTTAIT DANS SON ÉQUIPEMENT.", "À L’ÉPREUVE DES LANCERS. PAS DES GOÉLANDS."),
    _c(20, "quais", "ELZÉAR CORMIER", "AG",
       "SIX BUTS EN UNE GAME.", "TROIS DANS LE BON FILET."),
    # Les Phoques de La Pointe.
    _c(21, "pointe", "SYLVAIN « LA PLANCHE » RIOUX", "C",
       "PATINAIT COMME IL FAISAIT DU SKATE.", "SUR LES FESSES, EN SOURIANT."),
    _c(22, "pointe", "MARC-ANDRÉ « POUDREUSE » BÉRUBÉ", "AG",
       "ARRIVAIT AUX GAMES EN MOTONEIGE.", "MÊME EN MAI. SURTOUT EN MAI."),
    # Le petit-fils du buste du parc (`statues.BUSTES`) : il a de qui tenir.
    _c(23, "pointe", "BRUNO GAUTHIER", "D",
       "PETIT-FILS D’OMER GAUTHIER, L’INVENTEUR.", "A INVENTÉ LA FEINTE. APRÈS TOUT LE MONDE."),
    _c(24, "pointe", "JACQUES « LE PHOQUE » THÉRIAULT", "G",
       "SE COUCHAIT SUR LA GLACE.", "MÊME QUAND LE JEU ÉTAIT À L’AUTRE BOUT."),
    _c(25, "pointe", "KEVIN PARADIS", "AD",
       "LE SEUL KEVIN DE 1974.", "EN AVANCE SUR SON TEMPS. PAS SUR LE JEU."),
    # Les Chardons des Friches.
    _c(26, "friches", "RODRIGUE « LE CHARDON » LAPOINTE", "D",
       "PIQUAIT TOUT LE MONDE.", "SURTOUT LA RONDELLE DES AUTRES."),
    _c(27, "friches", "HERMAS DUCHESNE", "G",
       "JOUAIT SANS MASQUE.", "LA RONDELLE AVAIT PEUR DE LUI."),
    _c(28, "friches", "VICTOR « LA SCRAP » MORIN", "AG",
       "ÉQUIPEMENT VENU DE LA COUR À SCRAP.", "SES PATINS AVAIENT DES PNEUS D’HIVER."),
    _c(29, "friches", "CLÉMENT BOISVERT", "AD",
       "S’EST PERDU EN ALLANT À L’ARÉNA.", "RETROUVÉ EN AVRIL, EN PLEINE FORME."),
    _c(30, "friches", "ALPHONSE « GROS-BRAS » PICARD", "C",
       "N’A JAMAIS PERDU UNE MISE AU JEU.", "IL GARDAIT LA RONDELLE DANS SA POCHE."),
    # Les Dragons du Canton. Le neveu d'Irène Lam (la donneuse du Petit-Canton, `casino.py`).
    _c(31, "canton", "DAVID « LE DRAGON » CHAN", "C",
       "MEILLEUR PASSEUR DE LA LIGUE.", "IL PASSAIT AUSSI LES EGG ROLLS AU BANC."),
    _c(32, "canton", "HENRI LAM", "D",
       "NEVEU D’IRÈNE LAM.", "ELLE LUI A APPRIS À NE RIEN DIRE À PERSONNE."),
    _c(33, "canton", "ANDRÉ WONG", "G",
       "CONNAISSAIT LES RÈGLEMENTS PAR CŒUR.", "LES RÉCITAIT PENDANT LES BAGARRES."),
    _c(34, "canton", "MICHEL « PÉTARD » TRAN", "AG",
       "A FÊTÉ SON BUT AVEC DES PÉTARDS.", "L’ARÉNA A ÉTÉ ÉVACUÉ. DEUX FOIS."),
    _c(35, "canton", "PAUL NGUYEN-BOUCHARD", "AD",
       "COUSIN DE LA TOQUE, PAR ALLIANCE.", "A ENTENDU L’HISTOIRE DE SOREL 600 FOIS."),
    # Les Aiguilleurs de la Gare. Et la dernière n'est pas un joueur : c'est l'orgue.
    _c(36, "gare", "CONRAD « L’EXPRESS » VACHON", "AD",
       "LE PLUS RAPIDE DE LA LIGUE.", "NE S’ARRÊTAIT PAS AUX PASSAGES À NIVEAU."),
    _c(37, "gare", "ULYSSE BÉDARD", "C",
       "JAMAIS EN RETARD À UNE GAME.", "LE TRAIN DE 19 H 12, LUI, OUI."),
    _c(38, "gare", "HORACE « LE SIFFLET » GIGUÈRE", "D",
       "SIFFLAIT AVANT L’ARBITRE.", "LES DEUX ÉQUIPES S’ARRÊTAIENT."),
    _c(39, "gare", "EUGÈNE « WAGON » LESSARD", "G",
       "A BLOQUÉ CINQUANTE LANCERS EN UNE GAME.", "IL PRENAIT TOUT LE FILET, ASSIS."),
    _c(40, "gare", "GÉRARD MAILLOUX", "ORG",
       "A JOUÉ « LES PATINEURS » 11 000 FOIS.", "JAMAIS JUSQU’AU BOUT."),
)

#: Ce que le navigateur suit. `rayon_px` : à quelle distance on la ramasse (on marche dessus) ;
#: `prime` : ce que paie une carte ; `paliers` : la prime de plus à tant de cartes (la dernière, l'album
#: complet) ; `scintille_s` : un scintillement toutes les tant de secondes — assez pour l'œil qui fouille.
#: ⚠️ Des nombres plus bas que les paquets cachés (50 $, 500 $ à dix, 1 500 $ aux vingt) : il y en a deux
#: fois plus, et c'est un album, pas une paie.
REGLE: dict = {
    "rayon_px": 12,
    "prime": 25,
    "paliers": {"10": 250, "25": 500, "40": 1000},
    "scintille_s": 3,
}

#: Le sol d'un recoin : la ruelle, la friche, l'herbe, le quai. Pas la chaussée, pas le trottoir (on ne
#: cache rien là où tout le monde marche), pas le sable (une plage, ça se voit de loin).
RECOINS = ("x", ";", ",", "Q")
#: Un recoin a au moins tant de murs (tuiles qu'on ne marche pas) parmi ses huit voisines : un coin entre
#: deux murs en a trois, le fond d'une ruelle cinq. Un district qui en manque descend d'un cran.
ENCAISSEMENT_MIN = 3
#: Deux cartes, jamais à moins de tant de tuiles (de Tchebychev) l'une de l'autre : deux trouvailles.
ECART_MIN = 10
#: Les portes — la vraie, la condamnée, celle du garage : une carte ne se pose jamais sur leur pas (les deux
#: rangées sous elles, et une tuile de chaque côté : le perron déborde). Une porte condamnée n'est pas dans `ville["portes"]`, mais son perron se dessine : la
#: carte y avait l'air oubliée sur les marches (vu à la capture, n° 1).
PORTES = ("D", "d", "G")
#: Loin d'un paquet caché et d'une icône de frénésie : chaque trouvaille à sa place.
LOIN_D_UNE_CACHETTE = 6


def _encaissement(sol: list[str], x: int, y: int) -> int:
    """Combien des huit voisines de (x, y) ne se marchent pas (murs, bâtiments, clôtures, eau)."""
    n = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dx or dy) and not (0 <= y + dy < len(sol) and 0 <= x + dx < len(sol[y + dy])
                                   and carte.marchable(sol[y + dy][x + dx])):
                n += 1
    return n


def atteignables(ville: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'un piéton atteint depuis la planque, TOUTES les barrières piétonnes fermées (le pire
    cas, celui du juge des barrières) : une carte n'attend jamais une mission ni une heure."""
    sol = ville["sol"]
    murs: set[tuple[int, int]] = set()
    for b in ville.get("barrieres") or []:
        if "pieton" not in b.get("arrete", []) or b.get("existant"):
            continue
        for yy in range(b["y"], b["y"] + b["h"]):
            for xx in range(b["x"], b["x"] + b["l"]):
                if xx in (b["x"], b["x"] + b["l"] - 1) or yy in (b["y"], b["y"] + b["h"] - 1):
                    murs.add((xx, yy))
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    depart = (planque["x"], planque["y"])
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in vus or (nx, ny) in murs or not (0 <= ny < len(sol) and 0 <= nx < len(sol[ny])):
                continue
            if not carte.marchable(sol[ny][nx]):
                continue
            vus.add((nx, ny))
            file.append((nx, ny))
    return vus


def _cachettes(ville: dict) -> list[tuple[int, int]]:
    """Là où une trouvaille dort déjà : les paquets cachés et les icônes des frénésies."""
    return ([(p["x"], p["y"]) for p in ville.get("paquets") or []]
            + [(f["x"], f["y"]) for f in ville.get("frenesies") or []])


def recoins(ville: dict, district: dict, prises: set, pied: set) -> list[tuple[int, int, int]]:
    """Les recoins libres d'un district : `(encaissement, x, y)`, jamais sur une couche prise, dans une cour
    de gang ou autour d'un chantier, toujours rejoignables à pied depuis la planque."""
    sol = ville["sol"]
    zones = ville.get("zones") or []
    cours = [z for z in zones if z.get("gang")]
    chantiers = ville.get("chantiers") or []
    cachettes = _cachettes(ville)
    out = []
    for y in range(district["y"], min(district["y"] + district["h"], len(sol))):
        ligne = sol[y]
        for x in range(district["x"], min(district["x"] + district["l"], len(ligne))):
            if ligne[x] not in RECOINS or (x, y) in prises or (x, y) not in pied:
                continue
            if any(0 <= y - k and 0 <= x + dx < len(sol[y - k]) and sol[y - k][x + dx] in PORTES
                   for k in (1, 2) for dx in (-1, 0, 1)):
                continue
            if any(frenesies._dans(c, x, y) for c in cours) or any(frenesies._dans(c, x, y, 2) for c in chantiers):
                continue
            if any(max(abs(cx - x), abs(cy - y)) < LOIN_D_UNE_CACHETTE for cx, cy in cachettes):
                continue
            out.append((_encaissement(sol, x, y), x, y))
    return out


def choisir(candidats: list[tuple[int, int, int]], n: int, deja: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """⚠️ Une RÈGLE, pas un tirage : `n` recoins parmi `candidats`, les plus encaissés d'abord (un cran de
    moins s'il en manque), chacun le plus loin possible de ceux déjà choisis — ici et dans les districts
    voisins (`deja`) —, jamais à moins de `ECART_MIN`. L'égalité se tranche en ordre de lecture."""
    choisis: list[tuple[int, int]] = []
    for seuil in range(8, -1, -1):
        if seuil > ENCAISSEMENT_MIN and len([c for c in candidats if c[0] >= seuil]) < n:
            continue
        pool = sorted((c for c in candidats if c[0] >= seuil), key=lambda c: (c[2], c[1]))
        while len(choisis) < n:
            meilleur, cle = None, None
            for e, x, y in pool:
                if (x, y) in choisis:
                    continue
                loin = min((max(abs(x - a), abs(y - b)) for a, b in choisis + deja), default=999)
                if loin < ECART_MIN:
                    continue
                k = (min(loin, 60), e)
                if cle is None or k > cle:
                    meilleur, cle = (x, y), k
            if meilleur is None:
                break
            choisis.append(meilleur)
        if len(choisis) >= n or seuil <= 0:
            break
    return choisis


# --- Vague 3 : les bebelles ------------------------------------------------------------------------------------

#: ⚠️ LES BEBELLES (vague 3) : douze curiosités québécoises cachées dans les endroits durs — le bout de l'île, le
#: fond de l'aéroport, le fond du rang, le fond du ciné-parc, et le coin le plus loin de chaque district. Trouvée,
#: une bebelle se pose ELLE-MÊME sur l'étagère de la planque (`decoration.TROPHEES`, `etagere_bebelles`) : l'objet
#: est le trophée. Le SLUG est le nom (la sauvegarde garde `partie.collections.bebelles[slug]`), jamais un index —
#: mais l'ORDRE du catalogue est la place sur l'étagère : une bebelle de plus s'ajoute au bout.
#:
#: `ou` : une zone de la ville (`zone`) ou un bloc (`bloc`). `lignes` : ce qu'en dit le carnet — le ton de
#: docs/ecrire-drole.md, on frappe en haut (le proprio, le zonage, l'équipe qui déménage), jamais le petit monde.
#: `grille` : le dessin, 6 × 7 pixels (`.` : rien), et sa `palette` — peint par terre, sur l'étagère et au carnet.
def _b(slug: str, nom: str, ou: dict, lignes: tuple[str, str], grille: str, palette: dict) -> dict:
    return {"slug": slug, "nom": nom, "ou": ou, "lignes": list(lignes), "grille": grille.split(), "palette": palette}


BEBELLES: tuple[dict, ...] = (
    _b("bouteille", "LA BOUTEILLE À LA MER", {"zone": "ile"},
       ("LE MESSAGE : « RAPPORTEZ LA BOUTEILLE.", "DIX CENNES DE CONSIGNE. MERCI. »"),
       "..kk.. ..gg.. .gGgg. .gpgg. .gpGg. .gppg. .gggg.",
       {"k": "#8a5a2a", "g": "#3a7a4a", "G": "#8ac89a", "p": "#f0e6c8"}),
    # ⚠️ `enclos` : DANS la clôture de l'aéroport (`X`), pas dans l'herbe qui l'entoure — on y entre par la guérite,
    # que le laissez-passer ouvre (a02), après avoir sauté le trou du pont.
    _b("cendrier_expo", "LE CENDRIER DE L’EXPO 67", {"zone": "aeroport", "enclos": True},
       ("PRIS AU PAVILLON DE L’URSS, EN 1967.", "L’URSS N’A PAS PORTÉ PLAINTE. PLUS LE TEMPS."),
       "...... ...... .wwww. wbwwbw wwbbww swwwws .ssss.",
       {"w": "#e8e8ec", "b": "#2a5aa8", "s": "#8a909a"}),
    _b("raquette", "LA RAQUETTE EN BABICHE", {"bloc": "rang"},
       ("UNE SEULE. L’AUTRE EST PARTIE EN 1971", "AVEC LE BEAU-FRÈRE. LUI, ON L’ATTEND PAS."),
       ".bbbb. bllllb blbblb bllllb .bllb. ..bb.. ..bb..",
       {"b": "#7a4a22", "l": "#d8c090"}),
    _b("lunettes_3d", "LES LUNETTES 3D EN CARTON", {"bloc": "cineparc"},
       ("LE FILM ÉTAIT EN DEUX DIMENSIONS.", "LE PROPRIO LES VENDAIT QUAND MÊME. 2 $."),
       "...... ...... wwwwww rrwwcc rrwwcc w....w ......",
       {"w": "#f0ece0", "r": "#e03030", "c": "#30c8d8"}),
    _b("bonhomme", "LE BONHOMME EN PLASTIQUE", {"zone": "friches"},
       ("SA CEINTURE FLÉCHÉE EST PEINTE À LA MAIN.", "IL A LE REGARD DE CELUI QUI A TOUT VU."),
       "..rr.. .rrrr. .wkwk. .wwww. fyfrfy .wwww. .wwww.",
       {"r": "#d02a2a", "w": "#f4f4f8", "k": "#1c1a22", "f": "#2a5aa8", "y": "#e8c040"}),
    _b("calendrier", "LE CALENDRIER DU GARAGE, 1982", {"zone": "shop"},
       ("RESTÉ SUR FÉVRIER DEPUIS 1982.", "LE GARAGE AUSSI. LA FACTURE AUSSI."),
       ".rrrr. .rrrr. .wwww. .wgwg. .wwww. .gwgw. .wwww.",
       {"r": "#c83a2a", "w": "#f0ead8", "g": "#7a7a84"}),
    _b("lanterne", "LA LANTERNE DU SERRE-FREIN", {"zone": "gare"},
       ("ENCORE DE L’HUILE DEDANS.", "ELLE ATTEND LE TRAIN DE 19 H 12. NOUS AUSSI."),
       "..kk.. .k..k. .kkkk. .rRrr. .rrrr. .kkkk. .kkkk.",
       {"k": "#3a3a42", "r": "#c82a22", "R": "#ff8a5a"}),
    _b("chat_salue", "LE CHAT QUI SALUE", {"zone": "canton"},
       ("IL SALUE LES CLIENTS DEPUIS 1968.", "AUCUN NE LUI A RÉPONDU. IL CONTINUE."),
       ".w.w.w .wwwww .kwkw. .wwww. .rrrr. .wyyw. .wwww.",
       {"w": "#f4f0e8", "k": "#1c1a22", "r": "#d02a2a", "y": "#e8c040"}),
    _b("boite_biscuits", "LA BOÎTE DE BISCUITS DANOIS", {"zone": "faubourg"},
       ("DES BISCUITS, IL N’Y EN A JAMAIS EU.", "DES BOUTONS À COUDRE, DEPUIS 1953."),
       "...... .bbbb. bBBBBb bbbbbb bybyyb bbbbbb .bbbb.",
       {"b": "#2a4a9a", "B": "#6a8ad0", "y": "#e8c040"}),
    _b("flamant", "LE FLAMANT ROSE DE PARTERRE", {"zone": "erables"},
       ("INTERDIT PAR LE ZONAGE DES ÉRABLES.", "ARTICLE 12, ALINÉA « VOYONS DONC »."),
       ".pp... .pko.. ..p... ..ppp. .pppp. ...l.. ...l..",
       {"p": "#f07aa8", "k": "#1c1a22", "o": "#f0a040", "l": "#3a3a42"}),
    _b("tuque_marsouins", "LA TUQUE DES MARSOUINS", {"zone": "quais"},
       ("L’ÉQUIPE EST PARTIE À HARTFORD EN 1979.", "LA TUQUE EST RESTÉE. ELLE, ELLE EST FIDÈLE."),
       "..ww.. .tttt. tttttt wwwwww tttttt wwwwww ......",
       {"t": "#1a7a8a", "w": "#f0f0f0"}),
    _b("chien_tableau", "LE CHIEN DU TABLEAU DE BORD", {"zone": "pointe"},
       ("IL DIT OUI À TOUT DEPUIS 1977.", "ON L’A NOMMÉ AU CONSEIL MUNICIPAL."),
       ".bb... bbkb.. .bbb.. ..bbbb ..bbbb ..b..b ......",
       {"b": "#8a5a30", "k": "#1c1a22"}),
)

#: Ce que paie une bebelle (elles sont DURES à trouver : quatre fois une carte), et les primes aux paliers — la
#: dernière, l'étagère pleine.
REGLE_BEBELLES: dict = {"prime": 100, "paliers": {"6": 500, "12": 2500}}

#: Le sol d'une cachette de bebelle : les recoins des cartes, plus l'allée de pierre du rang et le sable.
SOLS_BEBELLE = RECOINS + ("g", "s")
#: ⚠️ Jamais collée au bord de la carte (`BORD_BEBELLE` tuiles ; trois en haut, sous les barres du HUD), ni dans
#: son coin nord-ouest (`COIN_BEBELLE` × `COIN_BEBELLE`) : la caméra s'y arrête et la mini-carte le couvre (vu à la
#: capture : le bonhomme au coin des Friches, la raquette au coin du rang, sous la mini-carte).
BORD_BEBELLE = 2
COIN_BEBELLE = 9
#: ⚠️ Ni sur la voie du train (posée APRÈS, sans une tuile : ses rails se peignent sur l'herbe) — tant de rangées
#: de part et d'autre de son rang (le bonhomme dormait entre les rails, vu à la capture).
VOIE_DU_TRAIN = 3


def _depuis(ville: dict, departs: list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """La distance À PIED (en pas de tuile) de chaque tuile atteinte depuis `departs`, les barrières piétonnes
    fermées — sauf celles qu'une MISSION ouvre (`condition.apres` : le pont et la guérite de l'aéroport) : une
    bebelle est dans un endroit DUR, elle peut attendre un laissez-passer ; jamais une heure ni un prix."""
    sol = ville["sol"]
    murs: set[tuple[int, int]] = set()
    for b in ville.get("barrieres") or []:
        if "pieton" not in b.get("arrete", []) or b.get("existant") or "apres" in (b.get("condition") or {}):
            continue
        for yy in range(b["y"], b["y"] + b["h"]):
            for xx in range(b["x"], b["x"] + b["l"]):
                if xx in (b["x"], b["x"] + b["l"] - 1) or yy in (b["y"], b["y"] + b["h"] - 1):
                    murs.add((xx, yy))
    dist = {d: 0 for d in departs}
    file = deque(departs)
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in dist or (nx, ny) in murs or not (0 <= ny < len(sol) and 0 <= nx < len(sol[ny])):
                continue
            if not carte.marchable(sol[ny][nx]):
                continue
            dist[(nx, ny)] = dist[(x, y)] + 1
            file.append((nx, ny))
    return dist


def _au_bout(sol: list[str], rect: dict | None, dist: dict, loin_de: list[tuple[int, int]], ecart: int,
             interdit=None) -> tuple[int, int] | None:
    """⚠️ Une RÈGLE, pas un tirage : dans `rect` (toute la carte si None), la tuile de cachette la plus LOIN à pied
    (`dist`), jamais sur le pas d'une porte ni à moins de `ecart` de `loin_de` ; l'égalité va au plus encaissé,
    puis à l'ordre de lecture."""
    meilleur, cle = None, None
    for (x, y), d in dist.items():
        if rect and not (rect["x"] <= x < rect["x"] + rect["l"] and rect["y"] <= y < rect["y"] + rect["h"]):
            continue
        if not (BORD_BEBELLE + 1 <= y < len(sol) - BORD_BEBELLE and BORD_BEBELLE <= x < len(sol[y]) - BORD_BEBELLE) \
                or (x < COIN_BEBELLE and y < COIN_BEBELLE):
            continue
        if sol[y][x] not in SOLS_BEBELLE or (interdit and interdit(x, y)):
            continue
        if any(0 <= y - k and 0 <= x + dx < len(sol[y - k]) and sol[y - k][x + dx] in PORTES
               for k in (1, 2) for dx in (-1, 0, 1)):
            continue
        if any(max(abs(cx - x), abs(cy - y)) < ecart for cx, cy in loin_de):
            continue
        k = (d, _encaissement(sol, x, y), -y, -x)
        if cle is None or k > cle:
            meilleur, cle = (x, y), k
    return meilleur


def poser_bebelles(ville: dict, cartes: list[dict]) -> list[dict]:
    """Les bebelles de la VILLE (celles d'une zone), sur la ville finie, sans un dé : dans leur zone, la cachette
    la plus loin à pied — de la planque, d'un amarrage pour l'île (on y arrive en chaloupe), du bout du pont pour
    l'aéroport (on y arrive en sautant le trou). Loin des paquets,
    des frénésies, des cartes et des autres bebelles ; jamais dans une cour de gang ni autour d'un chantier."""
    zones = ville.get("zones") or []
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    departs = [(planque["x"], planque["y"])]
    ile = ville.get("ile")
    if ile:
        departs += [(a["x"], a["y"]) for a in ile.get("amarrages", [])]
    # L'aéroport : son pont s'arrête au-dessus de l'eau (`aeroport.PONT`, le trou). On y arrive en sautant le trou
    # au volant — ou en chaloupe : la bebelle se cherche depuis le bout du pont, côté aéroport.
    pont = (ville.get("aeroport") or {}).get("pont")
    if pont:
        departs.append((pont["x"] + 1, pont["y"] + pont["nord"] + pont["trou"]))
    dist = _depuis(ville, departs)
    cours = [z for z in zones if z.get("gang")]
    chantiers = ville.get("chantiers") or []
    prises = frenesies._prises(ville)
    rang_du_train = (ville.get("train") or {}).get("rang")

    def interdit(x, y):
        if (x, y) in prises or (rang_du_train is not None and abs(y - rang_du_train) <= VOIE_DU_TRAIN):
            return True
        return any(frenesies._dans(c, x, y) for c in cours) or any(frenesies._dans(c, x, y, 2) for c in chantiers)

    loin = _cachettes(ville) + [(c["x"], c["y"]) for c in cartes]
    places: list[dict] = []
    for b in BEBELLES:
        z = b["ou"].get("zone")
        rect = next((q for q in zones if q.get("slug") == z and not q.get("gang")), None) if z else None
        if not rect:
            continue
        if b["ou"].get("enclos"):
            rect = _enclos(ville["sol"], rect) or rect
        ici = _au_bout(ville["sol"], rect, dist, loin + [(p["x"], p["y"]) for p in places], LOIN_D_UNE_CACHETTE, interdit)
        if ici:
            places.append({"slug": b["slug"], "x": ici[0], "y": ici[1], "indice": _indice(rect["nom"])})
    return places


def _indice(nom: str) -> str:
    """Le lieu, tel que le carnet le dit d'une bebelle qui manque (« LE RANG ») : l'indice, et rien de plus."""
    return nom.replace("'", "’").upper()


def _enclos(sol: list[str], z: dict) -> dict | None:
    """Le dedans de la clôture (`X`) d'une zone : le rectangle qu'elle borde, sans elle."""
    xs = [(x, y) for y in range(z["y"], min(z["y"] + z["h"], len(sol)))
          for x in range(z["x"], min(z["x"] + z["l"], len(sol[y]))) if sol[y][x] == "X"]
    if not xs:
        return None
    x0, x1 = min(x for x, _ in xs), max(x for x, _ in xs)
    y0, y1 = min(y for _, y in xs), max(y for _, y in xs)
    return {"x": x0 + 1, "y": y0 + 1, "l": x1 - x0 - 1, "h": y1 - y0 - 1, "nom": z["nom"]}


def places_des_blocs() -> list[dict]:
    """Les bebelles des BLOCS (le rang, le ciné-parc) : la cachette la plus loin à pied de l'arrivée du bloc, sur
    son plan écrit. ⚠️ En tuiles DU BLOC, jamais dans la ville (la bande nord les décalerait)."""
    from . import blocs  # ⚠️ ici : `blocs` importe `carte`, qui importe ce module
    places = []
    for b in BEBELLES:
        slug = b["ou"].get("bloc")
        bloc = slug and blocs.par_slug(slug)
        if not bloc:
            continue
        # ⚠️ Un arbre, un buisson du bloc est un DÉCOR posé sur son sol : on ne passe pas au travers — ses tuiles
        # comptent comme des murs pour le chemin (sinon « la plus loin » se cachait derrière une rangée d'arbres).
        decors = {(d["x"], d["y"]) for d in blocs.decor_du_bloc(bloc)}
        sol = ["".join("B" if (x, y) in decors else g for x, g in enumerate(ligne))
               for y, ligne in enumerate(blocs.sol_du_bloc(bloc))]
        dist = _depuis({"sol": sol}, [(bloc["arrivee"]["x"], bloc["arrivee"]["y"])])
        ici = _au_bout(sol, None, dist, [], 0)
        if ici:
            places.append({"slug": b["slug"], "bloc": slug, "x": ici[0], "y": ici[1], "indice": _indice(bloc["nom"])})
    return places


def poser(ville: dict) -> dict:
    """Les places des cartes de hockey, sur la ville FINIE. ⚠️ Aucun dé, rien de posé dans une autre liste :
    la ville reste la même, et une carte dont le district manque (la ville d'avant la bande nord) ne se pose
    pas. Rend `{"cartes": [{numero, x, y}]}`."""
    prises = frenesies._prises(ville)
    pied = atteignables(ville)
    zones = ville.get("zones") or []
    places: list[dict] = []
    deja: list[tuple[int, int]] = []
    for district in EQUIPES:
        d = next((z for z in zones if z.get("slug") == district and not z.get("gang")), None)
        siennes = [c for c in CARTES if c["district"] == district]
        if not d or not siennes:
            continue
        choisies = choisir(recoins(ville, d, prises, pied), len(siennes), deja)
        for c, (x, y) in zip(siennes, choisies):
            places.append({"numero": c["numero"], "x": x, "y": y})
            deja.append((x, y))
    # Les bebelles de la ville, APRÈS les cartes (elles s'en tiennent loin) : les cartes ne bougent pas d'une tuile.
    return {"cartes": places, "bebelles": poser_bebelles(ville, places)}


def exporter(places: dict | None, sons: dict | None = None) -> dict:
    """Ce que `/api/collections` sert : le catalogue (noms, positions, dos, équipes), la règle, et les places
    que la ville a trouvées (`poser`). Une carte sans place ne s'exporte pas avec une place : elle reste au
    catalogue (le carnet la montre, le marché aux puces pourra la vendre)."""
    ou = {p["numero"]: p for p in (places or {}).get("cartes", [])}
    cartes = []
    for c in CARTES:
        fiche = {k: c[k] for k in ("numero", "district", "nom", "position", "dos")}
        if c["numero"] in ou:
            fiche.update(x=ou[c["numero"]]["x"], y=ou[c["numero"]]["y"])
        cartes.append(fiche)
    return {"cartes": {"titre": "CARTES DE HOCKEY", "equipes": {d: {**e, "couleurs": list(e["couleurs"])} for d, e in EQUIPES.items()}, "positions": dict(POSITIONS),
                       "liste": cartes},
            "regle": {**REGLE, "paliers": dict(REGLE["paliers"])},
            "bebelles": _exporter_bebelles((places or {}).get("bebelles", [])),
            # Les sons des cartes (`audio.echantillons_a_part`) : hors des définitions, remis au paquet à l'arrivée.
            "sons": sons or {"lieu": "collections", "echantillons": []}}


def _exporter_bebelles(places: list[dict]) -> dict:
    """Le catalogue des bebelles, chacune avec sa place : celles de la ville (`poser`), celles des blocs
    (`places_des_blocs`, qui portent `bloc`). Une bebelle sans place reste au catalogue, sans place."""
    ou = {p["slug"]: p for p in list(places) + places_des_blocs()}
    liste = []
    for b in BEBELLES:
        fiche = {k: b[k] for k in ("slug", "nom", "lignes", "grille", "palette")}
        if b["slug"] in ou:
            fiche.update({k: v for k, v in ou[b["slug"]].items() if k != "slug"})
        liste.append(fiche)
    return {"titre": "BEBELLES", "liste": liste,
            "regle": {**REGLE_BEBELLES, "paliers": dict(REGLE_BEBELLES["paliers"])}}
