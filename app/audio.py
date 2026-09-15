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

from app import musique

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
    influence: float


def _e(slug: str, nom: str, prompt: str, duree_s: float, *, volume: float = 0.8,
       boucle: bool = False, variantes: int = 1, categorie: str = "sfx",
       influence: float = 0.6) -> Echantillon:
    return Echantillon(slug=slug, nom=nom, categorie=categorie, prompt=prompt,
                       duree_s=duree_s, boucle=boucle, volume=volume,
                       variantes=variantes, influence=influence)


#: ⚠️ `variantes` > 1 : le meme geste ne doit pas rendre le meme son dix fois
#: par seconde. Les pas, les coups et les grognements en ont trois ou quatre ;
#: c'est la ou l'oreille s'agace le plus vite. Un clic de menu, lui, DOIT etre
#: toujours le meme : une interface qui varie a l'air cassee.
#:
#: ⚠️ `volume` porte maintenant TOUT le dosage. La finition normalise chaque
#: fichier au meme pic (-1 dBFS), donc deux sons qui sortaient l'un a -24 dB et
#: l'autre a 0 dB sortent desormais pareil : le seul endroit ou l'un est plus
#: fort que l'autre, c'est ici. Les valeurs ci-dessous REPRODUISENT le melange
#: d'avant (pic mesure x volume d'avant) — sauf `pas` et `sonnette`, qui
#: mesuraient sous -23 dB une fois mixes, c'est-a-dire sous le seuil de ce
#: qu'on entend en jouant.
#:
#: ⚠️ `influence` (0 a 1) dit au modele a quel point coller a la description.
#: Haut pour ce qui doit etre UNE chose exacte (un clic, un klaxon, une
#: sirene) ; plus bas pour une matiere (une explosion, une foule), ou le
#: modele rend mieux quand on lui laisse de la place.
CATALOGUE: list[Echantillon] = [
    _e("pas", "Pas sur le trottoir", variantes=4, duree_s=0.5, volume=0.11,
       prompt="a single footstep, hard leather sole on damp concrete sidewalk, "
              "sharp heel tap then a small scuff of grit, dry close-up, "
              "no reverb, no music"),
    _e("coup", "Coup de poing", variantes=3, duree_s=0.8, volume=0.22,
       prompt="a single bare-knuckle punch landing hard on a leather jacket, "
              "sharp meaty slap with a dull low body thud underneath, dry and "
              "close, no reverb, no music"),
    _e("touche", "Coup encaissé", variantes=3, duree_s=0.9, volume=0.79,
       prompt="a short winded male grunt of pain after a punch to the ribs, "
              "breath forced out through the teeth, dry close-up, no words, "
              "no music"),
    # ⚠️ Un son PAR ARME (`armes.py`, champ `son`). Jusqu'au 13 sept. 2026,
    # tout jouait le coup de poing : la batte, le couteau, le pistolet et le
    # fusil aussi. Une arme qu'on n'entend pas, on ne sait pas qu'on la tient.
    # Le geste et l'impact sont dans le MEME echantillon (comme `coup`) : le
    # son part au debut de la phase active, avant de savoir s'il touche.
    _e("batte", "Coup de bâton", variantes=2, duree_s=0.9, volume=0.32,
       prompt="a wooden baseball bat swung hard and striking a body, a quick "
              "whoosh then a deep hollow wooden thwack, dry close-up, no reverb, "
              "no voices, no music"),
    _e("couteau", "Coup de couteau", variantes=2, duree_s=0.7, volume=0.26,
       prompt="a fast knife slash cutting through a leather jacket, a short "
              "sharp blade whoosh with a thin metallic ring, dry close-up, "
              "no voices, no music"),
    _e("pelle", "Coup de pelle", duree_s=1.0, volume=0.35,
       prompt="a steel garden shovel swung hard and hitting a body flat, a "
              "heavy whoosh then a bright ringing metal clang, dry close-up, "
              "no voices, no music"),
    _e("cone", "Coup de cône", duree_s=0.7, volume=0.24,
       prompt="a hollow plastic traffic cone swung and striking a body, a light "
              "whoosh then a dull hollow plastic whack, dry close-up, no voices, "
              "no music"),
    _e("bouteille", "Coup de bouteille", duree_s=0.8, volume=0.3,
       prompt="a glass beer bottle swung and smashing against a body, a short "
              "whoosh then a sharp glass clink and crack, dry close-up, "
              "no voices, no music"),
    _e("fronde", "Tir de fronde", duree_s=0.6, volume=0.22, influence=0.7,
       prompt="a slingshot fired: a rubber band stretched and released with a "
              "sharp elastic snap and a short whip of air, dry close-up, "
              "no voices, no music"),
    # ⚠️ Les armes a feu sont FORTES, et c'est voulu : un coup de feu qui
    # sonne comme une claque, on ne comprend pas pourquoi la rue se vide.
    _e("pistolet", "Coup de pistolet", variantes=2, duree_s=1.0, volume=0.7,
       prompt="a single 9mm pistol gunshot on a city street at night, a sharp "
              "loud crack with a short slap of echo off the buildings, "
              "no voices, no music"),
    _e("fusil", "Coup de fusil à pompe", variantes=2, duree_s=1.3, volume=0.85,
       prompt="a single pump-action shotgun blast on a city street, a deep "
              "heavy boom with a sharp crack, then the pump racked with a "
              "metallic clack-clack, short echo off the buildings, no voices, "
              "no music"),
    # Les trois du marche noir (14 sept. 2026). ⚠️ La mitraillette joue UN coup
    # par balle, douze fois par seconde : l'echantillon est court et sec, sinon
    # douze queues d'echo s'empilent. Et le Molotov s'entend quand il CASSE —
    # `combat.js` le joue a l'arrivee de la bouteille, pas au lancer.
    # ⚠️ 0,5 s et pas moins : c'est le PLANCHER du serveur (`duration_seconds`
    # >= 0.5), et sous lui il repond par une erreur qui n'est pas du JSON —
    # le script de generation tombait dessus sans rien expliquer.
    _e("mitraillette", "Coup de mitraillette", variantes=2, duree_s=0.5, volume=0.55,
       influence=0.7,
       prompt="a single 9mm submachine gun shot on a city street, one sharp "
              "tight crack, very short, almost no echo, no voices, no music"),
    _e("carabine", "Coup de carabine", duree_s=1.2, volume=0.85, influence=0.7,
       prompt="a single bolt-action rifle shot on a city street, a loud sharp "
              "crack with a rolling echo off the buildings, then the bolt "
              "worked with a metallic clack, no voices, no music"),
    _e("molotov", "Cocktail Molotov qui casse", duree_s=1.3, volume=0.7,
       prompt="a glass bottle shattering on asphalt then a sudden whoomp of "
              "gasoline igniting into a burst of flames with a short crackle, "
              "dry close-up, no voices, no music"),
    # Le jet de l'extincteur tourne tant qu'on appuie : une boucle, comme le
    # moteur, allumee et eteinte par `Son.SFX.jet(actif)` a chaque image.
    _e("extincteur", "Jet d'extincteur", duree_s=2.0, volume=0.35, boucle=True,
       prompt="a dry chemical fire extinguisher spraying continuously, a loud "
              "hissing rush of pressurized powder, steady, seamless loop, "
              "no voices, no music"),
    # Trois sons AUTOUR des armes : la gachette a vide (c'etait le buzzer des
    # menus — on croyait le bouton casse), l'arme de fortune qui casse (le
    # meme buzzer), et le geste de changer d'arme (c'etait le clic de menu).
    _e("vide", "Chargeur vide", duree_s=0.5, volume=0.3, influence=0.75,
       prompt="a handgun trigger pulled on an empty chamber, one dry metallic "
              "click, close-up, no gunshot, no voices, no music"),
    _e("casse", "Arme qui casse", duree_s=0.9, volume=0.4,
       prompt="a makeshift weapon breaking in the hand, a wooden handle snapping "
              "with a sharp crack and the pieces clattering onto asphalt, "
              "close-up, no voices, no music"),
    _e("degainer", "Dégainer", duree_s=0.6, volume=0.2, influence=0.7,
       prompt="quickly drawing a weapon from inside a jacket, a short rustle of "
              "leather and cloth with a small metallic click, close-up, "
              "no voices, no music"),
    _e("ramasse", "Objet ramassé", variantes=2, duree_s=0.7, volume=0.16,
       prompt="picking a small steel object up off wet asphalt, a brief "
              "metallic scrape then a bright clink, close-up, dry, no music"),
    _e("argent", "Argent encaissé", duree_s=1.2, volume=0.56,
       prompt="an old mechanical cash register drawer springing open, a bell "
              "ping and coins tumbling onto the metal tray, bright and close, "
              "no music"),
    _e("menu", "Clic de menu", duree_s=0.5, volume=0.38, influence=0.75,
       prompt="a single short retro user interface blip, dry electronic click "
              "with a tiny pitched tail, no reverb, no music"),
    _e("erreur", "Refus", duree_s=0.6, volume=0.56, influence=0.75,
       prompt="a short low electronic buzzer denying an action, flat dull "
              "tone, dry, no music"),
    _e("etoile", "Niveau de recherche", duree_s=1.2, volume=0.79, influence=0.75,
       prompt="a police radio alert chirp followed by a burst of squelch "
              "static, tense and short, no voices, no music"),
    # ⚠️ TROIS portes, pas une. Le meme grincement de bois servait au logement,
    # au depanneur et au taxi — on n'entendait pas ou l'on entrait. Le genre
    # vient de la FICHE : chaque piece dit quelle porte on pousse
    # (`carte._piece`, champ `porte`), chaque char dit s'il a des portieres
    # (`vehicules.py`, `portieres`). La moto et le velo n'en ont pas : on les
    # enfourche, et c'est le cliquetis de `ramasse` qui le dit.
    _e("porte_maison", "Porte de logement", duree_s=1.5, volume=0.66,
       prompt="a heavy old wooden apartment door: a key turning in the lock, "
              "the knob clicking, the door swinging open on a slightly creaky "
              "hinge and shutting with a solid wooden thump, small echoing "
              "stairwell, no voices, no music"),
    # ⚠️ Deuxieme recette (Martin a ecoute la premiere et l'a renvoyee) : plus
    # de ferme-porte « qui siffle » — un souffle d'air, le modele en fait
    # n'importe quoi.  
    _e("porte_commerce", "Porte de commerce", duree_s=1.5, volume=0.6, influence=0.7,
       prompt="a shop metalic sliding door opens as a small store's "
              "clacks softly shut, close-up, "
              "no voices, no music"),
    _e("porte_vehicule", "Portière", duree_s=1.0, volume=0.66, influence=0.7,
       prompt="an old sedan car door: the handle clicking, the door swinging "
              "and slamming shut with a solid metallic thunk and a short "
              "rattle of the window glass, outdoors on a quiet street, no "
              "engine, no music"),
    # ⚠️ Un velo et une moto n'ont pas de portiere : on les enfourche. Ca
    # jouait `ramasse` — le cliquetis d'un objet qu'on ramasse — et Martin
    # l'a entendu pour ce que c'etait. La bequille et le cadre, c'est autre
    # chose. Sert a tout char sans portieres (`vehicules.py`).
    _e("enfourcher", "Enfourcher un deux-roues", duree_s=0.9, volume=0.35,
       prompt="hopping onto a parked bicycle: the metal kickstand flicked up "
              "with a clank, the light steel frame and chain rattling as the "
              "rider lands on the saddle, close-up, outdoors, no voices, "
              "no music"),
    _e("choc", "Tôle froissée", variantes=2, duree_s=1.5, volume=1.0, influence=0.45,
       prompt="two cars colliding at city speed, one hard metal crunch, sheet "
              "metal buckling, headlight glass shattering onto the road, "
              "close, no music"),
    _e("explosion", "Explosion", duree_s=2.5, volume=1.0, influence=0.45,
       prompt="a car exploding, a sharp cracking blast then a deep "
              "body-shaking boom, metal debris and glass raining down onto "
              "asphalt, no music"),
    _e("klaxon", "Klaxon", variantes=2, duree_s=0.8, volume=0.79, influence=0.75,
       prompt="one short car horn honk from an old sedan, slightly flat "
              "two-tone blare, city street, no music"),
    _e("sirene", "Sirène de police", duree_s=4.0, volume=0.61, boucle=True,
       influence=0.75,
       prompt="a police car siren wailing up and down steadily, close, "
              "seamless loop, no music, no engine, no traffic"),
    # ⚠️ DEUX sirenes, pas une. Celle de la police monte et descend sans
    # s'arreter ; celle d'une ambulance fait deux notes, plus haut et plus
    # lent. Les confondre, c'est ne pas savoir qui arrive derriere soi — et
    # c'est toute la difference entre se ranger et se sauver.
    _e("sirene_ambulance", "Sirène d'ambulance", duree_s=4.0, volume=0.62,
       boucle=True, influence=0.75,
       prompt="an ambulance siren, two-tone hi-lo wail alternating slowly, "
              "seamless loop, no music, no engine, no traffic"),
    _e("helico", "Hélicoptère", duree_s=4.0, volume=0.68, boucle=True,
       influence=0.75,
       prompt="a police helicopter hovering overhead, rotor blades thumping "
              "steadily, seamless loop, no music, no voices, no siren"),
    _e("telephone", "Sonnerie du téléphone", duree_s=2.0, volume=0.62,
       influence=0.75,
       prompt="an old flip phone ringing twice on a table, thin electronic "
              "ringtone with a faint buzz of vibration, close, no voices, "
              "no music"),
    _e("moteur", "Moteur au ralenti", duree_s=4.0, volume=0.32, boucle=True,
       influence=0.75,
       prompt="a four cylinder car engine idling steadily at low rpm, "
              "close-up from outside the hood, slight lope, seamless loop, "
              "no music"),
    # La rumeur : son volume suit le nombre de gens autour du joueur.
    _e("foule", "Rumeur de la rue", duree_s=8.0, volume=0.23, boucle=True,
       influence=0.45,
       prompt="distant crowd of people chatting on a busy city sidewalk, "
              "murmur and footsteps, no distinct words, seamless loop, "
              "no music"),
    _e("passage_auto", "Auto qui passe", variantes=2, duree_s=2.0, volume=0.68,
       influence=0.45,
       prompt="a car driving past at city speed on wet asphalt, tyre roar "
              "swelling and falling away with a doppler shift, close, "
              "no horn, no music"),
    # ⚠️ Ce prompt disait « exhaust BARK », et le modele a rendu un CHIEN —
    # Martin l'a entendu tout de suite. Un mot d'argot de sonorisation
    # (« bark », « growl », « scream », « chirp ») est d'abord un cri d'animal :
    # dans une description de bruitage, on ecrit ce qu'on veut entendre, pas le
    # mot du metier. Le chien est garde dans `static/audio/reserve/`, et
    # `influence` remonte a 0,6 : sur ce son-la, on ne laisse plus de place.
    _e("passage_moto", "Moto qui passe", duree_s=2.0, volume=0.68, influence=0.6,
       prompt="a motorcycle riding past at speed on a city street, deep engine "
              "roar rising then falling away with a doppler drop, close, "
              "no music, no voices, no animals"),
    _e("sonnette", "Sonnette de vélo", duree_s=1.0, volume=0.11, influence=0.75,
       prompt="a bicycle bell struck twice, bright ringing brass with a "
              "shimmering tail, close, no music"),
    # --- L'eau ---------------------------------------------------------------
    # ⚠️ Depuis « L'eau n'est plus un mur », on entrait dans la baie sur
    # `choc` — la TOLE FROISSEE, le son d'un accident de char — et on nageait
    # dans le silence complet, les pas coupes et rien a la place. Trois sons,
    # et chacun repond a un moment que le jeu produisait deja sans le dire :
    # on entre, on avance, on coule.
    _e("plongeon", "Plongeon dans l'eau", variantes=2, duree_s=1.4, volume=0.55,
       influence=0.5,
       prompt="a person jumping feet first into cold sea water, one heavy "
              "splash, a mass of water thrown up then falling back, scattered "
              "droplets, close-up, outdoors, no voices, no music"),
    # ⚠️ TROIS variantes, comme les pas : une brassee revient une fois et
    # demie par seconde, et c'est la que l'oreille s'agace le plus vite.
    # ⚠️ Et ce n'est PAS une boucle : elle se joue a la distance parcourue
    # (`son.js`, `SFX.nage`), sans quoi un nageur immobile sonnerait comme une
    # fontaine.
    _e("nage", "Brassée", variantes=3, duree_s=0.8, volume=0.2, influence=0.5,
       prompt="a single swimmer arm stroke through open water, a short wet "
              "swirl and churn, water sliding off skin, close-up, no "
              "breathing, no voices, no music"),
    _e("couler", "On coule", duree_s=1.8, volume=0.7, influence=0.45,
       prompt="a head going under water, one gulp as the surface closes over, "
              "muffled bubbles rising, the sound turning dull and distant, "
              "close-up, no voices, no music"),
]

# --- La finition des bruitages -------------------------------------------------------
#
# ⚠️ Ce qu'ElevenLabs rend n'est PAS ce qu'on garde. Mesure du 13 septembre
# 2026 sur les 24 premiers fichiers (22 kHz, 32 kbit/s, stereo) :
#
# - il ne restait presque rien au-dessus de 8 kHz. Mesure, en comparant le
#   pic du signal filtre a 8 kHz au pic du fichier entier : -26 dB pour la
#   caisse enregistreuse, -27 pour la tole froissee, -30 pour le clic de
#   menu, -32 pour la porte. Or c'est LA que vit le clinquant d'une piece et
#   le verre d'un phare — on payait une generation dont on jetait le haut
#   avant meme de l'ecouter. Les memes sons sont aujourd'hui entre -6 et
#   -10 dB. ⚠️ Un klaxon, une sirene et un moteur, eux, n'ont pas bouge :
#   ils n'ont pas d'aigu a avoir, et c'est tres bien ;
# - un septieme du poids etait du silence en QUEUE (14 % en moyenne, mais
#   69 % d'un pas, 55 % d'un ramassage, 43 % d'un coup de poing) : de quoi
#   payer une bonne partie de l'aigu qu'on vient de recuperer ;
# - les pics allaient de -34 dB (un pas) a 0 dB pile (huit fichiers colles au
#   plafond), donc `volume` ne dosait rien : il multipliait un accident ;
# - deux fichiers etaient franchement STEREO (la porte, le refus : leurs deux
#   canaux ne se ressemblent qu'a 1 dB pres), et un son deja large ne se
#   laisse plus placer par le `StereoPanner` de `son.js`.
#
# On demande donc le meilleur master que le palier donne, et `ffmpeg` le
# ramene a la taille du jeu (`scripts/audio_elevenlabs.py`, `finir`).

#: Le master demande a ElevenLabs. 44,1 kHz : deux fois la bande passante du
#: 22 kHz d'avant, donc l'aigu existe. On ne le garde pas tel quel.
FORMAT_MASTER = "mp3_44100_128"

#: Le pic vise apres normalisation, pour tous les bruitages. -1 dBFS et pas
#: 0 : un encodeur mp3 depasse l'echantillon d'origine, et ca s'entend comme
#: une saturation. ⚠️ C'est ce qui rend `volume` credible : tous les fichiers
#: partent du meme niveau, le catalogue seul decide qui est plus fort.
PIC_VISE_DBFS = -1.0

#: Sous ce niveau, c'est la queue du son : on la coupe plutot que de payer
#: jusqu'aux deux tiers du fichier en silence. On en garde 30 ms, et on ferme par un fondu
#: de 15 ms — couper net sur une decroissance, ca fait un clic.
#: ⚠️ Ce seuil ne vaut QU'APRES normalisation : il est alors toujours a 44 dB
#: sous le pic, quelle que soit la generation. Applique avant, il tombe en
#: plein milieu d'un son sorti faible — voir `finir()`.
SEUIL_QUEUE_DBFS = -45.0
QUEUE_GARDEE_S = 0.03
FONDU_S = 0.015

#: Sous cette duree, il ne reste plus de son : la finition refuse plutot que
#: de livrer un fichier de souffle.
DUREE_PLANCHER_S = 0.05

#: Le rapport signal/bruit d'un bruitage BREF fini, sous lequel on a remonte
#: du souffle avec le son.
#:
#: ⚠️ Ce n'est PAS le gain applique, et je m'y suis trompe d'abord : j'avais
#: pose « plus de 20 dB de gain = generation ratee ». Faux. ElevenLabs rend
#: souvent un pas a bas niveau mais parfaitement propre — mesure : `pas-2`
#: demandait +29 dB de gain ET affichait le MEILLEUR plancher des quatre
#: (-47 dB, 46 dB de RSB). Le drapeau envoyait donc refaire, a credits
#: perdus, la meilleure prise du lot. Ce qui compte est le plancher de bruit
#: du fichier fini, pas le chemin pour y arriver.
#:
#: ⚠️ Et seulement sur un son BREF : une sirene ou un moteur sont un son
#: continu, leur « plancher » est le son lui-meme (13 dB pour la sirene).
RSB_PLANCHER_DB = 30.0

#: Deux debits, en mono et en 44,1 kHz. Un choc porte des transitoires et du
#: verre, il en a besoin ; une boucle de moteur est une matiere qui tourne, et
#: elle joue en continu — elle passe a 64.
DEBIT_BREF = "96k"
DEBIT_BOUCLE = "64k"

#: ⚠️ Une BOUCLE ne se rogne pas et ne se fond pas : la couture est exactement
#: ce que le rognage abime, et un fondu ferait un trou a chaque tour. Elle
#: n'a droit qu'au mono et au gain.


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
    # v2 / M8 — deux stations de plus, une par nouveau bout de ville. ⚠️ Elles
    # restent INSTRUMENTALES comme les autres : une voix chantee par-dessus une
    # sirene, on n'entend plus ni l'une ni l'autre.
    _r("dix_quatre", "10-4", "scanner",
       "tense instrumental cop-show groove, muted guitar stabs, dry rimshot drums, "
       "low synth drone, faint radio static and morse blips, 1970s police "
       "procedural, no vocals, loopable"),
    # ⚠️ Radio-Traversier reste declaree SANS char depuis M9 : le camion a
    # herite d'une station procedurale, et celle-ci attend le traversier de
    # M12 — c'est sa musique de pont, pas sa musique de cabine.
    _r("traversier", "Radio-Traversier", "rigodon",
       "lively Quebecois traditional reel, fiddle lead, diatonic accordion, foot "
       "tapping rhythm, spoons, upright bass, joyful village dance hall, "
       "instrumental, loopable"),
]

#: La musique de FOND : ce qu'on entend a pied, sous la rumeur de la ville.
#: Elle se tait quand une radio prend le relais, revient quand on descend.
AMBIANCES: list[Radio] = [
    _r("ville", "Baie-des-Brumes", "ambiant",
       "moody ambient score for a foggy harbour city at dusk, soft analog synth "
       "pads, distant sparse piano notes, faint foghorn, slow, melancholic, "
       "no drums, no vocals, seamless loop", duree_s=60, volume=0.3),
]

class Voix(TypedDict, total=False):
    slug: str
    texte: str
    genre: str
    voix: str
    volume: float
    #: Le rendu, quand la voix par defaut ne suffit pas : `style` (0 a 1)
    #: exagere le ton de la voix, `stabilite` (0 a 1) le laisse varier quand
    #: elle est basse. Absents = les reglages de la voix telle quelle.
    style: float
    stabilite: float


#: ⚠️ Deux voix nommees du compte ElevenLabs ; si l'une disparait,
#: `scripts/audio_elevenlabs.py --voix` le dit, il ne devine pas. Martin a
#: ajoute des voix quebecoises le 13 sept. : Felix (« l'homme de tous les
#: jours ») pour les passants, Amelie (accent d'ici, articulation nette) pour
#: les passantes.
VOIX_PAR_GENRE = {"homme": "Felix Tabarnak - Confident and Witty", "femme": "Amélie - Young, Confident and Friendly"}

#: ⚠️ Le crieur n'est PAS l'homme de tous les jours : avec Felix, ses cris ne
#: sonnaient « pas assez vendeur » (retour de Martin, 13 sept. 2026). Leo est
#: la voix de pub du compte (« enthousiaste, souriante, faite pour les
#: commerciaux »), poussee au style et laissee libre de varier.
VOIX_CRIEUR = "Léo - Français québécois"

#: La fille de la Brume : Julia — quebecoise, rauque et chaude, la seule voix
#: de femme du compte qui ne sonne pas comme une passante ou une institutrice.
#: Poussee au style et laissee varier : elle n'annonce pas, elle accoste.
VOIX_BRUME = "Julia"

#: COMMENT LA RUE PARLE — et c'est ici, pas dans le JS, parce que ce sont trois
#: reglages qui se decident ensemble.
#:
#: ⚠️ « Jamais deux fois de suite le meme » etait ECRIT et FAUX. Le moteur
#: tirait au hasard sans aucune memoire : sur quatre repliques par genre, une
#: chance sur quatre de repeter la precedente — dans une rue passante, on
#: entendait « Fait frette, hein? » trois fois en vingt secondes. Un tirage au
#: hasard PEUT sortir deux fois le meme ; c'est meme sa definition.
#:
#: ⚠️ Et le vrai coupable n'etait pas le tirage, c'etait la FREQUENCE : un
#: passant qui parle chaque fois qu'on le frole rend huit repliques fatigantes
#: bien avant qu'elles soient usees. La plupart des gens qu'on croise ne disent
#: rien, comme dans la vraie vie.
PAROLE = {
    "temps_mort_images": 420,   # 7 s entre deux repliques, partout dans la ville
    "chance": 0.35,             # ... et parler reste une CHANCE, pas une certitude
    # ⚠️ Combien de repliques on refuse de repeter. DEUX, et pas quatre comme
    # la fiche l'annonce — parce que la plus petite banque en compte TROIS (le
    # crieur). Pour en exclure quatre, il en faudrait au moins six par banque :
    # ce nombre-la monte le jour ou les banques montent, et un juge tient les
    # deux ensemble (`test_parole.py`) pour qu'on ne puisse pas bouger l'un
    # sans l'autre. Sinon la regle se retourne contre elle-meme : on exclut
    # tout, il ne reste rien a tirer, et plus personne ne parle.
    "memoire": 2,
}

#: Ce que disent les gens quand on les frole. Court, quebecois, jamais deux
#: fois de suite le meme (le moteur tire au hasard, avec un temps mort).
VOIX: list[Voix] = [
    {"slug": "salut_h", "texte": "Salut!", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "frette_h", "texte": "Fait frette, hein?", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "tasse_toi_h", "texte": "Heille ! Tâsse-toi don !", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.75},
    {"slug": "bonne_journee_h", "texte": "Bonne journée, là.", "genre": "homme", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.7},
    {"slug": "salut_f", "texte": "Salut!", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "excusez_f", "texte": "Excusez-moi.", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "belle_journee_f", "texte": "Belle journée, hein?", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    {"slug": "ca_va_f", "texte": "Ça va, toi?", "genre": "femme", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.7},
    # Le crieur : ce que lance l'homme-sandwich quand il vient vers toi
    # (`pietons.homme_sandwich`, `magasins.RECLAME`). Un genre a part : un
    # passant qu'on frole ne crie pas « approchez ».
    {"slug": "approchez_c", "texte": "Approchez, approchez, venez voir!", "genre": "crieur", "voix": VOIX_CRIEUR, "volume": 0.8, "style": 0.7, "stabilite": 0.3},
    {"slug": "special_c", "texte": "Le spécial du jour, c'est icitte!", "genre": "crieur", "voix": VOIX_CRIEUR, "volume": 0.8, "style": 0.7, "stabilite": 0.3},
    {"slug": "moitie_prix_c", "texte": "Moitié prix, moitié prix, aujourd'hui!", "genre": "crieur", "voix": VOIX_CRIEUR, "volume": 0.8, "style": 0.7, "stabilite": 0.3},
    # La fille de la Brume (13 sept. 2026, demande de Martin : « la prostituée
    # aussi doit parler, avec plusieurs dialogues différents »). Un genre a
    # elle : une passante qu'on frole ne dit pas ca, et elle ne dit pas
    # « Excusez-moi ». `entites.accosterDepuisLaBrume` en tire une quand on
    # passe pres de son coin — jamais deux fois de suite la meme.
    {"slug": "compagnie_b", "texte": "Tu cherches de la compagnie, mon beau?", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
    {"slug": "beau_bonhomme_b", "texte": "Heille, beau bonhomme! Viens icitte.", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
    {"slug": "frette_b", "texte": "Fait frette, hein? Viens te réchauffer.", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
    {"slug": "du_feu_b", "texte": "T'as du feu, mon chou?", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
    {"slug": "tout_seul_b", "texte": "Reste pas tout seul à soir, là.", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
    {"slug": "ca_te_tente_b", "texte": "Ça te tente-tu, un peu de compagnie?", "genre": "brume", "voix": VOIX_BRUME, "volume": 0.75, "style": 0.6, "stabilite": 0.35},
]


#: Les voix de l'histoire : une par personnage, nommees dans `missions.PERSONNAGES`.
#: A 44 kHz / 64 kbit/s (pas 22 kHz comme un bruitage) : on ecoute quelqu'un
#: parler, pas une portiere. Elles se chargent PAR MISSION, jamais au demarrage.
FORMAT_HISTOIRE = "mp3_44100_64"


def voix_histoire() -> list[dict]:
    """Chaque replique de `missions.repliques()`, avec la voix de son personnage."""
    from . import missions
    sortie = []
    for r in missions.repliques():
        perso = missions.personnage(r["qui"])
        if perso is None:
            raise ValueError(f"replique {r['slug']} : personnage inconnu {r['qui']!r}")
        sortie.append({"slug": r["slug"], "texte": r["texte"], "genre": perso["genre"], "voix": perso["voix"],
                       "volume": 0.9, "histoire": True, "qui": r["qui"], "mission": r["mission"],
                       "partie": r["partie"], "telephone": r["telephone"]})
    return sortie


def voix_journal() -> list[dict]:
    """Chaque manchette du Clairon, lue par le narrateur (la version `lu`, en casse naturelle)."""
    from . import journal, missions
    perso = missions.personnage("narrateur")
    if perso is None:
        raise ValueError("le narrateur manque a missions.PERSONNAGES")
    return [{"slug": f"narrateur-journal-{r['slug']}", "texte": r["lu"], "genre": perso["genre"], "voix": perso["voix"],
             "volume": 0.85, "histoire": True, "qui": "narrateur", "mission": "journal", "partie": "journal",
             "telephone": False}
            # ⚠️ Les LECONS y sont aussi : le narrateur les lit comme une
            # manchette. Tant que leurs mp3 n'existent pas, `exporter()` ne les
            # declare pas et l'encadre s'affiche sans voix — c'est la regle de
            # ce fichier, et c'est elle qui permet d'ecrire le texte avant de
            # depenser un credit.
            for r in journal.REGLES + journal.SPECIALES + journal.LECONS]


def toutes_les_voix() -> list[dict]:
    return list(VOIX) + voix_histoire() + voix_journal()


def voix_par_slug(slug: str) -> Voix | None:
    for voix in toutes_les_voix():
        if voix["slug"] == slug:
            return voix
    return None


def nom_fichier_voix(voix: dict) -> str:
    return f"{'histoire' if voix.get('histoire') else 'voix'}-{voix['slug']}.mp3"


def chemin_voix(voix: dict) -> Path:
    return RACINE_STATIQUE / DOSSIER / nom_fichier_voix(voix)


def voix_manquantes() -> list[dict]:
    return [v for v in toutes_les_voix() if not chemin_voix(v).is_file()]


#: Le format des radios : 44 kHz a 64 kbit/s. Plus bas, un cuivre devient une
#: bouillie ; plus haut, la piste depasse le demi-mega.
FORMAT_RADIO = "mp3_44100_64"


def radio_par_slug(slug: str) -> Radio | None:
    for radio in RADIOS:
        if radio["slug"] == slug:
            return radio
    return None


def station_existe(slug: str) -> bool:
    """La radio d'un char : une station ENREGISTREE (ici) ou une station
    PROCEDURALE (`musique.STATIONS`, ecrite par une graine). Les deux se
    jouent par le meme bouton RADIO ; c'est `son.js` qui choisit la source.

    ⚠️ Une troisieme sorte n'existe pas : un slug qui n'est ni dans l'une ni
    dans l'autre est un bouton RADIO qui ne fait rien.
    """
    if radio_par_slug(slug):
        return True
    return any(station["slug"] == slug for station in musique.STATIONS)


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
    """Les fichiers du dossier que plus personne ne reclame.

    ⚠️ `iterdir()` NE DESCEND PAS dans les sous-dossiers, et c'est ce qui rend
    `static/audio/reserve/` possible : une generation ratee mais bonne y est
    gardee sans etre reclamee par le catalogue, ni chargee par le jeu. Passer
    a `rglob()` exigerait de supprimer toute la reserve — voir son LISEZMOI.
    """
    dossier = RACINE_STATIQUE / DOSSIER
    if not dossier.is_dir():
        return []
    attendus = {nom_fichier(e, i) for e in CATALOGUE for i in range(1, e["variantes"] + 1)}
    attendus |= {nom_fichier_radio(r) for r in RADIOS + AMBIANCES}
    attendus |= {nom_fichier_voix(v) for v in toutes_les_voix()}
    return sorted(f.name for f in dossier.iterdir()
                  if f.is_file() and f.suffix == ".mp3" and f.name not in attendus)


#: LA RUMEUR DE LA FOULE — et ce qui la fait taire.
#:
#: ⚠️ Une rue qui se tait d'un coup dit « ils t'ont vu » mieux qu'une etoile de
#: plus, et elle le dit AVANT qu'on regarde le HUD. Le volume suivait deja le
#: nombre de gens autour ; il ne manquait qu'une raison de le faire tomber.
#:
#: ⚠️ Et le contraire compte autant : apres un coup de feu, la rumeur ne
#: reprend PAS au meme endroit — elle revient en cris, puis se calme. Une foule
#: qui murmure pareil avant et apres un mort n'est pas une foule, c'est un
#: bruit de fond.
RUMEUR = {
    "peur_images": 240,        # combien de temps la rue reste basse
    "peur_part": 0.18,         # ce qu'il reste du volume quand elle a peur
    "cri_images": 150,         # apres un coup de feu : elle crie
    "cri_part": 1.7,           # ... et plus fort que d'habitude
    # ⚠️ Quatre secondes pour retrouver son plein volume. C'est la CHUTE qui se
    # remarque, et c'est la remontee lente qui fait qu'on se sent surveille
    # encore un moment apres avoir range l'arme.
    "retour_par_image": 0.004,
}


def exporter() -> dict:
    """⚠️ Ne declare QUE les fichiers presents : le navigateur ne demande jamais
    un son qui n'existe pas, et se rabat sur la synthese sans un 404."""
    return {
        "dossier": DOSSIER,
        "parole": dict(PAROLE),
        "rumeur": dict(RUMEUR),
        # La musique ecrite en notes (aucun fichier) : voir `app/musique.py`.
        "musiques": musique.exporter(),
        # ⚠️ L'ECHELLE de qui gagne, et les reglages de la musique d'etat. Ils
        # sont ECRITS UNE FOIS, en Python : le navigateur lit sa priorite, il
        # ne l'invente pas. Sans ca, chaque endroit du JS aurait la sienne.
        "echelle": dict(musique.ECHELLE),
        "musique": dict(musique.MUSIQUE),
        "ambiances_de_district": dict(musique.AMBIANCES_DE_DISTRICT),
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
        # Les repliques de l'histoire : une voix par personnage, chargees par mission.
        "histoire": [
            {"slug": v["slug"], "qui": v["qui"], "mission": v["mission"], "partie": v["partie"],
             "telephone": v["telephone"], "volume": v["volume"],
             "fichier": nom_fichier_voix(v) if chemin_voix(v).is_file() else None}
            for v in voix_histoire() + voix_journal()
        ],
    }
