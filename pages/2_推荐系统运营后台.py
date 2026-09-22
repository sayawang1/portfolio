"""推荐系统运营后台"""
import streamlit as st
import os
import json
import uuid
import base64
import re
import requests
from datetime import datetime

from data_providers.slot_provider import get_slots_with_source

CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recommendation-demo", "configs",
)
os.makedirs(CONFIG_DIR, exist_ok=True)

GITHUB_REPO = "sayawang1/portfolio"
GITHUB_BRANCH = "main"
CONFIG_REPO_PATH = "recommendation-demo/configs"

ICON_OPTIONS = [
    "campaign_icon_1.png",
    "campaign_icon_2.png",
    "campaign_icon_3.png",
    "campaign_icon_4.png",
    "campaign_icon_5.png",
]

URL_OPTIONS = [
    "https://app.example.com/product/1",
    "https://app.example.com/product/2",
    "https://app.example.com/product/3",
    "https://app.example.com/product/4",
    "https://app.example.com/product/5",
]

MODEL_TO_ALGO = {
    "DeepFM v3（精排）": "deepfm",
    "双塔召回（DSSM）": "dssm",
    "字节千人千面": "bytedance_ps",
    "协同过滤 ItemCF": "item_cf",
    "内容召回 ContentBased": "content_based",
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


st.set_page_config(page_title="推荐系统运营后台", page_icon="🎛️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #E6E6E6; }
    h1, h2, h3, h4, h5 { color: #FFFFFF !important; }
    label, .stMarkdown, p { color: #E6E6E6 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
        background-color: #FFFFFF !important; color: #000000 !important;
        border: 1px solid #CCCCCC !important; border-radius: 6px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important; color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #000000 !important; }
    div[data-baseweb="popover"] div, ul[role="listbox"] li {
        background-color: #FFFFFF !important; color: #000000 !important;
    }
    ul[role="listbox"] li:hover { background-color: #F0F0F0 !important; }
    .stSlider [data-baseweb="slider"] div { color: #000000 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #151A1F; border: 1px solid #232A31;
        border-radius: 10px; padding: 14px;
    }
    .stButton>button {
        background-color: #FF4B4B; color: #FFFFFF;
        border: none; border-radius: 8px; padding: 8px 20px; font-weight: 600;
    }
    .stButton>button:hover { background-color: #E03E3E; }
    .footer-note { color: #6B7280; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎛️ 推荐系统运营后台")
st.caption("人工 > 算法 > 兜底 ｜ 权重竞争：人工权重×100+算法权重")

TIME_OPTIONS = ["2026 Q3 大促周期 (9/1-9/30)", "长期有效", "2026 双十一周期 (11/1-11/11)", "自定义时间段"]
AUDIENCE_OPTIONS = ["全量用户", "精准·VIP会员", "新用户", "高净值客户", "活跃用户", "流失预警用户"]
MODEL_OPTIONS = ["DeepFM v3（精排）", "双塔召回（DSSM）", "字节千人千面", "协同过滤 ItemCF", "内容召回 ContentBased"]
CONDITION_OPTIONS = ["设备: iOS/Android", "地域: 上海/杭州", "时段: 10:00-22:00", "用户: 已登录"]
ADV_OPTIONS = ["冷启动: 新用户走热门", "频控: 每用户日 3 次", "去重: 排除已点击"]

AUDIENCE_COND_MAP = {
    "全量用户": "",
    "精准·VIP会员": "is_vip == 1",
    "新用户": "is_registered == 1",
    "高净值客户": "aum_level == '高'",
    "活跃用户": "is_registered == 1",
    "流失预警用户": "is_registered == 1",
}

slot_list, slot_source = get_slots_with_source()
slot_options = [s["slot_id"] for s in slot_list]

# ========== 顶部：策略列表 ==========
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

# ========== 基础配置 + 算法策略 ==========
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 基础配置（大范围）")
    with st.container(border=True):
        slot_id = st.selectbox("位置选择", slot_options, index=0, key="base_slot")
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

        ab_enabled = st.toggle("启用 AB 测试", value=False)
        group_a = 70
        ab_group_a_algo = "item_cf"
        ab_group_b_algo = "bytedance_ps"
        if ab_enabled:
            group_a = st.slider("A 组流量 %", 0, 100, 70, 5)
            d1, d2 = st.columns(2)
            with d1:
                ab_group_a_algo = st.selectbox("A 组算法", MODEL_OPTIONS, index=3, key="ab_a")
            with d2:
                ab_group_b_algo = st.selectbox("B 组算法", MODEL_OPTIONS, index=2, key="ab_b")

st.divider()

# ========== 人工策略 ==========
st.markdown("### 人工策略（大范围中的小范围）")
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        manual_audiences = st.multiselect(
            "人工客群",
            AUDIENCE_OPTIONS,
            default=["精准·VIP会员"],
            key="manual_audience",
        )
        icon_selected = st.multiselect(
            "图标展示",
            ICON_OPTIONS,
            default=[],
            key="icon_select",
        )
        url_selected = st.multiselect(
            "跳转链接",
            URL_OPTIONS,
            default=[],
            key="url_select",
        )
        manual_weight = st.slider("人工权重（与算法竞争用，0-100）", 0, 100, 80, 5)
        is_fallback = st.toggle("作为兜底配置", value=False)
    with c2:
        st.markdown("**生效条件**")
        st.multiselect("条件", CONDITION_OPTIONS, default=CONDITION_OPTIONS, label_visibility="collapsed")
        st.markdown("**高级设置**")
        st.multiselect("设置", ADV_OPTIONS, default=ADV_OPTIONS, label_visibility="collapsed")

st.divider()

# ========== 底部操作 ==========
c_cancel, c_draft, c_publish = st.columns([6, 2, 2])
with c_draft:
    if st.button("保存草稿", use_container_width=True):
        st.info("草稿已保存")

with c_publish:
    if st.button("发布策略", use_container_width=True):
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

        # 产品映射：按图标/链接里的编号提取
        items_payload = []
        max_len = max(len(icon_selected), len(url_selected))
        for idx in range(max_len):
            icon = icon_selected[idx] if idx < len(icon_selected) else ""
            url = url_selected[idx] if idx < len(url_selected) else ""
            num = _extract_number(icon, url)
            pid = f"P{num:03d}" if num else f"P{idx+1:03d}"
            items_payload.append({
                "product_id": pid,
                "icon": icon,
                "jump_url": url,
            })

        manual_data = load_json("manual_config.json", {"manual_rules": []})
        manual_data["manual_rules"].append({
            "rule_id": f"rule_{uuid.uuid4().hex[:6]}",
            "slot_id": slot_id,
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
        algo_data.setdefault("slot_algorithm_bind", {})[slot_id] = {
            "algo_id": algo_id,
            "algo_weight": algo_weight,
            "base_condition": base_cond,
            "ab_test": {
                "enabled": ab_enabled,
                "group_a_ratio": group_a if ab_enabled else 100,
                "group_a_algo": MODEL_TO_ALGO.get(ab_group_a_algo, "item_cf"),
                "group_b_algo": MODEL_TO_ALGO.get(ab_group_b_algo, "bytedance_ps"),
            },
        }
        save_json("algorithm_config.json", algo_data)
        _github_commit_file("algorithm_config.json", algo_data)

        st.success("✅ 策略已发布！")
        st.rerun()

st.markdown(
    f'<p class="footer-note">数据源: 外部坑位系统（{slot_source}） ｜ 配置目录: recommendation-demo/configs ｜ 今日: 2026-09-22</p>',
    unsafe_allow_html=True,
)
