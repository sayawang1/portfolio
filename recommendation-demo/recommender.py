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
    ].nlargest(top_n, 'popularity')
