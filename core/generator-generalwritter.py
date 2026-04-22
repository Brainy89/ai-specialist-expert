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
    # --- Step 1: Gemini (The Researcher) ---
    gemini_options = ["google/gemini-2.0-flash-001", "google/gemini-flash-1.5"]
    print("Step 1: Researching with Gemini...")
    draft = get_ai_response_with_fallback(
        gemini_options, 
        "You are a researcher. Provide a detailed draft with facts and structure.",
        f"Research and write a draft about: {topic}"
    )

    # --- Step 2: Llama/Claude (The Writing Boost) ---
    writing_options = ["meta-llama/llama-3.1-70b-instruct", "anthropic/claude-3-haiku"]
    print("Step 2: Polishing with Writing Agent...")
    polished = get_ai_response_with_fallback(
        writing_options,
        "You are a creative writer. Make this content human-like and engaging.",
        f"Polish this content:\n\n{draft}"
    )

    # --- Step 3: ChatGPT (The Logic & QA Agent) ---
    # GPT-4o mini က logic စစ်တာ အရမ်းတော်ပြီး Free နီးပါး ဈေးသက်သာပါတယ် (OpenRouter မှာ free version ရှိတတ်ပါတယ်)
    gpt_options = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo"]
    print("Step 3: Final QA with ChatGPT...")
    final_output = get_ai_response_with_fallback(
        gpt_options,
        "You are a professional editor. Add a catchy title, meta description, and ensure the logical flow is perfect. Output the final blog post in Markdown format.",
        f"Review and finalize this blog post:\n\n{polished}"
    )
    
    return final_output

if __name__ == "__main__":
    test_topic = "Why Python is the best for AI development"
    print(f"--- Running Unstoppable Agent ---")
    try:
        final_result = start_pro_writing_agent(test_topic)
        print("\n--- FINAL CONTENT ---\n")
        print(final_result)
    except Exception as e:
        print(f"Fatal Error: {e}")