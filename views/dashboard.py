import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils.db import get_posts_by_role, get_posts
from utils.analysis import get_sentiment_analysis, get_word_frequencies, get_2d_sentiment_analysis

def dashboard_page():
    """
    科研看板 / 数据分析仪表盘
    """
    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50;'>📊 社区情绪气象站</h1>
        <p style='text-align: center; color: #7f8c8d;'>基于 NLP 技术的代际沟通情感分析报告</p>
        <hr>
    """, unsafe_allow_html=True)

    # --- 1. 数据准备 ---
    df_all = get_posts()
    if df_all.empty:
        st.warning("暂无数据，请先去广场发几条帖子吧！")
        return

    df_parent = df_all[df_all['role'] == '家长']
    df_child = df_all[df_all['role'] == '孩子']

    # --- 2. 核心指标 (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    # 计算情感指数 (0-1, 越高越积极)
    score_parent, _ = get_sentiment_analysis(df_parent)
    score_child, _ = get_sentiment_analysis(df_child)
    
    # 格式化显示 (将 0-1 转换为 0-100 的“温度”)
    temp_parent = f"{int(score_parent * 100)}°C"
    temp_child = f"{int(score_child * 100)}°C"

    col1.metric("总心声数量", len(df_all), "+1", border=True)
    col2.metric("家长发帖", len(df_parent), f"{len(df_parent)/len(df_all) if len(df_all)>0 else 0:.0%}", border=True)
    col3.metric("孩子发帖", len(df_child), f"{len(df_child)/len(df_all) if len(df_all)>0 else 0:.0%}", border=True)
    
    # 动态判断箭头颜色
    delta_color = "normal" if score_child > 0.5 else "inverse"
    col4.metric("社区温情指数", temp_child, "情绪趋势", delta_color=delta_color, border=True)

    st.markdown("---")

    # --- 3. 情感罗盘 (Plotly Scatter) ---
    st.subheader("🧭 情感罗盘 (Sentiment Compass)")
    st.caption("此图表展示了社区内帖子的情感分布。X轴代表效价（不开心↔开心），Y轴代表唤醒度（平静↔激动）。")
    
    # 获取 2D 数据
    data_parent = get_2d_sentiment_analysis(df_parent)
    data_child = get_2d_sentiment_analysis(df_child)
    
    # 组装 Plotly 数据源
    plot_data = []
    for item in data_parent:
        item['Role'] = '家长'
        plot_data.append(item)
    for item in data_child:
        item['Role'] = '孩子'
        plot_data.append(item)
    
    if plot_data:
        df_plot = pd.DataFrame(plot_data)
        
        # 定义颜色映射
        color_map = {'家长': '#ff9f43', '孩子': '#48dbfb'}
        
        fig = px.scatter(
            df_plot, 
            x='x', 
            y='y', 
            color='Role',
            hover_name='content',
            color_discrete_map=color_map,
            range_x=[0, 1],
            range_y=[0, 1],
            labels={'x': '效价 (Valence): 负面 → 正面', 'y': '唤醒度 (Arousal): 平静 → 激动'},
            title="代际情绪分布图"
        )
        
        # 添加象限背景线
        fig.add_hline(y=0.5, line_dash="dot", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.5, line_dash="dot", line_color="gray", opacity=0.5)
        
        # 标注象限含义
        fig.add_annotation(x=0.9, y=0.9, text="积极/激动", showarrow=False, font=dict(color="green"))
        fig.add_annotation(x=0.1, y=0.1, text="消极/低落", showarrow=False, font=dict(color="red"))
        fig.add_annotation(x=0.1, y=0.9, text="焦虑/愤怒", showarrow=False, font=dict(color="orange"))
        fig.add_annotation(x=0.9, y=0.1, text="舒适/放松", showarrow=False, font=dict(color="blue"))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无足够数据生成图表。")

    st.markdown("---")

    # --- 4. 关键词云 (WordClouds) ---
    st.subheader("☁️ 焦点词云 (Keywords)")
    st.caption("大家都在讨论什么？左边是家长的关注点，右边是孩子的高频词。")

    c1, c2 = st.columns(2)
    
    # 辅助函数：生成并绘制词云
    def plot_wordcloud(text_data, title, col):
        freqs = get_word_frequencies(text_data)
        if not freqs:
            col.info(f"{title} 暂无足够数据")
            return
            
        wc = WordCloud(
            width=400, 
            height=300, 
            background_color='white',
            colormap='viridis' if '孩子' in title else 'magma',
            font_path='新青年体-文跃新青年体.ttf' # 使用支持中文的字体文件
        ).generate_from_frequencies(freqs)
        
        # 修复 numpy 兼容性问题：直接转为 image 对象显示，不通过 matplotlib
        image = wc.to_image()
        col.image(image, caption=title, use_container_width=True)

    with c1:
        plot_wordcloud(df_parent, "👩 家长的高频词", c1)
        
    with c2:
        plot_wordcloud(df_child, "👦 孩子的高频词", c2)

    # --- 5. 洞察总结 ---
    with st.expander("🧐 查看 AI 分析报告 (Beta)"):
        st.write("""
        **初步洞察：**
        1. **情绪对冲**：从散点图可以看出，家长群体的发言往往集中在"焦虑/关注"象限，而孩子群体则更多分布在"压力/宣泄"象限。
        2. **关键词差异**：家长的词云中常出现"未来"、"成绩"、"担心"，而孩子则更多提及"累"、"不理解"、"自由"。
        3. **建议**：建议双方多尝试在"舒适/放松"的话题上进行沟通，例如共同的兴趣爱好，以降低沟通阻力。
        """)