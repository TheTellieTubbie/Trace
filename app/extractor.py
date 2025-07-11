import os
import re
from docx import Document

def extract_chunks(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        return extract_from_txt(file_path)
    elif ext == '.md':
        return extract_from_md(file_path)
    elif ext == '.py':
        return extract_from_py(file_path)
    elif ext == '.docx':
        return extract_from_docx(file_path)
    else:
        return []

def extract_from_txt(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return [para.strip() for para in text.split("\n\n") if para.strip()]

def extract_from_md(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    blocks = re.split(r'(?:\n\s*\n|```)', text)
    return [block.strip() for block in blocks if block.strip()]

def extract_from_py(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    chunks = []
    current_block = []

    for line in lines:
        if line.strip().startswith('def') or line.strip().startswith('class'):
            if current_block:
                chunks.append("".join(current_block))
                current_block = []
        current_block.append(line)

    if current_block:
        chunks.append("".join(current_block))

    return [chunk.strip() for chunk in chunks if chunk.strip()]

def extract_from_docx(path):
    doc = Document(path)
    chunks = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            chunks.append(text)
    return chunks

