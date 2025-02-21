import requests
import json
import time
import signal
import sys
from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def save_data_to_kafka(data):
    """
    Envoie des données dans le topic Kafka
    
    Parameters
    ----------
    
    changes : dictionary
        Les données à envoyer
    """
    for val in data:
        producer.send("wikipedia_changes", value=val)
        print(f"Envoyé : {val}")

def fetch_recent_changes(limit=10):
    """
    Récupère les modifications récentes sur Wikipédia.
    
    Parameters
    ----------
    
    limit : integer
        Le nombre de changements à renvoyer
        
    Returns
    ------
    
    Un dictionnaire contenant les changements ou vide si il y a eu une erreur.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "recentchanges",
        "rcprop": "title|timestamp|user|comment|flags",
        "rclimit": limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["query"]["recentchanges"]
    else:
        print(f"Erreur : {response.status_code}")
        return []

def save_data_to_file(data, filename="recent_changes.jsonl"):
    """
    Sauvegarde les modifications dans un fichier JSONL.
    
    Parameters
    ----------
    
    data : dictionary
        Les données à sauvegarder
        
    filename : string
        Le nom du fichier dans lequel on sauvegarde les données.
    
    """
    with open(filename, "a") as file:
        for val in data:
            file.write(json.dumps(val) + "\n")

def collect_data(interval=30, limit=5):
    """
    Collecte les données toutes les X secondes.
    
    
    Parameters
    ----------
    
    interval : integer
        Le nombre de secondes entre chaque requête.
        
    limit : integer
        Le nombre de changements à renvoyer
    """
    print("Démarrage de la collecte des données...")
    i = 1
    while True:
        data = fetch_recent_changes(limit=limit)
        save_data_to_file(data)
        save_data_to_kafka(data)
        print(f"Récupération {i} effectuée.")
        i += 1
        time.sleep(interval)
    
def exit_program(signum, frame):
    print("Collecte terminée.")
    producer.flush()
    producer.close()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_program)
    # Lancement de la collecte
    collect_data(interval=30, limit=5)
    
