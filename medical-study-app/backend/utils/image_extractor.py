import os
import io
from PIL import Image
from pptx import Presentation
from PyPDF2 import PdfReader
from typing import List, Tuple
import hashlib

class ImageExtractor:
    """Extract images from PDF and PowerPoint files"""

    @staticmethod
    def extract_from_pdf(file_path: str, output_dir: str) -> List[Tuple[str, int]]:
        """
        Extract images from PDF file.
        Returns list of (image_path, page_number) tuples.
        """
        images = []
        try:
            reader = PdfReader(file_path)

            for page_num, page in enumerate(reader.pages, start=1):
                # Check if page has images
                if '/XObject' in page['/Resources']:
                    x_object = page['/Resources']['/XObject'].get_object()

                    for obj_name in x_object:
                        obj = x_object[obj_name]

                        if obj['/Subtype'] == '/Image':
                            try:
                                # Extract image data
                                if '/Filter' in obj:
                                    filter_type = obj['/Filter']

                                    if filter_type == '/DCTDecode':  # JPEG
                                        img_data = obj.get_data()
                                        img = Image.open(io.BytesIO(img_data))
                                    elif filter_type == '/FlateDecode':  # PNG
                                        img_data = obj.get_data()
                                        size = (obj['/Width'], obj['/Height'])
                                        img = Image.frombytes('RGB', size, img_data)
                                    else:
                                        continue
                                else:
                                    # Try to get raw image data
                                    img_data = obj.get_data()
                                    img = Image.open(io.BytesIO(img_data))

                                # Skip very small images (likely icons/decorations)
                                if img.width < 50 or img.height < 50:
                                    continue

                                # Generate unique filename
                                img_hash = hashlib.md5(img_data).hexdigest()[:8]
                                filename = f"pdf_p{page_num}_{img_hash}.png"
                                img_path = os.path.join(output_dir, filename)

                                # Save image
                                img.save(img_path, 'PNG')
                                images.append((img_path, page_num))

                            except Exception as e:
                                print(f"Error extracting image from page {page_num}: {e}")
                                continue

        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")

        return images

    @staticmethod
    def extract_from_pptx(file_path: str, output_dir: str) -> List[Tuple[str, int]]:
        """
        Extract images from PowerPoint file.
        Returns list of (image_path, slide_number) tuples.
        """
        images = []
        try:
            prs = Presentation(file_path)

            for slide_num, slide in enumerate(prs.slides, start=1):
                for shape in slide.shapes:
                    # Check if shape contains an image
                    if hasattr(shape, "image"):
                        try:
                            image = shape.image

                            # Get image bytes
                            image_bytes = image.blob

                            # Open with PIL
                            img = Image.open(io.BytesIO(image_bytes))

                            # Skip very small images
                            if img.width < 50 or img.height < 50:
                                continue

                            # Generate unique filename
                            img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                            ext = image.ext  # e.g., 'png', 'jpg'
                            filename = f"pptx_s{slide_num}_{img_hash}.{ext}"
                            img_path = os.path.join(output_dir, filename)

                            # Save image
                            with open(img_path, 'wb') as f:
                                f.write(image_bytes)

                            images.append((img_path, slide_num))

                        except Exception as e:
                            print(f"Error extracting image from slide {slide_num}: {e}")
                            continue

        except Exception as e:
            print(f"Error processing PPTX {file_path}: {e}")

        return images

    @staticmethod
    def extract_images(file_path: str, output_dir: str) -> List[Tuple[str, int]]:
        """
        Extract images from document based on file type.
        Returns list of (image_path, page/slide_number) tuples.
        """
        os.makedirs(output_dir, exist_ok=True)

        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return ImageExtractor.extract_from_pdf(file_path, output_dir)
        elif ext in ['.pptx', '.ppt']:
            return ImageExtractor.extract_from_pptx(file_path, output_dir)
        else:
            return []
