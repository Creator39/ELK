# 🔐 PKI pour Stack ELK (Elasticsearch, Logstash, Kibana)

Infrastructure de clés publiques (PKI) automatisée pour sécuriser les communications TLS/SSL dans une stack ELK.

## 📋 Vue d'ensemble

Ce projet génère automatiquement :
- **1 Certificate Authority (CA)** auto-signée
- **1 certificat serveur** pour Elasticsearch (avec SAN)
- **2 certificats client** pour Logstash et Kibana

## 🚀 Installation

```bash
# Installer les dépendances
pip install cryptography pyyaml

# Ou avec uv (recommandé)
uv sync
```

## 📦 Utilisation

### Génération des certificats

```bash
python main.py
```

### Configuration

Modifier `certs_config.yaml` selon vos besoins.

## ⚠️ SÉCURITÉ - ERREURS CORRIGÉES

### ✅ Corrections appliquées :
1. **Chargement de la CA** : La clé privée existante est maintenant chargée au lieu d'être régénérée
2. **Organisation dynamique** : Utilise maintenant la config YAML au lieu d'être hardcodée
3. **Validation automatique** : Vérification de la chaîne de confiance après génération

### 🔴 À FAIRE AVANT PRODUCTION :

> ⚠️ **CRITIQUE** : Les clés privées sont actuellement **NON CHIFFRÉES** !

Consultez [SECURITY_RECOMMENDATIONS.md](SECURITY_RECOMMENDATIONS.md) pour :
- Chiffrer les clés privées avec un mot de passe
- Configuration ELK complète
- Bonnes pratiques de sécurité
- Checklist de déploiement

## 🔍 Vérification

```bash
# Vérifier la chaîne de confiance
openssl verify -CAfile certs_output/ca/ca_cert.pem certs_output/elasticsearch/elasticsearch_cert.pem
```

---

**✅ Le code a été audité et les erreurs critiques ont été corrigées.**  
**⚠️ Lisez [SECURITY_RECOMMENDATIONS.md](SECURITY_RECOMMENDATIONS.md) avant tout déploiement !**