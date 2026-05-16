---
title: AI Moderation
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 🤖 QuizOne AI Evaluation Service

An AI-powered microservice built with **FastAPI** to evaluate short-answer quiz responses using semantic similarity and keyword matching.

---

## 🚀 Features

* ✅ AI-based short answer evaluation
* ✅ Semantic similarity scoring (Sentence Transformers)
* ✅ Optional key point matching
* ✅ Quiz-level configurable marking rules
* ✅ Batch evaluation (multiple questions at once)
* ✅ Integer-based final marks (no decimal confusion)
* ✅ Easy integration with Spring Boot

---

## 🧠 How It Works

```
Student Answer
   ↓
AI Semantic Similarity
   ↓
(Optional) Key Point Matching
   ↓
Final Similarity Score
   ↓
Apply Quiz Threshold Rules
   ↓
Generate Final Marks
```

---

## 🔗 API Endpoint

### Evaluate Answers (Batch)

```
POST /evaluate-answer-batch
```

---

## 📥 Request Format

```json
{
  "quiz_settings": {
    "full_threshold": 85,
    "medium_threshold": 50,
    "low_threshold": 25,
    "full_percentage": 100,
    "medium_percentage": 50,
    "low_percentage": 25
  },
  "evaluations": [
    {
      "question": "What is inheritance?",
      "model_answer": "Inheritance allows one class to acquire properties and methods of another class.",
      "student_answer": "Child class can use parent class properties and methods.",
      "key_points": ["parent class", "child class", "properties", "methods"],
      "max_marks": 3
    }
  ]
}
```

---

## 📤 Response Format

```json
{
  "status": "SUCCESS",
  "total_questions": 1,
  "results": [
    {
      "question": "What is inheritance?",
      "student_answer": "Child class can use parent class properties and methods.",
      "semantic_score": 70.13,
      "keypoint_score": 100,
      "final_similarity": 79.09,
      "level": "MEDIUM",
      "raw_marks": 1.5,
      "final_marks": 2
    }
  ]
}
```

---

## 🧮 Marking Logic

### Step 1: Similarity Calculation

* Semantic similarity (AI model)
* Key point matching (optional)

### Step 2: Apply Thresholds

| Similarity         | Level  |
| ------------------ | ------ |
| ≥ full_threshold   | FULL   |
| ≥ medium_threshold | MEDIUM |
| ≥ low_threshold    | LOW    |
| < low_threshold    | WRONG  |

---

### Step 3: Marks Calculation

```
raw_marks = max_marks × percentage
```

---

### Step 4: Final Rounding

```
final_marks = floor(raw_marks + 0.5)
```

#### Examples:

| Raw Marks | Final Marks |
| --------- | ----------- |
| 2.76      | 3           |
| 2.5       | 3           |
| 1.23      | 1           |
| 0.43      | 0           |

---

## 🏗️ Project Structure

```
context_check/
│
├── main.py
├── requirements.txt
│
├── moderation/
│   ├── schemas.py
│   ├── service.py
│
├── evaluation/
│   ├── schemas.py
│   ├── service.py
│   ├── model_loader.py
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone <repo-url>
cd context_check
```

---

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Run the server

```
uvicorn main:app --reload
```

---

### 5. Open Swagger UI

```
http://localhost:8000/docs
```

---

## 🔧 Tech Stack

* FastAPI
* Sentence Transformers
* HuggingFace Transformers
* PyTorch
* Python

---

## 🔁 Integration with Spring Boot

1. Collect student answers
2. Prepare JSON request
3. Call AI API
4. Receive marks
5. Store results in database

---

## ⚠️ Important Notes

* Only supports **short answers (3–5 lines)**
* `key_points` is optional
* Thresholds must follow:

  ```
  full > medium > low
  ```
* AI result is treated as **final evaluation**

---

## 🏆 Use Case

* Online quizzes
* Subjective answer evaluation
* Automated grading systems
* AI-powered exam platforms

---

## 💬 One-line Summary

> AI service that evaluates subjective answers using semantic similarity and configurable quiz-level grading rules.

---

## 👨‍💻 Author

**Yug Patel**
AI & Data Science Developer

---

## 📌 Future Improvements

* Better key point semantic matching
* Plagiarism detection
* Answer explanation generation
* Multi-language support

---
