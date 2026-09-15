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


# --- La musique du menu ---------------------------------------------------------
# ⚠️ Le sequenceur pose ses notes sur l'horloge AUDIO, pas sur les images : le
# banc fait donc avancer `currentTime` de 1/60 a chaque `frame()`. Sans ca, tout
# serait programme au meme instant et la boucle ne bouclerait jamais.


def test_le_theme_du_menu_est_demande_des_le_titre(banc):
    r = banc("""function (L, o) {
        return { etat: L.B.etat, morceau: L.Son.Mus.courante,
                 catalogue: L.Son.Mus.morceaux().length };
    }""")
    assert r["etat"] == "titre"
    assert r["morceau"] == "titre", "le menu d'accueil doit reclamer sa musique"
    assert r["catalogue"] >= 1


def test_sans_son_accorde_la_musique_ne_pose_aucune_note(banc):
    """⚠️ Le piege : programmer dans un contexte suspendu. L'horloge y est figee,
    donc toutes les notes tomberaient au meme instant et sortiraient d'un seul
    coup, en paquet, a la seconde ou le joueur touche l'ecran."""
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(false);
        L.Son.sonder();
        // ⚠️ EN NOTES, expres. Ce juge parle du SEQUENCEUR — devenu le FILET
        // le 14 sept. 2026, quand les quinze morceaux sont passes en mp3. Sans
        // cette ligne il jugerait la boucle d'un fichier, qui n'a ni pas, ni
        // note, ni derive : il resterait vert en ne gardant plus rien, et le
        // filet ne serait plus garde par personne.
        delete L.Son.Mus.def('titre').fichier;
        o.frame(120);
        return { notes: joues.length, pas: L.Son.Mus.pas, debutT: L.Son.Mus.debutT };
    }""")
    assert r["notes"] == 0, "rien ne doit etre programme tant que le son est retenu"
    assert r["pas"] > 0, "le morceau doit quand meme avancer, pour rester deterministe"
    assert r["debutT"] == 0


def test_le_theme_joue_des_que_le_son_est_accorde(banc):
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.sonder();
        // ⚠️ EN NOTES, expres. Ce juge parle du SEQUENCEUR — devenu le FILET
        // le 14 sept. 2026, quand les quinze morceaux sont passes en mp3. Sans
        // cette ligne il jugerait la boucle d'un fichier, qui n'a ni pas, ni
        // note, ni derive : il resterait vert en ne gardant plus rien, et le
        // filet ne serait plus garde par personne.
        delete L.Son.Mus.def('titre').fichier;
        o.frame(200);
        const tons = joues.filter(function (n) { return n.quoi === 'ton'; });
        return { total: joues.length, tons: tons.length,
                 formes: Array.from(new Set(tons.map(function (n) { return n.forme; }))).sort(),
                 hz: tons.slice(0, 6).map(function (n) { return Math.round(n.hz); }),
                 instants: tons.slice(0, 6).map(function (n) { return Math.round(n.t * 1000); }) };
    }""")
    assert r["tons"] > 0, "le theme ne sort pas"
    # Basse (triangle), nappe (sine), chant (square) : les trois doivent sonner.
    assert set(r["formes"]) >= {"triangle", "sine", "square"}, r["formes"]
    # La premiere note de basse est un la (MIDI 45 = 110 Hz).
    assert 110 in r["hz"], r["hz"]
    assert r["instants"] == sorted(r["instants"]), "les notes doivent etre posees dans l'ordre"


def test_les_notes_tombent_en_mesure(banc):
    """Le rythme ne doit rien devoir a la cadence des images : deux attaques de
    basse sont separees d'un nombre entier de pas, au millieme pres."""
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.sonder();
        // ⚠️ EN NOTES, expres. Ce juge parle du SEQUENCEUR — devenu le FILET
        // le 14 sept. 2026, quand les quinze morceaux sont passes en mp3. Sans
        // cette ligne il jugerait la boucle d'un fichier, qui n'a ni pas, ni
        // note, ni derive : il resterait vert en ne gardant plus rien, et le
        // filet ne serait plus garde par personne.
        delete L.Son.Mus.def('titre').fichier;
        o.frame(400);
        const basse = joues.filter(function (n) { return n.quoi === 'ton' && n.forme === 'triangle'; });
        const ecarts = [];
        for (let i = 1; i < basse.length; i++) ecarts.push(basse[i].t - basse[i - 1].t);
        const def = L.Son.Mus.def('titre');
        return { combien: basse.length, ecarts: ecarts,
                 pasS: 60 / def.bpm / def.pas_par_temps };
    }""")
    assert r["combien"] >= 4, r["combien"]
    pas_s = r["pasS"]
    for ecart in r["ecarts"]:
        rapport = ecart / pas_s
        assert abs(rapport - round(rapport)) < 0.001, f"{ecart:.4f} s n'est pas un multiple de {pas_s:.4f}"
        assert round(rapport) >= 1


def test_la_boucle_reboucle_sur_elle_meme(banc):
    """Apres un tour complet, on doit retrouver exactement la meme note au meme
    endroit — sinon la boucle derive et finit par jouer n'importe quoi."""
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.sonder();
        // ⚠️ EN NOTES, expres. Ce juge parle du SEQUENCEUR — devenu le FILET
        // le 14 sept. 2026, quand les quinze morceaux sont passes en mp3. Sans
        // cette ligne il jugerait la boucle d'un fichier, qui n'a ni pas, ni
        // note, ni derive : il resterait vert en ne gardant plus rien, et le
        // filet ne serait plus garde par personne.
        delete L.Son.Mus.def('titre').fichier;
        const def = L.Son.Mus.def('titre');
        const pasS = 60 / def.bpm / def.pas_par_temps;
        // Un tour complet de la BASSE (son motif, pas celui du morceau) + un peu.
        const basseMotif = def.voix.filter(function (v) { return v.role === 'basse'; })[0].motif;
        const images = Math.ceil((basseMotif + 2) * pasS * 60) + 30;
        o.frame(images);
        const basse = joues.filter(function (n) { return n.quoi === 'ton' && n.forme === 'triangle'; });
        const debut = L.Son.Mus.debutT;
        // La note posee au pas 0 et celle posee au pas `basseMotif` : meme hauteur.
        function auPas(p) {
            const t = debut + p * pasS;
            return basse.filter(function (n) { return Math.abs(n.t - t) < 0.001; })
                        .map(function (n) { return Math.round(n.hz); });
        }
        return { premier: auPas(0), tour: auPas(basseMotif), motif: basseMotif };
    }""")
    assert r["premier"], "aucune note au pas 0"
    assert r["premier"] == r["tour"], f"la boucle derive : {r['premier']} puis {r['tour']}"


def test_commencer_la_partie_fait_taire_le_theme(banc):
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.sonder();
        o.frame(60);
        const auMenu = L.Son.Mus.courante;
        L.Jeu.commencer();
        const combien = joues.length;
        o.frame(120);
        const apres = joues.filter(function (n) { return n.quoi === 'ton'; }).length;
        const avant = joues.slice(0, combien).filter(function (n) { return n.quoi === 'ton'; }).length;
        return { auMenu: auMenu, enJeu: L.Son.Mus.courante, avant: avant, apres: apres };
    }""")
    assert r["auMenu"] == "titre"
    # ⚠️ En ville, ce n'est plus le SILENCE : depuis que chaque district a son
    # ambiance ecrite en notes, une autre piece prend la place. Ce qu'on exige
    # n'a pas change — le theme du menu ne suit pas en ville — mais on ne peut
    # plus le prouver en comptant les notes : une autre musique en pose aussi.
    assert r["enJeu"] != "titre", "la musique du menu ne doit pas suivre en ville"
    assert r["enJeu"] and r["enJeu"].startswith("amb_"), (
        "en ville, c'est l'ambiance du district qui joue : %s" % r["enJeu"]
    )


def test_le_son_coupe_ne_pose_pas_de_musique(banc):
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.B.options.muet = true;
        L.Son.sonder();
        o.frame(150);
        return { notes: joues.length, morceau: L.Son.Mus.courante };
    }""")
    assert r["morceau"] == "titre", "le morceau reste demande : c'est le son qui est coupe"
    assert r["notes"] == 0, "SON COUPE doit vraiment tout couper"


# --- Ce qui joue doit ATTEINDRE la sortie ---------------------------------------
# ⚠️ Le bug du 13 sept. 2026 : dans `echantillon()`, la source n'etait branchee
# sur rien. Le fichier se telechargeait, se decodait, la source demarrait, le
# gain etait au bon volume et relie au maitre — mais rien n'entrait dedans. Aucune
# erreur, aucun 404, aucune trace : juste le silence. Et le filet de synthese ne
# prenait pas le relais, parce que `joue()` rendait `true` (l'objet existait).
# Ces juges regardent donc le BRANCHEMENT, pas l'intention.


def test_un_echantillon_atteint_la_sortie(banc):
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const j = L.Son.echantillon('coup', { volume: 1 });
        const ctx = L.Son.contexte;
        return { charges: L.Son.charges, joue: !!j,
                 relie: j ? ctx.atteintLaSortie(j.source) : null,
                 gainRelie: j ? ctx.atteintLaSortie(j.gain) : null };
    }""")
    assert r["charges"] > 0, "aucun echantillon charge : le banc ne suit pas le bon chemin"
    assert r["joue"] is True, "l'echantillon n'a meme pas ete cree"
    assert r["relie"] is True, "la source ne va nulle part : elle jouera dans le vide"
    assert r["gainRelie"] is True


def test_un_echantillon_pose_dans_le_monde_atteint_la_sortie(banc):
    """Avec un `pan` : la chaîne est plus longue (source, gain, panoramique),
    et c'est justement la qu'une soudure manque le plus facilement."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const j = L.Son.echantillon('coup', { volume: 1, pan: 0.8 });
        const ctx = L.Son.contexte;
        return { joue: !!j, relie: j ? ctx.atteintLaSortie(j.source) : null };
    }""")
    assert r["joue"] is True
    assert r["relie"] is True, "avec un panoramique, le son n'atteint plus la sortie"


def test_une_boucle_atteint_la_sortie(banc):
    """L'ambiance, la sirene, le moteur : tout ce qui tourne en fond."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Son.boucle('foule', true, 0.5);
        const ctx = L.Son.contexte;
        const active = L.Son.boucleActive('foule');
        // On retrouve la source par le registre des boucles : elle doit sortir.
        const j = L.Son.echantillon('foule', { boucle: true, volume: 0.5 });
        return { active: active, relie: j ? ctx.atteintLaSortie(j.source) : null };
    }""")
    assert r["active"] is True
    assert r["relie"] is True


def test_une_note_synthetisee_atteint_la_sortie(banc):
    """Le filet lui-meme doit etre branche : c'est tout ce qui reste quand un
    fichier manque."""
    r = banc("""function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.sonder();
        L.Son.ton(440, 0.2, 'square', 0.5);
        return { pose: joues.filter(function (n) { return n.quoi === 'ton'; }).length };
    }""")
    assert r["pose"] >= 1, "la synthese ne pose plus rien"


def test_aucune_source_ne_joue_dans_le_vide(banc):
    """⚠️ LE juge de cette famille de pannes. On fait sonner tout ce que le jeu
    sait faire — bruitages, boucles, musique, repliques de l'histoire — puis on
    demande : y a-t-il une source qui a DEMARRE sans etre reliee a la sortie ?
    C'est exactement ce qui est arrive deux fois le 13 sept. 2026, dans
    `echantillon()` puis dans `Voix.parler()` : la meme ligne oubliee."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        o.frame(30);                                   // ambiance + bruitages
        for (const nom in L.Son.SFX) L.Son.SFX[nom]();  // tous les effets
        L.Son.boucle('sirene', true, 0.6);
        L.Son.jouerA('coup', L.B.joueur.x + 20, L.B.joueur.y, 320);
        // Les repliques de l'histoire : on en charge une mission et on parle.
        const h = (L.B.defs.audio.histoire || [])[0];
        if (h) { L.Son.Voix.chargerHistoire(h.mission); }
        await o.attendre(); await o.attendre(); await o.attendre();
        const parle = h ? !!L.Son.Voix.parler(h.slug, {}) : null;
        const parleTel = h ? !!L.Son.Voix.parler(h.slug, { telephone: true }) : null;
        // Et la musique du menu.
        L.Jeu.retourTitre();
        o.frame(60);
        const ctx = L.Son.contexte;
        return { muettes: ctx.sourcesMuettes(), sources: ctx.sources.length,
                 parle: parle, parleTel: parleTel };
    }""")
    assert r["sources"] > 10, f"trop peu de sons declenches pour juger : {r['sources']}"
    assert r["parle"] is True, "la replique de l'histoire n'a pas joue du tout"
    assert r["parleTel"] is True, "la replique au telephone n'a pas joue du tout"
    assert r["muettes"] == 0, f"{r['muettes']} sources ont demarre sans atteindre la sortie"


def test_une_replique_de_l_histoire_atteint_la_sortie(banc):
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const h = (L.B.defs.audio.histoire || [])[0];
        L.Son.Voix.chargerHistoire(h.mission);
        await o.attendre(); await o.attendre(); await o.attendre();
        const v = L.Son.Voix.parler(h.slug, {});
        const ctx = L.Son.contexte;
        return { slug: h.slug, joue: !!v,
                 relie: v ? ctx.atteintLaSortie(v.source) : null };
    }""")
    assert r["joue"] is True, f"la replique {r['slug']} ne joue pas"
    assert r["relie"] is True, "la voix joue mais n'atteint pas la sortie : on n'entend rien"


def test_une_replique_au_telephone_atteint_la_sortie(banc):
    """Le combine ajoute un filtre : une soudure de plus, un risque de plus."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const h = (L.B.defs.audio.histoire || [])[0];
        L.Son.Voix.chargerHistoire(h.mission);
        await o.attendre(); await o.attendre(); await o.attendre();
        const v = L.Son.Voix.parler(h.slug, { telephone: true });
        const ctx = L.Son.contexte;
        return { joue: !!v, relie: v ? ctx.atteintLaSortie(v.source) : null };
    }""")
    assert r["joue"] is True
    assert r["relie"] is True, "au telephone, la voix n'atteint pas la sortie"


# --- Le combine doit s'ENTENDRE ---------------------------------------------------
# ⚠️ Atteindre la sortie ne suffit pas : entre la voix et le maitre il y a des
# filtres, et un filtre peut rendre une replique inaudible sans rien casser.
# C'est ce qui est arrive : un seul `bandpass` a 1,5 kHz (Q 1,2) pincait si serre
# que sous 900 Hz — la ou la parole porte le gros de sa puissance — la voix au
# telephone sortait PLUS BAS qu'en direct. Aucun test ne le voyait : la chaîne
# etait branchee, la source demarrait, le volume etait « bon ». Ce juge ne lit
# donc pas les reglages, il CALCULE ce qui sort.


def _biquad(type_, f0, q, f, fs=48000.0):
    """Le gain lineaire d'un filtre biquad a la frequence `f`. Formules RBJ :
    celles que le Web Audio implemente vraiment."""
    import cmath
    import math
    w0 = 2 * math.pi * f0 / fs
    cw, alpha = math.cos(w0), math.sin(w0) / (2 * q)
    if type_ == "lowpass":
        b = ((1 - cw) / 2, 1 - cw, (1 - cw) / 2)
    elif type_ == "highpass":
        b = ((1 + cw) / 2, -(1 + cw), (1 + cw) / 2)
    elif type_ == "bandpass":
        b = (alpha, 0.0, -alpha)
    else:
        raise AssertionError(f"filtre inconnu sur le chemin d'une voix : {type_}")
    a = (1 + alpha, -2 * cw, 1 - alpha)
    z = cmath.exp(-2j * math.pi * f / fs)
    return abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))


def _sortie(chaine, f):
    """Ce qui sort vraiment de la chaîne a la frequence `f` : le gain, filtres compris."""
    g = chaine["gain"]
    for filtre in chaine["filtres"]:
        g *= _biquad(filtre["type"], filtre["frequence"], filtre["q"], f)
    return g


#: Le coeur de la parole. En dessous c'est la fondamentale, au-dessus les sifflantes ;
#: entre les deux, tout ce qui fait qu'on comprend une phrase.
BANDE_DE_LA_PAROLE = (400, 600, 900, 1400, 2000, 3000)


def test_au_telephone_la_voix_est_plus_forte_qu_en_direct(banc):
    """Une voix privee de ses graves s'entend moins fort a puissance egale, et
    un appel se prend au milieu des moteurs. Le combine doit donc sortir AU-DESSUS
    de la voix en direct sur toute la bande de la parole — jamais en dessous."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const h = (L.B.defs.audio.histoire || [])[0];
        L.Son.Voix.chargerHistoire(h.mission);
        await o.attendre(); await o.attendre(); await o.attendre();
        // On suit les branchements du gain de la voix jusqu'au maitre, en
        // relevant chaque filtre rencontre : c'est le chemin reel du son.
        function chaine(v) {
            const filtres = [];
            const vus = new Set();
            let n = v.gain;
            while (n && !vus.has(n)) {
                vus.add(n);
                if (n.frequency && n.Q) filtres.push({ type: n.type, frequence: n.frequency.value, q: n.Q.value });
                n = (n.__vers || [])[0];
            }
            return { gain: v.gain.gain.value, filtres: filtres };
        }
        const direct = chaine(L.Son.Voix.parler(h.slug, {}));
        const tel = chaine(L.Son.Voix.parler(h.slug, { telephone: true }));
        return { direct: direct, tel: tel };
    }""")
    assert r["tel"]["filtres"], "le telephone ne filtre rien : ce n'est plus un combine"
    for f in BANDE_DE_LA_PAROLE:
        direct, tel = _sortie(r["direct"], f), _sortie(r["tel"], f)
        assert tel > direct, (
            f"a {f} Hz le combine sort a {tel:.2f} contre {direct:.2f} en direct : "
            "au telephone, on ne s'entend plus parler"
        )


def test_le_combine_laisse_passer_toute_la_bande_telephonique(banc):
    """Un filtre trop pince sonne « radio cassee » et mange les formants. La
    bande d'un vrai telephone (300 Hz - 3,4 kHz) doit rester a peu pres plate :
    d'un bout a l'autre, pas plus de 6 dB d'ecart."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const h = (L.B.defs.audio.histoire || [])[0];
        L.Son.Voix.chargerHistoire(h.mission);
        await o.attendre(); await o.attendre(); await o.attendre();
        const v = L.Son.Voix.parler(h.slug, { telephone: true });
        const filtres = [];
        const vus = new Set();
        let n = v.gain;
        while (n && !vus.has(n)) {
            vus.add(n);
            if (n.frequency && n.Q) filtres.push({ type: n.type, frequence: n.frequency.value, q: n.Q.value });
            n = (n.__vers || [])[0];
        }
        return { gain: v.gain.gain.value, filtres: filtres };
    }""")
    import math
    niveaux = {f: _sortie(r, f) for f in (400, 700, 1000, 1500, 2200, 3000)}
    creux, sommet = min(niveaux.values()), max(niveaux.values())
    ecart = 20 * math.log10(sommet / creux)
    assert ecart < 6, (
        f"{ecart:.1f} dB entre le creux et le sommet de la bande "
        f"({ {f: round(n, 2) for f, n in niveaux.items()} }) : le combine pince trop"
    )


def test_la_page_qui_part_rend_la_carte_son(banc):
    """⚠️ Depuis qu'on ouvre un contexte des le chargement (pour savoir si le son
    est accorde), une page qui s'en va sans fermer le sien en laisse un derriere
    elle — et le navigateur en limite le nombre. Ca ne se voit pas en jouant ;
    ca se voit quand vingt pages s'ouvrent a la suite, comme dans nos tests."""
    r = banc("""function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        L.Jeu.commencer();
        o.frame(10);
        const avant = { etat: L.Son.etatSon(), contexte: !!L.Son.contexte };
        L.Son.fermer();
        return { avant: avant, apres: L.Son.etatSon(), contexte: !!L.Son.contexte,
                 musique: L.Son.Mus.courante };
    }""")
    assert r["avant"] == {"etat": "actif", "contexte": True}
    assert r["apres"] == "absent", "le contexte doit vraiment etre lache"
    assert r["contexte"] is False
    assert r["musique"] is None


def test_apres_fermeture_le_son_peut_repartir(banc):
    """Fermer ne doit pas condamner le son : un retour d'onglet le rouvre."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Son.fermer();
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const j = L.Son.echantillon('coup', { volume: 1 });
        const ctx = L.Son.contexte;
        return { etat: L.Son.etatSon(), rejoue: !!j,
                 relie: j ? ctx.atteintLaSortie(j.source) : null };
    }""")
    assert r["etat"] == "actif"
    assert r["rejoue"] is True, "le son ne repart pas apres une fermeture"
    assert r["relie"] is True


def test_la_station_procedurale_du_camion_joue_vraiment(banc):
    """⚠️ M9 avait mis la toune du camion dans le paquet et personne ne pouvait
    l'entendre : `Radio.station()` ne cherchait que dans les mp3, donc
    `Radio.jouer('station_camion')` rendait faux et le bouton RADIO du camion
    ne faisait strictement rien.

    Une station procedurale n'a pas de fichier : c'est le sequenceur qui la
    joue, note par note, comme le theme du menu. Elle demarre donc tout de
    suite — meme hors ligne, meme avant qu'un seul mp3 soit arrive.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const camion = o.char('camion', 24, 0, 0);
        L.Vehicules.monter(j, camion);
        const auVolant = { radio: L.Son.Radio.courante, sequenceur: L.Son.Mus.courante };
        L.Vehicules.descendre(j, true);
        const apres = { radio: L.Son.Radio.courante, sequenceur: L.Son.Mus.courante };
        // Un mp3, lui, ne passe pas par le sequenceur.
        const auto = o.char('auto', 48, 0, 0);
        L.Vehicules.monter(j, auto);
        const enregistree = { radio: L.Son.Radio.courante, sequenceur: L.Son.Mus.courante };
        L.Vehicules.descendre(j, true);
        return { auVolant: auVolant, apres: apres, enregistree: enregistree,
                 defaut: camion.def.radio,
                 procedurale: L.Son.Radio.estProcedurale('station_camion'),
                 enregistreeEstProc: L.Son.Radio.estProcedurale('la_brume'),
                 titreEstStation: L.Son.Radio.stations().some(function (s) { return s.slug === 'titre'; }) };
    }""")
    assert r["defaut"] == "station_camion", "le camion doit avoir sa station"
    assert r["procedurale"] is True and r["enregistreeEstProc"] is False
    assert r["auVolant"]["sequenceur"] == "station_camion", \
        "le sequenceur ne joue pas la station du camion : le bouton RADIO ne fait rien"
    assert r["apres"]["sequenceur"] is None, "la station continue une fois descendu du camion"
    assert r["apres"]["radio"] is None
    assert r["enregistree"]["sequenceur"] is None, \
        "un mp3 n'a rien a faire dans le sequenceur"
    assert r["titreEstStation"] is False, \
        "le theme du menu est dans le cycle de la radio : le bouton RADIO tomberait dessus"


def test_la_radio_allumee_au_bouton_fait_taire_la_ville(banc):
    """⚠️ Retour de Martin : « la radio des véhicules devrait arrêter la musique
    de fond ; quand on sort des véhicules, la musique de fond reprend. »

    Un char SANS station par defaut (ambulance, autobus, velo) garde l'ambiance
    de la ville au volant — c'est voulu. Mais le bouton RADIO y lancait une
    station PAR-DESSUS : `monter()` coupait l'ambiance, `Radio.jouer()` non.
    La regle vit maintenant dans la radio elle-meme : une station demandee
    fait taire la ville, et descendre du char la fait revenir.

    Le juge suit les VRAIES boucles (`ambiance-*`, `radio-*`), pas seulement
    l'etat demande : c'est le chevauchement qu'on entend qu'il faut proscrire."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        await o.attendre(); await o.attendre(); await o.attendre();
        // ⚠️ « La ville », c'est maintenant l'ambiance DU DISTRICT, ecrite en
        // notes et jouee par le sequenceur — il n'y a plus une seule piste
        // pour toute la ville. On la reconnait a son prefixe : c'est Python
        // qui les nomme (`musique.AMBIANCES_DE_DISTRICT`).
        function etat() {
            const radio = L.Son.Radio.demandee;
            const proc = radio ? L.Son.Radio.estProcedurale(radio) : false;
            const m = L.Son.Mus.courante;
            return { ville: !!(m && m.indexOf('amb_') === 0), radio: radio,
                     station: radio ? (proc ? m === radio : L.Son.boucleActive('radio-' + radio)) : false };
        }
        const aPied = etat();
        const j = L.B.joueur;
        const v = o.char('ambulance', 24, 0, 0);
        L.Vehicules.monter(j, v);
        await o.attendre(); await o.attendre(); await o.attendre();
        const auVolant = etat();
        o.tape('Tab', 2);                                   // le bouton RADIO
        await o.attendre(); await o.attendre(); await o.attendre();
        const allumee = etat();
        L.Vehicules.descendre(j, true);
        await o.attendre(); await o.attendre(); await o.attendre();
        const descendu = etat();
        return { defaut: v.def.radio, aPied: aPied, auVolant: auVolant, allumee: allumee, descendu: descendu };
    }""")
    assert r["defaut"] is None, "le juge veut un char sans station par defaut"
    assert r["aPied"]["ville"] is True and r["aPied"]["radio"] is None, "a pied, la ville doit jouer : %s" % r["aPied"]
    assert r["auVolant"]["ville"] is True and r["auVolant"]["radio"] is None, \
        "sans station par defaut, la ville continue au volant : %s" % r["auVolant"]
    assert r["allumee"]["radio"] and r["allumee"]["station"] is True, "le bouton RADIO n'allume rien : %s" % r["allumee"]
    assert r["allumee"]["ville"] is False, "la radio joue PAR-DESSUS la ville : %s" % r["allumee"]
    assert r["descendu"] == {"ville": True, "radio": None, "station": False}, \
        "descendu, la ville doit reprendre et la radio se taire : %s" % r["descendu"]


def test_une_station_procedurale_baisse_quand_quelqu_un_parle(banc):
    """⚠️ Le ducking passait par les BOUCLES (`radio-*`, `ambiance-*`), et une
    station procedurale n'en traverse aucune : elle aurait couvert la voix au
    telephone sans que rien ne baisse."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.Son.Mus.attenuation;
        L.Son.Voix.baisserLeReste(true);
        const pendant = L.Son.Mus.attenuation;
        L.Son.Voix.baisserLeReste(false);
        return { avant: avant, pendant: pendant, apres: L.Son.Mus.attenuation };
    }""")
    assert r["avant"] == 1 and r["apres"] == 1
    assert 0 < r["pendant"] < 1, "le sequenceur ne baisse pas pendant une replique"


# --- Toute la musique est generee par IA (14 sept. 2026) --------------------
#
# ⚠️ Demande de Martin : « je veux que toutes les musiques soient des musiques
# generees par IA ». Les quinze morceaux de `musique.py` ont chacun leur mp3, et
# `musique.py` annoncait cette porte depuis le premier jour : « elle se posera
# PAR-DESSUS comme les radios ».
#
# ⚠️ CES JUGES POSENT LE `fichier` EUX-MEMES, dans les definitions du banc. Ils
# doivent dire la meme chose avec ou sans mp3 dans `static/audio/` : autrement
# ils ne jugeraient pas le CABLAGE mais l'etat d'un dossier, et ils
# deviendraient verts ou rouges au gre des generations.


def test_la_musique_sort_du_mp3_et_le_sequenceur_se_tait(banc):
    """Les deux ensemble, ce serait le meme morceau joue deux fois, decale d'un
    temps. Le juge exige donc les deux moities : le fichier boucle ET plus une
    seule note d'oscillateur."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const def = L.Son.Mus.def('titre');
        def.fichier = 'musique-titre.mp3'; def.volume_fichier = 0.5;
        L.Son.Mus.jouer('titre');
        o.frame(2); await o.attendre(); await o.attendre(); o.frame(4);
        const ctx = L.Son.contexte;
        return { boucle: L.Son.boucleActive('musique-titre'),
                 muettes: ctx.sourcesMuettes(),
                 notes: joues.filter(function (x) { return x.quoi === 'ton'; }).length };
    }""")
    assert r["boucle"] is True, "le mp3 du theme ne tourne pas : le morceau est muet"
    assert r["notes"] == 0, \
        "le sequenceur pose ses notes PAR-DESSUS le mp3 : on entend le morceau deux fois"
    assert r["muettes"] == 0, "une source joue sans atteindre la sortie"


def test_un_mp3_qui_n_arrive_pas_rend_la_main_aux_notes(banc):
    """⚠️ LE FILET, et c'est la regle 1 d'`audio.py` : le jeu marche sans les
    fichiers. Un depot frais, une generation ratee, un reseau coupe — le
    sequenceur reprend le morceau exactement la ou il est ecrit, et le joueur
    n'a pas un trou de musique."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        // Un fichier que le faux reseau ne sait pas servir : le chargement rate.
        const def = L.Son.Mus.def('titre');
        def.fichier = 'musique-titre.introuvable'; def.volume_fichier = 0.5;
        L.Son.Mus.jouer('titre');
        o.frame(2); await o.attendre(); await o.attendre(); o.frame(6);
        return { boucle: L.Son.boucleActive('musique-titre'),
                 notes: joues.filter(function (x) { return x.quoi === 'ton'; }).length,
                 muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    assert r["boucle"] is False, "une boucle tourne sur un fichier qui n'est jamais arrive"
    assert r["notes"] > 0, "le mp3 a rate ET le sequenceur se tait : plus aucune musique"
    assert r["muettes"] == 0


def test_la_musique_en_mp3_baisse_quand_quelqu_un_parle(banc):
    """⚠️ Le ducking passait par les boucles `radio-*` et `ambiance-*`. Sans
    `musique-*`, l'ambiance du district et la musique de poursuite couvriraient
    la replique — exactement le bug que la station procedurale avait deja."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        const def = L.Son.Mus.def('titre');
        def.fichier = 'musique-titre.mp3'; def.volume_fichier = 0.5;
        L.Son.Mus.jouer('titre');
        o.frame(2); await o.attendre(); await o.attendre(); o.frame(2);
        function volume() {
            const ctx = L.Son.contexte;
            const g = ctx.sources.filter(function (s) { return s.__demarree; });
            return g.length ? g[g.length - 1].__vers[0].gain.value : null;
        }
        const avant = volume();
        L.Son.Voix.baisserLeReste(true);
        const pendant = volume();
        L.Son.Voix.baisserLeReste(false);
        return { avant: avant, pendant: pendant, apres: volume() };
    }""")
    assert r["avant"] and r["avant"] > 0, "le mp3 ne joue pas : %s" % r
    assert r["pendant"] < r["avant"], "la musique ne baisse pas pendant la replique : %s" % r
    assert abs(r["apres"] - r["avant"]) < 1e-9, "la musique ne remonte pas apres : %s" % r


def test_le_musicien_de_rue_joue_son_mp3_et_sa_guitare_suit_la_distance(banc):
    """⚠️ CE N'EST PAS UNE PISTE, C'EST UN SON DU MONDE : son volume vient de la
    DISTANCE, et il change a chaque image. Une boucle reglee une fois au depart
    resterait forte a l'autre bout de la rue.

    ⚠️ Le juge pose SON morceau dans les definitions et tourne la manivelle
    lui-meme : il ne depend ainsi ni du catalogue du jour, ni de ce qui traine
    dans `static/audio/`, ni de la place de `Son.Rue.tick()` dans `jeu.js`."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const piece = JSON.parse(JSON.stringify(L.Son.Mus.def('titre')));
        piece.slug = 'essai_rue';
        piece.fichier = 'musique-essai_rue.mp3';
        piece.volume_fichier = 0.5;
        L.B.defs.audio.musiques.push(piece);
        const slug = piece.slug;
        // ⚠️ L'ORDRE EXACT DE `jeu.js` : `Son.Rue.tick()` passe en tete de
        // `maj()`, `Entites.maj()` — celui qui DEMANDE — tout a la fin, et
        // `B.t++` juste apres lui. La demande que le tick lit porte donc
        // toujours le numero de l'image precedente.
        function image(volume) {
            L.Son.Rue.tick();
            if (volume !== null) L.Son.Rue.demander(slug, volume);
            L.B.t++;
        }
        image(1); image(1);
        await o.attendre(); await o.attendre();      // le fichier arrive
        image(1); image(1);
        const fort = L.Son.volumeBoucle('rue-' + slug);
        image(0.2); image(0.2);                      // on s'eloigne
        const loin = L.Son.volumeBoucle('rue-' + slug);
        for (let i = 0; i < 5; i++) image(null);     // on le laisse derriere
        return { fort: fort, loin: loin,
                 arretee: !L.Son.boucleActive('rue-' + slug),
                 muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    assert r["fort"] and r["fort"] > 0, "le musicien ne joue pas son mp3 : %s" % r
    assert r["loin"] < r["fort"], "le volume ne suit pas la distance : %s" % r
    assert r["arretee"] is True, "la toune continue une fois le musicien laisse derriere"
    assert r["muettes"] == 0


def test_le_musicien_et_le_district_jouent_en_meme_temps(banc):
    """⚠️ Deux cles de tampon differentes (`musique-` et `rue-`), et c'est tout
    l'interet : le musicien de rue joue PAR-DESSUS l'ambiance du district, comme
    un moteur de char. Une cle partagee ferait que l'un chasserait l'autre."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const amb = L.Son.Mus.def('amb_faubourg');
        amb.fichier = 'musique-amb_faubourg.mp3'; amb.volume_fichier = 0.3;
        const piece = JSON.parse(JSON.stringify(amb));
        piece.slug = 'essai_rue';
        piece.fichier = 'musique-essai_rue.mp3';
        piece.volume_fichier = 0.5;
        L.B.defs.audio.musiques.push(piece);
        function image() {
            L.Son.Mus.tick();
            L.Son.Rue.tick();
            L.Son.Rue.demander('essai_rue', 0.8);
            L.B.t++;
        }
        L.Son.Mus.jouer('amb_faubourg');
        image(); image();
        await o.attendre(); await o.attendre();
        image(); image();
        return { district: L.Son.boucleActive('musique-amb_faubourg'),
                 musicien: L.Son.boucleActive('rue-essai_rue'),
                 muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    assert r["district"] is True and r["musicien"] is True, \
        "les deux doivent jouer ensemble : %s" % r
    assert r["muettes"] == 0


def test_le_musicien_de_rue_ne_se_coupe_pas_a_chaque_image(banc):
    """⚠️ Trouve en branchant le mp3 du musicien, et ca ne touchait PAS qu'au
    mp3 : `Son.Rue.tick()` passe en tete de `maj()` dans `jeu.js`, alors
    qu'`Entites.maj()` — celui qui DEMANDE — tourne tout a la fin, juste avant
    `B.t++`. La demande que le tick lit porte donc toujours le numero de
    l'image precedente ; avec l'egalite stricte d'avant, le musicien etait
    reduit au silence a l'image suivant chacune de ses demandes, sans arret. Sa
    toune ne demarrait JAMAIS — ni en notes, ni en fichier — et rien ne le
    disait, parce qu'`Entites` continuait sagement a la demander.

    Le juge est EN NOTES : ce n'est pas un defaut du mp3, c'est un defaut de la
    cadence, et il doit tomber meme sans un seul fichier sur le disque."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const piece = JSON.parse(JSON.stringify(L.Son.Mus.def('titre')));
        piece.slug = 'essai_rue';
        delete piece.fichier;
        L.B.defs.audio.musiques.push(piece);
        const vus = [];
        for (let i = 0; i < 12; i++) {
            L.Son.Rue.tick();                    // le tick AVANT la demande
            L.Son.Rue.demander('essai_rue', 0.9);
            L.B.t++;
            if (i) vus.push(L.Son.Rue.jouee);    // la 1re image n'a rien a jouer
        }
        // Puis on le laisse derriere nous : elle doit bel et bien s'arreter.
        for (let i = 0; i < 5; i++) { L.Son.Rue.tick(); L.B.t++; }
        return { coupures: vus.filter(function (x) { return x === null; }).length,
                 fin: vus[vus.length - 1], laissee: L.Son.Rue.jouee };
    }""")
    assert r["fin"], "la toune n'a jamais demarre : %s" % r
    assert r["coupures"] == 0, \
        "le musicien est coupe %d image(s) sur 11 alors qu'on demande a chaque image" % r["coupures"]
    assert r["laissee"] is None, "la toune continue toute seule une fois le gars laisse derriere"
