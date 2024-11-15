from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

import os  # Import os module

from dotenv import load_dotenv  # Import dotenv for loading environment variables

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')  # Load API key from .env

app = FastAPI()

# Get the absolute path to the static directory
static_directory = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=static_directory), name="static")

class Question(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(static_directory, "index.html")) as f:
        return f.read()

@app.post("/ask")
async def ask_question(q: Question):
    try:
        # Call the Mistral API
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",  # Mistral API endpoint
            headers={
                "Authorization": "Bearer {API_KEY}",  # Use the API key from environment variable
                "Content-Type": "application/json",
            },
            json={
                "model": "ministral-3b-latest",  # Use the appropriate Mistral model
                "messages": [{"role": "user", "content": q.question}]
            }
        )
        
        response.raise_for_status()  # Raise an error for bad responses
        
        # Check if the response contains the expected structure
        if 'choices' in response.json() and len(response.json()['choices']) > 0:
            answer = response.json()['choices'][0]['message']['content']
            return {"answer": answer}
        else:
            raise HTTPException(status_code=500, detail="No valid response from Mistral API")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
