# Monter une mission — mode d'emploi pour une IA

Ce document explique **comment ajouter une mission de bout en bout** dans
Bandini, à l'intention d'une IA (ou d'un humain) qui découvre le projet. Il ne
remplace ni `docs/plan.md` (la vision) ni `docs/carte.md` (l'inventaire de la
ville) : il raconte la **recette**, pas le pourquoi.

> ⚠️ **Source de vérité : `app/missions.py`, rien d'autre.** C'est là que vivent
> les missions, leurs répliques, leurs scènes **et** leurs juges. Le navigateur
> ne décide rien : il joue les objectifs dans l'ordre et parle avec les mots
> d'ici. On ne touche jamais à `static/js/histoire.js` ou `scenes.js` pour
> *ajouter* une mission — on ne les touche que pour ajouter un **type** de plan
> (voir § 6), et alors on le fait pour tout le monde.

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

---

## 2. La structure d'une mission

```python
{
    "slug": "m7",                       # nom stable, cité partout ; m1…m97 existent déjà
    "titre": "Un titre court",          # ce qui s'affiche
    "donneur": "marco",                 # un slug de PERSONNAGES (§ 3)
    "prerequis": ["m5"],                # les missions DÉJÀ terminées ; [] pour la première
    "recompense": 400,                  # en dollars, > 0 (jugé)
    "phase": 1,                         # le palier de contenu (voir ci-dessous)
    "echec": ["mort", "arrete"],        # un sous-ensemble de ECHECS
    "exige": {"liberes": 3},            # FACULTATIF : condition d'« état » (pas encore lue au nav.)
    "donne": {"arme": "batte", "message": "LE BÂTON"},
    "objectifs": [ … ],                 # § 4
    "scenes": {"intro": [ … ], "fin": [ … ]},   # § 6
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

**Fichier cible** : `app/missions.py`, dans `CATALOGUE`, à la fin du bloc de
mission (après `m97` aujourd'hui). Le slug est l'ordre de nommage **M16** :
le tronc `m6` et `m97` se posent déjà sur `m5` ; les suivantes suivent.

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
| `tuer` | mettre KO `n` membres d'un `groupe` | `groupe`, `n`, `chef`, `arme`, `vie` |
| `survivre` | tenir | `secondes` |
| `course` | passer des points de passage, chrono | `points` |
| `courses` | `n` courses de taxi (klaxon = client) | `n` |
| `semer` | redescendre à 0 étoile | `etoiles` (posées au départ), `escorte` |
| `retourner` | revenir au donneur | — |

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
- `vie` — leurs points de vie.

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

Tout ça est jugé : `arme` doit exister, `propriete` doit exister.

---

## 8. La checklist de fin (ce que les tests vérifient)

Avant de dire « c'est fini », lancer :

```bash
uv run python scripts/verifier_table_des_jalons.py          # si une ligne de jalon a été ajoutée
uv run python -m pytest tests/test_missions.py tests/test_mise_en_scene.py tests/test_scenes_js.py -q
uv run python scripts/verifier_carte_du_plan.py             # SI un personnage a été ajouté (docs/carte.md !)
```

Et vérifier que `docs/carte.md` et `docs/plan.md` sont **mis à jour** (un
nouveau personnage → `docs/carte.md` § personnages ; une nouvelle mission →
ligne de jalon dans `docs/plan.md`).

### Ce que les juges refusent (récapitulatif)

- un objectif sans type, ou un type inconnu ;
- un `texte` d'objectif pas en MAJUSCULES ou trop long ;
- un `lieu`/`groupe`/`vehicule`/`arme`/`propriete` inconnu ;
- un `echec` hors de `ECHECS` (`mort`, `arrete`, `vehicule_detruit`, `chrono`) ;
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

Une mission est **trois choses** dans `app/missions.py` — ses objectifs, ses
dialogues et ses scènes — toutes trois jugées ; le donneur vit dans
`PERSONNAGES`, les scènes dans le vocabulaire de `TYPES_PLANS`, et le navigateur
ne décide rien.