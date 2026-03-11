from PIL import Image

def convert_image(input_file, output_file):
    img = Image.open(input_file)
    img.save(output_file)


def images_to_pdf(input_file, output_file):
    img = Image.open(input_file)

    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.save(output_file, "PDF")