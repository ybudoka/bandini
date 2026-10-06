"""Le paquet de definitions et la carte — ce que le navigateur recoit, en DEUX requetes.

Construits UNE fois au demarrage : les catalogues ne changent pas sous un
processus lance. L'`etag` est une empreinte du contenu : un navigateur qui a
deja le paquet revalide gratuitement (304), et sa sauvegarde locale sait si le
catalogue a change depuis (un vehicule possede qui n'existe plus, par exemple).

⚠️ **LA CARTE SORT DU PAQUET** (16 sept. 2026, decision de Martin). Avec
L'Ile-aux-Corneilles, le paquet passait a 75,3 Ko gzip sur un plafond de 75 ;
la carte en faisait plus de la moitie, et `test_definitions` ecrivait d'avance
que c'est a ce plafond-la qu'on la sortirait plutot que de relever encore. Elle
part donc sur `/api/carte`, avec son propre ETag, et le navigateur la remet
dans `defs.carte` en arrivant : aucun lecteur de la carte ne change, et
`assembler()` rend toujours le tout, tel que le navigateur le tient.

⚠️ **CE QU'UNE MISSION DEMANDE POUR SE JOUER SORT DU PAQUET, AUSSI** (24 sept. 2026) —
et cette fois ce n'est pas une precaution, c'est une reparation : le paquet pesait
369 224 octets bruts pour un plafond de 250 000 et 75 138 gzip pour 54 000, et son
juge etait rouge. Le CATALOGUE reste (le carnet, le GPS et le telephone le lisent en
entier) ; ce qu'elle DIT, MONTRE, ses VOIX et ses OBJECTIFS partent sur
`/api/mission/<slug>`, une reponse par mission, avec son ETag — la meme route et le
meme instant que ses mp3 (`Son.Voix.chargerHistoire`). Mesure : 369 224 a **220 367**
octets bruts, 75 138 a **48 971** gzip. Voir `missions.HORS_DU_PAQUET`.

⚠️ **LES NOTES DE LA MUSIQUE SORTENT DU PAQUET** (29 sept. 2026) — le plafond gzip avait
ete releve cinq fois en quatre jours. Les partitions de `musique.py` (le FILET : ce que le
sequenceur joue quand un mp3 manque) partent sur `/api/musiques`, une reponse pour toutes,
avec son ETag ; le navigateur la demande juste apres les definitions, en arriere-plan, et la
coquille du travailleur la garde (le filet tient hors ligne). Ce qui reste : tout ce qui
DECRIT un morceau (slug, nom, fichier, tempo — `Mus.def`, le jukebox et la radio le lisent
tout de suite), et les notes du theme du menu (`musique.NOTES_DANS_LE_PAQUET`), qui joue
avant tout autre reseau. Comme la carte, `assembler()` rend le tout, notes comprises.

⚠️ **LA SUITE DU PAQUET** (30 sept. 2026, la deuxieme cure) — sept octets de marge sous le plafond,
un jour apres la premiere. Le Clairon (manchettes, lecons, matins, la photo de Louise) et la hantise
des Galeries partent sur `/api/suite` (`DANS_LA_SUITE`), qui arrive comme les notes : juste apres,
en arriere-plan, garde hors ligne. Et trois choses que le navigateur ne lisait pas s'en vont pour de
bon : le vocabulaire des scenes et des objectifs (`types_plans`, `types_objectifs`), et la voix
ElevenLabs de chaque personnage (`CHAMPS_HORS_DU_PAQUET`). Les voix du journal et des repos
voyagent en series (`audio.series_des_repos`). Mesure : 255 021 → 233 247 octets bruts, 58 992 →
53 017 gzip. ⚠️ Et `test_chaque_cle_du_paquet_tient_son_budget` nomme QUI grossit, cle par cle.

⚠️ **Les definitions portent l'empreinte de la carte** (`carte_empreinte`), et
c'est ce qui garde la sauvegarde honnete : elle oublie une position quand
`empreinte` change, et `empreinte` change donc des que la CARTE change — meme
si pas un catalogue n'a bouge. C'est aussi ce qui dit au navigateur que les
deux reponses vont ensemble.
"""

from __future__ import annotations

import functools
import gzip
import hashlib
import json
from dataclasses import dataclass

from . import (armes, audio, patinoire, blocs, calendrier, saisons, pluie, halloween, carte, demenagement, derby, enseignes, fetes, garage, motoneige, photos, quatre_roues, saint_jean, territoires, devantures, dojo, economie, mantes, garderobe, interactions, journal, magasins,
               brouillard, loto, machine_a_sous, manettes, tables_de_jeu, missions, nord, nuit, pietons, recherche, rixes, techniques, vehicules, verglas, videopoker,
               musique, pont_de_glace, visages)
from . import collectionner, decoration, foyers, lectures, panneaux, pliage, rayons
from .blocs import galeries as galeries_hantees
from .version import VERSION

#: ⚠️ **LA SUITE DU PAQUET** (30 sept. 2026, la deuxième cure) : ce que le navigateur ne lit jamais
#: avant d'avoir quitté l'écran titre voyage sur `/api/suite`, demandé juste APRÈS les définitions, en
#: arrière-plan, et gardé par la coquille du travailleur (hors ligne, il est là) — le même chemin que les
#: notes de la musique. Il revient dans `B.defs` à son arrivée (`Suite.poser`), sous les mêmes clés :
#: aucun lecteur ne sait d'où il vient. Ce qui s'en sert attend qu'il soit là (`Suite.quand`) ou se
#: tait sans lui (`B.defs.x || …`) — jamais une exception dans `maj()`.
#:
#: Une clé n'entre ici qu'avec sa preuve (`tests/test_suite_js.py`) :
#: - le **Clairon** (`journal*`, les manchettes, les leçons, les matins calmes, et la photo de Louise) : il
#:   ne parle qu'au lever du jour ou quand on achète le journal ou vend une photo — et si le jour se lève
#:   avant l'arrivée de la suite, la manchette l'ATTEND au lieu de se perdre (`Missions.nouveauJour`) ;
#: - les **Galeries hantées** (`galeries`) : on n'y entre que par leur bloc, la nuit, et `Galeries.maj`
#:   se tait sans elles ;
#: - leurs **voix** (`voix_de_la_suite`, `audio.series_de_la_suite`) : le journal, le 6/49, Louise et les
#:   Galeries ne disent que ces textes-là. `Son.Voix.histoire()` les déplie à l'arrivée, et une banque encore
#:   vide ne se marque pas chargée tant que la suite n'est pas là (`Son.Voix.chargerHistoire`) ;
#: - la **lecture des passants** (`lectures`) : on ne lit qu'en jeu, un bouton tenu, et `Lecture` se tait
#:   sans elle (`test_lectures_js`).
DANS_LA_SUITE: tuple[str, ...] = ("journal", "journal_speciales", "journal_lecons", "journal_matins",
                                  "photos", "galeries", "voix_de_la_suite",
                                  "repliques_de_la_file", "klaxons", "patinoire", "lectures",
                                  "panneaux")

#: Ce qu'une fiche de personnage porte et qu'aucun script ne lit : sa voix ElevenLabs (le nom de la voix,
#: `audio.voix_*` la lit en Python pour générer ses mp3). 1 698 octets bruts / 658 gzip sur le paquet.
CHAMPS_HORS_DU_PAQUET: frozenset[str] = frozenset({"voix"})


def assembler() -> dict:
    # ⚠️ Les frontieres de gangs tiennent des DEUX fiches et d'aucune seule :
    # les rectangles de districts viennent de `carte`, qui ne sait pas qui tient
    # quoi ; les gangs viennent de `pietons`, qui ne sait pas ou sont les
    # rectangles. On les marie ICI, une fois, et le navigateur lit le resultat
    # au lieu de le recalculer — « une fiche que le navigateur ne lisait pas »
    # a son symetrique, « un calcul que Python ne pouvait pas juger ».
    ville = carte.exporter()
    gens = pietons.exporter()
    gens["frontieres"] = pietons.frontieres(ville)
    # Les territoires des gangs : les îlots de chaque district, et le cœur de chaque gang (`territoires.py`).
    gens["territoires"] = territoires.pour_le_navigateur()
    return {
        "version": VERSION,
        "tuile_px": carte.TUILE_PX,
        "audio": audio.exporter(),
        # Les voix du Clairon et des Galeries, en séries, avec leurs textes dans la suite (`DANS_LA_SUITE`).
        "voix_de_la_suite": audio.series_de_la_suite(),
        # Les klaxons de Ti-Guy (docs/jalons/les-klaxons-de-ti-guy.md), dans la suite (`DANS_LA_SUITE`).
        "klaxons": garage.exporter_klaxons(),
        "vehicules": vehicules.CATALOGUE,
        "conduite": vehicules.exporter_conduite(),
        "armes": armes.CATALOGUE,
        "ordre_armes": armes.ORDRE_CYCLE,
        "armes_regles": armes.REGLES,
        # Les coups de rue et les cours du dojo (docs/jalons/les-techniques-d-arts-martiaux.md).
        "techniques": techniques.CATALOGUE,
        # Le DOJO DION : les regles de la lecon et ce que Mireille dit (docs/jalons/le-dojo-du-quartier.md).
        "dojo": dojo.exporter(),
        # Les MANTES, le gang de l'école rivale du Petit-Canton : leur façon de se battre (docs/jalons/l-ecole-rivale.md).
        "mantes": mantes.exporter(),
        # Les bagarres de gangs vivantes : le cerveau du contact (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).
        "rixes": rixes.exporter(),
        "economie": economie.exporter(),
        # La machine du fond du bar (docs/jalons/le-videopoker-du-brouillard.md).
        "videopoker": videopoker.pour_le_navigateur(),
        # La machine à sous du casino du Dragon d'or (docs/jalons/le-casino-du-petit-canton.md).
        "machine_a_sous": machine_a_sous.pour_le_navigateur(),
        # Les tables du Dragon d'or : blackjack, roulette, poker, sic bo, baccara (même fiche, vague 2).
        "tables_de_jeu": tables_de_jeu.pour_le_navigateur(),
        # Les matins de brouillard (docs/jalons/le-brouillard-de-baie-des-brumes.md).
        "brouillard": brouillard.pour_le_navigateur(),
        # Trois jours de glace (docs/jalons/la-tempete-de-verglas.md).
        "verglas": verglas.pour_le_navigateur(),
        # L'année du jeu : quarante jours, douze mois, quatre saisons (`calendrier.py`).
        "calendrier": calendrier.pour_le_navigateur(),
        # Les saisons : la palette de la ville et la longueur du jour (`saisons.py`).
        "saisons": saisons.pour_le_navigateur(),
        # La pluie : les averses, les orages, les flaques, la gadoue et les feuilles (`pluie.py`).
        "pluie": pluie.pour_le_navigateur(),
        # L'Halloween : les citrouilles, les lumières, les déguisés, la maison hantée (`halloween.py`).
        "halloween": halloween.pour_le_navigateur(),
        # La patinoire du parc : ses couleurs, la glisse et la chute (`patinoire.py`) ; sa place est dans la carte.
        "patinoire": patinoire.pour_le_navigateur(),
        # La course des bois de La Pointe, lue sur la ville finie (docs/jalons/la-motoneige.md).
        "motoneige": motoneige.pour_le_navigateur(ville),
        # La course des Friches, en 4 roues, lue sur la ville finie (docs/jalons/les-4-roues.md).
        "quatre_roues": quatre_roues.pour_le_navigateur(ville),
        # Le soir du 24 juin : la rue du défilé, les feux (docs/jalons/la-saint-jean-sur-la-baie.md).
        "saint_jean": saint_jean.pour_le_navigateur(ville),
        # Décembre : les guirlandes, le sapin, les dindes (docs/jalons/le-temps-des-fetes.md).
        "fetes": fetes.pour_le_navigateur(ville),
        # La nuit aux Galeries de la Baie : la hantise et ce que dit le haut-parleur (docs/jalons/le-centre-d-achat-hante.md).
        "galeries": galeries_hantees.pour_le_navigateur(),
        # Ce que chiale la file de la foire quand on lui passe devant (docs/jalons/une-file-pour-entrer-a-la-foire.md) :
        # dans la SUITE, le paquet est a son plafond.
        "repliques_de_la_file": audio.voix_de_la_file(),
        # Le bingo, le Rialto, les quilles et le lave-auto (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md).
        "enseignes": enseignes.pour_le_navigateur(ville),
        # Le 1er juillet : les camions et les meubles du trottoir (docs/jalons/le-1er-juillet-jour-du-demenagement.md).
        "demenagement": demenagement.pour_le_navigateur(ville, carte.LEGENDE),
        # Les pièces que Ti-Guy pose sur un char (docs/jalons/le-garage-qui-modifie-les-chars.md).
        "garage": garage.exporter(),
        # Louise achète une photo par jour, et la une du lendemain l'affiche (docs/jalons/des-photos-pour-le-clairon.md).
        "photos": photos.pour_le_navigateur(),
        # Le chemin sur la baie gelée, lu sur la ville finie (docs/jalons/le-pont-de-glace.md).
        "pont": pont_de_glace.pour_le_navigateur(ville, carte.LEGENDE),
        # L'arène du derby, lue sur la ville finie (docs/jalons/le-derby-de-demolition-a-la-foire.md).
        "derby": derby.pour_le_navigateur(ville),
        # Le billet de Ti-Paul, et le tirage de la nuit (docs/jalons/le-6-49-du-depanneur.md).
        "loto": loto.pour_le_navigateur(),
        "recherche": recherche.exporter(),
        "pietons": gens,
        "manettes": manettes.exporter(),
        "devantures": devantures.exporter(),
        # Les panneaux drôles de la rue, à leur place sur la ville finie (`panneaux.py`) : dans la SUITE.
        "panneaux": panneaux.pour_le_navigateur(ville),
        # Les gestes du décor et de la rue : ACTION devant un banc, une poubelle, un artiste.
        "interactions": interactions.exporter(),
        # Ce que la nuit change (« la nuit a ses habitudes ») : les fenêtres qui
        # s'éteignent, les lampadaires qui grésillent, le last call, le camelot…
        "nuit": nuit.exporter(ville),
        "carte": ville,
        "missions": missions.pour_le_navigateur(),
        # Les PETITES JOBS, pliées (`missions.jobs_pour_le_navigateur`) : `Jobs.deplier` les remet dans `missions`.
        "jobs": missions.jobs_pour_le_navigateur(),
        # Les blocs de carte : leur passage en ville, et rien d'autre — leur carte voyage
        # à part, à la demande (`/api/carte/bloc/<slug>`).
        "blocs": blocs.pour_le_navigateur(),
        # Ce qui ouvre une serrure de bloc (la clé de la villa), et les missions qui le mettent au sac : une
        # partie qui l'a perdue le retrouve au chargement (`Sauvegarde.completer`).
        "cles_des_serrures": missions.cles_des_serrures(blocs.BLOCS),
        # La ville a descendu de tant de rangées (docs/jalons/la-ville-s-agrandit-au-nord.md) : une partie
        # écrite avant descend avec elle (`Sauvegarde.completer`).
        "decalage_nord": nord.DECALAGE_NORD,
        "defis": missions.DEFIS,
        # ⚠️ Sans la VOIX ElevenLabs de chacun (`CHAMPS_HORS_DU_PAQUET`) : elle ne sert qu'à générer ses mp3.
        # Et les deux rôles des petites jobs sans leurs couleurs : le passant qui t'interpelle porte la tenue de SON
        # archétype (`jobs.js`), jamais celles-là.
        "personnages": [{k: v for k, v in p.items() if k not in CHAMPS_HORS_DU_PAQUET
                         and not (k == "couleurs" and p["slug"] in missions.DONNEURS_PASSANTS)}
                        for p in missions.PERSONNAGES],
        # Le portrait de qui parle, à gauche de la boîte de dialogue (`visages.js`).
        "visages": visages.pour_le_navigateur(),
        # Les squelettes qu'on habille : les garde-robes des passants, la tenue des personnages.
        "garderobe": garderobe.exporter(),
        # Les quatre phrases de l'ouverture, avec leur slug de voix : le
        # navigateur les lit, il ne refait pas la regle du slug.
        "ouverture": missions.repliques_ouverture(),
        # Les scènes, en plans (voir `missions.TYPES_PLANS`) : `scenes.js` les joue
        # sans en connaître aucune par son nom. ⚠️ Le vocabulaire lui-même (`TYPES_PLANS`,
        # `TYPES_OBJECTIFS`) n'y voyage plus depuis le 30 sept. 2026 : aucun script ne le lisait,
        # et `test_mise_en_scene` juge l'accord des deux bouts sur le code de `scenes.js`.
        "scenes": {"ouverture": missions.SCENE_OUVERTURE},
        "repos": missions.REPOS,
        "journal": journal.REGLES,
        # La lecture des passants (`lectures.py`) : une ligne par passant, au bouton tenu, dans la suite.
        "lectures": lectures.exporter(),
        "journal_speciales": journal.SPECIALES,
        "journal_lecons": journal.LECONS,
        # Les matins calmes : les replis qui VARIENT quand rien n'est passe. Le
        # narrateur les lit comme une manchette, tires sans redire le precedent.
        "journal_matins": journal.MATINS,
        "marche_noir": magasins.MARCHE_NOIR,
        "magasins": magasins.CATALOGUE,
        "ambulants": magasins.AMBULANTS,
        "foyers": foyers.FOYERS,
        "reclame": magasins.RECLAME,
        "comptoirs": magasins.COMPTOIRS,
        # Le rayon de chaque enseigne (`rayons.py`) : ce que son comptoir vend, lu par son nom — dans la suite
        # (`DANS_LA_SUITE`) : rien ne l'achète avant l'écran titre, et sans lui un comptoir sert celui de son genre.
        "rayons": rayons.exporter(),
        "distributrices": magasins.DISTRIBUTRICES,
        "tenues": magasins.TENUES,
        "coiffures": magasins.COIFFURES,
    }


def empreinte(corps: bytes) -> str:
    return hashlib.sha256(corps).hexdigest()[:16]


@dataclass(frozen=True)
class Paquet:
    corps: bytes
    etag: str

    @property
    def taille(self) -> int:
        return len(self.corps)

    @functools.cached_property
    def fil(self) -> bytes:
        """Le corps compressé UNE fois, au plus fort (gzip 9), tel qu'il part sur le fil (`routes._revalide`).

        ⚠️ **NGINX COMPRESSE AU NIVEAU 1** (30 sept. 2026, docs/jalons/charger-les-districts-autour-du-joueur.md,
        vague 2) : `deploy/nginx` ne dit aucun `gzip_comp_level`, et son défaut est 1. Les juges de poids
        comptaient le niveau 6 ; le téléphone recevait la carte à 98 Ko quand ils en voyaient 70. Un paquet ne
        change pas sous un processus lancé : on le compresse au plus fort, une fois, à la première demande — et
        nginx comme Caddy laissent passer une réponse déjà encodée. `mtime=0` : les mêmes octets à chaque
        construction.
        ⚠️ `cached_property` sur une classe gelée : elle écrit dans `__dict__` sans passer par `__setattr__`."""
        return gzip.compress(self.corps, 9, mtime=0)


@dataclass(frozen=True)
class Paquets:
    """Les reponses : les definitions (`/api/definitions`), la carte (`/api/carte`), et
    une mission par mission (`/api/mission/<slug>`)."""

    definitions: Paquet
    carte: Paquet
    #: slug de mission -> tout ce qu'elle demande pour se jouer (`missions.pour_jouer`).
    #: ⚠️ Construits ici, une fois, comme les deux autres : une mission ne change pas
    #: sous un processus lance.
    a_jouer: dict[str, Paquet]
    #: UNE empreinte pour les trente-six, celle que le paquet nomme et que l'adresse
    #: porte (`?e=`) : la clef du cache hors ligne.
    missions_empreinte: str
    #: slug de bloc -> sa carte (`blocs.carte_du_bloc`), servie par `/api/carte/bloc/<slug>`.
    #: ⚠️ Hors de `/api/carte` : un bloc de plus ne change pas un octet de la ville.
    blocs: dict[str, Paquet]
    blocs_empreinte: str
    #: Les notes des morceaux (`/api/musiques`) : slug -> ses `voix`, sauf celles qui
    #: restent au paquet (`musique.NOTES_DANS_LE_PAQUET`). Les definitions nomment son
    #: empreinte (`musiques_empreinte`), comme celle de la carte.
    musiques: Paquet
    #: Les collections (`/api/collections`) : le catalogue des cartes de hockey et leurs places dans la ville
    #: (`collectionner`). ⚠️ Hors des définitions ET de la carte : les deux sont au ras de leur plafond. Les
    #: définitions nomment son empreinte (`collections_empreinte`), comme celle des notes.
    collections: Paquet
    #: La suite du paquet (`/api/suite`) : les clés de `DANS_LA_SUITE`, que le navigateur remet dans `B.defs`.
    #: Les définitions nomment son empreinte (`suite_empreinte`), comme celle des notes.
    suite: Paquet
    #: Les rayons des comptoirs (`/api/rayons`, `rayons.exporter`) : sortis de la suite le 6 oct. 2026. Les
    #: définitions nomment son empreinte (`rayons_empreinte`).
    rayons: Paquet


def _json(donnees: dict) -> bytes:
    return json.dumps(donnees, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _signer(donnees: dict) -> Paquet:
    """Pose `empreinte` dans les donnees et rend le paquet.

    Sans l'empreinte d'abord : elle depend du reste, on l'ajoute apres."""
    etag = empreinte(_json(donnees))
    donnees["empreinte"] = etag
    return Paquet(corps=_json(donnees), etag=etag)


def sortir_les_notes(audio_du_paquet: dict) -> dict:
    """Retire du paquet les notes des morceaux (le filet du sequenceur) et les rend.

    ⚠️ Seules les `voix` partent : le morceau reste declare (slug, nom, fichier, tempo,
    volume), et le navigateur les lui remet a l'arrivee (`Son.Notes`)."""
    notes = {}
    for morceau in audio_du_paquet["musiques"]:
        if morceau["slug"] not in musique.NOTES_DANS_LE_PAQUET:
            notes[morceau["slug"]] = morceau.pop("voix")
    return {"musiques": notes}


def construire() -> Paquets:
    donnees = assembler()
    # ⚠️ UNE SEULE ville generee pour les deux : `generer` coute une seconde et
    # demie, et deux villes batties separement pourraient ne pas etre la meme.
    ville = donnees.pop("carte")
    # ⚠️ Les places des cartes de hockey sortent de la carte AVANT qu'on la signe : elles voyagent avec leur
    # catalogue sur `/api/collections` (`collectionner.exporter`), pas un octet de plus sur `/api/carte`.
    # ⚠️ Et la planque qu'on décore (`decoration`) : ses trophées, son catalogue et leurs places, avec elles.
    a_part = collectionner.exporter(ville.pop("collections", None), audio.echantillons_a_part("collections"))
    a_part["planque"] = decoration.exporter()
    collections = _signer(a_part)
    donnees["collections_empreinte"] = collections.etag
    # ⚠️ LA CARTE VOYAGE PLIÉE (30 sept. 2026, `pliage`) : la même ville, en colonnes — 70 538 → 52 130 octets
    # gzip. Le navigateur la déplie en arrivant (`Pliage.deplier`), avant que quoi que ce soit la lise.
    carte = _signer(pliage.plier(ville))
    donnees["carte_empreinte"] = carte.etag
    musiques = _signer(sortir_les_notes(donnees["audio"]))
    donnees["musiques_empreinte"] = musiques.etag
    suite = _signer({cle: donnees.pop(cle) for cle in DANS_LA_SUITE})
    donnees["suite_empreinte"] = suite.etag
    # ⚠️ LES RAYONS DES COMPTOIRS VOYAGENT SEULS (`/api/rayons`, Martin, 6 oct. 2026) : ils ont fait déborder la
    # suite trois fois (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md). Demandés après elle, en
    # arrière-plan, gardés par la coquille ; sans eux, un comptoir sert celui de son genre.
    rayons = _signer({"rayons": donnees.pop("rayons")})
    donnees["rayons_empreinte"] = rayons.etag
    # Un paquet par mission, signe comme les autres.
    a_jouer = {m["slug"]: _signer(missions.pour_jouer(m["slug"])) for m in missions.CATALOGUE}
    # ⚠️ UNE empreinte pour les trente-six, posee dans l'adresse (`?e=`) comme celles
    # des deux autres paquets : c'est ce qui empeche une page gardee hors ligne de
    # servir la mission d'un AUTRE deploiement sous un catalogue qui ne la connait
    # pas. Une seule, et pas trente-six dans le paquet : elles sont baties ensemble, du
    # meme catalogue, et un seul mot qui change les renomme toutes — ce qui coute, en
    # ligne, trente-six 304 gratuits.
    des_missions = empreinte(_json({slug: paquet.etag for slug, paquet in sorted(a_jouer.items())}))
    donnees["missions_empreinte"] = des_missions
    # Les blocs de carte, une carte par bloc — même règle que les missions : signés ici,
    # une empreinte pour tous dans l'adresse (`?e=`).
    des_cartes = {b["slug"]: _signer(blocs.carte_du_bloc(b)) for b in blocs.BLOCS + blocs.SOUS_SOLS}
    des_blocs = empreinte(_json({slug: paquet.etag for slug, paquet in sorted(des_cartes.items())}))
    donnees["blocs_empreinte"] = des_blocs
    return Paquets(definitions=_signer(donnees), carte=carte, a_jouer=a_jouer,
                   missions_empreinte=des_missions, blocs=des_cartes, blocs_empreinte=des_blocs,
                   musiques=musiques, collections=collections, suite=suite, rayons=rayons)
