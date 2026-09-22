"""Un char sous le toit d'un garage n'éclaire rien.

Retour de Martin (22 sept. 2026), capture à l'appui : un char entré dans une carrosserie, caché sous
le toit, et ses phares et ses feux arrière brillaient par-dessus le toit et l'enseigne. Le toit
découpe le DESSIN du char ; les lampes, elles, se composent à la fin de l'image (`Base.fin`) — la
découpe ne les atteignait pas.

⚠️ Par le RENDU : les lampes sont ramassées en dessinant, on lit ce qu'une image vraie a allumé.
"""

NUIT = 0.9

#: Un char mené, posé dans la baie d'un garage (ou ailleurs), et les lampes que l'image allume
#: pour lui. La rue vidée : les lampes d'un autre char ne comptent pas.
BAIE = """
    function lampesDe(L, v) {
      const out = { phare: 0, arriere: 0, faisceau: 0 };
      for (const l of L.Vehicules.lampesDesPhares()) {
        if (l.phare === v) out.phare++;
        if (l.arriere === v) out.arriere++;
        if (l.faisceau === v) out.faisceau++;
      }
      return out;
    }
    function preparer(L) {
      L.Jeu.commencer();
      const t = L.B.defs.conduite.trafic;
      t.vehicules_max = 0; t.stationnes_max = 0; t.garer_la_nuit.max = 0;
      L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
      L.B.partie.heure = %s;
    }
    function poser(L, pg, x, y, angle) {
      const v = L.Vehicules.creer('auto', x, y, angle, { conducteur: 'trafic', etat: 'roule' });
      v.vitesse = 0; v.vx = 0; v.vy = 0;
      pg.admis = v; pg.dedans = v;
      L.B.joueur.x = x + 40; L.B.joueur.y = (pg.y + 4) * L.TT;
      L.Monde.centrerCamera(x, y);
      L.B.partie.heure = %s;
      L.Jeu.rendre();
      return v;
    }
""" % (NUIT, NUIT)


def test_sous_le_toit_de_chaque_garage_un_char_n_allume_rien(banc, paquet):
    """Dans la baie de chaque garage de la ville, rideau baissé, la nuit : pas une lueur, pas
    un faisceau. ⚠️ Le témoin : le même char sorti dans la rue, devant, s'allume."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        const TT = L.TT, out = [];
        for (const pg of L.Monde.portesDeGarage().filter(function (q) { return q.baie; })) {
          pg.ouverture = 0;
          const x = (pg.x + pg.l / 2) * TT, y = (pg.y - pg.baie / 2) * TT + 8;
          const dedans = [];
          for (const angle of [-Math.PI / 2, -Math.PI / 2 + 0.7, Math.PI / 2]) {
            const v = poser(L, pg, x, y, angle);
            dedans.push(lampesDe(L, v));
            L.Entites.retirer(v);
          }
          // Le meme, dans la rue, cinq tuiles devant le rideau.
          const w = poser(L, pg, x, (pg.y + 5) * TT, Math.PI / 2);
          const dehors = lampesDe(L, w);
          L.Entites.retirer(w);
          pg.admis = null; pg.dedans = null;
          out.push({ x: pg.x, y: pg.y, dedans: dedans, dehors: dehors });
        }
        return out;
    }""" % BAIE)
    assert r, "aucun garage à baie dans la ville"
    for g in r:
        for k, d in enumerate(g["dedans"]):
            assert d == {"phare": 0, "arriere": 0, "faisceau": 0}, \
                "garage (%s, %s), char n° %s sous le toit : %s" % (g["x"], g["y"], k, d)
        assert g["dehors"]["phare"] > 0 and g["dehors"]["arriere"] > 0, \
            "garage (%s, %s) : dans la rue, le même char n'éclaire pas — le juge ne mesure rien" % (g["x"], g["y"])


def test_le_nez_dehors_l_avant_eclaire_et_l_arriere_reste_sous_le_toit(banc, paquet):
    """Rideau levé, le char à moitié sorti, le nez vers la rue : ses phares, passés sous le
    linteau, s'allument ; ses feux arrière, encore sous le toit, non."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        const TT = L.TT;
        const pg = L.Monde.portesDeGarage().find(function (q) { return q.baie; });
        pg.ouverture = 1; pg.tient = 999;
        const x = (pg.x + pg.l / 2) * TT, y = L.Monde.basDuRideau(pg);
        const v = poser(L, pg, x, y, Math.PI / 2);
        return lampesDe(L, v);
    }""" % BAIE)
    assert r["phare"] > 0, "le nez dehors, les phares ne s'allument pas : %s" % r
    assert r["arriere"] == 0, "encore sous le toit, les feux arrière brillent à travers : %s" % r
