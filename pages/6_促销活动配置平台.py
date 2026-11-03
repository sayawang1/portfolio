# -*- coding: utf-8 -*-
"""
pages/6_促销活动配置平台.py  ·  v1
云服务促销活动配置平台 —— Tab1 系统介绍 / Tab2 在线演示（模板中心 → 活动配置 → 数据对接与官网发布）
纯本地 mock，无外部依赖。
"""
import streamlit as st

st.set_page_config(page_title="云服务促销活动配置平台", page_icon="🎁", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# 全站统一样式
# ============================================================
st.markdown("""
<style>
    [data-testid="stSidebar"] { display:none !important; }
    [data-testid="stSidebarNav"] { display:none !important; }
    .stApp { background-color:#F5F7FA; color:#1E293B; }
    h1,h2,h3,h4 { color:#0F172A !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid #E2E8F0 !important; background:#FFFFFF !important; border-radius:14px !important; }

    div[data-testid="stButton"] > button {
        border-radius:20px !important; border:1px solid transparent !important;
        background:transparent !important; color:#64748B !important;
        font-weight:600 !important; padding:8px 16px !important; transition:all .25s !important;
    }
    div[data-testid="stButton"] > button:hover { background:#FFFFFF !important; color:#0F172A !important; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background:#2563EB !important;color:#FFFFFF !important; box-shadow:0 4px 12px rgba(37,99,235,.3) !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap:6px; background:#FFFFFF; padding:6px; border-radius:12px; border:1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 18px; color:#64748B; font-weight:600; }
    .stTabs [aria-selected="true"] { background:#2563EB !important;color:#FFFFFF !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }

    .hero { padding:26px 4px 6px 4px; }
    .hero .eyebrow { color:#2563EB; font-size:12px; letter-spacing:3px; font-weight:700; }
    .hero h1 { margin:6px 0 8px 0; }
    .hero .sub { color:#64748B; font-size:14px; }

    .panel { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:20px; }
    .arch-box { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
                padding:16px; font-family:monospace; font-size:12.5px; line-height:1.8; color:#475569; }
    .feat { display:flex; gap:12px; margin:10px 0; align-items:flex-start; }
    .feat .fi { width:34px; height:34px; flex-shrink:0; border-radius:9px; background:#EFF6FF;
                border:1px solid #BFDBFE; text-align:center; line-height:32px; font-size:16px; }
    .feat .ft { color:#0F172A; font-weight:600; font-size:14px; }
    .feat .fd { color:#64748B; font-size:12.5px; line-height:1.6; }

    .callout { background:#F8FAFC; border-left:3px solid #2563EB; border-radius:8px;
               padding:12px 16px; color:#475569; font-size:13.5px; line-height:1.7; margin-top:14px; }
    .section-t { color:#0F172A; font-weight:700; font-size:15px; margin:8px 0 10px 0; }
    .note { color:#64748B; font-size:12px; margin-top:14px; }
    [data-testid="stWidgetLabel"] p { color:#64748B !important; font-size:13px !important; }
    .h1chip { display:inline-flex; align-items:center; justify-content:center;width:52px; height:52px; border-radius:14px; font-size:26px; margin-right:14px;vertical-align:middle; box-shadow:0 6px 14px rgba(15,23,42,.18); }

    /* 模板卡 */
    .tpl { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:18px; height:100%; }
    .tpl .badge { float:right; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; background:#F0FDF4; color:#16A34A; }
    .tpl .badge.warn { background:#FFFBEB; color:#D97706; }
    .tpl .ticon { width:38px; height:38px; border-radius:10px; background:#EFF6FF; text-align:center; line-height:38px; font-size:18px; margin-bottom:10px; }
    .tpl .tname { color:#0F172A; font-weight:700; font-size:15px; margin-bottom:6px; }
    .tpl .tdesc { color:#64748B; font-size:12.5px; line-height:1.7; margin-bottom:10px; min-height:42px; }
    .tpl .tag { display:inline-block; padding:3px 10px; border-radius:10px; background:#F1F5F9; color:#475569; font-size:11.5px; margin:0 6px 4px 0; }

    /* 步骤条 */
    .step { display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:10px; margin:4px 0; color:#64748B; font-size:13.5px; }
    .step .dot { width:24px; height:24px; border-radius:50%; background:#E2E8F0; color:#64748B; text-align:center; line-height:24px; font-size:12px; font-weight:700; flex-shrink:0; }
    .step.done .dot { background:#DCFCE7; color:#16A34A; }
    .step.cur { background:#EFF6FF; color:#1D4ED8; font-weight:700; }
    .step.cur .dot { background:#2563EB; color:#FFFFFF; }

    /* KPI */
    .kpi-row { display:flex; gap:14px; margin:16px 0; }
    .kpi { flex:1; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px; }
    .kpi .label { color:#64748B; font-size:12px; margin-bottom:6px; }
    .kpi .value { color:#0F172A; font-size:24px; font-weight:800; }
    .kpi.hot .value { color:#2563EB; }
    .kpi.green .value { color:#16A34A; }

    .pill { padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700; }
    .pill.ok   { background:#F0FDF4; color:#16A34A; }
    .pill.wait { background:#FFFBEB; color:#D97706; }
    .pill.draft{ background:#F1F5F9; color:#64748B; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 全站导航
# ============================================================
NAV = [
    ("🏠", "app.py", False),
    ("🧪 推荐", "pages/1_推荐系统Demo.py", False),
    ("🤖 客服", "pages/3_智能客服.py", False),
    ("🎯 营销", "pages/4_精准营销平台.py", False),
    ("🏦 报送", "pages/5_监管报送规则引擎.py", False),
    ("🎁 促销", "", True),
]
cols = st.columns([0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 8])
for (label, target, active), c in zip(NAV, cols):
    with c:
        if active:
            st.button(label, use_container_width=True, type="primary")
        elif st.button(label, use_container_width=True):
            st.switch_page(target)

st.markdown("""
<div class="hero">
  <div class="eyebrow">CLOUD PROMOTION CAMPAIGN CONFIGURATION PLATFORM</div>
  <h1><span class="h1chip" style="background:linear-gradient(135deg,#E8A33D,#F0C070)">🎁</span>云服务促销活动配置平台</h1>
  <div class="sub">大促活动的模板化 · 配置化 · 多系统对接发布：模板中心 → 五步活动配置 → CRM / 客服数据对接 → 官网发布</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="callout">💡 <b>演示说明：</b>本页基于真实项目经验还原设计，业务数据已脱敏，交互原型由本人独立设计并借助 AI 编程工具实现；页面内数据均为演示模拟数据。</div>', unsafe_allow_html=True)

# ============================================================
# Mock 数据
# ============================================================
TEMPLATES = [
    {"icon": "🌟", "name": "新用户有礼", "badge": "已配置 · 秒发", "cls": "",
     "desc": "面向新注册客户的代金券礼包，支持按产品线配置面额与发放规则。",
     "tags": ["代金券", "卡券"], "preset": {"name": "新用户有礼·代金券", "aud": "新客", "benefit": "代金券"}},
    {"icon": "🔄", "name": "老客续费奖励", "badge": "已配置 · 秒发", "cls": "",
     "desc": "面向存量客户的续费激励，按到期时间自动圈人，权益随订单联动发放。",
     "tags": ["续费补贴", "折扣"], "preset": {"name": "老客续费奖励", "aud": "存量", "benefit": "续费补贴"}},
    {"icon": "⚡", "name": "抢购有礼", "badge": "已配置 · 秒发", "cls": "warn",
     "desc": "限时限量抢购场景，支持库存管控与防超卖校验，适合大促引爆场。",
     "tags": ["卡券", "云服务器"], "preset": {"name": "抢购有礼", "aud": "全量", "benefit": "代金券"}},
]

DEFAULT_CAMPAIGNS = [
    ("十一·云资源限时折扣", "代金券", "CRM + 官网", "进行中", "1,246 / 1,520", "11.01 - 11.15"),
    ("企业存储扩容补贴", "续费补贴", "CRM", "待配置", "— / —", "12.01 - 2027.01.31"),
    ("新春续费代金券", "卡券", "官网活动页", "草稿", "— / —", "未设置"),
]

STEPS = ["基本信息", "权益配置", "优惠配置", "数据对接", "官网发布", "预览提交"]

# ============================================================
# Tabs
# ============================================================
tab_intro, tab_demo = st.tabs(["系统介绍", "🖥 在线演示（模板 → 配置 → 发布）"])

# ---------------- Tab 1：系统介绍 ----------------
with tab_intro:
    st.markdown('<div class="section-t">🧭 一、业务背景与核心问题</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="panel">
<div class="feat"><div class="fi">🔁</div><div><div class="ft">活动一次一配，无法复用</div>
<div class="fd">每一场大促活动都靠研发按需求单独开发上线，页面、规则、发放逻辑重复造轮子，研发排期成为活动上线的最大瓶颈。</div></div></div>
<div class="feat"><div class="fi">🧩</div><div><div class="ft">配置散落在多个系统</div>
<div class="fd">权益在卡券系统、客户在 CRM、页面在官网、数据在报表——一个活动要跨 4 个系统配置，漏配一处就是线上事故。</div></div></div>
<div class="feat"><div class="fi">⏱️</div><div><div class="ft">大促节奏快、容错低</div>
<div class="fd">促销节奏以天为单位，传统"提需求-排期-开发-测试"的链路跟不上；活动配置出错又直接影响资损与客诉。</div></div></div>
<div class="feat"><div class="fi">📊</div><div><div class="ft">效果数据回流割裂</div>
<div class="fd">发放、核销、转化数据分散在卡券 / CRM / 官网侧，运营无法实时看到一场活动的完整漏斗，复盘靠人工拼表。</div></div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-t" style="margin-top:22px;">🎯 二、产品定位与整体方案（为什么是这个方案）</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="callout" style="border-left:4px solid #2563EB; background:#F8FAFC; padding:18px 20px; border-radius:8px;">
<b style="color:#0F172A; font-size:14.5px;">定位：把促销活动从"研发项目"重构为"可配置资产"——模板化沉淀 + 五步配置流 + 多系统数据对接 + 多端发布。</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
方案核心不是再做一张配置表单，而是三层抽象：<br>
① <b>模板层</b>——把活动共性（权益类型 / 圈人规则 / 发放方式）沉淀为可领用模板，同类活动"领用即得 80%"；<br>
② <b>配置层</b>——五步配置流向导（基本信息 → 权益 → 优惠 → 数据对接 → 官网发布），每步内置校验与合规审核，把"漏配"挡在上线前；<br>
③ <b>对接层</b>——CRM / 客服 / 卡券 / 官网的对接项平台化登记，同步时效与状态可视，活动结束后数据自动回流成漏斗。</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-t" style="margin-top:22px;">🔄 三、核心业务流程（活动全生命周期）</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="arch-box" style="font-size:13px;">
【活动主流程】
  ① 模板中心：按活动类型筛选模板 → 领用（或从历史活动一键复用）
     ↓
  ② 五步配置向导：基本信息 → 权益配置 → 优惠配置（门槛 / 适用范围 / 合规校验）→ 数据对接 → 官网发布
     ↓
  ③ 校验与审批：规则引擎自动校验（额度 / 库存 / 防超卖 / 合规文案），异常项阻断提交
     ↓
  ④ 多端发布：官网活动页一键生成发布，CRM 侧同步圈人与触达任务
     ↓
  ⑤ 数据回流：发放 / 核销 / 转化按 T+1 汇聚为活动漏斗，支撑复盘与模板迭代
</div>
""", unsafe_allow_html=True)

    k1, k2 = st.columns(2, gap="large")
    with k1:
        st.markdown('<div class="section-t" style="margin-top:16px;">🔑 关键设计 · 模板与复用</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🗂</div><div><div class="ft">模板分类管理</div>
<div class="fd">按拉新 / 续费 / 抢购等场景沉淀模板，标注权益类型与适用系统，领用后仅需改差异化参数。</div></div></div>
<div class="feat"><div class="fi">♻️</div><div><div class="ft">历史活动一键复用</div>
<div class="fd">「我的活动」中任意已结束活动可复用为草稿，大促常驻活动只需改时间与额度。</div></div></div>
</div>
""", unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="section-t" style="margin-top:16px;">🔑 关键设计 · 校验与对接</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🛡</div><div><div class="ft">规则校验前置</div>
<div class="fd">预算 / 额度 / 库存 / 领取频次 / 合规文案在配置环节即校验，异常阻断提交，资损风险挡在上线前。</div></div></div>
<div class="feat"><div class="fi">🔗</div><div><div class="ft">数据对接可视化</div>
<div class="fd">每个活动的 CRM / 卡券 / 官网对接项状态可视（已对接 / 待对接），同步时效 T+1，数据回流自动成漏斗。</div></div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-t" style="margin-top:22px;">⚖️ 四、关键技术决策与风险控制</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🧠</div><div><div class="ft">决策① ｜ 模板 &gt; 表单：抽象活动模型</div>
<div class="fd">把活动抽象为「客群 × 权益 × 门槛 × 渠道 × 页面」五个可配置因子的组合，模板是因子的预组合；新活动类型优先判断能否用既有因子拼出，而不是新建开发。</div></div></div>
<div class="feat"><div class="fi">🚦</div><div><div class="ft">决策② ｜ 校验前置于发布</div>
<div class="fd">配置即校验、提交强阻断：预算超限、领取频次冲突、合规文案缺失等问题在向导内逐步拦截，而不是上线后靠客服救火。</div></div></div>
</div>
""", unsafe_allow_html=True)
    with d2:
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🔌</div><div><div class="ft">决策③ ｜ 对接项平台化登记</div>
<div class="fd">与 CRM / 卡券 / 官网的每个对接项（圈人、发放、页面、数据回流）在平台内登记状态与时效，跨系统协同从"口头约定"变为"看板管理"。</div></div></div>
<div class="feat"><div class="fi">🧱</div><div><div class="ft">决策④ ｜ 发布与活动解耦</div>
<div class="fd">官网活动页由平台按配置自动生成并独立发布，活动规则调整无需改页面代码；页面改版不影响活动引擎。</div></div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="callout" style="border-left:4px solid #B91C1C; background:#FEF2F2; padding:14px 18px; margin-top:14px; border-radius:8px;">
<b style="color:#0F172A; font-size:14px;">🛡️ 风险控制</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
① 预算与额度双闸门：活动预算与单客户领取上限双重校验，超限即阻断；② 库存与防超卖：限量权益扣减走库存中心，防并发超卖；③ 合规审核前置：活动文案与规则在发布前过合规检查项；④ 操作留痕：全部配置变更可追溯，支持一键回滚到历史版本。</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-t" style="margin-top:22px;">📈 五、业务价值与验证指标</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="callout" style="border-left:4px solid #B45309; background:#FFFBEB; padding:18px 20px; border-radius:8px;">
<b style="color:#0F172A; font-size:15px;">业务结果</b><br>
<span style="color:#475569; font-size:14px; line-height:1.9;">
✅ 活动上线从"研发排期周级"变为<b>"配置化上线"</b>，常规活动运营自助完成、研发仅承接新能力<br>
✅ 模板沉淀后同类活动<b>领用即得</b>，大促准备周期显著缩短<br>
✅ 活动数据 T+1 自动回流成完整漏斗，复盘从"人工拼表"变为<b>"看板直出"</b>
</span><br><br>
<b style="color:#0F172A; font-size:14px;">📐 验证指标体系</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
配置化上线占比 · 模板复用率 · 活动配置耗时 · 数据对接及时率 · 活动资损事故数（护栏指标）。
</span>
</div>
""", unsafe_allow_html=True)

# ---------------- Tab 2：在线演示 ----------------
with tab_demo:
    ss = st.session_state
    ss.setdefault("campaigns", list(DEFAULT_CAMPAIGNS))
    ss.setdefault("step", 0)
    ss.setdefault("tpl", None)
    ss.setdefault("published", False)
    ss.setdefault("cfg", {
        "name": "双十一·云资源限时折扣", "aud": "新客", "benefit": "代金券",
        "way": "系统自动发放", "rule": "满 300 元减 200 元",
        "limit": "个人限购领 1 张", "valid": "领取后 30 天内有效",
        "scope": ["云主机（必选）", "新注册用户", "Node 产品线", "数据库"],
        "market": True,
    })
    ss.setdefault("dock", {
        "客户标签/圈选记录": "已对接", "核销 / 用券记录": "已对接",
        "合同质押/发放关联": "已对接", "活动效果汇总": "待对接",
    })

    d1, d2, d3 = st.tabs(["🗂 模板中心 / 我的活动", "🧭 活动配置", "🔗 数据对接与官网发布"])

    # ============ 屏 1：模板中心 / 我的活动 ============
    with d1:
        st.markdown('<div class="section-t">活动模板中心 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 以客起步 · 活动模板化 · 领用创建一次复用 · 8 分钟创建一场活动</span></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        for col, tpl in zip([c1, c2, c3], TEMPLATES):
            with col:
                st.markdown(f"""
<div class="tpl">
  <span class="badge {tpl['cls']}">✔ {tpl['badge']}</span>
  <div class="ticon">{tpl['icon']}</div>
  <div class="tname">{tpl['name']}</div>
  <div class="tdesc">{tpl['desc']}</div>
  <div>{''.join(f'<span class="tag">{t}</span>' for t in tpl['tags'])}</div>
</div>
""", unsafe_allow_html=True)
                if st.button(f"领用此模板 · {tpl['name']}", key=f"use_{tpl['name']}", use_container_width=True):
                    ss["tpl"] = tpl["name"]
                    ss["cfg"]["name"] = tpl["preset"]["name"]
                    ss["cfg"]["aud"] = tpl["preset"]["aud"]
                    ss["cfg"]["benefit"] = tpl["preset"]["benefit"]
                    ss["step"] = 0
                    ss["published"] = False
                    st.toast(f"已领用模板「{tpl['name']}」，进入活动配置", icon="🎁")

        st.markdown('<div class="section-t" style="margin-top:22px;">我的活动</div>', unsafe_allow_html=True)
        rows_html = ""
        pill_map = {"进行中": "ok", "待配置": "wait", "草稿": "draft"}
        for nm, ben, sys_, status, cnt, period in ss["campaigns"]:
            rows_html += (f"<tr><td style='font-weight:600;color:#0F172A;'>{nm}</td>"
                          f"<td>{ben}</td><td>{sys_}</td>"
                          f"<td><span class='pill {pill_map.get(status, 'draft')}'>{status}</span></td>"
                          f"<td>{cnt}</td><td>{period}</td></tr>")
        st.markdown(f"""
<div class="panel" style="padding:6px 18px 12px 18px;">
<table style="width:100%;border-collapse:collapse;font-size:13px;color:#475569;">
<tr style="color:#94A3B8;font-size:12px;text-align:left;">
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">活动名称</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">权益类型</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">关联系统</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">状态</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">已发放 / 领取</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">有效期</th>
</tr>{rows_html}</table></div>
""", unsafe_allow_html=True)
        st.markdown('<div class="callout">👆 <b>试试：</b>领用一张模板 → 自动进入「活动配置」向导；已发布的活动会出现在「我的活动」列表中。</div>', unsafe_allow_html=True)

    # ============ 屏 2：活动配置 ============
    with d2:
        cur = ss["cfg"]
        l, r = st.columns([0.28, 0.72], gap="large")
        with l:
            st.markdown('<div class="section-t">配置进度</div>', unsafe_allow_html=True)
            step_html = ""
            for i, sname in enumerate(STEPS):
                cls = "done" if i < ss["step"] else ("cur" if i == ss["step"] else "")
                dot = "✔" if i < ss["step"] else str(i + 1)
                step_html += f'<div class="step {cls}"><div class="dot">{dot}</div>{sname}</div>'
            st.markdown(step_html, unsafe_allow_html=True)
            st.markdown('<div class="note">向导内每一步保存即校验，异常项阻断下一步。</div>', unsafe_allow_html=True)
        with r:
            step = ss["step"]
            st.markdown(f'<div class="section-t">活动配置 · {STEPS[step]}<span style="color:#64748B;font-size:12px;font-weight:400;">　当前活动：{cur["name"]}{("　模板：" + ss["tpl"]) if ss["tpl"] else ""}</span></div>', unsafe_allow_html=True)

            if step == 0:
                cur["name"] = st.text_input("活动名称", cur["name"])
                cA, cB = st.columns(2)
                with cA:
                    cur["aud"] = st.select_slider("目标客群", ["新客", "存量", "全量"], cur["aud"])
                with cB:
                    period = st.text_input("活动周期", "2026.11.01 - 2026.11.15")
                cur["budget"] = st.text_input("活动预算（元）", "200,000")
            elif step == 1:
                cA, cB = st.columns(2)
                with cA:
                    cur["benefit"] = st.selectbox("权益类型", ["代金券", "续费补贴", "卡券", "折扣券", "实物礼品"], index=["代金券", "续费补贴", "卡券", "折扣券", "实物礼品"].index(cur["benefit"]) if cur["benefit"] in ["代金券", "续费补贴", "卡券", "折扣券", "实物礼品"] else 0)
                with cB:
                    cur["way"] = st.selectbox("权益方式", ["系统自动发放", "客户手动领取", "订单联动发放"])
                st.markdown('<div class="note">权益由卡券系统承接，发放链路在「数据对接」步骤登记状态。</div>', unsafe_allow_html=True)
            elif step == 2:
                cA, cB = st.columns(2)
                with cA:
                    cur["rule"] = st.text_input("优惠 / 抵扣额度", cur["rule"])
                with cB:
                    cur["limit"] = st.text_input("领取 / 使用门槛", cur["limit"])
                cur["valid"] = st.text_input("使用有效期", cur["valid"])
                st.markdown("**适用范围（产品线 / 客群）**")
                cur["scope"] = st.multiselect("适配范围", ["云主机（必选）", "新注册用户", "Node 产品线", "数据库", "对象存储", "应用市场商品"], default=cur["scope"])
                cur["market"] = st.toggle("应用市场适配：支持第三方商品参与本活动", cur["market"])
                st.markdown('<div class="callout" style="margin-top:10px;">🛡 <b>规则校验：</b>预算额度 ✔ ｜ 领取频次 ✔ ｜ 合规文案 ✔ ｜ 库存防超卖 ✔ —— 全部通过，可进入下一步。</div>', unsafe_allow_html=True)
            elif step == 3:
                st.markdown("**对接项清单（跨系统协同看板）**")
                for k, v in list(ss["dock"].items()):
                    cA, cB = st.columns([2, 1])
                    with cA:
                        st.markdown(f"<div style='padding:6px 0;font-size:13.5px;color:#334155;'>{k}</div>", unsafe_allow_html=True)
                    with cB:
                        new_v = st.selectbox("状态", ["已对接", "待对接"], index=0 if v == "已对接" else 1, key=f"dock_{k}", label_visibility="collapsed")
                        ss["dock"][k] = new_v
                st.markdown('<div class="note">对接项由各系统负责人认领；全部「已对接」才允许进入发布环节。</div>', unsafe_allow_html=True)
            elif step == 4:
                pub = st.radio("官网活动页发布方式", ["使用已确认模板快速创建（推荐）", "创建活动预览检查后发布"], index=0)
                cur["url"] = st.text_input("活动地址", "https://cloud.example.com/promo/1111")
                st.markdown('<div class="note">活动页由平台按配置自动生成，规则调整无需改页面代码。</div>', unsafe_allow_html=True)
            else:  # 预览提交
                st.markdown(f"""
<div class="panel">
<div class="feat"><div class="fi">📛</div><div><div class="ft">{cur['name']}</div>
<div class="fd">客群：{cur['aud']} ｜ 权益：{cur['benefit']}（{cur['way']}）</div></div></div>
<div class="feat"><div class="fi">🧾</div><div><div class="ft">{cur['rule']}</div>
<div class="fd">{cur['limit']} ｜ {cur['valid']}</div></div></div>
<div class="feat"><div class="fi">🏷️</div><div><div class="ft">适用范围</div>
<div class="fd">{'、'.join(cur['scope'])}{'｜ 应用市场适配：开' if cur.get('market') else ''}</div></div></div>
<div class="feat"><div class="fi">🔗</div><div><div class="ft">数据对接</div>
<div class="fd">{'；'.join(f'{k}（{v}）' for k, v in ss['dock'].items())}</div></div></div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            nav_c1, nav_c2, nav_c3 = st.columns([1, 1, 2])
            with nav_c1:
                if st.button("← 上一步", disabled=step == 0, use_container_width=True):
                    ss["step"] = max(0, step - 1); st.rerun()
            with nav_c2:
                if step < len(STEPS) - 1:
                    blocked = (step == 3 and any(v == "待对接" for v in ss["dock"].values()))
                    if st.button("下一步 →", type="primary", disabled=blocked, use_container_width=True):
                        ss["step"] = step + 1; st.rerun()
                    if blocked:
                        st.markdown('<div class="note" style="color:#D97706;">⚠ 存在「待对接」项，完成对接后才能进入发布。</div>', unsafe_allow_html=True)
                else:
                    if st.button("✔ 提交发布", type="primary", use_container_width=True):
                        ss["campaigns"].insert(0, (cur["name"], cur["benefit"], "CRM + 官网", "进行中", "0 / 0", "2026.11.01 - 11.15"))
                        ss["published"] = True
                        st.success("已提交发布！活动已出现在「模板中心 / 我的活动」列表，可前往「数据对接与官网发布」查看数据回流。")

    # ============ 屏 3：数据对接与官网发布 ============
    with d3:
        st.markdown(f'<div class="section-t">{ss["cfg"]["name"]} · 数据对接（CRM / 客服）与官网发布</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="kpi-row">
  <div class="kpi hot"><div class="label">参与 / 活动数据</div><div class="value">8,612</div></div>
  <div class="kpi"><div class="label">权益发放</div><div class="value">12,480</div></div>
  <div class="kpi green"><div class="label">核销率</div><div class="value">73.1%</div></div>
  <div class="kpi"><div class="label">数据同步时效</div><div class="value">T+1 <em style="font-style:normal;font-size:13px;color:#64748B;">天</em></div></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("**活动数据：打通数据链路与 CRM / 客服客户经理**")
        dock_rows = [
            ("客户标签 / 圈选记录", "画像（标签类型）- 圈人 - 领取时效校验", "策略引擎 / CRM", "实时事件推送"),
            ("核销 / 用券记录", "核销数据、订单归因、核销时效", "卡券中心", "实时事件推送"),
            ("合同 / 发放关联", "大额发放与合同流程的关联登记", "CRM 客户经理", "T+1 批量下发"),
            ("活动效果汇总", "参与、转化、GMV 汇总", "CRM 客户经理", "T+1 批量下发"),
        ]
        rows_html = ""
        for name, detail, dep, sync in dock_rows:
            status = ss["dock"].get({"客户标签 / 圈选记录": "客户标签/圈选记录", "核销 / 用券记录": "核销 / 用券记录",
                                     "合同 / 发放关联": "合同质押/发放关联", "活动效果汇总": "活动效果汇总"}.get(name, name), "待对接")
            pill_cls = "ok" if status == "已对接" else "wait"
            rows_html += (f"<tr><td style='font-weight:600;color:#0F172A;'>{name}</td><td>{detail}</td>"
                          f"<td>{dep}</td><td>{sync}</td>"
                          f"<td><span class='pill {pill_cls}'>{status}</span></td></tr>")
        st.markdown(f"""
<div class="panel" style="padding:6px 18px 12px 18px;">
<table style="width:100%;border-collapse:collapse;font-size:13px;color:#475569;">
<tr style="color:#94A3B8;font-size:12px;text-align:left;">
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">开发对接项</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">明细</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">依赖系统</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">同步方式</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">状态</th>
</tr>{rows_html}</table></div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-t" style="margin-top:18px;">官网活动页发布</div>', unsafe_allow_html=True)
        pc1, pc2 = st.columns(2, gap="large")
        with pc1:
            st.markdown("""
<div class="panel" style="border-color:#2563EB; box-shadow:0 0 0 1px #2563EB;">
  <div class="feat"><div class="fi">⚡</div><div><div class="ft">使用已确认模板创建活动页</div>
  <div class="fd">页面结构复用已确认模板，按本活动配置自动填充文案与权益信息，历史活动一键套用，分钟级上线。</div></div></div>
  <div style="margin-top:8px;">模板状态：<span class="pill ok">模板就绪</span>　活动地址：<span style="font-family:monospace;font-size:12px;">https://cloud.example.com/promo/1111</span></div>
</div>
""", unsafe_allow_html=True)
        with pc2:
            st.markdown("""
<div class="panel">
  <div class="feat"><div class="fi">🔍</div><div><div class="ft">创建活动预览检查</div>
  <div class="fd">发布前对活动页进行可视化预览与规则校验（文案合规、权益展示、链接可达），确认无误后再对外发布。</div></div></div>
  <div style="margin-top:8px;">预览检查：<span class="pill ok">校验通过</span>　合规审核：<span class="pill ok">已通过</span></div>
</div>
""", unsafe_allow_html=True)

        btn_c1, btn_c2, _ = st.columns([1, 1, 3])
        with btn_c1:
            if st.button("↗ 跳转官网", use_container_width=True):
                st.info("演示环境：正式部署后此处将打开官网活动页（当前为模拟数据）。")
        with btn_c2:
            if st.button("🚀 提交发布", type="primary", use_container_width=True):
                st.success("发布成功！活动页已上线，数据回流看板将从明日 T+1 开始更新。")

    st.markdown('<div class="note">演示为纯本地规则实现（模板领用 / 五步配置向导 / 对接状态看板 / 发布流），示例数据均为模拟数据</div>', unsafe_allow_html=True)
