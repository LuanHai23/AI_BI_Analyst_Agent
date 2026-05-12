from fastapi import FastAPI, HTTPException
from app.llm.groq_client import LLMclient
from app.schemas.chat_schema import ChatRequest, ChatResponse

app = FastAPI(
    title = "AI Data Analyst Agent API",
    description = "Backend API for AI-powered data analysis agent",
    version = "0.1.0",
)

llm_client = LLMclient()


@app.get("/")
def root():
    return {
        "message": "AI Data Analyst Agent API is running",
        "docs": "/docs",
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = llm_client.chat(request.message)
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str())
    