# WT Offline Plotter

Capture en temps réel les positions (API localhost:8111) et visualise les trajets après la partie.

## Installation

- Créer un environnement Python et installer les dépendances :
  - `pip install -r requirements.txt`

## Utilisation

### 1) Capture en continu (temps réel)

```
python app.py capture
```

Options utiles :

- `--poll 1.0` cadence d’échantillonnage en secondes
- `--retry 2.0` attente entre les vérifications si aucune partie n’est en cours
- `--data <chemin>` dossier de stockage (par défaut: offline_plotter/data)
- `--once` capture un seul match et s’arrête

### 2) Lancer l’interface

```
python app.py serve
```

Puis ouvrir http://127.0.0.1:5000

### 3) Capture + interface en même temps

```
python app.py watch

Puis ouvrir http://127.0.0.1:5000/live pour suivre la partie en direct.
```

## Organisation des données

- `data/matches.db` : base SQLite (matches + positions)
- `data/maps/<map_id>.png` : image de la map (stockée une seule fois)

## Extraction des minimaps et generation des hash

Ces outils permettent de reconstituer un fichier de hash compatible avec
`/map.img` en partant des assets du jeu.

1) Inspecter les images deja capturees (pour deduire format et taille):

```
python tools/inspect_db_map_images.py
```

2) Extraire les vromf depuis l installation du jeu:

```
python tools/extract_wt_vromf.py --game-dir C:\WarThunder
```

3) Generer un nouveau fichier de hash:

```
python tools/build_map_hashes.py --input data/wt_vromf_unpacked --output map_hashes.generated.py
```

Le fichier `map_hashes.generated.py` peut ensuite remplacer `map_hashes.py`.

## Notes

- L’outil ne lit pas les replays : il enregistre les positions live via l’API locale War Thunder (localhost:8111), puis permet de revoir les chemins plus tard.
- Le regroupement par map tient compte du mode.
- Quand le joueur passe en air pendant une partie sol/mer, la map air est enregistree en metadonnees secondaires.
