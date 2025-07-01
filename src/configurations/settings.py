import os
import yaml
from pathlib import Path

class Settings:
    def __init__(self, model_file="models.yml"):
        self.model_config_path = Path(model_file)
        self.model_config = self._load_model_config()

    def _load_model_config(self):
        if not self.model_config_path.exists():
            raise FileNotFoundError(f"Model config file not found at {self.model_config_path}")

        with open(self.model_config_path, "r") as f:
            return yaml.safe_load(f)

    def get_models(self, provider: str) -> list:
        return self.model_config.get(provider.lower(), [])

    def get_all_providers(self) -> list:
        return list(self.model_config.keys())

# Singleton-style instantiation
settings = Settings()
