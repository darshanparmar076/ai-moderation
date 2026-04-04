import math
from sentence_transformers import util
from evaluation.model_loader import semantic_model


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.strip().lower().split())


def get_semantic_similarity(model_answer: str, student_answer: str) -> float:
    model_answer = normalize_text(model_answer)
    student_answer = normalize_text(student_answer)

    emb1 = semantic_model.encode(model_answer, convert_to_tensor=True)
    emb2 = semantic_model.encode(student_answer, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()
    return round(score * 100, 2)


def get_keypoint_score(key_points: list[str], student_answer: str) -> float:
    if not key_points:
        return 0.0

    student_answer = normalize_text(student_answer)
    matched = 0

    for point in key_points:
        point = normalize_text(point)
        if point and point in student_answer:
            matched += 1

    score = (matched / len(key_points)) * 100
    return round(score, 2)


def get_final_similarity(model_answer: str, student_answer: str, key_points: list[str] = None) -> dict:
    semantic_score = get_semantic_similarity(model_answer, student_answer)

    if key_points:
        keypoint_score = get_keypoint_score(key_points, student_answer)
        final_score = round((semantic_score * 0.70) + (keypoint_score * 0.30), 2)
    else:
        keypoint_score = None
        final_score = semantic_score

    return {
        "semantic_score": semantic_score,
        "keypoint_score": keypoint_score,
        "final_similarity": final_score
    }


def calculate_marks(
    final_similarity: float,
    max_marks: int,
    full_threshold: int,
    medium_threshold: int,
    low_threshold: int,
    full_percentage: int = 100,
    medium_percentage: int = 50,
    low_percentage: int = 25
) -> dict:

    if final_similarity >= full_threshold:
        raw_marks = max_marks * (full_percentage / 100)
        level = "FULL"
    elif final_similarity >= medium_threshold:
        raw_marks = max_marks * (medium_percentage / 100)
        level = "MEDIUM"
    elif final_similarity >= low_threshold:
        raw_marks = max_marks * (low_percentage / 100)
        level = "LOW"
    else:
        raw_marks = 0
        level = "WRONG"

    # Correct mathematical rounding
    final_marks = math.floor(raw_marks + 0.5)

    return {
        "level": level,
        "raw_marks": raw_marks,
        "final_marks": final_marks
    }


def evaluate_answer(
    question: str,
    model_answer: str,
    student_answer: str,
    max_marks: int,
    full_threshold: int,
    medium_threshold: int,
    low_threshold: int,
    key_points: list[str] = None,
    full_percentage: int = 100,
    medium_percentage: int = 50,
    low_percentage: int = 25
) -> dict:

    similarity_result = get_final_similarity(model_answer, student_answer, key_points)

    marks_result = calculate_marks(
        final_similarity=similarity_result["final_similarity"],
        max_marks=max_marks,
        full_threshold=full_threshold,
        medium_threshold=medium_threshold,
        low_threshold=low_threshold,
        full_percentage=full_percentage,
        medium_percentage=medium_percentage,
        low_percentage=low_percentage
    )

    return {
        "question": question,
        "student_answer": student_answer,
        "semantic_score": similarity_result["semantic_score"],
        "keypoint_score": similarity_result["keypoint_score"],
        "final_similarity": similarity_result["final_similarity"],
        "level": marks_result["level"],
        "raw_marks": marks_result["raw_marks"],
        "final_marks": marks_result["final_marks"]
    }