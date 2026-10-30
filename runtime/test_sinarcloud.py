from sinarcloud_client import SinarCloudClient


client = SinarCloudClient()

result = client.chat(
    model="deepseek/deepseek-v4-flash",
    prompt="Say hello"
)

print(result)