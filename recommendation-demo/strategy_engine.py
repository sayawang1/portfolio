"""策略引擎：三层优先级 —— 人工强干预 > 算法 > 兜底"""
import os
import hashlib
from datetime import datetime
import sys

# 复用 common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, get_config_dir

CONFIG_DIR = get_config_dir("recommendation-demo")

def _load(filename, default=None):
    return load_json(os.path.join(CONFIG_DIR, filename), default)

def _hit_ratio(user_id, slot_id, pct, salt=""):
    """按百分比稳定分流"""
    if pct >= 100:
        return True
    if pct <= 0:
        return False
    key = f"{user_id}_{slot_id}_{salt}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return (h % 100) < pct

def _match_target(user, target_type, target_condition):
    """判断用户是否命中目标条件"""
    if target_type == "all" or not target_condition:
        return True
    if target_type == "tag":
        try:
            return bool(eval(target_condition, {"__builtins__": {}}, dict(user)))
        except Exception:
            return False
    return False

# ============ Layer 1: 人工强干预 ============
def get_manual_items(slot_id, user):
    data = _load("manual_config.json", {"manual_rules": []})
    now = datetime.now()
    for rule in data.get("manual_rules", []):
        if not rule.get("enabled") or rule.get("slot_id") != slot_id:
            continue
        if rule.get("is_fallback"):
            continue  # 兜底规则留给 Layer 3
        try:
            start = datetime.strptime(rule["start_time"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(rule["end_time"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        if not (start <= now <= end):
            continue
        if not _match_target(user, rule.get("target_type", "all"), rule.get("target_condition", "")):
            continue
        if not _hit_ratio(user.get("user_id", "anon"), slot_id, rule.get("traffic_pct", 100), rule["rule_id"]):
            continue
        return {
            "source": "manual",
            "strategy_name": rule.get("remark", "人工强干预"),
            "rule_id": rule["rule_id"],
            "items": rule["items"],
        }
    return None

# ============ Layer 2: 算法推荐 ============
def get_algorithm_items(slot_id, user, interactions, item_sim, products):
    data = _load("algorithm_config.json", {})
    bind = data.get("slot_algorithm_bind", {}).get(slot_id)
    if not bind:
        return None

    from recommender import recommend_by_algorithm
    from ab_test import assign_group

    algo_id = bind.get("algo_id", "popularity")
    ab = bind.get("ab_test", {})
    group = "default"
    if ab.get("enabled"):
        group = assign_group(user.get("user_id", "anon"), slot_id, ab)
        if group == "A":
            algo_id = ab.get("group_a_algo", algo_id)
        elif group == "B":
            algo_id = ab.get("group_b_algo", algo_id)

    try:
        items = recommend_by_algorithm(user.get("user_id"), algo_id, interactions, item_sim, products, top_n=5)
    except Exception as e:
        return None
    if items is not None and len(items) > 0:
        return {
            "source": "algorithm",
            "strategy_name": f"算法推荐（{algo_id} / {group}组）",
            "algo_id": algo_id,
            "ab_group": group,
            "items": items,
        }
    return None

# ============ Layer 3: 兜底 ============
def get_fallback_items(slot_id, user, interactions, item_sim, products):
    # 先找人工兜底
    data = _load("manual_config.json", {"manual_rules": []})
    for rule in data.get("manual_rules", []):
        if not rule.get("enabled"):
            continue
        if rule.get("slot_id") != slot_id:
            continue
        if not rule.get("is_fallback"):
            continue
        if not _match_target(user, rule.get("target_type", "all"), rule.get("target_condition", "")):
            continue
        if not _hit_ratio(user.get("user_id", "anon"), slot_id, rule.get("traffic_pct", 100), rule["rule_id"]):
            continue
        return {
            "source": "fallback_manual",
            "strategy_name": "人工兜底",
            "rule_id": rule["rule_id"],
            "items": rule["items"],
        }

    # 默认兜底：热门
    from recommender import recommend_by_algorithm
    try:
        items = recommend_by_algorithm(user.get("user_id"), "popularity", interactions, item_sim, products, top_n=5)
    except Exception:
        items = products.head(5)
    return {
        "source": "fallback_default",
        "strategy_name": "全量兜底（热门）",
        "items": items,
    }

# ============ 统一入口 ============
def execute_strategy(slot_id, user, interactions, item_sim, products):
    result = get_manual_items(slot_id, user)
    if result:
        return result

    result = get_algorithm_items(slot_id, user, interactions, item_sim, products)
    if result:
        return result

    return get_fallback_items(slot_id, user, interactions, item_sim, products)
