"""Le tour de ce qui ferme l'hiver (docs/jalons/la-foire-fermee-l-hiver.md, vague 2).

Martin (30 sept. 2026) : « fais le tour des choses qui devraient l'être ». Tant que l'hiver tient : le derby
ne se court pas, le camion de crème glacée reste remisé, la cabane de fruits de mer est fermée, les quatre
artistes de rue ne sortent pas, les piscines hors terre sont bâchées, la fontaine est à sec et le barbecue
sous sa housse. Chaque juge regarde janvier (`jour = 2`) ET juillet (`jour = 22`) : une règle qui fermerait
tout l'année serait verte en janvier.
"""

from app import interactions, pietons

OUTILS = """
    function moment(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h === undefined ? 0.5 : h; }
"""


def test_trois_artistes_ont_leur_saison_et_le_jongleur_jongle_avec_le_feu():
    """Le musicien, le mime et l'échassier prennent congé l'hiver ; le jongleur reste, avec ses torches
    (vague 3, `test_foyers_de_l_hiver_js.py`)."""
    artistes = {p["slug"]: p for p in pietons.CATALOGUE if p.get("metier") in ("musicien", "amuseur", "jongleur", "echassier")}
    assert len(artistes) == 4
    assert all(p.get("froid_max") == pietons.ARTISTES_FROID_MAX for s, p in artistes.items() if s != "jongleur"), artistes
    assert artistes["jongleur"].get("froid_max") is None


def test_l_hiver_aucun_artiste_ne_joue_au_faubourg(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, TT = L.TT;
        j.invincible = 1e9;
        // ⚠️ Pas le jongleur : l'hiver, il jongle avec le feu (vague 3).
        const SPECTACLES = ['musicien', 'amuseur', 'echassier'];
        // Au coeur du Faubourg (ou ils jouent), le midi.
        function artistes() { return B.entites.filter(function (e) { return e.vivant && SPECTACLES.indexOf(e.metier) >= 0; }).length; }
        function tenir(jour, n) {
          moment(L, jour);
          for (let i = 0; i < n; i++) { o.frame(1); }
          return artistes();
        }
        // Au centre du Faubourg, par sa zone (`test_amuseurs_js.py`) : c'est la qu'ils jouent.
        const zf = (L.Monde.carte.zones || []).find(function (q) { return q.slug === 'faubourg'; });
        j.x = (zf.x + zf.l / 2) * TT; j.y = (zf.y + zf.h / 2) * TT; L.Monde.centrerCamera(j.x, j.y);
        const ete = tenir(22, 1800);
        // L'hiver arrive : on s'eloigne, ils rentrent hors de l'ecran ; on revient, personne ne ressort.
        moment(L, 2);
        j.x += 90 * TT; L.Monde.centrerCamera(j.x, j.y);
        for (let i = 0; i < 300; i++) o.frame(1);
        j.x -= 90 * TT; L.Monde.centrerCamera(j.x, j.y);
        const hiver = tenir(2, 1800);
        return { ete: ete, hiver: hiver, district: L.Monde.zoneA(j.x, j.y) && L.Monde.zoneA(j.x, j.y).district };
    }""")
    assert r["ete"] > 0, f"en juillet, aucun artiste au {r['district']} : le juge ne voit rien"
    assert r["hiver"] == 0, f"en janvier, {r['hiver']} artistes jouent dehors"


def test_l_hiver_la_cabane_de_fruits_de_mer_est_fermee(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        const c = B.defs.ambulants.find(function (a) { return a.slug === 'fruits_de_mer'; });
        const hotdog = B.defs.ambulants.find(function (a) { return a.slug === 'hotdog'; });
        function etat(jour) {
          moment(L, jour);
          for (let i = 0; i < 60; i++) L.Entites.majKiosques && L.Entites.majKiosques();
          const etals = B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'fruits_de_mer'; });
          return { ouvert: M.ouvert(c), hotdog: M.ouvert(hotdog), etals: etals.length,
                   vendeurs: etals.filter(function (e) { return e.vendeur; }).length };
        }
        return { hiver: etat(2), ete: etat(22) };
    }""")
    h, e = r["hiver"], r["ete"]
    assert e["ouvert"] and e["etals"] > 0, f"en juillet, la cabane est fermée : {e}"
    assert not h["ouvert"], "en janvier, la cabane de fruits de mer est ouverte"
    assert h["hotdog"], "en janvier, le kiosque à hot-dogs a fermé avec elle"


def test_l_hiver_le_derby_ne_se_court_pas(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire;
        const d = B.defs.defis.find(function (x) { return x.slug === 'derby'; });
        B.partie.defisOuverts = B.partie.defisOuverts || {}; B.partie.defisOuverts.derby = true;
        function essai(jour) {
          moment(L, jour, 0.9);
          B.defi = null; B.msg = '';
          H.commencerDefi(d);
          const parti = !!B.defi;
          const msg = B.msg;
          if (B.defi) H.abandonnerDefi();
          if (B.menu) L.Hud.fermerMenu();
          return { parti: parti, msg: msg };
        }
        return { hiver: essai(2), ete: essai(22), hors_hiver: !!d.hors_hiver };
    }""")
    assert r["hors_hiver"]
    assert r["ete"]["parti"], f"en juillet, le derby ne part pas : {r['ete']}"
    assert not r["hiver"]["parti"] and "PRINTEMPS" in r["hiver"]["msg"], r["hiver"]


def test_l_hiver_le_camion_de_creme_glacee_reste_remise(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Missions;
        const place = M.placeDuCamion();
        function camions() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; }).length; }
        function approcher(jour) {
          moment(L, jour);
          j.x = place.x + 300; j.y = place.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
          for (let k = 0; k < 130; k++) o.frame(1);
          return camions();
        }
        const ete = approcher(22);
        // La neige arrive, on n'y regarde pas : il repart hors de l'ecran, et il ne revient pas.
        moment(L, 2);
        j.x = place.x + 900; L.Monde.centrerCamera(j.x, j.y);
        for (let k = 0; k < 130; k++) o.frame(1);
        const parti = camions();
        const hiver = approcher(2);
        return { ete: ete, parti: parti, hiver: hiver };
    }""")
    assert r["ete"] == 1, f"en juillet, {r['ete']} camions : le juge ne voit rien"
    assert r["parti"] == 0 and r["hiver"] == 0, r


def test_l_hiver_la_piscine_hors_terre_est_bachee(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        function eau(jour) {
          moment(L, jour);
          const ctx = L.Base.nouveauCanvas(16, 16).getContext('2d'); ctx.traces = [];
          L.TUILES.o(ctx, 0, 16);
          return ctx.traces.filter(function (t) { return t[4] === '#3fa7c4' || t[4] === '#5cc3dc'; }).length;
        }
        return { hiver: eau(2), ete: eau(22) };
    }""")
    assert r["ete"] > 50, "en juillet, la piscine n'a pas d'eau : le juge ne voit rien"
    assert r["hiver"] == 0, f"en janvier, {r['hiver']} pixels d'eau bleue sous la neige"


def test_l_hiver_la_fontaine_est_a_sec_et_le_barbecue_sous_sa_housse(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, D = L.DECORS;
        j.invincible = 1e9;
        function devant(type, dy) {
          const d = B.entites.find(function (e) { return e.type === 'decor' && e.decor === type && !e.brise; });
          if (!d) return null;
          j.x = d.x; j.y = d.y + dy; j.vx = 0; j.vy = 0; j.face = 'haut'; j.angle = -Math.PI / 2;
          L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
          return d;
        }
        function jet(ferme) {
          const ctx = L.Base.nouveauCanvas(34, 30).getContext('2d'); ctx.traces = [];
          D.fontaine.peindre(ctx, 34, 30, 0, ferme);
          return ctx.traces.filter(function (t) { return t[4] === '#cfe6f5'; }).length;
        }
        const out = {};
        for (const [nom, jour] of [['hiver', 2], ['ete', 22]]) {
          moment(L, jour);
          const f = devant('fontaine', 20), fs = f && L.Interactions.decorSousLaMain(j);
          const b = devant('bbq', 12), bs = b && L.Interactions.decorSousLaMain(j);
          out[nom] = { fontaine: fs ? fs.invite : null, bbq: bs ? bs.invite : null,
                       dortFontaine: L.Entites.poseDuDecor && !!D.fontaine.fermeLHiver };
        }
        out.jet = [jet(false), jet(true)];
        return out;
    }""")
    boire, bbq = interactions.BOIRE, interactions.BARBECUE
    assert r["ete"]["fontaine"] == boire["invite"] and r["ete"]["bbq"] == bbq["invite"], r["ete"]
    assert r["hiver"]["fontaine"] == boire["hiver"], r["hiver"]
    assert r["hiver"]["bbq"] == bbq["hiver"], r["hiver"]
    assert r["jet"][0] > 0 and r["jet"][1] == 0, f"le jet de la fontaine : {r['jet']} (ouvert, fermé)"
