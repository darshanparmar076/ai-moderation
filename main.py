from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from transformers import pipeline

app = FastAPI()

# Load model once

moderator = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)

THRESHOLD = 0.70

# ----------- DTO -----------

class Question(BaseModel):
    question: str
    options: List[str]

class QuizRequest(BaseModel):
    questions: List[Question]

# ----------- CATEGORY MAP -----------

def map_category(label):
    mapping = {
    "toxic": "BAD_WORDS",
    "insult": "HARASSMENT",
    "threat": "VIOLENCE",
    "obscene": "EXPLICIT",
    "identity_hate": "HARASSMENT"
    }
    return mapping.get(label.lower(), "UNKNOWN")

# ----------- API -----------

@app.post("/moderate")
def moderate_quiz(data: QuizRequest):


    issues = []  

    for q_index, q in enumerate(data.questions):  

        # AI check question  
        results = moderator(q.question)[0]  
        for r in results:  
            if r["score"] > THRESHOLD and r["label"] != "neutral":  
                issues.append({  
                    "type": "QUESTION",  
                    "questionIndex": q_index,  
                    "text": q.question,  
                    "category": map_category(r["label"]),  
                    "confidence": round(r["score"], 4)  
                })  
                break  

        # AI check options for the current question
        for o_index, opt in enumerate(q.options):
            results = moderator(opt)[0]
            for r in results:
                if r["score"] > THRESHOLD and r["label"] != "neutral":
                    issues.append({
                        "type": "OPTION",
                        "questionIndex": q_index,
                        "optionIndex": o_index,
                        "text": opt,
                        "category": map_category(r["label"]),
                        "confidence": round(r["score"], 4)
                    })
                    break

    if not issues:  
        return {"status": "SAFE"}  

    return {  
        "status": "FLAGGED",  
        "issues": issues  
    }  