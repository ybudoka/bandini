"""Rosa habille l'hiver, vague 2 : le froid, la neige, le parapluie qui frappe, la ceinture fléchée.

Tranché par Martin (30 sept. 2026) — `docs/jalons/rosa-habille-l-hiver.md`. Les pièces elles-mêmes
(les places, le dessin) sont jugées dans `test_garderobe.py` et `test_garderobe_js.py`.
"""

from app import saisons

PARTIE = """
    L.Jeu.commencer();
    const B = L.B, p = B.partie, j = B.joueur, M = L.Missions;
    p.argent = 5000;
    const achat = function (slug) {
        const t = B.defs.tenues.find(function (x) { return x.slug === slug; });
        const it = M.menuVetements().items.find(function (i) { return i.libelle === t.nom.toUpperCase(); });
        it.faire();
    };
    // Le moment : `jour` et `heure` (les habits relisent la palette quand l'heure change).
    let pas = 0;
    const moment = function (jour) { p.jour = jour; p.heure = 0.5 + (++pas) * 1e-6; L.Saisons.palette(); };
"""


def _geler(banc, reglage):
    """La vie après dix minutes dehors (36 000 images de `majFroid`), sous le `reglage` donné."""
    return banc("""function (L, o) {
        """ + PARTIE + """
        moment(2);
        B.interieur = null;
        """ + reglage + """
        j.tenue = L.Garderobe.duJoueur(p, B.defs);
        j.vie = j.vieMax; j.froid = 0;
        let premiere = null;
        for (let k = 0; k < 36000; k++) {
            L.Entites.majFroid(j);
            if (premiere === null && j.vie < j.vieMax) premiere = k;
        }
        return { vie: j.vie, max: j.vieMax, premiere: premiere, dit: !!p.froidDit, bulle: j.bulle ? j.bulle.texte : null };
    }""")


def test_le_froid_mord_sans_tuque_ni_bottes_mais_ne_tue_jamais(banc):
    r = _geler(banc, "p.chapeau = null;")
    R = saisons.JOUEUR
    assert r["premiere"] is not None and r["premiere"] >= R["delai_s"] * 60, "il mord, mais pas avant une minute"
    assert r["vie"] == -(-r["max"] * R["plancher"] // 1), f"jamais sous {R['plancher']:.0%} : {r['vie']}/{r['max']}"
    assert r["dit"], "le premier coup de froid dit où acheter une tuque"


def test_une_tuque_seule_ne_suffit_pas_des_bottes_d_hiver_avec_oui(banc):
    seule = _geler(banc, "")                                  # la vieille tuque de Rocco, en souliers
    assert seule["vie"] < seule["max"], "une tuque sans bottes : il gèle quand même"
    deux = _geler(banc, "p.pieds = 'bottes_hiver';")
    assert deux["vie"] == deux["max"] and deux["premiere"] is None


def test_les_bottes_de_loup_marin_suffisent_seules(banc):
    r = _geler(banc, "p.chapeau = null; p.pieds = 'loup_marin';")
    assert r["vie"] == r["max"]


def test_jamais_dedans_ni_en_char_ni_en_juillet_ni_au_cafe(banc):
    for reglage in ("p.chapeau = null; B.interieur = { slug: 'x' };",
                    "p.chapeau = null; j.dansVehicule = { id: 1 };",
                    "p.chapeau = null; moment(21);",
                    "p.chapeau = null; j.cafeine = 1e9;"):
        r = _geler(banc, reglage)
        assert r["vie"] == r["max"], reglage


def test_sans_bottes_la_neige_ralentit_pas_le_deneige(banc):
    r = banc("""function (L, o) {
        """ + PARTIE + """
        moment(2);
        const sol = L.Son.solDuPas;
        const essai = function (pieds, dessous) {
            p.pieds = pieds; j.tenue = L.Garderobe.duJoueur(p, B.defs);
            L.Son.solDuPas = function () { return dessous; };
            const h = L.Entites.hiverAPied(j);
            return h ? h.neige : 1;
        };
        const out = { souliers: essai(null, 'pas_neige'), deneige: essai(null, 'pas'),
                      bottes: essai('bottes_hiver', 'pas_neige'), loup: essai('loup_marin', 'pas_neige') };
        L.Son.solDuPas = sol;
        return out;
    }""")
    assert r == {"souliers": saisons.JOUEUR["neige"], "deneige": 1, "bottes": 1, "loup": 1}, r


def test_le_parapluie_frappe_tant_qu_il_est_a_la_main_et_se_revire(banc):
    r = banc("""function (L, o) {
        """ + PARTIE + """
        achat('parapluie');
        const auSac = !!p.armes.parapluie, def = L.Combat.armeDef('parapluie');
        achat('parapluie');                               // on l'enleve : il sort du sac
        const enleve = !!p.armes.parapluie;
        achat('parapluie');
        for (let k = 0; k < def.usures; k++) L.Combat.userArme(def);
        return { auSac: auSac, enleve: enleve, degats: def.degats, batte: L.Combat.armeDef('batte').degats,
                 apres: { main: p.main, sac: !!p.armes.parapluie, garde: p.tenues.indexOf('parapluie') >= 0 },
                 gus: M.menuArmurerie ? M.menuArmurerie().items.some(function (i) { return /PARAPLUIE/.test(i.libelle || ''); }) : false };
    }""")
    assert r["auSac"] and not r["enleve"], "à la main, il est au sac ; enlevé, il en sort"
    assert 0 < r["degats"] < r["batte"], "un coup faible"
    assert r["apres"] == {"main": None, "sac": False, "garde": False}, "revirer, c'est le perdre : on en rachète un"
    assert not r["gus"], "Gus ne vend pas de parapluies"


def test_le_parapluie_ne_traine_pas_dans_la_rue():
    from pathlib import Path

    from app import armes
    par = next(a for a in armes.CATALOGUE if a["slug"] == "parapluie")
    assert par["prix"] == 0 and par["usures"] > 0
    # `semerDesArmesDeFortune` le filtre par son nom : il serait sinon une arme de fortune.
    source = (Path(__file__).parent.parent / "static" / "js" / "entites.js").read_text(encoding="utf-8")
    assert "a.slug !== 'parapluie'" in source


def test_la_ceinture_flechee_fait_sourire_un_vieux_une_seule_fois(banc):
    r = banc("""function (L, o) {
        """ + PARTIE + """
        moment(2);
        const essai = function (squelette, taille) {
            p.taille = taille; j.tenue = L.Garderobe.duJoueur(p, B.defs);
            for (let q = 0; q < 24; q++) {
                const w = L.Histoire.tuileLibre(j.x + 20, j.y, 3);
                const e = L.Entites.creerPieton(w.x, w.y, L.Entites.archetype('passant'));
                e.tenue = Object.assign({}, e.tenue, { squelette: squelette }); e.etat = 'flane'; e.bulle = null;
                L.Entites.indexer(); B.flecheeT = 0;
                L.Entites.majFlechee();
                const mot = e.bulle ? e.bulle.texte : null;
                if (mot) {
                    e.bulle = null; B.flecheeT = 0; L.Entites.majFlechee();
                    const encore = !!e.bulle;
                    L.Entites.retirer(e);
                    return { mot: mot, encore: encore };
                }
                L.Entites.retirer(e);
            }
            return null;
        };
        return { vieux: essai('vieux', 'ceinture_flechee'), jeune: essai('homme', 'ceinture_flechee'),
                 cuir: essai('vieux', 'ceinture') };
    }""")
    assert r["vieux"] and r["vieux"]["mot"] in saisons.JOUEUR["flechee"]["mots"], r
    assert not r["vieux"]["encore"], "une fois chacun"
    assert r["jeune"] is None, "un jeune s'en fiche"
    assert r["cuir"] is None, "une ceinture de cuir, personne ne la remarque"
