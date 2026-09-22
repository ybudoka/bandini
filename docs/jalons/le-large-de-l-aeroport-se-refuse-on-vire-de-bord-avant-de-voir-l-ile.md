# Le large de l'aéroport se refuse : on vire de bord avant de voir l'île

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « je voudrais que même en bateau on ne puisse pas aller
à l'île de l'aéroport avant que le pont soit réparé, une barrière invisible nous fait
tourner de bord avant qu'on puisse voir l'île ». Aujourd'hui rien n'arrête une chaloupe : le
large est ouvert jusqu'à la plage de l'île, et l'île cachée sur la carte (`masque`) se voit
à l'écran dès qu'on s'en approche. Remède : un large refusé autour de l'île, le rectangle du
masque élargi de ce que la caméra montre au plus loin (la demi-vue, 480 × 270, plus l'avance
de la caméra au volant, plus une tuile) — calculé côté jeu, où vit la caméra, et levé avec
le masque (`a01`). Une coque (ou un char blindé qui roule sur l'eau) qui s'en approche vire
de bord toute seule : le volant lui est pris le temps du demi-tour, le HUD dit pourquoi, et
elle ne franchit jamais la ligne. Un nageur y est repoussé de même : la travée manquante ne
se nage plus jusqu'au bout. Déjà dedans (vieille sauvegarde), on circule. Le mode photo ne
va pas non plus où l'œil ne va pas. Juges au bouton : un bateau lancé vers l'île par le nord
et par l'ouest vire de bord sans que la caméra montre une tuile du masque ; le nageur de la
travée est renvoyé ; TÉMOIN : `a01` faite, on passe.
