"""推荐系统运营后台 - 照图1原型设计（深色）"""
import streamlit as st
import os, sys, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_io import load_json, save_json, get_config_dir

CONFIG_DIR = get_config_dir("recommendation-demo")

st.set_page_config(page_title="推荐系统运营后台", page_icon="🎛️", layout="wide", initial_sidebar_state="collapsed")

# ============ 深色主题 CSS（图2风格） ============
st.markdown("""
<style>
    /* 整体背景 */
    .stApp { background-color: #0B0E11; color: #E6E6E6; }
    section[data-testid="stSidebar"] { background-color: #111417; }

    /* 标题 */
    h1, h2, h3, h4 { color: #FFFFFF !important; }

    /* 卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #151A1F;
        border: 1px solid #232A31;
        border-radius: 10px;
        padding: 12px;
    }

    /* 输入框 */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>div,
    .stMultiSelect>div>div>div {
        background-color: #1C2228 !important;
        color: #E6E6E6 !important;
        border: 1px solid #2A323A !important;
        border-radius: 6px !important;
    }

    /* 按钮 */
    .stButton>button {
        background-color: #FF4B4B; color: white; border-radius: 8px;
        border: none; padding: 8px 20px; font-weight: 600;
    }
    .stButton>button:hover { background-color: #E03E3E; }

    /* Tab */
    .stTabs [data-baseweb="tab"] { color: #9AA5B1; }
    .stTabs [aria-selected="true"] { color: #FF4B4B !important; }

    /* 标签徽章 */
    .badge {
        display: inline-block; padding: 2px 10px; margin-right: 6px;
        background-color: #1F2937; color: #9CA3AF;
        border-radius: 10px; font-size: 12px;
    }
    .badge-active { background-color: #FF4B4B; color: white; }

    /* 底部说明 */
    .footer-note { color: #6B7280; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎛️ 推荐系统运营后台")
st.caption("按图1原型：基础配置 / 算法策略 / 人工策略")

# 读取坑位
slots = load_json(os.path.join(CONFIG_DIR, "slots.json"), {"slots": []})
slot_options = [s["slot_id"] for s in slots["slots"]]

# ============ 第一行：基础配置 + 算法策略 ============
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 基础配置")
    with st.container(border=True):
        slot_id = st.selectbox("位置选择", slot_options, key="base_slot")
        time_window = st.selectbox("生效时间", ["2026 Q3 大促周期 (9/1-9/30)", "长期有效", "自定义"])
        audience = st.selectbox("客群标签", ["全量用户", "精准·VIP会员", "新用户"], key="base_audience")
        st.checkbox("全量发布（跳过灰度，对所有匹配用户生效）", value=True)

with col_right:
    st.markdown("#### 算法策略")
    with st.container(border=True):
        model = st.selectbox("模型选择", ["DeepFM v3（精排）", "双塔召回", "字节千人千面"])
        top_k = st.number_input("召回数量 Top-K", value=200, step=10)
        algo_weight = st.slider("策略权重（与人工竞争用，0-100）", 0, 100, 65, 5)
        ab_enabled = st.toggle("AB 测试", value=True)
        if ab_enabled:
            group_a = st.slider("实验组 %", 0, 100, 70, 5)
            st.caption(f"A组 {group_a}% ｜ 对照组 {100-group_a}%")
        with st.expander("模型参数（展开）"):
            st.text_input("recall_num", value="200")
            st.text_input("rank_num", value="20")

st.divider()

# ============ 第二行：人工策略 ============
st.markdown("#### 人工策略")
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        manual_audience = st.selectbox("客群标签", ["精准·VIP会员", "全量用户", "新用户"], key="manual_audience")
        icon_file = st.text_input("图标展示", "campaign_icon.png")
        jump_url = st.text_input("跳转链接", "https://app.example.com/promo/2026q3")
        manual_weight = st.slider("权重分配", 0, 100, 80, 5)
        is_fallback = st.toggle("是否兜底", value=True)
    with c2:
        st.markdown("**生效条件**")
        st.markdown(
            '<span class="badge">设备: iOS/Android</span>'
            '<span class="badge">地域: 上海/杭州</span>'
            '<span class="badge">时段: 10:00-22:00</span>'
            '<span class="badge">用户: 已登录</span>',
            unsafe_allow_html=True
        )
        st.button("+ 添加生效条件", key="add_cond")

        st.markdown("**高级设置**")
        st.markdown(
            '<span class="badge">冷启动: 新用户走热门</span>'
            '<span class="badge">频控: 每用户日 3 次</span>'
            '<span class="badge">去重: 排除已点击</span>',
            unsafe_allow_html=True
        )
        st.button("+ 添加高级设置", key="add_adv")

st.divider()

# ============ 底部操作 ============
c_cancel, c_draft, c_publish = st.columns([6, 2, 2])
with c_draft:
    st.button("保存草稿", use_container_width=True)
with c_publish:
    if st.button("发布策略", use_container_width=True):
        data = load_json(os.path.join(CONFIG_DIR, "manual_config.json"), {"manual_rules": []})
        data["manual_rules"].append({
            "rule_id": f"rule_{len(data['manual_rules'])+1:03d}",
            "slot_id": slot_id,
            "enabled": True,
            "target_type": "tag",
            "target_condition": "is_vip == 1" if "VIP" in manual_audience else "",
            "items": ["P001", "P002"],
            "traffic_pct": 100,
            "manual_weight": manual_weight,
            "algo_weight": algo_weight,
            "start_time": "2025-01-01 00:00:00",
            "end_time": "2030-12-31 23:59:59",
            "is_fallback": is_fallback,
            "remark": f"{manual_audience} 人工强推"
        })
        save_json(os.path.join(CONFIG_DIR, "manual_config.json"), data)

        algo_data = load_json(os.path.join(CONFIG_DIR, "algorithm_config.json"),
                              {"algorithms": [], "slot_algorithm_bind": {}})
        algo_data.setdefault("slot_algorithm_bind", {})[slot_id] = {
            "algo_id": "bytedance_ps" if "字节" in model else "item_cf",
            "algo_weight": algo_weight,
            "ab_test": {"enabled": ab_enabled, "group_a_ratio": group_a if ab_enabled else 100,
                        "group_a_algo": "item_cf", "group_b_algo": "bytedance_ps"}
        }
        save_json(os.path.join(CONFIG_DIR, "algorithm_config.json"), algo_data)
        st.success("策略已发布！")

st.markdown('<p class="footer-note">数据源: 外部坑位系统 ｜ 配置存储: recommendation-demo/configs ｜ 今日: 2026-09-21</p>',
            unsafe_allow_html=True)
