"""Un choix dans un dialogue (M16, 1er oct. 2026) — JOUÉ au bouton : d09, _Un compte sur l'île_, de chaque côté.

- La question de Léo ouvre la boîte des réponses AU-DESSUS de sa réplique ; ni ACTION, ni le temps, ni PAUSE ni
  Échap ne la passent : on répond (clavier, manette de Martin, doigt).
- « Tout de suite » : deux matelots, Léo qui paie, Sal qui verse sa part (250 $) ; la dette ne bouge pas.
- « Je paie » : 800 $ de sa poche, Sal les enlève de la dette ; pas une cenne de prime.
- La réponse se garde (`partie.mission.branche`, puis `partie.choix`), et une autre mission peut l'exiger.
- Passée sans réponse (une partie reprise), la question se REPOSE avant l'étape qui bifurque."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_d_js import CHEZ_SAL
from test_arc_f_js import DEDANS
from test_arc_i_js import EAU
from test_arc_p_js import RECHARGER
from test_classeur_js import MARTIN

AVANT = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'd01', 'd02', 'd03', 'd04', 'q08', 'i01']"

#: Jusqu'à la question : Sal au terminus, la chaloupe, l'île, la poignée de main de Léo — au bouton.
JUSQU_A_LA_QUESTION = """
  const textes = [];
  const DIALOGUE = L.Hud.dialogue;
  L.Hud.dialogue = function (qui, lignes) { textes.push(lignes.join(' ')); return DIALOGUE.apply(null, arguments); };
  function jusquALaQuestion(L, o) {
    const B = L.B, p = B.partie;
    faites(L, """ + AVANT + """);
    const j = recharger(L);
    p.dette = 14200; p.argent = 1000;
    const argent = paiements(L);
    const chez = chezSal(L, o);
    sortir(L, o);
    const v = B.mission.vehicule;
    embarquer(L, o, v);
    accoster(L, o, v, 'amarrage:hangar_ile');
    aTerre(L, o);
    serrer(L, o, 'leo');
    const q = { mission: chez.mission, etape: etape(L), menu: !!(B.menu && B.menu.choix), titre: B.menu && B.menu.titre,
                reponses: B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null,
                question: !!(B.cinema && B.cinema.question), boite: B.dialogue ? B.dialogue.lignes.join(' ') : null };
    return { q: q, argent: argent, v: v, j: j };
  }
  // Quelques images, sans rien toucher : la boîte des réponses ne choisit rien toute seule.
  function attendre(o, n) { for (let k = 0; k < n; k++) o.frame(1); }
"""

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + EAU + CHEZ_SAL + JUSQU_A_LA_QUESTION


def test_tout_de_suite_deux_matelots_leo_paie_et_sal_verse_sa_part(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const d = jusquALaQuestion(L, o);
        attendre(o, 20);
        o.tape('KeyE', 2); o.frame(2);
        const choisi = { branche: p.mission && p.mission.branche, menu: !!B.menu };
        jouer(L, o, 10);
        const matelots = B.mission.entites.filter(function (e) { return e.cible && e.etape === 3; });
        const pose = { etape: etape(L), n: matelots.length };
        matelots.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const couches = etape(L);
        serrer(L, o, 'leo');
        const paye = etape(L);
        embarquer(L, o, d.v);
        accoster(L, o, d.v, 'amarrage:bar');
        const rentre = etape(L);
        aTerre(L, o);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { q: d.q, choisi: choisi, pose: pose, couches: couches, paye: paye, rentre: rentre, textes: textes,
                 fait: !!p.missionsFaites.d09, choix: p.choix.d09, dette: p.dette,
                 argent: d.argent.map(function (a) { return a.montant; }) };
    }""")
    q = r["q"]
    assert q["mission"] == "d09" and q["etape"] == 2, q
    assert q["menu"] and q["question"] and q["titre"] == "TA RÉPONSE", q
    assert q["reponses"] == ["SAL VEUT SON ARGENT. TOUT DE SUITE.", "LAISSE FAIRE. JE PAIE TES 800 $."], q
    assert q["boite"].startswith("Huit cents? J'ai un hangar vide"), f"la question reste lisible sous les réponses : {q}"
    assert r["choisi"] == {"branche": "coucher", "menu": False}, r["choisi"]
    assert r["pose"] == {"etape": 3, "n": 2}, r["pose"]
    assert r["couches"] == 4 and r["paye"] == 6 and r["rentre"] == 7, r
    dites = " | ".join(r["textes"])
    assert "Tout de suite? Ben les gars du hangar" in dites and "Pour moé?" not in dites, dites
    assert "Tiens, ta part." in dites and "Huit cents de ta poche" not in dites, dites
    assert r["fait"] is True and r["choix"] == "coucher" and r["argent"] == [250] and r["dette"] == 14200, r


def test_je_paie_huit_cents_de_ma_poche_et_sal_les_enleve_de_la_dette(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const d = jusquALaQuestion(L, o);
        attendre(o, 20);
        o.tape('ArrowDown', 2); o.frame(2);
        const curseur = B.menu ? B.menu.curseur : null;
        o.tape('KeyE', 2); o.frame(2);
        const choisi = p.mission && p.mission.branche;
        jouer(L, o, 10);
        const apres = { etape: etape(L), argent: p.argent, matelots: B.mission.entites.filter(function (e) { return e.cible; }).length };
        embarquer(L, o, d.v);
        accoster(L, o, d.v, 'amarrage:bar');
        aTerre(L, o);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { curseur: curseur, choisi: choisi, apres: apres, textes: textes, fait: !!p.missionsFaites.d09,
                 choix: p.choix.d09, dette: p.dette, argentFinal: p.argent,
                 argent: d.argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["curseur"] == 1 and r["choisi"] == "payer", r
    assert r["apres"] == {"etape": 6, "argent": 200, "matelots": 0}, f"800 $ payés, et personne à coucher : {r['apres']}"
    dites = " | ".join(r["textes"])
    assert "Pour moé?" in dites and "les gars du hangar" not in dites, dites
    assert "Huit cents de ta poche" in dites and "Je les enlève de ta dette." in dites and "Tiens, ta part." not in dites, dites
    assert r["fait"] is True and r["choix"] == "payer" and r["dette"] == 13400, r
    assert sum(r["argent"]) == 0 and r["argentFinal"] == 200, f"pas une cenne de prime : {r}"


def test_la_question_attend_sa_reponse_puis_la_manette_de_martin_repond(banc):
    """Ni ACTION (qui passe une réplique), ni le temps de lire, ni PAUSE, RETOUR, FRAPPE ou la CARTE ne passent une question : la
    boîte des réponses est `obligatoire`. Puis la manette de Martin (8BitDo en Bluetooth, croix sur l'axe 9) descend
    d'une ligne et répond."""
    r = banc("function (L, o) {" + AIDES + MARTIN + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const d = jusquALaQuestion(L, o);
        // La boîte vient de s'ouvrir (ses images sourdes, comme sous un pouce qui martelait ACTION) : rien.
        B.menu.sourd = L.Histoire.CHOIX_SOURD;
        o.tape('KeyE', 2);
        const sourd = { branche: p.mission.branche || null, menu: !!B.menu };
        attendre(o, 900);                        // quinze secondes : la voix est finie depuis longtemps
        o.tape('Escape', 2); o.tape('Backspace', 2); o.tape('Space', 2); o.tape('KeyN', 2);   // PAUSE, RETOUR, FRAPPE, CARTE
        const tient = { branche: p.mission.branche || null, menu: !!(B.menu && B.menu.choix), question: !!(B.cinema && B.cinema.question),
                        etape: etape(L), etat: B.etat };
        martin(L);
        const BAS = 0.14285714285714285;
        croix(o, BAS);
        const curseur = B.menu ? B.menu.curseur : null;
        bouton(o, 0);
        return { q: d.q, sourd: sourd, tient: tient, curseur: curseur, branche: p.mission && p.mission.branche,
                 menu: !!B.menu, appareil: L.Entree.appareil };
    }""")
    assert r["q"]["menu"], r["q"]
    assert r["sourd"] == {"branche": None, "menu": True}, f"l'ACTION d'avant a choisi : {r['sourd']}"
    assert r["tient"] == {"branche": None, "menu": True, "question": True, "etape": 2, "etat": "jeu"}, r["tient"]
    assert r["curseur"] == 1 and r["branche"] == "payer" and r["menu"] is False, r


def test_on_repond_du_doigt(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        jusquALaQuestion(L, o);
        attendre(o, 20);
        L.Jeu.rendre();
        const zone = L.Hud.ciblesDuMenu().find(function (z) { return z.item === 1; });
        L.Hud.toucherMenu(zone.x + 4, zone.y + 4); o.frame(2);
        return { zone: !!zone, branche: p.mission && p.mission.branche, menu: !!B.menu };
    }""")
    assert r == {"zone": True, "branche": "payer", "menu": False}, r


def test_la_reponse_se_garde_dans_la_partie(banc):
    """Répondu : la branche vit dans la mission en cours (`partie.mission.branche`, sauvée avec elle) ; la mission
    faite, la réponse reste dans la partie (`partie.choix`) — sauvée, et retrouvée après un rechargement."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const d = jusquALaQuestion(L, o);
        attendre(o, 20);
        o.tape('ArrowDown', 2); o.frame(2); o.tape('KeyE', 2); o.frame(2);
        jouer(L, o, 10);
        L.Missions.sauvegarderPartie();
        const sauvee = JSON.parse(JSON.stringify(p.mission));
        embarquer(L, o, d.v); accoster(L, o, d.v, 'amarrage:bar'); aTerre(L, o);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        L.Missions.sauvegarderPartie();
        recharger(L);
        return { sauvee: { slug: sauvee.slug, branche: sauvee.branche }, choix: L.B.partie.choix,
                 fait: !!L.B.partie.missionsFaites.d09 };
    }""")
    assert r["sauvee"] == {"slug": "d09", "branche": "payer"}, r
    assert r["fait"] is True and r["choix"].get("d09") == "payer", r


def test_une_question_passee_se_repose_avant_l_etape_qui_bifurque(banc):
    """Une partie qui arrive à la poignée de main sans avoir répondu (la question sautée) : l'étape d'après ne se
    joue pas sur une branche au hasard — la question se repose, sa réplique et ses réponses."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """);
        recharger(L);
        commencer(L, o, 'd09');
        p.mission.etape = 2;
        L.Histoire.avancer();
        const redemande = { etape: etape(L), menu: !!(B.menu && B.menu.choix), boite: B.dialogue ? B.dialogue.lignes.join(' ') : null };
        attendre(o, 20);
        o.tape('KeyE', 2); o.frame(2);
        jouer(L, o, 10);
        return { redemande: redemande, branche: p.mission.branche, etape: etape(L) };
    }""")
    assert r["redemande"]["etape"] == 2 and r["redemande"]["menu"], r
    assert r["redemande"]["boite"].startswith("Huit cents?"), r
    assert r["branche"] == "coucher" and r["etape"] == 3, r


def test_une_mission_peut_exiger_ce_qu_on_a_repondu(banc):
    """`exige.choix` : une mission ne s'offre qu'à qui a donné CETTE réponse (une fiche de banc, pas une du
    catalogue)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        const exige = { choix: { d09: 'payer' } };
        const sans = L.Histoire.exigeTenu(exige);
        p.choix.d09 = 'coucher';
        const autre = L.Histoire.exigeTenu(exige);
        p.choix.d09 = 'payer';
        const bonne = L.Histoire.exigeTenu(exige);
        return { sans: sans, autre: autre, bonne: bonne };
    }""")
    assert r == {"sans": False, "autre": False, "bonne": True}, r


def test_une_question_posee_dans_une_scene_se_repond_et_pause_ne_la_passe_pas(banc):
    """Une question peut se poser SOUS une scène (une intro) : la boîte des réponses répond aux boutons pendant que
    la scène attend, et PAUSE — qui passe une scène — ne passe pas par-dessus une réponse qu'on n'a pas donnée."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """);
        commencer(L, o, 'd09');
        const m = L.Histoire.mission('d09');
        const question = m.dialogue.accueil[0];
        L.Scenes.jouer([{ type: 'dire' }, { type: 'attendre', duree: 30 }], {
          mission: m, lignes: [{ qui: 'leo', texte: question.texte, choix: question.choix, slug: 'leo-d09-14' }] });
        for (let k = 0; k < 20; k++) o.frame(1);
        const ouverte = { scene: !!B.scene, menu: !!(B.menu && B.menu.choix) };
        o.tape('Escape', 2);
        const apresPause = { scene: !!B.scene, menu: !!(B.menu && B.menu.choix) };
        o.tape('ArrowDown', 2); o.frame(1); o.tape('KeyE', 2);
        for (let k = 0; k < 200 && B.scene; k++) o.frame(1);
        return { ouverte: ouverte, apresPause: apresPause, branche: p.mission.branche, scene: !!B.scene };
    }""")
    assert r["ouverte"] == {"scene": True, "menu": True}, r
    assert r["apresPause"] == {"scene": True, "menu": True}, f"PAUSE a passé la question : {r}"
    assert r["branche"] == "payer" and r["scene"] is False, r
