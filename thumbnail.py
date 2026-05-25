#!/usr/bin/env python3
"""Generate a YouTube thumbnail by asking Claude to design an SVG."""

import argparse
import os
import re
import sys
from pathlib import Path

import anthropic
import resvg_py
from dotenv import load_dotenv
from github import Github

load_dotenv()

COMPANY_NAME = os.getenv("COMPANY_NAME", "")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "")
COMPANY_URL = os.getenv("COMPANY_URL", "")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

DEFAULT_VIBE = (
    "bold YouTube tutorial style; deep purple gradient background (#3a1273 to #5b1ea8 to #2a0d5c); "
    "primary title text in huge bright yellow (#ffe14d) Impact font; secondary text in white Impact font; "
    "a short orange (#ff6a00) pill/tag label at top-left (e.g. 'CLAUDE CODE'); "
    "the last 1-2 lines of the title share ONE single solid yellow (#ffe14d) skewed rectangle background — "
    "do NOT split them into separate rects; use a single <rect> with skewX(-10) tall enough to cover all "
    "highlighted lines, with dark purple (#2a0d5c) text on top — rect only has skewX, text has NO transform, "
    "rect width must be at least font-size × char-count × 0.85 + abs(tan(10°) × rect_bottom_y) + 80px; "
    "subtle diagonal yellow stripe accents in background (low opacity ~0.07); "
    "large glowing yellow radial burst circle behind robot on right half; "
    "terminal/code decoration lines at bottom-left in light purple monospace font; "
    "solid dark footer bar (#1a0640) at the very bottom (height ~48px) with company name in bold yellow on left, "
    "website URL in white center-left, email in white right-aligned — all clearly readable at 18-20px font size; "
    "Claude-style robot on right half with glowing cyan eyes; high-contrast, click-worthy"
)

SYSTEM_PROMPT = """You are a senior graphic designer creating YouTube video thumbnails.

Output requirements:
- Respond with ONLY a single SVG document, nothing else.
- Start your response with <svg and end with </svg>.
- No code fences, no preamble, no commentary.
- Use viewBox="0 0 1280 720" with width="1280" height="720" (16:9 YouTube thumbnail).
- Embed everything inline. No external images, fonts, scripts, or hrefs.
- Use only system sans-serif font stacks like "Impact, Arial Black, sans-serif" or "Helvetica Neue, Arial, sans-serif".
- Do not use emoji or decorative Unicode glyphs (e.g. 🔑, ★, ▮, ✓, ➜). The renderer has no glyphs for them and they appear as "?????". Draw any icons, stars, cursors, or arrows as SVG <path>, <rect>, <circle>, or <polygon> elements instead.
- Size every text container generously. SVG <text> never wraps or auto-shrinks; if a pill or badge is narrower than its text, the text overflows and visibly clips. For bold sans-serif, allow at least font-size × character-count × 0.85 of width, plus 40px of horizontal padding, plus space for any leading icon. When in doubt, oversize the container — empty padding looks fine, clipped text looks broken.
- Avoid decorative pills, badges, tags, or sticker labels longer than 8 characters. They are the most common source of clipped text. If you want a label, keep it to a single short word (e.g. "NEW", "LIVE", "TUTORIAL") or omit it entirely.
- Every <text> element and its container must fit inside the 1280×720 viewBox. Do not place text or rectangles whose right edge would exceed x=1280 or whose bottom edge would exceed y=720.
- Skewed highlight rectangles (the yellow background behind key words): apply skewX ONLY to the <rect>, NEVER to the <text>. The text sits on top with no transform. When highlighting multiple lines, use ONE single tall rect that covers all of them — do not use a separate rect per line. The rect must be wide enough to fully cover all text even after the skew shift — add at least (abs(tan(skewAngle)) × rect_bottom_y + 80px) of extra width beyond the widest text line.
- Branding footer: always render a solid dark rectangle (#1a0640 or similar) spanning the full width at the very bottom of the canvas (y=672, height=48). Inside it place: company name in bold yellow (~20px) at left, website URL in white (~18px) center-left, email address in white (~18px) right-aligned. No opacity fade — text must be fully opaque and clearly legible.

Design principles:
- Bold, high-contrast composition that reads clearly as a tiny mobile thumbnail.
- Title text huge (90-150pt), tight tracking, heavy weight, with a stroke or shadow for legibility.
- One strong focal point, one or two supporting visual elements (shapes, icons drawn as paths).
- Use gradients, layered shapes, and accent colors to create depth — avoid flat one-color backgrounds.
- Avoid clutter. If the design feels busy, remove something.
- Never include the words "YouTube" or fake play buttons.
- Never draw lightning bolts.

Robot character (required):
- Every thumbnail must include a friendly Claude-style robot as the main visual focal point, positioned on the right half of the canvas.
- Build the robot from SVG primitives: <rect>, <circle>, <ellipse>, <polygon>, <path>, <line>. No bitmaps or external references.
- Robot anatomy: rounded rectangular head with glowing rectangular eyes (bright cyan or matching accent color), an antenna (line + circle) on top, ear panels on the sides of the head, a mouth grille of short horizontal lines, a rectangular body with a chest screen showing code-like lines, two arms with rounded ends, and two legs with feet.
- Add an orange circular AI badge on the chest labeled "AI" in white bold text.
- Eyes must glow: use a radial gradient or bright fill to give them a lit-up look.
- The robot should feel tech-forward and friendly, not menacing.
"""


def generate_svg(client: anthropic.Anthropic, title: str, vibe: str) -> str:
    branding_lines = []
    if COMPANY_NAME:
        branding_lines.append(f"Company: {COMPANY_NAME}")
    if COMPANY_URL:
        branding_lines.append(f"Website: {COMPANY_URL}")
    if COMPANY_EMAIL:
        branding_lines.append(f"Email: {COMPANY_EMAIL}")
    branding_block = ("\n\nBranding (REQUIRED — include all of the following as a small watermark or footer, visible but not distracting):\n" + "\n".join(branding_lines)) if branding_lines else ""

    user_prompt = (
        f"Create a YouTube thumbnail SVG.\n\n"
        f"Title: {title}\n"
        f"Vibe / topic / style direction: {vibe}"
        f"{branding_block}\n\n"
        f"Design a thumbnail that would make someone click. Output the complete SVG now."
    )

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        message = stream.get_final_message()

    raw = "".join(b.text for b in message.content if b.type == "text")
    match = re.search(r"<svg[\s\S]*?</svg>", raw)
    if not match:
        raise RuntimeError(f"No <svg>…</svg> found in model response.\nFirst 500 chars:\n{raw[:500]}")
    return match.group(0)


def render_png(svg: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg, width=1280, height=720)
    output_path.write_bytes(bytes(png_bytes))


def upload_to_github(file_path: Path, repo_path: str | None = None) -> str | None:
    if not all([GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO]):
        return None
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPO}")
    dest = repo_path or f"thumbnails/{file_path.name}"
    content = file_path.read_bytes()
    try:
        existing = repo.get_contents(dest, ref=GITHUB_BRANCH)
        repo.update_file(dest, f"Update {file_path.name}", content, existing.sha, branch=GITHUB_BRANCH)
    except Exception:
        repo.create_file(dest, f"Add {file_path.name}", content, branch=GITHUB_BRANCH)
    return f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{dest}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a YouTube thumbnail with Claude.")
    parser.add_argument("--title", required=True, help="Main title text on the thumbnail")
    parser.add_argument("--vibe", default=DEFAULT_VIBE, help="Topic, mood, and style direction (default: brand vibe)")
    parser.add_argument("--output", default="outputs/thumbnail.png", help="Output PNG path")
    parser.add_argument("--save-svg", action="store_true", help="Also save the raw SVG alongside the PNG")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Add it to the .env file alongside COMPANY_NAME, COMPANY_EMAIL, and COMPANY_URL.")

    client = anthropic.Anthropic()
    print(f"Designing thumbnail for: {args.title!r}")
    svg = generate_svg(client, args.title, args.vibe)

    output = Path(args.output)
    render_png(svg, output)
    print(f"Saved PNG: {output}")

    if args.save_svg:
        svg_path = output.with_suffix(".svg")
        svg_path.write_text(svg)
        print(f"Saved SVG: {svg_path}")

    url = upload_to_github(output)
    if url:
        print(f"Uploaded to GitHub: {url}")


if __name__ == "__main__":
    main()
