<?xml version="1.0" encoding="UTF-8"?>
<!--
  LE DICTIONNAIRE DE PRONONCIATION DE BANDINI — comment les voix disent un mot,
  sans changer le mot qu'on lit.

  ElevenLabs applique ces règles de SON côté, au moment de générer : la boîte de
  dialogue affiche « Prenez donc la rue », la voix dit « Prenez don la rue ». Le
  texte et le jeu= ne bougent pas, et le juge mot à mot (test_interpretation.py)
  ne voit rien : c'est la troisième voie que docs/ecrire-un-accent.md § 5
  laissait fermée. Recette : docs/voix-de-l-histoire.md, « Le dictionnaire ».

  ⚠️ Des PHONÈMES IPA, plus des alias (Martin, 22 sept. 2026, après un essai
  « Deux piastres. » → pjɑs : « ça marche bien, je préfère que tu y ailles avec
  ça »). Le phonème dit le son exact (l'affrication de « p'tit », ptsɪ ; le
  « gang » d'ici, ɡɛŋ) là où un alias passait par une orthographe que le modèle
  relisait à sa façon. Il dépend du modèle : eleven_v3 le lit, multilingual_v2
  l'ignore — toutes les voix qui prennent ce dictionnaire sont en v3.

  ⚠️ Chaque règle garde sa lecture EN CLAIR juste après elle, « dit : piasses » :
  personne ici ne relit l'IPA d'un coup d'œil. Le juge exige les deux.

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
  <lexeme><grapheme>donc</grapheme><phoneme>dɔ̃</phoneme></lexeme> <!-- dit : don -->

  <!-- « Quinze mille piastres » : au Québec, des piasses. -->
  <lexeme><grapheme>piastres</grapheme><phoneme>pjɑs</phoneme></lexeme> <!-- dit : piasses -->

  <!-- Le « th » invite une lecture anglaise ; on dit « asteure ». -->
  <lexeme><grapheme>astheure</grapheme><phoneme>astœʁ</phoneme></lexeme> <!-- dit : asteure -->
  <lexeme><grapheme>Astheure</grapheme><phoneme>astœʁ</phoneme></lexeme> <!-- dit : Asteure -->

  <!-- « Envoye, fonce! » : lu à la française, le E final se tait (« envoie »).
       Ici on l'entend : « envoye » rime avec « oreille ». -->
  <lexeme><grapheme>Envoye</grapheme><phoneme>ɑ̃vwɛj</phoneme></lexeme> <!-- dit : Envoille -->

  <!-- « Skateux » se dit « skèteux », pas « skat-eux ». -->
  <lexeme><grapheme>Skateux</grapheme><phoneme>skɛtø</phoneme></lexeme> <!-- dit : Skèteux -->

  <!-- ===== Les mots mangés : une apostrophe, une syllabe de moins ===== -->

  <!-- L'apostrophe au milieu d'un mot se lit parfois comme une coupure : on
       écrit d'un bloc ce qui se dit d'un bloc. -->
  <lexeme><grapheme>su'l</grapheme><phoneme>syl</phoneme></lexeme> <!-- dit : sul -->
  <lexeme><grapheme>j'suis</grapheme><phoneme>ʃy</phoneme></lexeme> <!-- dit : chu -->
  <lexeme><grapheme>p't-être</grapheme><phoneme>ptɛt</phoneme></lexeme> <!-- dit : ptête -->
  <lexeme><grapheme>p'tit</grapheme><phoneme>ptsɪ</phoneme></lexeme> <!-- dit : ptit -->
  <lexeme><grapheme>y'a</grapheme><phoneme>jɑ</phoneme></lexeme> <!-- dit : ya -->
  <lexeme><grapheme>Y a</grapheme><phoneme>jɑ</phoneme></lexeme> <!-- dit : Ya -->
  <lexeme><grapheme>v'là</grapheme><phoneme>vlɑ</phoneme></lexeme> <!-- dit : vla -->

  <!-- ===== Les mots anglais du quotidien, comme on les dit ici ===== -->

  <!-- « une run qui traîne » -->
  <lexeme><grapheme>run</grapheme><phoneme>ʁɔn</phoneme></lexeme> <!-- dit : ronne -->
  <!-- « full haut » : pas le « u » de « futé ». -->
  <lexeme><grapheme>full</grapheme><phoneme>fʊl</phoneme></lexeme> <!-- dit : foule -->
  <!-- « Un stool nerveux » -->
  <lexeme><grapheme>stool</grapheme><phoneme>stul</phoneme></lexeme> <!-- dit : stoule -->
  <!-- La pub de Gus : « smoke mite », sans le « -ed ». -->
  <lexeme><grapheme>smoked meat</grapheme><phoneme>smok mit</phoneme></lexeme> <!-- dit : smoke mite -->
  <!-- « j'ai une job » : le J anglais, jamais celui de « jaune ». -->
  <lexeme><grapheme>job</grapheme><phoneme>dʒɔb</phoneme></lexeme> <!-- dit : djobbe -->
  <!-- « le reste de la gang » : ici, ça rime avec « gain », pas avec « gant ». -->
  <lexeme><grapheme>gang</grapheme><phoneme>ɡɛŋ</phoneme></lexeme> <!-- dit : gaingue -->
  <!-- « Le docker va essayer de filer » : dockeur, comme on l'entend au port. -->
  <lexeme><grapheme>docker</grapheme><phoneme>dɔkœʁ</phoneme></lexeme> <!-- dit : dockeur -->

  <!-- ===== Les noms ===== -->

  <!-- L'inspectrice Roy : un Roy d'ici se dit « Roi ». -->
  <lexeme><grapheme>Roy</grapheme><phoneme>ʁwa</phoneme></lexeme> <!-- dit : Roi -->
  <!-- Prévost, le patron de l'usine : le S et le T se taisent. -->
  <lexeme><grapheme>Prévost</grapheme><phoneme>pʁevo</phoneme></lexeme> <!-- dit : Prévo -->
  <!-- Ti-Guy : Guy comme « gui », jamais le « guy » anglais. AVANT « Guy ». -->
  <lexeme><grapheme>Ti-Guy</grapheme><phoneme>tsiɡi</phoneme></lexeme> <!-- dit : Ti-Gui -->

  <!-- ===== La typographie ===== -->

  <!-- « Perdu mon camion ET ma marchandise » : la majuscule insiste, mais un
       mot de deux capitales s'épelle comme un sigle (« E.T. »). -->
  <lexeme><grapheme>ET</grapheme><phoneme>e</phoneme></lexeme> <!-- dit : et -->

  <!-- =================================================================== -->
  <!-- ===== EN RÉSERVE : des mots qu'aucune réplique ne dit encore ===== -->
  <!-- =================================================================== -->

  <!-- ===== Le parler d'ici, ses autres formes ===== -->

  <!-- En tête de phrase, la majuscule fait une autre règle. -->
  <lexeme><grapheme>Donc</grapheme><phoneme>dɔ̃</phoneme></lexeme> <!-- dit : Don -->
  <lexeme><grapheme>coudonc</grapheme><phoneme>kudɔ̃</phoneme></lexeme> <!-- dit : coudon -->
  <lexeme><grapheme>Coudonc</grapheme><phoneme>kudɔ̃</phoneme></lexeme> <!-- dit : Coudon -->
  <lexeme><grapheme>piastre</grapheme><phoneme>pjɑs</phoneme></lexeme> <!-- dit : piasse -->
  <lexeme><grapheme>envoye</grapheme><phoneme>ɑ̃vwɛj</phoneme></lexeme> <!-- dit : envoille -->
  <lexeme><grapheme>skateux</grapheme><phoneme>skɛtø</phoneme></lexeme> <!-- dit : skèteux -->

  <!-- ===== Les mots mangés, leurs autres formes ===== -->

  <lexeme><grapheme>J'suis</grapheme><phoneme>ʃy</phoneme></lexeme> <!-- dit : Chu -->
  <lexeme><grapheme>j'sais pas</grapheme><phoneme>ʃepɑ</phoneme></lexeme> <!-- dit : chépas -->
  <lexeme><grapheme>J'sais pas</grapheme><phoneme>ʃepɑ</phoneme></lexeme> <!-- dit : Chépas -->
  <lexeme><grapheme>t'sais</grapheme><phoneme>tse</phoneme></lexeme> <!-- dit : tsé -->
  <lexeme><grapheme>T'sais</grapheme><phoneme>tse</phoneme></lexeme> <!-- dit : Tsé -->
  <lexeme><grapheme>P't-être</grapheme><phoneme>ptɛt</phoneme></lexeme> <!-- dit : Ptête -->
  <lexeme><grapheme>P'tit</grapheme><phoneme>ptsɪ</phoneme></lexeme> <!-- dit : Ptit -->
  <lexeme><grapheme>p'tite</grapheme><phoneme>ptsɪt</phoneme></lexeme> <!-- dit : ptite -->
  <lexeme><grapheme>P'tite</grapheme><phoneme>ptsɪt</phoneme></lexeme> <!-- dit : Ptite -->
  <lexeme><grapheme>Y'a</grapheme><phoneme>jɑ</phoneme></lexeme> <!-- dit : Ya -->
  <lexeme><grapheme>y'avait</grapheme><phoneme>javɛ</phoneme></lexeme> <!-- dit : yavait -->
  <lexeme><grapheme>Y'avait</grapheme><phoneme>javɛ</phoneme></lexeme> <!-- dit : Yavait -->
  <lexeme><grapheme>V'là</grapheme><phoneme>vlɑ</phoneme></lexeme> <!-- dit : Vla -->
  <!-- « su'a table » : sur la. -->
  <lexeme><grapheme>su'a</grapheme><phoneme>sya</phoneme></lexeme> <!-- dit : sua -->

  <!-- ===== L'anglais de la rue ===== -->

  <lexeme><grapheme>jobs</grapheme><phoneme>dʒɔb</phoneme></lexeme> <!-- dit : djobbes -->
  <lexeme><grapheme>gangs</grapheme><phoneme>ɡɛŋ</phoneme></lexeme> <!-- dit : gaingues -->
  <lexeme><grapheme>runs</grapheme><phoneme>ʁɔn</phoneme></lexeme> <!-- dit : ronnes -->
  <lexeme><grapheme>stoolé</grapheme><phoneme>stule</phoneme></lexeme> <!-- dit : stoulé -->
  <lexeme><grapheme>chum</grapheme><phoneme>tʃɔm</phoneme></lexeme> <!-- dit : tchomme -->
  <lexeme><grapheme>chums</grapheme><phoneme>tʃɔm</phoneme></lexeme> <!-- dit : tchommes -->
  <lexeme><grapheme>bum</grapheme><phoneme>bɔm</phoneme></lexeme> <!-- dit : bomme -->
  <lexeme><grapheme>bums</grapheme><phoneme>bɔm</phoneme></lexeme> <!-- dit : bommes -->
  <lexeme><grapheme>gun</grapheme><phoneme>ɡɔn</phoneme></lexeme> <!-- dit : gonne -->
  <lexeme><grapheme>guns</grapheme><phoneme>ɡɔn</phoneme></lexeme> <!-- dit : gonnes -->
  <lexeme><grapheme>deal</grapheme><phoneme>dil</phoneme></lexeme> <!-- dit : dile -->
  <lexeme><grapheme>deals</grapheme><phoneme>dil</phoneme></lexeme> <!-- dit : diles -->
  <lexeme><grapheme>dealer</grapheme><phoneme>dilœʁ</phoneme></lexeme> <!-- dit : dileur -->
  <lexeme><grapheme>pusher</grapheme><phoneme>pʊʃœʁ</phoneme></lexeme> <!-- dit : poucheur -->
  <lexeme><grapheme>fake</grapheme><phoneme>fek</phoneme></lexeme> <!-- dit : féque -->
  <lexeme><grapheme>cheap</grapheme><phoneme>tʃip</phoneme></lexeme> <!-- dit : tchipe -->
  <lexeme><grapheme>check</grapheme><phoneme>tʃɛk</phoneme></lexeme> <!-- dit : tchèque -->
  <lexeme><grapheme>Check</grapheme><phoneme>tʃɛk</phoneme></lexeme> <!-- dit : Tchèque -->
  <lexeme><grapheme>checker</grapheme><phoneme>tʃɛke</phoneme></lexeme> <!-- dit : tchèquer -->
  <lexeme><grapheme>checké</grapheme><phoneme>tʃɛke</phoneme></lexeme> <!-- dit : tchèqué -->
  <lexeme><grapheme>shift</grapheme><phoneme>ʃɪft</phoneme></lexeme> <!-- dit : chifte -->
  <lexeme><grapheme>loose</grapheme><phoneme>lus</phoneme></lexeme> <!-- dit : louse -->
  <lexeme><grapheme>tough</grapheme><phoneme>tɔf</phoneme></lexeme> <!-- dit : toff -->
  <lexeme><grapheme>right</grapheme><phoneme>ʁajt</phoneme></lexeme> <!-- dit : raïte -->
  <lexeme><grapheme>anyway</grapheme><phoneme>ɛnewe</phoneme></lexeme> <!-- dit : ènéwé -->
  <lexeme><grapheme>sorry</grapheme><phoneme>sɑʁi</phoneme></lexeme> <!-- dit : sâri -->

  <!-- ===== Le fun, la bouffe ===== -->

  <lexeme><grapheme>fun</grapheme><phoneme>fɔn</phoneme></lexeme> <!-- dit : fonne -->
  <lexeme><grapheme>party</grapheme><phoneme>pɑʁte</phoneme></lexeme> <!-- dit : pârté -->
  <lexeme><grapheme>cool</grapheme><phoneme>kul</phoneme></lexeme> <!-- dit : coule -->
  <lexeme><grapheme>lunch</grapheme><phoneme>lɔnʃ</phoneme></lexeme> <!-- dit : lonche -->
  <lexeme><grapheme>punch</grapheme><phoneme>pɔnʃ</phoneme></lexeme> <!-- dit : ponche -->
  <lexeme><grapheme>chips</grapheme><phoneme>tʃɪps</phoneme></lexeme> <!-- dit : tchipse -->
  <lexeme><grapheme>steamé</grapheme><phoneme>stime</phoneme></lexeme> <!-- dit : stimé -->
  <lexeme><grapheme>steamés</grapheme><phoneme>stime</phoneme></lexeme> <!-- dit : stimés -->

  <!-- ===== Le garage : un char se répare en anglais ===== -->

  <lexeme><grapheme>brakes</grapheme><phoneme>bʁek</phoneme></lexeme> <!-- dit : brèques -->
  <lexeme><grapheme>bumper</grapheme><phoneme>bɔmpœʁ</phoneme></lexeme> <!-- dit : bomper -->
  <lexeme><grapheme>muffler</grapheme><phoneme>mɔflœʁ</phoneme></lexeme> <!-- dit : mofleur -->
  <lexeme><grapheme>windshield</grapheme><phoneme>wɪnʃild</phoneme></lexeme> <!-- dit : winnechîld -->
  <lexeme><grapheme>flat</grapheme><phoneme>flat</phoneme></lexeme> <!-- dit : flatte -->
  <lexeme><grapheme>clutch</grapheme><phoneme>klɔtʃ</phoneme></lexeme> <!-- dit : clotche -->
  <lexeme><grapheme>starter</grapheme><phoneme>stɑʁtœʁ</phoneme></lexeme> <!-- dit : starteur -->
  <lexeme><grapheme>gear</grapheme><phoneme>ɡiʁ</phoneme></lexeme> <!-- dit : guire -->
  <lexeme><grapheme>hood</grapheme><phoneme>hʊd</phoneme></lexeme> <!-- dit : houde -->
  <lexeme><grapheme>trunk</grapheme><phoneme>tʁɔŋk</phoneme></lexeme> <!-- dit : tronque -->
  <lexeme><grapheme>truck</grapheme><phoneme>tʁɔk</phoneme></lexeme> <!-- dit : trok -->
  <lexeme><grapheme>trucks</grapheme><phoneme>tʁɔk</phoneme></lexeme> <!-- dit : troks -->
  <lexeme><grapheme>pick-up</grapheme><phoneme>pɪkɔp</phoneme></lexeme> <!-- dit : pic-oppe -->
  <lexeme><grapheme>scrap</grapheme><phoneme>skʁap</phoneme></lexeme> <!-- dit : scrappe -->
  <lexeme><grapheme>junk</grapheme><phoneme>dʒɔŋk</phoneme></lexeme> <!-- dit : djonque -->
  <lexeme><grapheme>towing</grapheme><phoneme>towɪŋ</phoneme></lexeme> <!-- dit : tôwing -->
  <lexeme><grapheme>speed</grapheme><phoneme>spid</phoneme></lexeme> <!-- dit : spide -->
  <!-- L'auto-patrouille, dans la bouche d'un bandit. -->
  <lexeme><grapheme>cruiser</grapheme><phoneme>kʁusœʁ</phoneme></lexeme> <!-- dit : crouseur -->

  <!-- ===== Les noms des personnages, pas encore dits ===== -->

  <!-- Gus Lévesque : le S se tait. -->
  <lexeme><grapheme>Lévesque</grapheme><phoneme>levɛk</phoneme></lexeme> <!-- dit : Lévêque -->
  <!-- Sven Haugen : le « au » norvégien s'ouvre, le G est dur. -->
  <lexeme><grapheme>Haugen</grapheme><phoneme>haʊɡɛn</phoneme></lexeme> <!-- dit : Haouguenne -->
  <!-- Rosa Di Meo : deux syllabes, « Méo ». -->
  <lexeme><grapheme>Meo</grapheme><phoneme>meo</phoneme></lexeme> <!-- dit : Méo -->
  <!-- Un Guy d'ici, seul : « Gui ». Après « Ti-Guy ». -->
  <lexeme><grapheme>Guy</grapheme><phoneme>ɡi</phoneme></lexeme> <!-- dit : Gui -->

  <!-- ===== Les abréviations et les codes ===== -->

  <lexeme><grapheme>Mme</grapheme><phoneme>madam</phoneme></lexeme> <!-- dit : Madame -->
  <lexeme><grapheme>Dr</grapheme><phoneme>dɔktœʁ</phoneme></lexeme> <!-- dit : Docteur -->
  <lexeme><grapheme>Sgt</grapheme><phoneme>sɛʁʒɑ̃</phoneme></lexeme> <!-- dit : Sergent -->
  <!-- Lu à la française, « OK » devient « o-ka ». -->
  <lexeme><grapheme>OK</grapheme><phoneme>oke</phoneme></lexeme> <!-- dit : oké -->
  <lexeme><grapheme>Ok</grapheme><phoneme>oke</phoneme></lexeme> <!-- dit : oké -->
  <lexeme><grapheme>ok</grapheme><phoneme>oke</phoneme></lexeme> <!-- dit : oké -->
  <!-- Le code radio de la police : « dix-quatre », pas « dix moins quatre ». -->
  <lexeme><grapheme>10-4</grapheme><phoneme>dizkatʁ</phoneme></lexeme> <!-- dit : dix-quatre -->

</lexicon>
