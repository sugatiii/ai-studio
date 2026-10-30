from openrouter_client import OpenRouterClient
from model_loader import ModelLoader


class AgentRunner:

    def __init__(self):

        self.client = OpenRouterClient()
        self.models = ModelLoader()

    def run(
        self,
        agent_name: str,
        prompt: str
    ):

        model = self.models.get_model(
            agent_name
        )

        return self.client.chat(
            model=model,
            prompt=prompt
        )