# Des voix qui jouent, et qui finissent leurs phrases

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux que tu regénères toutes les voix en mettant des pauses dans le
texte et de l'émotion, et un léger temps mort à la fin pour éviter les fins coupées ». Les
**83 répliques** (passants, radios, pubs, missions, journal, ouverture) refaites en
**eleven_v3** ; leur jeu vit dans `app/interpretation.py` — balises d'émotion **en anglais**
(`[sighs]`, `[coldly]`, liste fermée : une balise inconnue se lit à voix haute), pauses
« … » — et un juge exige **les mêmes mots** que la boîte (il attrape aussi un slug décalé
par une ligne insérée).

- ⚠️ **Les fins coupées venaient de DEUX endroits** : (1) le **fichier** — les 19 répliques
  du narrateur finissaient à 10-47 ms du dernier son ; `finir_voix` pose maintenant **0,35 s
  de temps mort** ; (2) **le jeu** — `majCinema` passait à la ligne suivante après le temps
  de *lire* (90 + 3 par caractère), voix ou pas, et la suivante **coupe** la voix : **9
  répliques de mission y perdaient déjà leur fin** (`bouchard-m4-6` : 7,06 s de voix, 5,65 s
  de ligne). Régénérer n'aurait réparé que la moitié, et les pauses auraient coupé tout le
  reste : la ligne **attend sa voix** (plafond +15 s si le navigateur ne dit jamais qu'elle
  s'est tue ; ACTION passe toujours).
- ⚠️ **v3 ajoute du silence de lui-même** — 1re génération : jusqu'à **2,9 s de zéros**
  après la dernière syllabe, 1 s avant « Excusez-moi », neuf trous de 1,2 à 1,6 s. La
  finition rogne les bords et ramène toute pause à **0,7 s** (seuil −45 dB, mesuré : le
  silence tombe sous −45, un soupir entre −35 et −45 — −48 d'abord ne ramenait rien), et la
  règle d'écriture est devenue « une balise par réplique dès qu'elle respire ». **Niveau** :
  de −32 à −15 LUFS avant (17 dB d'écart), toutes à **−19** maintenant ; l'encodeur mp3
  dépassait le pic visé de **2,3 dB**, la finition remesure et réencode. Durée totale 336 →
  407 s (×1,21), ouverture 25,7 s (sa musique fait 30 s) ; poids : histoire 2,5 Mo / 3,
  bruitages + passants 1,21 Mo / 1,5. Outils : `--masters DIR` garde les masters,
  **`--refinir`** rejoue la finition sans rien payer ; `--refaire ti_guy-m1-1` répondait
  « slug inconnu » (le `-1` lu comme une variante) — réparé. **13 159 crédits** (3 essais, 2
  générations). `test_interpretation.py` : 335 juges (mots, balises, câblage, temps mort et
  niveau mesurés sur chaque fichier, la ligne qui attend sa voix au banc — rouge sans le
  correctif de `histoire.js`).
- ⚠️ **À écouter** : aucun juge ne dit si l'émotion est la bonne — `--refinir` et
  `--refaire <slug>` pour celles à reprendre.
