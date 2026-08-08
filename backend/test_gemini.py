import os
import dotenv
from google import genai

dotenv.load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API Key: {api_key[:15]}...")

client = genai.Client(api_key=api_key)

# 1. Try listing models
print("\n--- Listing available models ---")
try:
    models = list(client.models.list())
    for m in models:
        print(f"Available Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

# 2. Test candidate flash models
models_to_test = ["gemini-3.5-flash", "gemini-3-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
print("\n--- Testing generate_content with models ---")
for m in models_to_test:
    try:
        res = client.models.generate_content(model=m, contents="Say hello in 3 words")
        print(f"SUCCESS ({m}): {res.text.strip()}")
    except Exception as e:
        print(f"FAILED ({m}): {e}")

