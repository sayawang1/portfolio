"""策略引擎 V2：范围匹配 -> 权重竞争 -> 分层兜底"""
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, get_config_dir
from common.hash_utils import hit_ratio

CONFIG_DIR = get_config_dir("recommendation-demo")

def _match_target(user, target_type, condition):
    if target_type == "all" or not condition:
        return True
    if target_type == "tag":
        try:
            return bool(eval(condition, {"__builtins__": {}}, dict(user)))
        except Exception:
            return False
    return False

def _in_time_window(start_str, end_str):
    try:
        now = datetime.now()
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        return start <= now <= end
    except Exception:
        return True

def get_manual_result(slot_id, position_id, user):
    """返回 (权重, 结果) 或 None"""
    data = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
    for rule in data.get("manual_rules", []):
        if not rule.get("enabled") or rule.get("is_fallback"):
            continue
        if rule.get("slot_id") != slot_id or rule.get("position_id") != position_id:
            continue
        if not _in_time_window(rule.get("start_time"), rule.get("end_time")):
            continue
        if not _match_target(user, rule.get("target_type"), rule.get("target_condition")):
            continue
        if not hit_ratio(user.get("user_id", "anon"), slot_id, position_id, rule.get("traffic_pct", 100), rule["rule_id"]):
            continue
        # 命中！
        return rule.get("manual_weight", 100), {
            "source": "manual",
            "strategy_name": rule.get("remark", "人工强干预"),
            "items": rule["items"],
            "weight": rule.get("manual_weight", 100)
        }
    return None

def get_algorithm_result(slot_id, position_id, user, interactions, item_sim, products):
    """返回 (权重, 结果) 或 None"""
    from recommender import recommend_by_algorithm
    from common.hash_utils import hit_ratio

    data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), {})
    bind = data.get("slot_algorithm_bind", {}).get(f"{slot_id}_{position_id}") or data.get("slot_algorithm_bind", {}).get(slot_id)
    if not bind:
        return None

    algo_id = bind.get("algo_id", "popularity")
    ab = bind.get("ab_test", {})
    if ab.get("enabled"):
        # AB测试内部分流
        if hit_ratio(user.get("user_id", "anon"), slot_id, position_id, ab.get("group_a_ratio", 50), "AB"):
            algo_id = ab.get("group_a_algo", algo_id)
        else:
            algo_id = ab.get("group_b_algo", algo_id)

    items = recommend_by_algorithm(user.get("user_id"), algo_id, interactions, item_sim, products, top_n=5)
    if items is not None and len(items) > 0:
        return bind.get("algo_weight", 65), {
            "source": "algorithm",
            "strategy_name": f"算法推荐（{algo_id}）",
            "algo_id": algo_id,
            "ab_group": "A" if ab.get("enabled") and algo_id == ab.get("group_a_algo") else "B" if ab.get("enabled") else "-",
            "items": items,
            "weight": bind.get("algo_weight", 65)
        }
    return None

def get_fallback_result(slot_id, position_id, user, interactions, item_sim, products):
    """兜底：人工兜底 > 系统默认兜底"""
    # 1. 人工兜底
    data = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
    for rule in data.get("manual_rules", []):
        if rule.get("is_fallback") and rule.get("enabled"):
            if rule.get("slot_id") == slot_id and rule.get("position_id") == position_id:
                if _match_target(user, rule.get("target_type"), rule.get("target_condition")):
                    return {
                        "source": "fallback_manual",
                        "strategy_name": "人工兜底",
                        "items": rule["items"],
                        "weight": 0
                    }
    # 2. 系统默认兜底（热门）
    from recommender import _popularity_recommend
    items = _popularity_recommend(products, top_n=5)
    return {
        "source": "fallback_default",
        "strategy_name": "系统默认兜底（热门）",
        "items": items,
        "weight": 0
    }

def execute_strategy(slot_id, position_id, user, interactions, item_sim, products):
    """
    决策流程 V2：范围匹配 -> 权重竞争 -> 兜底
    """
    # 1. 获取两边的结果
    manual_res = get_manual_result(slot_id, position_id, user)
    algo_res = get_algorithm_result(slot_id, position_id, user, interactions, item_sim, products)

    # 2. 权重竞争
    if manual_res and algo_res:
        if manual_res[0] >= algo_res[0]:
            return manual_res[1]
        else:
            return algo_res[1]
    elif manual_res:
        return manual_res[1]
    elif algo_res:
        return algo_res[1]
    else:
        return get_fallback_result(slot_id, position_id, user, interactions, item_sim, products)
