import streamlit as st
from utils.nickname import generate_nickname

def login_page():
    """
    渲染登录/身份选择页面
    """
    st.header("🌉 欢迎来到心桥 (HeartBridge)")
    st.subheader("在这里，听见彼此真实的心声")
    st.markdown("---")
    
    st.info("💡 这是一个完全匿名的社区。请选择你的身份，我们将为你生成一个专属的“树洞马甲”。")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 我是家长 👩‍🦳👨‍🦱")
        st.write("希望能听懂孩子的话，或者想分享育儿的苦恼。")
        if st.button("进入社区 (家长通道)", use_container_width=True):
            _login_action("家长")
            
    with col2:
        st.markdown("### 我是孩子 👧👦")
        st.write("有些话不想当面说，但希望有人能懂我的压力。")
        if st.button("进入社区 (孩子通道)", use_container_width=True):
            _login_action("孩子")

def _login_action(role):
    """
    处理登录动作：生成昵称，写入Session，刷新页面
    """
    nickname = generate_nickname(role)
    
    # 写入 Session
    st.session_state["role"] = role
    st.session_state["nickname"] = nickname
    st.session_state["logged_in"] = True
    
    st.success(f"身份确认成功！你的匿名身份是：**{nickname}**")
    st.rerun()
