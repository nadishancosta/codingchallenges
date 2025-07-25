from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- CRUCIAL STEP ---
# Load environment variables from the .env file at the very start.
load_dotenv()

# Now that environment is loaded, we can safely import the agent.
from agent import process_query

app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The origin of your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    """Receives a query, processes it with the agent, and returns the result."""
    result = process_query(request.query)
    return {"answer": result}

@app.get("/")
def read_root():
    return {"message": "AI Agent Backend is running"}