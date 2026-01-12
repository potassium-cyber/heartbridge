# GEMINI.md - 项目上下文定义文件

## 1. 项目概况 (Project Overview)

* **项目名称**：心桥 (HeartBridge) —— 基于代际视角的匿名亲子问答社区。
* **项目背景**：这是一个为学生竞赛准备的项目。旨在解决家庭教育中“孩子不愿说，家长听不到”的痛点。
* **核心目标**：创建一个完全匿名的“树洞”社区，将用户分为“家长”和“孩子”两个阵营。通过跨角色的提问与回答（如：别的家长回答你的孩子的问题），打破沟通壁垒。
* **科研价值**：后台需自动采集问答数据，通过 NLP（自然语言处理）技术分析高频“忌讳词汇”和“情绪温度”，为教育心理学研究提供数据支持。

## 2. 技术栈 (Tech Stack)

* **前端框架**：Streamlit (必须)。
* **编程语言**：Python 3.9+。
* **数据存储 (MVP阶段)**：
* 方案 A (推荐)：**Google Sheets** (通过 `st.connection` 连接，实现云端实时读写，方便多人同时比赛演示)。
* 方案 B (备选)：**SQLite** (本地文件数据库，开发简单)。


* **核心库**：
* `streamlit` (Web界面)
* `pandas` (数据处理)
* `snownlp` (中文情感分析)
* `wordcloud` (词云生成)
* `faker` (用于生成随机匿名昵称，或自定义生成逻辑)


## 3. 功能需求 (Functional Requirements)

### 3.1 角色与认证系统 (Role & Auth)

* **匿名登录**：无需手机号，用户进入网站仅需选择身份标签：
* 【我是家长】
* 【我是孩子】


* **自动昵称生成**：系统根据身份分配随机且有趣的昵称（禁止实名）。
* 家长池示例：*焦虑的猫头鹰、守望的长颈鹿*
* 孩子池示例：*想要自由的风、还没睡醒的考拉*


* **Session管理**：使用 `st.session_state` 记录当前用户的身份和昵称。

### 3.2 问答广场 (The Forum Feed)

* **界面布局**：使用 `st.tabs` 分为两个主要板块：
* **“孩子的心声”**：显示孩子发的贴，家长可以回复。
* **“家长的困惑”**：显示家长发的贴，孩子可以回复。


* **交互形式**：使用 `st.chat_message` 组件展示对话，模拟聊天室的亲切感。
* **内容发布**：简单的表单，包含：主题（标签）、正文、是否开启“绝对树洞模式”（开启后连昵称都隐藏）。

### 3.3 科研仪表盘 (Research Dashboard)

* *此功能面向比赛评委和研究者展示。*
* **词云图**：展示当前社区内讨论最激烈的话题（如：手机、早恋、成绩）。
* **情绪分析**：通过 `snownlp` 评分，展示当前社区的“焦虑指数”或“温情指数”走势。

## 4. 目录结构规范 (Directory Structure)

建议使用 `st.navigation` 进行多页面管理：

```text
HeartBridge/
├── main.py              # 入口文件，负责路由分发 (st.navigation)
├── requirements.txt     # 依赖库
├── .streamlit/
│   └── secrets.toml     # 存放数据库连接密钥
├── utils/
│   ├── db.py            # 封装所有数据库读写操作 (CRUD)
│   ├── nickname.py      # 随机昵称生成逻辑
│   └── analysis.py      # 情感分析与词云逻辑
└── views/
    ├── login.py         # 身份选择页
    ├── forum.py         # 问答广场主页
    └── dashboard.py     # 数据分析看板

```

## 5. 开发路线图 (Roadmap for AI Assistance)

当请求 Gemini 协助写代码时，请遵循以下顺序：

1. **Phase 1 - 数据层打通**：编写 `utils/db.py`，实现向 Google Sheets (或 CSV/SQLite) 写入一条“提问”和读取“提问列表”的功能。
2. **Phase 2 - 身份与昵称**：完成 `views/login.py`，实现随机昵称分配并存入 Session。
3. **Phase 3 - 核心交互**：利用 `st.chat_message` 完成 `views/forum.py`，实现发帖和回帖的 UI。
4. **Phase 4 - 科研可视化**：编写 `views/dashboard.py`，接入 NLP 分析库。

## 6. 编码规范 (Coding Style)

* **注释**：关键逻辑必须使用**中文注释**，方便学生理解。
* **模块化**：不要把所有代码写在一个文件里，UI 和 逻辑 (Utils) 要分离。
* **美观性**：默认开启 `layout="wide"`，并在适当位置使用 `st.info` / `st.warning` 提示信息。

## 8. 部署指南 (Deployment Guide)

为了实现云端数据的持久化保存，本项目支持 **Google Sheets** 作为数据库。部署步骤如下：

### 8.1 准备 Google Sheet
1.  创建一个新的 Google Sheet 表格。
2.  第一行必须填写以下表头（Header）：
    `id`, `role`, `nickname`, `title`, `content`, `is_hidden`, `created_at`, `likes`
3.  将该表格设置为“任何人有链接均可编辑” (或者仅分享给 Service Account 邮箱，更安全)。
4.  记录下表格 URL。

### 8.2 获取 API 密钥
1.  前往 [Google Cloud Console](https://console.cloud.google.com/)。
2.  创建一个新项目，并启用 **Google Sheets API** 和 **Google Drive API**。
3.  创建一个 **Service Account**，并下载 JSON 格式的密钥文件。

### 8.3 部署到 Streamlit Cloud
1.  将代码推送到 GitHub。
2.  登录 [Streamlit Community Cloud](https://share.streamlit.io/)，关联仓库并点击 Deploy。
3.  在部署界面的 **Advanced Settings -> Secrets** 中，填入以下配置：

```toml
[connections.gsheets]
spreadsheet = "你的Google表格公开链接"
type = "service_account"
project_id = "xxx"
private_key_id = "xxx"
private_key = "xxx"
client_email = "xxx"
client_id = "xxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "xxx"
```
*(注：只需将下载的 JSON 文件内容复制并转换为 TOML 格式填入即可)*

### 8.4 本地运行与云端模式切换
*   **本地模式**：如果不配置 Secrets，系统自动默认使用本地 `heartbridge.db` (SQLite)，方便开发。
*   **云端模式**：一旦配置了 `[connections.gsheets]`，系统自动切换为 Google Sheets 存储。
