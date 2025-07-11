import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename
from .extractor import extract_chunks
from .fingerprints import get_sha256, get_embeddings

main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    extracted_data = {}

    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        saved_paths = []

        for file in uploaded_files:
            if file.filename != "":
                filename = secure_filename(file.filename)
                save_path = os.path.join("uploads", filename)
                file.save(save_path)
                saved_paths.append(filename)

                chunks = extract_chunks(save_path)
                chunk_data = []

                for chunk in chunks:
                    hash_val = get_sha256(chunk)
                    embedding = get_embeddings(chunk)
                    chunk_data.append({
                        "text": chunk,
                        "hash": hash_val,
                        "embedding": embedding.tolist(),
                    })

                extracted_data[filename] = chunk_data


        return render_template("index.html", uploaded=True, files=saved_paths, extracted=extracted_data)

    return render_template("index.html", uploaded=False)
