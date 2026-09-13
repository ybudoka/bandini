"""Le son, et surtout le silence qui ne se dit pas.

⚠️ Le probleme que ces tests gardent : un AudioContext naît « suspended » tant
que la page n'a recu aucun VRAI geste (clic, touche, toucher), et `resume()` est
alors refuse. Or l'API Manette ne compte PAS comme un geste. Depuis qu'on peut
commencer la partie au pad (0.16.0), un joueur a la manette traversait donc
toute la ville en silence, sans le moindre message — la panne de Martin, le
13 sept. 2026. Le jeu doit DIRE qu'il attend un geste.

⚠️ `o.frame(2)` apres chaque `o.pad(...)`, jamais `frame(1)` : la boucle a un pas
fixe et un accumulateur.
"""


def test_sans_audio_du_tout_le_jeu_tourne_et_le_dit(banc):
    """Le banc n'a pas d'AudioContext : le jeu doit tourner, muet, sans planter."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(30);
        return { etat: L.Son.etatSon(), attente: L.Son.enAttente(),
                 contexte: L.Son.contexte, tourne: L.B.etat };
    }""")
    assert r["etat"] == "absent"
    assert r["attente"] is False, "pas d'audio du tout n'est pas une attente : rien ne la reglera"
    assert r["contexte"] is None
    assert r["tourne"] == "jeu"


def test_un_contexte_suspendu_se_dit_en_attente(banc):
    r = banc("""function (L, o) {
        o.brancherAudio(false);          // le navigateur refuse : aucun geste
        L.Son.sonder();
        const apres = { etat: L.Son.etatSon(), attente: L.Son.enAttente(),
                        brut: L.Son.contexte.state };
        L.Jeu.commencer(); o.frame(30);
        return { apres: apres, encore: L.Son.etatSon() };
    }""")
    assert r["apres"]["etat"] == "attente"
    assert r["apres"]["attente"] is True
    assert r["apres"]["brut"] == "suspended"
    assert r["encore"] == "attente", "jouer ne debloque rien : il faut un geste"


def test_un_contexte_qui_demarre_est_actif(banc):
    r = banc("""function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        L.Jeu.commencer(); o.frame(30);
        return { etat: L.Son.etatSon(), attente: L.Son.enAttente(), pret: L.Son.pret() };
    }""")
    assert r["etat"] == "actif"
    assert r["attente"] is False
    assert r["pret"] is True


def test_le_son_coupe_ne_se_confond_pas_avec_le_son_retenu(banc):
    """Deux silences tres differents : l'un est un choix, l'autre une panne."""
    r = banc("""function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        const avant = L.Son.etatSon();
        L.B.options.muet = true; L.Son.majVolume();
        return { avant: avant, apres: L.Son.etatSon(), attente: L.Son.enAttente() };
    }""")
    assert r["avant"] == "actif"
    assert r["apres"] == "coupe"
    assert r["attente"] is False, "le son coupe n'attend pas un geste : c'est voulu"


def test_commencer_a_la_manette_previent_qu_il_manque_un_geste(banc):
    """La panne de Martin, bout en bout : il demarre au pad, donc sans geste."""
    r = banc("""function (L, o) {
        o.brancherAudio(false);
        L.Son.sonder();
        const auTitre = L.B.etat;
        o.pad([0, 0], [1]); o.frame(2);      // bouton ACTION : la partie commence
        o.pad(null); o.frame(2);
        return { auTitre: auTitre, etat: L.B.etat, msg: L.B.msg, son: L.Son.etatSon() };
    }""")
    assert r["auTitre"] == "titre"
    assert r["etat"] == "jeu", "la manette doit quand meme pouvoir commencer la partie"
    assert r["son"] == "attente"
    assert "TOUCHE L'ECRAN" in (r["msg"] or ""), "le silence doit se dire a l'ecran"


def test_commencer_a_la_manette_ne_previent_pas_quand_le_son_marche(banc):
    r = banc("""function (L, o) {
        o.brancherAudio(true);
        L.Son.sonder();
        o.pad([0, 0], [1]); o.frame(2);
        o.pad(null); o.frame(2);
        return { etat: L.B.etat, msg: L.B.msg || '', son: L.Son.etatSon() };
    }""")
    assert r["etat"] == "jeu"
    assert r["son"] == "actif"
    assert "TOUCHE L'ECRAN" not in r["msg"], "ne pas crier au loup quand le son sort"


def test_l_avis_de_l_ecran_titre_se_montre_et_s_efface(banc):
    """Le bandeau du titre suit l'etat : visible en attente, cache des que ca marche."""
    r = banc("""function (L, o) {
        o.brancherAudio(false);
        L.Son.sonder(); L.Hud.majAvisSon();
        const avis = o.doc.getElementById('avis-son');
        const enAttente = avis.hidden;
        o.brancherAudio(true);               // comme si un geste arrivait
        L.Son.contexte.state = 'running';
        L.Hud.majAvisSon();
        return { enAttente: enAttente, apres: avis.hidden };
    }""")
    assert r["enAttente"] is False, "en attente, le bandeau doit etre VISIBLE (hidden = false)"
    assert r["apres"] is True, "des que le son sort, le bandeau disparaît"


def test_les_options_montrent_l_etat_du_son(banc):
    r = banc("""function (L, o) {
        o.brancherAudio(false);
        L.Son.sonder();
        L.Jeu.commencer();
        o.pad([0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]); o.frame(2);   // PAUSE
        o.pad(null); o.frame(2);
        const pause = L.B.menu && L.B.menu.titre;
        // OPTIONS est le 3e item du menu pause : on descend puis on valide.
        const items = L.B.menu.items.map(function (i) { return i.libelle; });
        const iOptions = items.indexOf('OPTIONS');
        L.B.menu.curseur = iOptions;
        o.pad([0, 0], [1]); o.frame(2); o.pad(null); o.frame(2);
        const m = L.B.menu;
        const ligne = m.items.filter(function (i) { return i.libelle === 'SON'; })[0];
        return { pause: pause, titre: m.titre, curseur: m.curseur,
                 detail: ligne && ligne.detail, actif: ligne && ligne.actif };
    }""")
    assert r["pause"] == "PAUSE"
    assert r["titre"] == "OPTIONS"
    assert r["detail"] == "TOUCHE L'ECRAN", "les OPTIONS doivent nommer la panne"
    assert r["actif"] is False, "cette ligne est un diagnostic, pas un reglage"
    assert r["curseur"] != 0, "le curseur ne doit pas s'ouvrir sur une ligne qu'on ne peut pas activer"
