"""推荐系统 Demo - 深色前端展示"""
import streamlit as st
import os
import json
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime

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
    matrix = interactions.pivot_table(index="user_id", columns="product_id", values="rating", fill_value=0)
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
            (products["category"].isin(liked_cats)) & (~products["product_id"].isin(user_rated))
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


def _match_condition(user, condition):
    if not condition:
        return True
    try:
        return bool(eval(condition, {"__builtins__": {}}, dict(user)))
    except Exception:
        return False


def _in_time_window(start_str, end_str):
    try:
        now = datetime.now()
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        return start <= now <= end
    except Exception:
        return True


def _stable_hash_group(user_id, slot_id, group_a_ratio):
    key = f"{user_id}_{slot_id}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return "A" if (h % 100) < group_a_ratio else "B"


# ============ Layer 1: 人工强干预 ============
def get_manual_result(slot_id, user, products):
    data_path = os.path.join(CONFIG_DIR, "manual_config.json")
    if not os.path.exists(data_path):
        return None
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    for rule in data.get("manual_rules", []):
        if not rule.get("enabled") or rule.get("is_fallback"):
            continue
        if rule.get("slot_id") != slot_id:
            continue
        if not _in_time_window(rule.get("start_time"), rule.get("end_time")):
            continue
        if not _match_condition(user, rule.get("base_condition", "")):
            continue
        if not _match_condition(user, rule.get("target_condition", "")):
            continue
        items = rule.get("items", [])
        matched = products[products["product_id"].isin(items)]
        if len(matched) > 0:
            return {
                "source": "manual",
                "strategy_name": rule.get("remark", "人工强干预"),
                "strategy_id": rule.get("rule_id", "-"),
                "weight": rule.get("manual_weight", 80),
                "items": matched,
                "icon": rule.get("icon", ""),
                "jump_url": rule.get("jump_url", ""),
                "audience": rule.get("audience_label", "-"),
            }
    return None


# ============ Layer 2: 算法推荐 ============
def get_algorithm_result(slot_id, user, interactions, item_sim, products):
    data_path = os.path.join(CONFIG_DIR, "algorithm_config.json")
    if not os.path.exists(data_path):
        return None
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    bind = data.get("slot_algorithm_bind", {}).get(slot_id)
    if not bind:
        return None

    if not _match_condition(user, bind.get("base_condition", "")):
        return None

    algo_id = bind.get("algo_id", "bytedance_ps")
    algo_weight = bind.get("algo_weight", 65)
    ab = bind.get("ab_test", {})
    ab_group = "-"

    if ab.get("enabled"):
        ab_group = _stable_hash_group(user["user_id"], slot_id, ab.get("group_a_ratio", 50))
        if ab_group == "A":
            algo_id = ab.get("group_a_algo", algo_id)
        else:
            algo_id = ab.get("group_b_algo", algo_id)

    items = recommend_by_algorithm(user["user_id"], algo_id, interactions, item_sim, products, top_n=5)
    if items is not None and len(items) > 0:
        return {
            "source": "algorithm",
            "strategy_name": f"算法推荐（{algo_id}）",
            "strategy_id": f"algo_{algo_id}",
            "weight": algo_weight,
            "items": items,
            "ab_group": ab_group,
        }
    return None


# ============ Layer 3: 兜底 ============
def get_fallback_result(slot_id, user, products, interactions, item_sim):
    data_path = os.path.join(CONFIG_DIR, "manual_config.json")
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for rule in data.get("manual_rules", []):
                if not rule.get("enabled") or not rule.get("is_fallback"):
                    continue
                if rule.get("slot_id") != slot_id:
                    continue
                if not _in_time_window(rule.get("start_time"), rule.get("end_time")):
                    continue
                if not _match_condition(user, rule.get("base_condition", "")):
                    continue
                if not _match_condition(user, rule.get("target_condition", "")):
                    continue
                items = rule.get("items", [])
                matched = products[products["product_id"].isin(items)]
                if len(matched) > 0:
                    return {
                        "source": "fallback_manual",
                        "strategy_name": "人工兜底",
                        "strategy_id": rule.get("rule_id", "-"),
                        "weight": rule.get("manual_weight", 0),
                        "items": matched,
                        "icon": rule.get("icon", ""),
                        "jump_url": rule.get("jump_url", ""),
                    }
        except Exception:
            pass

    items = recommend_by_algorithm(user["user_id"], "popularity", interactions, item_sim, products, top_n=5)
    return {
        "source": "fallback_algorithm",
        "strategy_name": "全量兜底（热门）",
        "strategy_id": "algo_popularity",
        "weight": 0,
        "items": items,
    }


# ============ 合并工具：人工 + 算法，去重，取前 N 条 ----------
def _merge_manual_algo(manual_items, algo_items, total=5):
    """人工 items 放前面，算法 items 去重后追加，总条数最多 total 条"""
    manual_list = manual_items.to_dict("records")
    manual_ids = set(manual_items["product_id"].tolist())

    algo_filtered = algo_items[~algo_items["product_id"].isin(manual_ids)].to_dict("records")

    # 人工优先，再算法，取前 total 条
    merged = manual_list + algo_filtered
    merged = merged[:total]

    return pd.DataFrame(merged)


# ============ 统一决策入口 ============
def execute_strategy(slot_id, user, interactions, item_sim, products):
    manual = get_manual_result(slot_id, user, products)
    algo = get_algorithm_result(slot_id, user, interactions, item_sim, products)

    if manual and algo:
        manual_score = manual["weight"] * 100 + algo["weight"]
        algo_score = algo["weight"] * 100 + manual["weight"]

        if manual_score >= algo_score:
            merged = _merge_manual_algo(manual["items"], algo["items"], total=5)
            return {
                "source": "manual",
                "strategy_name": manual["strategy_name"],
                "strategy_id": manual["strategy_id"],
                "weight": manual["weight"],
                "items": merged,
                "manual_items": manual["items"],
                "algo_items": algo["items"],
                "icon": manual.get("icon", ""),
                "jump_url": manual.get("jump_url", ""),
                "audience": manual.get("audience", "-"),
                "competition": f"人工 {manual_score} vs 算法 {algo_score} → 人工胜出",
                "ab_group": algo.get("ab_group", "-"),
            }
        else:
            merged = _merge_manual_algo(algo["items"], manual["items"], total=5)
            return {
                "source": "algorithm",
                "strategy_name": algo["strategy_name"],
                "strategy_id": algo["strategy_id"],
                "weight": algo["weight"],
                "items": merged,
                "manual_items": manual["items"],
                "algo_items": algo["items"],
                "competition": f"人工 {manual_score} vs 算法 {algo_score} → 算法胜出",
                "ab_group": algo.get("ab_group", "-"),
            }
    elif manual:
        return {
            **manual,
            "manual_items": manual["items"],
            "algo_items": pd.DataFrame(),
            "competition": "仅人工命中",
        }
    elif algo:
        return {
            **algo,
            "manual_items": pd.DataFrame(),
            "algo_items": algo["items"],
            "competition": "仅算法命中",
        }
    else:
        fallback = get_fallback_result(slot_id, user, products, interactions, item_sim)
        return {
            **fallback,
            "manual_items": pd.DataFrame(),
            "algo_items": fallback["items"],
            "competition": "均未命中 → 兜底",
        }


st.set_page_config(page_title="推荐系统 Demo", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")

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
    .cond-badge {
        display: inline-block; padding: 6px 14px; margin: 4px 6px 4px 0;
        background-color: #1F2937; color: #E6E6E6;
        border-radius: 12px; font-size: 13px;
    }
    .rec-card {
        background-color: #151A1F; border: 1px solid #232A31;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .rec-card h4 { margin: 0 0 6px 0; color: #FFFFFF; }
    .rec-card .meta { color: #6B7280; font-size: 12px; }
    .final-card {
        background-color: #1F2937; border: 2px solid #FF4B4B;
        border-radius: 12px; padding: 18px; margin: 12px 0 24px 0;
    }
    .final-card h3 { margin: 0 0 8px 0; color: #FF4B4B; }
    .footer-note { color: #4B5563; font-size: 12px; }
    .mock-note {
        color: #6B7280; font-size: 12px; font-style: italic;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📈 推荐系统 · 选品 & 效果预览")

if st.button("🔄 清除缓存并刷新", key="clear_cache_btn"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

users_all, user_source = get_users_with_source()
products_all, product_source = get_products_with_source()
interactions_all, interaction_source = get_interactions_with_source(users_all, products_all)
item_sim_all = build_item_similarity(interactions_all)

c_u1, c_u2, c_u3 = st.columns([2, 3, 3])
with c_u1:
    selected_user_id = st.selectbox("👤 选择用户", users_all["user_id"].tolist(), index=0)
user_row = users_all[users_all["user_id"] == selected_user_id].iloc[0]
with c_u2:
    st.markdown(f"**VIP**：{'✅ 是' if user_row['is_vip'] == 1 else '❌ 否'} ｜ **资产等级**：{user_row['aum_level']}")
with c_u3:
    st.markdown(f"**城市**：{user_row['city_tier']} ｜ **风险承受**：R{user_row['risk_tolerance']}")

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

result = execute_strategy(slot_id, user_row, interactions_all, item_sim_all, products_all)

st.markdown(
    f'<span class="cond-badge">策略来源: {result["source"]}</span>'
    f'<span class="cond-badge">命中策略: {result.get("strategy_id", "-")}</span>'
    f'<span class="cond-badge">竞争: {result.get("competition", "-")}</span>',
    unsafe_allow_html=True,
)

# 人工命中时显示图标和跳转
if result["source"] in ("manual", "fallback_manual"):
    icon_val = result.get("icon", "")
    url_val = result.get("jump_url", "")
    if icon_val:
        st.markdown(f"**图标**：`{icon_val}`")
    else:
        st.markdown("**图标**：（未配置）")
    if url_val:
        st.markdown(f"**跳转链接**：[{url_val}]({url_val})")
    else:
        st.markdown("**跳转链接**：（未配置）")

st.markdown("---")

merged_items = result.get("items")
manual_items = result.get("manual_items")
algo_items = result.get("algo_items")

if merged_items is not None and len(merged_items) > 0:
    is_single_slot = "banner" in slot_id.lower() or "banner" in st.session_state.selected_slot_label.lower()

    if is_single_slot:
        final = merged_items.iloc[0]
        st.markdown("### 🎯 最终展示位（唯一）")
        st.markdown(f"""
        <div class="final-card">
            <h3>🏆 {final.get('name', final['product_id'])}</h3>
            <div style="color:#9CA3AF;">类别：{final.get('category', '-')} ｜ 风险：R{final.get('risk_level', '-')} ｜ 热度：{final.get('popularity', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📋 推荐列表（候选池）")
        for _, row in merged_items.iterrows():
            st.markdown(f"""
            <div class="rec-card">
                <h4>{row.get('name', row['product_id'])}</h4>
                <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("### 📋 推荐列表")
        for _, row in merged_items.iterrows():
            st.markdown(f"""
            <div class="rec-card">
                <h4>{row.get('name', row['product_id'])}</h4>
                <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
            </div>
            """, unsafe_allow_html=True)

    m_count = len(manual_items) if manual_items is not None else 0
    a_count = len(algo_items) if algo_items is not None else 0
    st.markdown(
        f'<div class="mock-note">人工命中 {m_count} 条 ｜ 算法召回 {a_count} 条 ｜ 合并去重后取前 5 条（模拟数据）</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning("该坑位暂未配置策略，请在运营后台配置后查看效果。")

st.markdown(
    f'<p class="footer-note">数据源: 商品={product_source} ｜ 用户={user_source} ｜ 行为={interaction_source} ｜ 坑位={slot_source} ｜ 今日: 2026-09-21</p>',
    unsafe_allow_html=True,
)
