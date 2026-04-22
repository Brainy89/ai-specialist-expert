import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)


# ၁။ Specialist အလိုက် Prompt များကို သတ်မှတ်ခြင်း
SPECIALIST_SETTINGS = {
    "Networking": {
        "role": "Senior Network Engineer",
        "expertise": "Enterprise Networking, Cisco, MikroTik, Ubiquiti, OSPF, VLAN, VPN, and Network Security."
    },
    "Ruijie_Specialist": {
        "role": "Ruijie Networks Solution Architect",
        "expertise": "Ruijie Reyee Series, Cloud Management, SON (Self-Organizing Network), and Enterprise Switches."
    },
    "Tech_Expert": {
        "role": "Technology Content Strategist",
        "expertise": "Emerging tech, Software development, and AI trends."
    },
    "Computer_Hardware": {
        "role": "Hardware Specialist",
        "expertise": "Server architecture, PC performance, and hardware benchmarking."
    }
}

# System Prompt ထဲမှာ ဒါလေး ထပ်ထည့်ပါ
instructions = """
- Output everything in Myanmar language (Unicode).
- Use professional Myanmar technical terms where appropriate.
- If it's a technical term like 'Cloud Management' or 'Throughput', keep the English term in brackets, e.g., လှိုင်းနှုန်းဖြတ်သန်းမှု (Throughput)။
- Ensure the tone is helpful, professional, and industry-expert level.
"""

def get_ai_response_with_fallback(model_list, system_prompt, user_prompt):
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
            continue 
    return None

def start_pro_writing_agent(topic, category="Networking", history=""):
    # ရွေးချယ်ထားသော Specialist အချက်အလက်ကို ယူခြင်း
    spec = SPECIALIST_SETTINGS.get(category, SPECIALIST_SETTINGS["Networking"])
    
    # --- Step 1: Research (Gemini) ---
    gemini_options = ["google/gemini-2.0-flash-001", "google/gemini-flash-1.5"]
    print(f"Step 1: Researching as {spec['role']}...")
    
    research_system = f"You are a professional researcher. Topic category: {category}. Previous context: {history}"
    draft = get_ai_response_with_fallback(
        gemini_options, 
        research_system,
        f"Provide a technical and detailed research draft about: {topic}"
    )

    # --- Step 2: Expert Polishing (Llama/Claude) ---
    writing_options = ["meta-llama/llama-3.1-70b-instruct", "anthropic/claude-3-haiku"]
    print(f"Step 2: Expert Polishing ({category})...")
    
    # Ruijie အတွက် အထူးညွှန်ကြားချက်များ ထည့်သွင်းခြင်း
    ruijie_extra = "Focus on Ruijie Cloud App, SON technology, and Reyee series features." if category == "Ruijie_Specialist" else ""

    polish_system = f"""You are a {spec['role']} with 15+ years experience. Expertise: {spec['expertise']}.
    Instructions:
    - Use technical, accurate language (e.g., Throughput, Latency, PoE+, Layer 3).
    - Write in Myanmar language but keep technical terms in English where appropriate.
    - {ruijie_extra}
    - Avoid generic marketing fluff; provide real-world expert insights.
    - Context from history: {history}"""

    polished = get_ai_response_with_fallback(
        writing_options,
        polish_system,
        f"Rewrite and polish this technical draft in Myanmar language:\n\n{draft}"
    )

    # --- Step 3: Final QA (ChatGPT) ---
    gpt_options = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo"]
    print("Step 3: Final QA & Formatting...")
    
    final_output = get_ai_response_with_fallback(
        gpt_options,
        "You are a professional Technical Editor. Ensure the logical flow is perfect for a technical audience. Output in clean Markdown.",
        f"Review and finalize this technical post:\n\n{polished}"
    )
    
    return final_output

if __name__ == "__main__":
    # စမ်းသပ်ရန် (Ruijie အကြောင်း စမ်းကြည့်မယ်)
    test_topic = "Ruijie Reyee RG-RAP2260(G) Wi-Fi 6 AP အကြောင်း Technical Review"
    print(f"--- Running Specialist Agent ---")
    try:
        final_result = start_pro_writing_agent(test_topic, category="Ruijie_Specialist")
        print("\n--- FINAL CONTENT ---\n")
        print(final_result)
    except Exception as e:
        print(f"Fatal Error: {e}")