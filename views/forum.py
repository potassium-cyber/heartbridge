import streamlit as st
import pandas as pd
from utils.db import add_post, get_posts_by_role, like_post, unlike_post, init_db, add_comment, get_comments

def forum_page():
    """
    问答广场主页面 (优化UI版)
    """
    # 注入样式
    _load_forum_css()
    
    # 确保数据库是最新的
    init_db()

    # 初始化点赞记录 (Session 级)
    if "liked_posts" not in st.session_state:
        st.session_state["liked_posts"] = set()

    # 顶部标题区
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h2 style="margin:0;">🌉 心桥广场</h2>
            <p style="color: #666; font-size: 0.9rem;">在这里，每一份心声都值得被听见</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 发帖区域 (样式优化) ---
    with st.expander("📝 我要提问 / 发个贴", expanded=False):
        _render_post_form()

    # --- 帖子展示区域 (Tabs) ---
    st.write("") # Spacer
    tab_child, tab_parent = st.tabs(["👦 孩子的心声", "👩 家长的困惑"])

    # Tab 1: 显示孩子发的贴
    with tab_child:
        st.markdown('<div style="padding: 10px; background-color: #e3f2fd; border-radius: 8px; color: #1565c0; margin-bottom: 20px; font-size: 0.9rem;">💡 这里是孩子们的专属频道。各位家长，请暂时放下评判，用心倾听。</div>', unsafe_allow_html=True)
        df_child = get_posts_by_role("孩子")
        _render_post_list(df_child, role_type="child")

    # Tab 2: 显示家长发的贴
    with tab_parent:
        st.markdown('<div style="padding: 10px; background-color: #fff3e0; border-radius: 8px; color: #ef6c00; margin-bottom: 20px; font-size: 0.9rem;">💡 这里是家长们的树洞。孩子们，其实大人的世界也有迷茫。</div>', unsafe_allow_html=True)
        df_parent = get_posts_by_role("家长")
        _render_post_list(df_parent, role_type="parent")

def _load_forum_css():
    st.markdown("""
        <style>
        /* 帖子卡片容器 */
        .post-card {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .post-card:hover {
            box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        }
        
        /* 孩子贴配色 (清爽蓝) */
        .card-child {
            background-color: #ffffff;
            border-left: 5px solid #48dbfb;
        }
        /* 家长贴配色 (温暖橙) */
        .card-parent {
            background-color: #ffffff;
            border-left: 5px solid #ff9f43;
        }

        /* 标题样式 */
        .post-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }

        /* 元数据 (昵称时间) */
        .post-meta {
            font-size: 0.85rem;
            color: #95a5a6;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* 正文 */
        .post-content {
            font-size: 1rem;
            line-height: 1.6;
            color: #34495e;
            white-space: pre-wrap; /* 保留换行 */
        }

        /* 标签/Role Badge */
        .role-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            color: white;
        }
        .badge-child { background-color: #48dbfb; }
        .badge-parent { background-color: #ff9f43; }
        
        /* 评论区样式 */
        .comment-box {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        .comment-meta {
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

def _render_post_form():
    """
    渲染发帖表单 (保持逻辑，微调UI)
    """
    with st.form("post_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            title = st.text_input("标题", placeholder="给你的心事起个标题吧...")
        with col2:
            st.write("") 
            st.write("")
            is_hidden = st.checkbox("🎭 绝对匿名", help="勾选后隐藏昵称")
        
        content = st.text_area("正文", placeholder="在这里写下你的真实想法...", height=120)
        
        submitted = st.form_submit_button("发布心声 🚀", use_container_width=True)
        
        if submitted:
            if not title or not content:
                st.error("标题和内容不能为空哦！")
            else:
                current_role = st.session_state.get("role", "游客")
                current_nickname = st.session_state.get("nickname", "匿名用户")
                add_post(current_role, current_nickname, title, content, is_hidden)
                st.success("发布成功！")
                st.rerun()

def _render_post_list(df, role_type):
    """
    渲染帖子列表
    """
    if df.empty:
        st.info("👋 还没有内容，快来发布第一条心声吧！")
        return

    # 遍历 DataFrame 渲染每一行
    for index, row in df.iterrows():
        # 处理显示数据
        display_name = row['nickname']
        if row['is_hidden']:
            display_name = "某位" + ("家长" if row['role']=="家长" else "孩子")
        
        post_id = row['id']
        likes = row['likes'] if pd.notna(row['likes']) else 0
        created_at = row['created_at']

        # 获取评论
        comments_df = get_comments(post_id)
        comment_count = len(comments_df)

        # CSS 类名选择
        card_class = "card-parent" if role_type == "parent" else "card-child"
        badge_class = "badge-parent" if role_type == "parent" else "badge-child"
        role_label = "家长" if role_type == "parent" else "孩子"

        # --- 开始渲染卡片 ---
        with st.container():
            # 上半部分：纯 HTML 展示内容
            st.markdown(f"""
                <div class="post-card {card_class}">
                    <div class="post-title">{row['title']}</div>
                    <div class="post-meta">
                        <span class="role-badge {badge_class}">{role_label}</span>
                        <span>{display_name}</span>
                        <span>•</span>
                        <span>{created_at}</span>
                    </div>
                    <div class="post-content">{row['content']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- 交互区 (点赞 + 评论) ---
            col_like, col_spacer = st.columns([0.2, 0.8])
            with col_like:
                btn_key = f"like_{post_id}"
                is_liked = post_id in st.session_state["liked_posts"]
                
                if is_liked:
                    if st.button(f"❤️ {int(likes)}", key=btn_key):
                        unlike_post(post_id)
                        st.session_state["liked_posts"].remove(post_id)
                        st.rerun()
                else:
                    if st.button(f"🤍 {int(likes)}", key=btn_key):
                        like_post(post_id)
                        st.session_state["liked_posts"].add(post_id)
                        st.rerun()
            
            # --- 评论区 (Expander) ---
            with st.expander(f"💬 评论 ({comment_count})", expanded=False):
                # 1. 显示已有评论
                if not comments_df.empty:
                    for c_idx, c_row in comments_df.iterrows():
                        c_role = c_row['role']
                        c_nick = c_row['nickname']
                        c_content = c_row['content']
                        c_badge_color = "#48dbfb" if c_role == "孩子" else "#ff9f43"
                        
                        st.markdown(f"""
                            <div class="comment-box">
                                <div class="comment-meta">
                                    <span style="color:{c_badge_color}; font-weight:bold;">{c_nick}</span> 说:
                                </div>
                                <div>{c_content}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("暂无评论，来抢沙发吧~")
                
                # 2. 发送新评论表单
                # 使用唯一的 key 防止冲突
                with st.form(key=f"comment_form_{post_id}", clear_on_submit=True):
                    new_comment = st.text_input("写下你的看法...", placeholder="友善评论，温暖你我")
                    submitted_comment = st.form_submit_button("发送")
                    if submitted_comment and new_comment:
                        current_role = st.session_state.get("role", "游客")
                        current_nickname = st.session_state.get("nickname", "匿名用户")
                        add_comment(post_id, current_role, current_nickname, new_comment)
                        st.success("评论成功！")
                        st.rerun()
            
            st.markdown("---") # 分割线
