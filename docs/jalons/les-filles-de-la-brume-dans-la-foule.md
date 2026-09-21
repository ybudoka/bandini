# Les filles de la Brume dans la foule

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (« on ne distingue plus les prostituées, elles sont trop pareilles que tout
le monde ») : elles n'étaient qu'un **échange de palette** sur le corps commun — un chandail
rose voisin de celui de la passante, des cheveux noirs comme la moitié du catalogue — et à
**douze pixels de large**, sous la teinte de nuit, une couleur ne distingue rien.

- ⚠️ Ce qui se reconnaît à cette taille, c'est un **contour** : `SPRITES.racoleuse` est le
  **seul archétype de piéton à avoir son propre dessin** (jupe évasée **plus large que les
  épaules** — personne d'autre dans le jeu, jambes nues sous l'ourlet, talons, cheveux qui
  tombent de chaque côté du cou, blond platine que personne ne porte ; trois vues, trois
  images de marche, et la pose `couche` **sans laquelle un KO serait resté debout**). Rien
  de plus ne se montre : c'est une silhouette, pas une tenue. Deuxième signe, lu avant même
  la robe : elle **tient son coin** (`poste` à la naissance, rayon de 3 tuiles) — elle
  s'arrête deux fois plus souvent que les autres et revient vers son lampadaire, là où elle
  se remettait à flâner comme tout le monde dix secondes après être apparue ; ⚠️ une
  flânerie dure jusqu'à 330 images, alors elle **redécide toutes les 30** — sinon elle était
  à l'autre bout de la rue avant de seulement songer à revenir (mesuré : 56 px d'écart
  maximum en 40 s, contre 224 px pour une passante). Troisième signe, à bout de bras :
  l'invite ACTION la **nomme** (« LA BRUME — 60 $ ») — `interagir` la servait déjà mais
  `majInvite` l'avait oubliée, on appuyait sur ACTION en espérant que c'en était une ; une
  seule fonction (`filleSousLaMain`) sert les deux, pour que le HUD ne promette jamais autre
  chose que ce qui va se passer. 4 juges (le contour s'évase et le corps commun non, ses
  couleurs ne se recroisent nulle part dans le catalogue, elle tient son coin quand la
  passante s'en va, le HUD la nomme et se tait quand elle est partie)
