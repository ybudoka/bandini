# Monter une mission — mode d'emploi pour une IA

Ce document explique **comment ajouter une mission de bout en bout** dans
Bandini, à l'intention d'une IA (ou d'un humain) qui découvre le projet. Il ne
remplace ni `docs/plan.md` (la vision) ni `docs/carte.md` (l'inventaire de la
ville) : il raconte la **recette**, pas le pourquoi.

> ⚠️ **Une mission = un fichier.** Les missions vivent dans `app/missions/`,
> **une par fichier** (`m1.py`, `m2.py`, … `m97.py`) : chacun déclare `MISSION = {…}`
> et n'a besoin que de `_l`/`_p` (importés de `_commun.py`). Le moteur — les
> types d'objectifs, les personnages, les défis, les scènes d'ouverture, les
> juges — vit dans `app/missions/__init__.py`. **Ajouter une mission = créer son
> fichier et l'ajouter aux deux listes de `__init__.py`, rien d'autre.**
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
    "objectifs": [ … ],                 # § 4
    "scenes": {"intro": [ … ], "fin": [ … ]},   # FACULTATIF : § 6, le défaut les bâtit
    "dialogue": {                       # § 5
        "appel":      [ … ],
        "intro":      [ … ],
        "pendant":    [ … ],
        "client":     [ … ],
        "fin":        [ … ],
        "echec":      [ … ],
    },
}
```

**Fichier cible** : un **nouveau fichier** `app/missions/m7.py`, qui déclare
`MISSION = { … }` :

```python
"""La mission m7 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p   # les deux usines de répliques


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

Un **donneur** de mission doit exister dans `PERSONNAGES` avant la mission.
Chaque personnage :

```python
{
    "slug": "marco", "nom": "Marco", "genre": "homme",
    "voix": "Québec Tremblay - Confident and Measured",   # nom exact du compte ElevenLabs
    "couleurs": {"c": "#f1c40f", "h": "#101018", "s": "#c98d66", "p": "#2a2a3a"},
    "ou": "porte:garage",            # où il se tient : `porte:<lieu>` (dehors) ou `point:<type>` (dedans)
    "heler": "Hé! Viens ici!",       # sa BULLE quand il a une job pour toi — ≤ 16 caractères
    "parti_apres": "m5",             # FACULTATIF : il quitte sa place après cette mission
}
```

Règles à respecter :

- **`couleurs`** sont les permutations du sprite `joueur` (c chandail, h
  cheveux, s peau, p pantalon). Tous les personnages sont ce sprite repeint —
  **aucun sprite par personnage**.
- **`voix`** : ne pas inventer. Les voix disponibles sont celles du compte
  ElevenLabs de Martin (`docs/plan.md`, « Les voix de l'histoire ») ;
  `scripts/audio_elevenlabs.py --voix` les liste, il ne devine jamais.
- **`heler` ≤ 16** caractères (jugé `HELER_MAX`) : la bulle se lit en police
  3×5, plus long ça déborde de la tête.
- **`ou` vide** est réservé aux personnages qui ne se tiennent nulle part (le
  client de taxi, le narrateur).
- **`parti_apres`** ne s'écrit **jamais** en dur dans le JS : c'est une donnée
  ici, et un juge interdit tout slug de mission du côté navigateur.

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
| `course` | passer des points de passage, chrono | `points` |
| `courses` | `n` courses de taxi (klaxon = client) | `n` |
| `semer` | redescendre à 0 étoile | `etoiles` (posées au départ), `escorte` |
| `retourner` | revenir au donneur | — |

**Les neuf types de M16** (la « tranche 1 » : le moteur les déclare, chacun
attend son **juge de banc** avant de porter une mission) :

| Type | Ce qu'il demande | Clés notables |
|---|---|---|
| `suivre` | filer un piéton ou un char sans être vu — trop près ou trop loin, raté | `cible` |
| `proteger` | un personnage te suit à pied ou monte avec toi ; s'il meurt, échec `protege_mort` | `cible` |
| `pickpocket` | les poches d'un piéton **précis**, par-derrière (le jet de m2) | `cible` |
| `payer` | donner un montant | `montant` |
| `acheter` | un article à un comptoir | `article`, `ou` |
| `detruire` | un véhicule de la mission | `vehicule` (le char posé), `ou` (où il naît) |
| `sauter` | une rampe | `vol_px` (le juge du Grand Saut) |
| `eteindre` | un feu à l'extincteur (le jet existe, le feu de char aussi) | — |
| `boulots` | `n` boulots d'une `sorte` (généralise `courses`, qui reste au taxi) | `n`, `sorte` |

**Les quatre options transverses** (`OPTIONS_OBJECTIFS`) : ce ne sont **pas**
des types, mais des clés qui se posent sur **n'importe quel** objectif —
`chrono_s` (le chrono, que le défi avait déjà), `sans_etoile` (échec `etoile`
dès qu'on est vu), `sans_arme` (en territoire de gang les mains vides),
`contre` (des adversaires sur une `course`).

Contraintes **jugées** (voir `test_missions.py`) :

- `texte` en **MAJUSCULES**, une ligne (≤ 60 caractères) : c'est ce qui
  s'affiche en objectif.
- `lieu` doit exister dans `carte.SPECIAUX` (ou `kiosque`/`planque`).
- `groupe` doit exister dans `pietons.GANGS`.
- `vehicule` doit exister dans `vehicules.CATALOGUE`.
- `ou` de la forme `zone:<x>` → `x` dans `{cravates, port, faubourg}`.

⚠️ **Règle des hommes de mission (`tuer`)** : un objectif `tuer` pose des
membres d'un `groupe`, qui sortent de l'archétype (`pietons.py`) avec sa vie et
son arme. Deux clés passent par-dessus, **seulement pour CES hommes-là** :

- `arme` — ce qu'ils tiennent ; `""` = les poings (un homme sans arme ne peut
  pas non plus en **lâcher** une en tombant) ;
- `vie` — leurs points de vie ;
- `loin` — **ils arrivent** : au lieu d'attendre là où `ou` les pose, ils naissent à `loin`
  tuiles du joueur (16 au plus : au-delà de 260 px ils renoncent), juste hors de l'écran,
  **une fois l'intro finie**, et courent sur lui. Pendant l'intro, `cible` nomme le point d'où
  ils viendront : la caméra peut aller le voir, vide.

⚠️ **On ne touche jamais à l'archétype pour régler une bagarre.** Une Cravate
de rue doit rester ce qu'elle est : c'est elle qui tient le Faubourg (m5).
Ce qui change, c'est **qui on envoie**.

---

## 5. Les dialogues (`dialogue`)

Cinq temps, écrits avec les petites usines `_l` et `_p` :

```python
_l("marco", "Marco, le cousin. Viens au garage.")        # une réplique normale
_p("marco", "Cours, cousin!", 1)                          # PENDANT : accrochée à l'objectif n (0-based)
```

| Partie | Rôle | Règle |
|---|---|---|
| `appel` | le donneur t'appelle au combiné | une réplique, sauf un donneur rencontré en personne (m1) |
| `intro` | le donneur pose le contexte | 2 à 4 répliques |
| `pendant` | dite **quand un objectif commence** | **au moins une** (jugé) ; `_p(qui, texte, objectif)` |
| `client` | le client de m3 (réplique dite pendant une mission) | compte comme du « pendant » |
| `fin` | la récompense, dite par **quelqu'un qui est là** | 1 à 3 répliques |
| `echec` | on a raté | une réplique **au combiné** |

À partir de M16, **les dialogues sortent du paquet** : les répliques d'une
mission viennent par `/api/dialogue/<slug>` **quand le téléphone sonne** (avec un
ETag), et **les scènes voyagent avec elles**. Le catalogue (objectifs,
prérequis, `donne`) reste dans le paquet — c'est ce que le carnet et le GPS
lisent. Rien ne change pour **l'écriture** d'une mission : on écrit ici les
répliques comme avant, le routeur s'occupe du reste.

Règles jugées (`erreurs_de_mise_en_scene`) :

- `intro`, `fin`, `echec` **non vides** ;
- une réplique « pendant » (dont `client`) doit exister ;
- l'`objectif` d'une réplique `_p` doit pointer un objectif réel ;
- les répliques de chaque partie sont **toutes dites, et une seule fois**, par
  les plans `dire` de la scène correspondante (§ 6).

⚠️ **L'ordre des slugs de voix ne bouge jamais.** Le slug d'une réplique est
`<qui>-<mission>-<n>`, avec `n` compté dans l'ordre `appel, intro, client, fin,
echec, pendant`. Insérer une réplique au milieu renomme tout ce qui suit, et
des mp3 déjà générés deviendraient des 404. On **ajoute** à la fin, ou on
régénère (`scripts/audio_elevenlabs.py --refaire`).

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

Une scène est une **liste de plans**, typés dans `TYPES_PLANS`. `scenes.js` les
joue **sans connaître aucune scène par son nom**. Si une scène ne s'écrit pas
avec les types existants, on ajoute **un type** — jamais un
`if (slug === 'q07')`.

**Types de plan et clés** (`TYPES_PLANS` est la référence exacte) :

| Type | Rôle | Clés |
|---|---|---|
| `camera` | aller voir un lieu, le tenir, revenir | `vers`, `recul`, `duree`, `courbe`, `lissage` |
| `marcher` | un acteur va à un lieu à pied | `acteur`, `vers`, `duree`, `pres` |
| `conduire` | un char entre / part | `acteur`, `vehicule`, `couleur`, `vers`/`part`, `depuis`, `duree`, `courbe`, `fumee`, `portiere`, `retirer` |
| `geste` | un geste du sprite (montrer, donner, prendre, bras_croises, hausser, telephone) | `acteur`, `geste`, `duree`, `vers` |
| `entrer` / `sortir` | un acteur passe une porte | `acteur`, `dans`/`de`, `vers` |
| `coupe` | fondu vers un autre lieu puis retour | `vers`, `ferme`, `ouvre`, `tient` |
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

**Les acteurs nommables** : `joueur`, `donneur`, `vehicule`, `cible`, `fuyard`,
plus tout `slug` de `PERSONNAGES`. **Les formes de lieu** : un acteur,
`place:<acteur>`, `porte:<lieu>`, `ruelle:<lieu>`, `zone:<x>`, `chez:<personnage>`.

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

- `libere: "<district>"` — généralise `faubourg_libere` : le gang devient des
  passants, la zone s'efface de `carte.zones()` ;
- `calme: "<gang>"` — `hostile_toujours` et `hostile_si_arme` tombent ;
- `contact` — un numéro de plus au téléphone ;
- `vehicule`, `tenue`, `munitions`, `rabais` par comptoir ;
- `dette: -n`, `casier: -n`, `ami`/`ennemi`, `boulot`, `manchette`.

**`exige` et `ferme`** (M16) viennent compléter `prerequis` :

- `exige` — ce qu'il faut avoir **en plus** des prérequis : `argent_min`,
  `proprietes`, `liberes`, `dette`, `tenue`, `heure`. Un prérequis dit « après
  quoi » ; `exige` dit « dans quel état ».
- `ferme` — une mission qui en **ferme** une autre (un choix) : une mission
  fermée n'apparaît plus jamais, ni au téléphone ni au carnet.

Tout ça est jugé : `arme` doit exister, `propriete` doit exister.

---

## 8. La checklist de fin (ce que les tests vérifient)

Avant de dire « c'est fini », lancer :

```bash
uv run python scripts/verifier_missions.py --detail         # ce qui manque, en clair
uv run python scripts/verifier_table_des_jalons.py          # si une ligne de jalon a été ajoutée
uv run python -m pytest tests/test_missions.py tests/test_mise_en_scene.py tests/test_missions_en_scene_js.py -q
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

Et vérifier que `docs/carte.md` et `docs/plan.md` sont **mis à jour** (un
nouveau personnage → `docs/carte.md` § personnages ; une nouvelle mission →
ligne de jalon dans `docs/plan.md`).

### Ce que les juges refusent (récapitulatif)

- un objectif sans type, ou un type inconnu ;
- un `texte` d'objectif pas en MAJUSCULES ou trop long ;
- un `lieu`/`groupe`/`vehicule`/`arme`/`propriete` inconnu ;
- un `echec` hors de `ECHECS` (`mort`, `arrete`, `vehicule_detruit`, `chrono`,
  et depuis M16 `etoile`, `protege_mort`) ;
- un donneur sans position (`perso["ou"]` vide) ;
- `intro`/`fin`/`echec` sans répliques, ou pas de « pendant » ;
- une scène `intro` ou `fin` manquante ou vide ;
- un plan au type inconnu, aux clés inconnues, aux valeurs invalides ;
- un acteur ou un lieu inconnu dans un plan ;
- des répliques manquantes ou en double dans les plans `dire` ;
- une fin dite par un donneur absent, sans que personne n'aille le voir.

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

⚠️ **Ce document suit le moteur, pas l'inverse.** Les neuf types d'objectifs de
M16 (`suivre`, `proteger`, `pickpocket`, `payer`, `acheter`, `detruire`,
`sauter`, `eteindre`, `boulots`), les deux échecs (`etoile`, `protege_mort`),
les options transverses (`chrono_s`, `sans_etoile`, `sans_arme`, `contre`) et
l'extension `exige`/`ferme`/`donne` y figurent à leur place : un type n'est
**pas** livré tant qu'il n'a pas son juge de banc, et une mission qui s'en sert
avant ce juge n'est pas finie.