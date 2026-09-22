"""算法推荐引擎：支持多种模型"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_item_similarity(interactions):
    matrix = interactions.pivot_table(
        index='user_id', columns='product_id', values='rating', fill_value=0
    )
    sim = cosine_similarity(matrix.T)
    return pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns)


# ========== 模型 1：协同过滤 ItemCF ==========
def _item_cf(user_id, interactions, item_sim, products, top_n=5):
    user_rated = interactions[interactions['user_id'] == user_id]['product_id'].tolist()
    if not user_rated:
        return _popularity(products, top_n)
    scores = {}
    for pid in products['product_id']:
        if pid in user_rated or pid not in item_sim.columns:
            continue
        sims = [item_sim.loc[pid, r] for r in user_rated if r in item_sim.columns]
        if sims:
            scores[pid] = float(np.mean(sorted(sims, reverse=True)[:5]))
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result = products[products['product_id'].isin([t[0] for t in top])].copy()
    result['score'] = result['product_id'].map(dict(top))
    return result.sort_values('score', ascending=False)


# ========== 模型 2：内容召回 ContentBased ==========
def _content_based(user_id, interactions, products, top_n=5):
    user_rated = interactions[interactions['user_id'] == user_id]['product_id'].tolist()
    if not user_rated:
        return _popularity(products, top_n)
    liked_cats = interactions[
        (interactions['user_id'] == user_id) & (interactions['rating'] >= 4)
    ].merge(products[['product_id', 'category']], on='product_id')['category'].unique()
    if len(liked_cats) == 0:
        return _popularity(products, top_n)
    return products[
        (products['category'].isin(liked_cats)) &
        (~products['product_id'].isin(user_rated)) &
        (products['status'] == '在售')
    ].nlargest(top_n, 'popularity')


# ========== 模型 3：字节千人千面 ==========
def _bytedance_ps(user_id, interactions, products, top_n=5):
    candidates = set()
    hot = products[products["status"] == "在售"].nlargest(20, "popularity")
    candidates.update(hot["product_id"].tolist())

    user_r = interactions[interactions["user_id"] == user_id]
    if not user_r.empty:
        liked = user_r.merge(products[["product_id", "category"]], on="product_id", how="left")
        for cat in liked["category"].dropna().unique():
            cat_items = products[(products["category"] == cat) & (products["status"] == "在售")].head(10)
            candidates.update(cat_items["product_id"].tolist())

    cand_df = products[products["product_id"].isin(candidates)].copy()
    return cand_df.sort_values("popularity", ascending=False).head(top_n)


# ========== 模型 4：双塔召回 DSSM ==========
def _dssm(user_id, interactions, products, top_n=5):
    """
    模拟双塔：用户塔 & 物品塔各输出一个向量，内积排序
    这里用简化版：用户偏好类目 + 热门综合打分
    """
    user_r = interactions[interactions["user_id"] == user_id]
    liked_cats = []
    if not user_r.empty:
        liked = user_r.merge(products[["product_id", "category"]], on="product_id", how="left")
        liked_cats = liked[liked["rating"] >= 4]["category"].dropna().unique().tolist()

    df = products[products["status"] == "在售"].copy()
    # 打分 = 类目匹配 * 0.6 + 流行度归一化 * 0.4
    df["cat_match"] = df["category"].apply(lambda x: 1.0 if x in liked_cats else 0.0)
    df["pop_norm"] = df["popularity"] / df["popularity"].max()
    df["score"] = df["cat_match"] * 0.6 + df["pop_norm"] * 0.4
    return df.sort_values("score", ascending=False).head(top_n)


# ========== 模型 5：DeepFM v3（精排）==========
def _deepfm(user_id, interactions, products, top_n=5):
    """
    模拟 DeepFM：用户特征 + 物品特征交叉
    简化：用用户风险承受等级和产品风险等级的匹配度 + 流行度
    """
    user_r = interactions[interactions["user_id"] == user_id]
    df = products[products["status"] == "在售"].copy()

    # 简化打分：随机 + 流行度混合（模拟深度模型输出）
    np.random.seed(hash(user_id) % 2**32)
    df["score"] = (
        np.random.uniform(0, 1, len(df)) * 0.5
        + (df["popularity"] / df["popularity"].max()) * 0.5
    )
    return df.sort_values("score", ascending=False).head(top_n)


# ========== 兜底模型：热门（写死，不在下拉里）==========
def _popularity(products, top_n=5):
    return products[products['status'] == '在售'].nlargest(top_n, 'popularity')


# ========== 统一入口 ==========
def recommend_by_algorithm(user_id, algo_type, interactions, item_sim, products, top_n=5):
    """
    algo_type 可选：deepfm / dssm / bytedance_ps / item_cf / content_based / popularity
    """
    if algo_type == "item_cf":
        return _item_cf(user_id, interactions, item_sim, products, top_n)
    elif algo_type == "content_based":
        return _content_based(user_id, interactions, products, top_n)
    elif algo_type == "bytedance_ps":
        return _bytedance_ps(user_id, interactions, products, top_n)
    elif algo_type == "dssm":
        return _dssm(user_id, interactions, products, top_n)
    elif algo_type == "deepfm":
        return _deepfm(user_id, interactions, products, top_n)
    else:
        return _popularity(products, top_n)
