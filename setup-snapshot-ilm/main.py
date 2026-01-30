from  elasticsearch import Elasticsearch
import os
import time
import sys


def ilmHotPhase(body: dict, maxSize: str = "1GB", maxAge: str = "3d"):
    body["phases"]["hot"] = {
        "min_age": "0ms",
        "actions": {
            "rollover": {
                "max_size": maxSize,
                "max_age": maxAge
            },
            "set_priority": {
                "priority": 100
            }
        }
    }

def ilmFrozen(body: dict, freezeAfter: str = "2d"):
    body["phases"]["frozen"] = {
        "min_age": freezeAfter,
        "actions": {
            "searchable_snapshot": {},
            "set_priority": {
                "priority": 20
            }
        }
    }

def deletePhase(body: dict, deleteAfter: str = "3d"):
    body["phases"]["delete"] = {
        "min_age": deleteAfter,
        "actions": {
            "delete": {}
        }
    }

def ilmPolicy(es: Elasticsearch, 
              hotPhase: bool = True,
              deletePhase: bool = True, 
              freezePhase: bool = True,
              policyName: str = "snapshot-ilm-policy"):
    
    policy_body = {
        "policy": {
            "phases": {

            }
        }
    }
    if hotPhase:
        ilmHotPhase(policy_body["policy"])
    if freezePhase:
        ilmFrozen(policy_body["policy"])
    if deletePhase:
        deletePhase(policy_body["policy"])
    es.ilm.put_lifecycle(policy=policyName, body=policy_body)
    print(f"✅ ILM Policy '{policyName}' created with phases: {list(policy_body['policy']['phases'].keys())}")

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

def ilmTemplate(es: Elasticsearch, policyName: str = "snapshot-ilm-policy", 
                templateName: str = "snapshot-ilm-template", 
                aliasName: str = "snapshot-ilm-alias",
                pattern: str = "snapshot-ilm-*"):
    template_body = {
        "index_patterns": [pattern],
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "index.lifecycle.name": policyName,
            "index.lifecycle.rollover_alias": aliasName
        },
        "aliases": {
            aliasName: {}
        }
    }
    es.indices.put_index_template(name=templateName, body=template_body)
    print(f"✅ ILM Template '{templateName}' created for indices matching '{pattern}' with alias '{aliasName}'")

def main():
    try:
        policyName = "snapshot-ilm-policy"
        templateName = "snapshot-ilm-template"
        aliasName = "snapshot-ilm-alias"
        pattern = "snapshot-ilm-*"
        
        es = createClient()
        if es is not None and waitForElasticsearch(es):
            ilmPolicy(es, policyName=policyName)
            ilmTemplate(es, policyName=policyName, templateName=templateName, aliasName=aliasName, pattern=pattern)
            ilmBootstrapIndex = "snapshot-ilm-000001"
            if not es.indices.exists(index=ilmBootstrapIndex):
                es.indices.create(index=ilmBootstrapIndex, aliases={aliasName: {"is_write_index": True}})
                print(f"✅ Bootstrap index '{ilmBootstrapIndex}' created with alias '{aliasName}'")
        else:
            print("Failed to create Elasticsearch client.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()