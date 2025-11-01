#!/bin/bash

# =========================================================
# CONFIGURATION
# =========================================================

MASTER_CONTAINER="hadoop-project-master" # NOM DU NOUVEAU CONTENEUR MAÎTRE
LOCAL_DATA_FILE="ventes_big_data_final.csv"
HDFS_INPUT_DIR="/user/root/input_data"
HDFS_OUTPUT_ROOT="/user/root/output"
LOCAL_OUTPUT_BASE="./livrables_UA2"

SUCCESS_COUNT=0
TOTAL_JOBS=4

# Assurez-vous que les scripts Python ont les droits d'exécution
echo "Attribution des droits d'exécution aux scripts Python..."
chmod +x mapper_top10.py
chmod +x reducer_top10.py
chmod +x mapper_retour.py
chmod +x reducer_retour.py
chmod +x mapper_paiements.py
chmod +x reducer_paiements.py
chmod +x mapper_ca.py
chmod +x reducer_ca.py

# Fonction de vérification après job
check_job_status() {
    JOB_NAME=$1
    HDFS_OUTPUT_DIR=$2
    LOCAL_FILE=$3
    LOCAL_OUTPUT_DIR=$4
    
    if hdfs dfs -test -f "$HDFS_OUTPUT_DIR/_SUCCESS"; then
        echo "✅ SUCCÈS : Job '$JOB_NAME' terminé."
        hdfs dfs -get "$HDFS_OUTPUT_DIR/part-00000" "$LOCAL_OUTPUT_DIR/$LOCAL_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ ÉCHEC : Job '$JOB_NAME' n'a pas produit de fichier _SUCCESS."
    fi
}

# =========================================================
# ÉTAPE 1 : PRÉPARATION (HDFS)
# =========================================================

echo "--- ÉTAPE 1 : PRÉPARATION HDFS ---"
hdfs dfs -rm -r -f "$HDFS_INPUT_DIR" > /dev/null 2>&1
hdfs dfs -mkdir -p "$HDFS_INPUT_DIR"
echo "Chargement du fichier $LOCAL_DATA_FILE vers $HDFS_INPUT_DIR/..."
hdfs dfs -put -f "$LOCAL_DATA_FILE" "$HDFS_INPUT_DIR/"


# =========================================================
# ÉTAPE 2 : CA PAR PAYS ET MOIS (2.1 / 5.1)
# =========================================================

JOB_NAME="ca_pays_mois"
HDFS_OUTPUT_DIR="$HDFS_OUTPUT_ROOT/output_ca"
LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/output_ca"
LOCAL_FILE="ca_pays_mois.txt"

echo -e "\n--- ÉTAPE 2 : EXÉCUTION DU JOB '$JOB_NAME' (CA par Pays/Mois - Livrable 5.1) ---"
mkdir -p "$LOCAL_OUTPUT_DIR"
echo "Nettoyage de $HDFS_OUTPUT_DIR sur HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_DIR"

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -D mapreduce.job.name="CA Pays/Mois" \
    -files mapper_ca.py,reducer_ca.py \
    -mapper "python3 mapper_ca.py" \
    -reducer "python3 reducer_ca.py" \
    -input "$HDFS_INPUT_DIR/*" \
    -output "$HDFS_OUTPUT_DIR"

check_job_status $JOB_NAME $HDFS_OUTPUT_DIR $LOCAL_FILE $LOCAL_OUTPUT_DIR
echo "Aperçu du CA (Livrable 5.1 - Format Aligné) :"
cat "$LOCAL_OUTPUT_DIR/$LOCAL_FILE" 2>/dev/null | head -n 10 | column -t


# =========================================================
# ÉTAPE 3 : TOP 10 PRODUITS (2.2 / 5.2)
# =========================================================

JOB_NAME="top10_produits"
HDFS_OUTPUT_DIR="$HDFS_OUTPUT_ROOT/output_top10"
LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/output_top10"
LOCAL_FILE="classement_top10.txt"

echo -e "\n--- ÉTAPE 3 : EXÉCUTION DU JOB '$JOB_NAME' (Top 10 - Livrable 5.2) ---"
mkdir -p "$LOCAL_OUTPUT_DIR"
echo "Nettoyage de $HDFS_OUTPUT_DIR sur HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_DIR"

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -D mapreduce.job.name="Top 10 Produits" \
    -D mapreduce.job.reduces=1 \
    -files mapper_top10.py,reducer_top10.py \
    -mapper "python3 mapper_top10.py" \
    -reducer "python3 reducer_top10.py" \
    -input "$HDFS_INPUT_DIR/*" \
    -output "$HDFS_OUTPUT_DIR"

check_job_status $JOB_NAME $HDFS_OUTPUT_DIR $LOCAL_FILE $LOCAL_OUTPUT_DIR
echo "Aperçu du Top 10 (Livrable 5.2) :"
cat "$LOCAL_OUTPUT_DIR/$LOCAL_FILE" 2>/dev/null


# =========================================================
# ÉTAPE 4 : TAUX DE RETOUR (2.3 / 5.3)
# =========================================================

JOB_NAME="taux_de_retour"
HDFS_OUTPUT_DIR="$HDFS_OUTPUT_ROOT/output_retours"
LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/output_retours"
LOCAL_FILE="taux_global.txt"

echo -e "\n--- ÉTAPE 4 : EXÉCUTION DU JOB '$JOB_NAME' (Taux de Retour - Livrable 5.3) ---"
mkdir -p "$LOCAL_OUTPUT_DIR"
echo "Nettoyage de $HDFS_OUTPUT_DIR sur HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_DIR"

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -D mapreduce.job.name="Taux de Retour" \
    -D mapreduce.job.reduces=1 \
    -files mapper_retour.py,reducer_retour.py \
    -mapper "python3 mapper_retour.py" \
    -reducer "python3 reducer_retour.py" \
    -input "$HDFS_INPUT_DIR/*" \
    -output "$HDFS_OUTPUT_DIR"

check_job_status $JOB_NAME $HDFS_OUTPUT_DIR $LOCAL_FILE $LOCAL_OUTPUT_DIR
echo "Aperçu du Taux de Retour (Livrable 5.3) :"
cat "$LOCAL_OUTPUT_DIR/$LOCAL_FILE" 2>/dev/null


# =========================================================
# ÉTAPE 5 : RÉPARTITION DES PAIEMENTS (2.4 / 5.4)
# =========================================================

JOB_NAME="repartition_paiements"
HDFS_OUTPUT_DIR="$HDFS_OUTPUT_ROOT/output_paiements"
LOCAL_OUTPUT_DIR="$LOCAL_OUTPUT_BASE/output_paiements"
LOCAL_FILE="repartition_ca.txt"

echo -e "\n--- ÉTAPE 5 : EXÉCUTION DU JOB '$JOB_NAME' (Répartition Paiements - Livrable 5.4) ---"
mkdir -p "$LOCAL_OUTPUT_DIR"
echo "Nettoyage de $HDFS_OUTPUT_DIR sur HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_DIR"

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -D mapreduce.job.name="Répartition Paiements" \
    -D mapreduce.job.reduces=1 \
    -files mapper_paiements.py,reducer_paiements.py \
    -mapper "python3 mapper_paiements.py" \
    -reducer "python3 reducer_paiements.py" \
    -input "$HDFS_INPUT_DIR/*" \
    -output "$HDFS_OUTPUT_DIR"

check_job_status $JOB_NAME $HDFS_OUTPUT_DIR $LOCAL_FILE $LOCAL_OUTPUT_DIR
echo "Aperçu de la Répartition des Paiements (Livrable 5.4) :"
cat "$LOCAL_OUTPUT_DIR/$LOCAL_FILE" 2>/dev/null

# =========================================================
# ÉTAPE FINALE : LANCEMENT DU DASHBOARD
# =========================================================

echo -e "\n--- ÉTAPE FINALE : LANCEMENT DU DASHBOARD ---"

if [ "$SUCCESS_COUNT" -eq "$TOTAL_JOBS" ]; then
    echo "🎉 TOUS LES $TOTAL_JOBS JOBS MAPREDUCE ONT RÉUSSI. Les données sont prêtes."
    echo ""
    echo "▶️ Pour lancer le Tableau de Bord Streamlit, exécutez cette commande SÉPARÉMENT :"
    echo "   docker exec -it $MASTER_CONTAINER /bin/bash -c \"streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501\""
    echo ""
    echo "   Accédez ensuite à : http://localhost:8501"
else
    echo "⚠️ $SUCCESS_COUNT JOBS ONT RÉUSSI SUR $TOTAL_JOBS. Veuillez corriger les erreurs avant de lancer le dashboard."
fi

echo -e "\n--- FIN DU SCRIPT run.sh ---"
