#!/usr/bin/env python3
import sys
from operator import itemgetter

# --- CONFIGURATION ---
TOP_K = 10
# ---------------------

# Dictionnaire pour stocker le CA total FINAL pour chaque produit
global_product_totals = {}

for line in sys.stdin:
    # L'entrée du Reducer est : 1 \t CA_total_local \t produit_id
    try:
        # Le split doit gérer les champs de la ligne émise par le Mapper
        dummy_key, ca_net_str, produit_id = line.strip().split('\t', 2)
        ca_net = float(ca_net_str)
    except ValueError:
        continue

    # 1. Agrégation globale (très importante !)
    # Il est possible que le même produit_id apparaisse dans le Top 10 de plusieurs Mappers.
    # On doit donc AGGREGER son CA global.
    global_product_totals[produit_id] = global_product_totals.get(produit_id, 0.0) + ca_net


# --- Phase de Tri Global (après avoir reçu tous les résultats) ---

# Convertir le dictionnaire en une liste de tuples (CA, produit_id)
# pour le tri final.
final_sorted_totals = [
    (total_ca, prod_id) 
    for prod_id, total_ca in global_product_totals.items()
]

# 2. Trier par CA (premier élément du tuple) en ordre décroissant
final_sorted_totals.sort(key=itemgetter(0), reverse=True)

# 3. Afficher le Top K (10) des résultats GLOBAUX (le livrable final)
for ca_total, prod_id in final_sorted_totals[:TOP_K]:
    # Sortie finale : produit_id \t CA_net_Total
    print(f"{prod_id}\t{ca_total:.2f}")
