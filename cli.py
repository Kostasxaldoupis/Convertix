import argparse
import os

from converters.image_converter import convert_image, images_to_pdf
from converters.pdf_converter import pdf_to_docx
from converters.data_converter import csv_to_json

def get_extension(file):
        return os.path.splitext(file)[1].lower().replace(".", "")

CONVERTERS = {
    ("png", "jpg"): convert_image,
    ("jpg", "png"): convert_image,
    ("jpeg", "png"): convert_image,
    ("png", "webp"): convert_image,
    ("webp", "png"): convert_image,

    ("png", "pdf"): images_to_pdf,
    ("jpg", "pdf"): images_to_pdf,
    ("jpeg", "pdf"): images_to_pdf,

    ("pdf", "docx"): pdf_to_docx,
    ("csv", "json"): csv_to_json,
}

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")

args = parser.parse_args()

input_ext = get_extension(args.input)
output_ext = get_extension(args.output)

converter = CONVERTERS.get((input_ext, output_ext))

if not converter:
    print(f"❌ Error: Conversion {input_ext} → {output_ext} is not supported.")
else:
    try:
        print("🔄 Converting...")
        converter(args.input, args.output)
        print(f"✅ Success: {args.input} → {args.output} converted successfully.")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")