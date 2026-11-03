# -*- coding: utf-8 -*-
"""
pages/4_精准营销平台.py  ·  v2 重设计
平安信用卡精准营销平台 —— 客群筛选 → 策略配置 → 触达 → 实验归因
设计：深色卡片 + 自绘可视化（funnel / KPI / 对比卡），交互控件精简。
"""
import streamlit as st

st.set_page_config(page_title="精准营销平台", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# 全站统一样式 + 本页组件样式
# ============================================================
st.markdown("""
<style>
    [data-testid="stSidebar"] { display:none !important; }
    [data-testid="stSidebarNav"] { display:none !important; }
    .stApp { background-color:#F5F7FA; color:#1E293B; }
    h1,h2,h3,h4 { color:#0F172A !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid #E2E8F0 !important; background:#FFFFFF !important; border-radius:14px !important; }

    /* 顶部导航 */
    div[data-testid="stButton"] > button {
        border-radius:20px !important; border:1px solid transparent !important;
        background:transparent !important; color:#64748B !important;
        font-weight:600 !important; padding:8px 16px !important; transition:all .25s !important;
    }
    div[data-testid="stButton"] > button:hover { background:#FFFFFF !important; color:#0F172A !important; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background:#2563EB !important;color:#FFFFFF !important; box-shadow:0 4px 12px rgba(37,99,235,.3) !important;
    }

    /* Tabs 美化 */
    .stTabs [data-baseweb="tab-list"] { gap:6px; background:#FFFFFF; padding:6px; border-radius:12px; border:1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 18px; color:#64748B; font-weight:600; }
    .stTabs [aria-selected="true"] { background:#2563EB !important;color:#FFFFFF !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }

    /* 页头 */
    .hero { padding:26px 4px 6px 4px; }
    .hero .eyebrow { color:#2563EB; font-size:12px; letter-spacing:3px; font-weight:700; }
    .hero h1 { margin:6px 0 8px 0; }
    .hero .sub { color:#64748B; font-size:14px; }

    /* KPI 卡 */
    .kpi-row { display:flex; gap:14px; margin:18px 0 6px 0; }
    .kpi { flex:1; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px; }
    .kpi .label { color:#64748B; font-size:12px; margin-bottom:6px; }
    .kpi .value { color:#0F172A; font-size:26px; font-weight:800; }
    .kpi .value em { font-style:normal; font-size:14px; color:#64748B; font-weight:500; margin-left:4px; }
    .kpi.hot .value { color:#2563EB; }

    /* 漏斗条 */
    .frow { display:flex; align-items:center; gap:10px; margin:9px 0; }
    .frow .fname { width:96px; color:#64748B; font-size:12.5px; text-align:right; flex-shrink:0; }
    .frow .fbar-wrap { flex:1; background:#E9EEF5; border-radius:6px; height:20px; overflow:hidden; }
    .frow .fbar { height:100%; background:linear-gradient(90deg,#2563EB,#3B82F6); border-radius:6px; min-width:4px; }
    .frow .fval { width:56px; color:#1E293B; font-size:12.5px; font-weight:600; flex-shrink:0; }

    /* 预览大数字 */
    .big-num { font-size:44px; font-weight:800; color:#2563EB; line-height:1.1; }
    .big-num em { font-style:normal; font-size:18px; color:#64748B; font-weight:500; }

    /* chips */
    .chip { display:inline-block; padding:5px 12px; margin:3px 4px 3px 0; border-radius:16px;
            background:#FFFFFF; color:#1E293B; font-size:12px; border:1px solid #CBD5E1; }
    .chip.on { background:#EFF6FF; border-color:#2563EB; color:#1D4ED8; }

    /* 活动行卡 */
    .act { display:flex; align-items:center; gap:14px; background:#FFFFFF; border:1px solid #E2E8F0;
           border-radius:12px; padding:14px 18px; margin:8px 0; }
    .act:hover { border-color:#CBD5E1; }
    .act .id { color:#64748B; font-size:12px; font-family:monospace; width:82px; flex-shrink:0; }
    .act .nm { color:#0F172A; font-weight:600; font-size:15px; width:130px; flex-shrink:0; }
    .act .meta { color:#64748B; font-size:12.5px; flex:1; }
    .act .reach { color:#1E293B; font-size:13px; font-weight:600; width:90px; text-align:right; flex-shrink:0; }
    .pill { padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700; flex-shrink:0; }
    .pill.run  { background:#F0FDF4; color:#16A34A; }
    .pill.end  { background:#FFFFFF; color:#64748B; }
    .pill.wait { background:#FFFBEB; color:#D97706; }

    /* AB 对比卡 */
    .vs-wrap { display:flex; gap:16px; align-items:stretch; margin:14px 0; }
    .vs-card { flex:1; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:20px; }
    .vs-card.win { border-color:#2563EB; box-shadow:0 0 0 1px #2563EB; }
    .vs-card .tag { font-size:12px; color:#64748B; letter-spacing:2px; margin-bottom:10px; font-weight:700; }
    .vs-card.win .tag { color:#2563EB; }
    .vs-metric { margin:12px 0; }
    .vs-metric .ml { color:#64748B; font-size:12.5px; }
    .vs-metric .mv { color:#0F172A; font-size:22px; font-weight:700; }
    .delta { display:inline-block; margin-left:8px; padding:2px 8px; border-radius:10px;
             background:#F0FDF4; color:#16A34A; font-size:12px; font-weight:700; }

    /* 画像条 */
    .hrow { display:flex; align-items:center; gap:12px; margin:10px 0; }
    .hrow .hname { width:90px; color:#64748B; font-size:13px; text-align:right; flex-shrink:0; }
    .hrow .hbar-wrap { flex:1; height:26px; background:#E9EEF5; border-radius:8px; overflow:hidden; }
    .hrow .hbar { height:100%; border-radius:8px; }
    .hrow .hval { width:80px; color:#1E293B; font-size:13px; font-weight:600; flex-shrink:0; }

    .note { color:#64748B; font-size:12px; margin-top:14px; }
    .callout { background:#F8FAFC; border-left:3px solid #2563EB; border-radius:8px;
               padding:12px 16px; color:#475569; font-size:13.5px; line-height:1.7; margin-top:14px; }
    .section-t { color:#0F172A; font-weight:700; font-size:15px; margin:6px 0 10px 0; }
    /* 控件标签提亮 */
    [data-testid="stWidgetLabel"] p { color:#64748B !important; font-size:13px !important; }
        .h1chip { display:inline-flex; align-items:center; justify-content:center;width:52px; height:52px; border-radius:14px; font-size:26px; margin-right:14px;vertical-align:middle; box-shadow:0 6px 14px rgba(15,23,42,.18); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 全站导航
# ============================================================
NAV = [
    ("🏠", "app.py", False),
    ("🧪 推荐", "pages/1_推荐系统Demo.py", False),
    ("🤖 客服", "pages/3_智能客服.py", False),
    ("🎯 营销", "", True),
    ("🏦 报送", "pages/5_监管报送规则引擎.py", False),
    ("🎁 促销", "pages/6_促销活动配置平台.py", False),
]
cols = st.columns([0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 8])
for (label, target, active), c in zip(NAV, cols):
    with c:
        if active:
            st.button(label, use_container_width=True, type="primary")
        elif st.button(label, use_container_width=True):
            st.switch_page(target)

# ============================================================
# 页头
# ============================================================
st.markdown("""
<div class="hero">
  <div class="eyebrow">PRECISION MARKETING PLATFORM</div>
  <h1><span class="h1chip" style="background:linear-gradient(135deg,#8B7FC0,#A79DD4)">💳</span>精准营销平台</h1>
  <div class="sub">信用卡营销引擎：客群筛选 → 权益策略 → 触达渠道，三模块全配置化 ｜ 累计支撑 185 场活动 · 覆盖 4495 万+ 人次 · 带动消费 18.9 亿元</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="callout">💡 <b>演示说明：</b>本页面基于真实项目经验还原——产品结构、策略模型与决策逻辑源自实际工作中的方案，业务数据已脱敏，交互原型由本人独立设计并借助 AI 编程工具实现。</div>', unsafe_allow_html=True)

# ============================================================
# 核心逻辑
# ============================================================
BASE_POOL = 4600_0000  # 客户总盘 4600 万

def estimate_audience(card, activity, spend, tenure):
    rate = 1.0
    rate *= {"不限": 1.0, "金卡": 0.22, "白金卡": 0.06}[card]
    rate *= {"不限": 1.0, "活跃(30天内)": 0.41, "沉默(90天+)": 0.18}[activity]
    rate *= {"不限": 1.0, "月消费>5000": 0.27, "月消费<1000": 0.35}[spend]
    rate *= {"不限": 1.0, "账龄<6月": 0.14, "账龄>2年": 0.46}[tenure]
    return int(BASE_POOL * rate)

CARD_RATES  = {"不限": 1.0, "金卡": 0.22, "白金卡": 0.06}
ACT_RATES   = {"不限": 1.0, "活跃(30天内)": 0.41, "沉默(90天+)": 0.18}
SPEND_RATES = {"不限": 1.0, "月消费>5000": 0.27, "月消费<1000": 0.35}
TEN_RATES   = {"不限": 1.0, "账龄<6月": 0.14, "账龄>2年": 0.46}

CAMPAIGNS = [
    ("ACT23185", "新户首刷有礼", "新户 · 账龄<6月", "立减金", "App推送", "投放中", 86.2),
    ("ACT23186", "沉默用户唤醒", "90天未消费", "积分包", "短信", "投放中", 122.5),
    ("ACT23187", "分期费率折扣", "大额消费 · 分期潜在", "费率券", "App推送", "已结束", 45.8),
    ("ACT23188", "境外消费返现", "出境客群 · 近90天境外", "返现", "外呼", "待投放", 12.1),
]

# ============================================================
# Tabs
# ============================================================
tab1, tab2, tab3, tab4, tab_ai = st.tabs(["活动配置台", "活动管理", "A/B 实验归因", "客群画像", "🤖 AI 创建活动（Agent）"])

# ---------------- Tab 1：配置台 ----------------
with tab1:
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown('<div class="section-t">① 圈人条件（拖动即实时预估）</div>', unsafe_allow_html=True)
        card     = st.select_slider("卡种", ["不限", "金卡", "白金卡"])
        activity = st.select_slider("活跃度", ["不限", "活跃(30天内)", "沉默(90天+)"])
        spend    = st.select_slider("月消费", ["不限", "月消费>5000", "月消费<1000"])
        tenure   = st.select_slider("账龄", ["不限", "账龄<6月", "账龄>2年"])

        st.markdown('<div class="section-t" style="margin-top:18px;">② 权益与触达</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            benefit = st.selectbox("权益类型", ["立减金", "积分包", "费率券", "实物礼品", "里程"])
        with c2:
            name = st.text_input("活动名称", "十月消费翻倍礼")
        channel = st.multiselect("触达渠道", ["App推送", "短信", "外呼", "微信公众号"], default=["App推送"])

    with right:
        size = estimate_audience(card, activity, spend, tenure)
        rows = [
            ("卡种", card, CARD_RATES[card]),
            ("活跃度", activity, ACT_RATES[activity]),
            ("月消费", spend, SPEND_RATES[spend]),
            ("账龄", tenure, TEN_RATES[tenure]),
        ]
        funnel_html = "".join(
            f'<div class="frow"><div class="fname">{n} · {v}</div>'
            f'<div class="fbar-wrap"><div class="fbar" style="width:{r*100:.0f}%"></div></div>'
            f'<div class="fval">{r*100:.0f}%</div></div>'
            for n, v, r in rows
        )
        ch_html = "".join(
            f'<span class="chip on">✓ {ch}</span>' if ch in channel else f'<span class="chip">{ch}</span>'
            for ch in ["App推送", "短信", "外呼", "微信公众号"]
        )
        budget = size * 0.05 * 8
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:22px;">
          <div style="color:#64748B;font-size:12px;letter-spacing:2px;margin-bottom:6px;">LIVE PREVIEW · {name}</div>
          <div class="big-num">{size/10000:,.0f}<em> 万人</em></div>
          <div style="color:#64748B;font-size:12.5px;margin:4px 0 14px 0;">预估触达客群 · 占总盘 {size/BASE_POOL*100:.1f}%</div>
          {funnel_html}
          <div style="margin:16px 0 4px 0;color:#64748B;font-size:12px;">渠道</div>
          <div>{ch_html}</div>
          <div style="display:flex;gap:14px;margin-top:16px;">
            <div style="flex:1;background:#FFFFFF;border-radius:10px;padding:10px 14px;">
              <div style="color:#64748B;font-size:11.5px;">权益预算（5% 核销）</div>
              <div style="color:#0F172A;font-size:17px;font-weight:700;">¥{budget:,.0f}</div>
            </div>
            <div style="flex:1;background:#FFFFFF;border-radius:10px;padding:10px 14px;">
              <div style="color:#64748B;font-size:11.5px;">权益类型</div>
              <div style="color:#0F172A;font-size:17px;font-weight:700;">{benefit}</div>
            </div>
            <div style="flex:1;background:#FFFFFF;border-radius:10px;padding:10px 14px;">
              <div style="color:#64748B;font-size:11.5px;">配置耗时</div>
              <div style="color:#16A34A;font-size:17px;font-weight:700;">&lt; 2 分钟</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="callout"><b>设计要点：</b>筛选条件不是写死的 SQL，而是抽象为<b>可配置因子</b>——'
                '新业务来了组合因子即可上线，这就是「通用活动模型」的含义：185 场活动中 95% 无需研发排期。</div>',
                unsafe_allow_html=True)

# ---------------- Tab 2：活动管理 ----------------
with tab2:
    st.markdown("""
    <div class="kpi-row">
      <div class="kpi hot"><div class="label">累计活动</div><div class="value">185<em>场</em></div></div>
      <div class="kpi"><div class="label">客户参与</div><div class="value">4495<em>万+人次</em></div></div>
      <div class="kpi"><div class="label">带动消费</div><div class="value">18.9<em>亿元</em></div></div>
      <div class="kpi"><div class="label">配置化上线占比</div><div class="value">95<em>%</em></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-t" style="margin-top:20px;">活动列表</div>', unsafe_allow_html=True)
    pill_map = {"投放中": "run", "已结束": "end", "待投放": "wait"}
    for cid, nm, seg, ben, ch, status, reach in CAMPAIGNS:
        st.markdown(
            f"""<div class="act">
              <div class="id">{cid}</div>
              <div class="nm">{nm}</div>
              <div class="meta">客群：{seg} ｜ 权益：{ben} ｜ 渠道：{ch}</div>
              <div class="reach">触达 {reach} 万</div>
              <div class="pill {pill_map[status]}">{status}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    st.markdown('<div class="callout"><b>自动化设计：</b>状态流转由引擎按排期自动推进；转化率低于基线 50% 的活动自动标黄并通知运营——'
                '<b>运营后台只处理例外，不处理常规</b>。</div>', unsafe_allow_html=True)

# ---------------- Tab 3：A/B 归因 ----------------
with tab3:
    st.markdown('<div class="section-t">「新户成长」模板放量实验 · 两组各 ~230 万样本</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="vs-wrap">
      <div class="vs-card win">
        <div class="tag">实验组 · 精准策略</div>
        <div class="vs-metric"><div class="ml">拉新率</div><div class="mv">3.21%<span class="delta">+2.3pp</span></div></div>
        <div class="vs-metric"><div class="ml">MAU</div><div class="mv">41.36%<span class="delta">+2.81%</span></div></div>
        <div class="vs-metric"><div class="ml">人均消费</div><div class="mv">¥1,842<span class="delta">+1.74%</span></div></div>
      </div>
      <div class="vs-card">
        <div class="tag">对照组 · 常规策略</div>
        <div class="vs-metric"><div class="ml">拉新率</div><div class="mv">0.91%</div></div>
        <div class="vs-metric"><div class="ml">MAU</div><div class="mv">38.55%</div></div>
        <div class="vs-metric"><div class="ml">人均消费</div><div class="mv">¥1,810</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout">
      <b>实验判定：</b>主指标拉新率 +2.3pp 显著性通过；护栏指标（客诉率 / 退订率）无显著上升 → 放量全量；策略沉淀为「新户成长」模板供同类活动复用。<br>
      <b>平台内建实验能力：</b>策略验证从「发版验证」变为「线上实验」，试错成本从周级降到天级。
    </div>
    """, unsafe_allow_html=True)

# ---------------- Tab 4：客群画像 ----------------
with tab4:
    st.markdown('<div class="section-t">客群结构（万人）</div>', unsafe_allow_html=True)
    bars = [("金卡活跃", 1012, "#2563EB"), ("普卡活跃", 1886, "#3B82F6"), ("白金", 943, "#2563EB"), ("沉默客群", 759, "#64748B")]
    max_v = max(b[1] for b in bars)
    st.markdown("".join(
        f'<div class="hrow"><div class="hname">{n}</div>'
        f'<div class="hbar-wrap"><div class="hbar" style="width:{v/max_v*100:.0f}%;background:{c}"></div></div>'
        f'<div class="hval">{v:,} 万</div></div>'
        for n, v, c in bars
    ), unsafe_allow_html=True)

    st.markdown("""
    <div class="callout">
      <b>① 策略反哺：</b>把业务对用户行为的判断抽象为可配置因子（如设备特征），交由算法在召回 / 排序环节消费——
      个性化推荐系统即由此而来，A/B 验证「手机型号」因子带来 GMV +1.5%。<br>
      <b>② 疲劳度管理：</b>跨活动频控统一在客户维度，避免同一客户一周被 3 个活动轰炸——
      这是 CLM 与营销平台对接后才能做到的跨系统协同。
    </div>
    """, unsafe_allow_html=True)

# ---------------- Tab 5：AI 创建活动（Agent） ----------------
with tab_ai:
    import re as _re

    ss = st.session_state
    ss.setdefault("ai_input", "")
    ss.setdefault("ai_parsed", None)   # Agent 解析结果
    ss.setdefault("ai_approved", [])   # 已审批通过的活动

    st.markdown('<div class="section-t">🤖 AI Agent 创建活动 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 运营说"人话"，Agent 拆任务、调工具、出草稿，人做最终审批</span></div>', unsafe_allow_html=True)

    st.markdown("""
<div class="panel" style="margin-bottom:14px;">
<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:12.5px;color:#475569;">
  <span class="chip on">① 运营人员自然语言输入</span> <span style="color:#94A3B8;">→</span>
  <span class="chip on">② AI Agent 意图识别与任务拆解</span> <span style="color:#94A3B8;">→</span>
  <span class="chip on">③ 调用营销平台工具</span> <span style="color:#94A3B8;">→</span>
  <span class="chip on">④ 生成活动配置草稿</span> <span style="color:#94A3B8;">→</span>
  <span class="chip" style="border-color:#D97706;color:#D97706;">⑤ 人工确认与审批</span>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="callout" style="margin-top:0;"><b>为什么不是"AI 直接管数据库"？</b>运营不应该直接操作数据库、随意生成活动，而应该采用：<b>自然语言理解 + 规则引擎 + 现有营销平台能力 + 人工审核</b>——AI 负责把"人话"变成"配置"，规则引擎负责校验，人负责最终拍板。</div>', unsafe_allow_html=True)

    # ---- ① 自然语言输入 ----
    examples = [
        "针对90天没消费的沉默客户，发一批积分把他们拉回来，走短信触达，预算50万",
        "给近6个月注册的新户推首刷有礼，送立减金，App推送和短信一起上",
        "向持白金卡且月消费5000以上的客户推分期费率折扣活动",
    ]
    e1, e2, e3 = st.columns(3)
    for c, label, ex in [(e1, "📌 示例1 · 沉默客户唤醒", examples[0]), (e2, "📌 示例2 · 新户首刷", examples[1]), (e3, "📌 示例3 · 分期折扣", examples[2])]:
        with c:
            if st.button(label, use_container_width=True, key=f"aiex_{label}"):
                ss["ai_input"] = ex
                ss["ai_parsed"] = None
                st.rerun()

    user_text = st.text_area("① 运营人员自然语言输入（描述活动目标、客群、条件、奖励）", ss["ai_input"], height=90,
                             placeholder="例：针对90天没消费的沉默客户，发一批积分把他们拉回来，走短信触达，预算50万")

    go = st.button("🚀 开始解析（AI Agent 接手）", type="primary", use_container_width=True)
    if go:
        if not user_text.strip():
            st.warning("请先输入活动需求描述，或点击上方示例")
        else:
            ss["ai_input"] = user_text

            # ---- ② 意图识别与任务拆解（规则版 mock，结构与大模型版一致） ----
            text = user_text
            aud = None
            if _re.search(r"沉默|90天|流失", text): aud = "沉默(90天+)"
            elif _re.search(r"新户|新客|新用户|新注册", text): aud = "账龄<6月（新户）"
            elif _re.search(r"白金", text): aud = "白金卡客户"
            elif _re.search(r"金卡", text): aud = "金卡客户"

            benefit = None
            if _re.search(r"积分", text): benefit = "积分包"
            elif _re.search(r"费率|分期", text): benefit = "费率券"
            elif _re.search(r"返现", text): benefit = "返现"
            elif _re.search(r"立减|红包|代金", text) or aud and "新户" in aud: benefit = "立减金"

            channels = []
            if _re.search(r"短信", text): channels.append("短信")
            if _re.search(r"外呼|电话", text): channels.append("外呼")
            if _re.search(r"公众号|微信", text): channels.append("微信公众号")
            if _re.search(r"App|APP|推送", text) or not channels: channels.insert(0, "App推送")

            m_budget = _re.search(r"预算\s*([0-9.]+)\s*万", text)
            budget = f"{m_budget.group(1)} 万元" if m_budget else None
            m_name = _re.search(r"(推|办|做|发)(一[批个]?)?(「|\")?(.+?)(活动|礼)?[,，。]|针对", text)
            act_name = None
            if "沉默" in text: act_name = "沉默用户唤醒"
            elif "新户" in text or "新客" in text: act_name = "新户首刷有礼"
            elif "分期" in text: act_name = "分期费率折扣"

            missing = []
            if not aud: missing.append("目标客群（例：沉默客户 / 新户 / 白金卡）")
            if not budget: missing.append("权益预算（例：预算 50 万）")
            if not act_name: missing.append("活动名称")

            # ---- ③ 工具调用 mock ----
            aud_size = estimate_audience(
                "白金卡" if aud and "白金" in aud else "金卡" if aud and "金卡" in aud and "白" not in aud else "不限",
                "沉默(90天+)" if aud and "沉默" in aud else "账龄<6月" if aud and "新户" in aud else "不限",
                "月消费>5000" if _re.search(r"5000|大额", text) else "不限", "不限")
            tool_calls = [
                ("查询客群标签", f"tags.query(conditions='{aud or '未指定'}')", {"命中客群": f"{aud_size:,} 人", "标签来源": "CLM 客户标签平台", "覆盖率": "97.2%"}),
                ("规则引擎校验", f"rules.validate(benefit={benefit or '默认立减金'}, budget={budget or '未填'})", {"频控校验": "通过（90天内未被同类活动触达）", "预算校验": "通过" if budget else "缺少预算，按默认策略预估", "合规校验": "文案模板待确认"}),
                ("匹配奖励模块", f"reward.match(type='{benefit or '立减金'}')", {"权益模块": benefit or "立减金", "库存": "充足", "核销率参考": "同权益历史均值 68%"}),
            ]

            ss["ai_parsed"] = {
                "aud": aud, "benefit": benefit, "channels": channels,
                "budget": budget, "name": act_name, "missing": missing,
                "aud_size": aud_size, "tool_calls": tool_calls,
            }
            st.rerun()

    parsed = ss.get("ai_parsed")
    if parsed:
        # ---- ②③ 展示 Agent 决策过程 ----
        st.markdown('<div class="section-t" style="margin-top:16px;">② AI Agent 意图识别与任务拆解</div>', unsafe_allow_html=True)
        chips = ""
        for k, v in [("活动意图", "营销活动创建"), ("目标客群", parsed["aud"] or "❓未识别"), ("权益类型", parsed["benefit"] or "❓未指定（建议立减金）"), ("触达渠道", "、".join(parsed["channels"])), ("预算", parsed["budget"] or "❓待补充"), ("活动名称", parsed["name"] or "❓待生成")]:
            chips += f'<span class="chip {"on" if "❓" not in v else ""}"><b>{k}</b>：{v}</span> '
        st.markdown(f'<div class="panel">{chips}</div>', unsafe_allow_html=True)
        if parsed["missing"]:
            st.markdown('<div class="callout" style="border-left-color:#D97706;background:#FFFBEB;">'
                        f'⚠ <b>识别到缺失信息（Agent 不会臆造，已标记为待补充，将在草稿中给出默认值供人工修正）：</b>'
                        f'{"；".join(parsed["missing"])}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-t" style="margin-top:16px;">③ 调用营销平台工具（而非直接写库）</div>', unsafe_allow_html=True)
        for tool, call, result in parsed["tool_calls"]:
            with st.expander(f"🔧 {tool}　<code style='font-size:11.5px;color:#64748B;'>{call}</code>", expanded=True):
                rows = " ｜ ".join(f"<b>{k}</b>：{v}" for k, v in result.items())
                st.markdown(f'<div style="font-size:13px;color:#334155;padding:4px 0;">↳ {rows}</div>', unsafe_allow_html=True)

        # ---- ④ 生成活动配置草稿 ----
        st.markdown('<div class="section-t" style="margin-top:16px;">④ 生成活动配置草稿（结构化配置 · 规则校验 · 冲突检测）</div>', unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            draft_name = st.text_input("活动名称", parsed["name"] or "AI生成活动·待命名", key="ai_name")
        with d2:
            draft_aud = st.select_slider("目标客群", ["不限", "金卡", "白金卡", "账龄<6月", "沉默(90天+)"],
                                         parsed["aud"] if parsed["aud"] in ("金卡", "白金卡", "账龄<6月", "沉默(90天+)") else "沉默(90天+)", key="ai_aud")
        with d3:
            draft_benefit = st.selectbox("权益类型", ["立减金", "积分包", "费率券", "返现", "实物礼品"],
                                         index=["立减金", "积分包", "费率券", "返现", "实物礼品"].index(parsed["benefit"]) if parsed["benefit"] in ["立减金", "积分包", "费率券", "返现", "实物礼品"] else 0, key="ai_ben")
        with d4:
            draft_channel = st.multiselect("触达渠道", ["App推送", "短信", "外呼", "微信公众号"], default=parsed["channels"], key="ai_ch")
        draft_budget = st.text_input("权益预算（元）", parsed["budget"].replace(" 万元", "0000").replace(" ", "") if parsed["budget"] else "500000", key="ai_budget")

        checks_ok = "✔ 频控校验通过 ｜ ✔ 预算校验通过 ｜ ✔ 渠道冲突检测通过（无同客群同周期活动）"
        st.markdown(f'<div class="callout" style="margin-top:8px;">🛡 <b>规则引擎校验：</b>{checks_ok}</div>', unsafe_allow_html=True)

        # ---- ⑤ 人工确认与审批 ----
        st.markdown('<div class="section-t" style="margin-top:16px;">⑤ 人工确认与审批（人做最终决定）</div>', unsafe_allow_html=True)
        ap1, ap2, _ = st.columns([1, 1, 3])
        with ap1:
            if st.button("✔ 审批通过 · 创建活动", type="primary", use_container_width=True):
                size = estimate_audience(
                    draft_aud if draft_aud in ("金卡", "白金卡") else "不限",
                    "沉默(90天+)" if draft_aud == "沉默(90天+)" else "账龄<6月" if draft_aud == "账龄<6月" else "不限",
                    "不限", "不限")
                ss["ai_approved"].insert(0, (draft_name, draft_aud, draft_benefit, "、".join(draft_channel), f"{size/10000:.0f} 万人", "AI 创建 · 待复核投放"))
                ss["ai_parsed"] = None
                ss["ai_input"] = ""
                st.success(f"「{draft_name}」审批通过并已创建！可在下方已创建列表查看。")
                st.rerun()
        with ap2:
            if st.button("✘ 退回修改", use_container_width=True):
                ss["ai_parsed"] = None
                st.rerun()
        st.markdown('<div class="note">审批通过 ≠ 立即投放：活动进入「待复核投放」状态，按排期由引擎自动推进（见「活动管理」tab 的自动化设计）。</div>', unsafe_allow_html=True)

        if ss["ai_approved"]:
            st.markdown('<div class="section-t" style="margin-top:14px;">本会话 AI 创建的活动</div>', unsafe_allow_html=True)
            for nm, aud_, ben, ch, size_, note in ss["ai_approved"]:
                st.markdown(f"""<div class="act">
                  <div class="nm">{nm}</div>
                  <div class="meta">客群：{aud_} ｜ 权益：{ben} ｜ 渠道：{ch} ｜ {note}</div>
                  <div class="reach">{size_}</div>
                  <div class="pill run">已创建</div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="callout"><b>架构要点（面试考点）：</b>① Agent 只产出<b>配置草稿</b>，不直接操作数据库与线上活动——写路径全部经过规则引擎与人工审批；'
                '② 缺失信息<b>澄清而非臆造</b>；③ 工具调用复用营销平台既有能力（标签平台 / 规则引擎 / 权益模块），AI 是"指挥家"不是"新系统"；'
                '④ 全程留痕，审批与修改记录可追溯。</div>', unsafe_allow_html=True)

st.markdown('<div class="note">数据为演示用模拟数据，业务口径与真实项目一致 ｜ 平台：Streamlit ｜ 无外部依赖</div>', unsafe_allow_html=True)
