import streamlit as st
from views.login import login_page
from views.forum import forum_page
from views.dashboard import dashboard_page

# 页面配置
st.set_page_config(
    page_title="心桥 HeartBridge",
    page_icon="🌉",
    layout="wide"
)

def main():
    # 初始化 Session State
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["nickname"] = None

    # 路由控制
    if not st.session_state["logged_in"]:
        login_page()
    else:
        # 侧边栏导航
        with st.sidebar:
            st.title("🌉 心桥菜单")
            st.write(f"当前身份: **{st.session_state['role']}**")
            st.write(f"匿名昵称: **{st.session_state['nickname']}**")
            st.markdown("---")
            
            # 导航选项
            menu = st.radio("前往页面", ["问答广场", "科研看板"])
            
            st.markdown("---")
            if st.button("退出登录"):
                st.session_state.clear()
                st.rerun()
                
        # 根据选择渲染页面
        if menu == "问答广场":
            forum_page()
        elif menu == "科研看板":
            dashboard_page()

if __name__ == "__main__":
    main()
