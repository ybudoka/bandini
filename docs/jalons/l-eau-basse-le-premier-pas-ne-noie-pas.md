# L'eau basse : le premier pas ne noie pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « la premiere case de l eau ne prend pas d'énergie nie ne noie ».

- ⚠️ **Mesuré** : l'eau n'a aujourd'hui qu'une seule profondeur — dès le premier pixel
  mouillé le souffle part à **0,5 par image**, et immobile les pieds dans l'eau au bord de
  la grève **on coule en 3,3 s** (200 images pour 100 points), avec le réveil à l'hôpital et
  la facture.
- ⚠️ **Le plan le promettait déjà** : « L'eau n'est plus un mur » écrivait noir sur blanc
  « **il faut un bord** — on ne doit pas passer d'un pas de la terre ferme à la noyade », et
  c'est le seul point de cette fiche resté ouvert. Depuis, la grève s'est meublée et un
  **enfant barbote** dans la première tuile sans jamais rien risquer, à côté d'un joueur qui
  s'y noie. La règle tient en une phrase : **l'eau qui touche la terre est de l'eau basse —
  on y a pied**. Elle se **lit** dans la carte (quatre voisines en croix, la même mesure que
  le `trop_loin` de l'enfant qui barbote), elle ne se marque pas : un glyphe de haut-fond
  serait une deuxième vérité à tenir à jour, et la moindre retouche de la côte la ferait
  mentir. **975 tuiles sur 18 778** (5 %) : un liseré, pas une plage.
- ⚠️ **Et la géographie de M8 tient toujours** : les deux berges du chenal deviennent
  gratuites, la traversée passe de 88 à **72 points sur 100** — un pari, toujours au-dessus
  du seuil de 60 en deçà duquel le pont ne servirait plus à rien ; le juge de `test_eau.py`
  refait le calcul avec les deux berges en moins. ✅ **Livré** (16 sept. 2026) :
  `Monde.eauBasse(tx, ty)` — de l'eau dont une des quatre voisines n'en est pas — et
  `majJoueur` n'en tire que deux conséquences : le souffle ne part pas, `noyade` n'est pas
  appelée. **On y patauge quand même** à la vitesse de la nage, avec les remous et le corps
  coupé à la ligne d'eau : c'est de l'eau, ça se voit et ça ralentit — ce qui change, c'est
  ce qu'on y risque.
- ⚠️ **Et la barre remonte**, comme sur le sable (la régénération ordinaire, jamais le
  surplus) : l'eau basse est de la terre ferme pour le souffle, pas un purgatoire où il
  resterait figé — sinon revenir au bord à bout de souffle laissait le joueur planté dans
  dix centimètres d'eau, vivant et incapable de repartir.
- ⚠️ **Hors carte n'est pas de la terre** : la baie touche le bord du monde, et compter le
  vide comme une rive aurait fait un haut-fond du large.
- ⚠️ **Deux juges d'à côté ont dû recompter, et c'est le vrai travail de cette fiche** : le
  chenal du pont paie maintenant **9 tuiles sur 11** (72 points, toujours un pari), et
  `test_moteur_js` mesurait « une seconde de nage » **depuis l'entrée dans l'eau** — seize
  images de patauge dans le compte, 22 points là où la fiche en promet 30 ; il attend
  désormais d'être au large pour partir sa mesure.
- ⚠️ **Et un juge neuf a failli passer pour la mauvaise raison** : il lisait `B.transition`
  **à la fin** de sa boucle, quand le fondu est retombé et qu'on s'est réveillé à l'hôpital
  avec 100 points tout neufs — il aurait félicité le code d'avant pour une noyade complète.
  La noyade se guette **pendant** la boucle.
- ⚠️ **Ce qui ne change pas** : un char qui touche l'eau coule, l'eau basse comprise — c'est
  une règle de char, pas de souffle, et elle a ses propres juges. 5 juges neufs
  (`test_eau_basse_js.py`), **rouge-avant prouvé sur trois** dans un worktree isolé ; 1675
  tests.
