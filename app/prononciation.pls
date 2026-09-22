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
  que « astheure ». Un mot ENTIER seulement. Et seule la PREMIÈRE règle qui
  colle s'applique : « Ti-Guy » passe avant « Guy ».

  ⚠️ Deux parties. Au-dessus de la marque EN RÉSERVE, chaque règle touche une
  réplique qu'on entend déjà, et le juge (tests/test_prononciation.py) l'exige :
  une faute de frappe dans un mot ne corrigerait rien, en silence. En dessous,
  les mots que les prochaines missions diront sans doute (les anglicismes du
  garage et de la rue, les contractions, les noms des personnages pas encore
  dits) : ils attendent leur réplique, et le juge les laisse attendre.

  ⚠️ Rien ne se régénère tout seul : une règle neuve vaut pour la prochaine voix
  générée. `scripts/audio_elevenlabs.py` avec l'option « dictionnaire » le
  téléverse, liste les répliques déjà faites qu'il change, et la commande qui
  les referait (payant). Pas de double tiret dans un commentaire XML : le
  format l'interdit.

  Une règle entre ici parce qu'une voix du jeu a buté dessus, ou parce que la
  lecture française d'un mot n'est pas celle du Québec. Aucune n'a encore été
  écoutée (22 sept. 2026) : Martin juge à l'oreille, une règle qui sonne mal se
  retire.
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
  <lexeme><grapheme>donc</grapheme><alias>don</alias></lexeme>

  <!-- « Quinze mille piastres » : au Québec, des piasses. -->
  <lexeme><grapheme>piastres</grapheme><alias>piasses</alias></lexeme>

  <!-- Le « th » invite une lecture anglaise ; on dit « asteure ». -->
  <lexeme><grapheme>astheure</grapheme><alias>asteure</alias></lexeme>
  <lexeme><grapheme>Astheure</grapheme><alias>Asteure</alias></lexeme>

  <!-- « Envoye, fonce! » : lu à la française, le E final se tait (« envoie »).
       Ici on l'entend : « envoye » rime avec « oreille ». -->
  <lexeme><grapheme>Envoye</grapheme><alias>Envoille</alias></lexeme>

  <!-- « Skateux » se dit « skèteux », pas « skat-eux ». -->
  <lexeme><grapheme>Skateux</grapheme><alias>Skèteux</alias></lexeme>

  <!-- ===== Les mots mangés : une apostrophe, une syllabe de moins ===== -->

  <!-- L'apostrophe au milieu d'un mot se lit parfois comme une coupure : on
       écrit d'un bloc ce qui se dit d'un bloc. -->
  <lexeme><grapheme>su'l</grapheme><alias>sul</alias></lexeme>
  <lexeme><grapheme>j'suis</grapheme><alias>chu</alias></lexeme>
  <lexeme><grapheme>p't-être</grapheme><alias>ptête</alias></lexeme>
  <lexeme><grapheme>p'tit</grapheme><alias>ptit</alias></lexeme>
  <lexeme><grapheme>y'a</grapheme><alias>ya</alias></lexeme>
  <lexeme><grapheme>Y a</grapheme><alias>Ya</alias></lexeme>
  <lexeme><grapheme>v'là</grapheme><alias>vla</alias></lexeme>

  <!-- ===== Les mots anglais du quotidien, comme on les dit ici ===== -->

  <!-- « une run qui traîne » -->
  <lexeme><grapheme>run</grapheme><alias>ronne</alias></lexeme>
  <!-- « full haut » : pas le « u » de « futé ». -->
  <lexeme><grapheme>full</grapheme><alias>foule</alias></lexeme>
  <!-- « Un stool nerveux » -->
  <lexeme><grapheme>stool</grapheme><alias>stoule</alias></lexeme>
  <!-- La pub de Gus : « smoke mite », sans le « -ed ». -->
  <lexeme><grapheme>smoked meat</grapheme><alias>smoke mite</alias></lexeme>
  <!-- « j'ai une job » : le J anglais, jamais celui de « jaune ». -->
  <lexeme><grapheme>job</grapheme><alias>djobbe</alias></lexeme>
  <!-- « le reste de la gang » : ici, ça rime avec « gain », pas avec « gant ». -->
  <lexeme><grapheme>gang</grapheme><alias>gaingue</alias></lexeme>
  <!-- « Le docker va essayer de filer » : dockeur, comme on l'entend au port. -->
  <lexeme><grapheme>docker</grapheme><alias>dockeur</alias></lexeme>

  <!-- ===== Les noms ===== -->

  <!-- L'inspectrice Roy : un Roy d'ici se dit « Roi ». -->
  <lexeme><grapheme>Roy</grapheme><alias>Roi</alias></lexeme>
  <!-- Prévost, le patron de l'usine : le S et le T se taisent. -->
  <lexeme><grapheme>Prévost</grapheme><alias>Prévo</alias></lexeme>
  <!-- Ti-Guy : Guy comme « gui », jamais le « guy » anglais. AVANT « Guy ». -->
  <lexeme><grapheme>Ti-Guy</grapheme><alias>Ti-Gui</alias></lexeme>

  <!-- ===== La typographie ===== -->

  <!-- « Perdu mon camion ET ma marchandise » : la majuscule insiste, mais un
       mot de deux capitales s'épelle comme un sigle (« E.T. »). -->
  <lexeme><grapheme>ET</grapheme><alias>et</alias></lexeme>

  <!-- =================================================================== -->
  <!-- ===== EN RÉSERVE : des mots qu'aucune réplique ne dit encore ===== -->
  <!-- =================================================================== -->

  <!-- ===== Le parler d'ici, ses autres formes ===== -->

  <!-- En tête de phrase, la majuscule fait une autre règle. -->
  <lexeme><grapheme>Donc</grapheme><alias>Don</alias></lexeme>
  <lexeme><grapheme>coudonc</grapheme><alias>coudon</alias></lexeme>
  <lexeme><grapheme>Coudonc</grapheme><alias>Coudon</alias></lexeme>
  <lexeme><grapheme>piastre</grapheme><alias>piasse</alias></lexeme>
  <lexeme><grapheme>envoye</grapheme><alias>envoille</alias></lexeme>
  <lexeme><grapheme>skateux</grapheme><alias>skèteux</alias></lexeme>

  <!-- ===== Les mots mangés, leurs autres formes ===== -->

  <lexeme><grapheme>J'suis</grapheme><alias>Chu</alias></lexeme>
  <lexeme><grapheme>j'sais pas</grapheme><alias>chépas</alias></lexeme>
  <lexeme><grapheme>J'sais pas</grapheme><alias>Chépas</alias></lexeme>
  <lexeme><grapheme>t'sais</grapheme><alias>tsé</alias></lexeme>
  <lexeme><grapheme>T'sais</grapheme><alias>Tsé</alias></lexeme>
  <lexeme><grapheme>P't-être</grapheme><alias>Ptête</alias></lexeme>
  <lexeme><grapheme>P'tit</grapheme><alias>Ptit</alias></lexeme>
  <lexeme><grapheme>p'tite</grapheme><alias>ptite</alias></lexeme>
  <lexeme><grapheme>P'tite</grapheme><alias>Ptite</alias></lexeme>
  <lexeme><grapheme>Y'a</grapheme><alias>Ya</alias></lexeme>
  <lexeme><grapheme>y'avait</grapheme><alias>yavait</alias></lexeme>
  <lexeme><grapheme>Y'avait</grapheme><alias>Yavait</alias></lexeme>
  <lexeme><grapheme>V'là</grapheme><alias>Vla</alias></lexeme>
  <!-- « su'a table » : sur la. -->
  <lexeme><grapheme>su'a</grapheme><alias>sua</alias></lexeme>

  <!-- ===== L'anglais de la rue ===== -->

  <lexeme><grapheme>jobs</grapheme><alias>djobbes</alias></lexeme>
  <lexeme><grapheme>gangs</grapheme><alias>gaingues</alias></lexeme>
  <lexeme><grapheme>runs</grapheme><alias>ronnes</alias></lexeme>
  <lexeme><grapheme>stoolé</grapheme><alias>stoulé</alias></lexeme>
  <lexeme><grapheme>chum</grapheme><alias>tchomme</alias></lexeme>
  <lexeme><grapheme>chums</grapheme><alias>tchommes</alias></lexeme>
  <lexeme><grapheme>bum</grapheme><alias>bomme</alias></lexeme>
  <lexeme><grapheme>bums</grapheme><alias>bommes</alias></lexeme>
  <lexeme><grapheme>gun</grapheme><alias>gonne</alias></lexeme>
  <lexeme><grapheme>guns</grapheme><alias>gonnes</alias></lexeme>
  <lexeme><grapheme>deal</grapheme><alias>dile</alias></lexeme>
  <lexeme><grapheme>deals</grapheme><alias>diles</alias></lexeme>
  <lexeme><grapheme>dealer</grapheme><alias>dileur</alias></lexeme>
  <lexeme><grapheme>pusher</grapheme><alias>poucheur</alias></lexeme>
  <lexeme><grapheme>fake</grapheme><alias>féque</alias></lexeme>
  <lexeme><grapheme>cheap</grapheme><alias>tchipe</alias></lexeme>
  <lexeme><grapheme>check</grapheme><alias>tchèque</alias></lexeme>
  <lexeme><grapheme>Check</grapheme><alias>Tchèque</alias></lexeme>
  <lexeme><grapheme>checker</grapheme><alias>tchèquer</alias></lexeme>
  <lexeme><grapheme>checké</grapheme><alias>tchèqué</alias></lexeme>
  <lexeme><grapheme>shift</grapheme><alias>chifte</alias></lexeme>
  <lexeme><grapheme>loose</grapheme><alias>louse</alias></lexeme>
  <lexeme><grapheme>tough</grapheme><alias>toff</alias></lexeme>
  <lexeme><grapheme>right</grapheme><alias>raïte</alias></lexeme>
  <lexeme><grapheme>anyway</grapheme><alias>ènéwé</alias></lexeme>
  <lexeme><grapheme>sorry</grapheme><alias>sâri</alias></lexeme>

  <!-- ===== Le fun, la bouffe ===== -->

  <lexeme><grapheme>fun</grapheme><alias>fonne</alias></lexeme>
  <lexeme><grapheme>party</grapheme><alias>pârté</alias></lexeme>
  <lexeme><grapheme>cool</grapheme><alias>coule</alias></lexeme>
  <lexeme><grapheme>lunch</grapheme><alias>lonche</alias></lexeme>
  <lexeme><grapheme>punch</grapheme><alias>ponche</alias></lexeme>
  <lexeme><grapheme>chips</grapheme><alias>tchipse</alias></lexeme>
  <lexeme><grapheme>steamé</grapheme><alias>stimé</alias></lexeme>
  <lexeme><grapheme>steamés</grapheme><alias>stimés</alias></lexeme>

  <!-- ===== Le garage : un char se répare en anglais ===== -->

  <lexeme><grapheme>brakes</grapheme><alias>brèques</alias></lexeme>
  <lexeme><grapheme>bumper</grapheme><alias>bomper</alias></lexeme>
  <lexeme><grapheme>muffler</grapheme><alias>mofleur</alias></lexeme>
  <lexeme><grapheme>windshield</grapheme><alias>winnechîld</alias></lexeme>
  <lexeme><grapheme>flat</grapheme><alias>flatte</alias></lexeme>
  <lexeme><grapheme>clutch</grapheme><alias>clotche</alias></lexeme>
  <lexeme><grapheme>starter</grapheme><alias>starteur</alias></lexeme>
  <lexeme><grapheme>gear</grapheme><alias>guire</alias></lexeme>
  <lexeme><grapheme>hood</grapheme><alias>houde</alias></lexeme>
  <lexeme><grapheme>trunk</grapheme><alias>tronque</alias></lexeme>
  <lexeme><grapheme>truck</grapheme><alias>trok</alias></lexeme>
  <lexeme><grapheme>trucks</grapheme><alias>troks</alias></lexeme>
  <lexeme><grapheme>pick-up</grapheme><alias>pic-oppe</alias></lexeme>
  <lexeme><grapheme>scrap</grapheme><alias>scrappe</alias></lexeme>
  <lexeme><grapheme>junk</grapheme><alias>djonque</alias></lexeme>
  <lexeme><grapheme>towing</grapheme><alias>tôwing</alias></lexeme>
  <lexeme><grapheme>speed</grapheme><alias>spide</alias></lexeme>
  <!-- L'auto-patrouille, dans la bouche d'un bandit. -->
  <lexeme><grapheme>cruiser</grapheme><alias>crouseur</alias></lexeme>

  <!-- ===== Les noms des personnages, pas encore dits ===== -->

  <!-- Gus Lévesque : le S se tait. -->
  <lexeme><grapheme>Lévesque</grapheme><alias>Lévêque</alias></lexeme>
  <!-- Sven Haugen : le « au » norvégien s'ouvre, le G est dur. -->
  <lexeme><grapheme>Haugen</grapheme><alias>Haouguenne</alias></lexeme>
  <!-- Rosa Di Meo : deux syllabes, « Méo ». -->
  <lexeme><grapheme>Meo</grapheme><alias>Méo</alias></lexeme>
  <!-- Un Guy d'ici, seul : « Gui ». Après « Ti-Guy ». -->
  <lexeme><grapheme>Guy</grapheme><alias>Gui</alias></lexeme>

  <!-- ===== Les abréviations et les codes ===== -->

  <lexeme><grapheme>Mme</grapheme><alias>Madame</alias></lexeme>
  <lexeme><grapheme>Dr</grapheme><alias>Docteur</alias></lexeme>
  <lexeme><grapheme>Sgt</grapheme><alias>Sergent</alias></lexeme>
  <!-- Lu à la française, « OK » devient « o-ka ». -->
  <lexeme><grapheme>OK</grapheme><alias>oké</alias></lexeme>
  <lexeme><grapheme>Ok</grapheme><alias>oké</alias></lexeme>
  <lexeme><grapheme>ok</grapheme><alias>oké</alias></lexeme>
  <!-- Le code radio de la police : « dix-quatre », pas « dix moins quatre ». -->
  <lexeme><grapheme>10-4</grapheme><alias>dix-quatre</alias></lexeme>

</lexicon>
