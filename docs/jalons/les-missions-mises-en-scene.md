# Les missions mises en scène

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux que chaque mission vienne avec des animations et des
dialogues ». Devient une **décision** (« Contexte ») : une mission, c'est ses objectifs, ses
répliques à chaque temps (appel, intro, **pendant**, fin, échec) et ses **scènes** d'intro
et de fin — sinon elle n'est pas finie.

- ⚠️ **Mesuré le 16 sept. 2026** : les dialogues sont là sauf au milieu (le client de m3 est
  la seule réplique dite pendant une mission) ; les animations n'existent pas — `B.cinema`
  fige une boîte de texte, et la seule scène animée du jeu, l'ouverture, est écrite en dur
  (265 lignes pour une dizaine de secondes) ; **trois fins sur cinq sont dites par des
  absents** (m1, m4, m5) ; et la seule animation de fin est un `if (m.slug === 'm1')` dans
  `reussir()`.
- ⚠️ **Un vocabulaire, pas des scripts** : une scène est une liste de plans typés dans
  `missions.py` (`camera`, `marcher`, `conduire`, `geste`, `entrer`/`sortir`, `coupe`,
  `dire`, `titre`, `son`, `attendre`), six gestes dessinés une fois sur le sprite que
  partagent tous les personnages. Deux vagues : le metteur en scène **et l'ouverture
  réécrite dedans** (ses 13 juges sans retouche : la preuve que le vocabulaire suffit), puis
  les cinq missions de la v1.
- ⚠️ **Avant M16**, dont chaque mission l'écrira

⚠️ **1re vague livrée le 16 sept. 2026 — le metteur en scène.** Une scène est une liste de
plans dans `missions.py` (`TYPES_PLANS` : `camera`, `marcher`, `conduire`, `geste`,
`entrer`, `sortir`, `coupe`, `dire`, `titre`, `son`, `attendre`), jugée par
`erreurs_de_scene`, et `static/js/scenes.js` la joue sans connaître aucune scène par son nom
— un juge cherche dans son code le nom de chaque mission, personnage et lieu. Les plans se
suivent ; `ensemble` fait partir le suivant avec lui, `fond` laisse jouer sans retenir la
scène. **L'ouverture y est réécrite** (`SCENE_OUVERTURE`, quatorze plans à la place de 265
lignes) et **ses treize juges passent sans qu'on en touche un**. Tracée image par image
contre l'ancienne : même durée (1 399 images), même caméra, même noir, même titre, mêmes
bouffées de fumée, même position finale et même prochain dé — seules différences, le
bonhomme finit ses derniers 0,46 px jusqu'au quai (l'ancienne marche s'arrêtait à 55/56) et
le car quitte la ville une image plus tôt.

- ⚠️ **Il n'y a qu'une façon de finir** : jouée ou passée, la scène passe par `finir`, qui
  achève ce que les plans pas encore joués auraient laissé (le figurant rentré quitte la
  ville, celui qui sort se montre) — un juge passe la scène d'essai à huit moments et exige
  huit fois le même état et le même prochain dé. Un acteur dont le premier plan est `sortir`
  est caché dès la première image ; ce que la scène a fait naître la quitte avec elle ; le
  joueur revient où il était. **La mission se pose avant son intro** : le taxi de Marco
  existe pendant qu'il en parle, le titre et l'objectif s'annoncent à la fin, et le prochain
  dé est le même qu'avant. **Six gestes** (`montrer`, `donner`, `prendre`, `bras_croises`,
  `hausser`, `telephone`) dessinés une fois dans les trois faces du sprite que partagent
  tous les personnages ; un sprite qui ne les a pas retombe sur sa face. Le HUD se tait
  pendant toute scène, et le carton sait écrire un texte en plus du logo. **7 juges de banc
  et 7 Python, chaque règle vue rouge sans elle (15 mutations — la quinzième a trouvé une
  garde morte, retirée).**
- ⚠️ Un quatorzième juge d'ouverture, écrit après les treize par la session du logo
  (`test_le_titre_de_l_ouverture_est_le_logo`), fabriquait `B.ouverture` à la main pour
  dessiner le titre : il fabrique maintenant la scène (`B.scene` et son carton) — la règle
  jugée n'a pas bougé, et il rougit toujours quand le HUD n'écrit plus le logo. Reste la 2e
  vague : les cinq missions de la v1 mises en scène.

⚠️ **2e vague livrée le 17 sept. 2026 — les cinq missions de la v1, mises en scène.** Chaque
mission porte ses `scenes` (`intro`, `fin`) et ses répliques `pendant` dans `missions.py`,
et `erreurs_de_mise_en_scene` la refuse s'il en manque une : chaque réplique dite une fois,
des acteurs et des lieux connus (`place:`, `chez:`, `porte:`, `ruelle:`, `zone:`), et **une
fin qui se joue loin du donneur le fait venir ou va le voir chez lui**.

- Ti-Guy sort du garage, tend la clé et y rentre : le `if (m.slug === 'm1')` de `reussir()`
  est parti, et `parti_apres` le garde loin du terminus au rechargement. Madame Thibodeau
  montre ses deux Cravates — qui existent, la mission est posée avant l'intro ; Marco fait
  le tour du taxi et la caméra va voir le casse-croûte.
- ⚠️ **Bouchard et Josée parlent DEDANS, et la coupe sort voir la ville** : la pièce est
  mise de côté au noir (carte, gens et nom) puis rendue ; passée au milieu, elle revient
  d'abord. Les fins de M4 et M5 vont chez eux.
- ⚠️ **Au combiné quand celui qui parle n'est pas là**, tranché à la ligne : l'appel et
  l'échec toujours ; l'intro, la fin et `pendant` selon qu'il se tient à douze tuiles.
- ⚠️ **Jamais en pleine action** : l'argent et `donne` tout de suite, la scène de fin attend
  l'arrêt et moins de 3★ ; une intro à 3★ se dit sans scène.
- Quatre répliques `pendant` (M1, M2, M4, M5 ; le client de M3 l'était déjà) et leurs voix
  ElevenLabs, comptées **après** `echec` : aucun mp3 payé ne change de nom. Aucun slug de
  mission dans `histoire.js` (« Le Faubourg est tranquille » est passé dans `REPOS`).
- Le moteur compte les plans sautés, et un juge exige zéro pour chaque scène du catalogue —
  c'est lui qui a vu une mise en place qui oubliait le taxi. **6 juges Python de plus (13 en
  tout), 19 de banc et 1 de navigateur (M1 de l'intro à la fin, aucune erreur console), 17
  mutations toutes rouges.** Neuf juges existants suivent le nouveau comportement (parler
  joue une scène ; les répliques `pendant` figent la rue à pied) sans perdre ce qu'ils
  gardaient. À écouter par Martin : les quatre voix `pendant`.
