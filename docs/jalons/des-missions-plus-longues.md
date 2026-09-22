# Des missions plus longues : plus d'étapes, plus loin, plus de dialogue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « révise toutes mes missions pour que les missions soient plus longues, le
plus possible ». Les trois à la fois : **plus d'étapes** (deux à quatre objectifs de plus par
mission — un détour, une poursuite, semer la police, une livraison de plus), **des trajets plus
loin** (des lieux à l'autre bout de la ville quand l'histoire le permet), et **plus de dialogue**
(intros, fins et répliques `pendant` plus étoffées, chacune avec son `jeu=`). Toutes les missions,
m1 comprise. Les voix neuves sont générées dans le même passage (ElevenLabs v3) ; une réplique
existante qui change de place garde son mp3 (renommé), une qui change de mots est refaite.

- ⚠️ Chaque mission allongée se joue au banc jusqu'au bout : les juges existants qui la jouent
  étape par étape suivent les étapes neuves.
- ⚠️ « Qui parle se nomme » reste une fois par mission ; une étape neuve ne mène jamais à `usine`.

## Notes

Livré le 22 sept. 2026, en sept paquets travaillés en parallèle (un worktree chacun), puis réunis.

**Les 37 missions** ont 2 à 4 étapes de plus, surtout vers l'autre bout de la ville (phare, hôtel,
cantine des Quais, fourrière, Île-aux-Corneilles par le `ou` d'un `tuer`/`pirater`), et 3 à 6 répliques
de plus chacune (268 → 420 environ). Quelques exemples : m1 fait parler Marco et sème une étoile ;
m2 envoie à l'hôpital voir Ginette ; m3 porte « la boîte qui existe pas » au phare ; m6 ajoute le
pickpocket de Ti-Paul, le piquet des Boulonneux et le retour au Brouillard ; m52-m54 passent par l'île ;
f06 démolit l'autre char du stool après la filature. Aucun mot d'une réplique existante n'a changé ;
aucun lieu neuf, la ville ne bouge pas (`test_devants.py`).

- ⚠️ **La réplique `pendant` de l'objectif 0 ne se disait jamais** (`avancer(true)` se tait sous l'intro,
  `annoncer` ne l'armait pas) : « Le dépanneur d'abord » de m6 et le boîtier de m54 étaient payés et muets.
  Corrigé dans `annoncer` ; juge `test_la_replique_pendant_du_premier_objectif_se_dit_apres_l_intro`
  (rouge sans le correctif). Elle se dit maintenant dans m6, m4, f03, f06, f07, e02, h02, s01, p13, q03, m54.
- ⚠️ **69 mp3 payés ont changé de nom** (le slug suit la place) : renommés par (qui, mission, texte).
  **291 répliques n'ont pas de voix** (≈ 28 000 caractères, le quota du mois n'en avait plus que
  14 618) : Martin a choisi le texte seul pour l'instant.
- La flèche d'un `pirater` mène au terminal (au poste, quand c'est un mouillage) ; e12 visait
  `rampe:erables`, qui n'existe pas — la rampe du phare.
- Plafond de répliques de `test_missions.py` : 10 → 18 par mission (m6 : 20).
- Juges neufs qui jouent les missions jusqu'au bout : `test_tronc_du_tutoriel_plus_long_js.py` (m1-m3),
  `test_tronc_plus_long_js.py` (m4-m6, m97), `test_missions_longues_js.py` (e02, f02, f03, f08, f11, r01,
  s01), `test_p01_lampe_du_phare_js.py`, et ceux de `test_cinq_missions_js.py`, `test_dix_missions_js.py`,
  `test_dix_missions_deux_js.py`, `test_sven_missions_js.py` réécrits pour les étapes neuves.

Vus au banc, pas corrigés : dans p01, `acheter` la batte est déjà fait pour qui a joué m2 (l'extincteur
est le vrai achat) ; `boutique:artisan`/`boutique:industrie` ne donnent aucune flèche ; à 36 px d'un char,
ACTION y remonte au lieu de parler à la personne.
