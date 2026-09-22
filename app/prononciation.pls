<?xml version="1.0" encoding="UTF-8"?>
<!--
  LE DICTIONNAIRE DE PRONONCIATION DE BANDINI — comment les voix disent un mot,
  sans changer le mot qu'on lit.

  ElevenLabs applique ces règles de SON côté, au moment de générer : la boîte de
  dialogue affiche « Prenez donc la rue », la voix dit « Prenez don la rue ». Le
  texte et le jeu= ne bougent pas, et le juge mot à mot (test_interpretation.py)
  ne voit rien : c'est la troisième voie que docs/ecrire-un-accent.md § 5
  laissait fermée. Recette : docs/voix-de-l-histoire.md, « Le dictionnaire ».

  ⚠️ Des ALIAS, pas des phonèmes : l'alias marche avec tous les modèles, et on
  l'écrit comme on l'entend, en français. Le phonème IPA dépend du modèle
  (multilingual_v2 l'ignore), et personne ici ne relit de l'IPA.

  ⚠️ Sensible à la CASSE : « Astheure » en début de phrase est une autre règle
  que « astheure ». Et seule la PREMIÈRE règle qui colle s'applique.

  ⚠️ Rien ne se régénère tout seul : une règle neuve vaut pour la prochaine voix
  générée. `scripts/audio_elevenlabs.py` avec l'option « dictionnaire » liste
  les répliques qu'elle touche, et la commande qui les referait (payant).
  (Pas de double tiret dans un commentaire XML : le format l'interdit.)

  Une règle entre ici parce qu'une voix du jeu a buté dessus, ou parce que la
  lecture française d'un mot n'est pas celle du Québec. Le commentaire au-dessus
  dit laquelle des deux.
-->
<lexicon version="1.0"
      xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
      alphabet="ipa" xml:lang="fr-CA">

  <!-- ===== Le parler d'ici ===== -->

  <!-- Martin, 13 sept. 2026, en dictant le passant : « heille ! tasse toi don ! ».
       Le C final de « donc » est de France. -->
  <lexeme>
    <grapheme>donc</grapheme>
    <alias>don</alias>
  </lexeme>

  <!-- « Quinze mille piastres » : au Québec, des piasses. -->
  <lexeme>
    <grapheme>piastres</grapheme>
    <alias>piasses</alias>
  </lexeme>

  <!-- Le « th » invite une lecture anglaise ; on dit « asteure ». -->
  <lexeme>
    <grapheme>astheure</grapheme>
    <alias>asteure</alias>
  </lexeme>
  <lexeme>
    <grapheme>Astheure</grapheme>
    <alias>Asteure</alias>
  </lexeme>

  <!-- « Envoye, fonce! » : lu à la française, le E final se tait (« envoie »).
       Ici on l'entend : « envoye » rime avec « oreille ». -->
  <lexeme>
    <grapheme>Envoye</grapheme>
    <alias>Envoille</alias>
  </lexeme>

  <!-- « su'l pont » : un seul mot, pas « su », pause, « l ». -->
  <lexeme>
    <grapheme>su'l</grapheme>
    <alias>sul</alias>
  </lexeme>

  <!-- « Skateux » se dit « skèteux », pas « skat-eux ». -->
  <lexeme>
    <grapheme>Skateux</grapheme>
    <alias>Skèteux</alias>
  </lexeme>

  <!-- ===== Les mots anglais du quotidien, comme on les dit ici ===== -->

  <!-- « une run qui traîne » -->
  <lexeme>
    <grapheme>run</grapheme>
    <alias>ronne</alias>
  </lexeme>

  <!-- « full haut » : pas le « u » de « futé ». -->
  <lexeme>
    <grapheme>full</grapheme>
    <alias>foule</alias>
  </lexeme>

  <!-- « Un stool nerveux » -->
  <lexeme>
    <grapheme>stool</grapheme>
    <alias>stoule</alias>
  </lexeme>

  <!-- La pub de Gus : « smoke mite », sans le « -ed ». -->
  <lexeme>
    <grapheme>smoked meat</grapheme>
    <alias>smoke mite</alias>
  </lexeme>

  <!-- ===== Les noms ===== -->

  <!-- L'inspectrice Roy : un Roy d'ici se dit « Roi ». -->
  <lexeme>
    <grapheme>Roy</grapheme>
    <alias>Roi</alias>
  </lexeme>

  <!-- Prévost, le patron de l'usine : le S et le T se taisent. -->
  <lexeme>
    <grapheme>Prévost</grapheme>
    <alias>Prévo</alias>
  </lexeme>

  <!-- Ti-Guy : Guy comme « gui », jamais le « guy » anglais. -->
  <lexeme>
    <grapheme>Ti-Guy</grapheme>
    <alias>Ti-Gui</alias>
  </lexeme>

  <!-- ===== La typographie ===== -->

  <!-- « Perdu mon camion ET ma marchandise » : la majuscule insiste, mais un
       mot de deux capitales s'épelle comme un sigle (« E.T. »). -->
  <lexeme>
    <grapheme>ET</grapheme>
    <alias>et</alias>
  </lexeme>

</lexicon>
