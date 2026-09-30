/* Bandini — le garage qui modifie les chars (docs/jalons/le-garage-qui-modifie-les-chars.md).

   Chez Ti-Guy (`Missions.menuGarage`), quatre pieces et un klaxon au choix se posent sur le char gare
   devant le rideau : le moteur, le blindage, les pneus d'hiver, la nitro — et UN klaxon parmi six
   (docs/jalons/les-klaxons-de-ti-guy.md). Le catalogue est Python (`app/garage.py`, `B.defs.garage`) ;
   ici, ce qu'ils font.

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
  /** Le klaxon de ce slug. ⚠️ Un vieux `true` (les sauvegardes d'avant le 30 sept. 2026) : « Gens du pays ». */
  function klaxonParSlug(slug) {
    if (!slug) return null;
    const s = slug === true ? 'gens_du_pays' : slug;
    return klaxons().find(function (k) { return k.slug === s; }) || null;
  }
  /** Les klaxons. ⚠️ Ils voyagent dans la SUITE du paquet (`definitions.DANS_LA_SUITE`) : tant qu'elle n'est pas
      arrivee, aucun — le klaxon ordinaire joue, et le menu n'en montre pas. */
  function klaxons() { return (B.defs && B.defs.klaxons) || []; }

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
    preparerLeKlaxon(v);
    return v;
  }

  /** Ce que le klaxon posé fait entendre, demandé d'avance : ses sons (le lieu `klaxons`) ou les voix de Ti-Guy.
      Sans ça, le premier coup jouerait le filet. */
  function preparerLeKlaxon(v) {
    const k = klaxonParSlug(v.mods && v.mods.klaxon);
    if (!k) return;
    if (k.son) Son.Lieu.charger('klaxons');
    if (k.voix) Son.Voix.chargerHistoire('garage');
  }

  /** Ce qui se sauvegarde des pieces d'un char (ou rien). */
  function fiche(v) { return v && v.mods ? Object.assign({}, v.mods) : undefined; }

  /** Le prix des pieces posees, son klaxon compris. */
  function valeur(mods) {
    const d = donnees();
    if (!d || !mods) return 0;
    const k = klaxonParSlug(mods.klaxon);
    return d.pieces.reduce(function (t, p) { return t + (mods[p.slug] ? p.prix : 0); }, 0) + (k ? k.prix : 0);
  }

  /** Les lignes du menu de Ti-Guy : une par piece, posee ou a poser, puis une par klaxon — en poser un
      remplace l'autre. */
  function items(v, payer) {
    if (!accepte(v)) return [];
    const p = B.partie, pose = klaxonParSlug(v.mods && v.mods.klaxon);
    const lignes = klaxons().map(function (k) {
      const celui = !!pose && pose.slug === k.slug;
      return { libelle: 'POSER : ' + k.nom.toUpperCase(), detail: celui ? 'POSÉ' : k.prix + ' $',
               actif: !celui && p.argent >= k.prix,
               faire: function () {
                 if (!payer(k.prix, k.nom.toUpperCase())) return false;
                 poser(v, { klaxon: k.slug });
                 commenter(k.replique || k.slug, k.texte);
                 return false;
               } };
    });
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
    }).concat(lignes);
  }

  /** Ti-Guy commente la piece posee : sa voix, et la ligne a l'ecran. */
  /** `dit` : son texte, quand il ne vient pas des pieces (un klaxon porte le sien). */
  function commenter(slug, dit) {
    const texte = dit || donnees().repliques[slug];
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

  // --- Les klaxons (docs/jalons/les-klaxons-de-ti-guy.md) ---------------------------------

  /** Le klaxon de Ti-Guy de ce char, au volant du joueur seulement — ou null (le klaxon de sa fiche). */
  function klaxonDe(v) {
    return v && v.mods && v.mods.klaxon && v.conducteur === B.joueur ? klaxonParSlug(v.mods.klaxon) : null;
  }

  /** Le klaxon `k` sonne sur `v` : son air, son son ou la voix de Ti-Guy, et ce qu'il fait au trafic et a
      la police. Rend faux s'il n'a rien pu jouer (la voix pas encore arrivee) : le klaxon ordinaire joue. */
  function klaxonner(v, k) {
    if (k.air) Son.SFX.claironner(notesDe(k));
    else if (k.son) Son.SFX[k.son]();
    else if (k.voix && !crier(v, k)) return false;
    if (k.cede) Vehicules.cederLaVoie(v);
    if (k.enfants) Missions.attirerLesEnfants(v);
    if (k.delit && unVraiPolicierEntend(v, k.oreille_tuiles * TT)) {
      Police.signalerCrime(k.delit, v.x, v.y, true);
      Hud.message('UN VRAI POLICIER A ENTENDU TA FAUSSE SIRÈNE', 150);
    }
    return true;
  }

  /** L'air d'un klaxon, deplie : il voyage SERRE (`garage.air_serre` : « 440:1 392:1 523:3 » et `unite`,
      la note la plus courte en secondes). Deplie une fois, garde sur la fiche. */
  function notesDe(k) {
    if (!k.notes) {
      k.notes = k.air.split(' ').map(function (n) { const q = n.split(':'); return [+q[0], +q[1] * k.unite]; });
    }
    return k.notes;
  }

  /** Des canettes traînent derriere ce char ? (la marche nuptiale, `canettes`) — quel que soit son conducteur :
      elles sont attachees au pare-chocs, pas au klaxon. */
  function canettes(v) {
    if (!v.mods || !v.mods.klaxon) return false;
    const k = klaxonParSlug(v.mods.klaxon);
    return !!(k && k.canettes);
  }

  /** Une engueulade de Ti-Guy, tiree a l'empreinte de l'image — jamais celle du coup d'avant. */
  function crier(v, k) {
    const n = k.voix.length, avant = v.derniereEngueulade;
    let i = (B.t * 7 + 3) % n;
    if (i === avant) i = (i + 1 + (B.t % (n - 1))) % n;
    if (!Son.Voix.crier(k.voix[i])) return false;
    v.derniereEngueulade = i;
    return true;
  }

  /** Un vrai policier a portee d'oreille : un agent a pied (pas un vigile) ou une auto-patrouille. */
  function unVraiPolicierEntend(v, rayon) {
    const r2 = rayon * rayon;
    function pres(e) { const dx = e.x - v.x, dy = e.y - v.y; return dx * dx + dy * dy < r2; }
    return Police.agents().some(function (a) { return (!a.genreVision || a.genreVision === 'policier') && pres(a); })
      || Police.autos().some(pres);
  }

  return { accepte, poser, fiche, valeur, items, hiver, pointe, maj, klaxonDe, klaxonner, klaxonParSlug, notesDe, canettes, commenter };
})();
