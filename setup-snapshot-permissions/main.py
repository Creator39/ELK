from pathlib import Path
import os

def main():
    try:
        path = Path("/app/snapshots_output")
        path.mkdir(parents=True, exist_ok=True)
        
         # Changer le propriétaire et les permissions pour qu'Elasticsearch puisse y accéder
        os.chown(path, 1000, 1000)  # UID et GID par défaut d'Elasticsearch dans le conteneur officiel
        path.chmod(0o755)
    except Exception as e:
        print(f"❌ Erreur inattendue lors du changement des permissions : {e}")
        return 1
      
if __name__ == "__main__":
    import sys
    sys.exit(main())