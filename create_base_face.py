from PIL import Image
import requests
import os

# Create sample_images directory if it doesn't exist
os.makedirs("frontend/sample_images", exist_ok=True)

# For now, we'll create a base image that matches the uploaded face characteristics
# We'll enhance the realistic face generator to create the base image

def create_base_face_image():
    """Create a base face image similar to the uploaded one"""
    
    width, height = 600, 700
    img = Image.new('RGB', (width, height), color=(245, 245, 245))
    from PIL import ImageDraw, ImageFilter
    
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Realistic skin tone
    skin_tone = (225, 200, 180)
    
    # Draw background gradient
    for y in range(height):
        alpha = int((y / height) * 20)
        color = (min(255, 245 + alpha), min(255, 245 + alpha), min(255, 245 + alpha))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Head shape
    head_left, head_top = 130, 90
    head_right, head_bottom = 470, 540
    
    # Face oval
    draw.ellipse([head_left, head_top, head_right, head_bottom], 
                 fill=skin_tone, outline=(100, 70, 50), width=2)
    
    # Hair - brown color like in the image
    hair_color = (70, 50, 35)
    draw.ellipse([head_left - 5, head_top - 20, head_right + 5, head_top + 140], 
                 fill=hair_color, outline=(0, 0, 0), width=1)
    
    # Add hair texture details
    for i in range(8):
        x_offset = head_left + (head_right - head_left) // 8 * i
        draw.line([(x_offset, head_top - 20), (x_offset - 10, head_top + 80)], 
                 fill=(50, 30, 15), width=2)
    
    # Eyes - blue-gray like in image
    eye_y = head_top + 100
    left_eye_x = head_left + 80
    right_eye_x = head_right - 80
    
    # Eye whites
    draw.ellipse([left_eye_x - 22, eye_y - 16, left_eye_x + 22, eye_y + 16], 
                 fill=(255, 255, 255), outline=(100, 100, 100), width=1)
    draw.ellipse([right_eye_x - 22, eye_y - 16, right_eye_x + 22, eye_y + 16], 
                 fill=(255, 255, 255), outline=(100, 100, 100), width=1)
    
    # Irises - light blue/gray
    iris_color = (100, 150, 180)
    draw.ellipse([left_eye_x - 12, eye_y - 12, left_eye_x + 12, eye_y + 12], 
                 fill=iris_color)
    draw.ellipse([right_eye_x - 12, eye_y - 12, right_eye_x + 12, eye_y + 12], 
                 fill=iris_color)
    
    # Pupils
    draw.ellipse([left_eye_x - 6, eye_y - 6, left_eye_x + 6, eye_y + 6], 
                 fill=(0, 0, 0))
    draw.ellipse([right_eye_x - 6, eye_y - 6, right_eye_x + 6, eye_y + 6], 
                 fill=(0, 0, 0))
    
    # Eye highlights
    draw.ellipse([left_eye_x - 3, eye_y - 4, left_eye_x + 1, eye_y - 1], 
                 fill=(255, 255, 255))
    draw.ellipse([right_eye_x - 3, eye_y - 4, right_eye_x + 1, eye_y - 1], 
                 fill=(255, 255, 255))
    
    # Eyebrows - brown
    brow_color = (60, 40, 20)
    draw.arc([left_eye_x - 30, eye_y - 45, left_eye_x + 30, eye_y - 20], 
             0, 180, fill=brow_color, width=4)
    draw.arc([right_eye_x - 30, eye_y - 45, right_eye_x + 30, eye_y - 20], 
             0, 180, fill=brow_color, width=4)
    
    # Nose
    nose_y = eye_y + 50
    nose_color = (215, 180, 165)
    draw.polygon([(300, nose_y), (285, nose_y + 35), (315, nose_y + 35)], 
                 fill=nose_color, outline=(100, 70, 50), width=1)
    
    # Nostrils
    draw.ellipse([285, nose_y + 30, 292, nose_y + 39], fill=(100, 70, 50))
    draw.ellipse([308, nose_y + 30, 315, nose_y + 39], fill=(100, 70, 50))
    
    # Mouth - light pink like in image
    mouth_y = nose_y + 55
    mouth_color = (200, 130, 110)
    
    draw.ellipse([265, mouth_y, 335, mouth_y + 22], fill=mouth_color, 
                 outline=(150, 80, 70), width=2)
    draw.line([(265, mouth_y + 11), (335, mouth_y + 11)], fill=(120, 60, 50), width=2)
    
    # Beard/facial hair - stubble effect
    beard_color = (100, 70, 50, 100)
    for i in range(20):
        x = 200 + i * 5
        y = mouth_y + 25
        draw.point((x, y), fill=beard_color)
    
    # Cheeks - subtle blush
    blush_color = (255, 180, 170, 60)
    draw.ellipse([170, eye_y + 60, 220, eye_y + 120], fill=blush_color)
    draw.ellipse([380, eye_y + 60, 430, eye_y + 120], fill=blush_color)
    
    # Ears
    ear_color = (230, 200, 180)
    draw.ellipse([110, head_top + 60, 145, head_top + 180], fill=ear_color, 
                 outline=(100, 70, 50), width=1)
    draw.ellipse([455, head_top + 60, 490, head_top + 180], fill=ear_color, 
                 outline=(100, 70, 50), width=1)
    
    # Neck
    draw.rectangle([270, head_bottom - 10, 330, height - 80], fill=skin_tone, 
                   outline=(100, 70, 50), width=1)
    
    # Shirt
    shirt_color = (120, 40, 40)  # Dark red/maroon like in image
    draw.rectangle([0, height - 80, width, height], fill=shirt_color)
    
    # Apply blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    
    # Save as base_face.jpg
    img.save("frontend/sample_images/base_face.jpg", quality=95)
    print("[✓] Base face image created: frontend/sample_images/base_face.jpg")

# Create the base image
create_base_face_image()
