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
        # Indices des colonnes : quantité (9), est_retour (16)
        if len(row) < 17:
            continue

        quantite = int(row[9].strip())
        est_retour = row[16].strip()
        
        # 1. Émettre la quantité totale vendue (dénominateur)
        # Clé: 'SOLD' (pour les ventes)
        # Valeur: la quantité de cette transaction
        # Une clé unique 'RATE_STATS' est utilisée pour forcer un seul Reducer.
        print(f"RATE_STATS\tSOLD\t{quantite}")
        
        # 2. Émettre la quantité retournée (numérateur)
        if est_retour == '1':
            # Clé: 'RETURNED' (pour les retours)
            # Valeur: la quantité de cette transaction
            print(f"RATE_STATS\tRETURNED\t{quantite}")

    except (ValueError, IndexError):
        # Ignorer les lignes mal formatées
        continue

