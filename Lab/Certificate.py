from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List
import ipaddress
from .Certificate_CA import create_name


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
