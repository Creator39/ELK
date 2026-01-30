from  elasticsearch import Elasticsearch
import os
import time
import sys


def ilmPolicy(es: Elasticsearch):
    pass  # Implementation of ILM policy setup goes here

def waitForElasticsearch(es: Elasticsearch, timeout: int = 60):
    start_time = time.time()
    while True:
        try:
            print(f"Attempting to connect to Elasticsearch...")
            info = es.info()
            print(f"✅ Elasticsearch is reachable! Cluster: {info['cluster_name']}, Version: {info['version']['number']}")
            return True
        except Exception as e:
            print(f"⏳ Error connecting: {type(e).__name__}: {str(e)[:200]}. Retrying...")
        
        if time.time() - start_time > timeout:
            print("❌ Timeout waiting for Elasticsearch.")
            return False
        
        time.sleep(2)

def createClient() -> Elasticsearch:
    try:
        es = Elasticsearch(
            hosts=["https://elasticsearch:9200"],
            basic_auth=('elastic', os.getenv('ELASTIC_PASSWORD', "changeme527")),
            verify_certs=True,
            ca_certs='/app/certs/ca_cert.pem')
        return es
    except Exception as e:
        raise e
def main():
    try:
        es = createClient()
        if es is not None and waitForElasticsearch(es):
            ilmPolicy(es)
        else:
            print("Failed to create Elasticsearch client.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()