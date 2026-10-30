from openrouter_client import OpenRouterClient


client = OpenRouterClient()

result = client.chat(
    model="nvidia/nemotron-3.5-lightning:free",
    prompt="Say hello"
)

print(result)