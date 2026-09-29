/* Bandini — le dojo du quartier : LES COURS de Mireille Dion, et la lecon sur le
   tatami (docs/jalons/le-dojo-du-quartier.md).

   Python decide (`app/dojo.py` : les heures, le temps, les reussites ; `app/techniques.py` :
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
    pied_de_cote: ['TIENS', 'attaque', '... LÂCHE SUR LE ET'],
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

  /** Payer (une fois) et commencer. Rend true si la lecon part. ⚠️ Un cours rate reste
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
  //: `B.cours` : { slug, t, ouverte, fenetre, lance, vu, attend, reussis, rates, kevin, dit, ditT }.
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
    B.cours = { slug: slug, t: 0, ouverte: 0, fenetre: false, lance: false, vu: false, attend: false,
                tente: false, occupe: false, reussis: 0, rates: 0, kevin: k, dit: '', ditT: 0 };
    Jeu.transiter([10, 10], function () {
      const j = B.joueur;
      j.x = cx - d / 2; j.y = cy; j.vx = 0; j.vy = 0; Entites.regarder(j, 1, 0);
      if (B.cours) B.cours.marque = { x: j.x, y: j.y };
      k.x = cx + d / 2; k.y = cy; k.vx = 0; k.vy = 0; k.etat = 'fige';
      k.marque = { x: k.x, y: k.y };
      // Kevin fait face a Bandini — sauf pour l'etranglement, ou il lui tourne le dos.
      k.regard = (regles().lecons || {})[slug] === 'dos' ? { x: 1, y: 0 } : { x: -1, y: 0 };
      Entites.regarder(k, k.regard.x, k.regard.y);
      Entites.indexer();
    }, t.nom.toUpperCase());
    Techniques.quandPorte = quandPorte;
    dire('annonce_' + slug);
    return true;
  }

  /** Le moteur des techniques : `auteur` vient de PORTER `slug` sur `cible`. */
  function quandPorte(auteur, slug, cible) {
    const c = B.cours;
    // ⚠️ `c.fenetre` AUSSI : une technique dont l'etape 0 porte (le retournement du poignet)
    // porte dans la meme image que SAISIR — avant que `maj` ait note le geste lance.
    if (!c || auteur !== B.joueur || cible !== c.kevin || slug !== c.slug || !(c.lance || c.fenetre)) return;
    c.vu = true;
  }

  /** Avant chaque « et » : Kevin a sa marque, et ce que le cours demande de lui. */
  function miseEnPlace(c) {
    const k = c.kevin, t = Techniques.def(c.slug), lecon = (regles().lecons || {})[c.slug] || 'contact';
    if (k.marque && k.etat !== 'couche_dojo') { k.x = k.marque.x; k.y = k.marque.y; }
    if (k.regard) Entites.regarder(k, k.regard.x, k.regard.y);
    if (t.geste === 'tape') {
      // La chaine au maillon d'avant : la tape fait partir CE maillon-la.
      B.joueur.chaine = t.rang - 1; B.joueur.chaineT = Techniques.FENETRE;
    }
    if (lecon === 'arme' && k.etat !== 'couche_dojo') Combat.frapper(k, false);
    if (lecon === 'attaque' && k.etat !== 'couche_dojo') k.etat = 'attaque_joueur';
  }

  function juger(c) {
    const r = regles();
    c.attend = false;
    // Un « et » sans un geste n'est pas un rate : on cherchait peut-etre le bouton.
    const tente = c.tente; c.tente = false;
    if (!c.vu && !tente) return false;
    if (c.vu) { c.reussis++; c.dit = 'OUI !'; dire('oui_' + ((c.reussis - 1) % 2 + 1)); }
    else { c.rates++; c.dit = 'RATÉ'; dire('rate_' + ((c.rates - 1) % 2 + 1)); }
    c.ditT = 40;
    if (c.reussis >= r.reussites) { apprendre(c.slug); return true; }
    if (c.rates >= r.rates_max) { annuler('reprendre'); return true; }
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
    // Une TENTATIVE : un geste qui part (le coup, la prise, la roulade) — au front, pour
    // qu'un coup qui dure ne se compte pas deux fois.
    const occupe = j.etat === 'attaque' || !!j.prise || j.roule > 0;
    if (occupe && !c.occupe) c.tente = true;
    c.occupe = occupe;
    const r = regles(), phase = c.t % r.temps_images, temps = Math.floor(c.t / r.temps_images) % 3;
    // Au debut de chaque « un », Bandini reprend SA marque, face a Kevin — comme Kevin la sienne.
    // ⚠️ Sans elle, un coup de pied saute parti trop tot le laissait DERRIERE Kevin, dos a lui, et
    // tous les essais suivants rataient (Martin, 29 sept. : « trop difficile »). Pas en plein geste.
    if (temps === 0 && phase === 0 && c.marque && !occupe && !c.attend) {
      j.x = c.marque.x; j.y = c.marque.y; j.vx = 0; j.vy = 0;
      Entites.regarder(j, 1, 0);
      Entites.indexer();
    }
    // Le metronome : deux claquements de bois, puis un fort sur le « et ».
    if (phase === 0 && typeof Son !== 'undefined') Son.SFX.claquement(temps === 2);
    if (c.ditT > 0) c.ditT--;
    const ouverte = temps === 2 && phase < r.fenetre_images;
    if (ouverte && !c.fenetre) {
      if (c.attend) juger(c);          // un geste lance au temps d'avant : juge avant le suivant
      if (!B.cours) return;
      c.fenetre = true; c.ouverte++; c.vu = false; c.lance = false;
      miseEnPlace(c);
    }
    // Pendant la fenetre, on note si le geste est LANCE : la technique elle-meme, ou la prise
    // qui la precede. Elle peut PORTER plus tard (un vol, un etranglement qui tient).
    if (c.fenetre && (j.technique === c.slug || j.prise)) c.lance = true;
    if (!ouverte && c.fenetre) {
      c.fenetre = false;
      if (c.kevin.etat === 'attaque_joueur') c.kevin.etat = 'fige';
      // Lance et pas encore porte : on attend qu'il aboutisse (ou non).
      if (!c.vu && c.lance && (j.technique === c.slug || j.prise)) c.attend = true;
      else if (juger(c)) return;
    }
    if (c.attend && !c.vu && j.technique !== c.slug && !j.prise) { if (juger(c)) return; }
    if (c.attend && c.vu) { if (juger(c)) return; }
    c.t++;
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
    if (c && c.kevin) { c.kevin.marque = null; c.kevin.regard = null; if (c.kevin.etat === 'attaque_joueur') c.kevin.etat = 'fige'; }
  }

  /** En haut de l'ecran : « UPPERCUT · 2/3 », le compte (UN DEUX ET, la barre du « et » qui
      se vide tant qu'il est ouvert), la carte de ce qu'on fait, et le dernier verdict. */
  function dessiner(ctx) {
    const c = B.cours;
    if (!c || B.transition) return;
    const t = Techniques.def(c.slug), r = regles();
    const titre = t.nom.toUpperCase() + ' · ' + c.reussis + '/' + r.reussites;
    const pieces = carte(c.slug);
    let lc = 0;
    for (const p of pieces) lc += (p.glyphe ? Hud.largeurGlyphe(p.glyphe) : Atlas.largeurTexte(p.texte, 1)) + 4;
    lc -= 4;
    const COMPTE = ['UN', 'DEUX', 'ET'];
    const lcompte = Atlas.largeurTexte(COMPTE.join('  '), 1);
    // ⚠️ SOUS les etoiles de recherche (en haut, au centre) : a y = 6, le bandeau les couvrait.
    const l = Math.max(Atlas.largeurTexte(titre, 1), lc, lcompte) + 16, x = Math.round((VW - l) / 2), y = 26;
    ctx.fillStyle = 'rgba(11,10,18,0.78)'; ctx.fillRect(x, y, l, 42);
    Atlas.texte(ctx, titre, Math.round((VW - Atlas.largeurTexte(titre, 1)) / 2), y + 4, '#efe6d0', 1);
    // Le compte : le temps en cours s'allume, le « ET » en or ; sous lui, la fenetre qui se vide.
    const temps = Math.floor(c.t / r.temps_images) % 3, phase = c.t % r.temps_images;
    let cx = Math.round((VW - lcompte) / 2);
    for (let k = 0; k < 3; k++) {
      const allume = k === temps;
      Atlas.texte(ctx, COMPTE[k], cx, y + 13, allume ? (k === 2 ? '#e8b33c' : '#efe6d0') : '#4a4560', 1);
      if (k === 2 && c.fenetre) {
        const lt = Atlas.largeurTexte('ET', 1) + 6, part = 1 - phase / r.fenetre_images;
        ctx.fillStyle = '#e8b33c'; ctx.fillRect(cx - 3, y + 20, Math.max(1, Math.round(lt * part)), 2);
      }
      cx += Atlas.largeurTexte(COMPTE[k] + '  ', 1) + 1;
    }
    // La carte : les mots et les boutons de l'appareil qu'on tient, sur une ligne.
    let px = Math.round((VW - lc) / 2);
    for (const p of pieces) {
      if (p.glyphe) px += Hud.dessinerGlyphe(ctx, p.glyphe, px, y + 27) + 4;
      else {
        Atlas.texte(ctx, p.texte, px, y + 29, p.action ? '#e8b33c' : '#efe6d0', 1);
        px += Atlas.largeurTexte(p.texte, 1) + 4;
      }
    }
    if (c.ditT > 0 && c.dit) {
      Atlas.texte(ctx, c.dit, Math.round((VW - Atlas.largeurTexte(c.dit, 1)) / 2), y + 46,
                  c.dit === 'OUI !' ? '#8fd46a' : '#ff8a7a', 1);
    }
  }

  return { menuCours, accueillir, etatDuCours, acheter, commencer, maj, annuler, dessiner, carte };
})();
