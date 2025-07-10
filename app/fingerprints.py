import hashlib
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_embeddings(text):
   return embedding_model.encode(text)
