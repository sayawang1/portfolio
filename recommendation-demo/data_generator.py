"""数据生成模块:模拟商品、用户、交互数据"""
import streamlit as st
import numpy as np
import pandas as pd

@st.cache_data
def generate_products(n=60):
    np.random.seed(42)
    categories = ['基金', '保险', '存款', '理财', '信用卡', '贷款']
    risk_map = {
        '基金': (3, 5), '保险': (1, 3), '存款': (1, 1),
        '理财': (2, 4), '信用卡': (1, 3), '贷款': (2, 4),
    }
    rows = []
    for i in range(n):
        cat = np.random.choice(categories)
        r_min, r_max = risk_map[cat]
        rows.append({
            'product_id': f'P{i+1:03d}',
            'name': f'{cat}产品{i+1}号',
            'category': cat,
            'risk_level': np.random.randint(r_min, r_max + 1),
            'expected_return': round(0.02 + np.random.uniform(0, 0.08), 4),
            'popularity': np.random.randint(10, 1000),
            'status': np.random.choice(['在售', '在售', '在售', '下架'], p=[0.7, 0.1, 0.1, 0.1]),
        })
    return pd.DataFrame(rows)

@st.cache_data
def generate_users(n=300):
    np.random.seed(42)
    rows = []
    for i in range(n):
        rows.append({
            'user_id': f'U{i+1:04d}',
            'is_vip': np.random.choice([0, 1], p=[0.8, 0.2]),
            'aum_level': np.random.choice(['低', '中', '高'], p=[0.6, 0.3, 0.1]),
            'city_tier': np.random.choice(['一线', '二线', '三线'], p=[0.3, 0.4, 0.3]),
            'age_group': np.random.choice(['18-30', '31-45', '46-60'], p=[0.3, 0.5, 0.2]),
            'risk_tolerance': np.random.randint(1, 6),
        })
    return pd.DataFrame(rows)

@st.cache_data
def generate_interactions(users, products, n_per_user=6):
    np.random.seed(42)
    rows = []
    for uid in users['user_id']:
        sample = np.random.choice(products['product_id'], n_per_user, replace=False)
        for pid in sample:
            rows.append({
                'user_id': uid,
                'product_id': pid,
                'rating': np.random.randint(1, 6),
            })
    return pd.DataFrame(rows)
