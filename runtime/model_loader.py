from pathlib import Path
import yaml


class ModelLoader:

    def __init__(self, config_file="../configs/models.yaml"):
        self.config_file = config_file
        self.models = self._load()

    def _load(self):
        config = Path(self.config_file)

        if not config.exists():
            raise FileNotFoundError(
                f"Config not found: {config}"
            )

        with open(config, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get_model(self, agent_name: str):

        if agent_name not in self.models:
            raise ValueError(
                f"Agent '{agent_name}' not configured."
            )

        return self.models[agent_name]["model"]