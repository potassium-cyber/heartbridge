# 🚀 HeartBridge 全栈部署与故障排除手册

本手册涵盖了从代码推送到云端部署的全流程，特别收录了常见的 **Git 权限报错** 和 **Google API 鉴权报错** 的解决方案。

---

## 🛠 前置篇：Git 推送避坑指南

在将代码 Push 到 GitHub 时，Mac 用户常遇到 `403 Permission denied` 错误。如果遇到，请按以下方案解决。

### 🚨 常见报错
```text
remote: Permission to xxx denied to old-user.
fatal: unable to access ... : The requested URL returned error: 403
```

### 方案 A：温和清理法（推荐）
告诉 Mac 清除旧的 GitHub 账号缓存。
```bash
printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain erase
```
*之后再次 Push，系统会提示输入密码。注意：**密码必须填 GitHub Personal Access Token (PAT)，不能填登录密码！***

### 方案 B：核弹级绕过法（最快解决）
直接将 Token 写入 URL，跳过所有本地验证。
```bash
# 1. 去 GitHub Settings -> Developer settings -> Tokens 生成一个 Token (ghp_xxxx)
# 2. 执行以下命令 (替换你的 Token 和用户名)
git remote set-url origin https://<YOUR_TOKEN>@github.com/potassium-cyber/heartbridge.git

# 3. 直接 Push
git push -u origin main
```

---

## ☁️ 部署篇：Google Sheets 数据库配置

### 阶段一：准备 Google Cloud 环境 (关键！)

1.  **创建项目**
    *   访问 [Google Cloud Console](https://console.cloud.google.com/) -> 新建项目 `HeartBridge-App`。

2.  **🔔 启用必要 API (这一步最容易漏！)**
    *   点击左侧菜单 **APIs & Services** -> **Library**。
    *   搜索并启用 **Google Sheets API**。
    *   搜索并启用 **Google Drive API**。
    *   *注意：如果未启用这两个 API，后续会报 `PermissionError`。*

### 阶段二：创建机器人 (Service Account)

1.  **创建账号**
    *   菜单 -> **IAM & Admin** -> **Service Accounts** -> **+ CREATE SERVICE ACCOUNT**。
    *   Name: `streamlit-bot` -> Create。

2.  **赋予权限**
    *   Role 选择: **Basic** -> **Editor** (必须是编辑者)。

3.  **下载密钥**
    *   点击创建好的账号 -> **Keys** -> **Add Key** -> **JSON**。
    *   保存下载的 JSON 文件。

### 阶段三：配置 Google Sheets

1.  **新建表格**
    *   创建表格 `heartbridge_db`。
    *   **设置表头 (Row 1)**: `id`, `role`, `nickname`, `title`, `content`, `is_hidden`, `created_at`, `likes`。

2.  **🔔 分享给机器人 (Share)**
    *   打开 JSON 文件，复制 `"client_email"` (如 `streamlit-bot@...`).
    *   点击表格右上角 **Share** -> 粘贴邮箱。
    *   权限选 **Editor** -> Send。

---

## 🚀 上线篇：Streamlit Cloud 部署

1.  **部署应用**
    *   登录 [Streamlit Community Cloud](https://share.streamlit.io/) -> New app -> 选择 GitHub 仓库 -> Deploy。

2.  **配置 Secrets**
    *   在应用界面右下角 **Manage app** -> **Settings** -> **Secrets**。
    *   填入以下内容 (将 JSON 中的值填入对应位置)：

```toml
[connections.gsheets]
spreadsheet = "你的表格完整URL"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n注意要把JSON里的换行符保留\n直接复制长字符串\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

---

## 🔧 故障排除 (Troubleshooting)

### Q1: 报错 `PermissionError`
**原因**：机器人没有权限访问表格。
**检查清单**：
1.  **API 未启用**：回到 Google Cloud Console，检查 **Google Sheets API** 和 **Google Drive API** 是否状态为 Enabled。
2.  **未 Share**：检查 Google Sheet 的 Share 列表里是否有机器人的邮箱，且权限是 **Editor**。

### Q2: 报错 `StreamlitAPIException: Secrets format error`
**原因**：TOML 格式错误。
**解决**：
1.  检查第一行是否写了 `[connections.gsheets]`。
2.  检查 `private_key` 是否只有一行（包含 `\n`），不要手动换行。

### Q3: 报错 `WorksheetNotFound`
**原因**：表格链接填错了，或者找不到 Sheet。
**解决**：确保 Secrets 里的 `spreadsheet` 链接是正确的，且表格中至少有一个 Sheet。