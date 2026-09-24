"""Ça travaille : les chantiers en jeu.

⚠️ Python a jugé la géométrie de chaque phase (`test_chantiers.py`). Ici on juge
ce que le JEU en fait : poser la bonne phase le bon jour, jamais sous les yeux,
jamais sur quelqu'un, et défaire proprement ce qui appartenait à la maison.

⚠️ `Chantiers.maj` ne regarde qu'une image sur `CADENCE` (30) : un juge qui veut
voir une phase se poser laisse tourner au moins deux cadences.
"""

from app import chantiers, vehicules

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
        const sons = ['boule', 'marteau_piqueur', 'godet', 'bip_recul', 'marteau', 'scie', 'plaque', 'tas', 'conteneur'];
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


# --- 3e vague : la tranchée et l'équipe -------------------------------------------------

#: Une toile qui note ce qu'on y peint : chaque `fillRect` avec sa couleur du moment.
ENREGISTREUR = """
  function enregistreur() {
    const log = []; let style = '';
    return new Proxy({}, {
      get: function (t, k) {
        if (k === 'log') return log;
        if (k === 'fillStyle') return style;
        return function () { if (k === 'fillRect') log.push([style].concat(Array.from(arguments))); };
      },
      set: function (t, k, v) { if (k === 'fillStyle') style = v; return true; },
    });
  }
  // Le chantier dont la phase est `phase`, ou celui qui a une tranchée à cette phase.
  function avecTranchee(L) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.tranchee && c.def.tranchee.length; });
    if (i < 0) throw new Error('aucun chantier n\\'a de tranchée');
    return i;
  }
"""


def test_une_plaque_claque_sous_les_roues_et_ne_coute_rien(banc):
    """⚠️ Un nid-de-poule est un accident, une plaque d'acier est un décor qu'on
    sent : elle claque et elle secoue, elle ne coûte rien. Même répit que les
    nids (sans lui, un char lent la claque à chaque image), et rien à l'arrêt."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), ch = L.Chantiers.liste[i], t = ch.def.tranchee, TT = L.TT;
        const claque = [];
        const vrai = L.Son.SFX.chantier;
        L.Son.SFX.chantier = function (son, x, y, portee) { claque.push([son, Math.round(x), Math.round(y), portee]); return 1; };
        const j = L.B.joueur;
        j.x = t[0][0] * TT + 8; j.y = t[0][1] * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = t[0][0] * TT + 8; v.y = t[0][1] * TT + 8; L.Entites.indexer();
        const out = {};
        for (const phase of [0, 1, 2, 3, 4]) {
            L.Chantiers.appliquer(i, phase);
            out['phase' + phase] = t.map(function (c) { return L.Monde.plaqueDAcier(c[0], c[1]); });
        }
        out.ailleurs = L.Monde.plaqueDAcier(t[0][0] + 5, t[0][1] + 5);
        L.Chantiers.appliquer(i, 2);
        // 1. A L'ARRET
        v.vitesse = 0; v.vx = 0; v.vy = 0; v.plaqueT = 0;
        const vie0 = v.vie;
        L.B.cam.secousse = 0; claque.length = 0;
        for (let k = 0; k < 10; k++) L.Vehicules.majPlaque(v);
        out.arret = { claque: claque.length, secousse: L.B.cam.secousse };
        // 2. EN ROULANT : une fois, le temps du répit
        v.vitesse = 2; v.vx = 2; v.vy = 0; v.plaqueT = 0;
        for (let k = 0; k < 10; k++) L.Vehicules.majPlaque(v);
        out.roule = { claque: claque.slice(), perdu: vie0 - v.vie, secousse: L.B.cam.secousse, repit: v.plaqueT };
        // 3. Le répit passé, elle claque de nouveau.
        v.plaqueT = 0; claque.length = 0;
        L.Vehicules.majPlaque(v);
        out.encore = claque.length;
        // 4. En l'air, rien.
        v.plaqueT = 0; v.z = 12; claque.length = 0;
        L.Vehicules.majPlaque(v);
        out.enLAir = claque.length;
        v.z = 0;
        // 5. Le trafic claque aussi, mais la caméra ne tremble que pour le joueur.
        const autre = o.char('auto', 0, 0, 0);
        autre.x = t[1][0] * TT + 8; autre.y = t[1][1] * TT + 8; autre.vitesse = 2; autre.vx = 2; autre.vy = 0; autre.plaqueT = 0;
        L.B.cam.secousse = 0; claque.length = 0;
        L.Vehicules.majPlaque(autre);
        out.trafic = { claque: claque.length, secousse: L.B.cam.secousse };
        L.Son.SFX.chantier = vrai;
        return out;
    """))
    ph = vehicules.PHYSIQUE
    assert r["phase0"] == [False, False] and r["phase1"] == [False, False], "des plaques avant que le terrain soit rasé"
    assert r["phase2"] == [True, True] and r["phase3"] == [True, True], "la tranchée n'a pas ses plaques"
    assert r["phase4"] == [False, False], "le neuf debout, les plaques claquent encore"
    assert r["ailleurs"] is False
    assert r["arret"] == {"claque": 0, "secousse": 0}, f"un char à l'arrêt claque : {r['arret']}"
    assert [c[0] for c in r["roule"]["claque"]] == ["plaque"], f"une plaque, un claquement, puis le répit : {r['roule']}"
    assert r["roule"]["perdu"] == 0, "une plaque d'acier ne coûte rien"
    assert abs(r["roule"]["secousse"] - ph["plaque_secousse"]) < 1e-9, r["roule"]
    assert r["roule"]["repit"] > 0, "aucun répit : la plaque claque à chaque image"
    assert r["encore"] == 1, "le répit passé, elle ne claque plus"
    assert r["enLAir"] == 0, "un char qui saute claque sur la plaque"
    assert r["trafic"]["claque"] == 1 and r["trafic"]["secousse"] == 0, f"le trafic, lui : {r['trafic']}"


def test_les_plaques_survivent_a_une_porte(banc):
    """⚠️ Comme les nids : l'index vit SUR LA CARTE. Une pièce passe par `charger` ;
    ressorti, la tranchée doit encore claquer."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), t = L.Chantiers.liste[i].def.tranchee, c = L.Monde.carte;
        L.Chantiers.appliquer(i, 2);
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        const j = L.B.joueur;
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        L.Jeu.entrer(porte);
        o.fondu();
        const dedans = !!L.B.interieur;
        L.Jeu.sortir();
        o.fondu();
        return { dedans: dedans, dehors: L.B.interieur === null,
                 plaques: t.map(function (x) { return L.Monde.plaqueDAcier(x[0], x[1]); }) };
    """))
    assert r["dedans"] and r["dehors"], r
    assert r["plaques"] == [True, True], "ressorti d'une pièce, la tranchée ne claque plus"


def test_la_tranchee_se_peint_selon_la_phase_et_recuit_son_morceau(banc):
    """Des plaques d'acier jusqu'au neuf, l'asphalte refait ensuite, rien avant.
    Et le morceau de rue se recuit à chaque changement : sans cela, la couche
    peinte du cache garde l'ancienne rue."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), ch = L.Chantiers.liste[i], t = ch.def.tranchee, c = L.Monde.carte;
        const mx = Math.floor(t[0][0] / 16), my = Math.floor(t[0][1] / 16);
        const cle = mx + ',' + my;
        const px = (t[0][0] - mx * 16) * 16, py = (t[0][1] - my * 16) * 16;
        const dedans = function (r) { return r[1] >= px && r[1] < px + 32 && r[2] >= py && r[2] < py + 16; };
        const sortie = {};
        for (const phase of [0, 1, 2, 3, 4]) {
            // ⚠️ Le cache doit être REMPLI avant : un juge qui regarde un cache
            // vide ne verrait pas qu'on ne le vide plus.
            c.morceaux.set(cle, { cuit: true });
            L.Chantiers.appliquer(i, phase);
            const encore = c.morceaux.has(cle);
            const ctx = enregistreur();
            L.Chantiers.peindre(ctx, mx, my);
            const sur = ctx.log.filter(dedans).map(function (r) { return r[0]; });
            sortie[phase] = { acier: sur.indexOf('#7e858d') >= 0, refait: sur.indexOf('#25262c') >= 0,
                              ruban: sur.indexOf('#e8b33c') >= 0, encore: encore };
        }
        // ⚠️ Et une tranchée qui tombe dans un AUTRE morceau que la marge du bâtiment
        // (sur la graine livrée, elle est toujours dans le même) : la tranchée
        // recuit le sien, elle ne compte pas sur celui de la façade.
        const loinTuile = [t[0][0], t[0][1] + 32];
        ch.def.tranchee = [loinTuile, [loinTuile[0] + 1, loinTuile[1]]];
        const autre = Math.floor(loinTuile[0] / 16) + ',' + Math.floor(loinTuile[1] / 16);
        c.morceaux.set(autre, { cuit: true });
        L.Chantiers.appliquer(i, 2);
        sortie.autreMorceau = c.morceaux.has(autre);
        return sortie;
    """))
    for phase in "01":
        assert not r[phase]["acier"] and not r[phase]["refait"], f"la rue est peinte avant la tranchée : {r[phase]}"
    for phase in "23":
        assert r[phase]["acier"] and r[phase]["ruban"], f"phase {phase} : pas de plaques : {r[phase]}"
        assert not r[phase]["refait"]
    assert r["4"]["refait"] and not r["4"]["acier"], f"le neuf debout, la rue n'est pas refaite : {r['4']}"
    for phase in "01234":
        assert not r[phase]["encore"], "le morceau de la tranchée n'est pas recuit au changement de phase"
    assert r["autreMorceau"] is False, "la tranchée ne recuit pas son propre morceau"


def test_la_tranchee_ne_change_pas_sous_les_yeux(banc):
    """⚠️ Des plaques qui surgissent au milieu de la rue se voient autant qu'un mur :
    la caméra sur la TRANCHÉE (le bâtiment, lui, est plus haut que l'écran), la phase
    qui la change attend — et se pose dès qu'on a tourné le coin."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) {
            return c.posee === 1 && c.def.tranchee.length && c.def.phases[2].tranchee !== c.def.phases[1].tranchee;
        });
        if (i < 0) throw new Error('aucun chantier qui gagne sa tranchée à la prochaine phase');
        const ch = L.Chantiers.liste[i], d = ch.def, t = d.tranchee;
        // La tranchée tout en haut de l'écran : l'immeuble est au-dessus, hors de vue.
        poserLeJoueur(L, { x: t[0][0] * 16 + 8, y: t[0][1] * 16 + L.VH / 2 - 4 });
        const cam = L.B.cam;
        const immeubleVu = (d.y + d.h) * 16 + 40 > cam.y;
        const tranchee = t[0][1] * 16 + 16 > cam.y && t[0][1] * 16 < cam.y + L.VH;
        L.B.partie.jour += d.pas;
        o.frame(100);
        const devant = ch.posee;
        poserLeJoueur(L, loin(L));
        o.frame(100);
        return { immeubleVu: immeubleVu, tranchee: tranchee, devant: devant, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d) };
    """))
    assert not r["immeubleVu"] and r["tranchee"], f"le montage ne tient pas : {r}"
    assert r["devant"] == 1, "les plaques sont apparues sous les yeux du joueur"
    assert r["apres"] == r["voulue"] == 2, "hors de vue, la phase du jour doit se poser"


def _equipe(o_corps: str) -> str:
    return _juge(ENREGISTREUR + """
        // L'équipe du TERRAIN : le signaleur, lui, a ses propres juges.
        function equipe(L, id) {
            return L.B.entites.filter(function (e) { return e.equipeDe === id && e.vivant && e.posteDe !== 'signal'; });
        }
        // Le joueur au sud des postes, à portée de la bulle mais hors de l'écran.
        function auSud(L, ch, tuile) {
            poserLeJoueur(L, { x: tuile[0] * 16 + 8, y: tuile[1] * 16 + 8 + 300 });
        }
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].equipe.length === 2; });
        const ch = L.Chantiers.liste[i], d = ch.def, postes = d.phases[2].equipe, id = d.id;
        L.Chantiers.appliquer(i, 2);
    """ + o_corps)


def test_l_equipe_prend_son_poste_hors_de_l_ecran(banc):
    """Un ouvrier par poste, planté, intouchable, hors de la foule — et jamais sous
    les yeux du joueur, ni trop loin pour qu'on l'oublie aussitôt."""
    r = banc(_equipe("""
        // Loin : personne.
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        const loinN = equipe(L, id).length;
        // Sur les postes : ils seraient vus naître.
        poserLeJoueur(L, { x: postes[0][0] * 16 + 8, y: postes[0][1] * 16 + 8 });
        L.Chantiers.equiper();
        const surPlaceN = equipe(L, id).length;
        // Au sud, à portée de la bulle, hors de l'écran.
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const gens = equipe(L, id);
        const premiere = gens.length;
        L.Chantiers.equiper(); L.Chantiers.equiper();
        return { loinN: loinN, surPlaceN: surPlaceN, premiere: premiere, apres: equipe(L, id).length,
                 postes: postes, gens: gens.map(function (e) {
                     return { tx: Math.floor(e.x / 16), ty: Math.floor(e.y / 16), poste: e.posteDe, metier: e.metier,
                              intouchable: e.intouchable, etat: e.etat, chantier: !!e.chantier, arch: e.arch,
                              plante: !!e.plante, dansLaListe: L.B.entites.indexOf(e) >= 0 };
                 }),
                 voie: L.B.entites.filter(function (e) { return e.chantier; }).length };
    """))
    assert r["loinN"] == 0, "l'équipe naît à l'autre bout de la ville"
    assert r["surPlaceN"] == 0, "l'équipe naît sous les yeux du joueur"
    assert r["premiere"] == 2 and r["apres"] == 2, f"un poste, un homme — jamais deux : {r}"
    assert sorted((g["tx"], g["ty"]) for g in r["gens"]) == sorted(tuple(p) for p in r["postes"]), r["gens"]
    for g in r["gens"]:
        assert g["arch"] == "ouvrier" and g["metier"] == "chantier", g
        assert g["intouchable"] and g["etat"] == "fige" and g["plante"], g
        assert not g["chantier"], "marqué `chantier` : il passerait pour un ouvrier de la voie fermée"
    assert r["voie"] == 0


def test_l_equipe_rentre_la_nuit_et_avec_la_phase(banc):
    """Le jour elle travaille ; la nuit elle rentre — hors de l'écran seulement ;
    et une phase sans équipe (le neuf) la renvoie chez elle."""
    r = banc(_equipe("""
        auSud(L, ch, postes[0]);
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const jour = equipe(L, id).length;
        // La nuit, hors de l'écran : ils rentrent.
        L.B.partie.heure = 0.95;
        L.Chantiers.equiper();
        const nuit = equipe(L, id).length;
        // Et ils ne naissent pas la nuit.
        L.Chantiers.equiper();
        const nuitBis = equipe(L, id).length;
        // Le matin, ils reviennent ; le neuf, ils repartent.
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const matin = equipe(L, id).length;
        L.Chantiers.appliquer(i, 4);
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const neuf = equipe(L, id).length;
        // La nuit, mais sous les yeux : personne ne les voit disparaître.
        L.Chantiers.appliquer(i, 2);
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const avant = equipe(L, id);
        const e = avant[0];
        poserLeJoueur(L, { x: e.x, y: e.y + 30 });
        L.B.partie.heure = 0.95;
        L.Chantiers.equiper();
        return { jour: jour, nuit: nuit, nuitBis: nuitBis, matin: matin, neuf: neuf, sousLesYeux: equipe(L, id).length,
                 avant: avant.length };
    """))
    assert r["jour"] == 2, r
    assert r["nuit"] == 0 and r["nuitBis"] == 0, f"la nuit, l'équipe est encore au travail : {r}"
    assert r["matin"] == 2, f"au matin, l'équipe ne revient pas : {r}"
    assert r["neuf"] == 0, f"personne ne travaille sur un bâtiment neuf : {r}"
    assert r["sousLesYeux"] == r["avant"], f"l'équipe disparaît sous les yeux du joueur : {r}"


def test_l_equipe_regarde_passer(banc):
    """À moins de `REGARD` pixels, le visage tourné vers le joueur ; sinon vers la
    machine du jour."""
    r = banc(_equipe("""
        auSud(L, ch, postes[0]);
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const e = equipe(L, id)[0];
        const face = function (x, y) {
            poserLeJoueur(L, { x: x, y: y });
            e.face = 'bas';
            L.Chantiers.maj();
            return e.face;
        };
        const proche = { est: face(e.x + 40, e.y), ouest: face(e.x - 40, e.y), nord: face(e.x, e.y - 40), sud: face(e.x, e.y + 40) };
        const m = ch.machines[0];
        const eloigne = face(e.x + 60, e.y + L.Chantiers.REGARD + 200);
        const dx = m.x - e.x, dy = m.y - e.y;
        const versLaMachine = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
        return { proche: proche, eloigne: eloigne, versLaMachine: versLaMachine };
    """))
    assert r["proche"] == {"est": "droite", "ouest": "gauche", "nord": "haut", "sud": "bas"}, r["proche"]
    assert r["eloigne"] == r["versLaMachine"], f"loin du joueur, il ne regarde pas sa machine : {r}"


def test_l_equipe_suit_la_phase(banc):
    """⚠️ Un poste pris par l'homme d'hier reste « pris » : sans le renvoi de
    l'équipe au changement de phase, il resterait planté là où la grue se pose."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[3].equipe.length === 2; });
        const ch = L.Chantiers.liste[i], d = ch.def, id = d.id;
        const equipe = function () { return L.B.entites.filter(function (e) { return e.equipeDe === id && e.vivant && e.posteDe !== 'signal'; }); };
        L.B.partie.heure = 0.5;
        L.Chantiers.appliquer(i, 2);
        poserLeJoueur(L, { x: d.phases[2].equipe[0][0] * 16 + 8, y: d.phases[2].equipe[0][1] * 16 + 8 + 300 });
        L.Chantiers.equiper();
        const hier = equipe();
        L.Chantiers.appliquer(i, 3);
        const apresChangement = equipe().length, hierEncore = hier.filter(function (e) { return L.B.entites.indexOf(e) >= 0; }).length;
        L.Chantiers.equiper();
        return { hier: hier.length, apresChangement: apresChangement, hierEncore: hierEncore,
                 aujourdhui: equipe().map(function (e) { return [Math.floor(e.x / 16), Math.floor(e.y / 16)]; }),
                 postes: d.phases[3].equipe };
    """))
    assert r["hier"] == 2
    assert r["apresChangement"] == 0 and r["hierEncore"] == 0, f"l'équipe d'hier est restée : {r}"
    assert sorted(r["aujourdhui"]) == sorted(r["postes"]), f"l'équipe du jour n'est pas aux postes de la phase : {r}"


# --- 4e vague : le signaleur --------------------------------------------------------------

#: Un chantier dont le signaleur a huit tuiles de voie droite derrière lui (côté d'où vient
#: le trafic) : ni croisement ni ligne d'arrêt, pour qu'aucun feu ne brouille la mesure.
SIGNALEUR = """
  // Le signaleur tel que le jeu le lit : Python n'envoie que sa tuile [x, y] ; la voie est
  // la rangée dessous, et son sens se lit sur la carte.
  function sig(L, ch) {
    const s = ch.def.signaleur;
    return { x: s[0], y: s[1], voie: s[1] + 1, sens: L.Monde.fleche(s[0], s[1] + 1) };
  }
  function droit(L, ch) {
    const s = sig(L, ch), c = L.Monde.carte, p = { '<': 1, '>': -1 }[s.sens], voie = s.y + 1;
    for (let k = 0; k <= 8; k++) {
      const x = s.x + p * k;
      if (c.voie[voie][x] !== s.sens || L.Monde.intersectionA(x, voie) || c.arrets[x + ',' + voie]) return false;
    }
    return true;
  }
  function chantierDuSignaleur(L) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.signaleur && c.def.phases[2].tranchee === 'plaques' && droit(L, c); });
    if (i < 0) throw new Error('aucun chantier dont le signaleur ait une voie droite derrière lui');
    return i;
  }
  // Le joueur au sud du poste du signaleur, à portée de la bulle mais hors de l'écran.
  function auSudDuSignaleur(L, s) { poserLeJoueur(L, { x: s.x * 16 + 8, y: s.y * 16 + 8 + 300 }); }
  function homme(L, id) {
    return L.B.entites.find(function (e) { return e.equipeDe === id && e.posteDe === 'signal' && e.vivant; });
  }
  function palette(L, id) {
    return L.B.entites.find(function (e) { return e.type === 'decor' && e.palette === id; });
  }
  function char(L, ch, tuiles, extra) {
    const s = sig(L, ch), p = { '<': 1, '>': -1 }[s.sens];
    const v = L.Vehicules.creer('auto', (s.x + p * tuiles) * 16 + 8, (s.y + 1) * 16 + 8, s.sens === '<' ? Math.PI : 0,
                                Object.assign({ conducteur: 'trafic', etat: 'roule', sens: s.sens }, extra || {}));
    return v;
  }
"""


def _signal(corps: str) -> str:
    return _juge(SIGNALEUR + """
        L.Jeu.commencer();
        const i = chantierDuSignaleur(L), ch = L.Chantiers.liste[i], d = ch.def, s = sig(L, ch), id = d.id;
        L.B.partie.heure = 0.5;
        L.Chantiers.appliquer(i, 2);
    """ + corps)


def test_le_signaleur_nait_avec_sa_palette_et_s_en_va_avec_elle(banc):
    """Un homme sur son trottoir, intouchable, tourné vers la route, avec une palette
    dans la main — et jamais une palette qui dit ARRÊT toute seule."""
    r = banc(_signal("""
        const avant = { homme: !!homme(L, id), palette: !!palette(L, id) };
        // Sous les yeux : il ne naît pas.
        poserLeJoueur(L, { x: s.x * 16 + 8, y: s.y * 16 + 8 });
        L.Chantiers.equiper();
        const surPlace = !!homme(L, id);
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const e = homme(L, id), p = palette(L, id);
        e.face = 'haut';
        L.Chantiers.maj();
        const jour = { tx: Math.floor(e.x / 16), ty: Math.floor(e.y / 16), intouchable: e.intouchable, etat: e.etat,
                       metier: e.metier, chantier: !!e.chantier, face: e.face, arch: e.arch,
                       palette: !!p, decor: p && p.decor, solide: p && p.solide, aCote: p && Math.abs(p.x - e.x) < 12 && p.y >= e.y,
                       pose0: L.Entites.poseDuDecor(L.DECORS.panneau_signaleur, 0, false),
                       pose1: L.Entites.poseDuDecor(L.DECORS.panneau_signaleur, 180, false) };
        // Une seule palette, un seul homme, même après plusieurs passes.
        L.Chantiers.equiper(); L.Chantiers.equiper();
        const combien = { hommes: L.B.entites.filter(function (q) { return q.equipeDe === id && q.posteDe === 'signal'; }).length,
                          palettes: L.B.entites.filter(function (q) { return q.palette === id; }).length };
        // La phase 3 le garde ; le neuf et la démolition non.
        const parPhase = {};
        for (const phase of [0, 1, 3, 4]) {
            L.Chantiers.appliquer(i, phase);
            auSudDuSignaleur(L, s);
            L.Chantiers.equiper();
            parPhase[phase] = { homme: !!homme(L, id), palette: !!palette(L, id) };
        }
        // La nuit, hors de l'écran : il rentre, et la palette avec lui.
        L.Chantiers.appliquer(i, 2);
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const jourBis = { homme: !!homme(L, id), palette: !!palette(L, id) };
        L.B.partie.heure = 0.95;
        // ⚠️ Un homme resté sous les yeux la nuit : le DESSIN (la pose par défaut) et la
        // LOGIQUE (`false`, jamais de repos) disent la même chose — sinon la palette
        // montre ARRÊT pendant que le trafic passe.
        const f = L.DECORS.panneau_signaleur;
        const poseDeNuit = [L.Entites.poseDuDecor(f, 200), L.Entites.poseDuDecor(f, 200, false), L.Monde.estNuit()];
        L.Chantiers.equiper();
        const nuit = { homme: !!homme(L, id), palette: !!palette(L, id) };
        // L'homme parti (oublié loin du joueur) : la palette ne reste pas seule.
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        L.Entites.retirer(homme(L, id));
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        const orpheline = { homme: !!homme(L, id), palette: !!palette(L, id) };
        return { avant: avant, surPlace: surPlace, jour: jour, combien: combien, parPhase: parPhase, jourBis: jourBis,
                 nuit: nuit, orpheline: orpheline, poste: [s.x, s.y], poseDeNuit: poseDeNuit };
    """))
    assert r["avant"] == {"homme": False, "palette": False}
    assert r["surPlace"] is False, "le signaleur naît sous les yeux du joueur"
    j = r["jour"]
    assert (j["tx"], j["ty"]) == tuple(r["poste"]), j
    assert j["arch"] == "ouvrier" and j["intouchable"] and j["etat"] == "fige" and j["metier"] == "chantier", j
    assert not j["chantier"], "marqué `chantier`, il passerait pour un ouvrier de la voie fermée"
    assert j["face"] == "bas", "le signaleur ne regarde pas la route"
    assert j["palette"] and j["decor"] == "panneau_signaleur" and not j["solide"] and j["aCote"], j
    assert (j["pose0"], j["pose1"]) == (0, 1), "la palette ne dit pas ARRÊT puis LENTEMENT"
    assert r["combien"] == {"hommes": 1, "palettes": 1}, r["combien"]
    assert r["parPhase"]["0"] == r["parPhase"]["1"] == r["parPhase"]["4"] == {"homme": False, "palette": False}, r["parPhase"]
    assert r["parPhase"]["3"] == {"homme": True, "palette": True}, r["parPhase"]
    assert r["jourBis"] == {"homme": True, "palette": True}
    assert r["nuit"] == {"homme": False, "palette": False}, "la nuit, le signaleur est encore là"
    assert r["poseDeNuit"] == [1, 1, True], f"le dessin et la logique de la palette divergent la nuit : {r['poseDeNuit']}"
    assert r["orpheline"] == {"homme": False, "palette": False}, "la palette reste seule sur le trottoir"


def test_le_trafic_lit_la_palette(banc):
    """`signalDevant` : ARRÊT seulement, sur sa voie, dans son sens, avant lui, à moins
    de six tuiles, et jamais pour une poursuite ni une rame. Et `obstacleDevant` le
    lit — la conduite ordinaire du trafic n'a rien d'autre à savoir."""
    r = banc(_signal("""
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const dist = function (v) { return L.Chantiers.signalDevant(v); };
        const v = char(L, ch, 4);
        const out = { longueur: v.def.longueur, anime: L.DECORS.panneau_signaleur.anime,
                      patience: L.B.defs.conduite.trafic.patience_images };
        L.B.t = 0;                                           // la palette dit ARRÊT
        out.arret = dist(v);
        out.obstacle = L.Vehicules.obstacleDevant(v);
        L.B.t = 180;                                         // ... puis LENTEMENT
        out.lentement = dist(v);
        out.obstacleLent = L.Vehicules.obstacleDevant(v);
        L.B.t = 0;
        // Le même char, ailleurs : ce que le signaleur ne dit pas à tout le monde.
        const ailleurs = function (retouche) {
            const w = char(L, ch, 4); retouche(w); const r = dist(w); L.Entites.retirer(w); return r;
        };
        out.autreRangee = ailleurs(function (w) { w.y += 16; });
        out.autreSens = ailleurs(function (w) { w.sens = s.sens === '<' ? '>' : '<'; });
        out.dejaPasse = char(L, ch, -3) && (function () { const w = char(L, ch, -3); const r = dist(w); L.Entites.retirer(w); return r; })();
        out.trop_loin = (function () { const w = char(L, ch, L.Chantiers.PORTEE_SIGNAL_TUILES + 3); const r = dist(w); L.Entites.retirer(w); return r; })();
        out.poursuite = ailleurs(function (w) { w.poursuite = true; });
        out.rame = ailleurs(function (w) { w.rails = true; });
        // Sans son homme (oublié loin du joueur, la palette avec lui), personne ne dit rien.
        L.Entites.retirer(homme(L, id));
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        out.sansHomme = dist(v);
        return out;
    """))
    marge = r["longueur"] / 2
    assert r["anime"] < r["patience"], \
        "l'ARRÊT dure plus que la patience du trafic : il forcerait le passage au lieu de l'obéir"
    assert abs(r["arret"] - (4 * 16 - marge)) < 1e-6, f"la distance de l'ARRÊT n'est pas celle du nez : {r}"
    assert r["obstacle"] <= r["arret"], "la conduite ordinaire ne lit pas le signaleur"
    assert r["lentement"] == float("inf") or r["lentement"] is None, f"LENTEMENT arrête le trafic : {r}"
    # (JSON rend l'infini par `null`.)
    assert r["obstacleLent"] is None or r["obstacleLent"] > r["arret"], "LENTEMENT arrête encore le trafic"
    for cas in ("autreRangee", "autreSens", "dejaPasse", "trop_loin", "poursuite", "rame", "sansHomme"):
        assert r[cas] is None or r[cas] == float("inf"), f"le signaleur arrête aussi ce cas-là : {cas} = {r[cas]}"


def test_un_char_du_trafic_s_arrete_a_l_arret_et_repart_a_lentement(banc):
    """⚠️ Le geste, pas la fonction : un vrai char de trafic sur la voie du signaleur
    s'arrête avant la tranchée tant que la palette dit ARRÊT, sans jamais la passer, et
    repart quand elle dit LENTEMENT — en moins de trois secondes d'attente, sous la
    patience du trafic (il ne force pas le passage)."""
    r = banc(_signal("""
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const v = char(L, ch, 5);
        L.B.t = 0;
        const sens = { '<': 1, '>': -1 }[s.sens], mx = homme(L, id).x;
        const avance = function () { return (v.x - mx) * sens; };      // > 0 : il n'a pas passé le signaleur
        const trace = [];
        let force = 0;
        for (let k = 0; k < 175; k++) {
            L.Chantiers.maj();
            o.frame(1);
            if (v.force > 0) force++;
            if (k % 25 === 0) trace.push([Math.round(avance()), +v.vitesse.toFixed(2)]);
        }
        const arrete = { avance: avance(), vitesse: v.vitesse, force: force, patience: v.patience, t: L.B.t };
        L.B.t = 180;
        for (let k = 0; k < 200; k++) o.frame(1);
        return { arrete: arrete, trace: trace, apres: avance(), vitesseApres: v.vitesse, present: L.B.entites.indexOf(v) >= 0 };
    """))
    a = r["arrete"]
    assert a["vitesse"] < 0.1, f"le char roule encore sous ARRÊT : {r['trace']}"
    assert a["avance"] > 16, f"le char a passé le signaleur sous ARRÊT : {r['trace']}"
    assert a["force"] == 0, f"le char force le passage pendant ARRÊT (patience {a['patience']}) : {r['trace']}"
    assert r["present"], "le char a disparu"
    assert r["apres"] < 0, f"à LENTEMENT, le char n'a pas repris sa route : {r}"


# --- 5e vague : le tas de terre fait rampe ---------------------------------------------------

#: Un char lancé sur le tas de terre de la phase « rasé », mesuré image par image.
TAS = """
  // ⚠️ `o.char` pose RELATIVEMENT au joueur : ici, des coordonnées absolues.
  function poserUnChar(L, slug, x, y) {
    const v = L.Vehicules.creer(slug, x, y, 0, { etat: 'stationne' });
    L.Entites.indexer();
    return v;
  }
  // Le tas SEUL : la pelle voisine (à deux tuiles, arrête six) barrerait la route au banc.
  function appliquerSansLaPelle(L, i, phase) {
    const id = L.Chantiers.liste[i].def.id;
    L.Chantiers.appliquer(i, phase);
    for (const e of L.B.entites.slice()) if (e.machineDe === id && e.decor !== 'tas_de_terre') L.Entites.retirer(e);
    L.Entites.reindexerDecor();
  }
  // `gaz` 0 : le char roule sur son erre — un char qui rampe ne doit pas ré-accélérer en route.
  function surLeTas(L, o, slug, vitesse, phase, gaz, depart) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].machines.some(function (m) { return m.type === 'tas_de_terre'; }); });
    const ch = L.Chantiers.liste[i], id = ch.def.id;
    appliquerSansLaPelle(L, i, phase === undefined ? 2 : phase);
    const tas = L.B.entites.find(function (e) { return e.decor === 'tas_de_terre' && e.machineDe === id; });
    if (phase !== undefined && !tas) return { tas: false };
    poserLeJoueur(L, { x: tas.x, y: tas.y + 300 });
    const v = poserUnChar(L, slug, tas.x - (depart || 60), tas.y - 1);
    v.etat = 'roule';
    v.vitesse = vitesse; v.vx = vitesse; v.vy = 0; v.angle = 0;
    const vie0 = v.vie;
    let zMax = 0, vitesseMin = vitesse, decolle = -1;
    // Au plus 70 images, et on s'arrête dès qu'on a retombé passé le tas (voir plus bas) : ni jusqu'au mur d'en face.
    for (let k = 0; k < 70; k++) {
      L.Vehicules.majTas(v);
      L.Vehicules.majPhysique(v, { gaz: gaz === undefined ? 1 : gaz, frein: 0, direction: 0 });
      L.Vehicules.avancer(v);
      if (v.z > 0 && decolle < 0) decolle = k;
      zMax = Math.max(zMax, v.z);
      vitesseMin = Math.min(vitesseMin, Math.hypot(v.vx, v.vy));
      // Retombé ET passé le tas : on s'arrête là. Plus loin, c'est le mur du lot d'en face, pas le tas.
      if (decolle >= 0 && v.z === 0 && (v.x - tas.x) > 25) break;
    }
    return { tas: true, zMax: zMax, decolle: decolle, apres: (v.x - tas.x), vitesseMin: vitesseMin,
             perdu: vie0 - v.vie, brise: !!tas.brise, z: v.z, repit: v.tasT };
  }
"""


def test_le_tas_de_terre_est_une_rampe_douce(banc):
    """Un char lancé sur le tas décolle DOUCEMENT, sans perdre ni vitesse ni carrosserie,
    et retombe passé le tas. Plus doux qu'une rampe : moins que les 6 px au-delà desquels un
    char passe au-dessus des tuiles — même la moto, le char le plus rapide."""
    r = banc(_juge(TAS + """
        L.Jeu.commencer();
        const out = {};
        out.auto = surLeTas(L, o, 'auto', 3.4);
        out.moto = surLeTas(L, o, 'moto', 5.2);
        out.lent = surLeTas(L, o, 'auto', 1.1, undefined, 0, 36);
        out.autobus = surLeTas(L, o, 'autobus', 2.6);
        out.absent = surLeTas(L, o, 'auto', 3.4, 3);
        out.ph = L.B.defs.conduite.physique;
        return out;
    """))
    ph = r["ph"]
    for slug in ("auto", "moto", "autobus"):
        c = r[slug]
        assert c["decolle"] >= 0 and c["zMax"] > 0, f"{slug} : le tas ne fait pas décoller : {c}"
        assert c["zMax"] <= ph["tas_hauteur_max"], f"{slug} vole plus haut qu'un char qui passe un mur : {c}"
        assert c["perdu"] == 0, f"{slug} : une rampe ne coûte rien : {c}"
        assert not c["brise"], f"{slug} a déraciné le tas de terre : {c}"
        assert c["apres"] > 20, f"{slug} s'est arrêté sur le tas : {c}"
        assert c["vitesseMin"] > 0.5, f"{slug} : le tas l'a ralenti : {c}"
        assert c["z"] == 0, f"{slug} n'est pas retombé : {c}"
    assert r["lent"]["zMax"] == 0, f"un char qui rampe décolle : {r['lent']}"
    assert r["lent"]["apres"] > 5, f"un char lent bute sur le tas : {r['lent']}"
    assert r["absent"]["tas"] is False or r["absent"]["zMax"] == 0, "le tas n'existe plus en phase 3 : rien ne fait décoller"


def test_le_tas_de_terre_n_est_pas_un_mur_meme_pour_un_char_lourd(banc):
    """`decorDevant` l'ignore : la berline n'y bute pas, l'autobus (masse 3,2, au-delà du
    `arrete` de 3,0) ne le déracine pas. `arrete` ne sert plus qu'aux balles."""
    r = banc(_juge(TAS + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].machines.some(function (m) { return m.type === 'tas_de_terre'; }); });
        const ch = L.Chantiers.liste[i];
        appliquerSansLaPelle(L, i, 2);
        const tas = L.B.entites.find(function (e) { return e.decor === 'tas_de_terre' && e.machineDe === ch.def.id; });
        const out = { arrete: L.DECORS.tas_de_terre.arrete, rampe: L.DECORS.tas_de_terre.rampe };
        for (const slug of ['auto', 'autobus', 'camion']) {
            const v = poserUnChar(L, slug, tas.x, tas.y);
            v.vitesse = 3; v.vx = 3; v.vy = 0;
            out[slug] = { rencontre: L.Vehicules.decorDevant(v, tas.x, tas.y), traverse: L.Vehicules.heurterDecor(v, tas.x, tas.y), brise: !!tas.brise };
        }
        return out;
    """))
    assert r["rampe"] and r["arrete"], "le tas garde `arrete` pour les balles et déclare sa rampe"
    for slug in ("auto", "autobus", "camion"):
        assert r[slug]["rencontre"] is None, f"{slug} rencontre le tas comme un obstacle : {r[slug]}"
        assert r[slug]["traverse"] is True and not r[slug]["brise"], f"{slug} : {r[slug]}"


def test_le_tas_de_terre_ne_rebondit_pas_dix_fois(banc):
    """Le répit : rouler lentement sur le tas ne le fait pas rebondir à chaque image."""
    r = banc(_juge(TAS + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].machines.some(function (m) { return m.type === 'tas_de_terre'; }); });
        const ch = L.Chantiers.liste[i];
        appliquerSansLaPelle(L, i, 2);
        const tas = L.B.entites.find(function (e) { return e.decor === 'tas_de_terre' && e.machineDe === ch.def.id; });
        const v = poserUnChar(L, 'auto', tas.x, tas.y - 1);
        v.vitesse = 3; v.vx = 3; v.vy = 0;
        let decollages = 0, avant = 0;
        for (let k = 0; k < 20; k++) {
            L.Vehicules.majTas(v);
            if (v.vz > avant) decollages++;
            avant = v.vz;
            v.z = 0; v.vz = 0; avant = 0;          // on le repose : seul le répit peut l'empêcher de re-décoller
        }
        return { decollages: decollages, repit: v.tasT, ph: L.B.defs.conduite.physique };
    """))
    assert r["decollages"] == 1, f"le tas fait rebondir à chaque image : {r}"
    assert r["repit"] > 0


# --- 6e vague : la benne qu'on pousse ------------------------------------------------------

BENNE = TAS + """
  function benneDe(L, id) { return L.B.entites.filter(function (e) { return e.conteneurDe === id; }); }
  function chantierAvecBenne(L) {
    return L.Chantiers.liste.findIndex(function (c) { return c.def.conteneur; });
  }
  // La benne SEULE dans son coin : les machines voisines et l'équipe ne se mettent pas en travers.
  // ⚠️ LAZY comme l'équipe : elle ne naît que dans `equiper()`, joueur dans la bulle et hors de
  // l'écran — au sud de chez elle, comme `auSud` le fait pour l'équipe.
  function appliquerSeule(L, i, phase) {
    const id = L.Chantiers.liste[i].def.id, maison = L.Chantiers.liste[i].def.conteneur;
    L.Chantiers.appliquer(i, phase);
    for (const e of L.B.entites.slice()) if (e.machineDe === id) L.Entites.retirer(e);
    L.Entites.reindexerDecor();
    poserLeJoueur(L, { x: maison[0] * 16 + 8, y: maison[1] * 16 + 8 + 300 });
    L.Chantiers.equiper();
    return benneDe(L, id)[0];
  }
"""


def test_la_benne_est_la_pendant_les_travaux(banc):
    """Une seule, chez elle, solide, dans l'index du décor : des phases 1 à 3, jamais sur la maison
    condamnée ni sur le neuf — et jamais en double quand on repose la même phase.

    ⚠️ LAZY comme l'équipe (`poserLaBenneSiBesoin`, appelée par `equiper`) : le joueur doit être
    dans la bulle et hors de l'écran pour qu'elle naisse, sinon chaque chantier « ouvert » en
    poserait une au démarrage, qu'on le visite ou non — voir sa note dans `chantiers.js`."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const i = chantierAvecBenne(L), ch = L.Chantiers.liste[i], id = ch.def.id, maison = ch.def.conteneur;
        const parPhase = {};
        for (const phase of [0, 1, 2, 3, 4, 2, 2]) {
            L.Chantiers.appliquer(i, phase);
            poserLeJoueur(L, { x: maison[0] * 16 + 8, y: maison[1] * 16 + 8 + 300 });
            L.Chantiers.equiper();
            const b = benneDe(L, id);
            parPhase[phase] = { n: b.length };
            if (b.length) {
                const e = b[0];
                parPhase[phase].chez = [Math.floor(e.x / 16), Math.floor((e.y - 15) / 16)];
                parPhase[phase].solide = e.solide;
                parPhase[phase].indexee = L.Entites.decorAutour(e.x, e.y, 2).indexOf(e) >= 0;
                parPhase[phase].machine = e.machineDe !== undefined;
            }
        }
        return { parPhase: parPhase, maison: maison, fiche: L.DECORS.conteneur };
    """))
    p = r["parPhase"]
    assert p["0"]["n"] == 0 and p["4"]["n"] == 0, "une benne sur la maison condamnée ou sur le neuf"
    for phase in "123":
        assert p[phase]["n"] == 1, f"phase {phase} : {p[phase]}"
        assert p[phase]["chez"] == r["maison"] and p[phase]["solide"] and p[phase]["indexee"], p[phase]
        assert not p[phase]["machine"], "la benne est une machine : le chantier la ferait travailler"


def test_un_char_pousse_la_benne_et_la_paie(banc):
    """⚠️ Le geste : une berline lancée sur la benne la POUSSE — elle avance de sa portée, pas plus,
    et le char perd de sa vitesse en route ; au bout, c'est un mur."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const i = chantierAvecBenne(L), fiche = L.DECORS.conteneur;
        const b = appliquerSeule(L, i, 2);
        poserLeJoueur(L, { x: b.x, y: b.y + 300 });
        const dep = { x: b.x, y: b.y };
        const v = poserUnChar(L, 'auto', b.x - 60, b.y - 3);
        v.etat = 'roule'; v.vitesse = 2.6; v.vx = 2.6; v.vy = 0; v.angle = 0;
        const vie0 = v.vie, vitesses = [];
        let pousse = 0, bute = false;
        for (let k = 0; k < 120; k++) {
            const avant = b.x;
            L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 0 });
            L.Vehicules.avancer(v);
            if (b.x > avant) pousse++;
            if (k > 20 && k % 10 === 0) vitesses.push(+Math.hypot(v.vx, v.vy).toFixed(2));
        }
        const fin = { x: b.x, y: b.y };
        return { dep: dep, fin: fin, pousse: pousse, vitesses: vitesses, portee: fiche.portee,
                 dansLIndex: L.Entites.decorAutour(b.x, b.y, 2).indexOf(b) >= 0,
                 ancienneVide: L.Entites.decorAutour(dep.x, dep.y, 2).indexOf(b) >= 0 && Math.abs(b.x - dep.x) > 8,
                 vx: v.x - b.x, chocs: v.chocs, perdu: vie0 - v.vie };
    """))
    dx = r["fin"]["x"] - r["dep"]["x"]
    assert dx > 8, f"la benne n'a pas bougé sous un char lancé dessus : {r}"
    assert dx <= r["portee"] + 0.6, f"la benne est allée plus loin que sa portée : {dx} > {r['portee']}"
    assert abs(r["fin"]["y"] - r["dep"]["y"]) < 0.5, "la benne a dérivé de côté"
    assert r["pousse"] > 3
    assert r["dansLIndex"] and not r["ancienneVide"], "l'index du décor ne suit pas la benne"
    assert r["vx"] < 0, f"le char a traversé la benne : {r['vx']}"
    assert min(r["vitesses"]) < 2.0, f"pousser la benne ne coûte aucune vitesse : {r['vitesses']}"


def test_la_benne_ne_traverse_pas_un_mur(banc):
    """⚠️ Contre une VRAIE façade (le lot d'un chantier rasé n'en a plus) : la benne s'arrête à son
    pied, aucun coin de sa boîte n'entre dans une tuile solide — poussée par un char, ou d'un coup."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const f = L.DECORS.conteneur, sol = f.sol, c = L.Monde.carte;
        // Une façade quelconque de la ville, avec trois tuiles libres dessous.
        let mur = null;
        for (let ty = 3; ty < c.h - 6 && !mur; ty++) {
            for (let tx = 3; tx < c.w - 3 && !mur; tx++) {
                const s = L.Monde.solidite;
                if (s(tx, ty) === 1 && [-2, -1, 0, 1, 2].every(function (d) { return s(tx + d, ty + 1) === 0 && s(tx + d, ty + 2) === 0 && s(tx + d, ty + 3) === 0; })
                    && [-1, 0, 1].every(function (d) { return s(tx + d, ty) === 1; })) mur = { tx: tx, ty: ty };
            }
        }
        const x = mur.tx * 16 + 8, yMur = (mur.ty + 1) * 16;            // le pied du mur
        // Une benne à 9 px du mur (comme à l'ouverture du chantier).
        const b = L.Entites.creer('decor', x, yMur + 9 + sol[1], { decor: 'conteneur', r: f.r, solide: true, dessine: true });
        b.chez = { x: b.x, y: b.y };
        L.Entites.reindexerDecor();
        poserLeJoueur(L, { x: x, y: yMur + 300 });
        const direct = L.Entites.pousserDecor(b, 0, -12);           // 12 px > les 9 qui la séparent du mur
        const intacte = b.y === yMur + 9 + sol[1];
        // Puis un char, de face : elle monte jusqu'au mur, pas plus loin.
        const v = poserUnChar(L, 'auto', x - 2, b.y + 40);
        v.etat = 'roule'; v.angle = -Math.PI / 2; v.vitesse = 2.6; v.vx = 0; v.vy = -2.6;
        for (let k = 0; k < 120; k++) {
            L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 0 });
            L.Vehicules.avancer(v);
        }
        let coinsSolides = 0;
        for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
            if (L.Monde.solidite(Math.floor((b.x + sx * sol[0]) / 16), Math.floor((b.y + sy * sol[1]) / 16)) !== 0) coinsSolides++;
        }
        return { direct: direct, intacte: intacte, monte: b.y < yMur + 9 + sol[1] - 0.5, coinsSolides: coinsSolides,
                 hautDeLaBoite: b.y - sol[1], yMur: yMur };
    """))
    assert r["direct"] is False and r["intacte"], f"la benne est entrée dans la façade d'un coup : {r}"
    assert r["monte"], f"le char n'a pas poussé la benne vers le mur : {r}"
    assert r["coinsSolides"] == 0, f"un coin de la benne est dans un mur : {r}"
    assert r["hautDeLaBoite"] >= r["yMur"] - 0.01, f"la benne dépasse le pied du mur : {r}"


def test_l_index_du_decor_suit_la_benne_d_une_cellule_a_l_autre(banc):
    """⚠️ L'index fixe se range par cellules de 64 px : une benne qui en franchit une doit quitter
    la liste de l'ancienne et entrer dans celle de la nouvelle — sinon les piétons buteraient sur
    l'endroit qu'elle a quitté et traverseraient celui où elle est."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const f = L.DECORS.conteneur, c = L.Monde.carte;
        // Un coin de ville tout dégagé, à cheval sur une frontière de cellule verticale (x = 64 k).
        let lieu = null;
        for (let k = 2; k < 60 && !lieu; k++) {
            for (let ty = 4; ty < c.h - 4 && !lieu; ty++) {
                let libre = true;
                for (let tx = Math.floor((64 * k - 30) / 16); tx <= Math.floor((64 * k + 30) / 16) && libre; tx++) {
                    if (L.Monde.solidite(tx, ty) !== 0 || L.Monde.solidite(tx, ty - 1) !== 0) libre = false;
                }
                if (libre) lieu = { x: 64 * k - 3, y: ty * 16 + 12, k: k };
            }
        }
        const d = L.Entites.creer('decor', lieu.x, lieu.y, { decor: 'conteneur', r: f.r, solide: true, dessine: true, chez: { x: lieu.x, y: lieu.y } });
        L.Entites.reindexerDecor();
        const avant = L.Entites.decorAutour(lieu.x, lieu.y, 1).indexOf(d) >= 0;
        const ok = L.Entites.pousserDecor(d, 6, 0);
        return { lieu: lieu, avant: avant, ok: ok,
                 ici: L.Entites.decorAutour(d.x, d.y, 1).indexOf(d) >= 0,
                 celluleApres: Math.floor(d.x / 64), celluleAvant: Math.floor(lieu.x / 64) };
    """))
    assert r["avant"] and r["ok"], r
    assert r["celluleApres"] == r["celluleAvant"] + 1, f"le montage ne franchit pas de cellule : {r}"
    assert r["ici"], f"la benne n'est plus dans l'index de sa nouvelle cellule : {r}"


def test_la_benne_rentre_chez_elle_avec_la_phase(banc):
    """La phase change : la benne d'hier (poussée) s'en va, `equiper` en repose une chez elle — pas
    à l'endroit qu'on l'avait poussée."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const i = chantierAvecBenne(L), ch = L.Chantiers.liste[i], id = ch.def.id, maison = ch.def.conteneur;
        const b = appliquerSeule(L, i, 2);
        const chez = { x: b.chez.x, y: b.chez.y };
        L.Entites.pousserDecor(b, 10, 0);
        const poussee = { x: b.x, y: b.y };
        L.Chantiers.appliquer(i, 3);
        poserLeJoueur(L, { x: maison[0] * 16 + 8, y: maison[1] * 16 + 8 + 300 });
        L.Chantiers.equiper();
        const apres = benneDe(L, id);
        return { chez: chez, poussee: poussee, n: apres.length, apres: apres[0] && { x: apres[0].x, y: apres[0].y },
                 ancienne: L.B.entites.indexOf(b) >= 0 };
    """))
    assert r["poussee"]["x"] == r["chez"]["x"] + 10
    assert r["n"] == 1 and r["apres"] == r["chez"], f"la benne n'est pas rentrée : {r}"
    assert not r["ancienne"], "l'ancienne benne est restée dans la ville"


def test_le_poids_de_la_benne_se_paie_selon_la_masse_du_char(banc):
    """La berline la pousse à petite vitesse, l'autobus la sent à peine : le frein dépend de la
    masse du char, et il est borné."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const i = chantierAvecBenne(L), ph = L.B.defs.conduite.physique, fiche = L.DECORS.conteneur;
        const out = { ph: { f: ph.poussee_frein, max: ph.poussee_frein_max }, poussable: fiche.poussable };
        for (const slug of ['auto', 'autobus', 'moto', 'camion']) {
            const b = appliquerSeule(L, i, 2);
            poserLeJoueur(L, { x: b.x, y: b.y + 300 });
            const v = poserUnChar(L, slug, b.x - 8, b.y - 3);
            v.vitesse = 3; v.vx = 3; v.vy = 0;
            const c = { x: v.x, y: v.y, r: 7 };
            const ok = L.Vehicules.pousserLeDecor(v, b, c);
            out[slug] = { ok: ok, reste: +(Math.hypot(v.vx, v.vy) / 3).toFixed(4), masse: v.def.masse };
        }
        // ⚠️ Aucun char du parc n'atteint la borne du frein : un char imaginaire, dix fois plus léger.
        const b = appliquerSeule(L, i, 2);
        poserLeJoueur(L, { x: b.x, y: b.y + 300 });
        const leger = poserUnChar(L, 'moto', b.x - 8, b.y - 3);
        leger.def = Object.assign({}, leger.def, { masse: 0.05 });
        leger.vitesse = 3; leger.vx = 3; leger.vy = 0;
        L.Vehicules.pousserLeDecor(leger, b, { x: leger.x, y: leger.y, r: 7 });
        out.leger = { reste: +(Math.hypot(leger.vx, leger.vy) / 3).toFixed(4) };
        return out;
    """))
    for slug in ("auto", "autobus", "moto", "camion"):
        assert r[slug]["ok"], (slug, r[slug])
        attendu = 1 - min(r["ph"]["max"], r["poussable"] * r["ph"]["f"] / r[slug]["masse"])
        assert abs(r[slug]["reste"] - attendu) < 1e-3, (slug, r[slug], attendu)
    assert r["auto"]["reste"] < r["autobus"]["reste"] <= 1, "l'autobus sent la benne autant que la berline"
    assert abs(r["leger"]["reste"] - (1 - r["ph"]["max"])) < 1e-3, f"le frein n'est pas borné : {r['leger']}"


def test_la_portee_de_la_benne_tient_dans_son_bloc_libre(banc):
    """La garantie de Python (un bloc de sol libre de cinq tuiles de large) et la portée du jeu
    parlent de la même chose : la benne, poussée au bout, reste dans le bloc."""
    r = banc(_juge("""
        const f = L.DECORS.conteneur;
        return { portee: f.portee, sol: f.sol, poussable: f.poussable, arrete: f.arrete };
    """))
    demi_bloc = (chantiers.CONTENEUR_LARGEUR // 2) * 16 + 8
    assert r["portee"] + r["sol"][0] <= demi_bloc, "poussée au bout, la benne sortirait de son bloc libre"
    assert r["poussable"] > 0 and r["arrete"], "une benne poussable garde `arrete` (elle arrête les balles)"


def test_la_benne_bute_sur_un_autre_decor_solide(banc):
    """Poussée contre un banc ou une machine, elle ne le traverse pas : `pousserDecor` refuse."""
    r = banc(_juge(BENNE + """
        L.Jeu.commencer();
        const i = chantierAvecBenne(L), f = L.DECORS.conteneur;
        const b = appliquerSeule(L, i, 2);
        // Un décor solide juste à côté, à l'est, dans la direction de la poussée.
        const banc = L.Entites.creer('decor', b.x + f.sol[0] + 6, b.y, { decor: 'banc', r: 6, solide: true, dessine: true });
        L.Entites.reindexerDecor();
        const contre = L.Entites.pousserDecor(b, 8, 0);
        const x1 = b.x;
        const libre = L.Entites.pousserDecor(b, -8, 0);
        return { contre: contre, x1: x1, chez: b.chez.x, libre: libre, apres: b.x, solide: !!L.DECORS.banc };
    """))
    assert r["solide"]
    assert r["contre"] is False and r["x1"] == r["chez"], f"la benne a traversé le banc : {r}"
    assert r["libre"] is True and r["apres"] == r["chez"] - 8, f"la benne ne recule pas quand la voie est libre : {r}"


# --- 7e vague : de nouveaux chantiers quand les premiers sont finis -----------------------------

DORMANT = """
  function dormant(L) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.ouvre; });
    if (i < 0) throw new Error('aucun chantier dormant');
    return i;
  }
  // Ce que la couche peinte du chantier ajoute : les couleurs des planches et du panneau.
  function peintDeChantier(L, ch) {
    const d = ch.def, log = [];
    let style = '';
    const ctx = new Proxy({}, {
      get: function (t, k) {
        if (k === 'fillStyle') return style;
        return function () { if (k === 'fillRect') log.push([style].concat(Array.from(arguments))); };
      },
      set: function (t, k, v) { if (k === 'fillStyle') style = v; return true; },
    });
    // Tous les morceaux que touche le chantier.
    for (let my = Math.floor((d.y - 1) / 16); my <= Math.floor((d.y + d.h + 1) / 16); my++) {
      for (let mx = Math.floor((d.x - 1) / 16); mx <= Math.floor((d.x + d.l) / 16); mx++) L.Chantiers.peindre(ctx, mx, my);
    }
    return log.map(function (r) { return r[0]; });
  }
"""


def test_un_chantier_dort_jusqu_a_son_jour_puis_s_eveille_hors_de_vue(banc):
    """Le jour de l'ouverture, la maison passe de « telle quelle » à « condamnée » — et jamais sous les
    yeux du joueur : le dormant attend, comme toute autre phase, que le coin soit tourné."""
    r = banc(_juge(DORMANT + """
        L.Jeu.commencer();
        const i = dormant(L), ch = L.Chantiers.liste[i], d = ch.def, id = d.id, carte = L.Monde.carte;
        const rangees = function () {
            const out = [];
            for (let j = 0; j < d.h; j++) out.push(carte.sol[d.y + j].slice(d.x, d.x + d.l));
            return out;
        };
        L.B.partie.heure = 0.5;
        const dort = { dort: ch.dort, posee: ch.posee, etat: L.Chantiers.etat(ch), voulue: L.Chantiers.phaseVoulue(d),
                       sol: rangees(), base: d.phases[0].sol,
                       peint: peintDeChantier(L, ch).filter(function (c) { return c === '#e8b33c' || c === '#2b2734'; }).length,
                       entites: L.B.entites.filter(function (e) { return e.machineDe === id || e.equipeDe === id || e.conteneurDe === id || e.palette === id; }).length };
        // Le jour venu, mais le joueur devant : il attend.
        const debut = (L.B.partie.chantiers && L.B.partie.chantiers.debut) || 1;
        L.B.partie.jour = debut + d.ouvre;
        poserLeJoueur(L, { x: (d.x + d.l / 2) * 16, y: (d.y + d.h + 2) * 16 });
        o.frame(100);
        const devant = { dort: ch.dort, etat: L.Chantiers.etat(ch), voulue: L.Chantiers.phaseVoulue(d) };
        // Il tourne le coin : le chantier s'éveille.
        poserLeJoueur(L, loin(L));
        o.frame(100);
        const eveille = { dort: ch.dort, posee: ch.posee, etat: L.Chantiers.etat(ch), voulue: L.Chantiers.phaseVoulue(d),
                          peint: peintDeChantier(L, ch).filter(function (c) { return c === '#e8b33c' || c === '#2b2734'; }).length };
        return { dort: dort, devant: devant, eveille: eveille, ouvre: d.ouvre };
    """))
    dort = r["dort"]
    assert dort["dort"] and dort["posee"] == 0 and dort["etat"] == -1 and dort["voulue"] == -1, dort
    assert dort["sol"] == dort["base"], "un chantier dormant a changé la ville"
    assert dort["peint"] == 0, "un chantier dormant peint déjà des planches ou un panneau"
    assert dort["entites"] == 0, "un chantier dormant a déjà des machines, du monde ou une benne"
    assert r["devant"] == {"dort": True, "etat": -1, "voulue": 0}, f"le chantier s'est éveillé sous les yeux du joueur : {r['devant']}"
    assert r["eveille"]["dort"] is False and r["eveille"]["etat"] == 0 == r["eveille"]["voulue"], r["eveille"]
    assert r["eveille"]["peint"] > 0, "éveillé, le chantier n'a ni planches ni panneau"


def test_un_dormant_ne_fait_rien_travailler(banc):
    """Ni homme, ni signaleur, ni benne, ni son : un chantier qui n'a pas ouvert est une maison."""
    r = banc(_juge(DORMANT + """
        L.Jeu.commencer();
        const i = dormant(L), ch = L.Chantiers.liste[i], d = ch.def, id = d.id;
        L.B.partie.heure = 0.5;
        poserLeJoueur(L, { x: (d.x + d.l / 2) * 16 + 8, y: (d.y + d.h + 8) * 16 + 300 });
        L.Chantiers.equiper();
        for (let k = 0; k < 400; k++) { L.Chantiers.travailler(); L.B.t++; }
        return { entites: L.B.entites.filter(function (e) { return e.equipeDe === id || e.palette === id || e.conteneurDe === id; }).length,
                 journal: L.Chantiers.journal.filter(function (x) { return Math.abs(x.x - (d.x + d.l / 2) * 16) < 200 && Math.abs(x.y - (d.y + d.h / 2) * 16) < 200; }).length };
    """))
    assert r["entites"] == 0 and r["journal"] == 0, r


# --- 8e vague : la pelle du chantier se conduit -----------------------------------------------

PELLE = """
  function chantierDeLaPelle(L) {
    return L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].machines.some(function (m) { return m.type === 'pelleteuse'; }); });
  }
  function pelleDecor(L, ch) { return ch.machines.find(function (m) { return m.decor === 'pelleteuse'; }); }
  // Le joueur planté à côté du décor, tourné vers lui.
  function auPiedDeLaPelle(L, d) {
    const j = L.B.joueur;
    j.x = d.x - 22; j.y = d.y - 4; j.face = 'droite'; j.angle = 0; j.vx = 0; j.vy = 0; j.dansVehicule = null; j.dessine = true;
    L.Entites.indexer();
    return j;
  }
"""


def test_on_monte_dans_la_pelle_du_chantier(banc):
    """⚠️ L'étage 2 : le décor animé de la phase « rasé » est une pelle qu'on prend. Il faut être
    à portée ET lui faire face ; ACTION passe par `Missions.interagir` ; le décor cède sa place à un
    vrai char (plus de godet qui racle) ; et le crochet du chantier ne la reprend pas."""
    r = banc(_juge(PELLE + """
        L.Jeu.commencer();
        const i = chantierDeLaPelle(L), ch = L.Chantiers.liste[i], id = ch.def.id;
        L.Chantiers.appliquer(i, 2);
        L.B.partie.heure = 0.5;
        const d = pelleDecor(L, ch);
        const j = auPiedDeLaPelle(L, d);
        const out = { pres: !!L.Chantiers.pelleSousLaMain(j), invite: L.Chantiers.inviteMonter(j) };
        // Loin : rien.
        j.x = d.x - 200; out.loin = L.Chantiers.pelleSousLaMain(j); j.x = d.x - 22;
        // Dos tourné : rien (le bouton ne promet que ce qu'il fera).
        j.face = 'gauche'; j.angle = Math.PI; out.dos = L.Chantiers.pelleSousLaMain(j); j.face = 'droite'; j.angle = 0;
        // Une pelle brisée n'est plus une pelle.
        d.brise = true; out.brisee = L.Chantiers.pelleSousLaMain(j); d.brise = false;
        // La phase 3 n'a plus de pelle.
        const avant = L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).length;
        // ACTION.
        L.Missions.majInvite(j);
        out.inviteHud = L.B.invite;
        out.action = L.Missions.interagir(j);
        const v = L.B.entites.find(function (e) { return e.type === 'vehicule' && e.slug === 'pelleteuse'; });
        out.vehicule = v && { conducteur: v.conducteur === j, pelleDe: v.pelleDe, couleur: v.couleur, dedans: j.dansVehicule === v, nom: v.def.nom };
        out.decorRestant = L.B.entites.filter(function (e) { return e.decor === 'pelleteuse' && e.machineDe === id; }).length;
        out.machines = ch.machines.filter(function (m) { return m.decor === 'pelleteuse'; }).length;
        out.vehicules = L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).length - avant;
        // Le godet ne racle plus : aucune image de travail ne le joue.
        L.Son.SFX.chantier = function () {};
        const t0 = L.B.t, journalAvant = L.Chantiers.journal.length;
        for (let k = 0; k < 400; k++) { L.Chantiers.travailler(); L.B.t++; }
        out.godets = L.Chantiers.journal.slice(journalAvant).filter(function (x) { return x.son === 'godet'; }).length;
        return out;
    """))
    assert r["pres"] and r["invite"] == "MONTER : PELLETEUSE", r
    assert r["loin"] is None, "la pelle se prend de loin"
    assert r["dos"] is None, "la pelle se prend dos tourné"
    assert r["brisee"] is None, "on monte dans une pelle brisée"
    assert r["inviteHud"] == "MONTER : PELLETEUSE", f"le HUD ne promet pas ce qu'ACTION fait : {r['inviteHud']}"
    assert r["action"] is True
    assert r["vehicule"] == {"conducteur": True, "pelleDe": r["vehicule"]["pelleDe"], "couleur": "#e8b33c", "dedans": True, "nom": "Pelleteuse"}, r["vehicule"]
    assert r["decorRestant"] == 0 and r["machines"] == 0, "le décor est resté dans le chantier"
    assert r["vehicules"] == 1, "un seul char de plus"
    assert r["godets"] == 0, "le godet racle encore une pelle qui n'est plus là"


def test_la_pelle_roule_a_douze_kilometres_heure_et_ne_nait_pas_dans_la_rue(banc):
    r = banc(_juge(PELLE + """
        L.Jeu.commencer();
        const i = chantierDeLaPelle(L), ch = L.Chantiers.liste[i];
        L.Chantiers.appliquer(i, 2);
        const d = pelleDecor(L, ch), j = auPiedDeLaPelle(L, d);
        L.Missions.interagir(j);
        const v = j.dansVehicule;
        // Elle roule : plein gaz sur une centaine d'images, jusqu'à sa vitesse max.
        v.x = d.x + 60; v.y = d.y + 40; v.angle = 0; v.vx = 0; v.vy = 0; v.vitesse = 0;
        let vmax = 0;
        for (let k = 0; k < 90; k++) {
            L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 0 });
            v.x += v.vx; v.y += v.vy;
            vmax = Math.max(vmax, Math.hypot(v.vx, v.vy));
        }
        return { vmax: vmax, def: v.def.vitesse_max, etat: v.etat, pelleDe: v.pelleDe,
                 // `typeDeRue` (le trafic) écarte toute fiche de fréquence nulle : la pelle n'y naît pas.
                 dansLeTrafic: L.B.defs.vehicules.some(function (t) { return t.slug === 'pelleteuse' && t.phase === 1 && t.frequence > 0; }) };
    """))
    assert 1.0 < r["vmax"] <= r["def"] + 1e-6, f"elle ne roule pas à sa vitesse de fiche : {r}"
    assert r["dansLeTrafic"] is False, "la pelle naît dans la rue"


def test_la_pelle_defonce_a_douze_kilometres_heure_et_ne_casse_ni_les_machines_ni_les_commerces(banc):
    """⚠️ Le seuil de vitesse pour défoncer une clôture se règle sur SA vitesse (trois quarts de la
    vitesse max, jamais plus que le seuil de la fiche) : la pelle, à 1,1 px/image, traverse ce que le
    camion — au même pas — ne fait que heurter. Et sa masse (3,3) reste sous tout ce qui ne doit
    jamais céder : les machines du chantier, les commerces ambulants.

    ⚠️ **UNE CLÔTURE NEUVE PAR ESSAI** : une clôture défoncée l'est pour de bon. Le premier montage
    essayait la pelle, puis le camion sur la même tuile — brisée, elle ne retenait plus personne, et le
    juge « le camion ne la défonce pas au pas » passait pour de mauvaises raisons."""
    r = banc(_juge(PELLE + """
        L.Jeu.commencer();
        const c = L.Monde.carte, ph = L.B.defs.conduite.physique, out = { seuil: ph.defonce_vitesse_min };
        // Des clôtures (solidité 3 ou 4), pas des meubles, dont tout le voisinage — de quoi loger un
        // camion — est du sol ou d'autres clôtures : « tout ou rien », une façade touchée l'arrêterait.
        const cibles = [];
        for (let ty = 3; ty < c.h - 3 && cibles.length < 6; ty++) {
            for (let tx = 4; tx < c.w - 4 && cibles.length < 6; tx++) {
                const s = L.Monde.solidite(tx, ty);
                let net = (s === 3 || s === 4) && !L.Monde.estMeuble(tx, ty) && L.Monde.solidite(tx - 1, ty) === 0 && L.Monde.solidite(tx - 2, ty) === 0;
                for (let dx = -3; dx <= 1 && net; dx++) for (let dy = -1; dy <= 1 && net; dy++) {
                    const v = L.Monde.solidite(tx + dx, ty + dy);
                    if (v === 1 || v === 2 || (v !== 0 && v !== 3 && v !== 4)) net = false;
                }
                // À l'écart des précédentes : on ne défonce pas la voisine d'une clôture déjà brisée.
                if (net && cibles.every(function (q) { return Math.abs(q.tx - tx) > 6 || Math.abs(q.ty - ty) > 6; })) cibles.push({ tx: tx, ty: ty });
            }
        }
        out.nombre = cibles.length;
        poserLeJoueur(L, { x: (cibles[0].tx - 6) * 16, y: cibles[0].ty * 16 + 300 });
        let k = 0;
        const essai = function (slug, vitesse) {
            const cible = cibles[k++];
            const v = L.Vehicules.creer(slug, cible.tx * 16 - 4, cible.ty * 16 + 8, 0, { etat: 'roule', couleur: '#e8b33c' });
            L.Entites.indexer();
            v.vitesse = vitesse; v.vx = vitesse; v.vy = 0;
            const casse = L.Vehicules.defoncerDevant(v, cible.tx * 16 + 2, cible.ty * 16 + 8);
            return { casse: casse, garde: casse ? Math.hypot(v.vx, v.vy) / vitesse : null };
        };
        out.pelle = essai('pelleteuse', 1.1);
        out.pelleLente = essai('pelleteuse', 0.6);
        out.camion = essai('camion', 1.1);
        out.camionRapide = essai('camion', 1.8);
        // Ce qu'elle ne doit jamais casser : tout décor qui `arrete` au-delà de la masse de l'autobus.
        const masse = L.Vehicules.vehiculeDef('pelleteuse').masse, autobus = L.Vehicules.vehiculeDef('autobus').masse;
        out.masse = masse; out.masseAutobus = autobus;
        out.trop_legere = Object.keys(L.DECORS).filter(function (k) {
            const f = L.DECORS[k];
            return f.arrete && !f.poussable && !f.rampe && f.arrete > autobus && f.arrete <= masse;
        });
        return out;
    """))
    assert r["nombre"] >= 4, f"trop peu de clôtures isolées pour juger : {r['nombre']}"
    assert r["pelle"]["casse"] is True, f"la pelle à 1,1 px/image ne traverse pas la clôture : {r['pelle']}"
    assert r["pelle"]["garde"] > 0.9, f"elle perd de la vitesse en passant : {r['pelle']}"
    assert r["pelleLente"]["casse"] is False, f"à 0,6 px/image, la pelle défonce encore : le seuil n'existe pas : {r['pelleLente']}"
    assert r["camionRapide"]["casse"] is True, f"le montage ne prouve rien : le camion lancé ne la défonce pas : {r['camionRapide']}"
    assert r["camion"]["casse"] is False, f"le camion, au même pas que la pelle, la défonce aussi : {r['camion']}"
    assert r["masse"] > r["masseAutobus"]
    assert r["trop_legere"] == [], f"la pelle déracinerait ce que l'autobus ne peut pas : {r['trop_legere']}"


# --- 9e vague : la cabine de la grue ------------------------------------------------------------

GRUE = """
  function chantierDeLaGrue(L) {
    return L.Chantiers.liste.findIndex(function (c) { return c.def.phases[3].machines.some(function (m) { return m.type === 'grue'; }); });
  }
  function grueDecor(L, ch) { return ch.machines.find(function (m) { return m.decor === 'grue'; }); }
  function auPiedDeLaGrue(L, d) {
    const j = L.B.joueur;
    j.x = d.x - 20; j.y = d.y + 2; j.face = 'droite'; j.angle = 0; j.vx = 0; j.vy = 0; j.dansVehicule = null; j.dessine = true; j.manege = null;
    L.Entites.indexer();
    return j;
  }
  // La cabine : monter, avec ACTION et le stick simulés (le banc n'appelle pas `Entree.debutImage`).
  function monterEnCabine(L, i) {
    L.Chantiers.appliquer(i, 3);
    const ch = L.Chantiers.liste[i], d = grueDecor(L, ch), j = auPiedDeLaGrue(L, d);
    L.Missions.interagir(j);
    return { ch: ch, d: d, j: j };
  }
"""


def test_on_monte_dans_la_cabine_de_la_grue(banc):
    r = banc(_juge(GRUE + """
        L.Jeu.commencer();
        const i = chantierDeLaGrue(L), ch = L.Chantiers.liste[i];
        L.Chantiers.appliquer(i, 3);
        L.B.partie.heure = 0.5;
        const d = grueDecor(L, ch), j = auPiedDeLaGrue(L, d), out = {};
        out.pres = !!L.Chantiers.grueSousLaMain(j); out.invite = L.Chantiers.inviteGrue(j);
        j.x = d.x - 200; out.loin = L.Chantiers.grueSousLaMain(j); j.x = d.x - 20;
        j.face = 'gauche'; j.angle = Math.PI; out.dos = L.Chantiers.grueSousLaMain(j); j.face = 'droite'; j.angle = 0;
        d.brise = true; out.brisee = L.Chantiers.grueSousLaMain(j); d.brise = false;
        L.Missions.majInvite(j); out.inviteHud = L.B.invite;
        out.action = L.Missions.interagir(j);
        out.manege = j.manege && j.manege.quoi; out.dessine = j.dessine; out.auMat = Math.hypot(j.x - d.x, j.y - d.y) < 8;
        out.pose = d.poseManuelle;
        // La foire ne l'éjecte pas : ce n'est pas un manège, elle ne le connaît pas.
        for (let k = 0; k < 5; k++) L.Foire.maj();
        out.toujoursDedans = !!(j.manege && j.manege.quoi === 'grue');
        // Dedans, on ne monte pas dans autre chose ni ne rentre par une deuxième pression.
        out.doubleMonte = L.Chantiers.grueSousLaMain(j);
        return out;
    """))
    assert r["pres"] and r["invite"] == "MONTER : GRUE", r
    assert r["loin"] is None and r["dos"] is None and r["brisee"] is None, r
    assert r["inviteHud"] == "MONTER : GRUE", f"le HUD ne promet pas ce qu'ACTION fait : {r['inviteHud']}"
    assert r["action"] is True and r["manege"] == "grue" and r["dessine"] is False and r["auMat"], r
    assert isinstance(r["pose"], (int, float)), "la grue ne garde pas sa pose"
    assert r["toujoursDedans"], "la foire a éjecté le joueur de la cabine"
    assert r["doubleMonte"] is None


def test_la_fleche_suit_le_stick_et_action_redescend(banc):
    """Le stick dose la vitesse et donne le sens ; à zéro, la flèche ne bouge pas ; ACTION redescend et la
    grue reprend SON travail (elle ne garde pas la pose du pilote)."""
    r = banc(_juge(GRUE + """
        L.Jeu.commencer();
        const i = chantierDeLaGrue(L);
        L.B.partie.heure = 0.5;
        const c = monterEnCabine(L, i), d = c.d, j = c.j, f = L.DECORS.grue, out = { variantes: f.variantes };
        const pivoter = function (x, images) {
            L.Entree.axe.x = x;
            const p0 = d.poseManuelle;
            for (let k = 0; k < images; k++) { L.B.t++; L.Chantiers.maj(); }
            return d.poseManuelle;
        };
        const depart = d.poseManuelle;
        out.droite = pivoter(1, 30);
        const apresDroite = d.poseManuelle;
        out.gauche = pivoter(-1, 30);
        out.retour = d.poseManuelle;
        out.moitie = (function () { const a = d.poseManuelle; pivoter(0.5, 30); return (d.poseManuelle - a + f.variantes) % f.variantes; })();
        out.immobile = (function () { const a = d.poseManuelle; pivoter(0, 60); return d.poseManuelle - a; })();
        out.depart = depart; out.apresDroite = apresDroite;
        out.entier = Number.isInteger(d.poseManuelle) && d.poseManuelle >= 0 && d.poseManuelle < f.variantes;
        // ⚠️ La pression qui a fait monter ne fait pas descendre : à l'image même de la montée, ACTION
        // (encore « neuve ») est dépensée.
        const neuf = L.Entree.neuf;
        L.B.t = c.j.manege.monteT;
        L.Entree.neuf = function (a) { return a === 'action'; };
        L.Chantiers.maj();
        out.memeImage = !!(j.manege && j.manege.quoi === 'grue');
        // ACTION, l'image d'après : on redescend — et la grue reprend son travail TOUT DE SUITE.
        L.B.t++; L.Chantiers.maj();
        L.Entree.neuf = neuf;
        out.descendu = { manege: j.manege, dessine: j.dessine, poseLibre: d.poseManuelle === undefined, auPied: Math.hypot(j.x - d.x, j.y - d.y) < 30 };
        L.Entree.axe.x = 0;
        return out;
    """))
    v = r["variantes"]
    # 30 images à 0,18 pose : 5,4 poses, lues 5 (la pose est un entier).
    assert (r["apresDroite"] - r["depart"]) % v == 5, f"pleine vitesse à droite : {r}"
    assert (r["retour"] - r["depart"]) % v in (0, v - 1, 1), f"à gauche, la flèche ne revient pas : {r}"
    assert r["moitie"] in (2, 3), f"le stick à mi-course ne donne pas la moitié de la vitesse : {r}"
    assert r["immobile"] == 0, f"le stick à zéro tourne encore la flèche : {r}"
    assert r["entier"], "la pose n'est pas un entier de 0 à 15"
    assert r["memeImage"], "la pression qui a fait monter a aussi fait descendre"
    assert r["descendu"]["manege"] is None and r["descendu"]["dessine"] is True, r["descendu"]
    assert r["descendu"]["poseLibre"], "la grue garde la pose de son pilote : elle ne reprend pas son travail"
    assert r["descendu"]["auPied"]


def test_la_cabine_lache_quand_le_pilote_meurt_ou_sort(banc):
    r = banc(_juge(GRUE + """
        L.Jeu.commencer();
        const i = chantierDeLaGrue(L);
        L.B.partie.heure = 0.5;
        const c = monterEnCabine(L, i), d = c.d, j = c.j, out = {};
        j.vivant = false;
        L.Chantiers.maj();
        out.mort = { manege: j.manege, dessine: j.dessine, poseLibre: d.poseManuelle === undefined };
        j.vivant = true;
        // `Foire.descendre` lâche `j.manege` sans un mot : la grue reprend quand même son travail.
        const c2 = monterEnCabine(L, i);
        L.Foire.descendre(j, true);
        L.Chantiers.maj();
        out.foire = { manege: j.manege, poseLibre: c2.d.poseManuelle === undefined };
        return out;
    """))
    assert r["mort"] == {"manege": None, "dessine": True, "poseLibre": True}, r["mort"]
    assert r["foire"] == {"manege": None, "poseLibre": True}, r["foire"]


def test_la_grue_pilotee_se_dessine_a_la_pose_qu_on_lui_donne(banc):
    """`Entites.dessiner` lit `poseManuelle` avant l'horloge du décor — de jour comme de nuit."""
    r = banc(_juge(GRUE + """
        L.Jeu.commencer();
        const i = chantierDeLaGrue(L);
        const c = monterEnCabine(L, i), d = c.d;
        const cles = [];
        const cuire = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle) { cles.push(cle); return cuire.apply(L.Atlas, arguments); };
        const ctx = new Proxy({}, { get: function (t, k) { return function () {}; }, set: function () { return true; } });
        L.Monde.centrerCamera(d.x, d.y - 30);
        const dessin = function (heure, pose) {
            L.B.partie.heure = heure;
            d.poseManuelle = pose; cles.length = 0;
            L.Entites.dessiner(ctx, L.B.cam);
            return cles.filter(function (k) { return k.indexOf('decor|grue|') === 0; });
        };
        const out = { jour: dessin(0.5, 7), nuit: dessin(0.95, 11) };
        L.Atlas.cuirePeintre = cuire;
        return out;
    """))
    assert r["jour"] and set(r["jour"]) == {"decor|grue|7"}, r
    assert r["nuit"] and set(r["nuit"]) == {"decor|grue|11"}, f"la nuit, la grue pilotée retombe à sa pose de repos : {r}"
