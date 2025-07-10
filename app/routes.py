import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename
from .extractor import extract_chunks
from .fingerprints import get_sha256, get_embeddings, get_embeddings

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
                extracted_data[filename] = chunks


        return render_template("index.html", uploaded=True, files=saved_paths)

    return render_template("index.html", uploaded=False)
