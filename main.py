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
    # --- 会话恢复逻辑 (解决刷新掉线问题) ---
    # 如果 Session 中没有登录状态，但 URL 参数里有，则尝试恢复
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["nickname"] = None

    if not st.session_state["logged_in"]:
        # 检查 URL 参数
        qp = st.query_params
        if "role" in qp and "nickname" in qp:
            st.session_state["role"] = qp["role"]
            st.session_state["nickname"] = qp["nickname"]
            st.session_state["logged_in"] = True
            st.rerun() # 恢复后立即刷新以更新界面状态

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
                st.query_params.clear() # 同时清空 URL 参数
                st.rerun()
                
        # 根据选择渲染页面
        if menu == "问答广场":
            forum_page()
        elif menu == "科研看板":
            dashboard_page()

if __name__ == "__main__":
    main()
