import streamlit as st
from utils.nickname import generate_nickname

def login_page():
    """
    渲染登录/身份选择页面 (现代扁平化风格)
    """
    # 注入自定义 CSS
    _load_custom_css()

    # --- Hero Section (顶部宽幅Banner) ---
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">🌉 心桥 HeartBridge</h1>
            <p class="hero-subtitle">跨越代沟，听见彼此最真实的声音</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 引导语 ---
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 3rem; color: #555;">
            这是一个完全匿名的树洞社区。<br>
            在这里，身份仅仅是一个标签，我们更在乎你的心声。
        </div>
    """, unsafe_allow_html=True)
    
    # --- 身份选择卡片区域 ---
    # 使用 container 居中限制宽度，避免在大屏上太散
    with st.container():
        col1, col_space, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            st.markdown("""
                <div class="role-card card-parent">
                    <div class="card-icon">☕</div>
                    <h3>我是家长</h3>
                    <p>希望能听懂孩子的话<br>或者想分享育儿的苦恼</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("进入社区 (家长通道)", use_container_width=True, key="btn_parent"):
                _login_action("家长")
            
        with col2:
            st.markdown("""
                <div class="role-card card-child">
                    <div class="card-icon">🪁</div>
                    <h3>我是孩子</h3>
                    <p>有些话不想当面说<br>但希望有人能懂我的压力</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("进入社区 (孩子通道)", use_container_width=True, key="btn_child"):
                _login_action("孩子")

def _load_custom_css():
    st.markdown("""
        <style>
        /* 全局字体优化 */
        html, body, [class*="css"] {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }

        /* 隐藏 Streamlit 默认的顶部 Padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        /* Hero Section 样式 */
        .hero-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(118, 75, 162, 0.2);
            margin-bottom: 2rem;
        }
        .hero-title {
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
            color: white !important;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            font-weight: 300;
            opacity: 0.9;
        }

        /* 角色卡片通用样式 */
        .role-card {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 1rem;
            border: 1px solid #eee;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .role-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .card-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .role-card h3 {
            font-size: 1.5rem !important;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .role-card p {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* 特定角色配色微调 */
        .card-parent {
            border-top: 5px solid #FF9F43; /* 橙色 */
        }
        .card-child {
            border-top: 5px solid #48dbfb; /* 蓝色 */
        }

        /* 按钮美化 (尝试覆盖 Streamlit 默认样式) */
        div.stButton > button {
            border-radius: 25px;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            font-weight: 600;
            border: none;
            transition: all 0.3s;
        }
        /* 针对不同按钮的特定颜色不太好通过纯 CSS 这里区分，因为 Streamlit key 不直接暴露 class
           但我们可以通过通用样式提升质感 */
        div.stButton > button:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: scale(1.02);
        }

        </style>
    """, unsafe_allow_html=True)

def _login_action(role):
    """
    处理登录动作：生成昵称，写入Session，并持久化到 URL
    """
    nickname = generate_nickname(role)
    
    # 1. 写入 Session (用于当前运行逻辑)
    st.session_state["role"] = role
    st.session_state["nickname"] = nickname
    st.session_state["logged_in"] = True
    
    # 2. 写入 URL Query Params (用于刷新后恢复)
    st.query_params["role"] = role
    st.query_params["nickname"] = nickname
    
    st.success(f"身份确认成功！你的匿名身份是：**{nickname}**")
    st.rerun()
