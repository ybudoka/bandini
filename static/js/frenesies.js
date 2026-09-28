/* Bandini — les frénésies (P4, « Quatre activités que le jeu n'a pas », la quatrième).

   Martin, 28 sept. 2026 : « la frénésie on y va ». Les _rampages_ des GTA : une icône
   cachée dans une ruelle de chaque district (`carte.frenesies`, posée par `app/frenesies.py`
   sur la ville finie, sans un dé), une arme du catalogue PRÊTÉE, un chrono, un compte à
   faire — tant de membres d'une gang, ou tant de chars. Réussie, elle paie une fois, se
   note au carnet et ne revient plus (`partie.frenesies`, sauvegardé) ; ratée, l'icône
   attend qu'on s'éloigne et qu'on revienne.

   ⚠️ LES ENFANTS RESTENT INTOUCHABLES. Ils le sont pour tout le monde (`Entites.blesser`) ;
   ici, en plus, `compte` ne compte JAMAIS un intouchable : si la règle d'en haut sautait,
   une frénésie ne deviendrait pas pour autant une chasse aux enfants.

   ⚠️ EXPRÈS, JAMAIS AU TÉLÉPHONE. On marche sur l'icône, à pied : c'est le seul
   déclencheur. Pas pendant une mission ni un défi (l'icône le dit, et attend).

   ⚠️ L'ARME PRÊTÉE NE SE GARDE PAS. On la tient tout le long (pas de roue : c'est elle ou
   rien), ses munitions ne tarissent pas, et à la fin le sac redevient ce qu'il était. La
   sauvegarde écrite PENDANT une frénésie écrit le sac d'avant (`sansLePret`) : on ne
   repart pas d'un rechargement avec un pistolet à 999 balles.

   ⚠️ RIEN AU DÉMARRAGE : ni entité ni dé. L'icône se PEINT (`dessiner`), elle n'est pas un
   décor — un décor de plus au chargement décale le numéro de tout ce qui naît ensuite. Les
   renforts d'une frénésie de gang, eux, naissent pendant la frénésie, hors de l'écran :
   c'est le joueur qui l'a voulue. */

const Frenesies = (function () {
  'use strict';

  //: Au-delà, l'icône d'une frénésie ratée (ou refusée) se reprend.
  const RETOUR_PX = 48;
  //: Les munitions d'une arme prêtée : on ne les voit pas baisser.
  const SANS_FIN = 999;

  //: L'icône qui vient d'être ratée ou refusée : elle attend qu'on s'en éloigne.
  let enAttente = null;

  //: ⚠️ La VILLE (`B.defs.carte`), jamais `Monde.carte` : dans un bloc, `Monde.carte` est le bloc.
  function toutes() { return (B.defs && B.defs.carte && B.defs.carte.frenesies) || []; }
  function regle() { return (B.defs && B.defs.carte && B.defs.carte.frenesies_regle) || {}; }

  /** Celles qu'on peut voir et prendre : en ville seulement, ni dans une pièce ni dans un bloc. */
  function donnees() { return B.interieur || B.bloc ? null : toutes(); }

  function fiche(slug) { return toutes().find(function (f) { return f.slug === slug; }) || null; }
  function reussie(slug) { return !!(B.partie && B.partie.frenesies && B.partie.frenesies[slug]); }
  function reussies() { return toutes().filter(function (f) { return reussie(f.slug); }).length; }
  function enCours() { return B.frenesie || null; }
  function position(f) { return { x: f.x * TT + 8, y: f.y * TT + 8 }; }

  function gangDe(f) {
    return ((B.defs.pietons && B.defs.pietons.gangs) || []).find(function (g) { return g.slug === f.gang; }) || null;
  }

  function chrono(images) {
    const s = Math.max(0, Math.ceil(images / 60));
    return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
  }

  function quoi(f) {
    if (f.cible === 'chars') return 'CHARS';
    const g = gangDe(f);
    // « 10 CRAVATES », pas « 10 LES CRAVATES » : l'article tombe devant un nombre.
    return (g ? g.nom : f.gang).toUpperCase().replace(/^(LES|LA|LE) /, '');
  }

  /** « FRÉNÉSIE 3/10 LES CRAVATES 1:12 » : la ligne du haut, pendant qu'elle court. */
  function ligne() {
    const e = B.frenesie;
    if (!e) return null;
    const f = fiche(e.slug);
    if (!f) return null;
    return 'FRÉNÉSIE ' + e.compte + '/' + f.n + ' ' + quoi(f) + ' ' + chrono(f.chrono_s * 60 - e.t);
  }

  /** Ce qu'elle COMPTE. ⚠️ Écrit en toutes lettres, et d'abord ce qu'elle ne compte jamais. */
  function compte(f, e) {
    if (!e || e.intouchable || e.petit || e.partenaire || e.personnage) return false;
    if (f.cible === 'gang') return e.type === 'pieton' && e.gang === f.gang;
    return false;
  }

  // --- Le prêt de l'arme --------------------------------------------------------------------------

  function preter(f) {
    const p = B.partie, j = B.joueur, def = Combat.armeDef(f.arme);
    const sac = p.armes[f.arme];
    B.frenesie.avant = { arme: j.arme, partieArme: p.arme, sac: sac ? Object.assign({}, sac) : null };
    p.armes[f.arme] = { mun: def && def.chargeur === null ? null : SANS_FIN, usure: 0 };
    j.arme = f.arme; p.arme = f.arme;
  }

  function tenir(f) {
    const p = B.partie, j = B.joueur, sac = p.armes[f.arme];
    if (sac && sac.mun !== null) sac.mun = SANS_FIN;
    if (sac) sac.usure = 0;
    if (!j.dansVehicule && j.arme !== f.arme) { j.arme = f.arme; p.arme = f.arme; }
  }

  function rendre(e) {
    const p = B.partie, j = B.joueur, f = fiche(e.slug);
    if (!e.avant || !f) return;
    if (e.avant.sac) p.armes[f.arme] = e.avant.sac; else delete p.armes[f.arme];
    const avant = e.avant.arme && (e.avant.arme === 'poings' || p.armes[e.avant.arme]) ? e.avant.arme : null;
    if (j) j.arme = avant;
    p.arme = avant;
    e.avant = null;
  }

  /** La partie telle qu'elle s'écrit : pendant une frénésie, le sac D'AVANT le prêt. */
  function sansLePret(p) {
    const e = B.frenesie, f = e && fiche(e.slug);
    if (!e || !e.avant || !f || p !== B.partie) return p;
    const armes = Object.assign({}, p.armes);
    if (e.avant.sac) armes[f.arme] = e.avant.sac; else delete armes[f.arme];
    return Object.assign({}, p, { armes: armes, arme: e.avant.partieArme === f.arme ? null : e.avant.partieArme });
  }

  // --- Commencer, compter, finir ------------------------------------------------------------------

  function occupe() {
    return !!(B.mission || (B.partie && B.partie.mission) || B.defi);
  }

  function commencer(f) {
    B.frenesie = { slug: f.slug, t: 0, compte: 0, avant: null, renfortT: 0 };
    preter(f);
    enAttente = null;
    Son.SFX.frenesie();
    Hud.message('FRÉNÉSIE ! ' + f.n + ' ' + quoi(f) + ' EN ' + chrono(f.chrono_s * 60) + ' — ' + Combat.armeDef(f.arme).nom.toUpperCase(), 220);
    return B.frenesie;
  }

  function avancer() {
    const e = B.frenesie, f = e && fiche(e.slug);
    if (!f) return;
    e.compte++;
    if (e.compte >= f.n) finir(true);
  }

  /** `Entites.tuer` : un piéton est mort, et c'est un joueur qui l'a tué. */
  function abattu(p, source) {
    const e = B.frenesie, f = e && fiche(e.slug);
    if (!f || !source || source.type !== 'joueur' || p.compteFrenesie) return;
    if (!compte(f, p)) return;
    p.compteFrenesie = true;
    avancer();
  }

  /** `Vehicules.endommager` : un char tombe à zéro, et c'est un joueur qui l'a mis là. */
  function detruit(v) {
    const e = B.frenesie, f = e && fiche(e.slug);
    if (!f || f.cible !== 'chars' || v.derby || v.compteFrenesie) return;
    if (!v.agresseur || v.agresseur.type !== 'joueur' || v.conducteur === v.agresseur) return;
    v.compteFrenesie = true;
    avancer();
  }

  function finir(gagne, raison) {
    const e = B.frenesie, f = e && fiche(e.slug);
    if (!e) return;
    rendre(e);
    B.frenesie = null;
    if (!f) return;
    const p = B.partie;
    if (!gagne) {
      enAttente = f.slug;
      Hud.message('FRÉNÉSIE RATÉE — ' + (raison || ''), 200);
      Son.SFX.erreur();
      Histoire.noter('FRÉNÉSIE RATÉE : ' + f.titre, false);
      return;
    }
    p.frenesies[f.slug] = { jour: p.jour, temps: e.t };
    Son.SFX.frenesie_fin();
    Missions.encaisser(f.prime, 'FRÉNÉSIE — ' + f.titre.toUpperCase(), true);
    Missions.annoncerPrime(f.prime, f.titre, 'FRÉNÉSIE RÉUSSIE', 0);
    Hud.message('FRÉNÉSIE RÉUSSIE — ' + f.titre.toUpperCase(), 220);
    Histoire.noter('FRÉNÉSIE RÉUSSIE : ' + f.titre + ' — ' + f.prime + ' $', true);
    const liste = toutes();
    if (liste.length && liste.every(function (q) { return reussie(q.slug); })) {
      const bonus = regle().bonus_toutes || 0;
      if (bonus) Missions.encaisser(bonus, 'TOUTES LES FRÉNÉSIES', true);
      Hud.message('TOUTES LES FRÉNÉSIES — LA VILLE S’EN SOUVIENDRA' + (bonus ? ' (+' + bonus + ' $)' : ''), 260);
      Histoire.noter('TOUTES LES FRÉNÉSIES' + (bonus ? ' — ' + bonus + ' $' : ''), true);
    }
  }

  /** L'hôpital, la prison, une partie qui s'arrête : elle s'arrête là. */
  function rater(raison) { if (B.frenesie) finir(false, raison); }

  // --- Les renforts d'une frénésie de gang ----------------------------------------------------------

  function renforts(f, e) {
    const g = gangDe(f), r = regle(), j = B.joueur;
    const cadence = (r.renforts_cadence_s || 1.5) * 60, min = r.renforts_min || 4;
    if (!g || ++e.renfortT < cadence) return;
    e.renfortT = 0;
    const la = Entites.pietonsAutour(j.x, j.y, Entites.BULLE_OUBLI).filter(function (q) {
      return q.vivant && q.gang === f.gang && q.etat !== 'assomme';
    });
    if (la.length >= min) return;
    const place = Entites.placeDeNaissance();
    if (!place) return;
    const q = Entites.creerPieton(place.x, place.y, Entites.archetype(g.pieton));
    q.etat = 'attaque_joueur'; q.cri = 90; q.frenesie = f.slug;
  }

  // --- La boucle -----------------------------------------------------------------------------------

  function majEnCours(e) {
    const f = fiche(e.slug), j = B.joueur;
    if (!f || !j) { B.frenesie = null; return; }
    if (B.interieur || B.bloc) { finir(false, 'TU AS QUITTÉ LA RUE'); return; }
    e.t++;
    tenir(f);
    if (e.t > f.chrono_s * 60) { finir(false, 'TEMPS ÉCOULÉ'); return; }
    if (f.cible === 'gang') renforts(f, e);
  }

  function maj() {
    if (!B.partie || !B.joueur) return;
    if (B.frenesie) { majEnCours(B.frenesie); return; }
    const liste = donnees();
    if (!liste || B.menu || B.cinema || B.scene) return;
    const j = B.joueur, r = regle().rayon_px || 12;
    if (enAttente) {
      const f = fiche(enAttente), p = f && position(f);
      if (!p || dist2(j.x, j.y, p.x, p.y) > RETOUR_PX * RETOUR_PX) enAttente = null;
    }
    if (j.dansVehicule || j.hospitalise) return;
    for (const f of liste) {
      if (reussie(f.slug) || f.slug === enAttente) continue;
      const p = position(f);
      if (dist2(j.x, j.y, p.x, p.y) > r * r) continue;
      if (occupe()) {
        enAttente = f.slug;
        Hud.message('FRÉNÉSIE — PAS PENDANT UNE MISSION', 150);
        Son.SFX.erreur();
        return;
      }
      commencer(f);
      return;
    }
  }

  // --- L'icône : un crâne rouge qui flotte au-dessus de sa ruelle -----------------------------------

  //: 7 × 7, `#` l'os, `o` les orbites.
  const CRANE = [' ##### ', '#######', '#oo#oo#', '#oo#oo#', '###.###', ' #####', ' # # # '];

  function dessiner(ctx, cam) {
    const liste = donnees();
    if (!liste) return;
    for (const f of liste) {
      if (reussie(f.slug) || (B.frenesie && B.frenesie.slug === f.slug)) continue;
      const p = position(f);
      const flotte = Math.round(Math.sin((B.t || 0) / 18) * 2);
      const x = Math.round(p.x - cam.x - 3), y = Math.round(p.y - cam.y - 12 + flotte);
      if (x < -16 || y < -16 || x > VW + 16 || y > VH + 16) continue;
      // L'ombre sur le sol, qui ne flotte pas ; le halo rouge qui bat.
      ctx.fillStyle = 'rgba(0,0,0,0.30)';
      ctx.fillRect(x, Math.round(p.y - cam.y + 3), 7, 2);
      ctx.fillStyle = (B.t || 0) % 40 < 20 ? 'rgba(220,40,30,0.55)' : 'rgba(220,40,30,0.30)';
      ctx.fillRect(x - 1, y - 1, 9, 9);
      for (let jy = 0; jy < CRANE.length; jy++) {
        for (let ix = 0; ix < CRANE[jy].length; ix++) {
          const c = CRANE[jy][ix];
          if (c === '#') ctx.fillStyle = '#f2ecdc';
          else if (c === 'o' || c === '.') ctx.fillStyle = '#7a0f0a';
          else continue;
          ctx.fillRect(x + ix, y + jy, 1, 1);
        }
      }
      B.stats.rects += 30;
    }
  }

  /** Une nouvelle partie : rien en cours, rien en attente. */
  function oublier() { B.frenesie = null; enAttente = null; }

  return { donnees, toutes, fiche, reussie, reussies, enCours, position, ligne, compte, commencer, abattu, detruit,
           finir, rater, sansLePret, maj, dessiner, oublier };
})();
