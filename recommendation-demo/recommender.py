"""算法推荐引擎:支持多种推荐算法"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def build_item_similarity(interactions):
    matrix = interactions.pivot_table(
        index='user_id', columns='product_id', values='rating', fill_value=0
    )
    sim = cosine_similarity(matrix.T)
    return pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns)

def recommend_by_algorithm(user_id, algo_type, interactions, item_sim, products, top_n=5):
    if algo_type == 'item_cf':
        return _item_cf_recommend(user_id, interactions, item_sim, products, top_n)
    elif algo_type == 'popularity':
        return _popularity_recommend(products, top_n)
    elif algo_type == 'content_based':
        return _content_based_recommend(user_id, interactions, products, top_n)
    else:
        return _popularity_recommend(products, top_n)

def _item_cf_recommend(user_id, interactions, item_sim, products, top_n):
    user_rated = interactions[interactions['user_id'] == user_id]['product_id'].tolist()
    if not user_rated:
        return _popularity_recommend(products, top_n)
    scores = {}
    for pid in products['product_id']:
        if pid in user_rated or pid not in item_sim.columns:
            continue
        sims = [item_sim.loc[pid, r] for r in user_rated if r in item_sim.columns]
        if sims:
            scores[pid] = np.mean(sorted(sims, reverse=True)[:5])
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result = products[products['product_id'].isin([t[0] for t in top])].copy()
    result['score'] = result['product_id'].map(dict(top))
    return result.sort_values('score', ascending=False)

def _popularity_recommend(products, top_n):
    return products[products['status'] == '在售'].nlargest(top_n, 'popularity')

def _content_based_recommend(user_id, interactions, products, top_n):
    user_rated = interactions[interactions['user_id'] == user_id]['product_id'].tolist()
    if not user_rated:
        return _popularity_recommend(products, top_n)
    liked_cats = interactions[
        (interactions['user_id'] == user_id) & (interactions['rating'] >= 4)
    ].merge(products[['product_id', 'category']], on='product_id')['category'].unique()
    if len(liked_cats) == 0:
        return _popularity_recommend(products, top_n)
    return products[
        (products['category'].isin(liked_cats)) &
        (~products['product_id'].isin(user_rated)) &
        (products['status'] == '在售')
    ].nlargest(top_n, 'popularity')def bytedance_personalized(user_id, interactions, products, top_n=5):
    """
    字节千人千面（简化版）
    1. 多路召回：热门 + 分类偏好 + 协同召回
    2. 排序：按流行度
    """
    candidates = set()

    # 路1：热门召回
    hot = products[products["status"] == "在售"].nlargest(20, "popularity")
    candidates.update(hot["product_id"].tolist())

    # 路2：用户偏好分类召回
    user_r = interactions[interactions["user_id"] == user_id]
    if not user_r.empty:
        liked = user_r.merge(products[["product_id", "category"]], on="product_id", how="left")
        liked_cats = liked["category"].dropna().unique().tolist()
        for cat in liked_cats:
            cat_items = products[(products["category"] == cat) & (products["status"] == "在售")].head(10)
            candidates.update(cat_items["product_id"].tolist())

    # 排序
    cand_df = products[products["product_id"].isin(candidates)].copy()
    cand_df = cand_df.sort_values("popularity", ascending=False).head(top_n)
    return cand_df
