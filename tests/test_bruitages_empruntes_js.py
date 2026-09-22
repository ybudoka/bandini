"""Des bruitages déjà payés, là où le jeu n'avait que des oscillateurs — ou rien.

Martin (22 sept. 2026) : « prends des effets spéciaux existants pour les utiliser
aux endroits utiles avant d'en générer ». L'API ElevenLabs n'a pas de
bibliothèque d'effets à fouiller et le quota du mois est à sec : on emprunte les
échantillons de `static/audio/`, sans un octet de plus au seau.

- le tiroir-caisse (`argent`) à CHAQUE achat : `payer` le joue, une fois ;
- le décor qui cède s'entend, par sa matière (`casse`, `pelle`, `bouteille`) ;
- le maillet de la foire prend le coup de bâton (`batte`), la passe du pistolet
  à peinture le souffle de l'extincteur, coupé court ;
- les refus qui ne se disaient qu'à l'écrit jouent le refus (`erreur`).
"""


def _espion(nom):
    """Du JS qui compte les appels de `Son.SFX[nom]` dans `compte[nom]`, sans
    toucher au son."""
    return """(function () {
        const vrai = L.Son.SFX.%(n)s;
        L.Son.SFX.%(n)s = function () { compte.%(n)s = (compte.%(n)s || 0) + 1; return vrai.apply(null, arguments); };
    })();""" % {"n": nom}


def test_payer_fait_sonner_le_tiroir_caisse_une_fois(banc):
    """Le billet de foire, le métro, l'amende, l'hôpital… payaient en silence :
    seuls certains appelants jouaient `argent` eux-mêmes. Maintenant `payer` le
    joue — et ceux qui le rejouaient derrière ne le font plus (un café sonnait
    DEUX tiroirs-caisses)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const compte = {};
        %s
        L.B.partie.argent = 200;
        const avant = compte.argent || 0;
        L.Missions.payer(12, 'MÉTRO');
        const unAchat = (compte.argent || 0) - avant;
        L.Missions.payer(0, 'RIEN');
        const gratuit = (compte.argent || 0) - avant - unAchat;
        L.B.partie.argent = 1;
        const refuse = L.Missions.payer(50, 'TROP CHER');
        const refus = (compte.argent || 0) - avant - unAchat - gratuit;
        // Un café au kiosque : `payer` puis tout le reste, et UN seul tiroir.
        const j = L.B.joueur;
        L.B.partie.heure = 0.4;
        L.B.partie.argent = 200;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'cafe'; })[0];
        j.x = etal.x; j.y = etal.y + 22;
        L.Entites.regarder(j, 0, -1);
        L.Entites.indexer();
        const n = compte.argent || 0;
        const achat = L.Missions.interagir(j);
        return { unAchat: unAchat, gratuit: gratuit, refuse: refuse, refus: refus,
                 achat: achat, cafe: (compte.argent || 0) - n, paye: 200 - L.B.partie.argent };
    }""" % _espion("argent"))
    assert r["unAchat"] == 1, "payer ne fait pas sonner le tiroir-caisse : %s" % r
    assert r["gratuit"] == 0, "payer 0 $ fait sonner la caisse : %s" % r
    assert r["refuse"] is False and r["refus"] == 0, "un achat refusé fait sonner la caisse : %s" % r
    assert r["achat"] is True and r["paye"] > 0, "le café ne s'achète plus : %s" % r
    assert r["cafe"] == 1, "un café fait sonner %d tiroirs-caisses : %s" % (r["cafe"], r)


def test_un_decor_qui_cede_s_entend_par_sa_matiere(banc, paquet):
    """Un banc qu'on défonce sonnait comme rien : de la poussière, en silence.
    Le bois casse (`casse`), le métal sonne (`pelle`), le verre éclate
    (`bouteille`) — et le buisson, lui, n'a que sa poussière. On juge le
    FICHIER parti (le gain de sa fiche), pas seulement l'appel."""
    volumes = {e["slug"]: e["volume"] for e in paquet["audio"]["echantillons"]}
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const j = L.B.joueur, ctx = L.Son.contexte;
        const rendus = [];
        const vrai = L.Son.SFX.bris;
        L.Son.SFX.bris = function (d) { const s = vrai.apply(null, arguments); rendus.push(s); return s; };
        function casser(sorte) {
            const e = L.B.entites.find(function (q) { return q.type === 'decor' && q.decor === sorte && !q.brise; });
            if (!e) return { absent: sorte };
            j.x = e.x + 30; j.y = e.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
            L.B.t += 1;                     // une image neuve : un bris par image
            rendus.length = 0;
            const n = ctx.sources.length;
            L.Entites.briser(e);
            const g = ctx.sources.slice(n).filter(function (s) { return s.__demarree && s.buffer; })
                .map(function (s) { return s.__vers[0].gain.value; });
            return { slug: rendus[0] === undefined ? 'pas appele' : rendus[0], gains: g };
        }
        const r = { banc: casser('banc'), lampadaire: casser('lampadaire'), buisson: casser('buisson') };
        // Loin de l'écran : muet.
        const loin = L.B.entites.find(function (q) { return q.type === 'decor' && q.decor === 'banc' && !q.brise; });
        j.x = loin.x + 3000; j.y = loin.y; L.Monde.centrerCamera(j.x, j.y);
        L.B.t += 1; rendus.length = 0;
        L.Entites.briser(loin);
        r.loin = rendus.length;
        // Six décors dans la même image (l'explosion d'un char) : un seul bris.
        const tas = L.B.entites.filter(function (q) { return q.type === 'decor' && q.decor === 'banc' && !q.brise; }).slice(0, 6);
        j.x = tas[0].x; j.y = tas[0].y; L.Monde.centrerCamera(j.x, j.y);
        L.B.t += 1; rendus.length = 0;
        tas.forEach(function (e) { e.x = j.x; e.y = j.y; });
        tas.forEach(function (e) { L.Entites.briser(e); });
        r.six = rendus.filter(function (s) { return s; }).length;
        r.muettes = ctx.sourcesMuettes();
        return r;
    }""")
    assert r["banc"]["slug"] == "casse", "un banc qui casse ne sonne pas le bois : %s" % r["banc"]
    # À 30 px du joueur : le fichier de la fiche, un peu moins fort (`Son.depuis`).
    assert r["banc"]["gains"] and 0.8 * volumes["casse"] < r["banc"]["gains"][0] < volumes["casse"], (
        "le bris du banc ne joue pas le fichier `casse`, dosé à la distance : %s" % r["banc"])
    assert r["lampadaire"]["slug"] == "pelle", "un lampadaire qui tombe ne sonne pas le métal : %s" % r
    assert r["lampadaire"]["gains"] and 0.8 * volumes["pelle"] < r["lampadaire"]["gains"][0] < volumes["pelle"], (
        "le lampadaire ne joue pas le fichier `pelle` : %s" % r["lampadaire"])
    assert r["buisson"]["slug"] is None and r["buisson"]["gains"] == [], (
        "un buisson qui cède craque comme du bois : %s" % r["buisson"])
    assert r["loin"] == 0, "on entend un décor casser hors de l'écran"
    assert r["six"] == 1, "six décors dans la même image sonnent %d fois" % r["six"]
    assert r["muettes"] == 0


def test_le_maillet_prend_le_baton_et_le_pistolet_le_souffle_de_l_extincteur(banc, paquet):
    """Deux sons qui n'étaient que des oscillateurs empruntent un fichier payé.
    La passe du pistolet à peinture ne dure que 0,4 s : l'extincteur est une
    boucle de deux secondes, elle est COUPÉE (en fondu, pas net)."""
    volumes = {e["slug"]: e["volume"] for e in paquet["audio"]["echantillons"]}
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const ctx = L.Son.contexte;
        function ecoute(effet) {
            const n = ctx.sources.length, t0 = ctx.currentTime;
            L.Son.SFX[effet]();
            const s = ctx.sources.slice(n).filter(function (x) { return x.__demarree && x.buffer; });
            return s.map(function (x) {
                const g = x.__vers[0].gain;
                return { gain: g.value, arret: x.__arretT === undefined ? null : x.__arretT - t0,
                         fondu: (g.__courbes || []).length };
            });
        }
        return { maillet: ecoute('maillet'), pistolet: ecoute('pistolet_peinture'),
                 muettes: ctx.sourcesMuettes() };
    }""")
    assert len(r["maillet"]) == 1 and abs(r["maillet"][0]["gain"] - volumes["batte"]) < 0.02, (
        "le maillet ne joue pas le coup de bâton : %s" % r["maillet"])
    p = r["pistolet"]
    assert len(p) == 1 and abs(p[0]["gain"] - volumes["extincteur"] * 0.5) < 0.02, (
        "le pistolet à peinture ne joue pas le souffle de l'extincteur à mi-volume : %s" % p)
    assert p[0]["arret"] is not None and p[0]["arret"] <= 0.45, "la passe dure toute la boucle : %s" % p
    assert p[0]["fondu"] == 1, "la passe est coupée net, sans fondu : %s" % p
    assert r["muettes"] == 0


def test_les_refus_ecrits_jouent_aussi_le_refus(banc):
    """« RIEN À ACCROCHER DERRIÈRE », « PLUS TARD », la fontaine sèche… ne se
    disaient qu'à l'écrit, quand le reste du jeu joue `erreur` pour un refus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const compte = {};
        %s
        const j = L.B.joueur;
        // La remorqueuse, rien derrière elle.
        const v = L.Vehicules.creer('remorqueuse', j.x + 4000, j.y);
        const n = compte.erreur || 0;
        const accroche = L.Vehicules.basculerCrochet(v);
        return { accroche: accroche, crochet: (compte.erreur || 0) - n, def: !!(v && v.def && v.def.crochet) };
    }""" % _espion("erreur"))
    assert r["def"], "la remorqueuse n'a plus de crochet : le juge ne juge rien"
    assert r["accroche"] is False
    assert r["crochet"] == 1, "« RIEN À ACCROCHER » ne joue pas le refus : %s" % r
