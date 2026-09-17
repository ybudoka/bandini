"""Ça travaille : les chantiers en jeu.

⚠️ Python a jugé la géométrie de chaque phase (`test_chantiers.py`). Ici on juge
ce que le JEU en fait : poser la bonne phase le bon jour, jamais sous les yeux,
jamais sur quelqu'un, et défaire proprement ce qui appartenait à la maison.

⚠️ `Chantiers.maj` ne regarde qu'une image sur `CADENCE` (30) : un juge qui veut
voir une phase se poser laisse tourner au moins deux cadences.
"""

from app import chantiers

#: Loin de tout chantier : le joueur y est posé quand on veut qu'une phase ait le
#: droit de se poser. Choisi à l'exécution (voir `LOIN`).
LOIN = """
  function loin(L) {
    const liste = L.Chantiers.liste;
    const w = L.Monde.carte.w, h = L.Monde.carte.h;
    for (let y = 4; y < h - 4; y += 3) {
      for (let x = 4; x < w - 4; x += 3) {
        if (L.Monde.solidite(x, y) !== 0 || !L.Monde.carte.legende[L.Monde.carte.sol[y][x]].trottoir) continue;
        const assez = liste.every(function (ch) {
          const d = ch.def;
          return Math.abs(x - (d.x + d.l / 2)) > 60 || Math.abs(y - (d.y + d.h / 2)) > 40;
        });
        if (assez) return { x: x * 16 + 8, y: y * 16 + 8 };
      }
    }
    throw new Error('aucun trottoir loin des chantiers');
  }
  // ⚠️ L'horloge des chantiers SEULE, sans faire tourner la ville : en cent
  // images, le reste du jeu range ce qui traîne loin du joueur (un char garé,
  // une arme par terre) et le juge ne mesurerait plus rien.
  function tourner(L, cadences) {
    for (let k = 0; k < cadences * L.Chantiers.CADENCE + 1; k++) L.Chantiers.maj();
  }
  function poserLeJoueur(L, p) {
    const j = L.B.joueur; j.x = p.x; j.y = p.y; j.vx = 0; j.vy = 0; j.intouchable = true;
    L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
  }
"""


def _juge(corps: str) -> str:
    return "function (L, o) {" + LOIN + corps + "}"


def test_le_premier_matin_porte_ses_chantiers(banc):
    r = banc(_juge("""
        L.Jeu.commencer();
        const carte = L.Monde.carte;
        return L.Chantiers.liste.map(function (ch) {
            const d = ch.def;
            const rangees = [];
            let incoherent = 0;
            for (let j = 0; j < d.h; j++) {
                rangees.push(carte.sol[d.y + j].slice(d.x, d.x + d.l));
                for (let i = 0; i < d.l; i++) {
                    const g = carte.sol[d.y + j][d.x + i];
                    if (carte.solide[(d.y + j) * carte.w + d.x + i] !== ((carte.legende[g] || {}).solide || 0)) incoherent++;
                }
            }
            return { id: d.id, posee: ch.posee, decalage: d.decalage, rangees: rangees,
                     attendues: d.phases[ch.posee].sol, incoherent: incoherent,
                     machines: ch.machines.map(function (e) { return e.decor; }) };
        });
    """))
    assert len(r) >= 2
    for ch in r:
        assert ch["posee"] == ch["decalage"], ch
        assert ch["rangees"] == ch["attendues"], f"chantier {ch['id']} : le sol n'est pas celui du jour"
        assert ch["incoherent"] == 0, "la solidité ne suit pas le sol posé"
        assert tuple(m.removesuffix("_ouest") for m in ch["machines"]) == chantiers.MACHINES.get(ch["posee"], ()), ch


def test_le_jeu_et_le_generateur_lisent_la_meme_horloge(banc, paquet):
    """⚠️ Deux formules pour une horloge : un juge les compare jour par jour, sinon
    le jour où l'une change, deux appareils voient deux villes."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sortie = [];
        for (const debut of [1, 5]) {
            L.B.partie.chantiers = { debut: debut };
            for (let jour = 1; jour <= 30; jour++) {
                L.B.partie.jour = jour;
                sortie.push(L.Chantiers.liste.map(function (ch) { return L.Chantiers.phaseVoulue(ch.def); }));
            }
        }
        return sortie;
    }""")
    attendu = []
    for debut in (1, 5):
        for jour in range(1, 31):
            attendu.append([chantiers.phase_du_jour(ch, jour, debut) for ch in paquet["carte"]["chantiers"]])
    assert r == attendu


def test_une_phase_ne_se_pose_jamais_sous_les_yeux(banc):
    """⚠️ Le piège 4 du plan : recuire en plein jeu se voit. Devant le chantier, la
    phase du lendemain ATTEND ; dès qu'on tourne le coin, elle se pose."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee < 4; });
        const d = ch.def;
        const avant = ch.posee;
        poserLeJoueur(L, { x: (d.x + d.l / 2) * 16, y: (d.y + d.h + 2) * 16 });
        L.B.partie.jour += d.pas;
        o.frame(100);
        const devant = ch.posee;
        poserLeJoueur(L, loin(L));
        o.frame(100);
        return { avant: avant, devant: devant, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d) };
    """))
    assert r["voulue"] == r["avant"] + 1
    assert r["devant"] == r["avant"], "la phase s'est posée sous les yeux du joueur"
    assert r["apres"] == r["voulue"], "hors de vue, la phase du jour doit se poser"


def test_le_neuf_attend_que_personne_ne_soit_dans_l_empreinte(banc):
    """Un char garé sur le terrain rasé, et le lendemain le neuf remonte ses murs :
    il faut attendre qu'il soit parti, sinon il est muré dedans."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        // Une tuile de sol dans l'empreinte, loin des machines.
        let place = null;
        for (let j = 0; j < d.h && !place; j++) {
            for (let i = 0; i < d.l && !place; i++) {
                const x = d.x + i, y = d.y + j;
                if (d.masque[j][i] !== 'X' || L.Monde.solidite(x, y) !== 0) continue;
                if (ch.machines.some(function (e) { return Math.abs(e.x - (x * 16 + 8)) < 20 && Math.abs(e.y - (y * 16 + 8)) < 20; })) continue;
                place = { x: x * 16 + 8, y: y * 16 + 8 };
            }
        }
        const v = L.Vehicules.creer('auto', place.x, place.y, 0, { etat: 'stationne' });
        poserLeJoueur(L, loin(L));
        L.B.partie.jour += 30;                       // le neuf, pour sûr
        tourner(L, 3);
        const garee = ch.posee;
        L.Entites.retirer(v);
        tourner(L, 3);
        return { garee: garee, partie: ch.posee, derniere: d.phases.length - 1 };
    """))
    assert r["garee"] < r["derniere"], "le neuf a muré un char garé sur le chantier"
    assert r["partie"] == r["derniere"]


def test_le_neuf_remonte_ses_murs_et_la_demolition_les_ouvre(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0], d = ch.def;
        const solides = function () {
            let n = 0;
            for (let j = 0; j < d.h; j++) for (let i = 0; i < d.l; i++) {
                if (d.masque[j][i] === 'X' && L.Monde.solidite(d.x + i, d.y + j) === 1) n++;
            }
            return n;
        };
        let taille = 0;
        d.masque.forEach(function (r) { for (const c of r) if (c === 'X') taille++; });
        const vus = {};
        for (const phase of [0, 2, 3, 4]) { L.Chantiers.appliquer(0, phase); vus[phase] = solides(); }
        return { taille: taille, vus: vus };
    }""")
    assert r["vus"]["0"] == r["taille"]
    assert r["vus"]["2"] == 0 and r["vus"]["3"] == 0, "un terrain rasé garde des murs"
    assert r["vus"]["4"] == r["taille"], "le neuf n'a pas repris toute son empreinte"


def test_les_machines_travaillent_et_arretent_puis_s_en_vont(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0];
        const parPhase = {};
        for (let phase = 0; phase < ch.def.phases.length; phase++) {
            L.Chantiers.appliquer(0, phase);
            const machines = L.B.entites.filter(function (e) { return e.machineDe === ch.def.id; });
            parPhase[phase] = machines.map(function (e) {
                return { decor: e.decor, solide: e.solide,
                         indexee: L.Entites.decorAutour(e.x, e.y, 4).indexOf(e) >= 0 };
            });
        }
        return parPhase;
    }""")
    for phase, machines in r.items():
        attendues = chantiers.MACHINES.get(int(phase), ())
        # La grue à boule tournée vers l'ouest est la même machine, en miroir.
        assert tuple(m["decor"].removesuffix("_ouest") for m in machines) == attendues, (phase, machines)
        for m in machines:
            assert m["solide"], f"{m['decor']} ne bloque personne"
            assert m["indexee"], f"{m['decor']} n'est pas dans l'index du décor : le char la traverse"


def test_une_maison_rasee_n_avale_plus_personne(banc):
    """Les gens rentrent chez eux par les portes condamnées. Sur un terrain rasé,
    il n'y a plus de chez-eux — et personne n'y marche plus pour rentrer.

    ⚠️ On ne juge PAS la liste des portes : elle ne bouge pas, exprès (son ordre
    compte pour tout ce qui y tire au sort). On juge ce que les gens en FONT."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Un chantier qui A une porte : sur une maison sans porte, le juge
        // verifierait l'absence de rien et passerait sans la regle.
        const i = L.Chantiers.liste.findIndex(function (c) {
            return c.def.phases[0].sol.some(function (r, j) {
                for (let k = 0; k < r.length; k++) if ((r[k] === 'd' || r[k] === 'D') && c.def.masque[j][k] === 'X') return true;
                return false;
            });
        });
        if (i < 0) throw new Error('aucun chantier ne porte de porte : le juge ne prouverait rien');
        const ch = L.Chantiers.liste[i], d = ch.def;
        const porte = L.Monde.carte.portesFermees.find(function (q) {
            return q.x >= d.x && q.x < d.x + d.l && q.y >= d.y && q.y < d.y + d.h && d.masque[q.y - d.y][q.x - d.x] === 'X';
        });
        const vus = {};
        for (const phase of [0, 2]) {
            L.Chantiers.appliquer(i, phase);
            const passant = L.Entites.creerPieton(porte.x * 16 + 8, (porte.y + 2) * 16 + 8, L.Entites.archetype('passant'));
            passant.etat = 'flane';
            const envoye = L.Entites.envoyerAUnePorte(passant);
            vus[phase] = { sert: L.Entites.porteQuiSert(porte),
                           versElle: envoye && passant.porteBut === porte };
            L.Entites.retirer(passant);
        }
        return vus;
    }""")
    assert r["0"]["sert"] and r["0"]["versElle"], "la maison debout n'avale plus son voisin qui rentre"
    assert not r["2"]["sert"], "une maison rasée sert encore de porte"
    assert not r["2"]["versElle"], "un passant marche rentrer chez lui dans un terrain rasé"


def test_ce_qui_appartenait_a_la_maison_tombe_avec_elle(banc):
    """Une façade de logement, un équipement de toit, un tag, une fenêtre allumée :
    tout ça était à la MAISON. Sur un terrain rasé, ça flotterait au-dessus de rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte, def = carte.def;
        const ch = L.Chantiers.liste[0], d = ch.def;
        const siennes = function (x, y) {
            return x >= d.x && x < d.x + d.l && y >= d.y && y < d.y + d.h && d.masque[y - d.y][x - d.x] === 'X';
        };
        // ⚠️ Aucune maison en chantier de cette ville n'a de fenetre allumee : on en
        // allume une, sinon le juge verifierait qu'aucune lampe absente ne brille.
        let place = null;
        d.masque.forEach(function (r, j) { for (let k = 0; k < r.length && !place; k++) if (r[k] === 'X') place = [d.x + k, d.y + j]; });
        carte.lampes.push({ x: place[0] * 16 + 8, y: place[1] * 16 + 8, r: 20, c: 'rgba(255,212,150,0.22)' });
        const lampesSiennes = carte.lampes.filter(function (l) { return siennes(Math.floor(l.x / 16), Math.floor(l.y / 16)); });
        const etat = function () {
            let effacees = 0, total = 0;
            d.masque.forEach(function (r, j) {
                for (let i = 0; i < r.length; i++) if (r[i] === 'X') { total++; if (L.Chantiers.efface(d.x + i, d.y + j)) effacees++; }
            });
            return { effacees: effacees, total: total,
                     lampesAllumees: lampesSiennes.filter(function (l) { return !l.demolie; }).length,
                     toitsVisibles: (def.toits || []).filter(function (t) { return siennes(t.x, t.y) && !L.Chantiers.efface(t.x, t.y); }).length };
        };
        L.Chantiers.appliquer(0, 0); const debout = etat();
        L.Chantiers.appliquer(0, 2); const rase = etat();
        // Et ailleurs dans la ville, rien n'est effacé.
        const ailleurs = L.Chantiers.efface(d.x - 3, d.y - 3);
        return { debout: debout, rase: rase, lampes: lampesSiennes.length, ailleurs: ailleurs };
    }""")
    assert r["lampes"] >= 1
    assert r["debout"]["lampesAllumees"] == r["lampes"], "la maison debout s'est éteinte"
    assert r["debout"]["effacees"] == 0, "la maison debout a perdu sa façade"
    assert r["rase"]["effacees"] == r["rase"]["total"]
    assert r["rase"]["lampesAllumees"] == 0, "une fenêtre s'allume au-dessus d'un terrain rasé"
    assert r["rase"]["toitsVisibles"] == 0
    assert r["ailleurs"] is False


def test_le_cache_ne_se_vide_qu_autour_du_chantier(banc):
    """Poser une phase recuit les morceaux du chantier et de ses bords — pas la ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte, ch = L.Chantiers.liste[0], d = ch.def;
        carte.morceaux.clear();
        const mw = Math.ceil(carte.w / 16), mh = Math.ceil(carte.h / 16);
        for (let my = 0; my < mh; my++) for (let mx = 0; mx < mw; mx++) carte.morceaux.set(mx + ',' + my, {});
        const avant = carte.morceaux.size;
        L.Chantiers.appliquer(0, (ch.posee + 1) % d.phases.length);
        const touches = [];
        for (let my = 0; my < mh; my++) for (let mx = 0; mx < mw; mx++) {
            if (!carte.morceaux.has(mx + ',' + my)) touches.push([mx, my]);
        }
        return { avant: avant, touches: touches, d: { x: d.x, y: d.y, l: d.l, h: d.h } };
    }""")
    assert r["touches"], "rien n'a été recuit : le chantier ne se verrait pas"
    d = r["d"]
    for mx, my in r["touches"]:
        assert (d["x"] - 1) // 16 <= mx <= (d["x"] + d["l"]) // 16, (mx, my)
        assert (d["y"] - 1) // 16 <= my <= (d["y"] + d["h"] + 1) // 16, (mx, my)
    assert len(r["touches"]) <= 9


def test_une_vieille_partie_repart_de_son_jour(banc):
    """⚠️ Le piège 5 : la phase voyage dans la sauvegarde. Une partie d'avant les
    chantiers, rouverte au trentième jour, ne découvre pas trois bâtiments neufs
    qu'elle n'a jamais vus tomber : elle repart de son premier matin."""
    r = banc("""function (L, o) {
        const neuve = L.Sauvegarde.completer(null, L.B.defs);
        const vieille = L.Sauvegarde.completer({ jour: 30, argent: 10 }, L.B.defs);
        const gardee = L.Sauvegarde.completer({ jour: 30, chantiers: { debut: 12 } }, L.B.defs);
        L.B.partie = vieille;
        L.Jeu.commencer();
        return { neuve: neuve.chantiers, vieille: vieille.chantiers, gardee: gardee.chantiers,
                 phases: L.Chantiers.liste.map(function (ch) { return [ch.posee, ch.def.decalage]; }) };
    }""")
    assert r["neuve"] == {"debut": 1}
    assert r["vieille"] == {"debut": 30}
    assert r["gardee"] == {"debut": 12}, "une sauvegarde qui connaît ses chantiers les garde"
    for posee, decalage in r["phases"]:
        assert posee == decalage


def test_une_sauvegarde_dans_un_mur_neuf_ressort_devant_la_porte(banc):
    r = banc("""function (L, o) {
        const ch0 = L.B.defs.carte.chantiers[0];
        let place = null;
        ch0.masque.forEach(function (r, j) { for (let i = 0; i < r.length && !place; i++) if (r[i] === 'X') place = [ch0.x + i, ch0.y + j]; });
        L.B.partie.x = place[0] * 16 + 8; L.B.partie.y = place[1] * 16 + 8;
        L.B.partie.jour = 60;                        // le neuf est debout
        L.Jeu.commencer();
        const j = L.B.joueur;
        const tx = Math.floor(j.x / 16), ty = Math.floor(j.y / 16);
        return { solidite: L.Monde.solidite(tx, ty), posee: L.Chantiers.liste[0].posee };
    }""")
    assert r["posee"] == chantiers.DERNIERE
    assert r["solidite"] == 0, "le joueur reparaît dans un mur neuf"


def test_rien_ne_bouge_quand_on_est_dans_une_piece(banc):
    """Dans un intérieur, la carte active est la pièce : poser une phase y
    écrirait des murs dans le dépanneur."""
    r = banc(_juge("""
        L.Jeu.commencer();
        poserLeJoueur(L, loin(L));
        const ch = L.Chantiers.liste.find(function (c) { return c.posee < 4; });
        L.B.partie.jour += ch.def.pas * 2;
        L.B.interieur = { slug: 'essai' };
        tourner(L, 3);
        const dedans = ch.posee;
        L.B.interieur = null;
        tourner(L, 3);
        return { dedans: dedans, dehors: ch.posee, voulue: L.Chantiers.phaseVoulue(ch.def) };
    """))
    assert r["dedans"] < r["voulue"], "une phase s'est posée pendant qu'on était dans une pièce"
    assert r["dehors"] == r["voulue"]


def test_un_objet_par_terre_ne_finit_pas_mure(banc):
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        let place = null;
        for (let j = 0; j < d.h && !place; j++) for (let i = 0; i < d.l && !place; i++) {
            if (d.masque[j][i] === 'X' && L.Monde.solidite(d.x + i, d.y + j) === 0) place = { x: (d.x + i) * 16 + 8, y: (d.y + j) * 16 + 8 };
        }
        const arme = L.Entites.creer('ramassage', place.x, place.y, { r: 4, objet: 'arme', arme: 'pistolet', munitions: 6, t: 0, solide: false });
        poserLeJoueur(L, loin(L));
        L.B.partie.jour += 60;
        tourner(L, 3);
        return { posee: ch.posee, solidite: L.Monde.solidite(Math.floor(arme.x / 16), Math.floor(arme.y / 16)),
                 encore: L.B.entites.indexOf(arme) >= 0 };
    """))
    assert r["posee"] == chantiers.DERNIERE
    assert r["encore"]
    assert r["solidite"] == 0, "l'arme lâchée sur le chantier est murée dans le neuf"


def test_la_boule_se_balance_et_la_grue_tourne(banc):
    """Une articulation par machine, et elle BOUGE : chaque pose peint autre chose."""
    r = banc("""function (L, o) {
        const empreinte = function (nom, pose) {
            const f = L.DECORS[nom], traces = [];
            const faux = { fillRect: function (x, y, w, h) { traces.push([Math.round(x), Math.round(y), w, h]); } };
            Object.defineProperty(faux, 'fillStyle', { set: function () {}, get: function () { return ''; } });
            f.peindre(faux, f.w, f.h, pose);
            return JSON.stringify(traces);
        };
        const sortie = {};
        for (const nom of ['grue_a_boule', 'grue', 'pelleteuse']) {
            const f = L.DECORS[nom];
            const poses = new Set();
            for (let p = 0; p < f.variantes; p++) poses.add(empreinte(nom, p));
            sortie[nom] = { variantes: f.variantes, distinctes: poses.size, anime: f.anime, arrete: f.arrete, solide: f.solide };
        }
        return sortie;
    }""")
    for nom, f in r.items():
        assert f["anime"] and f["variantes"] >= 4, nom
        assert f["distinctes"] >= f["variantes"] // 2, f"{nom} ne bouge pas : {f}"
        assert f["solide"] and f["arrete"], f"{nom} : un char la traverse"


# --- 2e vague : le chantier travaille ----------------------------------------------------


def test_la_boule_touche_le_mur_au_pixel_pres(banc):
    """⚠️ La boule frappe POUR VRAI : à la pose du coup, son dernier pixel touche le
    premier pixel du mur — et à aucune autre pose elle n'y entre. Des deux côtés :
    la grue tournée vers l'ouest est un miroir, ancre comprise."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const traces = [];
        const faux = { fillRect: function (x, y, w, h) { traces.push([x, y, w, h]); } };
        Object.defineProperty(faux, 'fillStyle', { set: function () {}, get: function () { return ''; } });
        return L.Chantiers.liste.map(function (ch, i) {
            L.Chantiers.appliquer(i, 1);
            const e = ch.machines.find(function (m) { return m.frappe; });
            const f = L.DECORS[e.decor];
            const bords = [];
            for (let p = 0; p < f.variantes; p++) {
                traces.length = 0;
                f.peindre(faux, f.w, f.h, p);
                // Les deux rectangles de la boule : les derniers peints avant son reflet.
                const boule = traces.slice(-3, -1);
                const g = Math.min.apply(null, boule.map(function (q) { return q[0]; }));
                const dr = Math.max.apply(null, boule.map(function (q) { return q[0] + q[2] - 1; }));
                bords.push([e.x - f.ancre[0] + g, e.x - f.ancre[0] + dr]);
            }
            const mx = e.frappe[0], my = e.frappe[1];
            return { id: ch.def.id, decor: e.decor, sens: e.sens, ex: e.x, frappe: f.frappe, bords: bords,
                     mur: [mx * 16, (mx + 1) * 16 - 1],
                     solide: [L.Monde.solidite(mx, my), L.Monde.solidite(mx, my - 1)],
                     contact: L.Chantiers.CONTACT_X };
        });
    """))
    assert {c["sens"] for c in r} == {1, -1}, "il faut juger les deux côtés : " + str(r)
    for c in r:
        assert c["solide"] == [1, 1], f"chantier {c['id']} : la boule frappe un mur qui n'est pas là"
        gauche, droite = c["mur"]
        for pose, (g, d) in enumerate(c["bords"]):
            if c["sens"] > 0:
                assert d < gauche, (c["id"], pose, "la boule entre dans le mur")
                if pose == c["frappe"]:
                    assert d == gauche - 1, (c["id"], "au coup, la boule ne touche pas le mur")
                    assert c["ex"] + c["contact"] == gauche, "la poussière ne part pas du mur"
            else:
                assert g > droite, (c["id"], pose, "la boule entre dans le mur")
                if pose == c["frappe"]:
                    assert g == droite + 1, (c["id"], "au coup, la boule ne touche pas le mur")
                    assert c["ex"] - c["contact"] == droite + 1, "la poussière ne part pas du mur"


def test_le_coup_part_a_la_pose_qu_on_voit_et_le_chantier_se_tait_la_nuit(banc):
    """Le son, la poussière et la secousse partent à la PREMIÈRE image de la pose
    du coup. La nuit : plus un son, et les machines à leur pose de repos."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.Chantiers.appliquer(0, 1);
        const ch = L.Chantiers.liste[0];
        const e = ch.machines.find(function (m) { return m.frappe; });
        const f = L.DECORS[e.decor];
        poserLeJoueur(L, { x: e.x, y: e.y + 48 });
        const rumeurs = [];
        L.Son.SFX.rumeur_chantier = function (v) { rumeurs.push(v); };
        const tourne = function (n) {
            let secousse = 0;
            for (let k = 0; k < n; k++) {
                L.B.cam.secousse = 0;
                L.Chantiers.maj();
                secousse = Math.max(secousse, L.B.cam.secousse);
                L.B.t++;
            }
            return secousse;
        };
        L.B.partie.heure = 0.5;
        const t0 = L.B.t, particules = L.B.particules.length;
        const secousse = tourne(1300);
        const jour = L.Chantiers.journal.filter(function (x) { return x.t >= t0; });
        const coups = jour.filter(function (x) { return x.son === 'boule'; }).map(function (x) {
            return [L.Entites.poseDuDecor(f, x.t, false), L.Entites.poseDuDecor(f, x.t + 1, false)];
        });
        const rumeurJour = rumeurs.slice();
        L.B.partie.heure = 0.95;
        rumeurs.length = 0;
        const t1 = L.B.t;
        tourne(1300);
        const poses = new Set();
        for (let t = 0; t < f.anime * f.variantes; t++) poses.add(L.Entites.poseDuDecor(f, t));
        return { coups: coups, sons: jour.map(function (x) { return x.son; }), frappe: f.frappe,
                 particules: L.B.particules.length - particules, secousse: secousse,
                 rumeurJour: Math.min.apply(null, rumeurJour), nuit: L.Monde.estNuit(),
                 sonsDeNuit: L.Chantiers.journal.filter(function (x) { return x.t >= t1; }).length,
                 rumeurNuit: Math.max.apply(null, rumeurs), posesDeNuit: Array.from(poses) };
    """))
    assert len(r["coups"]) >= 7, r["sons"]
    for avant, pendant in r["coups"]:
        assert pendant == r["frappe"], "le coup part sur une autre pose que celle du coup"
        assert avant == r["frappe"] - 1, "le coup part en retard sur la pose qu'on voit"
    assert "marteau_piqueur" in r["sons"], "ce qu'on ne voit pas ne s'entend jamais"
    assert r["particules"] > 0, "pas de poussière au coup"
    assert r["secousse"] > 0, "à deux pas du coup, la rue ne tremble pas"
    assert r["rumeurJour"] > 0.5, "à deux pas du chantier, pas de rumeur"
    assert r["nuit"]
    assert r["sonsDeNuit"] == 0, "le chantier travaille la nuit"
    assert r["rumeurNuit"] == 0
    assert r["posesDeNuit"] == [0], "la nuit, les machines bougent encore"


def test_on_entend_le_chantier_avant_de_le_voir(banc):
    """La rumeur suit la distance : forte devant, plus faible au bout de la rue,
    rien au loin — et rien dans une pièce."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        const vus = [];
        L.Son.SFX.rumeur_chantier = function (v) { vus.push(v); };
        const mesure = function (p) { poserLeJoueur(L, p); vus.length = 0; L.Chantiers.travailler(); return vus[vus.length - 1]; };
        const cx = (d.x + d.l / 2) * 16, bas = (d.y + d.h) * 16;
        const pres = mesure({ x: cx, y: bas + 40 });
        const moyen = mesure({ x: cx, y: bas + 250 });
        const auLoin = mesure(loin(L));
        poserLeJoueur(L, { x: cx, y: bas + 40 });
        L.B.interieur = { banc: true };
        vus.length = 0; L.Chantiers.travailler();
        const piece = vus[vus.length - 1];
        L.B.interieur = null;
        return { pres: pres, moyen: moyen, loin: auLoin, piece: piece };
    """))
    assert r["pres"] > 0.8, r
    assert 0 < r["moyen"] < r["pres"], r
    assert r["loin"] == 0, r
    assert r["piece"] == 0, "on entend le chantier depuis une pièce"


def test_la_grue_se_dessine_tant_que_sa_fleche_est_a_l_ecran(banc):
    """⚠️ Un décor sortait de la liste de dessin à 48 px de l'écran, mesurés à son
    PIED : la grue — 112 px de large, 90 au-dessus de sa tuile — surgissait d'un
    coup en montant la rue. Et la nuit, elle se peint à sa pose de repos."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const f = L.DECORS.grue, cam = L.B.cam;
        const g = L.Entites.creer('decor', cam.x + 200, cam.y + 100, { decor: 'grue', r: 7, dessine: true, v: 0 });
        const compte = function (x, y) {
            g.x = x; g.y = y;
            L.Entites.dessiner(o.ctx, cam);
            return L.B.stats.entites;
        };
        const sousLEcran = compte(cam.x + 200, cam.y + L.VH + f.h + 20);
        const flecheEnBas = compte(cam.x + 200, cam.y + L.VH + f.ancre[1] - 10);
        const aGauche = compte(cam.x - f.w - 20, cam.y + 100);
        const flecheAGauche = compte(cam.x - 50, cam.y + 100);
        const cles = [];
        const cuire = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle) { if (cle.indexOf('decor|grue|') === 0) cles.push(cle); return cuire.apply(null, arguments); };
        L.B.t = 7 * f.anime;
        compte(cam.x + 200, cam.y + 100);
        const jour = cles.slice();
        cles.length = 0;
        L.B.partie.heure = 0.95;
        compte(cam.x + 200, cam.y + 100);
        L.Atlas.cuirePeintre = cuire;
        return { sousLEcran: sousLEcran, flecheEnBas: flecheEnBas, aGauche: aGauche,
                 flecheAGauche: flecheAGauche, jour: jour, nuit: cles };
    """))
    assert r["flecheEnBas"] == r["sousLEcran"] + 1, "le pied sous l'écran, la flèche visible : la grue ne se peint pas"
    assert r["flecheAGauche"] == r["aGauche"] + 1, "le pied à gauche de l'écran, la flèche visible : la grue ne se peint pas"
    assert r["jour"] == ["decor|grue|7"], r
    assert r["nuit"] == ["decor|grue|0"], "la nuit, la grue tourne encore"


def test_une_fleche_qui_depasse_retient_la_phase(banc):
    """⚠️ Le chantier hors de vue, mais la flèche de sa grue encore à l'écran :
    la phase attend — une grue qui s'évapore se voit autant qu'un mur."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0], d = ch.def;
        const g = d.phases[3].machines[0];
        g.x = d.x + d.l - 1;                     // au bord est : la flèche dépasse de l'empreinte
        L.Chantiers.appliquer(0, 3);
        poserLeJoueur(L, loin(L));
        for (const e of L.B.entites.slice()) {
            if (e === L.B.joueur || !(e.type === 'pieton' || e.type === 'agent' || e.type === 'vehicule')) continue;
            if (e.x > (d.x - 2) * 16 && e.x < (d.x + d.l + 2) * 16 && e.y > (d.y - 2) * 16 && e.y < (d.y + d.h + 2) * 16) L.Entites.retirer(e);
        }
        const f = L.DECORS.grue;
        L.B.cam.x = g.x * 16 + 8 - f.ancre[0] + f.w - 4;
        L.B.cam.y = (d.y + d.h / 2) * 16 - L.VH / 2;
        L.B.partie.jour += 60;
        tourner(L, 3);
        const retenue = ch.posee;
        L.B.cam.x += 16;
        tourner(L, 3);
        return { retenue: retenue, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d),
                 horsEmpreinte: L.B.cam.x - 16 > (d.x + d.l) * 16 + 40 };
    """))
    assert r["horsEmpreinte"], "le juge doit placer l'écran hors de la marge de l'empreinte"
    assert r["voulue"] == 4
    assert r["retenue"] == 3, "la phase s'est posée sous la flèche de la grue"
    assert r["apres"] == 4


def test_les_sons_du_chantier_sortent_avec_ou_sans_leur_fichier(banc):
    """Le filet, comme partout : avant que les fichiers arrivent, chaque son de
    chantier se synthétise — et tout ce qui démarre atteint la sortie. Trop loin,
    rien ne part. Fichiers chargés, la boule joue son échantillon ; le bip de
    recul, lui, reste synthétisé (trois bips à 1050 Hz) : il n'a pas de fichier."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        const j = L.B.joueur, SFX = L.Son.SFX;
        const sons = ['boule', 'marteau_piqueur', 'godet', 'bip_recul', 'marteau', 'scie'];
        const filet = {};
        for (const son of sons) {
            const n = joues.length;
            const v = SFX.chantier(son, j.x + 60, j.y, 340);
            filet[son] = { volume: v, joues: joues.length - n };
        }
        const n = joues.length;
        const loinV = SFX.chantier('boule', j.x + 500, j.y, 460);
        const loin = joues.length - n;
        await o.attendre(); await o.attendre(); await o.attendre();
        const ctx = L.Son.contexte;
        const m = joues.length;
        SFX.chantier('boule', j.x + 60, j.y, 460);
        const bouleFichier = joues.slice(m).map(function (x) { return x.quoi; });
        const k = joues.length;
        SFX.chantier('bip_recul', j.x + 60, j.y, 340);
        const bips = joues.slice(k).filter(function (x) { return x.quoi === 'ton' && x.hz === 1050; }).length;
        SFX.rumeur_chantier(0.5);
        const rumeur = L.Son.volumeBoucle('chantier');
        SFX.rumeur_chantier(0);
        return { filet: filet, loin: loin, loinV: loinV, bouleFichier: bouleFichier, bips: bips,
                 charge: L.Son.estCharge('boule'), rumeur: rumeur, eteinte: L.Son.boucleActive('chantier'),
                 muettes: ctx.sourcesMuettes() };
    }""")
    for son, f in r["filet"].items():
        assert f["volume"] > 0 and f["joues"] > 0, f"{son} : sans fichier, le chantier est muet"
    assert r["loin"] == 0 and r["loinV"] == 0, "un coup de boule s'entend à l'autre bout de la ville"
    assert r["charge"], "le fichier de la boule ne se charge pas"
    assert r["bouleFichier"] == ["echantillon"], "fichier chargé, la boule joue encore sa synthèse"
    assert r["bips"] == 3
    assert r["rumeur"] and r["rumeur"] > 0, "la rumeur du chantier ne tourne pas"
    assert r["eteinte"] is False, "la rumeur ne s'éteint pas"
    assert r["muettes"] == 0, "un son de chantier démarre sans atteindre la sortie"
