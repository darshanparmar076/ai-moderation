from fastapi import FastAPI

from moderation.schemas import QuizRequest
from moderation.service import moderate_quiz_service

from evaluation.schemas import BatchAnswerEvaluationRequest
from evaluation.service import evaluate_answer

app = FastAPI(title="QuizOne AI Service")


# ---------------------------
# Moderation API
# ---------------------------
@app.post("/moderate")
def moderate_quiz(data: QuizRequest):
    return moderate_quiz_service(data)


# ---------------------------
# Batch Answer Evaluation API
# ---------------------------
@app.post("/evaluate-answer-batch")
def evaluate_short_answer_batch(req: BatchAnswerEvaluationRequest):
    results = []

    # Quiz-level AI settings
    settings = req.quiz_settings

    for item in req.evaluations:
        result = evaluate_answer(
            question=item.question,
            model_answer=item.model_answer,
            student_answer=item.student_answer,
            key_points=item.key_points,
            max_marks=item.max_marks,

            full_threshold=settings.full_threshold,
            medium_threshold=settings.medium_threshold,
            low_threshold=settings.low_threshold,

            full_percentage=settings.full_percentage,
            medium_percentage=settings.medium_percentage,
            low_percentage=settings.low_percentage
        )

        results.append(result)

    return {
        "status": "SUCCESS",
        "total_questions": len(results),
        "quiz_settings": {
            "full_threshold": settings.full_threshold,
            "medium_threshold": settings.medium_threshold,
            "low_threshold": settings.low_threshold,
            "full_percentage": settings.full_percentage,
            "medium_percentage": settings.medium_percentage,
            "low_percentage": settings.low_percentage
        },
        "results": results
    }