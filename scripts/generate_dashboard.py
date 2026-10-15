import os
from PIL import Image, ImageDraw

def render_clean_animated_dashboard():
    os.makedirs("assets", exist_ok=True)
    base_file = "scripts/base_dashboard.png" if os.path.exists("scripts/base_dashboard.png") else "scripts/assets/base_dashboard.png"
    
    if not os.path.exists(base_file):
        print("ERROR: Base image not found!")
        return

    base_img = Image.open(base_file).convert("RGBA")
    w, h = base_img.size

    # Base scale factors for 2752 x 1536
    sx = w / 2752.0
    sy = h / 1536.0

    frames = []
    num_frames = 4

    cyan = (56, 189, 248, 255)
    red_beacon = (239, 68, 68, 255)
    amber_beacon = (250, 204, 21, 255)

    for i in range(num_frames):
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Subtle Aviation Warning Beacons on distant skyline towers (Blink)
        if i % 2 == 0:
            # Tower 1 Beacon
            b1_x = int(1030 * sx)
            b1_y = int(870 * sy)
            draw.rectangle([b1_x, b1_y, b1_x + int(4 * sx), b1_y + int(4 * sy)], fill=red_beacon)
            
            # Tower 2 Beacon
            b2_x = int(1518 * sx)
            b2_y = int(775 * sy)
            draw.rectangle([b2_x, b2_y, b2_x + int(4 * sx), b2_y + int(4 * sy)], fill=amber_beacon)

        # 2. Terminal Cursor Blink inside center IDE screen
        if i in (0, 1):
            cur_x = int(1335 * sx)
            cur_y = int(1095 * sy)
            draw.rectangle([cur_x, cur_y, cur_x + int(5 * sx), cur_y + int(12 * sy)], fill=cyan)

        # Convert frame cleanly to adaptive palette GIF
        frames.append(frame.convert("P", palette=Image.ADAPTIVE))

    output_path = "assets/developer-dashboard.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=450,
        loop=0,
        optimize=True
    )
    print(f"Clean animated dashboard successfully generated at {output_path}")

if __name__ == "__main__":
    render_clean_animated_dashboard()
