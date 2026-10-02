# La façade du garage Bandini

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (2 oct. 2026)_, sur une capture du garage la nuit, char rangé dans la baie : « il faudrait ajuster
ça », puis « mets aussi la façade pleine largeur si possible ».

Deux défauts sur la même capture :

- **La façade s'arrête au milieu du rideau.** Le mur à étages d'un commerce s'étend jusqu'au bout de son bâtiment
  sur le mur nu (`F`, `W` : `Monde.murDuBatiment`, `etages._mur`). Le rideau du garage (`G`, deux tuiles) l'arrête,
  et la devanture de GARAGE BANDINI commence sur sa deuxième tuile (`GWDW`) : la façade (le bardeau, les fenêtres
  d'étage) ne couvre ni la première tuile du rideau ni la brique d'à côté. Ce qu'on veut : le mur va d'un bout à
  l'autre du bâtiment, le rideau percé dedans.
- **Le nez du char sort du toit.** Un char rangé au fond de la baie y a son centre, et son avant dépasse
  au-dessus. Le dessin ne le cache que sur la baie (`Monde.sousLeToit`) : le capot se peint par-dessus la façade, en
  tache brune.

**Juges** : le mur du garage couvre tout son bâtiment, rideau compris, et c'est la seule devanture qui bouge ; un
char au fond de la baie n'a plus un pixel au-dessus du toit.

## Notes
