import streamlit as st
import pandas as pd
from utils.db import get_posts
from utils.analysis import get_sentiment_analysis, get_word_frequencies, get_2d_sentiment_analysis
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# 设置中文字体 (尝试解决 Matplotlib 中文乱码)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'PingFang SC', 'Heiti TC', 'Droid Sans Fallback']
plt.rcParams['axes.unicode_minus'] = False 

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
        # 情感分转为 0-100 的“温暖指数”
        warmth_index = int(avg_score * 100)
        st.metric("社区温情指数", f"{warmth_index}%", delta=f"{warmth_index-50}%" if warmth_index != 50 else None)
    with col3:
        # 统计焦虑帖子的比例 (得分低于 0.4 视为潜在焦虑)
        anxiety_count = len([s for s in all_scores if s < 0.4])
        anxiety_rate = int((anxiety_count / len(df)) * 100) if len(df) > 0 else 0
        st.metric("焦虑感知比例", f"{anxiety_rate}%")

    st.markdown("---")

    # --- 科研原理解读 ---
    with st.expander("📖 情感分析技术原理解读"):
        st.markdown("""
        **Q: 什么是“温情指数”？**
        > 我们使用 NLP (自然语言处理) 技术分析帖子内容的情感倾向。
        > * **0.0 - 0.2 (焦虑/消极)**: 通常包含压力、抱怨或求助的关键词。
        > * **0.4 - 0.6 (中性/平淡)**: 陈述事实，情绪波动不大。
        > * **0.8 - 1.0 (温暖/积极)**: 包含鼓励、感谢或开心的内容。
        """)

    # --- 科研分析核心区 ---
    st.markdown("### 📊 深度情感多维分析")
    
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.write("**🧭 深度心理模型 (Russell 环状图)**")
        points = get_2d_sentiment_analysis(df)
        if points:
            fig_2d, ax_2d = plt.subplots(figsize=(5, 4)) # 缩小尺寸
            
            x_vals = [p['x'] for p in points]
            y_vals = [p['y'] for p in points]
            ax_2d.scatter(x_vals, y_vals, alpha=0.5, c='#636EFA', s=60)
            
            ax_2d.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3)
            ax_2d.axvline(x=0.5, color='gray', linestyle='--', alpha=0.3)
            
            # 缩小字体以适应小图
            font_size = 8
            ax_2d.text(0.2, 0.85, "焦虑/愤怒", color='#EF553B', fontsize=font_size, ha='center')
            ax_2d.text(0.8, 0.85, "兴奋/快乐", color='#00CC96', fontsize=font_size, ha='center')
            ax_2d.text(0.2, 0.15, "抑郁/疲惫", color='#19D3F3', fontsize=font_size, ha='center')
            ax_2d.text(0.8, 0.15, "安详/放松", color='#AB63FA', fontsize=font_size, ha='center')
            
            ax_2d.set_xlim(0, 1)
            ax_2d.set_ylim(0, 1)
            ax_2d.tick_params(axis='both', which='major', labelsize=7)
            st.pyplot(fig_2d)
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

    # --- 词云区 ---
    st.subheader("☁️ 热门话题词云")
    word_counts = get_word_frequencies(df)
    if word_counts:
        # 尝试寻找中文字体
        font_path = None
        candidate_fonts = [
            '/System/Library/Fonts/STHeiti Light.ttc', 
            '/System/Library/Fonts/PingFang.ttc',
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
            'C:/Windows/Fonts/simhei.ttf'
        ]
        for path in candidate_fonts:
            if os.path.exists(path):
                font_path = path
                break
        
        try:
            wc = WordCloud(
                font_path=font_path,
                width=1000, height=300, # 扁平化，适应宽度
                background_color='white',
                max_words=100
            ).generate_from_frequencies(word_counts)

            fig_wc, ax_wc = plt.subplots(figsize=(10, 3))
            ax_wc.imshow(wc.to_image(), interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        except Exception as e:
            st.error(f"词云生成失败: {e}")
    
    # --- 数据透视 ---
    st.markdown("---")

    # --- 数据透视 ---
    st.markdown("---")
    st.subheader("📋 原始数据摘要 (仅科研用途)")
    st.dataframe(df[['role', 'title', 'created_at']], use_container_width=True)
