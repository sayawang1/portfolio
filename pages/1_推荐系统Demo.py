"""推荐系统 Demo - 深色前端展示（整段复制即可）"""
import streamlit as st
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo")
)

from data_providers.slot_provider import get_slots_with_source
from data_providers.product_provider import get_products_with_source
from data_providers.user_provider import get_users_with_source
from data_providers.interaction_provider import get_interactions_with_source

CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recommendation-demo", "configs",
)


def build_item_similarity(interactions):
    from sklearn.metrics.pairwise import cosine_similarity
    matrix = interactions.pivot_table(
        index="user_id", columns="product_id", values="rating", fill_value=0
    )
    sim = cosine_similarity(matrix.T)
    return pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns)


def recommend_by_algorithm(user_id, algo_type, interactions, item_sim, products, top_n=5):
    if algo_type == "item_cf":
        user_rated = interactions[interactions["user_id"] == user_id]["product_id"].tolist()
        if not user_rated:
            return products[products["status"] == "在售"].nlargest(top_n, "popularity")
        scores = {}
        for pid in products["product_id"]:
            if pid in user_rated or pid not in item_sim.columns:
                continue
            sims = [item_sim.loc[pid, r] for r in user_rated if r in item_sim.columns]
            if sims:
                scores[pid] = float(np.mean(sorted(sims, reverse=True)[:5]))
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = products[products["product_id"].isin([t[0] for t in top])].copy()
        result["score"] = result["product_id"].map(dict(top))
        return result.sort_values("score", ascending=False)
    elif algo_type == "content_based":
        user_rated = interactions[interactions["user_id"] == user_id]["product_id"].tolist()
        liked_cats = interactions[
            (interactions["user_id"] == user_id) & (interactions["rating"] >= 4)
        ].merge(products[["product_id", "category"]], on="product_id")["category"].unique()
        return products[
            (products["category"].isin(liked_cats))
            & (~products["product_id"].isin(user_rated))
            & (products["status"] == "在售")
        ].nlargest(top_n, "popularity")
    elif algo_type == "bytedance_ps":
        candidates = set()
        hot = products[products["status"] == "在售"].nlargest(20, "popularity")
        candidates.update(hot["product_id"].tolist())
        user_r = interactions[interactions["user_id"] == user_id]
        if not user_r.empty:
            liked = user_r.merge(products[["product_id", "category"]], on="product_id", how="left")
            for cat in liked["category"].dropna().unique():
                cat_items = products[(products["category"] == cat) & (products["status"] == "在售")].head(10)
                candidates.update(cat_items["product_id"].tolist())
        cand_df = products[products["product_id"].isin(candidates)].copy()
        return cand_df.sort_values("popularity", ascending=False).head(top_n)
    else:
        return products[products["status"] == "在售"].nlargest(top_n, "popularity")


st.set_page_config(
    page_title="推荐系统 Demo",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #E6E6E6; }
    h1, h2, h3, h4 { color: #FFFFFF !important; }
    .stButton>button {
        background-color: #1C2228; color: #E6E6E6;
        border: 1px solid #2A323A; border-radius: 8px;
        padding: 10px 18px; font-weight: 500;
    }
    .stButton>button:hover { border-color: #FF4B4B; color: #FF4B4B; }
    .primary-btn button { background-color: #FF4B4B !important; color: white !important; border: none !important; }
    .cond-badge {
        display: inline-block; padding: 4px 12px; margin: 4px 6px 4px 0;
        background-color: #1F2937; color: #9CA3AF;
        border-radius: 12px; font-size: 13px;
    }
    .rec-card {
        background-color: #151A1F; border: 1px solid #232A31;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .rec-card h4 { margin: 0 0 6px 0; color: #FFFFFF; }
    .rec-card .meta { color: #6B7280; font-size: 12px; }
    .footer-note { color: #4B5563; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📈 推荐系统 · 选品 & 效果预览")

# ---------- 从 provider 拿坑位 ----------
slot_list, slot_source = get_slots_with_source()
slot_map = {}
for s in slot_list:
    label = f"🎯 {s['slot_name']}"
    slot_map[label] = s["slot_id"]

if not slot_map:
    slot_map = {"📋 首页信息流": "app_home_feed"}

btn_cols = st.columns(len(slot_map))
if "selected_slot_label" not in st.session_state:
    st.session_state.selected_slot_label = list(slot_map.keys())[0]

for i, label in enumerate(slot_map.keys()):
    with btn_cols[i]:
        if st.button(label, use_container_width=True, key=f"slot_btn_{i}"):
            st.session_state.selected_slot_label = label

slot_id = slot_map[st.session_state.selected_slot_label]

c_left, c_right = st.columns([1, 3])
with c_left:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    run = st.button("🚀 开始推荐", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 从 provider 拿数据 ----------
products, product_source = get_products_with_source()
users, user_source = get_users_with_source()
interactions, interaction_source = get_interactions_with_source(users, products)
item_sim = build_item_similarity(interactions)

# ---------- 读取算法配置 ----------
algo_id = "bytedance_ps"
algo_weight = 65
ab_info = "未开启"
algo_path = os.path.join(CONFIG_DIR, "algorithm_config.json")
if os.path.exists(algo_path):
    try:
        with open(algo_path, "r", encoding="utf-8") as f:
            algo_data = json.load(f)
        bind = algo_data.get("slot_algorithm_bind", {}).get(slot_id, {})
        algo_id = bind.get("algo_id", "bytedance_ps")
        algo_weight = bind.get("algo_weight", 65)
        ab = bind.get("ab_test", {})
        if ab.get("enabled"):
            ab_info = f"A组 {ab.get('group_a_ratio', 50)}% / B组 {100 - ab.get('group_a_ratio', 50)}%"
    except Exception:
        pass

user = users.iloc[0]
items = recommend_by_algorithm(user["user_id"], algo_id, interactions, item_sim, products, top_n=5)

with c_right:
    st.markdown(
        f'<span class="cond-badge">坑位: {slot_id}</span>'
        f'<span class="cond-badge">算法: {algo_id}</span>'
        f'<span class="cond-badge">权重: {algo_weight}</span>'
        f'<span class="cond-badge">AB: {ab_info}</span>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("### 📋 推荐结果")

if items is not None and len(items) > 0:
    for _, row in items.iterrows():
        st.markdown(f"""
        <div class="rec-card">
            <h4>{row.get('name', row['product_id'])}</h4>
            <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("暂无推荐结果，请先到运营后台发布策略。")

st.markdown(
    f'<p class="footer-note">数据源: 商品={product_source} ｜ 用户={user_source} ｜ 行为={interaction_source} ｜ 坑位={slot_source} ｜ 今日: 2026-09-21</p>',
    unsafe_allow_html=True,
)
