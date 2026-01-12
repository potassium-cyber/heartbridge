import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import random

# 本地 SQLite 路径
DB_FILE = 'heartbridge.db'

# 检查是否配置了 Google Sheets 连接
# 在 Streamlit Cloud 的 Secrets 里配置了 [connections.gsheets] 才会生效
USE_GSHEETS = False
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    from streamlit_gsheets import GSheetsConnection
    USE_GSHEETS = True

def init_db():
    """
    初始化数据库。
    SQLite: 建表。
    GSheets: 检查 Worksheet 是否存在，不存在则创建 Header。
    """
    if USE_GSHEETS:
        # Google Sheets 模式由连接器自动管理，通常只需要确保 Sheet 存在
        # 这里我们可以做一个简单的连接测试
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            # 尝试读取，如果为空或报错，说明可能是新表
            df = conn.read(ttl=0) 
            if df.empty or set(df.columns) != {'id', 'role', 'nickname', 'title', 'content', 'is_hidden', 'created_at', 'likes'}:
                # 如果是空表，初始化表头 (但这步通常建议手动在 Google Sheet 第一行填好)
                # 这里的代码假设用户已经在 Google Sheet 里建好了对应的列名，或者接受自动创建
                pass
        except Exception as e:
            print(f"GSheets 连接警告: {e}")
    else:
        # SQLite 模式
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                nickname TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                is_hidden BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0
            )
        ''')
        # 迁移检查
        try:
            c.execute("SELECT likes FROM posts LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0")
        conn.commit()
        conn.close()

def get_posts():
    """获取所有帖子"""
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            # ttl=0 确保获取最新数据
            df = conn.read(ttl=0)
            # 确保数据类型正确
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['id'] = df['id'].astype(str) # ID 转字符串防止匹配错误
                df = df.sort_values(by='created_at', ascending=False)
            return df
        except Exception:
            return pd.DataFrame(columns=['id', 'role', 'nickname', 'title', 'content', 'is_hidden', 'created_at', 'likes'])
    else:
        conn = sqlite3.connect(DB_FILE)
        try:
            df = pd.read_sql_query("SELECT * FROM posts ORDER BY created_at DESC", conn)
            df['id'] = df['id'].astype(str)
        except:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

def get_posts_by_role(target_role):
    """按角色筛选"""
    df = get_posts()
    if df.empty:
        return df
    return df[df['role'] == target_role]

def add_post(role, nickname, title, content, is_hidden=False):
    """新增帖子"""
    new_data = {
        "id": str(int(datetime.now().timestamp() * 1000)), # 使用时间戳生成唯一 ID
        "role": role,
        "nickname": nickname,
        "title": title,
        "content": content,
        "is_hidden": is_hidden,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "likes": 0
    }
    
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = get_posts()
        # 追加新行
        updated_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        conn.update(data=updated_df)
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO posts (role, nickname, title, content, is_hidden, created_at, likes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (role, nickname, title, content, is_hidden, datetime.now(), 0))
        conn.commit()
        conn.close()

def like_post(post_id):
    """点赞 (+1)"""
    post_id = str(post_id)
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = get_posts()
        if not df.empty:
            # 找到对应的行并修改
            mask = df['id'] == post_id
            if mask.any():
                df.loc[mask, 'likes'] = df.loc[mask, 'likes'].astype(int) + 1
                conn.update(data=df)
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()

def unlike_post(post_id):
    """取消点赞 (-1)"""
    post_id = str(post_id)
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = get_posts()
        if not df.empty:
            mask = df['id'] == post_id
            if mask.any():
                current_likes = int(df.loc[mask, 'likes'].values[0])
                df.loc[mask, 'likes'] = max(0, current_likes - 1)
                conn.update(data=df)
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE posts SET likes = MAX(0, likes - 1) WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()