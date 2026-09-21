"""行为数据源：优先外部系统，失败用本地模拟"""
import os
import numpy as np
import pandas as pd

EXTERNAL_INTERACTION_API = os.getenv("INTERACTION_API_URL", "")


def _local_interactions(users, products, n_per_user=6):
    np.random.seed(42)
    rows = []
    for uid in users["user_id"]:
        sample = np.random.choice(products["product_id"], n_per_user, replace=False)
        for pid in sample:
            rows.append({
                "user_id": uid,
                "product_id": pid,
                "rating": int(np.random.randint(1, 6)),
            })
    return pd.DataFrame(rows)


def get_interactions_with_source(users, products, n_per_user=6):
    """返回 (df, source)"""
    if EXTERNAL_INTERACTION_API:
        try:
            import requests
            resp = requests.get(EXTERNAL_INTERACTION_API, timeout=3)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    return df, "external"
        except Exception:
            pass
    return _local_interactions(users, products, n_per_user), "local"


def get_interactions(users, products, n_per_user=6):
    """只返回 DataFrame"""
    df, _ = get_interactions_with_source(users, products, n_per_user)
    return df
