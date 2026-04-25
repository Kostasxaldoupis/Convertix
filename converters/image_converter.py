from PIL import Image
import os

def convert_image(input_file, output_file, quality=85):
    """Convert between image formats with quality control"""
    try:
        img = Image.open(input_file)
        
        # Handle transparency for JPEG (doesn't support alpha)
        if output_file.lower().endswith(('.jpg', '.jpeg')):
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        
        # Save with appropriate parameters
        save_kwargs = {}
        if output_file.lower().endswith(('.jpg', '.jpeg')):
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif output_file.lower().endswith('.png'):
            save_kwargs['compress_level'] = 6
        elif output_file.lower().endswith('.webp'):
            save_kwargs['quality'] = quality
        
        img.save(output_file, **save_kwargs)
        
    except Exception as e:
        raise RuntimeError(f"Image conversion failed: {str(e)}")

def images_to_pdf(input_file, output_file):
    """Convert single image to PDF"""
    try:
        img = Image.open(input_file)
        
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        
        img.save(output_file, "PDF", resolution=100.0, save_all=False)
    except Exception as e:
        raise RuntimeError(f"PDF creation failed: {str(e)}")

def resize_image(input_file, output_file, max_size=(1920, 1080)):
    """Bonus: Resize image during conversion"""
    img = Image.open(input_file)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(output_file);