#!/usr/bin/env python3
import sys

def reducer():
    current_mode = None
    current_ca_total = 0.0

    # L'entrée du Reducer est garantie d'être triée par clé (mode_paiement)
    for line in sys.stdin:
        # Supprimer les espaces blancs et séparer Clé et Valeur
        try:
            mode_paiement, ca_net_str = line.strip().split('\t', 1)
            ca_net = float(ca_net_str)
        except ValueError:
            # Sauter les lignes mal formatées
            continue

        # Logique d'agrégation MapReduce
        if current_mode == mode_paiement:
            current_ca_total += ca_net
        else:
            # Si le mode de paiement change, imprimer le résultat du mode précédent
            if current_mode is not None:
                # Émettre la paire (mode_paiement, CA_net_Total)
                print(f"{current_mode}\t{current_ca_total:.2f}")
            
            # Commencer l'agrégation pour le nouveau mode de paiement
            current_mode = mode_paiement
            current_ca_total = ca_net
            
    # Afficher le dernier mode de paiement après la boucle
    if current_mode is not None:
        print(f"{current_mode}\t{current_ca_total:.2f}")

reducer()
