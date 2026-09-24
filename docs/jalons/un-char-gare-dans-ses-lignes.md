# Un char garé dans ses lignes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui (« les voitures sont mal garré ») : dans un
stationnement, les chars débordaient par le nez sur le trottoir et laissaient le fond de
leur case vide. La cause est dans la ligne précédente — **la vue plongeante**. Le jour où
les poses `haut` et `bas` sont passées de douze rangées à la **longueur** du char (28 px
pour une berline), elles sont restées posées à la ligne de sol du **profil**. Or ces deux
lignes ne sont pas au même endroit : de profil, le dessin est une **élévation** — sa
dernière rangée est le **flanc**, et le flanc passe par le milieu du char, donc l'ancre
tombe sur `v.y` comme les pieds d'un passant ; de dos, c'est le char **vu d'en haut** — sa
dernière rangée est le **pare-chocs**, à une **demi-longueur** de `v.y`. Posée sur `v.y`,
elle mettait 28 px de caisse au nord d'un centre qui n'en compte que 14 : **tout char tourné
vers le nord ou le sud se dessinait 14 px devant lui-même**, garé comme en marche. Une case
de stationnement le montre au premier coup d'œil — elle fait 32 px de creux, le gabarit
exact d'une auto, alors le nez sortait sur le trottoir et le fond restait vide.

- ⚠️ **L'ancre du sprite ne bouge pas** (la même pour les trois poses, sinon le char saute
  d'un pixel en tournant) : c'est le SOL qu'on va chercher là où il est (`solDeLaPose`), et
  il vient de l'**empreinte du catalogue** — la même que la physique et que l'ombre. Ce
  qu'on voit est exactement ce qui bloque.
- ⚠️ **Et le cavalier prend le même décalage** : sans ça, le passant assis sur un vélo
  pédalait une demi-longueur devant sa selle. Mesuré après, sur les onze véhicules debout et
  les quatre caps : la dernière rangée tombe à la demi-longueur du centre (0 avant). 2 juges
  de banc, rouges avant (la caisse tient dans son empreinte de dos comme de face sans
  dépasser ni derrière ni devant, et le profil pose toujours sa ligne de sol sur `v.y` ; le
  cavalier est assis au milieu de sa machine)
