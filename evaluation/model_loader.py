from sentence_transformers import SentenceTransformer

# Load only once when app starts
semantic_model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")