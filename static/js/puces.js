/* Bandini — le marché aux puces du dimanche (P4, docs/jalons/le-marche-aux-puces-du-dimanche.md).

   Le dimanche (le jour de partie divisible par sept), de l'aube à midi, deux étals sur le terrain vague le plus
   proche de la planque (`app/puces.py`, sans un dé) : Ti-Rhéal et ses cartes de hockey — quatre numéros par
   semaine —, Gisèle et ses meubles (ceux qui portent `ou: puces`, moins cher qu'au catalogue, livrés le lendemain
   à la planque). On marchande : offrir moins, et le marchand accepte ou refuse selon son HUMEUR, une fonction de la
   semaine et de l'article — jamais `B.rng()`. Un refus tient jusqu'au dimanche suivant.

   ⚠️ RIEN NE NAÎT : les étals et les marchands se PEIGNENT (`dessiner`) — aucune entité, aucun passant de plus, rien
   qui s'empile ni ne décale un numéro. Le catalogue voyage avec les collections (`Collections.catalogue().puces`).

   ⚠️ LE MÊME DIMANCHE, LE MÊME ÉTAL POUR TOUT LE MONDE : `stock(semaine)` et `humeur(...)` ne lisent que la semaine
   et l'article. La partie ne garde que les refus de la semaine (`partie.puces = { semaine, refus }`). */

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

  /** Les refus de la semaine : un tableau neuf chaque dimanche. */
  function refus() {
    const p = B.partie, s = semaine(p.jour);
    if (!p.puces || typeof p.puces !== 'object' || p.puces.semaine !== s) p.puces = { semaine: s, refus: {} };
    if (!p.puces.refus || typeof p.puces.refus !== 'object') p.puces.refus = {};
    return p.puces.refus;
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
    if (accepte(s, slugEtal, article)) {
      if (!acheter(offre)) return null;
      Hud.message('MARCHÉ CONCLU : ' + offre + ' $', 150);
      return 'accepte';
    }
    refus()[cle] = true;
    const e = etal(slugEtal);
    Hud.message((e ? e.marchand.nom : 'LE MARCHAND') + ' : « ' + offre + ' $ ? T’ES DRÔLE, TOI. »', 170);
    Son.SFX.erreur();
    return 'refuse';
  }

  // --- Les menus ------------------------------------------------------------------------------------

  function menuArticle(e, article, nom, prix, acheter, retour) {
    const s = semaine(B.partie.jour), deja = refus()[e.slug + ':' + article];
    const offre = Math.round(prix * (regle().offre || 0.7));
    const items = [
      { libelle: 'ACHETER', detail: prix + ' $', actif: B.partie.argent >= prix,
        faire: function () { if (acheter(prix)) Hud.ouvrirMenu(retour()); return false; } },
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
    const dit = e.marchand.dit || [];
    return { titre: e.nom, sur: p.argent + ' $', largeur: 320, items: items,
             aide: dit.length ? '« ' + dit[semaine(p.jour) % dit.length] + ' »' : '' };
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
    Hud.ouvrirMenu(menuEtal(e.slug));
    return true;
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
           humeur, accepte, refusDeLaSemaine: refus, acheterCarte, acheterMeuble, marchander, menuEtal, sousLaMain, agir, dessiner, yAller };
})();
