import streamlit as st

# 1. 页面基本设置
st.set_page_config(
    page_title="saya | 产品经理作品集",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 自定义 CSS (终极暴力覆盖版)
st.markdown("""
<style>
/* =========================================================
   1. 清理所有原生干扰和顶部白条
   ========================================================= */
header, [data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; }

/* 全局背景色与基础设置 */
.stApp { background-color: #E8F3F0 !important; color: #111111 !important; }
.block-container { 
    padding-top: 2rem !important; 
    padding-bottom: 2rem !important; 
    max-width: 1280px !important; 
}

/* 强制两列等高，间距统一 */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 2rem !important;
}

/* =========================================================
   2. 左侧整列变卡片 (暴力锁死)
   ========================================================= */
[data-testid="column"]:nth-of-type(1) {
    background-color: #FEFEFD !important;
    border: 1.5px solid #DBDCDC !important;
    border-radius: 20px !important;
    padding: 2.5rem 2rem !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.03) !important;
    
    /* 强制撑满高度，使用 flex 排版 */
    min-height: calc(100vh - 4rem) !important;
    display: flex !important;
    flex-direction: column !important;
}

/* 强制内部容器撑满 */
[data-testid="column"]:nth-of-type(1) > div[data-testid="stVerticalBlock"] {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
}

/* 强行将“联系关注”踢到最底部 */
[data-testid="column"]:nth-of-type(1) > div[data-testid="stVerticalBlock"] > div:last-child {
    margin-top: auto !important;
}

/* =========================================================
   3. 按钮强杀原生蓝色 (浅绿底黑字)
   ========================================================= */
/* 基础按钮 */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background-color: #FEFEFD !important;
    border: 1.5px solid #DBDCDC !important;
    border-radius: 12px !important;
    color: #111111 !important;
    justify-content: flex-start !important;
    padding: 10px 16px !important;
    box-shadow: none !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #F2F6F3 !important;
    border-color: #C6DFD1 !important;
}

/* 强杀选中态 (Primary) 的蓝色 */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #E9F4EE !important;
    border-color: #C6DFD1 !important;
    color: #111111 !important;
}
/* 暴力强制内部所有子元素（文字和 SVG）变为纯黑 */
div[data-testid="stButton"] > button[kind="primary"] * {
    color: #111111 !important;
    fill: #111111 !important;
}

/* =========================================================
   4. 左侧文字、标签与联系区样式
   ========================================================= */
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.brand-logo {
    width: 40px; height: 40px; border-radius: 50%;
    background: #2C3E50; color: #FFF;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 17px;
}
.brand-name { font-size: 15px; font-weight: 800; color: #000000; }
.brand-sub { font-size: 12px; color: #111111; margin-top: 2px; }

.big-name {
    font-size: 44px; font-weight: 800; color: #000000;
    letter-spacing: -1px; line-height: 1.15;
    margin: 2px 0 16px 0;
}

.chip {
    display: inline-block; background: #F1F6F2; color: #111111;
    padding: 6px 14px; border-radius: 16px; font-size: 13px;
    margin: 0 6px 8px 0; border: 1.5px solid #DBDCDC;
}
.chip-blue { background: #E9F4EE; color: #111111; border: 1.5px solid #C6DFD1; }

.side-divider { border: none; border-top: 1.5px solid #E8F3F0; margin: 20px 0 18px 0; }
.side-label { color: #111111; font-size: 13px; font-weight: 700; margin-bottom: 12px; }
.side-footer { color: #111111; font-size: 12px; margin-top: 16px; }
.contact-box {
    background: #FEFEFD; border: 1.5px solid #DBDCDC;
    border-radius: 12px; padding: 12px 14px; display: flex; align-items: center; gap: 12px;
    margin-bottom: 10px;
}
.contact-icon {
    width: 34px; height: 34px; border-radius: 8px; background: #F1F6F2;
    display: flex; align-items: center; justify-content: center; font-size: 16px; border: 1px solid #DBDCDC;
}
.contact-info { display: flex; flex-direction: column; }
.contact-label { font-size: 11.5px; color: #111111; margin-bottom: 2px; }
.contact-value { font-size: 13.5px; font-weight: 700; color: #111111; text-decoration: none; }
.contact-value:hover { text-decoration: underline; }

/* =========================================================
   5. 右侧内容区
   ========================================================= */
.timeline-card {
    background: #FEFEFD; border-radius: 16px; padding: 24px 28px;
    border: 1.5px solid #DBDCDC; box-shadow: 0 4px 12px rgba(0,0,0,.03);
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 24px;
}
.timeline-eyebrow { color: #111111; font-size: 12px; letter-spacing: 2px; font-weight: 800; }
.timeline-title { color: #000000; font-size: 20px; font-weight: 800; margin-top: 6px; }
.timeline-sub { color: #111111; font-size: 14px; margin-top: 6px; }

/* 右侧卡片等高对齐 */
[data-testid="column"]:nth-of-type(2) [data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 1.5rem !important;
}
[data-testid="column"]:nth-of-type(2) [data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
}

a.matrix-card-link { text-decoration: none; display: flex; height: 100%; color: inherit; width: 100%; }
.matrix-card {
    background: #FEFEFD; border-radius: 16px; padding: 24px;
    border: 1.5px solid #DBDCDC; box-shadow: 0 4px 12px rgba(0,0,0,.03);
    display: flex; flex-direction: column; width: 100%; height: 100%;
    cursor: pointer; transition: transform .2s, box-shadow .2s, border-color .2s;
}
.matrix-card:hover { transform: translateY(-3px); border-color: #A9D2B9; box-shadow: 0 12px 24px rgba(45,90,65,.10); }
.mc-icon {
    width: 48px; height: 48px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; margin-bottom: 20px; flex-shrink: 0;
}
.icon-blue   { background: #EEF2F9; }
.icon-teal   { background: #EDF7F4; }
.icon-purple { background: #F3F1FA; }
.icon-orange { background: #FBF3EC; }
.mc-title { font-size: 18px; font-weight: 800; color: #000000; margin-bottom: 4px; }
.mc-sub   { font-size: 13px; color: #111111; margin-bottom: 14px; }
.mc-desc  { font-size: 14px; color: #111111; line-height: 1.7; margin-bottom: 20px; flex-grow: 1; }
.mc-chips { margin-bottom: 0; flex-shrink: 0; display: flex; flex-wrap: wrap; gap: 6px; }
.mc-chip {
    display: inline-block; background: #F1F6F2; color: #111111;
    border: 1.5px solid #DBDCDC; border-radius: 8px; padding: 4px 12px; font-size: 12px;
}

.panel { background: #FEFEFD; border-radius: 16px; padding: 32px; border: 1.5px solid #DBDCDC; box-shadow: 0 4px 12px rgba(0,0,0,.03); }
</style>
""", unsafe_allow_html=True)

# ===== Tab 状态 =====
ss = st.session_state
ss.setdefault("nav_tab", "首页")

# ===== 路由 =====
GOTO_MAP = {
    "reco":  "pages/1_推荐系统Demo.py",
    "cs":    "pages/3_智能客服.py",
    "mkt":   "pages/4_精准营销平台.py",
    "reg":   "pages/5_监管报送规则引擎.py",
    "promo": "pages/6_促销活动配置平台.py",
}
goto = st.query_params.get("goto")
if goto in GOTO_MAP:
    st.query_params.clear()
    st.switch_page(GOTO_MAP[goto])
    st.stop()

# ===== 布局 =====
side, main = st.columns([1, 2.8], gap="large")

# ================= 左侧：名片栏 =================
with side:
    # 我们使用容器包裹所有左侧元素，迫使 Flex 布局生效
    with st.container():
        st.markdown("""
        <div class="brand-row">
            <div class="brand-logo">S</div>
            <div>
                <div class="brand-name">saya</div>
                <div class="brand-sub">作品集 · Portfolio</div>
            </div>
        </div>
        <div class="big-name">saya</div>
        <div style="margin-bottom: 24px;">
            <span class="chip chip-blue">🖥 平台产品经理</span>
            <span class="chip chip-blue">🤖 AI 产品经理</span>
            <div style="margin-top: 8px;">
                <span class="chip">📖 看书</span>
                <span class="chip">🌍 全球旅游执行中</span>
                <span class="chip">🤿 潜水</span>
                <span class="chip">📷 摄影</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🏠 首页", use_container_width=True, key="nav_home",
                     type="primary" if ss["nav_tab"] == "首页" else "secondary"):
            ss["nav_tab"] = "首页"; st.rerun()
        if st.button("📝 文章", use_container_width=True, key="nav_posts",
                     type="primary" if ss["nav_tab"] == "文章" else "secondary"):
            ss["nav_tab"] = "文章"; st.rerun()
        if st.button("🗂 项目", use_container_width=True, key="nav_projects",
                     type="primary" if ss["nav_tab"] == "项目" else "secondary"):
            ss["nav_tab"] = "项目"; st.rerun()

        # 联系方式 (由于 CSS 中有 margin-top: auto，它会被推到最底)
        st.markdown("""
        <hr class="side-divider">
        <div class="side-label">联系 / 关注</div>
        <div class="contact-box">
            <div class="contact-icon">✉️</div>
            <div class="contact-info">
                <div class="contact-label">Email</div>
                <a class="contact-value" href="mailto:saya_jing@163.com">saya_jing@163.com</a>
            </div>
        </div>
        <div class="side-footer">© saya</div>
        """, unsafe_allow_html=True)

# ================= 右侧：内容区 =================
CARD_RECO = """
<a class="matrix-card-link" href="?goto=reco">
<div class="matrix-card">
    <div class="mc-icon icon-blue">🎯</div>
    <div class="mc-title">推荐策略配置平台</div>
    <div class="mc-sub">推荐系统 · 平台策略</div>
    <div class="mc-desc">金融推荐需同时满足运营可控、算法个性化与系统兜底。三级策略优先级：人工强干预 &gt; 算法推荐 &gt; 全量兜底，支持权重竞争与 A/B 分流。</div>
    <div class="mc-chips"><span class="mc-chip">坑位×客群×素材</span><span class="mc-chip">权重竞争</span><span class="mc-chip">A/B 分流</span></div>
</div>
</a>
"""

CARD_CS = """
<a class="matrix-card-link" href="?goto=cs">
<div class="matrix-card">
    <div class="mc-icon icon-teal">🤖</div>
    <div class="mc-title">智能客服与智能坐席辅助</div>
    <div class="mc-sub">智能客服 · 在线可对话</div>
    <div class="mc-desc">RAG + 大模型 + 智能体，双链路可切换，三维人机边界（风险 × 置信度 × 情绪），含情绪识别、实时话术、质检与服务总结。转人工率 -60%。</div>
    <div class="mc-chips"><span class="mc-chip">多 Agent</span><span class="mc-chip">在线对话</span><span class="mc-chip">转人工 -60%</span></div>
</div>
</a>
"""

CARD_MKT = """
<a class="matrix-card-link" href="?goto=mkt">
<div class="matrix-card">
    <div class="mc-icon icon-purple">💳</div>
    <div class="mc-title">精准营销平台</div>
    <div class="mc-sub">营销平台 · 可交互 Demo</div>
    <div class="mc-desc">营销流程抽象为「客群筛选 → 权益策略 → 触达渠道」三个可配置模块，185 场活动、覆盖 4495 万+ 人次、带动消费 18.9 亿元，95% 活动配置化上线。</div>
    <div class="mc-chips"><span class="mc-chip">客群筛选</span><span class="mc-chip">配置化 95%</span><span class="mc-chip">18.9 亿</span></div>
</div>
</a>
"""

CARD_REG = """
<a class="matrix-card-link" href="?goto=reg">
<div class="matrix-card">
    <div class="mc-icon icon-orange">🏦</div>
    <div class="mc-title">监管报送规则引擎</div>
    <div class="mc-sub">金融合规 · 可交互 Demo</div>
    <div class="mc-desc">不做填报工具、做规则引擎——监管条文拆解为自动化校验规则，完成中信登系统对接；现场改规则可看到异常数实时变化，政策更新以配置生效。</div>
    <div class="mc-chips"><span class="mc-chip">规则引擎</span><span class="mc-chip">中信登对接</span><span class="mc-chip">配置生效</span></div>
</div>
</a>
"""

CARD_PROMO = """
<a class="matrix-card-link" href="?goto=promo">
<div class="matrix-card">
    <div class="mc-icon icon-orange">🎁</div>
    <div class="mc-title">云服务促销活动配置平台</div>
    <div class="mc-sub">营销配置平台 · 可交互 Demo</div>
    <div class="mc-desc">大促活动从「一次一配、研发排期」到「模板领用 + 配置化上线」：模板中心 → 五步活动配置 → CRM / 客服数据对接 → 官网发布，活动全生命周期在线可演示。</div>
    <div class="mc-chips"><span class="mc-chip">模板化复用</span><span class="mc-chip">五步配置流</span><span class="mc-chip">CRM &amp; 官网对接</span></div>
</div>
</a>
"""

def render_projects():
    cards = [CARD_RECO, CARD_CS, CARD_MKT, CARD_REG, CARD_PROMO]
    for i in range(0, len(cards), 2):
        row = cards[i:i + 2]
        cols = st.columns(2, gap="medium")
        for col, card_html in zip(cols, row):
            with col:
                st.markdown(card_html, unsafe_allow_html=True)

with main:
    if ss["nav_tab"] == "首页":
        st.markdown("""
        <div class="timeline-card">
            <div>
                <div class="timeline-eyebrow">TIMELINE</div>
                <div class="timeline-title">最近记录</div>
                <div class="timeline-sub">公开项目与可交互演示，基于真实项目经验还原，业务数据已脱敏。</div>
            </div>
            <div style="text-align: right; flex-shrink: 0; margin-left: 20px;">
                <span class="mc-chip">Beta</span><br>
                <span style="color:#111111; font-size:13px; margin-top:6px; display:inline-block;">2026/11/03 更新</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_projects()

    elif ss["nav_tab"] == "文章":
        st.markdown("""
        <div class="panel" style="text-align:center; padding: 80px 32px;">
            <div style="font-size: 40px; margin-bottom: 16px;">📝</div>
            <div style="font-size:18px; font-weight:800; color:#000000; margin-bottom:16px;">文章整理中</div>
            <div style="font-size:15px; color:#111111; line-height:1.8;">产品方法论与项目复盘文章正在整理，稍后发布。</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="timeline-card">
            <div>
                <div class="timeline-eyebrow">PROJECTS</div>
                <div class="timeline-title">全部项目</div>
                <div class="timeline-sub">5 个可在线交互的产品演示，点击卡片直接进入。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_projects()
