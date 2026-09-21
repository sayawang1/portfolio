"""商品数据源：优先外部系统，失败用本地模拟"""
import os
import numpy as np
import pandas as pd

EXTERNAL_PRODUCT_API = os.getenv("PRODUCT_API_URL", "")


def get_products():
    if EXTERNAL_PRODUCT_API:
        try:
            import requests
            resp = requests.get(EXTERNAL_PRODUCT_API, timeout=3)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    return df
        except Exception:
            pass

    # 本地模拟
    np.random.seed(42)
    categories = ["基金", "保险", "存款", "理财", "信用卡", "贷款"]
    risk_map = {"基金": (3, 5), "保险": (1, 3), "存款": (1, 1),
                "理财": (2, 4), "信用卡": (1, 3), "贷款": (2, 4)}
    rows = []
    for i in range(60):
        cat = np.random.choice(categories)
        r_min, r_max = risk_map[cat]
        rows.append({
            "product_id": f"P{i+1:03d}",
            "name": f"{cat}产品{i+1}号",
            "category": cat,
            "risk_level": int(np.random.randint(r_min, r_max + 1)),
            "expected_return": round(0.02 + np.random.uniform(0, 0.08), 4),
            "popularity": int(np.random.randint(10, 1000)),
            "status": str(np.random.choice(["在售", "在售", "在售", "下架"], p=[0.7, 0.1, 0.1, 0.1])),
        })
    return pd.DataFrame(rows)
