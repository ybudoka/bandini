"""La fille de la Brume qui t'accoste (13 sept. 2026).

Demande de Martin : « la prostituée aussi doit parler, avec plusieurs
dialogues différents ». Elle ne disait jamais rien : `rumeurEtRepliques` saute
tout pieton qui a un `metier`, et elle en a un (`compagnie`). Ces juges
regardent ce que le navigateur fait — la bulle, la voix demandee, le repos —
en remplacant `Son.Voix.dire` par un carnet : le banc n'a pas d'oreille.
"""


def _brume(paquet):
    return [v for v in paquet["audio"]["voix"] if v["genre"] == "brume"]


ESPION = """
        const dits = [];
        L.Son.Voix.dire = function (genre, x, y, slug) { dits.push({ genre: genre, slug: slug || null }); return null; };
"""


def test_elle_t_accoste_quand_tu_passes_pres_de_son_coin(banc, paquet):
    """Une bulle avec une de SES repliques, et sa voix demandee sur le meme
    slug — jamais une replique de passante."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        """ + ESPION + """
        const j = L.B.joueur;
        const fille = o.poser('racoleuse', 40, 0);
        o.frame(3);
        return { metier: fille.metier, poste: !!fille.poste,
                 bulle: fille.bulle ? fille.bulle.texte : null, dits: dits,
                 regarde: fille.face };
    }""")
    textes = {v["texte"]: v["slug"] for v in _brume(paquet)}
    assert r["metier"] == "compagnie" and r["poste"] is True
    assert r["bulle"] in textes, f"pas une replique de la Brume : {r['bulle']!r}"
    brume = [d for d in r["dits"] if d["genre"] == "brume"]
    assert len(brume) == 1, r["dits"]
    assert brume[0]["slug"] == textes[r["bulle"]], "la voix ne dit pas ce que la bulle montre"
    assert not [d for d in r["dits"] if d["genre"] == "femme"], "elle ne dit pas « Excusez-moi »"


def test_plusieurs_dialogues_et_jamais_deux_fois_de_suite_le_meme(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        """ + ESPION + """
        const fille = o.poser('racoleuse', 40, 0);
        // ⚠️ La rue autour d'elle est VIDE : au terminus, une roulotte a cafe et son vendeur, Ti-Guy
        // et le figurant qui passe la poussent (la « separation »), et a plus de 48 px elle n'accoste
        // plus. Le juge tenait a l'endroit exact de la roulotte — deplacee de deux tuiles pour ne
        // plus boucher la porte du terminus (`app/devants.py`), la fille dérivait de 43 a 50 px.
        L.B.entites.filter(function (e) { return e !== fille && e.type === 'pieton' && Math.hypot(e.x - fille.x, e.y - fille.y) < 120; })
            .forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        const suite = [];
        for (let i = 0; i < 24; i++) {
            fille.accosteT = -99999; fille.bulle = null;
            o.frame(2);                        // ⚠️ jamais frame(1) : pas fixe et accumulateur
            suite.push(fille.bulle ? fille.bulle.texte : null);
        }
        return { suite: suite };
    }""")
    suite = r["suite"]
    assert all(suite), "une fois sans bulle"
    assert len(set(suite)) >= 3, f"toujours les memes mots : {set(suite)}"
    assert len(set(suite)) <= len(_brume(paquet))
    for a, b in zip(suite, suite[1:]):
        assert a != b, "la meme replique deux fois de suite"


def test_elle_se_repose_une_demi_minute_et_se_tait_quand_elle_fuit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(3);
        """ + ESPION + """
        // ⚠️ On compte les voix DE LA BRUME, pas toutes : la rue parle toute
        // seule — les passantes ont leurs repliques — et un bonjour de
        // trottoir passait pour une relance de la fille.
        const siennes = function () { return dits.filter(function (d) { return d.genre === 'brume'; }).length; };
        const fille = o.poser('racoleuse', 40, 0);
        o.frame(2);
        const premiere = siennes();
        fille.bulle = null;
        o.frame(600);                          // dix secondes : rien de neuf
        const apresDixSecondes = siennes();
        const bulleApres = !!fille.bulle;
        // Elle fuit (un coup a cote, une sirene) : plus un mot, meme reposee.
        fille.accosteT = -99999; fille.etat = 'fuit'; fille.minuterie = 600;
        o.frame(3);
        return { premiere: premiere, apresDixSecondes: apresDixSecondes, bulleApres: bulleApres,
                 enFuite: siennes(), bulleEnFuite: !!fille.bulle };
    }""")
    assert r["premiere"] == 1
    assert r["apresDixSecondes"] == 1 and r["bulleApres"] is False, "elle a repete avant la demi-minute"
    assert r["enFuite"] == 1 and r["bulleEnFuite"] is False, "elle accoste en fuyant"


def test_en_char_elle_ne_dit_rien(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ESPION + """
        const j = L.B.joueur;
        const fille = o.poser('racoleuse', 40, 0);
        j.dansVehicule = o.char('auto', 0, 0, 0);   // au volant, sans demarrer
        o.frame(3);
        return { dits: dits.length, bulle: !!fille.bulle };
    }""")
    assert r["dits"] == 0 and r["bulle"] is False


def test_une_passante_parle_toujours_comme_avant(banc):
    """Le chemin des passants n'a pas bouge : on frole une passante, elle dit un
    mot de femme — et la Brume ne se met pas devant elle quand elle n'est pas la.

    ⚠️ PARLER EST UNE CHANCE depuis M15 : la plupart des gens qu'on croise ne
    disent rien, parce qu'un passant qui parle chaque fois qu'on le frole rend
    huit repliques fatigantes bien avant qu'elles soient usees. Le juge met donc
    la chance a 1 : ce qu'il mesure, c'est le CHEMIN de la parole, pas le de.
    Le de, lui, se juge dans `test_moteur_js.py`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.defs.audio.parole.chance = 1;
        """ + ESPION + """
        o.poser('passante', 20, 0);
        o.frame(3);
        return { dits: dits };
    }""")
    assert [d["genre"] for d in r["dits"]] == ["femme"], r["dits"]
    assert r["dits"][0]["slug"] is None, "un passant tire sa replique au hasard, comme avant"


# ⚠️ LA NUIT QUI DURE (Martin, 21 sept. 2026, devant treize filles en grappe sur le
# quai : « il faudrait eviter qu'il y ait des attroupements comme ca »). La fille a
# un `metier`, donc `peupler` ne la compte pas dans la foule, et elle ne rentre
# jamais par une porte : chaque passant qui rentrait chez lui la nuit laissait sa
# place, et une chance sur cinq d'une fille de plus. Le banc rejoue cinq cents de
# ces places au meme endroit — la rue videe de ses flaneurs, puis `peupler`.
NUIT_QUI_DURE = """
        L.Jeu.commencer();
        L.graine(GRAINE);
        L.B.partie.heure = 0.05;
        const j = L.B.joueur;
        const zone = L.Monde.zoneA(j.x, j.y);
        function filles() {
            return L.B.entites.filter(function (e) { return e.type === 'pieton' && e.metier === 'compagnie' && e.vivant; });
        }
        function laRueSeVide() {
            for (let k = L.B.entites.length - 1; k >= 0; k--) {
                const e = L.B.entites[k];
                if (e.type === 'pieton' && !e.metier && !e.personnage && !e.mission) L.B.entites.splice(k, 1);
            }
            L.Entites.indexer();
        }
        function ecart(a, b) { return Math.hypot(a.poste.x - b.poste.x, a.poste.y - b.poste.y); }
"""


def test_la_nuit_la_brume_ne_fait_pas_d_attroupement(banc):
    """Toutes les filles restent : c'est le PLAFOND qu'on regarde. Quelques-unes
    dans la bulle — la Brume garde ses habituees — pas une grappe."""
    r = banc("""function (L, o) {""" + NUIT_QUI_DURE.replace("GRAINE", "7") + """
        for (let i = 1; i <= 500; i++) {
            laRueSeVide();
            L.B.t = i * 12;                    // `peupler` ne fait naitre qu'une image sur douze
            L.Entites.peupler();
        }
        const f = filles();
        let serre = null;
        f.forEach(function (a, i) { f.slice(i + 1).forEach(function (b) {
            const d = ecart(a, b); if (serre === null || d < serre) serre = d; }); });
        return { brume: !!(zone && zone.brume), nuit: L.Monde.estNuit(), filles: f.length, serre: serre };
    }""")
    assert r["brume"] and r["nuit"], f"le juge ne rejoue pas une nuit de Brume : {r}"
    assert r["filles"] >= 1, "la Brume n'a plus d'habituees"
    assert r["filles"] <= 3, f"{r['filles']} filles dans la bulle : un attroupement"
    assert r["serre"] is None or r["serre"] >= 160, f"deux coins a {r['serre']:.0f} px"


def test_chacune_son_coin(banc):
    """Une seule fille reste a la fois (la plus jeune) : le plafond ne mord
    jamais, et c'est l'ECART qu'on regarde. Aucune fille neuve ne prend son coin
    a moins de dix tuiles de celle qui est deja la."""
    r = banc("""function (L, o) {""" + NUIT_QUI_DURE.replace("GRAINE", "11") + """
        const serres = [];
        let naissances = 0;
        for (let i = 1; i <= 500; i++) {
            laRueSeVide();
            const avant = filles();
            L.B.t = i * 12;
            L.Entites.peupler();
            const neuves = filles().filter(function (e) { return avant.indexOf(e) < 0; });
            neuves.forEach(function (n) {
                naissances++;
                avant.forEach(function (a) { const d = ecart(n, a); if (d < 160) serres.push(Math.round(d)); });
            });
            if (neuves.length) avant.forEach(function (a) { L.B.entites.splice(L.B.entites.indexOf(a), 1); });
        }
        return { brume: !!(zone && zone.brume), nuit: L.Monde.estNuit(), naissances: naissances, serres: serres };
    }""")
    assert r["brume"] and r["nuit"], f"le juge ne rejoue pas une nuit de Brume : {r}"
    assert r["naissances"] >= 20, f"trop peu de filles pour juger l'ecart : {r['naissances']}"
    assert r["serres"] == [], f"des coins a moins de dix tuiles d'une autre : {r['serres']}"
