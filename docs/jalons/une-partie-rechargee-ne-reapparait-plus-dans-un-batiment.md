# Une partie rechargée ne réapparaît plus dans un bâtiment

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (21 sept. 2026, capture : le cousin debout sur le toit du garage Bandini, Marco
qui hèle devant la porte) : « l'apparition n'est pas correcte, j'ai apparu dans le bâtiment ».
Sa partie (emplacement 1, jour 277) est sauvegardée à 2549, 763 : la tuile 159, 47, deux rangées
de toit au-dessus de la porte du garage (159, 49), sur la carte d'aujourd'hui (même empreinte).
`commencer` pose le joueur à `p.x`, `p.y` sans regarder ce qu'il y a dessous, et rien ne le sort
d'un mur ensuite : il y reste pris.

La position sauvegardée est celle du joueur à la dernière sauvegarde (toutes les dix secondes), et
au volant c'est celle du char. Un char sous le toit d'un garage (la baie du rideau, livrée ce
matin), un bateau sur l'eau, un corps passé dans une façade : tout ça s'écrit tel quel, et la
partie se rouvre dedans.

- ⚠️ Le correctif est au CHARGEMENT, pas à la sauvegarde : c'est lui qui répare les parties déjà
  écrites, celle de Martin comprise. Une position où un piéton ne tient pas (mur, eau, grillage,
  barbelé) glisse sur la tuile à pied la plus proche, hors chaussée et hors meuble, au pixel près ;
  une position où l'on tient ne bouge pas d'un pixel.
- ⚠️ Un juge : la position de Martin, rechargée, réapparaît sur le trottoir devant le garage — rouge
  avant (le joueur reste sur le toit) ; et une position libre revient exactement où elle était.

## Notes

**Livré le 21 sept. 2026.**

- **`Jeu.commencer` passe la position par `ouTenirDebout`** avant de créer le joueur : une tuile où
  un piéton tient (`Monde.bloque(…, MASQUE_PIETON)` faux) garde son pixel ; sinon on prend la tuile
  à pied (`marchablePieton`, hors meuble) dont le centre est le plus près du pixel sauvegardé, à
  12 tuiles au plus. La partie de Martin (2549, 763, sur le toit) se rouvre à 159, 50 : le
  trottoir devant la porte du garage, pas la ruelle derrière (à égalité de rangées, le pixel
  sauvegardé est plus près de l'avant).
- ⚠️ **L'eau compte comme un mur** au chargement : une partie sauvegardée à la nage ou sur un
  bateau se rouvre sur la rive la plus proche, plus dans l'eau.
- Les juges (`test_districts_js`) : la position de Martin (deux rangées au-dessus de la porte), le
  milieu de la baie du rideau (le centre d'un char garé dessous), et une place sur le trottoir qui
  revient au pixel. Mutations : sans le correctif, la partie se rouvre sur le toit (2549, 763) et
  dans la baie ; avec « la première tuile trouvée » au lieu de la plus proche, on se rouvre dix
  tuiles au nord-ouest, derrière le garage. Rouge les deux fois.
- ⚠️ **Ce qui n'est pas trouvé : comment la partie s'est écrite là.** Martin : « directement en
  chargeant la partie… peut-être le garage, je suis pas certain ». Ce que le banc montre :
  - **Un chemin sûr vers un mur** : au volant sous le toit de Ti-Guy (auto ou autobus), la
    sauvegarde écrit le centre du char, 2512, 776 — un toit. Et l'autobus peut y rester : il passe
    le seuil sans que l'atelier le prenne tout de suite (pas de menu, rideau levé), et ACTION n'y
    fait pas descendre (« RECULE D'ABORD »). La sauvegarde automatique écrit ce mur toutes les dix
    secondes, et la partie se rouvrait dedans.
  - **2549, 763 n'est pas ce chemin-là** : sous le rideau, le bus ne dépasse pas x = 2516. Ce sont
    les coordonnées où `deplacerCercle` colle un corps de rayon 5 qui pousse à GAUCHE contre la
    colonne 158 et en BAS contre la rangée 48 (159 × 16 + 5, 48 × 16 − 5) : le cousin était déjà
    dans le toit, et il poussait vers le trottoir. La sauvegarde du 21 sept., 16 h 20, est celle
    d'après le chargement.
  - Piste non vérifiée : le serveur de dev sert le JS tel qu'il est sur le disque, et d'autres
    sessions y écrivaient le garage toute la journée — un état entre deux commits a pu laisser
    passer ce que le code livré ne laisse pas passer.

  Le correctif rend la partie jouable quoi qu'il soit arrivé ; si le cousin se retrouve encore
  dans un toit EN JOUANT, sans recharger, c'est un autre bogue.
- La suite complète : 3 720 verts, 9 rouges. Les deux rouges d'avant (les cravates de M2, la
  foule) rougissent aussi sans ce correctif ; les trois de `test_version` : la version est passée
  de 0.177 à 0.179 pendant les 30 minutes de la suite ; les quatre du navigateur, rejoués seuls,
  sont verts (39 verts avec `test_version`).
