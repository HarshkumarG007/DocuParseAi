import os
import uuid
import re
import mimetypes
from PIL import Image

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./storage/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "./storage/processed")
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def sanitize_filename(filename: str) -> str:
    """Remove path traversal characters and keep only alphanumeric, dash, underscore."""
    # Strip path traversal
    filename = os.path.basename(filename)
    # Remove everything except alphanumeric, -, _, .
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename

def validate_file(file_content: bytes, filename: str) -> tuple[bool, str]:
    if len(file_content) > MAX_FILE_SIZE:
        return False, "File exceeds 10MB limit."
        
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}"
        
    # Basic magic byte check for images
    if ext in {'.png', '.jpg', '.jpeg'}:
        # Check signature (JPEG: FF D8, PNG: 89 50 4E 47)
        if file_content.startswith(b'\xff\xd8') or file_content.startswith(b'\x89PNG\r\n\x1a\n'):
            return True, ext
        return False, "Invalid image signature."
        
    if ext == '.pdf':
        if file_content.startswith(b'%PDF-'):
            return True, ext
        return False, "Invalid PDF signature."
        
    return True, ext

def save_upload(file_content: bytes, original_filename: str) -> dict:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    is_valid, msg_or_ext = validate_file(file_content, original_filename)
    if not is_valid:
        raise ValueError(msg_or_ext)
        
    doc_id = f"doc_{uuid.uuid4().hex}"
    safe_name = sanitize_filename(original_filename)
    
    # We save it as the doc_id to avoid collision, keeping original name in metadata
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{msg_or_ext}")
    
    with open(file_path, "wb") as f:
        f.write(file_content)
        
    # Get image dimensions if it's an image
    width, height = 0, 0
    if msg_or_ext in {'.png', '.jpg', '.jpeg'}:
        with Image.open(file_path) as img:
            width, height = img.size
            
    # For MVP, if it's PDF, we just set 0,0 and we will convert it later in the pipeline
            
    return {
        "id": doc_id,
        "original_filename": safe_name,
        "file_path": file_path,
        "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream",
        "image_width": width,
        "image_height": height
    }
