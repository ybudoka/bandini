# Pas de stationnement en arrière du casse-croûte du ciné-parc

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (29 sept. 2026) : « ne mets pas de stationnement en arrière de la cabane ». Depuis
que le casse-croûte est au milieu du terrain, les cases derrière lui (au sud, colonnes 18 à
25 des deux dernières rangées) regardent un mur, pas l'écran : elles redeviennent de
l'asphalte. Un juge : aucune case dans l'ombre de la cabane.

## Notes

_Livré le 29 sept. 2026._

- **Les cases derrière la cabane** (`app/blocs/cineparc.py`) : les colonnes 18 à 25 des rangées 16 et 20, au sud du
  casse-croûte, redeviennent de l'asphalte — seize cases de moins, qui regardaient le mur de la cabane et pas
  l'écran. Les deux rangées gardent dix cases de chaque côté, en paires : les poteaux à haut-parleur tombent juste,
  et le devant de la porte s'ouvre sur une grande place d'asphalte.
- **Juge** (`test_cineparc_js.py`, celui de la cabane au milieu du terrain) : aucune case dans les colonnes de la
  cabane, au sud d'elle. Vu rougir en remettant les cases de la rangée 16. Regardé dans Chromium.
- Les spectateurs se garent ailleurs (leurs places se tirent à l'empreinte dans la liste des cases, qui a
  raccourci) — dans le bloc seulement.
