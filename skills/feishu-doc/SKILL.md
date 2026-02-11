---
name: feishu-doc
description: |
  Feishu document CONTENT read/write (读写文档内容). Only for reading, writing, and editing document text and blocks. Activate for: 读取文档, 写入文档, 编辑文档内容, 文档块, 云文档, read document, write document, edit content, append content, /docx/ URLs. For /wiki/ URLs: if user clearly mentions document/文档, you can use the wiki token directly as doc_token. Do NOT use for file-level operations (move/delete → feishu-drive), sharing (→ feishu-perm), or spreadsheets/bitables (→ feishu-sheets/feishu-bitable).
---

# Feishu Document Tool

Single tool `feishu_doc` with action parameter for all document operations.

## Token Extraction

- `/docx/` URL: `https://xxx.feishu.cn/docx/ABC123def` → `doc_token` = `ABC123def`
- `/wiki/` URL: `https://xxx.feishu.cn/wiki/ABC123def` → wiki token `ABC123def` can be used directly as `doc_token` (if you know it's a document). If unsure about file type, use `feishu_wiki` to resolve first.

## Actions

### Read Document

```json
{ "action": "read", "doc_token": "ABC123def" }
```

Returns: title, plain text content, block statistics. Check `hint` field - if present, structured content (tables, images) exists that requires `list_blocks`.

### Write Document (Replace All)

```json
{ "action": "write", "doc_token": "ABC123def", "content": "# Title\n\nMarkdown content..." }
```

Replaces entire document with markdown content. Supports: headings, lists, code blocks, quotes, links, images (`![](url)` auto-uploaded), bold/italic/strikethrough.

**Limitation:** Markdown tables are NOT supported.

### Append Content

```json
{ "action": "append", "doc_token": "ABC123def", "content": "Additional content" }
```

Appends markdown to end of document.

### Create Document

```json
{ "action": "create", "title": "New Document" }
```

With folder:

```json
{ "action": "create", "title": "New Document", "folder_token": "fldcnXXX" }
```

### List Blocks

```json
{ "action": "list_blocks", "doc_token": "ABC123def" }
```

Returns full block data including tables, images. Use this to read structured content.

### Get Single Block

```json
{ "action": "get_block", "doc_token": "ABC123def", "block_id": "doxcnXXX" }
```

### Update Block Text

```json
{
  "action": "update_block",
  "doc_token": "ABC123def",
  "block_id": "doxcnXXX",
  "content": "New text"
}
```

### Delete Block

```json
{ "action": "delete_block", "doc_token": "ABC123def", "block_id": "doxcnXXX" }
```

## Reading Workflow

1. Start with `action: "read"` - get plain text + statistics
2. Check `block_types` in response for Table, Image, Code, etc.
3. If structured content exists, use `action: "list_blocks"` for full data

## Collaboration with Other Skills

- **File operations** (move/delete/copy document): Use `feishu_drive` instead
- **Sharing/permissions**: Use `feishu_perm` instead
- **Wiki navigation**: Use `feishu_wiki` to list/create/move wiki nodes, then use this tool to edit content
- **Spreadsheet/Bitable**: If the content is a table, use `feishu-sheets` or `feishu-bitable` instead

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| Token not found | doc_token is wrong or is not a document | The URL might point to a sheet/bitable. Use `feishu_wiki` to check `obj_type` |
| No permission | Bot has no access | Ask user to share the document with the bot |

## Permissions

Required: `docx:document`, `docx:document:readonly`, `docx:document.block:convert`, `drive:drive`
