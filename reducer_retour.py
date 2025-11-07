#!/usr/bin/env python3
import sys

def reducer():
    # Variables pour stocker les totaux globaux
    total_sold_quantity = 0
    total_returned_quantity = 0

    # L'entrée est garantie d'être triée par clé ('RATE_STATS' dans notre cas)
    for line in sys.stdin:
        # L'entrée est : RATE_STATS \t TYPE (SOLD/RETURNED) \t QUANTITE
        try:
            # On ignore la clé 'RATE_STATS' car nous savons qu'il n'y en a qu'une
            _, stats_type, quantity_str = line.strip().split('\t', 2)
            quantity = int(quantity_str)
        except ValueError:
            continue

        # Agrégation des compteurs
        if stats_type == 'SOLD':
            total_sold_quantity += quantity
        elif stats_type == 'RETURNED':
            total_returned_quantity += quantity
            
    # --- Calcul final du Taux de Retour ---
    if total_sold_quantity > 0:
        # Calcul du taux de retour en pourcentage
        return_rate = (total_returned_quantity / total_sold_quantity) * 100
        
        # Le livrable 5.3 doit être clair (produit une sortie claire)
        print(f"Quantité Totale Vendue:\t{total_sold_quantity}")
        print(f"Quantité Totale Retournée:\t{total_returned_quantity}")
        print(f"Taux de Retour Global (%):\t{return_rate:.4f}%")
    else:
        print("Taux de Retour Global (%):\t0.00%")
        print("Erreur: Aucune quantité vendue trouvée.")

reducer()

