from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import run_prompt

app = FastAPI(
    # title="IAQ Analysis Tool API",
    # description="API for the AI-powered Indoor Air Quality Analysis Tool",
    # version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows our React frontend (running on a different port) to call the API
origins = [
    "http://localhost:3000", # The default port for React apps
    # Add any other origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body model for type checking
class QueryRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    """
    Receives a user query, processes it with the AI agent,
    and returns the structured analysis result.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannots be empty.")
    
    try:
        # This is the main call to our agent logic
        result = run_prompt(request.query)
        return await result
    except Exception as e:
        # Generic error handler for unexpected issues
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the IAQ Analysis Tool API"}