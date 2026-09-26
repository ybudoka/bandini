# Le brouillard de Baie-des-Brumes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ la ville porte son nom pour vrai — certains matins, un brouillard roule de la baie,
on n'y voit plus à trois coins de rue, et la police non plus.

**Aujourd'hui** la neige de M12 (`neige.js`) a déjà tout le mécanisme : une intensité **fonction du jour
et de l'heure** (pas de simulation, pas de dé), un voile peint par-dessus la ville, une option pour
l'allumer. Le brouillard le réutilise tel quel.

- **Quand** : certains matins, de l'aube à midi, plus épais près de l'eau (Les Quais, La Pointe).
- **Ce qu'il fait** : la vue se referme (un voile qui épaissit avec la distance à l'écran), la **police
  voit moins loin** — semer devient plus facile — et les phares comptent pour vrai (ils sont déjà « à la
  mesure de chaque char »). La corne de brume du phare sonne.
- **Ce qu'il donne aux missions** : une mission `sans_etoile` se prépare pour un matin de brouillard ; le
  Clairon l'annonce la veille (« Brouillard à couper au couteau demain »).

⚠️ **Ce qui guette** : le voile coûte au rendu, sur le téléphone de Martin (la dette « rythme mesuré sur
le vrai téléphone ») — le mesurer avant de l'allumer par défaut, comme la neige.

**Juges** : le même brouillard le même matin pour tout le monde ; la portée de vue de la police baisse
quand il est là et revient après ; aucun dé tiré par le brouillard.

### Le plan (26 sept. 2026)

1. `app/brouillard.py` : les matins (une chance par jour, à l'empreinte du jour), la montée de l'aube, le
   plein, la levée avant midi ; les effets (le voile, la vue de la police, la corne), plus épais aux
   Quais et à La Pointe.
2. `static/js/brouillard.js` : `intensiteA(jour, heure)` pure, comme la neige ; derrière l'option
   `brouillard` (NON par défaut, « BROUILLARD (ESSAI) ») tant que la sonde du navigateur ne l'a pas jugé.
3. Le voile : clair au centre, épais aux bords de l'écran — on voit autour de soi, pas au bout de la rue.
4. La police et les témoins voient moins loin (`Police.voit`, `quelqu_un_voit`) ; la corne du phare
   sonne ; le Clairon l'annonce la veille, sous la manchette.
5. Juges : le même brouillard pour tout le monde, la vue qui baisse et revient, aucun dé, l'annonce de la
   veille ; et la sonde du navigateur (`test_navigateur.py`), comme la neige.

## Notes

_Rien de livré._
