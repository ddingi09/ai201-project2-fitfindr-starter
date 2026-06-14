import os
from dotenv import load_dotenv
from groq import Groq

# Load from the current directory's .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.environ.get("GROQ_API_KEY")
print(f"API Key set: {bool(api_key)}")

if api_key:
    try:
        client = Groq(api_key=api_key)
        print("Groq client created successfully")

        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            temperature=0.9
        )
        print(f"Response received: {resp.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No API key found")
