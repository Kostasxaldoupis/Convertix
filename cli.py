import argparse
import os
import sys
import traceback

from converters.image_converter import convert_image, images_to_pdf
from converters.pdf_converter import pdf_to_docx
from converters.data_converter import csv_to_json

def get_extension(file):
    return os.path.splitext(file)[1].lower().replace(".", "")

# Much larger conversion map
CONVERTERS = {
    # Images
    ("png", "jpg"): convert_image,
    ("png", "jpeg"): convert_image,
    ("jpg", "png"): convert_image,
    ("jpeg", "png"): convert_image,
    ("png", "webp"): convert_image,
    ("webp", "png"): convert_image,
    ("png", "pdf"): images_to_pdf,
    ("jpg", "pdf"): images_to_pdf,
    ("jpeg", "pdf"): images_to_pdf,
    ("webp", "jpg"): convert_image,
    ("bmp", "png"): convert_image,
    
    # PDF
    ("pdf", "docx"): pdf_to_docx,
    
    # Data
    ("csv", "json"): csv_to_json,
    ("json", "csv"): None,  # Add if you implement
}

def convert_file(input_path, output_path):
    """Function to call from GUI with better error messages"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check input file size (warn if >100MB)
    file_size = os.path.getsize(input_path) / (1024 * 1024)
    if file_size > 100:
        print(f"⚠️  Large file: {file_size:.1f}MB - may take a while")
    
    input_ext = get_extension(input_path)
    output_ext = get_extension(output_path)
    
    # Try exact match first
    converter = CONVERTERS.get((input_ext, output_ext))
    
    # Try case-insensitive fallback
    if not converter:
        for (iext, oext), conv in CONVERTERS.items():
            if iext.lower() == input_ext and oext.lower() == output_ext:
                converter = conv
                break
    
    if not converter:
        supported = [f"{k[0]}→{k[1]}" for k in CONVERTERS.keys()]
        raise NotImplementedError(
            f"Conversion {input_ext} → {output_ext} not supported.\n"
            f"Supported: {', '.join(supported[:10])}..."
        )
    
    print(f"🔄 Converting: {input_path} → {output_path}")
    print(f"   Size: {file_size:.2f} MB")
    
    try:
        converter(input_path, output_path)
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {str(e)}") from e
    
    # Verify output was created
    if not os.path.exists(output_path):
        raise RuntimeError("Converter ran but no output file was created")
    
    output_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Success! Converted to {output_path} ({output_size:.2f} MB)")
    return True

def main():
    parser = argparse.ArgumentParser(description="Convertix - File Converter")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed errors")
    args = parser.parse_args()
    
    try:
        convert_file(args.input, args.output)
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except NotImplementedError as e:
        print(f"❌ {e}")
        sys.exit(2)
    except Exception as e:
        print(f"❌ {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()