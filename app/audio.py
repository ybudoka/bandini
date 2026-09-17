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
    _e("poing_americain", "Coup de poing américain", variantes=2, duree_s=0.8, volume=0.26,
       prompt="a single punch with brass knuckles landing hard on a body, a sharp "
              "meaty smack with a hard metallic knock of brass on bone underneath, "
              "dry close-up, no reverb, no voices, no music"),
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
    # ⚠️ Un REFUS, pas une alarme. Ce son part a chaque « PAS ASSEZ », chaque
    # commerce ferme, chaque menu qu'on annule : c'est le bruitage d'interface
    # qu'on entend le plus souvent apres le clic. Le buzzer electronique le
    # disait comme une faute — retour de Martin, 15 sept. 2026 : « beaucoup
    # trop agressif » —, et il sortait plus fort que le clic de menu (0,56
    # contre 0,38) pour dire qu'il ne se passe RIEN. Meme famille que `menu`,
    # une note plus bas, plus sourde, et plus courte.
    _e("erreur", "Refus", duree_s=0.5, volume=0.3, influence=0.75,
       prompt="a soft muted user interface refusal, two quiet low blips "
              "descending gently, rounded and dull, very short, dry, "
              "no buzzer, no rasp, no alarm, no distortion, no music"),
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
    # Le tramway (M12) : sa cloche quand les portes se ferment, et quand quelqu'un est
    # sur ses rails — il ne freine pas, il sonne.
    _e("cloche_tram", "Cloche du tramway", duree_s=1.5, volume=0.3, influence=0.7,
       prompt="a vintage streetcar foot bell rung twice, ding ding, bright brass "
              "clang with a short ring, outdoors on a city street, no voices, "
              "no music"),
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
    # --- Ça travaille : les chantiers (2e vague, 16 sept. 2026) ---------------
    # ⚠️ Des sons POSÉS dans le monde (`Son.SFX.chantier`) : ils partent de la
    # machine, plus faibles de loin — et JAMAIS la nuit : un chantier se tait à
    # la tombée du jour, et ses machines s'arrêtent avec lui. Chacun s'accroche
    # à un geste qu'on VOIT quand il y en a un : la boule au coup de sa pose
    # `frappe`, le godet quand la pelle racle. Le marteau-piqueur, le bip de
    # recul, le marteau et la scie sont ce qu'on ne voit pas derrière la
    # palissade — ils reviennent sur une horloge, jamais tous ensemble.
    _e("boule", "Boule de démolition", variantes=2, duree_s=2.0, volume=0.6,
       influence=0.5,
       prompt="a heavy steel wrecking ball smashing into a brick wall, one deep "
              "booming impact, then bricks and concrete chunks crumbling and "
              "tumbling down, dust, outdoors, no voices, no music"),
    _e("marteau_piqueur", "Marteau-piqueur", duree_s=2.5, volume=0.35,
       influence=0.6,
       prompt="a pneumatic jackhammer breaking a concrete slab, one rapid "
              "rattling burst of about two seconds then it stops, outdoors "
              "construction site, no voices, no music"),
    _e("godet", "Godet de pelle mécanique", variantes=2, duree_s=2.0, volume=0.35,
       influence=0.5,
       prompt="an excavator bucket scraping into gravel and broken bricks, then "
              "dumping the load with a rattling pour of stones, hydraulic hiss, "
              "outdoors, no voices, no music"),
    # ⚠️ PAS DE BIP DE RECUL ICI, et c'est mesuré : trois générations (« evenly
    # spaced beeps », puis les durées en toutes lettres, puis « dry, no reverb,
    # clean silence between each beep » à 1000 Hz) ont rendu trois SIFFLEMENTS
    # CONTINUS — à l'enveloppe par tranches de 10 ms, pas un seul silence entre
    # deux bips. Un bip de recul est de toute façon un ton électronique : il est
    # synthétisé dans `son.js` (`REPLI_CHANTIER.bip_recul`), et ne coûte rien.
    _e("marteau", "Coups de marteau", variantes=2, duree_s=1.2, volume=0.28,
       influence=0.6,
       prompt="a carpenter driving a nail into a wooden framing stud with a "
              "steel hammer, three quick sharp blows, outdoors, no voices, "
              "no music"),
    _e("scie", "Scie circulaire", duree_s=2.0, volume=0.25, influence=0.6,
       prompt="a circular saw spinning up and cutting through a wooden plank, "
              "high whining buzz, then spinning down, outdoors, no voices, "
              "no music"),
    # Les éboueurs (M12) : le bras du camion lève le bac, le secoue au-dessus de la
    # benne, le repose. Posé dans le monde comme les sons de chantier.
    _e("benne", "Bras du camion à ordures", duree_s=3.0, volume=0.35, influence=0.55,
       prompt="a garbage truck automated side arm lifting a plastic wheeled bin, "
              "hydraulic whine, the bin shaken and trash tumbling into the metal "
              "hopper, then the bin set back down on the curb, outdoors, "
              "no voices, no music"),
    # Le traversier (M12) : sa corne au départ et à l'arrivée. Posée dans le monde,
    # on l'entend de loin sur l'eau.
    _e("corne", "Corne du traversier", duree_s=4.0, volume=0.45, influence=0.6,
       prompt="a large car ferry ship horn sounding two long deep blasts across a "
              "calm harbour, low booming tone echoing over the water, outdoors, "
              "no voices, no music"),
    # La rumeur : une BOUCLE, dont le volume suit la distance au chantier le
    # plus proche. C'est elle qui dit « il y a un chantier par là » avant qu'on
    # le voie.
    # La tempete de neige (M12) : le vent, une BOUCLE dont le volume suit la tempete.
    _e("tempete", "Vent de tempete", duree_s=8.0, volume=0.35, boucle=True, influence=0.45,
       prompt="a winter blizzard wind howling and gusting through city streets at "
              "night, snow hissing, steady intensity, seamless loop, no voices, "
              "no music"),
    _e("chantier", "Rumeur de chantier", duree_s=6.0, volume=0.3, boucle=True,
       influence=0.45,
       prompt="distant construction site ambience, a diesel machine engine "
              "rumbling steadily with faint metal clanks, seamless loop, "
              "no beeps, no voices, no music"),
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

#: --- LA MUSIQUE, JOUEE PLUTOT QU'ECRITE ------------------------------------
#:
#: ⚠️ Demande de Martin (14 sept. 2026) : « je veux que toutes les musiques
#: soient des musiques generees par IA ». `musique.py` ecrit quinze pieces en
#: NOTES — le theme du menu, deux stations de char, cinq ambiances de district,
#: la poursuite, la bagarre et les cinq pieces du musicien de rue — et il
#: annonce cette porte depuis le premier jour, mot pour mot : « le jour ou
#: Martin veut une vraie piece jouee par de vrais instruments, elle se posera
#: PAR-DESSUS comme les radios ». C'est ce qui se passe ici.
#:
#: ⚠️ Les notes ne DISPARAISSENT pas, et ce n'est pas de la sentimentalite :
#: c'est la regle 1 de ce fichier. Un depot frais, une generation ratee, un
#: reseau coupe — `exporter()` ne declare que les fichiers presents, et le
#: sequenceur reprend le morceau exactement la ou il est ecrit. Le jeu n'a
#: jamais de trou de musique.
#:
#: ⚠️ Le `slug` est celui du morceau de `musique.py`, pas un nom neuf : c'est
#: ce qui fait que le chef d'orchestre, le bouton RADIO du camion, l'hysteresis
#: aux frontieres et l'echelle de priorite n'apprennent RIEN. Ils demandent
#: `amb_quais` comme avant ; c'est `son.js` qui sait si ca sort d'un fichier ou
#: d'un oscillateur. Un juge exige que les deux listes se recouvrent exactement.
#:
#: ⚠️ `volume` ne peut pas etre celui du morceau ecrit. Dans le sequenceur, le
#: volume du morceau MULTIPLIE celui de chaque voix (0,11 a 0,45) : `titre` a
#: 0,85 sort a un dixieme de l'echelle. Un mp3, lui, arrive normalise. Les deux
#: chiffres vivent donc cote a cote (`volume` pour les notes, celui-ci pour le
#: fichier) et le navigateur prend celui de la source qui joue.


class Piece(TypedDict):
    slug: str
    prompt: str
    duree_s: int
    volume: float


def _m(slug: str, prompt: str, *, duree_s: int, volume: float) -> Piece:
    return Piece(slug=slug, prompt=prompt, duree_s=duree_s, volume=volume)


#: ⚠️ Chaque prompt REPREND la fiche du morceau ecrit : meme tonalite, meme
#: tempo, meme intention. Sans ca on ne remplace pas une musique, on en met une
#: autre — et l'hysteresis, la queue et l'echelle ont ete reglees sur celles-la.
MUSIQUES: list[Piece] = [
    # Le menu. La grille de jazz la plus banale du monde, et c'est voulu : elle
    # doit tourner sous un menu sans jamais accrocher l'oreille.
    _m("titre",
       "slow smoky jazz trio at 92 bpm in A minor, walking upright bass, brushed "
       "snare, muted trumpet melody over warm electric piano chords, foggy "
       "harbour town at night, melancholic but calm, no vocals, seamless loop",
       duree_s=45, volume=0.5),

    # L'OUVERTURE. ⚠️ Trente secondes, comme la boucle ecrite : elle joue une
    # fois et demie pendant que le narrateur parle, puis la ville reprend. Un
    # morceau plus long ne se serait jamais entendu en entier ; un plus court se
    # serait entendu reboucler au milieu d'une phrase.
    _m("ouverture",
       "slow mournful cinematic opening at 64 bpm in A minor, long sustained "
       "low strings, distant foghorn, sparse felt piano, a night bus arriving in "
       "a wet harbour town, unresolved and heavy, no drums, no vocals, loopable",
       duree_s=30, volume=0.44),

    # --- Les deux stations de char (le bouton RADIO peut tomber dessus) ------
    _m("station_camion",
       "mid-tempo country rock instrumental at 104 bpm in C major, twangy "
       "telecaster, pedal steel, steady trucker backbeat, upright bass, the kind "
       "of tune a long-haul radio plays at 4 in the morning, no vocals, loopable",
       duree_s=45, volume=0.45),
    _m("station_remorqueuse",
       "slow dirty blues instrumental at 84 bpm in A minor, dry slide guitar, "
       "brushed drums, walking bass, hammond organ pad, scrapyard at dusk, "
       "no vocals, loopable",
       duree_s=45, volume=0.42),

    # --- Les cinq ambiances de district (ce qu'on entend a pied) ------------
    # ⚠️ Elles jouent SOUS la rumeur de la foule, les moteurs et les voix : pas
    # de batterie, pas de melodie qui accroche. Une musique de district qu'on
    # remarque est une musique de district ratee.
    _m("amb_faubourg",
       "sparse melancholic ambient score at 68 bpm in A minor, soft felt piano "
       "notes, low analog synth pad, distant foghorn, wet streets of an old "
       "working-class neighbourhood, no drums, no vocals, seamless loop",
       duree_s=60, volume=0.3),
    _m("amb_erables",
       "calm warm ambient score at 74 bpm in D major, gentle acoustic guitar "
       "harmonics, soft strings pad, lazy sunday morning in a quiet leafy "
       "suburb, nothing happens, no drums, no vocals, seamless loop",
       duree_s=60, volume=0.28),
    _m("amb_shop",
       "cold industrial ambient drone at 88 bpm in D minor, low detuned synth "
       "bass, distant metal clangs, hum of empty factories, bleak and hard, "
       "no melody, no drums, no vocals, seamless loop",
       duree_s=60, volume=0.3),
    _m("amb_quais",
       "wide slow maritime ambient score at 64 bpm in F minor, deep foghorn "
       "notes, creaking ropes, low cello drone, mist over harbour water, "
       "no drums, no vocals, seamless loop",
       duree_s=60, volume=0.3),
    _m("amb_pointe",
       "airy open ambient score at 80 bpm in E major, bright sustained strings, "
       "soft wind chimes, wind through trees on a headland above the sea, "
       "hopeful, no drums, no vocals, seamless loop",
       duree_s=60, volume=0.3),

    # --- Les deux musiques d'ETAT -------------------------------------------
    # ⚠️ Le seul moment ou la musique a le droit de prendre toute la place. Elle
    # doit s'entendre SOUS les sirenes : c'est pour ca qu'elle est rythmique et
    # basse plutot que melodique.
    _m("mus_poursuite",
       "urgent driving chase instrumental at 148 bpm in E minor, relentless "
       "sixteenth-note synth bass, hard kick and snare, stabbing brass, police "
       "pursuit through a city at night, tense, no vocals, seamless loop",
       duree_s=40, volume=0.5),
    _m("mus_bagarre",
       "heavy aggressive fight instrumental at 132 bpm in G minor, distorted "
       "guitar riff, pounding toms, dirty bass, street brawl, raw and physical, "
       "no vocals, seamless loop",
       duree_s=40, volume=0.48),

    # --- Les cinq pieces du musicien de rue ---------------------------------
    # ⚠️ UN SEUL HOMME AVEC UNE GUITARE. La fiche du morceau ecrit le dit en
    # majuscules — « deux voix, pas quatre » : un gars tout seul sur un trottoir
    # n'a pas de batteur derriere lui. Un prompt qui laisse arriver un groupe
    # donne une musique qui ne colle plus a ce qu'on VOIT, et c'est tout
    # l'interet du musicien de rue.
    _m("rue_complainte",
       "solo acoustic nylon guitar lament at 76 bpm in E minor, one street "
       "busker playing alone, fingerpicked chords and a sad simple melody, "
       "close mic, no other instruments, no drums, no vocals, loopable",
       duree_s=30, volume=0.5),
    _m("rue_reel",
       "solo acoustic steel string guitar reel at 132 bpm in G major, one busker "
       "playing fast flatpicked quebecois dance tune, foot tapping on pavement, "
       "no other instruments, no drums, no vocals, loopable",
       duree_s=30, volume=0.5),
    _m("rue_blues",
       "solo acoustic resonator guitar twelve-bar blues at 92 bpm in A minor, "
       "one busker playing alone on a sidewalk, thumb bass and slide licks, "
       "no other instruments, no drums, no vocals, loopable",
       duree_s=36, volume=0.5),
    _m("rue_valse",
       "solo acoustic guitar waltz in three four time at 116 bpm in D major, one "
       "busker playing alone, bass note on one and two strums after, old "
       "european fairground feel, no other instruments, no drums, no vocals, "
       "loopable",
       duree_s=30, volume=0.5),
    _m("rue_ballade",
       "very slow solo acoustic guitar ballad at 68 bpm in A minor, one busker "
       "playing alone, few notes, long silences, heard from around a corner, "
       "no other instruments, no drums, no vocals, loopable",
       duree_s=30, volume=0.46),

    # --- Les quatre musiques de commerce (M15 / demande de Martin) ----------
    # ⚠️ 45 s comme les autres. J'avais d'abord ecrit 20 s pour tenir sous un
    # plafond de 6 Mo ; Martin a tranche (« tu peux augmenter les budgets... pas
    # de sens ») et il a raison — ce plafond-la etait le NOTRE, pas celui du
    # telephone : les musiques ne se telechargent qu'a l'entree de la piece,
    # jamais au demarrage. Une boucle de 20 s dans une boutique s'entend
    # reboucler ; une de 45 s ne s'entend pas.
    _m("com_armurerie",
       "sparse tense instrumental at 72 bpm in C minor, low sustained cello drone, "
       "muted plucked guitar notes, distant room tone, a gun shop back counter, "
       "unsettling but quiet, no drums, no vocals, seamless loop",
       duree_s=45, volume=0.30),
    _m("com_boutique",
       "light breezy instrumental at 104 bpm in A major, clean electric piano, "
       "soft brushed drums, warm bass, the radio playing in a small clothing "
       "boutique, cheerful and unobtrusive, no vocals, seamless loop",
       duree_s=45, volume=0.32),
    _m("com_casse_croute",
       "warm vintage diner jukebox instrumental at 96 bpm in E major, reverb "
       "electric guitar, upright bass, shuffle brushes, 1950s greasy spoon at "
       "noon, slightly worn tape feel, no vocals, seamless loop",
       duree_s=45, volume=0.33),
    _m("com_garage",
       "greasy garage rock instrumental at 118 bpm in D minor, fuzzy electric "
       "guitar riff, dry drums, driving bass, a paint-spattered radio at the back "
       "of a body shop, no vocals, seamless loop",
       duree_s=45, volume=0.31),

]


def nom_fichier_musique(slug: str) -> str:
    return f"musique-{slug}.mp3"


def chemin_musique(slug: str) -> Path:
    return RACINE_STATIQUE / DOSSIER / nom_fichier_musique(slug)


def piece_par_slug(slug: str) -> Piece | None:
    for piece in MUSIQUES:
        if piece["slug"] == slug:
            return piece
    return None


def slugs_de_musique() -> set[str]:
    """Les morceaux que le jeu joue VRAIMENT, tels que `musique.py` les rend."""
    return {m["slug"] for m in musique.exporter()}


def musiques_manquantes() -> list[Piece]:
    """Les pieces qu'il reste a faire jouer par l'IA. Tant qu'une manque, son
    morceau ecrit en notes la remplace — le jeu n'attend rien.

    ⚠️ ON NE GENERE QUE CE QUE LE JEU JOUE. Une piece dont le slug ne
    correspond a aucun morceau de `musique.py` — une faute de frappe, un
    morceau renomme, une piece ecrite en avance pendant qu'une autre session
    ecrit encore le morceau — serait un fichier PAYE que personne ne jouerait
    jamais. Le filtre coute une ligne ; la generation coute des credits."""
    connus = slugs_de_musique()
    return [p for p in MUSIQUES
            if p["slug"] in connus and not chemin_musique(p["slug"]).is_file()]


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
    # --- LA RADIO PARLE (M15, 2e vague) -----------------------------------
    # ⚠️ **L'AME D'UNE RADIO, C'EST CE QUI SE DIT ENTRE LES TOUNES.** Les cinq
    # stations sont des boucles instrumentales depuis M7 ; le mecanisme pour y
    # glisser une voix existe deja en entier — `Son.Voix`, le ducking, le filtre
    # du combine. Il ne manquait que les clips.
    #
    # ⚠️ **Ce sont des VOIX, pas une troisieme sorte de son**, et c'est ce qui
    # rend la vague petite : meme generation, meme export, meme chargement, meme
    # ducking. Le `genre` separe deja les banques (homme, femme, crieur, brume) —
    # il en separe simplement deux de plus.
    #
    # ⚠️ **Personne au Choc** : juste sa musique. C'est le PROPOS de la station,
    # et une station qui se tait au milieu de quatre qui parlent dit quelque
    # chose qu'aucun clip ne dirait.
    {"slug": "brume_nuit_r", "texte": "Vous écoutez La Brume, cent trois virgule sept. Il est minuit passé sur le port.",
     "genre": "radio_brume", "voix": VOIX_BRUME, "volume": 0.62, "style": 0.35, "stabilite": 0.6},
    {"slug": "brume_pluie_r", "texte": "La pluie rentre par la baie. Restez au chaud, on continue.",
     "genre": "radio_brume", "voix": VOIX_BRUME, "volume": 0.62, "style": 0.35, "stabilite": 0.6},
    {"slug": "brume_demandes_r", "texte": "Une petite dernière avant les nouvelles, pour ceux qui travaillent de nuit.",
     "genre": "radio_brume", "voix": VOIX_BRUME, "volume": 0.62, "style": 0.35, "stabilite": 0.6},
    {"slug": "taxi_bonjour_r", "texte": "Taxi-Radio, votre station! On est en ondes, pis y fait beau à Baie-des-Brumes!",
     "genre": "radio_taxi", "voix": VOIX_CRIEUR, "volume": 0.66, "style": 0.65, "stabilite": 0.35},
    {"slug": "taxi_trafic_r", "texte": "Ça bouchonne su'l pont, mes amis. Prenez donc la rue des Érables.",
     "genre": "radio_taxi", "voix": VOIX_CRIEUR, "volume": 0.66, "style": 0.65, "stabilite": 0.35},
    {"slug": "taxi_merci_r", "texte": "Un gros merci à nos commanditaires, pis on remet ça!",
     "genre": "radio_taxi", "voix": VOIX_CRIEUR, "volume": 0.66, "style": 0.65, "stabilite": 0.35},
    # --- Les pubs. ⚠️ **ELLES CHANGENT QUAND TU ACHETES LE COMMERCE**, et c'est
    # cette ligne-la qui fait que ca vaut la peine, pas une autre : entendre son
    # propre commerce annonce a la radio, dans un char qu'on vient de voler, est
    # exactement ce que M15 promet. Une par commerce, plus sa jumelle « a toi ».
    {"slug": "pub_gus_r", "texte": "Chez Gus! Le meilleur smoked meat en ville, depuis mille neuf cent soixante-deux.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
    {"slug": "pub_gus_a_toi_r", "texte": "Chez Gus, sous nouvelle administration! Passez voir le nouveau proprio.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
    {"slug": "pub_rosa_r", "texte": "Boutique Rosa, rue du Faubourg. Habillez-vous comme du monde.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
    {"slug": "pub_rosa_a_toi_r", "texte": "Boutique Rosa a changé de mains! Venez rencontrer le nouveau proprio.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["femme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
    {"slug": "pub_tipaul_r", "texte": "Dépanneur Ti-Paul, ouvert tard. Bière frette, loterie, pis du bon café.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
    {"slug": "pub_tipaul_a_toi_r", "texte": "Le Dépanneur Ti-Paul est vendu! Le nouveau proprio vous attend.",
     "genre": "pub", "voix": VOIX_PAR_GENRE["homme"], "volume": 0.66, "style": 0.6, "stabilite": 0.4},
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


def voix_ouverture() -> list[dict]:
    """Les quatre phrases de l'ouverture, dites par le narrateur du Clairon.

    ⚠️ Exactement la meme mecanique que `voix_journal()` : le texte vit dans
    `missions.py`, le slug suit la place de la ligne, et le mp3 manquant laisse
    la phrase s'afficher sans voix. C'est ce qui permet d'ecrire l'ouverture,
    de la jouer et de la juger AVANT de depenser un credit.
    """
    from . import missions
    perso = missions.personnage("narrateur")
    if perso is None:
        raise ValueError("le narrateur manque a missions.PERSONNAGES")
    return [{"slug": ligne["slug"], "texte": ligne["texte"], "genre": perso["genre"], "voix": perso["voix"],
             # ⚠️ Un peu plus fort que la manchette : elle joue sur une musique,
             # pas dans le silence d'un encadre.
             "volume": 0.92, "histoire": True, "qui": ligne["qui"], "mission": ligne["mission"],
             "partie": ligne["partie"], "telephone": False}
            for ligne in missions.repliques_ouverture()]


def toutes_les_voix() -> list[dict]:
    return list(VOIX) + voix_histoire() + voix_journal() + voix_ouverture()


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
    attendus |= {nom_fichier_musique(p["slug"]) for p in MUSIQUES}
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

#: LES COUPS DES AUTRES S'ENTENDENT DE LA OU ILS SONT.
#:
#: ⚠️ Retour de Martin (16 sept. 2026) : « les cris doivent etre moins fort si on
#: est loin et devenir plus fort quand on s'approche », puis « meme que je veux
#: pas entendre quand on les voit pas ». Le grognement d'un coup encaisse
#: (`touche`) et le coup lui-meme (`batte`, `coup`...) partaient au PLEIN
#: volume, ou que ce soit — et la rixe de gangs nait expres hors de l'ecran :
#: on entendait six hommes se battre sans en voir un seul.
#:
#: La regle, pour tout ce que frappe ou encaisse QUELQU'UN D'AUTRE que le
#: joueur : hors de l'ecran, rien ; a l'ecran, le volume baisse en ligne droite
#: avec la distance au joueur. Le joueur s'entend toujours plein volume.
COUPS_DES_AUTRES = {
    # ⚠️ Un peu plus que la demi-diagonale de l'ecran (480 x 270 : 275 px),
    # pour qu'un coin de l'ecran s'entende encore un peu. Au bord gauche ou
    # droit (240 px), il reste un cinquieme du volume ; a deux pas, presque tout.
    "portee_px": 300,
    # Un homme dont le milieu vient de passer le bord se voit encore a moitie.
    "marge_px": 8,
}


def exporter() -> dict:
    """⚠️ Ne declare QUE les fichiers presents : le navigateur ne demande jamais
    un son qui n'existe pas, et se rabat sur la synthese sans un 404."""
    return {
        "dossier": DOSSIER,
        "parole": dict(PAROLE),
        "rumeur": dict(RUMEUR),
        "coups_des_autres": dict(COUPS_DES_AUTRES),
        # LA MUSIQUE. Chaque morceau part de `app/musique.py` (les notes, le
        # filet) et recoit ici le mp3 genere quand il est sur le disque — plus
        # le volume qui va AVEC ce fichier, qui n'est pas celui des notes.
        # ⚠️ `fichier: null` n'est pas un manque : c'est le sequenceur qui
        # joue, et le navigateur ne demande jamais un mp3 qui n'existe pas.
        "musiques": [
            {**m, "fichier": nom_fichier_musique(m["slug"])
                             if chemin_musique(m["slug"]).is_file() else None,
             "volume_fichier": (piece_par_slug(m["slug"]) or {}).get("volume")}
            for m in musique.exporter()
        ],
        # ⚠️ L'ECHELLE de qui gagne, et les reglages de la musique d'etat. Ils
        # sont ECRITS UNE FOIS, en Python : le navigateur lit sa priorite, il
        # ne l'invente pas. Sans ca, chaque endroit du JS aurait la sienne.
        "echelle": dict(musique.ECHELLE),
        "musique": dict(musique.MUSIQUE),
        "ambiances_de_district": dict(musique.AMBIANCES_DE_DISTRICT),
        # ⚠️ QUEL MORCEAU JOUE DANS QUELLE PIECE. Le navigateur lit, il ne
        # devine pas : une piece absente de cette carte reste SILENCIEUSE, et
        # c'est voulu — le poste, l'hopital et la planque ne sont pas des
        # commerces, et le silence y dit ce qu'aucune toune ne dirait.
        "musiques_de_commerce": dict(musique.MUSIQUES_DE_COMMERCE),
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
            for v in voix_histoire() + voix_journal() + voix_ouverture()
        ],
    }
