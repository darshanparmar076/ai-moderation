from pydantic import BaseModel
from typing import List


class Question(BaseModel):
    question: str
    options: List[str]


class QuizRequest(BaseModel):
    questions: List[Question]