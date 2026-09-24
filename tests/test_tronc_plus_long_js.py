"""« Des missions plus longues » (Martin, 22 sept. 2026) — le tronc m4, m5, m6, m97, JOUÉ au banc.

Chacune a gagné des étapes (un détour à l'autre bout de la ville, une poursuite, une bagarre, un
retour), et chaque étape neuve a sa réplique `pendant`. Les juges de structure disent que c'est
câblé ; ici, chaque mission se joue de la poignée de main (ou du `parler` au donneur) à la prime,
étape par étape et DANS L'ORDRE — les étapes neuves comprises, chacune par ce qui l'accomplit en jeu :
le char qu'on conduit jusqu'au lieu, les hommes qui ARRIVENT de loin et qu'on couche, le fuyard
qu'on rattrape et la caisse qu'on ramasse, les poches vidées par-derrière, le donneur rejoint.
Les trajets sont téléportés (le banc n'a pas de pilote) ; les étoiles des `semer` d'avant ce passage
tombent à la main, comme dans `test_cinq_missions_js.py`.
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function boite(L) {
    const c = L.B.cinema, l = c && c.lignes[Math.max(0, c.i)];
    return l ? { partie: c.partie, qui: l.qui, slug: l.slug, telephone: l.telephone } : null;
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function heure(L, nuit) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && L.Monde.estNuit(h) !== nuit; k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h;
  }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push({ montant: montant, raison: raison || null }); return vrai.apply(null, arguments); };
    return liste;
  }
  function hommes(L, etape) {
    const j = L.B.joueur;
    return L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === etape && e.vivant; })
      .map(function (e) { return { e: e, d: Math.round(Math.hypot(e.x - j.x, e.y - j.y)) }; });
  }
  // Une image, puis la réplique `pendant` qu'elle ouvre (le cas échéant), relevée et fermée.
  function pas(L, o, n) {
    let b = null;
    for (let k = 0; k < (n || 3); k++) { o.frame(1); if (!b && L.B.cinema) b = boite(L); fermer(L); }
    return b;
  }
  // Le char de la mission au pixel d'un lieu, le joueur au volant, arrêté.
  function garer(L, v, l) {
    const j = L.B.joueur;
    v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
  }
  function ici(L, l) { const j = L.B.joueur; j.x = l.x; j.y = l.y; L.Entites.indexer(); }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) o.frame(1); passer(L, o); }
"""


def test_m4_le_lunch_du_sergent_la_fourriere_les_cravates_puis_les_cles(banc):
    """Bouchard, au casse-croûte (son alibi est le `pendant` de l'objectif 0 : le moteur ne le dit pas
    encore après une intro, ce juge ne l'attend pas) ; de nuit, l'auto-patrouille au poste, Ti-Guy derrière ; semée, on la mène à la fourrière (à l'autre
    bout de la ville) pour ses plaques ; larguée au garage, deux Cravates arrivent les poings nus pour
    la prendre ; couchés, on rapporte les clés au casse-croûte : 400 $."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3']);
        const argent = paiements(L);
        heure(L, false);
        o.entrer(M.carte.portes.find(function (p) { return p.lieu === 'casse_croute'; }));
        const parle = L.Histoire.parler('bouchard');
        passer(L, o);
        pas(L, o, 5);
        o.sortir();
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Au poste, de nuit.
        const poste = L.Histoire.lieu('poste');
        ici(L, poste); o.frame(3);
        out.jour = { etape: etape(L), attend: B.mission.attend };
        heure(L, true);
        ici(L, poste);
        pas(L, o);
        out.poste = etape(L);
        // 1. L'auto-patrouille.
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        out.tiGuy = pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles, escorte: !!B.mission.escorte };
        // 2. Semée (le banc ne pilote pas une poursuite : les étoiles tombent à la main).
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        out.fourriere = { pendant: pas(L, o), etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                          gps: (L.Histoire.cible() || {}).nom || null };
        // 3. À la fourrière, au volant : on n'y descend pas.
        const f = L.Histoire.lieu('fourriere'), g = L.Histoire.lieu('garage');
        out.loin = Math.round(Math.hypot(f.x - poste.x, f.y - poste.y) / L.TT);
        garer(L, v, f);
        out.garage = { etape: etape(L), dans: j.dansVehicule === v };
        pas(L, o);
        out.garage.etape = etape(L);
        // 4. Larguée au garage.
        garer(L, v, L.Histoire.lieuDeLivraison('garage'));
        const tiGuy2 = pas(L, o);
        const deux = hommes(L, 5);
        out.cravates = { etape: etape(L), pendant: tiGuy2, dehors: !j.dansVehicule,
                         arrivent: deux.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme || null, vie: h.e.vieMax }; }) };
        // 5. On les couche.
        deux.forEach(function (h) { L.Entites.assommer(h.e); });
        const cles = pas(L, o);
        out.cles = { etape: etape(L), pendant: cles, ligne: L.Histoire.ligneObjectif() };
        // 6. Les clés, au casse-croûte.
        ici(L, L.Histoire.lieu('casse_croute'));
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m4; out.ami = !!B.partie.sergentAmi;
        out.argent = argent.map(function (a) { return a.montant; });
        out.garageLoin = Math.round(Math.hypot(f.x - g.x, f.y - g.y) / L.TT);
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m4", r
    assert r["jour"] == {"etape": 0, "attend": "ATTENDS LA NUIT"}
    assert r["poste"] == 1
    assert r["tiGuy"] and r["tiGuy"]["qui"] == "ti_guy", r["tiGuy"]
    assert r["semer"] == {"etape": 2, "etoiles": 2, "escorte": True}
    f = r["fourriere"]
    assert f["etape"] == 3 and f["ligne"].startswith("PASSE PAR LA FOURRIÈRE"), f
    assert f["pendant"] and f["pendant"]["qui"] == "bouchard" and f["pendant"]["telephone"] is True, f
    assert f["gps"] == "Fourrière municipale", "le GPS mène à la fourrière"
    assert r["loin"] >= 150 and r["garageLoin"] >= 150, f"un vrai détour : {r['loin']} et {r['garageLoin']} tuiles"
    assert r["garage"] == {"etape": 4, "dans": True}, "à la fourrière, on reste au volant ; ensuite, le garage"
    c = r["cravates"]
    assert c["etape"] == 5 and c["dehors"], c
    assert c["pendant"] and c["pendant"]["qui"] == "ti_guy", c
    assert len(c["arrivent"]) == 2, c
    for h in c["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
        assert h["arme"] is None and h["vie"] == 70, "deux petits, les poings nus"
    k = r["cles"]
    assert k["etape"] == 6 and k["ligne"].startswith("RAPPORTE LES CLÉS"), k
    assert k["pendant"] and k["pendant"]["qui"] == "bouchard", k
    assert r["fait"] is True and r["ami"] is True and r["argent"] == [400]


def test_m5_la_chef_des_quais_la_caisse_des_cravates_file_puis_la_cantine(banc):
    """Josée : les trois coins, le chef ; puis leur trésorier file en char avec la caisse — on le
    rattrape (on le cabosse), un Cravate en descend avec elle, on le couche, on la ramasse ; la police
    semée, la caisse va derrière la cantine des Quais (à l'autre bout de la ville), puis la planque."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4']);
        const argent = paiements(L);
        o.entrer(M.carte.portes.find(function (p) { return p.lieu === 'bar'; }));
        const parle = L.Histoire.parler('josee');
        passer(L, o);
        pas(L, o);
        o.sortir();
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Les trois coins.
        hommes(L, 0).forEach(function (h) { L.Entites.assommer(h.e); });
        const chef = pas(L, o);
        out.chef = { etape: etape(L), pendant: chef };
        // 1. Le chef.
        const lui = B.mission.entites.find(function (e) { return e.chef; });
        ici(L, { x: lui.x - 30, y: lui.y });
        L.Entites.assommer(lui);
        const tresorier = pas(L, o);
        const v = B.mission.fuyard;
        out.fuyard = { etape: etape(L), pendant: tresorier, char: v ? v.slug : null, file: v ? v.fuite : null,
                       d: v ? Math.round(Math.hypot(v.x - j.x, v.y - j.y)) : null, ligne: L.Histoire.ligneObjectif() };
        // 2. On le rattrape : cabossé à mort, il s'arrête, et un Cravate en descend avec la caisse.
        o.frame(60);
        v.vie = Math.floor(v.vieMax * 0.4);
        o.frame(2);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        out.caisse = { tombe: !!B.mission.fuyardTombe, porteur: !!porteur, etat: porteur ? porteur.etat : null, etape: etape(L) };
        ici(L, { x: porteur.x - 20, y: porteur.y });
        L.Entites.assommer(porteur);
        o.frame(2);
        const c = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        out.caisse.parTerre = !!c;
        ici(L, c);
        pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        // 3. Semée.
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        const cantine = pas(L, o);
        out.cantine = { etape: etape(L), pendant: cantine, ligne: L.Histoire.ligneObjectif(),
                        loin: Math.round(Math.hypot(L.Histoire.lieu('cantine').x - L.Histoire.lieu('bar').x,
                                                    L.Histoire.lieu('cantine').y - L.Histoire.lieu('bar').y) / L.TT) };
        // 4. Derrière la cantine.
        ici(L, L.Histoire.lieu('cantine'));
        const soeur = pas(L, o);
        out.planque = { etape: etape(L), pendant: soeur };
        // 5. La planque.
        ici(L, L.Histoire.lieu('planque'));
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m5; out.bar = !!B.partie.proprietes.bar;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m5", r
    assert r["chef"]["etape"] == 1 and r["chef"]["pendant"]["qui"] == "josee", r["chef"]
    f = r["fuyard"]
    assert f["etape"] == 2 and f["ligne"].startswith("RATTRAPE LA CAISSE"), f
    assert f["pendant"] and f["pendant"]["qui"] == "josee" and f["pendant"]["telephone"] is True, f
    assert f["char"] == "auto" and f["file"] is True and f["d"] < 250, f"le trésorier file en char, d'à côté ({f})"
    k = r["caisse"]
    assert k["tombe"] and k["porteur"] and k["etat"] == "fuit" and k["etape"] == 2, k
    assert k["parTerre"], "couché, le porteur lâche la caisse"
    assert r["semer"] == {"etape": 3, "etoiles": 3}, "la caisse ramassée, la police"
    c = r["cantine"]
    assert c["etape"] == 4 and c["ligne"].startswith("CACHE LA CAISSE"), c
    assert c["pendant"] and c["pendant"]["qui"] == "josee", c
    assert c["loin"] >= 120, f"la cantine est à l'autre bout de la ville ({c['loin']} tuiles du bar)"
    assert r["planque"]["etape"] == 5 and r["planque"]["pendant"]["qui"] == "josee", r["planque"]
    assert r["fait"] is True and r["bar"] is True and r["argent"] == [800]


def test_m6_le_tour_du_proprietaire_le_pickpocket_le_piquet_puis_le_brouillard(banc):
    """Josée présente la ville : Ti-Paul (puis les poches de SON pickpocket, par-derrière), Lulu à la
    cantine, Raymonde (puis trois Boulonneux qui arrivent sur son piquet, poings nus), Ovila au phare
    (qui a vu une auto sans phares) — et on revient au Brouillard : 300 $ et quatre numéros."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5']);
        const argent = paiements(L);
        function porte(lieu) { return M.carte.portes.find(function (p) { return p.lieu === lieu; }); }
        function serrer(slug) {
            const b = { avant: etape(L), rendu: L.Histoire.parler(slug), boite: boite(L) };
            fermer(L);
            b.pendant = pas(L, o);
            b.apres = etape(L);
            return b;
        }
        o.entrer(porte('bar'));
        const parle = L.Histoire.parler('josee');
        passer(L, o);
        pas(L, o, 5);
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        o.sortir();
        // 0. Ti-Paul, dehors.
        const ti = L.Histoire.donneur('tipaul');
        ici(L, { x: ti.x - 16, y: ti.y });
        out.tipaul = serrer('tipaul');
        // 1. Son pickpocket, par-derrière (le patron de f07).
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        out.poches = { la: !!victime, argent: victime ? victime.argent : null, ligne: L.Histoire.ligneObjectif() };
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        out.poches.vole = L.Combat.pickpocket(j);
        out.poches.lulu = pas(L, o);
        out.poches.apres = etape(L);
        out.poches.vide = victime.argent;
        // 2. Lulu, dedans.
        o.entrer(porte('cantine'));
        out.lulu = serrer('lulu');
        o.sortir();
        // 3. Raymonde, dehors — puis les Boulonneux.
        const ray = L.Histoire.donneur('raymonde');
        ici(L, { x: ray.x - 16, y: ray.y });
        out.raymonde = serrer('raymonde');
        const trois = hommes(L, 4);
        out.piquet = { etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       arrivent: trois.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme || null, vie: h.e.vieMax, gang: h.e.gang }; }) };
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        out.piquet.pendant = pas(L, o);
        out.piquet.apres = etape(L);
        // 5. Ovila, dedans, au phare — à l'autre bout de la ville.
        o.entrer(porte('phare'));
        out.ovila = serrer('ovila');
        o.sortir();
        out.ligneRetour = L.Histoire.ligneObjectif();
        const phare = L.Histoire.lieu('phare'), bar = L.Histoire.lieu('bar');
        out.loin = Math.round(Math.hypot(phare.x - bar.x, phare.y - bar.y) / L.TT);
        // 6. Le Brouillard.
        ici(L, bar);
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m6;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m6", r
    t = r["tipaul"]
    assert t["rendu"] and t["boite"]["partie"] == "accueil" and t["boite"]["qui"] == "tipaul", t
    assert t["avant"] == 0 and t["apres"] == 1, t
    assert t["pendant"] and t["pendant"]["qui"] == "tipaul" and t["pendant"]["telephone"] is False, t
    p = r["poches"]
    assert p["la"] and p["argent"] > 0 and p["ligne"].startswith("VIDE LES POCHES DU PICKPOCKET"), p
    assert p["vole"] is True and p["vide"] == 0 and p["apres"] == 2, p
    assert p["lulu"] and p["lulu"]["qui"] == "tipaul", p
    lu = r["lulu"]
    assert lu["boite"]["qui"] == "lulu" and lu["avant"] == 2 and lu["apres"] == 3, lu
    ra = r["raymonde"]
    assert ra["boite"]["qui"] == "raymonde" and ra["avant"] == 3 and ra["apres"] == 4, ra
    assert ra["pendant"] and ra["pendant"]["qui"] == "raymonde" and ra["pendant"]["telephone"] is False, ra
    q = r["piquet"]
    assert q["etape"] == 4 and q["ligne"].startswith("REPOUSSE LES BOULONNEUX"), q
    assert len(q["arrivent"]) == 3, q
    for h in q["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
        assert h["arme"] is None and h["vie"] == 80, "les poings nus"
    assert q["apres"] == 5 and q["pendant"] and q["pendant"]["qui"] == "raymonde", q
    ov = r["ovila"]
    assert ov["boite"]["qui"] == "ovila" and ov["avant"] == 5 and ov["apres"] == 6, ov
    assert ov["pendant"] and ov["pendant"]["qui"] == "ovila", ov
    assert r["ligneRetour"].startswith("RETOURNE AU BROUILLARD")
    assert r["loin"] >= 200, f"du phare au Brouillard, l'autre bout de la ville ({r['loin']} tuiles)"
    assert r["fait"] is True and r["argent"] == [p["argent"], 300], "les poches du pickpocket, puis la prime"


def test_m97_marco_te_vend_les_chiens_le_phare_le_taxi_puis_marco_en_personne(banc):
    """Marco, au garage : « Tiens, les voilà » — quatre Cravates arrivent de loin dès la fin de l'intro (le
    « Rien de personnel » de Marco est le `pendant` de l'objectif 0 : pas encore dit après une intro, ce
    juge ne l'attend pas) ; couchés, cinq
    étoiles ; semées, Ovila appelle du phare (il se nomme : sa première réplique de la mission) ; au
    phare, le taxi repart, on le rattrape, on reprend la caisse ; puis on retourne voir Marco, et la
    fin se dit DEVANT lui."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01']);
        // `exige: {liberes: 3}` : trois districts libérés (la forme de `tenirExige`, test_missions_en_scene_js).
        B.partie.libere = ((L.Monde.carte.def && L.Monde.carte.def.districts) || []).map(function (q) { return q.slug; }).slice(0, 3);
        const argent = paiements(L);
        const marco = L.Histoire.donneur('marco');
        ici(L, { x: marco.x - 16, y: marco.y });
        const parle = L.Histoire.parler('marco');
        passer(L, o);
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Les chiens de Bouchard arrivent.
        pas(L, o, 5);
        const quatre = hommes(L, 0);
        out.chiens = { etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       arrivent: quatre.map(function (h) { return { d: h.d, etat: h.e.etat }; }) };
        quatre.forEach(function (h) { L.Entites.assommer(h.e); });
        const cours = pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles, pendant: cours };
        // 2. Semée.
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        const ovila = pas(L, o);
        out.phare = { etape: etape(L), pendant: ovila, ligne: L.Histoire.ligneObjectif(),
                      texte: L.B.defs.missions.find(function (m) { return m.slug === 'm97'; }).dialogue.pendant
                          .filter(function (l) { return l.qui === 'ovila'; }).map(function (l) { return l.texte; }) };
        // 3. Au phare, à l'autre bout de la ville.
        const phare = L.Histoire.lieu('phare'), garage = L.Histoire.lieu('garage');
        out.loin = Math.round(Math.hypot(phare.x - garage.x, phare.y - garage.y) / L.TT);
        ici(L, phare);
        const repart = pas(L, o);
        const v = B.mission.fuyard;
        out.taxi = { etape: etape(L), pendant: repart, char: v ? v.slug : null, file: v ? v.fuite : null,
                     d: v ? Math.round(Math.hypot(v.x - j.x, v.y - j.y)) : null };
        // 4. On le rattrape, on reprend la caisse.
        o.frame(60);
        v.vie = Math.floor(v.vieMax * 0.4);
        o.frame(2);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        ici(L, { x: porteur.x - 20, y: porteur.y });
        L.Entites.assommer(porteur);
        o.frame(2);
        const c = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        ici(L, c);
        const garageDit = pas(L, o);
        out.retour = { etape: etape(L), pendant: garageDit, ligne: L.Histoire.ligneObjectif() };
        // 5. Devant Marco.
        const m2 = L.Histoire.donneur('marco');
        ici(L, { x: m2.x - 16, y: m2.y });
        const fin = [];
        for (let k = 0; k < 400 && B.partie.mission; k++) o.frame(1);
        for (let n = 0; (B.scene || B.cinema) && n < 6000; n++) {
            o.frame(1);
            const b = boite(L);
            if (b && (!fin.length || fin[fin.length - 1].slug !== b.slug)) fin.push(b);
            if (B.cinema && n % 30 === 0) L.Histoire.suivante();
        }
        out.fin = fin;
        out.fait = !!B.partie.missionsFaites.m97;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m97", r
    c = r["chiens"]
    assert c["etape"] == 0 and c["ligne"].startswith("COUCHE LES CHIENS"), c
    assert len(c["arrivent"]) == 4, c
    for h in c["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
    s = r["semer"]
    assert s["etape"] == 1 and s["etoiles"] == 5 and s["pendant"] and s["pendant"]["qui"] == "marco", s
    p = r["phare"]
    assert p["etape"] == 2 and p["ligne"].startswith("VA AU PHARE"), p
    assert p["pendant"] and p["pendant"]["qui"] == "ovila" and p["pendant"]["telephone"] is True, p
    assert "Ovila" in p["texte"][0], "sa première réplique de la mission le nomme"
    assert r["loin"] >= 200, f"le phare est à l'autre bout de la ville ({r['loin']} tuiles du garage)"
    t = r["taxi"]
    assert t["etape"] == 3 and t["char"] == "taxi" and t["file"] is True and t["d"] < 250, t
    assert t["pendant"] and t["pendant"]["qui"] == "ovila", t
    rt = r["retour"]
    assert rt["etape"] == 4 and rt["ligne"].startswith("RETOURNE RÉGLER ÇA AVEC MARCO"), rt
    assert rt["pendant"] and rt["pendant"]["qui"] == "marco" and rt["pendant"]["telephone"] is True, rt
    assert [b["qui"] for b in r["fin"]] == ["marco"] * 3, r["fin"]
    assert not any(b["telephone"] for b in r["fin"]), f"la fin se dit devant lui : {r['fin']}"
    assert r["fait"] is True and r["argent"] == [150]
