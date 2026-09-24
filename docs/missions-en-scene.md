# Bandini — les missions mises en scène, et le jeu d'acteur

← [le plan](plan.md), qui ne garde que ce qui reste à faire

Deux décisions qui vont ensemble : une mission a ses scènes et ses voix (16 sept. 2026), et elles doivent être bien jouées (20 sept. 2026). Le savoir-faire complet du second est dans [jeu-d-acteur.md](jeu-d-acteur.md) ; la recette pour monter une mission, dans [comment-monter-les-missions.md](comment-monter-les-missions.md).

## Les missions mises en scène (décision du 16 sept. 2026)

_Demande de Martin (16 sept. 2026) :_ « je veux que chaque mission vienne avec des
animations et des dialogues. »

**La règle.** Une mission, c'est **trois choses** : ses objectifs, ses **dialogues** et ses
**scènes**. Les trois vivent dans `missions.py`, les trois sont jugées, et une mission à qui
il en manque une **n'est pas finie** — ni les cinq de la v1, ni les cent de M16, ni celle
qu'on ajoutera dans un an. Le juge du catalogue la refuse, comme il refuse déjà un objectif
sans type. La règle des voix (ci-dessus) tient sans changer : le texte est la source, une
voix par personnage, une réplique sans mp3 s'affiche sans voix.

⚠️ **Mesuré le 16 sept. 2026, et c'est ce qui dit ce qui manque.**

- **Les dialogues sont là, sauf au milieu.** Les cinq missions ont six ou sept répliques,
  toutes dites à voix haute : l'appel (sauf m1, où Ti-Guy t'attend au terminus), l'intro, la
  fin, l'échec — et le client de m3, **la seule réplique du jeu dite pendant une mission**.
  Entre l'intro et la fin, le donneur se tait : le fuyard part en moto, le chef des Cravates
  sort, Ti-Guy démarre derrière l'auto-patrouille, et personne ne dit rien.
- **Les animations, elles, n'existent pas.** Pendant un dialogue, `B.cinema` fige la ville
  et pose une boîte de texte : le donneur reste planté, la caméra ne bouge pas. **La seule
  scène animée du jeu est l'ouverture**, et elle est écrite **en dur** dans `histoire.js` —
  ses temps en images (`OUV`), son autobus, son trajet : 265 lignes pour une scène d'une
  dizaine de secondes. Cent trente-quatre scènes écrites comme ça, c'est un moteur que personne ne
  relit plus.
- **La fin est dite par des absents.** Trois fins sur cinq se déclenchent loin du donneur :
  m1 finit au garage (Ti-Guy est au terminus), m4 au garage (Bouchard mange au
  casse-croûte), m5 à la planque (Josée est au Brouillard). Leur voix sort de nulle part, et
  sans le « (AU TÉLÉPHONE) » que porte l'appel.
- **Et la seule animation de fin de mission est un `if (m.slug === 'm1')`** dans
  `reussir()` : Ti-Guy rentre dans le terminus. C'est exactement ce que M16 interdit.

**Ce que chaque mission porte, au minimum :**

| Temps | Dialogue | Scène |
|---|---|---|
| **Appel** | une réplique, au combiné — sauf un donneur qu'on rencontre en personne | aucune : le téléphone fige déjà la ville (« Le char abrite, l'appel fige »), une scène de plus en ferait une pause |
| **Intro** | deux à quatre répliques du donneur | **elle montre** : le donneur fait un geste, la caméra va voir où l'on s'en va — le char, le coin de rue, le poste — et revient |
| **Pendant** | **au moins une**, accrochée à un objectif, dite quand il commence — au combiné si le donneur n'est pas là (la règle de `B.cinema` tient : elle fige à pied, jamais au volant) | facultative : un temps fort, si l'objectif en a un (le fuyard enfourche sa moto) |
| **Fin** | une à trois répliques, **dites par quelqu'un qui est là** | **on voit ce qu'on gagne** — la clé tendue, l'enseigne, la poignée de main — et la fin **passe la main** : si elle nomme le prochain donneur, la caméra va le voir |
| **Échec** | une réplique, **au combiné** : on n'est jamais à côté du donneur quand on rate | aucune de plus : le fondu de l'hôpital ou de la prison **est** la scène |

⚠️ **Un vocabulaire, pas cent trente-quatre scripts.** La règle de M16 s'étend aux scènes :
une scène est une **liste de plans** dans `missions.py`, typés comme les objectifs, et
`histoire.js` ne connaît aucune scène par son nom. Une dizaine de types (`TYPES_PLANS`) — et
si une scène ne s'écrit pas avec eux, on ajoute **un type**, jamais un
`if (slug === 'q07')` :

- `camera` — aller voir un lieu (tout ce que `resoudre()` connaît), le tenir, revenir ;
- `marcher` — un acteur va à un lieu, à pied, les jambes animées (`marcherVersLeQuai`,
  généralisé) ; ⚠️ vers le joueur, `pres` est obligatoire (22 px, la distance de parole) : sans
  lui l'acteur finit au pixel du joueur, dessus (Marco, m50) — le validateur le refuse ;
- `conduire` — un char de la scène entre par la rue, s'arrête, repart hors champ (l'autobus
  de l'ouverture, généralisé) ;
- `geste` — un acteur fait un geste : `montrer`, `donner`, `prendre`, `bras_croises`,
  `hausser`, `telephone` ;
- `entrer` et `sortir` — un acteur passe une porte (le Ti-Guy de m1, sans son `if`) ;
- `coupe` — un fondu vers un autre lieu, puis retour : c'est ce qui fait parler un donneur
  **chez lui** quand la fin se joue ailleurs, et ce qui montre dehors une scène qui commence
  dedans. `vers` peut être une **liste** de lieux, visités d'un seul aller-retour (le tour de
  m6 : quatre portes). ⚠️ Son propre noir, comme l'ouverture : `Jeu.transiter()` fige la boucle,
  et la scène doit continuer pendant le fondu ;
- `dire` — la réplique n de la partie : la scène se joue **sous** ses répliques ;
- `titre` — le carton : le titre de la mission à l'intro, la prime à la fin ;
- `son` — un bruitage du catalogue ;
- `attendre` — n images.

⚠️ **Les gestes se dessinent une fois pour tout le monde.** Les personnages sont tous le
sprite `joueur` repeint (`couleurs` : chandail, cheveux, peau, pantalon) : six gestes dessinés
sur lui, dans ses trois faces, servent à tous ceux qui le portent — ceux d'aujourd'hui
et ceux de M16. **Aucun sprite par mission** — ce
qu'une scène fait passer de main en main (la clé, la caisse) est un décor du catalogue.

**Les règles du moteur** — celles que l'ouverture a déjà payées, et qui deviennent
générales :

- ⚠️ **Aucun dé tiré.** Une partie jouée en regardant les scènes est exactement celle qu'on
  joue en les passant : même tuile, même monde, même prochain dé. C'est le juge central de
  l'ouverture, étendu au catalogue.
- ⚠️ **La mission se pose AVANT sa scène d'intro.** Aujourd'hui `commencer()` n'est appelé
  qu'à la fin du dialogue : quand Madame Thibodeau parle de ses deux Cravates, ils n'existent
  pas encore, et la caméra filmerait un coin vide. Ce n'est pas un dé de déplacé — la ville
  est figée pendant la scène et la scène n'en tire aucun, donc les tirages de `poser()`
  tombent dans le même ordre. ⚠️ Dedans (Josée au bar), rien ne se pose avant la sortie
  (`aPoser`) : la scène montre alors un **lieu** par `coupe`, jamais un acteur qui n'existe
  pas.
- ⚠️ **On la passe** : ACTION saute une réplique, PAUSE saute la scène, et l'on tombe
  exactement où elle nous aurait laissés. Une mission ratée se retente : une scène qu'on ne
  peut pas passer devient une punition à la deuxième tentative.
- ⚠️ **Elle se termine toujours.** Un plan dont le lieu ne se résout pas est **sauté**, jamais
  attendu ; une voix qui ne dit jamais qu'elle s'est tue garde son plafond (`majCinema`).
- ⚠️ **Elle ne déplace pas le joueur.** La caméra voyage, le bonhomme reste — ou revient à la
  dernière image (`retour`, la règle de l'ouverture revue du carnet).
- ⚠️ **Jamais en pleine action.** La scène de fin ne part ni à 3★ et plus, ni dans un char
  qui roule. **L'argent et `donne` sont accordés tout de suite** ; la scène attend qu'on soit
  à l'arrêt et hors poursuite. Rien de ce qu'on gagne ne dépend de l'avoir regardé.
- ⚠️ **Courte.** Elle se termine quand ses plans **et** ses répliques sont finis, jamais au
  premier des deux (la règle de l'ouverture) — et une scène ne tient pas plus de trois
  secondes après son dernier mot.
- ⚠️ **L'ordre des slugs de voix ne bouge pas.** `pendant` se compte **après** `echec` dans
  `repliques()` et `slugDeVoix()` : insérée avant `fin`, elle renommerait les quinze voix de
  fin et d'échec déjà générées, et quinze mp3 payés deviendraient des 404. Et une fin qui
  passe au combiné ne se **régénère** pas : le combiné est un filtre joué, pas un fichier.
  `renvoi` se compte **après** `pendant`, pour la même raison, et `accueil` après `renvoi`.
- **Le renvoi** (20 sept. 2026, m50) : ce que dit `qui` quand on **lui** parle alors que ce
  n'est pas encore son tour — `_r("lulu", "…", 0)`, accroché à l'objectif en cours. À la
  cantine, de jour, l'objectif 0 de m50 attend la noirceur et « parler à Lulu » ne compte
  qu'au suivant : elle disait le texte de repos de tout le monde (« le Faubourg est
  tranquille »), sans voix. Elle dit maintenant d'attendre la nuit. Il se dit **en
  personne** (jamais au combiné : on est devant lui), par `parler()`, avant le message du
  donneur ; une mission qui n'en écrit pas garde le comportement d'avant.

**Les cinq missions de la v1, mises en scène** — le banc d'essai du vocabulaire :

| # | Intro | Pendant | Fin |
|---|---|---|---|
| m1 | Ti-Guy `montrer` vers le garage ; `camera` sur le garage et sa ruelle — un lieu, pas le char : il appartient au deuxième objectif, qui ne se pose pas encore | quand on monte dans le char, au combiné | Ti-Guy `sortir` du garage, fait le tour du char, `donner` la clé ; il `entrer` au garage — et le `if` de `reussir()` disparaît |
| m2 | Madame Thibodeau `montrer` le coin ; `camera` sur les deux Cravates | le fuyard enfourche sa moto (`conduire`) | elle `prendre` la caisse, `donner` le bâton de son défunt |
| m3 | Marco `donner` les clés ; `camera` sur le taxi | le client (existe) | Marco fait le tour du taxi, `montrer` vers le casse-croûte ; `coupe` sur Bouchard à son dîner — la fin passe la main |
| m4 | Bouchard, dedans : `coupe` sur le poste (un lieu : l'auto-patrouille est le deuxième objectif) | quand Ti-Guy démarre derrière toi, au combiné | `coupe` au casse-croûte : Bouchard au `telephone`, ses deux répliques au combiné |
| m5 | Josée, dedans : `coupe` sur les trois coins des Cravates, un par un | quand le chef sort, au combiné | `coupe` au Brouillard : Josée devant sa porte, l'enseigne est à toi |
| m50 | `camera` sur la porte du garage ; Marco marche vers toi et te `montrer` la direction | quand le fuyard file avec le colis, au combiné | Marco revient vers toi et `prendre` le colis |

**Ce que ça coûte :**

- **Voix** : une réplique `pendant` par mission, ≈ 75 caractères — **400 pour la v1**, et
  ≈ **10 000** sur les cent trente-quatre de M16.
- **Musique** : **zéro**. Aucun morceau par mission : la scène baisse ce qui joue (le
  _ducking_ des voix existe).
- **Dessin** : six gestes, une fois.
- **Paquet** : une dizaine de plans pèsent un demi-kilo-octet par scène. Pour cinq missions,
  rien ; pour cent trente-quatre, ≈ 130 Ko bruts — les scènes **voyagent avec leurs
  répliques**, par `/api/mission/<slug>` (M16, livré le 24 sept. 2026).

**Juges** — on juge le câblage, pas la fiche :

- _Python_ (`test_mise_en_scene.py`) : chaque mission du catalogue a une scène `intro` et
  une scène `fin` non vides, des répliques `intro`, `fin` et `echec`, et au moins une
  réplique `pendant` accrochée à un objectif qui existe (comme chaque `renvoi`) ; chaque plan est d'un type connu,
  chaque lieu se résout, chaque acteur est le joueur, le donneur, un personnage connu ou un
  homme que la mission pose ; **une fin qui se déclenche loin du donneur** commence par une
  `coupe` chez lui ou le fait `marcher` jusqu'à toi — sinon ses répliques sont au combiné ;
  l'échec est au combiné.
- _Python_ : `histoire.js` ne contient **aucun slug de mission** — le juge qui aurait
  attrapé le `if` de Ti-Guy. ⚠️ Le remettre pour le voir rougir avant de le croire.
- _Banc_ : **chaque scène du catalogue** se termine, jouée sans jamais toucher ACTION et
  avec toutes ses voix absentes ; PAUSE à n'importe quel plan tombe sur le même état que la
  scène jouée jusqu'au bout ; le prochain dé (`B.rng()`) est le même avec et sans les
  scènes ; aucune scène ne part à 3★ ou au volant d'un char qui roule.
- _Banc_ : **l'ouverture, réécrite dans le vocabulaire, passe ses 13 juges sans qu'on en
  touche un.** C'est la preuve que les plans suffisent : s'ils n'écrivent pas l'ouverture, ils
  n'écriront pas cent trente-quatre missions. Le générique (2e vague de « La ligne
  d'histoire ») s'écrit dans le même vocabulaire.
- _Navigateur_ : m1 jouée de l'intro à la fin, aucune erreur console.
- _Martin_ : jouer m1 à m5 sans jamais entendre quelqu'un qui n'est pas là, et savoir où
  aller **avant** que l'objectif s'affiche, parce que la scène l'a montré.

**Comment on le livre** (taille 3, deux vagues, chacune jouable et déployée) :

1. **Le metteur en scène** (taille 2) : `TYPES_PLANS` et leur lecteur, les six gestes, la
   mission posée avant son intro, et **l'ouverture réécrite dedans** — rien ne change à
   l'écran, et c'est le but : ses 13 juges le prouvent.
2. **La v1 mise en scène** (taille 1) : les cinq scènes d'intro, les cinq de fin, les cinq
   répliques `pendant` et leurs voix, les fins d'absents au combiné ou en `coupe`, le `if` de
   m1 retiré. ⚠️ **Avant la première tranche de M16** : c'est ce vocabulaire que ses cent
   missions écriront.

## Le jeu d'acteur (décision du 20 sept. 2026)

_Demande de Martin (20 sept. 2026) :_ « pour les futures missions, je veux que tu documentes dans
les plans les bonnes pratiques pour faire de bonnes animations cinématiques et intéressantes, et de
bonnes voix avec de l'émotion — je veux un bon jeu d'acteur. »

**Le constat.** « Les missions mises en scène » a fait qu'une mission **a** des scènes et des voix, et
les juges le vérifient. Il n'a jamais dit qu'elles soient **bonnes** : une mission peut passer chaque
test et jouer comme une boîte de dialogue. Le sprite n'a pas de visage — c'est **la voix, la caméra,
le geste et le temps** qui jouent. Le guide complet est **`docs/jeu-d-acteur.md`** (à lire avant
d'écrire une scène ou un jeu de voix) ; ce qui suit en est l'essentiel.

**La scène.**

- **Une phrase d'intention** avant le premier plan : « après cette scène, le joueur sait / ressent… ».
  Sans elle, la scène est une pause.
- **L'image dit le _où_, la voix dit le _pourquoi_.** On ne décrit pas ce que la caméra montre, et on
  ne montre pas un lieu que la réplique n'a pas nommé.
- **Le geste tombe sur le mot qui le porte.** ⚠️ `ensemble` lance le plan suivant **sur la même
  image** (`demarrerLesSuivants`) : pour qu'un geste **précède** la parole, il faut un `attendre` entre
  les deux — le lecteur le permet, aucune mission ne le fait encore.
- **Le silence joue, et il vit dans la scène.** ⚠️ La finition des voix rogne tout silence de plus de
  0,7 s : un grand silence se joue par un `attendre` (≈ 30–55 images) **après** le `dire`, jamais dans
  le mp3.
- **Choisir le geste pour ce qu'il dit** (`montrer` enjeu, `donner` confiance, `prendre` demande,
  `bras_croises` méfiance, `hausser` désinvolture), et garder la gestuelle d'un personnage d'une
  mission à l'autre.
- **Ce que le moteur ne sait pas** — gros plan, zoom, tremblement, regard qui se tourne — s'ajoute en
  **type de plan** avec son juge de banc, jamais en `if (slug === …)`.
- **Le défaut est un minimum** : une mission qui a _un moment_ (un revirement, un lien, un passage de
  témoin) écrit sa scène.

**La voix.**

- **Écrire pour la bouche** (8–110 caractères, une ou deux phrases, québécois parlé) puis **jouer une
  intention** : un verbe d'action par réplique (convaincre, prévenir, cacher, tester…), et le
  sous-texte là où le jeu devient intéressant.
- **Un arc, pas un ton** : la fin sonne autrement que l'intro, l'échec autrement que la fin ; le
  personnage garde un registre de base et varie autour.
- **Les balises v3** : liste fermée (`interpretation.BALISES`), en anglais, **un ton au moins par
  réplique** (jugé), une balise en tête, `…` à **un seul endroit** par phrase et jamais après un mot
  seul (les trous de 1,2–2 s mesurés le 16 sept.).
- ⚠️ **Le volume ne joue pas** : tout est normalisé à −19 LUFS, un murmure n'est pas plus faible
  qu'un cri — le contraste doit venir de la livraison.
- **La voix se choisit avant le jeu**, pour son grain et son étendue : les balises ne transforment pas
  une voix (guide ElevenLabs), et Julia reste rauque quoi qu'on régénère.
- ⚠️ **Chaque réplique de mission porte son `jeu=`, dans le fichier de la mission** (depuis le
  21 sept. 2026 ; avant, il vivait dans `interpretation.JEU`) — sinon `test_chaque_voix_a_son_jeu…`
  rougit. Il est collé à la réplique : en insérer une n'emporte plus le jeu de sa voisine. Le slug du
  **mp3**, lui, suit toujours la place de la réplique : on ajoute à la fin, on n'insère que si on
  régénère.
- **On essaie une réplique avant de tout générer** (`--refaire <slug>`, payant), Martin écoute, puis
  `--voix` fait le reste ; une finition qui cloche se retouche gratuitement (`--refinir --masters`).
- ⚠️ **On se présente une fois par mission** (21 sept. 2026, demande de Martin : « normalement les gens se
  présentent avant de parler », puis « seulement une fois par mission ») : la première fois qu'on entend
  quelqu'un dans la mission — l'appel, le plus souvent — il dit son nom, dans **sa salutation** : Josée ne
  dit jamais bonjour, Lulu dit « mon grand », Bouchard sort son grade au premier appel. Ensuite, personne ne
  redit son nom dans la mission. Jugé (`erreurs_de_mise_en_scene`, `erreurs_de_presentation`) ; les formes
  sont au § 3.11 du guide, et la salutation de chacun dans sa fiche,
  [`docs/personnages/`](personnages/README.md).

**Ce qui est jugé, et ce qui ne l'est pas.** Les juges existants tiennent le câblage (la scène se
termine, les mêmes mots, les balises connues, un ton par réplique, la ligne qui attend sa voix). **Rien
ne juge qu'une scène est belle ni qu'une voix est juste** — et on n'en écrit pas : un juge de « bon jeu »
serait un juge à vide. La liste de contrôle du § 6 du guide se joue **à l'œil et à l'oreille**, mission
jouée de l'intro à la fin.
