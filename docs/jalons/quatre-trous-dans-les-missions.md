# Quatre trous dans les missions

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026), après une vérification des cinq missions et des trois
défis joués de bout en bout au banc, au bouton. Quatre correctifs. Tour du Faubourg et
Livraison sans bosse ne se gagnaient jamais : le panneau ne s'ouvre qu'à pied, et sans char
ces défis ratent à l'image suivante (« SANS CHAR, PAS DE TOUR ») — le chrono ne partira
qu'une fois dans le char. Un char qui explose avec le joueur au volant restait `stationne` :
`exploser()` pose l'épave, puis `descendre()` réécrit l'état ; la carcasse se remontait et
explosait une deuxième fois, et M3 et M4 ne rataient pas quand leur char sautait. Depuis
l'île, la chapelle Sainte-Anne est une destination possible du taxi et de la pizza, et on ne
l'atteint qu'à la nage. Le char de M1 dort à six tuiles du garage : il dormira plus loin.

**Livré.** Le tour et la livraison se commencent au panneau, à pied, et laissent dix
secondes pour monter dans un char (`ATTENTE_CHAR`, les mêmes que la moto du Grand Saut) : le
chrono, la police aux fesses et la référence « sans bosse » partent au volant
(`Histoire.partir`) ; sans char, « DÉFI RATÉ — IL FAUT UN CHAR ». `descendre()` n'écrit plus
`stationne` ni `laisse` sur une épave, et une mission rate dès que son char saute, quel que
soit l'objectif (`majObjectif`) — sauf le fuyard de M2, qu'on casse exprès, et un char déjà
livré. Le taxi et la pizza ne tirent que des lieux qu'un char atteint depuis là où il est
(`atteignableEnChar`, l'eau exclue) : la règle est la route, pas l'île. Le char de M1 dort
dans la ruelle la plus proche à vingt-quatre tuiles du garage au moins, tourné dans le sens
de la ruelle, hors de l'écran du garage. Le lieu porte sa distance (`ruelle:garage:24`) et
vit dans UNE constante, `RUELLE_DU_CHAR_DE_M1` : l'objectif y pose le char, et la coupe de
l'intro (les scènes de la 2e vague) y va le montrer — deux chaînes, et la caméra filmerait
une ruelle vide.

Juges, chacun vu rouge sans sa règle : `test_les_defis_ont_un_panneau_et_un_chrono`
(réécrit : il jugeait le défi qui rate à pied), `test_la_livraison_se_commence_a_pied_et_part_au_volant`,
`test_le_char_de_m1_dort_loin_du_garage` et
`test_le_char_de_la_mission_saute_sous_le_joueur_et_la_mission_rate` (`test_histoire_js.py`) ;
`test_une_epave_reste_une_epave_quand_on_etait_au_volant` et
`test_le_taxi_n_envoie_personne_ou_un_char_ne_va_pas` (`test_moteur_js.py`) ;
`test_les_lieux_des_scenes_existent_dans_la_ville` lit la distance d'une ruelle.

- ⚠️ Ti-Guy dit encore « la ruelle derrière le garage » : le char est maintenant à vingt-quatre
  tuiles. Changer le texte régénère sa voix (`ti_guy-m1-3`).

- ⚠️ Trouvé le même jour et pas dans cette ligne : l'appui d'ACTION qui lance une intro
  saute sa première réplique (`Combat.maj` ouvre le dialogue, `Histoire.maj` relit le même
  appui dans la même image).
