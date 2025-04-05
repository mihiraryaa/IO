import asyncio
import json
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import random

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

# Load sample resumes
sample_resumes = [
    {
        "name": "John Doe",
        "role": "Senior Software Engineer",
        "skills": ["JavaScript", "React", "AWS", "Node.js"],
    },
    {
        "name": "Jane Smith",
        "role": "Data Scientist",
        "skills": ["Python", "Machine Learning", "SQL", "TensorFlow"],
    },
    {
        "name": "Robert Johnson",
        "role": "Marketing Manager",
        "skills": ["Social Media", "Content Strategy", "SEO", "Analytics"],
    },
    {
        "name": "Sophia Chen",
        "role": "UX/UI Designer",
        "skills": ["Figma", "UI Design", "User Research", "Prototyping"],
    },
    {
        "name": "Michael Williams",
        "role": "Product Manager",
        "skills": ["Agile", "JIRA", "Product Strategy", "Stakeholder Management"],
    }
]

# Hardcoded analysis responses based on job descriptions
def get_analysis_response(job_desc, resume):
    """Generate a hardcoded analysis response based on job description and resume"""
    
    # Convert job description to lowercase for easier matching
    job_desc_lower = job_desc.lower()
    
    # Determine fit category based on basic keyword matching
    fit_category = "maybe-fit"  # Default
    
    # Check for developer/engineer roles
    if any(kw in job_desc_lower for kw in ["developer", "engineer", "programming", "coding"]):
        if resume["name"] == "John Doe":
            fit_category = "good-fit"
            details = "Strong experience in software development with the exact technical skills required."
        elif resume["name"] == "Jane Smith":
            fit_category = "maybe-fit"
            details = "Has technical background but focused more on data science than software engineering."
        else:
            fit_category = "bad-fit"
            details = "Doesn't have the required technical experience for this role."
    
    # Check for data science roles
    elif any(kw in job_desc_lower for kw in ["data", "analytics", "machine learning", "ai"]):
        if resume["name"] == "Jane Smith":
            fit_category = "good-fit"
            details = "Excellent match with strong data science skills and ML experience."
        elif resume["name"] == "John Doe":
            fit_category = "maybe-fit"
            details = "Has technical skills but lacks specific data science expertise."
        else:
            fit_category = "bad-fit"
            details = "Doesn't have the required data analysis experience."
    
    # Check for marketing roles
    elif any(kw in job_desc_lower for kw in ["marketing", "social media", "seo", "content"]):
        if resume["name"] == "Robert Johnson":
            fit_category = "good-fit"
            details = "Strong marketing background with experience in all required areas."
        else:
            fit_category = "bad-fit"
            details = "Doesn't have the required marketing experience for this role."
    
    # Check for design roles
    elif any(kw in job_desc_lower for kw in ["design", "ux", "ui", "user experience"]):
        if resume["name"] == "Sophia Chen":
            fit_category = "good-fit"
            details = "Excellent design skills with UX/UI expertise."
        else:
            fit_category = "bad-fit"
            details = "Doesn't have the required design experience for this role."
    
    # Check for product management roles
    elif any(kw in job_desc_lower for kw in ["product", "project manager", "agile", "scrum"]):
        if resume["name"] == "Michael Williams":
            fit_category = "good-fit"
            details = "Strong product management background with all required skills."
        else:
            fit_category = "bad-fit"
            details = "Doesn't have the required product management experience."
            
    # Generate random analysis for other cases
    else:
        # For queries we don't specifically handle, randomize the response
        fit_options = ["good-fit", "maybe-fit", "bad-fit"]
        random_index = random.randint(0, 2)
        fit_category = fit_options[random_index]
        
        if fit_category == "good-fit":
            details = f"{resume['name']} has most of the skills required for this position."
        elif fit_category == "maybe-fit":
            details = f"{resume['name']} has some relevant experience but might need additional training."
        else:
            details = f"{resume['name']} doesn't seem to match the requirements for this role."
    
    # Construct a response similar to what the AI would provide
    response = f"""**Fit Category: {fit_category.replace('-', ' ').title()}**

**Candidate Name:** {resume['name']}
**Current Role:** {resume['role']}
**Key Skills:** {', '.join(resume['skills'])}

**Analysis:**
{details}

Based on the job description provided, this candidate would be a {fit_category.replace('-', ' ')} for the role. 
The candidate's background in {resume['skills'][0]} and {resume['skills'][1]} {'aligns well with' if fit_category == 'good-fit' else 'partially matches' if fit_category == 'maybe-fit' else 'doesn\'t align with'} the requirements.

**Recommendation:**
{'Consider for interview' if fit_category != 'bad-fit' else 'Not recommended for this position'}
"""
    return response

@app.get("/")
def read_root():
    return {"message": "Mock Resume Analyzer API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "resumes_loaded": len(sample_resumes)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for processing resumes one by one.
    """
    client = f"{websocket.client.host}:{websocket.client.port}"
    print(f"New WebSocket connection from {client}")
    
    try:
        await websocket.accept()
        print(f"WebSocket connection accepted from {client}")
        
        while True:
            query = await websocket.receive_text()
            print(f"Received job description from {client}: {query[:50]}...")
            
            # Process each resume and send the result
            for resume in sample_resumes:
                try:
                    # Generate a mock analysis response
                    response = get_analysis_response(query, resume)
                    print(f"Processed resume for: {resume['name']}")
                    
                    # Send the response back to the client
                    await websocket.send_text(response)
                    print(f"Sent response for {resume['name']} to {client}")
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.5)
                except Exception as e:
                    error_msg = f"Error processing resume: {str(e)}"
                    print(error_msg)
                    await websocket.send_text(error_msg)
    except Exception as e:
        print(f"WebSocket connection error with {client}: {e}")
    finally:
        print(f"WebSocket connection closed with {client}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Mock Resume Analyzer Backend")
    print("=" * 50)
    print(f"Available endpoints:")
    print("  - GET /: Root endpoint")
    print("  - GET /health: Health check")
    print("  - WebSocket /ws: Resume analysis")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000) 