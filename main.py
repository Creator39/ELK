from pathlib import Path
from Lab.Certificate_CA import save_certificate_pem, display_certificate_info
from Lab.KeyManager import KeyManager
from Lab.Certificate import load_certificate_pem, create_server_certificate

def lab3_main():
    """
    Fonction principale du Lab 3.
    
    Workflow :
    1. Charger la CA créée dans le Lab 2
    2. Créer une nouvelle clé pour Elasticsearch
    3. Générer le certificat ES signé par la CA
    4. Vérifier la chaîne de confiance
    """
    print("\n" + "🧪 LAB 3 : CERTIFICAT SERVEUR ELASTICSEARCH ".center(60, "="))
    print()
    
    # Chemins
    lab2_dir = Path("./lab2_output")
    lab3_dir = Path("./lab3_output")
    lab2_dir.mkdir(exist_ok=True)
    lab3_dir.mkdir(exist_ok=True)
    
    # ========================================================================
    # ÉTAPE 1 : Charger la CA du Lab 2
    # ========================================================================
    print("=" * 60)
    print("ÉTAPE 1 : Chargement de la CA")
    print("=" * 60)
    
    ca_cert_path = lab2_dir / "ca_cert.pem"
    ca_cert = load_certificate_pem(ca_cert_path)
    
    # Charger aussi la clé privée de la CA (pour signer)
    key_manager = KeyManager(key_dir=lab2_dir / "keys")
    ca_private_key = key_manager.create_rsa_keypair("ca_key", key_size=4096)["private_key"]
    
    print(f"✅ CA prête à signer des certificats\n")
    
    # ========================================================================
    # ÉTAPE 2 : Générer la clé pour Elasticsearch
    # ========================================================================
    print("=" * 60)
    print("ÉTAPE 2 : Génération de la clé Elasticsearch")
    print("=" * 60)
    
    es_key_manager = KeyManager(key_dir=lab3_dir / "keys")
    es_keypair = es_key_manager.create_rsa_keypair("elasticsearch", key_size=2048)
    
    print()
    
    # ========================================================================
    # ÉTAPE 3 : Créer le certificat ES signé par la CA
    # ========================================================================
    print("=" * 60)
    print("ÉTAPE 3 : Création du certificat Elasticsearch")
    print("=" * 60)
    
    es_cert = create_server_certificate(
        server_private_key=es_keypair["private_key"],
        ca_cert=ca_cert,
        ca_private_key=ca_private_key,
        common_name="elasticsearch",
        dns_names=["localhost", "es.local"],
        ip_addresses=["127.0.0.1"],
        validity_days=365
    )
    
    # Afficher les informations
    display_certificate_info(es_cert)
    
    # Sauvegarder le certificat
    es_cert_path = lab3_dir / "elasticsearch_cert.pem"
    save_certificate_pem(es_cert, es_cert_path)
    
    # ========================================================================
    # ÉTAPE 4 : Instructions de vérification
    # ========================================================================
    print("=" * 60)
    print("VÉRIFICATION DE LA CHAÎNE DE CONFIANCE")
    print("=" * 60)
    
    print("\n📝 COMMANDES IMPORTANTES :\n")
    
    print("1. Afficher le certificat Elasticsearch :")
    print(f"   openssl x509 -in {es_cert_path} -text -noout\n")
    
    print("2. Vérifier que Subject ≠ Issuer (pas auto-signé) :")
    print(f"   openssl x509 -in {es_cert_path} -noout -subject -issuer\n")
    
    print("3. Vérifier la chaîne de confiance avec la CA :")
    print(f"   openssl verify -CAfile {ca_cert_path} {es_cert_path}\n")
    print("   → Devrait afficher : elasticsearch_cert.pem: OK\n")
    
    print("4. Voir les Subject Alternative Names (SAN) :")
    print(f"   openssl x509 -in {es_cert_path} -noout -ext subjectAltName\n")
    
    print("=" * 60)
    print("\n💡 POINTS CLÉS À OBSERVER :")
    print("   - Subject: CN=elasticsearch")
    print("   - Issuer: CN=ELK-Root-CA (différent du Subject !)")
    print("   - X509v3 Basic Constraints: CA:FALSE")
    print("   - X509v3 Extended Key Usage: TLS Web Server Authentication")
    print("   - X509v3 Subject Alternative Name: DNS:elasticsearch, DNS:localhost, IP:127.0.0.1")
    print("\n" + "=" * 60 + "\n")


# ============================================================================
# QUESTIONS DE RÉFLEXION
# ============================================================================

"""
APRÈS AVOIR EXÉCUTÉ CE SCRIPT, RÉPONDEZ À CES QUESTIONS :

1. Subject vs Issuer :
   - Pour Elasticsearch, sont-ils identiques ?
   - Que signifie cette différence ?

2. Signature :
   - Quelle clé a signé le certificat ES ? (clé CA ou clé ES ?)
   - Pourquoi cette distinction est importante ?

3. BasicConstraints :
   - Pourquoi ca=False pour Elasticsearch ?
   - Que se passerait-il si ca=True ?

4. ExtendedKeyUsage :
   - Que signifie SERVER_AUTH ?
   - Elasticsearch pourrait-il aussi être CLIENT_AUTH ?

5. Subject Alternative Names (SAN) :
   - Pourquoi avons-nous besoin de SAN ?
   - Que se passe-t-il si on se connecte avec un nom pas dans les SAN ?

6. Chaîne de confiance :
   - Que fait la commande `openssl verify` ?
   - Si vous supprimez ca_cert.pem, que se passe-t-il ?

7. Cas d'usage DevOps :
   - Dans Docker, Elasticsearch sera accessible par quel nom ?
   - Devriez-vous ajouter ce nom aux SAN ?
"""


if __name__ == "__main__":
    lab3_main()