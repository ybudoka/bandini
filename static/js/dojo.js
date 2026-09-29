/* Bandini — le dojo du quartier : LES COURS de Mireille Dion, et la lecon sur le
   tatami (docs/jalons/le-dojo-du-quartier.md).

   Python decide (`app/dojo.py` : les heures, les reussites, la remise en place ; `app/techniques.py` :
   les cours et leurs prix), ce module joue. ⚠️ Aucun `B.rng()` ici : une lecon ne decale
   pas un seul de du reste de la ville. */

const Dojo = (function () {
  'use strict';

  //: Les styles, dans l'ordre du menu : chacun son en-tete.
  const STYLES = [['boxe', 'BOXE'], ['karate', 'KARATÉ'], ['judo', 'JUDO'], ['jiujitsu', 'JIU-JITSU']];

  function regles() { return B.defs.dojo; }

  //: La carte de la lecon : ce qu'on fait, BOUTON compris. Une action d'`Entree` (en minuscules)
  //: se dessine pour l'appareil qu'on tient ; le reste est un mot. Martin, 28 sept. : « trop dur
  //: et pas clair » — les annonces de Mireille disent la hanche et la jambe, jamais le bouton.
  //: ⚠️ Ici, pas dans `app/dojo.py` : le paquet des definitions est a son plafond
  //: (`test_definitions`), et c'est de l'affichage.
  const RECETTES = {
    uppercut: ['FRAPPE', 'attaque'],
    pied_circulaire: ['FRAPPE', 'attaque'],
    pied_de_cote: ['TIENS', 'attaque', '... PUIS LÂCHE'],
    pied_saute: ['COURS VERS LUI', 'esquive', '+', 'attaque'],
    balayage: ['IL ATTAQUE : ROULE', 'esquive', 'PUIS', 'attaque'],
    projection_hanche: ['SAISIS', 'saisir', '+ POUSSE VERS LUI'],
    grand_fauchage: ['SAISIS', 'saisir', '+ TIRE VERS TOI'],
    sacrifice: ['SAISIS', 'saisir', '+ POUSSE DE CÔTÉ'],
    retournement_poignet: ['IL ARME SON COUP :', 'saisir'],
    etranglement: ['DANS SON DOS : TIENS', 'saisir', "JUSQU'AU BOUT"],
  };
  const ACTIONS = ['attaque', 'saisir', 'esquive'];

  /** Les pieces de la carte de `slug` : { action, glyphe } pour un bouton (au doigt, sans
      glyphe, le nom du bouton tactile dans `texte`), { texte } pour un mot. */
  function carte(slug) {
    return (RECETTES[slug] || []).map(function (m) {
      if (ACTIONS.indexOf(m) < 0) return { texte: m };
      const g = Hud.glypheDAction(m);
      return g ? { action: m, glyphe: g } : { action: m, texte: Entree.etiquettesTactiles('pied')[m] };
    });
  }

  /** Le maillon d'avant, pour une tape de la chaine : le circulaire (rang 5) attend l'uppercut. */
  function avant(t) {
    if (t.geste !== 'tape' || t.rang <= 1) return null;
    return (B.defs.techniques || []).find(function (q) { return q.geste === 'tape' && q.rang === t.rang - 1; }) || null;
  }

  /** Ou en est ce cours : 'appris', 'paye' (a reprendre), 'verrouille' (le maillon d'avant
      manque) ou 'a_vendre'. */
  function etatDuCours(slug) {
    const p = B.partie, t = Techniques.def(slug);
    if (p.techniques && p.techniques[slug]) return 'appris';
    if (p.coursPayes && p.coursPayes[slug]) return 'paye';
    const a = avant(t);
    // Le maillon d'avant se lit dans ce que la PARTIE sait (pas `Techniques.sait`, qui compte
    // la technique d'une lecon en cours comme sue).
    if (a && !a.gratuite && !(p.techniques && p.techniques[a.slug])) return 'verrouille';
    return 'a_vendre';
  }

  /** La nuit, le MENU ferme (comme tous les comptoirs du jeu), pas la porte. */
  function ferme() { return !Missions.ouvert({ heures: regles().heures }); }

  /** Payer (une fois) et commencer. Rend true si la lecon part. ⚠️ Un cours abandonne reste
      PAYE : on recommence sans repayer. */
  function acheter(slug) {
    // Une lecon a la fois : pendant l'uppercut, l'uppercut « se sait » — le circulaire ne
    // s'achete pas pour autant, et une lecon n'en remplace pas une autre.
    if (B.cours) return false;
    const etat = etatDuCours(slug), t = Techniques.def(slug);
    if (ferme() || etat === 'appris' || etat === 'verrouille') return false;
    if (etat === 'a_vendre') {
      if (!Missions.payer(t.prix, t.nom.toUpperCase())) return false;
      B.partie.coursPayes = B.partie.coursPayes || {};
      B.partie.coursPayes[slug] = true;
    }
    return commencer(slug);
  }

  /** ACTION pres de Mireille. La premiere fois : sa salutation, sa voix, son visage. Ensuite :
      LES COURS, et sa replique d'accueil (dite, pas affichee — le menu s'affiche). */
  function accueillir(premiere) {
    const m = (B.defs.personnages || []).find(function (q) { return q.slug === 'mireille'; });
    const texte = (regles().repliques || {}).salut;
    if (premiere && texte) {
      Hud.dialogue(m ? m.nom : 'MIREILLE', [texte], 360, { slug: 'mireille', humeur: 'neutre' });
      Son.Voix.chargerHistoire('dojo');
      if (Son.Voix.parler('mireille-dojo-salut', {}) && B.dialogue) B.dialogue.voix = true;
      return;
    }
    Hud.ouvrirMenu(menuCours());
    Son.Voix.chargerHistoire('dojo');
    Son.Voix.parler(ferme() ? 'mireille-dojo-ferme' : 'mireille-dojo-cours', {});
  }

  function menuCours() {
    const items = [];
    if (ferme()) {
      items.push({ libelle: 'FERMÉ — OUVRE À ' + Math.round(regles().heures[0] * 24) + ' H', actif: false });
      return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
    }
    for (const [style, titre] of STYLES) {
      items.push({ entete: titre, libelle: '', actif: false });
      for (const t of (B.defs.techniques || []).filter(function (q) { return q.style === style; })) {
        const etat = etatDuCours(t.slug), a = avant(t);
        const detail = { appris: 'APPRIS', paye: 'PAYÉ — À REPRENDRE',
                         verrouille: 'APRÈS ' + (a ? a.nom.toUpperCase() : ''), a_vendre: t.prix + ' $' }[etat];
        items.push({ libelle: t.nom.toUpperCase(), detail: detail,
                     actif: etat === 'a_vendre' || etat === 'paye',
                     // Une lecon qui part FERME le menu (`true`) : on est sur le tatami.
                     faire: function () { return acheter(t.slug); } });
      }
    }
    return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
  }

  // --- La lecon sur le tatami ---------------------------------------------------------
  //: `B.cours` : { slug, essai, lance, vu, reussis, remise, armeT, kevin, marque, dit, ditT }.
  //: ⚠️ A SON RYTHME (docs/jalons/le-dojo-apprendre-a-son-rythme.md) : ni metronome ni fenetre,
  //: ni rates qui arretent la lecon — on reste sur le tatami tant qu'on veut.
  //: ⚠️ Elle ne SURVIT a rien : une porte, la mort, une scene — `maj` la defait des que le
  //: joueur n'est plus au dojo. Le cours, lui, reste paye.

  function kevin() { return B.entites.find(function (e) { return e.partenaire && e.vivant; }) || null; }
  function mireille() { return B.entites.find(function (e) { return e.personnage === 'mireille'; }) || null; }

  /** Ce que Mireille dit : sa voix (`mireille-dojo-<cle>`), et, pour les repliques qui
      s'AFFICHENT (`dojo.AFFICHEES`), la boite du message. Sans mp3, le filet : le texte seul. */
  function dire(cle) {
    if (typeof Son !== 'undefined' && Son.Voix) {
      Son.Voix.chargerHistoire('dojo');
      Son.Voix.parler('mireille-dojo-' + cle, {});
    }
    const texte = (regles().repliques || {})[cle];
    if (texte) Hud.message(texte.toUpperCase(), 180);
  }

  function commencer(slug) {
    const piece = B.interieur, k = kevin(), t = Techniques.def(slug);
    if (!piece || piece.slug !== 'dojo' || !piece.tatami || !k || !t) return false;
    const d = regles().distances[(regles().lecons || {})[slug] || 'contact'];
    const cx = piece.tatami.x * TT + 8, cy = piece.tatami.y * TT + 8;
    B.cours = { slug: slug, essai: false, lance: false, vu: false, reussis: 0, remise: 0, armeT: 0,
                kevin: k, dit: '', ditT: 0 };
    Jeu.transiter([10, 10], function () {
      const j = B.joueur;
      j.x = cx - d / 2; j.y = cy; j.vx = 0; j.vy = 0; Entites.regarder(j, 1, 0);
      if (B.cours) B.cours.marque = { x: j.x, y: j.y };
      k.x = cx + d / 2; k.y = cy; k.vx = 0; k.vy = 0; k.etat = 'fige';
      k.marque = { x: k.x, y: k.y };
      // Kevin fait face a Bandini — sauf pour l'etranglement, ou il lui tourne le dos.
      k.regard = lecon(slug) === 'dos' ? { x: 1, y: 0 } : { x: -1, y: 0 };
      Entites.regarder(k, k.regard.x, k.regard.y);
      Entites.indexer();
    }, t.nom.toUpperCase());
    Techniques.quandPorte = quandPorte;
    dire('annonce_' + slug);
    return true;
  }

  function lecon(slug) { return (regles().lecons || {})[slug] || 'contact'; }

  /** Le moteur des techniques : `auteur` vient de PORTER `slug` sur `cible`. ⚠️ Retenu meme
      avant que `maj` ait vu l'essai partir : le retournement du poignet porte a son etape 0,
      dans la meme image que SAISIR. */
  function quandPorte(auteur, slug, cible) {
    const c = B.cours;
    if (!c || auteur !== B.joueur || cible !== c.kevin || slug !== c.slug) return;
    c.vu = true;
  }

  /** Kevin et Bandini reprennent leur marque, face a face (Kevin de dos pour l'etranglement).
      ⚠️ Bandini AUSSI : un coup de pied saute le laissait derriere Kevin, dos a lui (29 sept.). */
  function placer(c) {
    const k = c.kevin, j = B.joueur;
    if (k.marque && k.etat !== 'couche_dojo' && k.etat !== 'attaque') {
      k.x = k.marque.x; k.y = k.marque.y; k.vx = 0; k.vy = 0;
      if (k.regard) Entites.regarder(k, k.regard.x, k.regard.y);
    }
    if (c.marque) { j.x = c.marque.x; j.y = c.marque.y; j.vx = 0; j.vy = 0; Entites.regarder(j, 1, 0); }
    Entites.indexer();
  }

  /** Ce que la lecon demande de Kevin, tant que Bandini ne fait rien : la menace du balayage (il
      attaque, la roulade a une raison de partir), et, pour la parade, un coup arme LENTEMENT, un
      cri pour le dire, a intervalle regulier. */
  function kevinTravaille(c, occupe) {
    const k = c.kevin, r = regles(), l = lecon(c.slug);
    if (k.etat === 'couche_dojo' || k.vol) { c.armeT = 0; return; }
    if (l === 'attaque' && k.etat !== 'attaque') k.etat = 'attaque_joueur';
    if (l !== 'arme' || occupe || k.etat === 'attaque' || c.remise > 0) return;
    if (++c.armeT < r.cadence_arme) return;
    c.armeT = 0;
    if (!Combat.frapper(k, false)) return;
    if (k.phase === 'anticipation') k.techT = Math.max(k.techT, r.anticipation_kevin);
    Entites.bulle(k, 'HA !', { duree: r.anticipation_kevin });
  }

  /** Un essai vient de retomber (ou la technique vient de porter) : OUI, ou « tu danses tout
      seul » si le geste enseigne est parti sans porter. ⚠️ Aucun echec : rien ne se compte
      contre toi, la lecon dure tant que tu veux. Rend vrai si la lecon est finie. */
  function juger(c) {
    const r = regles();
    const vu = c.vu, lance = c.lance;
    c.essai = false; c.lance = false; c.vu = false;
    c.remise = r.remise_images;
    if (vu) {
      c.reussis++; c.dit = 'OUI !'; c.ditT = 40;
      if (c.reussis >= r.reussites) { apprendre(c.slug); return true; }
      dire('oui_' + ((c.reussis - 1) % 2 + 1));
    } else if (lance) {
      c.dit = 'PRESQUE'; c.ditT = 40;
      dire('dans_le_vide');
    }
    return false;
  }

  function maj() {
    const c = B.cours;
    if (!c) return;
    const j = B.joueur;
    if (!B.interieur || B.interieur.slug !== 'dojo' || !j || !j.vivant || B.cinema || !c.kevin.vivant) {
      annuler(null);
      return;
    }
    if (B.transition) return;
    const t = Techniques.def(c.slug), k = c.kevin;
    if (c.ditT > 0) c.ditT--;
    // UN ESSAI : du geste qui part (un coup, une prise, une roulade et ce qui la suit) jusqu'a ce
    // qu'il retombe — et que Kevin, s'il vole, soit retombe aussi.
    const occupe = j.etat === 'attaque' || !!j.prise || j.roule > 0 || j.sortieRoulade > 0;
    if (occupe) {
      c.essai = true; c.remise = 0;
      if (j.technique === c.slug || j.prise) c.lance = true;
    } else if ((c.essai || c.vu) && !k.vol) {
      if (juger(c)) return;
    }
    // Une tape de la chaine : on la garde au maillon d'avant, la tape suivante fait partir CE
    // maillon-la — sans enchainer les trois coups de rue a chaque essai.
    if (!occupe && t.geste === 'tape') { j.chaine = t.rang - 1; j.chaineT = Techniques.FENETRE; }
    // On souffle, puis chacun sur sa marque — pas en pleine course.
    if (c.remise > 0 && !occupe) {
      if (Math.hypot(j.vx, j.vy) > 0.2) c.remise = regles().remise_images;
      else if (--c.remise === 0) placer(c);
    }
    kevinTravaille(c, occupe);
  }

  function apprendre(slug) {
    const t = Techniques.def(slug);
    B.partie.techniques[slug] = true;
    if (B.partie.coursPayes) delete B.partie.coursPayes[slug];
    finir();
    dire('appris');
    Hud.message('TU SAIS ' + (t.nom.toUpperCase()) + ' !', 180);
  }

  /** La lecon s'arrete ; le cours reste paye. `cle` : ce que Mireille en dit (ou rien). */
  function annuler(cle) {
    if (!B.cours) return;
    finir();
    if (cle) dire(cle);
  }

  function finir() {
    const c = B.cours;
    B.cours = null;
    Techniques.quandPorte = null;
    if (c && c.kevin) {
      c.kevin.marque = null; c.kevin.regard = null;
      if (c.kevin.etat === 'attaque_joueur') c.kevin.etat = 'fige';
      if (c.kevin.bulle) Entites.bulle(c.kevin, '');
    }
  }

  /** En haut de l'ecran : « UPPERCUT · 2/3 », la carte de ce qu'on fait, et le dernier mot. */
  function dessiner(ctx) {
    const c = B.cours;
    if (!c || B.transition) return;
    const t = Techniques.def(c.slug), r = regles();
    const titre = t.nom.toUpperCase() + ' · ' + c.reussis + '/' + r.reussites;
    const pieces = carte(c.slug);
    let lc = 0;
    for (const p of pieces) lc += (p.glyphe ? Hud.largeurGlyphe(p.glyphe) : Atlas.largeurTexte(p.texte, 1)) + 4;
    lc -= 4;
    // ⚠️ SOUS les etoiles de recherche (en haut, au centre) : a y = 6, le bandeau les couvrait.
    const l = Math.max(Atlas.largeurTexte(titre, 1), lc) + 16, x = Math.round((VW - l) / 2), y = 26;
    ctx.fillStyle = 'rgba(11,10,18,0.78)'; ctx.fillRect(x, y, l, 30);
    Atlas.texte(ctx, titre, Math.round((VW - Atlas.largeurTexte(titre, 1)) / 2), y + 4, '#efe6d0', 1);
    // La carte : les mots et les boutons de l'appareil qu'on tient, sur une ligne.
    let px = Math.round((VW - lc) / 2);
    for (const p of pieces) {
      if (p.glyphe) px += Hud.dessinerGlyphe(ctx, p.glyphe, px, y + 15) + 4;
      else {
        Atlas.texte(ctx, p.texte, px, y + 17, p.action ? '#e8b33c' : '#efe6d0', 1);
        px += Atlas.largeurTexte(p.texte, 1) + 4;
      }
    }
    if (c.ditT > 0 && c.dit) {
      Atlas.texte(ctx, c.dit, Math.round((VW - Atlas.largeurTexte(c.dit, 1)) / 2), y + 34,
                  c.dit === 'OUI !' ? '#8fd46a' : '#e8b33c', 1);
    }
  }

  return { menuCours, accueillir, etatDuCours, acheter, commencer, maj, annuler, dessiner, carte };
})();
