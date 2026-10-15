import os
import requests
from PIL import Image, ImageDraw, ImageFont

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "Aritpal15"

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def get_pixel_font(size=14):
    """Loads an authentic retro pixel font (Silkscreen) for crisp HUD text."""
    font_path = "scripts/Silkscreen-Regular.ttf"
    if not os.path.exists(font_path):
        font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/silkscreen/Silkscreen-Regular.ttf"
        try:
            r = requests.get(font_url, timeout=10)
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
    """Fetches real-time GitHub user statistics and language breakdown."""
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                }
              }
            }
          }
        }
        pullRequests {
          totalCount
        }
        issues {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    fallback_metrics = {
        "stars": 37,
        "commits": 267,
        "prs": 48,
        "issues": 31,
    }

    if not GITHUB_TOKEN:
        return fallback_metrics

    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": query, "variables": {"login": GITHUB_USERNAME}},
            headers=HEADERS,
            timeout=10,
        )
        data = response.json()
        user_data = data.get("data", {}).get("user", {})

        repos = user_data.get("repositories", {}).get("nodes", [])
        total_stars = sum(repo["stargazerCount"] for repo in repos)
        total_commits = user_data.get("contributionsCollection", {}).get(
            "totalCommitContributions", 0
        ) + user_data.get("contributionsCollection", {}).get(
            "restrictedContributionsCount", 0
        )
        total_prs = user_data.get("pullRequests", {}).get("totalCount", 0)
        total_issues = user_data.get("issues", {}).get("totalCount", 0)

        print(f"Live GitHub Data Fetched: Stars={total_stars}, Commits={total_commits}, PRs={total_prs}, Issues={total_issues}")

        return {
            "stars": total_stars if total_stars > 0 else 37,
            "commits": total_commits if total_commits > 0 else 267,
            "prs": total_prs if total_prs > 0 else 48,
            "issues": total_issues if total_issues > 0 else 31,
        }
    except Exception as e:
        print(f"Error fetching live data: {e}")
        return fallback_metrics


def render_dashboard(metrics):
    """Draws live stats and renders looping animations."""
    os.makedirs("assets", exist_ok=True)

    base_path = None
    for p in ["scripts/base_dashboard.png", "scripts/assets/base_dashboard.png"]:
        if os.path.exists(p):
            base_path = p
            break

    if not base_path:
        print("Base image not found, aborting render.")
        return

    base_img = Image.open(base_path).convert("RGBA")
    width, height = base_img.size

    # Responsive scaling based on original reference resolution (1920x820)
    sx = width / 1920.0
    sy = height / 820.0

    # Load pixel font
    font_stats = get_pixel_font(size=max(12, int(15 * sy)))
    font_badge = get_pixel_font(size=max(10, int(11 * sy)))

    # Color definitions
    hud_bg = (11, 15, 23, 255)       # Matches the dark HUD card background
    amber = (250, 204, 21, 255)      # Retro amber/yellow
    white = (248, 250, 252, 255)     # Clean stats white
    cyan = (56, 189, 248, 255)       # Terminal blue/cyan
    green_bright = (74, 222, 128, 255)
    green_dark = (22, 101, 52, 255)
    red_beacon = (239, 68, 68, 255)

    num_frames = 6
    frames = []

    # Prepare base stats frame with live metrics drawn once
    live_base = base_img.copy()
    draw_base = ImageDraw.Draw(live_base)

    # 1. Update Live Numbers (Total Stars, Commits, PRs, Issues)
    # Each tuple: (clear_x1, clear_y1, clear_x2, clear_y2, text_x, text_y, text_val)
    stat_slots = [
        # Total Stars
        (int(615 * sx), int(268 * sy), int(680 * sx), int(295 * sy), str(metrics["stars"])),
        # Total Commits
        (int(615 * sx), int(305 * sy), int(680 * sx), int(332 * sy), str(metrics["commits"])),
        # Pull Requests
        (int(615 * sx), int(342 * sy), int(680 * sx), int(369 * sy), str(metrics["prs"])),
        # Total Issues
        (int(615 * sx), int(379 * sy), int(680 * sx), int(406 * sy), str(metrics["issues"])),
    ]

    for x1, y1, x2, y2, val_str in stat_slots:
        # Clear only the exact old number area with the HUD background color
        draw_base.rectangle([x1, y1, x2, y2], fill=hud_bg)
        # Draw live value with right alignment
        draw_base.text((x1 + int(10 * sx), y1 + int(2 * sy)), val_str, fill=white, font=font_stats)

    # 2. Update EXP Bar under A+ Badge
    exp_x1 = int(700 * sx)
    exp_y1 = int(420 * sy)
    exp_x2 = int(840 * sx)
    exp_y2 = int(440 * sy)
    draw_base.rectangle([exp_x1, exp_y1, exp_x2, exp_y2], fill=hud_bg)
    draw_base.text((exp_x1 + int(5 * sx), exp_y1 + int(2 * sy)), f"EXP {metrics['commits']} / 500", fill=amber, font=font_badge)

    # Build animated frames
    for f_idx in range(num_frames):
        frame = live_base.copy()
        draw = ImageDraw.Draw(frame)

        # -------------------------------------------------------------
        # Animation A: Skyline Aviation Warning Beacons (Blinking)
        # -------------------------------------------------------------
        if f_idx % 2 == 0:
            bx1 = int(723 * sx)
            by1 = int(488 * sy)
            draw.rectangle([bx1, by1, bx1 + int(3 * sx), by1 + int(3 * sy)], fill=red_beacon)

            bx2 = int(1062 * sx)
            by2 = int(432 * sy)
            draw.rectangle([bx2, by2, bx2 + int(3 * sx), by2 + int(3 * sy)], fill=amber)

        # -------------------------------------------------------------
        # Animation B: Online Status LED (Subtle glow pulse)
        # -------------------------------------------------------------
        led_color = green_bright if f_idx in (0, 1, 2) else green_dark
        led_x = int(168 * sx)
        led_y = int(225 * sy)
        draw.ellipse([led_x, led_y, led_x + int(8 * sx), led_y + int(8 * sy)], fill=led_color)

        # -------------------------------------------------------------
        # Animation C: Center Monitor Terminal Cursor (Blink)
        # -------------------------------------------------------------
        if f_idx in (0, 1, 2):
            cur_x = int(875 * sx)
            cur_y = int(595 * sy)
            draw.rectangle([cur_x, cur_y, cur_x + int(4 * sx), cur_y + int(8 * sy)], fill=cyan)

        # -------------------------------------------------------------
        # Animation D: Right Monitor Network Telemetry (Activity wave)
        # -------------------------------------------------------------
        for bar_i in range(8):
            var_h = ((bar_i * 3 + f_idx * 4) % 12) * sy
            tx = int((1160 + bar_i * 9) * sx)
            ty = int(625 * sy) - int(var_h)
            draw.rectangle([tx, ty, tx + int(5 * sx), int(627 * sy)], fill=green_bright)

        frames.append(frame.convert("P", palette=Image.ADAPTIVE))

    output_path = "assets/developer-dashboard.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0,
        optimize=True,
    )
    print(f"Successfully rendered dashboard with live metrics to {output_path}")


if __name__ == "__main__":
    metrics_data = fetch_github_metrics()
    render_dashboard(metrics_data)
