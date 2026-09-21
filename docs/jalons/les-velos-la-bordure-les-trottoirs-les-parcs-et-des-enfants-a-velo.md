# Les vélos : la bordure, les trottoirs, les parcs — et des enfants à vélo

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « les vélos peuvent passer dans les parcs, les
trottoirs, et restent souvent sur la bordure de la route, sauf pour virage à gauche. Je veux
aussi des enfants à vélo, seulement sur trottoir, casque, parc. » Aujourd'hui le vélo du
trafic roule au MILIEU de sa voie comme une auto, ne quitte jamais les flèches, et il n'y a
aucun enfant à vélo.

**Vague 1 — la bordure.** Le vélo du trafic roule collé au trottoir (décalé à droite dans la
voie de droite, jamais au milieu) ; sur une rue à deux voies par sens il garde celle du
trottoir et ne dépasse pas. Avant un virage à gauche il se range à gauche, près de la ligne
centrale, et tourne de là.

- ⚠️ L'intention de tourner se lit AVANT la ligne d'arrêt : elle se tire à l'empreinte (le
  vélo, le croisement), pas au dé — un dé de plus décale tout ce qui naît après.

**Vague 2 — le trottoir et le parc.** De temps en temps (à l'empreinte), un vélo monte sur
le trottoir — coincé derrière un char arrêté, ou le long d'un parc — et traverse le parc par
ses allées, au pas, en sonnant aux passants ; il redescend sur la chaussée par la voie la
plus proche.

- ⚠️ Au pas et en cédant : un vélo qui fauche les piétons du trottoir n'est plus un
  cycliste, c'est une arme.

**Vague 3 — les enfants à vélo.** Un petit vélo et un enfant casqué dessus ; trottoirs et
parcs SEULEMENT (jamais la chaussée, pas même les passages), le jour, dans les quartiers où
il y a des cours et des parcs ; intouchable comme l'enfant à pied.

- ⚠️ Un corps à lui (le casque se voit de loin) et pas un échange de palette.

## Notes

Livré le 21 sept. 2026, les trois vagues d'un coup. Le vélo du trafic reste un char **sur des
rails** : on ne touche qu'aux cibles qu'on lui donne (`Vehicules.prochaineCible`, qui enveloppe
maintenant `cibleDeLaVoie`). Les réglages sont dans `vehicules.TRAFIC["velo"]`, l'enfant dans
`pietons.CATALOGUE` (`enfant_velo`) et `pietons.ENFANTS_A_VELO`.

**La bordure.** Chaque cible du vélo est tassée de `bord_px` (4) vers le trottoir
(`aLaBordure`) ; il naît déjà tassé. Sur une rue à deux voies par sens, il revient dans celle du
trottoir dès qu'elle est libre (`voieDuVelo`, les gardes du déport).

- ⚠️ **Sur place, il garde son côté.** Une cible à moins d'un pixel devant est le point d'arrêt
  à la ligne : la laisser au milieu de la voie ramenait le vélo au milieu, trois pixels en crabe,
  le temps du rouge. Elle se pose sur sa ligne à lui.
- ⚠️ La fiche disait « ne dépasse pas » : il se **déporte** encore autour d'un obstacle planté,
  comme tout le trafic (`changerDeVoie`). Bloqué pour toujours derrière une panne, il serait pire
  qu'un vélo qui contourne ; il revient à la bordure dès que la voie du trottoir est libre.

**Le virage à gauche.** À `virage_tuiles` (5) de la ligne d'arrêt, le cycliste lit son
**intention** (`intentionDuVelo`) : les mêmes parts que le reste du trafic (55 % tout droit,
23 % à droite, 22 % à gauche), d'abord parmi les bras qui existent. S'il va à gauche, il se range
à gauche (la voie du milieu s'il y en a une, contre la ligne sinon), attend là, et tourne ; la
boîte prend son intention au lieu de tirer la sortie.

- ⚠️ **Aucun dé** : l'intention se lit à l'empreinte du cycliste et du croisement (`hash2`), la
  même à chaque lecture. Le vélo ne tire donc plus sa sortie au dé dans la boîte — c'est un dé de
  MOINS dans la file du jeu quand un vélo traverse un croisement.

**Le trottoir et le parc.** Trois façons de monter, toutes à l'empreinte, depuis la voie du bord
et jamais s'il va tourner à gauche (`monterSurLeTrottoir`) : le long d'un parc (`parc_chance`
par tuile longée) il le **traverse par ses allées** ; au hasard (`trottoir_chance`) il fait un
**bout de trottoir** de 4 à 10 tuiles ; **coincé** derrière un char arrêté (`coince_images`), un
cycliste sur deux (`coince_part`) monte et le longe. Hors de la rue il va **au pas**
(`trottoir_vitesse` 0,8 < `renverse_vitesse_min` 1,2), s'arrête derrière un passant et **sonne**
(`sonnette_images`), puis redescend dans la voie quand elle est libre (`attente_images` au plus).

- ⚠️ Ce qu'il foule hors de la rue : le trottoir et l'**allée** de parc (`g`), jamais la pelouse
  (on y sème arbres, bancs, buissons), jamais l'abord (le mobilier s'y range), jamais le coin
  d'un croisement (poteaux, traverses), rien où un décor est posé (`roulableHorsRue`) — sur des
  rails, il passerait au travers.
- ⚠️ La traversée est un Dijkstra à seaux plafonné (`noeuds_max`), l'allée coûtant moins que le
  trottoir : il passe PAR le parc plutôt qu'autour. Il **redescend à la sortie de l'allée**
  (`trottoir === 1`) : la première version le faisait longer le trottoir cinq tuiles à rebours
  puis repartir dans l'autre sens. Le chemin est lissé (`lisser`) : de tuile en tuile, il
  zigzaguait en travers de la place du parc.
- ⚠️ La trace du trafic ne le compte pas hors voie (`horsRue`), le chien de garde lui rend la
  voie (et oublie le trottoir) s'il le recale, et `test_le_trafic_reste_dans_sa_voie` l'écarte
  explicitement — il y passait, mais par chance de graine.

**Les enfants à vélo.** Des passants (`metier: 'cycliste'`, `frequence` 0), sur un corps à eux :
`SPRITES.enfant_velo`, 16 × 15, le casque (`e`) et le cadre (`v`) échangés d'un enfant à l'autre,
deux images par face pour les pédales. Deux au plus dans la bulle (`combien`), le jour
(`heures` 0,33 → 0,8), aux Érables, à La Pointe et au Faubourg ; ils naissent hors champ sur un
trottoir ou dans un parc, casque, cadre et chandail lus à l'empreinte de la tuile, et
`creerPieton` joue avec un dé **prêté** (`sansLeDe`, le même geste que les gens de l'abribus).
Intouchables comme l'enfant à pied, `temoin` 0.

- ⚠️ **Toute la rue est un mur pour lui, la traverse comprise** (`roulableEnfant` : trottoir,
  abord, pelouse, allée). Trois trous bouchés en chemin : il coupait le coin d'un îlot **en
  diagonale** en détalant (les deux axes, pris seuls, tombaient sur du trottoir) ; une fois sur
  la traverse, rien ne l'en faisait **ressortir** (il vise maintenant le bord le plus proche
  d'une tuile roulable, pas son centre — celui du coin l'envoyait contre le poteau du feu) ; et
  **`demeler`** — la foule qui attend au coin — le poussait d'un pixel sur les bandes. Un pas
  qui le mettrait sur la rue est annulé, dans sa routine comme dans la foule.

Juges : `tests/test_velos_js.py` (quatorze). Mutations, toutes rouges : sans la bordure, jamais
à gauche, l'intention au dé, le trottoir à pleine vitesse, la trace qui crie, la pelouse
permise, pas de descente à la sortie de l'allée, la traverse permise à l'enfant, la foule qui le
pousse, la naissance au dé, les enfants la nuit.

**Trois juges voisins tenaient par la graine**, et la nouvelle chronologie du trafic les a fait
basculer (le vélo ne tire plus sa sortie au dé, il roule ailleurs dans sa voie). Chacun tombait
déjà sur la base (`b6ffdc5`, sans ce jalon) dès qu'on bougeait le hasard — douze graines, ou un à
trois tirages de décalage — ; ils sont resserrés sur leur règle :

- `test_passage_pietons::test_la_ville_n_a_plus_une_seule_attente_sur_une_traverse` (base
  décalée : 3 sur 36) : un **camion surpris** par le feu, déjà dans sa distance de freinage,
  s'arrête où il est — la règle de `pointDArret` (« jamais derrière soi »). Le juge recalcule
  le point d'arrêt de la règle et ne compte que les chars arrêtés dessus ou avant ; remettre
  l'ancien défaut (le centre sur la ligne) le rougit toujours.
- `test_police_js::test_en_courant_on_ne_seme_pas_un_agent_mais_en_sprintant_on_gagne_du_terrain`
  (base : 4 graines sur 12) : la ligne droite est une voie, un char passait entre le joueur et
  l'agent. La rue est vidée de ses chars : le juge mesure la course à pied.
- `test_moteur_js::test_la_bagarre_tient_le_budget` (base : graine 6) : une **mère née à
  vingt-sept flâneurs avec son petit** en fait vingt-neuf ; le budget se décide à la naissance.
  Le petit qui suit sa mère ne compte pas à part.

**Et un bogue d'avant, trouvé en chemin par le singe** (`test_le_singe_ne_casse_rien[1]`, sur
`82b47c5` + ce jalon) : un char garé qui chevauche le joueur au ras du bord nord le **poussait
hors de la carte** (y = −3,5, dans le « mur » du dehors) — `heurterPietons` repoussait sans
borne. Reproduit sur la base sans ce jalon ; la poussée passe maintenant par
`Entites.dansLaCarte`, et `test_un_char_ne_pousse_personne_hors_de_la_carte` le tient.

Rebâti sur `82b47c5` (« le trafic ne rate plus ses virages dans les coins en L ») : l'intention
du cycliste prend le même repli que le reste du trafic, « tout droit, sinon à gauche ».

Suite complète sur `c59bf6d` + ce jalon : 3 684 verts, 2 rouges —
`test_histoire_js::test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler` et
`test_moteur_js::test_la_foule_ne_se_traverse_plus`, **rouges aussi sur `c59bf6d` sans lui**.

- ⚠️ Une idée laissée en chemin, pas une dette : **au jaune, un char déjà engagé devrait
  passer** au lieu de s'arrêter le nez sur les bandes. C'est ce que fait le vrai code de la
  route, et c'est la seule source des attentes « surprises » qui restent.
