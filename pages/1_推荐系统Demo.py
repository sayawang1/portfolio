"""推荐系统 Demo - 前端展示页"""
import streamlit as st
import sys
import os

# 告诉系统：去上一个文件夹里的 recommendation-demo 仓库找工具
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "recommendation-demo"))

from config_manager import init_strategies
from data_generator import generate_products, generate_users, generate_interactions
from recommender import build_item_similarity
from strategy_engine import execute_strategy

st.set_page_config(page_title="推荐系统 Demo", page_icon="🎛️", layout="wide")
init_strategies()

st.title("🎛️ 推荐策略配置平台")
st.markdown("**人工强干预 > 算法推荐 > 全量兜底**")

tab1, tab2, tab3 = st.tabs(["🔍 流量预览", "📊 策略总览", "📈 效果对比"])

products = generate_products()
users = generate_users()
interactions = generate_interactions(users, products)
item_sim = build_item_similarity(interactions)

with tab1:
    st.header("模拟用户命中")
    selected_uid = st.selectbox("选择用户", users['user_id'].head(50))
    user = users[users['user_id'] == selected_uid].iloc[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("用户ID", user['user_id'])
    c2.metric("VIP", "是" if user['is_vip'] == 1 else "否")
    c3.metric("资产等级", user['aum_level'])
    c4.metric("风险承受", f"R{user['risk_tolerance']}")
    
    strategy, recs, reason = execute_strategy(user, st.session_state.strategies, interactions, item_sim, products)
    
    st.subheader("🎯 命中策略")
    if strategy:
        st.success(f"命中:**{strategy['name']}** (优先级 P{strategy.get('priority', '?')})")
        st.caption(f"推荐来源:{reason}")
    
    st.subheader("📦 推荐结果")
    if not recs.empty:
        st.dataframe(recs[['product_id', 'name', 'category', 'risk_level']], hide_index=True)

with tab2:
    st.header("策略优先级链")
    for s in sorted(st.session_state.strategies, key=lambda x: x.get('priority', 99)):
        if s['status'] == 'running':
            st.write(f"**P{s.get('priority', '?')}** — {s['name']} | 流量 {s['traffic_pct']}%")

with tab3:
    st.header("策略效果对比")
    st.info("💡 这里将来可以对接真实的 A/B 测试数据。")
