import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.generator import start_pro_writing_agent
from fastapi.middleware.cors import CORSMiddleware

# Path ပြဿနာမတက်အောင် (core/ folder ကို သိအောင်)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.generator import start_pro_writing_agent

app = FastAPI(
    title="AI Specialist API",
    description="Networking & Ruijie Expert API",
    version="1.1.0"
)

# CORS Middleware (Chrome/Web အတွက် အထူးအရေးကြီးသည်)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Data Structure (Category ပါ ထည့်ထားပါတယ်)
class ContentRequest(BaseModel):
    topic: str
    category: str = "Networking" # Default က Networking ပါ

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Specialist API is running perfectly!"
    }

@app.post("/generate")
def generate_content_api(request: ContentRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
        
    try:
        print(f"Request Topic: {request.topic} | Category: {request.category}")
        
        # Core Logic ကို Category ပါ ထည့်ပို့လိုက်ပါမယ်
        result = start_pro_writing_agent(request.topic, category=request.category)
        
        if not result:
            raise HTTPException(status_code=500, detail="AI failed to generate content.")
            
        return {
            "status": "success",
            "category": request.category,
            "content": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

#if __name__ == "__main__":
# Local မှာ run ရင် api.main:app လို့ သုံးပါ
#   uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)