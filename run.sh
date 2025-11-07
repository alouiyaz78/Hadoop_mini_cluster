#!/bin/bash

# =========================================================
# CONFIGURATION
# =========================================================

MASTER_CONTAINER="hadoop-project-master"
LOCAL_DATA_FILE="ventes_big_data_final.csv"

# Chemins HDFS
HDFS_INPUT_DIR="/user/root/input"
HDFS_OUTPUT_ROOT="/user/root/output"

# Dossiers locaux pour les livrables
LOCAL_OUTPUT_BASE="./livrables_UA2"

SUCCESS_COUNT=0
TOTAL_JOBS=4

# Assurez-vous que les scripts Python ont les droits d'exécution
chmod +x mapper_*.py reducer_*.py

# =========================================================
# FONCTION DE NETTOYAGE/RENOMMAGE DES FICHIERS
# =========================================================

format_and_rename() {
    JOB_NAME=$1
    NEW_NAME=$2
    LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/$JOB_NAME"
    INPUT_FILE="$LOCAL_OUTPUT_DIR/part-00000"
    OUTPUT_FILE="$LOCAL_OUTPUT_DIR/$NEW_NAME"

    if [ -f "$INPUT_FILE" ]; then
        mv -f "$INPUT_FILE" "$OUTPUT_FILE"
        echo "✅ Fichier renommé : $INPUT_FILE -> $OUTPUT_FILE"
    else
        echo "⚠️ Fichier $INPUT_FILE non trouvé pour $JOB_NAME"
    fi
}

# =========================================================
# FONCTION D'EXECUTION DES JOBS
# =========================================================

execute_job() {
    JOB_NAME=$1
    MAPPER=$2
    REDUCER=$3
    REDUCES=$4
    LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/$JOB_NAME"
    HDFS_OUTPUT_DIR="$HDFS_OUTPUT_ROOT/$JOB_NAME"

    echo -e "\n--- EXÉCUTION DU JOB '$JOB_NAME' ---"
    mkdir -p "$LOCAL_OUTPUT_DIR"
    hdfs dfs -rm -r -f "$HDFS_OUTPUT_DIR"

    hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
        -D mapreduce.job.name="$JOB_NAME" \
        -D mapreduce.job.reduces=$REDUCES \
        -files $MAPPER,$REDUCER \
        -mapper "python3 $MAPPER" \
        -reducer "python3 $REDUCER" \
        -input "$HDFS_INPUT_DIR/*" \
        -output "$HDFS_OUTPUT_DIR"

    if hdfs dfs -test -f "$HDFS_OUTPUT_DIR/_SUCCESS"; then
        echo "✅ SUCCÈS : Job '$JOB_NAME' terminé."
        hdfs dfs -get "$HDFS_OUTPUT_DIR/part-00000" "$LOCAL_OUTPUT_DIR/"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ ÉCHEC : Job '$JOB_NAME' n'a pas produit de fichier _SUCCESS."
    fi
}

# =========================================================
# ÉTAPE 1 : PRÉPARATION HDFS
# =========================================================

hdfs dfs -rm -r -f "$HDFS_INPUT_DIR"
hdfs dfs -mkdir -p "$HDFS_INPUT_DIR"
hdfs dfs -put -f "$LOCAL_DATA_FILE" "$HDFS_INPUT_DIR/"

# =========================================================
# ÉTAPE 2 : EXÉCUTION DES JOBS
# =========================================================

# 5.1 CA par Pays/Mois
execute_job "output_ca" "mapper_ca.py" "reducer_ca.py" 1
format_and_rename "output_ca" "ca_pays_mois.txt"

# 5.2 Top 10 Produits
execute_job "output_top10" "mapper_top10.py" "reducer_top10.py" 1
format_and_rename "output_top10" "classement_top10.txt"

# 5.3 Taux de Retour
execute_job "output_retours" "mapper_retour.py" "reducer_retour.py" 1
format_and_rename "output_retours" "taux_global.txt"

# 5.4 Répartition Paiements
execute_job "output_paiements" "mapper_paiements.py" "reducer_paiements.py" 1
format_and_rename "output_paiements" "repartition_ca.txt"

# =========================================================
# ÉTAPE 3 : LANCEMENT DU DASHBOARD
# =========================================================

echo ""
echo "--- 🚀 LANCEMENT DU DASHBOARD STREAMLIT ---"
docker exec -d $MASTER_CONTAINER /bin/bash -c "nohup streamlit run /root/dashboard.py --server.address 0.0.0.0 --server.port 8501 > /root/streamlit.log 2>&1 &"
echo "✅ Dashboard lancé sur http://localhost:8501"

echo "🎯 Fin du script run.sh - $SUCCESS_COUNT/$TOTAL_JOBS jobs réussis."

