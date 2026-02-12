---
name: sophnet-pptx
description: 'For create/edit tasks, final reply must include a download URL and must not include local file paths (brief summary text is allowed). Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.'
---

# PPTX Skill

## TOP PRIORITY: URL Required, No Local Paths (Create/Edit)

**This rule overrides all formatting and style preferences.**

If the task creates or edits a `.pptx`, the final assistant reply MUST include:

- Success: `https://...`
- Upload skipped: `FILE_PATH=<absolute-path>`

Forbidden in create/edit replies: local file paths (e.g. `/tmp/...pptx`). Brief summary text is allowed.

Before sending the final answer, self-check: "Does my reply include URL and avoid local paths?"

## MANDATORY: Working Directory

**EVERY command in this skill MUST be executed from THIS skill's directory.** Before running ANY command — Python, Node.js, or bash script — you MUST `cd` into this skill's directory first. Determine the absolute path of this `SKILL.md` file and use its parent directory.

```bash
# FIRST COMMAND of every task — determine and cd into the skill directory
SKILL_DIR="<absolute-path-to-this-skills-sophnet-pptx-directory>"
cd "$SKILL_DIR"
```

**NEVER run commands from the repository root or any other directory.** If you do, `node` won't find `.js` files, `uv run` won't find `pyproject.toml`, and `python` won't have access to required packages.

## MANDATORY: Cleanup — Zero Residual Files

**CRITICAL: After every task, `$SKILL_DIR` must contain ONLY these permanent files:** `SKILL.md`, `editing.md`, `pptxgenjs.md`, `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json`, `node_modules/`, `scripts/`, `.venv/`. **NOTHING else.** No `.js` scripts, no `unpacked*/` directories, no `.py` scripts, no generated `.pptx` files, no thumbnail images.

Three enforced rules (non-negotiable):

1. **JS scripts MUST self-delete.** Every `.js` file you create MUST include `try { require("fs").unlinkSync(__filename); } catch(e) {}` as the LAST statement in the script (after `writeFile` resolves). Additionally, run with: `cd "$SKILL_DIR" && node _tmp_pptx.js; rm -f _tmp_pptx.js`
2. **Unpack to `/tmp/` only.** NEVER unpack into `$SKILL_DIR`. Use `/tmp/_tmp_pptx_unpacked/` and `rm -rf` it after packing.
3. **Python scripts and thumbnails go to `/tmp/`.** Write Python scripts to `/tmp/_tmp_*.py` and delete after execution. Generate thumbnails to `/tmp/`.

## Quick Reference

| Task                         | Guide                                                       |
| ---------------------------- | ----------------------------------------------------------- |
| Prepare Python environment   | `cd $SKILL_DIR && bash scripts/ensure_uv_env.sh`            |
| Read/analyze content         | `cd $SKILL_DIR && uv run --project . python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md)                               |
| Create from scratch          | Read [pptxgenjs.md](pptxgenjs.md)                           |
| Upload and print URL         | `cd $SKILL_DIR && bash scripts/upload_file.sh --file /abs/path/output.pptx --url-only` |

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
# CORRECT — run script, clean up, then ALWAYS upload the output file
cd "$SKILL_DIR" && node _tmp_pptx.js; rm -f _tmp_pptx.js; bash scripts/upload_file.sh --file /tmp/OUTPUT_NAME.pptx --url-only

# WRONG — running from repo root or other directory
node create_presentation.js              # ✗ Cannot find module
node /some/other/path/create_ppt.js      # ✗ Cannot find module 'pptxgenjs'

# WRONG — forgetting to upload after creating the file
cd "$SKILL_DIR" && node _tmp_pptx.js; rm -f _tmp_pptx.js   # ✗ Missing upload step!
```

Always save the script as `$SKILL_DIR/_tmp_pptx.js`. The script MUST include `try { require("fs").unlinkSync(__filename); } catch(e) {}` as its last statement to self-delete. The shell `rm -f` is a backup. **The `bash scripts/upload_file.sh --url-only` at the end is MANDATORY** — replace `OUTPUT_NAME.pptx` with the actual filename.

## MANDATORY: Upload After Every Create/Edit

**CRITICAL: After creating or modifying a PPTX file, you MUST run `scripts/upload_file.sh --url-only` and include the URL in the final reply.** This is NOT optional. Do NOT return local file paths. You may include brief summary text, but the reply must contain the download URL.

## Delivery

Local PPTX creation/editing does not require any Sophnet API key.

**IMPORTANT: After creating or modifying a PPTX, ALWAYS upload it and return the download URL.** This is the default behavior — do not skip the upload step.

```bash
cd "$SKILL_DIR" && bash scripts/upload_file.sh --file <absolute-path-to-pptx> --url-only
```

**Note:** The `cd "$SKILL_DIR"` prefix is MANDATORY — `scripts/upload_file.sh` is relative to the skill directory. Without it, the command fails with `No such file or directory`.

Upload command output contract:

- `FILE_PATH=<absolute-path>`
- `UPLOAD_STATUS=uploaded|skipped`
- `DOWNLOAD_URL=<https://...>` (present only when uploaded)
- With `--url-only` and successful upload: output is exactly one line, the raw `https://...` URL

Delivery rules:

- **ALWAYS `cd "$SKILL_DIR"` first, then call `bash scripts/upload_file.sh --url-only` after producing a PPTX file.**
- Final response for create/edit MUST include:
  - success: a valid `https://...` URL
  - missing API key fallback: `FILE_PATH=<absolute-path>`
- Do not include local file paths in create/edit responses.
- Keep URL output logic independent inside `sophnet-pptx/scripts`. Do not call other skills' upload scripts.

---

## Reading Content

```bash
# Text extraction
uv run --project . python -m markitdown presentation.pptx

# Visual overview
uv run --project . python scripts/thumbnail.py presentation.pptx

# Raw XML (always unpack to /tmp/, never to $SKILL_DIR)
uv run --project . python scripts/office/unpack.py presentation.pptx /tmp/_tmp_pptx_unpacked/
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

2. **Write `$SKILL_DIR/_tmp_pptx.js`** (always this exact filename). Key rules from the reference:
   - Shape enum: `pres.shapes.RECTANGLE`, NOT string `'rect'` or `'RECTANGLE'`
   - Color: `"FF0000"` (6-char hex, no `#` prefix)
   - Background: `slide.background = { color: "HEXVAL" }` (use `color` key, not `path`)
   - Save with: `pres.writeFile({ fileName: "/tmp/output.pptx" })`
   - **MANDATORY: copy the upload block from pptxgenjs.md** — every script MUST include `require("child_process").execSync` to call `scripts/upload_file.sh --url-only` inside the `writeFile().then()` callback, right after `fs.unlinkSync(__filename)`. This ensures the file is uploaded automatically and URL output is available for the final reply. See the "Setup & Basic Structure" section in [pptxgenjs.md](pptxgenjs.md) for the exact template.

3. **Run from `$SKILL_DIR`**:
   ```bash
   cd "$SKILL_DIR" && node _tmp_pptx.js; rm -f _tmp_pptx.js
   ```
   The script self-deletes, uploads the file, and prints the URL. Return a final reply that includes this URL and avoids local paths.

4. **Verify** — check the output file exists, then use markitdown for content QA:
   ```bash
   cd "$SKILL_DIR" && uv run --project . python -m markitdown /tmp/output.pptx
   ```

### What NOT to do

- Do NOT write or run `.js` files from the repository root — `require('pptxgenjs')` will fail
- Do NOT leave `.js` scripts in `$SKILL_DIR` after execution — always delete `_tmp_*` files
- Do NOT guess the pptxgenjs API — always refer to [pptxgenjs.md](pptxgenjs.md)
- Do NOT use string shape names like `'rect'` — use `pres.shapes.RECTANGLE`
- Do NOT skip reading [pptxgenjs.md](pptxgenjs.md) before coding
- Do NOT skip the upload step — ALWAYS run `scripts/upload_file.sh --url-only` after creating/modifying a file and include the URL in the final reply

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

| Theme                  | Primary               | Secondary             | Accent              |
| ---------------------- | --------------------- | --------------------- | ------------------- |
| **Midnight Executive** | `1E2761` (navy)       | `CADCFC` (ice blue)   | `FFFFFF` (white)    |
| **Forest & Moss**      | `2C5F2D` (forest)     | `97BC62` (moss)       | `F5F5F5` (cream)    |
| **Coral Energy**       | `F96167` (coral)      | `F9E795` (gold)       | `2F3C7E` (navy)     |
| **Warm Terracotta**    | `B85042` (terracotta) | `E7E8D1` (sand)       | `A7BEAE` (sage)     |
| **Ocean Gradient**     | `065A82` (deep blue)  | `1C7293` (teal)       | `21295C` (midnight) |
| **Charcoal Minimal**   | `36454F` (charcoal)   | `F2F2F2` (off-white)  | `212121` (black)    |
| **Teal Trust**         | `028090` (teal)       | `00A896` (seafoam)    | `02C39A` (mint)     |
| **Berry & Cream**      | `6D2E46` (berry)      | `A26769` (dusty rose) | `ECE2D0` (cream)    |
| **Sage Calm**          | `84B59F` (sage)       | `69A297` (eucalyptus) | `50808E` (slate)    |
| **Cherry Bold**        | `990011` (cherry)     | `FCF6F5` (off-white)  | `2F3C7E` (navy)     |

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

| Header Font  | Body Font     |
| ------------ | ------------- |
| Georgia      | Calibri       |
| Arial Black  | Arial         |
| Calibri      | Calibri Light |
| Cambria      | Calibri       |
| Trebuchet MS | Calibri       |
| Impact       | Arial         |
| Palatino     | Garamond      |
| Consolas     | Calibri       |

| Element        | Size          |
| -------------- | ------------- |
| Slide title    | 36-44pt bold  |
| Section header | 20-24pt bold  |
| Body text      | 14-16pt       |
| Captions       | 10-12pt muted |

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
