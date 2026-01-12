import streamlit as st
import pandas as pd
from utils.db import get_posts
from utils.analysis import get_sentiment_analysis, get_word_frequencies, get_2d_sentiment_analysis
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import os

# 设置中文字体 (仅为 Matplotlib 词云保留)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']

def dashboard_page():
    st.title("📊 科研看板 (Research Dashboard)")
    st.caption("基于 NLP 自然语言处理的代际沟通数据分析")

    df = get_posts()
    
    if df.empty:
        st.warning("暂无足够的数据进行分析，快去广场发帖吧！")
        return

    # --- 核心指标 ---
    avg_score, all_scores = get_sentiment_analysis(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("社区总帖子数", len(df))
    with col2:
        warmth_index = int(avg_score * 100)
        st.metric("社区温情指数", f"{warmth_index}%", delta=f"{warmth_index-50}%" if warmth_index != 50 else None)
    with col3:
        anxiety_count = len([s for s in all_scores if s < 0.4])
        anxiety_rate = int((anxiety_count / len(df)) * 100) if len(df) > 0 else 0
        st.metric("焦虑感知比例", f"{anxiety_rate}%")

    st.markdown("---")

    # --- 科研原理解读 ---
    with st.expander("📖 情感分析技术原理解读"):
        st.markdown("""
        **1. 核心指标定义**
        * **社区温情指数 (Warmth Index)**: 
            > 将所有帖子的平均情感得分 (0-1) 映射为百分比 (0-100%)。
            > * 指数 > 60%：表示社区整体氛围积极、温暖。
            > * 指数 < 40%：表示社区整体氛围低沉、充满压力。
        * **焦虑感知比例 (Anxiety Rate)**:
            > 统计所有帖子中，情感得分低于 **0.4 (负面/焦虑)** 的帖子占比。
            > * 这个比例越高，说明社区中需要心理疏导的用户越多。

        **2. 二维情绪模型 (Russell Map)**
        > 我们采用 Russell 的环状情绪模型对每条帖子进行坐标定位：
        > * **横轴 (Valence)**: 代表愉悦度，从消极(0)到积极(1)。
        > * **纵轴 (Arousal)**: 代表强度，从平静(0)到激动(1)。
        > * 通过这个模型，我们可以区分“愤怒”(高唤醒负面)和“抑郁”(低唤醒负面)。
        """)

    # --- 科研分析核心区 ---
    st.markdown("### 📊 深度情感多维分析")
    
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.write("**🧭 交互式心理模型 (Russell Map)**")
        points = get_2d_sentiment_analysis(df)
        if points:
            points_df = pd.DataFrame(points)
            # 使用 Plotly 创建交互式散点图
            fig_2d = px.scatter(
                points_df, x='x', y='y',
                hover_data={'content': True, 'x': ':.2f', 'y': ':.2f'},
                labels={'x': '效价 (消极->积极)', 'y': '唤醒度 (平静->激动)'},
                range_x=[0, 1], range_y=[0, 1],
                template="plotly_white",
                color_discrete_sequence=['#636EFA']
            )
            
            # 添加象限辅助线
            fig_2d.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
            fig_2d.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
            
            # 添加象限标注
            annotations = [
                dict(x=0.15, y=0.9, text="焦虑/愤怒", showarrow=False, font=dict(color="red")),
                dict(x=0.85, y=0.9, text="兴奋/快乐", showarrow=False, font=dict(color="green")),
                dict(x=0.15, y=0.1, text="抑郁/疲惫", showarrow=False, font=dict(color="blue")),
                dict(x=0.85, y=0.1, text="安详/放松", showarrow=False, font=dict(color="purple"))
            ]
            fig_2d.update_layout(annotations=annotations, height=400, margin=dict(l=0, r=0, t=30, b=0))
            
            st.plotly_chart(fig_2d, use_container_width=True)
        else:
            st.write("数据加载中...")

    with col_right:
        st.write("**📈 社区情绪分布 (效价分布)**")
        hist_df = pd.DataFrame(all_scores, columns=["sentiment"])
        if not hist_df.empty:
            counts = hist_df["sentiment"].value_counts(bins=5).sort_index()
            sentiment_labels = ["😩 焦虑", "😕 烦恼", "😐 平淡", "🙂 期待", "🥰 温暖"]
            
            if len(counts) == 5:
                chart_data = pd.DataFrame({"数量": counts.values}, index=sentiment_labels)
            else:
                labels = [f"{idx.left:.1f}-{idx.right:.1f}" for idx in counts.index]
                chart_data = pd.DataFrame({"数量": counts.values}, index=labels)

            st.bar_chart(chart_data, height=320) # 限制高度
        else:
            st.write("暂无数据")

    st.markdown("---")

    # --- 热门话题排行 (替代词云) ---
    st.subheader("🔥 社区热门话题榜 (Top 15)")
    word_counts = get_word_frequencies(df)
    
    if word_counts:
        # 将 Counter 转为 DataFrame
        wc_df = pd.DataFrame(list(word_counts.items()), columns=['关键词', '出现次数'])
        # 排序并取前 15
        wc_df = wc_df.sort_values(by='出现次数', ascending=False).head(15)
        
        # 使用 Plotly 绘制水平条形图
        fig_bar = px.bar(
            wc_df, 
            x='出现次数', 
            y='关键词', 
            orientation='h',
            text='出现次数', # 在条形末尾显示数字
            color='出现次数', # 颜色渐变
            color_continuous_scale='Blues' # 蓝色系渐变
        )
        
        # 翻转 Y 轴，让第一名在最上面
        fig_bar.update_layout(yaxis=dict(autorange="reversed"), height=500)
        
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("暂无足够的文本数据来生成话题榜。")
    
    # --- 数据透视 ---
    st.markdown("---")

    # --- 数据透视 ---
    st.markdown("---")
    st.subheader("📋 原始数据摘要 (仅科研用途)")
    st.dataframe(df[['role', 'title', 'created_at']], use_container_width=True)
