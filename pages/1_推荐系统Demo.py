"""推荐系统 Demo - 前端展示页"""
import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from data_generator import generate_products, generate_users, generate_interactions
from recommender import build_item_similarity
from strategy_engine import execute_strategy

st.set_page_config(page_title="推荐系统 Demo", page_icon="🛒", layout="wide")
st.title("🛒 推荐系统 Demo")
st.markdown("**三层优先级：人工强干预 > 算法推荐 > 全量兜底**")

# 数据
products = generate_products()
users = generate_users()
interactions = generate_interactions(users, products)
item_sim = build_item_similarity(interactions)

# 侧边栏
selected_uid = st.sidebar.selectbox("选择用户", users["user_id"].head(50))
user = users[users["user_id"] == selected_uid].iloc[0]

slot_options = {
    "app_home_banner": "APP首页Banner",
    "app_home_feed":   "APP首页信息流",
    "web_sidebar":     "网页侧边栏",
}
slot_id = st.sidebar.selectbox("选择坑位", list(slot_options.keys()),
                               format_func=lambda x: slot_options[x])

# 用户卡片
c1, c2, c3, c4 = st.columns(4)
c1.metric("用户ID", user["user_id"])
c2.metric("VIP", "是" if user["is_vip"] == 1 else "否")
c3.metric("资产等级", user["aum_level"])
c4.metric("风险承受", f"R{user['risk_tolerance']}")

# 执行策略
result = execute_strategy(slot_id, user, interactions, item_sim, products)

st.subheader("🎯 命中策略")
st.success(f"**{result['strategy_name']}**（来源：`{result['source']}`）")
if result.get("algo_id"):
    st.caption(f"算法：{result['algo_id']}，AB组：{result.get('ab_group', '-')}")

st.subheader("📋 推荐结果")
items = result.get("items")
if items is not None and len(items) > 0:
    cols = [c for c in ["product_id", "name", "category", "risk_level", "popularity"] if c in items.columns]
    st.dataframe(items[cols], hide_index=True)
else:
    st.warning("无推荐结果")
