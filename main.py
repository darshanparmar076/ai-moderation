from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from transformers import pipeline
import re

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

# ----------- VALIDATION -----------

def looks_like_gibberish_token(token: str) -> bool:
    t = token.lower()

    allow_short = {
        "a", "an", "i", "to", "of", "in", "on", "is", "it", "if", "or",
        "no", "yes", "true", "false", "api", "sql", "ui", "ux", "js", "ts", "ai", "ml"
    }

    if t in allow_short:
        return False

    if len(t) <= 2:
        return True

    vowels = sum(1 for c in t if c in "aeiouy")
    vowel_ratio = vowels / len(t)

    if len(t) >= 6 and vowel_ratio < 0.18:
        return True

    if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", t):
        return True

    return False

def is_valid_text(text: str) -> bool:
    if not text or not text.strip():
        return False

    # Must contain alphabetic content
    letter_count = sum(c.isalpha() for c in text)
    if letter_count == 0:
        return False

    tokens = [tok for tok in re.findall(r"[A-Za-z]+", text) if tok]
    if not tokens:
        return False

    gibberish_tokens = sum(1 for tok in tokens if looks_like_gibberish_token(tok))

    # If all tokens are gibberish, reject the text.
    if gibberish_tokens == len(tokens):
        return False

    return True

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

        # 🔹 Validate question first
        if not is_valid_text(q.question):
            issues.append({
                "type": "QUESTION",
                "questionIndex": q_index,
                "text": q.question,
                "category": "INVALID",
                "confidence": 1.0
            })
            continue  # skip AI check

        # 🔹 AI check question
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

        # 🔹 Validate + check options
        for o_index, opt in enumerate(q.options):

            if not is_valid_text(opt):
                issues.append({
                    "type": "OPTION",
                    "questionIndex": q_index,
                    "optionIndex": o_index,
                    "text": opt,
                    "category": "INVALID",
                    "confidence": 1.0
                })
                continue

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

    # ----------- RESPONSE -----------

    if not issues:
        return {
            "status": "SAFE"
        }

    return {
        "status": "FLAGGED",
        "issues": issues
    }
