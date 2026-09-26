/* Bandini — le garage qui modifie les chars (docs/jalons/le-garage-qui-modifie-les-chars.md).

   Chez Ti-Guy (`Missions.menuGarage`), cinq pieces se posent sur le char gare devant le rideau :
   le moteur, le blindage, les pneus d'hiver, la nitro, le klaxon « Gens du pays ». Le catalogue
   est Python (`app/garage.py`, `B.defs.garage`) ; ici, ce qu'elles font.

   ⚠️ UN CHAR MODIFIE A SA PROPRE FICHE (`v.def`, une copie de celle du catalogue) : le moteur gonfle
   la vitesse de pointe ET l'acceleration du meme facteur — la pointe est un equilibre entre
   l'acceleration et la friction, et un char qui n'atteint pas ce qu'on lui promet ment.

   ⚠️ LES PIECES VOYAGENT AVEC LE CHAR (`v.mods`) : la planque et ses soeurs des blocs (`Jeu`), la
   fourriere (`Missions.saisir`, `garnirLaFourriere`) — tout ce qui recree un char passe par `poser`. */

const Garage = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.garage; }
  function piece(slug) { const d = donnees(); return d ? d.pieces.find(function (p) { return p.slug === slug; }) : null; }
  function effet(slug) { const p = piece(slug); return p ? p.effet : {}; }

  /** Ce char prend-il des pieces ? (pas un velo) */
  function accepte(v) {
    const d = donnees();
    return !!(d && v && v.def && d.classes_exclues.indexOf(v.def.classe) < 0);
  }

  /** Pose les pieces `mods` sur le char : sa fiche a lui, sa vie. Rien si `mods` est vide. */
  function poser(v, mods) {
    if (!v || !mods || !Object.keys(mods).some(function (k) { return mods[k]; })) return v;
    v.mods = Object.assign({}, v.mods || {}, mods);
    const base = Vehicules.vehiculeDef(v.slug), d = Object.assign({}, base);
    if (v.mods.moteur) {
      const k = effet('moteur').vitesse;
      d.vitesse_max = base.vitesse_max * k; d.acceleration = base.acceleration * k;
    }
    const part = v.vieMax ? v.vie / v.vieMax : 1;
    v.vieMax = Math.round(base.vie * (v.mods.blindage ? effet('blindage').vie : 1));
    v.vie = Math.max(1, Math.round(v.vieMax * part));
    v.def = d;
    return v;
  }

  /** Ce qui se sauvegarde des pieces d'un char (ou rien). */
  function fiche(v) { return v && v.mods ? Object.assign({}, v.mods) : undefined; }

  /** Le prix des pieces posees. */
  function valeur(mods) {
    const d = donnees();
    if (!d || !mods) return 0;
    return d.pieces.reduce(function (t, p) { return t + (mods[p.slug] ? p.prix : 0); }, 0);
  }

  /** Les lignes du menu de Ti-Guy : une par piece, posee ou a poser. */
  function items(v, payer) {
    if (!accepte(v)) return [];
    const p = B.partie;
    return donnees().pieces.map(function (q) {
      const pose = !!(v.mods && v.mods[q.slug]);
      return { libelle: 'POSER : ' + q.nom.toUpperCase(), detail: pose ? 'POSÉ' : q.prix + ' $',
               actif: !pose && p.argent >= q.prix,
               faire: function () {
                 if (!payer(q.prix, q.nom.toUpperCase())) return false;
                 const m = {}; m[q.slug] = true;
                 poser(v, m);
                 commenter(q.slug);
                 return false;
               } };
    });
  }

  /** Ti-Guy commente la piece posee : sa voix, et la ligne a l'ecran. */
  function commenter(slug) {
    const texte = donnees().repliques[slug];
    Son.Voix.chargerHistoire('garage');
    Son.Voix.parler('ti_guy-garage-' + slug, {});
    if (texte) Hud.message('TI-GUY : « ' + texte.toUpperCase() + ' »', 300);
  }

  // --- Au volant -------------------------------------------------------------------------

  /** La neige et le verglas prennent leur part de l'adherence (ou du frein) `m` : des pneus d'hiver
      en rendent la part `garde`. Pure. */
  function hiver(v, m) {
    if (!v.mods || !v.mods.pneus || m >= 1) return m;
    return m + (1 - m) * effet('pneus').garde;
  }

  /** La pointe permise a cette image : la nitro la pousse. */
  function pointe(v) { return v.nitroT > 0 ? effet('nitro').poussee : 1; }

  /** La nitro, au bouton libre du volant (SAISIR) : une poussee, puis la recharge. */
  function maj() {
    const j = B.joueur, v = j && j.dansVehicule;
    if (!v || !v.mods || !v.mods.nitro) return;
    const e = effet('nitro');
    if (v.nitroT > 0) { v.nitroT--; if (v.nitroT === 0) v.nitroPret = B.t + Math.round(e.recharge_s * 60); }
    if (!Entree.neuf('saisir') || v.nitroT > 0) return;
    if (v.nitroPret && B.t < v.nitroPret) { Hud.message('NITRO : ÇA RECHARGE', 60); return; }
    v.nitroT = Math.round(e.duree_s * 60);
    v.vitesse = Math.max(v.vitesse, v.def.vitesse_max) * 1.1;     // le coup dans le dos
    Son.SFX.nitro();
  }

  /** Le klaxon « Gens du pays » : l'air de la fiche, note par note. */
  function klaxonne(v) { return !!(v && v.mods && v.mods.klaxon && v.conducteur === B.joueur); }

  return { accepte, poser, fiche, valeur, items, hiver, pointe, maj, klaxonne, commenter };
})();
