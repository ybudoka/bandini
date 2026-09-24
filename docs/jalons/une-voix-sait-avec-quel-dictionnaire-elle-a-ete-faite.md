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
