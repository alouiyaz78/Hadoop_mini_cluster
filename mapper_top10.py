#!/usr/bin/env python3
import sys
import csv
from operator import itemgetter

# --- CONFIGURATION ---
TOP_K = 10
# ---------------------

# Dictionnaire pour stocker le CA total par produit pour CE mapper
local_product_totals = {}

# Utilisation de csv.reader pour gérer les champs CSV, en ignorant l'en-tête
reader = csv.reader(sys.stdin, delimiter=',')

# Sauter l'en-tête (la première ligne)
try:
    next(reader) 
except StopIteration:
    sys.exit(0)

for row in reader:
    try:
        # Indices des colonnes : produit_id (5), prix_unitaire (8), quantité (9), est_retour (16)
        if len(row) < 17:
            continue

        produit_id = row[5].strip()
        prix_unitaire = float(row[8].strip())
        quantite = int(row[9].strip())
        est_retour = row[16].strip()
        
        # Calcul du Chiffre d'Affaires Net (CA)
        quantite_nette = -quantite if est_retour == '1' else quantite
        ca_net = prix_unitaire * quantite_nette
        
        # Agrégation locale (Combiner Pattern)
        # ----------------------------------------------------
        # Stocker/Accumuler le CA pour chaque produit_id traité
        local_product_totals[produit_id] = local_product_totals.get(produit_id, 0.0) + ca_net
        # ----------------------------------------------------

    except (ValueError, IndexError):
        continue

# --- Phase de Tri Local (après avoir traité toutes les lignes du split) ---

# Convertir le dictionnaire en une liste de tuples (CA, produit_id)
# pour faciliter le tri par le CA.
sorted_totals = [
    (total_ca, prod_id) 
    for prod_id, total_ca in local_product_totals.items()
]

# Trier par CA (premier élément du tuple) en ordre décroissant
sorted_totals.sort(key=itemgetter(0), reverse=True)

# Émettre le Top K (10) des résultats locaux
# On émet la clé '1' (une clé factice unique) pour forcer tous les résultats
# à aller au même Reducer pour le tri final.
for ca_total, prod_id in sorted_totals[:TOP_K]:
    # Émettre : Clé (unique pour forcer un seul Reducer) \t Valeur (CA_net_Total, produit_id)
    # Note: On émet le CA total local en premier pour que le Reducer puisse trier
    print(f"1\t{ca_total:.2f}\t{prod_id}")
