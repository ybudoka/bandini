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

⚠️ **Les definitions portent l'empreinte de la carte** (`carte_empreinte`), et
c'est ce qui garde la sauvegarde honnete : elle oublie une position quand
`empreinte` change, et `empreinte` change donc des que la CARTE change — meme
si pas un catalogue n'a bouge. C'est aussi ce qui dit au navigateur que les
deux reponses vont ensemble.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import (armes, audio, blocs, carte, devantures, economie, garderobe, interactions, journal, magasins,
               manettes, missions, nuit, pietons, recherche, techniques, vehicules, visages)
from .version import VERSION


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
    return {
        "version": VERSION,
        "tuile_px": carte.TUILE_PX,
        "audio": audio.exporter(),
        "vehicules": vehicules.CATALOGUE,
        "conduite": vehicules.exporter_conduite(),
        "armes": armes.CATALOGUE,
        "ordre_armes": armes.ORDRE_CYCLE,
        "armes_regles": armes.REGLES,
        # Les coups de rue et les cours du dojo (docs/jalons/les-techniques-d-arts-martiaux.md).
        "techniques": techniques.CATALOGUE,
        "economie": economie.exporter(),
        "recherche": recherche.exporter(),
        "pietons": gens,
        "manettes": manettes.exporter(),
        "devantures": devantures.exporter(),
        # Les gestes du décor et de la rue : ACTION devant un banc, une poubelle, un artiste.
        "interactions": interactions.exporter(),
        # Ce que la nuit change (« la nuit a ses habitudes ») : les fenêtres qui
        # s'éteignent, les lampadaires qui grésillent, le last call, le camelot…
        "nuit": nuit.exporter(ville),
        "carte": ville,
        "missions": missions.pour_le_navigateur(),
        # Les blocs de carte : leur passage en ville, et rien d'autre — leur carte voyage
        # à part, à la demande (`/api/carte/bloc/<slug>`).
        "blocs": blocs.pour_le_navigateur(),
        "defis": missions.DEFIS,
        "personnages": missions.PERSONNAGES,
        # Le portrait de qui parle, à gauche de la boîte de dialogue (`visages.js`).
        "visages": visages.pour_le_navigateur(),
        # Les squelettes qu'on habille : les garde-robes des passants, la tenue des personnages.
        "garderobe": garderobe.exporter(),
        # Les quatre phrases de l'ouverture, avec leur slug de voix : le
        # navigateur les lit, il ne refait pas la regle du slug.
        "ouverture": missions.repliques_ouverture(),
        # Les scènes, en plans (voir `missions.TYPES_PLANS`) : `scenes.js` les joue
        # sans en connaître aucune par son nom.
        "scenes": {"ouverture": missions.SCENE_OUVERTURE},
        "repos": missions.REPOS,
        "types_plans": {genre: list(cles) for genre, cles in missions.TYPES_PLANS.items()},
        "types_objectifs": list(missions.TYPES_OBJECTIFS),
        "journal": journal.REGLES,
        "journal_speciales": journal.SPECIALES,
        "journal_lecons": journal.LECONS,
        # Les matins calmes : les replis qui VARIENT quand rien n'est passe. Le
        # narrateur les lit comme une manchette, tires sans redire le precedent.
        "journal_matins": journal.MATINS,
        "marche_noir": magasins.MARCHE_NOIR,
        "magasins": magasins.CATALOGUE,
        "ambulants": magasins.AMBULANTS,
        "reclame": magasins.RECLAME,
        "comptoirs": magasins.COMPTOIRS,
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


def _json(donnees: dict) -> bytes:
    return json.dumps(donnees, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _signer(donnees: dict) -> Paquet:
    """Pose `empreinte` dans les donnees et rend le paquet.

    Sans l'empreinte d'abord : elle depend du reste, on l'ajoute apres."""
    etag = empreinte(_json(donnees))
    donnees["empreinte"] = etag
    return Paquet(corps=_json(donnees), etag=etag)


def construire() -> Paquets:
    donnees = assembler()
    # ⚠️ UNE SEULE ville generee pour les deux : `generer` coute une seconde et
    # demie, et deux villes batties separement pourraient ne pas etre la meme.
    carte = _signer(donnees.pop("carte"))
    donnees["carte_empreinte"] = carte.etag
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
    des_cartes = {b["slug"]: _signer(blocs.carte_du_bloc(b)) for b in blocs.BLOCS}
    des_blocs = empreinte(_json({slug: paquet.etag for slug, paquet in sorted(des_cartes.items())}))
    donnees["blocs_empreinte"] = des_blocs
    return Paquets(definitions=_signer(donnees), carte=carte, a_jouer=a_jouer,
                   missions_empreinte=des_missions, blocs=des_cartes, blocs_empreinte=des_blocs)
