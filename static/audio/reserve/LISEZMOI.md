# La réserve

Des sons **gardés**, que le catalogue ne réclame pas (encore).

Ce dossier existe pour une seule raison : une génération ratée n'est pas
toujours un déchet. Quand ElevenLabs rend autre chose que ce qu'on demandait,
et que cette autre chose est bonne, on la met ici plutôt que de la jeter — on
la repaiera sinon le jour où on la voudra vraiment.

⚠️ **Rien ici n'est chargé par le jeu.** `app/audio.py` ne décrit que les
fichiers du dossier au-dessus ; `Son.chargerEchantillons()` télécharge le
catalogue et rien d'autre. Un son en réserve ne pèse donc pas sur le premier
chargement, et il ne peut pas jouer.

⚠️ **Et rien ici n'est un orphelin.** `audio.orphelins()` parcourt le dossier
avec `iterdir()`, qui ne descend pas dans les sous-dossiers — c'est ce qui
rend cette réserve possible. Si quelqu'un passe un jour à `rglob()`, le juge
`test_aucun_fichier_orphelin` réclamera la suppression de tout ce qui est ici :
`test_la_reserve_ne_compte_pas_comme_un_orphelin` est là pour que ce
changement-là se voie.

## Comment en sortir un son

Lui écrire une entrée dans `CATALOGUE` (`app/audio.py`), puis le renommer au
nom que `audio.nom_fichier()` attend (`<slug>-1.mp3`) et le remonter d'un
dossier. ⚠️ Il n'aura **pas** subi la finition (`scripts/audio_elevenlabs.py`,
`finir()`) : mono, pic à −1 dBFS, queue rognée. Le plus simple est de le
refaire, ou de lui passer `finir()` à la main.

## Ce qui est là

| Fichier | D'où il vient |
|---|---|
| `chien-qui-jappe.mp3` | Sorti le 13 septembre 2026 d'une demande de **moto qui passe**. Le prompt disait « exhaust **bark** » — le modèle a pris le mot au pied de la lettre et a rendu un chien. Martin l'a entendu et a demandé de le garder. Un chien qui jappe derrière une clôture servira aux **terrains de banlieue** (P4, Les Érables) |
