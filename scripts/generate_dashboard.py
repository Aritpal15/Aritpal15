import os
import requests
from PIL import Image, ImageDraw, ImageFont

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "Aritpal15"

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


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
        print(f"Error fetching live data, using fallback: {e}")
        return fallback_metrics


def render_dashboard(metrics):
    """Animates scene elements and overlays live metrics onto frames."""
    os.makedirs("assets", exist_ok=True)

    base_path = None
    for p in ["scripts/base_dashboard.png", "scripts/assets/base_dashboard.png"]:
        if os.path.exists(p):
            base_path = p
            break

    if not base_path:
        print("Base image not found, generating template canvas.")
        base_img = Image.new("RGBA", (1920, 820), (11, 14, 20, 255))
    else:
        base_img = Image.open(base_path).convert("RGBA")

    width, height = base_img.size
    sx = width / 1920.0
    sy = height / 820.0

    # Color Palette
    amber = (250, 204, 21, 255)
    amber_soft = (252, 211, 77, 180)
    cyan = (56, 189, 248, 255)
    green_bright = (74, 222, 128, 255)
    green_dim = (34, 197, 94, 80)
    white = (248, 250, 252, 255)
    hud_bg = (11, 14, 20, 255)
    dark_bar = (30, 41, 59, 255)
    red_beacon = (239, 68, 68, 255)

    num_frames = 6
    frames = []

    for f_idx in range(num_frames):
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame, "RGBA")

        # ---------------------------------------------------------
        # 1. ANIMATION: Skyline Tower Beacon Lights (Blinking)
        # ---------------------------------------------------------
        if f_idx % 2 == 0:
            beacon_x = int(1060 * sx)
            beacon_y = int(430 * sy)
            draw.rectangle([beacon_x, beacon_y, beacon_x + int(3 * sx), beacon_y + int(3 * sy)], fill=red_beacon)
            beacon_x2 = int(720 * sx)
            beacon_y2 = int(480 * sy)
            draw.rectangle([beacon_x2, beacon_y2, beacon_x2 + int(3 * sx), beacon_y2 + int(3 * sy)], fill=amber)

        # ---------------------------------------------------------
        # 2. ANIMATION: Sleeping Cat Breathing (Subtle 1-2px rise/fall)
        # ---------------------------------------------------------
        cat_offset = 1 if f_idx in (1, 2) else 0
        cat_x1 = int(1400 * sx)
        cat_y1 = int(645 * sy) + int(cat_offset * sy)
        cat_x2 = int(1570 * sx)
        cat_y2 = int(660 * sy) + int(cat_offset * sy)
        draw.rectangle([cat_x1, cat_y1, cat_x2, cat_y2], fill=(245, 230, 211, 40))

        # ---------------------------------------------------------
        # 3. ANIMATION: Warm Desk Lamp Ambient Luminescence
        # ---------------------------------------------------------
        lamp_alpha = 35 if f_idx % 2 == 0 else 55
        lamp_x1 = int(1500 * sx)
        lamp_y1 = int(680 * sy)
        lamp_x2 = int(1850 * sx)
        lamp_y2 = int(770 * sy)
        draw.ellipse([lamp_x1, lamp_y1, lamp_x2, lamp_y2], fill=(251, 191, 36, lamp_alpha))

        # ---------------------------------------------------------
        # 4. ANIMATION: Triple Monitor Glow & Active Terminal Cursor
        # ---------------------------------------------------------
        # Left IDE monitor cursor blink
        if f_idx in (0, 1, 2):
            cur_x = int(880 * sx)
            cur_y = int(595 * sy)
            draw.rectangle([cur_x, cur_y, cur_x + int(5 * sx), cur_y + int(9 * sy)], fill=cyan)

        # Right Telemetry monitor live graph fluctuation
        graph_shift = (f_idx % 3) * 2
        for gx in range(0, 12):
            bar_h = 10 + ((gx * 7 + f_idx * 5) % 18)
            bx = int((1180 + gx * 10) * sx)
            by = int(630 * sy) - bar_h
            draw.rectangle([bx, by, bx + int(6 * sx), int(632 * sy)], fill=(34, 197, 94, 220))

        # ---------------------------------------------------------
        # 5. HUD: Profile Badge (Updated Fresher Title)
        # ---------------------------------------------------------
        title_box = [int(150 * sx), int(140 * sy), int(330 * sx), int(195 * sy)]
        draw.rectangle(title_box, fill=hud_bg)
        draw.text((int(152 * sx), int(142 * sy)), "ASPIRING CLOUD &", fill=amber)
        draw.text((int(152 * sx), int(158 * sy)), "DEVOPS ENGINEER", fill=amber)

        # Pulsing Seeking Roles LED
        led_color = green_bright if f_idx % 2 == 0 else green_dim
        draw.text((int(152 * sx), int(178 * sy)), "* SEEKING ROLES", fill=led_color)

        # ---------------------------------------------------------
        # 6. HUD: GitHub Live Statistics (Dynamic overwrite)
        # ---------------------------------------------------------
        stats_val_box = [int(615 * sx), int(160 * sy), int(720 * sx), int(325 * sy)]
        draw.rectangle(stats_val_box, fill=hud_bg)
        draw.text((int(630 * sx), int(168 * sy)), f"{metrics['stars']:>4}", fill=amber)
        draw.text((int(630 * sx), int(204 * sy)), f"{metrics['commits']:>4}", fill=cyan)
        draw.text((int(630 * sx), int(240 * sy)), f"{metrics['prs']:>4}", fill=green_bright)
        draw.text((int(630 * sx), int(276 * sy)), f"{metrics['issues']:>4}", fill=white)

        # ---------------------------------------------------------
        # 7. HUD: Programming Languages (Dynamic overwrite)
        # ---------------------------------------------------------
        lang_val_box = [int(1120 * sx), int(195 * sy), int(1520 * sx), int(335 * sy)]
        draw.rectangle(lang_val_box, fill=hud_bg)

        sy_lang = int(198 * sy)
        for name, pct in metrics["languages"][:4]:
            draw.text((int(1125 * sx), sy_lang), f"{name:<11} {pct:>5.1f}%", fill=cyan)
            # Dynamic block meter
            filled_blocks = int(pct // 10)
            for b in range(10):
                b_color = amber if (name == "Python" and b < filled_blocks) else (cyan if b < filled_blocks else dark_bar)
                bx_pos = int((1360 + b * 14) * sx)
                draw.rectangle(
                    [bx_pos, sy_lang + int(2 * sy), bx_pos + int(9 * sx), sy_lang + int(11 * sy)],
                    fill=b_color,
                )
            sy_lang += int(30 * sy)

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
    print(f"Successfully generated animated dashboard at {output_path}")


if __name__ == "__main__":
    metrics_data = fetch_github_metrics()
    render_dashboard(metrics_data)
