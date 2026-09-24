"""COMMENT UNE REPLIQUE SE DIT — les pauses, l'emotion, et le temps mort de la fin.

Le texte d'une replique vit ou il a toujours vecu (`audio.VOIX`, `missions.py`,
`journal.py`) : c'est lui que la boite de dialogue affiche. Ce module-ci ne
porte que la maniere de le DIRE, et c'est ce texte-la qu'ElevenLabs recoit.

    « Ton oncle Rocco est mort le mois passé. Il te laisse son garage, sa planque, pis son nom. »
    « [somber] Ton oncle Rocco est mort le mois passé. Il te laisse son garage, sa planque… pis son nom. »

⚠️ **Demande de Martin, 16 sept. 2026** : « regénère toutes les voix en mettant
des pauses dans le texte et de l'émotion, et un léger temps mort à la fin pour
éviter les fins coupées ».

⚠️ **Deux textes, UNE phrase.** Le texte joue ne change pas un mot : il ajoute
des balises d'emotion entre crochets (`[sighs]`), des silences (« … », « — ») et
de la ponctuation. Un juge (`test_interpretation.py`) retire tout ca et exige
les memes mots que la boite — une voix qui dit autre chose que ce qu'on lit est
pire qu'une voix plate. ⚠️ Le jeu d'une replique de MISSION vit dans le fichier de
la mission, colle a la replique (`jeu=`) : une replique inseree au milieu n'emporte
plus le jeu de sa voisine (le slug suit la PLACE, et le jeu d'avant se rangeait par
slug). Ce module n'a gardé que ce qui n'est pas une mission — passants, repos,
journal, ouverture — et rassemble le reste (`JEU`, tout en bas de sa table).

⚠️ **Pourquoi eleven_v3 et plus eleven_multilingual_v2.** v2 ne connait que ses
curseurs (`style`, `stabilite`) : ils poussent TOUTE la replique dans un sens,
ils ne font pas soupirer au milieu d'une phrase. v3 lit des balises d'emotion
dans le texte. Ses deux pieges, mesures le 16 sept. (un essai, puis les 83) :

- **les balises sont en ANGLAIS**, meme pour une phrase en francais — ce sont
  des indications de jeu, pas des mots a dire ;
- **une pause pese lourd** : « … » suivi de `[sighs]` au milieu d'une phrase a
  fait un trou de DEUX secondes, et la phrase a double de longueur (4,9 s ->
  10,2 s). Sur la premiere generation complete, neuf trous de plus d'une
  seconde : SEPT sur une replique qui changeait de balise en chemin, un sur
  « Lui… » (un mot seul, puis « … »), et le dernier etait une seconde de vide
  DEVANT « Excusez-moi ». D'ou la regle d'ecriture : une balise par replique
  des qu'elle respire, en tete ; « … » pour le seul endroit ou la phrase
  respire vraiment, jamais apres un mot seul.
  v3 ne connait pas `<break time>` (c'est du v2) : un juge l'interdit.

⚠️ **Les fins coupees venaient de DEUX endroits**, et regenerer ne reparait
que le premier :

1. le fichier : v2 comme v3 s'arretent sur la derniere syllabe — les 19
   repliques du narrateur finissaient a 10-47 ms du dernier son. C'est
   `TEMPS_MORT_S`, pose par `scripts/audio_elevenlabs.py` apres la generation
   (on ne le demande pas au modele : il le rendrait en souffle de piece, et pas
   toujours) ;
2. le jeu : une ligne de dialogue passait a la suivante apres
   `90 + 3 x longueur` images, voix ou pas — et la suivante COUPE la voix. Neuf
   repliques de mission y perdaient deja leur fin (`bouchard-m4-6` : 7,06 s de
   voix, 5,65 s de ligne). Une replique qui respire est plus longue : sans
   corriger `majCinema` (`histoire.js`), les pauses auraient coupe tout le reste.
"""

from __future__ import annotations

import re

#: Le modele. ⚠️ Le seul qui lise les balises d'emotion — v2 les dirait a voix haute.
MODELE = "eleven_v3"

#: ⚠️ v3 ne connait que TROIS stabilites : 0 (creatif), 0,5 (naturel), 1 (robuste).
#: Le creatif joue plus fort mais invente — des mots, des rires — et personne ne
#: peut l'entendre avant Martin. Le naturel suit les balises sans deraper.
#: Les `style` et `stabilite` d'`audio.VOIX` etaient des reglages de v2 : v3 n'a
#: pas de `style`, et l'emotion se dit maintenant ici, replique par replique.
STABILITE = 0.5

#: Le temps mort ajoute apres le dernier son. ⚠️ « Leger » : assez pour que la
#: derniere syllabe retombe avant la replique suivante, pas assez pour qu'on
#: attende. Le dialogue enchaine sur la fin du fichier (`Voix.parler` -> `fin`).
TEMPS_MORT_S = 0.35

#: ⚠️ LE SILENCE QUE v3 AJOUTE DE LUI-MEME — mesure sur la premiere generation
#: complete (16 sept. 2026) : jusqu'a 2,9 s de zeros apres la derniere syllabe
#: (`josee-m5-2`), une seconde de vide avant « Excusez-moi », et neuf repliques
#: avec un trou de 1,2 a 1,6 s au milieu. Un dialogue qui attend sa voix
#: attendait donc du vide. La finition rogne les deux bords a `BORD_S` et
#: ramene toute pause plus longue a `PAUSE_MAX_S` : la pause reste, le trou part.
#:
#: Le seuil : sur les fichiers normalises, le silence tombe entre -45 et -60 dB
#: (bruit de piece du narrateur) ou a -85 (numerique), un souffle ou un soupir
#: entre -35 et -45. ⚠️ -48 d'abord, et c'etait trop bas : sur l'essai du
#: narrateur, le bruit de piece d'un trou de deux secondes flottait a -47/-50,
#: et la moindre fenetre au-dessus du seuil remettait le compteur a zero — rien
#: n'etait ramene. Une parole ne reste jamais 0,7 s sous -45 : seules les vraies
#: pauses sont touchees.
SEUIL_SILENCE_DB = -45.0
BORD_S = 0.05
PAUSE_MAX_S = 0.7

#: Le fondu pose sur les derniers echantillons AVANT le temps mort : si le modele
#: a coupe en pleine onde, c'est ce qui evite le clic.
FONDU_FIN_S = 0.012

#: Le niveau de toutes les voix, en LUFS integres. ⚠️ Mesure avant : les 83
#: fichiers allaient de -32 a -15 LUFS (17 dB d'ecart : Bouchard a -21, Ti-Guy a
#: -15), mediane -19,6. On vise la mediane : le melange ne bouge pas en moyenne,
#: il se resserre. Le `volume` du catalogue redevient ce qu'il dit.
NIVEAU_LUFS = -19.0

#: ... sans jamais depasser ce pic : un cri normalise au niveau d'un murmure
#: monterait sinon au-dessus de 0 dBFS. Le gain s'arrete au premier des deux.
PIC_MAX_DBFS = -1.0

#: ⚠️ LE LIMITEUR. Une replique dite bas avec UNE consonne qui claque ne montait
#: pas au niveau des autres : le gain s'arretait au pic. Mesure a la premiere
#: egalisation : `bouchard-m4-2` (« [quietly] »), pic a -4,4 dBFS, sortie a -23,2
#: LUFS — 4 dB sous le reste. Un limiteur rabat ces pics brefs a `LIMITE_DBFS`, et
#: le gain peut pousser au plus `LIMITEUR_MAX_DB` dedans : au-dela, un limiteur
#: s'entend. Sa marge sous `PIC_MAX_DBFS` est pour l'encodeur, qui tremble.
LIMITE_DBFS = -3.0
LIMITEUR_MAX_DB = 6.0

#: ⚠️ LES VOIX QUI SONNENT DANS UNE PIECE — retour de Martin apres ecoute (16 sept.
#: 2026) : « caverneuses », puis « je les veux sans reverberation ». Mesure : la
#: vitesse de chute du son a la fin des syllabes (95e centile, dB/s) — une piece
#: la borne. Etalonnee en ajoutant soi-meme une reverberation a une voix seche
#: (534 dB/s -> 315 a RT 0,4 s -> 300 a RT 0,8 s).
#:
#: ⚠️ REGENERER NE SECHE RIEN : sur la meme phrase de Mme Thibodeau, v3 en
#: stabilite 0, 0,5 et 1, et avec une similarite basse, restent entre 294 et
#: 350 ; v2 et turbo montent a 423-443 mais perdent les balises d'emotion. Ce
#: qui seche, c'est l'ISOLATEUR d'ElevenLabs (`elevenlabs_voice_isolation`) : sur
#: la voix seche reverberee a RT 0,4 s, il est revenu de 315 a 532 (534 avant).
#:
#: ⚠️ ET IL NE SECHE QUE CE QUI EST MOUILLE. Passe sur les cinq voix les plus
#: lentes (62 repliques), mesure fichier fini contre fichier fini :
#:   - Julia 347 -> 373 et le narrateur 428 -> 471 : la piece part, le timbre
#:     reste (Julia gagne meme 6 dB d'air au-dessus de 8 kHz) ;
#:   - Amelie 432 -> 432, Felix 436 -> 438, Leo 443 -> 447 : RIEN a retirer —
#:     leur ecart avec v2 etait le debit de v3, pas une piece — et Felix et Leo
#:     y perdaient 1,5 a 4,6 dB d'aigus. Les secher les aurait ETOUFFES.
#: Ce qui reste a Julia (373, contre 510+ pour une voix seche) n'est pas la piece :
#: c'est sa voix, rauque, aux fins de mots soufflees — meme v2 isolee plafonne a 441.
#:
#: Les noms sont ceux du catalogue (`audio.py`, `missions.PERSONNAGES`).
VOIX_A_SECHER = frozenset({
    "Julia",                        # Mme Thibodeau, la Brume, La Brume a la radio
    "annonceur centre d'achat 1",   # le narrateur : ouverture et journal
})

#: L'isolateur refuse sous ce seuil (« below the minimum of 4.6 seconds », mesure) :
#: une replique plus courte part allongee de silence, et revient recoupee.
ISOLATION_MIN_S = 4.6

#: Ce que porte un fichier seche, dans son etiquette `comment` : c'est le fichier
#: qui prouve qu'il est passe par l'isolateur, pas la liste qui le promet.
MARQUE_SECHEE = "voix isolee"

#: ⚠️ L'EGALISATION — retour de Martin : « caverneuses ou etouffees ». Mesure (16
#: sept. 2026), par tiers d'octave, chaque replique v3 contre la MEME replique en
#: v2, mediane par voix : ce n'est pas la finition (master et fichier fini ont le
#: meme spectre a 0,3 dB pres), c'est v3 qui a deplace le timbre —
#:   - Julia +3 a +7 dB entre 100 et 250 Hz ; en haut -4 a -9 dB avant l'isolateur,
#:     encore -2 a -5 apres (il lui a rendu de l'air) ;
#:   - Amelie +6 a +18 dB entre 100 et 315 Hz, et +5 a +10 au-dessus de 2 kHz ;
#:     Jeanne Mance +6 a +11 entre 100 et 200 Hz, et +4 a +6 au-dessus de 3 kHz ;
#:   - Leo -5 a -9 dB entre 3 et 6 kHz : etouffe ;
#:   - Felix, le narrateur, Khaivan, Tremblay : a +-3 dB, rien a corriger.
#: D'ou des coupes et des rehausses DE LA TAILLE DE L'ECART, jamais plus. Verifie
#: sur dix repliques ecoutees en A/B : Mme Thibodeau repasse de 273 a 440 Hz de
#: centroide (482 en v2), Ti-Guy et le narrateur ne bougent pas.
#:
#: Le passe-haut, lui, est pour tout le monde : rien d'utile ne parle sous 85 Hz
#: chez un homme ni sous 120 Hz chez une femme, et c'est la que « caverneux » vit.
PASSE_HAUT_HOMMES = "highpass=f=85:p=2"
PASSE_HAUT_FEMMES = "highpass=f=120:p=2"
EGALISATION: dict[str, str] = {
    "Julia": PASSE_HAUT_FEMMES + ",equalizer=f=180:t=o:w=1.5:g=-5,highshelf=f=3500:g=2.5",
    "Amélie - Young, Confident and Friendly":
        # ⚠️ La coupe a 5 kHz est venue APRES : graves retires, Amelie ressortait a
        # +7,7 dB au-dessus de v2 entre 4 et 8 kHz — v3 l'avait deja rendue brillante.
        PASSE_HAUT_FEMMES + ",equalizer=f=150:t=o:w=1.2:g=-8,equalizer=f=400:t=o:w=1:g=-5"
        ",equalizer=f=5000:t=o:w=1.5:g=-4",
    # La repartitrice de la police : une voix de femme, le passe-haut des femmes.
    # Le scanner la coupe de toute facon sous 300 Hz (`Son.Ondes`).
    "Caroline - Soft Quebec accent": PASSE_HAUT_FEMMES,
    "Jeanne Mance - Charming, Clear and Young":
        PASSE_HAUT_FEMMES + ",equalizer=f=150:t=o:w=1.2:g=-6,equalizer=f=4000:t=o:w=1.5:g=-4",
    "Léo - Français québécois": PASSE_HAUT_HOMMES + ",highshelf=f=3000:g=5",
    "Alexandre - Authentic French Canadian": PASSE_HAUT_HOMMES + ",equalizer=f=110:t=o:w=1:g=-6",
}

#: Les balises de TON — l'emotion proprement dite. ⚠️ Elles sont separees des
#: balises de CORPS pour une regle : CHAQUE replique en porte au moins une. Un
#: simple soupir (`[sighs]`) ou un rire (`[laughs]`) dit comment le corps parle,
#: pas ce qu'on ressent ; une voix qui ne dit que ca sort plate a cote des
#: autres. `test_interpretation.py` exige qu'aucun jeu ne s'ecrive sans ton.
TONS = frozenset({
    "amused", "annoyed", "angry", "bitterly", "calm", "casually", "cheerful", "coldly",
    "concerned", "confident", "curious", "deadpan", "disappointed", "dramatic", "enthusiastic",
    "excited", "firmly", "gravely", "gruffly", "happy", "impressed", "knowingly",
    "matter-of-fact", "menacingly", "mischievously", "mysteriously", "nervously", "playfully",
    "quietly", "relieved", "sarcastic", "satisfied", "serious", "smugly", "softly", "somber",
    "surprised", "teasing", "tenderly", "warmly", "worried", "wryly",
})

#: Les balises de CORPS — ce que fait le corps, par-dessus le ton : un soupir,
#: un rire, un cri, un murmure. Elles n'expriment pas un sentiment a elles
#: seules, elles le colorent.
CORPS = frozenset({
    "groans", "laughs", "shouting", "sighs", "whispers",
})

#: Les balises d'ACCENT — un francais « pas d'ici », par la voix plutot que par
#: le vocabulaire (docs/ecrire-un-accent.md). Au plus UNE par replique, EN TETE :
#: elle prendrait la place du ton si elle trainait au milieu (docs/jeu-d-acteur.md
#: § 3.8). Validee a l'oreille avant d'entrer ici, jamais en passant — Sven, le
#: 22 sept. 2026 (Martin, apres l'avoir ecoutee : « c'est mieux »).
ACCENTS = frozenset({
    "Norwegian accent",
})

#: Les balises permises. ⚠️ Une liste FERMEE : une balise que v3 ne comprend pas,
#: il la lit a voix haute (« crochet, tristement »). On l'allonge quand on en
#: essaie une nouvelle, pas en passant.
BALISES = TONS | CORPS | ACCENTS

#: slug -> texte joue. ⚠️ Toutes les voix y sont (`test_interpretation.py`) :
#: une replique ajoutee sans son jeu sortirait plate a la prochaine generation.
#: Ceux des missions viennent de leur fichier (voir la fin de la table).
JEU: dict[str, str] = {
    # --- Les passants qu'on frole. Deux mots : une emotion, rarement une pause.
    "salut_h": "[cheerful] Salut!",
    "frette_h": "[casually] Fait frette… hein?",
    "tasse_toi_h": "[annoyed] Heille! Tâsse-toi don!",
    "bonne_journee_h": "[warmly] Bonne journée, là.",
    "salut_f": "[cheerful] Salut!",
    "excusez_f": "[surprised] Excusez-moi.",
    "belle_journee_f": "[happy] Belle journée… hein?",
    "ca_va_f": "[warmly] Ça va, toi?",
    # --- Le crieur : il vend, il ne murmure jamais.
    "approchez_c": "[excited] Approchez, approchez… venez voir!",
    "special_c": "[enthusiastic] Le spécial du jour… c'est icitte!",
    "moitie_prix_c": "[excited] [shouting] Moitié prix, moitié prix — aujourd'hui!",
    # --- La fille de la Brume : elle n'annonce pas, elle accoste. La pause est
    # dans l'invitation, jamais dans le prix.
    "compagnie_b": "[softly] Tu cherches de la compagnie… mon beau?",
    "beau_bonhomme_b": "[playfully] Heille, beau bonhomme! [whispers] Viens icitte.",
    "frette_b": "[teasing] Fait frette, hein? [softly] Viens te réchauffer.",
    "du_feu_b": "[playfully] T'as du feu… mon chou?",
    "tout_seul_b": "[softly] Reste pas tout seul… à soir, là.",
    "ca_te_tente_b": "[teasing] Ça te tente-tu… un peu de compagnie?",
    # --- La Brume a la radio : une animatrice de nuit, posee.
    "brume_nuit_r": "[calm] Vous écoutez La Brume, cent trois virgule sept. Il est minuit passé… sur le port.",
    "brume_pluie_r": "[softly] La pluie rentre par la baie. Restez au chaud… on continue.",
    "brume_demandes_r": "[warmly] Une petite dernière avant les nouvelles… pour ceux qui travaillent de nuit.",
    # --- Taxi-Radio : le matin, la bonne humeur a pleine voix.
    "taxi_bonjour_r": "[excited] Taxi-Radio, votre station! On est en ondes… pis y fait beau à Baie-des-Brumes!",
    "taxi_trafic_r": "[sighs] Ça bouchonne su'l pont, mes amis. [cheerful] Prenez donc la rue des Érables.",
    "taxi_merci_r": "[enthusiastic] Un gros merci à nos commanditaires… pis on remet ça!",
    # --- Les pubs, et les jumelles « a toi » des commerces qui s'achetent. ⚠️ Pas
    # de « … » devant la chute (les potins, la memoire, la cle a molette) : elle
    # tombe nette, ou elle ne tombe pas (`docs/ecrire-drole.md`, regle 4).
    "pub_gus_r": "[enthusiastic] Chez Gus! Le meilleur smoked meat en ville… depuis mille neuf cent soixante-deux.",
    "pub_rosa_r": "[confident] Boutique Rosa, rue du Faubourg. Habillez-vous… comme du monde.",
    "pub_tipaul_r": "[cheerful] Dépanneur Ti-Paul, ouvert tard. Bière frette, loterie… pis du bon café.",
    "pub_kiosque_r": "[cheerful] Le kiosque de Madame Thibodeau : journaux, gomme, billets de loto. "
                     "[playfully] Pis les potins, ça, c'est gratis.",
    "pub_kiosque_a_toi_r": "[excited] Le kiosque du Faubourg a un nouveau proprio! [wryly] Madame Thibodeau, elle, garde les potins.",
    "pub_bar_r": "[confident] Bar Le Brouillard, sur le port. La bière est frette, pis personne se souvient de rien.",
    "pub_bar_a_toi_r": "[excited] Bar Le Brouillard, sous nouvelle direction! "
                       "[mischievously] Le nouveau boss paye la première, s'il te connaît.",
    "pub_garage_r": "[enthusiastic] Garage Rocco Bandini : on répare toute, pis on pose pas de questions.",
    "pub_garage_a_toi_r": "[warmly] Le Garage Bandini reste dans la famille! [cheerful] Le neveu a repris la clé à molette.",
    # --- La police au scanner : la repartitrice est calme, c'est son metier ;
    # l'agent court. Et quand ils t'ont perdu, ils ne sont pas si tristes.
    "police_repere_1_r": "[matter-of-fact] Central à toutes les voitures : suspect signalé dans le secteur.",
    "police_repere_2_r": "[serious] Dix-quatre, j'ai un suspect en visuel.",
    "police_poursuite_1_r": "[firmly] Poursuite en cours! Toutes les unités disponibles.",
    "police_poursuite_2_r": "[excited] [shouting] Il se sauve! Je le suis, envoyez du renfort!",
    "police_perdu_1_r": "[disappointed] On l'a perdu. [deadpan] Je m'en vais prendre un café.",
    "police_perdu_2_r": "[calm] Fin des recherches. [deadpan] Retournez à vos beignes.",
    "police_barrage_1_r": "[confident] Barrage en place. Il passera pas par icitte.",
    "police_barrage_2_r": "[firmly] Barrage installé. Bloquez-moi toute ça.",
    "police_helico_1_r": "[serious] L'hélico décolle. On va l'avoir d'en haut.",
    "police_helico_2_r": "[confident] Ici l'hélico, je le vois. Y peut pas se cacher.",

    # Le jeu des répliques de MISSION n'est pas ici : il est collé à chaque réplique, dans le fichier
    # de la mission (`jeu=` sur `_l`/`_p`/`_r`/`_a`) — voir plus bas.

    # --- Le repos : ce que chacun dit quand aucune mission ne l'attend. Le même texte pour tous
    # (`missions.REPOS`), lu à sa façon — une balise de ton, en tête, avant M5 (`-1`) puis après (`-2`).
    "thibodeau-repos-1": "[warmly] Reviens me voir… plus tard.",
    "thibodeau-repos-2": "[softly] Le Faubourg est tranquille… Merci.",
    "marco-repos-1": "[quietly] Reviens me voir… plus tard.",
    "marco-repos-2": "[satisfied] Le Faubourg est tranquille… Merci.",
    "bouchard-repos-1": "[gruffly] Reviens me voir… plus tard.",
    "bouchard-repos-2": "[matter-of-fact] Le Faubourg est tranquille… Merci.",
    "josee-repos-1": "[knowingly] Reviens me voir… plus tard.",
    "tipaul-repos-1": "[casually] Reviens me voir… plus tard.",
    "tipaul-repos-2": "[cheerful] Le Faubourg est tranquille… Merci.",
    "lulu-repos-1": "[warmly] Reviens me voir… plus tard.",
    "lulu-repos-2": "[cheerful] Le Faubourg est tranquille… Merci.",
    "raymonde-repos-1": "[firmly] Reviens me voir… plus tard.",
    "raymonde-repos-2": "[matter-of-fact] Le Faubourg est tranquille… Merci.",
    "ovila-repos-1": "[calm] Reviens me voir… plus tard.",
    "ovila-repos-2": "[softly] Le Faubourg est tranquille… Merci.",
    "sven-repos-1": "[Norwegian accent][coldly] Reviens me voir… plus tard.",
    "sven-repos-2": "[Norwegian accent][matter-of-fact] Le Faubourg est tranquille… Merci.",
    "mo-repos-1": "[knowingly] Reviens me voir… plus tard.",
    "mo-repos-2": "[amused] Le Faubourg est tranquille… Merci.",
    "fern-repos-1": "[matter-of-fact] Reviens me voir… plus tard.",
    "fern-repos-2": "[relieved] Le Faubourg est tranquille… Merci.",
    "mado-repos-1": "[warmly] Reviens me voir… plus tard.",
    "mado-repos-2": "[cheerful] Le Faubourg est tranquille… Merci.",
    "gege-repos-1": "[firmly] Reviens me voir… plus tard.",
    "gege-repos-2": "[gruffly] Le Faubourg est tranquille… Merci.",
    "xavier-repos-1": "[disappointed] Reviens me voir… plus tard.",
    "xavier-repos-2": "[happy] Le Faubourg est tranquille… Merci.",
    "lachance-repos-1": "[calm] Reviens me voir… plus tard.",
    "lachance-repos-2": "[matter-of-fact] Le Faubourg est tranquille… Merci.",
    "gus-repos-1": "[gruffly] Reviens me voir… plus tard.",
    "gus-repos-2": "[matter-of-fact] Le Faubourg est tranquille… Merci.",
    "rosa-repos-1": "[wryly] Reviens me voir… plus tard.",
    "rosa-repos-2": "[amused] Le Faubourg est tranquille… Merci.",
    "ginette-repos-1": "[matter-of-fact] Reviens me voir… plus tard.",
    "ginette-repos-2": "[firmly] Le Faubourg est tranquille… Merci.",
    "gilles-repos-1": "[somber] Reviens me voir… plus tard.",
    "gilles-repos-2": "[warmly] Le Faubourg est tranquille… Merci.",
    "bonimenteur-repos-1": "[cheerful] Reviens me voir… plus tard.",
    "bonimenteur-repos-2": "[playfully] Le Faubourg est tranquille… Merci.",

    # --- Le Clairon : un vieil homme qui lit la manchette du matin. La pause
    # tombe entre le titre et ce qu'il en pense.
    "narrateur-journal-nuit_rouge": "[dramatic] Nuit rouge au Faubourg. Trois corps en une nuit… la police promet des renforts.",
    "narrateur-journal-un_mort": "[somber] Un mort dans la rue. Un passant retrouvé sans vie… témoins recherchés.",
    "narrateur-journal-un_blesse": "[serious] Un blessé à l'hôpital. Le docteur Lachance parle d'une nuit agitée… aux urgences.",
    "narrateur-journal-vague_de_vols": "[dramatic] Vague de vols d'autos. Trois véhicules disparus. [sarcastic] « On a nos soupçons », dit le sergent.",
    "narrateur-journal-un_char_vole": "[serious] Un char volé au Faubourg. On l'a vu disparaître en pleine rue. [wryly] Il est reparti en plein vol.",
    "narrateur-journal-taxi_qui_ne_dort_pas": "[curious] Le taxi qui ne dort pas. Un chauffeur enchaîne les courses… les clients parlent de brouillard.",
    "narrateur-journal-faubourg_inquiet": "[concerned] Le Faubourg s'inquiète. Les commerçants demandent plus de patrouilles.",
    "narrateur-journal-brume": "[somber] Brume sur le bassin. Le traversier a pris du retard… [sighs] rien à signaler.",
    # --- Les matins calmes : le narrateur, en paix, lit la ville qui se reveille.
    # Jamais de drame ici — c'est un homme qui aime les matins ou rien n'arrive.
    "narrateur-journal-matin_maree": "[calm] La marée est haute… les quais s'éveillent, les cordages craquent dans la brise.",
    "narrateur-journal-matin_mouettes": "[casually] Les mouettes crient tôt… elles tournent au-dessus du quai, puis elles se taisent.",
    "narrateur-journal-matin_boulanger": "[warmly] Ça sent le pain chaud! Le boulanger du Faubourg sort ses fournées… la rue marche le nez en l'air.",
    "narrateur-journal-matin_laitier": "[calm] Le laitier passe à l'aube. Les bouteilles s'alignent sur les perrons… [softly] le Faubourg dort encore, presque.",
    "narrateur-journal-matin_peche": "[satisfied] La pêche a été bonne… les bateaux rentrent au quai, les coffres pleins.",
    "narrateur-journal-matin_volets": "[cheerful] La ville ouvre les volets. Ils se lèvent un à un… Baie-des-Brumes s'étire au soleil.",
    "narrateur-journal-matin_silence": "[warmly] Un matin tranquille. Rien à signaler à Baie-des-Brumes… le meilleur genre de matin.",
    "narrateur-journal-cravates_chassees": "[excited] Les Cravates chassées du Faubourg! Trois coins de rue libérés en une nuit… toute la ville en parle.",
    "narrateur-journal-lecon_klaxon": "[amused] Le saviez-vous? Un coup de klaxon dans un taxi vous trouve un client. Ça marche aussi avec la pizza… l'ambulance et la remorqueuse.",
    "narrateur-journal-lecon_fourriere": "[matter-of-fact] Votre char a disparu? Mal garé, il est à la fourrière municipale. On peut l'y racheter… à un prix qui dépend de ce qu'il vaut.",
    "narrateur-journal-lecon_cafe": "[cheerful] Le café du matin. Un café au comptoir… et vous sprintez deux fois plus longtemps pendant une minute et demie.",
    "narrateur-journal-lecon_garage": "[knowingly] Le garage de Rocco. On y répare, on y repeint… et une peinture neuve fait oublier un char que la police cherche.",
    "narrateur-journal-lecon_proprietes": "[confident] Devenir propriétaire. Certains commerces de la ville se vendent… et ils rapportent tous les jours, que vous y soyez ou non.",
    "narrateur-journal-lecon_cloture": "[amused] Les raccourcis du Faubourg. Une clôture se franchit à pied — la police aussi… mais elle y perd le même temps que vous.",

    # --- L'ouverture. ⚠️ UNE pause par phrase, pas plus : la musique fait trente
    # secondes et reboucle, et la premiere minute de quelqu'un n'est pas a lui.
    "narrateur-ouverture-1": "[mysteriously] Baie-des-Brumes. Un port, du brouillard… pis du monde qui se mêle de ses affaires.",
    "narrateur-ouverture-2": "[somber] Ton oncle Rocco est mort le mois passé. Il te laisse son garage, sa planque… pis son nom.",
    "narrateur-ouverture-3": "[gravely] Il te laisse sa dette avec. Quinze mille piastres… à Sal le Barbier, qui compte les jours.",
    "narrateur-ouverture-4": "[wryly] T'arrives avec cinquante piastres pis un billet aller simple. Bonne chance… le jeune.",
}

# ⚠️ LE JEU D'UNE REPLIQUE DE MISSION VIT DANS LE FICHIER DE LA MISSION (`app/missions/<slug>.py`,
# `jeu=` sur `_l`/`_p`/`_r`/`_a`), colle a la replique qu'il joue : une mission se lit d'un bloc, et
# on n'a plus a tenir deux fichiers de front (Martin, 21 sept. 2026). On le rassemble ICI pour que
# tout le monde lise une seule table — `dit()`, les juges, `scripts/audio_elevenlabs.py`.
# ⚠️ L'import est en bas a dessein : `missions` n'a pas besoin de ce module.
from app import missions  # noqa: E402

JEU.update({r["slug"]: r["jeu"] for r in missions.repliques() if r.get("jeu")})

_BALISE = re.compile(r"\[([^\[\]]*)\]")


def a_secher(voix: dict) -> bool:
    return voix["voix"] in VOIX_A_SECHER


def egalisation(voix: dict) -> str:
    """Le filtre ffmpeg de cette voix : sa correction, ou le passe-haut des hommes."""
    return EGALISATION.get(voix["voix"], PASSE_HAUT_HOMMES)


def dit(voix: dict) -> str:
    """Le texte qu'ElevenLabs recoit pour cette replique : son jeu, ou son texte nu."""
    return JEU.get(voix["slug"], voix["texte"])


def balises(texte: str) -> list[str]:
    return _BALISE.findall(texte)


def mots(texte: str) -> list[str]:
    """Les mots d'une replique, sans ses balises ni sa ponctuation — ce qu'on ENTEND.

    ⚠️ Tout ce qui n'est pas une lettre ou un chiffre separe deux mots, trait
    d'union et apostrophe compris : « Tâsse-toi » et « su'l » se comparent alors
    pareil des deux cotes, et un « — » ajoute pour une pause ne compte pas.
    """
    return re.findall(r"\w+", _BALISE.sub(" ", texte).casefold())
