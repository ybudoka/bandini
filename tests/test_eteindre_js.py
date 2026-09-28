"""`eteindre` a enfin son feu (M16, 28 sept. 2026) — et f13, _Les volontaires_, s'en sert.

Avant, l'objectif attendait qu'AUCUN feu de l'heure ne brûle (`Incendies.feuActif()`), vrai
presque toujours : il passait dans la même image, et aucune mission ne pouvait allumer le sien.
Chaque `eteindre` allume maintenant LE SIEN sur la façade la plus proche de son `ou`
(`Incendies.allumerPourMission`, sans dé), qui résiste un tiers de seconde au jet, ne paie
pas la prime du pompier volontaire (c'est la mission qui paie) et s'en va avec la mission.

Les juges tiennent le jet AU BOUTON (J), comme le joueur — pas `j.phase` posé à la main."""

from test_dix_missions_deux_js import OUTILS, PLUS_LONGUES

#: Se planter au sud du feu, face au mur, et tenir J `n` images.
ARROSER = """
  function devantLeFeu(L, fe) {
    const j = L.B.joueur, p = L.Incendies.position(fe);
    j.x = p.x; j.y = p.y + 18; j.angle = -Math.PI / 2; j.face = 'haut';
    L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
    return p;
  }
  function arroser(L, o, fe, n) {
    const j = L.B.joueur, p = L.Incendies.position(fe);
    o.touche('KeyJ');
    let k = 0;
    for (; k < n && !fe.eteint; k++) { j.x = p.x; j.y = p.y + 18; j.angle = -Math.PI / 2; o.frame(1); ecouter(L); }
    o.relacher('KeyJ'); o.frame(1);
    return k;
  }
"""

AVANT_F13 = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'f11']"


def _f13(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ARROSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_F13 + """);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('mado');
        const sacAvant = !!B.partie.armes.extincteur;
        commencer(L, o, 'f13'); jouer(L, o);
        const sac = B.partie.armes.extincteur;
        const remis = { avant: sacAvant, mun: sac ? sac.mun : null, enMain: j.arme };
        const feux = [], lieux = ['kiosque', 'vetements', 'terminus'];
        for (let i = 0; i < 3; i++) {
            const fe = B.mission.feu, l = L.Histoire.lieu(lieux[i]);
            const p = fe ? L.Incendies.position(fe) : null;
            const c = L.Histoire.cible();
            const info = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), feu: !!fe,
                           loin: p ? Math.round(Math.hypot(p.x - l.x, p.y - l.y) / 16) : null,
                           gps: !!(c && p && c.x === p.x && c.y === p.y) };
            if (!fe) { feux.push(info); break; }
            if (""" + ("true" if lent else "false") + """ && i === 1) {
                for (let k = 0; k < 91 * 60 && B.partie.mission; k++) o.frame(1);
                return { remis: remis, feux: feux, rate: !B.partie.mission, fait: !!B.partie.missionsFaites.f13,
                         feuApres: !!L.Incendies.feuDeMission() };
            }
            // Un seul coup de jet ne suffit pas : il résiste.
            devantLeFeu(L, fe);
            const court = arroser(L, o, fe, 3);
            info.apresUnCoup = { eteint: fe.eteint, etape: etape(L) };
            const images = arroser(L, o, fe, 200);
            jouer(L, o);
            info.images = court + images; info.eteint = fe.eteint; info.apres = etape(L);
            feux.push(info);
        }
        const munFin = B.partie.armes.extincteur ? B.partie.armes.extincteur.mun : null;
        // Le pyromane file avec son bidon (le patron de f03) : on le laisse partir, puis on le casse.
        const f = B.mission.fuyard, depart = f ? { x: f.x, y: f.y } : null;
        jouer(L, o, 300);
        const fuite = { etape: etape(L), fuyard: !!f, ligne: L.Histoire.ligneObjectif(),
                        avance: f ? Math.round(Math.hypot(f.x - depart.x, f.y - depart.y) / 16) : 0 };
        L.Vehicules.endommager(f, 999, j); jouer(L, o, 2);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        L.Entites.assommer(porteur); jouer(L, o, 2);
        const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); jouer(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const mado = L.Histoire.donneur('mado');
        j.x = mado.x - 16; j.y = mado.y; L.Entites.indexer();
        finir(L, o);
        return { dispo: dispo && dispo.slug, remis: remis, feux: feux, munFin: munFin, fuite: fuite, retour: retour,
                 dites: dites, fait: !!B.partie.missionsFaites.f13, argent: argent.map(function (a) { return a.montant; }),
                 feuApres: !!L.Incendies.feuDeMission() };
    }""")


def test_f13_trois_feux_au_jet_le_pyromane_puis_mado(banc):
    r = _f13(banc)
    assert r["dispo"] == "f13", "Mado donne f13 après f11"
    assert r["remis"]["avant"] is False and r["remis"]["mun"] == 100 and r["remis"]["enMain"] == "extincteur", (
        f"Mado met l'extincteur plein dans les mains : {r['remis']}")
    assert len(r["feux"]) == 3, r["feux"]
    for i, (feu, texte) in enumerate(zip(r["feux"], ("ÉTEINS LE FEU DU KIOSQUE", "LA BOUTIQUE DE ROSA", "LE TERMINUS"))):
        assert feu["etape"] == i and feu["feu"], f"le feu {i} n'est pas allumé : {feu}"
        assert feu["ligne"].startswith(texte) and ":" in feu["ligne"], f"l'objectif dit son chrono : {feu['ligne']}"
        assert feu["loin"] <= 4, f"le feu {i} brûle loin de sa porte : {feu}"
        assert feu["gps"], f"la flèche ne pointe pas le feu {i}"
        assert feu["apresUnCoup"] == {"eteint": False, "etape": i}, f"un coup de jet l'éteint : {feu}"
        assert feu["eteint"] and feu["apres"] == i + 1, f"le jet n'a pas éteint le feu {i} : {feu}"
        assert 15 <= feu["images"] <= 40, f"un feu de mission tient un tiers de seconde au jet : {feu}"
    assert r["munFin"] >= 30, f"trois feux laissent de quoi en rater : {r['munFin']}"
    assert r["fuite"]["etape"] == 3 and r["fuite"]["fuyard"] and r["fuite"]["avance"] > 5, r["fuite"]
    assert r["retour"]["etape"] == 4 and r["retour"]["ligne"].startswith("RAPPORTE LE BIDON"), r["retour"]
    for dite in ("pendant:mado:0", "pendant:mado:1", "pendant:mado:2", "pendant:mado:3", "pendant:mado:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], f"la mission paie, pas la prime du feu : {r['argent']}"
    assert r["feuApres"] is False


def test_f13_le_feu_de_rosa_gagne_la_facade_si_on_traine(banc):
    r = _f13(banc, lent=True)
    assert r["rate"] is True and r["fait"] is False, r
    assert r["feuApres"] is False, "une mission ratée n'oublie pas son feu en ville"


def test_un_feu_de_mission_ne_tire_aucun_de_et_ne_paie_pas_la_prime(banc):
    """Le feu brûle (fumée, flammes) à l'empreinte de sa façade, jamais au dé : une scène
    qui le filme, ou une ville qui brûle loin, ne décale pas le hasard de tout le monde."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        const l = L.Histoire.lieu('kiosque');
        const avant = B.rng.etat ? B.rng.etat() : null;
        let tires = 0; const vrai = B.rng;
        B.rng = function () { tires++; return vrai.apply(null, arguments); };
        const fe = L.Incendies.allumerPourMission(l.x, l.y);
        const n0 = B.particules.length;
        for (let k = 0; k < 60; k++) L.Incendies.maj();
        const flammes = B.particules.length - n0;
        B.rng = vrai;
        const p = L.Incendies.position(fe);
        const f = L.Incendies.facadePres(l.x, l.y, 6);
        const mur = !L.Monde.marchablePieton(f.x, f.y) && L.Monde.marchablePieton(f.x, f.y + 1);
        L.Incendies.oublierLeFeuDeMission();
        return { tires: tires, flammes: flammes, mur: mur, feu: !!fe, apres: !!L.Incendies.feuDeMission(),
                 loin: Math.round(Math.hypot(p.x - l.x, p.y - l.y) / 16), avant: avant !== undefined };
    }""")
    assert r["feu"] and r["mur"], "le feu prend sur un mur qu'on peut approcher"
    assert r["loin"] <= 4, r
    assert r["flammes"] > 0, "le feu de mission ne fume pas"
    assert r["tires"] == 0, f"un feu qui brûle a tiré {r['tires']} dé(s)"
    assert r["apres"] is False
