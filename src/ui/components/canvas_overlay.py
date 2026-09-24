from PIL import Image, ImageDraw, ImageFont
import json

# Colors for specific fields (Matches design.md tokens)
COLOR_MAP = {
    "vendor": "#38BDF8",  # Sky Blue
    "date": "#34D399",    # Emerald
    "total": "#FBBF24",   # Amber
    "tax": "#A78BFA",     # Purple
    "subtotal": "#F472B6",# Pink
    "lineitem": "#94A3B8" # Slate
}

def render_bounding_boxes(image_path: str, extractions: list) -> Image.Image:
    """Draw bounding boxes on the original document image."""
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        # Fallback if image not found
        img = Image.new('RGBA', (800, 1000), color=(26, 26, 30, 255))
        
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    width, height = img.size
    
    for ext in extractions:
        field_type = ext.get("field_type", "")
        bbox_str = ext.get("bbox_json", "[]")
        
        try:
            bbox = json.loads(bbox_str)
        except:
            bbox = []
            
        if len(bbox) == 4:
            # Denormalize bounding box (from 0-1000 scale to true image pixels)
            x0 = int((bbox[0] / 1000.0) * width)
            y0 = int((bbox[1] / 1000.0) * height)
            x1 = int((bbox[2] / 1000.0) * width)
            y1 = int((bbox[3] / 1000.0) * height)
            
            color = COLOR_MAP.get(field_type, "#FFFFFF")
            # Semi-transparent fill
            fill_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (60,)
            outline_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
            
            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=outline_color, width=3)
            
    # Combine original image with overlay
    img = Image.alpha_composite(img, overlay)
    return img
