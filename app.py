# import imghdr
from PIL import Image
from io import BytesIO
import os
from flask import Flask, render_template, request, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_PATH"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB
app.config["UPLOAD_EXTENSIONS"] = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".txt",
    ".pdf",
    ".docx",
]


# Validación del contenido del archivo
# def validate_image(stream):
#     header = stream.read(512)
#     stream.seek(0)
#     format = imghdr.what(None, header)
#     if not format:
#         return None
#     return "." + (format if format != "jpeg" else "jpg")
def validate_image(stream):
    try:
        image = Image.open(BytesIO(stream.read()))
        stream.seek(0)  # Volver al inicio para que Flask pueda guardar la imagen luego
        return "." + image.format.lower()
    except Exception:
        return None


# Manejo de error cuando el archivo es muy grande
@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


# Página principal
@app.route("/")
def index():
    files = os.listdir(app.config["UPLOAD_PATH"])
    return render_template("index.html", files=files)


# Ruta para manejar la subida de archivos
@app.route("/", methods=["POST"])
def upload_files():
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)

    if filename != "":
        if not is_allowed_file(filename, uploaded_file.stream):
            return "Invalid image", 400
        uploaded_file.save(os.path.join(app.config["UPLOAD_PATH"], filename))

    return "", 204


def is_allowed_file(filename, stream):
    file_ext = os.path.splitext(filename)[1].lower()
    detected_ext = validate_image(stream)
    return file_ext in app.config["UPLOAD_EXTENSIONS"]  # and file_ext == detected_ext


# Ruta para servir los archivos subidos
@app.route("/uploads/<filename>")
def upload(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)
