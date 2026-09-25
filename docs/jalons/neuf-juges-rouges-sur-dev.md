# Neuf juges rouges sur dev

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 25 sept. 2026 (« règle les rouges ») : la suite complète ne peut pas être verte
sur `main` tant qu'ils y sont, et rien ne part en prod sans elle._

Neuf juges rouges sur `dev` au commit 4b6f406, **tous déjà rouges avant le travail de la session du 25
sept.** (rejoués sur les commits d'avant) :

1. `test_abri_js::test_une_balle_mord_la_tole_pas_le_conducteur` — « le joueur n'est pas monté » ;
2. `test_histoire_js::test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler` — « ils
   arrivent de hors de l'écran, pas de nulle part sous les yeux » ;
3. `test_histoire_js::test_les_personnages_disent_leur_repos_a_voix_haute` — l'ordre des personnages ;
4. `test_interieurs::test_une_piece_donne_quelque_chose_a_faire[hopital]` — « lachance n'est servi nulle
   part » ;
5. `test_interieurs_js::test_chaque_comptoir_dessine_est_servi_par_le_jeu` — « des points sans libellé
   d'invite : lachance » ;
6. et 7. `test_missions_en_scene_js::test_chaque_intro_se_joue_seule_et_rend_la_ville[f04-défaut]` et
   `[p01-défaut]` — un plan de l'intro ne trouve ni son lieu ni son acteur ;
8. `test_moteur_js::test_la_foule_ne_se_traverse_plus` — 333 chevauchements qui se creusent ;
9. `test_moteur_js::test_la_bagarre_tient_le_budget` — 72 piétons actifs pour 69.

⚠️ Pour chacun : **le juge a-t-il raison ?** Un rouge se règle en réparant le jeu, pas en relâchant le
juge — sauf si le juge mesure mal, et alors on le dit.

## Notes

Livré le 25 sept. 2026. Sept rouges réparés dans le jeu, deux juges qui comptaient mal, corrigés en le
disant :

- **Lachance (4, 5)** — le Dr Lachance attend DEDANS (`point:lachance`), et trois juges tenaient une
  liste écrite à la main des donneurs de pièce (contact, sergent, lulu, ovila). Les listes se lisent
  maintenant dans `missions.PERSONNAGES` ; côté jeu, `libelleDuPoint` (missions.js) donne « PARLER » à tout
  point qui est un personnage (`Histoire.personnageDuPoint`). Le prochain donneur dedans n'aura rien à
  écrire.
- **Repos (3)** — le juge figeait l'ordre et la liste exacte des personnages abordables : il demande
  maintenant que les quinze d'origine y soient (sous-ensemble), les nouveaux s'y ajoutent sans le casser.
- **Cravates de m2 (2)** — `placeDArrivee` gardait une place « hors champ » tant qu'elle était loin du
  JOUEUR, pas hors de l'ÉCRAN : à 200 px en largeur, on les voyait naître. Le test est maintenant le
  rectangle de la vue (`VW / 2 + 16`, `VH / 2 + 16`).
- **f04 et p01 (6, 7)** — `boutique:artisan` ne trouvait aucune boutique : `boutiquex` cherchait le mot
  dans l'enseigne seulement. Réparé en même temps par une autre session (be7eb60, « trois défauts vus au
  banc »), et mieux : le genre de la devanture, et une porte peinte seulement en dernier recours. C'est sa
  version qui reste ; d'ici reste le juge `test_une_boutique_se_trouve_par_son_genre_et_par_son_enseigne`.
- **Abri (1)** — le juge tirait cinq balles de pistolet (×30) sur une voiture de 100 PV : elle explosait
  avant la fin, « le joueur n'est pas monté ». Rouge depuis 8a0e098 (dés décalés, trouvé par bisect). Le
  juge mesure la tôle, pas la solidité : la voiture a 1000 PV.
- **Budget de la bagarre (9)** — le « +28 » du plafond comptait « les trois personnages de l'histoire » ;
  ils sont seize depuis M16, dehors et jamais endormis, comme les vendeurs. Le juge les compte un par un
  (+25 pour les trois déjà dedans : il ne se relâche pas d'une personne) et ajoute le vrai garde-fou —
  aucun personnage posé deux fois.
- **La foule (8)** — 333 creusements, tous la même paire : un donneur du terminus et le vendeur de la
  roulotte de café, à 7 px. La roulotte est fermée au matin, son vendeur arrive à l'ouverture, à son
  poste — sur le donneur. Deux corps plantés l'un dans l'autre se poussent hors de leur place, cessent de
  céder et y reviennent, six images sur six. Deux réparations dans `placeVisible` (histoire.js) :
  `placeTenue` compte le STAND d'un ambulant (toujours là, ouvert ou non) à deux tuiles ; et un donneur
  qui a épuisé ses essais (Fern, troisième au terminus après Ti-Guy et Mo) prend une place moins bonne
  mais libre (`repli`), puis un tour plus loin, avant de retomber sur `premiere`. Ce tour ne se fait que
  si rien n'a été trouvé : aucun autre donneur ne bouge.
- **Un dixième, en passant** — `test_amuseurs_js::test_le_public_applaudit_paie_et_se_renouvelle` a
  rougi sous ce correctif : il posait son jongleur à 36 px du joueur, c'est-à-dire sur la roulotte de café,
  et ne tenait que parce que Ti-Guy y était aussi et poussait le jongleur à côté. Il le pose maintenant sur
  la scène de la carte la plus proche, comme le jeu. Douze graines, base contre build : onze vertes des deux
  côtés (à la 99, un incident fait fuir le jongleur avant que le cercle paie).
