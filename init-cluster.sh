#!/bin/bash
set -e

echo "--------------------------------------"
echo "1️⃣ Construction de l'image Docker..."
echo "--------------------------------------"
docker build -t yazid/hadoop-cluster:latest .

echo "--------------------------------------"
echo "2️⃣ Démarrage des containers..."
echo "--------------------------------------"
docker-compose up -d

echo "⏳ Attente que SSH soit prêt sur tous les noeuds..."
sleep 5

echo "--------------------------------------"
echo "3️⃣ Formatage du NameNode si nécessaire..."
echo "--------------------------------------"
docker exec -it master bash -c "
if [ ! -f ~/hdfs/namenode/current/VERSION ]; then
    echo 'Formatage du NameNode...'
    /usr/local/hadoop/bin/hdfs namenode -format -force
fi
"

echo "--------------------------------------"
echo "4️⃣ Démarrage HDFS, YARN et Spark..."
echo "--------------------------------------"
docker exec -it master bash -c "/root/start-hadoop.sh"

echo "--------------------------------------"
echo "✅ Cluster initialisé. UI accessibles :"
echo "- HDFS : http://localhost:9870/"
echo "- YARN : http://localhost:8088/"
echo "- Spark Master : http://localhost:8080/"
