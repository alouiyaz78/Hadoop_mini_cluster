#!/bin/bash
# Utilisation de 'set -e' pour garantir l'arrêt du script si une erreur survient
set -e

echo "--------------------------------------"
echo "1️⃣ Construction de l'image Docker..."
echo "--------------------------------------"
# Utilisation du nom d'image défini pour le build
docker build -t yazid/hadoop-cluster:latest .

echo "--------------------------------------"
echo "2️⃣ Démarrage des containers..."
echo "--------------------------------------"
# Recrée les conteneurs (master, slave1, slave2)
docker-compose up -d

echo "⏳ Attente que SSH soit prêt sur tous les noeuds..."
sleep 5

echo "--------------------------------------"
echo "3️⃣ Formatage du NameNode si nécessaire..."
echo "--------------------------------------"
# 🚨 Correction de l'étape 3 : Tout sur une ligne unique pour éviter les erreurs de parsing
# Vérifie si le fichier VERSION existe (HDFS déjà formaté)
# Si non, formate le NameNode.
docker exec master bash -c 'if [ ! -f /root/hdfs/namenode/current/VERSION ]; then echo "Formatage du NameNode..."; /usr/local/hadoop/bin/hdfs namenode -format -force; fi'

echo "--------------------------------------"
echo "4️⃣ Démarrage HDFS, YARN et Spark PROPRE..."
echo "--------------------------------------"
# 🚨 Correction de l'étape 4 : Utilise 'source ~/.bashrc' pour charger le PATH et les variables HADOOP
docker exec master bash -c "source ~/.bashrc && /root/start-hadoop.sh"

echo "--------------------------------------"
echo "✅ Cluster initialisé. UI accessibles :"
echo "- HDFS : http://localhost:9870/"
echo "- YARN : http://localhost:8088/"
echo "- Spark Master : http://localhost:8080/"