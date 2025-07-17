import numpy as np
import re
import string
from sklearn.feature_extraction.text import CountVectorizer
from app.fingerprints import get_embeddings

def extract_features(text):
    words = text.split()
    sentences = re.split(r'[.!?]', text)

    num_words = len(words)
    num_sentences = len([s for s in sentences if s.strip()])
    avg_word_length = np.mean([len(w) for w in words]) if words else 0
    sentence_length = num_words / num_sentences if num_sentences > 0 else 0
    punctuation_count = sum(1 for c in text if c in string.punctuation)
    uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
    digit_ratio = sum(1 for c in text if c.isdigit()) / len(text) if text else 0

    return np.array([
        num_words,
        avg_word_length,
        sentence_length,
        punctuation_count,
        uppercase_ratio,
        digit_ratio,
    ])

def extract_combined_features(text):
    stylometric = extract_features(text)
    embeddings = get_embeddings(text)
    return np.concatenate([stylometric, embeddings])