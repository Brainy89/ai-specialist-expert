import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def start_gemini_agent(topic):
    response = client.chat.completions.create(
        # Model နာမည်ကို ဒါလေး ပြောင်းပေးပါ (OpenRouter Official Name)
        model="google/gemini-2.0-flash-001", 
        messages=[
            {
                "role": "system",
                "content": "You are a professional content writer."
            },
            {
                "role": "user",
                "content": f"Write a professional blog post about: {topic}"
            }
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    test_topic = "Why Python is the best for AI development"
    print(f"--- Running via OpenRouter (No VPN needed) ---")
    try:
        result = start_gemini_agent(test_topic)
        print(result)
    except Exception as e:
        print(f"Error: {e}")