# Des bruitages qui ont encore leur aigu

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« améliore les effets spéciaux en qualité », puis « génère-les avec
l'IA ») : les 24 bruitages étaient générés **à leur taille finale** (22 kHz, 32 kbit/s,
stéréo), et c'était trois défauts d'un coup.

- ⚠️ **Presque plus d'aigu** : en comparant le pic du signal filtré à 8 kHz au pic du
  fichier entier, il restait **−26 dB** pour la caisse enregistreuse, **−27** pour la tôle
  froissée, **−30** pour le clic de menu, **−32** pour la porte. Or c'est là que vit le
  clinquant d'une pièce et le verre d'un phare : on payait une génération dont on jetait le
  haut **avant même de l'écouter**. Les mêmes sons sont aujourd'hui entre **−6 et −10 dB**.
- ⚠️ Le klaxon, la sirène et le moteur n'ont pas bougé — ils n'ont pas d'aigu à avoir, et le
  juge ne leur en demande pas.
- ⚠️ **Des niveaux au hasard** : les pics allaient de **−34 dB** (un pas) à **0 dB pile**
  (huit fichiers collés au plafond), donc le `volume` du catalogue ne dosait rien — il
  multipliait un accident.
- ⚠️ **Deux fichiers larges** (la porte, le refus : leurs deux canaux ne se ressemblent qu'à
  1 dB près) — et un son déjà large ne se laisse plus placer par le `StereoPanner` de
  `son.js`, il arrive à gauche quoi qu'on lui demande. ElevenLabs rend désormais un
  **master** (`mp3_44100_128`) que `ffmpeg` ramène à la taille du jeu (`finir()`) : mono,
  normalisé au même pic (−1 dBFS), queue rognée puis fermée par un fondu de 15 ms, 96 kbit/s
  pour un bruit bref et 64 pour une boucle.
- ⚠️ **L'ordre des gestes est tout le problème** : rogner avant de normaliser — ce que
  j'avais fait d'abord — applique un seuil **absolu** de −45 dBFS à une génération sortie à
  −34 dB, donc **en plein milieu du son** ; mesuré : un pas réduit à 0,06 s puis remonté de
  +37 dB, il ne restait que le souffle. Normalisé d'abord, le seuil est toujours à 44 dB
  sous le pic.
- ⚠️ Une **boucle** ne se rogne ni ne se fond : c'est sa couture qu'on abîmerait, et le trou
  s'entendrait à chaque tour. Les `volume` sont recalculés pour **reproduire le mélange
  d'avant** (pic mesuré × ancien volume), sauf `pas` et `sonnette`, qui sortaient sous −23
  dB une fois mixés — sous ce qu'on entend en jouant. Nouveau champ `influence` : haut pour
  ce qui doit être **une** chose exacte (un clic, un klaxon, une sirène), plus bas pour une
  matière (une explosion, une foule), où le modèle rend mieux quand on lui laisse de la
  place. **32 fichiers pour 21 sons** — `pas` passe à 4 variantes, `coup` et `touche` à 3,
  `choc`, `klaxon` et `ramasse` à 2. Le script **dénonce ses propres ratés**, et il a fallu
  deux essais pour qu'il dénonce la bonne chose : j'avais posé « plus de +20 dB de gain =
  génération ratée », ce qui est **faux** — ElevenLabs rend souvent un pas à bas niveau mais
  parfaitement propre, et le drapeau envoyait refaire, à crédits perdus, la meilleure prise
  du lot (`pas-2` demandait +29 dB **et** affichait le meilleur plancher des quatre, −47
  dB). Ce qui compte est le **rapport signal/bruit du fichier fini**, pas le chemin pour y
  arriver : sous 30 dB, ça souffle, et `--refaire pas-2` refait **cette variante-là seule**
  au lieu des quatre.
- ⚠️ Et on ne voit le souffle **que quand le son s'arrête** : un buzzer de refus ou une auto
  qui passe remplissent toute leur durée, leur « plancher » est leur son (1 dB de RSB sur
  des fichiers impeccables) — sans un moment de calme, pas de verdict. Juges d'une autre
  **nature** que ceux du catalogue : ils ouvrent les octets (mono, 44,1 kHz, pic à −1 dBFS,
  pas de vide en queue, pas de souffle, et de l'énergie au-dessus de 8 kHz sur les deux sons
  les plus brillants). L'écart de niveau entre fichiers tombe de **34,4 dB à 1,8 dB**, ce
  qui reste étant celui de l'encodeur mp3. Poids : 184 Ko → **512 Ko** pour 32 fichiers,
  soit 551 Ko dans le seau que le juge plafonne à 600 — **il reste 49 Ko**, donc une
  variante de plus ne rentre pas sans relever le plafond ou baisser un débit.
- ⚠️ **Premier retour, et il valide la raison d'être du « en cours »** : Martin a écouté et
  « moto qui passe » était **un chien**. Le prompt disait « exhaust **bark** » — un mot
  d'argot de sonorisation est d'abord un cri d'animal, et le modèle l'a pris au pied de la
  lettre ; aucune mesure ne pouvait attraper ça, seule une oreille le pouvait. Prompt
  réécrit sans le mot (et `influence` remontée à 0,6 : sur ce son-là on ne laisse plus de
  place), son refait.
- ⚠️ Et le chien est **gardé** : `static/audio/reserve/` tient les générations ratées mais
  bonnes, hors catalogue — donc jamais téléchargées, jamais jouées. Ça ne tient qu'à un
  détail : `orphelins()` liste le dossier avec `iterdir()`, qui ne descend pas dans les
  sous-dossiers. Un juge garde cet invariant, pour que le jour où quelqu'un passera à
  `rglob()` ça se voie au lieu de réclamer la suppression de toute la réserve. Le chien
  jappera derrière une clôture quand viendront **les terrains de banlieue** (P4).
- ⚠️ **Ce qui a clos l'étape, c'est l'oreille de Martin**, pas un juge : aucun ne dit qu'un
  son est le BON son, seulement que la chaîne a tourné. Il a écouté le 13 sept. : la moto
  était un chien, la porte de commerce, la montée à vélo était un objet qu'on ramasse — les
  trois refaits (les deux derniers aux deux lignes suivantes), le reste tient
