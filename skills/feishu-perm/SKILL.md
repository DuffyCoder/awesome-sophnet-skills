---
name: feishu-perm
description: |
  Feishu permission and sharing management (权限与分享). Activate when user wants to: 分享文件, 分享文档, 添加协作者, 移除协作者, 查看权限, share document, share file, add collaborator, remove collaborator, manage permissions, grant access, revoke access, 权限管理, 共享, 协作. This is the ONLY tool for sharing and permission operations.
---

# Feishu Permission Tool

Single tool `feishu_perm` for managing file/document permissions.

## Actions

### List Collaborators

```json
{ "action": "list", "token": "ABC123", "type": "docx" }
```

Returns: members with member_type, member_id, perm, name.

### Add Collaborator

```json
{
  "action": "add",
  "token": "ABC123",
  "type": "docx",
  "member_type": "email",
  "member_id": "user@example.com",
  "perm": "edit"
}
```

### Remove Collaborator

```json
{
  "action": "remove",
  "token": "ABC123",
  "type": "docx",
  "member_type": "email",
  "member_id": "user@example.com"
}
```

## Token Types

| Type       | Description             |
| ---------- | ----------------------- |
| `doc`      | Old format document     |
| `docx`     | New format document     |
| `sheet`    | Spreadsheet             |
| `bitable`  | Multi-dimensional table |
| `folder`   | Folder                  |
| `file`     | Uploaded file           |
| `wiki`     | Wiki node               |
| `mindnote` | Mind map                |

## Member Types

| Type               | Description        |
| ------------------ | ------------------ |
| `email`            | Email address      |
| `openid`           | User open_id       |
| `userid`           | User user_id       |
| `unionid`          | User union_id      |
| `openchat`         | Group chat open_id |
| `opendepartmentid` | Department open_id |

## Permission Levels

| Perm          | Description                          |
| ------------- | ------------------------------------ |
| `view`        | View only                            |
| `edit`        | Can edit                             |
| `full_access` | Full access (can manage permissions) |

## Examples

Share document with email:

```json
{
  "action": "add",
  "token": "doxcnXXX",
  "type": "docx",
  "member_type": "email",
  "member_id": "alice@company.com",
  "perm": "edit"
}
```

Share folder with group:

```json
{
  "action": "add",
  "token": "fldcnXXX",
  "type": "folder",
  "member_type": "openchat",
  "member_id": "oc_xxx",
  "perm": "view"
}
```

## Handling /wiki/ URLs

For wiki URLs, use `type: "wiki"` and pass the wiki token directly:

```json
{
  "action": "add",
  "token": "wiki_token_from_url",
  "type": "wiki",
  "member_type": "email",
  "member_id": "user@example.com",
  "perm": "edit"
}
```

## Collaboration with Other Skills

- This is the ONLY skill for sharing and permission operations
- **feishu_doc / feishu-sheets / feishu-bitable**: Use those for content operations, then use this for sharing
- **feishu_drive**: Use that for file management (move/delete), use this for permission management

## Configuration

**IMPORTANT:** This tool is disabled by default. To enable it, the user needs to add to their openclaw.json:

```json
{
  "skills": {
    "entries": {
      "feishu-perm": {
        "enabled": true
      }
    }
  }
}
```

Or in the feishu channel tools config:
```yaml
channels:
  feishu:
    tools:
      perm: true # default: false (disabled)
```

If user requests sharing/permission operations and this tool is not available, inform them that feishu-perm needs to be enabled first.

## Permissions

Required: `drive:permission`
