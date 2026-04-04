from pydantic import BaseModel
from typing import Optional, List


class QuizEvaluationSettings(BaseModel):
    full_threshold: int
    medium_threshold: int
    low_threshold: int

    full_percentage: int = 100
    medium_percentage: int = 50
    low_percentage: int = 25


class AnswerEvaluationRequest(BaseModel):
    question: str
    model_answer: str
    student_answer: str
    key_points: Optional[List[str]] = None
    max_marks: int


class BatchAnswerEvaluationRequest(BaseModel):
    quiz_settings: QuizEvaluationSettings
    evaluations: List[AnswerEvaluationRequest]