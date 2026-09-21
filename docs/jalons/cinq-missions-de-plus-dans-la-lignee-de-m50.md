# Cinq missions de plus, dans la lignée de m50

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

demande de Martin (21 sept. 2026) : « crée-moi 5 nouvelles missions dans la lignée ».

_Ce que ça donne :_ cinq missions écrites à la main, chacune avec ses objectifs, ses répliques à
chaque temps, ses scènes et le jeu de chaque voix — le catalogue passe de huit à treize. Elles
suivent **m50** (_Le Cargo de Minuit_) : une faveur du Faubourg, un donneur qui parle québécois, un
lieu qu'on connaît, et rien qui demande un moteur neuf.

⚠️ **Deux règles ont décidé du choix** :

- **Que des donneurs qui existent** (Marco, Ti-Paul, Lulu, Raymonde, Bouchard) : aucune voix à
  auditionner, aucun personnage à poser (`docs/carte.md` ne bouge pas), et deux personnages de
  même voix ne se croisent pas (Marco et Ti-Paul partagent « Québec Tremblay » : jamais dans le
  même dialogue).
- **Que des types d'objectifs éprouvés** : `aller`, `monter`, `livrer`, `tuer`, `semer`, `parler`,
  `retourner`. Les neuf types de M16 (`suivre`, `proteger`, `pickpocket`…) attendent encore leur
  juge de banc, et `course` n'est pas joué en mission : une mission qui s'en sert avant n'est pas
  finie. C'est pourquoi la moitié de l'arc F du plan (`f06`, `f07`, `f09`) n'est pas dans ce lot.

| Slug | Titre | Donneur | Après | Ce qu'on fait |
|---|---|---|---|---|
| `f01` | Les Cravates reviennent | Marco | m50 | de nuit au garage : repousser trois Cravates qui arrivent de loin, coucher leur chef, revenir |
| `e01` | Les drifts de Ti-Paul | Ti-Paul | m6 | de nuit au dépanneur : trois Chevreuils, les poings nus, qui viennent se servir en bière |
| `q02` | Le poisson du vendredi | Lulu | e01 | le camion de poisson dort dans une ruelle des Quais : le livrer au casse-croûte, sans bosse |
| `s03` | La paie de la Prévost | Raymonde | q02 | voler le camion de paie près de l'hôtel, semer 2★, le livrer au bar de Josée (qui garde la caisse) |
| `m51` | La tournée du sergent | Bouchard | e01, q02 | serrer la main de trois commerçants (Thibodeau, Lulu, Ti-Paul) pour « la cotisation », rapporter les enveloppes |

⚠️ **Les prérequis font une chaîne exprès.** Le téléphone sonne pour la première mission
disponible dont l'appel n'a pas été dit, toutes les dix secondes (`DELAI_APPEL`) : cinq missions
ouvertes d'un coup à la fin de m6, c'est cinq appels de suite. Elles s'ouvrent donc dans l'ordre où
m6 présente les gens (Ti-Paul, Lulu, Raymonde), et Marco a sa suite de m50. Le « un appel par
demi-journée » de M16 les trierait mieux ; il n'est pas livré.

⚠️ **Les slugs suivent le plan de M16** quand la mission y est (`e01`, `q02`, `s03`, `f01`), avec
ce qui change : `f01` est donnée par Marco au garage (Ti-Guy n'a plus de place après m1) et n'a pas
d'extincteur (`eteindre` attend son juge) ; `q02` livre un camion, pas trois ; `s03` n'a pas de
gardiens, et elle finit au **bar de Josée**, pas à l'usine (voir les Notes : la cour ferme la nuit). `m51` n'est pas au plan : c'est un nom hors catalogue, comme m50.

⚠️ **Les voix ne sont pas générées** : ElevenLabs se paie au caractère, et Martin n'a pas encore
écouté un ton neuf. Chaque réplique a son jeu, collé à elle dans le fichier de la mission (`jeu=` ; un
juge l'exige) ; une réplique dont le fichier manque s'affiche sans voix. La commande est dans les Notes.

## Notes

⚠️ **Livré le 21 sept. 2026** — les cinq missions se jouent de l'appel à la prime
(`tests/test_cinq_missions_js.py`, au bouton, sous Node) ; leurs **38 voix** sont venues le même jour
(voir « Les 38 voix », plus bas).

**Ce qui est livré**

- Les cinq fichiers `app/missions/{f01,e01,q02,s03,m51}.py`, inscrits dans `CATALOGUE` **dans l'ordre du
  téléphone** (e01, q02, s03, m51, et f01 après m50). Le catalogue passe de 8 à 13 missions.
- **Le jeu des voix vit dans le fichier de la mission** (demande de Martin, même jour : « si on veut que
  les missions soient lues indépendantes, les interprétations devraient aussi être dans le fichier de
  mission »). `_l`, `_p`, `_r`, `_a` prennent un `jeu=`, collé à la réplique ; les **104 jeux** des huit
  missions d'avant ont déménagé de `interpretation.py` (aucun mot changé : les 136 entrées d'avant sont
  identiques une à une), et les 38 des cinq nouvelles y sont nées. `interpretation.JEU` **rassemble** le
  tout (`missions.repliques()` porte le `jeu`), et `missions.pour_le_navigateur()` le retire du paquet.
  Un effet de bord heureux : une réplique insérée n'emporte plus le jeu de sa voisine — seul le nom du
  mp3 suit encore la place. Docs ajustées : `comment-monter-les-missions.md` § 5, `jeu-d-acteur.md`
  § 3.9, `missions-en-scene.md`, `ecrire-drole.md`, `reprendre-le-travail.md`, `architecture.md`, et le
  squelette de `verifier_missions.py --squelette`.
- **Trois juges qui nommaient des missions en dur** ont été rendus génériques (le catalogue en fournit la
  liste) : les voix par mission (`test_audio.py`), les accueils de m6 (`test_mise_en_scene.py`), et
  l'aide `faites()` du banc de scènes — un donneur donne la **première** mission disponible de sa liste
  (`disponibleDe`), et f01 passait devant m97 chez Marco.
- **Deux juges neufs** : le jeu suit sa réplique quand on en insère une, et le jeu ne part pas au navigateur.

**Ce que le banc a montré** (et que le papier n'aurait pas dit)

- ⚠️ Le `aller` du dépanneur (rayon 4) **ne s'accomplissait pas** pour qui vient de parler à Ti-Paul :
  il se tient à 48 px du point, le joueur à 16 px de lui — 64,03 px pour un rayon de 64. On était AU
  dépanneur et il fallait un pas de plus. Rayon 6 pour e01 et f01.
- Les hommes de f01 et e01 naissent à 100–260 px, courent sur le joueur, et le chef de f01 sort quand les
  trois sont tombés (bâton, 160 PV). Si l'on se bat **à la porte** du donneur, `retourner` s'accomplit dans
  la même image que le dernier K.-O. : c'est voulu, on n'a pas à marcher pour rien.
- ⚠️ **`s03` ne finit pas à l'usine — un juge de la ville l'a refusé** (`test_barrieres.py`, rouge à la
  suite complète, pas au banc de la mission : celui-là téléportait le camion). La cour de l'usine est
  fermée la nuit par une chaîne (`carte.BARRIERES`, `condition: heure jour`, on la défonce à 1★), et la
  règle est écrite : « un lieu enfermé par une barrière d'heure, on le tolère, **sauf pour un lieu de
  mission** ». La paie va donc au **bar de Josée**, et Raymonde le dit (« mon usine, elle, est surveillée »).
  `usine` est aujourd'hui le seul lieu enfermé : aucun objectif `aller`/`livrer` ne peut le nommer.
- q02 paie 375 $ sans bosse (250 + la moitié), 250 avec ; s03 paie 450 $ et pose 2★ dès qu'on monte dans le
  camion ; m51 fait dire leur mot à Thibodeau, Lulu et Ti-Paul, chacun avec sa voix demandée.

**Ce qui reste — les voix** : 38 répliques, **≈ 3 750 caractères** facturés (le texte joué, balises
comprises). Rien n'est généré : une réplique dont le fichier manque s'affiche sans voix. Dans l'ordre du
guide (`docs/jeu-d-acteur.md` § 3.10) :

```bash
uv run python scripts/audio_elevenlabs.py --essai                      # ce qui serait généré, sans rien dépenser
uv run python scripts/audio_elevenlabs.py --refaire bouchard-m51-5     # une ligne clé — Martin écoute
uv run python scripts/audio_elevenlabs.py --voix                       # puis le reste
```

⚠️ **À écouter d'abord : `bouchard-m51-5` et `bouchard-m51-3`** — c'est la seule balise que le jeu n'a
**jamais** jouée (`[deadpan]`, dans la liste des tons depuis le début). Ensuite `raymonde-s03-3` (Nadine,
rauque : elle ne crie jamais, elle est plus dure posée) et `tipaul-e01-1` (Ti-Paul a la voix de Marco, plus
vif : ils ne sont jamais dans le même dialogue). Les scènes de m51 (et la fin de e01, qui nomme Lulu) sont
**à recaler sur les voix une fois entendues** (`ffprobe` + `silencedetect`, `docs/jeu-d-acteur.md`) : elles
n'utilisent que des `dire` qui se retiennent, mais aucun juge n'écoute.

**Le paquet** : les définitions passent de 39 526 à 41 886 octets gzip — **470 octets par mission**, tout
le catalogue voyageant dans le paquet. Plafond 40 000 → 44 000 (`test_definitions.py`, avec sa mesure) :
de la place pour quatre missions de plus. Le vrai remède reste `/api/dialogue/<slug>` (M16, tranche 1).

**Décisions de scénario à valider par Martin** : m51 est un sergent corrompu qui envoie le joueur ramasser
« la cotisation de la Fraternité » chez trois commerçants (dans la veine de m4) ; s03 est un vol de la paie
de Prévost au profit du syndicat de Raymonde, gardée au bar de Josée (le plan la voulait après q03, qui
n'existe pas). Aucune n'a
de nouveau personnage : `docs/carte.md` ne bouge pas.

### Les 38 voix (21 sept. 2026, livrées)

Martin : « il manque des voix pour les dernières missions créées ». Générées d'un coup, sans l'essai
d'une ligne clé que la note ci-dessus prévoyait : c'est lui qui les a demandées, et ça coûte peu
(≈ 3 800 crédits, 31 795 restants avant ; une ligne à refaire, ≈ 100). Masters gardés dans
`~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16/` : toute retouche de finition est gratuite
(`--refinir --masters`). `thibodeau-m51-8` (Julia) est passée par l'isolateur (`comment=voix isolee`).

- **Mesurées, pas écoutées** : −19,3 à −20,1 LUFS, pics ≤ −1,6 dBFS, 2,7 à 9,3 s. Trois fins muettes
  d'environ 1 s au lieu de 0,35 s (`marco-f01-3`, `marco-f01-4`, `raymonde-s03-7`), comme `marco-m3-2`,
  `bouchard-m4-4` ou `marco-m97-1` avant elles : la finition, pas la génération.
- **À écouter d'abord**, comme prévu : `bouchard-m51-3` et `bouchard-m51-5` (`[deadpan]`, jamais joué
  avant), `raymonde-s03-3` (Nadine), `tipaul-e01-1` (Ti-Paul sur la voix de Marco).
- ⚠️ **La voix de Lulu se faisait couper dans l'intro de q02.** q02 prenait l'intro « dedans » du
  défaut : sa première réplique (`lulu-q02-2`, 9,3 s = 559 images) jouait en `ensemble` sous une coupe de
  230 images, et la seconde la coupait en plein « le chauffeur s'est pogné la main ». q02 écrit
  maintenant son intro dans la forme de m51 : la coupe part `ensemble` AVEC la réplique, et c'est le
  `dire` (pas `ensemble`) qui retient la scène jusqu'au bout de la voix. La coupe tient 240 images :
  elle montre le camion pendant « dans une ruelle, plein de morue » et revient à la cantine juste avant
  la blague (4,1 s).
- **Un juge pour toutes les scènes** : `test_aucune_voix_de_scene_n_est_coupee_par_la_suivante`
  (`test_missions_en_scene_js.py`) joue chaque intro et chaque fin au banc, chaque voix « jouant » le
  temps de son mp3 plus 30 images de chargement, et refuse toute voix interrompue avant sa fin. Rouge
  sur q02 avant la correction (360 images). Et q02 rejoint le juge « la coupe filme ce qu'elle pose »
  (le camion est à l'écran pendant toute la coupe).
- ⚠️ **Quatre scènes coupaient déjà leurs voix** (pas de ce passage, marquées `xfail` strict dans
  `DEJA_COUPEES`) : l'intro de **m4** (Bouchard) et de **m5** (Josée), qui prennent l'intro « dedans » du
  défaut, celle de **m97** (même forme, écrite), et la fin de **m3** (Marco perd presque toute sa
  première réplique : `dire` `ensemble` devant un geste d'une seconde). Le jour où on les recale, le juge
  passe au vert et `strict` demande de les retirer de la liste. Le remède du défaut n'est pas trivial :
  retenir par la voix plutôt que par la coupe ferait parler la seconde réplique hors champ quand la
  première est courte.
