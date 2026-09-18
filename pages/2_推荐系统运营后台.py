"""推荐系统运营后台 - 展示与管理配置"""
import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, save_json, get_config_dir

CONFIG_DIR = get_config_dir("recommendation-demo")

st.set_page_config(page_title="推荐系统运营后台", page_icon="🎛️", layout="wide")
st.title("🎛️ 推荐系统运营后台")
st.caption("所有配置实时生效。修改配置后，请前往「推荐系统Demo」查看前端效果（记得清缓存）。")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 坑位管理", "✋ 人工强干预", "🧠 算法配置", "🧪 AB测试"])

# ---------- Tab 1: 坑位管理 ----------
with tab1:
    st.subheader("📋 当前坑位列表")
    slots_path = os.path.join(CONFIG_DIR, "slots.json")
    slots = load_json(slots_path, {"slots": []})
    if slots["slots"]:
        st.dataframe(slots["slots"], use_container_width=True, hide_index=True)
    else:
        st.info("暂无坑位配置。")

    st.divider()
    st.subheader("➕ 新增坑位")
    with st.form("add_slot"):
        sid = st.text_input("坑位ID（英文，如 app_detail_bottom）", "app_detail_bottom")
        sname = st.text_input("坑位名称", "详情页底部推荐")
        platform = st.selectbox("平台", ["app", "web"])
        if st.form_submit_button("保存新增坑位"):
            slots["slots"].append({"slot_id": sid, "slot_name": sname, "platform": platform, "enabled": True})
            save_json(slots_path, slots)
            st.success("保存成功！")
            st.rerun()

# ---------- Tab 2: 人工强干预 ----------
with tab2:
    st.subheader("📋 当前人工强干预规则")
    manual = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
    if manual["manual_rules"]:
        st.dataframe(manual["manual_rules"], use_container_width=True, hide_index=True)
    else:
        st.info("暂无人工强干预规则。")

    st.divider()
    st.subheader("➕ 新增人工强干预")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]

    with st.form("manual_form"):
        slot_id = st.selectbox("选择坑位", slot_options)
        items = st.text_input("指定内容ID（逗号分隔）", "P001,P002")
        target_type = st.selectbox("目标人群", ["all", "tag"])
        target_condition = st.text_input("标签条件（Python表达式，如 is_vip == 1）", "is_vip == 1")
        pct = st.slider("分流比例（%）", 0, 100, 20, 5)
        is_fallback = st.checkbox("作为兜底人工配置（算法失败时才用）")
        remark = st.text_input("备注", "VIP客户人工强推")
        if st.form_submit_button("保存人工配置"):
            data = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
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
            save_json(os.path.join(CONFIG_DIR, "manual_config.json"), data)
            st.success("保存成功！")
            st.rerun()

# ---------- Tab 3: 算法配置 ----------
with tab3:
    st.subheader("📋 当前坑位算法绑定")
    algo_data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), {"algorithms": [], "slot_algorithm_bind": {}})
    bind_data = []
    for s_id, config in algo_data.get("slot_algorithm_bind", {}).items():
        bind_data.append({
            "坑位": s_id,
            "绑定算法": config.get("algo_id", "-"),
            "AB测试": "✅ 启用" if config.get("ab_test", {}).get("enabled") else "❌ 未启用"
        })
    if bind_data:
        st.dataframe(bind_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无算法绑定配置。")

    st.divider()
    st.subheader("➕ 新增/修改算法绑定")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]
    algo_options = [a["algo_id"] for a in algo_data.get("algorithms", [])]

    with st.form("algo_form"):
        slot_id = st.selectbox("选择坑位", slot_options, key="algo_slot")
        algo_id = st.selectbox("绑定算法", algo_options)
        if st.form_submit_button("保存算法绑定"):
            algo_data.setdefault("slot_algorithm_bind", {}).setdefault(slot_id, {})["algo_id"] = algo_id
            save_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), algo_data)
            st.success("保存成功！")
            st.rerun()

# ---------- Tab 4: AB测试 ----------
with tab4:
    st.subheader("📋 当前 AB 测试配置")
    algo_data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), {"algorithms": [], "slot_algorithm_bind": {}})
    ab_table = []
    for s_id, config in algo_data.get("slot_algorithm_bind", {}).items():
        ab = config.get("ab_test", {})
        ab_table.append({
            "坑位": s_id,
            "状态": "✅ 启用" if ab.get("enabled") else "❌ 未启用",
            "A组算法": ab.get("group_a_algo", "-"),
            "B组算法": ab.get("group_b_algo", "-"),
            "A组流量": f"{ab.get('group_a_ratio', '-')}%" if ab.get("enabled") else "-"
        })
    if ab_table:
        st.dataframe(ab_table, use_container_width=True, hide_index=True)
    else:
        st.info("暂无AB测试配置。")

    st.divider()
    st.subheader("➕ 新增/修改 AB 测试")
    slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
    slot_options = [s["slot_id"] for s in slots["slots"]]
    algo_options = [a["algo_id"] for a in algo_data.get("algorithms", [])]

    with st.form("ab_form"):
        slot_id = st.selectbox("选择坑位", slot_options, key="ab_slot")
        enabled = st.checkbox("启用AB测试", value=True)
        ratio = st.slider("A组流量比例（%）", 0, 100, 50, 5)
        group_a = st.selectbox("A组算法", algo_options, index=0)
        group_b = st.selectbox("B组算法", algo_options, index=len(algo_options)-1)
        if st.form_submit_button("保存AB测试"):
            algo_data.setdefault("slot_algorithm_bind", {}).setdefault(slot_id, {})["ab_test"] = {
                "enabled": enabled,
                "group_a_ratio": ratio,
                "group_a_algo": group_a,
                "group_b_algo": group_b,
            }
            save_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), algo_data)
            st.success("保存成功！")
            st.rerun()
