"""
LAB 3 : Création d'un certificat serveur pour Elasticsearch
============================================================

Objectifs d'apprentissage :
1. Créer un certificat SIGNÉ PAR LA CA (pas auto-signé)
2. Ajouter des Subject Alternative Names (SAN)
3. Utiliser ExtendedKeyUsage pour l'authentification serveur
4. Vérifier la chaîne de confiance

Durée estimée : 25 minutes

Prérequis : Avoir complété le Lab 2 (CA créée)
"""

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List
import ipaddress

# Réutiliser les fonctions du Lab 2
from Certificate_CA import create_name, save_certificate_pem, display_certificate_info
from KeyManager import KeyManager


# ============================================================================
# NOUVEAU : Créer un certificat SERVEUR (signé par CA)
# ============================================================================

def create_server_certificate(
    server_private_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_private_key: rsa.RSAPrivateKey,
    common_name: str,
    dns_names: List[str] = None,
    ip_addresses: List[str] = None,
    validity_days: int = 365
) -> x509.Certificate:
    """
    Crée un certificat serveur signé par la CA.
    
    DIFFÉRENCE MAJEURE avec Lab 2 :
    - Subject ≠ Issuer (pas auto-signé)
    - Signé avec la CLÉ PRIVÉE DE LA CA
    - Extensions différentes (SERVER_AUTH, pas ca=True)
    
    Args:
        server_private_key: Clé privée du serveur (ES)
        ca_cert: Certificat de la CA (pour obtenir l'Issuer)
        ca_private_key: Clé privée de la CA (pour SIGNER)
        common_name: CN du serveur (ex: "elasticsearch")
        dns_names: Noms DNS alternatifs (ex: ["localhost", "es.local"])
        ip_addresses: Adresses IP (ex: ["127.0.0.1"])
        validity_days: Durée de validité (1 an par défaut)
        
    Returns:
        Un certificat X.509 signé par la CA
    """
    # Valeurs par défaut
    if dns_names is None:
        dns_names = []
    if ip_addresses is None:
        ip_addresses = []
    
    print(f"\n📝 Création du certificat serveur : {common_name}")
    
    # 1. Subject : Le serveur (elasticsearch)
    subject = create_name(common_name)
    
    # 2. Issuer : La CA (on l'extrait du certificat CA)
    issuer = ca_cert.subject
    
    print(f"   Subject : {common_name}")
    print(f"   Issuer  : {issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
    print(f"   → Ce certificat sera signé par la CA")
    
    # 3. Préparer les Subject Alternative Names (SAN)
    san_list = []
    
    # Ajouter le CN comme DNS name
    san_list.append(x509.DNSName(common_name))
    
    # Ajouter les DNS names additionnels
    for dns in dns_names:
        san_list.append(x509.DNSName(dns))
        print(f"   + DNS: {dns}")
    
    # Ajouter les IP addresses
    for ip in ip_addresses:
        san_list.append(x509.IPAddress(ipaddress.ip_address(ip)))
        print(f"   + IP: {ip}")
    
    # 4. Construire le certificat
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)  # ← Différent du subject !
        .public_key(server_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
        
        # EXTENSION 1 : BasicConstraints
        # ca=False : Ce n'est PAS une CA, juste un serveur
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        
        # EXTENSION 2 : KeyUsage
        # Différent de la CA : pas de key_cert_sign !
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,    # Peut signer des données
                key_encipherment=True,     # Peut chiffrer des clés (TLS)
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,       # NE PEUT PAS signer des certificats
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        
        # EXTENSION 3 : ExtendedKeyUsage
        # Indique que ce certificat est pour l'authentification SERVEUR
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,  # Authentification serveur
            ]),
            critical=False,
        )
        
        # EXTENSION 4 : SubjectAlternativeName
        # Liste tous les noms/IPs par lesquels le serveur peut être contacté
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        
        # 5. SIGNER avec la CLÉ PRIVÉE DE LA CA (pas la clé du serveur !)
        .sign(ca_private_key, hashes.SHA256())
    )
    
    print(f"✅ Certificat serveur créé (valide {validity_days} jours)")
    print(f"   Signé par : {issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}\n")
    
    return cert


# ============================================================================
# FONCTION : Charger un certificat depuis un fichier
# ============================================================================

def load_certificate_pem(filepath: Path) -> x509.Certificate:
    """
    Charge un certificat depuis un fichier PEM.
    
    Utile pour charger le certificat CA créé dans le Lab 2.
    """
    print(f"📂 Chargement du certificat depuis {filepath}...")
    
    with open(filepath, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read())
    
    print(f"✅ Certificat chargé")
    return cert


# ============================================================================
# EXERCICE PRATIQUE
# ============================================================================

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