from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import uuid
import sys
import shutil
from pathlib import Path

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Define supported conversions (mirrors cli.py)
SUPPORTED_CONVERSIONS = {
    "png": ["jpg", "webp", "pdf"],
    "jpg": ["png", "pdf"],
    "jpeg": ["png", "pdf"],
    "webp": ["png"],
    "pdf": ["docx"],
    "csv": ["json"],
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files.get("file")
            output_format = request.form.get("format")
            
            if not file or not output_format:
                return "Missing file or format", 400
            
            # Get input extension
            input_ext = file.filename.rsplit(".", 1)[-1].lower()
            
            # Validate conversion is supported
            if output_format not in SUPPORTED_CONVERSIONS.get(input_ext, []):
                return f"Conversion {input_ext} → {output_format} not supported", 400
            
            unique_name = str(uuid.uuid4())
            input_path = os.path.join(UPLOAD_FOLDER, unique_name + "_" + file.filename)
            file.save(input_path)
            
            output_file = unique_name + "." + output_format
            output_path = os.path.join(OUTPUT_FOLDER, output_file)
            
            # Call CLI converter
            result = subprocess.run(
                [sys.executable, "cli.py", input_path, output_path],
                capture_output=True,
                text=True,
                timeout=60  # Add timeout for large files
            )
            
            if result.returncode != 0 or not os.path.exists(output_path):
                return f"Conversion failed:\n{result.stderr or result.stdout}", 400
            
            # Send file and clean up AFTER sending
            response = send_file(output_path, as_attachment=True, download_name=output_file)
            
            # Cleanup after response (using @after_this_request)
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")
            
            return response
            
        except subprocess.TimeoutExpired:
            return "Conversion timed out (file too large?)", 408
        except Exception as e:
            return f"Server error: {str(e)}", 500
    
    return render_template("index.html", supported=SUPPORTED_CONVERSIONS)

if __name__ == "__main__":
    app.run(debug=True)