# YouTube Thumbnail Generator

Generates 1280×720 YouTube thumbnails using Claude to design SVGs, then rasterizes them to PNG. Every thumbnail features a Claude-style robot as the main visual element.

## Setup

**Install dependencies:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Configure `.env`:**

```env
ANTHROPIC_API_KEY=your_key_here

# Optional branding (added to every thumbnail footer)
COMPANY_NAME=Your Company
COMPANY_EMAIL=you@example.com
COMPANY_URL=https://example.com

# Optional GitHub auto-upload
GITHUB_TOKEN=your_token
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo
GITHUB_BRANCH=main
```

## Usage

```bash
python3 thumbnail.py --title "YOUR VIDEO TITLE" --save-svg
```

**Flags:**

| Flag | Description |
|---|---|
| `--title` | (Required) Main title text on the thumbnail |
| `--vibe` | Topic, mood, and style direction. Omit to use the brand default |
| `--output` | Output PNG path (default: `outputs/thumbnail.png`) |
| `--save-svg` | Also save the raw SVG alongside the PNG |

**Example:**

```bash
python3 thumbnail.py \
  --title "Build a Claude Code Skill" \
  --output outputs/claude-code-skill.png \
  --save-svg
```

## Claude Code Skill

This project includes a Claude Code skill that lets you generate thumbnails directly from the Claude Code interface. Just describe your video and Claude will design and render the thumbnail for you.

## Output

Generated thumbnails are saved to the `outputs/` directory as both PNG and SVG.
