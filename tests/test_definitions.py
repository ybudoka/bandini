import gzip
import json

from app import definitions


#: ⚠️ **LA GARDE DE LA DEUXIÈME CURE** (30 sept. 2026) : chaque clé des définitions, son poids gzip SEUL (octets,
#: niveau 6, le JSON du paquet) à la mesure du 30 sept. 2026, et son BUDGET. Le plafond d'en bas avait été relevé
#: presque chaque jour sans que rien ne dise qui mangeait la marge : en un jour après la première cure, les
#: saisons (+711), les photos (+660, clé neuve), l'Halloween (+625, clé neuve) et Le Boss (+542) l'avaient
#: remangée à sept octets près. Maintenant :
#: - une clé qui dépasse SON budget rougit en se nommant (`test_chaque_cle_du_paquet_tient_son_budget`) ;
#: - une clé neuve s'écrit ICI, avec son poids, ou elle rougit ;
#: - le plafond global, s'il cède, nomme les trois clés qui ont le plus grossi depuis cette mesure.
#: Relever un budget, c'est écrire ICI pourquoi, à la ligne de la clé ; mais d'abord regarder si elle peut sortir
#: (`definitions.DANS_LA_SUITE`, `/api/mission/<slug>`, un bloc, ou un champ qu'aucun script ne lit).
#: Budget de départ : la mesure + 10 % + 100, arrondi au 50.
MESURE_DU_PAQUET: dict[str, tuple[int, int]] = {
    "audio": (6_879, 7_800),     # +100 le 30 sept. 2026 : la patinoire du parc (sa rumeur de glace, sa valse du soir)
    "pietons": (5_227, 5_850),
    "defis": (4_088, 4_600),
    "economie": (3_943, 4_450),
    # M16, le reste (30 sept. 2026) : 42 octets gzip par mission au catalogue (titre, donneur, prérequis, prime,
    # `donne`) — vague 7, l'hôpital (h03-h07) : 4 028 → 4 240 ; vague 8, la fin de la dette (d05-d08), et l'échec et
    # la phase qui valent leur défaut ne voyagent plus (`missions.PAR_DEFAUT_AU_NAVIGATEUR`) : 4 274 ; vague 9, le
    # Clairon de Louise (l01-l06) : 4 523 — au-dessus du budget. Le message de la fin (`donne.message`) voyage
    # désormais avec la mission (`missions._sans_le_message`, `/api/mission/<slug>`) : 2 779. Budget recalculé par la
    # règle de départ (mesure + 10 % + 100) : ≈ 30 octets par mission, une dizaine de vagues. Vagues 10 à 12 (Roy,
    # la fin de l'arc R, ce qui restait des districts : 13 missions) : 3 073 ; vague 13, l'île, et tout `donne`
    # voyage avec la mission (`pour_jouer`) : 2 631 ; vague 14 (i06, i08, h08) : 2 793. 1er oct. 2026, le casse
    # (x01-x04) et d09 : 2 898 — et les douze PETITES JOBS n'y entrent pas : elles voyagent dans la suite (`jobs`,
    # `definitions.DANS_LA_SUITE`), « archétype@district » au lieu de leur passant entier (`missions._au_catalogue`).
    # Vagues 20 à 23 (1er oct. 2026 : p06-p12, e08-s13, q14 — quatorze missions de plus) : 3 195. Rien de ce qui reste
    # au catalogue ne sort sans que le carnet, le GPS ou le téléphone perde de quoi choisir (titre, donneur, prérequis,
    # prime ; et `echec` quand il ne vaut pas son défaut) : budget recalculé par la règle de départ.
    "missions": (3_195, 3_600),
    # Les PETITES JOBS, pliées (1er oct. 2026, `missions.jobs_pour_le_navigateur`) : douze jobs, une liste chacune
    # (slug, titre, donneur, prime, « archétype@district », prérequis) — `Jobs.deplier` les remet dans `missions`.
    # ⚠️ Le brut des définitions n'a plus que ≈ 50 octets de marge sous 242 000 : la prochaine clé qui grossit le passe.
    "jobs": (363, 500),
    "garderobe": (3_460, 3_950),
    "personnages": (2_728, 3_150),
    "vehicules": (1_973, 2_300),
    # Le caddie, la plaque de rue et le panneau drôle (2 oct. 2026, docs/jalons/le-decor-les-betes-et-les-gens-repondent.md) :
    # la fouille du caddie (six objets drôles), sa poussée (sept nombres) et ce que dit le passant bousculé, plus
    # l'invite et le gabarit de la plaque — 1 863 → 2 251. Les panneaux, eux, voyagent dans la SUITE (`panneaux`).
    "interactions": (2_251, 2_600),
    "visages": (1_695, 2_000),
    # Rosa habille l'hiver, vague 2 (30 sept. 2026) : `saisons.joueur` — le froid, la neige, le verglas et
    # la ceinture fléchée, avec leurs répliques (1 695 → 2 117).
    "saisons": (2_117, 2_400),
    "comptoirs": (1_547, 1_850),
    "recherche": (1_361, 1_600),
    "manettes": (1_265, 1_500),
    "armes": (1_126, 1_350),
    "techniques": (1_094, 1_350),
    "conduite": (1_000, 1_200),
    "nuit": (835, 1_050),
    "rixes": (604, 900),
    # Rosa habille l'hiver (30 sept. 2026) : la copie des tenues sort de `magasins` (rien ne la lisait) —
    # 795 → 310 —, et `tenues` grossit de douze pieces (542 → 872) : le paquet y gagne 71 octets bruts.
    "magasins": (310, 450),
    "tables_de_jeu": (790, 1_000),
    "halloween": (625, 800),
    "devantures": (616, 800),
    "garage": (561, 750),
    "tenues": (872, 1_050),
    "distributrices": (530, 700),
    "ambulants": (523, 700),
    # Les foyers de l'hiver (la foire fermée l'hiver, vague 3, 30 sept. 2026) : les places des braseros et de la
    # roulotte, la chaleur, le chocolat — lus en jeu, au premier hiver venu (il commence en janvier).
    "foyers": (277, 450),
    "demenagement": (455, 650),
    "pluie": (426, 600),
    "mantes": (421, 600),
    "verglas": (380, 550),
    "scenes": (363, 500),
    "saint_jean": (348, 500),
    "blocs": (348, 500),
    "machine_a_sous": (344, 500),
    "pont": (343, 500),
    "ouverture": (339, 500),
    "dojo": (308, 450),
    "videopoker": (304, 450),
    "fetes": (263, 400),
    "enseignes": (260, 400),
    "calendrier": (252, 400),
    "brouillard": (252, 400),
    "armes_regles": (153, 300),
    "coiffures": (152, 300),
    "loto": (144, 300),
    "marche_noir": (141, 300),
    "quatre_roues": (140, 300),
    "motoneige": (135, 250),
    "ordre_armes": (134, 250),
    "derby": (122, 250),
    "reclame": (121, 250),
    "repos": (107, 250),
    "cles_des_serrures": (64, 200),
    "suite_empreinte": (38, 150),
    # Les rayons des comptoirs, sortis de la suite le 6 oct. 2026 (`/api/rayons`).
    "rayons_empreinte": (38, 150),
    "musiques_empreinte": (38, 150),
    "missions_empreinte": (38, 150),
    "empreinte": (38, 150),
    "collections_empreinte": (38, 150),
    "carte_empreinte": (38, 150),
    "blocs_empreinte": (38, 150),
    "version": (29, 150),
    "decalage_nord": (23, 150),
    "tuile_px": (22, 150),
}


#: ⚠️ **LA MÊME GARDE POUR LA CARTE** (30 sept. 2026, docs/jalons/charger-les-districts-autour-du-joueur.md) : la
#: carte voyage PLIÉE (`app/pliage.py`), et chacune de ses clés a son poids gzip seul — tel qu'elle voyage, pliée —
#: et son budget, même règle qu'au-dessus (la mesure + 10 % + 100, arrondi au 50). Son plafond avait été relevé
#: onze fois en quinze jours sans que rien ne dise qui le mangeait. Une clé neuve de la carte s'écrit ICI (comme
#: dans `nord.DECALAGES`) ; relever un budget s'écrit à sa ligne, avec pourquoi.
MESURE_DE_LA_CARTE: dict[str, tuple[int, int]] = {
    "sol": (9_556, 10_650),
    "decor": (7_054, 7_900),
    # Des étages dedans aussi (30 sept. 2026) : +1 298 — les étages des triplex et le logement du commerçant.
    "interieurs": (7_754, 8_650),
    "voie": (2_760, 3_150),
    "montagne_russe": (1_988, 2_300),
    "devantures": (1_937, 2_250),
    "portes": (1_600, 1_900),
    "lampes": (1_484, 1_750),
    "autobus": (1_278, 1_550),
    "residences": (1_194, 1_450),
    "chantiers": (1_145, 1_400),
    "legende": (1_121, 1_350),
    "arrets": (969, 1_200),
    "toits": (958, 1_200),
    "points_interet": (902, 1_100),
    "zones": (808, 1_000),
    "eboueurs": (620, 800),
    "barrieres": (585, 750),
    "aeroport": (577, 750),
    "graffitis": (539, 700),
    "concessionnaires": (524, 700),
    "neige": (522, 700),
    "intersections": (516, 700),
    "frenesies": (500, 650),
    "decor_solide": (419, 600),
    "entraves": (408, 550),
    "feux_pietons": (389, 550),
    "tramway": (387, 550),
    "scenes": (353, 500),
    "nids_de_poule": (299, 450),
    "ile": (295, 450),
    "canton": (283, 450),
    "grille": (276, 450),
    "train": (260, 400),
    "kiosques_de_foire": (258, 400),
    "districts": (255, 400),
    "metro": (248, 400),
    "portes_garage": (245, 400),
    "familles": (245, 400),
    "zonage": (222, 350),
    "traversier": (221, 350),
    "incendies": (218, 350),
    "grille_nord": (211, 350),
    "ambulants": (210, 350),
    "train_de_foire": (203, 350),
    "aqueducs": (200, 350),
    "chemins_des_bois": (189, 350),
    "fourriere": (188, 350),
    "reclames": (181, 300),
    "navette": (178, 300),
    # Le tour de l'île (1er oct. 2026, i07) : six bouées de course.
    "regate": (60, 150),
    "rampes": (176, 300),
    "paquets": (172, 300),
    # La file devant l'arche (30 sept. 2026, docs/jalons/une-file-pour-entrer-a-la-foire.md) : `Monde.charger` la
    # lit avant JOUER — son serpentin est solide dès la première image.
    "file_de_foire": (161, 300),
    "jeux_de_foire": (147, 300),
    "stationnement_du_poste": (144, 300),
    "foire_enclos": (140, 300),
    "fermetures": (139, 300),
    "mouillages": (135, 250),
    "amarrages": (132, 250),
    "foire": (122, 250),
    "aqueduc": (102, 250),
    "patinoire": (101, 250),     # la patinoire du parc (30 sept. 2026) : sa place et ses deux portes
    "plages": (99, 250),
    "frenesies_regle": (84, 200),
    "entrave": (72, 200),
    "fermeture": (68, 200),
    "relief": (60, 200),
    "ponts": (60, 200),
    "quatre_roues": (55, 200),
    "lave_auto": (45, 150),
    "devant": (45, 150),
    "apparition": (45, 150),
    "empreinte": (38, 150),
    "slug": (37, 150),
    "roue": (37, 150),
    "nom": (37, 150),
    "flottants": (29, 150),
    "graine": (28, 150),
    "largeur": (23, 150),
    "hauteur": (23, 150),
    "decalage_nord": (23, 150),
    "tuile_px": (22, 150),
    "tuiles_bouchees": (21, 150),
}


def _gzip_par_cle(corps: bytes) -> dict[str, int]:
    """Le poids gzip de chaque clé des définitions, seule — comme `MESURE_DU_PAQUET` l'écrit."""
    return {cle: len(gzip.compress(json.dumps(valeur, ensure_ascii=False, separators=(",", ":"),
                                              sort_keys=True).encode("utf-8"), 6))
            for cle, valeur in json.loads(corps).items()}


def _qui_a_grossi(corps: bytes, combien: int = 3, mesure: dict[str, tuple[int, int]] | None = None) -> str:
    """Les clés qui ont le plus grossi depuis `MESURE_DU_PAQUET` (ou `mesure`) et les clés neuves, en une ligne."""
    mesure = MESURE_DU_PAQUET if mesure is None else mesure
    ecarts = sorted(((poids - mesure.get(cle, (0, 0))[0], cle) for cle, poids in _gzip_par_cle(corps).items()),
                    reverse=True)[:combien]
    ecarts = [(ecart, cle) for ecart, cle in ecarts if ecart > 0]
    if not ecarts:
        return "aucune clé n'a grossi depuis la mesure : elle est à réécrire"
    return ", ".join(f"{cle} +{ecart}" + ("" if cle in mesure else " (clé neuve)") for ecart, cle in ecarts)


def test_le_paquet_est_deterministe():
    # ⚠️ Deux constructions POUR DE VRAI : la fixture `paquets` n'en ferait qu'une.
    a, b = definitions.construire(), definitions.construire()
    for nom in ("definitions", "carte"):
        assert getattr(a, nom).corps == getattr(b, nom).corps, nom
        assert getattr(a, nom).etag == getattr(b, nom).etag, nom
        assert len(getattr(a, nom).etag) == 16, nom


def test_le_paquet_reste_leger(paquets):
    """⚠️ Budget releve a 600 Ko bruts le 13 sept. 2026 (demande de Martin).

    Mesure du 13 sept. 2026 : 370 Ko bruts / 43 Ko gzip, dont 306 Ko de carte
    pour 89 673 tuiles — et la carte ne pese que 26 Ko sur le fil, parce que
    `sol` et `voie` sont des suites de glyphes que gzip adore.

    Le brut n'est qu'un INDICATEUR : ce qui coute, c'est le gzip qui voyage
    et le temps de JSON.parse sur le telephone. Le plafond de 400 Ko etait a
    30 Ko d'etre touche par n'importe quel ajout ; il ne mesurait plus rien.
    Le gzip garde ses 70 Ko, et c'est lui le juge. Si le fil deborde, la
    carte sort du paquet (`/api/carte`, districts charges autour du joueur)
    — pas avant : personne n'a encore prouve le besoin de cette machinerie.
    Et ce qui n'est pas de la geographie (les dialogues de M16) n'entre pas
    ici du tout : une requete par mission, quand le telephone sonne.

    ⚠️ **Releve a 75 Ko gzip le 16 sept. 2026** (le petit train et la montagne
    russe de la foire). Mesure : 67 898 octets avant, 71 417 apres — dont
    2 667 pour la voie de la montagne russe, 407 points (x, y, z). Exportee en
    pixels ENTIERS (le dessin arrondit de toute facon), elle tombe a 1 975, et
    le paquet a 70 690 : sept cents octets au-dessus d'un plafond qui n'en
    laissait plus que deux mille a la ville entiere. Cinq Ko de plus, c'est
    une image de kiosque sur le fil, une fois, puis le cache de l'empreinte.
    Le remede du debordement reste celui d'au-dessus — la carte sort du paquet
    —, et c'est a ce plafond-ci qu'on le prendra.

    ⚠️ **LA CARTE EST SORTIE DU PAQUET le 16 sept. 2026** — decision de Martin,
    et c'est ce plafond-ci qui l'a demandee : avec L'Ile-aux-Corneilles, le paquet
    passait a 75 307 octets gzip (la ville seule 74 472, l'ile 835). Mesure au
    decoupage : les definitions 32 975 octets gzip (140 Ko bruts), la carte
    41 269 (374 Ko bruts). Chacune a desormais SON plafond.

    ⚠️ **Ce que le decoupage n'achete pas, et il faut le dire** : au premier
    chargement, le telephone recoit a peu pres autant d'octets qu'avant, en deux
    requetes paralleles au lieu d'une. Ce qu'il achete : un deploiement qui ne
    touche que les catalogues revalide la carte par un 304 (et l'inverse), deux
    `JSON.parse` plus petits, et un budget par sujet — la carte ne mange plus la
    marge des missions. Le vrai remede au poids du demarrage reste la dette des
    districts charges autour du joueur, avec son declencheur (« Dettes »).

    ⚠️ **La carte : 48 000 → 50 000 octets gzip le 21 sept. 2026.** Mesure : elle
    pesait 47 999 octets — UN de moins que le plafond, sans que personne y ait
    pense —, et le cabriolet rose (son nom dans les `rares` de deux districts et
    de leurs cours de gang) en a ajoute 13. Ce n'est pas le cabriolet qui a
    rempli la carte, c'est que le plafond n'avait plus de marge : le prochain
    ajout, quel qu'il soit, l'aurait fait tomber. Deux Ko de marge, et la meme
    regle qu'avant : le vrai juge du poids est le declencheur de la dette
    (« plus de 2 s entre Jouer et la ville »), pas ce nombre.

    ⚠️ **Les définitions : 40 000 → 44 000 octets gzip le 21 sept. 2026.** Mesure : huit missions
    pesaient 39 526 octets (474 sous le plafond), treize en pèsent 41 886 — **470 octets par mission**
    (objectifs, répliques, scènes : tout le catalogue voyage dans le paquet). Quatre mille de marge
    font place à quatre missions de plus ; ce n'est pas un droit d'en écrire cent. Le remède est
    écrit depuis le 16 sept. dans la fiche de M16 : les dialogues et les scènes sortent du paquet
    (`/api/dialogue/<slug>`, ETag), et le catalogue seul y reste. Il n'est pas livré ; ce plafond-ci
    est ce qui le rendra urgent. ⚠️ Le JEU des répliques (`jeu=`) n'y voyage PAS
    (`missions.pour_le_navigateur`) : il ne sert qu'à générer les voix.

    ⚠️ **La carte : 50 000 → 53 000 octets gzip, 450 000 → 520 000 bruts, le 21 sept. 2026**
    — l'aéroport (demande de Martin : « aggrandit la carte au sud »). Mesure : 48 282 → 50 331
    octets gzip, 409 780 → 483 244 bruts. Les 80 rangées que la carte gagne au sud font
    presque tout le brut (deux calques de 419 glyphes chacune) et presque rien sur le fil (de
    l'eau, que gzip avale) ; l'île dessinée et sa fiche font les deux Ko du fil (la fiche seule :
    454 octets). Une carte plus grande pèse plus : c'est le prix de la demande, pas une fuite.

    ⚠️ **Les définitions : 44 000 → 54 000 octets gzip, 200 000 → 250 000 bruts, le 21 sept.
    2026.** Trois sessions concurrentes ont grossi le paquet en même temps, chacune sans voir
    les deux autres : les dix missions du Faubourg/l'hôpital/l'aéroport (230 545 bruts / 50 590
    gzip, plafond jamais relevé pour elles), « Ça travaille » vagues 5-9 (+794 bruts / +111 gzip,
    la pelleteuse du catalogue des véhicules), Sven et le piratage — m52-m54, demande de Martin :
    « je veux de longue mission » (+9 840 bruts / +1 629 gzip, trois missions et un personnage).
    Mesuré une fois les trois réunies : **241 179 bruts / 52 330 gzip.** Plafond posé avec de la
    marge pour ne pas revenir ici au prochain petit ajout. Le remède reste le même, écrit depuis
    le 16 sept. dans la fiche de M16 : ce qui sert à jouer sort du paquet (`/api/mission/<slug>`,
    ETag) — il n'est pas livré, et ce plafond-ci s'en rapproche.

    ⚠️ **ET IL L'EST, LE 24 SEPT. 2026** : ce qui sert à JOUER une mission est sorti du
    paquet (`missions.HORS_DU_PAQUET` — répliques, scènes, voix, objectifs). 369 224 →
    **220 367 octets bruts**, 75 138 → **48 971 gzip**. Le juge était rouge depuis la
    veille ; le catalogue est passé de 170 à **53 octets gzip par mission**, ce qui laisse
    **94 missions de marge au lieu de cinq**. Les plafonds ne bougent pas : c'est le paquet
    qui a maigri.

    ⚠️ **Les définitions : 54 000 → 56 000 octets gzip le 26 sept. 2026.** Mesure : 53 660 avant la
    journée (340 de marge), et le 6/49 qui se dit l'a fait déborder — ses 55 voix, déclarées une par
    une, pesaient 8 870 bruts / 515 gzip. Elles voyagent maintenant en SÉRIE (`audio.serie_de_voix`,
    dépliée par `Son.Voix.histoire`), le chemin du pont de glace en rangées : 244 962 bruts / 54 404
    gzip avec l'année du jeu (`calendrier`) et le pont. Deux Ko de marge ; le remède du poids reste la
    dette des districts chargés autour du joueur.

    ⚠️ **Le brut : 250 000 → 260 000 le 26 sept. 2026**, même journée : les défis et les comptoirs de la
    cabane à sucre, du hockey, de la motoneige et du derby, l'année du jeu, la Saint-Jean et le ciné-parc —
    250 142 octets bruts, un indicateur (le gzip reste le juge, sous son plafond).

    ⚠️ **Le gzip : 56 000 → 58 000 le 26 sept. 2026, le soir.** Mesure : 54 404 le matin, 56 003 le soir —
    le dojo (une autre session), la motoneige, la Saint-Jean, le ciné-parc, la cabane à sucre, les défis
    du hockey et de la tire, et les Galeries (dont la voix au haut-parleur voyage déjà en série). Deux Ko
    de marge ; le remède du poids reste celui d'en haut, et c'est ce plafond-ci qui le rendra urgent.

    ⚠️ **La carte : 53 000 → 55 000 octets gzip le 26 sept. 2026, tard.** Mesure : 52 767 avant (233 de
    marge — la ville avait grossi sans y toucher : le dojo, le traversier), 53 023 avec les enseignes qui
    ouvrent pour vrai (quatre points de plus sur la carte, la baie du lave-auto, la toile du Rialto : +539
    bruts, +256 gzip). Deux Ko de marge, la même règle : le vrai juge est la dette du chargement.

    ⚠️ **Les définitions : 58 000 → 60 000 gzip, 260 000 → 270 000 bruts, le 27 sept. 2026.** Mesure :
    57 336 avec les enseignes, 57 757 avec le garage de Ti-Guy (ses pièces, ses répliques, l'air du klaxon),
    58 258 avec le 1er juillet (les places de seize camions et de trente-deux meubles) — 257 937 bruts. Le
    remède reste celui d'en haut ; ce plafond-ci le rapproche.

    ⚠️ **La carte : 55 000 → 67 000 octets gzip, 520 000 → 720 000 bruts, le 27 sept. 2026** — la ville
    s'agrandit au nord (demande de Martin : le Petit-Canton « comme le Faubourg », au nord, avec des friches
    et des voies ferrées ; `app/nord.py`). Mesure : 53 023 → 64 120 octets gzip (niveau 6) pour le paquet de
    la carte (682 287 bruts) : 110 rangées de 459 tuiles sur deux calques, et une deuxième ville
    dessus — des rues, des terrains, des wagons, pas de l'eau que gzip avale. Une carte plus grande pèse
    plus : c'est le prix de la demande. Trois Ko de marge, et la même règle : le vrai juge est la dette des
    districts chargés autour du joueur.

    ⚠️ **La carte : 67 000 → 68 000 octets gzip, le 28 sept. 2026** — le casino du Dragon d'or (demande de
    Martin : « un grand casino dans le quartier Petit-Canton »). Mesure : 66 608 sur `dev` (le bidonville de
    la gare venait d'en prendre sa part), 67 248 avec le casino — sa grande salle (228 octets), l'arche et les
    lanternes (253, idéogrammes compris) et le bois à clin de l'île (168). Ces deux derniers ont QUITTÉ le
    paquet des définitions, qui débordait (60 108 pour 60 000) : ils ne servent qu'à peindre la carte. Même
    règle qu'au nord : le vrai juge est la dette des districts chargés autour du joueur.

    ⚠️ **Les définitions : 60 000 → 62 000 gzip, le 28 sept. 2026, le soir.** Mesure : 59 952 sur `dev`
    après le casino (48 octets de marge — les frénésies, la cabane à sucre pour vrai, le bidonville),
    60 168 avec les trois missions d'infiltration de la villa (le catalogue +693 bruts, les noms des lieux
    de la villa dans `blocs` +223). Troisième relève en trois jours : le remède d'en haut ne peut plus
    attendre.

    ⚠️ **Et la fin de l'arc F de M16, le même soir, sous le même plafond.** Mesure : `dev` pesait
    59 983 (dix-sept octets de marge, après les frénésies) ; la fin de l'arc F de M16 — f10, f12, f13, Norbert, son visage et
    son point dans le hall — en ajoute 151, soit 60 134. Cinquante octets gzip par mission, c'est ce que le
    catalogue coûte depuis que les objectifs voyagent à part (24 sept.) ; soixante-dix missions de M16 restent
    à écrire, ≈ 3,5 Ko. Le remède reste celui d'en haut.

    ⚠️ **La carte : 68 000 → 69 000 octets gzip, le 28 sept. 2026, la nuit** — la cour à scrap de la gare
    (Martin : « je n'aime pas la partie avec les morceaux de train »). Mesure : 67 248 sur `dev`, 68 270 avec
    la cour — 287 piles de décor (+1 Ko ; les wagons partis ne rendaient presque rien, gzip avalait déjà leurs
    rangées répétées). Déjà UNE pile par trois tuiles au lieu d'une carcasse par tuile ; moins, la cour se vide.

    ⚠️ **Le brut des définitions : 270 000 → 275 000, le 28 sept. 2026, tard** — les statues des parcs
    (demande de Martin : « ajoute des statues dans les parcs »). Mesure : 269 100 bruts / 60 504 gzip sur
    `dev`, 270 194 / 61 038 avec les plaques qu'on lit à ACTION (`interactions.LIRE`, seize lignes : un
    accent voyage en échappement unicode, six octets). Le gzip, le vrai juge, reste sous son plafond ; le
    brut n'est qu'un indicateur, et il n'avait plus que 900 octets de marge.

    ⚠️ **La carte : 69 000 → 70 000 octets gzip, le 28 sept. 2026, tard** — les concessionnaires (Martin : « un
    vendeur de voitures neuves dans un quartier riche […] et un vendeur de voitures usagées »). Mesure : 68 399
    sur `dev` (601 octets de marge), 69 134 avec eux — le Salon et la cour de Ti-Pout au sol, leurs deux pièces,
    et leurs lots (seize places, leur stock et leurs prix). Brut : 711 965 → 715 042, sous ses 720 000. Même
    règle qu'au nord : le vrai juge est la dette des districts chargés autour du joueur.

    ⚠️ **La carte : 70 000 → 71 000 octets gzip, le 29 sept. 2026** — le lot de Prestige Automobiles retourné vers
    la rue et clôturé de fer forgé (Martin : « les véhicules doivent être en avant et clôturé »). Mesure : 69 967 sur
    `dev` (33 octets de marge, après le bus du Petit-Canton), 70 013 avec le lot — la clôture, son portail et ses
    heures (+46 gzip ; le brut, lui, BAISSE de 84 : les cases peintes sont parties). Même règle qu'au nord : le vrai
    juge est la dette des districts chargés autour du joueur.

    ⚠️ **Le brut de la carte : 720 000 → 722 000, le 29 sept. 2026** — les Mantes (l'école rivale, étape 4 du
    Petit-Canton). Mesure : 719 909 bruts / 70 116 gzip sur `dev` (91 octets de marge), 720 096 / 70 209 avec
    l'ÉCOLE LA MANTE (sa pièce reprise, son point) et le territoire du gang au bout des zones. Le gzip, le vrai
    juge, reste sous son plafond ; le brut n'est qu'un indicateur. Les définitions : +1 469 bruts / +280 gzip
    (l'archétype, sa garde-robe, `mantes.COMBAT`), 60 665 gzip, sous les 62 000.

    ⚠️ **Le brut des définitions : 275 000 → 280 000, le 29 sept. 2026** — le train (docs/jalons/le-train.md : « je
    veux un vrai train aérien, terrestre et tunnel »). Mesure : 274 852 bruts / 61 365 gzip sur `dev` (148 octets de
    marge), 275 321 / 61 442 avec ses trois sons au catalogue (le klaxon, la cloche du passage, le roulement) et leur
    lieu (`audio.LIEUX["train"]`). Le gzip, le vrai juge, reste sous son plafond ; le brut n'est qu'un indicateur.
    La carte ne bouge pas de plafond : 720 500 / 70 449 avec la clé `train`.

    ⚠️ **Les définitions : 62 000 → 64 000 gzip, le 29 sept. 2026, le soir** — l'ambiance du Petit-Canton et le défi
    des Mantes (docs/jalons/les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md). Mesure : 275 603 bruts / 61 557
    gzip sur `dev` (443 octets de marge), 278 071 / 62 234 avec eux — dont 2 604 bruts pour `amb_canton` (ses notes :
    le filet de toute musique, comme les six autres ambiances) et le reste pour `mantes.PROVOCATION` (huit répliques et
    ses garde-fous). Un cran franc de deux Ko ; le brut reste sous ses 280 000. La carte ne bouge pas.

    ⚠️ **Et le vieux maître, le même soir, sous le même plafond gzip** (l'arc c05 à c08, docs/jalons/l-ecole-rivale.md).
    Mesure : 278 071 bruts / 62 235 gzip sur `dev`, 280 599 / 62 874 avec lui — le catalogue de ses quatre missions (les cinquante octets
    gzip par mission d'en haut), le personnage et son repos (son premier, jamais dit, raccourci), son visage, sa tenue
    et la reprise de l'école (`mantes.REPRISE`). Le gzip, le vrai juge, reste sous ses 64 000 ; le brut, un
    indicateur, passe 280 000 → 285 000.

    ⚠️ **Les définitions : 64 000 → 66 000 gzip, 285 000 → 290 000 bruts, le 29 sept. 2026** — le chemin vers les
    quatre libérations de M16 (docs/jalons/m16-cent-missions.md). Mesure : 280 579 bruts / 62 857 gzip sur `dev`
    avant, 282 815 / 63 357 avec l'arc Q (trois missions, Cindy, le matelot, une manchette), **285 836 / 64 020**
    avec l'arc E (quatre missions, Diane et Jo, leurs visages, une manchette) — les 52,6 octets gzip par mission
    d'en haut, plus les personnages. Les arcs S et P (douze missions, six personnages) en demandent autant :
    deux Ko de plus, pas davantage. Ce qui en libérerait dix sans risque : les notes de `musique.py`
    (`audio.musiques`, 62 089 bruts / 10 302 gzip), qui peuvent venir avec leur district comme les mp3.
    Puis l'arc P (six missions, trois personnages, deux manchettes) : **290 969 / 65 061** — le brut passe ses
    290 000. Relevés à **300 000 / 67 000** d'un coup, pour l'arc S qui vient (six missions, trois personnages :
    ≈ 3 000 bruts et 1 000 gzip de plus) ; au-delà, c'est la musique qui sort, pas un plafond qui monte.

    ⚠️ **ET ELLE EST SORTIE, LE 29 SEPT. 2026 — LES PLAFONDS DESCENDENT : 300 000 → 256 000 bruts,
    67 000 → 59 000 gzip** (docs/jalons/le-paquet-des-definitions-maigrit.md). Mesure : **296 109 bruts /
    66 090 gzip** sur `dev`, **246 381 / 56 345** après deux sorties :
    - les NOTES de la musique (`/api/musiques`, `Son.Notes`) : 43 504 bruts / 8 783 gzip. Le morceau reste
      déclaré (slug, fichier, tempo) ; seules ses `voix` partent, sauf celles du thème du menu
      (`musique.NOTES_DANS_LE_PAQUET`), qui joue avant tout autre réseau. Elles sont demandées juste APRÈS
      les définitions, en arrière-plan, et la coquille du travailleur les garde : le filet tient hors ligne ;
    - ce que le navigateur ne lit pas d'un bruitage (nom, catégorie, `boucle`) : 6 224 bruts / 961 gzip.
      Et la durée de la sonnerie, que la cure du 28 sept. avait emportée alors que `Son.SFX.telephone()` la
      lit, revient seule (`audio.DUREES_LUES`).
    ⚠️ Ce que la sortie des notes n'achète pas, comme pour la carte : au premier chargement, le téléphone
    reçoit presque autant d'octets, en une requête de plus, APRÈS les définitions au lieu de dedans. Ce
    qu'elle achète : un `JSON.parse` plus petit avant le menu, des notes qui revalident en 304 quand un
    catalogue change, et DIX Ko de marge rendus aux missions. Les notes ont leur plafond à elles
    (43 775 bruts / 8 382 gzip à la mesure). Deux Ko et demi de marge gzip, pas plus : le prochain qui
    relève ce plafond regarde d'abord ce qui peut encore sortir (la fiche en nomme).

    ⚠️ **DEUXIÈME CURE, LE 30 SEPT. 2026 — LES PLAFONDS DESCENDENT ENCORE : 256 000 → 240 000 bruts,
    59 000 → 57 500 gzip** (docs/jalons/le-paquet-des-definitions-maigrit.md, « Fiche de la deuxième cure »).
    Un jour avait suffi à remanger la marge : **255 021 bruts / 58 992 gzip** sur `dev` (sept octets sous le
    plafond) — les saisons +1 275 gzip (lots 3 à 6), les photos du Clairon +697, Le Boss +542. Mesure après :
    **233 247 bruts / 53 017 gzip** (−21 774 / −5 975) :
    - LA SUITE DU PAQUET (`/api/suite`, `definitions.DANS_LA_SUITE`) : le Clairon (`journal*` et `photos`) et
      la hantise des Galeries, demandés juste après les définitions et gardés dans la coquille, comme les
      notes ; la manchette d'un jour qui se lève avant eux ATTEND (`Suite.quand`) : −4 444 gzip ;
    - ce qu'aucun script ne lisait : `types_plans`, `types_objectifs`, et la voix ElevenLabs de chaque
      personnage (`definitions.CHAMPS_HORS_DU_PAQUET`) : −971 ;
    - les voix du journal et des repos en SÉRIES (`audio.series_des_repos`), comme le 6/49 : −542.
    La suite a son plafond (10 562 bruts / 4 884 gzip à la mesure). 4 483 octets gzip de marge ; et le
    plafond qui cède NOMME maintenant les trois clés qui ont le plus grossi depuis `MESURE_DU_PAQUET` — le
    prochain qui déborde sait où couper, avant de relever quoi que ce soit.

    ⚠️ **LA CARTE PLIÉE, LE 30 SEPT. 2026 — SES PLAFONDS DESCENDENT : 722 000 → 560 000 bruts, 71 000 → 55 000
    gzip** (docs/jalons/charger-les-districts-autour-du-joueur.md, vague 1). Mesure : **720 915 bruts / 70 538
    gzip** sur `dev` (462 octets de marge, le plafond relevé onze fois en quinze jours), **539 632 / 52 129**
    une fois pliée (−181 283 / −18 409). Rien n'est sorti de la ville : ses longues listes d'objets de même forme
    (le décor, les lampes, les feux piétons, les toits…) voyagent EN COLONNES (`app/pliage.py`), et le navigateur
    la déplie en arrivant (`Pliage.deplier`, dans `Jeu.chargerDefinitions`), avant que quoi que ce soit la lise —
    la ville dépliée est celle d'avant à l'octet près (`test_pliage`). Le décor à lui seul : 13 871 → 7 054. Et
    la carte a maintenant SA garde par clé (`MESURE_DE_LA_CARTE`, `test_chaque_cle_de_la_carte_tient_son_budget`)
    : le plafond qui cède nomme les trois clés qui ont le plus grossi. Le vrai remède reste celui de la fiche —
    le squelette et les morceaux par district —, et son déclencheur est écrit dans « Dettes ».

    ⚠️ **240 000 → 241 000 BRUTS, LE MÊME JOUR, TRANCHÉ PAR MARTIN** (docs/jalons/des-corps-qui-tombent-pour-vrai.md).
    Le paquet était à 239 864 ; les bêtes qu'on écrase y ajoutent 233 octets (deux cris déclarés au lieu `betes`,
    `ecrasable` et `ecrase_rayon_px` dans la fiche). Regardé avant : fondre les deux cris en un seul rentrait sous le
    plafond, mais le chat et le raton auraient crié pareil — Martin a préféré relever. Le plafond gzip ne bouge pas.

    ⚠️ **LES VOIX DU CLAIRON PASSENT DANS LA SUITE, LE 30 SEPT. 2026 — SON PLAFOND MONTE : 13 000 → 19 500 bruts,
    6 000 → 8 500 gzip** (docs/jalons/le-clairon-a-plus-a-dire-des-manchettes-des-matins-et-des-lecons-de-plus.md).
    `dev` débordait déjà (240 119 bruts) et dix-neuf manchettes de plus le poussaient à 240 169 : les séries du
    journal, du 6/49, de Louise et des Galeries (`voix_de_la_suite`) suivent leurs textes, qui voyagent déjà dans
    la suite. Mesure : définitions 240 119 → **238 387** bruts, 54 290 → **53 744** gzip ; suite 10 562 → **17 635**
    bruts, 4 884 → **7 455** gzip. La suite arrive APRÈS l'écran titre, en arrière-plan : c'est là que le poids
    ne se sent pas.

    ⚠️ **LES KLAXONS DE TI-GUY PASSENT DANS LA SUITE, LE 30 SEPT. 2026 — SON PLAFOND BRUT MONTE : 19 500 → 21 000**
    (docs/jalons/les-klaxons-de-ti-guy.md). Dans les définitions, ils poussaient le paquet à 242 075 bruts (le
    plafond de Martin est 241 000) : ils sont partis dans la suite (`klaxons`, 1 777 octets bruts : six klaxons,
    trois airs de 532 octets, le texte de chaque commentaire de Ti-Guy). Le même jour, la file de la foire y a
    posé ses répliques (`repliques_de_la_file`) : la suite passait à 20 352. Regardé avant : `replique` ne s'écrit
    plus que s'il diffère du slug ; couper encore 852 octets, c'était retirer un klaxon ou les textes. Le plafond
    gzip (8 500) ne bouge pas.

    ⚠️ **241 000 → 242 000 BRUTS, LE 30 SEPT. 2026 AU SOIR, TRANCHÉ PAR MARTIN** (docs/jalons/la-patinoire-du-parc-deuxieme-vague.md).
    Les foyers de l'hiver avaient mené `dev` à 241 290 ; la patinoire y ajoute 278 octets (sa rumeur, sa valse et son
    lieu dans le catalogue audio) : 241 568. Proposé à Martin : relever, ou faire maigrir — il a relevé.

    ⚠️ **LA PATINOIRE DU PARC, LE MÊME JOUR — 21 000 → 23 000 bruts, 8 500 → 9 500 gzip**
    (docs/jalons/la-patinoire-du-parc.md). Sa fiche (couleurs, glisse, patineurs, patins et les mots de Madame
    Thibodeau, le son : 1 257 bruts, 726 gzip seule) n'est lue qu'en ville, l'hiver. Regardé avant : les
    définitions sont pleines (les klaxons en sont sortis pour ça), la carte a son plafond à elle. Mesure avec
    elle : suite 21 622 bruts, 8 998 gzip.

    ⚠️ **LES KLAXONS DE TI-GUY, DEUXIÈME VAGUE, LE MÊME JOUR — 23 000 → 25 000 bruts, 9 500 → 10 500 gzip, TRANCHÉ PAR
    MARTIN**
    (docs/jalons/les-klaxons-de-ti-guy-deuxieme-vague.md). Dix klaxons de plus (six airs, quatre bruitages) et
    le mot de Ti-Guy sur chacun : la clé `klaxons` passe de 1 777 à 3 541 octets bruts, la suite à 24 529 bruts et
    10 024 gzip.
    Regardé avant : les airs voyagent déjà serrés (« 440:1 392:1 », `garage.air_serre`) ; proposé à Martin —
    relever, retirer le texte des commentaires (la voix seule), ou charger les klaxons au garage : il a relevé.

    ⚠️ **DES ÉTAGES DEDANS AUSSI, LE 1er OCT. 2026 — LA CARTE : 560 000 → 562 000 BRUTS, TRANCHÉ PAR MARTIN**
    (docs/jalons/des-etages-dedans-aussi.md). `dev` était à 540 701 bruts / 51 045 gzip ; les pièces des étages
    (le logement au-dessus de 25 commerces, le troisième niveau de 8 triplex) y ajoutent 20 220 bruts —
    `interieurs` +19 389, `residences` +470, `devantures` +361 — : 560 921 / 52 614. Sur le fil, +1 569 gzip
    seulement : le plafond gzip (55 000) ne bouge pas. Proposé à Martin : relever, ou plier d'abord les pièces
    d'étages — il a relevé.

    ⚠️ **LES DÉFINITIONS : 242 000 → 255 000 BRUTS, LE 1er OCT. 2026, TRANCHÉ PAR MARTIN.** Mesure : 241 947
    bruts après le casse et les petites jobs (M16, vagues 15 à 19). Le brut n'est qu'un indicateur ; ce qui pèse
    sur le réseau, c'est le gzip, et lui garde son plafond (57 500) et sa garde par clé (`MESURE_DU_PAQUET`).
    Proposé à Martin : une cure 3 (plier les missions en colonnes, sortir les défis et les comptoirs) ou relever
    le brut — il a relevé.

    ⚠️ **LA LECTURE DES PASSANTS, LE 1er OCT. 2026 — LA SUITE : 25 000 → 29 000 BRUTS, 10 500 → 12 500 GZIP, TRANCHÉ
    PAR MARTIN** (docs/jalons/la-reputation-et-la-lecture-des-passants.md). Les 66 lignes de passants (`lectures`,
    3 641 bruts, 1 914 gzip seules) mènent la suite à 28 533 bruts et 11 844 gzip. Elle part après l'écran titre, en
    arrière-plan : le démarrage ne bouge pas. Proposé à Martin : relever, une requête à part, ou moins de lignes — il
    a relevé.

    ⚠️ **LES PANNEAUX DRÔLES, LE 2 OCT. 2026 — LA SUITE : 29 000 → 31 000 BRUTS, 12 500 → 13 000 GZIP, À VALIDER
    PAR MARTIN** (docs/jalons/le-decor-les-betes-et-les-gens-repondent.md). Quatorze panneaux à lire en ville
    (`panneaux.py`, leur place et leurs lignes : 1 397 bruts) mènent la suite à 30 264 bruts et 12 676 gzip. Ils
    ne servent qu'une fois dans la rue : la suite (après l'écran titre, en arrière-plan) est leur place, pas les
    définitions (le démarrage ne bouge pas) ni la carte (à cent octets gzip de son plafond). Les autres chemins :
    les mettre dans les définitions (sous leurs plafonds, mais lues avant l'écran titre), ou moins de panneaux.

    ⚠️ **LA CARTE : 562 000 → 600 000 BRUTS, 55 000 → 60 000 GZIP, LE 2 OCT. 2026, TRANCHÉ PAR MARTIN.** Mesure :
    561 155 bruts, 54 891 gzip (niveau 6), 52 821 sur le fil (niveau 9) — 109 octets de marge, après les panneaux
    drôles, le caddie et les bateaux d'hiver. Proposé à Martin : plier ce qui ne l'est pas encore, la vague 7 (le
    découpage par district, ~55 ms pour le plus gros risque) ou relever — il a relevé : la carte voyage déjà pliée
    et compressée au maximum, et le démarrage se joue sur les scripts (docs/jalons/charger-les-districts-autour-du-
    joueur.md). La garde par clé (`MESURE_DE_LA_CARTE`) reste : c'est elle qui dit qui grossit.

    ⚠️ **LES RAYONS DES COMPTOIRS, LE 3 OCT. 2026 — LA SUITE : 31 000 → 37 000 BRUTS, 13 000 → 15 500 GZIP, TRANCHÉ
    PAR MARTIN** (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md). Le rayon de chaque enseigne
    (24 comptoirs, 97 enseignes, 36 bouchées neuves) : 20 370 bruts tels quels, 6 201 compactés (`rayons.exporter`,
    2 140 gzip). Aucun plafond n'avait la marge ; les définitions d'avant l'écran titre étaient à 238 octets gzip du
    leur. Proposé à Martin : relever la suite, une requête à part, ou relever les définitions — il a relevé la
    suite : elle part après l'écran titre, et sans elle un comptoir sert celui de son genre.

    ⚠️ **LA VAGUE 2 DES COMPTOIRS, LE 6 OCT. 2026 — LA SUITE : 37 000 → 40 000 BRUTS, 15 500 → 16 500 GZIP, TRANCHÉ
    PAR MARTIN.** Les tenues et les armes (2a) ont tenu en compactant le format (8 128 → 7 220 octets : un nom par
    bouchée, plus de nom de rayon, plus les enseignes qui retombent d'elles-mêmes à leur famille) ; il restait 251
    octets, et les options du garage, les meubles et le neuf (2b à 2d) en demandent environ 2 000. Proposé à Martin :
    relever la suite, une requête à part pour les rayons — il a relevé : la suite part après l'écran titre.

    ⚠️ **LES SERVICES DES COMPTOIRS, LE 6 OCT. 2026 — LA SUITE : 40 000 → 44 000 BRUTS, 16 500 → 18 000 GZIP, TRANCHÉ
    PAR MARTIN.** La vague 3 (les services) a mangé la marge : 40 008 octets après avoir compacté les services (un nom
    seul quand il n'y a ni prix ni char) ; le photographe et les répliques des comptoirs en demandent environ 3 000 de
    plus. Proposé à Martin : relever, les rayons dans une requête à part, ou les répliques en voix — il a relevé.

    ⚠️ **LES RAYONS VOYAGENT SEULS, LE 6 OCT. 2026 (Martin).** Troisième débordement (44 397 / 44 000, les répliques des
    fournisseurs) : les rayons sortent de la suite (`/api/rayons`, `rayons_empreinte`) — la suite redescend à 30 630
    bruts, et les rayons ont leur propre plafond (13 799 bruts et 5 746 gzip à leur sortie ; la déco de la planque et
    les collections restent à venir).
    """
    for nom, brut_max, fil_max in (("definitions", 255_000, 57_500), ("carte", 600_000, 60_000),
                                   ("musiques", 50_000, 10_000), ("suite", 44_000, 18_000),
                                   ("rayons", 18_000, 7_500)):
        paquet = getattr(paquets, nom)
        mesures = {"definitions": MESURE_DU_PAQUET, "carte": MESURE_DE_LA_CARTE}
        qui = f" — qui a grossi : {_qui_a_grossi(paquet.corps, mesure=mesures[nom])}" if nom in mesures else ""
        assert paquet.taille < brut_max, f"{nom} : {paquet.taille} octets, le paquet enfle{qui}"
        sur_le_fil = len(gzip.compress(paquet.corps, 6))
        assert sur_le_fil < fil_max, f"{nom} : {sur_le_fil} octets gzip, le telephone va sentir passer{qui}"


def test_chaque_cle_du_paquet_tient_son_budget(paquets):
    """⚠️ La garde de la deuxième cure : QUI fait grossir le paquet se voit, clé par clé (`MESURE_DU_PAQUET`).
    Une clé qui dépasse son budget rougit en se nommant ; une clé neuve doit s'y écrire avec son poids. Relever
    un budget s'écrit à la ligne de la clé, avec pourquoi — après avoir regardé si elle peut sortir."""
    poids = _gzip_par_cle(paquets.definitions.corps)
    neuves = sorted(set(poids) - set(MESURE_DU_PAQUET))
    assert not neuves, ("clés neuves au paquet, sans poids écrit dans MESURE_DU_PAQUET : "
                        + ", ".join(f"{c} ({poids[c]} octets gzip)" for c in neuves)
                        + " — est-ce que le navigateur la lit avant l'écran titre ? Sinon, `DANS_LA_SUITE`")
    parties = sorted(set(MESURE_DU_PAQUET) - set(poids))
    assert not parties, f"clés sorties du paquet : {parties} — retire leur ligne de MESURE_DU_PAQUET"
    depassees = [f"{cle} : {poids[cle]} octets gzip pour un budget de {budget} (mesure {mesure}, +{poids[cle] - mesure})"
                 for cle, (mesure, budget) in MESURE_DU_PAQUET.items() if poids[cle] > budget]
    assert not depassees, ("des clés dépassent leur budget : " + " ; ".join(depassees)
                           + ". Avant de relever : ce qui peut sortir (voir MESURE_DU_PAQUET)")


def test_chaque_cle_de_la_carte_tient_son_budget(paquets):
    """La garde de la carte pliée (30 sept. 2026) : QUI fait grossir `/api/carte` se voit, clé par clé
    (`MESURE_DE_LA_CARTE`), comme pour les définitions. Une clé neuve de la carte doit s'y écrire avec son poids."""
    poids = _gzip_par_cle(paquets.carte.corps)
    neuves = sorted(set(poids) - set(MESURE_DE_LA_CARTE))
    assert not neuves, ("clés neuves à la carte, sans poids écrit dans MESURE_DE_LA_CARTE : "
                        + ", ".join(f"{c} ({poids[c]} octets gzip)" for c in neuves)
                        + " — un navigateur la lit-il avant JOUER ? Sinon, elle peut voyager à part")
    parties = sorted(set(MESURE_DE_LA_CARTE) - set(poids))
    assert not parties, f"clés sorties de la carte : {parties} — retire leur ligne de MESURE_DE_LA_CARTE"
    depassees = [f"{cle} : {poids[cle]} octets gzip pour un budget de {budget} (mesure {mesure}, +{poids[cle] - mesure})"
                 for cle, (mesure, budget) in MESURE_DE_LA_CARTE.items() if poids[cle] > budget]
    assert not depassees, "des clés de la carte dépassent leur budget : " + " ; ".join(depassees)


def test_la_suite_du_paquet_voyage_a_part(paquets):
    """Les clés de `DANS_LA_SUITE` ne sont plus dans les définitions ; elles sont dans la suite, entières, et les
    définitions nomment son empreinte — comme celle de la carte et des notes."""
    defs = json.loads(paquets.definitions.corps)
    suite = json.loads(paquets.suite.corps)
    complet = definitions.assembler()
    assert defs["suite_empreinte"] == suite["empreinte"] == paquets.suite.etag
    for cle in definitions.DANS_LA_SUITE:
        assert cle not in defs, f"« {cle} » voyage encore dans le paquet"
        assert suite[cle] == json.loads(json.dumps(complet[cle])), f"« {cle} » n'est pas arrivée entière"
    assert set(suite) == set(definitions.DANS_LA_SUITE) | {"empreinte"}, "la suite porte une clé qu'on n'a pas déclarée"
    assert all("voix" not in p for p in defs["personnages"]), "la voix ElevenLabs d'un personnage est revenue au paquet"


def test_l_empreinte_change_avec_le_contenu(monkeypatch):
    # ⚠️ Construit sous un `monkeypatch` du jeu : la fixture `paquets` ne le verrait pas.
    avant = definitions.construire()
    monkeypatch.setattr(definitions.economie, "ARGENT_DEPART", 51)
    apres = definitions.construire()
    assert apres.definitions.etag != avant.definitions.etag
    assert apres.carte.etag == avant.carte.etag, "un catalogue qui change ne doit pas faire retelecharger la ville"


def test_l_empreinte_des_definitions_suit_la_carte(monkeypatch):
    """⚠️ La sauvegarde oublie une position quand `empreinte` change
    (`Jeu.demarrer`). Depuis que la carte voyage a part, ce n'est vrai que parce
    que les definitions portent l'empreinte de leur carte : une ville redessinee
    sans qu'un seul catalogue bouge doit quand meme faire oublier la position."""
    from app import carte

    # ⚠️ Construit sous un `monkeypatch` du jeu : la fixture `paquets` ne le verrait pas.
    avant = definitions.construire()
    monkeypatch.setattr(carte, "GRAINE", carte.GRAINE + 1)
    # ⚠️ Trois défauts depuis le 27 sept. 2026 : `nord` (la bande nord, `app/nord.py`).
    monkeypatch.setattr(carte.generer, "__defaults__", (carte.PLAN, carte.GRAINE, True))
    apres = definitions.construire()
    assert apres.carte.etag != avant.carte.etag, "la carte n'a pas change : le juge ne mesure rien"
    assert apres.definitions.etag != avant.definitions.etag, "la carte a change et la sauvegarde ne le saura pas"


def test_le_paquet_contient_tout(paquet):
    """⚠️ `types_objectifs` n'y est plus (30 sept. 2026, la deuxième cure) : aucun script ne le lisait. Le
    contrat qu'il tenait — chaque objectif d'une mission est un type que le moteur connaît — se juge côté
    Python (`test_missions`), sur ce qui voyage vraiment : les objectifs de `/api/mission/<slug>`."""
    for cle in ("version", "empreinte", "tuile_px", "vehicules", "armes", "ordre_armes", "economie",
                "recherche", "carte", "missions", "defis", "magasins", "tenues"):
        assert cle in paquet, cle
    assert "types_objectifs" not in paquet and "types_plans" not in paquet
    assert json.dumps(paquet)  # serialisable


def test_les_objectifs_qui_voyagent_sont_des_types_connus(a_jouer):
    """Ce que `types_objectifs` promettait dans le paquet, jugé là où les objectifs voyagent : chaque objectif
    de chaque `/api/mission/<slug>` est d'un type de `missions.TYPES_OBJECTIFS`."""
    from app import missions
    vus = 0
    for slug, donnees in a_jouer.items():
        for o in donnees.get("objectifs") or []:
            assert o["type"] in missions.TYPES_OBJECTIFS, f"{slug} : objectif « {o['type']} » inconnu"
            vus += 1
    assert vus > 100, "le juge ne voit presque aucun objectif : il ne mesure rien"


def test_la_carte_voyage_a_part_et_se_reconnait(paquets):
    """Les definitions ne portent plus la carte, seulement son empreinte ; la
    carte porte la sienne, et c'est la meme. C'est ce que le navigateur verifie
    avant de les remettre ensemble."""
    defs = json.loads(paquets.definitions.corps)
    carte = json.loads(paquets.carte.corps)
    assert "carte" not in defs, "la carte est encore dans le paquet"
    assert defs["carte_empreinte"] == carte["empreinte"] == paquets.carte.etag
    assert defs["empreinte"] == paquets.definitions.etag
    assert carte["largeur"] > 0 and carte["sol"]


def test_les_notes_de_la_musique_voyagent_a_part(paquets):
    """⚠️ Les notes de `musique.py` — le FILET du sequenceur — sont sorties du paquet le
    29 sept. 2026 (`/api/musiques`). Le morceau reste DECLARE dans le paquet (slug, fichier,
    tempo : `Mus.def`, la radio et le jukebox le lisent tout de suite) ; seules ses `voix`
    partent — sauf celles du theme du menu, qui joue avant tout autre reseau."""
    from app import audio, musique

    defs = json.loads(paquets.definitions.corps)
    notes = json.loads(paquets.musiques.corps)
    assert defs["musiques_empreinte"] == notes["empreinte"] == paquets.musiques.etag
    completes = {m["slug"]: m for m in audio.exporter()["musiques"]}
    au_paquet = {m["slug"]: m for m in defs["audio"]["musiques"]}
    assert au_paquet.keys() == completes.keys(), "un morceau a disparu du paquet avec ses notes"
    assert musique.NOTES_DANS_LE_PAQUET <= au_paquet.keys()
    for slug, morceau in au_paquet.items():
        for cle in ("bpm", "pas", "nom", "fichier", "volume"):
            assert cle in morceau, f"{slug} : `{cle}` est parti avec les notes"
        if slug in musique.NOTES_DANS_LE_PAQUET:
            assert morceau["voix"] == completes[slug]["voix"], f"{slug} : le menu doit garder son filet"
            assert slug not in notes["musiques"]
        else:
            assert "voix" not in morceau, f"{slug} : ses notes voyagent encore dans le paquet"
            assert notes["musiques"][slug] == completes[slug]["voix"], f"{slug} : ses notes ne sont nulle part"


def test_des_notes_qui_changent_ne_font_pas_retelecharger_le_paquet(monkeypatch):
    """Une note corrigee change l'empreinte des notes, pas celle de la carte ; et les
    definitions, qui NOMMENT l'empreinte des notes, suivent — comme pour la carte."""
    from app import musique

    avant = definitions.construire()
    morceaux = [dict(m) for m in musique.MORCEAUX]
    ouv = next(m for m in morceaux if m["slug"] == "ouverture")
    ouv["voix"] = [dict(v) for v in ouv["voix"]]
    ouv["voix"][0]["volume"] = ouv["voix"][0]["volume"] + 0.01
    monkeypatch.setattr(musique, "MORCEAUX", morceaux)
    apres = definitions.construire()
    assert apres.musiques.etag != avant.musiques.etag
    assert apres.carte.etag == avant.carte.etag
