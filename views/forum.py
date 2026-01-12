import streamlit as st
import pandas as pd
from utils.db import add_post, get_posts_by_role, like_post, unlike_post, init_db

def forum_page():
    """
    问答广场主页面
    """
    # 确保数据库是最新的
    init_db()

    # 初始化点赞记录 (Session 级)
    if "liked_posts" not in st.session_state:
        st.session_state["liked_posts"] = set()

    st.title("🌉 心桥广场")
    st.caption("跨越代沟，听见彼此的真心话")

    # --- 发帖区域 (折叠式) ---
    with st.expander("📝 我要提问 / 发个贴", expanded=False):
        _render_post_form()

    # --- 帖子展示区域 (Tabs) ---
    tab_child, tab_parent = st.tabs(["👦 孩子的心声", "👩 家长的困惑"])

    # Tab 1: 显示孩子发的贴 (供家长看/回)
    with tab_child:
        st.info("这里是孩子们的心里话。各位家长，请耐心倾听。")
        df_child = get_posts_by_role("孩子")
        _render_post_list(df_child, icon="👦")

    # Tab 2: 显示家长发的贴 (供孩子看/回)
    with tab_parent:
        st.info("这里是家长们的迷茫。孩子们，其实大人也不容易。")
        df_parent = get_posts_by_role("家长")
        _render_post_list(df_parent, icon="👩")

def _render_post_form():
    """
    渲染发帖表单
    """
    with st.form("post_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            title = st.text_input("标题/话题", placeholder="例如：关于手机的使用...")
        with col2:
            is_hidden = st.checkbox("绝对树洞模式", help="勾选后将隐藏你的昵称")
        
        content = st.text_area("正文内容", placeholder="在这里写下你的真实想法...", height=100)
        
        submitted = st.form_submit_button("发布 🚀")
        
        if submitted:
            if not title or not content:
                st.error("标题和内容不能为空哦！")
            else:
                # 获取当前用户信息
                current_role = st.session_state.get("role", "游客")
                current_nickname = st.session_state.get("nickname", "匿名用户")
                
                # 写入数据库
                add_post(current_role, current_nickname, title, content, is_hidden)
                
                st.success("发布成功！刷新页面即可看到。")
                st.rerun()

def _render_post_list(df, icon):
    """
    渲染帖子列表
    """
    if df.empty:
        st.write("还没有人发帖呢，做第一个发言的人吧！")
        return

    # 遍历 DataFrame 渲染每一行
    for index, row in df.iterrows():
        # 处理显示名称
        display_name = row['nickname']
        if row['is_hidden']:
            display_name = "某位" + row['role'] # 如：某位家长 / 某位孩子
            
        # 使用 chat_message 模拟对话气泡
        with st.chat_message(row['role'], avatar=icon):
            col_msg, col_like = st.columns([0.9, 0.1])
            
            with col_msg:
                st.markdown(f"**{row['title']}**")
                st.caption(f"{display_name} · {row['created_at']}")
                st.write(row['content'])
            
            with col_like:
                # 唯一的 key 防止冲突
                btn_key = f"like_{row['id']}"
                # 如果点赞数为空 (旧数据), 默认为 0
                likes = row['likes'] if pd.notna(row['likes']) else 0
                
                st.write(f"👍 {int(likes)}")
                
                # 判断当前用户是否已点赞
                post_id = row['id']
                is_liked = post_id in st.session_state["liked_posts"]
                
                if is_liked:
                    if st.button("💔", key=btn_key, help="取消点赞"):
                        unlike_post(post_id)
                        st.session_state["liked_posts"].remove(post_id)
                        st.rerun()
                else:
                    if st.button("❤️", key=btn_key, help="点赞"):
                        like_post(post_id)
                        st.session_state["liked_posts"].add(post_id)
                        st.rerun()
