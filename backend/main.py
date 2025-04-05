from langchain_openai import ChatOpenAI
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("resume-analyzer")

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain model
try:
    logger.debug("Initializing OpenAI model")
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key or openai_api_key == "your_openai_api_key_here":
        logger.warning("OPENAI_API_KEY environment variable is not set or contains a placeholder. Using mock model.")
        # Use a mock model for testing if no API key is set
        model_openai = None
    else:
        model_openai = ChatOpenAI(model="gpt-4o-mini")
        logger.info("OpenAI model initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI model: {e}")
    # Fallback model if needed
    model_openai = None

# Load resume data
try:
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'resume_data.json')
    logger.debug(f"Loading resume data from: {data_path}")
    with open(data_path, 'r') as file:
        resumes = json.load(file)
    logger.info(f"Successfully loaded {len(resumes)} resumes")
except Exception as e:
    logger.error(f"Error loading resume data: {e}")
    resumes = []

def resume_model(query, resume_text):
    """
    Analyze a resume against a job description
    """
    if not model_openai:
        # Mock response for testing without API key
        logger.warning("Using mock response as OpenAI model is not initialized")
        name = "Unknown"
        for resume in resumes:
            if resume.get("resume_text") == resume_text:
                name = resume.get("name", "Unknown")
                break
        
        # Generate a mock response
        fit_options = ["high-fit", "maybe-fit", "bad-fit"]
        import random
        fit = random.choice(fit_options)
        return f"This is a mock response for {name}. Based on the resume and job description, this candidate is a {fit}. [This is simulated content since no OpenAI API key is configured]"
    
    try:
        logger.debug(f"Analyzing resume against job description")
        sys = SystemMessage(content="You are a resume analyzer. Given the candidate's resume and the job description categorize it as high-fit, maybe fit or bad fit with explanation")
        user = HumanMessage(content=f"# Job description: \n{query}\n# Resume:\n {resume_text}")
        prompt = [sys, user]
        res = model_openai.invoke(prompt)
        return res.content
    except Exception as e:
        logger.error(f"Error in resume_model: {e}")
        return f"Error analyzing resume: {str(e)}"

@app.get("/")
def read_root():
    logger.debug("Root endpoint called")
    return {"message": "Resume Analyzer API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "resumes_loaded": len(resumes), "openai_configured": model_openai is not None}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for processing resumes one by one.
    """
    client = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"New WebSocket connection from {client}")
    
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted from {client}")
        
        while True:
            query = await websocket.receive_text()
            logger.info(f"Received job description from {client}: {query[:50]}...")
            
            # Process each resume and send the result incrementally
            for i, resume in enumerate(resumes):
                try:
                    resume_text = resume.get("resume_text", "")
                    name = resume.get("name", "Unknown")
                    
                    logger.debug(f"Processing resume {i+1}/{len(resumes)} for: {name}")
                    
                    # Process the query using LangChain
                    response = resume_model(query, resume_text)
                    logger.debug(f"Processed resume for: {name}")
                    
                    # Send the response back to the client
                    await websocket.send_text(response)
                    logger.debug(f"Sent response for {name} to {client}")
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.5)
                except Exception as e:
                    error_msg = f"Error processing resume: {str(e)}"
                    logger.error(error_msg)
                    await websocket.send_text(error_msg)
    except Exception as e:
        logger.error(f"WebSocket connection error with {client}: {e}")
    finally:
        logger.info(f"WebSocket connection closed with {client}")
        try:
            await websocket.close()
        except:
            pass

# Print startup message for debugging
print("=" * 50)
print("Resume Analyzer Backend")
print("=" * 50)
print(f"OpenAI API Key configured: {model_openai is not None}")
print(f"Loaded {len(resumes)} resumes")
print("Available endpoints:")
print("  - GET /: Root endpoint")
print("  - GET /health: Health check")
print("  - WebSocket /ws: Resume analysis")
print("=" * 50)