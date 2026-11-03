"""推荐策略配置平台 - 浅色主题 ｜ 介绍 → 运营配置 / 选品与效果"""
import os
import json
import re
import sys
import uuid
import base64
import hashlib
import requests
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="推荐策略配置平台", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# 全局样式（浅色 · 白底蓝调）
# ============================================================
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background-color: #F5F7FA !important; color: #1E293B !important; }
    h1, h2, h3, h4 { color: #0F172A !important; }
    label, .stMarkdown p { color: #1E293B; }

    /* 顶部导航 */
    div[data-testid="stButton"] > button {
        border-radius: 20px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
        color: #475569 !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        padding: 6px 18px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border-color: #BFDBFE !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: #FFFFFF; padding: 6px; border-radius: 12px; border: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 18px; color: #475569; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: #2563EB !important; color: #FFFFFF !important; }

    /* 展示卡 */
    .rec-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .rec-card h4 { margin: 0 0 6px 0; color: #0F172A; }
    .rec-card .meta { color: #64748B; font-size: 12px; }
    .rec-icon {
        display: inline-block; width: 30px; height: 30px;
        background-color: #2563EB; border-radius: 8px;
        text-align: center; line-height: 30px;
        color: #FFFFFF; font-size: 16px; margin-right: 10px;
    }
    .final-card {
        background-color: #FFFFFF; border: 2px solid #2563EB;
        border-radius: 14px; padding: 18px; margin: 12px 0 24px 0;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12);
    }
    .final-card h3 { margin: 0 0 8px 0; color: #2563EB; }
    .cond-badge {
        display: inline-block; padding: 6px 14px; margin: 4px 6px 4px 0;
        background-color: #EFF6FF; color: #1D4ED8;
        border: 1px solid #BFDBFE; border-radius: 12px; font-size: 13px;
    }
    .slot-active .stButton>button {
        background-color: #2563EB !important; color: #FFFFFF !important;
        border: 2px solid #2563EB !important;
    }
    .no-data {
        color: #64748B; font-size: 14px;
        background-color: #FFFFFF; border: 1px dashed #CBD5E1;
        border-radius: 12px; padding: 40px; text-align: center; margin-top: 20px;
    }
    .footer-note { color: #94A3B8; font-size: 12px; }
    .mock-note { color: #94A3B8; font-size: 12px; font-style: italic; margin-top: 8px; }
        .h1chip { display:inline-flex; align-items:center; justify-content:center;width:52px; height:52px; border-radius:14px; font-size:26px; margin-right:14px;vertical-align:middle; box-shadow:0 6px 14px rgba(15,23,42,.18); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 顶部导航（全站统一 5 按钮）
# ============================================================
NAV = [
    ("🏠", "app.py", False), ("🧪 推荐", "", True),
    ("🤖 客服", "pages/3_智能客服.py", False),
    ("🎯 营销", "pages/4_精准营销平台.py", False), ("🏦 报送", "pages/5_监管报送规则引擎.py", False),
    ("🎁 促销", "pages/6_促销活动配置平台.py", False),
]
_nav_cols = st.columns([0.8, 0.9, 0.85, 0.85, 0.9, 0.9, 8])
for (_label, _target, _active), _c in zip(NAV, _nav_cols):
    with _c:
        if _active:
            st.button(_label, use_container_width=True, type="primary")
        elif st.button(_label, use_container_width=True):
            st.switch_page(_target)

# ============================================================
# 统一入口：先介绍，后演示
# ============================================================
if not st.session_state.get("reco_started"):
    st.markdown("""
    <style>
        .hero { padding:26px 4px 6px 4px; }
        .hero .eyebrow { color:#2563EB; font-size:12px; letter-spacing:3px; font-weight:700; }
        .hero h1 { margin:6px 0 8px 0; }
        .hero .sub { color:#64748B; font-size:14px; }
        .panel { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:20px;
                 box-shadow:0 1px 3px rgba(15,23,42,0.05); }
        .tier { display:flex; align-items:center; gap:14px; margin:10px 0; }
        .tier .tno { width:40px; height:40px; flex-shrink:0; border-radius:10px; text-align:center;
                     line-height:40px; font-weight:800; font-size:15px; }
        .tier .tname { color:#0F172A; font-weight:700; font-size:14.5px; }
        .tier .tdesc { color:#64748B; font-size:12.5px; line-height:1.6; }
        .feat { display:flex; gap:12px; margin:10px 0; align-items:flex-start; }
        .feat .fi { width:34px; height:34px; flex-shrink:0; border-radius:9px; background:#EFF6FF;
                    border:1px solid #BFDBFE; text-align:center; line-height:32px; font-size:16px; }
        .feat .ft { color:#0F172A; font-weight:600; font-size:14px; }
        .feat .fd { color:#64748B; font-size:12.5px; line-height:1.6; }
        .note { color:#94A3B8; font-size:12px; margin-top:14px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <div class="eyebrow">RECOMMENDATION STRATEGY PLATFORM</div>
      <h1><span class="h1chip" style="background:linear-gradient(135deg,#5C7CB8,#7E9BC9)">🧪</span>推荐策略配置平台</h1>
      <div class="sub">人工可控 × 算法个性 × 系统兜底：三级策略优先级架构，支持坑位 / 客群 / 素材配置与 A/B 分流</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="callout" style="background:#EFF6FF;border-left:3px solid #2563EB;border-radius:8px;padding:10px 14px;color:#1E293B;font-size:13.5px;line-height:1.7;">💡 <b>演示说明：</b>本页面基于真实项目经验还原——策略模型与配置流程源自实际工作中的方案，数据为脱敏示例，交互原型由本人独立设计并借助 AI 编程工具实现。</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.35, 1], gap="large")
    with c1:
        st.markdown('<div style="color:#0F172A;font-weight:700;font-size:15px;margin:8px 0 4px 0;">📌 业务背景</div>', unsafe_allow_html=True)
        st.markdown(
            """金融推荐系统需要同时满足三方诉求：**运营要可控**（重点资源必须按策略曝光）、
**算法要个性**（协同过滤提升转化）、**系统要兜底**（任何情况下坑位不能空）。
平台把三者抽象为**三级策略优先级**，按坑位配置竞争规则。"""
        )
        st.markdown('<div style="color:#0F172A;font-weight:700;font-size:15px;margin:18px 0 4px 0;">🏗️ 三级策略优先级</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="panel">
<div class="tier"><div class="tno" style="background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;">P1</div>
<div><div class="tname">人工强干预</div><div class="tdesc">运营按坑位 × 客群 × 素材定向配置，权重高时优先生效</div></div></div>
<div class="tier"><div class="tno" style="background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;">P2</div>
<div><div class="tname">算法推荐</div><div class="tdesc">协同过滤（Item-CF）按用户行为个性化召回</div></div></div>
<div class="tier"><div class="tno" style="background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0;">P3</div>
<div><div class="tname">全量兜底</div><div class="tdesc">人工默认池或指定算法兜底，保证坑位永不空窗</div></div></div>
</div>
""", unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="color:#0F172A;font-weight:700;font-size:15px;margin:8px 0 4px 0;">✨ 核心设计</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="feat"><div class="fi">🎯</div><div><div class="ft">坑位 × 客群 × 素材 三维配置</div>
<div class="fd">运营选择投放坑位、定向客群标签、配置素材与跳转链接</div></div></div>
<div class="feat"><div class="fi">⚖️</div><div><div class="ft">权重竞争机制</div>
<div class="fd">人工 / 算法 / 兜底按权重竞争同一坑位，权重越大优先级越高</div></div></div>
<div class="feat"><div class="fi">🔀</div><div><div class="ft">A/B 分流实验</div>
<div class="fd">稳定哈希分流（同用户永远同组），支持算法或客群维度测试</div></div></div>
<div class="feat"><div class="fi">🎛️</div><div><div class="ft">运营后台可视化</div>
<div class="fd">策略配置持久化（GitHub API 写回），配置即发布</div></div></div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns([1, 6])
    with b1:
        if st.button("🚀 开始演示", use_container_width=True, type="primary"):
            st.session_state.reco_started = True
            st.rerun()
    st.markdown('<div class="note">演示流程：先在「运营配置」发布策略 → 再到「选品与效果」查看三级竞争实况</div>', unsafe_allow_html=True)
    st.stop()

# 演示模式：返回介绍
_back, _rest = st.columns([1, 8])
with _back:
    if st.button("📖 介绍", use_container_width=True):
        st.session_state.reco_started = False
        st.rerun()

# ============================================================
# 公共依赖与配置
# ============================================================
CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recommendation-demo", "configs",
)
os.makedirs(CONFIG_DIR, exist_ok=True)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation-demo"))

from data_providers.slot_provider import get_slots_with_source
from data_providers.product_provider import get_products_with_source
from data_providers.user_provider import get_users_with_source
from data_providers.interaction_provider import get_interactions_with_source
from recommender import recommend_by_algorithm, build_item_similarity

GITHUB_REPO = "sayawang1/portfolio"
GITHUB_BRANCH = "main"
CONFIG_REPO_PATH = "recommendation-demo/configs"

ICON_OPTIONS = ["campaign_icon_1.png", "campaign_icon_2.png", "campaign_icon_3.png", "campaign_icon_4.png", "campaign_icon_5.png"]
URL_OPTIONS = [f"https://app.example.com/product/{i}" for i in range(1, 6)]
MODEL_TO_ALGO = {
    "DeepFM v3（精排）": "deepfm",
    "双塔召回（DSSM）": "dssm",
    "字节千人千面": "bytedance_ps",
    "协同过滤 ItemCF": "item_cf",
    "内容召回 ContentBased": "content_based",
}
TIME_OPTIONS = ["2026 Q3 大促周期 (9/1-9/30)", "长期有效", "2026 双十一周期 (11/1-11/11)", "自定义时间段"]
AUDIENCE_OPTIONS = ["全量用户", "注册用户", "非注册游客", "精准·VIP会员", "新用户", "高净值客户", "活跃用户", "流失预警用户"]
MODEL_OPTIONS = list(MODEL_TO_ALGO.keys())
CONDITION_OPTIONS = ["设备: iOS/Android", "地域: 上海/杭州", "时段: 10:00-22:00", "用户: 已登录"]
ADV_OPTIONS = ["冷启动: 新用户走热门", "频控: 每用户日 3 次", "去重: 排除已点击"]
AUDIENCE_COND_MAP = {
    "全量用户": "",
    "注册用户": "is_registered == 1",
    "非注册游客": "is_registered == 0",
    "精准·VIP会员": "is_vip == 1",
    "新用户": "is_new == 1",
    "高净值客户": "aum_level == '高'",
    "活跃用户": "is_active == 1",
    "流失预警用户": "is_churn_risk == 1",
}


def _extract_number(icon_str, url_str):
    m = re.search(r"/(\d+)/?$", url_str)
    if m:
        return int(m.group(1))
    m = re.search(r"icon_(\d+)", icon_str)
    if m:
        return int(m.group(1))
    return None


def _get_github_token():
    try:
        return st.secrets["GITHUB_TOKEN"]
    except Exception:
        return None


def _github_commit_file(filename, content_dict):
    token = _get_github_token()
    if not token:
        return False, "未配置 GITHUB_TOKEN"
    path = f"{CONFIG_REPO_PATH}/{filename}"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=5)
        sha = r.json().get("sha") if r.status_code == 200 else None
    except Exception:
        sha = None
    content_str = json.dumps(content_dict, ensure_ascii=False, indent=2)
    content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    payload = {"message": f"update {filename}", "content": content_b64, "branch": GITHUB_BRANCH}
    if sha:
        payload["sha"] = sha
    try:
        r = requests.put(url, headers=headers, json=payload, timeout=10)
        return (True, "已提交") if r.status_code in (200, 201) else (False, f"HTTP {r.status_code}")
    except Exception as e:
        return False, f"异常: {str(e)}"


def load_json(filename, default=None):
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(filename, data):
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 推荐引擎逻辑
# ============================================================
def _match_condition(user, condition):
    if not condition:
        return True
    try:
        return bool(eval(condition, {"__builtins__": {}}, dict(user)))
    except Exception:
        return False


def _in_time_window(start_str, end_str):
    try:
        now = datetime.now()
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        return start <= now <= end
    except Exception:
        return True


def _stable_hash_group(user_id, slot_id, group_a_ratio):
    key = f"{user_id}_{slot_id}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return "A" if (h % 100) < group_a_ratio else "B"


def _build_manual_result(rule, products):
    raw_items = rule.get("items", [])
    enriched = []
    for it in raw_items:
        if isinstance(it, str):
            enriched.append({"product_id": it, "icon": "", "jump_url": ""})
        elif isinstance(it, dict):
            enriched.append({
                "product_id": it.get("product_id", ""),
                "icon": it.get("icon", ""),
                "jump_url": it.get("jump_url", ""),
            })

    if not enriched:
        return None

    ids = [e["product_id"] for e in enriched]
    matched = products[products["product_id"].isin(ids)].copy()
    if len(matched) == 0:
        return None

    meta_map = {e["product_id"]: e for e in enriched}
    matched["icon"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("icon", ""))
    matched["jump_url"] = matched["product_id"].map(lambda x: meta_map.get(x, {}).get("jump_url", ""))

    return {
        "source": "manual",
        "strategy_name": rule.get("remark", "人工强干预"),
        "strategy_id": rule.get("rule_id", "-"),
        "weight": rule.get("manual_weight", 80),
        "items": matched,
        "audience": rule.get("audience_label", "-"),
    }


def get_manual_result(slot_id, user, products):
    data_path = os.path.join(CONFIG_DIR, "manual_config.json")
    if not os.path.exists(data_path):
        return None
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    non_fallback, fallback = [], []
    for rule in data.get("manual_rules", []):
        if not rule.get("enabled"):
            continue
        if rule.get("slot_id") != slot_id:
            continue
        if not _in_time_window(rule.get("start_time"), rule.get("end_time")):
            continue
        if not _match_condition(user, rule.get("base_condition", "")):
            continue
        if not _match_condition(user, rule.get("target_condition", "")):
            continue
        if rule.get("is_fallback"):
            fallback.append(rule)
        else:
            non_fallback.append(rule)

    for rule in non_fallback:
        result = _build_manual_result(rule, products)
        if result:
            return result
    for rule in fallback:
        result = _build_manual_result(rule, products)
        if result:
            return result
    return None


def get_algorithm_result(slot_id, user, interactions, item_sim, products):
    data_path = os.path.join(CONFIG_DIR, "algorithm_config.json")
    if not os.path.exists(data_path):
        return None
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    bind = data.get("slot_algorithm_bind", {}).get(slot_id)
    if not bind:
        return None
    if not _match_condition(user, bind.get("base_condition", "")):
        return None
    if bind.get("require_registered") and not user.get("is_registered", 1):
        return None

    algo_id = bind.get("algo_id", "item_cf")
    algo_weight = bind.get("algo_weight", 65)
    ab = bind.get("ab_test", {})
    ab_group = "-"
    if ab.get("enabled"):
        ab_group = _stable_hash_group(user["user_id"], slot_id, ab.get("group_a_ratio", 50))
        algo_id = ab.get("group_a_algo", algo_id) if ab_group == "A" else ab.get("group_b_algo", algo_id)

    items = recommend_by_algorithm(user["user_id"], algo_id, interactions, item_sim, products, top_n=5)
    if items is not None and len(items) > 0:
        items = items.copy()
        items["icon"] = ""
        items["jump_url"] = ""
        return {
            "source": "algorithm",
            "strategy_name": f"算法推荐（{algo_id}）",
            "strategy_id": f"algo_{algo_id}",
            "weight": algo_weight,
            "items": items,
            "ab_group": ab_group,
        }
    return None


def get_fallback_result(slot_id, user, products, interactions, item_sim):
    data_path = os.path.join(CONFIG_DIR, "manual_config.json")
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for rule in data.get("manual_rules", []):
                if not rule.get("enabled") or not rule.get("is_fallback"):
                    continue
                if rule.get("slot_id") != slot_id:
                    continue
                if not _in_time_window(rule.get("start_time"), rule.get("end_time")):
                    continue
                if not _match_condition(user, rule.get("base_condition", "")):
                    continue
                if not _match_condition(user, rule.get("target_condition", "")):
                    continue
                result = _build_manual_result(rule, products)
                if result:
                    result["source"] = "fallback_manual"
                    result["strategy_name"] = "人工兜底"
                    return result
        except Exception:
            pass

    items = recommend_by_algorithm(user["user_id"], "popularity", interactions, item_sim, products, top_n=5)
    items = items.copy()
    items["icon"] = ""
    items["jump_url"] = ""
    return {
        "source": "fallback_algorithm",
        "strategy_name": "全量兜底（热门）",
        "strategy_id": "algo_popularity",
        "weight": 0,
        "items": items,
    }


def _merge_manual_algo(manual_items, algo_items, total=5):
    manual_list = manual_items.to_dict("records")
    manual_ids = set(manual_items["product_id"].tolist())
    algo_filtered = algo_items[~algo_items["product_id"].isin(manual_ids)].to_dict("records")
    merged = (manual_list + algo_filtered)[:total]
    return pd.DataFrame(merged)


def execute_strategy(slot_id, user, interactions, item_sim, products):
    manual = get_manual_result(slot_id, user, products)
    algo = get_algorithm_result(slot_id, user, interactions, item_sim, products)

    if manual and algo:
        manual_score = manual["weight"] * 100 + algo["weight"]
        algo_score = algo["weight"] * 100 + manual["weight"]
        if manual_score >= algo_score:
            merged = _merge_manual_algo(manual["items"], algo["items"], total=5)
            return {**manual, "items": merged, "manual_items": manual["items"], "algo_items": algo["items"],
                    "competition": f"人工 {manual_score} vs 算法 {algo_score} → 人工胜出",
                    "ab_group": algo.get("ab_group", "-")}
        else:
            merged = _merge_manual_algo(algo["items"], manual["items"], total=5)
            return {**algo, "items": merged, "manual_items": manual["items"], "algo_items": algo["items"],
                    "competition": f"人工 {manual_score} vs 算法 {algo_score} → 算法胜出"}
    elif manual:
        return {**manual, "manual_items": manual["items"], "algo_items": pd.DataFrame(), "competition": "仅人工命中"}
    elif algo:
        return {**algo, "manual_items": pd.DataFrame(), "algo_items": algo["items"], "competition": "仅算法命中"}
    else:
        fallback = get_fallback_result(slot_id, user, products, interactions, item_sim)
        return {**fallback, "manual_items": pd.DataFrame(), "algo_items": fallback["items"], "competition": "均未命中 → 兜底"}


# ============================================================
# 演示主体：两个子菜单（先配置，后看效果）
# ============================================================
tab_cfg, tab_eff = st.tabs(["⚙️ 运营配置（第一步：先配置）", "📊 选品与效果（第二步：看效果）"])

# ============================================================
# Tab A：运营配置（原独立后台，逻辑不变）
# ============================================================
with tab_cfg:
    st.caption("人工 > 算法 > 兜底 ｜ 权重竞争：人工权重×100+算法权重")

    st.markdown("### 📋 已发布策略列表")
    manual_data = load_json("manual_config.json", {"manual_rules": []})
    rules = manual_data.get("manual_rules", [])

    if rules:
        for idx, rule in enumerate(rules):
            with st.container(border=True):
                c1, c2, c3, c4, c5, c6 = st.columns([1.3, 2.0, 1.5, 1.2, 1.2, 0.9])
                with c1:
                    st.markdown(f"**{rule['rule_id']}**")
                with c2:
                    st.markdown(f"{rule.get('slot_id', '-')} ｜ {rule.get('remark', '-')}")
                with c3:
                    st.markdown(f"客群: {rule.get('audience_label', '-')}")
                with c4:
                    st.markdown(f"人工权重: **{rule.get('manual_weight', '-')}**")
                with c5:
                    st.markdown(f"兜底: {'是' if rule.get('is_fallback') else '否'}")
                with c6:
                    if st.button("🗑️ 删除", key=f"del_{idx}"):
                        rules.pop(idx)
                        manual_data["manual_rules"] = rules
                        save_json("manual_config.json", manual_data)
                        _github_commit_file("manual_config.json", manual_data)
                        st.rerun()
    else:
        st.info("暂无已发布策略。")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### 基础配置（大范围）")
        with st.container(border=True):
            slot_id_cfg = st.selectbox("位置选择", [s["slot_id"] for s in get_slots_with_source()[0]], index=0, key="base_slot")
            time_window = st.selectbox("生效时间", TIME_OPTIONS, index=0, key="base_time")

            custom_start, custom_end = None, None
            if time_window == "自定义时间段":
                d1, d2 = st.columns(2)
                with d1:
                    custom_start = st.date_input("开始日期", value=datetime(2026, 1, 1))
                with d2:
                    custom_end = st.date_input("结束日期", value=datetime(2026, 12, 31))

            base_audience = st.selectbox("基础客群（大范围）", AUDIENCE_OPTIONS, index=0, key="base_audience")
            st.checkbox("全量发布（跳过灰度，对所有匹配用户生效）", value=True)

    with col_right:
        st.markdown("### 算法策略")
        with st.container(border=True):
            model = st.selectbox("模型选择", MODEL_OPTIONS, index=0, key="algo_model")
            st.number_input("召回数量 Top-K", min_value=10, max_value=200, value=200, step=10)
            algo_weight = st.slider("策略权重（与人工竞争用，0-100）", 0, 100, 65, 5)
            require_registered = st.toggle("仅注册用户生效（非注册用户走兜底）", value=True)

            ab_enabled = st.toggle("启用 AB 测试", value=False)
            group_a = 70
            ab_group_a_algo = "协同过滤 ItemCF"
            ab_group_b_algo = "字节千人千面"
            if ab_enabled:
                group_a = st.slider("A 组流量 %", 0, 100, 70, 5)
                d1, d2 = st.columns(2)
                with d1:
                    ab_group_a_algo = st.selectbox("A 组算法", MODEL_OPTIONS, index=3, key="ab_a")
                with d2:
                    ab_group_b_algo = st.selectbox("B 组算法", MODEL_OPTIONS, index=2, key="ab_b")

    st.divider()

    st.markdown("### 人工策略（大范围中的小范围）")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            manual_audiences = st.multiselect("人工客群", AUDIENCE_OPTIONS, default=["精准·VIP会员"], key="manual_audience")
            icon_selected = st.multiselect("图标展示", ICON_OPTIONS, default=[], key="icon_select")
            url_selected = st.multiselect("跳转链接", URL_OPTIONS, default=[], key="url_select")
            manual_weight = st.slider("人工权重（与算法竞争用，0-100）", 0, 100, 80, 5)
            is_fallback = st.toggle("作为兜底配置", value=False)
        with c2:
            st.markdown("**生效条件**")
            st.multiselect("条件", CONDITION_OPTIONS, default=CONDITION_OPTIONS, label_visibility="collapsed")
            st.markdown("**高级设置**")
            st.multiselect("设置", ADV_OPTIONS, default=ADV_OPTIONS, label_visibility="collapsed")

    st.divider()

    c_cancel, c_draft, c_publish = st.columns([6, 2, 2])
    with c_draft:
        if st.button("保存草稿", use_container_width=True):
            st.info("草稿已保存")

    with c_publish:
        if st.button("发布策略", use_container_width=True, type="primary"):
            if time_window == "自定义时间段" and custom_start and custom_end:
                start_str = f"{custom_start.strftime('%Y-%m-%d')} 00:00:00"
                end_str = f"{custom_end.strftime('%Y-%m-%d')} 23:59:59"
            elif time_window == "长期有效":
                start_str, end_str = "2025-01-01 00:00:00", "2030-12-31 23:59:59"
            else:
                start_str, end_str = "2026-09-01 00:00:00", "2026-09-30 23:59:59"

            conds = []
            for a in manual_audiences:
                if a == "全量用户":
                    conds = []
                    break
                c = AUDIENCE_COND_MAP.get(a, "")
                if c:
                    conds.append(c)

            if not conds:
                target_type, target_condition = "all", ""
                audience_label = "继承基础客群"
            else:
                target_type, target_condition = "tag", " and ".join(conds)
                audience_label = " + ".join(manual_audiences)

            base_cond = AUDIENCE_COND_MAP.get(base_audience, "")

            items_payload = []
            max_len = max(len(icon_selected), len(url_selected))
            for idx in range(max_len):
                icon = icon_selected[idx] if idx < len(icon_selected) else ""
                url = url_selected[idx] if idx < len(url_selected) else ""
                num = _extract_number(icon, url)
                pid = f"P{num:03d}" if num else f"P{idx+1:03d}"
                items_payload.append({"product_id": pid, "icon": icon, "jump_url": url})

            manual_data = load_json("manual_config.json", {"manual_rules": []})
            manual_data["manual_rules"].append({
                "rule_id": f"rule_{uuid.uuid4().hex[:6]}",
                "slot_id": slot_id_cfg,
                "position_id": "p1",
                "enabled": True,
                "base_audience": base_audience,
                "base_condition": base_cond,
                "target_type": target_type,
                "target_condition": target_condition,
                "audience_label": audience_label,
                "items": items_payload,
                "traffic_pct": 100,
                "manual_weight": manual_weight,
                "algo_weight": algo_weight,
                "start_time": start_str,
                "end_time": end_str,
                "is_fallback": is_fallback,
                "remark": f"{audience_label} 人工强推",
            })
            save_json("manual_config.json", manual_data)
            _github_commit_file("manual_config.json", manual_data)

            algo_id = MODEL_TO_ALGO.get(model, "item_cf")
            algo_data = load_json("algorithm_config.json", {"algorithms": [], "slot_algorithm_bind": {}})
            algo_data.setdefault("slot_algorithm_bind", {})[slot_id_cfg] = {
                "algo_id": algo_id,
                "algo_weight": algo_weight,
                "base_condition": base_cond,
                "require_registered": require_registered,
                "ab_test": {
                    "enabled": ab_enabled,
                    "group_a_ratio": group_a if ab_enabled else 100,
                    "group_a_algo": MODEL_TO_ALGO.get(ab_group_a_algo, "item_cf"),
                    "group_b_algo": MODEL_TO_ALGO.get(ab_group_b_algo, "bytedance_ps"),
                },
            }
            save_json("algorithm_config.json", algo_data)
            _github_commit_file("algorithm_config.json", algo_data)

            st.success("✅ 策略已发布！切到「选品与效果」页签查看效果。")
            st.rerun()

# ============================================================
# Tab B：选品与效果（原 Demo 主界面，逻辑不变）
# ============================================================
with tab_eff:
    st.markdown("#### 📈 选品 & 效果预览")
    if st.button("🔄 清除缓存并刷新", key="clear_cache_btn"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    users_all, user_source = get_users_with_source()
    products_all, product_source = get_products_with_source()
    interactions_all, interaction_source = get_interactions_with_source(users_all, products_all)
    item_sim_all = build_item_similarity(interactions_all)

    user_options = [""] + users_all["user_id"].tolist()
    if "selected_user_id" not in st.session_state:
        st.session_state.selected_user_id = ""

    c_u1, c_u2, c_u3 = st.columns([2, 3, 3])
    with c_u1:
        selected_user_id = st.selectbox(
            "👤 选择用户",
            user_options,
            index=user_options.index(st.session_state.selected_user_id) if st.session_state.selected_user_id in user_options else 0,
            key="user_select",
        )
        st.session_state.selected_user_id = selected_user_id

    user_row = None
    if selected_user_id:
        user_row = users_all[users_all["user_id"] == selected_user_id].iloc[0]

    with c_u2:
        if user_row is not None:
            type_label = {"vip": "VIP 会员", "registered": "注册用户", "guest": "非注册游客"}.get(user_row.get("user_type", ""), "-")
            vip_label = "✅ 是" if user_row['is_vip'] == 1 else "❌ 否"
            st.markdown(f"**类型**：{type_label} ｜ **VIP**：{vip_label} ｜ **资产等级**：{user_row['aum_level']}")
        else:
            st.markdown("**类型**：- ｜ **VIP**：- ｜ **资产等级**：-")
    with c_u3:
        if user_row is not None:
            st.markdown(f"**新用户**：{'是' if user_row.get('is_new') == 1 else '否'} ｜ **活跃**：{'是' if user_row.get('is_active') == 1 else '否'} ｜ **流失预警**：{'是' if user_row.get('is_churn_risk') == 1 else '否'}")
        else:
            st.markdown("**新用户**：- ｜ **活跃**：- ｜ **流失预警**：-")

    slot_list, slot_source = get_slots_with_source()

    SLOT_ORDER = ["app_home_banner", "app_home_feed", "web_sidebar", "ad_layer"]
    SLOT_LABEL = {
        "app_home_banner": "🎯 APP首页Banner",
        "app_home_feed": "🎯 APP首页信息流",
        "web_sidebar": "🎯 网页侧边栏",
        "ad_layer": "🎯 广告层",
    }

    available_slots = [s["slot_id"] for s in slot_list]
    ordered_slots = [sid for sid in SLOT_ORDER if sid in available_slots]
    if not ordered_slots:
        ordered_slots = SLOT_ORDER

    if "selected_slot_id" not in st.session_state:
        st.session_state.selected_slot_id = ""

    btn_cols = st.columns(4)
    for i, sid in enumerate(ordered_slots):
        is_selected = (sid == st.session_state.selected_slot_id)
        with btn_cols[i]:
            if is_selected:
                st.markdown('<div class="slot-active">', unsafe_allow_html=True)
                if st.button(SLOT_LABEL.get(sid, sid), key=f"slot_btn_{sid}"):
                    st.session_state.selected_slot_id = ""
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button(SLOT_LABEL.get(sid, sid), key=f"slot_btn_{sid}"):
                    st.session_state.selected_slot_id = sid
                    st.rerun()

    slot_id = st.session_state.selected_slot_id
    show_data = bool(user_row is not None and slot_id)

    if not show_data:
        st.markdown(
            '<div class="no-data">请先选择「用户」和「坑位」，才会展示推荐结果。还没配置策略？先到「运营配置」页签发布一条。</div>',
            unsafe_allow_html=True,
        )
    else:
        result = execute_strategy(slot_id, user_row, interactions_all, item_sim_all, products_all)

        source_map = {
            "manual": "✋ 人工强干预",
            "algorithm": "🤖 算法推荐",
            "fallback_manual": "🛟 人工兜底",
            "fallback_algorithm": "🛟 兜底（热门）",
        }
        source_label = source_map.get(result["source"], result["source"])

        sid = result.get("strategy_id", "-")
        algo_name_map = {
            "algo_deepfm": "DeepFM v3（精排）",
            "algo_dssm": "双塔召回（DSSM）",
            "algo_bytedance_ps": "字节千人千面",
            "algo_item_cf": "协同过滤 ItemCF",
            "algo_content_based": "内容召回 ContentBased",
            "algo_popularity": "兜底（热门）",
        }
        if sid.startswith("rule_"):
            algo_label = f"人工规则 {sid}"
        else:
            algo_label = algo_name_map.get(sid, sid)

        st.markdown(
            f'<span class="cond-badge">策略来源: {source_label}</span>'
            f'<span class="cond-badge">命中: {algo_label}</span>'
            f'<span class="cond-badge">竞争: {result.get("competition", "-")}</span>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        merged_items = result.get("items")
        manual_items = result.get("manual_items")
        algo_items = result.get("algo_items")

        if merged_items is not None and len(merged_items) > 0:
            is_single_slot = "banner" in slot_id.lower()

            if is_single_slot:
                final = merged_items.iloc[0]
                icon_html = '<span class="rec-icon">🎁</span>' if final.get("icon") else ""
                st.markdown("### 🎯 最终展示位（唯一）")
                st.markdown(f"""
                <div class="final-card">
                    <h3>{icon_html} 🏆 {final.get('name', final['product_id'])}</h3>
                    <div style="color:#64748B;">类别：{final.get('category', '-')} ｜ 风险：R{final.get('risk_level', '-')} ｜ 热度：{final.get('popularity', '-')}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### 📋 推荐列表（候选池）")
                for _, row in merged_items.iterrows():
                    icon_html = '<span class="rec-icon">🎁</span>' if row.get("icon") else ""
                    url = row.get("jump_url", "")
                    url_line = f'<div class="meta">🔗 <a href="{url}" target="_blank" style="color:#2563EB;">{url}</a></div>' if url else ""
                    st.markdown(f"""
                    <div class="rec-card">
                        <h4>{icon_html}{row.get('name', row['product_id'])}</h4>
                        <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
                        {url_line}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("### 📋 推荐列表")
                for _, row in merged_items.iterrows():
                    icon_html = '<span class="rec-icon">🎁</span>' if row.get("icon") else ""
                    url = row.get("jump_url", "")
                    url_line = f'<div class="meta">🔗 <a href="{url}" target="_blank" style="color:#2563EB;">{url}</a></div>' if url else ""
                    st.markdown(f"""
                    <div class="rec-card">
                        <h4>{icon_html}{row.get('name', row['product_id'])}</h4>
                        <div class="meta">类别：{row.get('category', '-')} ｜ 风险：R{row.get('risk_level', '-')} ｜ 热度：{row.get('popularity', '-')}</div>
                        {url_line}
                    </div>
                    """, unsafe_allow_html=True)

            m_count = len(manual_items) if manual_items is not None else 0
            a_count = len(algo_items) if algo_items is not None else 0
            st.markdown(
                f'<div class="mock-note">人工命中 {m_count} 条 ｜ 算法召回 {a_count} 条 ｜ 合并去重后共 {len(merged_items)} 条（模拟数据）</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="no-data">该坑位暂未配置策略，请到「运营配置」页签发布后查看效果。</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<p class="footer-note">数据源: 商品={product_source} ｜ 用户={user_source} ｜ 行为={interaction_source} ｜ 坑位={slot_source}</p>',
        unsafe_allow_html=True,
    )
