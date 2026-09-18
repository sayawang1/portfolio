"""推荐系统 Demo - 前端展示页（配置后的效果）"""
import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from data_generator import generate_products, generate_users, generate_interactions
from recommender import build_item_similarity
from strategy_engine import execute_strategy

st.set_page_config(page_title="推荐系统 Demo", page_icon="🛒", layout="wide")
st.title("🛒 推荐系统 Demo - 前端效果")
st.markdown("**三层优先级：人工强干预 > 算法推荐 > 全量兜底**")

# 侧边栏：加一个清除缓存按钮
if st.sidebar.button("🔄 刷新配置（清缓存）"):
    st.cache_data.clear()
    st.success("缓存已清除，请重新选择用户查看。")

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
st.subheader("👤 当前用户画像")
c1, c2, c3, c4 = st.columns(4)
c1.metric("用户ID", user["user_id"])
c2.metric("VIP", "是" if user["is_vip"] == 1 else "否")
c3.metric("资产等级", user["aum_level"])
c4.metric("风险承受", f"R{user['risk_tolerance']}")

st.divider()

# 执行策略
result = execute_strategy(slot_id, user, interactions, item_sim, products)

st.subheader("🎯 命中策略")
if result['source'] == 'manual':
    st.success(f"**{result['strategy_name']}**（运营人工强干预，直接覆盖算法）")
elif result['source'] == 'algorithm':
    st.info(f"**{result['strategy_name']}**（算法推荐，AB组：{result.get('ab_group', '-')}）")
else:
    st.warning(f"**{result['strategy_name']}**（算法失败，走全量兜底）")

st.divider()

# 推荐结果展示（前端卡片样式）
st.subheader("📋 前端推荐结果")
items = result.get("items")
if items is not None and len(items) > 0:
    # 使用列布局展示卡片
    cols = st.columns(3)
    for idx, row in items.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {row.get('name', row['product_id'])}")
                st.caption(f"类别：{row.get('category', '-')}")
                st.caption(f"风险等级：R{row.get('risk_level', '-')}")
                st.caption(f"热度：{row.get('popularity', '-')}")
                st.button("查看详情", key=row['product_id'], disabled=True)
else:
    st.warning("暂无推荐结果，请检查运营后台配置。")
