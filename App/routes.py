import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        saved_paths = []
        for file in uploaded_files:
            if file.filename != "":
                filename = secure_filename(file.filename)
                save_path = os.path.join("uploads", filename)
                file.save(save_path)
                saved_paths.append(filename)

        # TODO: Run extractor + fingerprint + graph
        return render_template("index.html", uploaded=True, files=saved_paths)

    return render_template("index.html", uploaded=False)
