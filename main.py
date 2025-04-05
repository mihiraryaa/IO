from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
from typing import Dict, List
import re

app = FastAPI()

# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LLM model
model_openai = ChatOpenAI(model="gpt-4")

# Load resume data
with open('data/resumes.json', 'r') as file:
    resumes = json.load(file)

@app.post("/classify")
async def classify_resumes(request: Request):
    data = await request.json()
    query = data.get("query", "")
    
    if not query:
        return {"error": "No query provided"}
    
    results = []
    
    for resume in resumes:
        content = resume["content"]
        
        # Extract basic info
        name = extract_name(content)
        skills = extract_skills(content)
        experience = extract_experience(content)
        
        # Get classification from LLM
        classification = await resume_model(query, content)
        
        # Parse the LLM response
        fit = parse_fit_category(classification)
        summary = parse_summary(classification)
        
        results.append({
            "name": name,
            "fit": fit,
            "summary": summary,
            "skills": skills,
            "experience": experience,
            "content": content
        })
    
    return results

async def resume_model(query: str, resume: str) -> str:
    sys = SystemMessage(content="""
        You are a resume analyzer. Given the candidate's resume and the job description, 
        categorize the candidate as "High Fit", "Maybe Fit", or "Not a Fit" with explanation.
        Also extract key skills and experience relevant to the job description.
        
        Respond in this format:
        Fit Category: [High Fit/Maybe Fit/Not a Fit]
        Explanation: [detailed explanation]
        Key Skills: [comma-separated list]
        Relevant Experience: [summary]
    """)
    
    user = HumanMessage(content=f"""
        Job Description:
        {query}
        
        Resume:
        {resume}
    """)
    
    response = await model_openai.ainvoke([sys, user])
    return response.content

def extract_name(content: str) -> str:
    # Simple name extraction from first line
    first_line = content.split('\n')[0].strip()
    if first_line.startswith('#'):
        return first_line[1:].strip()
    return "Unknown Candidate"

def extract_skills(content: str) -> List[str]:
    # Simple skills extraction (can be enhanced)
    skills = []
    skills_section = re.search(r'(?i)(skills|technical skills|competencies):?(.*?)(?=\n\n|\n\w)', content, re.DOTALL)
    if skills_section:
        skills_text = skills_section.group(2)
        # Extract bullet points or comma-separated items
        skills = re.findall(r'[\u2022\u25cf\-]\s*(.*?)(?=\n|$)|([A-Za-z]+(?:\s*[A-Za-z]+)*(?:\s*/\s*[A-Za-z]+)*)', skills_text)
        skills = [skill[0] or skill[1] for skill in skills if skill[0] or skill[1]]
        skills = [skill.strip() for skill in skills if skill.strip()]
    
    return skills[:10] if skills else ["No skills listed"]

def extract_experience(content: str) -> str:
    # Simple experience extraction (can be enhanced)
    experience_section = re.search(r'(?i)(experience|work history):?(.*?)(?=\n\n|\n\w)', content, re.DOTALL)
    if experience_section:
        return experience_section.group(2)[:500] + "..."  # Truncate
    return "No experience details"

def parse_fit_category(response: str) -> str:
    # Parse the fit category from LLM response
    match = re.search(r'Fit Category:\s*([^\n]+)', response, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Unknown Fit"

def parse_summary(response: str) -> str:
    # Parse the explanation from LLM response
    match = re.search(r'Explanation:\s*([^\n]+)', response, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "No detailed analysis available"

# Existing WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            query = await websocket.receive_text()
            
            for resume in resumes:
                response = await resume_model(query, resume["content"])
                await websocket.send_text(response)
                
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)