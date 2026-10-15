import os
import requests
from PIL import Image, ImageDraw, ImageFont

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "Aritpal15"

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def get_pixel_font(size=14):
    """Downloads and loads an authentic pixel font (Silkscreen) for crisp HUD rendering."""
    font_path = "scripts/Silkscreen-Regular.ttf"
    if not os.path.exists(font_path):
        font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/silkscreen/Silkscreen-Regular.ttf"
        try:
            r = requests.get(font_url, timeout=10)
            if r.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print(f"Could not download Silkscreen font: {e}")

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
        "languages": [
            ("Python", 49.32),
            ("JavaScript", 36.08),
            ("TypeScript", 8.20),
            ("Bash/Linux", 5.00),
        ],
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

        lang_sizes = {}
        for repo in repos:
            for edge in repo.get("languages", {}).get("edges", []):
                name = edge["node"]["name"]
                lang_sizes[name] = lang_sizes.get(name, 0) + edge["size"]

        total_size = sum(lang_sizes.values()) or 1
        sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)[:4]
        formatted_langs = [
            (name, round((size / total_size) * 100, 2))
            for name, size in sorted_langs
        ]

        return {
            "stars": total_stars if total_stars > 0 else 37,
            "commits": total_commits if total_commits > 0 else 267,
            "prs": total_prs if total_prs > 0 else 48,
            "issues": total_issues if total_issues > 0 else 31,
            "languages": formatted_langs if formatted_langs else fallback_metrics["languages"],
        }
    except Exception as e:
        print(f"Error fetching live data: {e}")
        return fallback_metrics


def render_dashboard(metrics):
    """Generates clean looping animations without destructive shape overlays."""
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

    # Responsive coordinate scale relative to the base reference
    sx = width / 1920.0
    sy = height / 820.0

    # Clean color palette
    cyan = (56, 189, 248, 255)
    green_bright = (74, 222, 128, 255)
    green_dark = (22, 101, 52, 255)
    amber = (250, 204, 21, 255)
    red_beacon = (239, 68, 68, 255)

    num_frames = 6
    frames = []

    for f_idx in range(num_frames):
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame)

        # -----------------------------------------------------------------
        # 1. Skyline Beacon Tower Lights (Subtle 2px city twinkle)
        # -----------------------------------------------------------------
        if f_idx % 2 == 0:
            bx1 = int(723 * sx)
            by1 = int(488 * sy)
            draw.rectangle([bx1, by1, bx1 + int(3 * sx), by1 + int(3 * sy)], fill=red_beacon)

            bx2 = int(1062 * sx)
            by2 = int(432 * sy)
            draw.rectangle([bx2, by2, bx2 + int(3 * sx), by2 + int(3 * sy)], fill=amber)

        # -----------------------------------------------------------------
        # 2. Left Status LED Pulse (Actively Seeking Roles)
        # -----------------------------------------------------------------
        led_color = green_bright if f_idx in (0, 1, 2) else green_dark
        led_x = int(168 * sx)
        led_y = int(225 * sy)
        draw.ellipse([led_x, led_y, led_x + int(8 * sx), led_y + int(8 * sy)], fill=led_color)

        # -----------------------------------------------------------------
        # 3. Center Monitor: Blinking Terminal Cursor in IDE
        # -----------------------------------------------------------------
        if f_idx in (0, 1, 2):
            cur_x = int(875 * sx)
            cur_y = int(595 * sy)
            draw.rectangle([cur_x, cur_y, cur_x + int(4 * sx), cur_y + int(8 * sy)], fill=cyan)

        # -----------------------------------------------------------------
        # 4. Right Monitor: Active Telemetry Network Activity
        # -----------------------------------------------------------------
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
    print(f"Clean dashboard generated at {output_path}")


if __name__ == "__main__":
    metrics_data = fetch_github_metrics()
    render_dashboard(metrics_data)
