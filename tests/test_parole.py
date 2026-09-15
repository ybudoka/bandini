"""M15, première vague — comment la rue parle, et quand elle se tait.

⚠️ Deux des trois morceaux sont des **correctifs**, et l'un d'eux réparait une
promesse écrite dans le code et jamais tenue : `audio.VOIX` disait « jamais deux
fois de suite le même » alors que le moteur tirait au hasard **sans aucune
mémoire**. Un tirage au hasard PEUT sortir deux fois le même — c'est même sa
définition.
"""

import pytest

from app import audio


def test_les_reglages_de_la_parole_tiennent_ensemble():
    """⚠️ Les trois nombres se décident ENSEMBLE, et c'est pour ça qu'ils sont
    dans une seule fiche.

    La mémoire doit rester **plus courte que la plus petite banque**, sinon la
    règle se retourne contre elle-même : on exclut tout, il ne reste rien à
    tirer, et plus personne ne parle."""
    p = audio.PAROLE
    assert p["temps_mort_images"] >= 240, "la rue parle plus souvent qu'avant, pas moins"
    assert 0 < p["chance"] < 1, "parler doit rester une chance, pas une certitude"
    banques: dict[str, int] = {}
    for voix in audio.VOIX:
        banques[voix["genre"]] = banques.get(voix["genre"], 0) + 1
    plus_petite = min(banques.values())
    assert p["memoire"] < plus_petite, (
        f"la mémoire ({p['memoire']}) atteint la plus petite banque ({plus_petite}) : "
        f"il ne resterait rien à tirer — {banques}"
    )


def test_la_rumeur_tombe_puis_remonte_doucement():
    """⚠️ Elle TOMBE d'un coup et REMONTE doucement. C'est la chute qui se
    remarque, et c'est la remontée lente qui fait qu'on se sent surveillé encore
    un moment après avoir rangé l'arme."""
    r = audio.RUMEUR
    assert 0 < r["peur_part"] < 0.5, "une rue qui a peur doit vraiment se taire"
    assert r["cri_part"] > 1, "après un coup de feu, la foule crie — elle ne murmure pas"
    assert r["peur_images"] >= 120, "la peur passe trop vite pour se sentir"
    # La remontée met au moins deux secondes à retrouver le plein volume.
    assert r["retour_par_image"] * 120 <= 1.0, (
        "la rumeur revient d'un coup : une foule qui reprend son murmure à la seconde "
        "où l'arme rentre dans la poche n'a pas eu peur"
    )


def test_le_clairon_a_de_quoi_enseigner():
    """Le repli « rien à signaler » enseigne une chose par matin calme. ⚠️ Chaque
    leçon dit par quelle statistique on PROUVE qu'on sait déjà : sans elle, le
    jeu expliquerait le taxi à quelqu'un qui a fait trente courses."""
    from app import journal
    assert len(journal.LECONS) >= 4, "le journal a vite fini d'enseigner"
    slugs = [le["slug"] for le in journal.LECONS]
    assert len(slugs) == len(set(slugs)), "deux leçons portent le même slug"
    for lecon in journal.LECONS:
        for champ in ("slug", "cle", "titre", "texte", "lu"):
            assert lecon.get(champ), f"{lecon.get('slug')} : « {champ} » manque"
        assert lecon["titre"] == lecon["titre"].upper(), lecon["slug"]
        # ⚠️ `lu` est ce que le narrateur DIT : en casse naturelle, sinon le TTS
        # épelle les majuscules. Même règle que les manchettes.
        assert lecon["lu"] != lecon["lu"].upper(), (
            f"{lecon['slug']} : le narrateur va épeler les majuscules"
        )


@pytest.mark.parametrize("lecon", [le for le in __import__("app.journal", fromlist=["x"]).LECONS],
                         ids=lambda le: le["slug"])
def test_chaque_lecon_a_sa_voix_declaree(lecon):
    """⚠️ Le narrateur les lit comme une manchette. Tant que les mp3 n'existent
    pas, `exporter()` ne les déclare pas et l'encadré s'affiche sans voix —
    c'est la règle d'`audio.py`, et c'est elle qui permet d'écrire le texte
    avant de dépenser un crédit."""
    voix = {v["slug"] for v in audio.voix_journal()}
    assert f"narrateur-journal-{lecon['slug']}" in voix


def test_le_tirage_des_repliques_passe_par_le_hasard_du_jeu(banc):
    """⚠️ « Jamais deux fois de suite le même » était ÉCRIT dans `audio.VOIX` et
    FAUX dans le moteur : le tirage passait par `Math.random()`, sans mémoire.
    Sur quatre répliques par genre, une chance sur quatre de répéter la
    précédente — dans une rue passante, on entendait « Fait frette, hein? »
    trois fois en vingt secondes.

    ⚠️ Et le tirage passe maintenant par `B.rng()`. Tout le hasard du jeu y
    passe déjà : c'est ce qui rend le banc reproductible, donc juge. Cette
    ligne-là lui échappait — et c'était précisément celle qu'on voulait
    pouvoir tester."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ On juge `tirer`, pas `dire` : `dire` a besoin de tampons charges,
        // donc de fichiers mp3 — le banc n'en a aucun. La REGLE, elle, n'a
        // besoin de rien, et c'est elle qu'on veut tenir.
        const voix = L.B.defs.audio.voix.filter(function (v) { return v.genre === 'homme'; });
        const suite = function (graine) {
            L.graine(graine);
            L.Son.Voix.dernieres = [];
            const dits = [];
            for (let i = 0; i < 12; i++) {
                const v = L.Son.Voix.tirer(voix);
                dits.push(v ? v.slug : null);
            }
            return dits;
        };
        const a = suite(7), b = suite(7), c = suite(8);
        let deuxDeSuite = 0;
        for (let i = 1; i < a.length; i++) if (a[i] && a[i] === a[i - 1]) deuxDeSuite++;
        return { a: a, memeGraine: a.join() === b.join(), autreGraine: a.join() !== c.join(),
                 deuxDeSuite: deuxDeSuite, banque: voix.length,
                 memoire: L.B.defs.audio.parole.memoire };
    }""")
    assert all(r["a"]), "personne ne parle : le juge ne prouve rien"
    # ⚠️ REPRODUCTIBLE : même graine, même suite. C'est ça qui fait du banc un
    # juge, et c'est ce que `Math.random()` interdisait.
    assert r["memeGraine"] is True, "deux parties de même graine ne disent pas la même chose"
    assert r["autreGraine"] is True, "la graine ne change rien : ce n'est plus du hasard"
    # ⚠️ Et jamais deux fois de suite la même — la promesse enfin tenue.
    assert r["deuxDeSuite"] == 0, (
        "%s répétitions immédiates sur douze répliques : %s" % (r["deuxDeSuite"], r["a"])
    )


def test_la_rue_se_tait_devant_une_arme_et_crie_apres_un_coup_de_feu(banc):
    """⚠️ L'ajout le moins cher de toute la vague, et celui qui se sent le plus.
    Une rue qui se tait d'un coup dit « ils t'ont vu » mieux qu'une étoile de
    plus — et elle le dit **avant** que tu regardes le HUD."""
    r = banc("""function (L, o) {
        const R = function () { return L.Son.Rumeur; };
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.arme = 'poings';
        for (let i = 0; i < 300; i++) o.frame(1);
        const calme = R().volume;
        // Une arme au poing : la rue tombe.
        j.arme = 'batte';
        for (let i = 0; i < 60; i++) o.frame(1);
        const peur = R().volume;
        // On la range : elle remonte, mais pas d'un coup.
        j.arme = 'poings';
        o.frame(30);
        const juste_apres = R().volume;
        for (let i = 0; i < 400; i++) o.frame(1);
        const revenue = R().volume;
        // Un coup de feu : elle ne murmure pas, elle CRIE.
        R().crier();
        o.frame(15);
        const cri = R().volume;
        return { calme: +calme.toFixed(3), peur: +peur.toFixed(3),
                 justeApres: +juste_apres.toFixed(3), revenue: +revenue.toFixed(3),
                 cri: +cri.toFixed(3) };
    }""")
    assert r["calme"] > 0.05, "la rue est déjà muette : le juge ne prouve rien (%s)" % r
    assert r["peur"] < r["calme"] * 0.5, "la rue ne se tait pas devant une arme : %s" % r
    # ⚠️ Elle TOMBE d'un coup et REMONTE doucement.
    assert r["justeApres"] < r["calme"], (
        "elle a retrouvé son murmure en une demi-seconde : elle n'a pas eu peur (%s)" % r
    )
    assert r["revenue"] >= r["calme"] * 0.8, "elle ne revient jamais : %s" % r
    # ⚠️ Et après un coup de feu, elle crie — plus fort que son murmure normal.
    assert r["cri"] > r["calme"], (
        "une foule qui murmure pareil avant et après un coup de feu n'est pas une foule, "
        "c'est un bruit de fond (%s)" % r
    )
