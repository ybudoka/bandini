# Les passants des petites jobs

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « Hé! Le jeune! » — le débardeur de t02

## En bref

| | |
|---|---|
| Slugs | `passant`, `passante` |
| Rôle | deux RÔLES, pas des personnes : le passant ordinaire qui t'interpelle dans la rue pour une petite job (M16, arc T) |
| Où | nulle part (`ou` vide) : `static/js/jobs.js` en fait naître un, de l'archétype et du district que la mission nomme (`"passant": {"archetype", "district", "nom"}`) |
| Voix | **Felix Tabarnak** (passant) et **Amélie** (passante) — les voix des passants de la rue (`audio.VOIX_PAR_GENRE`) |
| Bulle | leur hèlement (la partie `hele` de la mission, 16 caractères au plus) |
| Missions | **t01** (le banlieusard), **t02** (le débardeur), **t03** (la dame à la valise), **t04** (le jeune de La Pointe), **t05** (la passante), **t06** (le gérant de la taverne), **t09** (le p'tit camelot), **t11** (le promeneur), **t12** (le livreur), **t13** (le vieux), **t14** (la mariée), **t15** (le retardataire) |

## Leur histoire

Ils n'en ont pas, et c'est le principe : la ville est pleine de monde qui a un petit problème — un lunch, un autobus,
une sacoche, une pelle. Chacun a le nom que sa mission lui donne dans la boîte de dialogue (« Le débardeur »), la
tenue de son archétype, et pas de portrait : on ne le reverra pas.

## Comment ils parlent

- **Comme la rue** : court, pressé, drôle sans le vouloir. Un détail concret par réplique (la moutarde, les œufs dans
  la valise, le rouge à lèvres).
- **Tout en personne** : ils n'ont pas ton numéro — ni appel, ni échec au combiné (`histoire.js`, `lignesDe`).

## Comment ils saluent et se présentent

**Ils ne se présentent pas** — un inconnu qui t'arrête dans la rue ne dit pas son nom (`missions.on_le_rencontre` :
pas de `ou`). Ils te hèlent (« Psst! Le jeune! »), puis vont droit au problème.
