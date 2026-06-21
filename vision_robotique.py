import numpy as np
import math

class CameraIndustrielle:
    def __init__(self, nom_photo):
        """Initialisation de la caméra industrielle et des dimensions de la matrice."""
        self.nom = nom_photo
        self.lignes = 8
        self.colonnes = 8

    def capturer_tapis_vide(self):
        """Génère une matrice noire (remplie de zéros) simulant un tapis roulant vide."""
        return np.zeros((self.lignes, self.colonnes), dtype=int)   

    def capturer_piece(self):
        """Simule la capture d'une pièce blanche (pixels à 255) au centre du tapis."""
        image = self.capturer_tapis_vide()
        image[2:5, 2:5] = 255
        return image

    def binariser_image(self, image, seuil=100):
        """Filtre l'image à l'aide d'un seuil pour obtenir une matrice binaire (0 ou 1)."""
        masque = image > seuil
        image_nettoyee = masque.astype(int)
        return image_nettoyee

    def calculer_centre(self, image_binaire):
        """Calcule le centre de gravité géométrique (centroïde) de la pièce détectée."""
        indices_lignes, indices_colonnes = np.where(image_binaire == 1)
        
        # Si le tableau est vide (aucun pixel actif détecté)
        if indices_lignes.size == 0:
            return None
        
        # Calcul de la moyenne de chaque dimension indépendamment
        centre_y = np.mean(indices_lignes)
        centre_x = np.mean(indices_colonnes)
        
        return (centre_y, centre_x)

    def analyser_conformite(self, image_binaire):
        """Vérifie si la pièce possède le nombre nominal de pixels (Contrôle Qualité)."""
        if np.sum(image_binaire) != 9:
            print(" Avertissement : Pièce non conforme (défaut détecté).")
            return False
        else:
            print("✅$ La pièce est parfaite (conforme).")
            return True


# =====================================================================
# SCRIPT DE MISE EN OEUVRE ET SIMULATION
# =====================================================================
if __name__ == "__main__":
    print("====================================================")
    print(" SYSTEME DE VISION ARTIFICIELLE - INITIALISATION")
    print("====================================================")

    CAMERA = CameraIndustrielle("Sony_Industrial_X1") 
    
    # 1. Capture et binarisation d'une pièce normale
    matrice = CAMERA.capturer_piece()
    print(f"\nMatrice brute capturée :\n{matrice}")
    
    matrice_nettoyee = CAMERA.binariser_image(matrice)
    print(f"\nMatrice binarisée (Nettoyée) :\n{matrice_nettoyee}")
    
    centre = CAMERA.calculer_centre(matrice_nettoyee)
    print(f"\n Centre de gravité calculé : Y = {centre[0]}, X = {centre[1]}")

    # --- SIMULATION DU CONTRÔLE QUALITÉ ---
    print("\n=========================================")
    print("1 SÉQUENCE DE CONTRÔLE QUALITÉ AUTOMATIQUE")
    print("=========================================")

    # Test avec la pièce normale (qui possède bien 9 pixels blancs)
    print("\n--- Analyse de la Pièce 1 (Nominale) ---")
    conforme = CAMERA.analyser_conformite(matrice_nettoyee)

    # Création d'une deuxième pièce avec injection d'un défaut (un trou noir au centre)
    matrice_defectueuse = CAMERA.capturer_piece()
    matrice_defectueuse[3, 3] = 0  # Injection du pixel défectueux
    binaire_defectueuse = CAMERA.binariser_image(matrice_defectueuse)

    print("\n--- Analyse de la Pièce 2 (Anomalie injectée) ---")
    conforme_2 = CAMERA.analyser_conformite(binaire_defectueuse)