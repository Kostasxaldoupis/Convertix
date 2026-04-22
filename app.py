from flask import Flask, render_template, request, send_file
import os
import subprocess
import uuid
import sys

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":
        file = request.files["file"]
        output_format = request.form["format"]
        
        unique_name = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, unique_name + "_" + file.filename)
        
        file.save(input_path)
        
        output_file = unique_name + "." + output_format
        output_path = os.path.join(OUTPUT_FOLDER,output_file)
        
        result = subprocess.run(
            [sys.executable, "cli.py", input_path,output_path],
            capture_output = True,
            text = True
        )
        #if conversion fails
        if result.returncode != 0 or not os.path.exists(output_path):
            return f"Conversion failed:\n{result.stderr or result.stdout}", 400

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)