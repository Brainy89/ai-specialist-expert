import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def get_ai_response_with_fallback(model_list, system_prompt, user_prompt):
    """Model တစ်ခုမရရင် နောက်တစ်ခုကို Auto ပြောင်းသုံးမယ့် Function"""
    for model in model_list:
        try:
            print(f"Trying {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Failed {model}: {e}")
            continue # နောက် Model တစ်ခုကို ဆက်စမ်းမယ်
    return None

def start_pro_writing_agent(topic):
    # Step 1: Gemini (Research) - Fallback List
    gemini_options = [
        "google/gemini-2.0-flash-001",
        "google/gemini-flash-1.5-8b",
        "google/gemini-flash-1.5"
    ]
    
    print("Step 1: Researching...")
    draft = get_ai_response_with_fallback(
        gemini_options, 
        "You are a detailed researcher. Provide a rich draft with facts.",
        f"Research and write a draft about: {topic}"
    )

    if not draft:
        return "အကုန်စမ်းကြည့်တာ Gemini API လုံးဝ အလုပ်မလုပ်ပါဘူး။ Key သို့မဟုတ် Internet ကို စစ်ပေးပါ။"

    # Step 2: Llama (Writing Boost) - Fallback List
    llama_options = [
        "meta-llama/llama-3.1-70b-instruct:free",
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct:free"
    ]

    print("Step 2: Polishing...")
    final_content = get_ai_response_with_fallback(
        llama_options,
        "You are a creative editor. Rewrite the draft to be more professional and human.",
        f"Polish this draft and make it human-like:\n\n{draft}"
    )
    
    return final_content if final_content else draft # Llama မရရင် Gemini draft ကိုပဲ ပြန်ပေးမယ်

if __name__ == "__main__":
    test_topic = "Why Python is the best for AI development"
    print(f"--- Running Unstoppable Agent ---")
    try:
        final_result = start_pro_writing_agent(test_topic)
        print("\n--- FINAL CONTENT ---\n")
        print(final_result)
    except Exception as e:
        print(f"Fatal Error: {e}")