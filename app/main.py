from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as chat_router
import uvicorn

app = FastAPI(title="Medical Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"status": "OK"}

if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    print("Starting Medical Chatbot API on http://localhost:8000")