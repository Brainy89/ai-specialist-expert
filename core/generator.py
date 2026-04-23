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
    "General_Assistant": {
        "role": "Helpful AI Assistant",
        "expertise": "General knowledge, daily tasks, creative writing, and basic problem solving."
    },
    "Content_Writer": {
        "role": "Professional Content Writer & Marketing Strategist",
        "expertise": "Copywriting, AIDA marketing model, Social media content, Sale scripts, and Brand storytelling."
    },
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
    
    # Ruijie အတွက် အထူးညွှန်ကြားချက်
    ruijie_extra = "Focus on Ruijie Cloud App, SON technology, and Reyee series features." if category == "Ruijie_Specialist" else ""

    # Gemini တစ်ခုတည်းနဲ့တင် အမြန်ဆုံးနဲ့ အကောင်းဆုံးဖြစ်အောင် Prompt တစ်ခုတည်းမှာ အကုန်ပေါင်းလိုက်ပါတယ်
    gemini_options = ["google/gemini-2.0-flash-001", "google/gemini-flash-1.5"]
    
    system_prompt = f"""You are a {spec['role']} with 15+ years experience. 
    Expertise: {spec['expertise']}
    
    INSTRUCTIONS:
    - Write everything in Myanmar language (Unicode).
    - Use professional Myanmar technical terms where appropriate.
    - Keep English technical terms in brackets, e.g., လှိုင်းနှုန်းဖြတ်သန်းမှု (Throughput).
    - Ensure the tone is helpful, professional, and industry-expert level.
    - {ruijie_extra}
    - Avoid generic marketing fluff; provide real-world expert insights.
    - Formatting: Use clean Markdown with clear headings and bullet points.
    
    CONTEXT FROM PREVIOUS CHAT:
    {history}
    """

    print(f"Generating content using Gemini for {category} Specialist...")
    
    final_output = get_ai_response_with_fallback(
        gemini_options, 
        system_prompt,
        f"Please provide a professional response about: {topic}"
    )
    
    return final_output

if __name__ == "__main__":
    test_topic = "Ruijie Reyee RG-RAP2260(G) Wi-Fi 6 AP အကြောင်း Technical Review"
    print(f"--- Running Specialist Agent (High Speed) ---")
    try:
        final_result = start_pro_writing_agent(test_topic, category="Ruijie_Specialist")
        print("\n--- FINAL CONTENT ---\n")
        print(final_result)
    except Exception as e:
        print(f"Fatal Error: {e}")