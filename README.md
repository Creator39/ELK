# 🔐 Stack ELK Sécurisée avec TLS/SSL

Stack complète **Elasticsearch + Logstash + Kibana** avec génération automatique de certificats TLS/SSL via Docker.

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation rapide](#-installation-rapide)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Sécurité](#-sécurité)
- [Dépannage](#-dépannage)

---

## 🎯 Vue d'ensemble

Ce projet fournit une **stack ELK complète** avec :
- ✅ **Génération automatique de certificats** TLS/SSL (CA + certificats serveur/client)
- ✅ **Chiffrement bout-en-bout** de toutes les communications
- ✅ **Docker Compose** pour un déploiement simple
- ✅ **Health checks** automatiques
- ✅ **Volumes persistants** pour les données
- ✅ **Configuration via variables d'environnement**

### Composants

| Service | Version | Description | Port |
|---------|---------|-------------|------|
| **Elasticsearch** | 8.15.0 | Moteur de recherche et stockage | 9200, 9300 |
| **Logstash** | 8.15.0 | Pipeline de traitement | 5000, 5044, 9600 |
| **Kibana** | 8.15.0 | Interface web de visualisation | 5601 |
| **Setup (init)** | Python 3.13 | Génération des certificats | - |

---

🔧 Configuration

ELK/
├── Docker_Compose_ELK.yml      # Orchestration Docker (encore en version template)
├── Dockerfile                   # Image init pour certificats
├── main.py                      # Script génération certificats
├── generate_certs.py            # Logique de génération
├── certs_config.yaml            # Config des certificats
├── .env                         # Variables d'environnement (à créer) 
├── .env.example                 # Template du .env (pas encore implemeter)
├── utils/
│   ├── CertificateManager.py    # Gestion certificats
│   ├── KeyManager.py            # Gestion clés privées
│   └── load_config.py           # Chargement config
├── logstash/ (pas encore implemeter)
│   ├── config/
│   │   ├── logstash.yml         # Config principale
│   │   └── pipelines.yml        # Config pipelines
│   └── pipeline/
│       └── logstash.conf        # Pipeline de données
└── README.md                    # Ce fichier

---

📝 Personnalisation des certificats

    Modifiez certs_config.yaml