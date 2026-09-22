"""推荐系统 Demo - 深色 + 高亮选中"""
import streamlit as st
import os
import json
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime
import sys

from data_providers.slot_provider import get_slots_with_source
from data_providers.product_provider import get_products_with_source
from data_providers.user_provider import get_users_with_source
from data_providers.interaction_provider import get_interactions_with_source

CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recommendation-demo", "configs",
)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from recommender import recommend_by_algorithm, build_item_similarity


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

        raw_items = rule.get("items", [])
        enriched = []
        for it in raw_items:
            if isinstance(it, str):
                enriched.append({"product_id": it, "icon": "", "jump_url": ""})
            elif isinstance(it, dict):
                enriched.append({
                    "product_id": it.get("product_id", ""),
                    "icon": it.get("icon", ""),
                    "jump_url": it.get("jump_url", ""),
                })

        if not enriched:
            continue

        ids = [e["product_id"] for e in enriched]
        matched = products[products["product_id"].isin(ids)].copy()
        if len(matched) > 0:
            meta_map = {e["product_id"]: e for e in enriched}
            matched["icon"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("icon", ""))
            matched["jump_url"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("jump_url", ""))
            return {
                "source": "manual",
                "strategy_name": rule.get("remark", "人工强干预"),
                "strategy_id": rule.get("rule_id", "-"),
                "weight": rule.get("manual_weight", 80),
                "items": matched,
                "audience": rule.get("audience_label", "-"),
            }
    return None


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

    # ⭐ 只对注册用户生效
    if bind.get("require_registered") and not user.get("is_registered", 1):
        return None

    algo_id = bind.get("algo_id", "item_cf")
    algo_weight = bind.get("algo_weight", 65)
    ab = bind.get("ab_test", {})
    ab_group = "-"
    if ab.get("enabled"):
        ab_group = _stable_hash_group(user["user_id"], slot_id, ab.get("group_a_ratio", 50))
        algo_id = ab.get("group_a_algo", algo_id) if ab_group == "A" else ab.get("group_b_algo", algo_id)

    items = recommend_by_algorithm(user["user_id"], algo_id, interactions, item_sim, products, top_n=5)
    if items is not None and len(items) > 0:
        items = items.copy()
        items["icon"] = ""
        items["jump_url"] = ""
        return {
            "source": "algorithm",
            "strategy_name": f"算法推荐（{algo_id}）",
            "strategy_id": f"algo_{algo_id}",
            "weight": algo_weight,
            "items": items,
            "ab_group": ab_group,
        }
    return None


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

                raw_items = rule.get("items", [])
                enriched = []
                for it in raw_items:
                    if isinstance(it, str):
                        enriched.append({"product_id": it, "icon": "", "jump_url": ""})
                    elif isinstance(it, dict):
                        enriched.append({
                            "product_id": it.get("product_id", ""),
                            "icon": it.get("icon", ""),
                            "jump_url": it.get("jump_url", ""),
                        })

                if not enriched:
                    continue
                ids = [e["product_id"] for e in enriched]
                matched = products[products["product_id"].isin(ids)].copy()
                if len(matched) > 0:
                    meta_map = {e["product_id"]: e for e in enriched}
                    matched["icon"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("icon", ""))
                    matched["jump_url"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("jump_url", ""))
                    return {
                        "source": "fallback_manual",
                        "strategy_name": "人工兜底",
                        "strategy_id": rule.get("rule_id", "-"),
                        "weight": rule.get("manual_weight", 0),
                        "items": matched,
                        "audience": rule.get("audience_label", "-"),
                    }
        except Exception:
            pass

    items = recommend_by_algorithm(user["user_id"], "popularity", interactions, item_sim, products, top_n=5)
    items = items.copy()
    items["icon"] = ""
    items["jump_url"] = ""
    return {
        "source": "fallback_algorithm",
        "strategy_name": "全量兜底（热门）",
        "strategy_id": "algo_popularity",
        "weight": 0,
        "items": items,
    }


def _merge_manual_algo(manual_items, algo_items, total=5):
    manual_list = manual_items.to_dict("records")
    manual_ids = set(manual_items["product_id"].tolist())
    algo_filtered = algo_items[~algo_items["product_id"].isin(manual_ids)].to_dict("records")
    merged = (manual_list + algo_filtered)[:total]
    return pd.DataFrame(merged)


def execute_strategy(slot_id, user, interactions, item_sim, products):
    manual = get_manual_result(slot_id, user, products)
    algo = get_algorithm_result(slot_id, user, interactions, item_sim, products)

    if manual and algo:
        manual_score = manual["weight"] * 100 + algo["weight"]
        algo_score = algo["weight"] * 100 + manual["weight"]
        if manual_score >= algo_score:
            merged = _merge_manual_algo(manual["items"], algo["items"], total=5)
            return {**manual, "items": merged, "manual_items": manual["items"], "algo_items": algo["items"],
                    "competition": f"人工 {manual_score} vs 算法 {algo_score} → 人工胜出",
                    "ab_group": algo.get("ab_group", "-")}
        else:
            merged = _merge_manual_algo(algo["items"], manual["items"], total=5)
            return {**algo, "items": merged, "manual_items": manual["items"], "algo_items": algo["items"],
                    "competition": f"人工 {manual_score} vs 算法 {algo_score} → 算法胜出"}
    elif manual:
        return {**manual, "manual_items": manual["items"], "algo_items": pd.DataFrame(), "competition": "仅人工命中"}
    elif algo:
        return {**algo, "manual_items": pd.DataFrame(), "algo_items": algo["items"], "competition": "仅算法命中"}
    else:
        fallback = get_fallback_result(slot_id, user, products, interactions, item_sim)
        return {**fallback, "manual_items": pd.DataFrame(), "algo_items": fallback["items"], "competition": "均未命中 → 兜底"}


st.set_page_config(page_title="推荐系统 Demo", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #E6E6E6; }
    h1, h2, h3, h4 { color: #FFFFFF !important; }
    .stButton>button {
        background-color: #1C2228; color: #E6E6E6;
        border: 1px solid #2A323A; border-radius: 10px;
        padding: 14px 20px; font-weight: 500;
        width: 100%; font-size: 15px;
    }
    .stButton>button:hover { border-color: #FF4B4B; color: #FF4B4B; }
    .slot-active .stButton>button {
        background-color: #FF4B4B !important;
        color: #FFFFFF !important;
        border: 2px solid #FF4B4B !important;
    }
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
    .rec-icon {
        display: inline-block; width: 32px; height: 32px;
        background-color: #FF4B4B; border-radius: 6px;
        text-align: center; line-height: 32px;
        color: white; font-size: 18px; margin-right: 10px;
    }
    .final-card {
        background-color: #1F2937; border: 2px solid #FF4B4B;
        border-radius: 12px; padding: 18px; margin: 12px 0 24px 0;
    }
    .final-card h3 { margin: 0 0 8px 0; color: #FF4B4B; }
    .footer-note { color: #4B5563; font-size: 12px; }
    .mock-note { color: #6B7280; font-size: 12px; font-style: italic; margin-top: 8px; }
    .no-data {
        color: #6B7280; font-size: 14px;
        background-color: #151A1F; border: 1px dashed #2A323A;
        border-radius: 10px; padding: 40px; text-align: center;
        margin-top: 20px;
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

user_options = [""] + users_all["user_id"].tolist()
if "selected_user_id" not in st.session_state:
    st.session_state.selected_user_id = ""

c_u1, c_u2, c_u3 = st.columns([2, 3, 3])
with c_u1:
    selected_user_id = st.selectbox(
        "👤 选择用户",
        user_options,
        index=user_options.index(st.session_state.selected_user_id) if st.session_state.selected_user_id in user_options else 0,
        key="user_select",
    )
    st.session_state.selected_user_id = selected_user_id

user_row = None
if selected_user_id:
    user_row = users_all[users_all["user_id"] == selected_user_id].iloc[0]

with c_u2:
    if user_row is not None:
        type_label = {"vip": "VIP 会员", "registered": "注册用户", "guest": "非注册游客"}.get(user_row.get("user_type", ""), "-")
        vip_label = "✅ 是" if user_row['is_vip'] == 1 else "❌ 否"
        st.markdown(f"**类型**：{type_label} ｜ **VIP**：{vip_label} ｜ **资产等级**：{user_row['aum_level']}")
    else:
        st.markdown("**类型**：- ｜ **VIP**：- ｜ **资产等级**：-")
with c_u3:
    if user_row is not None:
        st.markdown(f"**新用户**：{'是' if user_row.get('is_new') == 1 else '否'} ｜ **活跃**：{'是' if user_row.get('is_active') == 1 else '否'} ｜ **流失预警**：{'是' if user_row.get('is_churn_risk') == 1 else '否'}")
    else:
        st.markdown("**新用户**：- ｜ **活跃**：- ｜ **流失预警**：-")

slot_list, slot_source = get_slots_with_source()

SLOT_ORDER = ["app_home_banner", "app_home_feed", "web_sidebar", "ad_layer"]
SLOT_LABEL = {
    "app_home_banner": "🎯 APP首页Banner",
    "app_home_feed": "🎯 APP首页信息流",
    "web_sidebar": "🎯 网页侧边栏",
    "ad_layer": "🎯 广告层",
}

available_slots = [s["slot_id"] for s in slot_list]
ordered_slots = [sid for sid in SLOT_ORDER if sid in available_slots]
if not ordered_slots:
    ordered_slots = SLOT_ORDER

if "selected_slot_id" not in st.session_state:
    st.session_state.selected_slot_id = ""

btn_cols = st.columns(4)
for i, sid in enumerate(ordered_slots):
    is_selected = (sid == st.session_state.selected_slot_id)
    with btn_cols[i]:
        if is_selected:
            st.markdown('<div class="slot-active">', unsafe_allow_html=True)
            if st.button(SLOT_LABEL.get(sid, sid), key=f"slot_btn_{sid}"):
                st.session_state.selected_slot_id = ""
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            if st.button(SLOT_LABEL.get(sid, sid), key=f"slot_btn_{sid}"):
                st.session_state.selected_slot_id = sid
                st.rerun()

slot_id = st.session_state.selected_slot_id

show_data = bool(user_row is not None and slot_id)

if not show_data:
    st.markdown(
        '<div class="no-data">请先选择「用户」和「坑位」，才会展示推荐结果。</div>',
        unsafe_allow_html=True,
    )
else:
    result = execute_strategy(slot_id, user_row, interactions_all, item_sim_all, products_all)

    source_map = {
        "manual": "✋ 人工强干预",
        "algorithm": "🤖 算法推荐",
        "fallback_manual": "🛟 人工兜底",
        "fallback_algorithm": "🛟 兜底（热门）",
    }
    source_label = source_map.get(result["source"], result["source"])

    sid = result.get("strategy_id", "-")
    algo_name_map = {
        "algo_deepfm": "DeepFM v3（精排）",
        "algo_dssm": "双塔召回（DSSM）",
        "algo_bytedance_ps": "字节千人千面",
        "algo_item_cf": "协同过滤 ItemCF",
        "algo_content_based": "内容召回 ContentBased",
        "algo_popularity": "兜底（热门）",
    }
    if sid.startswith("rule_"):
        algo_label = f"人工规则 {sid}"
    else:
        algo_label = algo_name_map.get(sid, sid)

    st.markdown(
        f'<span class="cond-badge">策略来源: {source_label}</span>'
        f'<span class="cond-badge">命中: {algo_label}</span>'
        f'<span class="cond-badge">竞争: {result.get("competition", "-")}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    merged_items = result.get("items")
    manual_items = result.get("manual_items")
    algo_items = result.get("algo_items")

    if merged_items is not None and len(merged_items) > 0:
        is_single_slot = "banner" in slot_id.lower()

        if is_single_slot:
            final = merged_items.iloc[0]
            icon_html = f'<span class="rec-icon">🎁</span>' if final.get("icon") else ""
            st.markdown("### 🎯 最终展示位（唯一）")
            st.markdown(f"""
            <div class="final-card">
                <h3>{icon_html} 🏆 {final.get('name', final['product_id'])}</h3>
                <div style="color:#9CA3AF;">类别：{final.get('category', '-')} ｜ 风险：R{final.get('risk_level', '-')} ｜ 热度：{final.get('popularity', '-')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📋 推荐列表（候选池）")
            for _, row in merged_items.iterrows():
                icon_html = f'<span class="rec-icon">🎁</span>' if row.get("icon") else ""
                url = row.get("jump_url", "")
                url_line = f'<div class="meta">🔗 <a href="{url}" target="_blank" style="color:#4A90D9;">{url}</a></div>' if url else ""
                st.markdown(f"""
                <div class="rec-card">
                    <h4>{icon_html}{row.get('name', row['product_id'])}</h4>
                    <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
                    {url_line}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("### 📋 推荐列表")
            for _, row in merged_items.iterrows():
                icon_html = f'<span class="rec-icon">🎁</span>' if row.get("icon") else ""
                url = row.get("jump_url", "")
                url_line = f'<div class="meta">🔗 <a href="{url}" target="_blank" style="color:#4A90D9;">{url}</a></div>' if url else ""
                st.markdown(f"""
                <div class="rec-card">
                    <h4>{icon_html}{row.get('name', row['product_id'])}</h4>
                    <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
                    {url_line}
                </div>
                """, unsafe_allow_html=True)

        m_count = len(manual_items) if manual_items is not None else 0
        a_count = len(algo_items) if algo_items is not None else 0
        st.markdown(
            f'<div class="mock-note">人工命中 {m_count} 条 ｜ 算法召回 {a_count} 条 ｜ 合并去重后共 {len(merged_items)} 条（模拟数据）</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="no-data">该坑位暂未配置策略，请在运营后台配置后查看效果。</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<p class="footer-note">数据源: 商品={product_source} ｜ 用户={user_source} ｜ 行为={interaction_source} ｜ 坑位={slot_source} ｜ 今日: 2026-09-22</p>',
    unsafe_allow_html=True,
)
