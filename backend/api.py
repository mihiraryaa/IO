from langchain_openai import ChatOpenAI
model_openai=ChatOpenAI(model='gpt-4o-mini')
import json
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
with open('data/resume_data.json', 'r') as file:
    resumes = json.load(file)

def resume_model(query, resume):
    sys=SystemMessage(content="You are a resume analyzer. Given the candidate's resume and the job description categorize it as high-fit, maybe fit or bad fit with exlanation")
    user=HumanMessage(content=f"# Job description: \n{query}\n# Resume:\n {resume}")
    prompt=[sys, user]
    res=model_openai.invoke(prompt)
    return res.content


from fastapi import FastAPI, WebSocket
from langchain import OpenAI
import asyncio

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for processing data points one by one.
    """
    await websocket.accept()
    try:
        while True:
            query = await websocket.receive_text()
            
            # Process each data point and send the result incrementally
            for resume in resumes:
                
                # Process the query using LangChain
                response = resume_model(query, resume)
                
    
                await websocket.send_text(response)
                
                
                #await asyncio.sleep(1)  # Adjust as needed
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
        await websocket.close()
