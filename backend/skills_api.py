from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


app = FastAPI()

class SkillFormat(BaseModel):
    skills: List[dict] = Field(description='List of relevant skills along with their priority score')

@app.post("/list_skills", response_model=SkillFormat)
async def list_skills(query: str):
    """
    Endpoint to take in a job description query and return a list of skills with default priority scores.
    """
    try:
        sys = SystemMessage(content=skills_prompt)
        user = HumanMessage(content=f"# Job description: \n {query} ")
        prompt = [sys, user]
        model = model_llama.with_structured_output(SkillFormat)
        res = model.invoke(prompt)
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

