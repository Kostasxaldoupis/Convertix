from pdf2docx import Converter
import os

def pdf_to_docx(input_file, output_file):
    """Convert PDF to DOCX with better error handling"""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"PDF file not found: {input_file}")
    
    # Check if PDF is valid (has content)
    if os.path.getsize(input_file) == 0:
        raise ValueError("PDF file is empty")
    
    try:
        cv = Converter(input_file)
        cv.convert(output_file, start=0, end=None)  # Convert all pages
        cv.close()
        
        # Verify output
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise RuntimeError("PDF conversion produced empty output")
            
    except Exception as e:
        # Clean up partial output if it exists
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass
        raise RuntimeError(f"PDF to DOCX conversion failed: {str(e)}")