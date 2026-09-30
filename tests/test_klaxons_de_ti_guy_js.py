"""Les klaxons de Ti-Guy, au banc (docs/jalons/les-klaxons-de-ti-guy.md ; Martin, 30 sept. 2026 : « trouve-moi
plein d'idées de klaxon à installer ; je veux que celui existant soit plus gras et plus fort »).

Un klaxon à la fois, au choix, au menu de Ti-Guy : chacun joue le sien et seulement le sien, au BOUTON ; en
poser un remplace l'autre ; un vieux `klaxon: true` joue encore « Gens du pays » ; la corne de 18 roues tasse
les passants de plus loin ; le faux whoop-whoop fait changer de voie le trafic devant, et chauffe devant un
vrai policier — pas devant un vigile, pas sans personne."""

import pytest

from app import garage

KLAXONS = {k["slug"]: k for k in garage.KLAXONS}

#: Un char au joueur, un coup de klaxon au bouton. `mods` : ses pièces. Les effets de `Son` sont remplacés par
#: un greffier (`joues`) : ce qu'on entend, dans l'ordre.
OUTILS = """
  L.Jeu.commencer();
  const T = L.TT, B = L.B, j = B.joueur, V = L.Vehicules, S = L.Son.SFX, Vx = L.Son.Voix;
  function vider() {
    B.entites = B.entites.filter(function (e) { return e === j || !(e.type === 'vehicule' || e.type === 'pieton' || e.type === 'police'); });
    L.Entites.indexer();
  }
  const joues = [];
  let voixArrivee = true;
  const vrais = { claironner: S.claironner, corne_a_air: S.corne_a_air, whoop_police: S.whoop_police, klaxon: S.klaxon, crier: Vx.crier };
  S.claironner = function (notes) { joues.push('air:' + notes.length + ':' + notes[0][0]); };
  S.corne_a_air = function () { joues.push('corne_a_air'); };
  S.whoop_police = function () { joues.push('whoop_police'); };
  S.klaxon = function () { joues.push('klaxon'); };
  Vx.crier = function (slug) { if (!voixArrivee) return false; joues.push('voix:' + slug); return true; };
  function rendre() { Object.assign(S, { claironner: vrais.claironner, corne_a_air: vrais.corne_a_air, whoop_police: vrais.whoop_police, klaxon: vrais.klaxon }); Vx.crier = vrais.crier; }
  /** Monte dans un char neuf posé en (x, y), cap à l'est. */
  function auVolant(x, y, mods) {
    const v = V.creer('auto', x, y, 0, { etat: 'stationne', couleur: '#c0392b' });
    L.Garage.poser(v, mods);
    V.monter(j, v); v.x = x; v.y = y; v.angle = 0; L.Entites.indexer();
    return v;
  }
  /** Un coup au bouton, et le temps que `klaxonT` retombe. */
  function klaxonner() { o.tape('Space', 1); for (let k = 0; k < 40; k++) o.frame(1); }
"""


@pytest.fixture(scope="module")
def klaxons(banc):
    return banc("function (L, o) {" + OUTILS + """
        const out = {};

        // --- Chacun joue le sien -------------------------------------------------------------------------
        out.joue = {};
        for (const m of [null, { klaxon: true }, { klaxon: 'gens_du_pays' }, { klaxon: 'parrain' }, { klaxon: 'cucaracha' },
                         { klaxon: 'corne_a_air' }, { klaxon: 'ti_guy' }, { klaxon: 'police' }]) {
            vider();
            const v = auVolant(j.x + 30, j.y, m);
            joues.length = 0;
            klaxonner();
            out.joue[m ? String(m.klaxon) : 'aucun'] = joues.slice();
            V.descendre(j, true); L.Entites.retirer(v);
        }
        // La voix pas encore arrivée : le klaxon ordinaire, pas le silence.
        vider();
        let v = auVolant(j.x + 30, j.y, { klaxon: 'ti_guy' });
        voixArrivee = false; joues.length = 0; klaxonner(); out.voixAbsente = joues.slice(); voixArrivee = true;
        // Six engueulades de suite : jamais deux fois la même. ⚠️ L'horloge posée au même reste à chaque coup :
        // sans la garde, le tirage à l'empreinte retomberait six fois sur la même.
        joues.length = 0;
        for (let k = 0; k < 6; k++) { B.t = 1000 + k * 35; klaxonner(); }
        out.engueulades = joues.slice();
        V.descendre(j, true); L.Entites.retirer(v);
        // Un char du trafic qui porte un klaxon de Ti-Guy : le klaxon de sa fiche (au joueur seulement).
        vider();
        v = V.creer('auto', j.x + 60, j.y, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        L.Garage.poser(v, { klaxon: 'parrain' });
        out.traficKlaxonDe = L.Garage.klaxonDe(v);
        L.Entites.retirer(v);

        // --- Au menu de Ti-Guy : en poser un remplace l'autre ------------------------------------------
        const p = B.partie;
        p.argent = 5000;
        vider();
        const c = V.creer('auto', j.x + 40, j.y, 0, { etat: 'stationne', couleur: '#c0392b' });
        function menu() {
            B.exterieur = { entites: [c], x: c.x, y: c.y };
            const items = L.Missions.menuGarage([], c).items;
            B.exterieur = null;
            return items;
        }
        function ligne(nom) { return menu().find(function (i) { return i.libelle === 'POSER : ' + nom; }); }
        Vx.demandees.length = 0;
        let avant = p.argent;
        ligne('KLAXON « LE PARRAIN »').faire();
        out.parrain = { paye: avant - p.argent, mods: Object.assign({}, c.mods), voix: Vx.demandees.slice() };
        avant = p.argent;
        ligne('CORNE À AIR DE 18 ROUES').faire();
        const parrain = ligne('KLAXON « LE PARRAIN »'), corne = ligne('CORNE À AIR DE 18 ROUES');
        out.corne = { paye: avant - p.argent, mods: Object.assign({}, c.mods), valeur: L.Garage.valeur(c.mods),
                      parrain: { detail: parrain.detail, actif: parrain.actif }, corne: { detail: corne.detail, actif: corne.actif },
                      lignes: menu().filter(function (i) { return /^POSER : (KLAXON|CORNE|LA VOIX|WHOOP)/.test(i.libelle); }).length };
        out.vieux = { valeur: L.Garage.valeur({ klaxon: true }), slug: L.Garage.klaxonParSlug(true).slug };
        L.Entites.retirer(c);

        // --- La corne de 18 roues tasse de plus loin ------------------------------------------------------
        const b = o.boulevard(false);
        function tasse(mods) {
            vider();
            const v = auVolant(b.x, b.y, mods);
            const q = L.Entites.creerPieton(b.x + 9 * T, b.y, null);
            q.etat = 'arret'; q.minuterie = 5000;
            L.Entites.indexer();
            o.tape('Space', 1); o.frame(3);
            const etat = q.etat;
            V.descendre(j, true); L.Entites.retirer(v); L.Entites.retirer(q); L.Entites.indexer();
            return etat;
        }
        out.tasse = { ordinaire: tasse(null), corne: tasse({ klaxon: 'corne_a_air' }) };

        // --- Le whoop-whoop : le trafic devant change de voie -----------------------------------------------
        const d = o.boulevard(true);
        function cede(mods) {
            vider();
            const v = auVolant(d.x, d.y, mods);
            const q = V.creer('auto', d.x + 4 * T, d.y, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
            q.vitesse = 0.6;
            L.Entites.indexer();
            o.tape('Space', 1); o.frame(3);
            const deport = q.deportT > 0;
            let ecart = 0;
            for (let k = 0; k < 90; k++) { o.frame(1); v.x = d.x; v.y = d.y; v.vitesse = 0; ecart = Math.max(ecart, Math.abs(q.y - d.y)); }
            V.descendre(j, true); L.Entites.retirer(v); L.Entites.retirer(q); L.Entites.indexer();
            return { deport: deport, ecart: Math.round(ecart) };
        }
        out.cede = { ordinaire: cede(null), whoop: cede({ klaxon: 'police' }) };

        // --- …et un vrai policier qui l'entend : un délit -----------------------------------------------------
        function entendu(qui, loin) {
            vider();
            B.crimes.length = 0; B.recherche.redites = {};
            const v = auVolant(d.x, d.y, { klaxon: 'police' });
            if (qui) {
                const a = L.Police.creerAgent(d.x, d.y + loin * T, 'flane', qui === 'garde' ? 'garde' : undefined);
                B.entites.push(a);
            }
            L.Entites.indexer();
            o.tape('Space', 1); o.frame(3);
            const r = B.crimes.filter(function (k) { return k.type === 'fausse_sirene'; }).map(function (k) { return k.rapporte; });
            V.descendre(j, true); L.Entites.retirer(v); vider();
            return r;
        }
        out.police = { personne: entendu(null), policier: entendu('policier', 6), loin: entendu('policier', 30),
                       vigile: entendu('garde', 6) };
        rendre();
        return out;
    }""")


def air(notes: list) -> str:
    """Ce que le greffier écrit d'un air : son nombre de notes et sa première, comme `String()` en JS."""
    return f"air:{len(notes)}:{notes[0][0]:g}"


def test_chaque_klaxon_joue_le_sien_et_seulement_le_sien(klaxons):
    j = klaxons["joue"]
    gens = air(garage.KLAXON_AIR)
    assert j["aucun"] == ["klaxon"], j
    assert j["gens_du_pays"] == [gens], j
    assert j["true"] == [gens], "un vieux `klaxon: true` (les sauvegardes d'avant) doit jouer « Gens du pays »"
    assert j["parrain"] == [air(garage.AIR_PARRAIN)], j
    assert j["cucaracha"] == [air(garage.AIR_CUCARACHA)], j
    assert j["corne_a_air"] == ["corne_a_air"], j
    assert j["police"] == ["whoop_police"], j
    assert len(j["ti_guy"]) == 1 and j["ti_guy"][0] in [f"voix:{s}" for s in KLAXONS["ti_guy"]["voix"]], j


def test_la_voix_de_ti_guy_absente_joue_le_klaxon_et_ne_se_repete_jamais(klaxons):
    assert klaxons["voixAbsente"] == ["klaxon"], "la voix pas encore arrivée : le klaxon ordinaire, pas le silence"
    e = klaxons["engueulades"]
    assert len(e) == 6, e
    assert all(a != b for a, b in zip(e, e[1:])), f"deux fois la même engueulade de suite : {e}"
    assert len(set(e)) >= 3, f"toujours les mêmes engueulades : {e}"


def test_un_char_du_trafic_garde_le_klaxon_de_sa_fiche(klaxons):
    assert klaxons["traficKlaxonDe"] is None


def test_poser_un_klaxon_remplace_l_autre(klaxons):
    p, c = klaxons["parrain"], klaxons["corne"]
    assert p["paye"] == KLAXONS["parrain"]["prix"] and p["mods"] == {"klaxon": "parrain"}, p
    assert "ti_guy-garage-parrain" in p["voix"], p
    assert c["paye"] == KLAXONS["corne_a_air"]["prix"] and c["mods"] == {"klaxon": "corne_a_air"}, c
    assert c["valeur"] == KLAXONS["corne_a_air"]["prix"], "la fourrière ne compte que le klaxon posé"
    assert c["corne"] == {"detail": "POSÉ", "actif": False}, c
    assert c["parrain"] == {"detail": f"{KLAXONS['parrain']['prix']} $", "actif": True}, "le Parrain se repose"
    assert c["lignes"] == len(garage.KLAXONS), c
    assert klaxons["vieux"] == {"valeur": KLAXONS["gens_du_pays"]["prix"], "slug": "gens_du_pays"}


def test_la_corne_de_18_roues_tasse_de_plus_loin(klaxons):
    t = klaxons["tasse"]
    assert t["ordinaire"] == "arret", f"le klaxon ordinaire porte déjà à neuf tuiles : le juge ne mord pas ({t})"
    assert t["corne"] == "tasse", f"la corne à air n'a pas tassé le passant à neuf tuiles : {t}"


def test_le_whoop_whoop_fait_changer_de_voie_le_trafic_devant(klaxons):
    c = klaxons["cede"]
    assert not c["ordinaire"]["deport"], f"le klaxon ordinaire fait déjà changer de voie : le juge ne mord pas ({c})"
    assert c["whoop"]["deport"], f"le trafic devant n'a pas cédé la voie au whoop-whoop : {c}"
    assert c["whoop"]["ecart"] >= 12, f"il a annoncé son déport sans changer de voie : {c}"


def test_le_whoop_whoop_chauffe_devant_un_vrai_policier_seulement(klaxons):
    p = klaxons["police"]
    assert p["personne"] == [], p
    assert p["loin"] == [], f"un policier à trente tuiles n'entend pas : {p}"
    assert p["vigile"] == [], f"un vigile privé n'est pas la police : {p}"
    assert p["policier"] == [True], f"un vrai policier à six tuiles l'a entendu : {p}"
