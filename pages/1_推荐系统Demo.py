"""推荐系统 Demo - 照图2风格（深色前端展示）"""
import streamlit as st
import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from data_generator import generate_products, generate_users, generate_interactions
from recommender import build_item_similarity
from strategy_engine import execute_strategy

st.set_page_config(page_title="推荐系统 Demo", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")

# ============ 深色主题 CSS（图2风格） ============
st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #E6E6E6; }
    h1, h2, h3 { color: #FFFFFF !important; }

    /* 按钮组 */
    .stButton>button {
        background-color: #1C2228; color: #E6E6E6;
        border: 1px solid #2A323A; border-radius: 8px;
        padding: 10px 18px; font-weight: 500;
    }
    .stButton>button:hover { border-color: #FF4B4B; color: #FF4B4B; }
    .stButton>button:focus:not(:active) { border-color: #FF4B4B; }

    /* 主操作按钮（开始选股） */
    .primary-btn button {
        background-color: #FF4B4B !important; color: white !important;
        border: none !important;
    }

    /* 启用条件徽章 */
    .cond-badge {
        display: inline-block; padding: 4px 12px; margin: 4px 6px 4px 0;
        background-color: #1F2937; color: #9CA3AF;
        border-radius: 12px; font-size: 13px;
    }

    /* 推荐结果卡片 */
    .rec-card {
        background-color: #151A1F; border: 1px solid #232A31;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .rec-card h4 { margin: 0 0 6px 0; color: #FFFFFF; }
    .rec-card .meta { color: #6B7280; font-size: 12px; }

    .footer-note { color: #4B5563; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ============ 标题 ============
st.markdown("# 📈 推荐系统 · 选品 & 效果预览")

# ============ 按钮组（照图2） ============
slot_map = {
    "🎯 首页Banner": "app_home_banner",
    "📋 首页信息流": "app_home_feed",
    "🌐 网页侧边栏": "web_sidebar",
    "🧪 AB-A组": "app_home_feed",
    "🧪 AB-B组": "app_home_feed",
}
btn_cols = st.columns(len(slot_map))
selected_slot_label = None
for i, (label, sid) in enumerate(slot_map.items()):
    with btn_cols[i]:
        if st.button(label, use_container_width=True, key=f"slot_{i}"):
            selected_slot_label = label

if not selected_slot_label:
    selected_slot_label = "📋 首页信息流"
slot_id = slot_map[selected_slot_label]

# ============ 主操作按钮 ============
c_left, c_right = st.columns([1, 3])
with c_left:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    run = st.button("🚀 开始推荐", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============ 数据 & 策略 ============
products = generate_products()
users = generate_users()
interactions = generate_interactions(users, products)
item_sim = build_item_similarity(interactions)

if run or True:
    user = users.iloc[0]
    result = execute_strategy(slot_id, "p1", user, interactions, item_sim, products)

    # 启用条件徽章
    with c_right:
        st.markdown(
            f'<span class="cond-badge">坑位: {slot_id}</span>'
            f'<span class="cond-badge">策略: {result["strategy_name"]}</span>'
            f'<span class="cond-badge">来源: {result["source"]}</span>'
            f'<span class="cond-badge">权重: {result.get("weight", "-")}</span>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 推荐结果卡片
    items = result.get("items")
    if items is not None and len(items) > 0:
        for _, row in items.iterrows():
            st.markdown(f"""
            <div class="rec-card">
                <h4>{row.get('name', row['product_id'])}</h4>
                <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("暂无推荐结果")

st.markdown('<p class="footer-note">数据源: 模拟数据 ｜ 策略: 人工 > 算法 > 兜底 ｜ 今日: 2026-09-21</p>',
            unsafe_allow_html=True)
