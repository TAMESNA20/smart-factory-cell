# 🏭 Smart Factory Cell — Integrated Robotics, Computer Vision & SQL Logging

Ce projet réalise l'intégration système complète d'une cellule de production automatisée. Il interconnecte un algorithme de vision par ordinateur (NumPy), un contrôleur cinématique de bras robotique industriel à machine à états (FSM), et une base de données relationnelle locale (SQLite) pour la supervision des données et la traçabilité des pannes.

## 🛠️ Architecture Système & Flux de Données

1. **Segment Vision (NumPy) :** Capture de matrices de pixels, binarisation par seuillage adaptatif, calcul du centroïde géométrique $(X, Y)$ et exécution du contrôle qualité automatique.
2. **Segment Robotique (Stäubli TX2) :** Automatisation du cycle via une Machine à États Finis (`INIT`, `ATTENTE`, `SAISIE`, `TRI`), conversion d'échelle de l'espace pixel vers l'espace articulaire (degrés) et calcul cinématique direct.
3. **Segment Data & Robustesse (SQLite) :** Journalisation en temps réel de la production (`INSERT INTO`) et interception des exceptions système par blocs `try/except` pour l'archivage automatique des codes de pannes.

## 💻 Langages & Technologies
- Python 3 (Modules natifs: `sqlite3`, `time`, `math`)
- NumPy (Calcul matriciel et traitement d'images)
