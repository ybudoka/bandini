# Le poste clôturé : du barbelé et une barrière coulissante

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (23 sept. 2026) : « le poste de police doit etre completement cloturé
barbelé pour ne pas qu'on vole les auto. crée une nouvelle cloture coulissante avec comme
morte une cloture barbelé. » (lu : « comme modèle »). Aujourd'hui le lot des autos-patrouilles (3 × 9 tuiles, collé
au mur est du poste) est ouvert sur la ruelle, le côté et la rue : on y entre à pied et on
repart avec une auto-patrouille. Le lot se ferme de barbelé (`X`) sur ses trois côtés
libres, et sa sortie sur la rue devient une BARRIÈRE COULISSANTE — un glyphe neuf (`Z`),
barbelée comme le reste (solidité 5, ni à pied ni en char, un lourd ne la défonce pas).

- ⚠️ Elle s'ouvre pour une auto-patrouille CONDUITE (par la police ou par le joueur qui en a
  volé une ailleurs), jamais pour un piéton ni un char civil : le panneau glisse le long de
  son rail, la tuile devient libre une fois ouverte, et se referme quand plus rien n'est
  dessous.
- ⚠️ La connexité : une barrière est une OUVERTURE qui a une clé — `franchissable` la
  compte, sinon le lot serait une poche fermée de barbelé.
- ⚠️ Posée dans `_stationnement_de_service`, donc EN DERNIER : rien d'autre ne bouge dans la
  ville (le juge « le lot ne déplace rien »). Juges : le lot est clos (on n'en sort que par
  la barrière), la barrière est large comme l'allée et donne sur la rue ; au banc, à pied et
  en char civil elle reste fermée et bloque, une auto-patrouille conduite l'ouvre, passe, et
  elle se referme. Capture avant de livrer.
