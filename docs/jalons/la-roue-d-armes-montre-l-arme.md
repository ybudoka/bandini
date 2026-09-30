# La roue d'armes montre l'arme

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Un panneau à droite de la roue, pour l'arme sous le pouce : un portrait pixel 48×24 par arme
(affiché ×2, il pâlit à sec), trois barres avec leurs chiffres (dégâts, portée en mètres,
cadence en coups par seconde), les munitions et le bruit, des étiquettes (automatique, en
cloche, explose, brûle, assomme…) et un descriptif de trois lignes au plus. Les descriptifs
et les portraits vivent dans le JS : le paquet des définitions n'a plus de marge, et Python
ne les lit jamais. Juges : chaque arme du catalogue a son portrait et son descriptif, le
descriptif tient, le panneau reste dans l'écran ; capture Chromium avant de livrer.
