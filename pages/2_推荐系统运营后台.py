"""推荐系统运营后台 - 深色 + 白底输入框"""
import streamlit as st
import os
import json
import uuid
from datetime import datetime

from data_providers.slot_provider import get_slots_with_source

CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recommendation-demo", "configs",
)
os.makedirs(CONFIG_DIR, exist_ok=True)


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
    .badge {
        display: inline-block; padding: 3px 10px; margin: 3px 6px 3px 0;
        background-color: #1F2937; color: #9CA3AF;
        border-radius: 10px; font-size: 12px;
    }
    .footer-note { color: #6B7280; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎛️ 推荐系统运营后台")
st.caption("按图1原型：基础配置 / 算法策略 / 人工策略")

TIME_OPTIONS = ["2026 Q3 大促周期 (9/1-9/30)", "长期有效", "2026 双十一周期 (11/1-11/11)", "自定义时间段"]
AUDIENCE_OPTIONS = ["全量用户", "精准·VIP会员", "新用户", "高净值客户", "活跃用户", "流失预警用户"]
MODEL_OPTIONS = ["DeepFM v3（精排）", "双塔召回（DSSM）", "字节千人千面", "协同过滤 ItemCF", "内容召回 ContentBased", "热门兜底 Popularity"]
CONDITION_OPTIONS = ["设备: iOS/Android", "地域: 上海/杭州", "时段: 10:00-22:00", "用户: 已登录"]
ADV_OPTIONS = ["冷启动: 新用户走热门", "频控: 每用户日 3 次", "去重: 排除已点击"]

slot_list, slot_source = get_slots_with_source()
slot_options = [s["slot_id"] for s in slot_list]

# ========== 顶部：策略列表 ==========
st.markdown("### 📋 已发布策略列表")
manual_data = load_json("manual_config.json", {"manual_rules": []})
rules = manual_data.get("manual_rules", [])

if rules:
    for idx, rule in enumerate(rules):
        with st.container(border=True):
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2.5, 1.3, 1.3, 1.3, 1.2])
            with c1:
                st.markdown(f"**{rule['rule_id']}**")
            with c2:
                st.markdown(f"{rule.get('slot_id', '-')} ｜ {rule.get('remark', '-')}")
            with c3:
                st.markdown(f"人工权重: **{rule.get('manual_weight', '-')}**")
            with c4:
                st.markdown(f"分流: {rule.get('traffic_pct', '-')}%")
            with c5:
                st.markdown(f"客群: {rule.get('audience_label', '-')}")
            with c6:
                if st.button("🗑️ 删除", key=f"del_{idx}"):
                    rules.pop(idx)
                    manual_data["manual_rules"] = rules
                    save_json("manual_config.json", manual_data)
                    st.rerun()
else:
    st.info("暂无已发布策略。")

st.divider()

# ========== 基础配置 + 算法策略 ==========
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 基础配置")
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

        audience = st.selectbox("客群标签", AUDIENCE_OPTIONS, index=0, key="base_audience")
        full_release = st.checkbox("全量发布（跳过灰度，对所有匹配用户生效）", value=True)

with col_right:
    st.markdown("### 算法策略")
    with st.container(border=True):
        model = st.selectbox("模型选择", MODEL_OPTIONS, index=0, key="algo_model")
        top_k = st.number_input("召回数量 Top-K", min_value=10, max_value=1000, value=200, step=10)
        algo_weight = st.slider("策略权重（与人工竞争用，0-100）", 0, 100, 65, 5)
        ab_enabled = st.toggle("AB 测试", value=True)
        group_a = 70
        if ab_enabled:
            group_a = st.slider("实验组 %", 0, 100, 70, 5)
            st.caption(f"A组 {group_a}% ｜ 对照组 {100 - group_a}%")
        with st.expander("模型参数（展开）"):
            st.text_input("recall_num", value="200")
            st.text_input("rank_num", value="20")

st.divider()

# ========== 人工策略 ==========
st.markdown("### 人工策略")
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        manual_audience = st.selectbox("客群标签", AUDIENCE_OPTIONS, index=1, key="manual_audience")
        icon_file = st.text_input("图标展示", value="campaign_icon.png")
        jump_url = st.text_input("跳转链接", value="https://app.example.com/promo/2026q3")
        manual_weight = st.slider("人工权重（与算法竞争用，0-100）", 0, 100, 80, 5)
        is_fallback = st.toggle("是否兜底", value=False)
    with c2:
        st.markdown("**生效条件**")
        selected_conds = st.multiselect("已选条件", CONDITION_OPTIONS, default=CONDITION_OPTIONS)
        badges_html = "".join([f'<span class="badge">{c}</span>' for c in selected_conds])
        st.markdown(badges_html, unsafe_allow_html=True)
        st.markdown("**高级设置**")
        selected_adv = st.multiselect("已选高级设置", ADV_OPTIONS, default=ADV_OPTIONS)
        adv_html = "".join([f'<span class="badge">{a}</span>' for a in selected_adv])
        st.markdown(adv_html, unsafe_allow_html=True)

st.divider()

# ========== 底部操作 ==========
c_cancel, c_draft, c_publish = st.columns([6, 2, 2])
with c_draft:
    if st.button("保存草稿", use_container_width=True):
        st.info("草稿已保存（演示）")
with c_publish:
    if st.button("发布策略", use_container_width=True):
        if time_window == "自定义时间段" and custom_start and custom_end:
            start_str = f"{custom_start.strftime('%Y-%m-%d')} 00:00:00"
            end_str = f"{custom_end.strftime('%Y-%m-%d')} 23:59:59"
        elif time_window == "长期有效":
            start_str, end_str = "2025-01-01 00:00:00", "2030-12-31 23:59:59"
        else:
            start_str, end_str = "2026-09-01 00:00:00", "2026-09-30 23:59:59"

        # 客群 → 条件映射
        if "VIP" in manual_audience:
            target_type, target_condition = "tag", "is_vip == 1"
        elif manual_audience == "新用户":
            target_type, target_condition = "tag", "is_new == 1"
        elif manual_audience == "高净值客户":
            target_type, target_condition = "tag", "aum_level == '高'"
        elif manual_audience == "活跃用户":
            target_type, target_condition = "tag", "is_active == 1"
        else:
            target_type, target_condition = "all", ""

        manual_data = load_json("manual_config.json", {"manual_rules": []})
        manual_data["manual_rules"].append({
            "rule_id": f"rule_{uuid.uuid4().hex[:6]}",
            "slot_id": slot_id,
            "position_id": "p1",
            "enabled": True,
            "target_type": target_type,
            "target_condition": target_condition,
            "audience_label": manual_audience,
            "items": ["P001", "P002", "P003"],
            "traffic_pct": 100,
            "manual_weight": manual_weight,
            "icon": icon_file,
            "jump_url": jump_url,
            "start_time": start_str,
            "end_time": end_str,
            "is_fallback": is_fallback,
            "remark": f"{manual_audience} 人工强推",
        })
        save_json("manual_config.json", manual_data)

        algo_data = load_json("algorithm_config.json", {"algorithms": [], "slot_algorithm_bind": {}})
        algo_data.setdefault("slot_algorithm_bind", {})[slot_id] = {
            "algo_id": "bytedance_ps" if "字节" in model else "item_cf",
            "algo_weight": algo_weight,
            "ab_test": {
                "enabled": ab_enabled,
                "group_a_ratio": group_a if ab_enabled else 100,
                "group_a_algo": "item_cf",
                "group_b_algo": "bytedance_ps",
            },
        }
        save_json("algorithm_config.json", algo_data)
        st.success(f"✅ 策略已发布！坑位：{slot_id} ｜ 人工权重：{manual_weight} ｜ 算法权重：{algo_weight}")
        st.rerun()

st.markdown(
    f'<p class="footer-note">数据源: 外部坑位系统（{slot_source}） ｜ 配置目录: recommendation-demo/configs ｜ 今日: 2026-09-21</p>',
    unsafe_allow_html=True,
)
  
