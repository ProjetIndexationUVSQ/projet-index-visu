from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

# Initialiser la session Spark avec Elasticsearch
spark = SparkSession.builder \
    .appName("Spark-Elasticsearch-Integration") \
    .config("spark.es.nodes", "localhost") \
    .config("spark.es.port", "9200") \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()

# Charger les données depuis Elasticsearch
df = spark.read.format("es").load("wikipedia_changes")  # ici tu peux remplacer avec le nom que tu as donnée à l'index @R

# Afficher les premières lignes
df.show(5)

#Transformation 1 : Nombre d'éditions par titre d'article
edits_per_title = df.groupBy("type").agg(count("user"))
edits_per_title.show()

# Arrêter Spark après traitement
spark.stop()
