"""策略执行引擎:按优先级顺序执行策略匹配"""
from recommender import recommend_by_algorithm

def _match_condition(user_row, condition_str: str) -> bool:
    if not condition_str:
        return True
    try:
        return bool(eval(condition_str, {}, user_row.to_dict()))
    except Exception:
        return False

def _match_strategy(user_row, strategy) -> bool:
    if strategy['status'] != 'running':
        return False
    if strategy['target_type'] == 'all':
        return True
    return _match_condition(user_row, strategy.get('target_condition', ''))

def execute_strategy(user_row, strategies, interactions, item_sim, products):
    sorted_strategies = sorted(
        [s for s in strategies if s['status'] == 'running'],
        key=lambda s: s.get('priority', 99)
    )
    for strategy in sorted_strategies:
        if _match_strategy(user_row, strategy):
            if strategy['rec_source'] == 'manual':
                recs = _get_manual_recommendations(strategy, products)
                return strategy, recs, f"人工强干预策略「{strategy['name']}」"
            else:
                recs = recommend_by_algorithm(
                    user_row['user_id'], strategy['algo_type'],
                    interactions, item_sim, products
                )
                return strategy, recs, f"算法推荐策略「{strategy['name']}」({strategy['algo_type']})"
    return None, products.head(5), "无匹配策略,返回默认推荐"

def _get_manual_recommendations(strategy, products):
    manual_items = strategy.get('manual_products', [])
    if not manual_items:
        return products.head(5)
    pid_weights = {item['pid']: item.get('weight', 1.0) for item in manual_items}
    result = products[products['product_id'].isin(pid_weights.keys())].copy()
    result['weight'] = result['product_id'].map(pid_weights)
    result = result.sort_values('weight', ascending=False)
    return result.drop(columns=['weight'])
