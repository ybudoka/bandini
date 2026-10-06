# Les quatre saisons, réalistes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 27 sept. 2026 : « les 4 saisons réalistes »._

_Ce que ça donne :_ on sait en quelle saison on est **en regardant l'écran**, sans lire le HUD. Janvier
est blanc, gris et glissant ; avril est brun, mouillé et plein de nids-de-poule ; juillet est vert,
tard le soir et plein de monde dehors ; octobre est rouge et orange, et les feuilles volent derrière
les chars. Un Québec vu de haut, qui change quatre fois par année.

**Aujourd'hui** la saison est une **étiquette**, pas un paysage. `app/calendrier.py` (26 sept. 2026)
donne une année de 40 jours, douze mois et quatre saisons (le jour 1 d'une partie est le 1er janvier),
en pure fonction du jour. Huit modules la lisent, chacun pour sa chose : la motoneige et le pont de
glace (l'hiver), la cabane à sucre (le printemps), la Saint-Jean, le déménagement et le ciné-parc
(l'été), le temps des Fêtes. **Le reste de la ville ne bouge pas** : les arbres sont verts en janvier,
et la neige de M12 (`neige.js`, derrière l'option « TEMPÊTES DE NEIGE (ESSAI) ») tombe **tous les
trois jours, toute l'année** — une tempête en juillet est possible. Le verglas a ses jours (9 à 11)
et le brouillard ses matins, sans lien avec la saison.

**Aujourd'hui, au volant** (`vehicules.js`, « Adherence ») : un char ne dérape pas, il **flotte**. Sa
vitesse glisse vers son cap d'une part `adh` par image, et `adh` est un seul nombre : l'adhérence du
char × la neige (0,3 en pleine tempête, 0,75 derrière la charrue) × le verglas (0,4) × la rue mouillée
(l'arroseuse), avec les **pneus d'hiver** du garage de Ti-Guy qui en rendent une part (`Garage.hiver`).
Sur la glace, le char tourne donc comme au sec et dérive un peu plus : pas de sous-virage, pas de
tête-à-queue, pas de contre-braquage, pas de roues bloquées. Le frein à main change `adh`, sans faire
partir l'arrière. Rien ne marque le sol, et rien ne crisse. Seul le **nid-de-poule** fait déjà perdre
le contrôle (`nid_derape_*` : quelques images sans direction et le nez qui part). Le trafic, lui,
roule sur des rails : il lève le pied dans la neige, mais il ne glisse jamais.

**Ce qu'on veut**, en cinq vagues jouables (à trancher par Martin — l'ordre, et ce qui tombe) :

- **Vague 1 — le paysage.** Une **palette par saison** pour ce qui pousse : le gazon, les parcs, les
  arbres de rue, les haies, les sentiers — vert tendre au printemps, vert franc l'été et jauni en
  août, rouge-orange-jaune à l'automne (des érables : c'est le Québec), branches nues l'hiver et
  conifères poudrés. **La neige qui tient l'hiver** : au sol, sur les toits et les chars garés, de
  décembre à mars, pas seulement pendant la tempête ; et **les tempêtes seulement l'hiver** (plus de
  flocons en juillet). **La longueur du jour** : le soleil se couche vers 16 h en décembre, vers 21 h
  en juin — la lumière suit, sans toucher aux heures des commerces ni aux habitudes de la nuit.
- **Vague 2 — la glace et le dérapage.** La **glace de l'hiver**, qui n'attend plus les trois jours du
  verglas : des **plaques de glace noire** qu'on voit à peine (sur les ponts, dans l'ombre des
  bâtiments, aux arrêts où les chars ont poli la neige), tirées à l'empreinte de la tuile ; au
  printemps, **le gel et le dégel** — la fonte le jour, le regel la nuit, la glace le matin ; les
  **patinoires** des parcs, où l'on glisse à pied ; la baie gelée (le pont de glace existe). Et un
  **vrai dérapage** quand ça glisse : l'**avant** qui refuse de tourner (**sous-virage** : tout droit
  dans le banc de neige), l'**arrière** qui part quand on accélère ou qu'on tire le frein à main en
  courbe (**survirage**), le **tête-à-queue** si on laisse faire, le **contre-braquage** qui rattrape,
  les **roues bloquées** qui ne dirigent plus quand on freine trop fort. Le sol le montre : des
  **traces de pneus** noires au sec, des **sillons** dans la neige, qui s'effacent. On l'entend : le
  **crissement** au sec, le silence inquiétant sur la glace, le **banc de neige** qui étouffe et où
  le char s'enlise (les roues patinent, on recule, on repart). À pied aussi : un passant qui court
  sur la glace **glisse et tombe**, et le joueur comme les autres. Le **trafic et la police** ne
  restent pas sur leurs rails partout : sur la glace, un char de la ville peut glisser dans le banc,
  accrocher celui d'en avant, finir dans le fossé.
- **Vague 3 — ce qui tombe, et le sol.** **La pluie** (printemps et automne), **les orages** l'été ;
  **la fonte** en avril : la gadoue brune, les flaques qui éclaboussent les passants, les bancs de
  neige sales qui rapetissent, les **nids-de-poule** ; **les feuilles mortes** au sol en octobre,
  soulevées derrière un char qui passe. L'**adhérence** suit le sol (gadoue, feuilles mouillées,
  pluie) et dérape comme sur la glace de la vague 2 — moins fort.
- **Vague 4 — les gens et la rue.** La **garde-robe par saison** (`garderobe.js`) : tuques, foulards
  et manteaux l'hiver, t-shirts et shorts l'été, imperméables sous la pluie ; les **abris Tempo** dans
  les entrées de novembre à avril ; les **bancs de neige** le long des trottoirs que la charrue
  laisse ; la fumée des cheminées l'hiver ; les terrasses, les bornes-fontaines ouvertes et les
  passants plus nombreux dehors l'été ; les citrouilles sur les perrons à l'Halloween (une date de
  plus dans `calendrier.DATES`).
- **Vague 5 — le son.** Une ambiance par saison, par ElevenLabs : le vent et la charrue l'hiver,
  l'eau qui coule à la fonte, les cigales et les tondeuses l'été, les outardes et la pluie à
  l'automne — en fondu enchaîné d'une saison à l'autre.

⚠️ **Ce qui coûte, et ce qui guette :**

- **Une pure fonction du jour et de l'heure**, comme `calendrier.py` : rien à sauvegarder, aucun dé,
  la même saison pour tout le monde. Ce qui se pose dans la ville (abris Tempo, bancs de neige,
  citrouilles, feuilles) se pose **en dernier, sans dé**, tiré à l'empreinte — sinon la ville glisse
  et les juges « ce module ne déplace rien » rougissent.
- **Pas de coupure à minuit** : la palette glisse d'une saison à l'autre sur un jour ou deux (le
  fondu, comme la musique). Une saison ne dure que dix jours du jeu : la transition se voit.
- **Le rythme sur le téléphone** : recolorer la ville ne se fait pas à chaque image — les morceaux
  peints en cache se refont quand la palette change, pas plus. La pluie et les feuilles sont des
  particules comme les flocons : les mesurer à la sonde de performance, et payer enfin la dette
  « le rythme mesuré sur le vrai téléphone de Martin » (son déclencheur disait : la neige).
- **L'option « TEMPÊTES DE NEIGE (ESSAI) »** : à trancher par Martin — la saison la remplace-t-elle
  (l'hiver neige pour tout le monde), ou reste-t-elle l'interrupteur de toute la météo ? La motoneige
  et le pont de glace en dépendent aujourd'hui. Et les juges de la neige posent des jours précis
  (`premier: 2`, `tous_les: 3`) : les faire lire la saison, pas l'inverse.
- **Le dérapage touche TOUTE la conduite** : les courses, les défis chronométrés, les poursuites, les
  records déjà battus. ⚠️ **Au sec, le char se conduit exactement comme aujourd'hui** (le nouveau modèle
  ne s'éveille que sous une adhérence de 1, et les juges de conduite du sec ne bougent pas) ; le
  dérapage ne se tire pas au dé (le côté où part l'arrière vient du volant, de la vitesse et du sol —
  le nid-de-poule, lui, lit l'empreinte de sa tuile).
- **Glisser doit rester jouable** : au téléphone et à la manette de Martin, le contre-braquage doit se
  sentir et rattraper — un char qu'on ne peut plus tenir n'est pas réaliste, il est injouable. Les
  pneus d'hiver (Ti-Guy) doivent enfin valoir leur prix : la différence se sent dès le premier coin.
- **Le trafic sur ses rails** : le laisser glisser, c'est le laisser quitter sa voie — et le trafic
  sait mal revenir sur son chemin (les pilotes qui se perdent, les chars plantés sur la bordure). Une
  glissade de la ville est donc **courte et finit arrêtée** (le banc, le fossé, l'accrochage), puis le
  char repart ou attend la dépanneuse ; jamais en pleine poursuite une police qui se perd.
- **Les traces de pneus** sont une mémoire, comme la neige déblayée : un nombre borné, qui s'efface,
  peintes au sol sous les chars — et jamais sauvegardées.
- ~~Une partie neuve commence le 1er janvier~~ — **tranché par Martin (4 oct. 2026) : « le jeu doit
  débuter à un moment sans neige »**. Une partie neuve commence le **1er mai** (`calendrier.DEPART`,
  jour 14) ; l'année, elle, ne bouge pas (le jour 1 reste le 1er janvier, les fenêtres de saison
  restent où elles sont), et une partie déjà commencée garde son jour.
- **Les missions** ne changent pas avec la saison, sauf celles qui le disent ; une mission ne doit
  jamais devenir impossible en hiver (la motoneige ne remplace pas un char qu'une mission exige).
- **Regarder une couche peinte** avant de livrer : une capture Chromium par saison, les juges verts
  ne voient pas une palette ratée.

**Juges** : la saison se lit du jour, la même pour tout le monde ; pas une tempête hors de l'hiver ;
la palette d'un parc diffère d'une saison à l'autre et glisse d'un jour à l'autre sans saut ; le soleil
se couche plus tôt en décembre qu'en juin, et les commerces ouvrent à la même heure ; rien de ce qui se
pose pour une saison ne déplace la ville ; un passant de janvier porte un manteau. Et au volant : au sec, la conduite ne change pas d'un
pixel ; sur la glace, un char lancé en courbe sous-vire, le frein à main en courbe fait partir l'arrière,
le contre-braquage rattrape et les pneus d'hiver rattrapent mieux ; des roues bloquées ne dirigent pas ;
un passant qui court sur la glace tombe ; un char de la ville qui glisse finit arrêté, jamais perdu.

### Tranché par Martin le 29 sept. 2026

_« ajoute l'automne avec les couleurs et les feuilles + halloween », puis « continue avec toutes les
saisons + pluie »._

- **L'option « TEMPÊTES DE NEIGE (ESSAI) » disparaît : la saison la remplace.** L'hiver neige pour tout le
  monde, jamais l'été ; la motoneige, le pont de glace et le hockey suivent l'hiver, pas l'option.
  (Le verglas a sa propre option, « VERGLAS (ESSAI) », et son jour 11 tombe en avril : il reste tel
  quel au lot 1, à trancher avec la glace du lot 6.)
- **Une partie commence toujours au même jour** (le 1er janvier à l'époque, le 1er mai depuis le
  4 oct. 2026) ; pour voir une saison sans jouer vingt-six jours, une
  triche **« CHANGER DE MOIS »** (TRICHES › DIVERS).
- **L'Halloween au complet** : le décor (citrouilles sur les perrons, lumières orange et violettes, toiles),
  les **passants déguisés** et les enfants qui passent l'Halloween, **une maison hantée ou un défi**, et
  **le son et la musique** du soir du 31 (ElevenLabs).
- **Le dérapage (vague 2) se fait, mais en dernier.**

**Les lots, dans l'ordre** (chacun jouable, jugé, atterri seul ; chacun son design au moment de s'y mettre) :

1. **Le paysage des quatre saisons** — la palette, la neige qui tient, les tempêtes l'hiver seulement,
   la longueur du jour, et la triche. _(la vague 1)_
2. **La pluie et le sol** — pluie au printemps et à l'automne, orages l'été, gadoue et flaques à la fonte,
   feuilles mortes soulevées derrière les chars, la rue mouillée qui glisse un peu. _(la vague 3)_
3. **L'Halloween** — le 31 octobre (jour 33 de l'année) : décor, passants déguisés, maison hantée ou
   défi, son.
4. **Les gens et la rue** — la garde-robe par saison, les abris Tempo, les bancs de neige, la fumée des
   cheminées, les terrasses. _(la vague 4, moins l'Halloween)_
5. **Le son des saisons**, en fondu enchaîné. _(la vague 5)_
6. **La glace et le vrai dérapage.** _(la vague 2)_

### Lot 1 — le paysage des quatre saisons (design approuvé par Martin le 29 sept. 2026)

- **La saison se calcule, elle ne se sauve pas.** `calendrier.py` (et `calendrier.js`) donnent, du jour
  et de l'heure, **la palette du moment** : un passage d'une saison à l'autre dure deux jours du jeu, en
  **huit paliers**. Le cache des morceaux (`Monde`, 16×16 tuiles) ne se vide qu'au changement de palier —
  un quart de journée pendant une transition, jamais le reste du temps. Aucun dé, rien de sauvé, la
  même palette pour tout le monde.
- **Le paysage.** Le gazon, la friche et les parcs : vert tendre au printemps (de la boue au début
  d'avril), vert franc l'été et jauni en août, passé à l'automne avec des **feuilles rouges et orange au
  sol**, **blanc** l'hiver avec de la terre qui perce. Les arbres : bourgeons, vert, **érables rouges,
  orange et jaunes** (la couleur de chaque arbre à l'empreinte de sa tuile), branches nues poudrées. Rien
  ne se pose : les mêmes sprites, une variante par palier. L'hiver, les trottoirs et les toits sont
  blanchis ; les rues restent grises (déneigées), et la tempête garde sa neige fraîche par-dessus.
- **La météo suit la saison.** L'option disparaît ; les tempêtes gardent leur rythme (une tous les trois
  jours), **seulement l'hiver**, pour tout le monde. ⚠️ La neige glissera donc pour tous l'hiver :
  mesurée à la sonde de performance avant d'atterrir.
- **La longueur du jour.** Le ciel suit la saison : noir vers 16 h 30 en décembre, clair jusqu'à 21 h en
  juin ; les **lampadaires et les fenêtres suivent la lumière**. ⚠️ **Les règles du jeu gardent
  l'horloge fixe** : commerces, barrières, police, missions « la nuit » — une mission ne change pas
  d'heure selon le mois.
- **La triche « CHANGER DE MOIS »** (TRICHES › DIVERS) : chaque appui avance au premier du mois suivant,
  à la même heure.
- **Juges** : la palette se tire du jour, la même pour tout le monde, et glisse sans saut ; pas de
  tempête hors de l'hiver ; rien ne déplace la ville ; décembre s'assombrit plus tôt que juin, et
  `estNuit` des règles ne bouge pas ; la triche change de mois ; au sec, la conduite ne change pas. Et
  **une capture Chromium par saison**, ouverte dans Aperçu avant d'atterrir.

### Lot 1 — le plan de travail (29 sept. 2026)

> **Pour l'agent qui exécute** : superpowers:subagent-driven-development (ou executing-plans), tâche par
> tâche ; les cases `- [ ]` se cochent dans le registre `.superpowers/sdd/saisons-lot-1/progress.md` du
> worktree (voir la mémoire « superpowers écrit dans le plan de Bandini » : « Tâche N », pas « Task N »).

**But** : on sait en quelle saison on est en regardant la ville — le gazon, la friche, les arbres, les
trottoirs et les toits changent de couleur avec l'année ; la neige ne tombe que l'hiver, pour tout le
monde ; la lumière suit la longueur du jour ; une triche avance d'un mois.

**Architecture** : `app/saisons.py` porte les **données** (six palettes, les images-clés de l'année, la
lumière) dans le paquet (`B.defs.saisons`) ; `static/js/saisons.js` (module `Saisons`) en tire **la
palette du moment**, pure fonction de `(jour, heure)`, arrondie à huit paliers par transition. Les
peintres de tuile (`sprites.js`) et l'arbre lisent `Saisons` au moment de cuire ; `Monde.dessinerSol`
jette les tuiles cuites et les morceaux **au changement de palier seulement** (clé `Saisons.cle()`).
La lumière passe par `Saisons.heureDeLumiere` et `Monde.ambianceVue()`, **pour le rendu seul** :
`Monde.ambiance(h)`, `estNuit`, `periode` gardent l'horloge fixe des règles.

**Outils** : Python 3.14 + uv, JS sans module (IIFE globales, ordre de `templates/index.html`), juges
pytest, banc Node (`banc`, `tests/banc.js` : canevas factice, `ctx.traces` note les `fillRect`),
Chromium par Playwright (`tests/test_navigateur.py`) pour la capture et le rythme.

**Spec** : la fiche ci-dessus (« Tranché par Martin le 29 sept. » et « Lot 1 — le design »).

#### Contraintes de tout le lot

- **Aucun dé** : ni `B.rng`, ni `Des`, ni `Math.random` dans `saisons.js` ni dans les peintres
  touchés ; la variante d'un arbre vient de `hash2` (déjà le cas de `fiche.variantes`, `entites.js`
  `creerDecor`).
- **Rien ne se pose, rien ne se sauve** : aucune tuile, aucun décor, aucune clé de sauvegarde neuve.
  La ville (`generer`) ne change pas d'un octet.
- **Les règles gardent l'horloge fixe** : `Monde.ambiance(h)` avec une heure, `Monde.estNuit`,
  `Monde.periode`, `rythme`, `app/nuit.py`, `economie.SIESTE` ne bougent pas.
- **Au sec, la conduite ne change pas d'un pixel.**
- Commentaires JS **sans accents** (comme `calendrier.js`), textes affichés en majuscules accentuées
  (`'MOIS SUIVANT'`) ; commentaires Python accentués.
- Tout se fait dans le worktree ; chaque tâche commitée (`BANDINI_VERSION=wip git commit --no-verify`)
  puis `git update-ref refs/wip/saisons-lot-1 HEAD` ; pytest avec
  `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv`.
- `uv run ruff check .` avant d'atterrir.

#### Ce que les juges des tâches ne couvrent pas d'eux-mêmes (et la tâche qui l'épingle)

1. **Entrer dans une pièce pendant qu'un palier change**, puis ressortir : la ville doit repeindre ses
   morceaux (clé de palier posée sur la carte, pas globale) — tâche 3.
2. **Une partie de la deuxième ou troisième année** (jour 41, 95…) : la même palette qu'au même jour de
   la première — tâche 2.
3. **La triche qui saute du grand froid à mars** : le pont de glace rend son eau à l'image suivante —
   tâche 7.
4. **Une vieille sauvegarde d'options avec `neige: false`** : il neige quand même l'hiver — tâche 5.
5. **Le rythme au changement de palier** : on ne jette que les tuiles et les arbres, pas les chars ni
   les passants cuits — tâche 3.

---

#### Tâche 1 — Les données des saisons (`app/saisons.py`, le paquet)

**Fichiers** : créer `app/saisons.py`, `tests/test_saisons.py` ; modifier `app/definitions.py` (import
l.38, clé à côté de `"calendrier"` l.80) ; `docs/architecture.md` (une ligne sous `calendrier.py`).

**Produit** : `B.defs.saisons = { paliers: 8, cles: [[jour, slug], …], palettes: {slug: {gazon, friche,
arbre, neige}}, lumiere: {solstice_ete, coucher: [moyenne, ampleur], lever: [moyenne, ampleur],
reference: [lever, coucher]} }`.

- [ ] **Étape 1 — le juge** (`tests/test_saisons.py`) :

```python
"""Les saisons de Baie-des-Brumes (`app/saisons.py`) : six palettes, les images-clés de l'année,
la lumière — des données seulement ; le navigateur en tire la palette du moment."""

from app import calendrier, saisons


def test_les_cles_couvrent_l_annee_dans_l_ordre():
    jours = [j for j, _ in saisons.CLES]
    assert jours[0] == 1 and jours[-1] == calendrier.ANNEE + 1
    assert jours == sorted(jours) and len(set(jours)) == len(jours)
    assert saisons.CLES[0][1] == saisons.CLES[-1][1] == "hiver", "l'année finit comme elle commence"
    assert {s for _, s in saisons.CLES} == set(saisons.PALETTES)


def test_une_transition_dure_au_plus_deux_jours():
    for (a, pa), (b, pb) in zip(saisons.CLES, saisons.CLES[1:]):
        if pa != pb:
            assert 1 <= b - a <= 2, f"{pa} → {pb} en {b - a} jours"


def test_chaque_palette_a_les_memes_couleurs():
    formes = {s: {k: sorted(v) if isinstance(v, dict) else None for k, v in p.items()}
              for s, p in saisons.PALETTES.items()}
    assert len({repr(f) for f in formes.values()}) == 1
    for p in saisons.PALETTES.values():
        assert len(p["arbre"]["teintes"]) == 3 and all(len(t) == 3 for t in p["arbre"]["teintes"])
        assert 0 <= p["arbre"]["feuillage"] <= 1 and 0 <= p["neige"] <= 1


def test_l_octobre_est_rouge_et_janvier_blanc():
    a = saisons.PALETTES["automne"]["arbre"]["teintes"]
    assert any(int(t[0][1:3], 16) > 2 * int(t[0][3:5], 16) for t in a), "pas un érable rouge"
    assert saisons.palette_du_jour(33) == "automne", "l'Halloween est en plein automne"
    assert saisons.palette_du_jour(1) == "hiver" and saisons.PALETTES["hiver"]["neige"] > 0.5
    assert saisons.PALETTES["hiver"]["arbre"]["feuillage"] == 0


def test_dans_le_paquet(paquet):
    assert paquet["saisons"] == saisons.pour_le_navigateur()
```

- [ ] **Étape 2** — `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run pytest tests/test_saisons.py -q` : rouge (`ImportError`).
- [ ] **Étape 3 — le module** (`app/saisons.py`) :

```python
"""Les saisons de Baie-des-Brumes : la ville change de couleur avec l'année (29 sept. 2026).

Le calendrier (`calendrier.py`) disait la saison ; la ville restait verte en janvier. Ici, les
DONNÉES seulement : six palettes (ce qui pousse, la neige qui tient), les images-clés de l'année (où
chaque palette tient et où elle glisse vers la suivante), et la longueur du jour. Le navigateur en
tire la palette du moment (`static/js/saisons.js`), en huit paliers par transition — c'est le palier
qui fait repeindre les tuiles cuites, pas l'heure.

⚠️ AUCUN DÉ, RIEN DE POSÉ : une pure fonction du jour et de l'heure ; la ville ne bouge pas d'un octet.
⚠️ LA LUMIÈRE EST POUR LES YEUX : les règles (commerces, barrières, police, missions « la nuit ») gardent
l'horloge fixe de `Monde.ambiance` ; seul le rendu lit `heureDeLumiere`.
"""

from __future__ import annotations

from app import calendrier

#: Combien de paliers dans une transition : un palier = une repeinte des tuiles cuites.
PALIERS = 8

#: Les images-clés : [jour de l'année (1 à 41, fractions permises), palette]. Deux clés de même palette
#: = la palette tient ; deux palettes différentes = elle glisse de l'une à l'autre.
CLES = [
    (1, "hiver"), (10.5, "hiver"),            # la neige tient jusqu'au 10 (fin mars)
    (12, "printemps"), (16, "printemps"),     # la fonte, puis le vert tendre
    (18, "ete"), (23, "ete"),
    (25, "fin_ete"), (27, "fin_ete"),         # août : le gazon jaunit
    (29, "automne"), (34, "automne"),         # octobre, l'Halloween (jour 33) en plein rouge
    (35.5, "novembre"), (37, "novembre"),     # les branches nues, le gazon brun
    (38, "hiver"), (41, "hiver"),
]

#: Chaque palette : le gazon (`,`), la friche (`;`), l'arbre de rue (trois teintes [cime, clair, sombre],
#: tirées à l'empreinte de sa tuile ; `feuillage` 0 = nu), et `neige` : la part de blanc sur les
#: trottoirs et les toits.
PALETTES = {
    "ete": {
        "gazon": {"fond": "#4f8d3e", "clair": "#5a9c47", "sombre": "#427a33", "brin": "#6aad55",
                  "terre": "#6d5c3e", "fleur": "#cfc95c", "feuille": "#4f8d3e", "feuille2": "#4f8d3e"},
        "friche": {"fond": "#6d6845", "clair": "#7b7551", "sombre": "#5b5638", "sec": "#a4975f"},
        "arbre": {"teintes": [["#2f6b2a", "#3f8d38", "#204d1e"], ["#2a6330", "#3a8440", "#1d4722"],
                              ["#356f27", "#468f35", "#25501b"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "printemps": {
        "gazon": {"fond": "#5f9a45", "clair": "#74b057", "sombre": "#4d8438", "brin": "#8cc46a",
                  "terre": "#6a5536", "fleur": "#e8d85a", "feuille": "#5f9a45", "feuille2": "#5f9a45"},
        "friche": {"fond": "#6a6a44", "clair": "#787a50", "sombre": "#585a37", "sec": "#9a9a60"},
        "arbre": {"teintes": [["#4f8f3a", "#6fb050", "#3a7029"], ["#5a9a40", "#7cbc58", "#437a2e"],
                              ["#6aa048", "#8cc466", "#4e8034"]], "feuillage": 0.8, "neige": 0},
        "neige": 0,
    },
    "fin_ete": {
        "gazon": {"fond": "#7a8c42", "clair": "#8f9c4f", "sombre": "#667838", "brin": "#a3a85c",
                  "terre": "#7a6443", "fleur": "#d9b24a", "feuille": "#7a8c42", "feuille2": "#7a8c42"},
        "friche": {"fond": "#7d7546", "clair": "#8b8252", "sombre": "#6a6339", "sec": "#b5a462"},
        "arbre": {"teintes": [["#4a6b2a", "#5f8436", "#34501e"], ["#2f6b2a", "#3f8d38", "#204d1e"],
                              ["#6b7a2a", "#869536", "#4f5c1e"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "automne": {
        "gazon": {"fond": "#6f7a3c", "clair": "#7f8646", "sombre": "#5c6632", "brin": "#8e8a4c",
                  "terre": "#6d5536", "fleur": "#c8622a", "feuille": "#c0392b", "feuille2": "#e67e22"},
        "friche": {"fond": "#76663f", "clair": "#86744a", "sombre": "#625434", "sec": "#b08850"},
        "arbre": {"teintes": [["#b8321f", "#d9502e", "#7f2416"], ["#d9731f", "#f09a3a", "#9a4f14"],
                              ["#d4a91c", "#efcb3e", "#9a7a12"]], "feuillage": 0.95, "neige": 0},
        "neige": 0,
    },
    "novembre": {
        "gazon": {"fond": "#6b6a45", "clair": "#77744f", "sombre": "#57553a", "brin": "#83805a",
                  "terre": "#5e4a32", "fleur": "#8a5a34", "feuille": "#8a5a34", "feuille2": "#7a4a2a"},
        "friche": {"fond": "#6a5f42", "clair": "#776b4c", "sombre": "#574e36", "sec": "#948058"},
        "arbre": {"teintes": [["#7a4a26", "#94603a", "#5a361c"], ["#8a5a2e", "#a67040", "#643f20"],
                              ["#6e5a34", "#8a7244", "#4f4024"]], "feuillage": 0.3, "neige": 0},
        "neige": 0,
    },
    "hiver": {
        "gazon": {"fond": "#e8edf2", "clair": "#f6f8fb", "sombre": "#cfd8e2", "brin": "#b9c4cf",
                  "terre": "#8a7f70", "fleur": "#dfe6ee", "feuille": "#e8edf2", "feuille2": "#e8edf2"},
        "friche": {"fond": "#e3e7ea", "clair": "#f2f4f6", "sombre": "#c9d0d6", "sec": "#a89f86"},
        "arbre": {"teintes": [["#7a4a26", "#94603a", "#5a361c"], ["#8a5a2e", "#a67040", "#643f20"],
                              ["#6e5a34", "#8a7244", "#4f4024"]], "feuillage": 0, "neige": 1},
        "neige": 0.7,
    },
}

#: La longueur du jour. `coucher`/`lever` = [moyenne, ampleur] en heures : l'heure du jour de l'année x
#: est moyenne ± ampleur × cos(2π (x − solstice_ete) / ANNEE) — 16 h 15 au 21 décembre, 20 h 45 au
#: 21 juin. `reference` = le lever et le coucher de l'horloge fixe (`Monde.TEINTES` : 0,30 et 0,80).
LUMIERE = {"solstice_ete": 19.7, "coucher": [18.5, 2.25], "lever": [6.25, -1.2], "reference": [7.2, 19.2]}


def palette_du_jour(jour_de_l_annee: float) -> str:
    """La palette qui TIENT ce jour-là (la clé précédente), sans le glissement — pour les juges."""
    nom = CLES[0][1]
    for j, s in CLES:
        if jour_de_l_annee >= j:
            nom = s
    return nom


def pour_le_navigateur() -> dict:
    return {"paliers": PALIERS, "cles": [[j, s] for j, s in CLES], "palettes": PALETTES,
            "lumiere": LUMIERE, "annee": calendrier.ANNEE}
```

  et dans `app/definitions.py` : `saisons` dans l'import de la l.38, puis sous la clé du calendrier :
  `# Les saisons : la palette de la ville et la longueur du jour (`saisons.py`).` /
  `"saisons": saisons.pour_le_navigateur(),`.
- [ ] **Étape 4** — `uv run pytest tests/test_saisons.py tests/test_definitions.py tests/test_calendrier.py -q` :
  vert. ⚠️ `test_definitions` juge **le poids du paquet** : s'il rougit sur la taille, le dire (ne pas
  relever le plafond sans Martin).
- [ ] **Étape 5** — la ligne de `docs/architecture.md` sous `calendrier.py` :
  `| `saisons.py` | **les saisons de la ville** : six palettes (gazon, friche, arbres, neige qui tient), les images-clés de l'année, la longueur du jour — des données, le navigateur tire la palette du moment | les clés couvrent l'année, une transition ≤ 2 jours, octobre rouge, janvier blanc |` ;
  commit `wip: les saisons — les données`.

#### Tâche 2 — La palette du moment (`static/js/saisons.js`)

**Fichiers** : créer `static/js/saisons.js`, `tests/test_saisons_js.py` ; modifier `templates/index.html`
(le `<script>` juste **après** `calendrier.js`, l.190, avant `atlas.js`) et `static/js/jeu.js` l.1531
(`Saisons: Saisons,` après `Calendrier: Calendrier,`).

**Consomme** : `B.defs.saisons` (tâche 1), `Calendrier.jourDeLAnnee`.
**Produit** : `Saisons.paletteA(jour, heure)` → `{ gazon, friche, arbre: {teintes, feuillage, neige},
neige }` (couleurs `'#rrggbb'`) ; `Saisons.cleA(jour, heure)` → chaîne (`'hiver'`, `'automne>novembre:3'`) ;
`Saisons.palette()` / `Saisons.cle()` (la partie ; l'été si pas de partie) ; `Saisons.enneiger(style)` →
copie de `style` dont chaque couleur `'#…'` est mêlée au blanc de neige (`'#eef2f6'`) de `palette().neige`,
mémorisée par clé ; `Saisons.heureDeLumiere(jour, heure)` → heure 0..1 (tâche 6).

- [ ] **Étape 1 — le juge** (`tests/test_saisons_js.py`) :

```python
"""La palette du moment (`static/js/saisons.js`) : une pure fonction du jour et de l'heure, la même
pour tout le monde, qui glisse d'une saison à l'autre en huit paliers, sans saut."""


def test_la_palette_suit_l_annee(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, p = function (j, h) { return S.paletteA(j, h); };
        return {
            janvier: p(1, 0.5).gazon.fond, juillet: p(21, 0.5).gazon.fond, octobre: p(32, 0.5).arbre.teintes[0][0],
            halloween: S.cleA(33, 0.9), an2: S.cleA(41 + 32, 0.5), an3: S.cleA(81 + 32, 0.5), an1: S.cleA(33, 0.5),
            memeJour: JSON.stringify(p(15, 0.3)) === JSON.stringify(p(15, 0.3)),
            neigeJanvier: p(2, 0.5).neige, neigeJuillet: p(21, 0.5).neige,
        };
    }""")
    assert r["janvier"] == "#e8edf2" and r["juillet"] == "#4f8d3e" and r["octobre"] == "#b8321f"
    assert r["halloween"] == "automne"
    assert r["an1"] == r["an2"] == r["an3"], "la deuxième année n'a pas les couleurs de la première"
    assert r["memeJour"] and r["neigeJanvier"] == 0.7 and r["neigeJuillet"] == 0


def test_la_palette_glisse_sans_saut(banc):
    """Toutes les demi-heures d'une année : d'un moment au suivant, la palette ne change que d'un
    palier (1/8 de l'écart entre deux saisons) au plus — et la clé ne change qu'avec la palette."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, rgb = function (c) { return [1, 3, 5].map(function (i) { return parseInt(c.substr(i, 2), 16); }); };
        let pire = 0, cles = 0, prec = null, cprec = null, faux = 0;
        for (let j = 1; j <= 41; j++) for (let k = 0; k < 48; k++) {
            const h = k / 48, g = rgb(S.paletteA(j, h).gazon.fond), c = S.cleA(j, h);
            if (prec) {
                const d = Math.max.apply(null, g.map(function (v, i) { return Math.abs(v - prec[i]); }));
                pire = Math.max(pire, d);
                if (c !== cprec) cles++; else if (d !== 0) faux++;
            }
            prec = g; cprec = c;
        }
        return { pire: pire, cles: cles, faux: faux };
    }""")
    assert r["faux"] == 0, "la couleur change sans que la clé change : le cache ne se repeindrait pas"
    # Le plus grand écart entre deux palettes voisines (automne → hiver en passant par novembre, hiver → printemps) :
    # 0xe8 − 0x5f = 137 ; un palier en fait au plus 137/8 ≈ 18, plus l'arrondi.
    assert r["pire"] <= 20, f"un saut de {r['pire']} dans le vert"
    assert 30 <= r["cles"] <= 60, f"{r['cles']} changements de palier dans l'année"


def test_enneiger_blanchit_l_hiver_seulement(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, st = { fond: '#9a9689', tole: true };
        L.B.partie.jour = 21; const ete = S.enneiger(st);
        L.B.partie.jour = 2; const hiver = S.enneiger(st), encore = S.enneiger(st);
        return { ete: ete.fond, hiver: hiver.fond, tole: hiver.tole, meme: hiver === encore };
    }""")
    assert r["ete"] == "#9a9689" and r["hiver"] != "#9a9689" and r["tole"] is True and r["meme"]
    assert int(r["hiver"][1:3], 16) > 0xd0, "un trottoir de janvier n'est pas blanchi"
```

- [ ] **Étape 2** — `uv run pytest tests/test_saisons_js.py -q` : rouge (`L.Saisons` indéfini).
- [ ] **Étape 3 — le module** (`static/js/saisons.js`) :

```js
/* Bandini — les saisons de la ville (docs/jalons/les-quatre-saisons-realistes.md, lot 1).

   La palette du moment : le gazon, la friche, les arbres, la neige qui tient sur les trottoirs et
   les toits. ⚠️ UNE PURE FONCTION DU JOUR ET DE L'HEURE (`app/saisons.py` donne les palettes et les
   images-cles) : aucun de, rien a sauvegarder, la meme ville pour tout le monde.

   ⚠️ HUIT PALIERS PAR TRANSITION : la couleur ne glisse pas a chaque image, elle saute d'un palier
   a l'autre. C'est le palier (`cle`) qui fait repeindre les tuiles cuites et les morceaux
   (`Monde.dessinerSol`) : une repeinte toutes les deux minutes pendant une transition, jamais le
   reste du temps — le rythme sur le telephone.

   ⚠️ LA LUMIERE EST POUR LES YEUX (`heureDeLumiere`) : les regles gardent l'horloge fixe de
   `Monde.ambiance`. */

const Saisons = (function () {
  'use strict';

  //: La neige qui tient, sur un trottoir ou un toit.
  const BLANC = [238, 242, 246];

  function donnees() { return B.defs && B.defs.saisons; }

  function rgb(c) { return [parseInt(c.substr(1, 2), 16), parseInt(c.substr(3, 2), 16), parseInt(c.substr(5, 2), 16)]; }
  function hex(v) { return '#' + v.map(function (x) { return ('0' + Math.round(x).toString(16)).slice(-2); }).join(''); }
  function meler(a, b, t) { const x = rgb(a), y = rgb(b); return hex(x.map(function (v, i) { return v + (y[i] - v) * t; })); }

  /** Mele deux valeurs de palette de meme forme : couleurs, nombres, tableaux, objets. */
  function melerTout(a, b, t) {
    if (typeof a === 'string') return t === 0 ? a : meler(a, b, t);
    if (typeof a === 'number') return a + (b - a) * t;
    if (Array.isArray(a)) return a.map(function (v, i) { return melerTout(v, b[i], t); });
    const o = {};
    for (const k in a) o[k] = melerTout(a[k], b[k], t);
    return o;
  }

  /** Ou en est l'annee : { de, vers, palier } — `palier` de 0 a paliers-1 dans une transition. */
  function position(jour, heure) {
    const d = donnees(), x = Calendrier.jourDeLAnnee(jour) + (heure || 0);
    const cles = d.cles;
    for (let i = 0; i < cles.length - 1; i++) {
      const a = cles[i], b = cles[i + 1];
      if (x >= a[0] && x < b[0]) {
        if (a[1] === b[1]) return { de: a[1], vers: a[1], palier: 0 };
        return { de: a[1], vers: b[1], palier: Math.floor((x - a[0]) / (b[0] - a[0]) * d.paliers) };
      }
    }
    return { de: cles[0][1], vers: cles[0][1], palier: 0 };
  }

  function cleA(jour, heure) {
    const p = position(jour, heure);
    return p.de === p.vers ? p.de : p.de + '>' + p.vers + ':' + p.palier;
  }

  const memo = new Map();
  function paletteA(jour, heure) {
    const d = donnees(), cle = cleA(jour, heure);
    if (memo.has(cle)) return memo.get(cle);
    const p = position(jour, heure);
    const pal = melerTout(d.palettes[p.de], d.palettes[p.vers], p.palier / d.paliers);
    memo.set(cle, pal);
    return pal;
  }

  function maintenant() { return B.partie ? [B.partie.jour, B.partie.heure] : [21, 0.5]; }
  function palette() { const m = maintenant(); return paletteA(m[0], m[1]); }
  function cle() { const m = maintenant(); return cleA(m[0], m[1]); }

  /** Le style d'un trottoir ou d'un toit sous la neige qui tient : chaque couleur melee au blanc
      de `palette().neige`. Le meme objet tant que la cle ne change pas (les peintres le lisent a
      chaque tuile cuite). */
  const neiges = new Map();
  function enneiger(style) {
    const n = palette().neige;
    if (!n) return style;
    const k = cle();
    let parStyle = neiges.get(k);
    if (!parStyle) { parStyle = new Map(); neiges.set(k, parStyle); }
    if (parStyle.has(style)) return parStyle.get(style);
    const o = {};
    for (const c in style) o[c] = typeof style[c] === 'string' && style[c][0] === '#' ? meler(style[c], hex(BLANC), n) : style[c];
    parStyle.set(style, o);
    return o;
  }

  function heureDeLumiere(jour, heure) { return heure; }   // la tache 6 la remplit

  return { paletteA, cleA, palette, cle, enneiger, heureDeLumiere };
})();
```

- [ ] **Étape 4** — `uv run pytest tests/test_saisons_js.py tests/test_calendrier.py -q` : vert. Ajouter
  `saisons.js` à la carte de `docs/architecture.md` (scripts JS, à côté de `calendrier.js`). Commit
  `wip: les saisons — la palette du moment`.

#### Tâche 3 — Le sol peint suit la saison (gazon, friche, trottoirs, toits)

**Fichiers** : `static/js/sprites.js` (`herbe` l.2614, `friche` l.2660, `trottoir` l.2575, `toitPlat`
l.3121, `toitEnPente` l.3133), `static/js/atlas.js` (l.510 : `oublier(prefixe)`), `static/js/monde.js`
(`dessinerSol` l.2003) ; juge `tests/test_saisons_sol_js.py`.

**Consomme** : `Saisons.palette()`, `Saisons.cle()`, `Saisons.enneiger(style)`.
**Produit** : `Atlas.oublier(prefixe)` ; la carte porte `carte.palier` (la clé du palier de ses morceaux).

- [ ] **Étape 1 — le juge** :

```python
"""Le sol suit la saison : le gazon et la friche prennent la palette du moment, les trottoirs et les
toits blanchissent l'hiver ; les morceaux ne se repeignent qu'au changement de palier."""


def test_le_gazon_change_avec_l_annee(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        function peindre(g, v) { const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d'); ctx.traces = []; L.TUILES[g](ctx, v, L.TT); return ctx.traces.map(function (t) { return t[4]; }); }
        const out = {};
        [['janvier', 2], ['juillet', 21], ['octobre', 32]].forEach(function (m) {
            L.B.partie.jour = m[1]; L.B.partie.heure = 0.5;
            let gazon = [];
            for (let v = 0; v < 16; v++) gazon = gazon.concat(peindre(',', v));
            out[m[0]] = { gazon: gazon, friche: peindre(';', 3), trottoir: peindre('.', 0), toit: peindre('B', 0) };
        });
        return out;
    }""")
    assert r["juillet"]["gazon"][0] == "#4f8d3e", "l'été n'a plus le gazon d'avant"
    assert r["janvier"]["gazon"][0] == "#e8edf2"
    assert r["juillet"]["trottoir"] != r["janvier"]["trottoir"] and r["juillet"]["toit"] != r["janvier"]["toit"]
    assert r["octobre"]["friche"][0] != r["juillet"]["friche"][0]
    assert {"#c0392b", "#e67e22"} & set(r["octobre"]["gazon"]), "pas une feuille rouge dans le gazon d'octobre"
    assert not {"#c0392b", "#e67e22"} & set(r["juillet"]["gazon"])


def test_les_morceaux_ne_se_repeignent_qu_au_palier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, c = L.Monde.carte;
        p.jour = 21; p.heure = 0.5; L.Jeu.rendre();
        const avant = c.morceaux.size, sprites = L.Atlas.taille;
        const m0 = Array.from(c.morceaux.values())[0];
        p.heure = 0.6; L.Jeu.rendre();
        const memeHeure = Array.from(c.morceaux.values())[0] === m0;
        p.jour = 32; L.Jeu.rendre();
        const autreSaison = Array.from(c.morceaux.values())[0] !== m0;
        return { avant: avant, memeHeure: memeHeure, autreSaison: autreSaison, palier: c.palier, reste: L.Atlas.taille, sprites: sprites };
    }""")
    assert r["avant"] > 0 and r["memeHeure"], "un morceau repeint sans changement de palier"
    assert r["autreSaison"] and r["palier"] == "automne"
    assert r["reste"] > 0, "on a jeté tout l'atlas (les chars, les passants) au lieu des tuiles"


def test_la_ville_repeint_en_sortant_d_une_piece(banc):
    """On entre dans une pièce en été, le palier change dedans, on ressort : la ville se repeint."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, ville = L.Monde.carte;
        p.jour = 21; p.heure = 0.5; L.Jeu.rendre();
        const m0 = Array.from(ville.morceaux.values())[0];
        const porte = L.Monde.carte.portes && L.Monde.carte.portes[0];
        L.Jeu.entrer(porte); L.Jeu.rendre();
        p.jour = 32; L.Jeu.rendre();
        L.Jeu.sortir(); L.Jeu.rendre();
        return { repeint: Array.from(L.Monde.carte.morceaux.values())[0] !== m0, palier: L.Monde.carte.palier, ville: L.Monde.carte === ville };
    }""")
    assert r["ville"] and r["repeint"] and r["palier"] == "automne"
```

  ⚠️ Le troisième juge suppose `Jeu.entrer(porte)` / `Jeu.sortir()` ; vérifier leur signature dans
  `jeu.js` (l.1523 les exporte) et prendre la première porte de commerce comme les juges existants
  (`grep -rn "Jeu.entrer(" tests | head`) — adapter l'appel, pas la règle.
- [ ] **Étape 2** — `uv run pytest tests/test_saisons_sol_js.py -q` : rouge.
- [ ] **Étape 3 — les peintres** (`sprites.js`) :
  - `herbe(ctx, v, T)` : en tête, `const G = typeof Saisons !== 'undefined' ? Saisons.palette().gazon : GAZON;`
    et remplacer chaque `GAZON.` par `G.` dans la fonction. Puis, **après** les touffes/terre/pissenlits,
    les feuilles mortes (seulement si la palette en a — `G.feuille !== G.fond`) :

```js
    // Les FEUILLES MORTES (les saisons, lot 1) : deux ou trois feuilles par tuile, jamais alignees
    // (la lecon des pissenlits), rouges et orange — la palette d'ete les a de la couleur du fond.
    if (G.feuille !== G.fond) {
      for (let i = 0; i < 3; i++) {
        if (bruit(v + 1, 71 + i) < 0.35) continue;
        ctx.fillStyle = i === 1 ? G.feuille2 : G.feuille;
        const x = 2 + Math.floor(bruit(v + 1, 51 + i * 5) * (T - 4)), y = 2 + Math.floor(bruit(v + 1, 61 - i * 3) * (T - 4));
        ctx.fillRect(x, y, 2, 1); ctx.fillRect(x, y + 1, 1, 1);
      }
    }
```

  - `friche(ctx, v, T)` : `const F = typeof Saisons !== 'undefined' ? Object.assign({}, FRICHE, Saisons.palette().friche) : FRICHE;`
    et `FRICHE.` → `F.` dans la fonction.
  - `trottoir` : `const pal = ...` devient
    `const pal0 = usage === 3 ? BETON_USINE : rang === 1 ? BETON_CHIC : BETON; const pal = typeof Saisons !== 'undefined' ? Saisons.enneiger(pal0) : pal0;`
  - `toitPlat` et `toitEnPente` : première ligne `if (typeof Saisons !== 'undefined') style = Saisons.enneiger(style);`
- [ ] **Étape 4 — le cache** :
  - `atlas.js` : `function oublier(prefixe) { for (const k of Array.from(cache.keys())) if (k.indexOf(prefixe) === 0) cache.delete(k); }`,
    exporté à côté de `vider`.
  - `monde.js`, en tête de `dessinerSol` (l.2003), avant de chercher les morceaux :

```js
    // ⚠️ LA SAISON CHANGE DE PALIER (les saisons, lot 1) : les tuiles cuites et les morceaux de
    // CETTE carte se repeignent — pas les chars ni les passants de l'atlas. La cle est posee sur la
    // carte : une piece traversee pendant le changement ne laisse pas la ville a l'ancienne couleur.
    if (typeof Saisons !== 'undefined') {
      const k = Saisons.cle();
      if (carte.palier !== k) {
        if (carte.palier !== undefined) { Atlas.oublier('tuile|'); Atlas.oublier('decor|arbre'); }
        carte.morceaux.clear();
        carte.palier = k;
      }
    }
```

  (lire les premières lignes de `dessinerSol` pour le nom exact de la carte courante — `carte` ou
  `Monde.carte` — et le garder.)
- [ ] **Étape 5** — `uv run pytest tests/test_saisons_sol_js.py tests/test_interieurs_js.py tests/test_la_nuit_js.py -q`,
  puis `uv run pytest tests -q -k "tuile or trottoir or toit or morceau" -x -p no:randomly` : vert. Un
  juge d'avant qui compare une couleur de gazon ou de trottoir **exacte** en janvier (le jour 1 d'une
  partie !) rougira : il doit poser l'été (`B.partie.jour = 21`), pas l'inverse — le noter dans le
  commit. Commit `wip: les saisons — le sol`.

#### Tâche 4 — Les arbres suivent la saison

**Fichiers** : `static/js/sprites.js` (`DECORS.arbre` l.5752) ; juge `tests/test_saisons_arbres_js.py`.

**Consomme** : `Saisons.palette().arbre` ; la clé de cache `'decor|arbre|' + pose` jetée par la tâche 3.

- [ ] **Étape 1 — le juge** :

```python
"""Les arbres de rue : verts l'été, érables rouges, orange et jaunes l'automne (à l'empreinte de
leur tuile, sans dé), nus et poudrés l'hiver."""


def _cimes(banc, jour):
    return banc("""function (L) {
        L.Jeu.commencer(); L.B.partie.jour = %d; L.B.partie.heure = 0.5;
        const d = L.DECORS.arbre, out = [];
        for (let t = 0; t < d.variantes; t++) {
            const ctx = L.Base.nouveauCanvas(d.w, d.h).getContext('2d'); ctx.traces = [];
            d.peindre(ctx, d.w, d.h, t); out.push(ctx.traces.map(function (x) { return x[4]; }));
        }
        return out;
    }""" % jour)


def test_trois_teintes_d_erable_en_octobre(banc):
    oct_ = _cimes(banc, 32)
    assert len(oct_) == 3 and len({c[1] for c in oct_}) == 3, "les trois arbres d'octobre ont la même couleur"
    assert "#b8321f" in oct_[0]


def test_l_arbre_est_nu_et_poudre_en_janvier(banc):
    jan = _cimes(banc, 2)
    toutes = {c for t in jan for c in t}
    assert not toutes & {"#2f6b2a", "#b8321f", "#7a4a26"}, "une cime en janvier"
    assert "#eef2f6" in toutes, "pas de neige sur les branches"


def test_l_ete_garde_l_arbre_d_avant(banc):
    ete = _cimes(banc, 21)
    assert ete[0][:2] == ["#5a3a1a", "#2f6b2a"]


def test_la_teinte_ne_tire_aucun_de(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const arbres = L.B.entites.filter(function (e) { return e.decor === 'arbre'; });
        return Array.from(new Set(arbres.map(function (e) { return e.v; }))).sort();
    }""")
    assert r == [0, 1, 2], "les trois teintes ne sont pas toutes en ville"
```

  ⚠️ Le dernier juge vérifie que les trois teintes existent en ville ; que `variantes` ne tire pas de
  dé est déjà garanti par `creerDecor` (`hash2`) — le vérifier en ajoutant, dans le même juge, la
  comparaison des `id` et des positions des entités avec et sans `DECORS.arbre.variantes` (retirer
  la propriété, `Jeu.commencer()`, noter `[id, x, y]` de toutes les entités ; la remettre, recommencer ;
  égalité). Lire comment les juges « ce module ne déplace rien » font
  (`grep -rln "ne deplace rien\|ne_deplace_rien" tests`) et suivre leur recette.
- [ ] **Étape 2** — rouge.
- [ ] **Étape 3 — l'arbre** (remplace l'entrée `arbre` l.5752 ; `variantes: 3` = la teinte, tirée par
  `creerDecor` à l'empreinte) :

```js
  // ⚠️ L'ARBRE SUIT LA SAISON (docs/jalons/les-quatre-saisons-realistes.md, lot 1) : `variantes` est sa
  // TEINTE (trois erables : rouge, orange, jaune en octobre ; trois verts l'ete), tiree a l'empreinte
  // de sa tuile par `creerDecor`. `feuillage` 0 = nu ; `neige` poudre les branches. L'atlas le jette au
  // changement de palier (`Monde.dessinerSol`). L'ete, c'est l'arbre d'avant, au pixel.
  arbre: { arrete: 2.0, w: 18, h: 26, ancre: [9, 25], r: 5, solide: true, variantes: 3, peindre: function (ctx, w, h, teinte) {
    const a = typeof Saisons !== 'undefined' ? Saisons.palette().arbre
      : { teintes: [['#2f6b2a', '#3f8d38', '#204d1e']], feuillage: 1, neige: 0 };
    const t = a.teintes[(teinte || 0) % a.teintes.length];
    ctx.fillStyle = '#5a3a1a'; ctx.fillRect(8, 16, 3, 9);
    if (a.feuillage >= 0.5) {
      ctx.fillStyle = t[0]; ctx.fillRect(2, 4, 14, 13); ctx.fillRect(5, 1, 8, 3); ctx.fillRect(0, 7, 18, 7);
      ctx.fillStyle = t[1]; ctx.fillRect(4, 3, 6, 5); ctx.fillRect(2, 9, 5, 4);
      ctx.fillStyle = t[2]; ctx.fillRect(10, 10, 6, 6); ctx.fillRect(6, 14, 8, 3);
    } else {
      // Les branches nues : un Y et ses fourches.
      ctx.fillStyle = '#5a3a1a';
      ctx.fillRect(9, 8, 1, 8); ctx.fillRect(5, 5, 1, 6); ctx.fillRect(13, 4, 1, 7); ctx.fillRect(6, 10, 3, 1); ctx.fillRect(10, 9, 3, 1);
      ctx.fillRect(3, 3, 1, 3); ctx.fillRect(15, 2, 1, 3); ctx.fillRect(8, 2, 1, 6);
      if (a.feuillage > 0) {        // novembre : les dernieres feuilles
        ctx.fillStyle = t[0]; ctx.fillRect(4, 4, 2, 1); ctx.fillRect(12, 3, 2, 1); ctx.fillRect(9, 6, 2, 1);
      }
      if (a.neige > 0) {
        ctx.fillStyle = '#eef2f6';
        ctx.fillRect(5, 4, 1, 1); ctx.fillRect(13, 3, 1, 1); ctx.fillRect(8, 1, 1, 1); ctx.fillRect(3, 2, 1, 1); ctx.fillRect(15, 1, 1, 1); ctx.fillRect(6, 9, 3, 1);
      }
    }
  } },
```

  ⚠️ `poseDuDecor` et `e.v` : `anime` est absent de l'arbre, donc la pose est `e.v` (`entites.js`
  l.5470). Vérifier qu'aucun autre code ne cuit `'decor|arbre'` sans pose (`grep -n "decor|' + " static/js`),
  notamment `dessinerBetes` (l.5344) qui partage la clé.
- [ ] **Étape 4** — `uv run pytest tests/test_saisons_arbres_js.py -q` et les juges qui touchent les
  arbres : `uv run pytest tests -q -k "arbre or decor"`. Commit `wip: les saisons — les arbres`.

#### Tâche 5 — La neige suit l'hiver, l'option disparaît

**Fichiers** : `static/js/neige.js` (l.11-14 en-tête, `intensiteA` l.34, `intensite` l.45,
`rangDeTempete`, `operation` l.71, `couverture` l.88), `static/js/pont.js` (l.12, l.29),
`static/js/missions.js` (l.2828-2833), `static/js/vehicules.js` (l.1059), `static/js/hud.js` (l.741-742),
`static/js/base.js` (l.70), `static/js/jeu.js` (l.1413) ; docstrings `app/neige.py` (l.5-6, 13-14),
`app/calendrier.py` (l.11-14) ; juges `tests/test_neige_js.py`, `tests/test_deneigement_js.py`,
`tests/test_motoneige_js.py`, `tests/test_pont_de_glace_js.py`, `tests/test_hockey_js.py`,
`tests/test_navigateur.py` (l.627).

- [ ] **Étape 1 — les juges réécrits d'abord** :
  - `test_neige_js.py` : `test_sans_l_option_il_ne_neige_rien` devient
    `test_hors_de_l_hiver_il_ne_neige_rien` : le même soir de tempête (`jour ≡ premier mod tous_les`)
    mais **en juillet** (le premier jour ≥ 21 qui tombe sur le rythme : `21 + ((t.premier - 21) % t.tous_les + t.tous_les) % t.tous_les`),
    mêmes assertions (`i == 0`, `adh == 1`, `frein == 1`, `trafic == 1`, `rects == 0`). Toutes les
    lignes `B.options.neige = …` disparaissent.
  - Nouveau juge dans `test_neige_js.py` :

```python
def test_une_tempete_seulement_l_hiver_sur_trois_ans(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const N = L.Neige, C = L.Calendrier, hors = [], dedans = [];
        for (let j = 1; j <= 120; j++) {
            const i = Math.max(N.intensiteA(j, 20 / 24), N.intensiteA(j, 22 / 24));
            if (i > 0) (C.saison(j) === 'hiver' ? dedans : hors).push(j);
        }
        return { hors: hors, dedans: dedans };
    }""")
    assert r["hors"] == [], f"des tempêtes hors de l'hiver : {r['hors']}"
    assert len(r["dedans"]) >= 9, "l'hiver ne neige presque plus"


def test_une_vieille_option_eteinte_n_empeche_pas_l_hiver(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const t = L.B.defs.carte.neige.tempete;
        L.B.partie.jour = t.premier; L.B.partie.heure = 21 / 24;
        return { i: L.Neige.intensite(), cle: 'neige' in L.B.options };
    }""", stockage={"bandini-options-v1": '{"neige": false, "brouillard": false}'})
    assert r["i"] > 0 and r["cle"] is False
```

  - `test_deneigement_js.py` : `sansOption` → « hors de l'hiver » (même recette, un jour d'été) ; la
    boucle `jour < t.premier + 3*t.tous_les + 3` ne compte plus que les tempêtes d'hiver : lire le juge,
    garder ce qu'il prouve (l'annonce, la nuit d'opération, la fin au matin) sur des jours d'hiver.
  - `test_motoneige_js.py:12`, `test_pont_de_glace_js.py` (l.12, 117, 120 : la ligne « sans » devient
    « hors du grand froid », un jour d'été), `test_hockey_js.py:108` (la variante « sans neige » devient
    « l'été »), `test_navigateur.py:627` : retirer l'option ; ces juges posent déjà un jour d'hiver
    (le vérifier : sinon, poser `jour` sur un soir de tempête d'hiver).
- [ ] **Étape 2** — rouge (`test_une_tempete_seulement_l_hiver_sur_trois_ans` : jours 11, 14… en avril).
- [ ] **Étape 3 — le code** :
  - `neige.js` `intensiteA` : après `if (!d) return 0;` →
    `if (Calendrier.saison(jour) !== 'hiver') return 0;          // la saison, pas une option (29 sept. 2026)` ;
    `rangDeTempete(jour)` : même garde en tête (`return -1`), pour que le déneigement suive.
  - `intensite()` : `if (!B.partie || B.interieur) return 0;` ; `operation()` : `if (!B.partie) return null;` ;
    `couverture()` : retirer `!B.options.neige`. En-tête l.11-14 réécrit : « ⚠️ L'HIVER NEIGE POUR TOUT
    LE MONDE (Martin, 29 sept. 2026 : la saison remplace l'option « TEMPÊTES DE NEIGE (ESSAI) ») : une
    tempête tous les `tous_les` soirs, seulement les jours d'hiver du calendrier. »
  - `pont.js` l.29 : retirer `B.options && B.options.neige &&` ; l.12 : « l'hiver du jeu, pour tout le
    monde ».
  - `missions.js` `hiverDeMotoneige` : `return !!(B.partie && Calendrier.saisonDuJour() === 'hiver');`
  - `vehicules.js` l.1059 : `const hiver = Calendrier.saisonDuJour() === 'hiver';`
  - `hud.js` : retirer la ligne `bascule('neige', …)` et son commentaire « M12 ».
  - `base.js` l.70 : retirer `neige: false` ; `jeu.js` l.1413, après l'`Object.assign` :
    `delete B.options.neige;   // l'option n'existe plus : l'hiver neige pour tout le monde (29 sept. 2026)`.
  - Docstrings `app/neige.py` et `app/calendrier.py` : la neige suit l'hiver (plus « derrière son option »).
- [ ] **Étape 4** — `uv run pytest tests/test_neige.py tests/test_neige_js.py tests/test_deneigement.py tests/test_deneigement_js.py tests/test_motoneige_js.py tests/test_pont_de_glace_js.py tests/test_hockey_js.py tests/test_calendrier.py -q`,
  puis `grep -rn "options.neige\|options\['neige'\]" static app tests` : vide. Commit
  `wip: les saisons — la neige suit l'hiver`.

#### Tâche 6 — La longueur du jour

**Fichiers** : `static/js/saisons.js` (`heureDeLumiere`), `static/js/monde.js` (`ambianceVue`,
`estNuitVue`, `lampesVisibles` l.2551, export l.2583), `static/js/jeu.js` (l.1256, l.1263),
`static/js/vehicules.js` (l.3513, l.3589), `static/js/traversier.js` (l.333) ; juge
`tests/test_saisons_lumiere_js.py`.

**Consomme** : `B.defs.saisons.lumiere`. **Produit** : `Monde.ambianceVue()`, `Monde.estNuitVue()`.
⚠️ **Ne passent PAS à la vue** (règles, ou alignées sur une règle) : `barriereFermee`, `police.js`,
`galeries.js`, `entites.js` (434, 775, 2098, 2239, 3487, 5384, 5408), `chantiers.js`, `autobus.js`,
`interactions.js`, `vehicules.js:295`, `missions.js:1377`, `histoire.js`, `cineparc.js`, `infiltration.js`
(le cône suit la vision de la police), `son.js`, `hud.js:3076` (l'icône dit l'heure des règles).

- [ ] **Étape 1 — le juge** :

```python
"""La lumière suit la saison, les règles gardent l'horloge : en décembre il fait noir à 17 h 30, en
juin il fait clair à 21 h ; `Monde.estNuit` (les commerces, la police, les missions) ne bouge pas."""


def test_la_nuit_tombe_plus_tot_en_decembre(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, M = L.Monde, out = {};
        [['decembre', 39], ['juin', 19], ['mars', 10]].forEach(function (m) {
            p.jour = m[1];
            out[m[0]] = [17.5, 21, 12].map(function (h) { p.heure = h / 24; return [M.estNuitVue(), M.estNuit(), M.ambianceVue().alpha]; });
        });
        return out;
    }""")
    assert r["decembre"][0][0] is True, "il ne fait pas noir à 17 h 30 en décembre"
    assert r["juin"][1][0] is False, "il fait noir à 21 h en juin"
    assert r["decembre"][2][2] == 0 and r["juin"][2][2] == 0, "midi n'est plus clair"
    # L'horloge des règles : la même d'un mois à l'autre.
    assert [x[1] for x in r["decembre"]] == [x[1] for x in r["juin"]] == [x[1] for x in r["mars"]]


def test_la_lumiere_glisse_sans_saut_d_un_jour_a_l_autre(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons; let pire = 0, prec = null;
        for (let k = 0; k < 40 * 96; k++) {
            const j = 1 + Math.floor(k / 96), h = (k % 96) / 96, v = S.heureDeLumiere(j, h);
            if (prec !== null) { let d = Math.abs(v - prec); d = Math.min(d, 1 - d); pire = Math.max(pire, d); }
            prec = v;
        }
        return pire;
    }""")
    assert r < 0.03, f"la lumière saute de {r * 24:.2f} h d'un quart d'heure à l'autre"


def test_les_lampadaires_suivent_la_lumiere(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie; p.heure = 17.5 / 24;
        p.jour = 39; const hiver = L.Monde.lampesVisibles().length;
        p.jour = 19; const ete = L.Monde.lampesVisibles().length;
        return { hiver: hiver, ete: ete };
    }""")
    assert r["hiver"] > 0 and r["ete"] == 0
```

  ⚠️ `lampesVisibles` a peut-être des arguments (la vue de la caméra) : lire sa signature l.2549 et
  l'appeler comme `jeu.js` l.1240-1256 le fait.
- [ ] **Étape 2** — rouge.
- [ ] **Étape 3 — le code** :
  - `saisons.js`, remplacer `heureDeLumiere` :

```js
  /** L'heure DE LUMIERE : l'heure de l'horloge fixe (`Monde.TEINTES`) qui a la meme lumiere que
      `heure` ce jour-la. Le jour reel (lever -> coucher, qui suivent l'annee) est etire sur le jour
      de reference (7 h 12 -> 19 h 12), la nuit reelle sur la nuit de reference. Pure et continue :
      l'annee glisse avec `jour + heure`, sans saut a minuit. */
  function heureDeLumiere(jour, heure) {
    const d = donnees();
    if (!d) return heure;
    const l = d.lumiere, x = Calendrier.jourDeLAnnee(jour) + heure;
    const c = Math.cos(2 * Math.PI * (x - l.solstice_ete) / d.annee);
    const lever = l.lever[0] + l.lever[1] * c, coucher = l.coucher[0] + l.coucher[1] * c;
    const rl = l.reference[0], rc = l.reference[1], h = heure * 24;
    let r;
    if (h >= lever && h <= coucher) r = rl + (h - lever) / (coucher - lever) * (rc - rl);
    else {
      const depuis = h > coucher ? h - coucher : h + 24 - coucher, nuit = 24 - (coucher - lever);
      r = rc + depuis / nuit * (24 - (rc - rl));
    }
    return (r % 24) / 24;
  }
```

  - `monde.js`, sous `estNuit` :

```js
  /** La lumiere QU'ON VOIT, qui suit la saison (`Saisons.heureDeLumiere`) : le voile, les lampes,
      les phares. ⚠️ Pour les yeux seulement — les regles lisent `ambiance()` / `estNuit()`, a
      l'horloge fixe : une mission ne change pas d'heure selon le mois. */
  function ambianceVue() {
    if ((carte && carte.interieur) || !B.partie || typeof Saisons === 'undefined') return ambiance();
    return ambiance(Saisons.heureDeLumiere(B.partie.jour, B.partie.heure));
  }
  function estNuitVue() { return ambianceVue().alpha > 0.4; }
```

    exporter `ambianceVue, estNuitVue` l.2583 ; dans `lampesVisibles` (l.2551), `ambiance()` → `ambianceVue()`.
  - `jeu.js` l.1256 et l.1263 : `Monde.ambiance()` → `Monde.ambianceVue()`.
  - `vehicules.js` l.3513 et l.3589 : `Monde.ambiance()` → `Monde.ambianceVue()`.
  - `traversier.js` l.333 : `Monde.estNuit()` → `Monde.estNuitVue()`.
- [ ] **Étape 4** — `uv run pytest tests/test_saisons_lumiere_js.py tests/test_la_nuit_js.py tests/test_saisons_js.py -q`
  puis `uv run pytest tests -q -k "nuit or phare or lampe or traversier"`. ⚠️ Un juge d'avant qui
  regarde la lumière **un jour d'hiver** (le jour 1 d'une partie) à une heure de crépuscule peut
  rougir : il doit poser l'équinoxe (`jour = 10`) s'il juge l'horloge, pas la saison. Commit
  `wip: les saisons — la longueur du jour`.

#### Tâche 7 — La triche « MOIS SUIVANT »

**Fichiers** : `static/js/calendrier.js` (`premierDuMoisSuivant`, `moisEcrit`), `static/js/hud.js`
(`menuDebug`, sous `entete('DIVERS')` l.2565) ; juge dans `tests/test_debug_js.py`.

- [ ] **Étape 1 — le juge** (à la fin de `tests/test_debug_js.py`, même recette que
  `test_argent_et_sante_dans_le_menu_debug`) :

```python
def test_mois_suivant_avance_au_premier_du_mois(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie; p.jour = 5; p.heure = 0.4;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.find(function (i) { return i.libelle === 'MOIS SUIVANT'; });
        const out = [];
        for (let k = 0; k < 13; k++) { item.faire(item); out.push([p.jour, L.Calendrier.mois(p.jour), item.detail]); }
        return { out: out, heure: p.heure };
    }""")
    mois = [m for _, m, _ in r["out"]]
    assert mois[:3] == ["mars", "avril", "mai"] and mois[10] == "janvier" and mois[11] == "fevrier"
    assert r["out"][0][0] == 7 and r["out"][10][0] == 41, "janvier de la deuxième année"
    assert r["out"][0][2] == "MARS" and r["heure"] == 0.4


def test_le_pont_rend_son_eau_apres_un_saut(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie; p.jour = 4; p.heure = 0.5; o.frame(2);
        const avant = L.Pont.froid();
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.find(function (i) { return i.libelle === 'MOIS SUIVANT'; });
        item.faire(item); item.faire(item); L.Hud.fermerMenu && L.Hud.fermerMenu(); o.frame(2);
        return { avant: avant, apres: L.Pont.froid(), jour: p.jour };
    }""")
    assert r["avant"] is True and r["apres"] is False and r["jour"] == 11
```

  ⚠️ Vérifier les noms `Pont.froid` et `Hud.fermerMenu` (`grep -n "froid\b\|return {" static/js/pont.js`,
  `grep -n "fermerMenu" static/js/hud.js`) ; ajouter à la fin du juge ce que `test_pont_de_glace_js.py`
  vérifie pour « l'eau rendue » (les tuiles du chemin redevenues de l'eau), avec la même fonction.
- [ ] **Étape 2** — rouge.
- [ ] **Étape 3 — le code** :
  - `calendrier.js` :

```js
  /** Le jour de partie ou commence le mois qui suit `jour` (janvier de l'annee suivante apres
      decembre). La triche MOIS SUIVANT. */
  function premierDuMoisSuivant(jour) {
    const d = donnees(), j = jourDeLAnnee(jour);
    for (const m of d.mois) if (m[1] > j) return jour + (m[1] - j);
    return jour + (d.annee - j) + 1;
  }

  function moisEcrit(jour) { const m = mois(jour); return m ? ECRITS[m] : ''; }
```

    et les ajouter au `return`.
  - `hud.js`, sous `entete('DIVERS')` :

```js
      // Les saisons se voient sans jouer vingt-six jours (les quatre saisons, lot 1). Un seul
      // `nouveauJour` : la manchette et les effets d'UNE nuit, pas d'un mois.
      { libelle: 'MOIS SUIVANT', detail: Calendrier.moisEcrit(B.partie.jour), faire: function (item) {
        B.partie.jour = Calendrier.premierDuMoisSuivant(B.partie.jour);
        Missions.nouveauJour(); Missions.sauvegarderPartie();
        item.detail = Calendrier.moisEcrit(B.partie.jour);
        return false;
      } },
```

- [ ] **Étape 4** — `uv run pytest tests/test_debug_js.py tests/test_calendrier.py tests/test_pont_de_glace_js.py -q` :
  vert. Commit `wip: les saisons — la triche du mois`.

#### Tâche 8 — Regarder, mesurer, livrer

- [ ] **Les captures** : une capture Chromium par saison (15 janvier, 15 avril, 15 juillet, 31 octobre
  à 18 h, et la même rue), par la recette de la mémoire « Capturer une pièce du jeu » (werkzeug port 0,
  Playwright headless, `B.partie.jour/heure`, `Jeu.rendre()`), copiées dans
  `~/dev/bandini/captures/saisons-*.png` et ouvertes par `open` pour Martin. Regarder : une palette
  ratée, un damier de paliers, un arbre d'hiver illisible — les juges verts ne les voient pas.
- [ ] **Le rythme** : `uv run pytest tests/test_navigateur.py -q -k "rythme or tempete"` ; la tempête est
  maintenant pour tout le monde l'hiver.
- [ ] **La suite ciblée** : tous les fichiers touchés et leurs juges, `test_definitions.py`,
  `test_table_des_jalons.py`, puis `uv run ruff check .` ; atterrir (mémoire « Atterrir avant la suite
  complète »), la suite complète après.
- [ ] **La doc** : sous `### Lot 2 — la pluie et le sol (design approuvé par Martin le 29 sept. 2026)

- **Quand il pleut** (`app/pluie.py`, `static/js/pluie.js`, la recette du brouillard : à l'empreinte du
  jour, jamais au dé) : au printemps et à l'automne, une averse un jour sur deux environ, à une heure et
  pour une durée tirées du jour ; l'été, un soir d'orage sur trois (éclairs et tonnerre). Jamais l'hiver.
  Pour tout le monde, sans option (comme la neige).
- **Ce qu'on voit** : la pluie en traits obliques et un voile gris léger, plus dense à l'orage, avec un
  flash blanc bref à l'éclair. Toute la chaussée est mouillée pendant l'averse et sèche une heure après
  (le reflet de l'arroseuse). Des **flaques** sur les rues et les trottoirs, à l'empreinte de la tuile,
  qui restent un peu après la pluie et rapetissent.
- **Ce qu'on sent** : la rue mouillée glisse comme celle de l'arroseuse (0,8) et freine plus long ; au
  sec, rien ne change. Un char qui passe dans une flaque éclabousse (gouttes, son) ; un passant tout près
  proteste.
- **La fonte d'avril** (jours 11 à 13 — avril commence au jour 11) : de la gadoue brune au bord des rues et sur les trottoirs, qui
  glisse un peu. Les bancs de neige sales viendront avec les bancs de neige (lot 4).
- **Les feuilles d'octobre** : un char qui roule en soulève derrière lui (bornées) ; mouillées, elles
  glissent un peu plus.
- **Le son** (ElevenLabs) : une boucle de pluie en fondu enchaîné, deux tonnerres, une éclaboussure.
- **Pas dans ce lot** : les parapluies (lot 4), l'ambiance par saison (lot 5), le vrai dérapage (lot 6).
- **Juges** : jamais de pluie l'hiver, la même pour tout le monde ; mouillé glisse, sec ne change rien ;
  aucun dé, rien de posé ; une flaque éclabousse ; des feuilles seulement l'automne ; le rythme sous
  l'orage ; des captures sous la pluie.

### Lot 3 — l'Halloween (design approuvé par Martin le 29 sept. 2026)

- **Le décor, tout octobre** (`app/halloween.py`, `static/js/halloween.js`, la recette des Fêtes) : une
  citrouille sur le perron d'une maison sur trois environ, à l'empreinte de la maison — PEINTE, jamais
  posée ; la nuit, elle s'allume (sa lueur orange). **Le soir du 31** (jour 33), les fenêtres prennent des
  lumières orange et violettes. Le Clairon, la veille : « C'EST L'HALLOWEEN DEMAIN SOIR : ATTENTION AUX
  PETITS MONSTRES. »
- **Les gens, le 31 dès 16 h** : un passant sur trois est déguisé (sorcière, fantôme, squelette,
  citrouille — à l'empreinte du passant, des pièces neuves de la garde-robe) ; des bandes de deux ou trois
  enfants déguisés, un sac orange à la main, vont de porte en porte dans les quartiers de maisons et disent
  « DES BONBONS! » aux portes qui ont leur citrouille — bornées, pour le rythme.
- **La maison hantée** (plutôt qu'un défi) : le 31, de 18 h à minuit, un logement des Érables (une maison
  qu'on visite déjà, choisie une fois pour toutes, sans pièce neuve), sa porte marquée d'une grosse
  citrouille. Dedans, la recette des Galeries : les lumières s'éteignent une à une, un fantôme apparaît et
  s'évanouit, une voix chuchote ; au fond, le sac de bonbons vaut une prime, une fois par année.
- **Le son** : une musique d'Halloween (ElevenLabs) en fondu enchaîné, dehors le soir du 31 ; un rire de
  sorcière, une porte qui grince, un souffle de fantôme (chargés le 31 seulement) ; les voix de la maison.
- **Juges** : le décor en octobre seulement, les lumières et les déguisés le 31 seulement ; aucun dé, rien de
  posé, la ville ne bouge pas ; la maison hantée seulement le 31 au soir, le sac paie une fois ; les enfants
  bornés ; captures du soir du 31 et la sonde du rythme.

### Lot 6 — la glace et le vrai dérapage (design approuvé par Martin le 29 sept. 2026)

Trois vagues jouables. ⚠️ **La règle d'or : au sec, la conduite ne change pas d'un pixel** — le nouveau
modèle ne s'éveille que sous une adhérence de 1 (neige, glace, pluie, gadoue, feuilles).

- **Vague 6a — le dérapage** (les chars du joueur, de la police, des missions) : le **sous-virage** (lancé
  sur la glace, le volant mord moins, tout droit), le **survirage** (le frein à main en courbe ou trop de gaz
  en tournant font partir l'arrière ; laissé faire, le **tête-à-queue**), le **contre-braquage** qui rattrape
  (au clavier comme à la manette), les **roues bloquées** (frein à fond sur la glace : le volant ne dirige
  plus) ; les **pneus d'hiver** de Ti-Guy en rendent une vraie part. Le sol le montre (des traces noires au
  sec, des sillons dans la neige, bornées, qui s'effacent) et l'oreille l'entend (le crissement au sec, le
  silence sur la glace).
- **Vague 6b — la glace** : de la glace noire l'hiver (sur les ponts, et sur des tuiles de rue à
  l'empreinte), le gel et le dégel au printemps (la glace le matin, fondue l'après-midi) ; un passant qui
  court sur la glace glisse et tombe, le joueur compris. **Le verglas** : son option disparaît, comme celle de
  la neige, et il tombe les derniers jours de mars, pour tout le monde (Martin, 29 sept. 2026).
- **Vague 6c — la ville glisse aussi** : un char du trafic qui freine sur la glace glisse un peu et finit
  ARRÊTÉ, jamais perdu hors de sa voie (pas de glissade pour la police en pleine poursuite) — _fait avec la 6b, le
  1er oct. 2026 (sur ses rails)_ ; les bancs de neige (lot 4) enlisent — les roues patinent, on recule, on repart.
- **Les courses et les défis chronométrés** d'un jour d'hiver deviennent plus durs : gardé (Martin) ; les
  records déjà battus restent.
- **Juges** : au sec, la même trajectoire au pixel que l'ancien modèle ; sur la glace, un char lancé en courbe
  sous-vire, le frein à main en courbe fait partir l'arrière, le contre-braquage rattrape et les pneus d'hiver
  rattrapent mieux ; des roues bloquées ne dirigent pas ; un passant qui court sur la glace tombe ; un char de
  la ville qui glisse finit arrêté, jamais perdu.

## Notes` de ce fichier, « Lot 1 livré le … » (ce qui est fait, ce qui ne l'est
  pas, les juges et leurs mutations) ; la cellule du plan : « ✅ lot 1 livré : … ; lot 2 à faire : la
  pluie et le sol » ; `docs/architecture.md` (tâches 1-2). La ligne reste ⬜ **en cours** (cinq lots
  restent).

### Lot 6, vague 6c — les bancs de neige qui enlisent (design du 1er oct. 2026)

_Demandé par Martin le 1er oct. 2026 : un char qui fonce dans un banc de neige ralentit fort, peut rester pris (les
roues patinent, la neige gicle), et s'en sort en marche arrière, en berçant, ou avec un 4 roues ; la motoneige y
passe ; les bancs grossissent avec les tempêtes et fondent au dégel ; la police et le trafic ne s'y jettent pas
exprès ; le dessin des bancs (4b) cohérent avec leur physique._

- **Le banc chevauche la bordure** : peint en 4b DANS la rue (3 à 6 px), il mangeait la voie — une voie a 16 px, un
  char 14, ses roues passent à 3 px de la bordure. Il se peint maintenant à cheval sur la bordure : une lèvre dans la
  rue (au plus 3 px : les roues d'un char au milieu de sa voie ne la touchent jamais) et le gros sur le bord du
  trottoir. La physique lit le MÊME profil (une fonction pure, partagée par le dessin et la conduite) : là où il est
  peint, il tient ; là où il ne l'est pas, rien.
- **Ce qu'il fait aux roues** (les quatre roues du char, pas sa carrosserie qui le surplombe) : effleuré de côté, il
  freine un peu et la neige gicle ; abordé lentement, il retient (on le monte au pas, jamais on ne reste bloqué
  devant un trottoir) ; abordé vite (la vitesse VERS le banc, pas le long), le char s'y plante — **pris** : les roues
  patinent, la neige gicle, le moteur s'emballe. On s'en sort en **marche arrière** (lentement), en **berçant**
  (avancer, reculer, avancer : chaque aller-retour en rythme compte plus), ou on ne s'y prend pas du tout en **4 roues**
  (et en camion lourd : ils poussent la neige, plus lents). La **motoneige** et les coques n'en savent rien.
- **Le calendrier** (pure fonction du jour et de l'heure, aucun dé) : la grosseur suit la neige qui tient (4b) et
  **grossit à chaque tempête** de l'hiver (la charrue repousse la neige au bord), jusqu'à un plafond ; au **dégel**,
  elle fond avec la palette. Les morceaux se repeignent quand la grosseur change de palier, pas à chaque image.
- **La ville** : le trafic est sur ses rails, au milieu de sa voie — il ne touche jamais un banc. L'IA hors des rails
  (la police, les poursuivants) y perd de la vitesse mais n'y reste jamais prise : elle ne s'y jette pas exprès, et
  elle en ressort.
- **Juges** : le profil du dessin et celui de la conduite sont le même ; au milieu de sa voie, rien ; foncer y
  plante le char (plusieurs graines de départ, plusieurs bancs) ; la marche arrière en sort, le bercement plus vite ;
  le 4 roues et la motoneige passent ; l'IA n'y reste pas ; les bancs grossissent aux tempêtes et fondent au dégel ;
  aucun dé, rien de posé ; au sec et l'été, la conduite au pixel. Mesure A/B appariée ; captures (pris de jour, de
  nuit, la neige qui gicle).

### Lot 4 — les gens et la rue (découpé le 29 sept. 2026, en deux vagues)

_Le lot 3 (l'Halloween) avance dans une autre session ; le lot 4 ne touche pas à ses fichiers
(`halloween.*`) et se greffe à côté de son déguisé dans `Entites.imageDe` (le déguisement du 31 passe
AVANT la saison : une sorcière n'enfile pas de manteau par-dessus sa robe). L'ordre de Martin tient : la
glace et le dérapage (lot 6) restent en dernier, à part._

**Vague 4a — la garde-robe des saisons, et le parapluie** (la plus visible, zéro physique) :

- **Le froid du moment** (`froid`, une valeur de plus dans chaque palette de `app/saisons.py` : 1
  l'hiver, 0,65 en novembre, 0,45 au printemps, 0,4 à l'automne, 0,1 en août, 0 en juillet) glisse
  en huit paliers comme le reste. Chaque passant est plus ou moins **frileux**, à l'empreinte de sa
  tenue : le froid qu'il sent = `froid + (frileux − ½) × 0,3`. Personne ne change d'habit d'un coup
  à minuit, et tout le monde ne se couvre pas le même jour.
- **L'habit du moment** (`Saisons.vetir(tenue, passant)`, pure, mémorisée par tenue et par palier) :
  la tenue TIRÉE ne change pas (le tirage, les couleurs, `e.swaps`, la sauvegarde : rien) ; c'est
  l'image qui s'habille. Au grand froid : **manteau** (de la couleur du haut : le gang et l'uniforme
  restent reconnaissables), pantalon, **bottes**, **tuque** (sauf un chapeau d'uniforme : képi, casque
  de chantier, casquette du garde et du livreur, bandeau des Mantes), et un **foulard** pour les
  frileux. À mi-saison fraîche : le coton ouaté ou le chandail au lieu du t-shirt, plus de short. L'été
  : **t-shirt** au lieu du manteau, la tuque tombe, des **shorts**, les souliers au lieu des bottes
  (sauf les bottes de travail). Le tablier, le sarrau, la veste de travail et la veste de kung-fu
  restent. **Dedans** (une pièce), on garde l'habit de base : on a enlevé son manteau.
- **Sous la pluie** (`Pluie.intensite()`), un passant sur deux environ ouvre un **parapluie** de la
  couleur de son accent (peint par-dessus sa tête, cuit une fois par couleur) ; les autres remontent
  leur **capuche**. Un passant qui court, se bat ou fuit le referme.
- **Ni les personnages ni le joueur** ne changent : on les reconnaît à leur tenue (Martin tranchera
  s'il veut Marco en tuque).
- **Juges** : un passant de janvier porte un manteau, des bottes et une tuque ; un passant de juillet,
  jamais de manteau ni de tuque ; l'uniforme et le gang gardent leur couleur et leur chapeau ; la tenue
  tirée n'est pas touchée et aucun dé n'est tiré ; le passage de novembre à l'hiver est graduel (pas
  une coupure) ; dedans, l'habit de base ; le parapluie sous la pluie seulement, jamais au sec ; la
  sonde du rythme en foule, en janvier et sous l'averse ; des captures de chaque saison, le jour et la
  nuit.

**Vague 4b — la rue** (du décor PEINT, jamais posé : la ville ne bouge pas) :

- **Les bancs de neige** le long des trottoirs, tant que la neige tient, que la charrue laisse (peints
  dans la tuile de rue au bord du trottoir, à l'empreinte ; sales et plus bas au dégel) ;
- **la fumée des cheminées** l'hiver sur les toits des maisons (la recette du chalet, `Blocs.FUMEE`,
  pure fonction du temps, bornée à l'écran) ;
- **les abris Tempo** dans les entrées de novembre à avril (à l'empreinte de la maison, s'il y a une
  entrée à côté) ;
- **les terrasses** l'été devant les restos et les bars (tables et parasols peints sur le trottoir).
- Plus de passants dehors l'été : ⚠️ touche au dé de `peupler` — à mesurer contre les juges avant de le
  promettre ; sinon, ça tombe.

### Lot 5 — le son des saisons (29 sept. 2026)

- **Quatre ambiances** (ElevenLabs, des boucles de dix secondes, `LIEUX["saisons"]`) : l'hiver, le vent
  froid qui siffle entre les maisons et une charrue qui gratte au loin ; le printemps, l'eau de fonte qui
  coule dans les gouttières et les merles ; l'été, les cigales et une tondeuse au loin ; l'automne, le vent
  dans les feuilles sèches et les outardes qui passent. Août sonne comme l'été, novembre comme l'automne.
- **En fondu enchaîné** : le volume de chaque ambiance suit la palette du moment — pendant une transition,
  l'une descend pendant que l'autre monte, palier par palier, et le volume glisse d'une image à l'autre
  (jamais une coupure). Une pure fonction du jour et de l'heure, aucun dé.
- **Discrètes** : sous la musique du district, plus basses la nuit, presque couvertes sous la pluie et la
  tempête (qui ont leur boucle), muettes dedans.
- **Juges** : la bonne ambiance à chaque saison, le fondu sans saut (d'une image à l'autre et d'un palier à
  l'autre), le silence dedans, aucun dé ; les sons au paquet (le poids).

### Lot 4, vague 4c — les restes (tranché par Martin le 29 sept. 2026)

- **Le plafond des sons de lieu à 1,35 Mo** : validé par Martin.
- **Les personnages et le joueur s'habillent selon la saison, DEHORS seulement** (« il change juste à
  l'extérieur ») : dans une pièce, leur tenue de tous les jours. Un manteau et une tuque dans LEUR palette
  (on les reconnaît) ; le visage des dialogues ne change pas. Rien au dé.
- **Terrasses et Tempo solides** : on ne marche plus sur les tables des terrasses ; les chars ne passent plus
  sous les abris Tempo (les piétons, oui : c'est un abri). Ils existent selon la saison : leur collision
  apparaît et disparaît avec eux, sans décaler la ville ni aucun dé ; personne coincé dedans au changement
  de saison ; aucun donneur ni aucune porte bloqués.
- **Les enfants habillés** selon la saison.
- **Des manteaux d'hiver de vraies couleurs** : foncés et variés (marine, noir, bourgogne, forêt, brun…),
  plus la reprise pastel de la couleur du haut ; à l'empreinte.
- **Les bornes-fontaines ouvertes l'été** : quelques-unes les jours de chaleur, un jet d'eau dessiné, des
  enfants qui jouent autour, le son de l'eau (ElevenLabs, un lieu chargé à la demande) ; à l'empreinte,
  rien de posé.

## Notes

### Lot 1 — le paysage des quatre saisons (livré le 29 sept. 2026)

- **La palette du moment** (`app/saisons.py`, `static/js/saisons.js`) : six palettes (hiver, printemps,
  été, fin d'été, automne, novembre) et les images-clés de l'année ; une transition glisse en huit
  paliers sur un jour et demi à deux jours. L'Halloween (jour 33) est en plein rouge.
- **Ce qui la lit** : tout ce qui peint du gazon (`gazonDuMoment` — la pelouse, la bande devant les
  maisons, le pied des clôtures, le tour de la piscine ; la relecture a trouvé les trois derniers, restés
  vert d'été dans une ville blanche), la friche, les trottoirs et les toits (`Saisons.enneiger`, la neige
  qui tient l'hiver), et l'arbre de rue — trois teintes à l'empreinte de sa tuile (`variantes`, sans dé :
  jugé en deux bancs, avec et sans), érables rouges, orange et jaunes en octobre, branches nues poudrées
  l'hiver. L'été, c'est la ville d'avant, au pixel.
- **Le cache** : `Monde.dessinerSol` jette les tuiles cuites et les arbres de l'atlas (`Atlas.oublier`)
  quand la clé de palier change — une clé pour l'atlas, une par carte pour ses morceaux (une pièce
  traversée, une carte qui naît). L'image du changement coûte 3,8 ms contre 0,6 (Chromium, Mac).
- **La neige suit l'hiver, l'option a disparu** : une tempête tous les trois soirs, les jours d'hiver
  seulement, pour tout le monde ; la motoneige, le pont de glace et le hockey suivent l'hiver ; une vieille
  sauvegarde qui avait l'option la perd au chargement. Le rythme en pleine tempête : 1,8 ms par image.
  ⚠️ Une partie neuve a donc sa première tempête le soir du jour 2.
- **La longueur du jour** (`Saisons.heureDeLumiere`, `Monde.ambianceVue`) : le voile, les lampadaires,
  les phares, les feux et le traversier suivent la saison — noir vers 17 h 30 en décembre, clair à 21 h
  en juin. Les **règles** gardent l'horloge fixe (`ambiance(h)`, `estNuit`, `periode`) : commerces,
  barrières, police, missions, l'icône du HUD.
- **La triche MOIS SUIVANT** (TRICHES › DIVERS) : au premier du mois suivant, à la même heure, un seul
  `nouveauJour`.
- **Juges** : `test_saisons.py`, `test_saisons_js.py`, `test_saisons_sol_js.py`, `test_saisons_arbres_js.py`,
  `test_saisons_lumiere_js.py`, et dans `test_neige_js.py`, `test_debug_js.py` ; chacun vu rougir sous sa
  mutation. Réécrits : les juges « sans l'option » de la neige, du déneigement, de la motoneige, du pont
  et du hockey (un soir au rythme, en juillet) ; `test_quartiers` et le faisceau de `test_la_nuit_js`
  posent l'été ou fin septembre (ils jugent le quartier et l'horloge, pas la saison).
- **La mini-carte** (et la carte ouverte) : l'herbe prend la couleur `mini` de la palette — blanche
  l'hiver, rousse en octobre, le vert d'avant l'été (Martin : « corrige la mini carte »). Le fond et le
  masque de l'herbe se cuisent une fois (12 ms) ; au palier, on ne fait que reteindre (moins d'une ms).
- **Pas fait, à dire** : les buissons restent verts l'hiver ; les pavés de l'abord et
  les toits des cabanes ne prennent pas la neige ; l'icône du HUD montre le soleil sous le voile d'un
  17 h 30 de décembre — **voulu, tranché par Martin le 29 sept. 2026 : elle dit l'heure des règles** ; le verglas garde son option et son jour d'avril
  (lot 6).

### Lot 2 — la pluie et le sol (livré le 29 sept. 2026)

- **Le temps qu'il fait** (`app/pluie.py`, `static/js/pluie.js`) : une averse un jour sur deux environ au
  printemps et à l'automne (entre 6 h et 16 h, de deux à sept heures), un orage un soir sur trois l'été
  (entre 16 h 30 et 23 h), jamais l'hiver — à l'empreinte du jour, pour tout le monde, sans option.
- **La rue mouillée** : pendant l'averse et une heure après, l'adhérence tombe à 0,8 (0,75 sur les feuilles
  mouillées, quand il y en a au sol), le freinage à 0,85, le trafic lève le pied de 10 %. Au sec : 1,
  exactement. Derrière l'arroseuse sous la pluie, les deux s'ajoutent (0,64) — laissé ainsi.
- **À l'écran** : les traits de pluie et le voile gris, plus denses à l'orage ; l'éclair par-dessus la nuit
  (la relecture l'a trouvé terne, peint dessous) ; le reflet de la rue mouillée ; les **flaques** (3,5 % des
  tuiles de rue et de trottoir, à l'empreinte), qui durent trois heures et rapetissent ; la **gadoue**
  d'avril (jours 11 à 13) sur les trottoirs et au bord des rues, qui glisse un peu (0,9).
- **Les chars** : dans une flaque, au-dessus de 1,2, un char éclabousse (gouttes, son) et le passant le plus
  proche proteste — jamais le passager du char, un passant assommé, ni quelqu'un qui parle déjà. En octobre
  et novembre, un char lancé soulève des feuilles derrière lui.
- **Le son** (ElevenLabs, 296 crédits) : une boucle de pluie de 8 s (en fondu, son volume suit l'averse —
  la relecture l'a trouvée figée presque muette, corrigé), deux tonnerres qui suivent l'éclair après un
  délai, une éclaboussure ; un groupe `LIEUX["pluie"]` chargé à la première averse (demandé une fois toutes
  les 300 images, pas à chaque image). Le tonnerre et l'éclaboussure ont leur synthèse de repli.
- **Le rythme** : 2,2 ms par image en plein orage (Chromium, comme la nuit).
- **Juges** : `test_pluie.py`, `test_pluie_js.py` (19 juges), la sonde `test_l_orage_tient_le_rythme` ;
  chacun vu rougir sous sa mutation (garde d'hiver, physique, appel dans `vehicules.js`, tonnerre, volume).
- **Pas fait, à dire** : la boucle de pluie n'a pas de synthèse de repli (hors ligne à la première averse, la
  pluie est muette) ; les parapluies (lot 4) ; l'ambiance par saison (lot 5).

### Lot 3 — l'Halloween (livré le 29 sept. 2026)

- **Le décor** (`app/halloween.py`, `static/js/halloween.js`) : tout octobre, une citrouille sur le perron
  d'un logement sur trois (à l'empreinte du logement, PEINTE et triée avec les gens), allumée la nuit avec
  sa lueur ; le soir du 31 dès 16 h, les fenêtres et les vitrines en orange et violet ; le Clairon la veille.
  Le 31 est maintenant une date du calendrier (`calendrier.DATES["halloween"]`, jour 33).
- **Les déguisés** : dès 16 h le 31, un passant sur trois (à l'empreinte de son numéro, jamais un membre de
  gang ni un personnage) sort en sorcière (chapeau pointu, une pièce neuve), fantôme (la capuche, la robe et
  la peau blanches), squelette (le motif « os », neuf) ou citrouille. ⚠️ Les pièces de costume sont
  dessinées dans `garderobe.js` mais JAMAIS mises dans les listes du tirage (`app/garderobe.py`) : une pièce
  de plus y changerait la tenue de tout le monde.
- **Les enfants** : de 17 h à 21 h 30 le 31, dans les Érables, La Pointe et le Faubourg, jusqu'à quatre bandes
  de deux ou trois enfants déguisés (par leurs couleurs : l'enfant est dessiné à la main) naissent hors de
  l'écran au pied d'une citrouille, vont de citrouille en citrouille (l'état `cap` du camelot, les autres
  suivent le chef comme le petit suit sa mère) et disent « DES BONBONS! » ; ils rentrent hors de l'écran après
  l'heure. Pas de sac orange dessiné.
- **La maison hantée** : le plus grand logement des Érables (le premier venu faisait six tuiles sur cinq),
  sa porte marquée d'une grosse citrouille tout octobre. Le 31 de 18 h à minuit : la porte grince, les
  lumières s'éteignent une à une, un fantôme se montre et s'évanouit quand on l'approche, une voix chuchote
  (« Dr. Von Fusion - VF », réservée), et le sac de bonbons au fond paie 150 $ une fois par année. L'habitant
  du logement y reste planté — laissé.
- **Le son** : la musique d'Halloween (45 s, ElevenLabs, avec son jumeau en notes) dehors dès 18 h le 31, à la
  place de celle du district ; le rire d'une sorcière qui passe (au plus une fois aux dix secondes), la porte
  qui grince, le souffle du fantôme (`LIEUX["halloween"]`, chargés le 31) ; cinq murmures.
- **La relecture** (un agent neuf) a trouvé, et c'est corrigé : les policiers, les vigiles, les commis et
  les gens d'une mission se déguisaient (un agent en sorcière en pleine poursuite) ; une bande que la ville
  retirait au loin gardait sa place et plus aucun enfant ne naissait ; l'invite « (ACTION) » du sac était
  écrasée par le murmure ; la maison restait hantée à l'étage ; une partie qui démarre au chalet perdait la
  maison ; deux citrouilles à sa porte ; la lueur sur un lot démoli ; la musique dans les blocs ; un rire aux
  dix secondes (maintenant 25). `B.partie.halloweenAn` est une clé de sauvegarde neuve : « une fois par
  année » demande de s'en souvenir.
- **Le rythme** : 2,0 ms par image le soir du 31 dans les Érables (Chromium).
- **Juges** : `test_halloween.py` (5), `test_halloween_js.py` (18), la sonde `test_le_soir_de_l_halloween_tient_le_rythme`.

### Lot 4, vague 4a — la garde-robe des saisons et le parapluie (livrée le 29 sept. 2026)

- **L'habit du moment** (`Saisons.vetir`, appelé par `Entites.imageDe`) : la tenue TIRÉE ne change pas
  (ni le tirage, ni `e.swaps`, ni la sauvegarde) ; l'image s'habille selon le **froid** de la palette
  (1 l'hiver, 0,65 en novembre, 0,45 au printemps, 0,4 à l'automne, 0,1 en août, 0 l'été — il glisse en
  paliers) et la **frilosité** du passant, à l'empreinte de sa tenue. En janvier : **manteau** (de la
  couleur du haut), pantalon, **bottes**, **tuque** et, pour les frileux, un **foulard** ; en novembre et
  au printemps, le coton ouaté au lieu du t-shirt, plus de short ; en juillet, **t-shirt**, **short** pour
  qui en porte, plus de tuque ni de manteau. Le tablier, le sarrau, la veste de travail et la veste de
  kung-fu restent ; le képi de l'agent, la casquette du garde et du livreur, le bandeau des Mantes aussi
  (et pas de foulard sur un uniforme). Dedans, on a enlevé son manteau. Les personnages et le joueur ne
  changent pas.
- **Sous la pluie** : un passant au pas sur deux environ ouvre un **parapluie** de sa couleur d'accent
  (cuit une fois par couleur, peint par-dessus sa tête) ; qui court, se bat ou fuit le referme ; les
  frileux sans parapluie remontent leur **capuche**.
- **Le rythme** : 2,8 ms par image pour soixante passants sous l'averse (vingt-huit parapluies), 2,8 ms
  sans l'habit du moment (Chromium, Mac ; `test_la_foule_des_saisons_tient_le_rythme`). L'habit se calcule
  une fois par tenue et par palier, le moment une fois par image.
- **Juges** : `test_saisons_habits_js.py` (7 juges : janvier et juillet, l'uniforme et le gang, pure et
  sans dé, de novembre à l'hiver peu à peu, `imageDe` dessine l'habit, le parapluie, la capuche) ; chacun vu
  rougir sous sa mutation (14 mutations : l'habit inerte, sans bottes, froid nul, sans uniforme, sans
  métier, habillé dedans, parapluie en courant, tous aussi frileux, `imageDe` sans saison, parapluie pas
  peint, personnage habillé, capuche sous le parapluie, jamais de pluie, pas de short).
- **Captures** (`captures/saisons-habits-*.png`) : la planche des douze mêmes passants en janvier, avril,
  juillet, octobre et novembre ; la rue à midi et le soir, l'averse et ses parapluies.
- **L'Halloween** (lot 3, une autre session) : son déguisé du 31 passe AVANT la saison dans `imageDe` —
  une sorcière n'enfile pas de manteau — branché à l'atterrissage du lot 3 (`Entites.imageDe` : le costume d'abord, sinon l'habit du moment).
- **Pas fait, à dire** : le manteau reprend la couleur du haut (un manteau pastel l'hiver) — lisible,
  mais pas « un manteau d'hiver » ; les mitaines et les bottes d'hiver ne se voient pas à cette taille ;
  les enfants (dessinés à la main, sans garde-robe) ne s'habillent pas ; le joueur non plus.

### Lot 4, vague 4b — la rue des saisons (livrée le 29 sept. 2026)

- **Tout est peint, rien n'est posé** (`static/js/rue_des_saisons.js`, les données dans `saisons.RUE`) :
  aucune tuile, aucun décor, aucun identifiant, aucun dé ; la ville ne bouge pas d'un octet. Bancs, Tempo
  et terrasses se peignent dans les morceaux cuits (`Monde.peindreDevantures`) et ne lisent que la
  palette du moment : ils se repeignent au palier avec le gazon, jamais à chaque image.
- **Les bancs de neige** : dans la rue, le long de chaque trottoir (jamais sur une traverse, une entrée,
  une ruelle ou un rail), tant que la neige tient ; leur largeur suit la neige (3 à 6 px), leur profil une
  houle continue d'une tuile à l'autre (au hasard pur, il faisait un peigne — vu sur la capture) ; au
  dégel, ils rapetissent et se salissent de gravier.
- **Les abris Tempo** (22 dans la ville) : dans l'entrée de stationnement qui longe une maison (quatre
  sur cinq, à l'empreinte) et devant le rideau d'un garage de maison ; montés dès novembre (froid ≥ 0,5),
  démontés au dégel quand la neige a fondu de moitié. Un char passe dessous comme avant (peints au sol).
- **La fumée des cheminées** (les `cheminee` des toits) : dès novembre, une part des cheminées égale au
  froid (toutes en janvier) ; des bouffées grises qui montent et dérivent vers l'est, d'après `B.t`, pour
  les morceaux à l'écran seulement.
- **Les terrasses** (34) : l'été, sur le trottoir devant les restos et les bars (`bouffe`, `nuit`), une
  table ronde et deux chaises par tuile, un parasol rayé sur deux ; jamais devant une porte ni sur du
  décor (banc, poubelle, lampadaire). Les passants marchent par-dessus (peintes au sol).
- **Le rythme** : 1,7 à 2,0 ms par image en janvier sous quatre cheminées qui fument ; la repeinte de
  tous les morceaux à l'écran (un changement de palier) : 4,3 ms avec la rue des saisons, 2,6 ms sans
  (Chromium, Mac ; `test_la_rue_d_hiver_tient_le_rythme`). Les tuiles à banc se cherchent une fois par
  morceau et par carte.
- **Juges** : `test_saisons_rue_js.py` (5 juges : les bancs, les Tempo, les terrasses, la fumée, rien de
  posé ni tiré et le rendu qui passe par la rue) ; 21 mutations, toutes rouges (bancs toujours, sur une
  traverse, dans les entrées, dégel propre, Tempo jamais démonté, Tempo l'été, Tempo sur le gazon,
  terrasses l'hiver, devant la porte, sur le décor, partout, fumée en octobre, toutes les cheminées, fumée
  au dé, rue et fumée débranchées…). Deux mutations n'ont d'abord rien dit (la fumée et la rue
  débranchées du rendu, un garde de fumée redondant) : le juge « rien de posé » épie maintenant le rendu.
- **Captures** (`captures/saisons-rue-*.png`) : les maisons, un resto et des cheminées en janvier (le
  jour et le soir), au dégel, en juillet (le jour et le soir) et en novembre.
- **Pas fait, à dire** : les passants marchent sur les tables des terrasses et les chars roulent sous les
  Tempo (peints au sol, ils ne bloquent rien — les poser déplacerait la ville) ; pas de char garé sous
  un Tempo ; les bancs n'ont pas de trouée devant les entrées de stationnement ; plus de passants dehors
  l'été : **tombé** (il touchait au dé de `peupler`) ; les bornes-fontaines ouvertes de l'été : pas faites.

### Lot 4, vague 4c — les restes (livrée le 29 sept. 2026)

- **Le plafond des sons de lieu** (1,35 Mo) : validé par Martin, écrit dans le juge
  (`test_le_poids_audio_reste_raisonnable`). Les lieux pèsent maintenant 1,31 Mo avec la borne.
- **Les personnages et le joueur s'habillent DEHORS** (`Saisons.vetir`) : du côté du froid seulement — au
  grand froid un manteau de LEUR couleur (jamais un manteau foncé de passant), des bottes, une tuque de la
  couleur de leur bas (un képi, un feutre restent), le foulard des frileux ; à la mi-saison, les manches
  longues. Dedans, et l'été, leur tenue de tous les jours, telle quelle. Le portrait des dialogues ne change
  pas. Le joueur 2 de la coop (dessiné à la main, sans tenue) ne change pas.
- **Des manteaux d'hiver de vraies couleurs** (`saisons.HABITS["manteaux"]`) : au grand froid, 65 % des
  passants (à l'empreinte de la tenue) portent un manteau foncé — marine, noir, bourgogne, forêt, brun,
  charbon, bleu, rouille, aubergine, kaki ; les autres reprennent la couleur de leur haut. Jamais un gang ni
  un uniforme (`haut_fixe`).
- **Les enfants habillés** (`SPRITES.enfant.saisons`, lus par `Saisons.ficheDuMoment`) : deux habits tirés de
  ses poses lettre par lettre — les manches longues au frais (novembre, le printemps, l'Halloween), l'habit
  de neige au grand froid (la tuque au pompon blanc de la couleur de son manteau, les mitaines de celle de
  son pantalon). Ses couleurs à lui restent (`e.swaps`) ; dehors seulement. La tuque était d'abord de la
  couleur du pantalon : sur un pantalon noir, elle disparaissait dans le contour (vu à la capture).
- **Terrasses et Tempo solides** (`RueDesSaisons.tempoBloque`, `RueDesSaisons.bloquer`) : un char n'entre
  plus sous un Tempo monté (par `Monde.barriereBloque` : le pas, le trafic, la route) ; un piéton y passe. On
  bute sur la table et les chaises d'une terrasse l'été (par `Entites.bloquerParDecor`, comme la calèche).
  Rien de posé : la collision se lit dans `lieux(carte)` et la palette, comme le dessin. **Personne n'y
  reste pris** : un char déjà sous un Tempo quand on le monte en sort (le Tempo ne l'arrête que s'il n'y est
  pas déjà) ; quand les tables sortent, qui s'y tenait est poussé au sud, sur le trottoir, jamais vers la
  façade. **Aucun Tempo devant une cachette de bungalow** (`portes_garage`) : cinq en avaient un, retirés —
  il en reste 17. Aucune table devant ni à côté d'une porte, aucun donneur sur une terrasse.
- **Les bornes-fontaines ouvertes de la canicule** (`saisons.RUE["bornes"]`) : les jours de chaleur de l'été
  (six sur dix environ, à l'empreinte du jour, jamais sous la pluie), de 11 h à 19 h 30, une borne sur sept
  environ crache vers la rue (à l'empreinte de la borne et du jour) : le jet de gouttes qui monte et retombe,
  la flaque qui brille, et trois enfants en maillot qui courent dans l'eau et sautent — triés avec les gens.
  Quand un char roule à côté, ils remontent sur le trottoir derrière la borne et attendent. Tout est peint
  d'après `B.t` : ni entité, ni dé. Le son : une boucle ElevenLabs (`borne_ete`, 8 s, 65 Ko, **340
  crédits**), l'eau sur l'asphalte et les enfants qui crient de joie, plus forte en approchant, muette
  dedans, un lieu chargé à la demande. Le geste « FERMER LA BORNE » répond « LES ENFANTS JOUENT : ON LA
  LAISSE COULER », et l'eau rend le souffle comme une borne qu'on ouvre soi-même.
- **La ville d'avant ne bouge pas** : `carte.generer()` en JSON, avant et après, identiques à l'octet
  (772 Ko) ; aucune entité née, aucun dé tiré (jugé).
- **Le rythme** (Chromium, Mac, machine chargée) : un jour de canicule (15 bornes ouvertes dans la ville),
  1,9 ms par image ; le rendu 1,27 ms avec la borne et ses enfants à l'écran, 1,24 ms sans
  (`test_la_canicule_tient_le_rythme`). En janvier, 2,3 ms par image ; la foule des saisons, 3,1 ms.
- **Juges** : `test_saisons_habits_js.py` (3 de plus : les personnages et le joueur dehors, les manteaux
  foncés, les enfants), `test_saisons_rue_js.py` (8 de plus : les tables, le passant qui en sort, les Tempo
  au volant, portes et garages, les bornes du jour de chaleur, la borne peinte sans rien poser, les enfants
  prudents, le son, le geste et le souffle), la sonde `test_la_canicule_tient_le_rythme`. **34 mutations**, 33 rouges ; la 34e (retirer le garde « un char seulement » de `tempoBloque`) est équivalente — `Monde.barriereBloque` ne l'appelle que pour un char. Une mutation est d'abord restée verte : le Tempo qui bloque aussi le char déjà dessous — le garde-fou des murs le SAUTAIT dehors ; le juge suit maintenant le char image par image (il sort en roulant, sans bond).
- **Captures** (`captures/saisons-restes-*.png`) : la planche des personnages et du joueur (janvier dehors,
  janvier dedans, juillet), les manteaux de janvier, les enfants (juillet, novembre, janvier), Marco et le
  joueur dans la rue en janvier, une terrasse en juillet, un char arrêté devant un Tempo, une borne ouverte.
- **Pas fait, à dire** : les enfants de la borne sont peints (on ne les bouscule pas, on ne leur parle pas) ;
  l'enfant à vélo ne s'habille pas ; un char qui roule SUR le trottoir traverse encore les tables (seuls les
  piétons butent, comme demandé) ; un passant immobile sur une table au changement de palier est poussé,
  mais un personnage « figé » dont le poste tomberait sur une table y reviendrait (aucun ne l'est : jugé).
- **fix du 30 sept. 2026 — un vrai panache** (Martin : le jet est trop fin, « plus gros ») : le filet de
  30 px est devenu un panache qui **traverse la rue**. Il sort de la bouche latérale à 8 px du sol, monte
  à 18 px (`haut_px`), s'ouvre jusqu'à 14 px de large (`large_px`) et retombe à `traverse` = 85 % de la
  chaussée passé le bord du trottoir, entre 24 et 60 px de la borne (`jet_min_px`, `jet_px`) : 35 px sur une
  rue à deux voies, 60 sur une à quatre (`RueDesSaisons.panacheDe`, une fois par borne, lu sur les tuiles).
  Le jet plein a un halo, un ventre plus sombre, un cœur blanc, des vagues qui le parcourent et des éclats
  qui brillent ; passé 72 % du chemin il se défait en paquets qui retombent, 30 gouttes s'en détachent ; à
  la chute, une couronne de gouttes qui rebondissent et de la brume. Au sol : l'asphalte mouillé et la
  flaque qui respire, **arrêtées par la bordure d'en face** (un clip sur la chaussée), le pied de la borne
  mouillé, l'eau qui file dans le caniveau d'un côté (à l'empreinte de la borne), l'ombre du panache, les
  ronds qui partent de la chute, l'écume et le ciel dans la flaque. Le panache se trie avec les gens **en
  trois tronçons** (un enfant passe devant ou derrière l'eau) ; les enfants courent dessous, d'un bout à
  l'autre ; on se rafraîchit n'importe où sous lui (`dansUnJet` : la distance au segment borne-chute), pas
  au-delà. **Un char qui roule dans l'eau la fait gicler** de chaque côté (peint, par-dessus lui). Toujours
  sans entité ni dé, d'après `B.t` ; la ville ne bouge pas (seules les données de la borne changent).
  **Le rythme** (Chromium, Mac, `test_la_canicule_tient_le_rythme`) : le rendu 1,44–1,48 ms avec la borne à
  l'écran contre 1,31–1,33 sans (+0,1 à 0,17 ms ; avant : +0,02) ; 2,3–2,4 ms par image un jour de canicule
  (2,2 au commit d'avant). **Juge** : `test_le_panache_traverse_la_rue` (il retombe dans la chaussée, passé
  son milieu, peint il monte à `haut_px` et couvre sa portée en l'air, trois tronçons, mouillé dessous et
  sec au-delà, la gerbe du char) — 6 mutations, 6 rouges. **Captures** : `captures/borne-panache-*.png`
  (une rue à deux voies et une à quatre, trois images de jour et trois de soir à 19 h 12, un char dans
  l'eau, la vue à l'échelle du jeu). Le soir de juillet, la borne ferme à 19 h 30 : il fait encore clair.

### Lot 5 — le son des saisons (livré le 29 sept. 2026)

- **Quatre ambiances** (ElevenLabs, 860 crédits — générées une fois à 10 s, trop lourdes d'un
  demi-Ko pour le plafond d'un fichier de lieu, puis refaites à 9,5 s : quatre boucles de 76 Ko) :
  `saison_hiver` (le vent froid entre les maisons, une charrue qui gratte au loin), `saison_printemps` (la
  fonte dans les gouttières, les merles), `saison_ete` (les cigales, une tondeuse au loin),
  `saison_automne` (les feuilles sèches sur l'asphalte, les outardes). Août sonne comme l'été, novembre
  comme l'automne (`saisons.SON`).
- **En fondu enchaîné** (`Saisons.sonA`, `Saisons.majSon`, un pas de la boucle du jeu) : le volume voulu de
  chaque ambiance suit la palette — pendant une transition, l'une descend pendant que l'autre monte, palier
  par palier — et le volume joué glisse vers lui en deux secondes, image par image. Plus bas la nuit (× 0,45),
  presque couvert sous la pluie et la tempête (× 0,3, elles ont leur boucle), muet dedans.
- **Chargées à la demande** : chaque ambiance est un lieu (`LIEUX["saison_…"]`) — on ne télécharge que la
  saison qu'on entend (et celle vers qui elle glisse). Hors ligne avant le chargement : muette, pas de
  synthèse de repli (comme la pluie).
- **Juges** : `test_saisons_son_js.py` (4 juges : le catalogue et les lieux, la bonne ambiance à chaque
  saison, la nuit, la pluie, dedans ; le fondu image par image de novembre à l'hiver, sans dé, qui ne charge
  que ce qu'il entend et éteint tout dedans ; la boucle du jeu qui l'allume) ; 8 mutations, toutes rouges.
- **Le plafond des sons de lieu relevé** (`test_le_poids_audio_reste_raisonnable`) : de 1 000 000 à
  1 350 000 octets — les lieux pesaient déjà 0,94 Mo (pluie, Halloween, train, explosifs), les quatre
  ambiances en ajoutent 0,3. **À valider par Martin.**
- **À écouter par Martin** : personne d'autre ne peut juger un son (`static/audio/saison_*.mp3`) ; s'il
  en refuse un, `scripts/audio_elevenlabs.py --refaire saison_ete`.

### Lot 6, vague 6a — le dérapage (livrée le 29 sept. 2026)

- **Le modèle** (`static/js/derapage.js`, appelé par `Vehicules.majPhysique` ; ses réglages vivent dans le fichier, HORS du paquet : ils faisaient déborder le plafond gzip des définitions de 29 octets) : l'adhérence
  du sol (`g` : la neige et la glace que les pneus d'hiver rendent en partie, la rue mouillée, la pluie) est
  calculée une fois, avant le volant ; la PERTE (1 − g) mène tout le reste, et une perte nulle rend l'ancien
  calcul au pixel près (jugé : la même trajectoire, scriptée sur 90 images, avec et sans le module).
- **Le sous-virage** : le braquage perd jusqu'à 90 % à pleine vitesse sur un sol sans adhérence. **Les roues
  bloquées** : frein à fond, lancé, sur un sol qui a perdu 30 % ou plus — il reste 12 % du braquage. **Le
  survirage** : le frein à main en courbe (et, doucement, le gaz à fond en tournant) pousse un LACET qui
  s'ajoute au cap ; le sol le reprend peu à peu, le **contre-braquage** beaucoup plus vite ; laissé faire, le
  tête-à-queue. Les **pneus d'hiver** rendent une vraie part (jugé : 20 % de rotation de plus au moins).
- **Au sol** : des traces noires au sec quand on glisse de biais (et le crissement, ElevenLabs, chargé la
  première fois qu'on conduit), des sillons dans la neige, rien sur la glace ; 160 marques au plus, qui
  s'effacent en 45 s.
- ⚠️ **La motoneige** (et ce qui est fait pour la neige, `hors_neige` sous 1) n'a pas de dérapage : sur ses
  skis, elle glisse comme avant — sa course des bois est réglée là-dessus (elle rougissait).
- ⚠️ **Le gaz est doux** : plus fort, le survirage au gaz compensait le sous-virage et le char tournait sur la
  glace autant qu'au sec (vu au banc).
- **Juges** : `test_derapage_js.py` (10), chacun vu rougir sous sa mutation (sans sous-virage, sans
  contre-braquage, roues bloquées qui dirigent, sans frein à main). Réécrits : la glissade de la neige et de
  la pluie se mesure à la TRAJECTOIRE qui suit moins le volant (l'écart cap-direction ne le dit plus quand le
  char sous-vire au lieu de flotter).
- **La relecture** (un agent neuf) a trouvé, et c'est corrigé : le lacet durait plus que l'élan (un char
  arrêté pivotait de trois quarts de tour sur la neige) — il s'éteint maintenant avec la vitesse ; les coques
  marquaient l'eau et crissaient — exemptées ; au clavier (frein tout ou rien), freiner sur la neige bloquait
  toujours les roues — elles ne bloquent qu'après un frein TENU 18 images (des coups de frein gardent le
  volant : on pompe, comme en vrai), et plus sur la rue arrosée sous la pluie ; la police bloquait ses roues
  et partait en tête-à-queue au demi-tour — l'IA ne bloque pas et rattrape son arrière d'elle-même ; la
  marche arrière crissait ; les traces suivaient dans le chalet.
- **Pas fait, à dire** : ça ne se juge qu'au volant — à la manette de Martin, le contre-braquage doit se
  sentir et rattraper ; les réglages sont en tête de `static/js/derapage.js` (`REGLAGES`). Sous la pluie, une rue mouillée ne crisse
  ni ne marque (voulu : le crissement est le son du sec).


### Lot 6, vague 6b — la glace (livrée le 1er oct. 2026)

- **Où** (`static/js/glace.js`, ses réglages en tête du fichier, hors du paquet comme ceux du dérapage) : une plaque
  au plus par cellule de 6 × 6 tuiles, une cellule sur quatre — 527 plaques dans la ville, à l'empreinte de leur
  cellule : sur la chaussée (une sur deux, quand la cellule en a une, sur la **ligne d'arrêt**, là où les chars
  polissent la neige — 67 en tout), sur les **trottoirs** (une sur trois), et huit sur le **tablier du pont de La
  Pointe**, qui gèle avant tout. Une plaque est une ellipse au bord irrégulier, de 16 à 34 px de long dans le sens
  de la rue, qui ne déborde jamais de sa surface (l'asphalte, ou le trottoir). Trois à six à l'écran. **Rien n'est
  posé, rien n'est tiré** : aucune tuile, aucune entité, aucun identifiant, aucun dé (jugé) — la ville ne glisse pas.
- **Quand** (`intensiteA`, une pure fonction du jour et de l'heure) : **tout l'hiver** (décembre à mars), tout le
  jour ; en **avril** et en **novembre**, le gel et le dégel — pleine la nuit et jusqu'à 8 h, fondue à midi, elle
  regèle dès 20 h si le lendemain gèle encore (pas le dernier soir d'avril, ni avant le premier matin de novembre) ;
  jamais de saut, ni à minuit ni d'une saison à l'autre (jugé au quart d'heure sur deux ans). Novembre est un ajout :
  les premiers gels, la transition vers l'hiver.
- **Ce qu'on voit** : sur l'asphalte, de la **glace noire** — une tache sombre et lustrée, plus foncée au cœur, deux
  ou trois traits de reflet ; sur le trottoir, une glace bleutée ; un éclat de soleil qui saute d'une plaque à
  l'autre. Peinte SOUS la neige (une tempête la cache), en fondu quand elle fond. **La nuit**, une plaque à moins de
  70 px d'un lampadaire, ou dans le faisceau d'un phare, **renvoie la lumière** : une lueur froide dans la liste des
  lampes, et ses reflets et un éclat repeints PAR-DESSUS le voile (`dessinerReflets`) — on la voit venir dans ses
  phares. Captures regardées : le jour (l'arrêt, le trottoir, le pont), la nuit (le lampadaire, les phares), un
  matin d'avril à demi fondu, juillet sans rien.
- **Au volant** : sur une plaque, le sol ne tient plus que **0,3** (le frein 0,45) — le **minimum** avec la neige et
  le verglas, pas un produit (une plaque sous la tempête ne glisse pas deux fois). Le **dérapage de la vague 6a**
  s'éveille : le char lancé sous-vire, le frein tenu bloque les roues, le frein à main fait partir l'arrière ; les
  **pneus d'hiver** de Ti-Guy en rendent une part. Hors d'une plaque, rien ne change (jugé au pixel). La motoneige
  et les coques n'en ont pas (comme le dérapage).
- **Le trafic, sur ses rails** (`Glace.surRails`, lu par `rouler`) : sur une plaque, il **patine au départ** (au
  plus 35 % de son élan) et **freine long** (le frein à 45 %), la caisse **chasse un peu** quand il freine et avance
  encore (un roulis à l'empreinte, que le cap reprend ; arrêté à la ligne, il est droit) — mais il ne quitte jamais
  son rail : `rouler` n'avance jamais plus loin que sa cible, ni la ligne d'arrêt ni sa voie ; à une ligne d'arrêt
  glacée, il y arrive plus vite et s'y arrête pile. **Devant quelqu'un à pied**, le frein reste plein (sans ça, un
  passant qui surgit à 38 px était fauché à 1,3 px/image). La **police en poursuite** n'y glisse pas. La police hors des rails (et les
  poursuivants) prend le dérapage de 6a, qu'elle rattrape d'elle-même. Les **autobus et les rames** (`ligne`)
  tiennent leur horaire : la glace ne les touche pas (une rame roule sur l'acier ; au banc, un autobus lent à
  démarrer gardait ses passagers, une rame restait prise au coin). La police hors des rails : sur le verglas, elle
  arrive plus tard, mais elle arrive, sans tourner en rond (jugé sur cinq départs). Une « prudence » de l'IA (lever le pied en courbe) a été
  essayée et retirée : mesurée, elle ne faisait que la ralentir — la police ne tournait pas en rond sans elle.
- **À pied** : le joueur qui **court** (ESQUIVE, du souffle) sur une plaque garde 85 % de son élan (il glisse), et
  **tombe** au bout de 14 images de course sur la glace (24 en bottes d'hiver), 45 images au sol ; en marchant, jamais.
  Un **passant qui s'y sauve** en courant tombe au bout de 8 à 15 images (à l'empreinte de son numéro), reste 70 images
  à terre, se relève et reprend sa fuite. Jamais un passant de mission, un agent, un figurant qui tient son poste, un
  enfant qui suit sa mère ni un cycliste. ⚠️ Les agents à pied ne glissent pas (la police les mène, `Police.gere`).
- **Le verglas** (Martin, 29 sept. 2026) : l'option « VERGLAS (ESSAI) » disparaît (une vieille sauvegarde la perd) ;
  il tombe les **trois derniers jours de mars** (8, 9 et 10 de l'année, chaque année), pour tout le monde — la radio
  l'annonce, le Clairon, les génératrices. Ces soirs-là, la **pluie verglaçante prend la place de la tempête de
  neige** (le soir du 8 n'a plus de neige, ni de déneigement le lendemain). Pendant le verglas, les plaques comptent
  encore (le minimum : 0,3 sous 0,4).
- **La mesure** (Chromium, Mac ; A/B apparié : la glace coupée et allumée en alternance, 40 blocs de 30 images, dans
  la même page, deux passes par scène) : la simulation 2,2 ms contre 2,2 (le jour, trois plaques), 1,9 contre 1,9 (le
  pont, six plaques), 1,9 contre 2,0 (la nuit dans les phares) ; le rendu 1,00 contre 1,00 ms le jour, 0,88 contre
  0,90 sur le pont, 1,23 contre 1,31 la nuit — au plus **0,1 ms par image** (la nuit, où elle cherche les lampes et
  repasse ses reflets), rien le jour. Une plaque se peint une fois (un canevas gardé, 96 au plus). Sous la charge de
  quatre bancs, la même mesure donnait les mêmes écarts.
- **Juges** : `tests/test_glace_js.py` (14) — le calendrier sans saut ; les plaques à l'empreinte, sur leur
  surface, à l'arrêt, au trottoir, au pont ; aucun dé ni entité ; elle se voit le jour et luit la nuit sous un
  lampadaire ou dans un phare ; sur six plaques, le char sous-vire, freine long et les pneus d'hiver aident ; la
  police arrive sans tourner en rond (cinq départs, au sec, au verglas, sur la glace) ; sur six plaques, le trafic
  freine long, chasse un peu, reste sur son rail, repart en patinant ; quatre graines de 2 000 images en janvier sans
  qu'un char tourne en rond ni sorte de sa voie ; sur quatre plaques, le joueur qui court tombe (pas en marchant, pas
  l'été, plus tard en bottes) ; sur quatre plaques, le passant qui se sauve tombe et se relève (pas l'été, pas celui
  d'une mission) ; assommé pendant sa chute, il reste couché ; le trafic sur une plaque ne fauche pas un passant qui
  surgit ; le verglas pour tout le monde fin mars ; plus d'option au menu. **37 mutations, 35 rouges** — les deux
  vertes, notées : retirer le contre-braquage de l'IA, ou la laisser accélérer quand elle ne fait pas face, ne fait pas
  tourner la police en rond en terrain ouvert (c'est sa loi de pilotage entière qui la garde : un pilote qui ne lève
  jamais le pied et braque mollement fait deux tours et demi autour du joueur sur la glace, et là le juge rougit).
- **La relecture** (un agent neuf) a trouvé, et c'est corrigé : un passant assommé pendant sa chute se redessinait
  debout ; le roulis tournait une auto arrêtée à la ligne, sans retour ; sur une plaque, le trafic pouvait faucher un
  passant qui surgit ; les feux de circulation et les feux arrière faisaient luire la glace ; le juge du trafic ne
  voyait pas la ligne d'arrêt (refait sur six lignes glacées). Les plaques de la ligne d'arrêt suivent le sens de la
  voie (`Monde.sensArret`).
- **Réécrits** : `test_verglas_js.py` (sans option : « hors de ses jours, il n'existe pas », le soir sans verglas
  est un soir de décembre, et la glace noire coupée — on y juge le verglas) ; `test_deneigement_js.py` (tout un
  hiver : le soir du 8 est au verglas) ; `test_police_js.py::test_en_courant_on_ne_seme_pas_un_agent…` coupe la glace
  (un sprint qui croise une plaque tombe : ce juge mesure l'endurance) ; `test_tramway_js.py::test_deux_rames_qui_se_croisent…`
  et `test_on_attend_l_autobus_js.py::test_l_autobus_s_arrete_pour_eux…` coupent la glace (le trafic qui patine
  retarde les rames et l'autobus au-delà de leur budget d'images ; le juge du tramway tenait déjà par la graine sur
  la base : sur douze graines, deux impasses de 387 images et deux fois aucune croisée).
- **La ville roule l'hiver** : sur 40 graines × 2 000 images de janvier, la trace du trafic ne crie ni au chien de
  garde, ni au hors-voie, ni au char qui tourne en rond — avec la glace comme sans (40 contre 40).
- **Les rouges d'avant** (rejoués sur la base `b523c126`, sans la glace, mêmes rouges) : `test_motoneige_js::test_la_course_des_bois…`,
  `test_boulots_js::…pizza…`, `test_chantiers::…avec_ou_sans_chantiers…`, `test_defis_graduels_js` (neuf épreuves au
  bouton), `test_dix_missions_js` (e12, f05), `test_garages_ou_l_on_entre_js::…carrosserie…`, `test_histoire_js::…premiere_bagarre…`,
  `test_les_deux_fins_js` (m99 ×2), `test_la_nuit_js::…sort_de_l_eau…`, `test_missions_en_scene_js` (p13, p14 : douze),
  `test_orignal_js::…sentier_du_bois…`, `test_velos_js::…bordure…`, `test_carte_du_depot` (foyers, rixes).
- **Pas fait, à dire** : la vague **6c** reste — les **bancs de neige qui enlisent** (les roues patinent, on recule,
  on repart). La glissade du trafic sur la glace, prévue en 6c, est faite ici (sur ses rails). La glace ne se juge
  qu'au volant et au pied : à la manette de Martin, la plaque doit se voir venir, et le contre-braquage rattraper. Les
  agents à pied ne tombent pas. Rien ne fond sous les pneus ni ne se sale (la glace est une fonction du calendrier).

### Lot 6, vague 6c — les bancs de neige qui enlisent (livrée le 1er oct. 2026)

- **Le banc chevauche la bordure** (`static/js/bancs_de_neige.js`, ses réglages en tête du fichier, hors du paquet
  comme ceux du dérapage et de la glace ; le dessin dans `rue_des_saisons.js`) : peint en 4b DANS la rue (3 à 6 px), il
  mangeait la voie — une voie a 16 px, un char 14, ses roues passent à 3 px de la bordure. Il est maintenant à cheval :
  une lèvre de 1 à 3 px dans la rue (jamais plus), le gros sur le bord du trottoir, une crête blanche sur la bordure et
  un trait gris-bleu côté trottoir (sur un trottoir enneigé, sans lui, il s'y fondait — vu sur la capture). **Le dessin
  et les roues lisent le même profil** (`largeurs`) : jugé pixel par pixel sur six morceaux, zéro écart.
- **On a pelleté les entrées** : plus de banc devant un rideau de garage, une allée, un stationnement ou la rampe du
  skatepark (de l'autre côté du trottoir et de l'abord, `uneEntree`) — on se plantait en entrant chez Ti-Guy, et le saut
  du skatepark ne se prenait plus l'hiver (deux juges l'ont dit). Les bancs de 4b ont enfin leur trouée devant les entrées.
- **Ce qu'il fait aux roues** (les quatre roues, pas la carrosserie qui surplombe ; `maj`, appelé par `majPhysique`) :
  - **effleuré** de biais, il freine un peu et la neige gicle ; on glisse le long, comme contre une bordure ;
  - **abordé au pas**, il retient : on le monte (et on en redescend) à 0,25 px/image au plus — aucun trottoir n'est fermé
    au char qui y va doucement ;
  - **abordé vite** (0,9 px/image ou plus VERS le banc, pas le long), le char s'y **plante** : le nez s'enfonce de 1 à 3
    px, une gerbe de neige, un « whoump » (ElevenLabs), la caméra qui tressaute, et le HUD : « PRIS DANS LE BANC — RECULE,
    OU BERCE : AVANCE, RECULE, AVANCE » (rappelé quand on patine et que le HUD n'a rien d'autre à dire) ;
  - **pris**, il ne roule plus : le gaz fait patiner les roues (la neige gicle derrière, le moteur s'emballe —
    ElevenLabs), un peu de neige se peint sur son nez ; **la marche arrière** l'en sort en deux secondes environ, **bercer**
    (avancer, reculer, en rythme : moins de 40 images entre deux) en une ; le char va et vient d'un pixel et demi, on le
    voit bercer. Le gaz seul ne l'en sort jamais. Sorti, il recule au pas hors du banc ;
  - **le 4 roues et les camions lourds** (masse 2,5 et plus : le camion, l'autobus, l'asphalteuse, la pelleteuse) le
    poussent : plus lents, jamais pris ; **la motoneige** et les coques n'en savent rien ;
  - **l'IA hors des rails** (la police, les poursuivants) y perd de l'élan, n'y reste jamais prise ; **le trafic** roule
    sur ses rails au milieu de sa voie : jugé sur toutes les bordures de la ville, aucune roue d'une auto, d'un camion ou
    d'une moto au milieu de sa voie ne touche le banc, même plus gros que le plafond.
- **Le calendrier** (`grosseurA`, une pure fonction du jour et de l'heure) : la neige qui tient (la palette de 4b), plus
  **0,15 par tempête de l'hiver** (peu à peu, pendant qu'elle tombe : la charrue repousse au bord), au plus trois (le
  deuxième hiver en a quatre) ; au dégel, il fond avec la palette, sale. Le banc s'élargit sur le trottoir, sa lèvre ne
  dépasse jamais 3 px. Les morceaux se repeignent quand la grosseur change de palier (`BancsDeNeige.cle`) : jamais un
  jour calme, quatre fois une soirée de tempête.
- **Rien de posé, rien de tiré** : aucune tuile, aucune entité, aucun dé (la gerbe tire ses grains à l'empreinte de
  l'image et du char) ; seul l'état d'un char pris vit sur le char (`v.banc`), et un char déplacé par autre chose (la
  remorqueuse, un char qui le pousse) n'est plus pris.
- **La mesure** (Chromium, Mac ; A/B apparié : les bancs coupés et allumés en alternance, 40 blocs de 30 images dans la
  même page) : pris et patinant, la simulation 3,0 ms contre 3,0, le rendu 1,49 contre 1,49 ; en roulant le long d'une
  rue bordée de bancs, 3,08 contre 3,09 et 1,66 contre 1,60 — au plus 0,06 ms par image. La repeinte de tous les
  morceaux à l'écran (un palier) : 7,2 ms en janvier contre 4,5 à 6,5 en juillet (les bancs à cheval sur la bordure, les
  Tempo, la neige des trottoirs), quelques fois par tempête.
- **Juges** : `tests/test_bancs_de_neige_js.py` (10) — la grosseur aux tempêtes et au dégel, le plafond, la repeinte ;
  le dessin et les roues au pixel ; au milieu de sa voie, rien ; y foncer plante (six bancs, trois graines), les roues
  patinent, la neige gicle, le son et le HUD ; on sort en reculant, plus vite en berçant (six bancs, deux graines) ; au
  pas, on le monte ; le 4 roues et le camion le poussent, la motoneige n'en sait rien ; l'IA n'y reste jamais prise
  (six bancs, trois angles, deux graines, police et poursuivant) ; aucun dé, et hors du banc la conduite au pixel
  (l'été contre la bordure, l'hiver au milieu de la voie) ; devant les portes de garage, on a pelleté. **29 mutations,
  29 rouges** (le plafond n'a mordu qu'abaissé de quatre à trois tempêtes : aucun hiver n'en avait plus de quatre).
- **Retouchés** (ils posaient un char immobile ou une trajectoire sur un banc de janvier) : `test_derapage_js` (le
  pilote sur place), `test_neige_js::test_sur_la_neige_un_char_glisse…`, `test_glace_js` (la traversée d'une plaque de
  la ligne d'arrêt qui longe la bordure), `test_nids_de_poule_js` (le nid au bord), `test_conduite_js::test_un_mur…`
  (plein nord, il traversait un trottoir), `test_verglas_js::test_sur_la_glace_le_char_glisse` (volant à fond vers la bordure), `test_chantiers_js::test_le_tas_de_terre…` (l'élan traverse un trottoir) : chacun coupe les bancs (`BancsDeNeige.couper`) et le dit.
- **Captures** regardées : la rue en janvier, en mars après deux tempêtes, au dégel ; un char pris de jour (la neige sur
  le nez, la gerbe derrière), le soir (dans les phares), sous la tempête.
- **Pas fait, à dire** : ça ne se juge qu'au volant — à la manette de Martin, le seuil (0,9 px/image vers le banc), le
  temps pour sortir et le rythme du bercement sont dans `REGLAGES`. Les agents à pied et les passants traversent le banc
  comme avant (peint). Une opération de déneigement ne charge pas les bancs dans les camions : ils grossissent jusqu'au
  plafond, puis fondent au dégel. Un char laissé pris sur la chaussée est « mal garé » : la fourrière passe.
