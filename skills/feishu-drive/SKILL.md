---
name: feishu-drive
description: |
  Feishu file-level management (文件管理): move, delete, copy, list files/folders, get file metadata. Activate for ANY file-level operation regardless of file type: 移动文件, 删除文件, 复制文件, 文件夹, 文件列表, 文件信息, move file, delete file, copy file, list files, create folder, 云空间, drive. This is the correct tool when user wants to move/delete/organize ANY Feishu file (documents, spreadsheets, bitables, etc). Do NOT use for reading/editing file content (use feishu-doc, feishu-sheets, or feishu-bitable instead).
---

# Feishu Drive Tool

Single tool `feishu_drive` for cloud storage operations.

## Token Extraction

From URL `https://xxx.feishu.cn/drive/folder/ABC123` → `folder_token` = `ABC123`

## Actions

### List Folder Contents

```json
{ "action": "list" }
```

Root directory (no folder_token).

```json
{ "action": "list", "folder_token": "fldcnXXX" }
```

Returns: files with token, name, type, url, timestamps.

### Get File Info

```json
{ "action": "info", "file_token": "ABC123", "type": "docx" }
```

Searches for the file in the root directory. Note: file must be in root or use `list` to browse folders first.

`type`: `doc`, `docx`, `sheet`, `bitable`, `folder`, `file`, `mindnote`, `shortcut`

### Create Folder

```json
{ "action": "create_folder", "name": "New Folder" }
```

In parent folder:

```json
{ "action": "create_folder", "name": "New Folder", "folder_token": "fldcnXXX" }
```

### Move File

```json
{ "action": "move", "file_token": "ABC123", "type": "docx", "folder_token": "fldcnXXX" }
```

### Delete File

```json
{ "action": "delete", "file_token": "ABC123", "type": "docx" }
```

## File Types

| Type       | Description             |
| ---------- | ----------------------- |
| `doc`      | Old format document     |
| `docx`     | New format document     |
| `sheet`    | Spreadsheet             |
| `bitable`  | Multi-dimensional table |
| `folder`   | Folder                  |
| `file`     | Uploaded file           |
| `mindnote` | Mind map                |
| `shortcut` | Shortcut                |

## Configuration

```yaml
channels:
  feishu:
    tools:
      drive: true # default: true
```

## Permissions

- `drive:drive` - Full access (create, move, delete)
- `drive:drive:readonly` - Read only (list, info)

## Collaboration with Other Skills

- **Read/edit document content**: Use `feishu_doc` instead
- **Read/edit spreadsheet cells**: Use `feishu-sheets` instead
- **Read/edit bitable records**: Use `feishu-bitable` instead
- **Sharing/permissions**: Use `feishu_perm` instead
- **Wiki node operations**: Use `feishu_wiki` for wiki-specific navigation (list spaces, create wiki nodes)

## Known Limitations

- **Bots have no root folder**: Feishu bots use `tenant_access_token` and don't have their own "My Space". The root folder concept only exists for user accounts. This means:
  - `create_folder` without `folder_token` will fail (400 error)
  - Bot can only access files/folders that have been **shared with it**
  - **Workaround**: User must first create a folder manually and share it with the bot, then bot can create subfolders inside it
