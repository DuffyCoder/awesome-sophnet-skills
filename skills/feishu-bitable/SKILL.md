---
name: feishu-bitable
description: "Feishu Bitable (多维表格) CRUD operations: list/create/update/delete tables, records, fields, and views. Bitable is a structured database-like table with fields (columns with types) and records (rows), similar to Airtable/Notion database. Activate for: 多维表格, bitable, lark base, 数据表, 记录管理, 字段管理, database table, /base/ URLs, /wiki/ URLs with table= parameter. Do NOT confuse with feishu-sheets (电子表格/spreadsheet) which is cell-based like Excel."
metadata: {"clawdbot":{"emoji":"📊","requires":{"env":["FEISHU_APP_ID","FEISHU_APP_SECRET"]},"primaryEnv":"FEISHU_APP_ID"}}
---

# Feishu Bitable Skill

CRUD operations for Feishu Bitable (多维表格) — tables, records, fields, and views.

## Environment Variables

`FEISHU_APP_ID` and `FEISHU_APP_SECRET` are already available from the Feishu channel configuration. No extra setup is needed. The CLI reads them automatically via `dotenv` or shell environment.

## Extracting app-token from URLs

Feishu Bitable URLs come in three formats. Extract the `app-token` as follows:

| URL Format | Example | app-token |
|-----------|---------|-----------|
| **Wiki /wiki/** | `feishu.cn/wiki/AbCdEf?table=tblXXX` | Wiki token `AbCdEf` can be used directly as app-token (Feishu API accepts it) |
| **Standalone /base/** | `feishu.cn/base/basXXXXXX` | `basXXXXXX` |
| **Advanced /app/** | `feishu.cn/app/AbCdEf?pageId=pgeXXX` | `AbCdEf` |

The `table=tblXXX` query parameter is the `table-id`. The `view=vewXXX` parameter is the view-id.

**Note on /wiki/ URLs:** Feishu Bitable API accepts wiki tokens directly. If user provides a /wiki/ URL with `table=` parameter, you can safely pass the wiki token as `--app-token`. If unsure whether the URL is a bitable, use `feishu_wiki` to check `obj_type` first.

## CLI Reference

All commands are run from the skill directory:

```bash
cd skills/feishu-bitable
node bin/cli.js <command> [options]
```

### Commands

| Command | Required Options | Optional | Description |
|---------|-----------------|----------|-------------|
| `test` | — | — | Test connection and token validity |
| `get-app` | `--app-token` | — | Get bitable app info |
| `list-tables` | `--app-token` | `--page-size`, `--page-token` | List all tables |
| `list-fields` | `--app-token --table-id` | `--page-size` | List fields in a table |
| `list-records` | `--app-token --table-id` | `--page-size`, `--page-token`, `--filter`, `--sort` | List records |
| `list-views` | `--app-token --table-id` | `--page-size` | List views |
| `create-table` | `--app-token --name` | `--fields <json>` | Create a new table |
| `create-record` | `--app-token --table-id --data <json>` | — | Create one record |
| `batch-create` | `--app-token --table-id --data <json-array>` | — | Batch create records (max 100) |
| `update-record` | `--app-token --table-id --record-id --data <json>` | — | Update a record |
| `delete-record` | `--app-token --table-id --record-id` | — | Delete a record |

### Data format

The `--data` option accepts inline JSON or a file reference with `@` prefix:

```bash
# Inline JSON
--data '{"任务名称": "新任务", "状态": "待办"}'

# From file
--data @examples/create-records.json
```

For `batch-create`, `--data` must be a JSON array of record objects.

### Typical workflow

1. Parse the user's Feishu URL to extract `app-token` and `table-id`
2. `list-tables` → confirm the target table exists
3. `list-fields` → understand the table schema (field names and types)
4. Perform the requested operation (list/create/update/delete records)
5. Verify the result by re-reading if needed

## Field Types

| Type | API Value | Example Data |
|------|-----------|-------------|
| Text | 1 | `"Hello"` |
| Number | 2 | `123.45` |
| SingleSelect | 3 | `"选项名"` |
| MultiSelect | 4 | `["A", "B"]` |
| DateTime | 5 | Unix timestamp in ms: `1700000000000` |
| Checkbox | 7 | `true` / `false` |
| User | 11 | `[{"id": "ou_xxx"}]` |
| URL | 15 | `"https://..."` |
| Formula | 20 | Read-only, computed |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 1254003 | WrongBaseToken | Check app-token format |
| 1254004 | WrongTableId | Verify table-id exists via `list-tables` |
| 1254041 | TableIdNotFound | Table does not exist |
| 1254043 | RecordIdNotFound | Record does not exist |
| 403 | Forbidden | App needs to be added as bitable collaborator with edit permission |

## Collaboration with Other Skills

- **File operations** (move/delete bitable): Use `feishu_drive` instead
- **Sharing/permissions**: Use `feishu_perm` instead
- **Wiki navigation**: Use `feishu_wiki` to discover file type from /wiki/ URLs when ambiguous
- **Spreadsheets**: If user mentions 单元格/cell/行列/row/column/A1, use `feishu-sheets` instead
- **Documents**: If user wants to edit text/paragraphs, use `feishu_doc` instead

## Notes

- Max 100 records per batch request
- Field names must exactly match the column names in the bitable
- DateTime fields use Unix timestamps in milliseconds
- Formula fields are read-only
