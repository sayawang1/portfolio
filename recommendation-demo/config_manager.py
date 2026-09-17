"""策略配置管理器:负责策略的增删改查"""
import streamlit as st

def get_default_strategies():
    return [
        {
            'id': 'S001', 'name': 'VIP客户人工强推', 'priority': 1, 'traffic_pct': 20,
            'target_type': 'tag', 'target_condition': "is_vip == 1",
            'rec_source': 'manual',
            'manual_products': [{'pid': 'P001', 'weight': 1.0}, {'pid': 'P002', 'weight': 0.8}],
            'algo_type': None, 'status': 'running', 'is_fallback': False,
        },
        {
            'id': 'S002', 'name': '高净值算法推荐', 'priority': 2, 'traffic_pct': 30,
            'target_type': 'tag', 'target_condition': "aum_level == '高'",
            'rec_source': 'algorithm', 'manual_products': [], 'algo_type': 'item_cf',
            'status': 'running', 'is_fallback': False,
        },
        {
            'id': 'S003', 'name': '全量兜底策略', 'priority': 3, 'traffic_pct': 50,
            'target_type': 'all', 'target_condition': '',
            'rec_source': 'algorithm', 'manual_products': [], 'algo_type': 'popularity',
            'status': 'running', 'is_fallback': True,
        },
    ]

def init_strategies():
    if 'strategies' not in st.session_state:
        st.session_state.strategies = get_default_strategies()
    return st.session_state.strategies

def add_strategy(strategy):
    existing_ids = [s['id'] for s in st.session_state.strategies]
    num = 1
    while f"S{num:03d}" in existing_ids:
        num += 1
    strategy['id'] = f"S{num:03d}"
    st.session_state.strategies.append(strategy)

def delete_strategy(strategy_id):
    for i, s in enumerate(st.session_state.strategies):
        if s['id'] == strategy_id:
            if s.get('is_fallback'):
                return False, "兜底策略不可删除"
            st.session_state.strategies.pop(i)
            return True, "删除成功"
    return False, "策略不存在"
