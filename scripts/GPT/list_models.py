from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

models = client.models.list()

print("\nMODELLI DISPONIBILI:\n")

for model in sorted(models.data, key=lambda m: m.id):
    print(model.id)