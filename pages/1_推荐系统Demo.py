"""推荐系统 Demo - 深色前端展示"""
import streamlit as st
import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from data_generator import generate_products, generate_users, generate_interactions
from recommender import build_item_similarity
from strategy_engine import execute_strategy

st.set_page_config(page_title="推荐系统 Demo", layout="wide")

# 深色主题 CSS
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stCard { background-color: #1E1E1E; border-radius: 12px; padding: 16px; border: 1px solid #333; }
    .stBadge { background-color: #4A90D9; color: white; border-radius: 12px; padding: 2px 10px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 推荐系统 Demo")

# ...（数据加载逻辑不变）

slot_id = st.sidebar.selectbox("选择坑位", ["ad_layer", "web_sidebar"])
position_id = st.sidebar.selectbox("选择展示位", ["ad_layer_p1", "ad_layer_p2", "ad_layer_p3"])

# 执行策略
result = execute_strategy(slot_id, position_id, user, interactions, item_sim, products)

st.subheader("🎯 命中策略")
if result['source'] == 'manual':
    st.markdown(f'<span class="stBadge">人工强干预</span>', unsafe_allow_html=True)
elif result['source'] == 'algorithm':
    st.markdown(f'<span class="stBadge">算法推荐</span>', unsafe_allow_html=True)
else:
    st.markdown(f'<span class="stBadge">兜底保障</span>', unsafe_allow_html=True)

st.subheader("📋 推荐结果")
for _, row in result["items"].iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {row.get('name', row['product_id'])}")
            st.caption(f"类别：{row.get('category', '-')} | 风险等级：R{row.get('risk_level', '-')}")
        with col2:
            st.metric("热度", row.get('popularity', '-'))
