# Le dojo : des leçons qu'on comprend

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 28 sept. 2026 : « pour apprendre les mouvements d'arts martiaux c'est trop dur et pas clair ». Suite
du [dojo du quartier](le-dojo-du-quartier.md#fiche). Trois causes lues dans le code : rien ne dit quels
boutons (les annonces de Mireille sont poétiques, et seulement dites — pas affichées, le paquet était à son
plafond) ; la fenêtre du « et » ne dure que 0,4 s toutes les 2,25 s, signalée par un claquement et trois
petits points ; et un « et » où l'on ne fait rien compte comme un raté — cinq, et la leçon s'arrête pendant
qu'on cherche encore le bouton.

- **Une carte « quoi faire »** sous le titre de la leçon, avec les vrais boutons de l'appareil qu'on tient
  (les glyphes de l'aide, `Hud.glypheDAction`) : FRAPPE sur le « et » (uppercut, circulaire) ; TIENS FRAPPE…
  lâche sur le « et » (pied de côté) ; COURS + FRAPPE (pied sauté) ; il attaque : ESQUIVE puis FRAPPE
  (balayage) ; SAISIS + VERS LUI / VERS TOI / DE CÔTÉ (hanche, fauchage, sacrifice) ; il arme : SAISIS
  (poignet) ; dans son dos : TIENS SAISIR (étranglement). La recette est une donnée courte de
  `app/dojo.py`, pas un texte.
- **Ne rien faire n'est pas un raté** : un « et » sans geste ne compte pas ; un raté, c'est un geste tenté
  qui ne porte pas (trop tôt, mauvais). Les cinq ratés ne comptent que les vraies tentatives.
- **Le rythme plus lisible, un peu plus large** : la fenêtre passe de 24 à 36 images (0,6 s), et une barre
  dorée se vide sous les trois points pendant qu'elle est ouverte.
- **Juges au banc, au bouton** : une leçon sans geste ne s'arrête pas ; un geste trop tôt est un raté ; chaque
  cours a sa recette ; la carte change de glyphe entre clavier et manette. Mutations, et une capture.
