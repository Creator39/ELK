from elasticsearch import Elasticsearch
import os
import ssl

print('SSL version:', ssl.OPENSSL_VERSION)
print('Connecting to Elasticsearch...')

es = Elasticsearch(
    hosts=["https://elasticsearch:9200"],
    basic_auth=('elastic', os.getenv('ELASTIC_PASSWORD')),
    verify_certs=True,
    ca_certs='/app/certs/ca_cert.pem'
)

try:
    # Test ping
    ping_result = es.ping()
    print(f'Ping result: {ping_result}')
    
    # Test info
    info = es.info()
    print(f'Connected! Cluster: {info["cluster_name"]}')
    print(f'Version: {info["version"]["number"]}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
