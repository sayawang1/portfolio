"""推荐系统运营后台 - 深色版"""
import streamlit as st
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, save_json, get_config_dir

CONFIG_DIR = get_config_dir("recommendation-demo")

# 深色主题设置
st.set_page_config(page_title="推荐系统运营后台", layout="wide", initial_sidebar_state="collapsed")

# 自定义深色 CSS
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #262730; color: #FAFAFA; }
    .stButton>button { background-color: #4A90D9; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #357ABD; }
    div[data-testid="stMetricValue"] { color: #4A90D9; }
    .stDataFrame { background-color: #1E1E1E; }
</style>
""", unsafe_allow_html=True)

st.title("🎛️ 推荐系统运营后台")
st.caption("配置策略优先级：人工强干预 > 算法推荐 > 兜底")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 坑位与展示位", "✋ 人工强干预", "🧠 算法配置", "🧪 AB测试"])

# ---------- Tab 1: 坑位与展示位 ----------
with tab1:
    st.subheader("坑位与展示位列表（外部同步）")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    for slot in slots["slots"]:
        with st.container(border=True):
            st.markdown(f"**{slot['slot_name']}** (`{slot['slot_id']}`) · {slot['platform'].upper()}")
            for pos in slot.get("positions", []):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ {pos['position_name']} (`{pos['position_id']}`)")

# ---------- Tab 2: 人工强干预 ----------
with tab2:
    st.subheader("人工强干预配置")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    pos_options = [(s["slot_id"], p["position_id"]) for s in slots["slots"] for p in s.get("positions", [])]

    with st.form("manual_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_slot = st.selectbox("选择坑位", [s["slot_id"] for s in slots["slots"]])
            selected_pos = st.selectbox("选择展示位", [p["position_id"] for s in slots["slots"] if s["slot_id"] == selected_slot for p in s["positions"]])
            items = st.text_input("指定内容ID（逗号分隔）", "P001,P002")
            target_type = st.selectbox("目标人群", ["all", "tag"])
            target_condition = st.text_input("标签条件（如 is_vip == 1）", "is_vip == 1")
        with col2:
            pct = st.slider("分流比例（%）", 0, 100, 100, 5)
            weight = st.slider("人工权重（0-100）", 0, 100, 80, 5)
            remark = st.text_input("备注", "VIP客户强推")
            is_fallback = st.checkbox("作为兜底配置（算法失败时生效）")
        if st.form_submit_button("保存配置"):
            data = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
            data["manual_rules"].append({
                "rule_id": f"rule_{len(data['manual_rules'])+1:03d}",
                "slot_id": selected_slot,
                "position_id": selected_pos,
                "enabled": True,
                "target_type": target_type,
                "target_condition": target_condition,
                "items": [x.strip() for x in items.split(",") if x.strip()],
                "traffic_pct": pct,
                "manual_weight": weight,
                "start_time": "2025-01-01 00:00:00",
                "end_time": "2030-12-31 23:59:59",
                "operator": "运营",
                "remark": remark,
                "is_fallback": is_fallback
            })
            save_json(os.path.join(CONFIG_DIR, "manual_config.json"), data)
            st.success("保存成功！")
            st.rerun()

    st.divider()
    st.subheader("当前人工规则")
    manual = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
    st.dataframe(manual["manual_rules"], use_container_width=True, hide_index=True)

# ---------- Tab 3 & 4 逻辑类似，此处略（可用原版逻辑，替换成新字段） ----------
