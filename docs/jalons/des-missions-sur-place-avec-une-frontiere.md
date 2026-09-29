# Des missions sur place, avec une frontière

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (29 sept. 2026) : « pour certaines missions, je veux des raccourcis vers le moment
de la journée et l'endroit, avec une frontière qui nous garde dans la mission — le tout réutilisable ».
Tranché avec lui : c'est pour **le joueur** (pas une triche), le saut est **automatique** (pas offert),
la frontière est **un district ou un bloc** (pas un cercle), et la franchir **avertit puis fait rater**.

Deux clés **indépendantes** dans le fichier de la mission — une mission peut avoir l'une sans l'autre
(une poursuite gardée dans les Quais n'a pas besoin de saut) :

```python
sur_place = {"lieu": "villa_chemin", "heure": "nuit", "char": True}   # heure : "nuit" ou (0.75, 0.95)
frontiere = "bloc:villa"                                              # ou un district : "quais", "pointe"…
```

**Le saut (`sur_place`).** Après l'accueil du donneur (en personne ou au combiné — l'accueil se joue,
c'est le trajet qu'on saute) : fondu au noir, l'horloge **avance** jusqu'à la fenêtre voulue (jamais en
arrière ; déjà dedans, elle ne bouge pas), et l'on se relève à `lieu` — à pied, ou au volant du char de
la mission si `char`. Les étoiles s'effacent (des heures ont passé, comme à la sieste). Passer minuit
est un **vrai changement de jour** (`nouveauJour` : dette, revenus) — le temps a vraiment passé. Un lieu
de bloc passe par `Blocs.sauter`, qui existe déjà. Le premier `aller … nuit` sur ce lieu est alors fait
en arrivant.

**La frontière (`frontiere`).** Active dès l'arrivée (dès le début sans `sur_place`), jusqu'à la fin de
la mission. Dehors : « RETOURNE DANS LES QUAIS » et un compte de **10 s** au HUD ; revenir l'annule, zéro
fait rater la mission (raison `hors_zone`). Le compte se fige sous une scène ou un menu. Dans une pièce,
c'est la porte qui compte (`B.exterieur`) ; pour un bloc, être en ville, c'est être dehors. Le district
se lit par `Monde.zoneA(x, y).district` (les neuf, nord compris). La mini-carte et la grande carte
grisent le hors-zone.

**Pilotes** : `v01` « La clé du maire » (`bloc:villa`, de nuit — une infiltration ne se quitte pas) et
`q13` « La nuit des Morues » (le district de l'hôtel, de nuit — on tient l'hôtel).

- ⚠️ **Refusé au chargement** (jugé) : un district ou un bloc inconnu, une `heure` mal formée, un `lieu`
  de `sur_place` inconnu, et **tout lieu d'objectif hors de la frontière** de sa mission.
- ⚠️ **Le dernier objectif de v01 se joue au bord** (« RESSORS PAR LE CHEMIN ») : la mission doit être
  finie AVANT que le passage ne ramène en ville, sinon le compte partirait sur une mission gagnée. À
  mesurer au banc.
- ⚠️ **Juges de banc**, chacun cassé par une mutation : le saut pose au lieu et à l'heure (et ne recule
  jamais l'horloge), le char quand `char` ; sortir lance le compte, zéro fait rater, revenir l'annule ;
  une scène fige le compte ; la pièce (la porte compte) ; le bloc (en ville = dehors) ; une mission
  sans les clés ne change pas. Et `test_missions_en_scene_js` pour les deux pilotes.
- ⚠️ La doc suit dans le même passage : la table des clés de
  [comment-monter-les-missions.md](../comment-monter-les-missions.md).
