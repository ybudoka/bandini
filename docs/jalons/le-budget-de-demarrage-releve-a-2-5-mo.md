# Le budget de démarrage relevé à 2,5 Mo

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « augmente la limite ». Les voix de la rue passées en 44 kHz avaient
mangé 200 Ko : bruitages et passants à **1,41 Mo sur 1,5**, 94 Ko de marge — le prochain
bruitage débordait. Relevé à **2,5 Mo** dans `test_audio.py` (1,1 Mo de marge), et pas à
1,6 : ce plafond a déjà été relevé cinq fois par bonds de 50 Ko, et un budget qu'on relève à
chaque ajout n'est plus un budget.

- ⚠️ Ce que le plafond protège, mesuré dans `son.js` : les bruitages et les voix de la rue
  se téléchargent **en arrière-plan** après le premier geste (`reveiller` →
  `chargerEchantillons`, `Voix.charger`), le jeu n'attend pas — chaque effet garde sa
  synthèse en attendant. Il coûte donc de la bande passante, pas un écran de chargement.
