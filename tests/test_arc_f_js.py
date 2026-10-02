"""La fin de l'arc F (M16, 28 sept. 2026) — f10 et f12 JOUÉES au bouton, de l'appel à la prime,
sur le modèle de `test_quatre_missions_js.py`. f13, la troisième, a son juge avec `eteindre`
(`test_eteindre_js.py`).

- f10, _La chemise hawaïenne_ : l'option `tenue` (« en la portant ») — arrivé à l'hôtel dans
  le mauvais linge, rien n'avance et la ligne dit quoi enfiler ; Norbert ne reconnaît pas qui ne
  la porte pas. `remet` met la chemise au sac.
- f12, _Le Faubourg te dit merci_ : cinq poignées de main, dehors, `sans_etoile` sur chacune.

⚠️ Depuis le 2 oct. 2026, f10 est l'ACTE 2 de _Rosa et ses clients_ (docs/jalons/des-missions-en-chapitres.md, vague F) :
une partie qui a fait f03 commence au marqueur de l'acte 2 (étape 5), et tout est décalé de 6. f12 reste une mission
(elle attend trois fils : f08, f09 et f10)."""

import pytest

from outils_missions import OUTILS, PLUS_LONGUES

DEDANS = """
  function dedans(L, o, lieu) {
    const B = L.B, j = B.joueur, M = L.Monde;
    aPied(L);
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur ? B.interieur.slug : null;
  }
  function sortir(L, o) {
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
    jouer(L, o);
    return !L.B.interieur;
  }
  // Enfiler une tenue au comptoir de Rosa (le menu que le comptoir ouvre).
  function enfiler(L, nom) {
    const i = L.Missions.menuVetements().items.find(function (x) { return x.libelle === nom; });
    if (i) i.faire();
    return L.B.partie.tenue;
  }
"""


def test_f10_la_chemise_se_porte_pour_que_norbert_ouvre_puis_les_cravates_et_rosa(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm50', 'f01', 'f03']);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('rosa');
        commencer(L, o, 'rosa_et_ses_clients');
        for (let k = 0; k < 20 && etape(L) < 6; k++) { o.frame(1); ecouter(L); }
        jouer(L, o);
        const sac = { a: B.partie.tenues.indexOf('chemise_hawai') >= 0, porte: B.partie.tenue };
        // À l'hôtel dans le chandail : on y est, et rien n'avance.
        const h = L.Histoire.lieu('hotel');
        j.x = h.x; j.y = h.y + 8; L.Entites.indexer(); jouer(L, o, 30);
        const mauvaisLinge = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const porte = enfiler(L, 'CHEMISE HAWAÏENNE'); jouer(L, o);
        const enChemise = { etape: etape(L), porte: porte };
        // Dedans : Norbert au bout du comptoir. Sans la chemise, il ne reconnaît personne.
        const piece = dedans(L, o, 'hotel');
        const norbert = B.entites.find(function (e) { return e.personnage === 'norbert'; });
        const remis = enfiler(L, 'CHANDAIL DE ROCCO');
        const sansElle = serrer(L, o, 'norbert');
        const refus = { etape: etape(L), msg: B.msg || null, ligne: L.Histoire.ligneObjectif() };
        enfiler(L, 'CHEMISE HAWAÏENNE');
        const avecElle = serrer(L, o, 'norbert');
        const lettre = { etape: etape(L) };
        const dehors = sortir(L, o);
        const gars = B.mission.entites.filter(function (e) { return e.cible && e.etape === 8; });
        const bagarre = { etape: etape(L), n: gars.length,
                          hotel: Math.max.apply(null, gars.map(function (e) { return Math.round(Math.hypot(e.x - h.x, e.y - h.y) / 16); })) };
        gars.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        serrer(L, o, 'rosa');
        finir(L, o);
        return { remis: remis, dispo: dispo && dispo.slug, sac: sac, mauvaisLinge: mauvaisLinge, enChemise: enChemise, piece: piece,
                 norbert: !!norbert, sansElle: sansElle, refus: refus, avecElle: avecElle, lettre: lettre, dehors: dehors,
                 bagarre: bagarre, retour: retour, dites: dites, fait: !!B.partie.missionsFaites.f10 && !!B.partie.missionsFaites.rosa_et_ses_clients,
                 argent: argent.map(function (a) { return a.montant; }), contact: !!B.partie.contacts.norbert };
    }""")
    assert r["dispo"] == "rosa_et_ses_clients", "Rosa donne son chapitre, à l'acte 2, après f03"
    assert r["sac"] == {"a": True, "porte": "chandail"}, f"Rosa met la chemise au sac, sans nous l'enfiler : {r['sac']}"
    assert r["mauvaisLinge"]["etape"] == 6 and r["mauvaisLinge"]["ligne"] == "ENFILE : CHEMISE HAWAÏENNE", r["mauvaisLinge"]
    assert r["enChemise"] == {"etape": 7, "porte": "chemise_hawai"}, r["enChemise"]
    assert r["piece"] == "hotel" and r["norbert"], "Norbert se tient dans le hall de l'hôtel"
    assert r["remis"] == "chandail", "le juge n'a pas remis le chandail : il ne regarde rien"
    assert r["refus"]["etape"] == 7 and "ENFILE" in (r["refus"]["msg"] or ""), f"Norbert ouvre à n'importe qui : {r['refus']}"
    assert r["refus"]["ligne"].endswith("ENFILE : CHEMISE HAWAÏENNE"), r["refus"]
    assert r["avecElle"] == "accueil" and r["lettre"]["etape"] == 8, f"la poignée de main de Norbert : {r}"
    assert r["dehors"] and r["bagarre"]["etape"] == 8 and r["bagarre"]["n"] == 2 and r["bagarre"]["hotel"] <= 6, r["bagarre"]
    assert r["retour"]["etape"] == 9 and r["retour"]["ligne"].startswith("RETOURNE VOIR ROSA"), r["retour"]
    for dite in ("pendant:rosa:5", "accueil:norbert:7", "pendant:rosa:6", "pendant:rosa:7", "pendant:norbert:8", "pendant:rosa:9"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300] and r["contact"], r


def _f12(banc, vu=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm50', 'f01', 'f02', 'f03', 'f04', 'f05', 'f06',
                   'f07', 'f08', 'f09', 'f10', 'm51']);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('thibodeau');
        commencer(L, o, 'f12'); jouer(L, o);
        const tournee = [];
        const qui = ['gus', 'rosa', 'mado', 'fern', 'marco'];
        for (let i = 0; i < qui.length; i++) {
            const c = L.Histoire.cible(), d = L.Histoire.donneur(qui[i]);
            const t = { etape: etape(L), gps: !!(c && d && Math.hypot(c.x - d.x, c.y - d.y) < 4) };
            if (""" + ("true" if vu else "false") + """ && i === 2) {
                B.recherche.etoiles = 1; B.recherche.vu = 1; jouer(L, o, 3);
                return { rate: !B.partie.mission, fait: !!B.partie.missionsFaites.f12, tournee: tournee };
            }
            t.partie = serrer(L, o, qui[i]);
            t.apres = etape(L);
            tournee.push(t);
        }
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        serrer(L, o, 'thibodeau');
        finir(L, o);
        return { dispo: dispo && dispo.slug, tournee: tournee, retour: retour, dites: dites,
                 fait: !!B.partie.missionsFaites.f12, argent: argent.map(function (a) { return a.montant; }),
                 rabais: B.partie.rabais.casse_croute };
    }""")


def test_f12_cinq_enveloppes_cinq_poignees_de_main_puis_le_kiosque(banc):
    r = _f12(banc)
    assert r["dispo"] == "f12", "Madame Thibodeau donne f12 après f08, f09 et f10"
    assert len(r["tournee"]) == 5, r["tournee"]
    for i, t in enumerate(r["tournee"]):
        assert t["etape"] == i and t["gps"], f"la flèche ne mène pas au commerçant {i} : {t}"
        assert t["partie"] == "accueil" and t["apres"] == i + 1, f"la poignée de main {i} n'a rien dit ou rien fait : {t}"
    assert r["retour"]["etape"] == 5 and r["retour"]["ligne"].startswith("RAPPORTE LES ENVELOPPES"), r["retour"]
    for qui, n in (("gus", 0), ("rosa", 1), ("mado", 2), ("fern", 3), ("marco", 4)):
        assert f"accueil:{qui}:{n}" in r["dites"], f"{qui} n'a rien dit : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500] and r["rabais"] == 0.9, r


def test_f12_une_etoile_et_personne_ne_paie(banc):
    r = _f12(banc, vu=True)
    assert r["rate"] is True and r["fait"] is False, r
    assert len(r["tournee"]) == 2, "deux enveloppes avant que la police nous voie"


#: Les chapitres du Faubourg (2 oct. 2026, vague F) : (le chapitre, son acte 1 fait, l'étape de son 2e marqueur, qui
#: parle à l'échec de l'acte 2). _Mado et ses volontaires_ a sa reprise dans `test_eteindre_js.py` (le feu de Rosa).
CHAPITRES_F = [
    ("rosa_et_ses_clients", ["m6", "m50", "f01", "f03"], 5, "rosa"),
    ("grand_mo_et_le_kiosque", ["m6", "f04"], 7, "thibodeau"),
    ("deuxieme_service", ["m6", "m50", "f01", "f06"], 5, "marco"),
]


@pytest.mark.parametrize("slug,avant,marqueur,qui", CHAPITRES_F, ids=[c[0] for c in CHAPITRES_F])
def test_un_chapitre_du_faubourg_se_reprend_a_l_acte_2(banc, slug, avant, marqueur, qui):
    """Une vieille partie qui a fait la mission de l'acte 1 commence le chapitre à l'acte 2 ; mort à l'hôpital pendant
    son premier objectif : c'est l'échec de l'acte 2 qu'on entend, l'acte 1 reste fait, et le menu REPRENDRE L'ACTE 2
    ramène au premier objectif de l'acte, pas au début du chapitre."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + DEDANS + """
        L.Jeu.commencer(); L.B.partie.jour = 21; L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5'].concat(""" + str(avant) + """));
        const SLUG = '""" + slug + """', E = """ + str(marqueur + 1) + """;
        const dispo = (L.Histoire.disponibleDe('""" + qui + """') || {}).slug || null;
        commencer(L, o, SLUG);
        for (let k = 0; k < 60 && etape(L) !== null && etape(L) < E; k++) { o.frame(1); ecouter(L); }
        const debut = etape(L);
        L.Missions.hopital('banc');
        for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
        const menu = B.menu ? B.menu.items.map(function (x) { return x.libelle; }) : null;
        const item = B.menu.items.find(function (x) { return x.libelle.indexOf('REPRENDRE') === 0; });
        if (item.faire(item) !== false && B.menu) L.Hud.fermerMenu();
        o.fondu(); for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
        for (let k = 0; k < 60 && etape(L) !== null && etape(L) < E; k++) { o.frame(1); ecouter(L); }
        const m = L.Histoire.courante();
        return { dispo: dispo, debut: debut, menu: menu, echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }),
                 repris: { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L) },
                 acte1: !!B.partie.missionsFaites[m.remplace[0]], acte2: !!B.partie.missionsFaites[m.remplace[1]] };
    }""")
    assert r["debut"] == marqueur + 1, f"une vieille partie reprend à l'acte 2 : {r}"
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 2", "PLUS TARD"], r["menu"]
    assert r["echec"] == [f"echec:{qui}:{marqueur}"], f"l'échec de l'acte 2, pas celui de l'acte 1 : {r['echec']}"
    assert r["repris"] == {"mission": slug, "etape": marqueur + 1}, r["repris"]
    assert r["acte1"] is True and r["acte2"] is False, r
