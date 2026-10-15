import os
import requests
from PIL import Image, ImageDraw, ImageFont

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "Aritpal15"

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_font(size):
    font_path = "scripts/Silkscreen-Regular.ttf"
    if not os.path.exists(font_path):
        url = "https://raw.githubusercontent.com/google/fonts/main/ofl/silkscreen/Silkscreen-Regular.ttf"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print(f"Font download notice: {e}")

    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def fetch_github_metrics():
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes { stargazerCount }
        }
        pullRequests { totalCount }
        issues { totalCount }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    fallback = {"stars": 37, "commits": 275, "prs": 48, "issues": 31}
    if not GITHUB_TOKEN:
        return fallback

    try:
        res = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"login": GITHUB_USERNAME}}, headers=HEADERS, timeout=10)
        data = res.json().get("data", {}).get("user", {})
        repos = data.get("repositories", {}).get("nodes", [])
        stars = sum(r["stargazerCount"] for r in repos)
        commits = data.get("contributionsCollection", {}).get("totalCommitContributions", 0) + data.get("contributionsCollection", {}).get("restrictedContributionsCount", 0)
        prs = data.get("pullRequests", {}).get("totalCount", 0)
        issues = data.get("issues", {}).get("totalCount", 0)

        print(f"==> LIVE GITHUB DATA: Stars={stars}, Commits={commits}, PRs={prs}, Issues={issues}")
        return {
            "stars": stars if stars > 0 else 37,
            "commits": commits if commits > 0 else 275,
            "prs": prs if prs > 0 else 48,
            "issues": issues if issues > 0 else 31
        }
    except Exception as e:
        print(f"API Error: {e}")
        return fallback

def render_dashboard(metrics):
    os.makedirs("assets", exist_ok=True)
    base_file = "scripts/base_dashboard.png" if os.path.exists("scripts/base_dashboard.png") else "scripts/assets/base_dashboard.png"
    if not os.path.exists(base_file):
        print("ERROR: Base image not found!")
        return

    base_img = Image.open(base_file).convert("RGBA")
    w, h = base_img.size
    print(f"==> EXACT BASE IMAGE DIMENSIONS: Width={w}, Height={h}")

    # Standard palette colors
    bg_color = (12, 17, 26, 255)
    text_white = (248, 250, 252, 255)
    amber = (250, 204, 21, 255)
    cyan = (56, 189, 248, 255)
    green_bright = (74, 222, 128, 255)
    dark_screen = (8, 16, 24, 255)

    font_num = get_font(max(11, int(h * 0.024)))
    font_small = get_font(max(9, int(h * 0.016)))

    # Calculate actual visual box anchors
    # Total Stars row center is around 24.5% of total height
    row_starts = [
        int(h * 0.235),  # Stars
        int(h * 0.282),  # Commits
        int(h * 0.330),  # PRs
        int(h * 0.378)   # Issues
    ]
    box_x1 = int(w * 0.320)
    box_x2 = int(w * 0.365)
    box_h = int(h * 0.032)

    cleaned_base = base_img.copy()
    draw_clean = ImageDraw.Draw(cleaned_base)

    values = [str(metrics["stars"]), str(metrics["commits"]), str(metrics["prs"]), str(metrics["issues"])]

    for y_top, val in zip(row_starts, values):
        draw_clean.rectangle([box_x1, y_top, box_x2, y_top + box_h], fill=bg_color)
        draw_clean.text((box_x1 + 4, y_top + 1), val, fill=text_white, font=font_num)

    # EXP Banner under badge
    exp_y = int(h * 0.412)
    exp_x1 = int(w * 0.380)
    exp_x2 = int(w * 0.445)
    draw_clean.rectangle([exp_x1, exp_y, exp_x2, exp_y + int(h * 0.024)], fill=bg_color)
    draw_clean.text((exp_x1 + 4, exp_y + 1), f"EXP {metrics['commits']}/500", fill=amber, font=font_small)

    frames = []
    num_frames = 4

    for i in range(num_frames):
        f = cleaned_base.copy()
        d = ImageDraw.Draw(f)

        # 1. Aviation Skyline Beacons (Blink)
        if i % 2 == 0:
            d.rectangle([int(w * 0.375), int(h * 0.590), int(w * 0.375) + 3, int(h * 0.590) + 3], fill=(239, 68, 68, 255))
            d.rectangle([int(w * 0.552), int(h * 0.525), int(w * 0.552) + 3, int(h * 0.525) + 3], fill=amber)

        # 2. Center Monitor Terminal Cursor (Blink)
        if i in (0, 1):
            cx = int(w * 0.485)
            cy = int(h * 0.708)
            d.rectangle([cx, cy, cx + 4, cy + 8], fill=cyan)

        # 3. Right Monitor Activity Equalizer
        rx_start = int(w * 0.578)
        rx_end = int(w * 0.655)
        ry_bottom = int(h * 0.760)
        d.rectangle([rx_start, int(h * 0.725), rx_end, ry_bottom], fill=dark_screen)

        bars = 10
        bw = (rx_end - rx_start) // bars
        heights = [
            [6, 14, 20, 10, 16, 22, 12, 18, 24, 14],
            [12, 20, 14, 18, 10, 16, 24, 12, 16, 20],
            [18, 10, 24, 14, 22, 12, 16, 20, 10, 16],
            [14, 16, 10, 22, 14, 24, 18, 14, 20, 12]
        ][i]

        for b_idx, bh in enumerate(heights):
            bx = rx_start + (b_idx * bw)
            d.rectangle([bx, ry_bottom - bh, bx + bw - 2, ry_bottom], fill=green_bright)

        frames.append(f.convert("P", palette=Image.ADAPTIVE))

    output_path = "assets/developer-dashboard.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0,
        optimize=True
    )
    print(f"Generated new GIF successfully at {output_path}")

if __name__ == "__main__":
    data = fetch_github_metrics()
    render_dashboard(data)
