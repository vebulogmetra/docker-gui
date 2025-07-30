#!/usr/bin/env python3
"""
Modern icon generator for Docker GUI
Creates a professional icon using PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Installing...")
    import subprocess
    subprocess.run(["uv", "add", "pillow"], check=True)
    from PIL import Image, ImageDraw, ImageFont

def create_docker_gui_icon():
    """Create a modern Docker GUI icon"""
    
    # Create a 256x256 image with a gradient background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (Docker blue to darker blue)
    for y in range(size):
        # Gradient from top to bottom
        r = int(0 + (y / size) * 20)
        g = int(120 + (y / size) * 30)
        b = int(215 + (y / size) * 40)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Draw a modern container shape with rounded corners
    container_width = 160
    container_height = 100
    x = (size - container_width) // 2
    y = (size - container_height) // 2
    
    # Container body with rounded corners
    corner_radius = 15
    
    # Main container body
    draw.rounded_rectangle(
        [x, y, x + container_width, y + container_height],
        radius=corner_radius,
        fill=(255, 255, 255, 255),
        outline=(200, 200, 200, 255),
        width=3
    )
    
    # Container lid with rounded corners
    lid_height = 25
    lid_y = y - lid_height
    draw.rounded_rectangle(
        [x - 15, lid_y, x + container_width + 15, y],
        radius=corner_radius,
        fill=(240, 240, 240, 255),
        outline=(200, 200, 200, 255),
        width=2
    )
    
    # Draw modern GUI elements (lines representing interface)
    line_y_start = y + 25
    line_spacing = 12
    
    for i in range(4):
        line_y = line_y_start + i * line_spacing
        line_length = container_width - 30
        line_x = x + 15
        
        # Varying line lengths for more realistic look
        if i == 0:
            line_length = int(line_length * 0.8)
        elif i == 1:
            line_length = int(line_length * 0.9)
        elif i == 2:
            line_length = int(line_length * 0.7)
        else:
            line_length = int(line_length * 0.6)
        
        draw.line(
            [line_x, line_y, line_x + line_length, line_y],
            fill=(100, 100, 100, 255),
            width=2
        )
    
    # Add a modern Docker whale symbol
    whale_size = 35
    whale_x = x + container_width - whale_size - 15
    whale_y = y + 10
    
    # Whale body (ellipse)
    draw.ellipse(
        [whale_x, whale_y, whale_x + whale_size, whale_y + whale_size//2],
        fill=(0, 150, 136, 255),
        outline=(0, 100, 86, 255),
        width=2
    )
    
    # Whale tail (modern triangular shape)
    tail_points = [
        (whale_x + whale_size//2, whale_y + whale_size//2),
        (whale_x + whale_size + 8, whale_y + 8),
        (whale_x + whale_size + 8, whale_y + whale_size//2 - 8)
    ]
    draw.polygon(tail_points, fill=(0, 150, 136, 255), outline=(0, 100, 86, 255))
    
    # Add some small circles representing containers
    circle_radius = 4
    circle_y = y + container_height + 15
    
    # Three small circles
    for i in range(3):
        circle_x = x + 30 + i * 25
        draw.ellipse(
            [circle_x - circle_radius, circle_y - circle_radius,
             circle_x + circle_radius, circle_y + circle_radius],
            fill=(0, 120, 215, 255),
            outline=(0, 80, 180, 255),
            width=1
        )
    
    # Add a subtle shadow effect
    shadow_offset = 3
    shadow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    
    # Create shadow for container
    shadow_draw.rounded_rectangle(
        [x + shadow_offset, y + shadow_offset, 
         x + container_width + shadow_offset, y + container_height + shadow_offset],
        radius=corner_radius,
        fill=(0, 0, 0, 30)
    )
    
    # Composite shadow with main image
    img = Image.alpha_composite(shadow_img, img)
    
    # Save the icon
    icon_path = "icon.png"
    img.save(icon_path, "PNG", optimize=True)
    print(f"✅ Modern icon created: {icon_path}")
    
    return icon_path

if __name__ == "__main__":
    create_docker_gui_icon() 