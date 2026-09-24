# Une passe visuelle sur les pâtés de maison

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « fais une passe visuelle d'amélioration de tous les pâtés de maison »,
puis « les affiches des commerçants doivent être au-dessus du mur » et « les clôtures
doivent clôturer les terrains, pas juste être là seules ». Quatre morceaux, un seul sujet :
ce qu'on voit d'un îlot. **Le sol** — trottoir, herbe, ruelle font **43 % de la ville** (28
%, 10,5 %, 4,7 %) et se peignaient avec **quatre** tuiles de 16 px tirées sur `hash2 % 4` ;
seize usures maintenant (`Monde.USURES_DE_SOL`, la leçon de l'asphalte du stationnement
appliquée à trente fois la surface) et, sur le trottoir, une **dalle de deux tuiles de
côté** : il peignait son joint sur *chaque* tuile, en haut et à gauche — un trait tous les
seize pixels sur le quart de la ville, et ce qu'on lisait c'était la grille de la carte.
Fissures, rapiéçages, taches, mousse au joint ; touffes, plaques de terre et pissenlits dans
le gazon ; goudron, huile, gravier dans la ruelle ; et **huit grains de toit** au lieu de
quatre, avec membrane rapiécée, flaque et coulée de rouille — un entrepôt de La Shop couvre
trois cents tuiles d'un seul tenant, quatre grains dessus font un papier peint.

- ⚠️ Deux règles tiennent tout le bloc, et elles viennent du stationnement : **aucune usure
  ne touche le bord de la tuile** (sinon on redessine la grille), et **une usure est un
  dessin, pas du bruit** (trois ou quatre variantes sur seize). **Les allées de parc** :
  glyphe `g`, de la **poussière de pierre**. Quatre allées de deux tuiles et une place de 5
  × 5 au cœur, ça fait près de la moitié d'un îlot — peintes avec le béton de la rue, nos
  parcs étaient des dalles avec du gazon dessus. Ce n'est pas du sable non plus : la plage
  borde l'eau, l'allée traverse la pelouse. **L'enseigne** monte **au-dessus du mur**
  (`ENSEIGNE_Y` négatif : elle déborde de 12 px sur la tuile de toit) ; le bandeau, l'auvent
  et la vitre se partageaient les 16 px d'*une* tuile — cinq pixels pour le nom, quatre pour
  l'auvent, trois pour la vitrine. Le mur dégagé donne un auvent de 5 px et une **vitrine de
  9** (elle triple, et c'est elle qui s'allume la nuit). Ça tient à un invariant que
  personne n'avait écrit — **au-dessus d'une devanture il y a du toit, sur toute sa
  largeur**, vrai 105 fois sur 105 — et un juge le dit maintenant tout haut, sur cinq
  graines. **Les clôtures** : mesuré sur la ville livrée, **361 tuiles en 80 morceaux, dont
  69 sans un seul coin** (216 tuiles de barre droite) et **24 toutes seules**. Trois
  sources, trois torts : le terrain vague ne peignait qu'**un** côté et **une tuile sur
  deux** (le code le disait : « à demi n'est pas un juge »), la cour de gang que la rangée
  du sud, et le U de `_jardin` se posait tuile par tuile pendant que `poser_cloture` en
  refusait **en silence**. `clore()` pose des **enceintes** — tout ou rien à 75 %, une
  trouée garantie qui donne sur du marchable, aucune tuile laissée seule — et
  `elaguer_les_clotures()` enlève après coup ce que la ville leur mange (le glyphe de
  remplacement se lit dans les voisines, comme `defoncer`).
- ⚠️ **Une clôture ne remplace ni un mur ni une chaussée** : sans ce garde-fou, le barbelé
  de la cour des Skateux mangeait deux colonnes de leur stationnement et « il y a un
  tremplin à La Pointe à tout coup » redevenait une légende. Et la **cour arrière d'un
  bungalow se clôture** enfin — la banlieue clôturait ses terrains *vides* et pas ses
  maisons, l'inverse de ce qu'on voit par la fenêtre. Résultat : **483 tuiles en 41
  enceintes, zéro barre droite, zéro tuile seule**.
- ⚠️ **`Des.brule()`** : le barbelé et le terrain vague tiraient dans le dé PRINCIPAL, un
  coup par tuile. Cesser de tirer décale toute la suite du hasard (`batiment_forme`
  l'écrivait déjà) — mesuré, douze scènes d'amuseur disparaissaient du Faubourg et « un
  amuseur naît au centre-ville » tombait, pour une histoire de clôture. On brûle ce qu'on ne
  tire plus, et on le dit. **Et un rond de terre au pied des arbres de trottoir** (retour de
  Martin, une fois la passe vue) : un arbre planté dans le béton sans rien à son pied n'est
  pas planté, il est *posé* — la place publique du Faubourg en portait quatre debout sur des
  dalles. C'est la **légende** qui décide (`terre` sur l'herbe, le sable et l'allée de
  parc), pas le dessin, et c'est une **couche peinte** cuite avec le morceau : rien ne s'y
  cogne, et elle passe sous les entités — repeinte à chaque image, elle recouvrirait les
  pieds de qui marche juste au nord de l'arbre.
- ⚠️ C'est la **bordure** d'un pixel qui fait la fosse, pas la terre : sans la coupe dans le
  béton, le rond brun se lit comme une tache. 583 arbres sur 596 sont sur du gazon — le jour
  où l'on plantera des arbres de rue pour de bon, chacun aura sa fosse sans qu'on touche à
  une ligne.
- ⚠️ Trois juges de banc tenaient à **un pixel**, au **premier décor de la liste** et à
  **deux pas près** : re-semés et resserrés sur ce qu'ils mesurent vraiment. 11 juges neufs
