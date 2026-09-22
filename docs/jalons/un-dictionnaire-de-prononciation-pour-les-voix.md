# Un dictionnaire de prononciation pour les voix

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « crée moi un dictionnaire pour mon jeu » (lien vers les
pronunciation dictionaries d'ElevenLabs). C'est la troisième voie que
docs/ecrire-un-accent.md § 5 laissait fermée : la voix prononce autrement un mot SANS que le
texte affiché ni le jeu= changent — la règle s'applique côté ElevenLabs, le juge mot à mot
ne voit rien. Un lexique PLS dans le dépôt (règles alias : l'orthographe qu'on veut
entendre, comme « tâsse-toi don » que Martin a dicté le 13 sept.) ; le serveur MCP
elevenlabs apprend à téléverser un lexique et à passer pronunciation_dictionary_locators ;
scripts/audio_elevenlabs.py le téléverse quand il a changé (empreinte) et le joint à chaque
voix ; un juge valide le lexique (XML, pas de doublon, chaque mot existe dans une réplique).
Rien n'est régénéré sans l'accord de Martin : le dictionnaire vaut pour la prochaine
génération ou un --refaire.
