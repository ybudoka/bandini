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
pire qu'une voix plate. Et comme le slug suit la PLACE de la replique, ce meme
juge attrape une replique inseree dans une mission : les interpretations d'en
dessous ne collent plus a leur texte, et il le dit.

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

#: Les balises permises. ⚠️ Une liste FERMEE : une balise que v3 ne comprend pas,
#: il la lit a voix haute (« crochet, tristement »). On l'allonge quand on en
#: essaie une nouvelle, pas en passant.
BALISES = TONS | CORPS

#: slug -> texte joue. ⚠️ Toutes les voix y sont (`test_interpretation.py`) :
#: une replique ajoutee sans son jeu sortirait plate a la prochaine generation.
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
    # --- Les pubs, et leurs jumelles « a toi ».
    "pub_gus_r": "[enthusiastic] Chez Gus! Le meilleur smoked meat en ville… depuis mille neuf cent soixante-deux.",
    "pub_gus_a_toi_r": "[excited] Chez Gus, sous nouvelle administration! [cheerful] Passez voir le nouveau proprio.",
    "pub_rosa_r": "[confident] Boutique Rosa, rue du Faubourg. Habillez-vous… comme du monde.",
    "pub_rosa_a_toi_r": "[excited] Boutique Rosa a changé de mains! [warmly] Venez rencontrer le nouveau proprio.",
    "pub_tipaul_r": "[cheerful] Dépanneur Ti-Paul, ouvert tard. Bière frette, loterie… pis du bon café.",
    "pub_tipaul_a_toi_r": "[excited] Le Dépanneur Ti-Paul est vendu! [cheerful] Le nouveau proprio vous attend.",

    # --- M1, Ti-Guy : content de te voir, puis complice.
    "ti_guy-m1-1": "[excited] Heille! Le cousin de Rocco! [warmly] T'as fait bon voyage?",
    "ti_guy-m1-2": "[quietly] Rocco est parti se faire oublier. Le garage… c'est toi qui le tiens, astheure.",
    "ti_guy-m1-3": "[mischievously] Y a un char qui traîne dans une ruelle, un peu plus loin. Personne va s'en ennuyer.",
    "ti_guy-m1-4": "[serious] Ramène-le au garage sans le bosser… pis sans que personne te voie.",
    "ti_guy-m1-5": "[excited] Pas une bosse! [laughs] T'es ben le cousin de Rocco.",
    "ti_guy-m1-6": "[warmly] Tiens, la clé de la planque. Dors là… pis fais-toi pas pogner.",
    "ti_guy-m1-7": "[disappointed] Ouain… On va dire que c'était un essai. [sighs] Reviens me voir.",
    # Pendant (2e vague des scènes) : au combiné, pendant qu'on roule.
    "ti_guy-m1-8": "[amused] Beau char! Ramène-le au garage tranquillement, pis évite la police.",
    # --- M2, Madame Thibodeau : inquiete, puis en colere, puis tendre.
    "thibodeau-m2-1": "[worried] C'est Madame Thibodeau, du kiosque. Les Cravates me font des misères… Viens me voir, veux-tu?",
    "thibodeau-m2-2": "[bitterly] Deux Cravates sont venus me « protéger ». [angry] Ils ont vidé ma caisse.",
    "thibodeau-m2-3": "[quietly] Ils rôdent encore au coin. Fais-leur comprendre… avec tes poings, pas plus.",
    "thibodeau-m2-4": "[angry] Le troisième s'est sauvé en moto avec mon argent. Rattrape-le.",
    "thibodeau-m2-5": "[relieved] Mon argent! [warmly] T'es un bon garçon, toi.",
    "thibodeau-m2-6": "[tenderly] Tiens… le bâton de mon défunt. Pis au kiosque, c'est moins cher pour toi.",
    "thibodeau-m2-7": "[concerned] Ils t'ont eu, hein? Repose-toi… pis reviens.",
    "thibodeau-m2-8": "[worried] Il se sauve avec ma caisse! Lâche-le pas!",
    # --- M3, Marco : l'affaire d'abord, et la mise en garde a voix basse.
    "marco-m3-1": "[casually] Marco, le cousin. J'ai un taxi qui dort au garage. [mischievously] Ça te tente de faire du cash?",
    "marco-m3-2": "[serious] Trois clients, pas plus. Pis tu me ramènes le taxi… entier.",
    "marco-m3-3": "[quietly] Ouvre l'œil. Y a du monde en ville… qui pose des questions sur toi.",
    "civil-m3-4": "[smugly] Roule, mon homme. Pis fais pas de folies… j'suis de la police.",
    "marco-m3-5": "[impressed] Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte.",
    "marco-m3-6": "[casually] Y mange là tous les midis. Sois poli… c'est un ami de la famille.",
    "marco-m3-7": "[disappointed] Mon taxi… Bon. On efface… [groans] pis on recommence.",
    # --- M4, le sergent Bouchard : bourru, et il baisse la voix pour le sale.
    "bouchard-m4-1": "[gruffly] Bouchard. Marco m'a parlé de toi. Viens dîner au casse-croûte… j'ai une job.",
    "bouchard-m4-2": "[quietly] Y a une auto-patrouille au poste que j'aimerais voir disparaître. Papiers… pas propres.",
    "bouchard-m4-3": "[serious] Prends-la de nuit, sans témoin. Ti-Guy va te suivre en char, pour faire diversion.",
    "bouchard-m4-4": "[firmly] Largue-la au garage. Pis si mes gars te courent après… sème-les.",
    "bouchard-m4-5": "[satisfied] Propre. À partir d'aujourd'hui, si un de mes gars te pogne… tu dis mon nom.",
    "bouchard-m4-6": "[gravely] Un mot d'avertissement… Josée, au bar, cherche du monde comme toi. Fais attention.",
    "bouchard-m4-7": "[nervously] J'ai rien vu, j'ai rien entendu. [sighs] Reviens quand ça sera calme.",
    "ti_guy-m4-8": "[confident] C'est Ti-Guy, j'suis juste derrière toi. Roule, j'm'occupe des bœufs.",
    # --- M5, Josee : froide, et elle pese chaque ordre.
    "josee-m5-1": "[coldly] Josée. On m'appelle la Chef. Viens au Brouillard… j'ai à te parler.",
    "josee-m5-2": "[coldly] Les Cravates tiennent trois coins de rue. Je les veux vides… avant la nuit.",
    "josee-m5-3": "[menacingly] Leur chef va sortir quand ses gars vont tomber. Lui, je le veux couché.",
    "josee-m5-4": "[matter-of-fact] Un témoin va appeler la police, c'est sûr. Sème-les, pis rentre à ta planque.",
    "josee-m5-5": "[satisfied] Le Faubourg respire. Le bar est à toi… pis toute la ville va le lire demain matin.",
    "josee-m5-6": "[mysteriously] On va se reparler. Y a plus grand… que le Faubourg.",
    "josee-m5-7": "[disappointed] Les Cravates sont encore là. Reviens quand tu seras prêt.",
    "josee-m5-8": "[menacingly] Leur chef vient de sortir. Couche-le, pis le Faubourg est à nous.",
    # --- M6, Josee presente la ville : plus chaude qu'a M5, elle donne des noms.
    "josee-m6-1": "[confident] Josée. Le Faubourg est à nous. Viens au bar… je te présente la ville.",
    "josee-m6-2": "[matter-of-fact] Quatre coins, quatre personnes. Ti-Paul au dépanneur… ma sœur Lulu à la cantine.",
    "josee-m6-3": "[matter-of-fact] Raymonde tient le syndicat à l'usine… pis Ovila garde le phare.",
    "josee-m6-4": "[warmly] Va leur serrer la main… Dans cette ville, tout commence par là.",
    "josee-m6-5": "[satisfied] Quatre poignées de main. [warmly] Le monde va t'appeler par ton nom… astheure.",
    "josee-m6-6": "[mysteriously] Garde l'œil ouvert… Il se passe plus de choses que t'en penses.",
    "josee-m6-7": "[disappointed] Tu reviendras… quand tu auras le temps de faire le tour.",
    "josee-m6-8": "[knowingly] Le dépanneur d'abord. Ti-Paul en sait plus… qu'il en a l'air.",
    # --- M97, Marco trahit : froid, amer, puis qui se rend a l'evidence.
    "marco-m97-1": "[coldly] Marco. Viens au garage, cousin. On a à se parler… toi pis moi.",
    "marco-m97-2": "[bitterly] Bouchard m'a montré ton dossier. T'as bâti un nom… sur mon dos.",
    "marco-m97-3": "[menacingly] Pis il paie pour te voir tomber… Tiens, les voilà.",
    "marco-m97-4": "[impressed] T'es plus dur que les chiens qu'il a lâchés. Garde le taxi… il est à toi.",
    "marco-m97-5": "[somber] Moi, je disparais… La ville est à toi, cousin.",
    "marco-m97-6": "[coldly] Tiens-toi prêt… On va régler ça bien comme il faut.",
    "marco-m97-7": "[worried] Cours, cousin… Ceux-là ne font pas de quartier.",

    # --- Le Clairon : un vieil homme qui lit la manchette du matin. La pause
    # tombe entre le titre et ce qu'il en pense.
    "narrateur-journal-nuit_rouge": "[dramatic] Nuit rouge au Faubourg. Trois corps en une nuit… la police promet des renforts.",
    "narrateur-journal-un_mort": "[somber] Un mort dans la rue. Un passant retrouvé sans vie… témoins recherchés.",
    "narrateur-journal-un_blesse": "[serious] Un blessé à l'hôpital. Le docteur Lachance parle d'une nuit agitée… aux urgences.",
    "narrateur-journal-vague_de_vols": "[dramatic] Vague de vols d'autos. Trois véhicules disparus. [sarcastic] « On a nos soupçons », dit le sergent.",
    "narrateur-journal-un_char_vole": "[serious] Un char volé au Faubourg. Le propriétaire l'avait laissé tourner. [deadpan] Il ne tourne plus.",
    "narrateur-journal-taxi_qui_ne_dort_pas": "[curious] Le taxi qui ne dort pas. Un chauffeur enchaîne les courses… les clients parlent de brouillard.",
    "narrateur-journal-faubourg_inquiet": "[concerned] Le Faubourg s'inquiète. Les commerçants demandent plus de patrouilles.",
    "narrateur-journal-brume": "[somber] Brume sur le bassin. Le traversier a pris du retard… [sighs] rien à signaler.",
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
