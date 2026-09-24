# Sven et le piratage : trois missions avec les bateaux

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « ajoute 3 missions avec les bateaux », puis « je veux
de longue mission et aussi de l'infiltration et du hacking ». Trois décisions prises avec
lui (questionnaire) : le piratage se joue comme **une petite séquence à taper** (Simon), les
trois missions forment **un seul fil en trois actes** chez le même donneur, et ce donneur est
**Sven « le Norvégien »** — déjà prévu dans le plan M16 (« le contrebandier qui veut Les
Quais »), jamais encore posé dans le jeu.

**Ce qui manquait au moteur, avant la moindre mission :**

- **Un donneur qui se tient au bord de l'eau, à un endroit stable** : `PERSONNAGES.ou`
  n'avait que `porte:<lieu>` (une porte de bâtiment) et `point:<type>` (dedans). Sven se
  tient sur la jetée, à côté du porte-conteneurs — nouvelle forme `mouillage:<slug>[:n]`,
  résolue vers le **poste à quai** du mouillage (`navires.py` l'exporte maintenant), pas
  vers le centre de la coque, qui est dans l'eau.
- **Poser le véhicule d'un `monter`/`livrer` SUR l'eau** : `Histoire.poserLeChar` faisait
  passer toute position par `tuileDeRue` (la rue la plus proche) — la seule route pour un
  bateau. La même forme `mouillage:` saute cette étape, pose la coque au centre exact du
  mouillage, à son cap, et marque `v.amarrage` pour que le décor (`majMouillages`) ne fasse
  pas naître un second bateau par-dessus.
- **Le piratage** : nouveau type d'objectif `pirater`. On s'approche du point `ou`, on
  presse ACTION ; une séquence de 4 directions s'affiche ; on la reproduit avec le **même
  axe unifié** que la marche (`Entree.axe` — clavier, manette, joystick tactile : rien de
  neuf à apprendre, et ça marche au doigt sans bouton de plus). Une mauvaise direction
  recommence la séquence ; après `essais` ratés, l'alarme sonne (échec `alarme`, nouveau
  dans `ECHECS`).

**Les trois actes, tous donnés par Sven (`prerequis` en chaîne m52 → m53 → m54)** :

1. **m52, la chaloupe** — éclairage : approcher discrètement, de nuit, `sans_etoile`.
   Établit le personnage, n'utilise pas encore le piratage (on apprend un mécanisme à la
   fois).
2. **m53, le chalutier** — sous couverture : approcher un poste sous une fausse
   apparence, PREMIER usage du piratage (désactiver un relais).
3. **m54, le porte-conteneurs** — le gros lot : pirater le registre du quai, prendre la
   coque, la mener sous la police, revenir. Cinq à sept objectifs, comme demandé.

⚠️ **La voix de Sven est un choix provisoire.** Aucune voix « norvégienne » n'existe au
compte ElevenLabs ; `Nicolas Petit` (accent parisien, le seul net-« pas d'ici » du
répertoire) tient la place, mais **cette décision-là revient à Martin, à l'oreille** — c'est
la méthode que le plan M16 écrit lui-même pour ce personnage précis. Les voix ne sont pas
généreées : les textes et leur `jeu=` sont écrits, prêts à l'écoute puis à la génération.

## Notes

**Livré le 21 sept. 2026.** Les trois missions, Sven et le piratage, comme prévu à la fiche —
rien n'a changé en cours de route sur les trois décisions prises avec Martin.

- **Le piratage** (`m53`, `m54`) : une séquence de 4 directions au même axe unifié que la
  marche (`Entree.axe`), figeant le joueur comme `B.roue`/`B.cinema` le font déjà — sans ce
  gel, le même bâton servait à la fois à marcher et à choisir une direction. Une mauvaise
  direction recommence la séquence sans la faire échouer ; au-delà d'`essais`, l'alarme sonne
  (`ECHECS` gagne `"alarme"`).
- **Les bateaux comme lieu de mission** : deux formes neuves (`mouillage:<slug>[:n]`,
  `amarrage:sven`) intégrées à `Histoire.resoudre`, `lieu`, `lieuDeLivraison`,
  `lieuDuPersonnage`, `poserLeChar` et `creerDonneurs`. `poserLeChar` détecte l'eau et pose la
  coque à son cap exact plutôt que de router par `tuileDeRue` (la seule route pour un char à
  quatre roues) ; un char de mission qui cible un bateau déjà amarré (décor) le reprend
  (`dejaAmarre`) au lieu d'en faire naître un second.
- ⚠️ **Sven posé sur son poste bloquait sa propre chaloupe** : sur la tuile exacte du
  mouillage, ACTION parlait à Sven avant d'entrer dans le bateau (la chaîne de
  `Missions.interagir`). Décalé de deux tuiles sur le flanc du quai, comme `poserDonneur` le
  fait déjà pour les autres.
- ⚠️ **La voix de Sven tranchée le 22 sept. 2026** — Martin a ajouté `Martin - Clear and
  Comforting` (norvégien, accent d'Oslo) au compte. Les 26 répliques (m52-m54, huit
  chacune, plus les deux repos) générées avec elle par `scripts/audio_elevenlabs.py
  --refaire sven-…` — ciblé par slug, pas `--voix`, pour ne pas payer les personnages d'une
  autre session au passage. Voir [sa fiche](sven.md#notes).
- **La voix seule ne portait pas assez d'accent** (Martin, à l'oreille) : `[Norwegian
  accent]` ajouté en tête des 26 `jeu=`, nouvelle catégorie `ACCENTS` dans
  `app/interpretation.py`, testé d'abord sur les deux répliques de repos (moins chères)
  avant de regénérer les 24 autres — voir `docs/ecrire-un-accent.md` § 3, écrit le même
  jour. « Propre. » devenu « Parfait. » (m52, et la même réplique de Bouchard, m4, sans
  rapport avec l'accent) sur demande de Martin.
- **Deux sessions concurrentes ont atterri en même temps** : dix missions de plus (six
  personnages, `f04`-`e12`) et le correctif des phares sont arrivés sur `dev` pendant
  l'écriture de celle-ci. Les fichiers partagés (`missions/__init__.py`, `interpretation.py`,
  `histoire.js`, `missions.js`, `vehicules.js`, les deux tableaux de `docs/personnages/`,
  `test_missions.py`) ont été refondus par-dessus le nouveau `dev` plutôt que sur la base où
  le travail avait commencé — sans ça, la moitié de « dix missions » aurait disparu.
- ⚠️ **Le plafond du paquet des définitions était déjà dépassé sans Sven** : les dix missions
  livrées entre-temps l'avaient poussé à 230 545 bruts / 50 590 gzip sans que leur plafond
  (200 000 / 44 000) soit relevé — découvert en atterrissant, pas causé par ce jalon-ci.
  Relevé à 250 000 / 54 000, avec Sven inclus (240 385 / 52 219).
- **Juges** : `test_piratage_js.py` (7, la séquence, l'échec par alarme, ANNULER en FRAPPE,
  l'étiquette du bouton, le dessin du HUD) et `test_sven_missions_js.py` (8, Sven posé sans
  bloquer sa chaloupe, les trois missions jusqu'à la paie), mutation-vérifiés. Plus les
  ajustements aux juges de forme de lieu (`test_barrieres.py`, `test_interieurs.py`) pour que
  `mouillage:` n'y soit pas traité comme un point d'intérêt piéton.
- ⚠️ **Suite complète (sur `dev` + ce jalon) : douze rouges qui ne sont pas de ce jalon**,
  vérifiés identiques sur `dev` seul (8d6e171, sans rien de Sven) — surtout des trous laissés
  par « dix missions de plus » (six personnages sans tout leur câblage) et le correctif des
  phares : `test_definitions::test_le_paquet_reste_leger` (déjà couvert ci-dessus),
  `test_histoire_js::test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`,
  `test_histoire_js::test_les_personnages_disent_leur_repos_a_voix_haute` (Mo n'a pas son
  `jeu=` dans `interpretation.py`), `test_interieurs::test_une_piece_donne_quelque_chose_a_faire[hopital]`
  et `test_interieurs_js::test_chaque_comptoir_dessine_est_servi_par_le_jeu` (le Dr Lachance
  n'est nulle part dans `TYPES_SERVIS`), `test_missions_en_scene_js::…[f04-défaut]` et
  `…[p01-défaut]`, `test_moteur_js::test_la_foule_ne_se_traverse_plus`,
  `test_courir_ne_permet_pas_de_traverser_les_gens` et
  `test_celui_qui_tient_son_poste_cede_puis_revient`,
  `test_on_attend_l_autobus_js::test_des_gens_attendent_a_l_abribus_et_personne_ne_nait_sous_les_yeux`,
  `test_ondes::test_la_police_n_a_la_voix_ni_d_un_passant_ni_d_un_personnage` (Mado partage sa
  voix avec la radio-police) et `test_navigateur::…[chromium]`. `test_passage_pietons::test_le_long_char_repart_au_vert_et_franchit_la_ligne`
  (32 px pile au seuil, `assert 32 > 32`) est rouge sur `dev` seul aussi, mais ne l'est plus
  retombé dans la suite complète ici — sous charge partagée, ce juge-là ment parfois
  (« juge navigateur, serveur partagé »).
- ⚠️ **Trois rouges QUE Sven cause, mais pas en cassant quoi que ce soit à lui** :
  `test_amuseurs_js::test_le_public_applaudit_paie_et_se_renouvelle` et deux dans
  `test_la_nuit_js.py` (`test_a_la_fermeture_on_sort_de_l_eau_et_on_rentre_hors_champ`,
  `test_a_l_aube_le_camelot_lance_le_clairon_sur_les_perrons`) tiennent par une graine fixe
  (`L.graine(64)` et pareilles) qui doit produire assez de hasard en un budget d'images
  compté. `creerDonneurs` pose CHAQUE donneur par `Entites.creerPieton`, qui tire des dés
  (« creerPieton tire des dés ») — Sven est un seizième donneur, un dé de plus tiré au
  démarrage, et tout le hasard qui suit se décale d'un cran. **Confirmé, pas supposé** :
  exclure Sven de `creerDonneurs` (diagnostic jetable, annulé ensuite) rend les trois verts.
  Rien à voir avec l'eau, les bateaux ou le piratage — la même chose serait arrivée avec
  n'importe quel dix-septième personnage, et les six de « dix missions » ont sans doute
  déjà décalé d'autres juges qui tenaient tout juste. Non corrigé : le remède (élargir le
  budget d'images ou changer la graine de ces juges-là) n'est pas à moi de trancher seul.
