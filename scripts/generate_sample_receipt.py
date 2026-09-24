from PIL import Image, ImageDraw, ImageFont
import os

def create_receipt():
    # Create a simple white image
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    # Draw text
    draw.text((20, 20), "ACME CORP", fill="black", font=title_font)
    draw.text((20, 70), "123 Business Rd.", fill="black", font=font)
    draw.text((20, 100), "Date: 2024-05-15", fill="black", font=font)
    
    draw.text((20, 150), "-"*40, fill="black", font=font)
    draw.text((20, 180), "Coffee              $4.50", fill="black", font=font)
    draw.text((20, 210), "Laptop Stand        $45.00", fill="black", font=font)
    draw.text((20, 240), "-"*40, fill="black", font=font)
    
    draw.text((20, 270), "Subtotal            $49.50", fill="black", font=font)
    draw.text((20, 300), "Tax                 $2.48", fill="black", font=font)
    draw.text((20, 350), "Total               $51.98", fill="black", font=title_font)
    
    return img

def main():
    img = create_receipt()
    os.makedirs("data/samples", exist_ok=True)
    path = "data/samples/sample_receipt.jpg"
    img.save(path)
    print(f"Generated sample receipt at {path}")
    print("You can upload this image to the Streamlit UI to test the extraction pipeline.")

if __name__ == "__main__":
    main()
