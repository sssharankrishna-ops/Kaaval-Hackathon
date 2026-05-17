from PIL import Image, ImageDraw, ImageFilter
import random
import os

def create_realistic_face(filename, age_label="", is_damaged=False, seed=None):
    """Generate realistic synthetic human face images"""
    if seed:
        random.seed(seed)
    
    width, height = 500, 600
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Skin tone variations (realistic)
    skin_tones = [
        (255, 219, 172),  # Fair
        (246, 194, 109),  # Light
        (219, 172, 86),   # Medium
        (192, 155, 89),   # Medium dark
        (141, 85, 36),    # Dark
    ]
    base_skin = random.choice(skin_tones)
    
    if is_damaged:
        # Darken and desaturate for damaged look
        base_skin = tuple(int(c * 0.8) for c in base_skin)
    
    # Draw background gradient
    for y in range(height):
        alpha = int((y / height) * 30)
        color = (
            min(255, base_skin[0] + alpha),
            min(255, base_skin[1] + alpha // 2),
            min(255, base_skin[2])
        )
        draw.line([(0, y), (width, y)], fill=color)
    
    # Head shape with shading
    head_left, head_top = 120, 80
    head_right, head_bottom = 380, 480
    
    # Draw face oval
    draw.ellipse([head_left, head_top, head_right, head_bottom], 
                 fill=base_skin, outline=(100, 50, 30), width=2)
    
    # Add face shading for depth
    for i in range(20):
        shade = int((i / 20) * 50)
        alpha = int(100 * (1 - i / 20))
        draw.ellipse(
            [head_left + i, head_top + i, head_right - i, head_bottom - i],
            outline=(0, 0, 0, alpha),
            width=1
        )
    
    # Hair
    hair_color = random.choice([(30, 20, 15), (80, 60, 40), (100, 80, 60), (60, 40, 20)])
    if is_damaged:
        hair_color = tuple(int(c * 0.7) for c in hair_color)
    
    # Hair shape (top part of head)
    draw.ellipse([head_left, head_top - 20, head_right, head_top + 120], 
                 fill=hair_color, outline=(0, 0, 0), width=1)
    
    # Eyes
    eye_y = head_top + 80
    left_eye_x = head_left + 70
    right_eye_x = head_right - 70
    
    # Eye whites
    eye_white = (255, 255, 255) if not is_damaged else (230, 230, 230)
    draw.ellipse([left_eye_x - 20, eye_y - 15, left_eye_x + 20, eye_y + 15], 
                 fill=eye_white, outline=(100, 100, 100), width=1)
    draw.ellipse([right_eye_x - 20, eye_y - 15, right_eye_x + 20, eye_y + 15], 
                 fill=eye_white, outline=(100, 100, 100), width=1)
    
    # Irises
    iris_color = random.choice([(70, 130, 180), (139, 69, 19), (8, 8, 8)])
    draw.ellipse([left_eye_x - 10, eye_y - 10, left_eye_x + 10, eye_y + 10], 
                 fill=iris_color)
    draw.ellipse([right_eye_x - 10, eye_y - 10, right_eye_x + 10, eye_y + 10], 
                 fill=iris_color)
    
    # Pupils
    pupil_color = (0, 0, 0) if not is_damaged else (60, 60, 60)
    draw.ellipse([left_eye_x - 5, eye_y - 5, left_eye_x + 5, eye_y + 5], 
                 fill=pupil_color)
    draw.ellipse([right_eye_x - 5, eye_y - 5, right_eye_x + 5, eye_y + 5], 
                 fill=pupil_color)
    
    # Eye highlights
    if not is_damaged:
        draw.ellipse([left_eye_x - 2, eye_y - 3, left_eye_x + 2, eye_y - 1], 
                     fill=(255, 255, 255))
        draw.ellipse([right_eye_x - 2, eye_y - 3, right_eye_x + 2, eye_y - 1], 
                     fill=(255, 255, 255))
    
    # Eyebrows
    brow_color = tuple(int(c * 0.7) for c in hair_color)
    draw.arc([left_eye_x - 25, eye_y - 40, left_eye_x + 25, eye_y - 20], 
             0, 180, fill=brow_color, width=3)
    draw.arc([right_eye_x - 25, eye_y - 40, right_eye_x + 25, eye_y - 20], 
             0, 180, fill=brow_color, width=3)
    
    # Nose
    nose_y = eye_y + 40
    nose_color = tuple(int(c * 1.1) for c in base_skin) if not is_damaged else tuple(int(c * 0.9) for c in base_skin)
    nose_color = tuple(min(255, c) for c in nose_color)
    
    draw.polygon([(250, nose_y), (240, nose_y + 30), (260, nose_y + 30)], 
                 fill=nose_color, outline=(100, 50, 30), width=1)
    
    # Nostrils
    nostril_color = (100, 50, 30) if not is_damaged else (80, 30, 10)
    draw.ellipse([240, nose_y + 25, 245, nose_y + 32], fill=nostril_color)
    draw.ellipse([255, nose_y + 25, 260, nose_y + 32], fill=nostril_color)
    
    # Mouth
    mouth_y = nose_y + 50
    mouth_color = (200, 80, 80) if not is_damaged else (150, 40, 40)
    
    # Lips
    draw.ellipse([220, mouth_y, 280, mouth_y + 20], fill=mouth_color, outline=(150, 50, 50), width=1)
    # Mouth line
    draw.line([(220, mouth_y + 10), (280, mouth_y + 10)], fill=(100, 30, 30), width=2)
    
    # Cheeks (blush)
    if not is_damaged:
        blush_color = (255, 150, 150, 80)
        draw.ellipse([150, eye_y + 50, 190, eye_y + 100], fill=blush_color)
        draw.ellipse([310, eye_y + 50, 350, eye_y + 100], fill=blush_color)
    
    # Ears
    ear_color = tuple(int(c * 1.05) for c in base_skin)
    ear_color = tuple(min(255, c) for c in ear_color)
    
    draw.ellipse([100, head_top + 50, 130, head_top + 150], fill=ear_color, outline=(100, 50, 30), width=1)
    draw.ellipse([370, head_top + 50, 400, head_top + 150], fill=ear_color, outline=(100, 50, 30), width=1)
    
    # Neck
    neck_color = ear_color
    draw.rectangle([220, head_bottom - 20, 280, height - 50], fill=neck_color, outline=(100, 50, 30), width=1)
    
    # Add damage if needed
    if is_damaged:
        for _ in range(15):
            x = random.randint(150, 350)
            y = random.randint(120, 400)
            size = random.randint(15, 40)
            damage_color = (80, 40, 20, 120)
            draw.rectangle([x, y, x + size, y + size], fill=damage_color)
            # Scratch lines
            draw.line([(x, y), (x + size, y + size)], fill=(50, 20, 10), width=2)
    
    # Apply blur for smoothing
    if not is_damaged:
        img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    else:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Age progression effect
    if age_label:
        age_num = int(age_label)
        if age_num > 40:
            # Add wrinkles for older age
            wrinkle_color = (150, 100, 80, 100)
            num_wrinkles = (age_num - 40) // 10
            for _ in range(num_wrinkles):
                x = random.randint(150, 350)
                y = random.randint(100, 400)
                draw.line([(x, y), (x + random.randint(10, 30), y + random.randint(-5, 5))], 
                         fill=wrinkle_color, width=1)
    
    # Add text label
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    text = filename.replace('.jpg', '').replace('.jpeg', '').upper()
    text_color = (255, 255, 255) if is_damaged else (30, 30, 30)
    
    # Draw text with background
    text_y = height - 80
    draw.rectangle([10, text_y - 25, width - 10, text_y + 25], fill=(0, 0, 0, 180))
    
    # Center text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    
    draw.text((text_x, text_y - 15), text, fill=text_color, font=font)
    
    if age_label:
        age_text = f"Age: {age_label}"
        age_bbox = draw.textbbox((0, 0), age_text, font=font)
        age_width = age_bbox[2] - age_bbox[0]
        age_x = (width - age_width) // 2
        draw.text((age_x, height - 50), age_text, fill=text_color, font=font)
    
    img.save(f"frontend/sample_images/{filename}")
    return filename

# Create sample images directory
sample_dir = "frontend/sample_images"
os.makedirs(sample_dir, exist_ok=True)

# Generate realistic samples
print("[*] Generating realistic AI human face images...")

for i in range(1, 6):
    create_realistic_face(f"person_{i}_damaged.jpg", is_damaged=True, seed=i)
    print(f"  ✓ person_{i}_damaged.jpg (damaged)")
    
    create_realistic_face(f"person_{i}_restored.jpg", is_damaged=False, seed=i)
    print(f"  ✓ person_{i}_restored.jpg (restored)")

print("\n[*] Generating age progression series...")
ages = [18, 25, 35, 45, 55, 65, 75, 80]
for age in ages:
    create_realistic_face(f"age_{age}.jpg", age_label=str(age), is_damaged=False, seed=100 + int(age))
    print(f"  ✓ age_{age}.jpg")

print(f"\n[✓] All realistic human face images generated!")
