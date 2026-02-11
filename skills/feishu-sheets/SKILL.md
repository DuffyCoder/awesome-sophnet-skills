---
name: feishu-sheets
description: "Feishu Spreadsheet (电子表格/Sheets) cell-based operations like Excel/Google Sheets: create spreadsheets, manage worksheets (sheet tabs), read/write/append cell ranges using A1 notation. Activate for: 电子表格, spreadsheet, Excel, 工作表, 单元格, 行列, 表格数据, cell, range, row, column, /sheets/ URLs. This is a cell-grid spreadsheet (like Excel), NOT a structured database. Do NOT confuse with feishu-bitable (多维表格) which is record/field based like Airtable."
metadata: {"clawdbot":{"emoji":"📊","requires":{"env":["FEISHU_APP_ID","FEISHU_APP_SECRET"]},"primaryEnv":"FEISHU_APP_ID"}}
---

# Feishu Sheets Skill

CRUD operations for Feishu Spreadsheets (电子表格) — spreadsheet, worksheet, and cell-level operations.

## Environment Variables

`FEISHU_APP_ID` and `FEISHU_APP_SECRET` are required. The CLI reads them via `dotenv` or shell environment.

## Extracting spreadsheet-token from URLs

| URL Format | Example | spreadsheet-token |
|-----------|---------|-------------------|
| **Direct /sheets/** | `feishu.cn/sheets/AbCdEfGhIj` | `AbCdEfGhIj` |
| **Wiki /wiki/** | `feishu.cn/wiki/AbCdEf` (if it's a sheet) | Wiki token `AbCdEf` can be used directly as spreadsheet-token |

**Note on /wiki/ URLs:** Feishu Sheets API accepts wiki tokens directly. If user says "读取这个电子表格" + a /wiki/ URL, you can pass the wiki token directly as `--spreadsheet-token`. If unsure whether the URL is a sheet, use `feishu_wiki` to check `obj_type` first.

## CLI Reference

```bash
cd skills/feishu-sheets
node bin/cli.js <command> [options]
```

### Commands

| Command | Required Options | Optional | Description |
|---------|-----------------|----------|-------------|
| `test` | — | — | Test connection |
| `create-spreadsheet` | — | `--title`, `--folder-token` | Create spreadsheet |
| `get-spreadsheet` | `--spreadsheet-token` | — | Get spreadsheet info |
| `list-sheets` | `--spreadsheet-token` | — | List all worksheets |
| `get-sheet` | `--spreadsheet-token --sheet-id` | — | Get worksheet info |
| `add-sheet` | `--spreadsheet-token --title` | `--index` | Add a worksheet |
| `delete-sheet` | `--spreadsheet-token --sheet-id` | — | Delete a worksheet |
| `read` | `--spreadsheet-token --range` | `--value-render` | Read cell data |
| `write` | `--spreadsheet-token --range --values` | — | Write cell data |
| `append` | `--spreadsheet-token --range --values` | — | Append data after existing |
| `prepend` | `--spreadsheet-token --range --values` | — | Insert data before existing |
| `batch-read` | `--spreadsheet-token --ranges` | — | Read multiple ranges |
| `batch-write` | `--spreadsheet-token --data` | — | Write multiple ranges |

### Range format

Ranges use the format `sheetId!StartCell:EndCell`:
- `abc123!A1:C5` — read cells A1 to C5 in sheet `abc123`
- `abc123!A:C` — read entire columns A to C
- `abc123!1:5` — read rows 1 to 5

Get sheet-id via `list-sheets` first.

### Data format

Cell values use **2D arrays** (array of rows):

```bash
# Write 2 rows x 3 columns
--values '[["Name","Age","City"],["Alice",30,"Beijing"]]'

# From file
--values @data.json
```

### Typical workflow

1. Parse URL to extract `spreadsheet-token`
2. `list-sheets` → get sheet-id(s) and understand structure
3. `read --range sheetId!A1:Z1` → read headers to understand columns
4. Perform operation: read data, write/append/prepend data
5. Verify by reading back

### Value types in cells

| Type | Example | Notes |
|------|---------|-------|
| String | `"hello"` | Text value |
| Number | `42`, `3.14` | Numeric value |
| Boolean | `true`/`false` | Boolean |
| Formula | `"=SUM(A1:A10)"` | Must start with `=` |
| null | `null` | Clear cell |

### Difference from Bitable (多维表格)

- **Sheets** (本技能): Traditional spreadsheet with rows/columns/cells, A1-style addressing
- **Bitable**: Structured database with typed fields, record-based, more like Airtable

## Collaboration with Other Skills

- **File operations** (move/delete spreadsheet): Use `feishu_drive` instead
- **Sharing/permissions**: Use `feishu_perm` instead
- **Wiki navigation**: Use `feishu_wiki` to discover file type from /wiki/ URLs when ambiguous
- **Documents**: If user wants to edit text/paragraphs, use `feishu_doc` instead
- **Multi-dim tables**: If user mentions 多维表格/bitable/records/fields, use `feishu-bitable` instead

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 99991663 | Token expired | Auto-refreshed |
| 99991668 | No permission | Add app as collaborator |
| 90030101 | Spreadsheet not found | Token might be wrong, or the wiki URL might not be a sheet — use `feishu_wiki` to check `obj_type` |
| 90030003 | Sheet not found | Check sheet-id via list-sheets |
