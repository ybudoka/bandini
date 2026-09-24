# La nuit a ses habitudes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « la nuit, personne ne se baigne, plus de véhicules
stationnés, et donne-moi d'autres idées pour la nuit » — puis, devant la liste : « je veux
toutes les idées ». « Plus de véhicules stationnés » veut dire **davantage, et ailleurs**
(tranché avec Martin) : c'est la dette que [la nuit ne se vide pas](la-nuit-ne-se-vide-pas.md)
avait écrite d'avance (« plus dans les entrées des Érables la nuit, moins sur les rues
commerçantes »).

Ce que la nuit fait déjà, et qu'on ne refait pas : les feux qui clignotent (`TRAFIC.clignotant_*`),
les kiosques fermés, la Brume, les cônes de vision raccourcis, l'équipe du chantier qui rentre,
les autobus plus rares, le quai du cargo ouvert, le rythme des districts.

**Vague 1 — les deux demandes.** Les baigneurs ne naissent que le jour, et ceux qui restent à la
brunante rentrent **hors de l'écran**. Les chars garés suivent l'heure : plus nombreux la nuit, et
d'abord dans les entrées de cour et les rues à logements ; le jour, d'abord devant les commerces.

- ⚠️ L'heure de la plage vit dans `pietons.PLAGE`, **pas** sur l'archétype `enfant` : toute la
  ville s'en sert, et les enfants disparaîtraient de partout la nuit.
- ⚠️ `stationnes_max` reste un entier de 0 à 20 (un juge le tient) : la nuit a sa propre clé.
- ⚠️ Chaque naissance évitée décale tous les dés qui suivent (`Vehicules.peupler`) : choisir la
  place ne tire **aucun dé de plus**.

**Vague 2 — ce qu'on voit.** Les **phares** éclairent devant les chars qui roulent (deux faisceaux
dans le tampon de lumière, des feux arrière rouges). Les **fenêtres** des immeubles à logements
s'allument à la brunante et s'éteignent une à une vers 2 h. En quartier pauvre, **un lampadaire
sur quelques-uns est mort** ou grésille : des poches d'ombre.

- ⚠️ Le budget : 25 lampes par image. Les phares se comptent avec les lampadaires.
- ⚠️ Quelle fenêtre, quel lampadaire : une empreinte de sa position, **jamais un dé**, et rien ne
  bouge dans la ville (`carte.generer` identique).

**Vague 3 — qui est dehors.** Le **last call** : à la fermeture des bars, une grappe de fêtards
titubants sort des devantures de nuit, chante et cherche la chicane. Le **camelot du _Clairon_**
passe à l'aube et lance le journal sur les perrons. La nuit, une poubelle fouillée sort un **raton
laveur** au lieu du rat, et les goélands dorment.

**Vague 4 — ce que ça change au jeu.** Les **comptoirs ferment la nuit**, sauf le dépanneur et le
bar (seuls les kiosques ont des heures aujourd'hui : `Missions.ouvert`). L'**arroseuse de nuit** : un
camion de la ville sur une boucle tracée comme celle des éboueurs, et l'asphalte mouillé derrière
elle qui glisse un moment.

- ⚠️ Chaque vague est jouable, testée, et ses juges **rougissent sans leur règle** (mutations).

## Notes

✅ **Livré** (21 sept. 2026), les quatre vagues.

- ⚠️ **Deux idées de la fiche existaient déjà en partie** : une fenêtre de logement sur trois
  s'allumait déjà à la brunante (la lampe `fenetre` des résidences) — mais toute la nuit, toutes
  ensemble ; et un lampadaire sur trois était déjà **mort** en quartier pauvre (`mobilier.eclairer`,
  3e vague des quartiers). Ce qui est livré : chaque fenêtre a son **coucher** (22 h → 3 h) et son
  **lever** (5 h → 6 h 15), et une part des lampadaires pauvres qui marchent encore **grésille**.
- ⚠️ **Le jour ne change pas d'un dé** — c'est ce qui a gardé la suite à sa place : le banc joue à
  8 h 24. Les chars garés du jour gardent leur tirage (un juge compare les places ET l'état du dé) ;
  les comptoirs ouvrent tous à 8 h au plus tard ; tout ce que la nuit fait naître lit l'heure avant
  de tirer. Ce qui se décide « au hasard » la nuit (quelle fenêtre, quel lampadaire, combien de
  fêtards, ce qu'ils chantent, qui cogne, la gerbe de l'arroseuse) se lit **à l'empreinte**
  (`hash2`), jamais au dé du jeu.
- ⚠️ **Les chars garés de nuit : un tirage à part.** Première version : le tirage du jour, qui
  refusait les cases hors d'une rue à logements pendant ses premiers essais. Or une tuile tirée au
  hasard n'est une case qu'une fois sur dix — ça faisait **moins** de chars la nuit (0 contre 1 en
  4 000 images, le juge l'a vu). La nuit **choisit parmi les cases libres** de l'anneau
  (`placeDeNuit`), d'abord en rue résidentielle, une fois sur sept devant un commerce. La ville a 581
  cases : 515 en zone industrielle, **48 en rue résidentielle** (les entrées des Érables), 18 devant
  des commerces — c'est aux Érables que la nuit se voit.
- ⚠️ **Le crieur naissait à 2 h du matin** : `naitreLesSortes` ne lisait pas les heures, seul
  l'homme-sandwich le faisait. Corrigé pour toutes les sortes, et ⚠️ **les heures se lisent sur
  l'ARCHÉTYPE** — une sorte ne les porte pas sur elle (le premier juge l'a montré : le crieur ne
  rentrait jamais). Passé ses heures, une sorte rentre **hors de l'écran**.
- **La plage** ferme de 19 h 12 à 7 h 12 (`PLAGE.heures`, pas sur l'archétype `enfant` que toute la
  ville partage). ⚠️ Celui qui barbote vise **six pixels au-delà** du centre de la tuile sèche : `cap`
  s'arrête à 12 px de son but, et visé au centre il restait les pieds dans l'eau.
- **Les phares** : ramassés en dessinant (`allumerLesPhares`, comme les feux), un faisceau **étiré**
  dans l'axe du char (`Base.fin` sait maintenant étirer un halo : `a`, `e`) et un feu arrière ; deux
  places gardées pour le char du joueur. Le plafond de lampes passe de 50 à 62 (le juge du plafond
  compte maintenant les phares).
- **Le last call** : les bars sont les devantures de la famille « nuit » sauf À LOUER (dix dans la
  ville, `nuit.bars`), la grappe naît **dans la porte** qui s'ouvre, une fois par bar et par nuit ;
  ce sont des ivrognes (leur routine) qui chantent des airs du folklore au lieu d'insulter, et celui
  qu'on frôle se retourne — un sur trois passe aux poings (`attaque_joueur`).
- **Le camelot** : le corps du crieur, repeint, et la routine du facteur sans les portes. ⚠️ Deux
  défauts vus au banc : il visait un perron **derrière un mur** (`cap` marche en ligne droite — dix
  secondes le nez contre la cour ; il ne vise plus que ce qu'il voit, `ligneLibre`), et un perron
  raté se **raye** de la tournée au lieu d'être revisé sans fin. Le journal est un décalque qui porte
  son jour ; rentré à 9 h, hors champ.
- **Le raton** : une bête de ruelle la nuit (comme le chat), et la fouille de nuit change le rat de
  la table en raton qui **pèse double** — toujours UN `B.rng()`. Il sort de la poubelle et file à
  l'opposé du joueur (`fairePartirUnRaton`, `libre` : il longe les murs). La queue annelée en anneaux
  de deux sur deux : à un pixel, on ne lisait pas les anneaux (aperçu ×10).
- **Les comptoirs** : `comptoirFerme` sert l'invite ET le menu (« FERMÉ — OUVRE À 7 H »). Le
  dépanneur vend sous la famille « bouffe » : c'est la **pièce** qui le garde ouvert.
- **L'arroseuse** : la tournée de la charrue (même voirie), le camion-citerne et le gyrophare de la
  charrue. ⚠️ **Assombrir un asphalte déjà noir ne se voyait pas** (capture) : ce qui dit « mouillé »,
  ce sont les **reflets** — un voile bleuté et des miroitements en tirets. Rues mouillées oubliées à
  chaque nouvelle partie, comme le last call.
- **Deux fichiers de juges** : `test_la_nuit.py` (10) et `test_la_nuit_js.py` (18). ⚠️ **52
  mutations**, une par règle, **toutes rouges** — après avoir durci huit juges qui ne mordaient pas au
  premier passage : deux appelaient la fonction au lieu de passer par le jeu (le last call, les
  journaux rentrés), un ne regardait pas le deuxième frôlement, un tirait 0,999 (le rat avec ou sans
  poids — à 0,9, le jour rend un reste de poutine et la nuit un raton), deux n'avaient pas de perron
  caché, un n'avait qu'un sous-cas de lever de fenêtre, et un posait la caméra assez loin pour que
  « hors champ » soit gratuit.
- **Regardé dans Chromium** : les phares, les fenêtres à 21 h et à 3 h 30, le lampadaire allumé puis
  noir, la grappe devant Le Brouillard qui chante, le raton et le journal (aperçu ×10), l'arroseuse et
  sa rue qui miroite.
- ⚠️ **Deux juges étaient déjà rouges avant ce jalon** et le restent, à l'identique sur la base
  sans lui (`b6ffdc5`) : `test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler` et
  `test_la_foule_ne_se_traverse_plus` (les mêmes 333 chevauchements creusés). Pas de ce jalon. Le
  reste est vert : la suite complète sur `b6ffdc5` + le jalon (3 609 juges), puis, remontée sur les
  garages (`40c2fbb`), le rejugement des fichiers touchés des deux côtés (503) et les 38 juges
  Chromium.
