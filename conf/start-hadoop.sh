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
$HADOOP_HOME/sbin/start-dfs.sh

# Démarrage YARN
echo "Démarrage YARN..."
$HADOOP_HOME/sbin/start-yarn.sh

# Démarrage Spark
echo "Démarrage Spark..."
$SPARK_HOME/sbin/start-master.sh
