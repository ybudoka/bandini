# La voix au téléphone qu'on n'entendait plus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (« les voix au téléphone ne sont pas assez forte ») : ce n'était pas une
question de **volume** mais de **filtre**. Le combiné était un seul `bandpass` à 1,5 kHz (Q
1,2) — bien plus pincé qu'un vrai téléphone, 6 dB par octave de chaque côté. Or c'est **sous
900 Hz** que la parole porte le gros de sa puissance : mesuré, la voix au combiné sortait à
**−6,5 dB à 500 Hz** et **−11 dB à 300 Hz**, donc **plus bas qu'en direct**, et les 1,6× de
compensation étaient loin du compte. C'est maintenant la **vraie bande téléphonique** (300
Hz – 3,4 kHz), dessinée par un passe-haut puis un passe-bas qui laissent **plat** tout ce
qu'il y a entre — et 2× de compensation, parce qu'une voix coupée de ses graves s'entend
moins fort à puissance égale et qu'un appel se prend au milieu des moteurs. Après : **+8,1
dB à 500 Hz, +7,6 dB à 1 kHz, +7,7 dB à 3 kHz** — de +4 à +18 dB selon la fréquence, et le
combiné passe **au-dessus** de la voix en direct sur toute la bande de la parole.

- ⚠️ Encore un test d'une autre **nature** : les juges existants vérifiaient que la réplique
  au téléphone **atteint la sortie** (elle l'atteignait, la chaîne était branchée, la source
  démarrait) — atteindre la sortie ne dit rien de ce qui **en sort**. Les 2 nouveaux ne
  lisent pas les réglages, ils **calculent** la réponse réelle de la chaîne (formules RBJ,
  celles que le Web Audio implémente) en suivant les branchements du gain jusqu'au maître :
  le combiné doit sortir au-dessus du direct sur toute la bande de la parole, et cette bande
  doit rester plate à 6 dB près. Remis l'ancien filtre, ils tombent (12,7 dB d'écart : « le
  combiné pince trop »)
