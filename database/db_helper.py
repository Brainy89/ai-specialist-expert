import sqlite3

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, role TEXT, message TEXT)''')
    conn.commit()
    conn.close()

def save_message(user_id, role, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history VALUES (?, ?, ?)", (user_id, role, message))
    conn.commit()
    conn.close()

def get_history(user_id, limit=5):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    # နောက်ဆုံးပြောခဲ့တဲ့ message အချို့ကိုပဲ ယူမယ်
    c.execute("SELECT role, message FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    
    # AI နားလည်မယ့် string format ပြောင်းမယ်
    history_str = ""
    for role, msg in reversed(rows):
        history_str += f"{role}: {msg}\n"
    return history_str