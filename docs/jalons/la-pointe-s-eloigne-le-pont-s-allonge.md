# La Pointe s'éloigne : le pont s'allonge

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « aggrandit la carte vers le bas et déplace l'ile ou est la
foire vers le bas pour allonger le pont et l'éloigner du reste de la ville ».

- **Une seule rangée change, et c'est par elle que la carte grandit.** La ville est une grille de
  20 colonnes × 12 rangées de blocs (`carte.COLONNES`, `carte.RANGEES`) ; la première rangée de la
  bande sud **EST** le chenal que le pont enjambe. Elle passe de **11 à 24 tuiles** : le pont fait
  24 tuiles au lieu de 11, La Pointe descend de 13, et la carte passe de **419 × 211 à 419 × 224**.
  Aucune autre rangée ne bouge : la foire garde son enceinte de 52 × 31 à la tuile près (elle
  descend de 13, rien d'autre), comme les bois, les maisons et le phare.
- **Ce que cette rangée porte ailleurs.** Elle est aussi la rangée nord des Quais et le haut de la
  baie. Les blocs de commerces du port deviennent donc profonds — deux rangées de bâtiments dos à
  dos au lieu d'une — et la baie gagne treize tuiles. C'était le prix : une rangée traverse toute
  la ville, on ne l'allonge pas pour un seul district. Les autres formes (insérer une rangée,
  descendre le district) coûtent la même chose et abîment la foire en plus.
- **Le chenal élargi se remplissait de sable.** Mesuré avant de livrer : à 24 tuiles, la règle des
  plages (un tiers du bassin quand il y a une rive en face) en donnait **huit par rive**, et la
  traversée à la nage retombait de 24 tuiles d'eau à **11** — le chenal plus large ne coûtait plus
  rien, et la coque du traversier passait sur du sable. Règle ajoutée : **un bassin qu'un pont
  enjambe n'a pas de plage sur les deux rives qu'il relie** (`_rives_d_un_pont`). L'appel est sauté
  en entier, avant le premier dé de `_plage` : pas une plage de la ville ne se déplace.
- **Le prix de la nage monte d'un cran, et c'est la vraie décision.** Onze tuiles se nageaient à
  jeun (72 points de souffle sur 100). La traversée la plus courte fait maintenant **22 tuiles**
  (au coin nord-ouest, pas sous le pont) : **160 points à jeun — impossible — et 80 avec un café**.
  Trois crans, trois endroits : la ville à pied, La Pointe au café, l'Île-aux-Corneilles au café
  **et** l'estomac plein.
- **Le juge du chenal ne lit plus une colonne.** `test_le_chenal_du_pont_est_un_pari_pas_une_promenade`
  mesurait la hauteur d'eau sous le tablier ; il fait maintenant le tour de l'eau (le pont défait)
  et prend **la nage la plus courte de La Pointe à la ville**. C'est ce qui a montré le sable :
  l'ancien juge voyait 24 et se taisait pendant qu'on traversait en 11. Un second juge dit que le
  tablier va d'une rive à l'autre (le chenal sous lui vaut sa longueur, ni plus ni moins).
- **L'île descend de treize tuiles avec la bande sud** (`ile.ILE["y"]` : 139 → 152). Sa rive la plus
  proche fait toujours 30 tuiles d'eau. La laisser en place la mettait dans le couloir du
  traversier : celui-ci prend la traversée la plus au nord-ouest, la nouvelle passait à une tuile de
  sa ceinture, et la ville n'était plus la même avec et sans l'île.
- **Toute la ville est re-tirée, et c'était inévitable.** Les îlots consomment le dé commun dans
  l'ordre `(colonne, rangée)` : des blocs de port plus profonds, c'est plus de parcelles, donc tout
  ce qui vient après change de place — 22 % des tuiles du nord, qui n'était pourtant pas touché.
  **Douze juges sans rapport sont tombés**, tous verts sur la base ; aucun n'a été assoupli sans
  raison écrite :
  - **la ville s'est livrée sans camion à ordures** (`eboueurs.tracer` rendait `None`, sans un mot) :
    la boucle n'essayait qu'**une seule** place pour sa première étape, et celle-là partait vers
    l'ouest sur un boulevard qui ne mène nulle part. La première étape a maintenant ses candidates
    comme les autres ; une boucle qui marchait du premier coup ne change pas d'une tuile ;
  - **la ligne 2 laissait 148 tuiles sans un arrêt** (84 permis) : elle descendait le trottoir du
    **bord de la carte**, où l'abribus tomberait hors de la ville — donc aucun arrêt, jamais. Cette
    voie-là coûte maintenant comme une voie du milieu (`COUT_SANS_ABRI`), et la boucle est choisie
    en mesurant d'avance son plus long désert ;
  - **le tramway est passé de 12 arrêts à 4 et le quai du traversier n'avait plus le sien** : une
    rame roule par **paires de voies opposées**, et sur un boulevard à quatre voies la seule paire
    est celle du MILIEU — aucune ne longe un trottoir. La voie du milieu lui coûte donc elle aussi
    (`tramway.COUT_VOIE_DU_MILIEU = 8`, plus cher qu'un virage), et il a repris les rues à deux
    voies. Le quai ayant descendu de 17 tuiles, son arrêt est à 36 tuiles et non 29
    (`PRES_DU_TRAVERSIER` : 32 → 40) ;
  - **« la ville avec ou sans chantiers est la même » n'était vrai que par chance** : l'enceinte
    d'un chantier s'écartait du mobilier avec **une marge d'une tuile**, et cette marge-là a mordu
    un bord de rue de sept tuiles — les 1 900 meubles qui suivaient se décalaient tous. L'enceinte
    s'écarte maintenant sans sa marge : ses tuiles sont un LOT de bâtiment, jamais un bord de rue ;
  - **la cale du cargo était SUR sa chaîne** : l'enceinte du mouillage descend désormais avec la
    cale au lieu de la couper ;
  - **trois juges de goût, relus plutôt que remontés** : la saleté se mesure en objets **par mille
    tuiles marchables** (3,5 pour mille, comme les 3,2 acceptés à l'œil ; le plafond en objets
    rougissait parce que la ville a grandi) ; le panneau du Grand Saut a droit à ses 8 tuiles, qui
    sont ce que son code permet depuis toujours (`[3, 5, 7]` + le pied) ; et le filet
    (`boucher_les_poches`) a le droit de reboucher une encoignure de 2 × 2 entre deux entrepôts sur
    la graine livrée — pas une cour (moins de dix tuiles).
- **Suite complète verte** : 2 313 juges Python, la suite JS, `ruff`.
