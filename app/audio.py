"""Les sons de Baie-des-Brumes — le catalogue, pas les octets.

Bandini a commence tout synthetise (oscillateurs et bruit blanc, dans
`son.js`). Depuis le 12 septembre 2026, les sons importants sont de VRAIS
echantillons, generes une fois par ElevenLabs (serveur MCP `elevenlabs`) et
versionnes dans `static/audio/`. Le module decrit **ce qu'on veut entendre** ;
`scripts/audio_elevenlabs.py` va le chercher.

Trois regles, dans cet ordre :

1. **Le jeu marche sans les fichiers.** `exporter()` ne declare que les
   fichiers REELLEMENT presents sur le disque ; le navigateur retombe sur la
   synthese pour tout le reste. Un depot frais, une generation ratee, une
   coupure de reseau : le son sort quand meme.
2. **La recette est dans le depot.** Le `prompt` qui a produit un son vit ici,
   a cote du son : on peut le regenerer, le corriger, le comparer. Un fichier
   audio sans sa recette est un cul-de-sac.
3. **Les prompts sont en anglais.** C'est la langue que le modele de bruitage
   comprend le mieux ; le reste du catalogue reste en francais.

⚠️ Les voix des personnages (M6) et les radios (M3) viendront par le meme
chemin, avec `categorie` = "voix" et "radio".
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

#: Ou vivent les fichiers, par rapport a `static/`.
DOSSIER = "audio"
RACINE_STATIQUE = Path(__file__).resolve().parent.parent / "static"

CATEGORIES = ("sfx", "voix", "radio")


class Echantillon(TypedDict):
    slug: str
    nom: str
    categorie: str
    prompt: str
    duree_s: float
    boucle: bool
    volume: float
    variantes: int


def _e(slug: str, nom: str, prompt: str, duree_s: float, *, volume: float = 0.8,
       boucle: bool = False, variantes: int = 1, categorie: str = "sfx") -> Echantillon:
    return Echantillon(slug=slug, nom=nom, categorie=categorie, prompt=prompt,
                       duree_s=duree_s, boucle=boucle, volume=volume, variantes=variantes)


#: ⚠️ `variantes` > 1 : le meme geste ne doit pas rendre le meme son dix fois
#: par seconde. Les pas et les coups en ont deux ; c'est la ou l'oreille
#: s'agace le plus vite.
CATALOGUE: list[Echantillon] = [
    _e("pas", "Pas sur le trottoir", variantes=2, duree_s=0.5, volume=0.35,
       prompt="a single soft footstep on a wet concrete sidewalk, close-up, dry, "
              "no reverb, no music"),
    _e("coup", "Coup de poing", variantes=2, duree_s=0.7, volume=0.9,
       prompt="a hard bare-knuckle punch landing on a leather jacket, short dry "
              "impact, no music"),
    _e("touche", "Coup encaissé", duree_s=0.7, volume=0.7,
       prompt="a short male grunt of pain after being hit, dry, close-up, no music"),
    _e("ramasse", "Objet ramassé", duree_s=0.6, volume=0.6,
       prompt="picking up a small metal object from the pavement, short bright "
              "clink, no music"),
    _e("argent", "Argent encaissé", duree_s=0.9, volume=0.7,
       prompt="old cash register drawer opening with coins clinking, short, "
              "bright, no music"),
    _e("menu", "Clic de menu", duree_s=0.5, volume=0.5,
       prompt="a short dry retro user interface click, single blip, no music"),
    _e("erreur", "Refus", duree_s=0.6, volume=0.5,
       prompt="a short low buzzer denial tone, dry, no music"),
    _e("etoile", "Niveau de recherche", duree_s=1.0, volume=0.7,
       prompt="a tense police radio alert chirp followed by static, short, no music"),
    _e("porte", "Porte", duree_s=1.0, volume=0.6,
       prompt="an old wooden door opening with a short creak, close-up, no music"),
    _e("choc", "Tôle froissée", duree_s=1.2, volume=0.9,
       prompt="two cars colliding, sharp metal crunch and glass, short, no music"),
    _e("explosion", "Explosion", duree_s=2.0, volume=1.0,
       prompt="a car exploding, deep boom with debris falling, no music"),
    _e("klaxon", "Klaxon", duree_s=0.7, volume=0.7,
       prompt="a single short car horn honk, city street, no music"),
    _e("sirene", "Sirène de police", duree_s=4.0, volume=0.6, boucle=True,
       prompt="a police car siren wailing steadily, seamless loop, no music, "
              "no engine, no traffic"),
    _e("moteur", "Moteur au ralenti", duree_s=4.0, volume=0.5, boucle=True,
       prompt="a four cylinder car engine idling steadily, seamless loop, "
              "close-up, no music"),
    # La rumeur : son volume suit le nombre de gens autour du joueur.
    _e("foule", "Rumeur de la rue", duree_s=8.0, volume=0.5, boucle=True,
       prompt="distant crowd of people chatting on a busy city sidewalk, murmur and "
              "footsteps, no distinct words, seamless loop, no music"),
    _e("passage_auto", "Auto qui passe", variantes=2, duree_s=1.8, volume=0.6,
       prompt="a car driving past at city speed, engine whoosh with doppler effect, "
              "close, no music, no horn"),
    _e("passage_moto", "Moto qui passe", duree_s=1.8, volume=0.6,
       prompt="a motorcycle roaring past on a city street, doppler effect, close, no music"),
    _e("sonnette", "Sonnette de vélo", duree_s=0.7, volume=0.5,
       prompt="a bicycle bell ringing twice, bright, close, no music"),
]

SLUGS = tuple(e["slug"] for e in CATALOGUE)


class Radio(TypedDict):
    slug: str
    nom: str
    style: str
    prompt: str
    duree_s: int
    volume: float
    phase: int


def _r(slug, nom, style, prompt, *, duree_s=45, volume=0.45, phase=1) -> Radio:
    return Radio(slug=slug, nom=nom, style=style, prompt=prompt, duree_s=duree_s,
                 volume=volume, phase=phase)


#: Les stations. Une piste par station, INSTRUMENTALE (une voix chantee par-
#: dessus une sirene, c'est illisible), generee par ElevenLabs Music. Elle
#: boucle ; la coupure au rebouclage passe pour un jingle de station.
#: ⚠️ `duree_s` se paie a la seconde et se telecharge au premier tour de cle :
#: 45 s a 64 kbit/s font 360 Ko, ce qu'un telephone avale sans broncher.
RADIOS: list[Radio] = [
    _r("la_brume", "La Brume", "jazz",
       "slow smoky late-night jazz trio, upright bass, brushed drums, muted trumpet, "
       "foggy harbour town mood, instrumental, lo-fi radio feel, steady tempo, loopable"),
    _r("taxi_radio", "Taxi-Radio", "country",
       "warm mid-tempo country instrumental, twangy telecaster, pedal steel, shuffle "
       "drums, upright bass, Quebec country bar feel, no vocals, loopable"),
    # Martin trouvait le punk trop hardcore pour la moto : techno.
    _r("le_choc", "Le Choc", "techno",
       "driving underground techno instrumental, 128 bpm, four-on-the-floor kick, "
       "acid bassline, hypnotic synth stabs, Montreal warehouse rave at 3 am, "
       "no vocals, loopable"),
]

#: La musique de FOND : ce qu'on entend a pied, sous la rumeur de la ville.
#: Elle se tait quand une radio prend le relais, revient quand on descend.
AMBIANCES: list[Radio] = [
    _r("ville", "Baie-des-Brumes", "ambiant",
       "moody ambient score for a foggy harbour city at dusk, soft analog synth "
       "pads, distant sparse piano notes, faint foghorn, slow, melancholic, "
       "no drums, no vocals, seamless loop", duree_s=60, volume=0.3),
]

class Voix(TypedDict):
    slug: str
    texte: str
    genre: str
    voix: str
    volume: float


#: ⚠️ Deux voix nommees du compte ElevenLabs ; si l'une disparait,
#: `scripts/audio_elevenlabs.py --voix` le dit, il ne devine pas. Leo parle
#: quebecois. Sarah est une voix anglaise que le modele multilingue fait
#: parler francais : le jour ou une Quebecoise entre dans la bibliotheque,
#: c'est ici qu'on la nomme.
VOIX_PAR_GENRE = {"homme": "Léo - Français québécois", "femme": "Sarah - Mature, Reassuring, Confident"}

#: Ce que disent les gens quand on les frole. Court, quebecois, jamais deux
#: fois de suite le meme (le moteur tire au hasard, avec un temps mort).
VOIX: list[Voix] = [
    {"slug": "salut_h", "texte": "Salut!", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "frette_h", "texte": "Fait frette, hein?", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "tasse_toi_h", "texte": "Heille, tasse-toi donc!", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.75},
    {"slug": "bonne_journee_h", "texte": "Bonne journée, là.", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "salut_f", "texte": "Salut!", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "excusez_f", "texte": "Excusez-moi.", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "belle_journee_f", "texte": "Belle journée, hein?", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "ca_va_f", "texte": "Ça va, toi?", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
]


def voix_par_slug(slug: str) -> Voix | None:
    for voix in VOIX:
        if voix["slug"] == slug:
            return voix
    return None


def nom_fichier_voix(voix: Voix) -> str:
    return f"voix-{voix['slug']}.mp3"


def chemin_voix(voix: Voix) -> Path:
    return RACINE_STATIQUE / DOSSIER / nom_fichier_voix(voix)


def voix_manquantes() -> list[Voix]:
    return [v for v in VOIX if not chemin_voix(v).is_file()]


#: Le format des radios : 44 kHz a 64 kbit/s. Plus bas, un cuivre devient une
#: bouillie ; plus haut, la piste depasse le demi-mega.
FORMAT_RADIO = "mp3_44100_64"


def radio_par_slug(slug: str) -> Radio | None:
    for radio in RADIOS:
        if radio["slug"] == slug:
            return radio
    return None


def nom_fichier_radio(radio: Radio) -> str:
    return f"radio-{radio['slug']}.mp3"


def chemin_radio(radio: Radio) -> Path:
    return RACINE_STATIQUE / DOSSIER / nom_fichier_radio(radio)


def radios_manquantes() -> list[Radio]:
    return [r for r in RADIOS + AMBIANCES if not chemin_radio(r).is_file()]


def par_slug(slug: str) -> Echantillon | None:
    for echantillon in CATALOGUE:
        if echantillon["slug"] == slug:
            return echantillon
    return None


def nom_fichier(echantillon: Echantillon, indice: int) -> str:
    """`coup-1.mp3`, `coup-2.mp3`... — l'indice commence a 1, comme on compte."""
    return f"{echantillon['slug']}-{indice}.mp3"


def chemin(echantillon: Echantillon, indice: int) -> Path:
    return RACINE_STATIQUE / DOSSIER / nom_fichier(echantillon, indice)


def fichiers_presents(echantillon: Echantillon) -> list[str]:
    return [nom_fichier(echantillon, i) for i in range(1, echantillon["variantes"] + 1)
            if chemin(echantillon, i).is_file()]


def manquants() -> list[tuple[Echantillon, int]]:
    """Ce qu'il reste a generer — lu par `scripts/audio_elevenlabs.py`."""
    return [(e, i) for e in CATALOGUE for i in range(1, e["variantes"] + 1)
            if not chemin(e, i).is_file()]


def orphelins() -> list[str]:
    """Les fichiers du dossier que plus personne ne reclame."""
    dossier = RACINE_STATIQUE / DOSSIER
    if not dossier.is_dir():
        return []
    attendus = {nom_fichier(e, i) for e in CATALOGUE for i in range(1, e["variantes"] + 1)}
    attendus |= {nom_fichier_radio(r) for r in RADIOS + AMBIANCES}
    attendus |= {nom_fichier_voix(v) for v in VOIX}
    return sorted(f.name for f in dossier.iterdir()
                  if f.is_file() and f.suffix == ".mp3" and f.name not in attendus)


def exporter() -> dict:
    """⚠️ Ne declare QUE les fichiers presents : le navigateur ne demande jamais
    un son qui n'existe pas, et se rabat sur la synthese sans un 404."""
    return {
        "dossier": DOSSIER,
        "echantillons": [
            {**echantillon, "fichiers": fichiers_presents(echantillon)}
            for echantillon in CATALOGUE
        ],
        # Les radios se chargent au premier tour de cle, jamais au demarrage.
        "radios": [
            {"slug": r["slug"], "nom": r["nom"], "style": r["style"], "volume": r["volume"],
             "fichier": nom_fichier_radio(r) if chemin_radio(r).is_file() else None}
            for r in RADIOS
        ],
        "ambiances": [
            {"slug": r["slug"], "nom": r["nom"], "style": r["style"], "volume": r["volume"],
             "fichier": nom_fichier_radio(r) if chemin_radio(r).is_file() else None}
            for r in AMBIANCES
        ],
        # Les repliques des passants : quelques mots, deux voix, en francais.
        "voix": [
            {"slug": v["slug"], "texte": v["texte"], "genre": v["genre"], "volume": v["volume"],
             "fichier": nom_fichier_voix(v) if chemin_voix(v).is_file() else None}
            for v in VOIX
        ],
    }
