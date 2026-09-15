"""Ce qui se dit destructible l'est-il vraiment ?

⚠️ **La panne que ce fichier garde.** Jusqu'au 15 sept. 2026, `Entites.briser`
n'avait qu'UN seul appelant : le char lancé. La fiche d'un lampadaire disait
`casse: 0.7` depuis toujours, et on pouvait lui vider un chargeur de carabine
dessus sans qu'il bronche — la balle traversait le décor, l'explosion d'un char
ne filtrait que `q.vivant`, le brasier d'un molotov non plus.

Et la moitié la plus sournoise : `buisson` et `corde_a_linge` déclaraient
`casse` avec `solide: false`. L'index du décor ne prenait QUE le solide, et
c'est dans cet index que le char cherche ce qu'il renverse. Deux fiches qui se
disaient destructibles depuis le premier jour, et que **rien au monde** ne
pouvait toucher.

Deux filets, comme la carte du dépôt : `scripts/verifier_ce_qui_casse.py` lit
le catalogue et le câblage (et deux gardes Claude Code l'appellent plus tôt,
à l'écriture et avant le commit) ; les juges de banc, eux, tirent pour de vrai.
"""

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))

import verifier_ce_qui_casse as juge  # noqa: E402


# --- Le catalogue et le câblage ---------------------------------------------


def test_le_depot_passe_son_propre_juge(racine):
    """Le dernier filet : ce que les gardes Claude Code disent plus tôt."""
    sortie = subprocess.run(
        [sys.executable, "scripts/verifier_ce_qui_casse.py"],
        cwd=racine,
        capture_output=True,
        text=True,
    )
    assert sortie.returncode == 0, sortie.stderr


def test_le_juge_lit_vraiment_le_catalogue(racine):
    """⚠️ Un juge qui ne lit rien ne rougit jamais. Celui-ci parse du JS : s'il
    perdait `const DECORS` (renommé, déplacé, réécrit en module), il rendrait un
    catalogue vide et resterait **vert pour toujours**. On vérifie donc qu'il
    voit les fiches, et qu'il en lit les bons chiffres."""
    source = (racine / "static/js/sprites.js").read_text(encoding="utf-8")
    fiches = juge.fiches(source)
    assert len(fiches) > 15, "le lecteur de catalogue ne trouve presque rien : %d" % len(fiches)
    assert fiches["lampadaire"]["casse"] == "0.7"
    assert fiches["lampadaire"]["pv"] == "60"
    assert "pv" not in fiches["arbre"], "un arbre ne tombe pas à l'arme"
    assert fiches["arbre"]["arrete"] == "2.0"


def _sources(racine):
    return {c: (racine / c).read_text(encoding="utf-8") for c in juge.SURVEILLES}


def test_un_decor_qui_casse_sans_pv_est_vu(racine):
    """La panne d'origine, refaite à la main : le lampadaire qui encaisse."""
    sources = _sources(racine)
    sources[juge.SPRITES] = sources[juge.SPRITES].replace("casse: 0.7, pv: 60,", "casse: 0.7,")
    reproches = juge.juger(sources)
    assert any("lampadaire" in r and "pv" in r for r in reproches), reproches


def test_un_decor_solide_fantome_pour_les_chars_est_vu(racine):
    """Le décor qu'on ajoute un jour en oubliant sa fiche : solide pour les
    gens, et l'autobus le traverse."""
    sources = _sources(racine)
    sources[juge.SPRITES] = sources[juge.SPRITES].replace(
        "  poubelle: {",
        "  parcometre: { w: 6, h: 18, ancre: [3, 17], r: 2, solide: true },\n  poubelle: {",
    )
    reproches = juge.juger(sources)
    assert any("parcometre" in r for r in reproches), reproches


def test_un_arbre_qu_on_rendrait_cassable_est_vu(racine):
    """L'autre sens : ce qui ARRÊTE un char encaisse les balles. Un arbre avec
    des `pv`, c'est une rue qu'on démonte au pistolet."""
    sources = _sources(racine)
    sources[juge.SPRITES] = sources[juge.SPRITES].replace(
        "arbre: { arrete: 2.0,", "arbre: { arrete: 2.0, pv: 40,"
    )
    assert any("arbre" in r for r in juge.juger(sources))


def test_une_arme_debranchee_est_vue(racine):
    """Le câblage : la fiche ne vaut rien si personne ne s'en sert. On coupe
    chacun des trois chemins, un par un."""
    for fichier, motif in (
        (juge.COMBAT, "Entites.endommagerDecor("),      # la balle et le feu
        (juge.VEHICULES, "Entites.endommagerDecor("),   # l'explosion
        (juge.VEHICULES, "Entites.briser("),            # le char
        (juge.ENTITES, "function endommagerDecor("),    # la fonction elle-même
    ):
        sources = _sources(racine)
        sources[fichier] = sources[fichier].replace(motif, "void 0 && (")
        assert juge.juger(sources), "couper « %s » dans %s ne rougit pas" % (motif, fichier)


# --- Et le jeu, pour de vrai ------------------------------------------------


#: Trouve un décor de cette sorte dans la ville et plante le joueur devant, à
#: `recul` pixels à sa gauche, en le rendant intouchable (on tire, pas on meurt).
_DEVANT = """
    function devant(sorte, recul) {
      const d = L.B.entites.find(function (q) {
        return q.type === 'decor' && q.decor === sorte && !q.brise;
      });
      if (!d) throw new Error('aucun ' + sorte + ' dans la ville');
      const j = L.B.joueur;
      j.x = d.x - recul; j.y = d.y; j.intouchable = true;
      L.Entites.regarder(j, 1, 0);
      L.Entites.indexer();
      return d;
    }
    function vider(arme, coups) {
      const j = L.B.joueur, def = L.Combat.armeDef(arme);
      let tires = 0;
      for (let c = 0; c < coups; c++) {
        L.B.partie.armes[arme] = { mun: 99, usure: 0 };
        j.etat = 'flane'; j.phase = null;
        L.Combat.tirer(j, def);
        tires++;
        for (let i = 0; i < 30; i++) { L.B.t++; L.Entites.indexer(); L.Combat.maj(); }
      }
      return tires;
    }
"""


def test_une_balle_abat_un_lampadaire(banc):
    """⚠️ LE JUGE DE LA PANNE. Un lampadaire porte `casse: 0.7` : un char le
    couche. Avant le 15 sept. 2026, une carabine ne lui faisait rien du tout.

    60 PV, et le pistolet en met 30 : il tombe au DEUXIÈME coup, pas au premier
    — sinon une balle perdue démonte la rue. Et il laisse des débris."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        """ + _DEVANT + """
        const poteau = devant('lampadaire', 40);
        const fiche = L.DECORS.lampadaire;
        vider('pistolet', 1);
        const apresUn = { brise: !!poteau.brise, pv: poteau.pv };
        vider('pistolet', 1);
        const debris = L.B.entites.filter(function (q) { return q.debris && !q.brise; }).length;
        return { pvFiche: fiche.pv, apresUn: apresUn, brise: !!poteau.brise,
                 solide: poteau.solide, dessine: poteau.dessine, debris: debris };
    }""")
    assert r["pvFiche"] == 60
    assert r["apresUn"]["brise"] is False, "un lampadaire ne tombe pas sur UNE balle de pistolet"
    assert r["apresUn"]["pv"] == 30, "la première balle n'a pas mordu : %s" % r["apresUn"]
    assert r["brise"] is True, "deux balles de pistolet et le lampadaire tient encore"
    assert r["solide"] is False and r["dessine"] is False, "un poteau à terre reste debout"
    assert r["debris"] >= 1, "il est tombé sans laisser de débris"


def test_un_arbre_encaisse_un_chargeur_et_arrete_la_balle(banc):
    """L'autre moitié de la règle : ce qui ARRÊTE un char n'a pas de `pv` et ne
    tombe JAMAIS. Un arbre encaisse une mitraillette entière — et il arrête la
    balle, ce qui en fait un abri. Sans ça, une fusillade se passerait dans une
    rue où plus rien ne protège au bout de trois secondes."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        """ + _DEVANT + """
        const arbre = devant('arbre', 40);
        const projectiles = function () {
          return L.B.entites.filter(function (q) { return q.type === 'projectile'; }).length;
        };
        vider('carabine', 5);
        return { brise: !!arbre.brise, entame: arbre.pv !== undefined,
                 pvFiche: L.DECORS.arbre.pv || null,
                 solide: arbre.solide, restants: projectiles() };
    }""")
    assert r["pvFiche"] is None, "un arbre ne doit pas avoir de `pv`"
    assert r["brise"] is False, "cinq balles de carabine ont abattu un arbre"
    assert r["entame"] is False, "l'arbre s'est fait entamer alors qu'il encaisse"
    assert r["solide"] is True
    assert r["restants"] == 0, "les balles ont traversé l'arbre au lieu de s'y planter"


def test_un_banc_est_un_abri_sans_etre_un_bouclier(banc):
    """⚠️ LA MESURE QUI DÉCIDE DE TOUT : de combien la balle « attrape » un décor.

    Le canon crache à hauteur de poitrine (`y - 6`) et un décor est ancré à ses
    PIEDS. La première version rattrapait l'écart en élargissant la cible de
    sept pixels — le chiffre du test des gens. Un banc se retrouvait avec une
    prise de douze pixels de rayon, **plus large que celle d'un passant** : la
    balle s'arrêtait dessus avant d'atteindre quelqu'un qui se tenait à côté.
    Un banc devenait un gilet pare-balles.

    Les deux moitiés, dans le même juge : devant le banc on prend la balle,
    derrière le banc on est à l'abri. C'est la seule façon de dire qu'un
    chiffre est le bon — l'un ou l'autre seul se règle en le tordant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        """ + _DEVANT + """
        const siege = devant('banc', 40);
        const j = L.B.joueur;
        function tirerSur(dx, dy) {
          const c = L.Entites.creerPieton(siege.x + dx, siege.y + dy, L.Entites.archetype('ouvrier'));
          c.etat = 'fige'; c.vie = 100; c.vieMax = 100;
          j.x = siege.x - 40; j.y = c.y; j.intouchable = true;
          L.Entites.regarder(j, 1, 0);
          L.Entites.indexer();
          vider('pistolet', 1);
          const touche = c.vie < c.vieMax;
          L.Entites.retirer(c);
          return touche;
        }
        // Devant le banc, sur le trottoir : rien ne s'interpose.
        const aCote = tirerSur(0, 10);
        // Derrière le banc, pile dans son axe : le banc encaisse.
        const derriere = tirerSur(25, 0);
        return { aCote: aCote, derriere: derriere, brise: !!siege.brise };
    }""")
    assert r["aCote"] is True, (
        "un passant à côté du banc n'a pas pris la balle : le banc sur-protège"
    )
    assert r["derriere"] is False, (
        "le banc n'arrête plus rien : il n'y a plus d'abri dans une fusillade"
    )


def test_un_buisson_tombe_et_n_arrete_rien(banc):
    """⚠️ LA SECONDE PANNE, et la plus vieille. `buisson` et `corde_a_linge`
    portent `casse` avec `solide: false` — et l'index du décor ne prenait que le
    SOLIDE. C'est dans cet index que le char cherche ce qu'il renverse : deux
    fiches destructibles sur le papier que **rien** ne pouvait toucher, depuis
    le premier jour.

    ⚠️ La règle existait en DEUX exemplaires — `reindexerDecor` et `creerDecor`
    — et le premier correctif n'en a touché qu'un : le buisson entrait dans
    l'index après le premier bris de la partie, jamais à la construction de la
    ville. Ce juge tire sur un buisson de la vraie carte, pas sur un posé à la
    main, et c'est ce qui a attrapé la copie oubliée.

    L'index le porte maintenant, mais il ne bloque toujours rien : on le
    traverse à pied et la balle le dépasse. Ce qui tranche, c'est `solide`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        """ + _DEVANT + """
        const buisson = devant('buisson', 40);
        const j = L.B.joueur;
        // À pied : on marche DANS le buisson, il ne repousse pas.
        j.x = buisson.x - 12; j.y = buisson.y;
        for (let i = 0; i < 12; i++) L.Entites.deplacerCercle(j, 1, 0, 0);
        const traverse = j.x >= buisson.x - 0.5;
        // Et un passant DERRIÈRE lui prend quand même la balle.
        const derriere = L.Entites.creerPieton(buisson.x + 25, buisson.y, L.Entites.archetype('ouvrier'));
        derriere.etat = 'fige'; derriere.vie = 100; derriere.vieMax = 100;
        j.x = buisson.x - 40; j.y = buisson.y; j.intouchable = true;
        L.Entites.regarder(j, 1, 0); L.Entites.indexer();
        // La mitraillette : 9 points, et surtout elle ne tire pas EN CLOCHE —
        // une bille de fronde passerait par-dessus le buisson sans le voir.
        vider('mitraillette', 1);
        const apresUn = { brise: !!buisson.brise, pv: buisson.pv,
                          passant: derriere.vie < derriere.vieMax };
        vider('mitraillette', 1);
        return { pvFiche: L.DECORS.buisson.pv, solide: buisson.solide,
                 traverse: traverse, apresUn: apresUn, brise: !!buisson.brise };
    }""")
    assert r["pvFiche"] == 15 and r["solide"] is False
    assert r["traverse"] is True, "un buisson bloque maintenant le passage à pied"
    assert r["apresUn"]["brise"] is False and r["apresUn"]["pv"] == 6, (
        "la balle n'a pas mordu le buisson — est-il seulement dans l'index ? %s"
        % r["apresUn"]
    )
    assert r["apresUn"]["passant"] is True, (
        "le buisson a arrêté la balle : ce qui n'est pas `solide` n'arrête rien"
    )
    assert r["brise"] is True, "deux rafales et le buisson tient encore"


def test_une_explosion_emporte_le_decor_autour(banc):
    """`Entites.autour(…, q.vivant)` ne voit pas le décor — il ne vit pas. Un
    cratère avec le lampadaire encore debout au milieu ne se croit pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        """ + _DEVANT + """
        const poteau = devant('lampadaire', 0);
        const j = L.B.joueur;
        const v = L.Vehicules.creer('auto', poteau.x + 10, poteau.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        return { etat: v.etat, brise: !!poteau.brise, pv: poteau.pv };
    }""")
    assert r["etat"] == "epave"
    assert r["brise"] is True, "le lampadaire est resté debout dans le cratère : %s" % r


def test_le_lendemain_rend_les_pv_entames(banc):
    """Ce qu'une arme a entamé sans l'abattre se referme au matin, comme le
    reste. ⚠️ Sans ça, un poteau à demi troué par une balle du mardi tomberait
    d'une seule balle le vendredi — et le quartier s'userait tout seul."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        """ + _DEVANT + """
        const poteau = devant('lampadaire', 40);
        vider('pistolet', 1);
        const entame = poteau.pv;
        L.Entites.reparerLeDecor();
        const apresNuit = poteau.pv;
        vider('pistolet', 1);
        return { entame: entame, apresNuit: apresNuit === undefined ? null : apresNuit,
                 brise: !!poteau.brise, pvApres: poteau.pv };
    }""")
    assert r["entame"] == 30, "la balle n'a pas entamé le poteau"
    assert r["apresNuit"] is None, "les PV entamés ont survécu à la nuit : %s" % r
    assert r["brise"] is False and r["pvApres"] == 30, (
        "le poteau réparé est tombé d'une seule balle : %s" % r
    )
