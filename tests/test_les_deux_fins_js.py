"""M13 — les deux fins. _Sacrer son camp_ (m99), JOUÉE au banc jusqu'au générique.

Le juge de structure (`erreurs_de_mise_en_scene`) dit qu'un générique a sa scène, ses répliques et
`donne.generique` ; ici, on le VOIT se jouer : le capitaine Bérubé au bout du quai, la nuit qu'on
attend, le passage qu'on paie, le traversier qui largue avec le joueur sur le pont — puis la fin,
le générique (le narrateur, les chiffres de la partie dans les cartons), le BILAN, et une ville
où l'on joue encore.

_Le Boss_ (m98) viendra avec la vague 2 : il demande quatre districts libérés, et un seul se libère
aujourd'hui (docs/jalons/m13-les-deux-fins.md).
"""

OUTILS = """
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function ici(L, l) { const j = L.B.joueur; j.x = l.x; j.y = l.y; L.Entites.indexer(); }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function pas(L, o, n) { for (let k = 0; k < (n || 3); k++) { o.frame(1); fermer(L); } }
  // L'heure `h` (en heures) — le traversier ne dépend que d'elle (`Traversier.placeA`).
  function aLHeure(L, h) { L.B.partie.heure = (h / 24) % 1; }
"""

PREPARER = """
        L.Jeu.commencer(); L.graine(9);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
"""


def test_le_capitaine_berube_se_tient_au_bout_du_quai_du_traversier(banc):
    """`ou: "traversier:quais"` : posé à côté du bout du quai, sur du marchable, là où la flèche
    du GPS d'un `aller` vers `traversier:quais` le trouve."""
    r = banc("function (L, o) {" + OUTILS + PREPARER + """
        const b = L.Histoire.donneur('berube'), q = L.Histoire.lieu('traversier:quais');
        return { b: b ? { x: b.x, y: b.y, marche: L.Monde.marchablePieton(Math.floor(b.x / L.TT), Math.floor(b.y / L.TT)) } : null,
                 q: q ? { x: q.x, y: q.y, nom: q.nom } : null,
                 pointe: !!L.Histoire.lieu('traversier:pointe'), rien: L.Histoire.lieu('traversier:nulle_part') };
    }""")
    assert r["q"], "le quai du traversier n'est pas un lieu"
    assert r["pointe"] and r["rien"] is None
    assert r["b"], "le capitaine Bérubé n'est pas en ville"
    assert r["b"]["marche"], "Bérubé se tient dans l'eau"
    d = ((r["b"]["x"] - r["q"]["x"]) ** 2 + (r["b"]["y"] - r["q"]["y"]) ** 2) ** 0.5
    assert d <= 6 * 16, f"Bérubé est à {d:.0f} px du quai — un `aller` de rayon 6 ne l'atteindrait pas"


def test_m99_le_dernier_traversier_se_joue_jusqu_au_generique_puis_la_ville_reste(banc):
    """De jour, Bérubé fait attendre la nuit ; la nuit tombée, le passage se paie (500 $) ; sur le
    pont à 23 h 54, le traversier largue à minuit — la mission est faite. La fin se dit DEVANT le
    capitaine, puis le générique : le narrateur (sans nom au-dessus de la boîte), les chiffres de
    la partie dans les cartons, la musique `generique`. Ensuite le BILAN s'ouvre, la fin est
    retenue (`fins`), Bérubé a quitté la ville, et on rejoue : le traversier accoste à La Pointe
    et le joueur en descend à pied."""
    r = banc("function (L, o) {" + OUTILS + PREPARER + """
        B.partie.argent = 16000;
        aLHeure(L, 12);
        const berube = L.Histoire.donneur('berube');
        ici(L, { x: berube.x - 16, y: berube.y });
        const out = { parle: L.Histoire.parler('berube') };
        passer(L, o);
        out.slug = B.partie.mission && B.partie.mission.slug;
        // 0. De jour : on attend la nuit, au quai.
        pas(L, o, 5);
        out.jour = { etape: etape(L), attend: B.mission && B.mission.attend };
        // La nuit : 23 h 54, le traversier à quai aux Quais, départ à minuit.
        aLHeure(L, 23.9);
        const argent = B.partie.argent;
        pas(L, o, 5);
        out.nuit = { etape: etape(L), paye: argent - B.partie.argent, ligne: L.Histoire.ligneObjectif() };
        // 2. Sur le pont.
        o.frame(2);
        const d = L.Traversier.donnees(), q = d.escales.find(function (e) { return e.district === 'quais'; });
        const rang = d.coque.cabine === 0 ? 1 : 0;
        ici(L, { x: (q.x + 2) * L.TT + 8, y: (q.y + rang) * L.TT + 8 });
        const vus = { narrateur: 0, berube: 0, anonyme: true, cartons: [], musique: null, generique: false };
        let n = 0;
        for (; n < 4000 && B.partie.mission; n++) o.frame(1);
        out.largue = { images: n, fini: !B.partie.mission, aBord: !!j.aBord, faite: !!B.partie.missionsFaites.m99 };
        // La fin, puis le générique.
        for (let k = 0; k < 9000 && (B.scene || B.cinema || B.generiqueEnAttente || B.finEnAttente); k++) {
            const c = B.cinema, l = c && c.lignes[Math.max(0, c.i)];
            if (l && l.qui === 'narrateur') { vus.narrateur++; if (!c.anonyme) vus.anonyme = false; }
            if (l && l.qui === 'berube') vus.berube++;
            if (B.scene && B.scene.carton && B.scene.carton.texte && vus.cartons.indexOf(B.scene.carton.texte) < 0) vus.cartons.push(B.scene.carton.texte);
            if (B.scene && B.scene.plans === (B.defs.missions.find(function (m) { return m.slug === 'm99'; }).scenes || {}).generique) vus.generique = true;
            if (B.scene && B.scene.musique && !vus.musique) vus.musique = B.scene.musique;
            o.frame(1);
            if (c && k % 20 === 0) L.Histoire.suivante();
        }
        out.apres = { scene: !!B.scene, cinema: !!B.cinema, menu: B.menu ? B.menu.titre : null,
                      fins: Object.keys(B.partie.fins || {}), berube: !!L.Histoire.donneur('berube') };
        out.vus = vus;
        out.valeurs = { argent: B.partie.argent, coffre: (B.partie.planque && B.partie.planque.coffre) || 0 };
        // La partie continue : on ferme le BILAN, le traversier traverse et accoste en face.
        L.Hud.fermerMenu();
        for (let k = 0; k < 20000 && j.aBord; k++) o.frame(1);
        out.accoste = { aBord: !!j.aBord, pointe: L.Traversier.escaleIci(j) ? L.Traversier.escaleIci(j).district : null };
        const x0 = j.x, y0 = j.y;
        o.touche('KeyW'); o.frame(30); o.relacher('KeyW');
        o.touche('KeyD'); o.frame(30); o.relacher('KeyD');
        out.bouge = Math.round(Math.hypot(j.x - x0, j.y - y0));
        return out;
    }""")
    assert r["parle"] and r["slug"] == "m99", r
    assert r["jour"]["etape"] == 0 and r["jour"]["attend"] == "ATTENDS LA NUIT", r["jour"]
    assert r["nuit"]["etape"] == 2 and r["nuit"]["paye"] == 500, r["nuit"]
    assert r["largue"]["fini"] and r["largue"]["faite"], r["largue"]
    assert r["vus"]["berube"] >= 2, "la fin ne se dit pas"
    assert r["vus"]["generique"], "le générique ne s'est pas joué"
    assert r["vus"]["narrateur"] >= 4 and r["vus"]["anonyme"], r["vus"]
    assert r["vus"]["musique"] == "generique", r["vus"]
    fortune = r["valeurs"]["argent"] + r["valeurs"]["coffre"]
    assert f"{fortune:,}".replace(",", " ") + " $" in r["vus"]["cartons"], r["vus"]["cartons"]
    assert "7" in r["vus"]["cartons"], "sept missions faites (m1 à m6, et m99)"
    assert any(c.endswith("À SAL") or c == "RÉGLÉE" for c in r["vus"]["cartons"]), r["vus"]["cartons"]
    assert not any("{" in c for c in r["vus"]["cartons"]), r["vus"]["cartons"]
    assert r["apres"]["menu"] == "BILAN" and not r["apres"]["scene"] and not r["apres"]["cinema"], r["apres"]
    assert r["apres"]["fins"] == ["m99"], r["apres"]
    assert not r["apres"]["berube"], "Bérubé est encore au quai après son dernier traversier"
    assert not r["accoste"]["aBord"] and r["accoste"]["pointe"] == "pointe", r["accoste"]
    assert r["bouge"] > 10, "après le générique, le joueur ne bouge plus"


def test_m99_ne_s_ouvre_qu_avec_quinze_mille_piastres(banc):
    """`exige: {argent_min: 15000}` : sans l'argent, Bérubé n'a pas de mission à donner."""
    r = banc("function (L, o) {" + OUTILS + PREPARER + """
        B.partie.argent = 14999;
        const pauvre = L.Histoire.disponibleDe ? !!L.Histoire.disponibleDe('berube') : null;
        B.partie.argent = 15000;
        const riche = L.Histoire.disponibleDe ? !!L.Histoire.disponibleDe('berube') : null;
        return { pauvre: pauvre, riche: riche };
    }""")
    assert r == {"pauvre": False, "riche": True}, r
