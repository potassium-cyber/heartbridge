import sqlite3
import pandas as pd
from datetime import datetime

# 数据库文件路径
DB_FILE = 'heartbridge.db'

def init_db():
    """
    初始化数据库：如果表不存在则创建。
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 创建帖子表 (posts)
    # 字段包含：id, 角色(role), 昵称(nickname), 标题(title), 内容(content), 是否隐藏(is_hidden), 创建时间(created_at), 点赞数(likes)
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
    
    # 简单的 Schema 迁移检查：如果 likes 列不存在，则添加
    # (为了兼容旧的数据库文件)
    try:
        c.execute("SELECT likes FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0")
        conn.commit()
    
    conn.commit()
    conn.close()

def add_post(role, nickname, title, content, is_hidden=False):
    """
    新增一条提问/帖子。
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 插入数据
    c.execute('''
        INSERT INTO posts (role, nickname, title, content, is_hidden, created_at, likes)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (role, nickname, title, content, is_hidden, datetime.now()))
    
    conn.commit()
    conn.close()

def like_post(post_id):
    """
    给指定帖子点赞 (+1)
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def unlike_post(post_id):
    """
    取消点赞 (-1)
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 确保点赞数不为负
    c.execute("UPDATE posts SET likes = MAX(0, likes - 1) WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_posts():
    """
    获取所有帖子列表。
    
    Returns:
        pd.DataFrame: 包含所有帖子数据的 DataFrame
    """
    conn = sqlite3.connect(DB_FILE)
    
    # 使用 pandas 读取 sql，方便后续处理
    try:
        df = pd.read_sql_query("SELECT * FROM posts ORDER BY created_at DESC", conn)
    except Exception as e:
        print(f"读取数据失败: {e}")
        df = pd.DataFrame() # 返回空 DataFrame 防止报错
    finally:
        conn.close()
        
    return df

def get_posts_by_role(target_role):
    """
    根据发帖人角色筛选帖子。
    例如：在“孩子的心声”板块，应该显示 role='孩子' 的帖子。
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        query = "SELECT * FROM posts WHERE role = ? ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=(target_role,))
    except Exception as e:
        print(f"读取分角色数据失败: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# 如果直接运行此文件，则初始化数据库（用于测试）
if __name__ == "__main__":
    init_db()
    print("数据库已初始化。")
    
    # 测试插入一条数据
    # add_post("孩子", "还没有睡醒的考拉", "关于学习", "我总是感觉压力很大...", False)
    # print("测试数据已插入。")
    
    # 测试读取
    # print(get_posts())
