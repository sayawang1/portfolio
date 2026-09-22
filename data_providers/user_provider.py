"""用户数据源：优先外部系统，失败用本地模拟
金融行业用户分层：
- 非注册用户（游客）
- 注册普通用户
- 精准 VIP 会员
每个用户还带有：新用户 / 高净值 / 活跃 / 流失预警 等标签
"""
import os
import numpy as np
import pandas as pd

EXTERNAL_USER_API = os.getenv("USER_API_URL", "")


def _local_users():
    np.random.seed(42)
    rows = []
    for i in range(100):
        user_id = f"u{i+1:03d}"

        # ========== 1. 注册状态 ==========
        # 70% 注册用户，30% 非注册游客
        is_registered = int(np.random.choice([1, 0], p=[0.7, 0.3]))

        if is_registered == 0:
            # 游客：只有基础字段
            rows.append({
                "user_id": user_id,
                "user_type": "guest",
                "is_registered": 0,
                "is_vip": 0,
                "is_new": 0,
                "is_active": 0,
                "is_churn_risk": 0,
                "aum_level": "-",
                "city_tier": "-",
                "age_group": str(np.random.choice(["18-30", "31-45", "46-60"], p=[0.3, 0.5, 0.2])),
                "risk_tolerance": 0,
            })
            continue

        # ========== 2. 注册用户的属性 ==========
        # VIP：占注册用户的 25%
        is_vip = int(np.random.choice([1, 0], p=[0.25, 0.75]))
        user_type = "vip" if is_vip == 1 else "registered"

        # 新用户：占注册用户的 20%
        is_new = int(np.random.choice([1, 0], p=[0.20, 0.80]))

        # 活跃用户：占注册用户的 60%
        is_active = int(np.random.choice([1, 0], p=[0.60, 0.40]))

        # 流失预警：只在非活跃用户里出现，占非活跃的 50%
        is_churn_risk = 0
        if is_active == 0:
            is_churn_risk = int(np.random.choice([1, 0], p=[0.50, 0.50]))

        # 资产等级：VIP 大概率高净值；普通用户以中低为主
        if is_vip == 1:
            aum_level = str(np.random.choice(["高", "中", "低"], p=[0.6, 0.3, 0.1]))
        else:
            aum_level = str(np.random.choice(["高", "中", "低"], p=[0.05, 0.35, 0.60]))

        rows.append({
            "user_id": user_id,
            "user_type": user_type,
            "is_registered": 1,
            "is_vip": is_vip,
            "is_new": is_new,
            "is_active": is_active,
            "is_churn_risk": is_churn_risk,
            "aum_level": aum_level,
            "city_tier": str(np.random.choice(["一线", "二线", "三线"], p=[0.3, 0.4, 0.3])),
            "age_group": str(np.random.choice(["18-30", "31-45", "46-60"], p=[0.3, 0.5, 0.2])),
            "risk_tolerance": int(np.random.randint(1, 6)),
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
