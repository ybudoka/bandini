# Trois juges rouges neufs sur dev

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « les régler ». Suite complète sur ee88faed : 6 914 verts, 3 rouges,
tous rouges aussi sur d02326a6 (venus d'autres sessions dans l'heure) : 1)
test_debug_js::test_chaque_endroit_cle_se_rejoint_et_sa_porte_s_ouvre — le Prestige (menu
ENDROITS CLÉS : rendu, pas de menu) ; 2)
test_chantiers_js::test_un_char_du_trafic_s_arrete_a_l_arret_et_repart_a_lentement — « à
LENTEMENT, le char n'a pas repris sa route » ; 3)
test_mise_en_scene::test_chaque_mission_est_finie — « m54 intro : lieu inconnu 'poste' ».

- ⚠️ Le juge a-t-il raison ? On répare le jeu, sauf si le juge mesure mal — et alors on le
  dit.

## Notes

Livré le 29 sept. 2026.

- **1) Le Prestige au menu — le juge avait tort** (fautif : 6a805c2f, le point du Salon devant le portail).
  Le menu ENDROITS CLÉS y pose le joueur, ACTION n'ouvre rien ; décision écrite (« Le lot devant,
  clôturé »), jugée (`test_le_point_du_salon_mene_au_portail`), et Martin, 29 sept. : « laisser comme ça ».
  Pour un lot clôturé, le juge exige le portail au-dessus du point et la porte du lot dans l'axe, qui mène à
  ce lieu ; un témoin exige le Salon au menu. Deux mutations le font rougir.
- **2) Le char au chantier — le juge passait par chance de foule** (fautif : 84d48f52, qui change qui naît en
  ville). Une passante bute contre le signaleur (figé), `demeler` la pousse au bord de la voie, le char
  s'arrête pour elle — à raison. Le juge écarte la foule (l'équipe du chantier reste) et exige qu'à
  LENTEMENT le char passe SANS FORCER : il ne mordait pas avant (« LENTEMENT arrête encore » restait vert,
  le char finissait par forcer).
- **3) m54 — le jeu avait tort** (fautif : 967cf129, le registre au poste de police). Le premier objectif
  est devenu `ou: "poste"`, un nom de porte nu ; m54 n'écrit pas de scène, et `lieu_a_montrer` filmait ce
  nom tel quel alors qu'il préfixe déjà `porte:` pour un `lieu`. Un `ou` nu se montre maintenant
  `porte:<ou>` (sauf `LIEUX_NOMMES` et `quai`) : même pixel en jeu. La mutation refait le rouge exact.

⚠️ Vu en route, à trancher par Martin : une passante qui flâne contre le signaleur est poussée par `demeler`
au bord de la chaussée et y reste ≈ 8 s, bloquant le trafic jusqu'à ce qu'un char force — contraire à « on
ne pose pas le pied sur la chaussée » (`demeler` en protège déjà l'enfant à vélo, pas les autres).

