#!/bin/bash
set -e

echo "--------------------------------------"
echo "1️⃣ Construction de l'image Docker..."
echo "--------------------------------------"
# Vous utilisez 'yazid/hadoop-cluster:latest' pour le build
docker build -t yazid/hadoop-cluster:latest .

echo "--------------------------------------"
echo "2️⃣ Démarrage des containers..."
echo "--------------------------------------"
# Cette commande recrée les conteneurs avec la nouvelle image et la commande corrigée
docker-compose up -d

echo "⏳ Attente que SSH soit prêt sur tous les noeuds..."
sleep 5

echo "--------------------------------------"
echo "3️⃣ Formatage du NameNode si nécessaire..."
echo "--------------------------------------"
# Note: On utilise 'bash -c' ici car c'est une simple vérification de fichier
docker exec master bash -c "
if [ ! -f ~/hdfs/namenode/current/VERSION ]; then
    echo 'Formatage du NameNode...'
    # Pour que hdfs soit trouvé, on utilise le chemin absolu ou on s'assure du PATH.
    /usr/local/hadoop/bin/hdfs namenode -format -force
fi
"

echo "--------------------------------------"
echo "4️⃣ Démarrage HDFS, YARN et Spark PROPRE..."
echo "--------------------------------------"
# 🚨 CORRECTION CRUCIALE : On utilise 'bash -c "source ..."' pour charger le PATH et les ENV
docker exec master bash -c "source ~/.bashrc && /root/start-hadoop.sh"

echo "--------------------------------------"
echo "✅ Cluster initialisé. UI accessibles :"
echo "- HDFS : http://localhost:9870/"
echo "- YARN : http://localhost:8088/"
echo "- Spark Master : http://localhost:8080/"