"""坑位数据源：优先外部系统，失败用本地兜底"""
import os
import json
import requests

# 外部坑位系统地址（真实对接时改这里）
EXTERNAL_SLOT_API = os.getenv("SLOT_API_URL", "")  # 例如 https://api.yourcompany.com/slots

# 本地兜底数据
FALLBACK_SLOTS = [
    {"slot_id": "app_home_banner", "slot_name": "APP首页Banner", "platform": "app",
     "positions": [{"position_id": "p1", "position_name": "位置1"}]},
    {"slot_id": "app_home_feed", "slot_name": "APP首页信息流", "platform": "app",
     "positions": [{"position_id": "p1", "position_name": "位置1"}]},
    {"slot_id": "web_sidebar", "slot_name": "网页侧边栏", "platform": "web",
     "positions": [{"position_id": "p1", "position_name": "位置1"}]},
]


def get_slots():
    """获取坑位列表：先调外部，失败用本地"""
    if EXTERNAL_SLOT_API:
        try:
            resp = requests.get(EXTERNAL_SLOT_API, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass

    # 本地兜底：优先读 configs/slots.json
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "slots.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("slots"):
                return data["slots"]
        except Exception:
            pass

    return FALLBACK_SLOTS


def get_slot_options():
    """返回 slot_id 列表，给页面下拉用"""
    return [s["slot_id"] for s in get_slots()]
