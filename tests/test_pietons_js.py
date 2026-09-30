"""Les gens de la rue, sous Node : la foule, les sortes de gens, l'enfant et sa mère,
la fille de la Brume, le feu piéton, la rumeur, le marchand, celui qui tient son poste.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
(Le catalogue Python des piétons se juge dans `test_pietons.py`.)
"""


def test_un_pieton_attend_le_blanc_et_ne_reste_pas_planté_la_ou_il_n_y_a_pas_de_feu(banc):
    """⚠️ « Sinon ils ne passent pas » demande une **exception**, sinon la foule
    s'échoue. Les croisements en **T** n'ont pas de feux — ils ont un STOP.

    Si un piéton n'y traverse jamais, un côté de rue entier devient un cul-de-sac
    pour la foule, et **aucun juge existant ne le verrait** : « un seul îlot
    marchable » parle de géométrie, pas de circulation. La règle juste est donc :
    **au feu, on attend le blanc ; sans feu, on traverse quand c'est libre**."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT, out = {};

        // 0. LE PASSAGE A L'OUEST DU CROISEMENT, aux deux bouts du cycle : au rouge des
        // chars on passe, au vert on attend. ⚠️ Venu de `test_un_pieton_attend_au_feu_avant_de_traverser`
        // (vague C, 28 sept. 2026) ; il posait l'heure du monde et la laissait la — on
        // la remet, pour que la suite parte du meme instant qu'avant.
        (function () {
            const inter = c.intersections.find(function (i) { return i.feux; });
            // Le passage a l'ouest du croisement, sur la rue est-ouest : tuile '='.
            const tx = inter.x - 1, ty = inter.y;
            const est = L.Monde.glyphe(tx, ty);
            const t0 = L.B.t;
            L.B.t = -inter.decalage;                      // phase 0 : nord-sud roule, est-ouest est au rouge
            const rougeEO = !L.Monde.feuVert(inter, '>');
            const surAuRouge = L.Entites.traverseeSure(tx, ty, [0, 1]);
            L.B.t += Math.floor((L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images));
            const vertEO = L.Monde.feuVert(inter, '>');
            const surAuVert = L.Entites.traverseeSure(tx, ty, [0, 1]);
            L.B.t = t0;
            out.phases = { glyphe: est, rougeEO: rougeEO, surAuRouge: surAuRouge, vertEO: vertEO, surAuVert: surAuVert };
        })();

        // 1. AU FEU : on ne s'engage que sur le blanc, jamais autrement.
        const inter = c.intersections.find(function (i) { return i.feux; });
        let passage = null;
        for (let y = inter.y - 3; y < inter.y + inter.h + 3 && !passage; y++) {
            for (let x = inter.x - 3; x < inter.x + inter.l + 3; x++) {
                if (L.Monde.glyphe(x, y) === '=') { passage = { x: x, y: y }; break; }
            }
        }
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        let fautes = 0, sûr = 0;
        const t0 = L.B.t;
        for (let k = 0; k < cycle; k++) {
            L.B.t = t0 + k;
            const ok = L.Entites.traverseeSure(passage.x, passage.y, [0, 1]);
            const feu = L.Monde.feuPieton(inter, '>');
            if (ok) { sûr++; if (feu !== 'blanc') fautes++; }
        }
        L.B.t = t0;
        out.auFeu = { sûr: sûr, fautes: fautes, cycle: cycle };

        // 2. SANS FEU : un T. On traverse des que la rue est libre.
        const te = c.intersections.find(function (i) { return !i.feux && i.bras.length === 3; });
        let sansFeu = null;
        for (let y = te.y - 3; y < te.y + te.h + 3 && !sansFeu; y++) {
            for (let x = te.x - 3; x < te.x + te.l + 3; x++) {
                const g = L.Monde.glyphe(x, y);
                if (g === '=' || g === ':') { sansFeu = { x: x, y: y, g: g }; break; }
            }
        }
        // On vide la rue de ses chars : rien ne doit plus empecher de passer.
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        L.Entites.indexer();
        out.sansFeu = { trouve: !!sansFeu,
                        passe: sansFeu ? L.Entites.traverseeSure(sansFeu.x, sansFeu.y, [0, 1]) : null };

        // 3. LE BUDGET : un feu par bout de traverse, pas un par tuile.
        const poteaux = (c.def.feux_pietons || []);
        const tuiles = {};
        let surLeTrottoir = 0, doublons = 0;
        for (const f of poteaux) {
            const cle = f.x + ',' + f.y;
            if (tuiles[cle]) doublons++;
            tuiles[cle] = true;
            if (L.Monde.glyphe(f.x, f.y) === '.') surLeTrottoir++;
        }
        let passages = 0;
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const g = c.sol[y][x];
            if (g === '=' || g === ':') passages++;
        }
        out.budget = { poteaux: poteaux.length, doublons: doublons,
                       surLeTrottoir: surLeTrottoir, tuilesDePassage: passages };
        return out;
    }""")

    p = r["phases"]
    assert p["glyphe"] == "=", "la tuile choisie n'est pas un passage de la rue est-ouest"
    assert p["rougeEO"] is True and p["surAuRouge"] is True, "au rouge des chars, le pieton doit pouvoir traverser"
    assert p["vertEO"] is True and p["surAuVert"] is False, "au vert des chars, le pieton doit attendre"
    a = r["auFeu"]
    assert a["sûr"] > 0, "on ne traverse jamais au feu : la foule s'échoue"
    assert a["fautes"] == 0, (
        "on s'engage %s images sur %s alors que le feu n'est pas au blanc" % (a["fautes"], a["cycle"])
    )
    s = r["sansFeu"]
    assert s["trouve"] is True, "le juge n'a pas trouvé de passage sans feu : il ne prouve rien"
    assert s["passe"] is True, (
        "sans feu et sans un char en vue, on ne traverse pas : un côté de rue entier "
        "devient un cul-de-sac pour la foule"
    )
    b = r["budget"]
    assert b["doublons"] == 0, "deux poteaux sur la même tuile : %s" % b
    assert b["poteaux"] == b["surLeTrottoir"], (
        "un poteau est planté ailleurs que sur le trottoir : il se fait faucher, et il "
        "cache la ligne d'arrêt (%s)" % b
    )
    # ⚠️ Un par BOUT, pas un par tuile : il y a bien plus de tuiles de passage
    # que de poteaux, et c'est la mesure qui le dit.
    assert b["poteaux"] < b["tuilesDePassage"] / 3, (
        "autant de poteaux que de tuiles de passage : %s" % b
    )


def test_une_sorte_de_gens_est_un_corps_et_une_routine(banc, paquet):
    """⚠️ Demande de Martin : « des amuseurs publics, des musiciens de rue, des
    exhibitionnistes. »

    La ville avait **24 archétypes et 4 corps** : vingt et un portaient celui du
    joueur avec un échange de palette. Et sur six `metier`, **deux** faisaient
    quelque chose dans le moteur ; les autres n'étaient que des nombres. Une
    sorte était donc une couleur et trois chiffres — le dépôt a déjà payé ce
    défaut une fois, avec les filles de la Brume qu'on ne distinguait plus de
    personne.

    **Une sorte = un corps + une routine.** Le corps est jugé côté Python ;
    ici, c'est la **routine** — ce qu'elle fait que les autres ne font pas.

    ⚠️ **L'amuseur et le musicien se jugent dans `test_amuseurs_js.py`** (vague C,
    28 sept. 2026), plus sévèrement : l'attroupement de 3 à 5 à chaque image vue
    et les témoins attentifs (`test_quand_on_le_voit_il_a_entre_trois_et_cinq_personnes_autour`),
    le numéro qui bouge et le corps de chacun (`test_chacun_des_quatre_fait_un_numero_qui_bouge`),
    la toune, le public et le poste du musicien (`test_le_musicien_joue_vraiment_et_plus_fort_de_pres`).
    Il reste ici l'exhibitionniste, que personne d'autre ne regarde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(101);
        // ⚠️ En juillet : l'homme au manteau prend congé l'hiver (`froid_max`), et une partie
        // commence en janvier.
        L.B.partie.jour = 22;
        const j = L.B.joueur;
        const out = {};

        function poser(slug, dx, dy) {
            const a = L.Entites.archetype(slug);
            const e = L.Entites.creerPieton(j.x + dx, j.y + dy, a);
            e.etat = slug === 'exhibitionniste' ? 'flane' : 'fige';
            if (e.etat === 'fige') e.plante = { x: e.x, y: e.y };
            L.Entites.indexer();
            return e;
        }

        // L'EXHIBITIONNISTE ouvre son manteau : elle crie et fuit.
        // ⚠️ On vide la rue d'abord : il ouvre son manteau AU PREMIER QUI
        // FLANE, et le juge regarde SA dame. Un passant de la ville arrive
        // entre-temps, c'est lui qui prend le geste — et le juge conclut qu'il
        // n'y a pas eu de geste.
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 140) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const ex = poser('exhibitionniste', 30, 0);
        const dame = o.poser('passante', 34, 10);
        dame.etat = 'flane';
        L.Entites.indexer();
        let ouvert = -1;
        for (let i = 0; i < 60 && ouvert < 0; i++) { o.frame(1); if (ex.manteauT > 0) ouvert = i; }
        out.manteau = { ouvert: ouvert >= 0, image: ex.poseFixe, fuit: dame.etat === 'fuit',
                        crie: dame.cri > 0, corps: ex.sprite };
        // ⚠️ Et un AGENT qui passe l'arrete, lui — la seule fois ou la police
        // s'occupe de quelqu'un d'autre que le joueur.
        ex.manteauT = 0; ex.poseFixe = null;
        const agent = L.Police.creerAgent(ex.x + 24, ex.y, 'flane');
        L.Entites.indexer();
        o.frame(30);
        out.police = { fuit: ex.etat === 'fuit', menace: ex.menace === agent, suit: !!agent.but };
        return out;
    }""")
    m = r["manteau"]
    assert m["ouvert"] is True and m["image"] == 1, (
        "le manteau ne s'ouvre pas, ou sur la mauvaise image : %s" % m
    )
    assert m["fuit"] is True and m["crie"] is True, "elle ne crie pas, ou ne fuit pas : %s" % m
    assert m["corps"] == "exhibitionniste"
    assert r["police"] == {"fuit": True, "menace": True, "suit": True}, (
        "un agent doit l'arrêter, LUI : c'est ce qui rend la police crédible (%s)" % r["police"]
    )


def test_les_cinq_qui_viennent_avec_font_chacune_son_metier(banc, paquet):
    """⚠️ La deuxième vague des « sortes de gens », et la même règle : **une
    sorte = un corps + une routine**.

    Celles-ci ne sont pas du remplissage — chacune sert une fiche **déjà
    livrée** : la contractuelle rend « mal garé » visible avant que la fourrière
    n'avale le char, le touriste est le meilleur témoin de la ville, l'ivrogne
    est le seul qui ne fuit pas devant une arme, le jogger ne s'arrête jamais,
    et le facteur fait battre les portes sans jamais entrer.

    Le corps est jugé côté Python ; ici, c'est la **routine**."""
    mots = paquet["pietons"]["paroles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(77);
        const j = L.B.joueur, TT = L.TT, out = {};

        // 1. LA CONTRACTUELLE : elle va au char mal gare et elle verbalise.
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        v.laisse = true;
        const agente = o.poser('contractuelle', 70, 0);
        agente.etat = 'flane';
        L.Entites.indexer();
        const loin0 = Math.hypot(v.x - agente.x, v.y - agente.y);
        let cap = false;
        for (let i = 0; i < 400 && !v.contravention; i++) { o.frame(1); if (agente.etat === 'cap') cap = true; }
        out.contravention = { malGare: L.Missions.malGare(v), cap: cap,
                              tickets: v.contravention || 0,
                              rapproche: Math.hypot(v.x - agente.x, v.y - agente.y) < loin0,
                              dit: agente.bulle ? agente.bulle.texte : null,
                              corps: agente.sprite };
        L.Entites.retirer(agente); L.Entites.retirer(v);

        // 2. LE TOURISTE : il leve la tete devant une vitrine et il photographie.
        const c = L.Monde.carte;
        let devant = null;
        for (let y = 4; y < c.h - 4 && !devant; y++) {
            for (let x = 4; x < c.w - 4; x++) {
                if (c.sol[y][x] !== 'W') continue;
                if (!L.Monde.marchablePieton(x, y + 2) || L.Monde.estChaussee(x, y + 2)) continue;
                devant = { x: x * TT + 8, y: (y + 2) * TT + 8 };
                break;
            }
        }
        j.x = devant.x; j.y = devant.y + 40; L.Monde.centrerCamera(j.x, j.y);
        const t = o.poser('touriste', devant.x - j.x, devant.y - j.y);
        t.etat = 'flane';
        L.Entites.indexer();
        L.B.particules.length = 0;
        // ⚠️ ON ATTEND LA PHOTO, PAS LE PREMIER ARRET. Le juge sortait de sa
        // boucle des que le touriste s'arretait — or un flaneur s'arrete AUSSI
        // tout seul (une fois sur trois, `majPieton`), et `majPhoto` ne part
        // que depuis `flane`. Le juge lisait donc parfois une pause ordinaire
        // et concluait « il ne regarde pas la vitrine ». Il ne tenait que tant
        // que le de tombait bien, et il est tombe le jour ou une routine de
        // plus a decale le hasard.
        let arrete = false, photo = false;
        for (let i = 0; i < 400 && !photo; i++) {
            o.frame(1);
            if (t.etat === 'arret') arrete = true;
            if (t.face === 'haut' && L.B.particules.length > 0) photo = true;
        }
        out.photo = { arrete: arrete, leveLaTete: t.face === 'haut',
                      flash: L.B.particules.length > 0, corps: t.sprite,
                      temoin: L.Entites.archetype('touriste').temoin };
        L.Entites.retirer(t);

        // 3. L'IVROGNE : il zigzague, il ne fuit pas, et il finit par tomber.
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        // ⚠️ ON NE COMPARE PAS DEUX PROMENADES. Additionner les virages de
        // deux marches au hasard, c'est mesurer le terrain autant que la
        // demarche : un passant coince entre deux clotures tourne beaucoup, et
        // le juge devenait une loterie. Ce qui distingue vraiment l'ivrogne est
        // GEOMETRIQUE : un pieton ordinaire suit l'un des QUATRE axes, donc une
        // de ses deux vitesses est toujours nulle ; l'ivrogne, lui, a sa
        // direction tournee par un sinus — ses deux vitesses sont non nulles
        // presque tout le temps. C'est la regle elle-meme, pas son ombre.
        // ⚠️ ON NE MESURE QUE LA FLANERIE LIBRE, et c'est la moitie du juge.
        // Le passant ordinaire a DEUX autres facons de marcher, toutes deux
        // obliques et toutes deux legitimes : pousse sur la chaussee, il
        // regagne le trottoir le plus proche en diagonale ; et une fois sur
        // douze, `quelquUnRentre()` lui donne une porte et il y va tout
        // droit — `etat` reste « flane » pendant ce temps-la. Le temoin du
        // juge est tombe sur la deuxieme : cent dix-neuf images a marcher
        // vers sa porte, et le juge a accuse « un passant ordinaire marche en
        // biais ». C'etait vrai, et ca ne disait rien de l'ivrogne. Ce qui
        // distingue l'ivrogne, c'est que sa FLANERIE est tordue — alors on
        // ne mesure que la flanerie.
        // ⚠️ ON COMPTE DES PAS, PAS DES IMAGES. A 240 images fixes, ce qu'on
        // mesure depend de ce que le flaneur a fait de sa journee : s'il rentre
        // chez lui, s'il se fait pousser sur la chaussee ou s'il s'arrete, la
        // moitie des images ne compte pas. Le plancher de l'echantillon
        // (« personne n'a marche ») est tombe a 58 pour 60 demandes le jour ou
        // les cours arriere se sont cloturees — pour deux pas, et sans que rien
        // de l'ivrogne ait change. On marche donc jusqu'a EN AVOIR ASSEZ.
        const PAS_VOULUS = 160, IMAGES_MAX = 900;
        function deTravers(e) {
            let bouge = 0, obliques = 0;
            for (let i = 0; i < IMAGES_MAX && bouge < PAS_VOULUS; i++) {
                o.frame(1);
                if (e.porteBut) continue;                       // il rentre chez lui
                if (e.recul > 0) continue;                      // il vient d'encaisser
                if (L.Monde.estChaussee(Math.floor(e.x / TT), Math.floor(e.y / TT))) continue;
                if (Math.hypot(e.vx, e.vy) < 0.1) continue;
                bouge++;
                if (Math.abs(e.vx) > 0.05 && Math.abs(e.vy) > 0.05) obliques++;
            }
            return { pct: bouge ? Math.round(100 * obliques / bouge) : 0, pas: bouge };
        }
        // ⚠️ Le temoin a 24 px, pas 40 : depuis que le trottoir fait une tuile,
        // quarante pixels a l'ouest tombaient dans l'abord ou le mur du bloc,
        // et un passant ne dans un mur ne reagit a rien.
        const soul = o.poser('ivrogne', 40, 0); soul.etat = 'flane';
        const sobre = o.poser('passant', -24, 0); sobre.etat = 'flane';
        L.Entites.indexer();
        const vireSoul = deTravers(soul), vireSobre = deTravers(sobre);
        // Une arme sous le nez : tout le monde fuit, lui repond.
        // ⚠️ UN TEMOIN NEUF POUR L'ALERTE, pose a cote de l'ivrogne. Celui qui
        // vient de marcher cent soixante pas pour la mesure du zigzag est, a
        // cette image-ci, QUELQUE PART dans le quartier — le reprendre dans le
        // rayon de l'ivrogne, c'etait parier sur sa promenade, et le pari se
        // perd des qu'un lot de la ville change. Il s'etait deja perdu « le
        // jour ou les cours arriere se sont cloturees » (voir plus haut), et il
        // s'est reperdu le 16 sept. 2026 quand la palissade de banlieue est
        // passee des lots vides aux vraies cours. Ce qu'on prouve ici n'a rien
        // a voir avec sa marche : c'est qu'un passant ORDINAIRE, a la meme
        // place et sous la meme arme, reagit la ou l'ivrogne repond.
        sobre.etat = 'flane'; soul.etat = 'flane'; soul.bulle = null;
        const temoin = o.poser('passant', 16, 0); temoin.etat = 'flane';
        // ⚠️ A COTE DE L'IVROGNE, pas du joueur. `poser` place par rapport au
        // JOUEUR, et l'ivrogne vient de marcher cent soixante pas : mesure du
        // 17 sept. 2026, il etait a 191 px — hors du rayon de peur (sept
        // tuiles). Le juge notait « le passant ne reagit pas » alors que le
        // passant n'etait pas la, et il ne tenait que par la promenade de
        // l'ivrogne (la 4e vague des quartiers l'a defaite).
        temoin.x = soul.x + 16; temoin.y = soul.y; temoin.plante = null;
        L.Entites.indexer();
        L.Entites.alerter(soul.x, soul.y, j, 2);
        out.ivrogne = { zigzag: vireSoul.pct, droit: vireSobre.pct,
                        pasSoul: vireSoul.pas, pasSobre: vireSobre.pas, corps: soul.sprite,
                        fuit: soul.etat === 'fuit', repond: soul.bulle ? soul.bulle.texte : null,
                        lAutreFuit: temoin.etat === 'fuit' || temoin.etat === 'temoin' };
        soul.etat = 'flane';
        // ⚠️ ON FORCE LA REGLE, on ne joue pas sa probabilite. A six pour cent
        // par seconde, 1500 images donnent vingt-cinq occasions : une sur cinq
        // de n'en voir aucune, et le juge devient une loterie. On met la chance
        // a 1 dans la fiche et on mesure qu'il tombe ; le taux livre, lui, se
        // juge a part (`test_pietons.py`).
        const vraiTaux = L.B.defs.pietons.reactions.ivrogne_chute;
        L.B.defs.pietons.reactions.ivrogne_chute = 1;
        let tombe = false;
        // ⚠️ ET ON LE REMET DEBOUT S'IL S'ARRETE. Un flaneur s'arrete tout seul
        // une fois sur trois, pour 50 a 209 images, et `majIvrogne` ne regarde
        // qu'un ivrogne qui FLANE : mesure du 17 sept. 2026, sa halte a dure
        // 195 images, son compte a gele a 45 — UNE COCHE avant la chute — et le
        // juge a note « il ne tombe jamais tout seul ». Ce qu'on prouve, c'est
        // qu'il tombe en marchant ; la duree de ses haltes est une autre regle.
        for (let i = 0; i < 400 && !tombe; i++) {
            o.frame(1);
            if (soul.etat === 'arret') { soul.etat = 'flane'; soul.minuterie = 0; }
            if (soul.etat === 'assomme') tombe = true;
        }
        L.B.defs.pietons.reactions.ivrogne_chute = vraiTaux;
        out.ivrogne.tombe = tombe;
        out.ivrogne.taux = vraiTaux;
        L.Entites.retirer(soul); L.Entites.retirer(sobre);

        // 4. LE JOGGER : il ne s'arrete JAMAIS, et il ne temoigne de rien.
        const jog = o.poser('jogger', 40, 0); jog.etat = 'flane';
        const flaneur = o.poser('passant', -40, 0); flaneur.etat = 'flane';
        // ⚠️ LE TRAFIC NE DOIT PAS DECIDER DU RESULTAT. On pose les deux a une
        // distance fixe du joueur, sans regarder ce qui roule : le temoin s'est
        // fait ecraser par une moto a la HUITIEME image sur neuf cents, le juge
        // a compte zero pause et a accuse « un flaneur ne s'arrete jamais ».
        // `intouchable` est le drapeau des enfants : le char ne les renverse
        // pas. Il ne touche NI aux pauses NI a la marche — les deux seules
        // choses qu'on mesure ici — et il rend le decor reproductible.
        jog.intouchable = true; flaneur.intouchable = true;
        L.Entites.indexer();
        let pauses = 0, pausesFlaneur = 0;
        let routeJ = 0, routeF = 0;
        let avantJ = { x: jog.x, y: jog.y }, avantF = { x: flaneur.x, y: flaneur.y };
        for (let i = 0; i < 900; i++) {
            // ⚠️ ON FORCE LA DECISION, on ne l'attend pas. Un flaneur ne
            // decide de s'arreter que lorsque son `butT` tombe — une fois par
            // cinq secondes environ, et une fois sur trois seulement. Attendre
            // que le hasard le fasse, c'est jouer a pile ou face avec son
            // temoin : le juge est tombe le jour ou le passant n'a pas fait UNE
            // pause en neuf cents images. En remettant `butT` a zero a chaque
            // image, les deux passent par la meme porte, des centaines de fois.
            if (jog.etat === 'flane') jog.butT = 0;
            if (flaneur.etat === 'flane') flaneur.butT = 0;
            // ⚠️ ET ON LES GARDE DEHORS. `quelquUnRentre()` donne une porte a
            // un flaneur une fois sur douze, et `porteBut` court-circuite
            // toute la flanerie : il marche vers chez lui, il ne s'arrete
            // plus, et `butT` ne sert plus a rien. Le temoin y est parti, et
            // le juge a dit « un flaneur ne fait jamais de pause » — ce qui
            // est faux de la flanerie et vrai de celui qui rentre souper.
            // Rentrer chez soi est une TROISIEME routine ; elle ne repond ni
            // a la question du jogger ni a celle de l'ivrogne.
            jog.porteBut = null; flaneur.porteBut = null;
            o.frame(1);
            if (jog.etat === 'arret') pauses++;
            if (flaneur.etat === 'arret') pausesFlaneur++;
            routeJ += Math.hypot(jog.x - avantJ.x, jog.y - avantJ.y);
            routeF += Math.hypot(flaneur.x - avantF.x, flaneur.y - avantF.y);
            avantJ = { x: jog.x, y: jog.y }; avantF = { x: flaneur.x, y: flaneur.y };
        }
        out.jogger = { pauses: pauses, pausesFlaneur: pausesFlaneur, corps: jog.sprite,
                       vivants: jog.vivant && flaneur.vivant,
                       route: Math.round(routeJ), routeFlaneur: Math.round(routeF),
                       temoin: L.Entites.archetype('jogger').temoin };
        L.Entites.retirer(jog); L.Entites.retirer(flaneur);

        // 5. LE FACTEUR : il fait battre la porte, et il N'ENTRE PAS.
        // ⚠️ Une porte de la VILLE D'AVANT (27 sept. 2026) : la première de la liste est maintenant dans la
        // bande nord, loin de là où ce juge a été réglé, et le facteur ne finissait pas sa tournée à l'écran.
        const n = L.B.defs.decalage_nord || 0;
        const porte = c.portesFermees.find(function (p) { return p.y >= n && L.Monde.marchablePieton(p.x, p.y + 1); });
        j.x = porte.x * TT + 8; j.y = (porte.y + 4) * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const fac = o.poser('facteur', 0, -2 * TT);
        fac.etat = 'flane';
        L.Entites.indexer();
        let ouverte = 0, vise = false, dit = null;
        for (let i = 0; i < 500; i++) {
            o.frame(1);
            if (fac.etat === 'cap') vise = true;
            // ⚠️ On attrape la bulle AU PASSAGE : elle dure quatre-vingts
            // images, la tournee en dure cinq cents. La lire a la fin, c'est
            // lire apres qu'elle s'est fermee.
            if (fac.bulle && !dit) dit = fac.bulle.texte;
            ouverte = Math.max(ouverte, L.Monde.battant(porte.x, porte.y));
        }
        out.facteur = { vise: vise, battant: Math.round(ouverte * 100) / 100, dit: dit,
                        dehors: L.B.entites.indexOf(fac) >= 0,
                        desservies: (fac.tournee || []).length, corps: fac.sprite };
        return out;
    }""")

    # --- La contractuelle -----------------------------------------------------
    c = r["contravention"]
    assert c["malGare"] is True, "le décor du juge est faux : le char doit être mal garé"
    assert c["cap"] is True and c["rapproche"] is True, "elle ne va pas au char : %s" % c
    assert c["tickets"] == 1, "elle ne verbalise pas, ou deux fois : %s" % c
    # ⚠️ Le mot vient de `pietons.PAROLES`, pas du JavaScript.
    assert c["dit"] == mots["contractuelle"]["verbalise"], (
        "elle ne dit pas ce que la fiche dit : %s" % c
    )
    assert c["corps"] == "contractuelle"

    # --- Le touriste ----------------------------------------------------------
    p = r["photo"]
    assert p["arrete"] is True and p["leveLaTete"] is True, "il ne regarde pas la vitrine : %s" % p
    assert p["flash"] is True, "pas de flash : %s" % p
    assert p["corps"] == "touriste"
    # ⚠️ Son intérêt n'est pas le flash, c'est qu'il REGARDE : le meilleur
    # témoin de la ville, et le seul à 1,0.
    assert p["temoin"] == 1.0, "le touriste doit être le témoin parfait : %s" % p

    # --- L'ivrogne ------------------------------------------------------------
    i = r["ivrogne"]
    # ⚠️ L'ivrogne est de travers presque tout le temps ; un passant suit un
    # axe, donc jamais. La marge est énorme parce que la règle est nette.
    # ⚠️ Et le decor doit AVOIR FLANE : sans ces deux lignes, un temoin qui
    # passe ses 240 images a rentrer chez lui donne « 0 % de pas obliques » et
    # le juge passe au vert en n'ayant rien mesure du tout.
    assert i["pasSoul"] >= 120 and i["pasSobre"] >= 120, (
        "le décor du juge est faux : personne n'a marché sur le trottoir (%s)" % i
    )
    assert i["zigzag"] >= 70, "l'ivrogne marche droit : %s %% de pas obliques" % i["zigzag"]
    assert i["droit"] <= 10, (
        "le décor du juge est faux : un passant ordinaire ne marche pas en biais (%s)" % i
    )
    assert i["fuit"] is False, "l'ivrogne fuit devant une arme : %s" % i
    assert i["lAutreFuit"] is True, "le décor du juge est faux : le passant, lui, doit réagir"
    assert i["repond"] == mots["ivrogne"]["sans_peur"], "il ne répond pas : %s" % i
    assert i["tombe"] is True, "il ne tombe jamais tout seul : %s" % i
    # Et le taux livré reste celui d'un ivrogne, pas d'un pantin.
    assert 0.01 <= i["taux"] <= 0.2, "il tombe %s fois par seconde" % i["taux"]
    assert i["corps"] == "ivrogne"

    # --- Le jogger ------------------------------------------------------------
    g = r["jogger"]
    assert g["pauses"] == 0, "le jogger s'arrête : %s" % g
    assert g["vivants"] is True, "le décor du juge est faux : le trafic a tué un des deux (%s)" % g
    assert g["pausesFlaneur"] > 0, "le décor du juge est faux : un flâneur, lui, fait des pauses (%s)" % g
    assert g["route"] > g["routeFlaneur"], "le jogger ne court pas plus loin qu'un flâneur : %s" % g
    assert g["temoin"] == 0.0, "le jogger ne témoigne de rien : %s" % g
    assert g["corps"] == "jogger"

    # --- Le facteur -----------------------------------------------------------
    f = r["facteur"]
    assert f["vise"] is True, "il ne fait pas sa tournée : %s" % f
    assert f["battant"] > 0.5, "la porte ne bat pas : %s" % f
    assert f["dit"] == mots["facteur"]["livre"], "il ne dit pas ce que la fiche dit : %s" % f
    # ⚠️ ET IL N'ENTRE PAS : c'est toute la différence avec le flâneur qui
    # rentre chez lui — celui-là disparaît derrière le battant.
    assert f["dehors"] is True, "le facteur est entré : %s" % f
    assert f["desservies"] >= 1, "aucune porte desservie : %s" % f
    assert f["corps"] == "facteur"


def test_les_trois_de_la_rue_ont_chacune_leur_crochet(banc, paquet):
    """⚠️ Troisième vague des « sortes de gens », et la même règle : une sorte =
    un corps + une routine. Celles-ci ont été choisies pour leur **crochet** :

    - le **crieur** hurle ce que **tu** as fait hier — la manchette du Clairon
      (`journal.py`) compare tes statistiques du jour à celles d'hier ;
    - le **laveur** ne travaille qu'au **feu rouge** : il ne s'approche que des
      chars **arrêtés** — la même horloge que les feux pour piétons ;
    - le **pickpocket** vole les **autres** : un crime que tu n'as pas commis,
      une victime qui crie, et un agent qui arrête quelqu'un d'autre que toi.
    """
    mots = paquet["pietons"]["paroles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Ce juge mesure le crime d'autrui SANS méprise : la méprise (M12) a les siens
        // (`test_crime_d_autrui_js.py`), et une empreinte qui tombe bien ne doit rien y changer.
        L.B.defs.recherche.autrui.chance = 0;
        L.graine(88);
        const j = L.B.joueur, TT = L.TT, out = {};
        const d = o.ligneDroite();

        // 1. LE CRIEUR hurle la manchette — celle du Clairon, pas une phrase à lui.
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.derniereManchette = { slug: 'nuit_rouge', titre: 'NUIT ROUGE AU FAUBOURG' };
        const cri = o.poser('crieur', 20, 0);
        cri.etat = 'fige'; cri.plante = { x: cri.x, y: cri.y };
        L.Entites.indexer();
        let dit = null, bouge = 0;
        const poste = { x: cri.x, y: cri.y };
        for (let i = 0; i < 120 && !dit; i++) { o.frame(1); if (cri.bulle) dit = cri.bulle.texte; }
        for (let i = 0; i < 60; i++) { o.frame(1); bouge = Math.max(bouge, Math.hypot(cri.x - poste.x, cri.y - poste.y)); }
        out.crieur = { dit: dit, corps: cri.sprite, bouge: Math.round(bouge),
                       vitesse: L.Entites.archetype('crieur').vitesse };
        L.Entites.retirer(cri);

        // 2. LE LAVEUR : il laisse passer un char qui ROULE, il lave celui qui est ARRETE.
        // ⚠️ SUR LA CHAUSSEE : un laveur de vitres travaille dans la rue, et
        // `charArrete` ne regarde que les chars qui sont sur la route — sinon
        // il laverait les autos garees dans les cours.
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const roule = o.char('auto', 30, 0, 0);
        roule.vitesse = 3; roule.vx = 3;
        const lav = o.poser('laveur', 0, 0);
        lav.etat = 'flane';
        L.Entites.indexer();
        let versLeRoulant = false;
        for (let i = 0; i < 60; i++) { o.frame(1); roule.vitesse = 3; if (lav.etat === 'cap') versLeRoulant = true; }
        out.laveur = { suitUnRoulant: versLeRoulant };
        L.Entites.retirer(roule);
        // Et maintenant un char a l'arret, pile devant lui.
        j.x = d.x; j.y = d.y;
        const arrete = o.char('auto', 26, 0, 0);
        arrete.vitesse = 0; arrete.vx = 0; arrete.vy = 0;
        L.Entites.indexer();
        let lave = -1, propose = null;
        for (let i = 0; i < 300 && lave < 0; i++) {
            o.frame(1);
            arrete.vitesse = 0; arrete.vx = 0; arrete.vy = 0;
            if (lav.bulle && !propose) propose = lav.bulle.texte;
            if (lav.laveT > 0) lave = i;
        }
        out.laveur.lave = lave >= 0;
        out.laveur.propose = propose;
        out.laveur.corps = lav.sprite;
        out.laveur.surLeChar = lave >= 0 ? Math.round(Math.hypot(lav.x - arrete.x, lav.y - arrete.y)) : null;
        L.Entites.retirer(lav); L.Entites.retirer(arrete);

        // 3. LE PICKPOCKET vole un passant — dans le dos, et l'argent CHANGE de poche.
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 160) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const voleur = o.poser('pickpocket', 0, 0);
        voleur.etat = 'flane'; voleur.argent = 0;
        const victime = o.poser('passant', 40, 0);
        victime.etat = 'flane'; victime.argent = 37; victime.face = 'droite';
        // ⚠️ LE JOUEUR S'ECARTE. `o.poser` fait naitre le voleur SUR lui : le
        // joueur se tenait donc entre le voleur et sa victime, et selon le tirage
        // le voleur le poussait, qui poussait la victime — tous les trois glissaient
        // vers l'est pendant 850 images sans que la main atteigne une poche. Le
        // pickpocket n'y etait pour rien (mesure du 16 sept. 2026, le jour ou le
        // tirage de la ville a glisse avec l'hopital). On le pose derriere le
        // voleur, sur le meme trottoir : pas sur la chaussee.
        j.x -= 3 * TT;
        L.Entites.indexer();
        let vole = -1;
        for (let i = 0; i < 900 && vole < 0; i++) {
            o.frame(1);
            // ⚠️ ON TIENT LA RUE VIDE PENDANT TOUTE LA MESURE. `peupler()`
            // repose des passants a chaque seconde, et le voleur prend le
            // PREMIER qui passe : le juge voyait alors un vol — le bon geste,
            // la bonne bulle — sur quelqu'un d'autre, et concluait que sa
            // victime n'avait rien perdu.
            for (const q of L.B.entites.slice()) {
                if (q.type === 'pieton' && q !== voleur && q !== victime) L.Entites.retirer(q);
            }
            victime.face = 'droite';                    // il regarde a l'oppose : on l'aborde de dos
            if (voleur.voleT > 0) vole = i;
        }
        out.vol = { vole: vole >= 0, poches: victime.argent, butin: voleur.argent,
                    crie: victime.cri > 0, fuit: victime.etat === 'fuit',
                    menace: victime.menace === voleur,
                    dit: victime.bulle ? victime.bulle.texte : null,
                    corps: voleur.sprite };
        // ⚠️ Et un agent l'arrete, LUI.
        voleur.voleT = 0; voleur.etat = 'flane'; voleur.repos = 0;
        const agent = L.Police.creerAgent(voleur.x + 30, voleur.y, 'flane');
        L.Entites.indexer();
        o.frame(30);
        out.vol.police = { neVolePlus: voleur.repos > 0 || voleur.etat === 'fuit' };
        return out;
    }""")

    c = r["crieur"]
    # ⚠️ Il dit LA MANCHETTE, pas une phrase à lui : c'est tout le personnage.
    assert c["dit"] == "NUIT ROUGE AU FAUBOURG", (
        "le crieur ne hurle pas la manchette du Clairon : %s" % c
    )
    assert c["corps"] == "crieur"
    assert c["vitesse"] == 0.0 and c["bouge"] <= 2, (
        "un crieur de journaux tient son coin : %s px parcourus" % c["bouge"]
    )

    lv = r["laveur"]
    # ⚠️ AU FEU ROUGE : il ne court pas après un char qui roule.
    assert lv["suitUnRoulant"] is False, (
        "il s'approche d'un char qui roule : ce n'est plus un métier, c'est un accident"
    )
    assert lv["lave"] is True, "il ne lave jamais un char arrêté : %s" % lv
    assert lv["surLeChar"] is not None and lv["surLeChar"] <= 26, (
        "il lave de loin : %s px du char" % lv["surLeChar"]
    )
    assert lv["propose"] == mots["laveur"]["propose"], "il ne dit pas ce que la fiche dit : %s" % lv
    assert lv["corps"] == "laveur"

    v = r["vol"]
    assert v["vole"] is True, "le pickpocket ne vole personne : %s" % v
    # ⚠️ L'argent CHANGE de poche : sinon le vol n'est qu'une animation, et
    # fouiller le volé rapporterait quand même.
    assert v["poches"] == 0 and v["butin"] == 37, (
        "l'argent n'a pas changé de poche : %s" % v
    )
    assert v["crie"] is True and v["fuit"] is True, "la victime ne réagit pas : %s" % v
    assert v["menace"] is True, "la victime en veut à quelqu'un d'autre que son voleur : %s" % v
    assert v["dit"] == mots["pickpocket"]["au_voleur"], "elle ne crie pas au voleur : %s" % v
    assert v["corps"] == "pickpocket"
    assert v["police"]["neVolePlus"] is True, (
        "il vole sous le nez d'un agent : la police n'existe pas que pour le joueur, "
        "mais elle existe quand même (%s)" % v["police"]
    )


def test_le_marchand_reste_derriere_son_comptoir(banc):
    """⚠️ Le guichet du camion-restaurant est TROUE pour qu'on voie le marchand
    dedans — encore faut-il qu'il y soit. `peupler()` oubliait tout pieton a
    plus de 520 px du joueur, marchands compris : on debarquait de l'autobus
    et les neuf comptoirs de la ville se vidaient a la premiere image. Un
    marchand tient son poste comme un personnage d'histoire : il attend.
    """
    r = banc("""function (L, o) {
        L.B.partie.jour = 22; L.Jeu.commencer();   // ⚠️ EN JUILLET, DES LE DEPART (les marchands se postent a `commencer`) : l'hiver, la cabane de fruits de mer est fermée (docs/jalons/la-foire-fermee-l-hiver.md)
        const compter = function () {
            return { comptoirs: L.B.entites.filter(function (e) { return e.type === 'ambulant'; }).length,
                     marchands: L.B.entites.filter(function (e) { return e.commerce; }).length };
        };
        const avant = compter();
        o.frame(60);
        return { avant: avant, apres: compter() };
    }""")
    assert r["avant"]["comptoirs"] > 0, "aucun commerce ambulant sur la carte"
    assert r["avant"]["marchands"] == r["avant"]["comptoirs"], "un comptoir nait sans marchand"
    assert r["apres"]["marchands"] == r["apres"]["comptoirs"], "les marchands s'oublient quand on est loin"


def test_la_foule_ne_se_traverse_plus(banc):
    """Retour de Martin : « empeche que les choses se chevauchent ».

    ⚠️ Personne ne poussait personne : deux passants qui se croisaient se
    superposaient EXACTEMENT. Mesure avant correctif, en marchant deux minutes
    dans la ville : 1032 paires enfoncees l'une dans l'autre en 960 images,
    jusqu'a 9,9 px — deux corps de 10 px parfaitement confondus. Apres : 0,1 px
    au pire, des la premiere image (personne ne NAIT non plus dans quelqu'un).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let paires = 0, pire = 0, images = 0, nes = 0;
        // ⚠️ On mesure aussi la DUREE d'un chevauchement, et combien passent le
        // pixel : c'est ca, « se traverser ». Une profondeur seule ne distingue
        // pas deux corps confondus d'un frolement d'une image entre deux
        // passants qui se croisent de face.
        let gros = 0, plusLong = 0, creuse = 0;
        const durees = {}, profond = {}, creuseT = {};
        // Naitre dans quelqu'un se voit a un chevauchement PLEIN (meme pixel) :
        // les deux branches de placeDeNaissance rendent un centre de tuile.
        const touches = ['KeyD', 'KeyW', 'KeyA', 'KeyS'];
        for (let bloc = 0; bloc < 24; bloc++) {
            const t = touches[bloc % 4];
            o.touche(t);
            for (let k = 0; k < 40; k++) {
                o.frame(1); images++;
                const gens = L.B.entites.filter(L.Entites.deboutDansLaFoule);
                const vues = {};
                for (let a = 0; a < gens.length; a++) {
                    for (let b = a + 1; b < gens.length; b++) {
                        const d = Math.hypot(gens[a].x - gens[b].x, gens[a].y - gens[b].y);
                        const chevauche = gens[a].r + gens[b].r - d;
                        if (chevauche > gens[a].r + gens[b].r - 0.001) nes++;
                        // ⚠️ **LA FOULE ENTRE ELLE, pas le joueur contre elle.** Deux
                        // passants se démêlent tous les deux : chacun cède la moitié,
                        // et un chevauchement qui dure est un vrai défaut. Le joueur,
                        // lui, POUSSE — et quand il coince quelqu'un contre un mur,
                        // personne n'a plus où aller : mesuré le 17 sept. 2026 au
                        // terminus, 5,2 px d'enfoncement, un passant acculé à la
                        // façade. Ce cas-là a son juge à lui, et il est plus sévère
                        // (`test_courir_ne_permet_pas_de_traverser_les_gens` : on
                        // n'entre pas dans quelqu'un qui a de quoi s'écarter).
                        if (gens[a].type === 'joueur' || gens[b].type === 'joueur') continue;
                        if (chevauche > 0) { paires++; pire = Math.max(pire, chevauche); }
                        const cle = gens[a].id + '-' + gens[b].id;
                        if (chevauche > 1) {
                            gros++;
                            durees[cle] = (durees[cle] || 0) + 1;
                            plusLong = Math.max(plusLong, durees[cle]);
                            vues[cle] = true;
                            // ⚠️ LA VRAIE REGLE : un chevauchement SE DEFAIT. Deux
                            // corps qui s'enfoncent l'un dans l'autre d'une image a
                            // l'autre, c'est ca, se traverser — un nombre d'images
                            // n'est qu'une consequence, et il depend du trajet des
                            // passants.
                            // ⚠️ ... et un creusement qui se DEFAIT l'image suivante est une
                            // bousculade — un troisieme corps qui pousse — pas une traversee.
                            // On ne compte que ceux qui creusent ET tiennent.
                            if (profond[cle] !== undefined && chevauche > profond[cle] + 0.01) {
                                creuseT[cle] = (creuseT[cle] || 0) + 1;
                                if (creuseT[cle] >= 2) creuse++;
                            } else creuseT[cle] = 0;
                            profond[cle] = chevauche;
                        }
                    }
                }
                for (const cle in durees) if (!vues[cle]) { durees[cle] = 0; delete profond[cle]; delete creuseT[cle]; }
            }
            o.relacher(t);
        }
        return { images: images, paires: paires, pire: +pire.toFixed(2), nes_empiles: nes,
                 gros: gros, plusLong: plusLong, creuse: creuse };
    }""")
    assert r["images"] == 960
    assert r["nes_empiles"] == 0, "on ne nait pas dans quelqu'un"
    # ⚠️ CE QU'ON INTERDIT, C'EST DE SE TRAVERSER : un chevauchement qui DURE,
    # ou qui va jusqu'à confondre deux corps. Le juge exigeait moins d'un pixel
    # à toute image — c'était la MESURE du jour, pas la règle : deux passants
    # qui se croisent de face se rapprochent de quatre pixels en une image, et
    # la séparation les défait à la suivante. Exiger moins d'un pixel revenait à
    # exiger que personne ne se croise jamais de face, et ça tenait au trajet des
    # passants, pas au code. Le défaut d'origine (1032 paires, 9,9 px, tenues)
    # reste rouge des trois côtés.
    # ⚠️ **Reformule le 15 sept. 2026, et cette fois sur la REGLE.** Il exigeait
    # qu'aucun chevauchement ne tienne plus d'UNE image — un nombre qui dependait
    # du trajet des passants, pas du code : une seule paire l'a depasse, deux
    # images a 1,05 px, le jour ou la ville est redevenue reproductible (elle ne
    # l'etait pas, voir `test_reproductible`). Ce qu'on veut dire par « se
    # traverser », c'est deux corps qui s'ENFONCENT l'un dans l'autre au lieu de
    # se defaire. Ca, c'est une regle, et elle se mesure sans seuil : mesure du
    # jour, ZERO enfoncement sur 960 images.
    assert r["creuse"] == 0, (
        f"{r['creuse']} fois un chevauchement s'est CREUSE au lieu de se défaire : "
        "la séparation ne pousse pas assez fort, et la foule se traverse"
    )
    assert r["plusLong"] <= 4, (
        f"un chevauchement tient {r['plusLong']} images : deux corps restent pris l'un dans l'autre"
    )
    assert r["gros"] <= 8, f"{r['gros']} chevauchements de plus d'un pixel en 960 images"
    assert r["pire"] < 4.0, f"deux personnes s'enfoncent de {r['pire']} px l'une dans l'autre"


def test_courir_ne_permet_pas_de_traverser_les_gens(banc, paquet):
    """⚠️ Le plafond de separation doit passer DEVANT les jambes les plus
    rapides du jeu. Fixe a 1,5 px, il arretait bien le joueur qui MARCHE
    (1,2 px/image) et laissait passer celui qui SPRINTE (2,1) : il suffisait
    de tenir MAJ pour entrer dans le vendeur.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const pas = L.Entites.pasDeDemele();
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        function foncer(sprint) {
            j.x = t.x - 40; j.y = t.y; j.vx = 0; j.vy = 0;
            if (sprint) o.touche('ShiftLeft');
            o.touche('KeyD'); o.frame(120); o.relacher('KeyD');
            if (sprint) o.relacher('ShiftLeft');
            return +Math.hypot(j.x - t.x, j.y - t.y).toFixed(1);
        }
        return { pas: pas, marche: foncer(false), sprint: foncer(true), r: j.r + t.r };
    }""")
    vitesses = paquet["recherche"]["vitesses"]
    assert r["pas"] > vitesses["joueur_sprint"], "on sprinte plus vite qu'on ne se demele"
    assert r["marche"] >= r["r"] - 0.5, "on entre dans un personnage en marchant"
    assert r["sprint"] >= r["r"] - 0.5, "on entre dans un personnage en courant"


def test_celui_qui_tient_son_poste_cede_puis_revient(banc):
    """⚠️ « Fige » veut dire « il tient son poste », pas « c'est un poteau ».
    Vraiment immobile, un donneur plante sur le trottoir bouchait la rue POUR
    TOUJOURS : l'agent lance aux trousses du joueur venait buter dessus et y
    restait — 260 images sur place, l'arrestation n'arrivait jamais. Il se
    laisse donc bousculer de quelques pixels, et il rentre chez lui.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        // ⚠️ **LA RUE AUTOUR DE LUI EST VIDE** : une roulotte a cafe a 1 tuile de Ti-Guy fait ce juge.
        // A l'ouest, elle se tenait sur la piste du coureur — il mesurait 1 px, la roulotte, pas la
        // laisse ; deplacee a l'est (`app/devants.py` : elle bouchait la porte du terminus), Ti-Guy
        // se retrouvait coince contre elle, a 12,1 px et incapable de revenir. Le juge parle d'un
        // donneur, pas d'une roulotte : on l'ote, et ce qu'on mesure est la laisse toute seule.
        L.B.entites.filter(function (e) { return e.type === 'ambulant' && Math.hypot(e.x - t.x, e.y - t.y) < 200; })
            .forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        o.frame(2);
        const poste = { x: t.plante ? t.plante.x : t.x, y: t.plante ? t.plante.y : t.y };
        j.x = poste.x - 40; j.y = poste.y; j.vx = 0; j.vy = 0;
        // ⚠️ **ON LE POUSSE, ON NE LE CONTOURNE PAS.** Le juge courait droit
        // vers l'est pendant 240 images et lisait le déplacement à la fin :
        // sauf que `demeler` écarte les corps qui se touchent, donc le joueur
        // DÉRIVE de quelques pixels, passe à côté du poste et continue sa
        // course — mesuré le 16 sept. 2026, il finissait 228 px plus loin sans
        // avoir bousculé personne, et le juge concluait « on ne peut pas le
        // tasser ». Ce qu'on mesure est une POUSSÉE : on garde donc le joueur
        // sur la ligne du poste pendant qu'il pousse. Le contournement a son
        // propre juge ; celui-ci n'en parle pas.
        o.touche('ShiftLeft'); o.touche('KeyD');
        for (let i = 0; i < 240; i++) { j.y = poste.y; o.frame(1); }
        const pousse = Math.hypot(t.x - poste.x, t.y - poste.y);
        o.relacher('KeyD'); o.relacher('ShiftLeft');
        // ⚠️ Et on le DEPLACE pour de bon, de huit pixels (sous la laisse) : en rue libre la poussee
        // ne l'ecarte que d'un dixieme de pixel, et « il rentre » serait vrai sans qu'il ait a rentrer.
        t.x = poste.x + 8; t.y = poste.y;
        j.x = poste.x - 200; j.y = poste.y;              // on le lache
        // ⚠️ Il rentre à pied, et le chemin du retour dépend de ce qu'il a autour
        // (un banc, un passant, la largeur du trottoir) : 180 images le ramenaient
        // à un demi-pixel près tant que la trame n'avait pas bougé, et à 1,0 px
        // pile le 17 sept. 2026. On lui laisse le temps d'arriver plutôt que
        // d'élargir la règle : « à sa place » veut dire à sa place.
        for (let i = 0; i < 600 && Math.hypot(t.x - poste.x, t.y - poste.y) > 1; i++) o.frame(1);
        return { pousse: +pousse.toFixed(1), rentre: +Math.hypot(t.x - poste.x, t.y - poste.y).toFixed(1),
                 etat: t.etat };
    }""")
    # ⚠️ Le plancher est « un peu », pas un demi-pixel : en rue libre la laisse le ramene a chaque
    # image et l'equilibre est a 0,1-0,3 px (le demi-pixel d'avant n'etait tenu que par la roulotte).
    assert r["pousse"] > 0.05, "on doit pouvoir le tasser un peu, sinon il bouche la rue"
    assert r["pousse"] < 12, f"on l'a promene de {r['pousse']} px : il n'est plus a son poste"
    # ⚠️ **UN PIXEL, c'est à sa place** : il marche par pas de fraction de pixel et
    # s'arrête dès qu'il est chez lui. Le juge exigeait STRICTEMENT moins d'un
    # pixel, et il l'obtenait tant que le trottoir d'à côté était celui-là ; le
    # 17 sept. 2026, la trame a bougé et il s'est posé à 1,0 px pile. Un donneur
    # large de douze pixels est à son poste à un pixel près — ce qu'on juge, c'est
    # qu'il RENTRE, pas qu'il vise le sous-pixel.
    assert r["rentre"] <= 1, "lache, il doit revenir a sa place"
    assert r["etat"] == "fige"


def test_demeler_ne_pousse_pas_un_passant_sur_la_chaussee(banc):
    """⚠️ Martin, 29 sept. 2026 : « garder les passants au trottoir ». Une passante qui
    flânait contre le signaleur d'un chantier (figé, il ne cède pas) était poussée par
    `demeler` au bord de la voie, le corps dedans, et y restait huit secondes : le trafic
    s'arrêtait pour elle, puis forçait. Ici le geste entier, hors chantier : un homme figé
    au bord du trottoir, une passante qui marche sur lui en longeant la bordure (un pixel
    côté rue), et un char du trafic qui arrive sur la voie d'à côté. Elle ne mord jamais la
    chaussée, elle ne lui passe pas au travers, et le char passe sans s'arrêter pour elle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const c = L.Monde.carte, M = L.Monde, TT = L.TT;
        // Un bout de trottoir droit sur sept tuiles, une voie droite dessous : ni croisement
        // ni ligne d'arrêt huit tuiles en amont, pour que rien d'autre n'arrête le char.
        function scene() {
            for (let y = 20; y < c.h - 3; y++) {
                for (let x = 12; x < c.w - 12; x++) {
                    const sens = c.voie[y + 1][x];
                    if (sens !== '<' && sens !== '>') continue;
                    const p = sens === '<' ? 1 : -1;
                    let ok = true;
                    for (let k = -3; k <= 3 && ok; k++) {
                        ok = M.estTrottoir(x + k, y) && !M.bloque(x + k, y, M.MASQUE_PIETON)
                            && !M.bloque(x + k, y - 1, M.MASQUE_PIETON) && M.estChaussee(x + k, y + 1);
                    }
                    for (let k = -4; k <= 8 && ok; k++) {
                        const vx = x + p * k;
                        ok = c.voie[y + 1][vx] === sens && !M.intersectionA(vx, y + 1) && !c.arrets[vx + ',' + (y + 1)];
                    }
                    if (ok) return { tx: x, ty: y, sens: sens, p: p };
                }
            }
            return null;
        }
        const s = scene();
        if (!s) return { trouve: false };
        const j = L.B.joueur;
        j.x = s.tx * TT + 8; j.y = s.ty * TT + 8 - 220; j.vx = 0; j.vy = 0; j.intouchable = true;
        const homme = L.Entites.creerPieton(s.tx * TT + 8, s.ty * TT + 8, L.Entites.archetype('ouvrier'));
        homme.etat = 'fige'; homme.intouchable = true;
        const elle = L.Entites.creerPieton(s.tx * TT + 8 - 26, s.ty * TT + 8 + 1, L.Entites.archetype('passante'));
        const bordure = (s.ty + 1) * TT;
        const nous = [homme, elle, j];
        // La rue autour d'eux, vide : ce qu'on juge, c'est eux trois.
        function vider(v) {
            L.B.entites.filter(function (q) {
                return nous.indexOf(q) < 0 && q !== v && Math.hypot(q.x - homme.x, q.y - homme.y) < 20 * TT
                    && (q.type === 'pieton' || q.type === 'vehicule');
            }).forEach(function (q) { L.Entites.retirer(q); });
        }
        let mord = 0, auCentre = 0, dmin = Infinity;
        function mesurer() {
            // Elle marche sur lui, toujours : ni arrêt, ni demi-tour.
            elle.etat = 'flane'; elle.dir = 0; elle.butT = 1000;
            mord = Math.max(mord, elle.y + elle.r - bordure);
            if (M.estChaussee(Math.floor(elle.x / TT), Math.floor(elle.y / TT))) auCentre++;
            dmin = Math.min(dmin, Math.hypot(elle.x - homme.x, elle.y - homme.y));
        }
        // 1. Elle bute contre lui, et pousse, cinq secondes.
        for (let k = 0; k < 300; k++) { L.B.partie.heure = 0.5; vider(null); mesurer(); o.frame(1); }
        mesurer();
        const avantLeChar = { mord: +mord.toFixed(2), y: +(elle.y - s.ty * TT).toFixed(2) };
        // 2. Un char du trafic arrive sur la voie du bord, six tuiles en amont.
        const v = L.Vehicules.creer('auto', (s.tx + s.p * 6) * TT + 8, (s.ty + 1) * TT + 8, s.sens === '<' ? Math.PI : 0,
                                    { conducteur: 'trafic', etat: 'roule', sens: s.sens });
        const avance = function () { return (v.x - homme.x) * s.p; };     // > 0 : pas encore passé
        let pourElle = 0, force = 0, arret = 0;
        for (let k = 0; k < 300; k++) {
            L.B.partie.heure = 0.5; vider(v); mesurer();
            o.frame(1);
            if (avance() > 0) {
                if (v.devant === elle) pourElle++;
                if (v.force > 0) force++;
                if (Math.abs(v.vitesse) < 0.05) arret++;
            }
        }
        mesurer();
        return { trouve: true, avantLeChar: avantLeChar, mord: +mord.toFixed(2), auCentre: auCentre,
                 dmin: +dmin.toFixed(2), rayons: elle.r + homme.r, pourElle: pourElle, force: force,
                 arret: arret, passe: avance() < 0, present: L.B.entites.indexOf(v) >= 0 };
    }""")
    assert r["trouve"], "aucun trottoir droit au bord d'une voie droite : le juge ne prouve rien"
    assert r["mord"] <= 0, (
        f"démêlée contre un corps figé, la passante mord la chaussée de {r['mord']} px "
        f"({r['auCentre']} images le centre dessus ; avant le char : {r['avantLeChar']})"
    )
    assert r["dmin"] > r["rayons"] - 1.5, f"elle lui passe au travers : {r['dmin']} px entre les centres"
    assert r["present"] and r["passe"], f"le char n'a pas passé l'homme au bord du trottoir : {r}"
    assert r["pourElle"] == 0 and r["force"] == 0, f"le char s'arrête pour elle, ou force le passage : {r}"


def test_la_rue_se_peuple_puis_s_oublie(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(600);
        const j = L.B.joueur;
        // ⚠️ Les marchands derriere leur kiosque ne sont pas la foule.
        const pietons = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const loin = pietons.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) > L.Entites.BULLE_OUBLI + 80;
        });
        const dansLEcran = pietons.filter(function (e) { return L.Entites.visibleAEcran(e.x, e.y, 0); });
        // On se teleporte a l'autre bout : la foule doit suivre, pas rester la.
        // ⚠️ « L'autre bout » reste la VILLE, pas le relief (`relief.py`, 21 sept.
        // 2026) : sa chaine de montagnes, a l'est, est infranchissable — personne
        // n'y nait, n'y marche ni n'y suit personne.
        const c = L.Monde.carte;
        const largeurRelief = c.def.relief ? c.def.relief.montagnes.l * L.TT : 0;
        j.x = c.pxW - largeurRelief - 200; j.y = c.pxH - 200;
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(600);
        const apres = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const proches = apres.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) < L.Entites.BULLE_OUBLI;
        });
        return { avant: pietons.length, loin: loin.length, vus: dansLEcran.length,
                 apres: apres.length, proches: proches.length, max: L.Entites.MAX_PIETONS,
                 sol: apres.map(function (e) { return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)); }) };
    }""")
    # +1 : une mere nait avec son petit, et la bulle compte les vivants AVANT.
    assert 4 <= r["avant"] <= r["max"] + 1, "la rue est vide ou bondee"
    assert r["loin"] == 0, "des pietons trainent hors de la bulle"
    assert r["vus"] > 0, "personne a l'ecran"
    assert r["proches"] == r["apres"] > 0, "la foule n'a pas suivi le joueur"
    assert all(s in (0, 3) for s in r["sol"]), "un pieton est ne dans un mur"


def test_un_enfant_ne_peut_pas_etre_touche(banc):
    """⚠️ Regle du moteur, pas consigne : RIEN n'atteint un enfant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur;
        // ⚠️ **LA RUE SE VIDE** : six coups de couteau touchent TOUT ce qui est à
        // portée, et un passant de plus à côté de l'enfant met un mort au compteur
        // que ce juge veut à zéro (17 sept. 2026, la trame a bougé).
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const petit = o.poser('enfant', 12, 0);
        o.viser(petit);
        const avant = petit.vie;
        // Au poing, au couteau, et d'une balle en pleine poitrine.
        j.arme = 'couteau'; L.B.partie.armes.couteau = { mun: null, usure: 0 };
        for (let coup = 0; coup < 6; coup++) {
            L.Combat.frapper(j, true);
            for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
        }
        const auCouteau = petit.vie;
        const direct = L.Entites.blesser(petit, 999, j, {});
        return { avant: avant, auCouteau: auCouteau, direct: direct,
                 vivant: petit.vivant, etat: petit.etat, tues: L.B.partie.stats.tues,
                 intouchable: petit.intouchable, sprite: petit.sprite };
    }""")
    assert r["intouchable"] is True and r["sprite"] == "enfant"
    assert r["auCouteau"] == r["avant"], "un enfant a perdu de la vie"
    assert r["direct"] is False, "blesser() a accepte de toucher un enfant"
    assert r["vivant"] is True and r["tues"] == 0
    assert r["etat"] == "fuit", "il devrait detaler"


def test_la_mere_ne_sort_pas_sans_son_petit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        const mere = o.poser('mere', 30, 0);
        mere.etat = 'flane';
        const petit = mere.petit;
        // On eloigne le petit : il doit revenir vers elle.
        petit.x = mere.x + 120; petit.y = mere.y + 80;
        const avant = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        o.frame(240);
        const apres = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        return { arch: petit ? petit.arch : null, avant: avant, apres: apres,
                 suit: petit.suit === mere };
    }""")
    assert r["arch"] == "enfant", "la mere est sortie sans son petit"
    assert r["suit"] is True
    assert r["apres"] < r["avant"], "le petit ne rejoint pas sa mere"


def test_la_fille_de_la_brume_a_une_silhouette_a_elle(banc):
    """⚠️ Retour de Martin : « on ne distingue plus les prostituées, elles sont
    trop pareilles que tout le monde. » Elles etaient le corps commun repeint
    en rose — et a douze pixels de large, sous la teinte de nuit, une couleur
    ne distingue rien. Ce juge tient le CONTOUR : la jupe s'evase plus large
    que les epaules (personne d'autre), et sous l'ourlet les jambes sont de la
    peau la ou tout le monde a du pantalon."""
    r = banc(r"""function (L, o) {
        // La largeur de chaque rangee du dessin de face, pixels poses.
        function largeurs(nom) {
            return L.SPRITES[nom].poses.bas[0].map(function (l) { return l.replace(/\./g, '').length; });
        }
        const f = largeurs('racoleuse'), j = largeurs('joueur');
        const jambes = L.SPRITES.racoleuse.poses.bas[0][13];
        L.Jeu.commencer();
        const fille = o.poser('racoleuse', 12, 0);
        return { sprite: fille.sprite, epaulesF: f[7], jupeF: Math.max(f[11], f[12], f[13]),
                 epaulesJ: j[7], hanchesJ: Math.max(j[11], j[12], j[13]),
                 jambes: jambes, cheveux: fille.swaps.h, robe: fille.swaps.c,
                 poses: Object.keys(L.Atlas.cuire('racoleuse', L.SPRITES.racoleuse, null).poses).sort() };
    }""")
    assert r["sprite"] == "racoleuse", "elle porte encore le corps de tout le monde"
    assert r["jupeF"] - r["epaulesF"] >= 4, "la jupe ne s'evase pas : de loin, c'est un passant"
    assert r["hanchesJ"] - r["epaulesJ"] <= 1, "le corps commun, lui, tombe droit — c'est le contraste"
    assert "s" in r["jambes"] and "p" not in r["jambes"], "les jambes ne sont pas nues sous l'ourlet"
    assert r["cheveux"] == "#f2d27a" and r["robe"] == "#ff3d8e"
    # ⚠️ Elle meurt comme les autres : sans `couche`, un KO restait debout.
    for pose in ("bas", "haut", "cote", "gauche", "droite", "couche"):
        assert pose in r["poses"], pose


def test_la_fille_de_la_brume_tient_son_coin(banc):
    """Le deuxieme signe, celui qu'on lit avant meme la robe : elle ATTEND.
    Elle flanait comme tout le monde dix secondes apres etre apparue.

    ⚠️ **On mesure jusqu'a sa premiere FUITE, pas au-dela.** Le juge prenait
    son écart maximum sur quarante secondes, fuite comprise : une fille qui
    détale d'un coup de feu court 240 px — et c'est exactement ce qu'elle doit
    faire. Une fois partie, elle ne revient pas : la fuite lui fait traverser
    une rue, et un passant ne remet pas le pied sur la chaussée hors d'un
    passage. Le juge a donc rougi le jour où les lampadaires ont bougé de trois
    tuiles ; aucune ligne de *son* code n'avait changé, mais la ville autour
    d'elle oui, et avec elle ce qui l'effraie. Il tenait par chance.

    Ce que le poste promet, et la seule chose : **tant que rien ne lui fait
    peur, elle ne flâne pas au loin.** Le juge le dit maintenant, et il exige
    aussi d'avoir eu de quoi regarder — sinon une fuite à la troisième seconde
    le ferait passer sans rien mesurer.

    ⚠️ **SIX ESSAIS, UNE GRAINE CHACUN** (16 sept. 2026, le métro). Mesuré sur
    un seul essai, le contraste avec la passante tenait par l'ordre des dés : sur
    la base seule, décaler TROIS dés faisait marcher la fille 554 px et la
    passante 121 — la passante marche entre 121 et 1 383 px selon le tirage.
    Une probabilité se mesure avec une graine par essai. Sur six : avec son
    poste, la passante marche au moins 1,5 fois plus qu'elle (douze mesures, la
    base et le métro, six décalages de dés) ; sans poste, le rapport tombe à
    1,0. Et une fois sur trente-six, elle s'écarte de 510 px sans fuir — d'où
    « cinq essais sur six », et pas six.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const essais = [];
        for (let n = 0; n < 6; n++) {
            L.graine(34 + n);
            const fille = o.poser('racoleuse', 20, 0);
            const passante = o.poser('passante', -20, 0);
            fille.etat = 'flane'; passante.etat = 'flane';
            const p0 = { x: fille.x, y: fille.y };
            let ecart = 0, chemin = 0, cheminPassante = 0, arrets = 0, calmes = 0, fuite = false;
            let px = passante.x, py = passante.y, fx = fille.x, fy = fille.y;
            for (let i = 0; i < 80; i++) {
                o.frame(30);
                if (fille.etat === 'fuit') fuite = true;
                if (!fuite) {
                    calmes++;
                    if (fille.etat === 'arret') arrets++;
                    ecart = Math.max(ecart, Math.hypot(fille.x - p0.x, fille.y - p0.y));
                    chemin += Math.hypot(fille.x - fx, fille.y - fy);
                    // ⚠️ La passante se mesure SUR LA MEME FENETRE : comparer 40 s
                    // de flanerie a 13 s de faction ne compare rien.
                    cheminPassante += Math.hypot(passante.x - px, passante.y - py);
                }
                fx = fille.x; fy = fille.y;
                px = passante.x; py = passante.y;
            }
            essais.push({ poste: !!fille.poste, calmes: calmes, arrets: arrets, ecart: Math.round(ecart),
                          chemin: Math.round(chemin), passante: Math.round(cheminPassante) });
            L.Entites.retirer(fille); L.Entites.retirer(passante);
        }
        return essais;
    }""")
    assert all(e["poste"] for e in r), "elle n'a pas de coin a tenir"
    # ⚠️ VINGT RELEVES, soit dix secondes, par essai qui compte : c'est la
    # fenetre que la fiche nomme — « elle se remettait a flaner au bout de dix
    # secondes ». En deca, l'essai n'a rien vu.
    vus = [e for e in r if e["calmes"] >= 20]
    assert len(vus) >= 4, f"seulement {len(vus)} essais avant qu'elle prenne peur : le juge n'a rien mesure"
    au_coin = sum(1 for e in vus if e["ecart"] < 80)
    assert au_coin >= len(vus) - 1, (
        f"tant que rien ne l'effraie, elle ne doit pas quitter son coin : {[e['ecart'] for e in vus]}")
    # ⚠️ On mesure le CHEMIN, pas l'ecart au depart : une flaneuse qui revient
    # sur ses pas fait un long chemin et un petit ecart.
    fille = sum(e["chemin"] for e in vus)
    passante = sum(e["passante"] for e in vus)
    assert passante > 100 * len(vus), "⚠️ une passante, elle, doit continuer de flaner"
    # ⚠️ ET C'EST LE CONTRASTE QUI COMPTE, sur la SOMME des essais : la passante
    # marche plus de 1,3 fois ce que marche la fille. Avec son poste, le rapport
    # ne descend pas sous 1,5 ; sans, il est a 1,0.
    assert passante > 1.3 * fille, f"elle marche autant qu'une passante : {fille} px contre {passante}"
    arrets = sum(e["arrets"] for e in vus)
    calmes = sum(e["calmes"] for e in vus)
    assert arrets > calmes * 0.5, (
        f"elle attend {arrets} releves sur {calmes} : elle flane au lieu de tenir son coin"
    )


def test_la_rumeur_suit_la_foule_et_les_passants_parlent(banc):
    """Une rue vide se tait, une rue pleine murmure ; et le passant qui nous
    frôle tente de parler. ⚠️ Deux des trois affirmations se contentaient de
    `typeof … === 'function'` : une rumeur figée à plein volume passait.
    Le suivi fin (volume = foule du moment, la peur, le cri) est jugé par
    `test_parole.py::test_la_rue_se_tait_devant_une_arme_et_crie_apres_un_coup_de_feu` ;
    ici, les deux bouts."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur;
        // Sans audio sous Node : on verifie la mecanique, pas le son.
        const p = o.poser('passante', 12, 0);
        p.etat = 'flane';
        o.frame(2);
        const parle = p.aParle === true;
        // La rumeur ne lit que les gens a 200 px ; on vide ce rayon, puis on
        // y pose une foule figee (`poser`), et on laisse remonter.
        const autour = function () {
            return L.Entites.pietonsAutour(j.x, j.y, 200).filter(function (e) { return !e.metier; });
        };
        autour().forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        o.frame(60);
        const vide = { gens: autour().length, volume: +L.Son.Rumeur.volume.toFixed(3) };
        for (let k = 0; k < 8; k++) o.poser('passante', 40 + 10 * k, 40);
        o.frame(15 * 20);
        const foule = { gens: autour().length, volume: +L.Son.Rumeur.volume.toFixed(3) };
        return { parle: parle, vide: vide, foule: foule };
    }""")
    assert r["parle"] is True, "un passant qui nous frole doit tenter de parler"
    assert r["vide"]["gens"] == 0, "la rue n'est pas vide, le juge ne prouve rien : %s" % r
    assert r["vide"]["volume"] <= 0.02, "une rue vide murmure encore : %s" % r
    assert r["foule"]["gens"] >= 8, "la foule posee s'est dispersee : %s" % r
    assert r["foule"]["volume"] >= 0.6, "huit passants autour et la rue reste muette : %s" % r
