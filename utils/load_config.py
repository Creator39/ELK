"""
Config Loader - Charge la configuration depuis YAML
"""

import yaml
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path: Path):
        # TODO: Stocker le chemin
        # TODO: Charger le fichier YAML
        pass
    
    def _load_yaml(self) -> dict:
        """
        Charge le fichier YAML.
        
        Indice : 
        - Utilisez yaml.safe_load()
        - Gérez FileNotFoundError si le fichier n'existe pas
        """
        # TODO: Votre code ici
        pass
    
    def get_ca_config(self) -> dict:
        """Retourne la config de la CA"""
        # TODO: Accéder à self.config['ca']
        pass
    
    def get_services_config(self) -> dict:
        """Retourne la config des services"""
        # TODO: Accéder à self.config['services']
        pass