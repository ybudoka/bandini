# Monter une mission — mode d'emploi pour une IA

Ce document explique **comment ajouter une mission de bout en bout** dans
Bandini, à l'intention d'une IA (ou d'un humain) qui découvre le projet. Il ne
remplace ni `docs/vision.md` (la vision) ni `docs/carte.md` (l'inventaire de la
ville) : il raconte la **recette**, pas le pourquoi. Pour que la mission soit
**bien jouée** — scènes qui racontent, voix qui ont de l'émotion — lis aussi
`docs/jeu-d-acteur.md` : les juges vérifient que c'est câblé, pas que c'est juste.

> ⚠️ **Une mission = un fichier, et il dit tout.** Les missions vivent dans `app/missions/`,
> **une par fichier** (`m1.py`, `m2.py`, … `m97.py`, `e01.py`, `f01.py`…) : chacun déclare
> `MISSION = {…}` et n'a besoin que de `_l`/`_p`/`_r`/`_a` (importés de `_commun.py`).
> **Le jeu des voix y est aussi** : chaque réplique porte son `jeu=` (ce qu'ElevenLabs
> *dit*, § 5) — on n'ouvre plus `app/interpretation.py` pour écrire une mission. Le moteur — les
> types d'objectifs, les personnages, les défis, les scènes d'ouverture, les
> juges — vit dans `app/missions/__init__.py`. **Ajouter une mission = créer son
> fichier et l'ajouter aux deux listes de `__init__.py`, rien d'autre.**
>
> **Une mission courte se fait en chapitre** (§ 7 bis) : 5 à 10 minutes, coupée en actes qu'on reprend.
>
> On ne touche jamais à `static/js/histoire.js` ou `scenes.js` pour *ajouter*
> une mission — on ne les touche que pour ajouter un **type** de plan (voir § 6),
> et alors on le fait pour tout le monde.

---

## 1. Ce qu'est une mission : trois choses obligatoires

Une mission est un dicton dans `CATALOGUE`, et elle **n'est pas finie** tant
qu'elle ne porte pas **les trois** :

1. Ses **objectifs** — ce que le joueur fait, dans l'ordre ;
2. Ses **dialogues** — les répliques, à chaque temps (appel, intro, pendant,
   fin, échec) ;
3. Ses **scènes** — les plans (caméra, gestes, entrées/sorties…) qui mettent en
   scène l'intro et la fin.

Les trois sont **jugées**. Une mission à qui il en manque une fait rougir un
test (`erreurs_de_mise_en_scene`), pas seulement un œil humain.

> ⚠️ **Mais tu n'as à écrire que les deux premières** (20 sept. 2026, demande de
> Martin : « je veux que ça soit facile d'ajouter des missions, comme des blocs
> Lego »). Les **scènes ont un défaut** : `missions.scene_par_defaut` les bâtit de
> ce que ton fichier dit déjà — qui la donne, où il se tient, ce qu'elle demande
> d'abord, où elle se termine. Tu en écris une ? La tienne gagne. Aucune ? Les
> animations jouent quand même, et le juge est content. Voir § 6.

---

## 2. La structure d'une mission

```python
{
    "slug": "m7",                       # nom stable, cité partout ; m1…m97 existent déjà
    "titre": "Un titre court",          # ce qui s'affiche
    "donneur": "marco",                 # un slug de PERSONNAGES (§ 3)
    "prerequis": ["m5"],                # FACULTATIF (défaut []) : les missions DÉJÀ terminées
    "recompense": 400,                  # en dollars, > 0 (jugé)
    "phase": 1,                         # FACULTATIF (défaut 1) : le palier de contenu
    "echec": ["mort", "arrete"],        # FACULTATIF (défaut ["mort", "arrete"])
    "exige": {"liberes": 3},            # FACULTATIF : condition d'« état » (pas encore lue au nav.)
    "donne": {"arme": "batte", "message": "LE BÂTON"},   # FACULTATIF (défaut {})
    "sur_place": {"lieu": "hotel", "heure": "nuit"},     # FACULTATIF : le saut après l'intro (voir dessous)
    "frontiere": "quais",               # FACULTATIF : un district, ou "bloc:<slug>" (voir dessous)
    "objectifs": [ … ],                 # § 4
    "scenes": {"intro": [ … ], "fin": [ … ]},   # FACULTATIF : § 6, le défaut les bâtit
    "dialogue": {                       # § 5
        "appel":      [ … ],
        "intro":      [ … ],
        "pendant":    [ … ],
        "renvoi":     [ … ],           # FACULTATIF : § 5
        "accueil":    [ … ],           # FACULTATIF : § 5
        "client":     [ … ],
        "fin":        [ … ],
        "echec":      [ … ],
    },
}
```

**Sur place, avec une frontière** (29 sept. 2026, `static/js/surplace.js`) — deux clés
**indépendantes**, pour une mission où le trajet et l'attente n'apportent rien :

- `sur_place = {"lieu": …, "heure": "nuit" | (h0, h1)}` — à la fin de l'intro, fondu au noir,
  l'horloge **avance** jusqu'à l'heure (`"nuit"` : 20 h 45, le réveil de la sieste ; une fenêtre
  `(h0, h1)` dans `[0, 1)`, 0 = minuit, qui peut passer minuit comme `(0.9, 0.1)`), jamais en arrière ;
  passer minuit est un **vrai jour** (`nouveauJour` : dette, revenus). On se relève à pied au `lieu`
  (un lieu de bloc fait entrer dans le bloc), sans étoile. Un `aller … nuit` sur ce lieu se fait en
  arrivant. ⚠️ Pas de `char` : monter dans un char de mission garé compte comme un **vol**
  (`Vehicules.monter`) — à trancher avec la première mission qui en aura besoin.
- `frontiere = "<district>" | "bloc:<slug>"` — armée dès l'arrivée (dès la fin de l'intro sans
  `sur_place`), gardée par la sauvegarde. Dehors, « RETOURNE DANS LES QUAIS », la ligne d'objectif dit
  « — REVIENS ! 7 S », et après **10 s** la mission rate (`hors_zone`). Le compte dort sous une scène, un
  dialogue, un menu, la pause. Dans une pièce, c'est **la porte** qui compte ; dans un bloc, **son
  passage** en ville. Les districts : ceux de `carte.DISTRICTS` et du nord, plus `ile` et `aeroport`. Le
  hors-zone se grise sur la mini-carte et la grande carte (une frontière de district seulement).
  ⚠️ **La frontière tombe au premier `retourner`** (tranché par Martin le 30 sept. 2026) : rapporter le
  butin au donneur se fait ailleurs — `v03` est gardée dans la villa jusqu'à « RAPPORTE LE GRAND LIVRE ».
  Une mission dont les objectifs commencent HORS de la frontière (e07 : le vol de clé en ville, avant
  la villa) ne la prend pas.
- ⚠️ **Tout lieu nommé** (`sur_place`, un `lieu` ou un `ou` d'objectif) doit être **dans** la frontière
  (jugé sur la ville, `tests/test_sur_place.py`) : sinon la mission envoie le joueur là où elle le fait
  rater — jusqu'au premier `retourner`. Exemples : `v01`, `v02`, `v03` (`bloc:villa`), `q13` (`quais`),
  `p05` (`pointe`). ⚠️ Un chemin de sortie de bloc sous une frontière veut un rayon qui couvre toute la
  sortie (6 au chemin de la villa) : sinon on ressort sans l'avoir « fait », et la mission rate.
  `test_chaque_mission_sur_place_se_joue_sur_place` juge d'office toute mission qu'on y branche.

**Fichier cible** : un **nouveau fichier** `app/missions/m7.py`, qui déclare
`MISSION = { … }` :

```python
"""La mission m7 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p, _r   # les trois usines de répliques


MISSION = {
    "slug": "m7", "titre": "Un titre court", "donneur": "marco", "prerequis": ["m5"],
    # … tout le dicton ci-dessus …
}
```

Puis **enregistrer la mission** dans `app/missions/__init__.py`, aux deux
endroits :

```python
from . import m1, m2, m3, m4, m5, m6, m97, m7      # 1. l'import

CATALOGUE: list[Mission] = [m1.MISSION, m2.MISSION, …, m97.MISSION, m7.MISSION]  # 2. la liste
```

Le slug est l'ordre de nommage **M16** : le tronc `m6` et `m97` se posent déjà
sur `m5` ; les suivantes suivent. **Rien d'autre à toucher** : `definitions.py`
sert le `CATALOGUE` tel quel, le navigateur lit `B.defs.missions`.

---

## 3. Les personnages (`PERSONNAGES`)

Un **donneur** de mission doit exister dans `PERSONNAGES` avant la mission — **et sa fiche** dans
[`docs/personnages/`](personnages/README.md) : son histoire, sa personnalité, sa façon de parler et de se
présenter. On la lit avant d'écrire sa première réplique ; un personnage neuf a la sienne dans le même
passage. Chaque personnage :

```python
{
    "slug": "marco", "nom": "Marco", "genre": "homme",
    "voix": "Québec Tremblay - Confident and Measured",   # nom exact du compte ElevenLabs
    "couleurs": {"c": "#f1c40f", "h": "#101018", "s": "#c98d66", "p": "#2a2a3a"},
    "ou": "porte:garage",            # où il se tient : `porte:<lieu>` (dehors) ou `point:<type>` (dedans)
    "heler": "Hé! Viens ici!",       # sa BULLE quand il a une job pour toi — ≤ 16 caractères
    "parti_apres": "m5",             # FACULTATIF : il quitte sa place après cette mission
    "arrive_apres": "c04",           # FACULTATIF : il n'est à sa place qu'après cette mission (le vieux maître)
}
```

Règles à respecter :

- **`couleurs`** sont les permutations du sprite `joueur` (c chandail, h
  cheveux, s peau, p pantalon). Tous les personnages sont ce sprite repeint —
  **aucun sprite par personnage**.
- **`voix`** : ne pas inventer. Les voix disponibles sont celles du compte
  ElevenLabs de Martin (`docs/voix-de-l-histoire.md`) ; le serveur
  MCP `elevenlabs` les liste (`scripts/audio_elevenlabs.py --voix` ne fait que
  **générer** les répliques), et on ne devine jamais un nom.
- **`heler` ≤ 16** caractères (jugé `HELER_MAX`) : la bulle se lit en police
  3×5, plus long ça déborde de la tête.
- **`ou` vide** est réservé aux personnages qui ne se tiennent nulle part (le
  client de taxi, le narrateur).
- **`parti_apres`** ne s'écrit **jamais** en dur dans le JS : c'est une donnée
  ici, et un juge interdit tout slug de mission du côté navigateur. ⚠️ Il ne part
  pas tant qu'une mission ni faite ni fermée a **besoin de lui** (il la donne, ou un
  `parler` le vise) : `Histoire.estParti`. Marco (`m97`) reste pour f08, f09 et f12
  si on les joue après, et s'en va à la fin de la dernière.

---

## 4. Les objectifs (`TYPES_OBJECTIFS`)

Un objectif est un dicton `{"type": …, "texte": …}` plus ses clés. Le type doit
appartenir à `TYPES_OBJECTIFS` (sinon le juge refuse). Voici les types et leurs
clés :

| Type | Ce qu'il demande | Clés notables |
|---|---|---|
| `aller` | atteindre un lieu (rayon en tuiles) | `lieu`, `rayon`, `nuit` (attendre la nuit) |
| `parler` | toucher un personnage et lui parler | `cible` (`personnages:` ou `arch:`) |
| `monter` | monter dans le véhicule de la mission | `vehicule`, `ou` (dont `ruelle:<lieu>:<n>`), `prete` |
| `livrer` | amener le véhicule à un lieu | `lieu`, `rayon`, `sans_degats` (prime) |
| `ramasser` | ramasser un objet | `cible: fuyard` (le rattraper d'abord), `vehicule` |
| `tuer` | mettre KO `n` membres d'un `groupe` | `groupe`, `n`, `chef`, `arme`, `vie`, `loin` |
| `survivre` | tenir | `secondes` |
| `course` | passer des points de passage **dans l'ordre** (lue depuis le 29 sept. 2026 : avant, elle avançait dans la même image), le chrono par `chrono_s` ; la flèche vise le point suivant, la ligne compte « 2/4 » ; `a_pied` : au volant, rien ne compte (`p04`) | `points` (des lieux que `resoudre` connaît : un lieu, `zone:`, `pont`, `foire`…), `rayon` (3), `a_pied` |
| `courses` | `n` courses de taxi (klaxon = client) | `n` |
| `semer` | redescendre à 0 étoile | `etoiles` (posées au départ), `escorte` |
| `retourner` | revenir au donneur | — |

**Les neuf types de M16** (la « tranche 1 » : le moteur les déclare, chacun
attend son **juge de banc** avant de porter une mission) :

| Type | Ce qu'il demande | Clés notables |
|---|---|---|
| `suivre` | filer un piéton ou un char sans être vu — trop près ou trop loin, raté | `cible` |
| `proteger` | le **donneur qui est déjà là** (jamais un second) attend qu'on le rejoigne (le GPS mène à lui), puis te suit sur tes pas, à pied, ou monte dans ton char arrêté près de lui ; `lieu` n'est atteint qu'avec lui (il descend en arrivant) ; mission finie, il rentre à son poste hors champ ; couché ou mort, échec `protege_mort` | `cible` |
| `pickpocket` | les poches d'un piéton **précis**, par-derrière (le jet de m2) | `cible` |
| `payer` | donner un montant | `montant` |
| `acheter` | un article à un comptoir | `article`, `ou` |
| `detruire` | un véhicule de la mission | `vehicule` (le char posé), `ou` (où il naît) |
| `sauter` | une rampe | `vol_px` (le juge du Grand Saut) |
| `eteindre` | le feu **de la mission** (depuis le 28 sept. 2026) : il prend sur la façade la plus proche de `ou` (`Incendies.allumerPourMission`, une spirale sans dé), se pose avant l'intro (la caméra le filme), résiste un tiers de seconde au jet d'extincteur, ne paie pas la prime du pompier volontaire et s'en va avec la mission ; la flèche le pointe. Avec `remet: "extincteur"`, le donneur en met un plein dans les mains. Exemple : `f13` | `ou` (un lieu **déjà** de mission — une porte neuve élargirait son devant, et la ville glisserait) |
| `boulots` | `n` boulots d'une `sorte` (généralise `courses`, qui reste au taxi) | `n`, `sorte` |
| `pirater` | s'approcher de `ou`, ACTION l'ouvre, guider une étincelle dans un labyrinthe électrifié (`circuit.js`, depuis le 27 sept. 2026) de la prise au port avec le stick (le même axe unifié que la marche, `Entree.axe` — clavier, manette, doigt) ; un fil touché est un zap (retour au relais), au-delà de `essais` zaps c'est l'échec `alarme` ; le tracé vient de l'empreinte (mission, étape), `longueur` + 3 colonnes sur 4 rangées ; la flèche mène au terminal (le poste, pour un mouillage) — un `ou` loin du donneur se trouve (l'île de m53, m54) | `ou`, `rayon` (déf. 3), `longueur` (déf. 4), `essais` (déf. 3) |
| `obtenir` | (l'infiltration, 28 sept. 2026) un objet dans le sac (`partie.objets[objet]`), d'où qu'il vienne : posé à son lieu (`ou`) et ramassé en marchant dessus, ou dans la poche d'un garde de ronde (`garde`, le slug de sa ronde dans la fiche du bloc — `ou` ne dit alors que où le chercher), volé par-derrière (ACTION, il ne sent rien) ou lâché quand on l'assomme ; `nom` : ce que le HUD dit en le prenant ; `dessin` : `cle`, `dossier`, `registre` ou `sac` (jugé). Une mission ratée fait retomber ce que ses objectifs avaient mis dans le sac (`Infiltration.rendre`). Ou d'une **table de jeu** (`table: "tripot"`, c02, 29 sept. 2026) : l'objet ne se pose nulle part en ville, il vient du feutre (les dés pipés du Pouce, qu'on glisse dans sa manche à la barbotte — `Tripot.glisser`, `tripot.PREUVE`) ; `ou` ne dit que où aller, et l'objectif avance à la sortie (dans une pièce, `majObjectif` dort) | `objet`, `ou`, `garde`, `table`, `nom`, `dessin` |
| `chercher` | (1er oct. 2026, t07) quelqu'un **se cache** (`qui`, un archétype) à 4 à `rayon` tuiles de `ou` (le donneur par défaut) — sur un trottoir collé à un mur ou un décor, jamais la chaussée, l'eau ni le pas d'une porte ; sa place vient de l'empreinte (le jour, la mission), **sans un dé ni un numéro de la ville** (`Histoire.poserLaCachette`). Caché, on ne le voit pas ; la flèche mène au coin, puis se tait ; la ligne d'objectif dit FROID, TIÈDE, CHAUD, BRÛLANT. Trouvé (à pied, à deux pas), il **te suit** comme un escorté, et le `retourner` qui suit ne se fait pas sans lui (« IL EST PAS AVEC TOI ») | `qui`, `ou`, `rayon` (déf. 10), `nom` |
| `remorquer` | (1er oct. 2026, e05) un char (`vehicule`) est PRIS dans la piscine de villa `ou` (`piscine:<lieu>`) dès que l'objectif commence ; la remorqueuse l'en sort au **treuil** — klaxon, à sept tuiles au plus, par-dessus la haie (`Vehicules.aCrocher`, `static/js/piscine.js`) — et on l'amène, accroché, à `lieu` | `vehicule`, `ou`, `lieu`, `rayon` |
| `plonger` | (1er oct. 2026, e14) le char de la mission (le `monter` d'avant) finit dans la piscine `lieu` (`piscine:<lieu>`) : arrêté à cinq tuiles au plus du bord, on descend, il roule dedans et y reste pris (au volant, la ligne dit de descendre) | `lieu` |
| `embarquer` | (M13) être à bord du traversier — à pied ou au volant — quand il **quitte** `escale` ; c'est `Traversier.embarquer` qui prend ce qui est sur le pont à l'heure du départ, et manquer le départ, c'est attendre le suivant (deux heures), pas un échec ; la flèche mène au bout du quai (`traversier:<escale>`) | `escale` (un district de `traversier.ESCALES` : `quais` ou `pointe`) |

⚠️ **`objet` sur n'importe quel objectif** (l'infiltration) : ce que l'objectif FINI met dans le sac — le
code que le terminal piraté crache (`pirater` de v03, `objet: code_voute`), et qui ouvre la serrure du
bloc qui l'attend. `obtenir` le met lui-même, au moment où on le ramasse.

**Les options transverses** (`OPTIONS_OBJECTIFS`) : ce ne sont **pas**
des types, mais des clés qui se posent sur **n'importe quel** objectif —
`chrono_s` (le chrono, que le défi avait déjà ; la ligne d'objectif affiche le temps qui
reste depuis le 28 sept. 2026), `sans_etoile` (échec `etoile` dès qu'on est vu), `sans_arme`
(en territoire de gang les mains vides — lue depuis le 29 sept. 2026 : une arme au poing chez un
gang, c'est l'échec `arme`, et la ligne d'objectif dit « RANGE TON ARME » avant qu'on y entre ;
`q06`), `contre` (des adversaires sur une `course` — ⚠️ encore lue par personne : `p04` bat le temps de
Zed au lieu de courir contre lui). Et deux de plus (28 sept. 2026) : **`remet`** — ce que le
donneur te met dans les mains quand l'objectif commence : une arme, chargée à plein et en
main (`f13`, l'extincteur), ou une tenue, mise au sac (`f10`, la chemise) — et **`tenue`** —
l'objectif ne s'accomplit qu'en la **portant** : un `aller` arrivé dans le mauvais linge
attend (« ENFILE : … »), un `parler` refuse la poignée de main (`f10`, Norbert).
Et deux encore (29 sept. 2026, M13, `m98` _Le Boss_) : **`allies`** — une liste de gangs dont deux membres
chacun arrivent à tes côtés quand l'objectif commence, en courant de l'autre bout de la rue ; ils visent les
hommes de la mission (`cible`) et jamais toi ni l'un des leurs, rien ne les retourne contre toi, et ils restent
tant que les objectifs suivants les nomment (puis rentrent chez eux) — et **`treve`** : la police rentre au poste
quand l'objectif commence (les étoiles à zéro : Bouchard rappelle ses chiens). **`etoiles`**, qu'avait `semer`,
sert aussi `survivre` : on TIENT à ce niveau-là, le chrono court.

Contraintes **jugées** (voir `test_missions.py`) :

- `texte` en **MAJUSCULES**, une ligne (≤ 60 caractères) : c'est ce qui
  s'affiche en objectif.
- `lieu` doit exister dans `carte.SPECIAUX` (ou `kiosque`/`planque`).
- ⚠️ **`lieu` derrière une barrière d'heure : seulement pour une petite job** (la règle de l'usine, 1er oct. 2026 —
  `missions.barriere_d_heure`, `test_barrieres.py`). La porte de l'usine (`usine`) est dans la cour, que sa chaîne
  ferme la nuit. Une mission qui y va ne s'offre qu'aux heures où la barrière est **ouverte** (`Jobs.aLHeure` : un
  passant ne te la propose que le jour), et prise, elle **tient la barrière ouverte** jusqu'à sa fin
  (`Monde.barriereFermee` : la chaîne attend la job) — elle ne peut pas finir porte fermée. Seule une petite job
  (`passant`) sait s'offrir à l'heure : une mission du téléphone ou du carnet, un défi, s'y font refuser
  (`erreurs_de_passant`). La barrière se trouve toute seule (celle dont `ou.lieu` est un `lieu` de la mission) et
  voyage avec la job (un septième champ, pour elles seules). Exemples : `t08`, `t10`. `parler` à quelqu'un qui s'y
  tient reste permis à tous. Le juge ne tourne pas au banc de la mission : lancer `tests/test_barrieres.py`.
- **`aller` à pied, en portant** (t08) : `a_pied` — au volant, l'objectif attend (« À PIED, DESCENDS ») ; `depose` —
  arrivé, l'objet que l'`obtenir` d'avant a mis dans le sac en sort (la boîte suivante peut se ramasser). Le dessin
  `boite` (une boîte de carton) s'ajoute à `cle`, `dossier`, `registre`, `sac`.
- ⚠️ **`piscine:<lieu>`** (e05, e14) : la piscine creusée de villa la plus proche de `<lieu>` (un lieu connu, ou
  `bloc:<slug>` — le passage d'un bloc en ville : `piscine:bloc:villa`, celle au bout du chemin du maire). Aucune
  porte neuve, la ville ne bouge pas ; `test_interieurs` exige qu'il y en ait une à `villas.PRES_TUILES` tuiles.
- `obtenir` pose son objet à **toute forme de lieu** (`rampe:pointe`, `zone:<x>`, `boutique:<mot>` — 1er oct. 2026,
  e08) : un nom nu reste un lieu de porte.
- ⚠️ **`ou: "quai"` et `ou: "bois"` ne posent rien** : `Histoire.tuileDeQuai` cherche les glyphes `q`/`j`
  et `tuileDeBois` le glyphe `n`, que la carte n'a plus — ils rendent `null`, et ce qu'on voulait y poser naît sur
  le joueur (q11, p05 l'ont vu au banc). Nommer un lieu, une `ruelle:` ou une `zone:` à la place.
- ⚠️ **L'Île-aux-Corneilles (`ile.py`) n'est jamais un `lieu`** : elle ne se rejoint pas à pied, et
  `test_barrieres.py` veut qu'on atteigne à pied depuis la planque tout lieu de mission (et `chapelle`
  n'est pas dans `carte.SPECIAUX`). On y envoie par l'`ou` d'un `tuer` ou d'un `pirater` — `"ou":
  "chapelle"`, `"ou": "hangar_ile"` : la flèche suit l'homme posé ou le terminal, on y va en bateau,
  on débarque et on monte à pied (m52-m54, juges `test_m5x_joue_jusqu_au_bout…`).
- ⚠️ **Un lieu de BLOC** (la villa du maire, `app/blocs/villa.py` : `villa_chemin`, `villa_service`,
  `villa_bureau`, `villa_terminal`, `villa_voute`) se nomme comme un lieu de la ville (`lieu`, `ou`) : ce sont
  les `lieux` de la fiche du bloc, que `blocs.LIEUX_PAR_BLOC` recopie avant tout import. En ville, la flèche
  vise le passage du bloc ; dedans, le lieu. Ils ne comptent pas dans `devants.lieux_de_mission` (la ville ne
  bouge pas) et `blocs.erreurs` juge qu'on les rejoint à pied depuis l'arrivée — escaliers pris, serrures
  ouvertes. Une scène les montre par `bloc:<slug>` (le passage en ville, le panneau) : c'est aussi ce que le
  défaut vise. ⚠️ **Tout ce qui s'y joue doit tourner dans un BLOC, jamais dans une pièce** : dans une pièce,
  `majObjectif` et la police dorment.
- ⚠️ **Un `aller` sur le lieu du donneur veut un rayon de 6 tuiles, pas 4** : il se tient à ~48 px du
  point, et le joueur qui lui parle à 16 px de plus (Ti-Paul : 64,03 px contre 64) — on serait AU lieu et
  la mission demanderait un pas de plus.
- `groupe` doit exister dans `pietons.GANGS`.
- `vehicule` doit exister dans `vehicules.CATALOGUE`.
- `ou` de la forme `zone:<x>` → `x` dans `{cravates, port, faubourg}`.
- ⚠️ **Un `monter`/`livrer`/`pirater` sur l'eau** : `ou`/`lieu` en `mouillage:<slug>[:n]` (un grand
  bateau — `carte.mouillages`, `navires.py` ; le centre de la coque, à son cap, hors de `tuileDeRue`) ou
  `amarrage:sven` (la chaloupe amarrée le plus près de son mouillage), ou `amarrage:<lieu>` (l'amarrage de la
  ville le plus près d'un lieu — un point d'eau au pied d'un quai, où l'on accoste : m53, `amarrage:hopital`, le
  relais de la rive nord). Le personnage qui se tient sur un
  mouillage (`ou: "mouillage:<slug>[:n]"` dans `PERSONNAGES`) se pose sur son **poste** — la tuile de quai
  d'à côté, jamais le centre de la coque — pour ne pas boucher l'accès au bateau (m52-m54, Sven).

⚠️ **Règle des hommes de mission (`tuer`)** : un objectif `tuer` pose des
membres d'un `groupe`, qui sortent de l'archétype (`pietons.py`) avec sa vie et
son arme. Deux clés passent par-dessus, **seulement pour CES hommes-là** :

- `arme` — ce qu'ils tiennent ; `""` = les poings (un homme sans arme ne peut
  pas non plus en **lâcher** une en tombant) ;
- `vie` — leurs points de vie ;
- `pieton` — **qui** on envoie, quand ce n'est pas le membre de rue du gang : un piéton de mission
  de fréquence 0 (`matelot`, les gars de Sven, q13 — jugé) ; le gang, lui, reste ce qu'il est ;
- `chef` — **le chef** : le bâton et 160 de vie par défaut, et il vient au joueur ; mais `arme`, `vie` et `ou`
  passent aussi par-dessus pour lui (c06 : Kenny attend à la porte de chez Gus, à mains nues) ;
- `loin` — **ils arrivent** : au lieu d'attendre là où `ou` les pose, ils naissent à `loin`
  tuiles du joueur (16 au plus : au-delà de 260 px ils renoncent), juste hors de l'écran,
  **une fois l'intro finie**, et courent sur lui. Pendant l'intro, `cible` nomme le point d'où
  ils viendront : la caméra peut aller le voir, vide.

⚠️ **On ne touche jamais à l'archétype pour régler une bagarre.** Une Cravate
de rue doit rester ce qu'elle est : c'est elle qui tient le Faubourg (m5).
Ce qui change, c'est **qui on envoie**.

---

## 5. Les dialogues (`dialogue`)

Les temps de dialogue, écrits avec les petites usines `_l`, `_p`, `_r` et `_a`. **Chacune prend
un `jeu=` en dernier** : la même phrase, jouée (§ « Chaque réplique veut aussi son jeu », plus bas).

```python
_l("marco", "Cousin, c'est Marco. Viens au garage.",
   jeu="[casually] Cousin, c'est Marco… Viens au garage.")          # l'appel : il se nomme, une fois pour la mission
_p("marco", "Cours, cousin!", 1, jeu="[firmly] Cours, cousin!")      # PENDANT : accrochée à l'objectif n (0-based)
_r("lulu", "Reviens ce soir.", 0, jeu="[warmly] Reviens ce soir.")   # RENVOI : quand on lui parle trop tôt, à l'objectif n
```

| Partie | Rôle | Règle |
|---|---|---|
| `appel` | le donneur t'appelle au combiné | une réplique, sauf un donneur rencontré en personne (m1) |
| `intro` | le donneur pose le contexte | 2 à 4 répliques |
| `pendant` | dite **quand un objectif commence** | **au moins une** (jugé) ; `_p(qui, texte, objectif)` |
| `renvoi` | ce que dit `qui` quand on **lui** parle alors que ce n'est pas encore son tour (m50 : Lulu, de jour, dit d'attendre la nuit) | facultatif ; `_r(qui, texte, objectif)` ; dit **en personne**, jamais au combiné |
| `accueil` | ce que dit la cible d'un objectif `parler` quand on lui **serre la main** (m6 : Ti-Paul, Lulu, Raymonde, Ovila), avant que l'objectif avance | facultatif ; `_a(qui, texte, objectif)` ; l'objectif est un `parler` dont `qui` est la cible (jugé) ; dit **en personne** ; sans elle, la poignée de main est muette |
| `client` | le client de m3 (réplique dite pendant une mission) | compte comme du « pendant » |
| `fin` | la récompense, dite par **quelqu'un qui est là** | 1 à 3 répliques |
| `echec` | on a raté | une réplique **au combiné** |

✅ **Depuis le 24 sept. 2026, tout ce qui sert à JOUER une mission sort du
paquet** : ses répliques, ses **scènes**, ses **voix** et ses **objectifs**
viennent par `/api/mission/<slug>` (avec un ETag), demandés dès que la bulle de
son donneur s'allume ou que le téléphone la choisit. Le catalogue — son titre,
son donneur, ses prérequis, sa récompense — reste dans le paquet : c'est ce que
le carnet, le GPS et le téléphone lisent, et il faut l'avoir en entier.

⚠️ **Rien ne change pour l'écriture d'une mission** : on écrit ici son fichier
comme avant, objectifs et répliques ensemble, et `missions.pour_jouer` fait le
partage. C'est le seul endroit où le découpage se décide
(`missions.HORS_DU_PAQUET`).

Règles jugées (`erreurs_de_mise_en_scene`) :

- `intro`, `fin`, `echec` **non vides** ;
- une réplique « pendant » (dont `client`) doit exister ;
- l'`objectif` d'une réplique `_p` ou `_r` doit pointer un objectif réel ;
- les répliques de chaque partie sont **toutes dites, et une seule fois**, par
  les plans `dire` de la scène correspondante (§ 6) ;
- ⚠️ **on se présente une fois par mission** (21 sept. 2026, demande de Martin) : la première réplique de
  l'`appel` porte le nom de celui qui appelle — « Cousin, c'est Marco. », « Ici le sergent Bouchard. » —
  et **personne ne redit son nom** ensuite dans la mission (ni au `pendant`, ni à la `fin`, ni à
  l'`echec`, même au combiné) ; et, dans l'ordre du catalogue, la première réplique qu'on entend d'un
  personnage le nomme (`erreurs_de_presentation`). Chacun le fait **à sa façon** : la salutation est dans
  sa fiche, [`docs/personnages/`](personnages/README.md), et les formes dans `docs/jeu-d-acteur.md` § 3.11.
  Le juge ne voit pas la première réplique d'un autre personnage dite de loin (un `pendant`) : nomme-la à
  la main.

⚠️ **L'ordre des slugs de voix ne bouge jamais.** Le slug d'une réplique est
`<qui>-<mission>-<n>`, avec `n` compté dans l'ordre `appel, intro, client, fin,
echec, pendant, renvoi, accueil`. Insérer une réplique au milieu renomme tout ce qui suit, et
des mp3 déjà générés deviendraient des 404. On **ajoute** à la fin, ou on
régénère (`scripts/audio_elevenlabs.py --refaire`).

⚠️ **Chaque réplique veut aussi son jeu, et il est collé à elle** (21 sept. 2026, demande de
Martin : « si on veut que les missions soient lues indépendantes, les interprétations devraient
aussi être dans le fichier de mission »). Le texte est ce qu'on *lit* ; le `jeu=` est ce
qu'ElevenLabs *dit* : les mêmes mots, plus des balises d'émotion en anglais (`[worried]`,
`[sighs]`), des « … » et de la ponctuation. **Une réplique sans son `jeu=` fait rougir
`test_interpretation.py`.** Un verbe d'action par réplique, un ton au moins, un arc du début à
la fin de la mission : tout est dans `docs/jeu-d-acteur.md` § 3.

```python
_a("thibodeau", "Mon argent! T'es un bon garçon, toi.", 1,
   jeu="[relieved] Mon argent! [warmly] T'es un bon garçon, toi.")
```

Ce que ça change, et ce que ça ne change pas :

- **Le jeu suit sa réplique.** Avant, il se rangeait par slug dans `interpretation.py` : insérer
  une réplique au milieu décalait tous les slugs d'en dessous, et chaque voix se mettait à jouer la
  phrase de sa voisine. Collé à la réplique, il n'y a plus de décalage possible — le piège de
  l'ordre reste seulement pour les **mp3** (ci-dessus).
- **Un commentaire d'intention, une fois, au-dessus de `"dialogue"`** : « Marco : la
  désinvolture de qui a peur et le cache… ». C'est l'arc que les balises notent (`docs/jeu-d-acteur.md`
  § 3.3), et il se lit avec le reste de la mission.
- **`app/interpretation.py` garde ce qui n'est pas une mission** : les passants, les repos, le
  journal, l'ouverture, la liste des balises, la finition des voix. Il **rassemble** le jeu des
  missions dans `JEU` (les juges et `scripts/audio_elevenlabs.py` lisent une seule table).
- **Le navigateur ne reçoit jamais le jeu** (`missions.pour_le_navigateur()`) : ce ne serait
  que des balises entre crochets dans le paquet.
- **`jeu=` est facultatif pour l'usine, pas pour le juge** : `_l("marco", "…")` s'écrit sans, mais
  `test_interpretation.py` refuse la réplique — une mission n'est pas finie avant.
- **La variante d'HIVER** (`hiver=(texte, jeu)`, 29 sept. 2026) : ce que la réplique dit tant que la
  neige tient — l'hiver, la moto est remisée et le fuyard file en motoneige, et la mission ne peut plus
  dire « en moto ». `_l(...)` et `_p(...)` la prennent : les mêmes mots, et le même jeu, à la saison
  près. Elle a **sa voix**, au slug de la réplique suivi de `-hiver` (`missions.repliques`) : aucune
  autre voix ne change de nom, et `--refaire <slug>-hiver` la génère seule. Le navigateur choisit
  (`Histoire.lignesDe`, `Saisons.enHiver`). Un **objectif** a la sienne aussi : `"hiver": "RATTRAPE LE
  FUYARD EN MOTONEIGE"` à côté de `"texte"` (`Histoire.texteDObjectif`). ⚠️ Un fuyard ou un char de
  mission en moto devient une motoneige l'hiver, une berline sous la pluie (`charDeSaison`) : une
  réplique qui dit « moto » veut sa variante (m2, f04, p13, q10 l'ont).

### 5 bis. Un choix dans un dialogue (1er oct. 2026)

Les choix « ferme l'autre » (`q10`/`q11`, `d07`/`d08`, `r03`/`r04`) se font en prenant une mission plutôt qu'une
autre. Celui-ci se fait **en parlant** : une réplique pose une question, le joueur répond (deux ou trois réponses, au
clavier, à la manette ou au doigt), et **la même mission bifurque**. Tout se déclare dans son fichier — exemple
complet : `app/missions/d09.py` (Léo doit 800 $ à Sal ; on le couche, ou on paie pour lui).

```python
"accueil": [
    _a("leo", "Huit cents? J'ai un hangar vide pis une chaloupe qui prend l'eau. Tu veux quoi, au juste?", 2,
       jeu="…",
       choix=[("coucher", "SAL VEUT SON ARGENT. TOUT DE SUITE."),     # (clé, ce que le joueur répond)
              ("payer", "LAISSE FAIRE. JE PAIE TES 800 $.")]),
    _a("leo", "Tout de suite? Ben les gars du hangar vont avoir leur mot à dire.", 2, jeu="…", branche="coucher"),
    _a("leo", "Toé? Pour moé? J'ai rien vu, pis j'oublierai pas.", 2, jeu="…", branche="payer"),
],
"objectifs": [ …,
    {"type": "tuer", …, "branche": "coucher"},                       # ne se joue que sur cette branche
    {"type": "payer", "montant": 800, "texte": "PAIE LES 800 $ DE LÉO", "branche": "payer"},
    …],                                                              # sans `branche` : sur les deux
"branches": {"payer": {"recompense": 0, "donne": {"dette": -800, "message": "…"}}},  # ce que la fin paie autrement
```

- **La question** : `choix=[(clé, texte), …]` sur `_l`, `_p` ou `_a`, dans l'`intro`, un `pendant` ou un `accueil`
  (en personne, jamais à l'appel ni à la fin) ; **une par mission** ; 2 ou 3 réponses ; le texte d'une réponse en
  MAJUSCULES, 44 caractères au plus. Le joueur ne parle pas : ses réponses s'affichent, elles ne se disent pas.
- **À l'écran** : la réplique reste dans sa boîte, sa voix continue, et la boîte **TA RÉPONSE** s'ouvre juste
  au-dessus (`Histoire.ouvrirLeChoix`, un menu du HUD `obligatoire`). Ni ACTION, ni le temps de lire, ni PAUSE,
  RETOUR, FRAPPE ou CARTE ne la passent ; elle fait la sourde oreille 12 images en s'ouvrant (un pouce qui martèle
  ACTION ne répond pas par accident). Sous une scène, la scène attend la réponse.
- **Ce qui bifurque** : une **réplique** (`branche=clé`, dite seulement sur cette branche — après la question,
  dans l'ordre où on l'entend), un **objectif** (`"branche": clé`, sauté sur l'autre — jamais l'objectif où la
  question se pose, ni un avant ; une question d'intro ne décide qu'à partir de l'objectif 1, le 0 se pose avant
  l'intro), et **ce que la fin paie** (`branches[clé]` : `recompense`, `donne` par-dessus celui de la mission,
  `ferme`). Chaque réponse doit changer quelque chose (jugé).
- **La sauvegarde** : la réponse vit dans `partie.mission.branche` pendant la mission, puis dans
  `partie.choix[<slug>]` quand elle réussit. Une autre mission peut l'**exiger** : `"exige": {"choix": {"d09":
  "payer"}}` (une relation qui a changé). Une question qu'on n'a pas répondue (sautée avec sa scène) se **repose**
  avant l'étape qui bifurque ; un banc qui saute à la fin prend la première réponse.
- **Les juges** : la forme, `missions.erreurs_de_choix` (cousu à `erreurs_de_mise_en_scene`,
  `tests/test_choix.py`) ; le jeu, au bouton et de chaque côté, `tests/test_choix_js.py`.

### 5 ter. Une petite job : un passant qui la donne (1er oct. 2026)

Une mission courte peut se donner **dans la rue, par un passant ordinaire** — pas un personnage de l'histoire : il
te repère, marche jusqu'à toi en te hélant, et ACTION à côté de lui lance son intro, puis la job, **sans
téléphone**. Exemples : `t02.py` (le débardeur et son lunch), `t03.py` (un lift, `proteger`), `t05.py` (la sacoche,
`pickpocket`), `t13.py` (la pelle du vieux, `tuer` + `retourner`), `t07.py` (le p'tit qui se cache, `chercher` +
`retourner`).

```python
"donneur": "passant",                     # ou "passante" : deux RÔLES (`missions.DONNEURS_PASSANTS`)
"prerequis": ["m6"],                      # après le tour du propriétaire
"passant": {"archetype": "docker",        # QUI : un archétype de la rue (`pietons.CATALOGUE`, jamais un gang ni un métier)
            "district": "quais",          # OÙ il se présente (None : partout)
            "nom": "Le débardeur"},       # le nom de sa boîte de dialogue (24 caractères au plus)
"dialogue": {
    "hele": [_l("passant", "Hé! Le jeune!", jeu="[cheerful] Hé! Le jeune!")],   # son hèlement : SA BULLE et sa voix (≤ 16)
    "intro": [ … ], "pendant": [ … ], "fin": [ … ], "echec": [ … ],             # PAS d'appel : il n'a pas ton numéro
},
```

- **Le moteur** (`static/js/jobs.js`) : une offre par **demi-journée** au plus (`partie.jobOfferte`), jamais
  pendant une mission, un défi, une sonnerie ou une poursuite, seulement **à pied** et dehors, une minute et demie au
  moins après la dernière mission ; la job tirée à l'empreinte de la demi-journée parmi celles **de ton district**
  (ou de partout). Il naît **à l'empreinte** : à 7–11 tuiles, sur un trottoir d'où il marche jusqu'à toi, un dé
  prêté (`creerPieton` en tire deux), un numéro hors de la suite (`Entites.enDehorsDeLaSuite`), sa tenue tirée de
  la garde-robe de son archétype : la ville ne glisse pas. Laissé en plan (on s'éloigne, trente secondes sans lui
  parler), il dit « Laisse faire. » et redevient un passant ; la job reviendra une autre demi-journée.
- **Une job ne s'offre jamais autrement** : ni au téléphone, ni au carnet, ni par la bulle d'un donneur
  (`Histoire.disponibles` les écarte). Elle **voyage pliée** (la clé `jobs` du paquet, une liste par job :
  `missions.jobs_pour_le_navigateur`, l'ordre de `CHAMPS_D_UNE_JOB`), et le navigateur la remet dans le catalogue en
  arrivant (`Jobs.deplier`) ; son passant entier (le nom de sa boîte) arrive avec elle (`/api/mission/<slug>`). Une
  petite job n'a ni `exige` ni `ferme`.
- **Tout se dit en personne** (même l'échec), sans portrait, sous le nom de `passant.nom`, avec la voix des passants
  (Felix, Amélie). Il **ne se présente pas** (un inconnu ne dit pas son nom).
- **La fin se dit devant lui** : le dernier objectif est un `retourner` (il attend là où il t'a hélé), ou il est avec
  toi (`proteger`, `cible` = le passant). Jugé : `missions.erreurs_de_passant` (`tests/test_jobs.py`) ; au banc,
  `tests/test_jobs_js.py`. La triche (SAUT VERS UNE MISSION) et les bancs le font se présenter à deux pas
  (`Jobs.offrir(slug, true)`).
- `hele` se compte en **dernier** dans `PARTIES` : aucune voix déjà payée ne change de nom.

---

## 6. Les scènes (`scenes`, le vocabulaire de plans)

> ⚠️ **Commence par ne pas en écrire.** `missions.scene_par_defaut` bâtit l'intro
> et la fin de ce que ta fiche dit déjà. Quatre formes, et on ne les a pas
> inventées — ce sont celles que les missions écrites à la main ont fini par
> prendre (mesuré le 20 sept. 2026 : **cinq des seize scènes du catalogue étaient
> mot pour mot celles du défaut**, elles sont effacées, et le paquet exporté n'a
> pas bougé d'un octet) :
>
> | Le donneur | L'intro par défaut | La fin par défaut |
> |---|---|---|
> | **dehors** (`porte:`) | il dit un mot, `montrer` vers le premier lieu que la mission nomme, la caméra y va, il finit, la caméra revient | **chez lui** : il `prendre` ce qu'on rapporte, il `donner` ce qu'on gagne |
> | **dedans** (`point:`) | il dit un mot, une `coupe` sort voir ce lieu, il `bras_croises`, il finit | **ailleurs** : une `coupe` chez lui — sans elle, on l'entendrait de nulle part |
>
> **Écris la tienne quand tu veux mieux**, et seulement alors : m2 vise la `cible`
> (les deux Cravates posées), m5 tient son dernier plan vingt images de plus, m1
> fait sortir Ti-Guy du garage. ⚠️ Le défaut, lui, ne vise **que ce que Python peut
> garantir** — un lieu nommé par un objectif, la porte du donneur (`chez:`), le
> joueur, le donneur. Jamais `cible` ni `fuyard` : un plan dont le lieu ne se
> résout pas est **sauté en silence**, et une animation qui ne joue pas est pire
> qu'une animation absente.

> **Écrire la tienne, oui — mais pour dire quelque chose.** Une phrase d'intention
> d'abord (« après cette scène, le joueur sait / ressent… »), l'image pour le *où*
> et la voix pour le *pourquoi*, le geste sur le mot qui le porte, un silence
> après la réplique qui compte : `docs/jeu-d-acteur.md` § 2.

Une scène est une **liste de plans**, typés dans `TYPES_PLANS`. `scenes.js` les
joue **sans connaître aucune scène par son nom**. Si une scène ne s'écrit pas
avec les types existants, on ajoute **un type** — jamais un
`if (slug === 'q07')`.

**Types de plan et clés** (`TYPES_PLANS` est la référence exacte) :

| Type | Rôle | Clés |
|---|---|---|
| `camera` | aller voir un lieu, le tenir, revenir | `vers`, `recul`, `duree`, `courbe`, `lissage` |
| `marcher` | un acteur va à un lieu à pied ; **`pres` est obligatoire quand `vers` est `joueur`** (22 px, la distance de parole) — sans lui il finit sur le joueur | `acteur`, `vers`, `duree`, `pres` |
| `conduire` | un char entre / part | `acteur`, `vehicule`, `couleur`, `vers`/`part`, `depuis`, `duree`, `courbe`, `fumee`, `portiere`, `retirer` |
| `geste` | un geste du sprite (montrer, donner, prendre, bras_croises, hausser, telephone) | `acteur`, `geste`, `duree`, `vers` |
| `entrer` / `sortir` | un acteur passe une porte | `acteur`, `dans`/`de`, `vers` |
| `coupe` | fondu vers un autre lieu — ou une **liste** de lieux, visités d'un seul aller-retour — puis retour | `vers` (un lieu ou une liste), `ferme`, `ouvre`, `tient` (par lieu) |
| `dire` | réplique(s) de la partie, la scène se joue **sous** elles | `repliques` (comptées à partir de 1) |
| `titre` | le carton (logo ou texte) | `texte`, `sous`, `logo`, `monte`, `tenu`, `descend` |
| `son` | un bruitage, un morceau, une boucle | `sfx` / `musique` / `boucle` (un seul) |
| `attendre` | n images | `duree` |

**Clés partout** : `type` (obligatoire), `ensemble` (le plan part sans
attendre le précédent), `fond` (le plan ne retient pas la scène).

**Règles du moteur** (toutes jugées) :

- **Un plan dont le lieu ou l'acteur ne se résout pas est SAUTÉ**, jamais
  attendu : une scène se termine toujours.
- **Aucun dé tiré** : jouer la scène ou la passer donne le même monde.
- **La mission se pose AVANT sa scène d'intro** (sinon la caméra filme un coin
  vide). Dedans, rien ne se pose avant la sortie.
- **On la passe** : ACTION saute une réplique, PAUSE saute la scène.
- **Elle ne déplace pas le joueur** (la caméra voyage, le bonhomme reste).
- **Jamais en pleine action** : la scène de fin ne part ni à 3★ ni dans un char
  en marche ; l'argent et `donne` sont accordés tout de suite.
- **Courte** : ≤ 3 secondes après le dernier mot.
- **Une réplique ne se cale pas toute seule.** Une `dire` en `ensemble` joue sous le plan qui
  retient la scène ; si ce plan finit avant la voix, la réplique suivante la COUPE. Mesurer la
  voix (`ffprobe`), laisser de la marge (un `attendre`) : `m6` est l'exemple, et
  `test_le_tour_du_proprietaire_laisse_finir_ses_repliques` en est le juge. Plus simple quand on ne
  veut qu'une coupe sous la réplique : la coupe en `ensemble`, PUIS la `dire` sans `ensemble` — c'est la
  voix qui retient la scène (`q02`, `m51`). `test_aucune_voix_de_scene_n_est_coupee_par_la_suivante`
  joue toutes les scènes avec la durée de leurs mp3 : il refuse une voix coupée, une fois générée.

**Les acteurs nommables** : `joueur`, `donneur`, `vehicule`, `cible`, `fuyard`,
plus tout `slug` de `PERSONNAGES`. **Les formes de lieu** : un acteur,
`place:<acteur>`, `porte:<lieu>`, `ruelle:<lieu>`, `zone:<x>`, `chez:<personnage>`, `bloc:<slug>` (le
passage d'un bloc de carte, en ville — la villa de v01 à v03).

⚠️ **La fin ne parle pas par la bouche d'un absent.** Si le dernier objectif
n'est pas `retourner` (et qu'on n'est pas chez le donneur), la scène de fin doit
soit **faire venir** le donneur (`sortir` + `marcher`), soit **aller le voir**
(`coupe` vers `chez:<donneur>` ou `donneur`). Sinon on entend quelqu'un qui n'est
pas là — et le juge le refuse.

---

## 7. `donne` : ce que la fin accorde

En plus de `recompense`, la mission peut donner :

- `arme` — un slug d'`armes.CATALOGUE` ;
- `propriete` — un slug d'`economie.PROPRIETES` ;
- `vehicule` — un véhicule garé à la planque ;
- `message` — le toast de récompense ;
- d'autres clés spécifiques (rabais, `sergent_ami`, `faubourg_libere`,
  `manchette`, `contacts`…).

À partir de M16, `donne` grossit. Chaque clé a **un** endroit qui la lit, dans
`Histoire.recompenser()` :

- `technique` — une technique du répertoire (payante au DOJO DION) que le donneur t'**apprend** (c07, le retournement
  du poignet) ; déjà sue, rien de plus ;
- `libere: "<district>"` — généralise `faubourg_libere` : son gang ne sort plus dans la rue
  (`Entites.gangChasse`), ne saute plus sur personne (`gangCalme`), sort du jeu des territoires
  (`Territoires.horsJeu`) et rend les coins qu'il avait pris (`Territoires.liberer`) ; sous la
  mini-carte, sa cour redevient le nom du quartier (`q13`, les Quais) ;
- `calme: "<gang>"` — `hostile_toujours` et `hostile_si_arme` tombent ;
- `a_vendre: "<propriété>"` — une propriété que rien ne vendait (`phase: 2`) se met en vente
  (`partie.enVente`) : l'hôtel après `q07`, la quatrième propriété de _Le Boss_ ;
- `contact` — un numéro de plus au téléphone ;
- `vehicule`, `tenue`, `munitions`, `rabais` par comptoir ;
- `dette: -n`, `casier: -n`, `ami`/`ennemi`, `boulot`, `manchette` ;
- `boss: true` (M13, `m98`) — **la ville change de couleur**, pour de bon (`partie.boss`, gardé par la
  sauvegarde) : les gangs des districts libérés reviennent dans leur cour à tes couleurs, on te salue dans la
  rue, plus de rixe aux frontières, le nom sous la mini-carte et la grande carte à l'or des Bandini
  (`pietons.BOSS`).

**`exige` et `ferme`** (M16) viennent compléter `prerequis` :

- `exige` — ce qu'il faut avoir **en plus** des prérequis : `argent_min`,
  `proprietes`, `liberes`, `dette`, `tenue`, `heure`, `choix` (une réponse donnée dans une autre mission, § 5 bis), et `une_de` (29 sept. 2026, q13 : l'une
  **ou** l'autre de ces missions faite — un prérequis ne sait dire que « et », et après un choix
  `ferme`, la suite s'ouvre par l'un ou l'autre côté). Un prérequis dit « après
  quoi » ; `exige` dit « dans quel état ».
- `ferme` — une mission qui en **ferme** une autre (un choix) : une mission
  fermée n'apparaît plus jamais, ni au téléphone ni au carnet.

Tout ça est jugé : `arme` doit exister, `propriete` doit exister.

**`generique: true`** (M13) — une **fin de partie**. Après la scène de fin, la mission joue sa
scène `scenes["generique"]` sous ses répliques `dialogue["generique"]`, dites par le **narrateur du
Clairon** et lui seul, sans nom au-dessus de la boîte (comme l'ouverture) ; puis le BILAN s'ouvre, la
fin est retenue (`partie.fins`) et **la partie continue**. Les trois vont ensemble (jugé) : un générique
sans scène est muet, une scène sans `donne.generique` ne se joue jamais. `generique` se compte en
dernier dans `PARTIES` (les voix déjà payées gardent leur slug). Un plan `titre` y écrit les chiffres
de la partie entre accolades — `{fortune}`, `{missions}`, `{proprietes}`, `{jours}`, `{dette}`,
`{liberes}` (`VALEURS_DE_TITRE`, toute autre clé est refusée). Une fin de partie paie `recompense: 0`,
et c'est la seule mission qui le peut. Exemples : `m99.py` (on part), `m98.py` (on reste — sa musique à lui,
`generique_boss`, et un carton écrit en toutes lettres, « DÉCHIRÉE »).

---

## 7 bis. Un chapitre : une mission de 5 à 10 minutes

Martin, 30 sept. 2026 : « les missions doivent durer au moins 5 à 10 minutes chacune ». Une mission qui
raconte plusieurs choses s'écrit en **chapitre** : un fichier comme les autres, dont les objectifs sont
coupés par des **actes**. Le premier : `app/missions/la_pointe.py` (six actes, du pont bloqué à la paix
signée). La fiche : `docs/jalons/des-missions-en-chapitres.md`.

```python
"remplace": ["p02", "p05"],          # s'il reprend des missions existantes : une par acte, dans l'ordre
"objectifs": [
    {"type": "acte", "texte": "ACTE 1 — LE PONT EST BLOQUÉ", "donneur": "bilodeau"},
    {"type": "tuer", …, "renforts": {"vagues": 1, "n": 2}},
    {"type": "retourner", "texte": "RETOURNE VOIR M. BILODEAU", "donne": {"message": "LE PONT EST OUVERT"}},
    {"type": "acte", "texte": "ACTE 2 — LES COLLETS", "donneur": "trappeur",
     "sur_place": {"lieu": "phare", "heure": "nuit"}},
    …
],
```

- **Le marqueur `acte`** est instantané : son `texte` en carton, le **point de reprise** (la place en ville,
  le char, l'arme), le `donneur` de l'acte — c'est lui qui a la bulle, que le `retourner` vise et que le
  téléphone rappelle. `sur_place` (facultatif) fait le saut à l'heure et au lieu, comme § 2. Un chapitre
  **commence** par un acte et ne **finit** pas sur un acte (`erreurs_de_chapitre`, jugé).
- **Mourir ou se faire pogner** dans un chapitre ouvre, après l'hôpital ou le poste, **REPRENDRE L'ACTE N**
  (l'arme de l'acte est rendue, même confisquée) ou **PLUS TARD** (l'acte reste atteint, le donneur de
  l'acte rappellera). Rien à écrire : c'est le moteur (`static/js/chapitres.js`).
- **Un `retourner` au milieu d'un chapitre passe à l'acte suivant** ; chaque acte paie SA prime par le `donne` de
  son dernier objectif (`"donne": {"prime": 150, "message": …}`), et `recompense` est celle du dernier acte. Une vieille
  partie qui avait fait la mission d'un acte le saute : ni rejoué, ni repayé.
- **Les répliques** : `appel` et `intro` sont celles du premier acte ; ce qui ouvre un acte suivant
  (le donneur qui appelle, puis ce qu'il explique) est un `pendant` **sur l'étape du marqueur** ; la fin
  d'un acte, dite en personne, un `pendant` sur le marqueur de l'acte **suivant** ; `fin` est celle du
  dernier acte, **chez le donneur du dernier acte** (`donneur_final`). « Qui parle se nomme » : une fois par
  personne dans le chapitre. Plafond de répliques : 18 **par acte**. Quand un arc existant passe en chapitre, le
  nom redit à l'appel d'un acte suivant se COUPE dans la même voix (`ffmpeg`, au silence, le temps mort de 0,35 s
  remis) plutôt que de payer une voix neuve (la dette, 2 oct. 2026).
- **L'échec d'un acte** : `_e(qui, texte, marqueur, jeu=…)` dans `echec` — dite seulement si c'est cet acte qui rate
  (`marqueur` = l'étape de son `acte`) ; une réplique `_l` sans étape se dit pour n'importe lequel. Un arc passé en
  chapitre garde ainsi l'échec de chacune de ses missions.
- **`remplace`** : une partie qui avait fait ces missions reprend au premier acte pas fait ; toutes faites,
  le chapitre l'est aussi. Une mission remplacée sort du catalogue ; un `prerequis` peut la nommer encore : il
  attend alors son ACTE (h03 attend d01, l'acte 1 de _La dette de Rocco_), marqué fait quand l'acte finit.
- **Ce qui ne se met pas en chapitre** : un acte avec un `exige` (il bloquerait tout le chapitre dès son premier
  acte), une `frontiere`, un échec propre (`arme`), ou un bout d'un CHOIX (`ferme`) — ces missions restent seules.
- **Le chronomètre** : le temps de chaque acte s'écrit dans la partie (`durees`), et le carnet l'affiche à côté
  de FAITE. C'est lui qui dit si on tient 5 à 10 minutes.

**Ce qui fait durer** — des options, jamais automatiques, à mettre là où l'histoire les justifie :

| Option ou type | Sur | Ce que ça fait |
|---|---|---|
| `renforts: {"vagues": 2, "n": 2}` | `tuer`, `tenir` | quand il ne reste qu'UN debout, la vague suivante arrive de loin |
| `poursuite: {"groupe": "skateux", "chars": 1}` | `aller`, `livrer`, `retourner`, `proteger` | un char du gang naît hors champ et te colle ; l'objectif fait, il retourne au trafic |
| `etoiles: 2` | tout objectif | la police à ce niveau au départ |
| `donne: {…}` | tout objectif | ce que CET objectif accorde quand il est fait ; `prime` (la prime de l'acte) se paie au bandeau avec son `message` |
| `tenir` (type) | — | rester à `lieu` (`rayon`) `secondes` ; en sortir remet à zéro, ou rate (`strict`) ; `groupe`/`n`/`renforts` : ceux qui viennent te déloger |
| `relais: 1` | `ramasser` + `cible: fuyard` | rattrapé, il saute dans un autre char tout près, N fois |

La tournée (N arrêts dans l'ordre) n'est pas un type : c'est une `course` sans `chrono_s`.


## 8. La checklist de fin (ce que les tests vérifient)

Avant de dire « c'est fini », lancer :

```bash
uv run python scripts/verifier_missions.py --detail         # ce qui manque, en clair
uv run python scripts/verifier_table_des_jalons.py          # si une ligne de jalon a été ajoutée
uv run python -m pytest tests/test_missions.py tests/test_mise_en_scene.py tests/test_missions_en_scene_js.py -q
uv run python -m pytest tests/test_interpretation.py -q -k "jeu or balises"   # chaque réplique a son jeu
uv run python scripts/verifier_carte_du_plan.py             # SI un personnage a été ajouté (docs/carte.md !)
```

⚠️ **Et il n'y a rien à inscrire dans les juges.** Ils lisent le catalogue —
`ordre_topologique()`, `fin_dite_en_personne()` — au lieu de nommer les missions
en dur, et chaque mission est jugée **deux fois** : avec la scène qu'elle écrit,
et avec celle que le défaut lui bâtirait. Le 20 sept. 2026, quatre d'entre eux
nommaient encore des slugs, et l'un d'eux s'était arrêté à m5 pendant que le
catalogue en comptait huit.

Le squelette d'un fichier neuf s'imprime :

```bash
uv run python scripts/verifier_missions.py --squelette m7 --donneur josee
```

Et vérifier que `docs/carte.md` et le plan sont **mis à jour** (un
nouveau personnage → `docs/carte.md` § personnages ; une nouvelle mission →
ligne de jalon : ⬜ dans `docs/plan.md` tant qu'elle est en cours, puis ✅ dans
`docs/jalons/README.md`).

### Ce que les juges refusent (récapitulatif)

- un objectif sans type, ou un type inconnu ;
- un `texte` d'objectif pas en MAJUSCULES ou trop long ;
- un `lieu`/`groupe`/`vehicule`/`arme`/`propriete` inconnu ;
- un `echec` hors de `ECHECS` (`mort`, `arrete`, `vehicule_detruit`, `chrono`,
  et depuis M16 `etoile`, `protege_mort`, `alarme`, `arme`, et `hors_zone` — la frontière) ;
- un `sur_place` ou une `frontiere` mal formés (`erreurs_de_sur_place`), ou un lieu nommé hors de
  sa frontière ;
- un donneur sans position (`perso["ou"]` vide) ;
- `intro`/`fin`/`echec` sans répliques, ou pas de « pendant » ;
- une scène `intro` ou `fin` manquante ou vide ;
- un plan au type inconnu, aux clés inconnues, aux valeurs invalides ;
- un acteur ou un lieu inconnu dans un plan ;
- des répliques manquantes ou en double dans les plans `dire` ;
- une fin dite par un donneur absent, sans que personne n'aille le voir ;
- une réplique **sans son `jeu=`** (dans le fichier de la mission), un jeu qui ne dit pas
  **les mêmes mots** que la boîte, une balise que v3 ne connaît pas, un jeu sans
  aucune balise de **ton**.

Et ce qu'**aucun** juge ne refuse : une scène plate, une voix fausse. Ça s'écoute.

---

## 9. Les défis (à part, pour mémoire)

À côté de `CATALOGUE`, `DEFIS` porte les **défis** : un panneau en ville, un
chrono, une prime, une seule fois. Ce n'est **pas** une mission (pas de scènes,
pas de donneur) — mais les jeux d'adresse de la foire y tiennent le même rail :
un lieu, un compte, un chrono, une prime, un texte en majuscules. Une prime de
foire ne bat **jamais** un boulot honnête à l'heure (`prime / chrono_s` sous le
taux du taxi).

---

## 10. Résumé en une phrase

Une mission est **trois choses** — ses objectifs, ses dialogues et ses scènes —
toutes trois jugées ; elle vit **dans son propre fichier** `app/missions/<slug>.py`
(`MISSION = {…}`), le donneur dans `PERSONNAGES` (dans `__init__.py`), les scènes
dans le vocabulaire de `TYPES_PLANS`, et le navigateur ne décide rien. **Mais tu
n'écris que ce qui la distingue** : les clés par défaut et les deux scènes lui
sont données — c'est le bloc Lego.

⚠️ **Et elle se joue.** Câblée, elle passe les juges ; bien jouée, elle se souvient.
`docs/jeu-d-acteur.md` dit comment : une intention par scène, une émotion par
réplique, un silence là où ça compte.

⚠️ **Ce document suit le moteur, pas l'inverse.** Les neuf types d'objectifs de
M16 (`suivre`, `proteger`, `pickpocket`, `payer`, `acheter`, `detruire`,
`sauter`, `eteindre`, `boulots`), les deux échecs (`etoile`, `protege_mort`),
les options transverses (`chrono_s`, `sans_etoile`, `sans_arme`, `contre`) et
l'extension `exige`/`ferme`/`donne` y figurent à leur place : un type n'est
**pas** livré tant qu'il n'a pas son juge de banc, et une mission qui s'en sert
avant ce juge n'est pas finie.