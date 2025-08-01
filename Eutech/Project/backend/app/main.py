from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import run_prompt
import json

app = FastAPI()

origins = ["http://localhost:3000",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannots be empty.")
    
    try:
        result = await run_prompt(request.query)
        return result
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "API"}