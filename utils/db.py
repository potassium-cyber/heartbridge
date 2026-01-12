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
    SQLite: 建表 (posts, comments)。
    GSheets: 检查 Worksheet 是否存在。
    """
    if USE_GSHEETS:
        # Google Sheets 模式由连接器自动管理
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            # 这里仅做连接测试，实际表结构由读写操作动态决定
            pass 
        except Exception as e:
            print(f"GSheets 连接警告: {e}")
    else:
        # SQLite 模式
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # 帖子表
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
        
        # 评论表
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                role TEXT NOT NULL,
                nickname TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            # 默认读取第一个 worksheet
            df = conn.read(ttl=0)
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['id'] = df['id'].astype(str)
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
        "id": str(int(datetime.now().timestamp() * 1000)),
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

# --- 评论相关功能 ---

def get_comments(post_id):
    """获取指定帖子的所有评论"""
    post_id = str(post_id)
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            # 假设评论存在名为 'comments' 的 worksheet 中
            # 注意：Streamlit GSheet 连接器默认读第一个 sheet，读其他 sheet 需要指定 worksheet 参数
            df = conn.read(worksheet="comments", ttl=0)
            if not df.empty:
                df['post_id'] = df['post_id'].astype(str)
                # 筛选当前帖子的评论
                df = df[df['post_id'] == post_id]
                df = df.sort_values(by='created_at', ascending=True)
                return df
        except Exception:
            # 如果 worksheet 不存在或报错
            return pd.DataFrame(columns=['id', 'post_id', 'role', 'nickname', 'content', 'created_at'])
        return pd.DataFrame()
    else:
        conn = sqlite3.connect(DB_FILE)
        try:
            df = pd.read_sql_query("SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC", conn, params=(post_id,))
        except:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

def add_comment(post_id, role, nickname, content):
    """新增评论"""
    new_data = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "post_id": str(post_id),
        "role": role,
        "nickname": nickname,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if USE_GSHEETS:
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            df = conn.read(worksheet="comments", ttl=0)
        except:
            df = pd.DataFrame(columns=['id', 'post_id', 'role', 'nickname', 'content', 'created_at'])
            
        updated_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        conn.update(worksheet="comments", data=updated_df)
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO comments (post_id, role, nickname, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (post_id, role, nickname, content, datetime.now()))
        conn.commit()
        conn.close()