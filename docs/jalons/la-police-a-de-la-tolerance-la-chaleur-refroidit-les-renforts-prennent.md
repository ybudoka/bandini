# La police a de la tolérance : la chaleur refroidit, les renforts prennent le temps de venir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin en jouant (22 sept. 2026) : « la police arrive trop rapidement et les
étoiles aussi. il faut plus de tolérance ». Trois causes lues dans police.js.

- ⚠️ La chaleur ne refroidit JAMAIS : trois petits délits espacés de vingt minutes font une
  étoile, pour toute la partie.
- ⚠️ Un carambolage compte chaque accrochage : trois chars touchés devant un passant, c'est
  une étoile d'un coup, sans témoin à convaincre.
- ⚠️ Les renforts d'un palier naissent à l'instant où l'étoile tombe, à moins de 420 px d'où
  l'on t'a vu (parfois d'une porte à l'écran), et courent à 1,6 px/image : trois secondes et
  demie plus tard, ils sont là. Le correctif, en données dans app/recherche.py : la chaleur
  refroidit après un répit sans nouveau délit compté (les étoiles, elles, ne tombent
  toujours que hors de vue) ; un même délit de conduite répété dans la foulée ne compte
  qu'une fois ; les renforts d'une étoile neuve arrivent après un délai, jamais d'une porte
  à l'écran — les agents déjà sur place réagissent tout de suite. Des juges pour chacune des
  trois, et une mutation pour chacun.
