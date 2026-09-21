# Jouer juste — cinématiques, animations et voix de Bandini

Guide pour toute personne (ou IA) qui monte une mission : **comment mettre une
scène en images, et comment faire dire une réplique avec de l'émotion.** Trois
moitiés, dans cet ordre :

1. **la scène** — ce que la caméra, les gestes et le temps peuvent faire, avec
   les plans qui existent vraiment (`TYPES_PLANS`) ;
2. **la voix** — écrire pour la bouche, jouer une intention, poser les balises
   d'émotion d'ElevenLabs v3 (le `jeu=` de chaque réplique, dans le fichier de la mission ;
   `app/interpretation.py` garde la liste des balises et la finition) ;
3. **les deux ensemble** — quand la parole et l'image se répondent.

> Ce document ne remplace ni `docs/comment-monter-les-missions.md` (la
> *recette*, le « comment » technique) ni `docs/ecrire-drole.md` (le texte, et ce
> qui le rend drôle) : il dit **comment bien jouer** ce que ces deux-là font
> écrire. La décision est dans `docs/missions-en-scene.md`, « Le jeu d'acteur ».

⚠️ **Ce que les juges vérifient, et ce qu'ils ne vérifient pas.** Ils jugent le
**câblage** : la scène se termine, les répliques sont dites une fois, la voix dit
les mêmes mots que la boîte, les balises sont connues de v3. **Aucun juge ne sait
si une scène est belle ni si une voix est juste** — une mission peut passer tous
les tests et jouer comme une boîte de dialogue. Le jeu d'acteur se juge **à
l'œil et à l'oreille**, et c'est Martin qui écoute. Ce guide est donc une liste
de gestes de métier, pas une liste de règles vérifiées.

---

## 1. Le principe : un bonhomme de 16 pixels n'a pas de visage

Tous les personnages sont le même sprite `joueur` repeint, vu de profil, sans
expression. **Il ne peut pas sourire, froncer les sourcils, pleurer.** Ce qu'un
acteur de cinéma fait avec son visage, Bandini le fait avec **quatre outils** :

| Outil | Ce qu'il joue |
|---|---|
| **La voix** | presque toute l'émotion — c'est le visage du jeu |
| **Le geste** (6 en tout) | l'intention du corps : montrer, donner, attendre, se dérober |
| **La caméra** | où regarder, et donc quoi ressentir : ce qu'on montre, ce qu'on cache, quand |
| **Le temps** | les silences, les battements, ce qu'on laisse retomber |

**Conséquence : on ne compense jamais un manque de jeu par plus de texte.** Une
scène plate ne s'arrange pas avec une réplique de plus ; elle s'arrange avec un
regard de caméra, un silence, ou une voix qui change de ton.

---

## 2. La scène — la mettre en images

### 2.1 Une scène = une chose que le joueur apprend ou ressent

Avant d'écrire un seul plan, **une phrase** : *« Après cette scène, le joueur sait
_ ___ / ressent _ ___. »* Si la phrase ne s'écrit pas, la scène n'a pas de raison
d'être — elle sera une pause. Exemples tirés du catalogue :

- m1, intro : *sait où est le char* (Ti-Guy montre, la caméra va voir la ruelle) ;
- m1, fin : *ressent qu'il est accepté* (Ti-Guy sort du garage, fait l'effort de
  venir jusqu'à lui, tend la clé) ;
- m97, intro : *ressent la trahison dite comme un détail* (Marco hausse les épaules en
  lâchant « Tiens, les voilà » — `hausser` sur une réplique `[menacingly]`).

### 2.2 Montrer avant de dire — et ne pas dire ce qu'on montre

La caméra qui va voir un lieu **remplace** une phrase d'explication. Si Ti-Guy
montre le garage et que la caméra y va, la réplique n'a pas à décrire le garage :
elle peut dire ce que **l'image ne montre pas** (ce qu'il en pense, ce qui est
risqué, ce qu'il attend de toi). L'image porte le *où*, la voix porte le *pourquoi*.

⚠️ Le contraire aussi : ne montre jamais un lieu que la réplique n'a pas nommé.
La caméra qui part sans raison est un tic, pas une mise en scène.

### 2.3 Le geste tombe sur le mot qui le porte, la caméra arrive avec lui

⚠️ **Comment les plans s'enchaînent** (`demarrerLesSuivants`, `scenes.js`) : un plan
`ensemble` — ou instantané — fait partir **le suivant sur la même image** ; le
premier plan qui dure et qui n'est pas `ensemble` retient la scène jusqu'à sa fin.
Écrire `geste` (`ensemble`) puis `dire`, c'est donc les lancer **ensemble**, pas
l'un après l'autre :

```python
{"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:garage",
 "duree": 70, "ensemble": True},                          # le bras part…
{"type": "dire", "repliques": [3, 4], "ensemble": True},  # …avec la réplique qui nomme la ruelle
{"type": "attendre", "duree": 30},                        # la voix continue…
{"type": "coupe", "vers": "ruelle:garage:24", ...},       # …et l'image change SOUS elle
```

C'est le m1 de Ti-Guy : le geste tombe **sur** la réplique qui nomme la ruelle, et
la coupe arrive **pendant** qu'il parle encore — la voix passe par-dessus le
changement d'image. Même logique pour la caméra (`ensemble` + `courbe: "freine"`) :
elle arrive au moment où le mot **atterrit**, pas dix images après.

**Un geste qui précède la parole** (l'anticipation d'un comédien : le corps décide
avant la bouche) s'écrit avec un `attendre` entre les deux :
`geste` (`ensemble`) → `attendre` 8–15 → `dire`. Le lecteur le permet ; ⚠️ **aucune
mission du catalogue ne le fait encore** : essaie-le, regarde-le, garde-le s'il joue.

### 2.4 Chaque geste dit quelque chose — choisis-le pour ce qu'il dit

Six gestes existent, dessinés une fois pour tout le monde. Le choix du geste **est**
une décision de jeu :

| Geste | Ce qu'il dit | À réserver pour |
|---|---|---|
| `montrer` | « regarde là » — une direction, un enjeu | l'intro : la caméra suit le bras |
| `donner` | la confiance, le prix payé | la fin : ce qu'on gagne se **voit** passer de main en main |
| `prendre` | la demande, ou l'appropriation | reprendre la caisse, le colis : le geste avant la gratitude |
| `bras_croises` | l'attente, l'autorité, la méfiance | un donneur qui jauge (Bouchard, Josée, Marco qui trahit) |
| `hausser` | « je n'y peux rien » / « ça m'est égal » | une complicité désinvolte (Marco), ou une menace qui fait l'innocente |
| `telephone` | quelqu'un parle de loin | une fin dite d'ailleurs (Bouchard au combiné, m4) — l'**appel**, lui, n'a pas de scène : le combiné fige déjà la ville |

**Donne à chaque personnage sa gestuelle, et garde-la** d'une mission à l'autre : c'est
ce qui le fait reconnaître avant qu'il ne parle. Aujourd'hui, le défaut fait croiser
les bras aux donneurs qu'on rencontre dedans (Bouchard, Josée), Marco hausse les
épaules à m97, Thibodeau prend et donne. Ce n'est pas encore une règle : c'est la
pente que les scènes ont prise, à suivre ou à décider.

### 2.5 Le temps est un outil : anticipation, battement, retombée

Les durées sont en **images (60 = une seconde)**. Les quatre premières lignes sont
les temps des scènes **déjà jouées** (`TEMPS_PAR_DEFAUT`, et les scènes écrites à la
main : geste 60–70, garde 90) ; les deux dernières sont des **repères** tirés des
attentes qu'on y trouve (`attendre` 15 et 55 dans l'ouverture, 30 dans m1) — à régler
à l'œil.

| Ce qu'on joue | Durée | Pourquoi |
|---|---|---|
| un geste (`montrer`, `donner`, `prendre`) | **60–70** | une seconde : lisible sans traîner |
| une posture de garde (`bras_croises`) | **90** | le corps parle pendant que la bouche se tait |
| la caméra qui va voir | **45**, `freine` | assez long pour suivre, assez court pour ne pas perdre le fil |
| la caméra qui revient | **40**, `freine` | un peu plus vite que l'aller |
| un battement avant un moment fort (`attendre`) | **15–30** | le souffle avant le coup |
| ce qu'on laisse retomber après une réplique forte | **30–55** | la réaction — voir § 2.6 |

⚠️ **Le plafond** : une scène ne tient pas plus de 3 secondes (180 images) après
son dernier mot, et se termine **toujours** (un plan qui ne se résout pas est
sauté). Le silence, oui — l'attente, non.

**Les courbes.** `freine` à l'**arrivée** (la caméra ralentit en s'approchant),
`accelere` au **départ** (un char qui s'en va), `droite` presque jamais pour de la
caméra : un mouvement à vitesse constante est un mouvement de machine.

### 2.6 Le silence joue aussi

Les meilleurs moments d'une scène sont souvent **ce qui suit** une réplique, pas la
réplique. Après celle qui compte : un `attendre` de 30 images, et elle retombe. Un plan
`attendre` est un **battement de comédien** — l'ouverture en tient un de 55 images
quand le bonhomme arrive au quai, m1 un de 30 avant la coupe sur la ruelle.

⚠️ **Le silence dramatique vit dans la scène, pas dans le fichier audio.** La
finition des voix rogne tout silence de plus de 0,7 s et ne laisse que 0,35 s de
temps mort : *demander à la voix un grand silence, c'est l'obtenir raboté*. Un
long silence se joue par un plan `attendre` (ou une caméra qui tient) **après**
le `dire`.

### 2.7 Ne montre pas un coin vide, ne parle pas de nulle part

Trois règles du moteur qui sont d'abord des règles de jeu :

- **La mission se pose avant son intro** : la caméra ne filme jamais un lieu où
  ce qu'on annonce n'existe pas encore (m2 : `cible` nomme le point d'où les
  Cravates *arriveront*, la caméra le voit vide, puis elles surgissent).
- **La fin est dite par quelqu'un qui est là** : sinon `coupe` chez le donneur, ou
  fais-le `sortir` et `marcher`. Une voix qui sort de nulle part est un bug de jeu
  d'acteur autant que de câblage.
- **La fin passe la main** : si elle nomme le prochain donneur, la caméra va le
  voir. C'est ce qui fait qu'une histoire est une histoire et pas cent missions.

### 2.8 Ce que le moteur ne sait pas (encore) — et comment le demander

Sois honnête sur la limite : **pas de gros plan, pas de zoom, pas de tremblement
d'écran dans les plans, pas de regard qui se tourne** (l'orientation se déduit du
sens du geste ou de la marche). Si une scène a *vraiment* besoin d'un de ces outils, **ajoute un type de plan**
(`TYPES_PLANS`, avec son juge de banc) qui servira aux cent missions — jamais un
`if (slug === 'q07')` dans `scenes.js`. Et demande-toi d'abord si un `attendre`
bien placé ne fait pas le même travail.

### 2.9 Le storyboard en trois lignes, avant d'écrire les plans

Pour chaque scène (`intro`, `fin`), écris **trois lignes** :

```
Intention : ce que le joueur apprend ou ressent (une phrase)
On voit    : le geste, la caméra, ce qui entre ou sort (dans l'ordre)
On entend  : les répliques, et le silence qui suit la plus forte
```

Puis traduis en plans. Si « On voit » est vide, c'est une boîte de dialogue : voir
§ 4, le **défaut** que le moteur bâtit tout seul (`scene_par_defaut`) est un
minimum honnête, pas un plafond. **Écris la tienne quand tu veux mieux.**

---

## 3. La voix — écrire pour la bouche, puis jouer une intention

Toutes les répliques sont dites par ElevenLabs **eleven_v3**, une voix par
personnage. Le texte affiché et le **jeu** (`jeu=`) sont **deux textes de la même phrase**,
écrits ensemble dans le fichier de la mission (`_l(qui, texte, jeu=…)`) : le premier se lit,
le second se joue.

### 3.1 Écrire pour la bouche

- **Court.** 8 à 110 caractères, une phrase ou deux (jugé) ; **dix répliques par
  mission au plus** (jugé). Une réplique longue devient un monologue plat : coupe-la
  en deux **battements** avec un changement de ton entre les deux.
- **Parlé, pas écrit.** « Pis », « astheure », « icitte », « ben » : la voix
  québécoise n'est crédible que si le texte l'est. Lis la réplique **à voix haute**
  avant de la donner ; si elle trébuche dans ta bouche, elle trébuchera dans la sienne.
- **Le mot fort à la fin** (`ecrire-drole.md` § 2.3) : c'est là que la voix
  descend, que la pause tombe, que la balise se mérite.
- **Une pensée par réplique.** Deux idées, deux répliques (et deux tons).

### 3.2 L'intention avant la balise

Une balise ne *fait* pas le jeu ; elle **le note**. Le jeu vient de la question
qu'on pose à chaque réplique **avant** de choisir la moindre balise :

> **Que veut ce personnage de celui qui l'écoute — et que cache-t-il ?**

Un verbe d'action par réplique : *convaincre, rassurer, menacer, tester, cacher,
supplier, congédier, séduire.* « Il te laisse sa dette avec » ne *dit* pas la dette :
elle **prévient**. La voix qui prévient (`[gravely]`) n'est pas celle qui informe.

**Le sous-texte est là où le jeu devient intéressant** : l'écart entre ce qu'on dit
et ce qu'on veut. Marco dit « Garde le taxi… il est à toi » (`[impressed]`) alors
qu'il vient de vouloir te faire tomber — la voix admire pendant que les mots
congédient. Josée ne hausse jamais le ton : elle est *plus* menaçante posée
(`[menacingly]`, `[matter-of-fact]`) qu'en colère.

### 3.3 Un arc, pas un ton

Une mission n'est pas une émotion ; c'est un **trajet**. Le personnage doit **ne
pas sonner pareil** à l'intro, à la fin et à l'échec — et le contraste est ce qui
fait sentir l'histoire. Les arcs du catalogue :

| Personnage | Intro | Fin | Échec |
|---|---|---|---|
| Ti-Guy, m1 | `excited`, `quietly`, `mischievously`, `serious` | `excited` + `laughs`, `warmly` | `disappointed` + `sighs` |
| Mme Thibodeau, m2 | `worried` (l'appel), `bitterly` → `angry`, `quietly` | `relieved` → `warmly`, `tenderly` | `concerned` |
| Marco, m97 | `coldly` (l'appel), `bitterly`, `menacingly` | `impressed`, `somber` | `coldly` (et `worried` en pendant) |

Deux règles qui en sortent :

- **La fin sonne autrement que l'intro.** Le soulagement se joue *par contraste*
  avec l'inquiétude d'avant : Thibodeau passe de `worried` à `relieved` puis
  `tenderly` en deux répliques.
- **Un personnage garde un registre de base.** Josée est froide même quand elle est
  chaude ; Bouchard est bourru même quand il s'inquiète. Le ton **varie autour** de
  ce registre, il ne le quitte pas.

### 3.4 Les balises v3 — la liste fermée

Les balises se posent **dans le texte joué**, entre crochets, **en anglais**,
même sur une phrase française : ce sont des indications de jeu, pas des mots.
La liste est **fermée** (`interpretation.BALISES`) : v3 lit à voix haute une
balise qu'il ne comprend pas (« crochet, tristement »).

- **`TONS`** — ce qu'on *ressent* : `warmly`, `coldly`, `worried`, `menacingly`,
  `tenderly`, `bitterly`, `mischievously`, `relieved`, `somber`…
- **`CORPS`** — ce que le corps *fait* : `sighs`, `laughs`, `groans`, `whispers`,
  `shouting`.

⚠️ **Toute réplique porte au moins un TON** (jugé). Un soupir ou un rire dit
*comment* le corps parle, pas *ce qu'on ressent* : une réplique qui ne porte que
`[sighs]` sort plate à côté des autres. Le corps **colore** le ton, il ne le remplace pas.

⚠️ **Ce que la voix choisie peut ou non faire.** Les balises ne transforment pas
une voix : « une voix qui chuchote ne se met pas à crier avec `[shouting]` ».
**Choisis la voix pour l'étendue du rôle** avant d'écrire le jeu — un personnage qui
doit hurler ne se joue pas avec une voix rauque et basse (voir § 3.8). Une balise
qui ne colle pas au caractère de la voix affaiblit la réplique au lieu de la porter.

### 3.5 Ce que la ponctuation joue

| Signe | Effet | À retenir |
|---|---|---|
| `…` | une pause qui pèse | **un seul endroit par phrase** : là où elle respire vraiment |
| `—` | un revirement, une phrase qui se reprend | pour changer d'idée au milieu |
| `!` | plus d'énergie | avec `[excited]`, `[enthusiastic]`, `[shouting]` : c'est ce que les répliques du catalogue en font |
| `.` | un ton posé, tenu | la ponctuation de Josée et de Bouchard |
| `?` | la voix monte | pour une vraie question |

⚠️ **Une pause pèse lourd en v3.** Mesuré le 16 sept. 2026 : `…` suivi de
`[sighs]` au milieu d'une phrase a fait un trou de **deux secondes** (4,9 s → 10,2 s
pour la phrase). Sur la première génération complète, neuf trous de plus d'une
seconde : sept sur des répliques qui **changeaient de balise en chemin**, un
sur « Lui… » (un mot seul puis `…`). D'où :

- **une balise par réplique**, **en tête**, dès qu'elle respire ; deux balises
  seulement si la phrase **change vraiment de propos** et **au passage d'une phrase
  à l'autre** (« Heille, beau bonhomme! `[whispers]` Viens icitte. ») ;
- **jamais `…` après un mot seul** ;
- **pas de SSML** (`<break time>` est du v2 ; v3 le lit ou l'ignore — un juge l'interdit).

**Majuscules pour l'emphase.** La doc d'ElevenLabs recommande de mettre **un mot** en
majuscules pour l'appuyer (« It was a VERY long day »). Le juge des mots compare
sans la casse, donc c'est permis — mais **on ne l'a pas encore essayé ici** :
essaie sur une seule réplique, écoute, et garde-le seulement s'il sonne juste.

### 3.6 Le volume ne joue pas : tout est ramené à −19 LUFS

⚠️ **Piège de jeu d'acteur.** La finition (`finir_voix`) ramène **chaque voix au
même niveau** (−19 LUFS) : un murmure n'est donc pas plus faible qu'un cri dans le
jeu. **Le contraste doit venir de la livraison** (`[whispers]` change le *timbre*,
`[shouting]` la *tension*), jamais du volume. Un `[quietly]` qui compte sur un
volume bas pour se faire sentir sonnera comme les autres — et un limiteur
(−3 dBFS) rabat les consonnes qui claquent sur les répliques dites bas.

### 3.7 Le téléphone : écrire pour un combiné

La voix « au combiné » est un **filtre joué**, pas un fichier différent : les
mêmes mots, le même mp3. Écris donc l'appel **pour la situation** : plus court,
plus pressé, sans cérémonie (« Il se sauve avec ma caisse! Lâche-le pas! »), et
n'y mets pas un geste ni un plan — le téléphone fige déjà la ville.

### 3.8 Distribuer avant d'écrire

**Une voix par personnage**, et elle se choisit **avant** le jeu, parmi celles du
compte de Martin (le serveur MCP `elevenlabs` les liste ; on n'invente pas un
nom). Ce qu'il faut savoir :

- **Le grain vient de la voix, pas de la balise.** Julia (Mme Thibodeau) est rauque, aux
  fins de mots soufflées : mesuré, ça ne part ni en régénérant ni à l'isolateur — c'est
  sa voix. Un rôle se **choisit** donc pour le grain qu'il demande, avant d'écrire son jeu.
- **L'accent est dans l'échantillon de la voix.** Une québécoise d'origine garde son
  accent en v3 (les huit du jeu le prouvent) ; une **multilingue**, on ne sait pas :
  aucune voix du compte n'est vérifiée en v3, et son français « vérifié » est souvent
  un aperçu fabriqué. **Lis `verified_languages`** (API `v2/voices`), pas l'étiquette
  `language`, et **fais écouter** avant de distribuer (`docs/plan.md`, M16, « Les 34
  personnages de plus »). v3 ne tolère d'ailleurs qu'**une** balise d'accent par
  réplique, en tête — elle prendrait la place de l'émotion.
- **Chaque voix passe par une égalisation** (`interpretation.EGALISATION` : un passe-haut
  à 85 Hz par défaut, 120 Hz pour les voix de femmes qu'on y a inscrites, et une coupe
  ou une rehausse **de la taille de l'écart mesuré** pour celles qui en ont besoin) — une
  nouvelle voix se **mesure** contre les autres avant d'être ajoutée : trop caverneuse,
  trop étouffée, trop réverbérée, et elle sonne dans une autre pièce.
- **La stabilité reste à 0,5** (`interpretation.STABILITE`) : « Créatif » joue plus
  fort mais **invente** (des mots, des rires) ; « Robuste » ignore les balises.

### 3.9 Le jeu est collé à la réplique, dans le fichier de la mission

⚠️ **Depuis le 21 sept. 2026, le jeu vit dans la mission** (demande de Martin : « si on veut
que les missions soient lues indépendantes, les interprétations devraient aussi être dans le
fichier de mission »). Chaque usine de réplique (`_l`, `_p`, `_r`, `_a`) prend un `jeu=` :

```python
# app/missions/m2.py
_a("thibodeau", "Mon argent! T'es un bon garçon, toi.", 1,
   jeu="[relieved] Mon argent! [warmly] T'es un bon garçon, toi.")
```

**Chaque réplique doit avoir son `jeu=`** — sinon `test_chaque_voix_a_son_jeu…` rougit, et la voix
sortirait plate à la prochaine génération. Le slug de la voix, lui, reste `<qui>-<mission>-<n>`
(`ti_guy-m1-3`), compté dans l'ordre `appel, intro, client, fin, echec, pendant, renvoi, accueil` :
c'est le **nom du mp3**, et il suit la place de la réplique. L'ancien piège — une réplique insérée
au milieu décalait tous les slugs, et chaque jeu se mettait à dire la phrase de sa voisine — n'existe
plus, puisque le jeu voyage avec sa réplique ; mais un mp3 déjà payé garde son nom, alors on **ajoute
à la fin** (`docs/comment-monter-les-missions.md` § 5) et on n'insère que si on régénère.

**Écris l'intention une fois, en commentaire, au-dessus de `"dialogue"`** : l'arc du personnage
(« Thibodeau : inquiète, puis en colère, puis tendre »). Les balises la notent réplique par
réplique ; le commentaire dit pourquoi, et il se lit avec le reste de la mission.

`app/interpretation.py` garde le jeu de ce qui n'est **pas** une mission — les passants, les
repos, le journal, l'ouverture — et **rassemble** celui des missions dans `JEU` : les juges et
`scripts/audio_elevenlabs.py` lisent une seule table. Le navigateur, lui, ne reçoit jamais le jeu
(`missions.pour_le_navigateur()`).

**Le texte joué dit les mêmes mots** que la boîte (jugé) : tu ajoutes des balises,
des `…` et de la ponctuation, **jamais un mot**. Une voix qui dit autre chose que
ce qu'on lit est pire qu'une voix plate.

### 3.10 Écouter, essayer une ligne, puis tout générer

⚠️ **On ne juge pas une voix à l'œil, et l'IA non plus.** Le processus :

1. écrire le jeu (§ 3.2 à 3.5) ;
2. `--essai` dit ce qui serait généré **sans rien dépenser** ; puis **générer une ou deux
   répliques clés** — celles qui portent un ton nouveau —
   avec `scripts/audio_elevenlabs.py --refaire <slug>` (**payant**, au caractère) ;
3. **Martin écoute** et dit lesquelles refaire ;
4. seulement alors, générer le reste : `--voix` fait ce qui manque.

Une balise qu'on n'a jamais entendue ne s'ajoute pas à `BALISES` en passant : on
l'essaie sur **une** réplique, on écoute, puis on l'ajoute. Et pour une voix
qui sonne bien mais dont la **finition** cloche (niveau, temps mort, égalisation),
`--refinir --masters` est **gratuit** : ne regénère pas ce qu'on peut retoucher.

---

## 4. Les deux ensemble — quand l'image et la voix se répondent

### 4.1 Chaque réplique a son moment

Dans une scène, ne lance pas toutes les répliques d'un coup et n'habille pas par-dessus :
**donne à chaque réplique un événement**. m2, intro :

```python
{"type": "dire", "repliques": [1]},                       # elle se plaint
{"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "cible",
 "duree": 60, "ensemble": True},                          # elle montre le coin…
{"type": "camera", "vers": "cible", "duree": 45, "courbe": "freine",
 "ensemble": True},                                       # …la caméra y va, vide…
{"type": "dire", "repliques": [2, 3]},                    # …pendant qu'elle en parle
{"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},   # on revient
```

La première réplique **plante** le personnage, le geste **ouvre** l'enjeu, la
caméra **le montre pendant que la voix l'explique**, et le retour **referme**. Quatre
temps, un rythme.

### 4.2 Le son avant l'image

Un bruitage (`son`) qui précède de quelques images ce que la caméra va montrer fait
sentir qu'on *entend* avant de voir : un moteur qui démarre, une porte. Écris `son`,
un `attendre` de 10–15 images, puis le plan (rappel : sans `attendre`, le plan suivant
part **sur la même image**, § 2.3). ⚠️ Comme l'anticipation du geste, le catalogue ne le
fait pas encore : essaie, regarde. **Pas de musique par mission** (plan : coût zéro) : la
scène **baisse** ce qui joue, et la parole passe devant.

### 4.3 Le silence après la réplique qui compte

Chaque scène a **une** réplique qui doit atterrir. Mets un `attendre` (30–55 images)
ou une caméra qui **tient** juste après elle — avant le plan suivant. Deux
répliques fortes à la suite s'annulent.

### 4.4 La scène par défaut est un minimum

`scene_par_defaut` bâtit une scène propre — il dit un mot, montre, la caméra va voir,
il finit, la caméra revient. **Elle est correcte, jamais mémorable.** Écris la tienne
quand la mission a *un moment*. Trois occasions qui le méritent :

- **un revirement** (m97 : Marco hausse les épaules en livrant le guet-apens, puis croise
  les bras en disant qu'il disparaît) ;
- **un lien** (m1 : Ti-Guy sort du garage pour te donner la clé) ;
- **un passage de témoin** (m3 : Marco montre le casse-croûte, `coupe` sur Bouchard).

Une mission moyenne se contente du défaut ; une mission qui **marque** écrit la sienne.

---

## 5. Une réplique, démontée

> **Mme Thibodeau, m2, fin** — le joueur a rattrapé le fuyard et rapporte la caisse.
>
> Texte affiché : « Mon argent! T'es un bon garçon, toi. »
> Jeu : `[relieved] Mon argent! [warmly] T'es un bon garçon, toi.`

- **Le sous-texte.** Elle ne dit pas « merci » : elle **reconnaît**. « Un bon garçon »
  est le mot de la tendresse d'une femme qui vient d'avoir peur.
- **L'arc.** Elle était `worried` puis `angry` ; elle est `relieved`, puis `warmly` :
  le soulagement d'abord (le corps se relâche), la chaleur ensuite (la personne revient).
  **Deux tons, un seul point de bascule** : le passage d'une phrase à l'autre.
- **La pause.** Aucune dans le jeu : le soulagement ne réfléchit pas. La seule respiration
  vient de la scène.
- **Le geste.** Le plan de fin (celui du défaut) la fait `prendre` la caisse **sur** cette
  réplique, puis `donner` le bâton sur la suivante (« Tiens, le bâton de mon défunt. »
  `[tenderly]`). Le geste raconte l'échange que le texte ne dit pas.
- **La voix.** Julia, rauque, aux fins de mots soufflées : c'est ce grain qui fait la
  tendresse fatiguée — un choix de rôle, pas un réglage (§ 3.8).

---

## 6. La liste de contrôle du jeu d'acteur

Avant de dire « c'est fini », **joue la mission de l'intro à la fin** et vérifie :

**La scène**
- [ ] Chaque scène a une phrase d'intention (§ 2.1) — et je peux la dire.
- [ ] L'image dit le *où*, la voix dit le *pourquoi* (§ 2.2) : aucune réplique ne décrit ce que la caméra montre.
- [ ] Les gestes sont choisis pour ce qu'ils disent (§ 2.4), et le donneur garde sa gestuelle.
- [ ] Il y a **au moins un silence** qui joue (§ 2.6), posé **dans la scène**, pas dans l'audio.
- [ ] Personne ne parle de nulle part, et la fin passe la main si elle nomme le suivant.
- [ ] Je peux **passer** la scène (ACTION, PAUSE) sans que rien ne casse.

**La voix**
- [ ] Chaque réplique a un **verbe d'action** (§ 3.2) ; le ton n'est pas celui de la réplique d'à côté.
- [ ] La fin **sonne autrement** que l'intro (§ 3.3) — le personnage a un trajet.
- [ ] **Un ton** au moins par réplique, **une balise en tête**, jamais `…` après un mot seul (§ 3.5).
- [ ] Le **jeu** de chaque réplique est son `jeu=`, dans le fichier de la mission, et dit **les mêmes mots** (§ 3.9).
- [ ] Le rôle est **dans l'étendue de la voix** choisie (§ 3.8) ; le volume ne porte pas l'émotion (§ 3.6).
- [ ] J'ai fait **écouter** au moins la réplique la plus difficile avant de tout générer (§ 3.10).

```bash
uv run python scripts/verifier_missions.py --detail
uv run python -m pytest tests/test_mise_en_scene.py -q
uv run python -m pytest tests/test_interpretation.py -q -k "jeu or balises"
```

Les tests disent que **c'est câblé**. Seule l'écoute dit que **c'est juste**.

---

## Sources

- **Ce dépôt** — `app/interpretation.py` (les balises, les mesures du 16 sept. 2026, la
  finition), `app/missions/__init__.py` (`TYPES_PLANS`, `TEMPS_PAR_DEFAUT`,
  `scene_par_defaut`), les missions écrites à la main (`m1.py`, `m2.py`, `m3.py`,
  `m97.py`), et `docs/voix-de-l-histoire.md`, `docs/missions-en-scene.md`.
- **ElevenLabs, guide de prompt d'Eleven v3** — les balises (`[whispers]`, `[sighs]`,
  `[excited]`, `[sarcastic]`, `[curious]`, `[laughs]`…), la ponctuation et les
  majuscules pour le rythme et l'emphase, les trois stabilités (Créatif, Naturel,
  Robuste), et le principe que la voix choisie borne ce que les balises peuvent faire :
  <https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices>.
