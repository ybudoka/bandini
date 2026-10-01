"""Le p'tit perdu (M16, vague 22, 1er oct. 2026) — `chercher` : quelqu'un SE CACHE, on le cherche à pied, on le ramène.

- t07 jouée au bouton : la mère te hèle, son p'tit est caché à quatre à dix tuiles d'elle (invisible), la ligne dit
  FROID, TIÈDE, CHAUD, BRÛLANT ; trouvé, il te suit ; revenir sans lui ne finit rien ; avec lui, la mère paie.
- Il se cache SANS UN DÉ et hors de la suite des numéros : la ville d'une partie où il se cache est la même ; et la même
  journée, il se cache au même endroit."""

from test_jobs_js import AIDES as AIDES_JOBS

BASE = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"

AIDES = AIDES_JOBS + """
  function prendreT07(L, o) {
    poserA(L, 'cantine', 40);
    L.Jobs.offrir('t07', true);
    const mere = L.B.job.e;
    const pris = luiParler(L, o);
    return { pris: pris, mere: mere };
  }
"""


def test_t07_le_p_tit_cache_trouve_a_pied_et_ramene_a_sa_mere(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        const argent = paiements(L);
        const d = prendreT07(L, o);
        jouer(L, o, 4);
        const c = B.mission.cachette, e = c && c.e;
        const cache = { arch: e && e.arch, dessine: e ? e.dessine : null, etape: etape(L),
                        mere: e ? Math.round(Math.hypot(e.x - d.mere.x, e.y - d.mere.y) / 16) : null,
                        eau: e ? L.Monde.estEau(Math.floor(e.x / 16), Math.floor(e.y / 16)) : null,
                        chaussee: e ? L.Monde.estChaussee(Math.floor(e.x / 16), Math.floor(e.y / 16)) : null };
        // FROID loin, BRÛLANT tout près : la ligne d'objectif le dit.
        const lignes = [];
        for (const dt of [14, 8, 4, 2]) {
          j.x = e.x + dt * 16; j.y = e.y; L.Entites.indexer(); jouer(L, o, 2);
          lignes.push(L.Histoire.ligneObjectif());
        }
        const pasEncore = etape(L);
        // À pied, à côté de lui : trouvé.
        j.x = e.x + 10; j.y = e.y; L.Entites.indexer(); jouer(L, o, 4);
        const trouve = { etape: etape(L), dessine: e.dessine, suit: e.suit === j, protege: B.mission.protege === e };
        // Revenir sans lui : il est resté loin derrière (posé à vingt tuiles), la mère attend.
        e.x = d.mere.x + 320; e.y = d.mere.y; e.suit = null;
        j.x = d.mere.x - 14; j.y = d.mere.y; L.Entites.indexer(); jouer(L, o, 2);
        const sansLui = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        e.x = j.x + 12; e.y = j.y; e.suit = j; L.Entites.indexer();
        finir(L, o);
        return { pris: d.pris, cache: cache, lignes: lignes, pasEncore: pasEncore, trouve: trouve, sansLui: sansLui,
                 dites: dites, fait: !!p.missionsFaites.t07, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t07", r
    c = r["cache"]
    assert c["arch"] == "enfant" and c["dessine"] is False and c["etape"] == 0, c
    assert 4 <= c["mere"] <= 11 and c["eau"] is False and c["chaussee"] is False, c
    assert [lg.split(" — ")[-1] for lg in r["lignes"]] == ["FROID", "TIÈDE", "CHAUD", "BRÛLANT"], r["lignes"]
    assert r["pasEncore"] == 0
    assert r["trouve"] == {"etape": 1, "dessine": True, "suit": True, "protege": True}, r["trouve"]
    assert r["sansLui"]["etape"] == 1 and "PAS AVEC TOI" in r["sansLui"]["ligne"], r["sansLui"]
    assert "pendant:passante:0" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [60], r


def test_il_se_cache_sans_de_ni_numero_et_au_meme_endroit(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        prendreT07(L, o);
        const m = L.Histoire.mission('t07'), o0 = m.objectifs[0], un = B.mission.cachette.e;
        function prochain() { const e = L.Entites.creer('decor', 0, 0); L.Entites.retirer(e); return e.id; }
        L.graine(77); const de = B.rng(); const id0 = prochain();
        L.graine(77); const deux = L.Histoire.poserLaCachette(m, o0); const de2 = B.rng(); const id1 = prochain();
        return { de: de, de2: de2, id0: id0, id1: id1, idCache: deux.id, meme: un.x === deux.x && un.y === deux.y };
    }""")
    assert r["idCache"] >= 1e9, r
    assert r["de"] == r["de2"], f"il a tiré un dé de la ville en se cachant : {r}"
    assert r["id1"] == r["id0"] + 1, f"il a pris un numéro de la ville : {r}"
    assert r["meme"] is True, f"la même journée, il se cache au même endroit : {r}"
