from pdf2docx import Converter

def pdf_to_docx(input_file,output_file):
    cv = Converter(input_file)
    cv.convert(output_file)
    cv.close()
    
    