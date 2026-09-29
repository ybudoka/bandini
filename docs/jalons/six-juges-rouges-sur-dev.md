# Six juges rouges sur dev

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « les rouges qui restent ». Rouges sur dev (bbca3176), rejoués
seuls : 1) test_quai_se_marche::test_aucun_quai_ni_terrain_vague_ne_se_referme — « 3 tuiles
de friche enfermées par du décor : (375, 16), (381, 24), (381, 25) » ; 2)
test_interieurs::test_les_lieux_des_missions_existent — « m53 : amarrage:hopital
introuvable » ; 3)
test_parole::test_la_rue_se_tait_devant_une_arme_et_crie_apres_un_coup_de_feu — la rumeur ne
suit pas la foule (peur 0,18 pour 1 voulu) ; 4)
test_navigateur::test_la_premiere_mission_se_joue_en_scenes_de_l_intro_a_la_fin — « parler à
Ti-Guy ne joue pas sa scène d'intro » ; 5, 6)
test_navigateur::test_les_echantillons_se_chargent_dans_un_vrai_navigateur et
::test_l_ambiance_et_les_voix_se_decodent — délai de 20 s dépassé, même seuls.

- ⚠️ Pour chacun : le juge a-t-il raison ? On répare le jeu, sauf si le juge mesure mal — et
  alors on le dit.
