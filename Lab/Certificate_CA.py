from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass
from KeyManager import KeyManager
from cryptography.hazmat.primitives import serialization


"""
Un certificat X.509 contient :

1. SUBJECT (Sujet) : Qui possède ce certificat
   - CN (Common Name)    : elasticsearch
   - O (Organization)    : ELK-DevOps-Formation
   - C (Country)         : MG

2. ISSUER (Émetteur) : Qui a signé ce certificat
   - Pour une CA auto-signée : Subject = Issuer

3. VALIDITÉ :
   - not_valid_before : Date de début
   - not_valid_after  : Date d'expiration

4. CLÉ PUBLIQUE : La clé publique du propriétaire

5. SERIAL NUMBER : Numéro unique du certificat

6. EXTENSIONS : Règles et contraintes
   - BasicConstraints : Est-ce une CA ?
   - KeyUsage : À quoi sert cette clé ?
   - SubjectAlternativeName : Noms DNS alternatifs
"""

def create_name(common_name: str, organization: str = "ELK-DevOps", country: str = "MG") -> x509.Name:
    """
    Crée un objet Name pour le Subject ou l'Issuer.
    
    Args:
        common_name: Le CN (nom principal)
        organization: Nom de l'organisation
        country: Code pays (2 lettres)
        
    Returns:
        Un objet x509.Name
    
    Point important : NameOID permet d'identifier les champs standardisés
    """
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

def create_ca_certificate(
    private_key: rsa.RSAPrivateKey,
    common_name: str = "ELK-CA",
    validity_days: int = 3650  # 10 ans
) -> x509.Certificate:
    """
    Crée un certificat auto-signé pour la Certificate Authority.
    
    Auto-signé signifie : Subject = Issuer (la CA se signe elle-même)
    
    Args:
        private_key: Clé privée de la CA
        common_name: Nom de la CA
        validity_days: Durée de validité en jours
        
    Returns:
        Un certificat X.509
    """
    # 1. Créer le Subject et l'Issuer (identiques pour auto-signé)
    subject = issuer = create_name(common_name)
    
    print(f"📝 Création du certificat CA : {common_name}")
    
    # 2. Construire le certificat avec CertificateBuilder
    cert = (
        x509.CertificateBuilder()
        
        # Qui possède ce certificat
        .subject_name(subject)
        
        # Qui a signé ce certificat (soi-même pour une CA)
        .issuer_name(issuer)
        
        # La clé publique du propriétaire
        .public_key(private_key.public_key())
        
        # Numéro de série unique (généré aléatoirement)
        .serial_number(x509.random_serial_number())
        
        # Période de validité
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
        
        # EXTENSION 1 : BasicConstraints
        # ca=True signifie "ce certificat peut signer d'autres certificats"
        # path_length=0 signifie "ne peut pas créer de CA intermédiaires"
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,  # Cette extension est critique (doit être comprise)
        )
        
        # EXTENSION 2 : KeyUsage
        # Définit comment cette clé peut être utilisée
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,   # Peut signer
                key_cert_sign=True,       # Peut signer des certificats ← Important pour CA
                crl_sign=True,            # Peut signer des listes de révocation
                key_encipherment=False,   # Ne chiffre pas de clés
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        
        # 3. Signer le certificat avec la clé privée
        # hashes.SHA256() est l'algorithme de signature
        .sign(private_key, hashes.SHA256())
    )
    
    print(f"✅ Certificat CA créé (valide {validity_days} jours)")
    
    return cert

def save_certificate_pem(cert: x509.Certificate, filepath: Path) -> None:
    """
    Sauvegarde un certificat au format PEM.
    
    Format PEM pour certificat :
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
    """
    print(f"💾 Sauvegarde du certificat dans {filepath}...")
    
    # Convertir en bytes PEM
    pem_bytes = cert.public_bytes(encoding=serialization.Encoding.PEM)
    
    # Créer le dossier si nécessaire
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Écrire le fichier
    filepath.write_bytes(pem_bytes)
    
    # Les certificats peuvent avoir des permissions 644 (publics)
    filepath.chmod(0o644)
    
    print(f"✅ Certificat sauvegardé")

def display_certificate_info(cert: x509.Certificate) -> None:
    """
    Affiche les informations principales du certificat.
    """
    print("\n" + "="*60)
    print("INFORMATIONS DU CERTIFICAT")
    print("="*60)
    
    # Subject
    print(f"\n📋 Subject (Propriétaire) :")
    for attr in cert.subject:
        print(f"   {attr.oid._name} = {attr.value}")
    
    # Issuer
    print(f"\n🔏 Issuer (Émetteur) :")
    for attr in cert.issuer:
        print(f"   {attr.oid._name} = {attr.value}")
    
    # Validité
    print(f"\n📅 Validité :")
    print(f"   Début     : {cert.not_valid_before_utc}")
    print(f"   Fin       : {cert.not_valid_after_utc}")
    
    # Serial Number
    print(f"\n🔢 Serial Number : {cert.serial_number}")
    
    # Extensions
    print(f"\n🔧 Extensions :")
    for ext in cert.extensions:
        print(f"   - {ext.oid._name} (critical={ext.critical})")
    
    print("\n" + "="*60 + "\n")


# ============================================================================
# EXERCICE PRATIQUE : Créer votre CA
# ============================================================================

def main():
    """
    Fonction principale du Lab 2.
    
    IMPORTANT : Décommentez et adaptez l'import de KeyManager en haut du fichier
    """
    print("\n" + "🧪 LAB 2 : CRÉATION DE LA CA ".center(60, "="))
    print()
    
    # Pour ce lab, on va créer les clés directement
    # Dans votre code final, vous utiliserez votre KeyManager du Lab 1
    
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    print("🔑 Génération de la clé CA (4096 bits)...")
    ca_private_key = KeyManager(Path("./lab2_output/keys")).create_rsa_keypair(
        key_name="ca_key",
        key_size=4096
    )["private_key"]
    print("✅ Clé CA générée\n")
    # Créer le certificat CA
    ca_cert = create_ca_certificate(
        private_key=ca_private_key,
        common_name="ELK-Root-CA",
        validity_days=3650  # 10 ans
    )
    
    # Afficher les informations
    display_certificate_info(ca_cert)
    
    # Sauvegarder le certificat
    output_dir = Path("./lab2_output")
    cert_path = output_dir / "ca_cert.pem"
    save_certificate_pem(ca_cert, cert_path)
    
if __name__ == "__main__":
    main()