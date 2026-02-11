---
name: feishu-wiki
description: |
  Feishu knowledge base (知识库) navigation and wiki node type resolver. Activate when: user mentions 知识库/知识空间/wiki, user provides a feishu.cn/wiki/ URL and you DON'T know the file type, or you need to list/create/move/rename wiki nodes. Key fact: wiki tokens can be passed directly to feishu_doc/feishu-sheets/feishu-bitable APIs without resolving first, BUT you must know the file type to pick the right skill.
---

# Feishu Wiki Tool

Single tool `feishu_wiki` for knowledge base operations.

## Important: /wiki/ URL Handling Strategy

Feishu `/wiki/` URLs don't reveal the file type (docx, sheet, bitable, slides). Two strategies:

### Strategy A: User context is clear → skip resolution, pass wiki token directly

If the user says "读取这个**电子表格** https://xxx.feishu.cn/wiki/ABC" — you already know it's a sheet, so pass the wiki token `ABC` directly to feishu-sheets as `spreadsheet-token`. All Feishu content APIs (docx, sheets, bitable) accept wiki tokens directly.

### Strategy B: File type is unknown → resolve first

If the user just says "帮我看看这个 https://xxx.feishu.cn/wiki/ABC" with no type hint:

1. Extract token: `https://xxx.feishu.cn/wiki/ABC123def` → `token` = `ABC123def`
2. Call `{ "action": "get", "token": "ABC123def" }` → returns `obj_type`
3. Route based on `obj_type`:
   - `docx` or `doc` → use `feishu_doc` (can pass wiki token directly as `doc_token`)
   - `sheet` → use feishu-sheets (can pass wiki token directly as `spreadsheet-token`)
   - `bitable` → use feishu-bitable (can pass wiki token directly as `app-token`)
   - `slides` → no content editing API, only metadata via `feishu_drive`
   - `mindnote` → no content editing API

### Shortcut: URL has `table=` parameter → always bitable

`feishu.cn/wiki/XXX?table=tblYYY` → directly use feishu-bitable, skip resolution.

## Token Extraction

From URL `https://xxx.feishu.cn/wiki/ABC123def` → `token` = `ABC123def`

## Actions

### Get Node Details (for type discovery)

```json
{ "action": "get", "token": "ABC123def" }
```

Returns: `node_token`, `obj_token`, `obj_type`, `title`.

### List Knowledge Spaces

```json
{ "action": "spaces" }
```

### List Nodes

```json
{ "action": "nodes", "space_id": "7xxx" }
{ "action": "nodes", "space_id": "7xxx", "parent_node_token": "wikcnXXX" }
```

### Create Node

```json
{ "action": "create", "space_id": "7xxx", "title": "New Page" }
{ "action": "create", "space_id": "7xxx", "title": "Sheet", "obj_type": "sheet", "parent_node_token": "wikcnXXX" }
```

`obj_type`: `docx` (default), `sheet`, `bitable`, `mindnote`, `file`, `doc`, `slides`

### Move Node

```json
{ "action": "move", "space_id": "7xxx", "node_token": "wikcnXXX", "target_space_id": "7yyy", "target_parent_token": "wikcnYYY" }
```

### Rename Node

```json
{ "action": "rename", "space_id": "7xxx", "node_token": "wikcnXXX", "title": "New Title" }
```

## Collaboration with Other Skills

- **feishu_doc**: After resolving a docx wiki node, use feishu_doc to read/write content
- **feishu-sheets**: After resolving a sheet wiki node, use feishu-sheets CLI for cell operations
- **feishu-bitable**: After resolving a bitable wiki node, use feishu-bitable CLI for record operations
- **feishu_drive**: For file-level operations (move/delete) on wiki nodes, use feishu_drive
- **feishu_perm**: For sharing/permission on wiki nodes, use feishu_perm

## Permissions

Required: `wiki:wiki` or `wiki:wiki:readonly`
