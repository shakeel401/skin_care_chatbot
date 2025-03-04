import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router  # Import the router

app = FastAPI()

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the chat router
app.include_router(chat_router)

@app.get("/")  # Changed to GET for better REST API practice
def read_route():
    return {"message": "SkinCare Chatbot API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use PORT from env or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
