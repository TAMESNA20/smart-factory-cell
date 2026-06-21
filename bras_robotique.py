import math
import random
import time

# =====================================================================
# GESTION DES EXCEPTIONS PERSONNALISÉES
# =====================================================================
class PieceDefectueuseError(Exception):
    """Exception levée lorsqu'un composant non autorisé arrive sur le tapis."""
    pass

# =====================================================================
# CLASSE PRINCIPALE : CONTRÔLE DU BRAS ROBOTIQUE
# =====================================================================
class BrasRobotique:
    def __init__(self, nom_robot):
        """Initialisation de la structure et des attributs du robot."""
        self.nom = nom_robot
        self.axe1 = 0.0               # Angle de la Base (limites : -180 à 180)
        self.axe2 = 0.0               # Angle de l'Épaule (limites : -90 à 90)
        self.pince_ouverte = True     # État de l'actionneur de saisie
        self.bac_pieces = []          # Base de données des pièces triées
        self.etat = "INIT"            # État initial de la machine à états

    def statut(self):
        """Affiche l'état articulaire et la position cartésienne calculée."""
        etat_pince = "OUVERTE" if self.pince_ouverte else "FERMÉE"
        pos_x, pos_y = self.calculer_position_pince()
        print(f"[{self.nom}] Angles : Base = {self.axe1}° | Épaule = {self.axe2}° | Pince : {etat_pince}")
        print(f"      📍 Position Pince : X = {pos_x:.2f}m , Y = {pos_y:.2f}m")

    def deplacer_axes(self, angle1, angle2):
        """Met à jour les angles du robot après vérification des butées mécaniques."""
        if (-180.0 <= angle1 <= 180.0) and (-90.0 <= angle2 <= 90.0):
            self.axe1 = angle1
            self.axe2 = angle2
            print(f"[{self.nom}] Mouvement réussi vers Base={angle1}° , Épaule={angle2}°")
            self.statut()
        else:
            print(f"[ALERTE] Mouvement impossible : Angles ({angle1}°, {angle2}°) hors limites physiques !")

    def piloter_pince(self, ouvrir):
        """Gère l'ouverture et la fermeture de la pince pneumatique."""
        if self.pince_ouverte == ouvrir:
            etat = "ouverte" if ouvrir else "fermée"
            print(f"[{self.nom}] L'actionneur est déjà dans l'état demandé : pince déjà {etat}.")
        else:
            self.pince_ouverte = ouvrir
            action = "Ouverture" if ouvrir else "Fermeture"
            print(f"[{self.nom}] {action} de la pince réussie.")

    def arret_urgence(self):
        """Procédure de repli de sécurité en cas d'anomalie sur la ligne."""
        self.axe1 = 0.0
        self.axe2 = 0.0
        self.pince_ouverte = False
        print(f"\n [ALERTE ROUGE] ARRÊT D'URGENCE ACTIVÉ SUR {self.nom} ! Moteurs coupés, pince verrouillée.")

    def detecter_piece(self, piece):
        """Analyse le composant présenté par les capteurs du tapis roulant."""
        nom_piece = piece["type"]
        poids_piece = piece["poids"]
        print(f"[CAPTEUR] Pièce détectée : {nom_piece} (Poids : {poids_piece}g)")
        
        # Sécurité A : Filtrage des pièces tolérées sur la ligne
        if nom_piece == "Châssis":
            raise PieceDefectueuseError("Type de composant 'Châssis' non autorisé sur cette ligne !")
        
    def saisir_piece(self, piece):
        """Exécute la séquence physique de capture si la charge est tolérée."""
        # Sécurité B : Vérification de la surcharge de l'actionneur
        if piece["poids"] >= 450:
            raise ValueError(f"Surcharge critique détectée : {piece['poids']}g (Limite max : 450g)")
        
        self.piloter_pince(True)
        self.piloter_pince(False)
        self.bac_pieces.append(piece)

    def afficher_rapport(self):
        """Génère le bilan complet de la session de production."""
        poids_total = 0
        for p in self.bac_pieces:
            poids_total += p["poids"]
        print(f"\n--- RAPPORT DE PRODUCTION ---")
        print(f"Nombre total de pièces traitées : {len(self.bac_pieces)}")
        print(f"Poids total supporté : {poids_total}g")
        print(f"-----------------------------")

    def executer_cycle(self, piece_sur_tapis=None):
        """Boucle centrale de la Machine à États Finis (FSM)."""
        try:
            if self.etat == "INIT":
                print(f"\n[INIT] Démarrage et recalibrage du bras robotique...")
                self.axe1 = 0.0
                self.axe2 = 0.0
                self.pince_ouverte = True
                self.etat = "ATTENTE"
                
            elif self.etat == "ATTENTE":
                if piece_sur_tapis is None:
                    print(f"[ATTENTE] En veille, aucun composant sur le tapis...")
                else:
                    self.detecter_piece(piece_sur_tapis)
                    self.etat = "SAISIE"
                    
            elif self.etat == "SAISIE":
                print(f"\n[SAISIE] Phase d'approche et de capture...")
                self.deplacer_axes(45.0, 45.0)
                self.saisir_piece(piece_sur_tapis)
                self.etat = "TRI"
                
            elif self.etat == "TRI":
                print(f"\n[TRI] Acheminement vers le bac de stockage...")
                self.deplacer_axes(-90.0, 0.0)
                self.piloter_pince(True)
                print(f"La pièce '{piece_sur_tapis['type']}' est triée avec succès.")
                self.etat = "ATTENTE"
                
        except (PieceDefectueuseError, ValueError) as erreur_panne:
            print(f"\n[PANNE SYSTÈME] Exception interceptée : {erreur_panne}")
            self.arret_urgence()
            self.etat = "ERREUR"

    def calculer_position_pince(self):
        """Modélisation géométrique : Cinématique Directe (Moteur -> Espace Cartésien)."""
        L_1 = 1.0
        L_2 = 0.8
        angl1_rad = math.radians(self.axe1)
        angl2_rad = math.radians(self.axe2)
        x = (L_1 * math.cos(angl1_rad)) + (L_2 * math.cos(angl1_rad + angl2_rad))
        y = (L_1 * math.sin(angl1_rad)) + (L_2 * math.sin(angl1_rad + angl2_rad))
        return x, y

# =====================================================================
# SIMULATION DE L'ENVIRONNEMENT EXTIERIEUR
# =====================================================================
def generer_piece_aleatoire():
    """Générateur de données simulant le défilement du tapis roulant."""
    list_pieces = ["Pignon", "Circuit", "Axe", "Châssis"]
    piece_nom = random.choice(list_pieces)
    poids_piece = random.randint(50, 500)  
    return {"type": piece_nom, "poids": poids_piece}


# =====================================================================
# SCÉNARIOS DE TEST AUTOMATIQUES
# =====================================================================
if __name__ == "__main__":
    print("====================================================")
    print("LOGICIEL DE NAVIGATION ET DE TRI - STAUBLI TX2")
    print("====================================================")

    # --- SCÉNARIO 1 : GESTION DES ERREURS & SECURITÉ ---
    print("\n[SCÉNARIO 1] ÉVALUATION DES SYSTÈMES DE SÉCURITÉ")
    robot_test = BrasRobotique("Staubli_TX2")
    robot_test.executer_cycle()  # INIT

    piece_interdite = {"type": "Châssis", "poids": 200}