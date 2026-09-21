"""用户数据源：优先外部系统，失败用本地模拟"""
import os
import numpy as np
import pandas as pd

EXTERNAL_USER_API = os.getenv("USER_API_URL", "")


def get_users():
    if EXTERNAL_USER_API:
        try:
            import requests
            resp = requests.get(EXTERNAL_USER_API, timeout=3)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    return df
        except Exception:
            pass

    np.random.seed(42)
    rows = []
    for i in range(100):
        rows.append({
            "user_id": f"u{i+1:03d}",
            "is_vip": int(np.random.choice([0, 1], p=[0.8, 0.2])),
            "aum_level": str(np.random.choice(["低", "中", "高"], p=[0.6, 0.3, 0.1])),
            "city_tier": str(np.random.choice(["一线", "二线", "三线"], p=[0.3, 0.4, 0.3])),
            "age_group": str(np.random.choice(["18-30", "31-45", "46-60"], p=[0.3, 0.5, 0.2])),
            "risk_tolerance": int(np.random.randint(1, 6)),
        })
    return pd.DataFrame(rows)
