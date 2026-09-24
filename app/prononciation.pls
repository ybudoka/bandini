<?xml version="1.0" encoding="UTF-8"?>
<!--
  LE DICTIONNAIRE DE PRONONCIATION DE BANDINI — comment les voix disent un mot,
  sans changer le mot qu'on lit.

  ElevenLabs applique ces règles de SON côté, au moment de générer : la boîte de
  dialogue affiche « Quinze piastres », la voix dit « Quinze piasses ». Le texte
  et le jeu= ne bougent pas, et le juge mot à mot (test_interpretation.py) ne
  voit rien : c'est la troisième voie que docs/ecrire-un-accent.md § 5 laissait
  fermée. Recette : docs/voix-de-l-histoire.md, « Le dictionnaire ».

  ⚠️ UNE RÈGLE N'ENTRE QU'APRÈS UNE ÉCOUTE SANS/AVEC. Les 23 et 24 sept. 2026,
  Martin a écouté onze phrases dites sans puis avec 107 règles : SANS gagnait
  pour 27 mots (p'tit, truck, chum, Roy, OK, full, donc, docker, run…), c'était
  PAREIL pour 5 (gang, job, y'a, ET, Y a), AVEC ne gagnait que pour astheure et
  piastres. Les voix québécoises d'eleven_v3 disent déjà bien le parler d'ici :
  une règle qui n'aide pas nuit. Ne rien ajouter « au cas où ».

  ⚠️ Phonème IPA OU alias, celui que l'oreille a choisi. Le phonème dit le son
  exact ; il ne vaut que pour eleven_v3 (multilingual_v2 l'ignore) — toutes les
  voix qui prennent ce dictionnaire sont en v3. L'alias réécrit le mot comme on
  l'entend : « Envoye » → « Anvoueille » a battu trois autres essais, dont deux
  en IPA. Chaque règle garde sa lecture EN CLAIR juste après elle (« dit : … ») :
  personne ici ne relit l'IPA d'un coup d'œil. Le juge l'exige.

  ⚠️ Sensible à la CASSE : « Astheure » en début de phrase est une autre règle
  que « astheure ». Un mot ENTIER seulement. Et seule la PREMIÈRE règle qui
  colle s'applique.

  ⚠️ Deux parties. Au-dessus de la marque EN RÉSERVE, chaque règle touche une
  réplique qu'on entend déjà, et le juge (tests/test_prononciation.py) l'exige.
  En dessous, les autres formes d'un mot DÉJÀ écouté (le singulier, la
  minuscule), qu'aucune réplique ne dit encore.

  ⚠️ Rien ne se régénère tout seul : une règle neuve vaut pour la prochaine voix
  générée. `scripts/audio_elevenlabs.py` avec l'option « dictionnaire » le
  téléverse, liste les répliques déjà faites qu'il change, et la commande qui
  les referait (payant). Pas de double tiret dans un commentaire XML : le
  format l'interdit.
-->
<lexicon version="1.0"
      xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
      alphabet="ipa" xml:lang="fr-CA">

  <!-- « Quinze mille piastres » : au Québec, des piasses. Écouté le 23 sept.
       2026 (Rosa, « quinze piastres ») : mieux avec. -->
  <lexeme><grapheme>piastres</grapheme><phoneme>pjɑs</phoneme></lexeme> <!-- dit : piasses -->

  <!-- Le « th » invite une lecture anglaise ; on dit « asteure ». Écouté le
       23 sept. 2026 (Rosa, « Astheure, ça coûte ») : mieux avec. -->
  <lexeme><grapheme>astheure</grapheme><phoneme>astœʁ</phoneme></lexeme> <!-- dit : asteure -->
  <lexeme><grapheme>Astheure</grapheme><phoneme>astœʁ</phoneme></lexeme> <!-- dit : Asteure -->

  <!-- « Envoye, fonce! » : lu à la française, le E final se tait (« envoie »),
       et v3 seul ne le dit pas non plus. Martin : « devrait sonner envoueille ».
       Écouté le 24 sept. 2026 (Ti-Paul), quatre variantes : l'alias
       « Anvoueille » gagne, devant « Envoueille » et les IPA ɑ̃vwɛːj, ɑ̃ˈvwɛj. -->
  <lexeme><grapheme>Envoye</grapheme><alias>Anvoueille</alias></lexeme> <!-- dit : Anvoueille -->

  <!-- =================================================================== -->
  <!-- ===== EN RÉSERVE : les autres formes des mots écoutés ============= -->
  <!-- =================================================================== -->

  <lexeme><grapheme>piastre</grapheme><phoneme>pjɑs</phoneme></lexeme> <!-- dit : piasse -->
  <lexeme><grapheme>envoye</grapheme><alias>anvoueille</alias></lexeme> <!-- dit : anvoueille -->

</lexicon>
