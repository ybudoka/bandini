"""Le téléphone qui trie (M16, 28 sept. 2026) — la fiche : « un appel par demi-journée, jamais
pendant une mission, jamais à 3★ et plus ; le donneur le plus proche appelle d'abord ».

Avec les quarante missions d'aujourd'hui (et cent demain), m6 en ouvre une dizaine d'un coup :
le combiné sonnait pour la première du catalogue, puis la suivante 45 s après chaque mission
finie. Jugé ici au banc, sur la vraie boucle (`o.frame`), jamais en appelant `majTelephone`."""

#: Une partie juste après m6 : une dizaine de missions s'annoncent au téléphone.
APRES_M6 = """
  function apresM6(L) {
    L.Jeu.commencer();
    const p = L.B.partie;
    ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { p.missionsFaites[s] = 1; });
    p.appels = {}; p.appelT = null; p.dernierAppel = null;
    // ⚠️ Invincible : planté devant la cantine, les Morues le couchaient, et l'hôpital (dedans)
    // retient le téléphone — on jugeait la bagarre, pas l'appel.
    L.B.joueur.invincible = 1e6;
    return p;
  }
  function demi(L) { return L.B.partie.jour * 2 + (L.B.partie.heure >= 0.5 ? 1 : 0); }
  // Jusqu'au prochain appel (sa première réplique ouverte), `n` images au plus.
  // `garder` (facultatif) repasse à chaque image : planter le joueur, tenir les étoiles.
  function attendreUnAppel(L, o, n, garder) {
    for (let i = 0; i < n; i++) {
      if (garder) garder();
      o.frame(1);
      const c = L.B.cinema;
      if (c && c.partie === 'appel') {
        const r = { i: i, demi: demi(L), qui: c.lignes[0].qui, slug: Object.keys(L.B.partie.appels).slice(-1)[0] };
        L.Histoire.finir();
        return r;
      }
    }
    return null;
  }
"""


def test_jamais_deux_appels_dans_la_meme_demi_journee(banc):
    """On prend la mission annoncée et on la finit tout de suite : avant, la suivante sonnait
    45 s plus tard (`DELAI_APPEL`) — dans la même demi-journée. Elle attend maintenant midi
    (ou minuit), et sonne dès qu'il arrive."""
    r = banc("function (L, o) {" + APRES_M6 + """
        const p = apresM6(L);
        p.heure = 0.02;                      // tôt : la demi-journée a presque quatre minutes devant elle
        const premier = attendreUnAppel(L, o, 4000);
        p.missionsFaites[premier.slug] = 1;  // prise et finie dans la foulée
        const second = attendreUnAppel(L, o, 20000);
        return { premier: premier, second: second, dernier: p.dernierAppel, heure: p.heure };
    }""")
    assert r["premier"] and r["second"], r
    assert r["second"]["demi"] == r["premier"]["demi"] + 1, f"deux appels dans la même demi-journée : {r}"
    assert r["second"]["slug"] != r["premier"]["slug"]
    # Il sonne à l'ouverture de la demi-journée suivante, pas une relance plus tard.
    assert 0.5 <= r["heure"] < 0.52, f"l'appel attendait midi et a traîné après : heure {r['heure']}"
    assert r["dernier"] == r["second"]["demi"]


def test_jamais_a_trois_etoiles(banc):
    r = banc("function (L, o) {" + APRES_M6 + """
        const p = apresM6(L), R = L.B.recherche;
        // ⚠️ La police se tait : à trois étoiles vraies, elle arrête le joueur en cinq secondes, le
        // menu « ARRÊTÉ » fige la partie, et le téléphone se taisait pour une autre raison (vu au banc).
        L.Police.maj = function () {};
        let sonne = false, images = 0;
        for (let i = 0; i < 6000; i++) {
            const t = L.B.t;
            R.etoiles = 3; R.vu = 0; o.frame(1);
            if (L.B.t > t) images++;
            if (L.B.sonnerie || L.B.cinema) { sonne = true; break; }
        }
        // La poursuite finie (les étoiles tombent pour de bon), l'appel retenu sonne.
        const apres = attendreUnAppel(L, o, 900, function () { R.etoiles = 0; R.vu = 0; });
        return { sonne: sonne, apres: apres, images: images, menu: !!L.B.menu };
    }""")
    assert r["sonne"] is False, "le téléphone sonne en pleine poursuite à trois étoiles"
    assert r["images"] >= 5900 and not r["menu"], f"la partie était figée, le juge ne regardait rien : {r}"
    assert r["apres"] is not None, "l'appel retenu par la poursuite ne sonne plus jamais"


def test_le_donneur_le_plus_proche_appelle_d_abord(banc):
    """Deux parties au même point de l'histoire, le joueur planté à deux bouts de la ville :
    ce n'est pas le même qui appelle, et c'est chaque fois celui dont la porte est la plus près."""
    corps = """function (L, o) {""" + APRES_M6 + """
        const p = apresM6(L), j = L.B.joueur;
        const lieu = L.Histoire.lieu('%s');
        // Planté à deux tuiles de la porte, sans y entrer (la foule pousse).
        const appel = attendreUnAppel(L, o, 4000, function () { j.x = lieu.x + 32; j.y = lieu.y + 32; j.vx = 0; j.vy = 0; });
        // Le plus proche, compté ici : parmi ce qui s'annonçait, la porte la plus près.
        const proches = L.Histoire.disponibles().filter(function (m) { return m.prerequis.length; })
            .map(function (m) { const q = L.Histoire.lieuDuPersonnage(m.donneur); return { qui: m.donneur, d: q ? Math.hypot(q.x - j.x, q.y - j.y) : 1e9 }; })
            .sort(function (a, b) { return a.d - b.d; });
        return { qui: appel && appel.qui, attendu: proches[0].qui, n: proches.length, dedans: !!L.B.interieur };
    }"""
    phare = banc(corps % "phare")
    cantine = banc(corps % "cantine")
    assert phare["qui"] == phare["attendu"], phare
    assert cantine["qui"] == cantine["attendu"], cantine
    assert phare["qui"] != cantine["qui"], f"le même donneur appelle des deux bouts de la ville : {phare} {cantine}"
