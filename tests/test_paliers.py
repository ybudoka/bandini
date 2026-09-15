"""Les boulots montent en grade — la première des quatre activités du net.

⚠️ **Un boulot qui paie et rien d'autre n'est pas une activité, c'est un
distributeur.** Les paliers transforment « je fais trois courses pour manger »
en « j'en fais cinquante parce qu'au bout il y a quelque chose ».

⚠️ Et ce qu'on y gagne n'est presque jamais de l'argent : un palier qui paie
mieux rend le boulot meilleur que la mission, et le jeu se joue tout seul. Ce
qu'on gagne, ce sont des CAPACITÉS.
"""

import pytest

from app import economie


def test_chaque_boulot_a_ses_trois_paliers_et_ils_montent():
    """Trois paliers par boulot, dans l'ordre, et jamais deux fois le même
    compte — un palier qui tomberait au même moment qu'un autre volerait
    l'annonce du premier."""
    assert set(economie.PALIERS) == set(economie.BOULOTS), (
        "un boulot sans paliers, ou des paliers sans boulot"
    )
    for slug, paliers in economie.PALIERS.items():
        comptes = [p["compte"] for p in paliers]
        assert len(paliers) == 3, f"{slug} : {len(paliers)} paliers"
        assert comptes == sorted(set(comptes)), f"{slug} : {comptes}"
        assert comptes[0] >= 5, f"{slug} : le premier palier tombe trop tôt"


@pytest.mark.parametrize("slug", sorted(economie.PALIERS))
def test_un_palier_dit_ce_qu_il_donne_et_le_navigateur_sait_le_faire(slug):
    """⚠️ Le défaut qui revient, dans les deux sens : une fiche que le
    navigateur ne lit pas, ou un `type` que le navigateur ne sait pas servir.
    `PALIERS_TYPES` est la moitié d'un contrat — l'autre est `avantage()` et
    `donnerLePalier()` dans `missions.js`."""
    for palier in economie.PALIERS[slug]:
        assert palier["type"] in economie.PALIERS_TYPES, palier
        for champ in ("compte", "type", "valeur", "nom", "detail"):
            assert palier.get(champ) not in (None, ""), f"{slug} : « {champ} » manque"
        assert palier["nom"] == palier["nom"].upper(), palier["nom"]
        assert palier["detail"] == palier["detail"].upper(), palier["detail"]
        if palier["type"] == "char":
            from app import vehicules
            assert vehicules.par_slug(palier["valeur"]), (
                f"{slug} : « {palier['valeur']} » n'est pas au catalogue — "
                "un palier qui promet un char et n'en pose aucun est pire que pas de palier"
            )
        if palier["type"] == "rabais":
            assert palier.get("cle"), f"{slug} : un rabais sans clé ne s'applique nulle part"


def test_aucun_palier_ne_fait_passer_un_boulot_devant_tous_les_autres():
    """⚠️ LE JUGE QUI TIENT L'ÉQUILIBRE, et il regarde le joueur QUI A TOUT
    DÉBLOQUÉ, pas le débutant : un déséquilibre qu'on met cinquante courses à
    fabriquer ne se verrait nulle part si on ne mesurait que le premier jour.

    C'est la même borne que `test_chaque_boulot_vaut_la_peine` — on la rejoue
    avec les primes de palier, parce qu'une borne qui ne vaut qu'au premier
    jour n'est pas une borne."""
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    for slug in economie.BOULOTS:
        gain = economie.gain_avec_paliers(slug)
        assert taxi <= gain <= 4 * taxi, (
            f"{slug} rapporte {gain} $ tous paliers faits, contre {taxi} $ au taxi de base"
        )
        par_seconde = gain / (20 * economie.BOULOTS[slug]["etapes"])
        assert par_seconde < economie.GAIN_MAX_PAR_SECONDE, slug


def test_les_recompenses_ne_sont_presque_jamais_de_l_argent():
    """⚠️ Ce qu'on gagne, ce sont des CAPACITÉS. Un seul type touche à l'argent
    du boulot lui-même — au-delà, faire son boulot paierait mieux que de jouer
    l'histoire, et le jeu se jouerait tout seul."""
    types = [p["type"] for liste in economie.PALIERS.values() for p in liste]
    payants = [t for t in types if t == "prime"]
    assert len(payants) <= len(economie.PALIERS), (
        "plus d'un palier payant par boulot : ce n'est plus une capacité, c'est une paie"
    )
    assert len(set(types)) >= 4, "les paliers se ressemblent tous : il n'y a rien à viser"


def test_la_fiche_descend_au_navigateur():
    paquet = economie.exporter()
    assert set(paquet["paliers"]) == set(economie.PALIERS)
    for slug, liste in economie.PALIERS.items():
        assert paquet["paliers"][slug] == [dict(p) for p in liste]


# --- Les paliers en jeu ------------------------------------------------------

DECOR = """
    L.Jeu.commencer();
    L.graine(11);
    const p = L.B.partie, paliers = L.B.defs.economie.paliers;
    const faire = function (slug, n) {
        for (let i = 0; i < n; i++) L.Missions.compterLeBoulot(slug);
    };
"""


def test_un_palier_ne_se_donne_qu_une_fois_et_sa_recompense_existe(banc):
    """⚠️ Un palier qui promet un char et n'en pose aucun est pire que pas de
    palier du tout. Et il est marqué AVANT que sa récompense soit posée : sinon
    le char se regarait à chaque sauvegarde."""
    r = banc("""function (L, o) {
        %s
        const cible = paliers.taxi.find(function (q) { return q.type === 'char'; });
        faire('taxi', cible.compte - 1);
        const avant = { debloque: L.Missions.palierDebloque('taxi', cible),
                        char: p.planque.vehicule };
        faire('taxi', 1);
        const apres = { debloque: L.Missions.palierDebloque('taxi', cible),
                        char: p.planque.vehicule ? p.planque.vehicule.slug : null };
        // On efface le char et on continue : il ne se regare pas tout seul.
        p.planque.vehicule = null;
        faire('taxi', 40);
        return { avant: avant, apres: apres, voulu: cible.valeur,
                 regare: p.planque.vehicule, compte: p.boulots.taxi };
    }""" % DECOR)
    assert r["avant"]["debloque"] is False and r["avant"]["char"] is None, (
        "le palier tombe avant son compte : %s" % r
    )
    assert r["apres"]["debloque"] is True, "le palier ne tombe jamais : %s" % r
    assert r["apres"]["char"] == r["voulu"], "le char promis n'est pas garé : %s" % r
    assert r["regare"] is None, "le palier se redonne : le char se regare tout seul (%s)" % r


def test_le_compte_des_boulots_survit_a_la_partie(banc):
    """⚠️ Le compte vivait sur le module `boulot`, donc il repartait de zéro à
    chaque rechargement — « cinquante courses » n'aurait jamais voulu dire quoi
    que ce soit. Et `histoire.js` le lisait pour la mission des courses : elle
    comptait les courses de la SESSION, pas celles du joueur."""
    r = banc("""function (L, o) {
        %s
        faire('taxi', 7);
        const sauve = JSON.parse(JSON.stringify(p));
        const repris = L.Sauvegarde.completer(sauve, L.B.defs);
        return { dansLaPartie: p.boulots.taxi, apresReprise: repris.boulots.taxi,
                 vuParHistoire: L.Missions.boulot.faits.taxi };
    }""" % DECOR)
    assert r["dansLaPartie"] == 7, r
    assert r["apresReprise"] == 7, "le compte ne survit pas à une reprise : %s" % r
    assert r["vuParHistoire"] == 7, "l'histoire ne voit pas le vrai compte : %s" % r


def test_le_plus_fort_gagne_et_les_paliers_ne_s_additionnent_pas(banc):
    """⚠️ Sans cette règle, « +10 % puis +25 % de vie » ferait +35 %, et la
    fiche dirait une chose pendant que le jeu en ferait une autre."""
    r = banc("""function (L, o) {
        %s
        const vies = paliers.ambulance.filter(function (q) { return q.type === 'vie'; });
        const base = L.Missions.avantage('vie', 1);
        faire('ambulance', vies[0].compte);
        const unSeul = L.Missions.avantage('vie', 1);
        faire('ambulance', vies[1].compte - vies[0].compte);
        const lesDeux = L.Missions.avantage('vie', 1);
        return { base: base, unSeul: unSeul, lesDeux: lesDeux,
                 attendu: vies[1].valeur, somme: vies[0].valeur + vies[1].valeur };
    }""" % DECOR)
    assert r["base"] == 1, "un avantage tombe sans palier : %s" % r
    assert r["unSeul"] == economie.PALIERS["ambulance"][0]["valeur"], r
    assert r["lesDeux"] == r["attendu"], (
        "les deux paliers de vie s'additionnent au lieu de se remplacer : %s" % r
    )


def test_la_vie_du_joueur_suit_vraiment_le_palier(banc):
    """⚠️ Le seul avantage qui ne se lise pas au moment de s'en servir : une
    barre de vie se décide à la naissance. Il fallait donc que `vieMax` cesse
    d'être un littéral — et un juge qui ne mesurerait que `avantage()` ne
    l'aurait jamais vu."""
    r = banc("""function (L, o) {
        %s
        const base = L.B.joueur.vieMax;
        const vies = paliers.ambulance.filter(function (q) { return q.type === 'vie'; });
        faire('ambulance', vies[1].compte);
        // On renaît : c'est là que la barre se décide.
        L.Entites.creerJoueur(L.B.joueur.x, L.B.joueur.y, p);
        return { base: base, apres: L.B.joueur.vieMax, valeur: vies[1].valeur };
    }""" % DECOR)
    assert r["base"] == 100, "le décor du juge est faux : %s" % r
    assert r["apres"] == round(100 * r["valeur"]), (
        "la vie ne suit pas le palier : %s" % r
    )


def test_le_lot_finit_par_ne_plus_rien_prendre(banc):
    """Les deux paliers de remorquage se lisent au comptoir de la fourrière —
    ⚠️ et à moitié prix puis gratuit, c'est le PLUS PETIT qui gagne : un rabais
    se compare à l'envers d'un bonus."""
    r = banc("""function (L, o) {
        %s
        const plein = L.Missions.prixRachat('auto');
        const p1 = paliers.remorquage[0], p2 = paliers.remorquage[1];
        faire('remorquage', p1.compte);
        const moitie = L.Missions.prixRachat('auto');
        faire('remorquage', p2.compte - p1.compte);
        return { plein: plein, moitie: moitie, gratuit: L.Missions.prixRachat('auto') };
    }""" % DECOR)
    assert r["plein"] > 0, "le décor du juge est faux : le rachat est déjà gratuit (%s)" % r
    assert r["moitie"] == round(r["plein"] * economie.PALIERS["remorquage"][0]["valeur"]), r
    assert r["gratuit"] == 0, "le lot fait encore payer : %s" % r
