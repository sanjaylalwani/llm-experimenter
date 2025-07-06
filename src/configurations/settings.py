import os
import yaml
from pathlib import Path

class Settings:
    def __init__(self):
        # Get the directory where the script is located
        base_dir = Path(__file__).parent

        # Build the full path to your YAML file
        file_path = base_dir / 'models.yml'
        with open(file_path, "r") as f:
            self.model_config =  yaml.safe_load(f)
        self.defaults = self.model_config.get("defaults", {
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 1.0,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        })

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
