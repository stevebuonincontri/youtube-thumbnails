---
name: thumbnail-SKILL
description: Generate a YouTube thumbnail (1280×720 PNG) featuring a Claude-style robot by asking Claude to design an SVG and rendering it. Use when the user asks to create, design, or generate a YouTube thumbnail.
---

# YouTube Thumbnail Generator

Generates a YouTube thumbnail featuring a Claude-style robot as the main visual element by having Claude design an SVG, then rasterizing it to a 1280×720 PNG. The robot is always present — no lightning bolts. Placed in the YouTube project directory, it can be run with a title and vibe description to produce a thumbnail image.

## When to use

- "Make a thumbnail for my video about X"
- "Generate a YouTube thumbnail titled Y"
- "Design a thumbnail with vibe Z"

## Inputs to gather

Before running, make sure you have:
- **title** — the bold text that will appear on the thumbnail
- **vibe** — topic, mood, and style direction (optional — omit `--vibe` to use the brand default)
- **output path** (optional) — defaults to `outputs/thumbnail.png`

If the user gave you a video idea but no explicit title or vibe, propose a title and run without `--vibe` to use the brand default style.

### Default vibe (brand standard)

When `--vibe` is omitted, `thumbnail.py` uses the brand vibe defined in `DEFAULT_VIBE` inside the script:

- Deep purple gradient background (#3a1273 → #5b1ea8 → #2a0d5c)
- Bold yellow (#ffe14d) Impact font for primary title; white Impact for secondary lines
- Orange (#ff6a00) pill tag at top-left (e.g. "CLAUDE CODE")
- The last 1–2 title lines share **one single solid yellow skewed rect** — not separate rects per line
- `skewX(-10)` on the rect only; text has no transform; rect wide enough to cover all highlighted text
- Subtle diagonal yellow stripe accents (opacity ~0.07)
- Glowing yellow radial burst behind robot on right half
- Terminal/code decoration lines bottom-left in light purple monospace
- **Solid footer bar** (#1a0640, full width, ~48px tall): company name bold yellow left, website white center-left, email white right-aligned — fully opaque, clearly readable
- Claude-style robot right half with glowing cyan eyes

## How to run

The script lives at `/Users/steve/Documents/youtube/thumbnail.py`. Requirements (`anthropic`, `resvg-py`, `python-dotenv`) are listed in `requirements.txt` in that directory. All configuration is read from `.env`:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Required. Your Anthropic API key. |
| `COMPANY_NAME` | Optional. Branding included as a required watermark/footer on the thumbnail (e.g. `Hometask AI`). |
| `COMPANY_EMAIL` | Optional. Contact email included as a required watermark/footer (e.g. `sales@hometask.io`). |
| `COMPANY_URL` | Optional. Homepage URL included as a required watermark/footer (e.g. `https://hometask.io`). |

Run from the youtube project directory:

```bash
cd /Users/steve/Documents/youtube
python3 thumbnail.py --title "TITLE" --vibe "VIBE DESCRIPTION" --output outputs/some-name.png --save-svg
```

Flags:
- `--title` (required) — main thumbnail text
- `--vibe` (required) — topic/mood/style direction passed to the designer prompt
- `--output` — PNG path (default `outputs/thumbnail.png`)
- `--save-svg` — also write the raw SVG next to the PNG (useful for iteration)

## After running

- Confirm the PNG was written and report its path as a clickable link.
- If the user wants tweaks ("make it more red", "swap the title"), re-run with adjusted `--title`/`--vibe` rather than hand-editing the SVG — the model regenerates a fresh design each call.
- If you saved the SVG and the user wants a small surgical edit (one color, one word), it's reasonable to edit the SVG directly and re-rasterize, but a fresh generation usually looks better.

## Common issues

- **`ANTHROPIC_API_KEY not set`** — check `/Users/steve/Documents/youtube/.env` exists and contains `ANTHROPIC_API_KEY`, `COMPANY_NAME`, `COMPANY_EMAIL`, and `COMPANY_URL`.
- **Branding not appearing** — the prompt enforces branding as REQUIRED. If `COMPANY_EMAIL`, `COMPANY_NAME`, or `COMPANY_URL` are set in `.env` but not showing, regenerate — the designer is instructed to always include them as a watermark/footer.
- **`python: command not found`** — use `python3` instead of `python`.
- **Clipped text in pills/badges** — the SVG renderer doesn't auto-fit text. If the design comes back with clipped labels, regenerate; the system prompt already discourages this but it sometimes slips through.
- **Missing glyphs (?????)** — emoji or decorative Unicode rendered as question marks. Regenerate; the prompt forbids these but enforce by re-running if seen.
