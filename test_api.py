import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print("--- DIAGNOSTIC TEST ---")

# 2. Check Key Existence
if not api_key:
    print("FATAL: GOOGLE_API_KEY not found in .env")
    exit(1)
else:
    print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# 3. Test Model Connection
print("\nAttempting to connect to Gemini...")
try:
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    response = llm.invoke("Hello, say 'API Working' if you hear me.")
    print("\nSUCCESS! Model Response:")
    print(response.content)
except Exception as e:
    print("\nFATAL: Model connection failed!")
    print(f"Error: {e}")
