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
        const fille = o.poser('racoleuse', 40, 0);
        o.frame(2);
        const premiere = dits.length;
        fille.bulle = null;
        o.frame(600);                          // dix secondes : rien de neuf
        const apresDixSecondes = dits.length;
        const bulleApres = !!fille.bulle;
        // Elle fuit (un coup a cote, une sirene) : plus un mot, meme reposee.
        fille.accosteT = -99999; fille.etat = 'fuit'; fille.minuterie = 600;
        o.frame(3);
        return { premiere: premiere, apresDixSecondes: apresDixSecondes, bulleApres: bulleApres,
                 enFuite: dits.length, bulleEnFuite: !!fille.bulle };
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
    mot de femme — et la Brume ne se met pas devant elle quand elle n'est pas la."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ESPION + """
        o.poser('passante', 20, 0);
        o.frame(3);
        return { dits: dits };
    }""")
    assert [d["genre"] for d in r["dits"]] == ["femme"], r["dits"]
    assert r["dits"][0]["slug"] is None, "un passant tire sa replique au hasard, comme avant"
