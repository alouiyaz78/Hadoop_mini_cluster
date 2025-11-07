#!/usr/bin/env python3
import sys
import csv
from datetime import datetime

# Indices des colonnes
IDX_TS = 1
IDX_PAYS = 3
IDX_PRIX = 8
IDX_QUANTITE = 9
IDX_EST_RETOUR = 16 
DELIMITER = ','

reader = csv.reader(sys.stdin, delimiter=DELIMITER)

try:
    next(reader) # Sauter l'en-tête
except StopIteration:
    sys.exit(0)

for cols in reader:
    if len(cols) < 17:  
        continue

    try:
        pays = cols[IDX_PAYS].strip()
        ts_str = cols[IDX_TS].strip()
        prix_unitaire = float(cols[IDX_PRIX].strip())
        quantite = int(cols[IDX_QUANTITE].strip())
        retour_val = cols[IDX_EST_RETOUR].strip()
        
        if '.' in ts_str:
            date_format = "%Y-%m-%d %H:%M:%S.%f"
        else:
            date_format = "%Y-%m-%d %H:%M:%S"
            
        date = datetime.strptime(ts_str, date_format)
        annee_mois = f"{date.year}-{date.month:02d}"
        
        montant = prix_unitaire * quantite
        
        if retour_val == '1': 
            montant = -montant

        # Clé robuste : PAYS_ANNEE-MOIS (le Reducer splittera par '_')
        print(f"{pays}_{annee_mois}\t{montant:.2f}")
        
    except ValueError as e:
        sys.stderr.write(f"ERROR: Conversion failed ({e}) on line: {cols}\n")
