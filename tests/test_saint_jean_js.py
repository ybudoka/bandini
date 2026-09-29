"""La Saint-Jean, au banc (docs/jalons/la-saint-jean-sur-la-baie.md) : le soir du 24 juin seulement, le
défilé ferme SA rue (à la place de l'entrave du jour) et la rend après ; ses chars la remontent dans
l'ordre ; les feux partent à 22 h sans tirer un dé ; le Clairon l'annonce. Et côté Python : la rue du défilé
est une rue que la carte sait déjà barrer sans couper la ville, dans le Faubourg ; le soir tient dans la journée."""

import villes

from app import calendrier, saint_jean

FETE = """
  function aLHeure(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h / 24; }
  function laFete(L) { return L.B.defs.calendrier.dates.saint_jean; }
"""


def test_le_defile_ferme_sa_rue_le_soir_de_la_fete_seulement(banc):
    r = banc("function (L, o) {" + FETE + """
        L.Jeu.commencer();
        const B = L.B, Mo = L.Monde, f = laFete(L), rue = B.defs.saint_jean.rue;
        function fermee() {
            const b = Mo.barrieres().find(function (q) { return q.slug === 'defile'; });
            return b ? { ferme: Mo.barriereFermee(b), x: b.x, y: b.y, plein: b.plein } : null;
        }
        aLHeure(L, f, 15); const apresMidi = fermee();
        aLHeure(L, f, 20); const soir = fermee(); const entrave = Mo.entraveDuJour().slug;
        aLHeure(L, f, 23); const apres = fermee();
        aLHeure(L, f + 1, 20); const lendemain = fermee();
        aLHeure(L, f + B.defs.calendrier.annee, 20); const anDApres = fermee();
        return { rue: rue, apresMidi: apresMidi, soir: soir, entrave: entrave, apres: apres, lendemain: lendemain, anDApres: anDApres };
    }""")
    assert r["apresMidi"] is None and r["apres"] is None and r["lendemain"] is None, r
    assert r["soir"] == {"ferme": True, "x": r["rue"]["x"], "y": r["rue"]["y"], "plein": True}, r
    assert r["entrave"] == "defile", "le soir de la fête, la rue du défilé n'a pas pris la place de l'entrave du jour"
    assert r["anDApres"], "la Saint-Jean ne revient pas l'année suivante"


def test_les_chars_remontent_la_rue_dans_l_ordre(banc):
    r = banc("function (L, o) {" + FETE + """
        L.Jeu.commencer();
        const B = L.B, S = L.SaintJean, f = laFete(L), rue = B.defs.saint_jean.rue, h = B.defs.saint_jean.horaire.defile;
        const vertical = rue.h >= rue.l, suivi = [];
        for (let k = 0; k <= 20; k++) {
            aLHeure(L, f, h[0] + (h[1] - h[0]) * k / 20);
            suivi.push(S.chars().map(function (c) { return { k: c.k, s: vertical ? c.y : c.x, x: c.x, y: c.y }; }));
        }
        return { rue: rue, vertical: vertical, suivi: suivi };
    }""")
    rue = r["rue"]
    vus = set()
    tete = {}
    for image in r["suivi"]:
        for c in image:
            vus.add(c["k"])
            assert rue["x"] * 16 <= c["x"] <= (rue["x"] + rue["l"]) * 16 and rue["y"] * 16 <= c["y"] <= (rue["y"] + rue["h"]) * 16, (
                f"un char hors de sa rue : {c}")
            assert c["s"] >= tete.get(c["k"], -1), f"le char {c['k']} recule"
            tete[c["k"]] = c["s"]
        for a, b in zip(image, image[1:]):
            assert (a["s"] - b["s"]) * (b["k"] - a["k"]) >= 0, "les chars se doublent"
    assert vus == set(range(4)), f"tous les chars ne sont pas passés : {vus}"
    assert r["suivi"][0] == [] or r["suivi"][-1] == [], "le défilé ne commence ni ne finit hors de la rue"


def test_les_feux_partent_a_22_h_sans_tirer_un_de(banc):
    r = banc("function (L, o) {" + FETE + """
        L.Jeu.commencer();
        const B = L.B, S = L.SaintJean, f = laFete(L);
        const ctx = { fillRect: function () {}, set fillStyle(c) {}, set globalAlpha(a) {} };
        aLHeure(L, f, 20); const avant = S.fusees().length;
        aLHeure(L, f, 22.2);
        L.graine(9); const temoin = [B.rng(), B.rng()]; L.graine(9);
        let vues = 0, lampes = 0;
        for (let k = 0; k < 300; k++) { B.t++; S.maj(); vues = Math.max(vues, S.fusees().length); S.dessinerFeux(ctx, { x: 0, y: 0 }); lampes = Math.max(lampes, S.lampes({ x: 0, y: 0 }).length); }
        const apresRng = [B.rng(), B.rng()];
        aLHeure(L, f + 1, 22.2); const lendemain = S.fusees().length;
        return { avant: avant, vues: vues, lampes: lampes, temoin: temoin, apresRng: apresRng, lendemain: lendemain };
    }""")
    assert r["avant"] == 0 and r["lendemain"] == 0, r
    assert r["vues"] >= 2 and r["lampes"] >= 1, r
    assert r["apresRng"] == r["temoin"], "les feux ont tiré au dé du jeu"


def test_le_clairon_l_annonce(banc):
    r = banc("function (L, o) {" + FETE + """
        L.Jeu.commencer();
        const f = laFete(L), l = {};
        for (const k of [-2, -1, 0, 1]) { L.B.partie.jour = f + k; l[k] = L.SaintJean.ligneDuClairon(); }
        return l;
    }""")
    from app import saint_jean
    assert r["-2"] is None and r["1"] is None, r
    assert r["-1"] == saint_jean.CLAIRON["veille"] and r["0"] == saint_jean.CLAIRON["jour"], r


# --- La rue du défilé et le soir de la fête, côté Python --------------------------------------------


def test_la_rue_du_defile_est_une_fermeture_du_faubourg_qui_n_enferme_rien():
    v = villes.exporter()
    r = saint_jean.rue_du_defile(v)
    assert r, "pas de rue pour le défilé"
    rues = [{k: f[k] for k in ("x", "y", "l", "h")} for f in v["fermetures"] if not f.get("ecartee")]
    assert r in rues, "le défilé ferme une rue que le juge de connexité n'a pas vue"
    z = next(q for q in v["zones"] if q.get("district") == "faubourg" and q.get("slug") == "faubourg")
    assert z["x"] <= r["x"] and r["x"] + r["l"] <= z["x"] + z["l"] and z["y"] <= r["y"] and r["y"] + r["h"] <= z["y"] + z["h"]
    assert max(r["l"], r["h"]) >= saint_jean.DEFILE["ecart_tuiles"] * 2, "trop courte pour un défilé"


def test_le_soir_de_la_fete_et_le_paquet():
    h = saint_jean.HORAIRE
    assert 17 <= h["defile"][0] < h["defile"][1] <= h["feux"][0] < h["feux"][1] <= 24
    assert calendrier.mois(calendrier.DATES["saint_jean"]) == "juin"
    assert villes.assembler()["saint_jean"] == saint_jean.pour_le_navigateur(villes.exporter())
