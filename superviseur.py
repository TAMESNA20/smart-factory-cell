import sqlite3
import time
from vision_robotique import CameraIndustrielle
from bras_robotique import BrasRobotique

class SuperviseurCellule:
    def __init__(self):
        """
        Constructeur de la classe SuperviseurCellule.
        Initialise les composants matériels (Caméra, Robot) et configure
        la base de données SQLite pour la traçabilité de la production.
        """
        # 1. Instanciation des modules de vision et de robotique existants
        self.camera = CameraIndustrielle("Sony_X1")
        self.robot = BrasRobotique("Staubli_TX2")
        
        # 2. Configuration et nommage de la table SQL de supervision
        self.nom_table_sql = "historique_production"
        
        # 3. Connexion à la base de données locale 
        self.connexion = sqlite3.connect("gestion_usine.db")
        self.curseur = self.connexion.cursor()
        
        # 4. Création automatique de la table avec son schéma relationnel
        self.curseur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.nom_table_sql} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horodatage TEXT DEFAULT CURRENT_TIMESTAMP,
                type_piece TEXT,
                statut TEXT,
                coord_x REAL,
                coord_y REAL
            )
        """)
        self.connexion.commit()  # Validation de la structure dans le fichier .db
        print(" [SUPERVISEUR] Cellule connectée et opérationnelle.")
        print(f"🗄️ [SQLITE] Base de données locale 'gestion_usine.db' initialisée.")
    
    def log_production_sql(self, type_piece, statut_production, x_pos, y_pos):
        """
        Génère et exécute une requête SQL INSERT afin d'enregistrer 
        les données d'un cycle ou d'une panne dans la base de données.
        """
        # Utilisation de requêtes paramétrées (?) pour éviter les injections SQL
        requete_sql = f"""
            INSERT INTO {self.nom_table_sql} (type_piece, statut, coord_x, coord_y) 
            VALUES (?, ?, ?, ?);
        """
        
        try:
            # Exécution de la requête avec conversion explicite des coordonnées en réels
            self.curseur.execute(requete_sql, (type_piece, statut_production, float(x_pos), float(y_pos)))
            self.connexion.commit()  # Validation définitive de la transaction dans le fichier
            print(f" [SQLITE SUCCESS] Données archivées : {type_piece} | Statut: {statut_production}")
        except Exception as err_sql:
            print(f"[SQLITE ERROR] Impossible de journaliser dans la base : {err_sql}")

    def ordonnancer_cycle(self, simuler_defaut=False):
        """
        Orchestre le cycle complet de production :
        1. Capture et binarisation d'image (NumPy)
        2. Contrôle qualité et calcul du centroïde
        3. Prise de décision et pilotage des axes du bras robotique
        4. Enregistrement des résultats dans la base SQL
        """
        print("\n --- DÉMARRAGE D'UN NOUVEAU CYCLE DE PRODUCTION ---")
        
        try:
            # --- ÉTAPE 1 : TRAITEMENT D'IMAGE (NumPy) ---
            if simuler_defaut:
                matrice = self.camera.capturer_piece()
                matrice[3, 3] = 0  # Injection artificielle d'une anomalie (trou noir au centre)
            else:
                matrice = self.camera.capturer_piece()
                
            # Binarisation de la matrice (conversion en pixels de 0 et 1)
            matrice_binaire = self.camera.binariser_image(matrice)
            
            # --- ÉTAPE 2 : ANALYSE ET ALGORITHME GÉOMÉTRIQUE ---
            est_conforme = self.camera.analyser_conformite(matrice_binaire)
            centre = self.camera.calculer_centre(matrice_binaire)
            
            # Extraction des coordonnées ou repli sur des valeurs de sécurité
            if centre is not None:
                y_pixel, x_pixel = centre
            else:
                y_pixel, x_pixel = 0.0, 0.0
            
            # --- ÉTAPE 3 : PILOTAGE ET MACHINE À ÉTATS DU ROBOT ---
            if est_conforme:
                print(f" [SUPERVISEUR] -> Ordre envoyé au bras : Saisir au centre ({x_pixel}, {y_pixel})")
                
                # Vérification et initialisation de la machine à états du robot
                if self.robot.etat == "INIT":
                    self.robot.executer_cycle()
                
                # Conversion d'échelle : Transformation de l'espace pixel vers l'espace articulaire (degrés)
                self.robot.deplacer_axes(x_pixel * 15.0, y_pixel * 15.0)
                statut_final = "CONFORME"
            else:
                print(" [SUPERVISEUR] -> Rejet automatique de la pièce. Activation du protocole de sécurité.")
                self.robot.arret_urgence()
                statut_final = "REJET_DEFAUT"
                
            # --- ÉTAPE 4 : ARCHIVAGE ET SUPREVISION SQL ---
            self.log_production_sql("Axe_Moteur_A", statut_final, x_pixel, y_pixel)

        except Exception as e:
            # --- GESTION DES PANNES SYSTÈME ---
            print(f"\n [CRITICAL ERROR] Interception d'une anomalie système : {e}")
            self.robot.arret_urgence()  # Arrêt immédiat des actionneurs par sécurité
            
            # Journalisation de la panne avec les détails de l'erreur pour la maintenance
            self.log_production_sql("PANNE_SYSTEME", f"ERREUR: {str(e)[:20]}", 0.0, 0.0)

    def __del__(self):
        """
        Méthode destructrice. Assure la fermeture propre et sécurisée
        de la connexion SQLite à la fermeture du programme.
        """
        try:
            self.connexion.close()
            print("\n[SQLITE] Connexion à la base de données fermée proprement.")
        except:
            pass


# =====================================================================
# SCRIPT D'ÉVALUATION ET DE CONFIGURATION DU SYSTÈME EN LOCAL
# =====================================================================
if __name__ == "__main__":
    # Création du superviseur central de l'usine
    cellule = SuperviseurCellule()
    
    # --- TEST 1 : Simulation d'un flux nominal (Pièce conforme) ---
    print("\n--- [TEST 1 : PIÈCE CONFORME] ---")
    cellule.ordonnancer_cycle(simuler_defaut=False)
    
    # Temporisation de simulation entre deux pièces sur le tapis roulant
    time.sleep(2)
    
    # --- TEST 2 : Simulation d'un cas de tri (Pièce défectueuse) ---
    print("\n--- [TEST 2 : PIÈCE DÉFECTUEUSE] ---")
    cellule.ordonnancer_cycle(simuler_defaut=True)