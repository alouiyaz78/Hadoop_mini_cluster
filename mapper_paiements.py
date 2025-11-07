#!/usr/bin/env python3
import sys
import csv

# Utilisation de csv.reader pour gérer les champs CSV
reader = csv.reader(sys.stdin, delimiter=',')

# Sauter l'en-tête (la première ligne)
try:
    next(reader) 
except StopIteration:
    sys.exit(0)

for row in reader:
    try:
        # Indices des colonnes
        if len(row) < 17:
            continue

        # Clé : mode_paiement
        mode_paiement = row[11].strip()
        
        # Valeurs pour le calcul du CA Net
        prix_unitaire = float(row[8].strip())
        quantite = int(row[9].strip())
        est_retour = row[16].strip()
        
        # Calcul du Chiffre d'Affaires Net (CA)
        # S'il y a un retour ('1'), la quantité devient négative pour soustraire la vente.
        quantite_nette = -quantite if est_retour == '1' else quantite
        ca_net = prix_unitaire * quantite_nette
        
        # Émettre la paire (Clé, Valeur) : (mode_paiement, CA_net)
        print(f"{mode_paiement}\t{ca_net:.2f}")

    except (ValueError, IndexError):
        # Ignorer les lignes mal formatées ou incomplètes
        continue
