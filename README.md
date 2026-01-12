# 🌉 心桥 (HeartBridge)

> **基于代际视角的匿名亲子问答社区与情感分析平台**

[![Streamlit App](https://static.streamlit.io/badge_streamlit.svg)](https://share.streamlit.io/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 项目立意

在现代家庭教育中，常面临“孩子不愿说，家长听不到”的痛点。**心桥 (HeartBridge)** 旨在创建一个完全匿名的“树洞”社区：
*   **跨角色沟通**：打破“面对面”的权力不对等，通过跨角色的提问与回答（如：别的家长回答你的孩子的问题），消除沟通壁垒。
*   **科研赋能**：利用自然语言处理 (NLP) 技术，实时监控社区情绪温度，为家庭教育心理学研究提供真实的数据支撑。

---

## ✨ 核心功能

### 1. 🎭 匿名身份系统
*   **智能昵称**：基于角色（家长/孩子）随机生成可爱的匿名身份（如：*焦虑的猫头鹰*、*想要自由的风*）。
*   **绝对树洞**：支持开启“绝对匿名”模式，连马甲也不显示。

### 2. 💬 问答广场 (The Forum Feed)
*   **气泡式交互**：采用聊天室风格，降低表达负担。
*   **分板块展示**：区分“孩子的心声”与“家长的困惑”，支持点赞与互动。

### 3. 📊 科研仪表盘 (Research Dashboard)
*   **二维心理模型**：基于 **Russell 环状情绪模型**，通过“效价-唤醒度”双维度对用户情绪进行精确定位。
*   **情绪分布图**：5级情感分层，直观展示社区当前的焦虑或温情指数。
*   **话题排行榜**：实时提取高频讨论词条，捕捉代际冲突的热点话题。

---

## 🛠️ 技术栈

*   **前端框架**: [Streamlit](https://streamlit.io/) (交互式 Web 应用)
*   **数据存储**: SQLite (本地开发) / [Google Sheets](https://www.google.com/sheets/about/) (云端部署)
*   **情感分析**: [SnowNLP](https://github.com/isnowfy/snownlp) + 专家规则校准
*   **数据可视化**: [Plotly](https://plotly.com/python/) (交互式图表)
*   **文本处理**: [Jieba](https://github.com/fxsjy/jieba) (中文分词)

---

## 🚀 快速开始

### 本地运行
1. **克隆仓库**:
   ```bash
   git clone https://github.com/your-username/heartbridge.git
   cd heartbridge
   ```

2. **安装依赖**:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **启动应用**:
   ```bash
   python -m streamlit run main.py
   ```

### 注入测试数据
为了测试科研看板的分析效果，可运行测试脚本：
```bash
python utils/seed_data.py
```

---

## 🧭 心理学分析原理

本项目的情感分析不仅停留在“正负面”，而是引入了心理学经典模型：
*   **Valence (效价)**: 衡量情绪的积极/消极程度。
*   **Arousal (唤醒度)**: 衡量情绪的强烈/平静程度。

通过二者结合，我们可以区分出 **“焦虑/愤怒”** (高唤醒负面) 与 **“抑郁/疲惫”** (低唤醒负面)，从而为教育干预提供更精准的分类。

---

## 📂 目录结构

```text
HeartBridge/
├── main.py              # 入口文件，负责路由分发
├── requirements.txt     # 项目依赖
├── utils/
│   ├── db.py            # 数据库适配器 (SQLite/GSheets)
│   ├── analysis.py      # 二维情感分析与文本处理逻辑
│   ├── nickname.py      # 随机昵称生成算法
│   └── seed_data.py     # 测试数据生成器
└── views/
    ├── login.py         # 身份选择页
    ├── forum.py         # 问答广场主页
    └── dashboard.py     # 交互式科研看板
```

---

## 🛡️ 开源协议
本项目采用 [MIT License](LICENSE) 协议。
