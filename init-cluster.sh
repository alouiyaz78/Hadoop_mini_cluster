#!/bin/bash
# Utilisation de 'set -e' pour garantir l'arrêt du script si une erreur survient
set -e

# Mise à jour du nom du conteneur Maître
MASTER_CONTAINER="hadoop-project-master"

echo "--------------------------------------"
echo "1️⃣ Construction de l'image Docker..."
echo "--------------------------------------"
# Utilisation du nom d'image défini pour le build
docker build -t yazid/hadoop-cluster:latest .

echo "--------------------------------------"
echo "2️⃣ Démarrage des containers..."
echo "--------------------------------------"
# Recrée les conteneurs (hadoop-project-master, slave1, slave2)
docker-compose up -d

echo "⏳ Attente que SSH soit prêt sur tous les noeuds..."
sleep 5

echo "--------------------------------------"
echo "3️⃣ Formatage du NameNode si nécessaire..."
echo "--------------------------------------"
# Exécute la commande sur le nouveau conteneur
docker exec ${MASTER_CONTAINER} bash -c 'if [ ! -f /root/hdfs/namenode/current/VERSION ]; then echo "Formatage du NameNode..."; /usr/local/hadoop/bin/hdfs namenode -format -force; fi'

echo "--------------------------------------"
echo "4️⃣ Démarrage HDFS, YARN et Spark PROPRE..."
echo "--------------------------------------"
# Utilise le nouveau conteneur pour démarrer les services
docker exec ${MASTER_CONTAINER} bash -c "source ~/.bashrc && /root/start-hadoop.sh"

echo "--------------------------------------"
echo "✅ Cluster initialisé. UI accessibles :"
echo "- HDFS : http://localhost:9870/"
echo "- YARN : http://localhost:8088/"
echo "- Spark Master : http://localhost:8080/"
echo "- Streamlit Dashboard (DÉMARRAGE MANUEL) : http://localhost:8501/"
echo ""
echo "▶️ Pour lancer le tableau de bord, utilisez la commande (dans le même répertoire) :"
echo "docker exec -it ${MASTER_CONTAINER} /bin/bash -c \"streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501\""