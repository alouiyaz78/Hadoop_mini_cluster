# Hadoop Mini Cluster Project





Ce projet fournit un \*\*cluster Hadoop et Spark prêt à l'emploi\*\* dans un conteneur Docker, idéal pour les tests et travaux pratiques en Big Data.



\## Caractéristiques

\- Ubuntu 22.04 avec OpenJDK 8

\- Hadoop 3.3.6 et Spark 3.5.0 installés

\- SSH sans mot de passe pour Hadoop

\- Répertoires HDFS et logs prêts à l'emploi

\- Script de démarrage pour lancer le cluster facilement



\## Utilisation

1\. Pull de l'image Docker :  

&nbsp;  ```bash

&nbsp;  docker pull alouiyaz/hadoop-groupe3:tagname



2.Lancer le conteneur :



docker run -it alouiyaz/hadoop-groupe3:tagname





3.Démarrer le cluster Hadoop :



./start-hadoop.sh

