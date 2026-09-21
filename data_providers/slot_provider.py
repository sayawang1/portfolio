"""坑位数据源：优先外部系统，失败用本地兜底"""
import os
import json
import requests

EXTERNAL_SLOT_API = os.getenv("SLOT_API_URL", "")

FALLBACK_SLOTS = [
    {
        "slot_id": "app_home_banner",
        "slot_name": "APP首页Banner",
        "platform": "app",
        "positions": [{"position_id": "p1", "position_name": "位置1"}],
    },
    {
        "slot_id": "app_home_feed",
        "slot_name": "APP首页信息流",
        "platform": "app",
        "positions": [{"position_id": "p1", "position_name": "位置1"}],
    },
    {
        "slot_id": "web_sidebar",
        "slot_name": "网页侧边栏",
        "platform": "web",
        "positions": [{"position_id": "p1", "position_name": "位置1"}],
    },
    {
        "slot_id": "ad_layer",
        "slot_name": "广告层",
        "platform": "app",
        "positions": [
            {"position_id": "ad_layer_p1", "position_name": "广告位1"},
            {"position_id": "ad_layer_p2", "position_name": "广告位2"},
            {"position_id": "ad_layer_p3", "position_name": "广告位3"},
        ],
    },
]


def get_slots_with_source():
    """返回 (slots, source)，source 为 'external' 或 'local'"""
    if EXTERNAL_SLOT_API:
        try:
            resp = requests.get(EXTERNAL_SLOT_API, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    return data, "external"
                if isinstance(data, dict) and data.get("slots"):
                    return data["slots"], "external"
        except Exception:
            pass

    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "recommendation-demo", "configs", "slots.json",
    )
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("slots"):
                return data["slots"], "local"
        except Exception:
            pass

    return FALLBACK_SLOTS, "local"


def get_slots():
    """只返回坑位列表"""
    slots, _ = get_slots_with_source()
    return slots


def get_slot_options():
    """返回 slot_id 列表"""
    return [s["slot_id"] for s in get_slots()]
