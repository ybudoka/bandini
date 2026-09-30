/* Bandini — le marché aux puces du dimanche (P4, docs/jalons/le-marche-aux-puces-du-dimanche.md).

   Le dimanche (le jour de partie divisible par sept), de l'aube à midi, deux étals sur le terrain vague le plus
   proche de la planque (`app/puces.py`, sans un dé) : Ti-Rhéal et ses cartes de hockey — quatre numéros par
   semaine —, Gisèle et ses meubles (ceux qui portent `ou: puces`, moins cher qu'au catalogue, livrés le lendemain
   à la planque). On marchande : offrir moins, et le marchand accepte ou refuse selon son HUMEUR, une fonction de la
   semaine et de l'article — jamais `B.rng()`. Un refus tient jusqu'au dimanche suivant.

   ⚠️ RIEN NE NAÎT : les étals et les marchands se PEIGNENT (`dessiner`) — aucune entité, aucun passant de plus, rien
   qui s'empile ni ne décale un numéro. Le catalogue voyage avec les collections (`Collections.catalogue().puces`).

   ⚠️ LE MÊME DIMANCHE, LE MÊME ÉTAL POUR TOUT LE MONDE : `stock(semaine)` et `humeur(...)` ne lisent que la semaine
   et l'article. La partie ne garde que les refus de la semaine et les marchands déjà rencontrés
   (`partie.puces = { semaine, refus, connus }`).

   LA DEUXIÈME VAGUE (30 sept. 2026) : les marchands PARLENT (leurs voix voyagent sur `/api/collections`, en séries,
   et se chargent en approchant du marché ouvert — `majSon`), chacun se nomme la première fois qu'on s'arrête à son
   étal ; la RUMEUR d'un dimanche matin, dosée à la distance du terrain et qui glisse ; et Gisèle RACHÈTE les meubles
   livrés à la planque — bas (`rachat`), on peut lui demander plus (`demande`), son humeur décide, jamais un dé. Un
   meuble vendu quitte la partie : il revient au catalogue et à son étal. */

const Puces = (function () {
  'use strict';

  function donnees() { const c = Collections.catalogue(); return (c && c.puces) || null; }
  function regle() { const d = donnees(); return (d && d.regle) || {}; }
  function etals() { const d = donnees(); return (d && d.etals) || []; }
  function etal(slug) { return etals().find(function (e) { return e.slug === slug; }) || null; }

  /** Le jour de partie est-il un dimanche ? (Le 7, le 14… : `jour % 7 === 0`.) */
  function dimanche(jour) { return jour > 0 && jour % 7 === 0; }
  function semaine(jour) { return Math.floor((jour - 1) / 7); }
  /** Ouvert : un dimanche, de `ouvre_h` à `ferme_h`. Pure. */
  function ouvertA(jour, heure) {
    const r = regle(), h = heure * 24;
    return !!donnees() && dimanche(jour) && h >= (r.ouvre_h || 6) && h < (r.ferme_h || 12);
  }
  function ouvert() { return !!B.partie && !B.interieur && !B.bloc && ouvertA(B.partie.jour, B.partie.heure); }

  /** Ce que Ti-Rhéal a cette semaine : `cartes_par_semaine` numéros de la Ligue, tirés de la SEMAINE par un hachage
      (sans doublon, dans l'ordre du tirage). Le même pour tout le monde. */
  function stock(sem) {
    const n = regle().cartes_par_semaine || 4, total = Collections.total() || 40, out = [];
    for (let k = 0; out.length < Math.min(n, total) && k < 200; k++) {
      const numero = 1 + hash2(sem * 7919 + 101, k * 31 + 7) % total;
      if (out.indexOf(numero) < 0) out.push(numero);
    }
    return out;
  }
  /** Les meubles de Gisèle : ceux du catalogue qui se vendent aux puces. */
  function meublesAuxPuces() { return Decoration.meubles().filter(function (m) { return m.ou.indexOf('puces') >= 0; }); }

  function prixCarte() { return regle().prix_carte || 120; }
  function prixMeuble(m) { return Math.round(m.prix * (regle().rabais_meubles || 0.6)); }
  /** L'humeur du marchand pour CET article cette semaine (0 à 99) : sous `humeur`, il accepte l'offre. Pure. */
  function humeur(sem, slugEtal, article) {
    let h = 0;
    for (const c of String(slugEtal) + ':' + article) h = (h * 31 + c.charCodeAt(0)) | 0;
    return hash2(sem * 613 + 17, h) % 100;
  }
  function accepte(sem, slugEtal, article) { return humeur(sem, slugEtal, article) < (regle().humeur || 45); }

  /** Ce que la partie garde du marché : les refus de la SEMAINE (un tableau neuf chaque dimanche) et les marchands
      déjà rencontrés (`connus`, pour toujours : on ne se présente qu'une fois). */
  function etat() {
    const p = B.partie, s = semaine(p.jour);
    const avant = p.puces && typeof p.puces === 'object' ? p.puces : {};
    const connus = avant.connus && typeof avant.connus === 'object' && !Array.isArray(avant.connus) ? avant.connus : {};
    if (avant.semaine !== s) p.puces = { semaine: s, refus: {}, connus: connus };
    if (!p.puces.refus || typeof p.puces.refus !== 'object') p.puces.refus = {};
    p.puces.connus = connus;
    return p.puces;
  }
  function refus() { return etat().refus; }

  // --- Ce que disent les marchands ------------------------------------------------------------------

  /** Le texte de la réplique `cle` de `qui` (casse naturelle), ou ''. */
  function texte(qui, cle) { const d = donnees(), r = d && d.repliques && d.repliques[qui]; return (r && r[cle]) || ''; }
  const derniere = {};          // la dernière chose que chaque marchand a dite, par `qui` : l'aide de son menu
  let voixPretes = false;
  /** Les voix et la rumeur rejoignent le son, une fois : elles voyagent avec le catalogue, hors des définitions. */
  function preparer() {
    const d = donnees();
    if (voixPretes || !d) return;
    voixPretes = true;
    if (d.sons) Son.Lieu.declarer(d.sons);
    if (d.voix) Son.Voix.declarer(d.voix);
    Son.Voix.chargerHistoire('puces');
  }
  /** `qui` dit sa réplique `cle` : la voix (si elle est là), et le texte qu'on affiche. Rend le texte. */
  function dire(qui, cle) {
    const t = texte(qui, cle);
    if (!t) return '';
    preparer();
    Son.Voix.parler(qui + '-puces-' + cle, {});
    derniere[qui] = t;
    return t;
  }
  function majuscules(t) { return String(t || '').toUpperCase(); }
  /** La première phrase d'une réplique : ce que le bandeau du HUD tient (une quarantaine de lettres). */
  function premierePhrase(t) { return String(t || '').split(/(?<=[.!?])\s+/)[0]; }
  /** Un menu assez large pour la réplique écrite à son pied (quatre pixels par lettre), sans passer l'écran. */
  function largeurPour(aide, min) { return Math.min(VW - 20, Math.max(min, aide.length * 4 + 20)); }
  function aideDe(qui) { return derniere[qui] ? '« ' + majuscules(derniere[qui]) + ' »' : ''; }
  /** Ce qu'un marchand dit en nous voyant : son nom la PREMIÈRE fois (`salut`), sinon rien à vendre (`rien`) ou sa
      ligne de la semaine (`accueil-<n>`). Une règle, pas un dé. */
  function accueil(e) {
    const qui = e.marchand.qui, st = etat();
    if (!st.connus[qui]) { st.connus[qui] = B.partie.jour; return 'salut'; }
    if (!aVendre(e)) return 'rien';
    return 'accueil-' + (1 + semaine(B.partie.jour) % 3);
  }
  /** L'étal a-t-il encore quelque chose que tu n'as pas ? */
  function aVendre(e) {
    if (e.vend === 'cartes') return stock(semaine(B.partie.jour)).some(function (n) { return !Collections.trouvee(n); });
    return meublesAuxPuces().some(function (m) { return !Decoration.commande('planque', m.slug); });
  }

  // --- Les achats -----------------------------------------------------------------------------------

  /** Acheter une carte à Ti-Rhéal, au prix affiché ou à l'offre acceptée. Elle entre dans l'album par la seule porte
      de l'album (`Collections.donner(numero, 'puces')`) — sans la prime d'une carte trouvée par terre : on l'a
      payée. Les paliers, eux, suivent. */
  function acheterCarte(numero, prix) {
    if (Collections.trouvee(numero) || !Missions.payer(prix, 'CARTE N° ' + numero)) return false;
    return Collections.donner(numero, 'puces');
  }

  /** Acheter un meuble à Gisèle : payé, livré le lendemain à la planque de Rocco (`Decoration`). */
  function acheterMeuble(slug, prix) {
    const m = Decoration.meubles().find(function (q) { return q.slug === slug; });
    if (!m || Decoration.commande('planque', slug) || !Missions.payer(prix, m.nom)) return false;
    const p = B.partie;
    if (!p.meubles || typeof p.meubles !== 'object') p.meubles = {};
    if (!p.meubles.planque || typeof p.meubles.planque !== 'object') p.meubles.planque = {};
    p.meubles.planque[slug] = { jour: p.jour };
    Hud.message(m.nom + ' — LIVRÉ DEMAIN À LA PLANQUE', 180);
    Histoire.noter('ACHETÉ AUX PUCES : ' + m.nom, false);
    return true;
  }

  /** Marchander : l'offre (`offre` × le prix). Acceptée, on achète à ce prix ; refusée, l'article garde son prix
      jusqu'au dimanche suivant — et le marchand le dit. Rend 'accepte', 'refuse' ou null. */
  function marchander(slugEtal, article, prix, acheter) {
    const s = semaine(B.partie.jour), cle = slugEtal + ':' + article;
    if (refus()[cle]) return null;
    const offre = Math.round(prix * (regle().offre || 0.7));
    const e = etal(slugEtal), qui = e && e.marchand.qui;
    if (accepte(s, slugEtal, article)) {
      if (!acheter(offre)) return null;
      dire(qui, 'accepte');
      Hud.message('MARCHÉ CONCLU : ' + offre + ' $', 150);
      return 'accepte';
    }
    refus()[cle] = true;
    Hud.message((e ? e.marchand.nom : 'LE MARCHAND') + ' : « ' + offre + ' $ ? ' + majuscules(premierePhrase(dire(qui, 'refuse'))) + ' »', 170);
    Son.SFX.erreur();
    return 'refuse';
  }

  // --- Les menus ------------------------------------------------------------------------------------

  function menuArticle(e, article, nom, prix, acheter, retour) {
    const s = semaine(B.partie.jour), deja = refus()[e.slug + ':' + article];
    const offre = Math.round(prix * (regle().offre || 0.7));
    const items = [
      { libelle: 'ACHETER', detail: prix + ' $', actif: B.partie.argent >= prix,
        faire: function () { if (acheter(prix)) { dire(e.marchand.qui, 'vente'); Hud.ouvrirMenu(retour()); } return false; } },
      { libelle: deja ? 'IL NE BAISSERA PAS' : 'OFFRIR ' + offre + ' $', actif: !deja && B.partie.argent >= offre, article: article,
        faire: function () { marchander(e.slug, article, prix, acheter); Hud.ouvrirMenu(retour()); return false; } },
      { libelle: 'RETOUR', faire: function () { Hud.ouvrirMenu(retour()); return false; } },
    ];
    void s;
    return { titre: nom, sur: B.partie.argent + ' $', largeur: 300, items: items, retour: function () { Hud.ouvrirMenu(retour()); } };
  }

  /** Le menu de l'étal `slug` : ce qu'il vend cette semaine, et ce qui est déjà à toi. */
  function menuEtal(slug) {
    const e = etal(slug), p = B.partie;
    if (!e) return null;
    const refaire = function () { return menuEtal(slug); };
    const items = [];
    if (e.vend === 'cartes') {
      for (const n of stock(semaine(p.jour))) {
        const c = Collections.fiche(n);
        if (!c) continue;
        const a = Collections.trouvee(n);
        items.push({ libelle: 'N° ' + n + '  ' + c.nom, detail: a ? 'DANS L’ALBUM' : prixCarte() + ' $', actif: !a, numero: n,
                     faire: function () { Hud.ouvrirMenu(menuArticle(e, 'carte' + n, 'N° ' + n + '  ' + c.nom, prixCarte(),
                       function (x) { return acheterCarte(n, x); }, refaire)); return false; } });
      }
    } else {
      for (const m of meublesAuxPuces()) {
        const a = Decoration.commande('planque', m.slug);
        items.push({ libelle: m.nom, detail: a ? 'À TOI' : prixMeuble(m) + ' $', actif: !a, meuble: m.slug,
                     faire: function () { Hud.ouvrirMenu(menuArticle(e, m.slug, m.nom, prixMeuble(m),
                       function (x) { return acheterMeuble(m.slug, x); }, refaire)); return false; } });
      }
    }
    if (!items.length) items.push({ libelle: 'RIEN CETTE SEMAINE', actif: false });
    if (e.vend === 'meubles') {
      const n = aRacheter().length;
      items.push({ libelle: 'VENDRE UN MEUBLE', detail: n ? n + ' À LA PLANQUE' : 'RIEN À VENDRE', actif: n > 0, vendre: true,
                   faire: function () { dire(e.marchand.qui, 'rachat'); Hud.ouvrirMenu(menuVente(slug)); return false; } });
    }
    const qui = e.marchand.qui, aide = aideDe(qui);
    return { titre: e.nom, sur: p.argent + ' $', largeur: largeurPour(aide, 320), items: items, aide: aide,
             // On s'en va : le marchand salue (Échap, B). Le menu se ferme.
             retour: function () {
               const t = dire(qui, 'aurevoir');
               Hud.fermerMenu();
               if (t) Hud.message(e.marchand.nom + ' : « ' + majuscules(premierePhrase(t)) + ' »', 150);
             } };
  }

  // --- La vente à Gisèle ----------------------------------------------------------------------------

  /** Ce que Gisèle rachèterait : chaque meuble du catalogue LIVRÉ dans une planque (celle de Rocco, le chalet) — pas
      un trophée, pas un meuble commandé d'hier qui n'est pas encore arrivé. `{ piece, meuble }`, dans l'ordre. */
  function aRacheter() {
    const p = B.partie, out = [];
    if (!p || !p.meubles) return out;
    for (const piece of Object.keys(p.meubles).sort()) {
      if (!Decoration.places(piece)) continue;
      for (const m of Decoration.meubles()) if (p.meubles[piece][m.slug] && Decoration.livre(piece, m.slug)) out.push({ piece: piece, meuble: m });
    }
    return out;
  }
  /** Son prix : `rachat` × celui du catalogue. ⚠️ Bas, exprès : plus qu'on ne l'a payé, jamais (jugé). */
  function prixRachat(m) { return Math.round(m.prix * (regle().rachat || 0.25)); }
  function prixDemande(m) { return Math.round(prixRachat(m) * (regle().demande || 1.3)); }
  /** Gisèle accepte-t-elle de monter pour ce meuble cette semaine ? Son HUMEUR (la même fonction, un autre article). */
  function accepteDeMonter(sem, slug) { return humeur(sem, 'meubles', 'rachat:' + slug) < (regle().humeur_rachat || 40); }

  /** Le meuble quitte la planque ET la sauvegarde (`partie.meubles`) : l'argent, le carnet. Il revient au catalogue et
      à l'étal de Gisèle, comme s'il n'avait jamais été à toi. */
  function vendreMeuble(piece, slug, prix) {
    const p = B.partie, m = Decoration.meubles().find(function (q) { return q.slug === slug; });
    if (!m || !p.meubles || !p.meubles[piece] || !Decoration.livre(piece, slug)) return false;
    delete p.meubles[piece][slug];
    Missions.encaisser(prix, m.nom);
    Histoire.noter('VENDU AUX PUCES : ' + m.nom + ' (' + prix + ' $)', false);
    return true;
  }
  /** Le marchandage à l'envers : on demande `demande` × son prix. Elle monte, on vend ; elle refuse, le meuble garde
      son prix jusqu'au dimanche suivant. Rend 'accepte', 'refuse' ou null. */
  function demanderPlus(piece, slug) {
    const s = semaine(B.partie.jour), cle = 'rachat:' + slug, m = Decoration.meubles().find(function (q) { return q.slug === slug; });
    if (!m || refus()[cle] || !Decoration.livre(piece, slug)) return null;
    const prix = prixDemande(m);
    if (accepteDeMonter(s, slug)) {
      if (!vendreMeuble(piece, slug, prix)) return null;
      dire('gisele', 'plus-accepte');
      return 'accepte';
    }
    refus()[cle] = true;
    Hud.message('GISÈLE : « ' + prix + ' $ ? ' + majuscules(premierePhrase(dire('gisele', 'plus-refuse'))) + ' »', 170);
    Son.SFX.erreur();
    return 'refuse';
  }

  /** Ce qu'on peut vendre à Gisèle : un meuble par ligne, son prix à elle. */
  function menuVente(slugEtal) {
    const p = B.partie, retour = function () { Hud.ouvrirMenu(menuEtal(slugEtal)); };
    const items = aRacheter().map(function (a) {
      const nom = a.meuble.nom + (a.piece === 'planque' ? '' : ' (' + a.piece.toUpperCase() + ')');
      return { libelle: nom, detail: prixRachat(a.meuble) + ' $', vend: a.meuble.slug, piece: a.piece,
               faire: function () { Hud.ouvrirMenu(menuRachat(slugEtal, a.piece, a.meuble, nom)); return false; } };
    });
    if (!items.length) items.push({ libelle: 'RIEN À VENDRE', actif: false });
    items.push({ libelle: 'RETOUR', faire: function () { retour(); return false; } });
    const aide = aideDe('gisele');
    return { titre: 'VENDRE À GISÈLE', sur: p.argent + ' $', largeur: largeurPour(aide, 320), items: items, aide: aide, retour: retour };
  }

  /** Un meuble qu'on vend : à son prix, ou demander plus. */
  function menuRachat(slugEtal, piece, m, nom) {
    const deja = refus()['rachat:' + m.slug], prix = prixRachat(m), plus = prixDemande(m);
    const apres = function () { Hud.ouvrirMenu(menuVente(slugEtal)); };
    const items = [
      { libelle: 'VENDRE', detail: prix + ' $', faire: function () {
        if (vendreMeuble(piece, m.slug, prix)) dire('gisele', 'rachat-conclu');
        apres(); return false; } },
      { libelle: deja ? 'ELLE NE MONTERA PAS' : 'DEMANDER ' + plus + ' $', actif: !deja, demander: true,
        faire: function () { demanderPlus(piece, m.slug); apres(); return false; } },
      { libelle: 'RETOUR', faire: function () { apres(); return false; } },
    ];
    return { titre: nom, sur: B.partie.argent + ' $', largeur: 300, items: items, retour: apres,
             aide: 'LE CATALOGUE LE VEND ' + m.prix + ' $' };
  }

  /** L'étal devant soi : à moins d'une tuile et demie de sa table, le marché ouvert. */
  function sousLaMain(j) {
    if (!ouvert() || !j || j.dansVehicule) return null;
    for (const e of etals()) {
      if (typeof e.x !== 'number') continue;
      const cx = (e.x + 1) * TT, cy = e.y * TT + 8;
      if (Math.abs(j.x - cx) < 26 && Math.abs(j.y - cy) < 26) return e;
    }
    return null;
  }

  function agir(j) {
    const e = sousLaMain(j);
    if (!e) return false;
    j.animT = 10; j.animType = 'ramasse';
    dire(e.marchand.qui, accueil(e));
    Hud.ouvrirMenu(menuEtal(e.slug));
    return true;
  }

  // --- La rumeur ------------------------------------------------------------------------------------

  let niveau = 0;
  /** Le volume que la rumeur VISE : plein sur le terrain, nul à `portee_px` de son bord ; nul hors des heures, dans une
      pièce ou un bloc (`ouvert`). Pure. */
  function cibleDuSon(j) {
    const d = donnees();
    if (!ouvert() || !d || !d.terrain || !j) return 0;
    const t = d.terrain, x0 = t.x * TT, y0 = t.y * TT, x1 = (t.x + t.l) * TT, y1 = (t.y + t.h) * TT;
    const dx = Math.max(x0 - j.x, 0, j.x - x1), dy = Math.max(y0 - j.y, 0, j.y - y1);
    const portee = (d.rumeur && d.rumeur.portee_px) || 320;
    return Math.max(0, 1 - Math.hypot(dx, dy) / portee);
  }
  /** À chaque image : la rumeur GLISSE vers sa cible (on arrive, midi sonne : jamais d'un coup), et la première fois
      qu'elle se fait entendre, les voix et le son du marché se chargent. */
  function majSon() {
    const d = donnees();
    if (!d || !B.partie) return;
    const cible = cibleDuSon(B.joueur), pas = 1 / (((d.rumeur && d.rumeur.glisse_s) || 2.5) * 60);
    niveau = cible > niveau ? Math.min(cible, niveau + pas) : Math.max(cible, niveau - pas);
    if (niveau > 0.02) preparer();
    if (niveau > 0 || cible > 0) Son.SFX.rumeur_puces(niveau);
    majChien(d);
  }
  function volumeDuSon() { return niveau; }

  // LE CHIEN DU MARCHÉ (30 sept. 2026) : UN aboiement, au loin, de l'autre côté du terrain — pas dans la boucle, où il
  // reviendrait à chaque tour. À l'HORLOGE (`B.t`), jamais au dé : le premier `chien_s[0]` secondes après qu'on entend le
  // marché, les suivants à un écart qui change sans tirage (comme les bruits de quartier). Il se tait quand la rumeur
  // se tait ; son fichier vient avec elle (`LIEUX["puces"]`), et sans lui on n'entend rien — pas de filet.
  let prochainChien = null, nChiens = 0;
  const chiens = [];
  function majChien(d) {
    const iv = (d.rumeur && d.rumeur.chien_s) || [35, 70], t = d.terrain;
    if (niveau < 0.25 || !t || !B.joueur) { prochainChien = null; return; }
    if (prochainChien === null) { prochainChien = B.t + iv[0] * 60; return; }
    if (B.t < prochainChien) return;
    nChiens++;
    prochainChien = B.t + (iv[0] + (nChiens * 17) % Math.max(1, iv[1] - iv[0])) * 60;
    const angle = nChiens * 2.39996, loin = (d.rumeur && d.rumeur.chien_px) || 224;
    const x = (t.x + t.l / 2) * TT + Math.cos(angle) * loin, y = (t.y + t.h / 2) * TT + Math.sin(angle) * loin;
    chiens.push({ t: B.t, x: x, y: y });
    if (chiens.length > 20) chiens.shift();
    Son.jouerA('chien_puces', x, y, (d.rumeur && d.rumeur.portee_px || 320) + 100);
  }

  // --- Le dessin ------------------------------------------------------------------------------------

  function px(ctx, c, x, y, l, h) { ctx.fillStyle = c; ctx.fillRect(x, y, l || 1, h || 1); }

  /** Un marchand, debout derrière sa table : 8 × 13, ses couleurs. */
  function peindreMarchand(ctx, m, x, y) {
    px(ctx, 'rgba(0,0,0,0.25)', x + 1, y + 12, 6, 1);
    px(ctx, '#2a2a34', x + 2, y + 9, 4, 3);                 // les jambes
    px(ctx, m.chandail, x + 1, y + 4, 6, 5);                // le chandail
    px(ctx, m.peau, x, y + 5, 1, 3); px(ctx, m.peau, x + 7, y + 5, 1, 3);   // les bras
    px(ctx, m.peau, x + 2, y, 4, 4);                        // la tête
    px(ctx, m.cheveux, x + 2, y, 4, 1);
    px(ctx, '#1c1a22', x + 3, y + 2, 1, 1); px(ctx, '#1c1a22', x + 5, y + 2, 1, 1);
    B.stats.rects += 9;
  }

  /** Une table pliante de deux tuiles, sa nappe, et ce qu'elle porte. */
  function peindreEtal(ctx, e, x, y) {
    px(ctx, 'rgba(0,0,0,0.3)', x + 1, y + 13, 30, 2);
    px(ctx, '#5a5a62', x + 2, y + 9, 1, 5); px(ctx, '#5a5a62', x + 29, y + 9, 1, 5);   // les pattes
    px(ctx, e.nappe, x, y + 2, 32, 8);                                                  // la nappe
    px(ctx, '#f0ead8', x, y + 9, 32, 1);
    for (let i = 0; i < 32; i += 4) px(ctx, '#f0ead8', x + i, y + 2, 2, 1);             // le bord à carreaux
    if (e.vend === 'cartes') {
      const eq = (Collections.catalogue() && Collections.catalogue().cartes && Collections.catalogue().cartes.equipes) || {};
      const couleurs = Object.keys(eq).map(function (d) { return eq[d].couleurs[0]; });
      for (let i = 0; i < 6; i++) {
        px(ctx, '#f4efe2', x + 2 + i * 5, y + 3, 4, 5);
        px(ctx, couleurs[i % (couleurs.length || 1)] || '#7a4a2a', x + 3 + i * 5, y + 4, 2, 2);
      }
    } else {
      px(ctx, '#7a1e1e', x + 2, y, 10, 5); px(ctx, '#2e5a2a', x + 4, y + 1, 2, 2); px(ctx, '#2e5a2a', x + 8, y + 1, 2, 2);  // un coussin à carreaux
      px(ctx, '#6a4424', x + 15, y - 2, 8, 7); px(ctx, '#a8c8d8', x + 16, y - 1, 5, 4);   // un téléviseur
      px(ctx, '#9a9aa4', x + 17, y - 5, 1, 3); px(ctx, '#9a9aa4', x + 20, y - 5, 1, 3);
      px(ctx, '#b8864a', x + 25, y + 4, 6, 4); px(ctx, '#3a5a7a', x + 26, y + 5, 4, 2);   // un tapis roulé
    }
    B.stats.rects += 14;
  }

  function dessiner(ctx, cam) {
    if (!ouvert()) return;
    const d = donnees();
    if (!d || !d.terrain) return;
    const tx = d.terrain.x * TT - cam.x, ty = d.terrain.y * TT - cam.y;
    if (tx > VW + 40 || ty > VH + 40 || tx + d.terrain.l * TT < -40 || ty + d.terrain.h * TT < -40) return;
    // La pancarte, plantée au coin : MARCHÉ AUX PUCES, en lettres de carton.
    px(ctx, '#6a4424', Math.round(tx + 3), Math.round(ty - 2), 1, 12);
    px(ctx, '#f0e0b0', Math.round(tx - 4), Math.round(ty - 8), 16, 7);
    px(ctx, '#b02a22', Math.round(tx - 2), Math.round(ty - 6), 12, 1); px(ctx, '#b02a22', Math.round(tx - 2), Math.round(ty - 3), 9, 1);
    for (const e of etals()) {
      if (typeof e.x !== 'number') continue;
      const x = Math.round(e.x * TT - cam.x), y = Math.round(e.y * TT - cam.y);
      peindreMarchand(ctx, e.marchand, x + 12, y - 12);
      peindreEtal(ctx, e, x, y);
    }
  }

  /** TRICHES : au marché — le dimanche suivant (ou celui-ci), à 8 h, devant l'étal de Ti-Rhéal. */
  function yAller() {
    const p = B.partie, e = etals()[0];
    if (!p || !e || typeof e.x !== 'number') return false;
    if (!dimanche(p.jour)) p.jour += 7 - (p.jour % 7);
    p.heure = 8 / 24;
    const j = B.joueur;
    if (j.dansVehicule) Vehicules.descendre(j, true);
    j.x = (e.x + 1) * TT; j.y = (e.y + 1) * TT + 10; j.vx = 0; j.vy = 0;   // devant la table, face à elle
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
    return true;
  }

  return { donnees, regle, etals, etal, dimanche, semaine, ouvertA, ouvert, stock, meublesAuxPuces, prixCarte, prixMeuble,
           humeur, accepte, refusDeLaSemaine: refus, acheterCarte, acheterMeuble, marchander, menuEtal, sousLaMain, agir, dessiner, yAller,
           texte, dire, accueil, aRacheter, prixRachat, prixDemande, accepteDeMonter, vendreMeuble, demanderPlus, menuVente, menuRachat,
           cibleDuSon, majSon, maj: majSon, volumeDuSon, chiens };
})();
