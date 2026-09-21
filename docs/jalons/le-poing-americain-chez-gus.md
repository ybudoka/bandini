# Le poing américain chez Gus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « on devrait aussi pouvoir l'acheter ». Il valait **0 $** et ne se
vendait nulle part : on ne l'avait qu'en couchant un homme de Sal. Il se vend maintenant
**chez Gus, 25 $, en tête de vitrine** (`magasins.py`) : il cogne à peine plus que les
poings (12 contre 8), il coûte donc moins que la fronde (30 $), et les prix des armes
achetables montent toujours dans l'ordre du catalogue. On le ramasse encore sur un homme de
Sal couché. Juges : `test_le_poing_americain_s_achete_chez_gus` (`test_armes.py` — la
vitrine de Gus se lit du moins cher au plus cher) et
`test_le_poing_americain_se_paie_au_comptoir_de_gus` (`test_moteur_js.py` — la porte, le
point `acheter`, la touche ACTION, le sac, puis « DEJA A TOI »).
