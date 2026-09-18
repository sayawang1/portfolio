"""推荐系统运营后台"""
import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, save_json, get_config_dir

CONFIG_DIR = get_config_dir("recommendation-demo")

st.set_page_config(page_title="推荐系统运营后台", page_icon="🎛️", layout="wide")
st.title("🎛️ 推荐系统运营后台")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 坑位管理", "✋ 人工强干预", "🧠 算法配置", "🧪 AB测试"])

# ---------- Tab 1: 坑位管理 ----------
with tab1:
    st.subheader("坑位列表")
    slots_path = os.path.join(CONFIG_DIR, "slots.json")
    slots = load_json(slots_path, {"slots": []})
    st.dataframe(slots["slots"], use_container_width=True)

    st.divider()
    st.subheader("新增坑位")
    with st.form("add_slot"):
        sid = st.text_input("坑位ID", "app_detail_bottom")
        sname = st.text_input("坑位名称", "详情页底部推荐")
        platform = st.selectbox("平台", ["app", "web"])
        if st.form_submit_button("保存"):
            slots["slots"].append({"slot_id": sid, "slot_name": sname, "platform": platform, "enabled": True})
            save_json(slots_path, slots)
            st.success("保存成功！")
            st.rerun()

# ---------- Tab 2: 人工强干预 ----------
with tab2:
    st.subheader("人工强干预配置")
    st.caption("优先级最高，命中后直接覆盖算法。勾选『作为兜底』则只在算法失败时生效。")

    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]

    with st.form("manual_form"):
        slot_id = st.selectbox("选择坑位", slot_options)
        items = st.text_input("指定内容ID（逗号分隔）", "P001,P002")
        target_type = st.selectbox("目标人群", ["all", "tag"])
        target_condition = st.text_input("标签条件（Python表达式）", "is_vip == 1")
        pct = st.slider("分流比例（%）", 0, 100, 20, 5)
        is_fallback = st.checkbox("作为兜底人工配置（算法失败时才用）")
        remark = st.text_input("备注", "VIP客户人工强推")
        if st.form_submit_button("保存"):
            path = os.path.join(CONFIG_DIR, "manual_config.json")
            data = load_json(path, {"manual_rules": []})
            data["manual_rules"].append({
                "rule_id": f"rule_{len(data['manual_rules'])+1:03d}",
                "slot_id": slot_id,
                "priority": 1 if not is_fallback else 99,
                "enabled": True,
                "target_type": target_type,
                "target_condition": target_condition,
                "items": [x.strip() for x in items.split(",") if x.strip()],
                "traffic_pct": pct,
                "start_time": "2025-01-01 00:00:00",
                "end_time": "2030-12-31 23:59:59",
                "operator": "运营",
                "remark": remark,
                "is_fallback": is_fallback,
            })
            save_json(path, data)
            st.success("保存成功！")
            st.rerun()

    st.divider()
    st.subheader("当前人工规则")
    manual = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
    st.dataframe(manual["manual_rules"], use_container_width=True)

# ---------- Tab 3: 算法配置 ----------
with tab3:
    st.subheader("算法绑定")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]
    algo_data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"),
                          {"algorithms": [], "slot_algorithm_bind": {}})
    algo_options = [a["algo_id"] for a in algo_data["algorithms"]]

    with st.form("algo_form"):
        slot_id = st.selectbox("选择坑位", slot_options, key="algo_slot")
        algo_id = st.selectbox("绑定算法", algo_options)
        if st.form_submit_button("保存"):
            algo_data.setdefault("slot_algorithm_bind", {}).setdefault(slot_id, {})["algo_id"] = algo_id
            save_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), algo_data)
            st.success("保存成功！")

    st.divider()
    st.subheader("算法库")
    st.dataframe(algo_data["algorithms"], use_container_width=True)

# ---------- Tab 4: AB测试 ----------
with tab4:
    st.subheader("AB测试配置")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]
    algo_data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"),
                          {"algorithms": [], "slot_algorithm_bind": {}})
    algo_options = [a["algo_id"] for a in algo_data["algorithms"]]

    with st.form("ab_form"):
        slot_id = st.selectbox("选择坑位", slot_options, key="ab_slot")
        enabled = st.checkbox("启用AB测试", value=True)
        ratio = st.slider("A组流量比例（%）", 0, 100, 50, 5)
        group_a = st.selectbox("A组算法", algo_options, index=0)
        group_b = st.selectbox("B组算法", algo_options, index=len(algo_options)-1)
        if st.form_submit_button("保存"):
            algo_data.setdefault("slot_algorithm_bind", {}).setdefault(slot_id, {})["ab_test"] = {
                "enabled": enabled,
                "group_a_ratio": ratio,
                "group_a_algo": group_a,
                "group_b_algo": group_b,
            }
            save_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), algo_data)
            st.success("保存成功！")
