# Quatre juges rouges sur dev

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demandé par Martin le 29 sept. 2026, après « Les juges : moins de doublons, plus de
morsure ». Quatre juges rouges sur dev (49479e3b), tous rouges avant ce chantier : 1)
test_la_nuit::test_les_comptoirs_ferment_la_nuit_ouvrent_avant_le_jeu_et_le_bar_ferme_au_last_call
— « cineparc ouvre après 8 h » ; 2)
test_debug_js::test_chaque_porte_des_blocs_se_rejoint_et_s_ouvre — la porte du ciné-parc ; 3)
test_defis_graduels_js::test_l_esquive_se_gagne_sans_frapper — « DÉFI RATÉ — IL T'A
SONNÉ » après 46 roulades ; 4)
test_velos_js::test_la_ville_roule_avec_ses_velos_sans_une_anomalie[23] — « HORS VOIE
autobus ROULE ».

- ⚠️ Pour chacun : le juge a-t-il raison ? Un rouge se règle en réparant le jeu, pas en
  relâchant le juge — sauf si le juge mesure mal, et alors on le dit.

## Notes

Livré le 29 sept. 2026. Chaque rouge trouvé par `git bisect`, et tranché : le juge ou le jeu ?

- **Le ciné-parc, deux juges — le juge avait tort** (fautif : f350b9e5, le casse-croûte). La note du
  ciné-parc dit « l'été seulement, le soir, de 17 h à 2 h » (Martin, 27 sept.), et `test_cineparc_js` exigeait
  déjà ce comptoir FERMÉ à 11 h : les deux juges se contredisaient. `test_la_nuit` juge maintenant le
  casse-croûte à part, comme le bar (fermé le midi, ouvert avant la nuit, fermé après minuit et avant le
  jour) ; `test_debug_js` attend la porte `cineparc:Le casse-croûte du ciné-parc` — la villa, seul bloc sans
  porte, garde le cas « à son arrivée ». Six mutations d'heures et de porte les font rougir.
- **L'esquive — le juge avait tort** (fautif : 8455744e, les statues). La statue du cavalier est au cœur de
  la place du parc, sur le cercle de 48 px du boxeur du juge : il visait un point caché derrière le socle,
  ne tournait plus, et prenait tous ses coups au même endroit. Un joueur contourne ; le boxeur du juge
  aussi, maintenant (il vise le point suivant quand il ne se rapproche plus). Sans le contournement : rouge.
- **L'autobus hors voie — le jeu avait tort** (fautif : 36c20bd2, le bidonville, qui a déplacé la ville ;
  graine 23). Un autobus de ligne, le nez dans une boîte, attendait qu'une mère et son enfant finissent de
  traverser ; une auto engagée dans la même boîte a perdu patience et forcé dans son flanc — partagé aux
  masses, image après image, l'autobus a glissé de 20 px sur le trottoir. `heurterVehicules` : **celui qui
  force s'arrête contre l'autre**, il ne le déplace plus. Sans la règle : rouge ; graines 1, 5, 23 et dix
  autres sans une anomalie ; les juges du trafic, de la police et des piétons passent.

⚠️ Restés ouverts, à trancher par Martin :
1. le bronze dans le ring de l'esquive : on le garde (choix actuel), ou le ring refuse un monument (il
   partirait à 11 tuiles, dans un coin plus encombré) ;
2. le juge de l'esquive ne prouve pas que la ROULADE sert : un boxeur qui ne roule jamais gagne (vie 0,56),
   et `roulades >= 3` compte les appuis, pas les roulades — un juge qui ne mord pas, d'avant ;
3. le chien de garde et le vélo qui redescend du trottoir sont « forcés » eux aussi : s'ils touchent un
   autre char, c'est eux qui reculent (aucun juge n'a bougé) ;
4. deux chars finissent encore ensemble dans une boîte quand l'attente déborde — la soupape voulue, la vraie
   racine de l'autobus : non touchée.

