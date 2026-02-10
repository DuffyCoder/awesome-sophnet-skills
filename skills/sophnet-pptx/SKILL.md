---
name: sophnet-pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
---

# PPTX Skill

## MANDATORY: Working Directory

**EVERY command in this skill MUST be executed from THIS skill's directory.** Before running ANY command — Python, Node.js, or bash script — you MUST `cd` into this skill's directory first. Determine the absolute path of this `SKILL.md` file and use its parent directory.

```bash
# FIRST COMMAND of every task — determine and cd into the skill directory
SKILL_DIR="<absolute-path-to-this-skills-sophnet-pptx-directory>"
cd "$SKILL_DIR"
```

**NEVER run commands from the repository root or any other directory.** If you do, `node` won't find `.js` files, `uv run` won't find `pyproject.toml`, and `python` won't have access to required packages.

## Quick Reference

| Task | Guide |
|------|-------|
| Prepare Python environment | `cd $SKILL_DIR && bash scripts/ensure_uv_env.sh` |
| Read/analyze content | `cd $SKILL_DIR && uv run --project . python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |
| Optional upload for URL | `cd $SKILL_DIR && bash scripts/upload_file.sh --file /abs/path/output.pptx` |

## Python Runtime (uv)

**CRITICAL: All Python execution in this skill MUST use `uv run --project .` from the skill directory. NEVER use bare `python3`, `python`, or `pip install` directly — the required packages (python-pptx, markitdown, lxml, etc.) are ONLY available inside the uv virtual environment defined by this skill's `pyproject.toml`. Direct `python3` will fail with ModuleNotFoundError.**

First, ensure the environment is set up (run once per session):

```bash
cd "$SKILL_DIR"
bash scripts/ensure_uv_env.sh
```

Then ALL Python commands must use this prefix:

```bash
cd "$SKILL_DIR" && uv run --project . python <script-or-module>
```

This applies to both the provided scripts AND any inline Python code you write. For inline code, use:

```bash
cd "$SKILL_DIR" && uv run --project . python -c "from pptx import Presentation; ..."
```

## Node.js Runtime (pptxgenjs)

**CRITICAL: All Node.js execution for creating presentations from scratch MUST run from this skill directory.** The `pptxgenjs`, `react-icons`, `sharp` etc. packages are installed in this skill's local `node_modules/`. Running `node` from any other directory will fail with `Cannot find module`.

```bash
# CORRECT — always cd first, then run node
cd "$SKILL_DIR" && node create_presentation.js

# WRONG — running from repo root or other directory
node create_presentation.js              # ✗ Cannot find module
node /some/other/path/create_ppt.js      # ✗ Cannot find module 'pptxgenjs'
```

When writing a `.js` file to create slides, save it inside `$SKILL_DIR` (e.g. `$SKILL_DIR/create_presentation.js`), then execute from `$SKILL_DIR`.

## Delivery

Local PPTX creation/editing does not require any Sophnet API key.

Upload is optional and only needed when a download URL is explicitly requested.

```bash
bash scripts/upload_file.sh --file <absolute-path-to-pptx>
```

Upload command output contract:
- `FILE_PATH=<absolute-path>`
- `UPLOAD_STATUS=uploaded|skipped`
- `DOWNLOAD_URL=<https://...>` (present only when uploaded)

Delivery rules:
- Use local file delivery by default; do not require API key.
- Call `scripts/upload_file.sh` only when URL output is needed.
- If `UPLOAD_STATUS=uploaded`, return the exact `DOWNLOAD_URL` value.
- If `UPLOAD_STATUS=skipped` (missing API key), return `FILE_PATH` instead of failing the whole task.
- Keep URL output logic independent inside `sophnet-pptx/scripts`. Do not call other skills' upload scripts.

---

## Reading Content

```bash
# Text extraction
uv run --project . python -m markitdown presentation.pptx

# Visual overview
uv run --project . python scripts/thumbnail.py presentation.pptx

# Raw XML
uv run --project . python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

Use when no template or reference presentation is available. **You MUST follow the steps below in order. Do NOT freestyle — read the reference first, write the script, then run it from `$SKILL_DIR`.**

### Step-by-step workflow

1. **Read the API reference FIRST** — open and read [pptxgenjs.md](pptxgenjs.md) in full before writing any code. It contains correct syntax, required enums, and a Common Pitfalls section that prevents crashes.

2. **Write a `.js` file inside `$SKILL_DIR`** — save your script as e.g. `$SKILL_DIR/create_presentation.js`. Key rules from the reference:
   - Shape enum: `pres.shapes.RECTANGLE`, NOT string `'rect'` or `'RECTANGLE'`
   - Color: `"FF0000"` (6-char hex, no `#` prefix)
   - Background: `slide.background = { color: "HEXVAL" }` (use `color` key, not `path`)
   - Save with: `pres.writeFile({ fileName: "/tmp/output.pptx" })`

3. **Run from `$SKILL_DIR`** — the local `node_modules/` with pptxgenjs is here:
   ```bash
   cd "$SKILL_DIR" && node create_presentation.js
   ```

4. **Verify** — check the output file exists, then use markitdown for content QA:
   ```bash
   cd "$SKILL_DIR" && uv run --project . python -m markitdown /tmp/output.pptx
   ```

5. **Upload (if URL requested)**:
   ```bash
   cd "$SKILL_DIR" && bash scripts/upload_file.sh --file /tmp/output.pptx
   ```

### What NOT to do

- Do NOT write or run `.js` files from the repository root — `require('pptxgenjs')` will fail
- Do NOT guess the pptxgenjs API — always refer to [pptxgenjs.md](pptxgenjs.md)
- Do NOT use string shape names like `'rect'` — use `pres.shapes.RECTANGLE`
- Do NOT skip reading [pptxgenjs.md](pptxgenjs.md) before coding

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
uv run --project . python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
uv run --project . python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images (optional — requires LibreOffice)

**Prerequisites:** LibreOffice (`soffice`) and Poppler (`pdftoppm`) must be installed. If `soffice` is not available, **skip Visual QA entirely** — do NOT attempt to install it or call `soffice.py`. Content QA with markitdown is sufficient.

Check first:
```bash
which soffice && echo "available" || echo "NOT available — skip Visual QA"
```

If available, convert to images:
```bash
cd "$SKILL_DIR" && uv run --project . python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

---

## Dependencies

- `uv` - Python environment and dependency manager for this skill (`bash scripts/ensure_uv_env.sh`)
- `uv run --project . python -m markitdown` - text extraction
- `uv run --project . python scripts/thumbnail.py` - thumbnail grids
- `pptxgenjs` - creating from scratch (installed locally in skill `node_modules/`; if missing run `cd <skill-dir> && npm install pptxgenjs react react-dom react-icons sharp`)
- LibreOffice (`soffice`) - PDF conversion (**optional**; skip Visual QA if not installed)
- Poppler (`pdftoppm`) - PDF to images (**optional**; used with LibreOffice)
