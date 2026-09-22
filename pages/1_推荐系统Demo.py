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
        background-color: #
