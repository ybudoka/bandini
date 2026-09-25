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

_Rien de livré._
