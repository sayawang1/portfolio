"""用户数据源：金融行业标准画像"""
import os
import numpy as np
import pandas as pd

EXTERNAL_USER_API = os.getenv("USER_API_URL", "")


def _local_users():
    np.random.seed(42)
    rows = []
    for i in range(100):
        uid = f"u{i+1:03d}"

        # ===== 用户类型 =====
        if i < 50:
            is_registered = 1
            # 前 30 个是 VIP，后 20 个普通注册用户
            if i < 30:
                is_vip = 1
                user_type = "vip"
            else:
                is_vip = 0
                user_type = "registered"
        else:
            is_registered = 0
            is_vip = 0
            user_type = "guest"

        # ===== 资产等级 =====
        if i < 10:
            aum_level = "高"       # 前 10 个 VIP 高净值
        elif is_registered:
            aum_level = str(np.random.choice(["低", "中", "高"], p=[0.4, 0.4, 0.2]))
        else:
            aum_level = "-"        # 游客无资产等级

        # ===== 新用户（注册 < 7 天）=====
        if is_registered and i in [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]:
            is_new = 1
        else:
            is_new = int(np.random.choice([0, 1], p=[0.9, 0.1])) if is_registered else 0

        # ===== 活跃用户（近 30 天有交易）=====
        if is_registered:
            is_active = int(np.random.choice([0, 1], p=[0.3, 0.7]))
        else:
            is_active = int(np.random.choice([0, 1], p=[0.5, 0.5]))

        # ===== 流失预警（近 60 天无交易）=====
        if is_registered and i in [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]:
            is_churn_risk = 1
        elif not is_registered and i in [75, 76, 77, 78, 79, 80]:
            is_churn_risk = 1
        else:
            is_churn_risk = int(np.random.choice([0, 1], p=[0.85, 0.15]))

        rows.append({
            "user_id": uid,
            "user_type": user_type,            # vip / registered / guest
            "is_registered": is_registered,     # 1=注册 0=非注册
            "is_vip": is_vip,
            "is_new": is_new,
            "is_active": is_active,
            "is_churn_risk": is_churn_risk,
            "aum_level": aum_level,
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
