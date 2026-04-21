from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Geen OPENAI_API_KEY gevonden in environment variables.")
    raise SystemExit

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-4o-mini",
    input="Zeg alleen: ok"
)

print(response.output_text)
