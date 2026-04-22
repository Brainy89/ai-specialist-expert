import os
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Path ပြဿနာမတက်အောင် (core/ နဲ့ database/ ကို သိအောင်)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.generator import start_pro_writing_agent
from database.db_helper import init_db, save_message, get_history

load_dotenv()
init_db() # Database ကို အရင်ဆောက်မယ်

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# User category ကို ခေတ္တမှတ်ထားရန်
user_category = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Networking 🌐", callback_data='Networking'),
            InlineKeyboardButton("Ruijie Specialist 📡", callback_data='Ruijie_Specialist'),
        ],
        [
            InlineKeyboardButton("Tech Expert 💻", callback_data='Tech_Expert'),
            InlineKeyboardButton("Hardware 🛠️", callback_data='Computer_Hardware'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "မင်္ဂလာပါ။ AI Content Specialist Bot မှ ကြိုဆိုပါတယ်။\nဘယ် Specialist နဲ့ ဆွေးနွေးချင်ပါသလဲ?", 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_category[query.from_user.id] = query.data
    await query.edit_message_text(text=f"Selected: {query.data} ✅\nအခု သင်သိလိုတဲ့ Topic ကို ပို့ပေးလို့ရပါပြီ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    topic = update.message.text
    
    # ရွေးထားတဲ့ category ကိုယူမယ်၊ မရှိရင် Networking ကိုသုံးမယ်
    category = user_category.get(user_id, "Networking")
    
    # ၁။ အရင်ပြောထားတဲ့ History ကို DB ကနေယူမယ်
    history_context = get_history(user_id)
    
    wait_msg = await update.message.reply_text(f"[{category}] Specialist က စဉ်းစားပေးနေပါတယ်... ခဏစောင့်ပေးပါဗျာ။")
    
    try:
        # ၂။ AI Agent ဆီ history ပါ ထည့်ပို့မယ်
        result = start_pro_writing_agent(topic, category=category, history=history_context)
        
        # ၃။ မေးခွန်းနဲ့ အဖြေကို DB မှာ သိမ်းမယ်
        save_message(user_id, "User", topic)
        save_message(user_id, "AI Specialist", result[:500]) # အကျဉ်းချုပ်ပဲသိမ်းမယ် (Memory context အတွက်)
        
        # စာသားရှည်ရင် ခွဲပို့မယ်
        if len(result) > 4096:
            for i in range(0, len(result), 4096):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=result[i:i+4096])
        else:
            await update.message.reply_text(result)
            
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    t_request = HTTPXRequest(connect_timeout=600, read_timeout=600)
    application = ApplicationBuilder().token(TOKEN).request(t_request).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler)) # Button တွေအတွက်
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running with Specialist Menu & Database...")
    application.run_polling()