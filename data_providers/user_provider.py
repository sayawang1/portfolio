"""用户数据源：优先外部系统，失败用本地模拟"""
import os
import numpy as np
import pandas as pd

EXTERNAL_USER_API = os.getenv("USER_API_URL", "")


def _local_users():
    np.random.seed(42)
    rows = []
    for i in range(100):
        # 前 50 个：注册用户（其中前 30 个是 VIP）
        # 后 50 个：非注册用户（游客）
        if i < 30:
            user_type = "vip"
            is_vip = 1
            is_registered = 1
        elif i < 50:
            user_type = "registered"
            is_vip = 0
            is_registered = 1
        else:
            user_type = "guest"
            is_vip = 0
            is_registered = 0

        # 前 15 个 VIP 是"高净值"
        if i < 15:
            aum = "高"
        elif i < 50:
            aum = str(np.random.choice(["低", "中"], p=[0.5, 0.5]))
        else:
            aum = "-"  # 非注册用户无资产等级

        rows.append({
            "user_id": f"u{i+1:03d}",
            "user_type": user_type,          # vip / registered / guest
            "is_vip": is_vip,
            "is_registered": is_registered,  # 1=注册 0=非注册
            "aum_level": aum,
            "city_tier": str(np.random.choice(["一线", "二线", "三线"], p=[0.3, 0.4, 0.3])) if is_registered else "-",
            "age_group": str(np.random.choice(["18-30", "31-45", "46-60"], p=[0.3, 0.5, 0.2])),
            "risk_tolerance": int(np.random.randint(1, 6)) if is_registered else 0,
        })
    return pd.DataFrame(rows)


def get_users_with_source():
    if EXTERNAL_USER_API:
        try:
            import requests
            resp = requests.get(EXTERNAL_USER_API, timeout=3)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    return df, "external"
        except Exception:
            pass
    return _local_users(), "local"


def get_users():
    df, _ = get_users_with_source()
    return df
