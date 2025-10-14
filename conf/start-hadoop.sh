#!/bin/bash
# -------------------------------
# Script de démarrage Hadoop + Spark
# -------------------------------

# Démarrer SSH (nécessaire pour Hadoop)
service ssh start

HADOOP_HOME=/usr/local/hadoop
SPARK_HOME=/usr/local/spark

# Créer répertoires HDFS si non existants
mkdir -p ~/hdfs/namenode ~/hdfs/datanode ~/hdfs/secondary

# Démarrage HDFS
echo "Démarrage HDFS..."
set +e # Désactiver l'arrêt en cas d'erreur/avertissement
$HADOOP_HOME/sbin/start-dfs.sh
set -e # Réactiver l'arrêt

# Démarrage YARN
echo "Démarrage YARN..."
set +e # Désactiver l'arrêt en cas d'erreur/avertissement
$HADOOP_HOME/sbin/start-yarn.sh
set -e # Réactiver l'arrêt

# Démarrage Spark
echo "Démarrage Spark..."
$SPARK_HOME/sbin/start-master.sh
