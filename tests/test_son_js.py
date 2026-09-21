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
    assert "TOUCHE L'ÉCRAN" in (r["msg"] or ""), "le silence doit se dire a l'ecran"


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
    assert "TOUCHE L'ÉCRAN" not in r["msg"], "ne pas crier au loup quand le son sort"


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
    assert r["detail"] == "TOUCHE L'ÉCRAN", "les OPTIONS doivent nommer la panne"
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
        // ⚠️ Le ducking GLISSE (voir « Le ducking ») : une seconde de pas fixes.
        for (let k = 0; k < 60; k++) L.Son.Mus.tick();
        const pendant = L.Son.Mus.attenuation;
        L.Son.Voix.baisserLeReste(false);
        for (let k = 0; k < 240; k++) L.Son.Mus.tick();
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
        // ⚠️ Le ducking GLISSE : on laisse passer une seconde de pas fixes.
        for (let k = 0; k < 60; k++) L.Son.Mus.tick();
        const pendant = volume();
        L.Son.Voix.baisserLeReste(false);
        for (let k = 0; k < 240; k++) L.Son.Mus.tick();
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


def test_la_musique_du_district_se_tait_dans_la_foire(banc):
    """⚠️ Dans l'enceinte de la foire, l'ambiance du district — La Pointe — ne
    doit plus jouer. L'orgue du manège est la musique du lieu : il sort par
    `Son.Rue` PAR-DESSUS, et laisser l'ambiance dessous ferait deux musiques à
    la fois. Dehors, elle revient.

    ⚠️ Ce n'est PAS une règle d'état : la poursuite et la bagarre, qui se
    décident plus haut dans `Chef.voulu`, continuent de couvrir dans la foire
    — on se cache sous un comptoir, la ville ne devient pas sourde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(107);
        o.frame(2);
        const j = L.B.joueur, C = L.Son.Chef, TT = L.TT;
        const f = L.Monde.carte.def.foire;
        // Le milieu de l'enceinte, la ou l'allée se trouve.
        const dedans = { x: (f.x + f.l / 2) * TT, y: (f.y + f.h / 2) * TT };
        const avant = L.Son.Mus.courante;
        // Dehors, au sud de la palissade.
        j.x = dedans.x; j.y = dedans.y;
        o.frame(2);
        const dans = L.Monde.dansLaFoire(Math.floor(j.x / TT), Math.floor(j.y / TT));
        const enFoire = L.Son.Mus.courante;
        // Et la poursuite garde son rang, meme a l'interieur.
        L.B.recherche.etoiles = L.B.defs.audio.musique.poursuite_etoiles;
        o.frame(2);
        const poursuite = L.Son.Mus.courante;
        L.B.recherche.etoiles = 0;
        while (L.Son.Mus.courante === 'mus_poursuite' && L.B.t < 60 * 30) o.frame(1);
        return { avant: avant, dans: dans, enFoire: enFoire, poursuite: poursuite };
    }""")
    assert r["avant"] and r["avant"].startswith("amb_"), (
        "avant, c'est l'ambiance du district qui joue : %s" % r["avant"]
    )
    assert r["dans"], "le juge ne s'est pas place dans la foire"
    assert r["enFoire"] is None, (
        "la musique du district ne doit pas jouer dans la foire : %s" % r["enFoire"]
    )
    assert r["poursuite"] == "mus_poursuite", (
        "la poursuite doit continuer de couvrir meme dans la foire : %s" % r["poursuite"]
    )


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


# --- La borne-fontaine defoncee ----------------------------------------------


def test_une_borne_defoncee_ne_joue_pas_un_accident_de_char(banc):
    """⚠️ **Retour de Martin : « le son des bornes-fontaines brisées n'est pas
    correct ».** Mesuré : la borne jouait `SFX.choc` — la tôle froissée d'une
    collision — au bris **et toutes les 24 images pendant les dix secondes du
    jet**. Dix-sept accidents de char pour une borne. Et le premier était un
    doublon : le char qui la renverse joue déjà `choc` à la même image.

    Le bruit de l'impact appartient à ce qui a défoncé. La borne, elle, n'a que
    son bouchon et son eau — et **une seule fois**."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(17);
        const j = L.B.joueur;
        const borne = L.B.entites.find(function (e) { return e.type === 'decor' && e.decor === 'borne_fontaine' && !e.brise; });
        if (!borne) return { pasDeBorne: true };
        j.x = borne.x; j.y = borne.y + 20; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        // On compte ce que le jeu DEMANDE a jouer, sans toucher au son.
        const compte = {};
        ['choc', 'borne_cassee', 'borne_jet'].forEach(function (nom) {
            const vrai = L.Son.SFX[nom];
            L.Son.SFX[nom] = function () { compte[nom] = (compte[nom] || 0) + 1; return vrai.apply(null, arguments); };
        });
        L.Entites.briser(borne);
        const auBris = { choc: compte.choc || 0, casse: compte.borne_cassee || 0 };
        // Toute la vie de la gerbe, et un peu plus.
        o.frame(660);
        const jets = L.B.entites.filter(function (e) { return e.type === 'jet_eau'; }).length;
        return { auBris: auBris, choc: compte.choc || 0, casse: compte.borne_cassee || 0, jets: jets };
    }""")
    assert not r.get("pasDeBorne"), "la ville n'a pas de borne-fontaine"
    assert r["auBris"]["casse"] == 1, "la borne ne fait aucun bruit en sautant : %s" % r
    assert r["auBris"]["choc"] == 0, "casser une borne joue le choc d'un accident de char : %s" % r
    assert r["casse"] == 1, "le bouchon saute plus d'une fois : %s" % r
    assert r["choc"] == 0, "le jet rejoue un choc de tôle pendant qu'il coule : %s" % r
    assert r["jets"] == 0, "la gerbe ne s'arrête jamais : %s" % r


def test_le_jet_d_une_borne_est_tenu_et_suit_la_distance(banc):
    """⚠️ Un jet est un son **continu**, pas un son rejoué : il se tient à
    chaque image avec la vérité du moment (plus de gerbe, trop loin, dans une
    pièce), exactement comme celui de l'extincteur. Et il se tait quand la
    gerbe meurt — sans ça, une borne cassée en début de partie sifflerait
    jusqu'à la fin."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(17);
        const j = L.B.joueur;
        // ⚠️ UNE BORNE D'OU L'ON PEUT S'ELOIGNER de 900 px vers l'est. « La
        // premiere borne venue » a fini un jour au coin nord-est de la carte (le
        // 16 sept. 2026, quand l'hopital a grandi et que le tirage de la ville a
        // glisse) : le joueur pose 200 px plus loin etait ramene dans la carte,
        // a trois pixels de la gerbe, et le juge accusait le son de ne pas
        // baisser avec la distance.
        const borne = L.B.entites.find(function (e) {
            return e.type === 'decor' && e.decor === 'borne_fontaine' && !e.brise
                && (e.x + 900) / L.TT < L.Monde.carte.w - 2;
        });
        if (!borne) return { pasDeBorne: true };
        j.x = borne.x; j.y = borne.y + 20; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const forces = [];
        const vrai = L.Son.SFX.borne_jet;
        L.Son.SFX.borne_jet = function (f) { forces.push(f); return vrai.apply(null, arguments); };
        o.frame(10);
        const avant = forces.slice();
        L.Entites.briser(borne);
        forces.length = 0;
        o.frame(30);
        const pres = forces.slice();
        // On s'eloigne : le souffle baisse, puis se tait.
        forces.length = 0;
        j.x = borne.x + 200; j.y = borne.y; L.Monde.centrerCamera(j.x, j.y);
        o.frame(5);
        const loin = forces.slice();
        forces.length = 0;
        j.x = borne.x + 900; L.Monde.centrerCamera(j.x, j.y);
        o.frame(5);
        const tresLoin = forces.slice();
        // La gerbe meurt : plus un souffle.
        j.x = borne.x; j.y = borne.y + 20; L.Monde.centrerCamera(j.x, j.y);
        o.frame(640);
        forces.length = 0;
        o.frame(5);
        return { avant: avant, pres: pres, loin: loin, tresLoin: tresLoin, apres: forces.slice() };
    }""")
    assert not r.get("pasDeBorne")
    # ⚠️ « À chaque image, à une près » : une image peut se perdre dans un
    # fondu ou un menu, et ce n'est pas ce qu'on mesure. Ce qu'on mesure, c'est
    # la différence entre un son TENU (trente fois) et un son REJOUÉ (l'ancien :
    # une fois toutes les 24 images, donc une ou deux).
    assert max(r["avant"]) == 0, "ça souffle sans qu'aucune borne soit cassée : %s" % r["avant"][:4]
    assert len(r["pres"]) >= 29, "le souffle n'est pas tenu à chaque image : %s appels pour 30 images" % len(r["pres"])
    assert min(r["pres"]) > 0.5, "on est sur la borne et on ne l'entend presque pas : %s" % r["pres"][:4]
    assert 0 < max(r["loin"]) < min(r["pres"]), "le souffle ne baisse pas avec la distance : %s" % r["loin"][:4]
    assert max(r["tresLoin"]) == 0, "on entend la borne à neuf cents pixels : %s" % r["tresLoin"][:4]
    assert max(r["apres"]) == 0, "la gerbe est morte et le souffle continue : %s" % r["apres"]


def test_le_coup_d_un_autre_s_entend_de_la_ou_il_est(banc):
    """⚠️ Retour de Martin (16 sept. 2026) : « les cris doivent être moins fort
    si on est loin et devenir plus fort quand on s'approche », puis « même que je
    veux pas entendre quand on les voit pas ». Le grognement d'un coup encaissé
    partait au plein volume, où que ce soit.

    ⚠️ **L'écran, pas un rayon** : à 200 px au-dessus du joueur on est plus près
    qu'à 200 px à sa droite — mais hors de la vue, qui est plus large que haute.
    L'un s'entend, l'autre non. Et on juge les DEUX chemins : le filet
    (oscillateurs, avant que les fichiers arrivent) et l'échantillon."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        const j = L.B.joueur, SFX = L.Son.SFX, c = L.Monde.carte;
        // Au milieu de la ville : la caméra n'est bornée par aucun bord.
        j.x = Math.floor(c.pxW / 2); j.y = Math.floor(c.pxH / 2);
        L.Monde.centrerCamera(j.x, j.y);
        function filet(dx, dy) {
            const n = joues.length;
            const v = L.Son.depuis({ x: j.x + dx, y: j.y + dy }, SFX.touche);
            return { v: v, sources: joues.length - n };
        }
        const sansFichier = { charge: L.Son.estCharge('touche'),
                              pres: filet(20, 0), dessus: filet(0, 200) };
        await o.attendre(); await o.attendre(); await o.attendre();
        const ctx = L.Son.contexte;
        // Le volume d'un echantillon est sur son gain, branche juste derriere la source.
        function gains(qui) {
            const n = ctx.sources.length;
            const v = L.Son.depuis(qui, SFX.touche);
            const g = ctx.sources.slice(n).filter(function (s) { return s.__demarree; })
                .map(function (s) { return s.__vers[0].gain.value; });
            return { v: v, gains: g };
        }
        const autour = function (dx, dy) { return gains({ x: j.x + dx, y: j.y + dy }); };
        const r = {
            sansFichier: sansFichier, charge: L.Son.estCharge('touche'),
            base: L.B.defs.audio.echantillons.find(function (e) { return e.slug === 'touche'; }).volume,
            joueur: gains(j), pres: autour(20, 0), milieu: autour(120, 0), bord: autour(220, 0),
            dessus: autour(0, 200), dehors: autour(400, 0), muettes: ctx.sourcesMuettes(),
        };
        // ⚠️ Et apres, le son ordinaire est rendu a lui-meme : un volume reste
        // pose ferait chuchoter tout le jeu.
        const n = ctx.sources.length;
        SFX.touche();
        r.apres = ctx.sources.slice(n).map(function (s) { return s.__vers[0].gain.value; });
        return r;
    }""")
    f = r["sansFichier"]
    assert f["charge"] is False, "le fichier était déjà là : le filet n'est pas jugé"
    assert f["pres"]["v"] > 0.9 and f["pres"]["sources"] > 0, "sans fichier, un coup à deux pas est muet"
    assert f["dessus"]["v"] == 0 and f["dessus"]["sources"] == 0, (
        "sans fichier, on entend un coup hors de l'écran")
    assert r["charge"], "le grognement ne se charge pas : l'échantillon n'est pas jugé"
    base = r["base"]
    assert r["joueur"]["gains"] == [base], "le joueur ne s'entend plus plein volume : %s" % r["joueur"]
    for cle in ("pres", "milieu", "bord"):
        assert len(r[cle]["gains"]) == 1, "à l'écran (%s), rien n'est parti : %s" % (cle, r[cle])
    pres, milieu, bord = (r[k]["gains"][0] for k in ("pres", "milieu", "bord"))
    assert base > pres > milieu > bord > 0, (
        "le coup ne baisse pas avec la distance : %s > %s > %s > %s" % (base, pres, milieu, bord))
    assert r["dessus"] == {"v": 0, "gains": []}, "on entend un coup au-dessus de l'écran : %s" % r["dessus"]
    assert r["dehors"] == {"v": 0, "gains": []}, "on entend un coup hors de l'écran : %s" % r["dehors"]
    assert r["muettes"] == 0
    assert r["apres"] == [base], "après un coup lointain, le son du joueur reste bas : %s" % r["apres"]


def test_le_klaxon_du_trafic_s_entend_de_la_ou_il_est(banc):
    """⚠️ Retour de Martin (16 sept. 2026) : « réduit un peu les klaxon des
    voiture qui passe ». Le char impatient klaxonnait au PLEIN volume, même hors
    de l'écran — mesuré au bord d'une rue du centre, les deux tiers des klaxons
    venaient d'un char qu'on ne voyait pas.

    On passe par le VRAI chemin (`klaxonT`, comme le trafic bloqué et le char
    heurté), et on ne compte que les sources qui jouent le fichier du klaxon :
    une image pose d'autres sons, et les confondre ferait passer n'importe quoi."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        const j = L.B.joueur, c = L.Monde.carte, ctx = L.Son.contexte;
        j.x = Math.floor(c.pxW / 2); j.y = Math.floor(c.pxH / 2);
        L.Monde.centrerCamera(j.x, j.y);
        // Les tampons du klaxon (deux variantes) : on les reconnait a l'objet.
        const tampons = new Set();
        for (let i = 0; i < 40; i++) tampons.add(L.Son.echantillon('klaxon').source.buffer);
        function klaxons(n) {
            return ctx.sources.slice(n).filter(function (s) { return s.__demarree && tampons.has(s.buffer); })
                .map(function (s) { return s.__vers[0].gain.value; });
        }
        function impatient(dx, dy) {
            const v = o.char('auto', dx, dy, 0);
            v.conducteur = 'trafic'; v.klaxonT = 30;
            const n = ctx.sources.length;
            // ⚠️ Une image du banc n'est pas toujours UNE mise a jour : on avance
            // jusqu'a ce que le klaxon soit parti, sinon il sonnerait pendant
            // l'essai suivant et serait compte au mauvais char.
            for (let k = 0; k < 6 && v.klaxonT === 30; k++) o.frame(1);
            const g = klaxons(n);
            L.Entites.retirer(v);
            return g;
        }
        const r = {
            base: L.B.defs.audio.echantillons.find(function (e) { return e.slug === 'klaxon'; }).volume,
            pres: impatient(40, 0), bord: impatient(220, 0),
            // ⚠️ Au-DESSUS : 200 px plus bas, le milieu de la carte est dans
            // l'eau, et un char qui coule ne klaxonne pas — ce cas-la etait
            // muet avec ou sans la regle.
            dessus: impatient(0, -200), dehors: impatient(420, 0),
        };
        // Le sien, au volant : plein volume.
        const v = o.char('auto', 40, 0, 0);
        L.Vehicules.monter(j, v);
        const n = ctx.sources.length;
        o.tape('KeyJ', 2);
        o.frame(3);
        r.joueur = klaxons(n);
        r.muettes = ctx.sourcesMuettes();
        return r;
    }""")
    base = r["base"]
    assert r["joueur"] == [base], "au volant, son propre klaxon n'est plus plein volume : %s" % r
    assert len(r["pres"]) == 1 and len(r["bord"]) == 1, "un char à l'écran klaxonne en silence : %s" % r
    assert base > r["pres"][0] > r["bord"][0] > 0, "le klaxon ne baisse pas avec la distance : %s" % r
    assert r["dessus"] == [], "on entend klaxonner un char au-dessus de l'écran : %s" % r["dessus"]
    assert r["dehors"] == [], "on entend klaxonner un char hors de l'écran : %s" % r["dehors"]
    assert r["muettes"] == 0


# --- Les musiques s'enchainent en fondu (20 sept. 2026) ---------------------
#
# ⚠️ Demande de Martin : « les transitions de musique doivent toujours se faire
# en crossover, a moins que ce soit necessaire pour l'effet et l'ambiance ».
# Avant, `boucle(..., false)` faisait `source.stop()` : la piste s'arretait net.
#
# ⚠️ Le banc a une horloge audio FIGEE (`currentTime` vaut 0) : un juge qui veut
# voir le temps passer l'avance lui-meme. Et il lit les courbes que le jeu pose
# (`__courbes`) et l'instant d'arret des sources (`__arretT`) — c'est ce qui
# distingue un fondu d'une coupure, sans oreille.

#: Le morceau qui joue est celui qu'on ENTEND : les juges posent leur `fichier`
#: eux-memes (voir plus haut), pour ne pas dependre de ce qui traine dans
#: `static/audio/`.
_OUTILS_FONDU = """
        function poser(slug) {
            const def = L.Son.Mus.def(slug);
            def.fichier = 'musique-' + slug + '.mp3'; def.volume_fichier = 0.5;
        }
        /** La source qui porte la boucle de `cle` : la derniere demarree dont le
            gain de volume porte ce fichier n'existe pas au banc, on suit donc
            l'ordre de demarrage. */
        function chaine(source) {
            const c = []; let n = source;
            while (n.__vers && n.__vers.length) { n = n.__vers[0]; c.push(n); }
            return { volume: c[0], entree: c[1], sortie: c[2] };
        }
        function sources() { return L.Son.contexte.sources.filter(function (s) { return s.__demarree; }); }
        function image() { L.Son.Mus.tick(); }
"""


def test_une_musique_qui_en_remplace_une_autre_se_fond_dedans(banc):
    """⚠️ Le juge exige les TROIS moities du crossfade : l'ancienne ne s'arrete
    pas (elle s'arrete APRES la fin de sa courbe), la nouvelle MONTE depuis zero
    sur la meme duree, et les deux courbes ensemble sont a PUISSANCE CONSTANTE —
    une rampe lineaire ferait un creux de 3 dB au milieu.

    ⚠️ Et la duree vient de Python : on change `fondu_s` dans les definitions et
    la courbe suit. Un `2` ecrit en dur dans le JS ne passerait pas."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.B.defs.audio.musique.fondu_s = 3.5;
        poser('titre'); poser('amb_quais');
        L.Son.Mus.jouer('titre');
        image(); await o.attendre(); await o.attendre(); image();
        const vieille = sources()[0];
        L.Son.contexte.currentTime = 10;
        L.Son.Mus.jouer('amb_quais');
        image(); await o.attendre(); await o.attendre(); image();
        const neuve = sources()[1];
        const v = chaine(vieille), n = chaine(neuve);
        return {
            nb: sources().length,
            vieille: { arretT: vieille.__arretT, courbes: v.sortie.gain.__courbes || null,
                       entree: v.entree.gain.__courbes || null },
            neuve: { arretT: neuve.__arretT === undefined ? null : neuve.__arretT,
                     entree: n.entree.gain.__courbes || null, depart: n.entree.gain.value,
                     sortie: n.sortie.gain.__courbes || null },
            actives: { titre: L.Son.boucleActive('musique-titre'), amb: L.Son.boucleActive('musique-amb_quais') },
            muettes: L.Son.contexte.sourcesMuettes(),
        };
    }""")
    assert r["nb"] == 2, "les deux morceaux doivent avoir joue : %s" % r
    # L'ancienne : une courbe descendante de 1 a 0 sur la duree de Python, et un
    # arret APRES elle — jamais a l'instant du changement (10 s).
    (sortie,) = r["vieille"]["courbes"]
    assert sortie["duree"] == 3.5 and sortie["t"] == 10, "l'ancienne ne baisse pas sur fondu_s : %s" % sortie
    assert sortie["courbe"][0] == 1 and abs(sortie["courbe"][-1]) < 1e-6, "la courbe ne va pas de 1 a 0"
    assert r["vieille"]["arretT"] >= 10 + 3.5, \
        "l'ancienne piste est coupee net (arret a %s) : c'est le blanc qu'on ne veut plus" % r["vieille"]["arretT"]
    # La nouvelle : elle part de ZERO et monte sur la meme duree, sans etre arretee.
    (entree,) = r["neuve"]["entree"]
    assert entree["duree"] == 3.5 and entree["t"] == 10, "la nouvelle ne monte pas sur fondu_s : %s" % entree
    assert entree["courbe"][0] == 0 and abs(entree["courbe"][-1] - 1) < 1e-6, "la courbe ne va pas de 0 a 1"
    assert r["neuve"]["depart"] == 0, "la nouvelle piste entre a plein volume : c'est un coup sec"
    assert r["neuve"]["arretT"] is None and r["neuve"]["sortie"] is None
    # Puissance constante : sin² + cos² = 1 a chaque point.
    for a, b in zip(entree["courbe"], sortie["courbe"]):
        assert abs(a * a + b * b - 1) < 1e-5, "le fondu n'est pas a puissance constante : %s, %s" % (a, b)
    assert r["actives"] == {"titre": False, "amb": True}, \
        "`boucleActive` ne doit dire vrai que de ce qu'on est cense entendre : %s" % r["actives"]
    assert r["muettes"] == 0, "une piste du fondu n'atteint pas la sortie"


def test_eteindre_la_musique_est_un_fondu_et_zero_est_une_coupure(banc):
    """Arreter n'est pas remplacer : la musique qui s'en va SEULE baisse aussi
    (on sort d'un commerce, on descend du char). Et la coupure franche reste
    possible — c'est l'exception que Martin garde pour « l'effet et l'ambiance » —
    mais elle se demande : `0`."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        poser('titre'); poser('amb_quais');
        L.Son.contexte.currentTime = 4;
        L.Son.Mus.jouer('titre');
        image(); await o.attendre(); await o.attendre(); image();
        const a = sources()[0];
        L.Son.Mus.arreter();
        const doux = { arretT: a.__arretT, courbes: chaine(a).sortie.gain.__courbes || null,
                       active: L.Son.boucleActive('musique-titre'), courante: L.Son.Mus.courante };
        L.Son.Mus.jouer('amb_quais');
        image(); await o.attendre(); await o.attendre(); image();
        const b = sources()[1];
        L.Son.Mus.arreter(0);
        const net = { arretT: b.__arretT, courbes: chaine(b).sortie.gain.__courbes || null };
        return { doux: doux, net: net, fondu: L.B.defs.audio.musique.fondu_s };
    }""")
    assert r["doux"]["arretT"] >= 4 + r["fondu"], "arreter() coupe net au lieu de baisser : %s" % r["doux"]
    assert r["doux"]["courbes"] and r["doux"]["courbes"][0]["duree"] == r["fondu"]
    assert r["doux"]["active"] is False and r["doux"]["courante"] is None
    assert r["net"]["arretT"] == 4, "arreter(0) doit couper net, tout de suite : %s" % r["net"]
    assert r["net"]["courbes"] is None, "arreter(0) ne doit poser aucun fondu"


def test_toutes_les_portes_de_la_musique_passent_par_le_fondu(banc):
    """⚠️ Il y a cinq endroits qui eteignent une musique : le sequenceur et ses
    mp3 (`Mus`), la radio enregistree, l'ambiance enregistree, et les deux
    fins du musicien de rue. Le juge les prend TOUS : le jour ou une sixieme
    porte s'ajoute avec `boucle(slug, false)`, elle ne doit pas revenir a la
    coupure sans que ca se voie."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        poser('amb_quais');
        L.B.defs.audio.radios = [{ slug: 'essai_radio', fichier: 'radio-essai.mp3', volume: 0.4 }];
        L.B.defs.audio.ambiances = [{ slug: 'essai_amb', fichier: 'ambiance-essai.mp3', volume: 0.3 }];
        const piece = JSON.parse(JSON.stringify(L.Son.Mus.def('amb_quais')));
        piece.slug = 'essai_rue'; piece.fichier = 'musique-essai_rue.mp3'; piece.volume_fichier = 0.5;
        const autre = JSON.parse(JSON.stringify(piece));
        autre.slug = 'essai_rue2'; autre.fichier = 'musique-essai_rue2.mp3';
        L.B.defs.audio.musiques.push(piece, autre);
        L.Son.contexte.currentTime = 7;
        function rue(slug) {
            for (let i = 0; i < 2; i++) { L.Son.Rue.tick(); L.Son.Rue.demander(slug, 0.8); L.B.t++; }
        }
        const sorties = {};
        function noter(nom, cle, faire) {
            const s = sources().length;
            const avant = new Set(sources());
            faire();
            const nouvelle = sources().filter(function (x) { return !avant.has(x); });
            return { nom: nom, cle: cle, nouvelle: nouvelle };
        }
        // 1. Mus + mp3
        L.Son.Mus.jouer('amb_quais'); image(); await o.attendre(); await o.attendre(); image();
        const mus = sources()[sources().length - 1];
        L.Son.Mus.arreter(); sorties.mus = mus.__arretT;
        // 2. La radio enregistree
        L.Son.Radio.jouer('essai_radio'); await o.attendre(); await o.attendre();
        const radio = sources()[sources().length - 1];
        L.Son.Radio.arreter(); sorties.radio = radio.__arretT;
        // 3. L'ambiance enregistree
        L.Son.Ambiance.jouer(); await o.attendre(); await o.attendre();
        const amb = sources()[sources().length - 1];
        L.Son.Ambiance.arreter(); sorties.ambiance = amb.__arretT;
        // 4. Le musicien de rue : il change de toune...
        rue('essai_rue'); await o.attendre(); await o.attendre(); rue('essai_rue');
        const r1 = sources()[sources().length - 1];
        rue('essai_rue2'); rue('essai_rue2');
        sorties.rue_change = r1.__arretT;
        await o.attendre(); await o.attendre(); rue('essai_rue2');
        // 5. ...puis on le laisse derriere.
        const r2 = sources()[sources().length - 1];
        for (let i = 0; i < 5; i++) { L.Son.Rue.tick(); L.B.t++; }
        sorties.rue_fin = r2.__arretT;
        return { sorties: sorties, vif: L.B.defs.audio.musique.fondu_vif_s, fondu: L.B.defs.audio.musique.fondu_s,
                 rue1: r1 !== r2, muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    s = r["sorties"]
    assert r["rue1"], "le juge n'a pas vu deux tounes de rue : %s" % r
    for porte, minimum in (("mus", r["fondu"]), ("radio", r["fondu"]), ("ambiance", r["fondu"]),
                           ("rue_change", r["vif"]), ("rue_fin", r["vif"])):
        assert s[porte] is not None, "%s : la source n'a jamais ete arretee : %s" % (porte, s)
        assert s[porte] >= 7 + minimum, \
            "%s s'arrete net (a %s, il fallait au moins %s) : %s" % (porte, s[porte], 7 + minimum, s)
    assert r["muettes"] == 0


def test_le_sequenceur_fait_aussi_son_fondu_pas_seulement_le_mp3(banc):
    """⚠️ LE FILET AUSSI. Sans mp3 (hors ligne, fichier rate), c'est le
    sequenceur qui joue — et il ne programme qu'un quart de seconde d'avance :
    en changeant de morceau, l'ancien se tairait en un quart de seconde, et le
    « fondu » n'aurait rien a baisser. Il faut que l'ancienne piste CONTINUE de
    poser ses notes, dans sa chaine qui baisse, jusqu'au bout de la courbe."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        const joues = o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        // EN NOTES, expres : ce juge parle du sequenceur.
        delete L.Son.Mus.def('titre').fichier;
        delete L.Son.Mus.def('amb_quais').fichier;
        const ctx = L.Son.contexte;
        L.Son.Mus.jouer('titre');
        ctx.currentTime = 1; image();
        const chaineTitre = L.Son.Mus.chaine;
        ctx.currentTime = 3; image();
        L.Son.Mus.jouer('amb_quais');
        const enFondu = L.Son.Mus.sortantes.length;
        function notesVers(chaine) {
            return ctx.sources.filter(function (s) {
                return s.__vers[0] && s.__vers[0].__vers.indexOf(chaine.entree) >= 0;
            }).length;
        }
        const avant = notesVers(chaineTitre);
        // Une seconde plus tard, en plein fondu (2 s) : l'ancienne joue encore.
        for (let k = 0; k < 8; k++) { ctx.currentTime += 0.125; image(); }
        const pendant = notesVers(chaineTitre);
        const sortantesPendant = L.Son.Mus.sortantes.length;
        // Apres la courbe, elle s'efface d'elle-meme.
        ctx.currentTime = 20; image();
        const fin = L.Son.Mus.sortantes.length;
        const neuve = L.Son.Mus.chaine;
        return { enFondu: enFondu, avant: avant, pendant: pendant, sortantesPendant: sortantesPendant, fin: fin,
                 autreChaine: neuve !== chaineTitre, muettes: ctx.sourcesMuettes(),
                 courbeTitre: chaineTitre.entree.__vers[0].gain.__courbes || null,
                 courbeNeuve: neuve.entree.gain.__courbes || null };
    }""")
    assert r["enFondu"] == 1, "l'ancienne piste n'est pas gardee pour finir sa courbe : %s" % r
    assert r["pendant"] > r["avant"], "l'ancienne se tait tout de suite au lieu de baisser : %s" % r
    assert r["sortantesPendant"] == 1
    assert r["fin"] == 0, "l'ancienne piste ne s'efface jamais : elle programmerait des notes pour toujours"
    assert r["autreChaine"] is True, "les deux morceaux partagent une chaine : le fondu baisserait aussi le nouveau"
    assert r["courbeTitre"] and r["courbeNeuve"]
    assert r["muettes"] == 0


def test_la_musique_d_etat_entre_vite_mais_en_fondu_et_la_ville_revient_doucement(banc):
    """⚠️ « A moins que ce soit necessaire pour l'effet et l'ambiance » : la
    poursuite qui arrive ne peut pas mettre deux secondes a monter — on
    l'entendrait apres l'avoir vue. Elle entre donc sur `fondu_vif_s`. Mais elle
    entre EN FONDU : c'est la duree qui change, pas la regle. Et quand la police
    lache, la ville revient sur `fondu_s` — le joueur souffle."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        poser('mus_poursuite');
        for (const m of L.Son.Mus.morceaux()) if (m.slug.indexOf('amb_') === 0) poser(m.slug);
        L.Jeu.commencer();
        o.frame(2); await o.attendre(); await o.attendre(); image();
        const ville = L.Son.Chef.piste;
        const debut = sources().length;
        L.B.recherche.etoiles = 3;
        L.Son.Chef.maj();
        image(); await o.attendre(); await o.attendre(); image();
        const poursuite = sources()[sources().length - 1];
        const entrant = chaine(poursuite).entree.gain.__courbes;
        const piste = L.Son.Chef.piste;
        // La police lache : la queue s'epuise, la ville revient.
        L.B.recherche.etoiles = 0; L.Son.Chef.queue = 0;
        L.Son.Chef.maj();
        image(); await o.attendre(); await o.attendre(); image();
        const retour = sources()[sources().length - 1];
        const revenant = chaine(retour).entree.gain.__courbes;
        return { ville: ville, piste: piste, entrant: entrant, revenant: revenant, retour: L.Son.Chef.piste,
                 vif: L.B.defs.audio.musique.fondu_vif_s, fondu: L.B.defs.audio.musique.fondu_s,
                 muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    assert r["ville"] and r["ville"].startswith("amb_"), "la ville ne jouait pas au depart : %s" % r
    assert r["piste"] == "mus_poursuite", "la poursuite ne prend pas la main : %s" % r
    assert r["entrant"] and r["entrant"][0]["duree"] == r["vif"], \
        "la poursuite n'entre pas sur fondu_vif_s : %s" % r["entrant"]
    assert r["vif"] < r["fondu"]
    assert r["retour"] and r["retour"].startswith("amb_"), "la ville ne revient pas : %s" % r
    assert r["revenant"] and r["revenant"][0]["duree"] == r["fondu"], \
        "la ville ne revient pas sur fondu_s : %s" % r["revenant"]
    assert r["muettes"] == 0


def test_changer_de_piste_pendant_un_fondu_ne_fait_pas_planter_la_musique(banc):
    """⚠️ Une courbe posee sur un parametre qui en suit deja une leve
    `NotSupportedError` dans le navigateur (le banc fait de meme). Une piste qui
    en remplace une autre PENDANT que celle-ci monte encore recevrait donc sa
    courbe de sortie sur le gain de sa courbe d'entree : d'ou deux gains par
    piste. Le juge change de piste trois fois d'affilee, sans laisser le temps
    passer — le pire cas."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        poser('titre'); poser('amb_quais'); poser('amb_faubourg');
        L.Son.Mus.jouer('titre');
        image(); await o.attendre(); await o.attendre(); image();
        L.Son.Mus.jouer('amb_quais');
        image(); await o.attendre(); await o.attendre(); image();
        L.Son.Mus.jouer('amb_faubourg');
        image(); await o.attendre(); await o.attendre(); image();
        const s = sources();
        return { nb: s.length, courante: L.Son.Mus.courante,
                 actives: ['titre', 'amb_quais', 'amb_faubourg'].map(function (x) { return L.Son.boucleActive('musique-' + x); }),
                 arrets: s.map(function (x) { return x.__arretT === undefined ? null : x.__arretT; }),
                 muettes: L.Son.contexte.sourcesMuettes() };
    }""")
    assert r["nb"] == 3 and r["courante"] == "amb_faubourg", r
    assert r["actives"] == [False, False, True], r
    assert r["arrets"][0] is not None and r["arrets"][1] is not None and r["arrets"][2] is None, \
        "les deux premieres doivent baisser, la derniere jouer : %s" % r
    assert r["muettes"] == 0


# --- Le volume baisse et remonte graduellement (20 sept. 2026) --------------
#
# ⚠️ Demande de Martin, dans le prolongement du fondu enchaine : « il faut aussi
# baisser les volumes et les monter graduellement ». Le ducking mettait la musique
# au quart D'UN COUP a la premiere syllabe et la remettait d'un coup a la derniere.
#
# ⚠️ Ces juges avancent `Mus.tick()` pas a pas — c'est `maj()`, a 60 par seconde —
# et lisent le volume a CHAQUE pas : « ca finit au quart » ne dit rien d'une
# courbe, il faut voir qu'aucun pas ne saute.


def _est_graduelle(serie, depart, arrivee, ce_qu_on_juge):
    """Monotone, sans saut, et arrivee EXACTE : rend le nombre de pas du trajet."""
    sens = 1 if arrivee > depart else -1
    course = abs(arrivee - depart)
    pas = [(b - a) * sens for a, b in zip([depart] + serie, serie)]
    assert all(p >= -1e-9 for p in pas), "%s : le volume repart en arriere : %s" % (ce_qu_on_juge, serie[:40])
    assert max(pas) < 0.25 * course, \
        "%s : un pas saute de %.0f%% du chemin (c'est un coup sec) : %s" % (ce_qu_on_juge, 100 * max(pas) / course, serie[:6])
    assert abs(serie[-1] - arrivee) < 1e-9, "%s : n'arrive pas (%s au lieu de %s)" % (ce_qu_on_juge, serie[-1], arrivee)
    return next(i for i, v in enumerate(serie) if abs(v - arrivee) < 1e-9) + 1


def test_la_musique_baisse_puis_remonte_graduellement_et_remonte_plus_lentement(banc):
    """Deux moities, et une troisieme : elle baisse sans saut, elle remonte sans
    saut ET ELLE REMONTE PLUS LENTEMENT — c'est ce qui laisse deux repliques
    d'une meme conversation sans faire sauter la musique entre les deux."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        // ⚠️ LES CHIFFRES SONT CEUX DU JUGE, pas ceux de Python : un `0.25`, un `0.3` ou
        // un `1.2` ecrits en dur dans le JS donneraient la meme courbe que le paquet
        // et ne rougiraient jamais. Ici, tout est double : la courbe doit suivre.
        Object.assign(L.B.defs.audio.musique, { ducking: 0.4, baisse_s: 0.6, remonte_s: 2.4 });
        poser('titre');
        L.Son.Mus.jouer('titre');
        image(); await o.attendre(); await o.attendre(); image();
        function volume() { const g = sources(); return g[g.length - 1].__vers[0].gain.value; }
        const plein = volume();
        L.Son.Voix.baisserLeReste(true);
        const descente = [];
        for (let k = 0; k < 150; k++) { image(); descente.push(volume()); }
        L.Son.Voix.baisserLeReste(false);
        const montee = [];
        for (let k = 0; k < 420; k++) { image(); montee.push(volume()); }
        const m = L.B.defs.audio.musique;
        return { plein: plein, descente: descente, montee: montee, ducking: m.ducking, baisse: m.baisse_s, remonte: m.remonte_s };
    }""")
    assert r["plein"] > 0
    bas = r["plein"] * r["ducking"]
    n_baisse = _est_graduelle(r["descente"], r["plein"], bas, "la descente")
    n_remonte = _est_graduelle(r["montee"], bas, r["plein"], "la remontee")
    assert n_baisse >= 0.15 * 60, "la musique tombe en %d pas : c'est un saut, pas une descente" % n_baisse
    assert n_remonte > 2 * n_baisse, \
        "elle remonte en %d pas et baisse en %d : elle doit revenir bien plus lentement" % (n_remonte, n_baisse)
    # Les durees viennent de Python : le niveau se rapproche de sa cible comme
    # exp(-t / (duree / 3)) et s'arrete a 0,005 pres. Deux fois les chiffres, deux fois le trajet.
    import math
    for n, duree, ce in ((n_baisse, r["baisse"], "la descente"), (n_remonte, r["remonte"], "la remontee")):
        attendu = math.log((1 - r["ducking"]) / 0.005) * (duree / 3) * 60
        assert 0.75 * attendu < n < 1.25 * attendu, \
            "%s prend %d pas, il en faut ~%d pour %s s : la duree ne vient pas de Python" % (ce, n, attendu, duree)


def test_deux_repliques_qui_s_enchainent_ne_font_pas_sauter_la_musique(banc):
    """⚠️ Le vrai defaut : une conversation, c'est des repliques a une seconde
    l'une de l'autre. Avant, la musique remontait a fond entre chacune ; elle n'en
    a maintenant pas le temps, elle reste sous la voix d'un bout a l'autre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const S = L.Son;
        S.Voix.baisserLeReste(true);
        for (let k = 0; k < 90; k++) S.Mus.tick();       // la premiere replique, bien installee
        S.Voix.baisserLeReste(false);
        let entre = 0;
        for (let k = 0; k < 10; k++) { S.Mus.tick(); entre = Math.max(entre, S.Mus.attenuation); }
        S.Voix.baisserLeReste(true);                       // la suivante, un sixieme de seconde apres
        let pire = 0;
        for (let k = 0; k < 60; k++) { S.Mus.tick(); pire = Math.max(pire, S.Mus.attenuation); }
        return { entre: entre, pire: pire, plancher: L.B.defs.audio.musique.ducking };
    }""")
    assert r["entre"] < 0.6, "entre deux repliques la musique remonte a %.2f : elle saute" % r["entre"]
    assert r["pire"] < 0.6 and r["pire"] > r["plancher"], r


def test_une_musique_qui_demarre_pendant_une_replique_baisse_elle_aussi(banc):
    """⚠️ Avant, seules les boucles DEJA en marche baissaient : une piste lancee
    pendant un dialogue (on entre dans un commerce en plein appel) entrait au plein
    volume et couvrait la voix jusqu'a la fin de la replique."""
    r = banc("""async function (L, o) {""" + _OUTILS_FONDU + """
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        poser('titre'); poser('amb_quais');
        L.Son.Mus.jouer('titre');
        image(); await o.attendre(); await o.attendre(); image();
        L.Son.Voix.baisserLeReste(true);
        for (let k = 0; k < 90; k++) image();
        L.Son.Mus.jouer('amb_quais');
        image(); await o.attendre(); await o.attendre();
        for (let k = 0; k < 10; k++) image();
        const g = sources();
        return { volume: g[g.length - 1].__vers[0].gain.value, n: g.length, ducking: L.B.defs.audio.musique.ducking };
    }""")
    assert r["n"] == 2, r
    assert abs(r["volume"] - 0.5 * r["ducking"]) < 1e-9, \
        "la nouvelle piste joue a %s au lieu de %s : elle couvre la replique" % (r["volume"], 0.5 * r["ducking"])


def test_le_musicien_de_rue_glisse_sous_la_musique_d_etat_et_sous_une_voix(banc):
    """⚠️ Le musicien de rue a sa propre sortie, et deux raisons de baisser : une voix
    (`Rue.attenuation`) et la musique d'ETAT (`rue_sous_etat`, quand la police te court
    apres). Les deux etaient des sauts."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const piece = JSON.parse(JSON.stringify(L.Son.Mus.def('titre')));
        piece.slug = 'essai_rue'; piece.fichier = 'musique-essai_rue.mp3'; piece.volume_fichier = 0.5;
        L.B.defs.audio.musiques.push(piece);
        function image() {
            L.Son.Mus.tick(); L.Son.Rue.tick(); L.Son.Rue.demander('essai_rue', 1); L.B.t++;
            return L.Son.volumeBoucle('rue-essai_rue');
        }
        image(); image();
        await o.attendre(); await o.attendre();
        image(); image();
        const plein = image();
        function serie(n) { const v = []; for (let k = 0; k < n; k++) v.push(image()); return v; }
        L.Son.Chef.piste = 'mus_poursuite';
        const etatBas = serie(120);
        L.Son.Chef.piste = null;
        const etatHaut = serie(300);
        L.Son.Voix.baisserLeReste(true);
        const voixBas = serie(120);
        L.Son.Voix.baisserLeReste(false);
        const voixHaut = serie(300);
        const m = L.B.defs.audio.musique;
        return { plein: plein, etatBas: etatBas, etatHaut: etatHaut, voixBas: voixBas, voixHaut: voixHaut,
                 sousEtat: m.rue_sous_etat, ducking: m.ducking };
    }""")
    p = r["plein"]
    assert p > 0
    _est_graduelle(r["etatBas"], p, p * r["sousEtat"], "la guitare sous la poursuite")
    _est_graduelle(r["etatHaut"], p * r["sousEtat"], p, "la guitare qui revient apres la poursuite")
    _est_graduelle(r["voixBas"], p, p * r["ducking"], "la guitare sous une voix")
    _est_graduelle(r["voixHaut"], p * r["ducking"], p, "la guitare qui revient apres une voix")
