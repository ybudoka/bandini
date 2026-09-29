/* Bandini — l'explosion commune (29 sept. 2026, « les explosifs »).

   ⚠️ UNE SEULE EXPLOSION : le char qui saute, la grenade, la dynamite passent
   tous par `faire`. Deux explosions ecrites deux fois divergent — l'une casse
   le lampadaire, l'autre pas. Ce qui est propre au char (l'epave, le cable,
   celui qui est au volant) reste dans `Vehicules.exploser`.

   ⚠️ LA CHAINE SE JOUE UNE IMAGE A LA FOIS. Un char mis a zero PENDANT une
   explosion ne saute pas dans sa boucle (`differer`) : il attend l'image
   suivante (`maj`). Dix chars gares cote a cote faisaient sinon dix
   explosions imbriquees dans la meme image — et le dixieme mordait des gens
   que le premier parcourait encore. */

const Explosions = (function () {
  'use strict';

  let enCours = 0;
  let attente = [];

  function regles() {
    return (B.defs.armes_regles && B.defs.armes_regles.explosion) || { bruit_tuiles: 30 };
  }

  /** Une explosion en (x, y). `o.rayon` et `o.degats` (au centre, lineaire
      jusqu'au bord) ; `o.coupable` — le joueur ou null — decide du delit ;
      `o.auteur` est celui que `blesser` accuse (le joueur, ou le char qui
      saute) ; `o.source` est le char qui saute : on ne l'abime pas lui-meme,
      et qui est dedans en descend. */
  function faire(x, y, o) {
    enCours++;
    try {
      for (let i = 0; i < 40; i++) {
        const a = B.rng() * Math.PI * 2, s = 1 + B.rng() * 3;
        Entites.particule(x, y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 30 + B.rng() * 20, i % 3 ? '#ff8c1a' : '#3a3a3a', 2 + (i % 2), 0.1);
      }
      Entites.decal(x, y, 'impact');
      Son.SFX.explosion();
      B.cam.secousse = Math.max(B.cam.secousse, 1.2);
      for (const e of Entites.autour(x, y, o.rayon, function (q) { return q !== o.source && q.vivant; })) {
        const part = 1 - Math.hypot(e.x - x, e.y - y) / o.rayon;
        if (part <= 0) continue;
        if (e.type === 'vehicule') Vehicules.endommager(e, Math.round(o.degats * part), o.coupable);
        else if (e.type === 'pieton' || e.type === 'joueur') {
          if (o.source && e.dansVehicule === o.source) Vehicules.descendre(e, true);
          // ⚠️ SA PROPRE EXPLOSION BLESSE LE JOUEUR. `blesser` refuse qu'un joueur
          // blesse un joueur (la coop, Martin 22 sept.) : accusee par lui-meme, la
          // grenade tenue trop longtemps ne lui faisait rien. On l'accuse donc du
          // char qui saute, ou de personne. Celle du PARTENAIRE, elle, reste
          // accusee du partenaire — et `blesser` la refuse, comme il se doit.
          const qui = e === o.auteur ? (o.source || null) : (o.auteur || o.coupable);
          Entites.blesser(e, Math.round(o.degats * part), qui, { renverse: true, angle: angleVers(x, y, e.x, e.y), saigne: 120 });
        }
      }
      // ⚠️ Le DECOR aussi. `Entites.autour(..., q.vivant)` ne le voit pas — le
      // decor ne vit pas — et une explosion qui laisse le lampadaire debout au
      // milieu du cratere ne se croit pas une seconde.
      for (const d of Entites.decorAutour(x, y, o.rayon)) {
        if (d.brise) continue;
        const part = 1 - Math.hypot(d.x - x, d.y - y) / o.rayon;
        if (part > 0) Entites.endommagerDecor(d, Math.round(o.degats * part));
      }
      if (o.coupable) {
        Police.signalerCrime('explosion', x, y, true);
        Entites.alerter(x, y, o.coupable, 3);
        // Une explosion S'ENTEND, comme un coup de feu — de plus loin.
        Police.entendre(x, y, regles().bruit_tuiles * TT);
      }
    } finally { enCours--; }
  }

  /** Vrai si le char doit attendre l'image suivante : on est DANS une explosion. */
  function differer(v) {
    if (!enCours) return false;
    if (attente.indexOf(v) < 0) attente.push(v);
    return true;
  }

  function maj() {
    if (!attente.length) return;
    const lot = attente;
    attente = [];
    for (const v of lot) Vehicules.exploser(v);
  }

  /** Une partie neuve n'herite pas d'une chaine en cours. */
  function oublier() { attente = []; enCours = 0; }

  /** Au noir d'un changement de scene : la chaine en attente se joue TOUT DE
      SUITE, dans le monde qu'on quitte. ⚠️ Sinon le maillon suivant sautait
      dans la piece, sur la carte de la piece (la relecture du 29 sept. 2026).
      Borne : une chaine de cent chars ne fige pas le fondu. */
  function solder() {
    for (let n = 0; attente.length && n < 100; n++) maj();
    attente = [];
  }

  return { faire, differer, maj, oublier, solder };
})();
