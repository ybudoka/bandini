# Des bagarres de gangs vivantes, et armées

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « revise les bagarres de gang pour que ce soit dynamique et réaliste,
aussi des armes à feu »._

_Ce que ça donne :_ une bagarre de gangs qui bouge — ils encerclent, reculent, s'abritent derrière un char,
tirent par salves, rechargent, fuient blessés, appellent du renfort — et chaque gang se reconnaît à son arme.

**Aujourd'hui** :
- **La rixe à la frontière** (`entites.js`, état `bagarre`) : trois contre trois ; chacun marche droit sur le
  rival le plus proche, se plante à 22 px et frappe au bâton au métronome (`e.t % 38`), 25 s, puis les
  debout s'en vont.
- **Un gang contre toi** (état `attaque_joueur`) : il court en ligne droite, frappe toutes les 40 images à
  18 px. Ni cercle, ni recul, ni abri.
- **Aucun membre de gang n'a d'arme à feu** (`pietons.py` : `batte`, ou rien). Le seul PNJ qui tire est
  l'agent (`police.js`), et `Combat.tirer` d'un PNJ vise **toujours le joueur**.
- Le joueur, lui, a treize armes ; la balle s'arrête au décor (`mordreLeDecor`) — l'abri existe déjà.

**Tranché avec Martin (30 sept. 2026)** :
- **Les deux bagarres** : un seul cerveau de combat sert la rixe gang contre gang ET le gang qui te tombe
  dessus.
- **Un arsenal par gang**, porté par **un membre sur trois** ; les autres gardent leur arme blanche :

  | Gang | Arme signature | Sa façon de se battre |
  |---|---|---|
  | Cravates (Faubourg) | pistolet | propre, précis, mi-distance |
  | Morues (Quais) | fusil à pompe | foncent, tirent de près |
  | Chevreuils (Érables) | carabine | restent loin, lents et justes |
  | Boulonneux (La Shop) | mitraillette | rafales qui s'ouvrent, les plus dangereux |
  | Skateux (La Pointe) | cocktail Molotov | lancent et courent, mettent le feu |
  | Mantes (Petit-Canton) | **aucune** | l'école : les techniques, pas les balles |

- **Les quatre comportements** : la tactique au contact, la fusillade, le moral et les blessés, les renforts.
- **L'approche A** : un module neuf, livré en quatre vagues.

### L'architecture

- **`app/rixes.py`** — la fiche, envoyée au paquet sous `B.defs.rixes` : `ARSENAL` (gang → arme), `PART_ARMEE`
  (1/3), la **distance de tir** de chaque arme (le fusil de près, la carabine de loin), et les réglages de
  chaque vague (`CONTACT`, `FUSILLADE`, `MORAL`, `RENFORTS`). Rien n'est codé en dur dans le navigateur.
- **`static/js/rixe.js`** — le cerveau : `Rixe.maj(e, cible)`. Il connaît trois **rôles**, lus sur l'arme en
  main : `melee` (bâton, couteau, poings), `tireur` (type `tir` sans cloche), `lanceur` (la cloche du
  Molotov). L'état du combattant tient dans `e.rixe` (`posture`, `minuterie`, `abri`, `salve`, `chargeur`).
- **`entites.js`** ne fait plus que **déléguer** : la branche `bagarre` passe le rival (`rivalDe`), la branche
  `attaque_joueur` passe le joueur. Les Mantes (`Techniques.parer`), le cousin qui dicte ses coups
  (`coupsDictes`) et l'allié (`allie`) gardent leur branche : le cerveau ne les prend pas.
- **`Combat.tirer(e, arme, cible)`** — une cible optionnelle ; sans elle, le joueur (l'agent ne change pas).
- **Qui t'attaque ne change pas** : `hostile_si_arme`, `hostile_toujours`, la cour, l'îlot pris — seule la
  façon de se battre change.
- **L'arme d'un membre** se tire **à l'empreinte** à sa naissance (`hash2(e.id, …) % 3`), jamais au dé du
  jeu. Seuls les membres nés de la rue et des rixes la reçoivent : un homme de mission garde l'arme que sa
  mission lui donne (« la première bagarre se gagne aux poings » reste vraie).

### Les vagues

1. **Le cerveau et la tactique au contact.** `rixe.js` et `rixes.py` ; les deux branches y délèguent. Au
   contact : ils se **répartissent autour** de la cible (chacun sa place sur un cercle, par son numéro) au
   lieu de faire la file ; ils **tournent** (un pas de côté), **reculent** après leur coup, **esquivent**
   parfois un coup armé ; chacun frappe **à son rythme** (une cadence de base, décalée à l'empreinte), plus
   jamais au métronome commun.
2. **L'arsenal et la fusillade.** Un membre sur trois porte l'arme de son gang et la sort **dès que le
   combat commence**. Le tireur tient **sa distance** (celle de son arme), cherche un **abri** à portée (un
   char, un mur, du mobilier qui arrête la balle), **sort pour une salve** de deux à quatre coups, **rentre**,
   et **recharge** — un temps mort qu'on voit et qu'on peut punir. Avant sa première balle, il **lève
   l'arme** un instant (le geste qu'on voit venir, comme l'anticipation d'un coup). Il **manque** : sa
   dispersion est plus large que la tienne. Le lanceur de Molotov vise **le groupe**, puis s'éloigne en
   courant.
   - Un coup de feu entre gangs **s'entend** (`Police.entendre`) et fait fuir la rue, mais **ne te colle
     aucune étoile** : c'est un crime d'autrui (`Police.crimeDAutrui`).
   - Une balle perdue qui couche un passant **ne t'est pas comptée** (ni force de gang, ni recherche).
3. **Le moral et les blessés.** Sous un seuil de vie, un blessé **recule** et se bat de loin, ou **fuit en
   boitant** ; quand un camp a perdu la moitié des siens, **les autres se sauvent** (la déroute). Un membre
   couché **lâche son arme** au sol — on la **ramasse** comme les autres.
4. **Les renforts.** Un membre qui perd **crie** ; les siens à portée (dans la bulle, hors de l'écran)
   **accourent**, au plus quelques-uns par rixe ; une fois sur quelques-unes, ils arrivent **en char** et en
   descendent. Une rixe où l'on s'attarde peut donc grossir.

### Ce qui guette

- **Le hasard de la ville** : rien au `B.rng` du monde pour choisir une arme, une place ou un renfort — tout
  à l'empreinte (`hash2`). Un renfort né « au dé » décalerait tous les dés qui suivent (la leçon du char en
  panne), et une entité posée tôt décale les identifiants (e12).
- **Personne n'apparaît à l'écran** : renforts et rixes naissent hors champ (`visibleAEcran`), comme
  aujourd'hui.
- **Les trois réflexes « contre le joueur »** (`alerter`, `blesser`, `majAttaque`) ont chacun leur juge :
  une balle de rixe ne doit pas les réveiller contre toi.
- **L'équilibre** : une mitraillette de Boulonneux, à trois, peut te coucher en deux secondes. Un facteur de
  dégâts des tirs de gang contre le joueur (`degats_contre_joueur`, dans la fiche) se règle au banc, et la
  levée d'arme te laisse le temps de rouler.
- **Les exceptions tenues** : la paix du Boss (pas de rixe), les alliés (ne te touchent jamais, ni une balle),
  un gang libéré ou calmé (M16), les Mantes (sans arme à feu), les missions qui nomment un gang (`groupe`).
- **Le poids du paquet** : la fiche `rixes` s'ajoute au paquet — `test_definitions` dans les juges ciblés.

### Juges (par vague)

1. Deux membres au contact d'une même cible ne sont jamais à la même place (le cercle) ; deux membres ne
   frappent pas à la même image plus d'une fois sur N ; après son coup, il recule ; la rixe finit toujours.
2. Un gang sur trois porte son arme signature, **toujours la même** pour le même membre (l'empreinte) ; les
   Mantes jamais ; le tireur se tient dans sa fourchette de distance ; il va à l'abri quand il y en a un ; il
   recharge après son chargeur ; une rixe armée ne te donne aucune étoile ; un homme de mission garde son
   arme.
3. Un blessé sous le seuil recule ; la moitié du camp couchée, les autres fuient ; l'arme lâchée se
   ramasse.
4. Un cri fait accourir les siens, jamais plus que le plafond, jamais à l'écran ; rien ne tire `B.rng` (la
   ville ne bouge pas : les juges « ce module ne déplace rien »).

Et à chaque vague : une **capture** de la rixe (Chromium), et la jouer au banc.

## Notes

### Vague 1 — le cerveau et la tactique au contact — **livrée le 30 sept. 2026**

**Ce qui a changé en route** (le plan d'en dessous est celui d'avant le code) :
- **Il frappe DE SA PLACE**, plus « la portée prime » : la portée (20 px) dépassant le cercle (16), tous cognaient
  dès l'arrivée, du même côté. Il frappe de sa place (`place_px`), ou d'où il est si sa place est dans un mur ; et
  pour la gagner il **contourne** la cible (`contourne_rad`) au lieu de lui passer à travers.
- **Huit places, les libres seulement** (`places`) : le joueur de départ est contre la façade du Terminus, et la
  place du troisième tombait dans le mur. Chacun prend le milieu de sa part : devant un mur, ils s'ouvrent en
  éventail (la capture du 30 sept.).
- **Coincé, il frappe d'où il est** (`coince_images`) : à portée, loin de sa place, et plus moyen d'en approcher
  (des corps la tiennent). Au siège de m98, six alliés plantés sur le cercle autour de toi : les Cravates n'ont
  passé que 36 images en plein geste de tout le siège (450 avec la règle). Et **une cible qui bouge** se frappe à
  portée (`bouge_px`) : sa place bouge avec elle.
- **Seul, il garde son côté** : le premier du rang garde la place d'où il arrive, les autres s'étalent à partir
  de lui (réparti au milieu des places libres, un homme seul recevait le côté opposé).
- **L'allié de m98 garde sa branche** (essayé par le cerveau, puis défait : il restait coincé derrière toi), mais
  frappe à **son délai à lui** au lieu du métronome `e.t % 38` (l'instant exact tombait hors de portée d'un
  Cravate qui bouge), et **laisse filer les fuyards** (`cibleDeLAllie` : celui qui se bat d'abord ; au banc, un
  allié courait 460 images après un fuyard aussi rapide que lui). Le siège : 42 coups et 5 couchés (47 et 5 sur
  `dev`, 18 et 2 au pire du chemin).
- **Le rythme est une échéance** (la relecture) : le délai avant le prochain coup ne s'écoulait que dans le
  cerveau, qui n'est pas appelé pendant le geste — 70 images entre deux élans au lieu de 40, le gang frappait un
  tiers moins souvent. Une échéance sur l'horloge de l'homme (`e.t`), pour lui comme pour l'allié, et un recul
  qui est un pas en arrière (10 images) et non une retraite.
- **Deux juges lisent mieux** : l'encerclement à la moyenne de l'écart (89° avec, 23° sans ; un pas de côté
  rapproche deux hommes un instant, c'est voulu), le regard face au rival DU MOMENT (l'ancien couché).
- **m3 passe à la graine 1** : semer le client de la police tenait par la graine (la 3 et la 4 ratent aussi sur
  `dev`) ; la dette est au plan.

#### Le plan (30 sept. 2026)

> **Pour qui exécute :** superpowers:subagent-driven-development ou superpowers:executing-plans, tâche par tâche ;
> les cases (`- [ ]`) suivent l'avancement. Lire la [fiche](#fiche) avant.

**But :** un seul cerveau (`Rixe.maj`) mène l'homme de gang au contact — dans la rixe comme contre toi : il prend
SA place autour de la cible, tourne, recule après son coup, esquive parfois, et frappe à son rythme à lui.

**Architecture :** `app/rixes.py` porte les chiffres (`B.defs.rixes.contact`) ; `static/js/rixe.js` décide
(`e.vx`, `e.vy`, `Combat.frapper`) ; `entites.js` lui passe la main depuis `bagarre` et `attaque_joueur`, et
applique le pas comme pour tout le monde. Un champ `e.faceVers` (qui expire, `e.faceT`) le garde tourné vers sa
cible quand il recule.

**Outils :** Python 3 / pytest (juges), JavaScript sans module (le navigateur), le banc Node (`tests/banc.js`,
fixture `banc`), `uv`.

**Contraintes globales** (de la fiche) :
- Aucun `B.rng()` ni `Math.random()` dans `rixe.js` : tout à l'empreinte (`hash2(e.id, …)`, `e.t`).
- Les Mantes (`e.techniques`), le cousin (`e.coupsDictes`), le salut (`e.salut`) et l'allié (`allie`) gardent
  leur branche ; le cerveau ne prend que `e.gang` (et, dans la rixe, tout rixeur non Mante).
- Rien ne se retourne contre le joueur : les juges de `tests/test_bagarre_js.py` restent verts tels quels.
- Personne n'apparaît à l'écran ; rien ne change à la naissance des gens (la ville ne bouge pas).
- Le poids du paquet : `tests/test_definitions.py` dans les juges ciblés.

**À surveiller aux juges** (cinq risques que les tâches épinglent) :
1. Un gang qui colle au joueur contre un mur : sa place sur le cercle est dans le mur — il doit quand même
   frapper (la portée prime sur la place ; juge de la tâche 3).
2. Six rixeurs nés à la même image frappaient à la même image (`e.t` égal) : juge de la tâche 2.
3. Un homme qui recule tourne le dos à sa cible : `faceVers` (juge de la tâche 2).
4. Un rixeur qui passe à `flane` garde un vieux `e.rixe` et compte encore dans le cercle d'une cible : le filtre
   d'état de `assaillants` (juge de la tâche 3, trois autour du joueur puis un qui s'en va).
5. Les juges de mission qui font se battre le joueur contre un gang (`test_histoire_js`,
   `test_missions_en_scene_js`, `test_le_boss_js`, arcs) : lancés à la tâche 4.

Commandes (depuis le worktree) : `export UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv`, puis
`uv run pytest …`.

#### Tâche 1 — la fiche `rixes.py`, au paquet

**Fichiers :** créer `app/rixes.py`, `tests/test_rixes.py` ; modifier `app/definitions.py` (l'import de la
ligne 56 et le dictionnaire, à côté de `"mantes": mantes.exporter()`).

**Produit :** `rixes.CONTACT` (dict), `rixes.exporter() -> {"contact": {...}}`, et `B.defs.rixes.contact` au
navigateur.

- [ ] **Le juge, rouge d'abord** — `tests/test_rixes.py` :

```python
"""Des bagarres de gangs vivantes, et armées — la fiche (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

from pathlib import Path

import villes

from app import rixes

RIXE_JS = Path(__file__).resolve().parent.parent / "static" / "js" / "rixe.js"


def test_la_fiche_du_contact_se_tient():
    """Des chiffres qui se contredisent font un combat qui grince."""
    f = rixes.CONTACT
    assert 0 < f["cercle_px"] < f["portee_px"], "sa place doit être à portée de coup"
    assert 0 <= f["cadence_ecart"] < f["cadence_images"]
    # Il revient de son recul AVANT son prochain coup : sinon il frappe dans le vide, de loin.
    assert f["recul_images"] < f["cadence_images"] - f["cadence_ecart"]
    assert 0 < f["recul_allure"] <= 1
    assert 0 < f["tourne_min"] <= f["tourne_max"]
    assert 0 < f["pas_images"] < f["tourne_min"], "un pas de côté plus long que l'attente entre deux"
    assert 0 <= f["esquive_pct"] <= 100


def test_le_paquet_porte_la_fiche_des_rixes():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce défaut huit fois."""
    assert villes.assembler()["rixes"] == rixes.exporter()
```

- [ ] `uv run pytest tests/test_rixes.py -q` → ROUGE (`ImportError: cannot import name 'rixes'`).
- [ ] **La fiche** — `app/rixes.py` :

```python
"""Des bagarres de gangs vivantes, et armées (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).

Martin (30 sept. 2026) : « revise les bagarres de gang pour que ce soit dynamique et réaliste ». Ce module décide ;
le navigateur joue (`static/js/rixe.js`) : UN SEUL CERVEAU pour la rixe à la frontière (sa cible : un rival) et
pour le gang qui te tombe dessus (sa cible : toi).

⚠️ Toutes les durées en images (60 par seconde), les distances en pixels ; RIEN au dé du jeu — la place, le
rythme et l'esquive se lisent à l'EMPREINTE de l'identifiant (la leçon du char en panne).
"""

from __future__ import annotations

#: VAGUE 1 — AU CONTACT. Avant : chacun marchait droit sur sa cible, se plantait et cognait au métronome
#: (`e.t % 38` dans la rixe, `% 40` contre toi) — six hommes nés à la même image frappaient à la même image, en
#: file indienne. Maintenant chacun prend SA place sur un cercle autour de la cible (son rang parmi ceux qui la
#: visent), fait un pas de côté de temps en temps, recule après son coup, et esquive parfois le tien.
CONTACT: dict = {
    "portee_px": 20,          # d'où il frappe (la rixe frappait à 22, le gang contre toi à 18)
    "cercle_px": 16,          # le rayon de sa place autour de la cible : en deçà de la portée
    "cadence_images": 40,     # un coup toutes les deux tiers de seconde, en moyenne…
    "cadence_ecart": 12,      # … plus ou moins ça, à l'empreinte : jamais au métronome commun
    "recul_images": 18,       # après son coup (ou une esquive), il recule ce temps-là
    "recul_allure": 0.6,      # à reculons, moins vite qu'en avançant
    "tourne_min": 50,         # entre deux pas de côté, en images (à l'empreinte)
    "tourne_max": 110,
    "tourne_rad": 0.7,        # l'ampleur du pas de côté, en tournant autour de la cible
    "pas_images": 24,         # combien de temps il le tient
    "esquive_pct": 30,        # sur cent coups armés à portée, combien il en esquive
    "esquive_marge_px": 8,    # « à portée » : celle de l'arme de la cible, plus ça
}


def exporter() -> dict:
    """Ce que le navigateur reçoit sous `B.defs.rixes`."""
    return {"contact": dict(CONTACT)}
```

- [ ] **Au paquet** — `app/definitions.py` : ajouter `rixes` à l'import de la ligne 56 (ordre de la liste
  existante), et sous `"mantes": mantes.exporter(),` :

```python
        # Les bagarres de gangs vivantes : le cerveau du contact (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).
        "rixes": rixes.exporter(),
```

- [ ] `uv run pytest tests/test_rixes.py tests/test_definitions.py -q` → VERT.
- [ ] Commit : `feat: la fiche des rixes, au paquet — le contact en chiffres` (+ la ligne Co-Authored-By).

#### Tâche 2 — le cerveau, et la rixe qui s'en sert

**Fichiers :** créer `static/js/rixe.js` ; modifier `templates/index.html` (la ligne `js/rixe.js` juste après
`js/techniques.js`, ligne 208), `static/js/jeu.js` (`Rixe: Rixe,` dans `window.BANDINI`, après
`Techniques: Techniques,`), `static/js/entites.js` (la branche `bagarre` ≈ l. 4813, `finirLaBagarre` ≈ l. 3372,
la fin de `majPieton` ≈ l. 5044) ; juges dans `tests/test_bagarre_js.py` et `tests/test_rixes.py`.

**Consomme :** `B.defs.rixes.contact` (tâche 1), `Entites.pietonsAutour(x, y, r)`, `Combat.frapper(e, fort) ->
bool`, `hash2`, `angleVers` (globaux de `base.js`).
**Produit :** `Rixe.maj(e, cible, vitesse) -> bool` (vrai si un coup est parti à cette image) ; `e.rixe`
(`{ cible, posture: 'approche'|'recul', minuterie, pret, derive, deriveT, tourneT, esquives, vuArmer }`) ;
`e.faceVers` / `e.faceT` (lus par `majPieton`).

- [ ] **Les juges, rouges d'abord** — à la fin de `tests/test_bagarre_js.py` :

```python
def test_ils_ne_frappent_pas_au_metronome(banc):
    """Six hommes nés à la même image frappaient à la même image (`e.t % 38`) : une chorégraphie, pas une
    rixe. Chacun a maintenant son rythme (la cadence de la fiche, décalée à l'empreinte)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(16);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        let departs = 0, ensemble = 0;
        const avant = {};
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          const ceTour = {};
          for (const e of rixeurs(L)) {
            const frappe = e.etat === 'attaque' && e.phase === 'anticipation' && avant[e.id] !== 'attaque';
            avant[e.id] = e.etat;
            if (!frappe) continue;
            departs++;
            ceTour[e.gang] = (ceTour[e.gang] || 0) + 1;
          }
          for (const g in ceTour) if (ceTour[g] > 1) ensemble += ceTour[g];
        }
        return { trouve: true, departs: departs, ensemble: ensemble };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["departs"] >= 6, "trop peu de coups pour juger (%s)" % r
    assert r["ensemble"] / r["departs"] < 0.3, "ils frappent encore en choeur (%s)" % r


def test_il_recule_apres_son_coup_en_regardant_sa_cible(banc):
    """Après son coup il se dégage — et il recule FACE à sa cible, pas le dos tourné (`faceVers`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(17);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        const f = L.B.defs.rixes.contact;
        let reculs = 0, face = 0, dos = 0;
        const suivi = {};
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          for (const e of rixeurs(L)) {
            if (!e.vivant || !e.rixe || !e.rixe.cible) continue;
            const c = e.rixe.cible, d = Math.hypot(c.x - e.x, c.y - e.y);
            const s = suivi[e.id] = suivi[e.id] || { etat: e.etat, d: d, recule: false };
            // La sortie du coup : on note la distance, puis on la relit a la fin du recul.
            if (s.etat === 'attaque' && e.etat !== 'attaque') { s.recule = true; s.depart = d; s.n = 0; }
            if (s.recule && e.rixe.posture === 'recul') {
              const vers = Math.atan2(c.y - e.y, c.x - e.x);
              const regard = { droite: 0, bas: Math.PI / 2, gauche: Math.PI, haut: -Math.PI / 2 }[e.face];
              if (regard !== undefined) {
                const ecart = Math.abs(Math.atan2(Math.sin(vers - regard), Math.cos(vers - regard)));
                if (ecart < Math.PI / 2) face++; else dos++;
              }
            }
            if (s.recule && ++s.n === f.recul_images) { if (d > s.depart + 4) reculs++; s.recule = false; }
            s.etat = e.etat;
          }
        }
        return { trouve: true, reculs: reculs, face: face, dos: dos };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["reculs"] >= 2, "personne ne se dégage après son coup (%s)" % r
    assert r["dos"] == 0, "il recule en tournant le dos à sa cible (%s)" % r
```

  ⚠️ Avant d'écrire le juge du regard, vérifier les valeurs de `e.face` dans `regarder` (`entites.js`) et
  ajuster la table `{ droite, bas, gauche, haut }` à ce qu'elle rend vraiment.

  Et à la fin de `tests/test_rixes.py` :

```python
def test_le_cerveau_ne_tire_aucun_de_du_jeu():
    """⚠️ Un dé tiré ici décalerait tout le hasard de la ville : tout se lit à l'empreinte."""
    source = RIXE_JS.read_text(encoding="utf-8")
    assert "B.rng" not in source and "Math.random" not in source
```

- [ ] `uv run pytest tests/test_bagarre_js.py -k "metronome or recule" tests/test_rixes.py -q` → ROUGE.
- [ ] **Le cerveau** — `static/js/rixe.js` :

```js
/* Bandini — le cerveau d'un homme de gang qui se bat (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).

   UN SEUL CERVEAU pour la rixe a la frontiere (sa cible : un rival) et pour le gang qui te tombe dessus (sa
   cible : toi). `entites.js` lui passe la main depuis `bagarre` et `attaque_joueur` ; il ne fait que DECIDER
   (`e.vx`, `e.vy`, `Combat.frapper`) — le pas se fait apres, comme pour tout le monde (`majPieton`).

   Vague 1, AU CONTACT : chacun prend SA place sur un cercle autour de la cible (son rang parmi ceux qui la
   visent), fait un pas de cote de temps en temps, recule apres son coup en lui faisant face, esquive parfois le
   coup qu'on arme contre lui, et frappe a SON rythme.

   ⚠️ AUCUN DE DU JEU : la place, le rythme et l'esquive se lisent a l'EMPREINTE (`hash2` de l'identifiant et de
   son horloge `e.t`), jamais par `B.rng()` — un de tire ici decalerait tout le hasard de la ville (la lecon du
   char en panne ; un juge lit ce fichier et refuse `B.rng`). */

const Rixe = (function () {
  'use strict';

  //: Ceux qui se battent, a cette image : les deux etats du cerveau, et le coup lui-meme (`Combat` ecrase l'etat
  //: par 'attaque' le temps des trois temps). ⚠️ Un homme qui est passe a `flane` garde son vieux `e.rixe` :
  //: sans ce filtre, il tiendrait encore une place dans le cercle d'une cible qu'il a quittee.
  const EN_COMBAT = { bagarre: true, attaque_joueur: true, attaque: true };

  function fiche() { return B.defs.rixes.contact; }

  /** Sa cadence a lui : la base de la fiche, plus ou moins `cadence_ecart`, a l'empreinte du coup `n`. */
  function cadenceDe(e, f, n) {
    return f.cadence_images + hash2(e.id, 0xCADE + n) % (2 * f.cadence_ecart + 1) - f.cadence_ecart;
  }

  /** L'attente avant son prochain pas de cote. */
  function tourneDe(e, f, n) {
    return f.tourne_min + hash2(e.id, 0x7042 + n) % (f.tourne_max - f.tourne_min + 1);
  }

  /** L'etat du combattant, cree au premier appel. ⚠️ `pret` part DECALE a l'empreinte : six hommes nes a la
      meme image ont la meme horloge, et sans ce decalage ils frappent a la meme image. */
  function etat(e, f) {
    if (!e.rixe) {
      e.rixe = { cible: null, posture: 'approche', minuterie: 0, pret: hash2(e.id, 0x51C0) % f.cadence_images,
                 derive: 0, deriveT: 0, tourneT: tourneDe(e, f, 0), esquives: 0, vuArmer: false };
    }
    return e.rixe;
  }

  /** Ceux qui visent la meme cible, ranges par identifiant : leur rang donne leur place sur le cercle. */
  function assaillants(cible, f) {
    return Entites.pietonsAutour(cible.x, cible.y, f.cercle_px * 8).filter(function (q) {
      return q.rixe && q.rixe.cible === cible && EN_COMBAT[q.etat];
    }).sort(function (a, b) { return a.id - b.id; });
  }

  /** Sa place : sur le cercle, a son rang. L'angle de depart est celui du PREMIER du rang, vu de la cible —
      le cercle se forme la ou ils sont, il ne les arrache pas de leur cote de la rue. */
  function place(e, cible, f) {
    const tous = assaillants(cible, f);
    const n = Math.max(1, tous.length), rang = Math.max(0, tous.indexOf(e));
    const tete = tous[0] || e;
    const a = angleVers(cible.x, cible.y, tete.x, tete.y) + rang * 2 * Math.PI / n + e.rixe.derive;
    return { x: cible.x + Math.cos(a) * f.cercle_px, y: cible.y + Math.sin(a) * f.cercle_px };
  }

  /** La cible arme un coup, a portee de lui : il se degage — une fois sur `esquive_pct`, et une seule decision
      par coup (`vuArmer` retombe quand la cible n'arme plus). */
  function esquive(e, cible, d, f) {
    const arme = cible.etat === 'attaque' && cible.phase === 'anticipation' && cible.arc;
    if (!arme) { e.rixe.vuArmer = false; return false; }
    if (e.rixe.vuArmer || d > (cible.arc.portee || 18) + f.esquive_marge_px) return false;
    e.rixe.vuArmer = true;
    if (hash2(e.id, e.t) % 100 >= f.esquive_pct) return false;
    e.rixe.esquives++;
    return true;
  }

  function reculer(r, f) { r.posture = 'recul'; r.minuterie = f.recul_images; }

  /** Une image de combat contre `cible`, a `vitesse` (celle de sa course). Rend vrai si un coup est parti. */
  function maj(e, cible, vitesse) {
    const f = fiche(), r = etat(e, f);
    r.cible = cible;
    // ⚠️ Il regarde SA CIBLE, meme en reculant : `majPieton` le tourne sinon dans le sens de son pas, et un
    // homme qui se degage tournerait le dos a celui qu'il vient de frapper. Deux images : ca s'eteint seul
    // quand le cerveau ne le mene plus.
    e.faceVers = cible; e.faceT = 2;
    const dx = cible.x - e.x, dy = cible.y - e.y, d = Math.hypot(dx, dy) || 1;
    if (r.pret > 0) r.pret--;
    if (r.posture !== 'recul' && esquive(e, cible, d, f)) reculer(r, f);
    if (r.posture === 'recul') {
      if (--r.minuterie <= 0) r.posture = 'approche';
      e.vx = -dx / d * vitesse * f.recul_allure;
      e.vy = -dy / d * vitesse * f.recul_allure;
      return false;
    }
    // Le pas de cote : il tourne autour de sa cible, de temps en temps, d'un cote ou de l'autre.
    if (--r.tourneT <= 0) {
      r.derive = (hash2(e.id, e.t) & 1 ? 1 : -1) * f.tourne_rad;
      r.deriveT = f.pas_images;
      r.tourneT = tourneDe(e, f, e.t);
    }
    if (r.deriveT > 0 && --r.deriveT === 0) r.derive = 0;
    // ⚠️ LA PORTEE PRIME SUR LA PLACE : sa place peut tomber dans un mur (la cible y est adossee) — a portee et
    // pret, il frappe d'ou il est.
    if (d <= f.portee_px && r.pret <= 0) {
      e.vx = 0; e.vy = 0;
      if (Combat.frapper(e, false)) { r.pret = cadenceDe(e, f, e.t); reculer(r, f); return true; }
    }
    const p = place(e, cible, f);
    const px = p.x - e.x, py = p.y - e.y, dp = Math.hypot(px, py);
    if (dp > 2) {
      const allure = Math.min(1, dp / 12);          // il ralentit en arrivant : pas de va-et-vient sur sa place
      e.vx = px / dp * vitesse * allure;
      e.vy = py / dp * vitesse * allure;
    } else { e.vx = 0; e.vy = 0; }
    return false;
  }

  return { maj: maj, assaillants: assaillants };
})();
```

- [ ] **Chargé et exposé** — `templates/index.html`, après la ligne de `js/techniques.js` :

```html
<script src="{{ url_for('static', filename='js/rixe.js') }}?v={{ version }}"></script>
```

  et dans `window.BANDINI` (`static/js/jeu.js`), après `Techniques: Techniques,` : `Rixe: Rixe,`.

- [ ] **La rixe passe la main** — `static/js/entites.js`, branche `bagarre` : garder tout jusqu'à
  `vitesse = v.pieton_course * e.allure;` et `const mante = …`, puis remplacer la suite de la branche par :

```js
      if (!mante) {
        // LE CERVEAU DU CONTACT (`rixe.js`) : sa place autour du rival, son rythme, le recul, l'esquive.
        // ⚠️ Tu passais par la : un passant te prend pour un des leurs (M12).
        if (Rixe.maj(e, e.rival, vitesse)) Police.crimeDAutrui('coup_pieton', e.x, e.y, e);
      } else {
        const dx = e.rival.x - e.x, dy = e.rival.y - e.y, norme = Math.hypot(dx, dy) || 1;
        if (Techniques.parer(e, e.rival)) return;
        if (norme > mante.saisie_px - 2) {
          e.vx = dx / norme * vitesse;
          e.vy = dy / norme * vitesse;
        } else {
          e.vx = 0; e.vy = 0;
          regarder(e, dx, dy);
          if (e.t % mante.cadence_images === 0) {
            Combat.frapper(e, false);
            Police.crimeDAutrui('coup_pieton', e.x, e.y, e);
          }
        }
      }
```

  (le commentaire des Mantes au-dessus de `const mante` reste). Dans `finirLaBagarre`, ajouter `e.rixe = null;`.

- [ ] **Le regard** — à la fin de `majPieton`, remplacer `regarder(e, e.vx, e.vy);` par :

```js
    // ⚠️ Au combat, on regarde SA CIBLE, meme en reculant (`Rixe`, `faceVers`) ; sinon, le sens du pas.
    if (e.faceT > 0 && e.faceVers) { e.faceT--; regarder(e, e.faceVers.x - e.x, e.faceVers.y - e.y); }
    else regarder(e, e.vx, e.vy);
```

- [ ] `uv run pytest tests/test_bagarre_js.py tests/test_rixes.py tests/test_combat_js.py -q` → VERT (les
  anciens juges de la rixe compris, sans y toucher).
- [ ] Commit : `feat: la rixe au contact — chacun sa place, son rythme, et il recule face à sa cible`.

#### Tâche 3 — le gang contre toi passe par le même cerveau, et l'esquive

**Fichiers :** modifier `static/js/entites.js` (branche `attaque_joueur` ≈ l. 4751) ; juges dans un nouveau
`tests/test_rixe_js.py`.

**Consomme :** `Rixe.maj(e, cible, vitesse) -> bool`, `Rixe.assaillants(cible, f)`, `e.rixe.esquives` (tâche 2).

- [ ] **Les juges, rouges d'abord** — `tests/test_rixe_js.py` :

```python
"""Des bagarres de gangs vivantes — le gang contre toi, au banc (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

#: Trois Cravates, nés à la même image du même côté du joueur, lancés contre lui. Le joueur est increvable (sa vie
#: remise à chaque image) : on juge LEUR façon de se battre, pas sa survie.
TROIS = """
    function trois(L, dx) {
      const j = L.B.joueur, gens = [];
      for (const dy of [-10, 0, 10]) {
        const e = L.Entites.creerPieton(j.x + dx, j.y + dy, L.Entites.archetype('cravate'));
        e.etat = 'attaque_joueur'; e.courage = 1; e.arme = 'batte';
        gens.push(e);
      }
      L.Entites.indexer();
      return gens;
    }
    function tenir(L) { const j = L.B.joueur; j.vie = j.vieMax || 100; j.vivant = true; }
"""


def test_trois_cravates_se_repartissent_autour_du_joueur(banc):
    """Nés du même côté, ils l'encerclent au lieu de faire la file : l'écart d'angle le plus petit entre deux
    d'entre eux, vu du joueur, dépasse 60° (le cercle parfait en donne 120)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        %s
        const gens = trois(L, 60);
        let pire = Math.PI * 2;
        for (let i = 0; i < 300; i++) {
          tenir(L); o.frame(1);
          if (i < 180) continue;          // le temps d'arriver
          const j = L.B.joueur;
          const angles = gens.filter(function (e) { return e.vivant; })
            .map(function (e) { return Math.atan2(e.y - j.y, e.x - j.x); }).sort(function (a, b) { return a - b; });
          for (let k = 0; k < angles.length; k++) {
            const suivant = k + 1 < angles.length ? angles[k + 1] : angles[0] + Math.PI * 2;
            pire = Math.min(pire, suivant - angles[k]);
          }
        }
        return { pire: pire * 180 / Math.PI, etats: gens.map(function (e) { return e.etat; }) };
    }""" % TROIS)
    assert r["pire"] > 60, "ils font la file au lieu d'encercler (%s)" % r


def test_celui_qui_s_en_va_rend_sa_place(banc):
    """⚠️ Un homme passé à `flane` garde son vieux `e.rixe` : il ne doit plus compter dans le cercle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(22);
        %s
        const gens = trois(L, 40);
        for (let i = 0; i < 120; i++) { tenir(L); o.frame(1); }
        const f = L.B.defs.rixes.contact;
        const avant = L.Rixe.assaillants(L.B.joueur, f).length;
        gens[0].etat = 'flane';
        return { avant: avant, apres: L.Rixe.assaillants(L.B.joueur, f).length };
    }""" % TROIS)
    assert r["avant"] == 3 and r["apres"] == 2, r


def test_adosse_a_un_mur_il_frappe_quand_meme(banc):
    """La portée prime sur la place : une place dans le mur ne l'empêche pas de cogner."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(23);
        %s
        const j = L.B.joueur, TT = L.TT;
        // Un trottoir dont la tuile du dessus est un mur : le joueur s'y adosse.
        let place = null;
        const c = L.Monde.carte;
        for (let ty = 5; ty < c.h - 5 && !place; ty++) for (let tx = 5; tx < c.w - 5 && !place; tx++) {
          if (L.Monde.marchablePieton(tx, ty) && !L.Monde.marchablePieton(tx, ty - 1)
              && L.Monde.marchablePieton(tx - 2, ty) && L.Monde.marchablePieton(tx + 2, ty)) place = { tx: tx, ty: ty };
        }
        j.x = place.tx * TT + 8; j.y = place.ty * TT + 4;
        L.Monde.centrerCamera(j.x, j.y);
        const gens = trois(L, 30);
        let coups = 0;
        const avant = {};
        for (let i = 0; i < 400; i++) {
          tenir(L); o.frame(1);
          for (const e of gens) { if (e.etat === 'attaque' && avant[e.id] !== 'attaque') coups++; avant[e.id] = e.etat; }
        }
        return { coups: coups };
    }""" % TROIS)
    assert r["coups"] >= 3, "adossé au mur, personne ne le frappe (%s)" % r


def test_il_esquive_parfois_ton_coup(banc):
    """Le joueur arme son bâton vingt fois à portée : le Cravate en esquive quelques-uns, jamais tous."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(24);
        %s
        const j = L.B.joueur;
        L.Combat.ramasserArme('batte', null);
        j.arme = 'batte';
        const e = trois(L, 16)[1];
        let armes = 0;
        for (let i = 0; i < 1400 && armes < 20; i++) {
          tenir(L);
          if (j.etat !== 'attaque' && i % 60 === 0) {
            L.Entites.regarder(j, e.x - j.x, e.y - j.y);
            if (L.Combat.frapper(j, false)) armes++;
          }
          o.frame(1);
        }
        return { armes: armes, esquives: e.rixe ? e.rixe.esquives : -1 };
    }""" % TROIS)
    assert r["armes"] >= 15, "le joueur n'a pas pu armer (%s)" % r
    assert 1 <= r["esquives"] < r["armes"], r
```

  ⚠️ `trois(L, 16)[1]` naît à 16 px : vérifier au premier passage que `creerPieton` le pose bien (sinon
  partir à 20). Et `Combat.ramasserArme(slug, mun)` : lire sa signature (`combat.js` l. 88) avant.

- [ ] `uv run pytest tests/test_rixe_js.py -q` → ROUGE (encercler, esquiver ; `celui_qui_s_en_va` rouge faute
  de `e.rixe`).
- [ ] **Le gang contre toi passe la main** — `static/js/entites.js`, branche `attaque_joueur` : garder tout
  jusqu'à la ligne du salut (`if (e.salut > 0) { … return; }`), puis envelopper la suite :

```js
      const mante = e.techniques && B.defs.mantes;
      if (e.gang && !mante && !e.coupsDictes) {
        // LE CERVEAU DU CONTACT (`rixe.js`) : il t'encercle avec les siens, recule, esquive, frappe a son rythme.
        Rixe.maj(e, B.joueur, vitesse);
      } else {
        // (les lignes d'avant, de `const colle = …` a `if (norme < portee … ) Combat.frapper(e);`, telles
        // quelles — moins leur propre `const mante`, deja lue plus haut)
      }
```

- [ ] `uv run pytest tests/test_rixe_js.py tests/test_bagarre_js.py tests/test_rixes.py -q` → VERT.
- [ ] Commit : `feat: le gang contre toi au contact — il t'encercle, recule et esquive`.

#### Tâche 4 — juger large, regarder, atterrir

- [ ] **Les juges ciblés**, en parallèle (lanceur Python, pas de xdist) : `test_rixes.py`, `test_rixe_js.py`,
  `test_bagarre.py`, `test_bagarre_js.py`, `test_combat_js.py`, `test_pietons.py`, `test_territoires_js.py`,
  `test_definitions.py`, `test_histoire_js.py`, `test_missions_en_scene_js.py`, `test_le_boss_js.py`,
  `test_arc_q_js.py`, `test_arc_p_js.py`, `test_quatre_missions_js.py`, `test_dix_missions_deux_js.py`,
  `test_tripot_js.py`, `test_son_js.py`, `test_routes.py`, `test_hors_ligne.py`. Un rouge : le rejouer sur la base
  (worktree détaché) avant de le croire mien.
- [ ] `uv run ruff check .` → propre.
- [ ] **Regarder** : une capture Chromium (Playwright, werkzeug port 0) d'une rixe allumée et de trois Cravates
  autour du joueur ; l'ouvrir dans Aperçu (copie dans `captures/`).
- [ ] **Atterrir** : commits rejoués sur `dev` (`rebase dev`, puis `merge --ff-only` dans l'arbre principal) ;
  la ligne du plan passe à « ✅ vague 1 livrée : … ; vague 2 à faire » ; ces notes prennent « — **livrée le …** ».
- [ ] La suite complète ensuite, puis `git push`.

### Vague 2 — l'arsenal et la fusillade — **plan** (30 sept. 2026)

> Exécuté comme la vague 1 : sur place, tâche par tâche, juges d'abord, une relecture neuve à la fin.

**But :** un membre de gang sur trois dégaine l'arme de son gang au premier échange et s'en sert en tireur (sa
distance, son abri, ses salves, sa recharge, la levée d'arme, des balles qui manquent) ou en lanceur (le Molotov
des Skateux) — dans la rixe comme contre toi.

**Architecture :** la fiche `rixes.TIR` et `rixes.ARSENAL` (au paquet `B.defs.rixes`) ; `rixe.js` gagne deux
rôles lus sur l'arme en main (`tireur`, `lanceur`) à côté du contact ; `Combat.tirer(e, arme, cible)` vise la
cible passée et, pour un tireur de gang, disperse à l'empreinte ; `blesser` ne retourne plus contre toi celui
qu'un AUTRE a touché.

**Ce que l'exploration a trouvé** (et que le plan corrige) :
- `Combat.tirer` ne note pas `avantLeCoup` : au bout du tir, `majAttaque` rend le PNJ à `'attaque_joueur'` — un
  tireur de rixe se retournerait contre toi à sa première balle.
- `Combat.tirer` d'un PNJ vise toujours le joueur, et sa dispersion tire `B.rng()`.
- `blesser` d'un passant (ou d'un membre de gang hors rixe) par un PIÉTON jette le courage et peut l'envoyer en
  `attaque_joueur` : une balle perdue de rixe le lancerait sur toi.
- `Police.entendre` déplace `dernierVu` (la position que la police te prête) au coup de feu, même d'un autre.
- La bouteille en cloche retombe au bout d'environ 30 images : le Molotov (3,4 px/image) tombe vers 100 px, quelle
  que soit la cible — le lanceur se place à cette distance.

**Contraintes** (de la fiche) : rien au `B.rng()` pour choisir une arme, un abri ou une salve ; un homme de
mission (`cible`, `personnage`), un allié et les Mantes ne reçoivent pas d'arme ; aucune étoile au joueur pour une
rixe armée ; l'agent (`police.js`) tire comme avant (sans `cible`, rien ne change pour lui).

#### Tâche 1 — la fiche du tir, au paquet

`app/rixes.py` : `ARSENAL` (gang → arme : cravates pistolet, morues fusil, chevreuils carabine, boulonneux
mitraillette, skateux molotov), `PART_ARMEE = 3` (un sur trois, `hash2(e.id, …) % 3 == 0`), et `TIR` :
distances par arme (pistolet 70–140, fusil 30–70, carabine 140–210, mitraillette 60–120, molotov 85–110),
`lever_images` 30, `salve` (2, 4), `rafale_images` 24, `entre_salves_images` 70, `recharge_images` 90,
`dispersion_facteur` 2, `abri_tuiles` 5, `degats_contre_joueur` 0,5, `fuite_images` 60. `exporter()` les porte.
Juges (`test_rixes.py`) : chaque arme de l'arsenal existe, est de type `tir`, et sa fourchette tient dans sa
portée ; les Mantes n'ont rien ; la fourchette du Molotov contient sa distance de chute (`vproj` × 30) ; le
paquet les porte ; `MESURE_DU_PAQUET` relevé.

#### Tâche 2 — `Combat.tirer` vise sa cible, et rien ne se retourne contre toi

- `tirer(e, arme, cible)` : `cible` optionnelle (défaut : le joueur, l'agent ne change pas). Avec une cible : il
  note `avantLeCoup` (il reprend la rixe après sa balle), vise la cible, disperse `dispersion × facteur` À
  L'EMPREINTE (`hash2`), fait fuir la rue (`alerter`, menace = lui), s'entend (`Police.entendre(…, autrui)`, qui
  ne touche pas `dernierVu`) et peut valoir une méprise (`crimeDAutrui('arme_sortie')`).
- La balle d'un tireur de gang qui te touche fait `degats × degats_contre_joueur`.
- `blesser` : touché par un piéton (pas par toi), on fuit — le dé du courage est toujours jeté (le hasard ne
  bouge pas), mais il ne décide plus que pour un coup du joueur.
Juges (`test_rixe_js.py`) : la balle part vers la cible et pas vers toi ; après sa balle il est de nouveau en
`bagarre` ; tirer sur une cible ne tire aucun `B.rng()` ; un Cravate hors rixe touché par une Morue fuit ;
`entendre(…, autrui)` laisse `dernierVu` ; la balle d'un Boulonneux te prend moitié moins.

#### Tâche 3 — le tireur et le lanceur

`rixe.js` : `armer(e)` au premier échange (l'arsenal, un sur trois, jamais un homme de mission, un allié ou un
Mante) ; le rôle se lit sur l'arme en main. Le TIREUR : lève l'arme (`lever_images`) avant sa première balle ;
tient sa fourchette de distance ; cherche un ABRI (une tuile marchable à `abri_tuiles` au plus, d'où la cible ne
le voit pas — `Monde.ligneLibre` —, dans sa fourchette, la plus proche ; recherchée toutes les 60 images) ; sort
pour une salve (2 à 4 balles à l'empreinte, ou une rafale de `rafale_images` à la mitraillette), rentre ; recharge
son chargeur (celui de l'arme) en `recharge_images`. Le LANCEUR : se place à sa distance de chute, lance, puis se
sauve `fuite_images` ; ses trois bouteilles lancées, il finit aux poings.
Juges (`test_rixe_js.py`) : un sur trois armé, toujours le même homme, jamais un Mante ni un homme de mission ;
le tireur tient sa fourchette ; il ne tire pas avant la levée ; il recharge (un trou d'au moins `recharge_images`
entre deux balles après son chargeur) ; l'abri trouvé est caché de la cible ; le Molotov part de sa fourchette
et laisse un brasier près de la cible ; la rixe armée à la frontière ne te donne ni étoile ni crime, et personne
ne passe en `attaque_joueur`.

#### Tâche 4 — juger large, regarder, atterrir

Les juges de la vague 1 et la série des missions ; une capture d'une rixe armée ; la ligne du plan et ces notes.
