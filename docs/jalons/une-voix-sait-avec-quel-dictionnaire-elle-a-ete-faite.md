# Une voix sait avec quel dictionnaire elle a été faite

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

`scripts/audio_elevenlabs.py --dictionnaire` liste les voix « à refaire » : toute voix qui existe et
dit un mot du lexique. Il ne sait pas avec quel dictionnaire elle a été faite — le 24 sept. 2026,
il listait encore les douze voix qu'on venait de refaire avec lui (1 071 caractères à repayer pour
rien). Martin : oui, qu'on le règle.

Chaque voix touchée porte dans son mp3 une étiquette `dictionnaire` : les règles qui l'ont touchée,
telles qu'elles étaient (`piastres=pjɑs;Envoye=Anvoueille`). `--dictionnaire` ne liste plus qu'une
voix dont l'étiquette diffère du lexique actuel — une règle neuve, changée ou retirée. `--refinir`
et `--secher` gardent l'étiquette (le master est le même). Les douze voix du 24 sept. reçoivent la
leur sans être régénérées.

## Notes

Livré le 24 sept. 2026.

- **L'étiquette** : `prononciation.ETIQUETTE` (« dictionnaire »), une trame ID3 que ffmpeg écrit et
  relit (`-metadata`, `ffprobe format_tags`), IPA compris. Sa valeur est `prononciation.signature` :
  les règles qui touchent la réplique, `mot=son` séparés par `;`. `prononciation.a_refaire(texte,
  étiquette)` compare avec les règles d'aujourd'hui ; une voix jamais touchée n'en porte pas et
  n'est jamais à refaire.
- **Le script** : `finir_voix(..., dictionnaire=)` écrit l'étiquette ; la génération passe la
  signature (rien si la voix est partie sans dictionnaire) ; `--refinir` et `--secher` relisent
  celle du fichier avant de le remplacer (`etiquette_dictionnaire`). `--dictionnaire` sonde toutes
  les voix en parallèle (≈ 2 s) et dit, pour chacune à refaire, ce qu'elle devrait porter et ce
  qu'elle porte.
- **Les douze voix du 24 sept.** ont reçu leur étiquette par une recopie `ffmpeg -c copy
  -map_metadata 0` (le son ne bouge pas, la marque « voix isolee » du narrateur reste) :
  `--dictionnaire` n'a plus rien à refaire.
- **Juges** (`tests/test_prononciation.py`) : la signature, `a_refaire` dans ses cinq cas, le
  câblage des trois finitions, et un vrai `finir_voix` qui laisse l'étiquette dans le mp3.
  Mutations (l'étiquette sous un autre nom ; `--refinir` qui ne la reporte pas) : rouges.
