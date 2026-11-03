# -*- coding: utf-8 -*-
"""
pages/3_智能客服.py  ·  v4 八屏版
智能客服 & 坐席辅助 —— Tab1 系统介绍（五段叙事） / Tab2 在线演示（8 屏）
PC对话 / APP对话 / 坐席工作台 / 知识管理 / 数据看板 / 任务中心 / 后台设置 / 质检工作台
纯本地规则实现，无外部依赖。
"""
import datetime
import re

import streamlit as st

st.set_page_config(page_title="智能客服与坐席辅助", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# 全站统一样式 + 本页组件
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

    .stTabs [data-baseweb="tab-list"] { gap:6px; background:#FFFFFF; padding:6px; border-radius:12px; border:1px solid #E2E8F0; flex-wrap:wrap !important; }
    .stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 14px; color:#64748B; font-weight:600; }
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
    [data-testid="stChatMessage"] { background-color:#FFFFFF !important; border:1px solid #E2E8F0 !important; border-radius:12px !important; }
    [data-testid="stChatInput"] textarea, [data-testid="stChatInput"] > div {
        background:#FFFFFF !important; border-color:#E2E8F0 !important; color:#1E293B !important;
    }
    [data-testid="stExpander"] { border:1px solid #E2E8F0 !important; border-radius:10px !important; background:#FFFFFF !important; }
    [data-testid="stExpander"] p, [data-testid="stExpander"] li { color:#475569 !important; }
    .h1chip { display:inline-flex; align-items:center; justify-content:center;width:52px; height:52px; border-radius:14px; font-size:26px; margin-right:14px;vertical-align:middle; box-shadow:0 6px 14px rgba(15,23,42,.18); }

    /* KPI */
    .kpi-row { display:flex; gap:14px; margin:16px 0; }
    .kpi { flex:1; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px; }
    .kpi .label { color:#64748B; font-size:12px; margin-bottom:6px; }
    .kpi .value { color:#0F172A; font-size:24px; font-weight:800; }
    .kpi.hot .value { color:#2563EB; }
    .kpi.green .value { color:#16A34A; }
    .kpi.warn .value { color:#D97706; }

    /* 通用条形 */
    .hrow { display:flex; align-items:center; gap:12px; margin:9px 0; }
    .hrow .hname { width:130px; color:#64748B; font-size:12.5px; text-align:right; flex-shrink:0; }
    .hrow .hbar-wrap { flex:1; height:20px; background:#E9EEF5; border-radius:6px; overflow:hidden; }
    .hrow .hbar { height:100%; border-radius:6px; min-width:4px; }
    .hrow .hval { width:64px; color:#1E293B; font-size:12.5px; font-weight:600; flex-shrink:0; }

    .pill { padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700; display:inline-block; }
    .pill.ok  { background:#F0FDF4; color:#16A34A; }
    .pill.wait{ background:#FFFBEB; color:#D97706; }
    .pill.risk{ background:#FEF2F2; color:#DC2626; }
    .pill.draft{background:#F1F5F9; color:#64748B; }

    /* 坐席档案 */
    .profile { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px; font-size:13px; color:#334155; }
    .profile .p-title { font-weight:700; color:#0F172A; font-size:14px; margin-bottom:10px; }
    .profile .p-row { display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px dashed #F1F5F9; }
    .profile .p-row .k { color:#94A3B8; }
    .profile .p-row .v { font-weight:600; color:#0F172A; text-align:right; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 全站导航
# ============================================================
NAV = [
    ("🏠", "app.py", False),
    ("🧪 推荐", "pages/1_推荐系统Demo.py", False),
    ("🤖 客服", "", True),
    ("🎯 营销", "pages/4_精准营销平台.py", False),
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

st.markdown("""
<div class="hero">
  <div class="eyebrow">INTELLIGENT CUSTOMER SERVICE SYSTEM</div>
  <h1><span class="h1chip" style="background:linear-gradient(135deg,#5FA396,#82B7AC)">🤖</span>华为云智能客服 &amp; 客服智能辅助系统</h1>
  <div class="sub">面向云服务场景，构建覆盖客户自助服务、人工坐席辅助与运营管理的智能客服体系 ｜ 8 屏完整演示：C 端双端对话 → 坐席工作台 → 运营管理后台</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="callout">💡 <b>演示说明：</b>本页基于真实项目经验还原设计，业务数据已脱敏，交互原型由本人独立设计并借助 AI 编程工具实现（非华为官方产品）；完整工程版（FastAPI + RAG）见本地仓库，面试可现场演示。</div>', unsafe_allow_html=True)

# ============================================================
# Agent 核心逻辑（规则版，结构与大模型版一致）
# ============================================================
KB = [
    {"id": "KB001", "q": "云服务器怎么续费",
     "a": "可在控制台「弹性云服务器 ECS-实例-更多-续费」单台续费，或在「费用中心-续费管理」批量续费；支持设置自动续费，到期前 7 天会短信与站内信提醒。",
     "kw": ["续费", "自动续费", "到期"]},
    {"id": "KB002", "q": "ECS 实例怎么升配降配",
     "a": "关机后在控制台「实例-变更规格」即可升配/降配，变更一般 3-5 分钟生效，按需计费实例变更后按新规格计费。",
     "kw": ["升配", "降配", "规格", "变更"]},
    {"id": "KB003", "q": "云服务器备份怎么做",
     "a": "可通过云备份服务创建手动快照，或配置备份策略按天/周自动备份；建议业务变更前先做快照，恢复时在「备份-恢复」一键回滚。",
     "kw": ["备份", "快照", "回滚"]},
    {"id": "KB004", "q": "磁盘扩容后要不要重启",
     "a": "云硬盘支持在线扩容，控制台扩容容量后，还需在系统内扩展分区与文件系统（Linux 用 growpart，Windows 用磁盘管理），一般无需重启实例。",
     "kw": ["磁盘", "扩容", "硬盘"]},
    {"id": "KB005", "q": "带宽不够可以临时升级吗",
     "a": "支持按需临时升级带宽：固定带宽可在「弹性公网 IP-带宽调价」即时升配；突发流量场景也可改用按使用流量计费。",
     "kw": ["带宽", "升级", "流量", "网速"]},
    {"id": "KB006", "q": "安全组怎么放行端口",
     "a": "在「安全组-入方向规则」添加规则：协议（TCP/UDP）、端口（如 80/443/22）、源地址（建议限定网段），保存后即时生效，无需重启。",
     "kw": ["安全组", "端口", "放行", "开放"]},
    {"id": "KB007", "q": "本月账单和费用明细在哪看",
     "a": "可在「费用中心-账单管理」查看月度账单与按资源/按产品的费用明细，支持导出；也可设置费用预警，超过阈值自动通知。",
     "kw": ["账单", "费用", "扣费", "明细", "多少钱"]},
    {"id": "KB008", "q": "误购实例怎么退款退订",
     "a": "包年包月实例支持五天内无理由退订（控制台「退订管理」自助提交），退款按使用时长扣除部分费用。涉及退款规则咨询较多时，也可为您转人工核对。",
     "kw": ["退款", "退订", "误购"]},
    {"id": "KB009", "q": "实例到期未续费会怎样",
     "a": "到期后实例停止服务，数据保留 7 天（宽限期），期间续费可恢复；超过宽限期未续费资源将被释放且无法找回，请留意到期提醒。",
     "kw": ["到期", "欠费", "停机", "释放"]},
    {"id": "KB010", "q": "网站域名备案流程和时长",
     "a": "在「ICP 备案控制台」提交主体与网站信息，初审 2 个工作日，管局审核一般 5-20 个自然日；备案期间网站需不可访问。",
     "kw": ["备案", "域名", "网站", "icp"]},
    {"id": "KB011", "q": "云服务器密码忘了怎么重置",
     "a": "可在控制台「实例-更多-重置密码」重置 Linux root 或 Windows Administrator 密码，重置后需重启实例生效；若已配置密钥对也可用密钥登录。",
     "kw": ["密码", "重置", "登录", "忘记"]},
    {"id": "KB012", "q": "企业实名认证怎么办理",
     "a": "在「账号中心-实名认证」选择企业认证，提交营业执照与法人信息，一般 1-3 个工作日完成审核；认证后可开具企业发票并升级账户权限。",
     "kw": ["企业认证", "实名", "资质", "营业执照"]},
    {"id": "KB013", "q": "CPU 使用率告警怎么配置",
     "a": "在「云监控-告警-创建告警规则」选择实例与指标（如 CPU 使用率 > 80% 持续 5 分钟），配置通知对象即可；建议同时配置磁盘与内存告警。",
     "kw": ["告警", "监控", "报警", "cpu"]},
    {"id": "KB014", "q": "有没有优惠活动或代金券",
     "a": "本月有云资源限时折扣与新客代金券活动，可在官网「最新活动」页领取；代金券在支付时自动抵扣，有效期以券面为准。",
     "kw": ["优惠", "活动", "代金券", "折扣"]},
    {"id": "KB015", "q": "数据丢了/服务出问题怎么投诉",
     "a": "非常抱歉给您带来影响。数据类问题我会立即升级为紧急工单并转接人工专家跟进处理，您的会话记录与实例信息会同步给坐席，无需重复描述。",
     "kw": ["数据丢", "丢了", "投诉", "故障", "不能用"]},
]

TOOLS = {
    "查询资源账单": {"desc": "查询账户当期账单与资源费用明细", "params": ["account_id"],
               "run": lambda: {"当期账单": "¥1,286.40", "ECS 费用": "¥892.00", "存储/带宽": "¥394.40", "状态": "未出账"}},
    "办理续费": {"desc": "对指定实例发起续费与优惠核验", "params": ["实例ID", "时长"],
               "run": lambda: {"实例": "ECS-yaojing-01", "时长": "1 年", "优惠核验": "新客代金券 ¥200 已抵扣", "应付": "¥3,164.00", "备注": "正式支付需客户确认"}},
    "查询工单进度": {"desc": "查询名下工单处理进度", "params": ["工单号"],
               "run": lambda: {"工单号": "WD2026102134", "主题": "磁盘扩容后挂载异常", "状态": "处理中", "负责工程师": "张工", "预计完成": "今日 18:00 前"}},
}

NEG_WORDS = ["气死", "垃圾", "态度", "投诉", "骗子", "烦", "忽悠", "敷衍", "再不", "不给", "差评", "举报", "太差", "恶心", "坑"]
RISK_HIGH = ["退款", "数据丢", "丢了", "盗用", "销户", "投诉", "故障", "报警", "律师", "银监会", "12378", "多扣", "不能用", "停机"]
RISK_MID = ["续费", "升级", "退款", "账单", "费用", "备案"]
DEFAULT_TH = {"conf": 0.62, "emotion": 0.60}


def retrieve(text):
    best, best_score = None, 0.0
    t = set(text)
    for item in KB:
        kw_hit = sum(1 for k in item["kw"] if k in text)
        char_ov = len(t & set(item["q"])) / max(len(set(item["q"])), 1)
        score = 0.55 * (kw_hit / max(len(item["kw"]), 1)) + 0.45 * char_ov
        if score > best_score:
            best, best_score = item, score
    return best, round(min(best_score, 1.0), 2)


def emotion_score(text):
    hits = sum(1 for w in NEG_WORDS if w in text)
    exclaim = text.count("！") + text.count("!")
    return round(min(0.15 + 0.28 * hits + 0.1 * exclaim, 1.0), 2)


def risk_level(text):
    if any(w in text for w in RISK_HIGH):
        return "高"
    if any(w in text for w in RISK_MID):
        return "中"
    return "低"


def classify_intent(text):
    if re.search(r"账单|多少钱|费用|续费|退订|扩容|升配|备案", text) and re.search(r"查|多少|办|申请|看|怎么", text):
        return "业务办理"
    if re.search(r"投诉|态度|举报|垃圾|气死|差评", text):
        return "投诉与情绪"
    if re.search(r"人工|真人|客服呢|转接", text):
        return "要求转人工"
    if re.search(r"你好|在吗|谢谢|拜拜|哈喽", text):
        return "寒暄"
    return "知识问答"


def route(text, th):
    """核心路由：业务风险 × 模型置信度 × 客户情绪 三维定义边界。"""
    intent = classify_intent(text)
    kb, ret = retrieve(text)
    conf = round(min(0.35 + 0.62 * ret, 0.98), 2)
    emo = emotion_score(text)
    risk = risk_level(text)

    if intent == "投诉与情绪" or emo >= th["emotion"] or risk == "高":
        decision, reason = "转人工", "命中高风险业务或负面情绪，边界外移交人工（携带上下文）"
    elif intent == "业务办理":
        tool = next((t for t in TOOLS if any(k in text for k in t[:2])), None)
        decision, reason = ("调用工具", f"识别为业务办理，调用工具「{tool}」并回填结果") if tool \
            else ("澄清反问", "识别为业务办理但缺少要素，先向客户澄清")
    elif intent == "要求转人工":
        decision, reason = "转人工", "客户明确要求，直接移交"
    elif conf >= th["conf"] and kb is not None:
        decision, reason = "知识应答", f"检索命中 {kb['id']}，置信度 {conf} ≥ 阈值 {th['conf']}"
    else:
        decision, reason = "澄清反问", f"置信度 {conf} 低于阈值 {th['conf']}，宁问勿答"

    return {"intent": intent, "kb": kb, "conf": conf, "emo": emo,
            "risk": risk, "decision": decision, "reason": reason, "ret": ret}


def make_ticket(text, trace):
    no = "WD" + datetime.datetime.now().strftime("%H%M%S")
    return {"工单号": no, "紧急程度": "P1" if trace["risk"] == "高" else "P2",
            "携带上下文": f"客户诉求：{text}｜意图：{trace['intent']}｜情绪分：{trace['emo']}｜风险：{trace['risk']}"}


# ============================================================
# Tabs
# ============================================================
tab_intro, tab_demo = st.tabs(["系统介绍", "🖥 在线演示（8 屏完整版）"])

# ---------------- Tab 1：系统介绍 ----------------
with tab_intro:
    # ── 1. 业务背景与核心问题 ──
    st.markdown('<div class="section-t">🧭 一、业务背景与核心问题</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="panel">
<div class="feat"><div class="fi">🧩</div><div><div class="ft">复杂场景理解不足</div>
<div class="fd">传统客服机器人只会"关键词问答"，面对业务办理、多条件组合的场景无法理解真实诉求，答非所问。</div></div></div>
<div class="feat"><div class="fi">🚧</div><div><div class="ft">信息割裂、体验被动</div>
<div class="fd">知识库、话务平台、客服系统各自独立；客户要么反复描述，要么被生硬转人工，问题一次解决率低。</div></div></div>
<div class="feat"><div class="fi">⚖️</div><div><div class="ft">风险响应滞后</div>
<div class="fd">高风险诉求（投诉、资损、监管）依赖客户主动投诉才暴露，缺少前置识别与干预。</div></div></div>
<div class="feat"><div class="fi">📉</div><div><div class="ft">坐席负担重、知识更新慢</div>
<div class="fd">坐席人工记录小结、检索话术效率低；知识库靠人工整理，更新滞后，服务质量不可持续。</div></div></div>
</div>
""", unsafe_allow_html=True)

    # ── 2. 产品定位与整体方案 ──
    st.markdown('<div class="section-t" style="margin-top:22px;">🎯 二、产品定位与整体方案（为什么是这个方案）</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="callout" style="border-left:4px solid #2563EB; background:#F8FAFC; padding:18px 20px; border-radius:8px;">
<b style="color:#0F172A; font-size:14.5px;">定位：面向云服务场景，构建覆盖客户自助服务、人工坐席辅助与运营管理的智能客服体系。</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
方案不是做"更聪明的问答机器人"，而是把客服重构为<b>具备决策与执行能力的智能体</b>。原因有三：<br>
① <b>问答机器人解决不了"办理"</b>——查账单、办续费需要调用真实系统，必须引入任务编排与工具调用；<br>
② <b>纯自动化不可行</b>——云服务场景有刚性风险边界（资损、数据安全），必须设计"边界内自主闭环、边界外移交人工"的人机协同；<br>
③ <b>一次性建全能力成本过高</b>——按"先 C 端问答 → 再坐席辅助 → 后运营管理"分阶段建设，每阶段都有独立业务价值。</span>
</div>
""", unsafe_allow_html=True)

    # ── 3. 核心业务流程 ──
    st.markdown('<div class="section-t" style="margin-top:22px;">🔄 三、核心业务流程（端到端服务闭环）</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="arch-box" style="font-size:13px;">
【服务主流程】
  ① 客户接入（官网 PC / 移动端 APP，文字或语音）
     ↓
  ② 意图识别 + 三维评估（业务风险 × 模型置信度 × 客户情绪）
     ↓
  ③ 边界内自主处理：RAG 知识应答（带引用溯源） / 工具调用办理（查账单、办续费，结果回填）
     ↓
  ④ 边界外移交：高风险或低置信 → 携带完整上下文转人工，客户无需重复描述
     ↓
  ⑤ 坐席辅助（坐席工作台）：客户档案 & 工单聚合 · 情绪识别 · 话术推荐 · 实时质检
     ↓
  ⑥ 服务总结 & 工单自动生成
     ↓
  ⑦ 「作业即标注」：服务过程转化为标注数据 → 线上反馈 → 标注回流 → 知识库更新 → 模型持续优化
</div>
""", unsafe_allow_html=True)

    # 关键设计（2 列）
    k1, k2 = st.columns(2, gap="large")
    with k1:
        st.markdown('<div class="section-t" style="margin-top:16px;">🔑 关键设计 · C 端自助</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">💬</div><div><div class="ft">RAG 智能问答</div>
<div class="fd">检索 → 生成 → 引用溯源，回答可验证；多轮会话记忆，跨轮次理解真实诉求；PC 与 APP 双端同源。</div></div></div>
<div class="feat"><div class="fi">🔧</div><div><div class="ft">工具调用办理</div>
<div class="fd">查账单、办续费等直连业务系统，结果回填对话，实现"问答即办理"。</div></div></div>
</div>
""", unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="section-t" style="margin-top:16px;">🔑 关键设计 · B 端坐席辅助</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">📝</div><div><div class="ft">档案 · 情绪 · 话术 · 质检</div>
<div class="fd">客户档案与工单聚合呈现、情绪负面趋势预警、合规话术推荐、违规话术即时提醒。</div></div></div>
<div class="feat"><div class="fi">📄</div><div><div class="ft">服务总结 & 工单生成</div>
<div class="fd">会话结束自动生成小结与工单，坐席从"记录员"回归"问题解决者"。</div></div></div>
</div>
""", unsafe_allow_html=True)

    # ── 4. 关键技术决策与风险控制 ──
    st.markdown('<div class="section-t" style="margin-top:22px;">⚖️ 四、关键技术决策与风险控制</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🧠</div><div><div class="ft">决策① ｜ AI Agent 任务编排为核心</div>
<div class="fd">以 Agent 任务编排替代单轮问答；多模态 RAG 解决知识准确性与单据/图像理解，GraphRAG 解决客户—产品—账户关系推理。把"知识检索"与"关系推理"拆分解，兼顾能力上限与落地成本（与技术团队共同确定）。</div></div></div>
<div class="feat"><div class="fi">📐</div><div><div class="ft">决策② ｜ 三维人机协同边界</div>
<div class="fd">不追求转人工率的极值，按业务风险、模型置信度、客户情绪三个维度定义能力边界——边界内自主闭环，边界外携带上下文移交人工。</div></div></div>
</div>
""", unsafe_allow_html=True)
    with d2:
        st.markdown("""
<div class="panel" style="height:100%;">
<div class="feat"><div class="fi">🏷️</div><div><div class="ft">决策③ ｜ 作业即标注的知识闭环</div>
<div class="fd">主导感知—决策—执行闭环设计：智能服务总结、情绪识别、智能话术、实时质检、知识管理；以"作业即标注"把服务过程转化为标注数据，结合线上反馈—标注回流—知识更新，模型与知识库质量可持续优化。</div></div></div>
<div class="feat"><div class="fi">🧱</div><div><div class="ft">决策④ ｜ 平台化复用</div>
<div class="fd">知识库、话术配置与任务编排抽象为统一能力层，官网与 APP、渠道伙伴场景共用同一套配置与知识资产，避免同类能力重复建设。</div></div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="callout" style="border-left:4px solid #B91C1C; background:#FEF2F2; padding:14px 18px; margin-top:14px; border-radius:8px;">
<b style="color:#0F172A; font-size:14px;">🛡️ 风险控制</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
① 高风险业务（资损、投诉、监管类）强制转人工，不允许模型自主办理；② 知识库模型不直接写库，所有修复走人工审核（发现→归因→修复→复验）；③ 服务过程实时质检，违规话术即时拦截；④ 全链路数据脱敏与权限隔离。</span>
</div>
""", unsafe_allow_html=True)

    # ── 5. 业务价值与验证指标 ──
    st.markdown('<div class="section-t" style="margin-top:22px;">📈 五、业务价值与验证指标</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="callout" style="border-left:4px solid #B45309; background:#FFFBEB; padding:18px 20px; border-radius:8px;">
<b style="color:#0F172A; font-size:15px;">业务结果（上线前后同期对比）</b><br>
<span style="color:#475569; font-size:14px; line-height:1.9;">
✅ <b>转人工率下降 60%</b>，<b>工单量下降 80%</b>，客户问题自助解决效率显著提升<br>
✅ 「未诉先办」主动预警：实现高风险客户的前置识别与干预<br>
✅ AI 驱动的增值服务推荐，贡献上线后 <b>5% 的增值收入</b>
</span><br><br>
<b style="color:#0F172A; font-size:14px;">📐 验证指标体系</b><br>
<span style="color:#475569; font-size:13.5px; line-height:1.8;">
围绕客户问题解决效率、坐席服务质量与客服运营效率三条主线持续验证：<b>转人工率 · 用户满意度 · 工单处理时长 · 话术采纳率</b>（另辅以问题一次解决率、知识库覆盖率等过程指标）。
</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="callout" style="margin-top:14px;"><b>🚀 完整版：</b>完整系统含 C 端双端（PC / APP）、坐席工作台、知识管理、运营看板、任务中心、后台设置与质检工作台 —— 均已在右侧「在线演示」中可交互。</div>', unsafe_allow_html=True)

# ---------------- Tab 2：在线演示（8 屏） ----------------
with tab_demo:
    ss = st.session_state
    ss.setdefault("messages_pc", [])
    ss.setdefault("messages_app", [])
    ss.setdefault("tickets", [])
    ss.setdefault("th", dict(DEFAULT_TH))
    ss.setdefault("docs", [
        {"title": "如何重置云服务器密码？", "sys": "ECS · 常见问题", "time": "2026-10-29", "status": "已生效", "hits": 1284},
        {"title": "如何申请退还误购实例？", "sys": "计费 · 高风险问答", "time": "2026-10-25", "status": "已生效", "hits": 342},
        {"title": "云服务器快照与备份的区别？", "sys": "存储 · 常见问题", "time": "2026-10-21", "status": "已生效", "hits": 747},
        {"title": "磁盘扩容后需要重启吗？", "sys": "ECS · 常见问题", "time": "2026-10-18", "status": "已生效", "hits": 742},
        {"title": "安全组放行端口配置步骤", "sys": "网络 · 配置指南", "time": "2026-10-12", "status": "已生效", "hits": 508},
        {"title": "实例到期未续费会停机吗？", "sys": "计费 · 常见问题", "time": "2026-10-08", "status": "已生效", "hits": 689},
        {"title": "域名备案流程与审核时长", "sys": "备案 · 流程指南", "time": "2026-09-30", "status": "已生效", "hits": 913},
        {"title": "如何配置 CPU 使用率告警？", "sys": "监控 · 配置指南", "time": "2026-09-26", "status": "已生效", "hits": 615},
    ])
    ss.setdefault("tasks", [
        {"name": "云耀服务器卡顿 · 1 年", "level": "高", "status": "待响应", "owner": "王工", "sla": "2 小时", "src": "在线会话"},
        {"name": "云耀云服务器续费流程咨询", "level": "中", "status": "进行中", "owner": "AI Agent", "sla": "8 小时", "src": "APP 会话"},
        {"name": "带宽突发限流预警跟进", "level": "高", "status": "处理中", "owner": "李工", "sla": "4 小时", "src": "告警联动"},
        {"name": "客户投诉服务器购买流程", "level": "高", "status": "待审批", "owner": "AI Agent", "sla": "2 小时", "src": "质检升级"},
        {"name": "续费优惠即将到期提醒", "level": "低", "status": "待响应", "owner": "运营组", "sla": "24 小时", "src": "营销联动"},
        {"name": "备案审核时长咨询", "level": "低", "status": "已办结", "owner": "AI Agent", "sla": "24 小时", "src": "PC 会话"},
    ])
    ss.setdefault("qc", [
        {"sess": "会话 #CS10241", "agent": "坐席 · 刘敏", "rule": "承诺未兑现（预计完成时间已超 2 次）", "score": 62, "status": "待复核",
         "clip": "客户：工单说今天 18:00 前完成，现在还没人联系我。　坐席：马上就好，您再等等。"},
        {"sess": "会话 #CS10238", "agent": "坐席 · 王凯", "rule": "服务禁语（直接否定客户）", "score": 71, "status": "待复核",
         "clip": "客户：是不是你们系统出 bug 了？　坐席：不是我们系统的问题，是您自己操作不对。"},
        {"sess": "会话 #CS10235", "agent": "AI Agent", "rule": "（推荐学习样本）高风险升级处置规范", "score": 96, "status": "已通过",
         "clip": "客户：数据丢了！　AI：已升级 P1 工单并转人工专家，上下文同步，30 秒内接入。"},
    ])

    # ───────── 通用：渲染一条 AI 消息（含 trace / ticket） ─────────
    def render_msg(m):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("trace"):
                t = m["trace"]
                with st.expander("🧠 Agent 决策过程"):
                    st.markdown(
                        f"- **意图识别**：{t['intent']}\n"
                        f"- **知识检索**：{'命中 ' + t['kb']['id'] + '《' + t['kb']['q'] + '》 召回分 ' + str(t['ret']) if t['kb'] else '未命中知识条目'}\n"
                        f"- **置信度**：{t['conf']}（阈值 {ss['th']['conf']}）\n"
                        f"- **情绪分**：{t['emo']}（阈值 {ss['th']['emotion']}）｜**业务风险**：{t['risk']}\n"
                        f"- **路由决策**：`{t['decision']}` —— {t['reason']}"
                    )
            if m.get("ticket"):
                st.json(m["ticket"])

    def process(prompt, store):
        store.append({"role": "user", "content": prompt})
        trace = route(prompt, ss["th"])
        if trace["decision"] == "转人工":
            ticket = make_ticket(prompt, trace)
            ss["tickets"].append(ticket)
            reply = ("非常理解您的心情，这件事我会优先为您处理。已为您转接人工坐席，"
                     "会话与上下文已同步给坐席，无需重复描述。")
            store.append({"role": "assistant", "content": reply, "trace": trace, "ticket": ticket})
        elif trace["decision"] == "调用工具":
            tool = next((t for t in TOOLS if any(k in prompt for k in t[:2])), None)
            result = TOOLS[tool]["run"]() if tool else {}
            rows = "\n".join(f"| {k} | {v} |" for k, v in result.items())
            reply = f"已为您调用「{tool}」，结果如下：\n\n| 项目 | 结果 |\n|---|---|\n{rows}\n\n还需要我继续办理或调整吗？"
            store.append({"role": "assistant", "content": reply, "trace": trace})
        elif trace["intent"] == "寒暄":
            store.append({"role": "assistant",
                          "content": "您好，我是云服务智能助手 ☺ 可以帮您查账单、办续费、查工单进度，也可以解答配置与计费问题。请说说您的需求～",
                          "trace": trace})
        elif trace["decision"] == "知识应答":
            store.append({"role": "assistant",
                          "content": trace["kb"]["a"] + f"\n\n（来源：知识库 {trace['kb']['id']}）",
                          "trace": trace})
        else:
            store.append({"role": "assistant",
                          "content": "为了准确帮您处理，想跟您确认一下：您是想【查询/办理】还是【咨询规则】呢？也可以直接说\"查账单\"、\"办续费\"、\"查工单\"。",
                          "trace": trace})

    s_pc, s_app, s_seat, s_kb, s_dash, s_task, s_set, s_qc = st.tabs(
        ["💻 PC 客服对话", "📱 APP 客服对话", "🎧 坐席工作台", "📚 企业知识管理",
         "📊 数据看板", "✅ 任务管理中心", "⚙️ 后台设置", "🔍 质检工作台"])

    # ============ 屏 1：PC 端客服对话 ============
    with s_pc:
        st.markdown('<div class="section-t">💻 C 端 · 官网 PC 客服对话 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 知识应答 → 工具调用 → 转人工，边界可调</span></div>', unsafe_allow_html=True)
        c_th1, c_th2, c_info = st.columns([1, 1, 1.6])
        with c_th1:
            ss["th"]["conf"] = st.slider("置信度阈值", 0.30, 0.95, ss["th"]["conf"], 0.01, key="th_conf_pc", help="调高 → 机器少答、多问；调低相反")
        with c_th2:
            ss["th"]["emotion"] = st.slider("情绪阈值", 0.20, 1.00, ss["th"]["emotion"], 0.05, key="th_emo_pc", help="调低 → 更快转人工，体验优先")
        with c_info:
            st.markdown(
                f'<div class="panel" style="padding:8px 14px;font-size:12.5px;color:#64748B;">'
                f'知识库 {len(ss["docs"])}+ 条 · 当前阈值：置信度 <b style="color:#1D4ED8;">{ss["th"]["conf"]}</b> / 情绪 <b style="color:#1D4ED8;">{ss["th"]["emotion"]}</b>'
                f' ｜ 本会话累计转人工 <b style="color:#D97706;">{len(ss["tickets"])}</b> 单</div>',
                unsafe_allow_html=True,
            )

        ex1, ex2, ex3, ex4 = st.columns(4)
        for c, label, q in [
            (ex1, "📖 问：到期未续费会停机吗", "实例到期未续费会停机吗"),
            (ex2, "🔧 办：查一下我的账单", "查一下我的资源账单"),
            (ex3, "😤 测：数据丢了很生气", "我的数据怎么丢了！再不给解决我就投诉到银监会！"),
            (ex4, "🧹 清空 PC 会话", None),
        ]:
            with c:
                if st.button(label, use_container_width=True, key=f"pc_{label}"):
                    if q is None:
                        ss["messages_pc"] = []
                    else:
                        ss["queued_pc"] = q
                    st.rerun()

        if ss.get("queued_pc"):
            process(ss.pop("queued_pc"), ss["messages_pc"])
            st.rerun()

        chat = st.container(height=380)
        with chat:
            if not ss["messages_pc"]:
                st.markdown('<div style="text-align:center;color:#64748B;padding-top:110px;font-size:14px;">'
                            '👆 点击上方快捷问题，或在下方输入框直接提问<br>试试从「知识应答 → 工具调用 → 转人工」各触发一次</div>',
                            unsafe_allow_html=True)
            for m in ss["messages_pc"]:
                render_msg(m)

        if prompt := st.chat_input("试试：怎么续费 / 查一下我的账单 / 我的数据丢了，气死我了", key="pc_input"):
            process(prompt, ss["messages_pc"])
            st.rerun()

        st.markdown('<div class="callout"><b>建议演示路径：</b>① 问「到期未续费会停机吗」→ 知识应答（展开决策过程看三维路由）；'
                    '② 问「查一下我的账单」→ 工具调用与结果回填；③ 说「数据丢了，投诉到银监会」→ 高风险 + 高情绪 → 自动转人工并生成 P1 工单；'
                    '④ 把置信度阈值拉到 0.95 再问 ① → 同一句话变成澄清反问；⑤ 去屏幕 7「后台设置」改阈值 → 回到这里路由同步变化（配置与运行时联动）。</div>',
                    unsafe_allow_html=True)

    # ============ 屏 2：APP 端客服对话 ============
    with s_app:
        st.markdown('<div class="section-t">📱 C 端 · 移动端 APP 客服对话 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 与 PC 同一引擎与知识资产，渠道隔离、体验一致</span></div>', unsafe_allow_html=True)
        lc, mc, rc = st.columns([1.2, 2.2, 1.2])
        with lc:
            st.markdown("""
<div class="profile">
  <div class="p-title">📱 双端同源设计</div>
  <div class="p-row"><span class="k">会话引擎</span><span class="v">同一 Agent</span></div>
  <div class="p-row"><span class="k">知识资产</span><span class="v">同一知识库</span></div>
  <div class="p-row"><span class="k">人机边界</span><span class="v">同一套阈值</span></div>
  <div class="p-row"><span class="k">工单体系</span><span class="v">统一工单池</span></div>
  <div class="p-row"><span class="k">会话记忆</span><span class="v">渠道内隔离</span></div>
</div>
""", unsafe_allow_html=True)
        with mc:
            exa, exb, exc = st.columns(3)
            for c, label, q in [
                (exa, "查订单/工单", "帮我查一下工单进度"),
                (exb, "转人工", "我要转人工客服"),
                (exc, "🧹 清空", None),
            ]:
                with c:
                    if st.button(label, use_container_width=True, key=f"app_{label}"):
                        if q is None:
                            ss["messages_app"] = []
                        else:
                            ss["queued_app"] = q
                        st.rerun()

            if ss.get("queued_app"):
                process(ss.pop("queued_app"), ss["messages_app"])
                st.rerun()

            chat = st.container(height=380)
            with chat:
                if not ss["messages_app"]:
                    st.markdown('<div style="text-align:center;color:#64748B;padding-top:110px;font-size:14px;">'
                                '👆 移动端演示：试试「查工单进度」或「转人工」</div>', unsafe_allow_html=True)
                for m in ss["messages_app"]:
                    render_msg(m)

            if prompt := st.chat_input("输入消息…", key="app_input"):
                process(prompt, ss["messages_app"])
                st.rerun()
        with rc:
            st.markdown("""
<div class="profile">
  <div class="p-title">📐 移动端体验要点</div>
  <div class="p-row"><span class="k">首响</span><span class="v">&lt; 1 秒</span></div>
  <div class="p-row"><span class="k">断线续聊</span><span class="v">支持</span></div>
  <div class="p-row"><span class="k">语音输入</span><span class="v">语音转文字</span></div>
  <div class="p-row"><span class="k">快捷入口</span><span class="v">工单/续费/账单</span></div>
  <div class="p-row"><span class="k">满意度评价</span><span class="v">会话结束弹窗</span></div>
</div>
""", unsafe_allow_html=True)

    # ============ 屏 3：坐席工作台 ============
    with s_seat:
        st.markdown('<div class="section-t">🎧 B 端 · 坐席接线 · 工单处理对话界面 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 客户档案 × 会话 × AI 辅助三栏协同</span></div>', unsafe_allow_html=True)
        cl, cm, cr = st.columns([1, 1.6, 1], gap="medium")
        with cl:
            st.markdown("""
<div class="profile">
  <div class="p-title">👤 客户档案</div>
  <div class="p-row"><span class="k">客户姓名</span><span class="v">王建国</span></div>
  <div class="p-row"><span class="k">账户类型</span><span class="v">企业客户</span></div>
  <div class="p-row"><span class="k">会员等级</span><span class="v">黄金会员</span></div>
  <div class="p-row"><span class="k">持有产品</span><span class="v">云耀云服务器 ECS</span></div>
  <div class="p-row"><span class="k">历史工单</span><span class="v">3 次</span></div>
  <div class="p-row"><span class="k">客户价值</span><span class="v">中高（年消费 ¥1.2 万）</span></div>
</div>
""", unsafe_allow_html=True)
            st.markdown("""
<div class="profile" style="margin-top:12px;">
  <div class="p-title">🧾 工单信息</div>
  <div class="p-row"><span class="k">工单主题</span><span class="v">磁盘扩容后挂载异常</span></div>
  <div class="p-row"><span class="k">工单编号</span><span class="v">WD2026102134</span></div>
  <div class="p-row"><span class="k">工单状态</span><span class="v">处理中</span></div>
  <div class="p-row"><span class="k">优先级</span><span class="v" style="color:#DC2626;">P1 · 高</span></div>
  <div class="p-row"><span class="k">创建时间</span><span class="v">2026-11-02</span></div>
  <div class="p-row"><span class="k">负责工程师</span><span class="v">张工</span></div>
</div>
""", unsafe_allow_html=True)
        with cm:
            st.markdown("**💬 沟通记录**（AI 实时转写 · 意图与情绪已标注）")
            chat = st.container(height=330)
            with chat:
                st.chat_message("user").markdown("我的 ECS 磁盘扩容之后一直挂载不上，业务都受影响了，你们怎么处理的？")
                st.chat_message("assistant").markdown("王先生您好，非常抱歉给您业务带来影响。我已看到您的工单 WD2026102134（磁盘扩容后挂载异常），工程师张工正在处理，我为您同步一下最新进展。")
                st.chat_message("user").markdown("好了两天了，时间还没法定吗？")
                st.chat_message("assistant").markdown("理解您着急。目前定位到是扩容后的分区表未更新，工程师正在为您执行在线修复，预计今天 18:00 前完成，完成后我会第一时间通知您。")
                st.chat_message("assistant").markdown("我同步了处理进度：修复动作已完成 70%，数据完好无风险，请您放心。")
            st.markdown('<div class="note">📌 转人工携带上下文：客户诉求（挂载异常 / 业务受影响）· 情绪（焦虑）· 风险（高·业务受损）已自动带入，客户无需重复描述。</div>', unsafe_allow_html=True)
        with cr:
            st.markdown("**😒 情绪识别**")
            st.markdown("""
<div class="hrow"><div class="hname">当前负面值</div><div class="hbar-wrap"><div class="hbar" style="width:62%;background:linear-gradient(90deg,#F59E0B,#DC2626);"></div></div><div class="hval">0.62</div></div>
<div class="hrow"><div class="hname">焦虑趋势</div><div class="hbar-wrap"><div class="hbar" style="width:48%;background:#F59E0B;"></div></div><div class="hval">上升 ↑</div></div>
""", unsafe_allow_html=True)
            st.markdown('<div class="note" style="margin-top:2px;">⚠ 客户提及"业务受影响"，情绪连续 2 轮上升，建议主动给进度承诺。</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-t" style="margin-top:12px;">🧠 智能话术推荐</div>', unsafe_allow_html=True)
            picked = st.session_state.setdefault("script", None)
            sc1, sc2, sc3 = st.columns(3)
            if sc1.button("道歉安抚", key="sc1", use_container_width=True):
                ss["script"] = "确实给您和业务造成了困扰，非常抱歉。我现在就把处理进展同步给您。"
            if sc2.button("进度承诺", key="sc2", use_container_width=True):
                ss["script"] = "修复已完成 70%，预计今天 18:00 前恢复，完成后我第一时间联系您；如果提前恢复也会提前通知。"
            if sc3.button("补偿方案", key="sc3", use_container_width=True):
                ss["script"] = "本次故障影响的时长，我们会按 SLA 给予资源时长补偿，稍后我把方案发到您的站内信。"
            if ss.get("script"):
                st.markdown(f'<div class="callout" style="margin-top:6px;">{ss["script"]}</div>', unsafe_allow_html=True)
                if st.button("✅ 采纳并回填到会话", key="sc_use"):
                    ss["script_used"] = True
                    st.toast("话术已回填坐席输入框", icon="✅")

            st.markdown('<div class="section-t" style="margin-top:12px;">📈 续费/采购趋势</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="hrow"><div class="hname">实例续费意愿</div><div class="hbar-wrap"><div class="hbar" style="width:74%;background:#2563EB;"></div></div><div class="hval">较高</div></div>
<div class="hrow"><div class="hname">扩容需求</div><div class="hbar-wrap"><div class="hbar" style="width:58%;background:#3B82F6;"></div></div><div class="hval">上升</div></div>
<div class="hrow"><div class="hname">增值服务机会</div><div class="hbar-wrap"><div class="hbar" style="width:36%;background:#93C5FD;"></div></div><div class="hval">云备份</div></div>
""", unsafe_allow_html=True)

            if st.button("📝 生成服务总结 & 工单", use_container_width=True, type="primary", key="seat_summary"):
                st.markdown("""
<div class="callout" style="margin-top:8px;">
<b>服务小结（AI 生成）：</b>客户王建国，企业客户/黄金会员，反馈 ECS 磁盘扩容后挂载异常影响业务（工单 WD2026102134，P1）。已同步处理进度（修复 70%，预计 18:00 前完成），承诺按 SLA 补偿并通知结果。<br>
<b>待办：</b>① 完成后主动外呼确认恢复；② 跟进 SLA 补偿发放；③ 挖掘云备份增值需求（已识别意向）。<br>
<b>工单状态：</b>保持 P1 · 处理中，自动关联本会话记录。
</div>
""", unsafe_allow_html=True)

    # ============ 屏 4：企业知识管理 ============
    with s_kb:
        st.markdown('<div class="section-t">📚 企业知识管理系统 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 知识条目 · 审核生效 · 命中分析（作业即标注闭环）</span></div>', unsafe_allow_html=True)
        q1, q2 = st.columns([2, 1])
        with q1:
            kw = st.text_input("搜索知识条目", "", label_visibility="collapsed", placeholder="搜索：标题 / 所属系统，如「磁盘」「计费」")
        with q2:
            f_status = st.select_slider("状态筛选", ["全部", "已生效", "待审核"])

        docs = ss["docs"]
        if kw:
            docs = [d for d in docs if kw in d["title"] or kw in d["sys"]]
        if f_status != "全部":
            docs = [d for d in docs if d["status"] == f_status]

        rows_html = ""
        pill_map = {"已生效": "ok", "待审核": "wait"}
        for d in docs:
            rows_html += (f"<tr><td style='font-weight:600;color:#0F172A;'>{d['title']}</td>"
                          f"<td>{d['sys']}</td>"
                          f"<td><span class='pill {pill_map.get(d['status'], 'draft')}'>{d['status']}</span></td>"
                          f"<td>{d['time']}</td><td>{d['hits']:,} 次</td></tr>")
        if rows_html:
            st.markdown(f"""
<div class="panel" style="padding:6px 18px 12px 18px;">
<table style="width:100%;border-collapse:collapse;font-size:13px;color:#475569;">
<tr style="color:#94A3B8;font-size:12px;text-align:left;">
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">标题</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">所属系统</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">状态</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">更新时间</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">本月命中</th>
</tr>{rows_html}</table></div>
""", unsafe_allow_html=True)
        else:
            st.info("没有匹配的知识条目。")

        st.markdown('<div class="section-t" style="margin-top:18px;">➕ 新增知识（走审核流，模型不直接写库）</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns([1.4, 1, 0.6])
        with f1:
            new_title = st.text_input("问题标题", placeholder="如：如何绑定解绑 SSH 密钥对？")
        with f2:
            new_sys = st.selectbox("所属系统", ["ECS · 常见问题", "计费 · 常见问题", "网络 · 配置指南", "存储 · 配置指南", "备案 · 流程指南"])
        with f3:
            st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
            if st.button("提交审核", type="primary", use_container_width=True):
                if new_title.strip():
                    ss["docs"].insert(0, {"title": new_title.strip(), "sys": new_sys, "time": "2026-11-03", "status": "待审核", "hits": 0})
                    st.success(f"「{new_title.strip()}」已提交，进入待审核队列")
                else:
                    st.warning("请填写问题标题")

        st.markdown('<div class="callout"><b>作业即标注闭环：</b>线上会话未命中的问题自动进入候选池 → 知识运营补录 → 审核生效 → 命中率回升；'
                    '本月知识新增 42 条，其中 <b>68% 来自会话挖掘</b>，知识库覆盖率从 81% 提升到 93%。</div>', unsafe_allow_html=True)

    # ============ 屏 5：数据看板 ============
    with s_dash:
        st.markdown('<div class="section-t">📊 客服运营数据看板 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 数据为演示模拟数据，口径与验证指标体系一致</span></div>', unsafe_allow_html=True)
        st.markdown("""
<div class="kpi-row">
  <div class="kpi green"><div class="label">转人工率（较上线前 -60%）</div><div class="value">18.4%</div></div>
  <div class="kpi hot"><div class="label">AI 独立解决率</div><div class="value">92.1%</div></div>
  <div class="kpi"><div class="label">平均转人工等待</div><div class="value">26 <em style="font-style:normal;font-size:13px;color:#64748B;">分钟</em></div></div>
  <div class="kpi warn"><div class="label">问题一次解决率</div><div class="value">64.7%</div></div>
</div>
""", unsafe_allow_html=True)

        b1, b2 = st.columns(2, gap="large")
        with b1:
            st.markdown("**转人工主因分布**")
            bars1 = [("复杂业务咨询", 35, "#2563EB"), ("高风险业务", 28, "#DC2626"), ("情绪升级", 22, "#F59E0B"), ("低置信度", 15, "#94A3B8")]
            st.markdown("".join(
                f'<div class="hrow"><div class="hname">{n}</div>'
                f'<div class="hbar-wrap"><div class="hbar" style="width:{v*2.4}%;background:{c}"></div></div>'
                f'<div class="hval">{v}%</div></div>' for n, v, c in bars1
            ), unsafe_allow_html=True)
            st.markdown('<div class="note">↑ 高风险与情绪类转人工属<b>主动设计</b>（边界外移交），并非能力不足；真正待优化的是复杂咨询理解。</div>', unsafe_allow_html=True)
        with b2:
            st.markdown("**工单处理时长分布**")
            bars2 = [("AI 自动闭环", 42, "#16A34A"), ("坐席 30 分钟内", 31, "#2563EB"), ("当日办结", 18, "#3B82F6"), ("跨日跟进", 9, "#94A3B8")]
            st.markdown("".join(
                f'<div class="hrow"><div class="hname">{n}</div>'
                f'<div class="hbar-wrap"><div class="hbar" style="width:{v*2.4}%;background:{c}"></div></div>'
                f'<div class="hval">{v}%</div></div>' for n, v, c in bars2
            ), unsafe_allow_html=True)
            st.markdown('<div class="note">↑ AI 自动闭环 + 坐席快速办结合计 73%，工单平均处理时长较上线前缩短。</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-t" style="margin-top:16px;">近 14 天转人工率趋势</div>', unsafe_allow_html=True)
        trend = [24, 23, 25, 22, 21, 20, 21, 19, 20, 18, 19, 18, 18, 18]
        max_t, min_t = max(trend), min(trend)
        spark = "".join(
            f'<div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px;">'
            f'<div style="font-size:9px;color:#94A3B8;">{v}</div>'
            f'<div style="width:70%;height:{14 + (v - min_t) / max(max_t - min_t, 1) * 60:.0f}px;background:linear-gradient(180deg,#3B82F6,#93C5FD);border-radius:3px;"></div>'
            f'<div style="font-size:9px;color:#CBD5E1;">D{i+1}</div></div>'
            for i, v in enumerate(trend)
        )
        st.markdown(f'<div class="panel" style="display:flex;gap:6px;align-items:flex-end;height:130px;padding:12px;">{spark}</div>', unsafe_allow_html=True)
        st.markdown('<div class="callout"><b>看板即运营：</b>指标异动自动下钻到会话明细与任务中心（屏幕 6）——例如"低置信度转人工占比上升"会自动生成知识补录任务，进入屏幕 4 的候选池。</div>', unsafe_allow_html=True)

    # ============ 屏 6：任务管理中心 ============
    with s_task:
        st.markdown('<div class="section-t">✅ 任务管理中心 <span style="color:#64748B;font-size:12px;font-weight:400;">—— AI 预处理的任务流：风险分级 × SLA × 人工审批</span></div>', unsafe_allow_html=True)
        tf1, tf2 = st.columns([1, 1.6])
        with tf1:
            f_level = st.select_slider("风险等级", ["全部", "高", "中", "低"])
        with tf2:
            st.markdown('<div class="panel" style="padding:8px 14px;font-size:12.5px;color:#64748B;">'
                        f'今日任务 <b style="color:#2563EB;">{len(ss["tasks"])}</b> ｜ 待审批 <b style="color:#D97706;">{sum(1 for t in ss["tasks"] if t["status"] == "待审批")}</b>'
                        ' ｜ 超时风险任务自动置顶</div>', unsafe_allow_html=True)

        tasks = [t for t in ss["tasks"] if f_level == "全部" or t["level"] == f_level]
        level_pill = {"高": "risk", "中": "wait", "低": "draft"}
        rows_html = ""
        for i, t in enumerate(tasks):
            rows_html += (f"<tr><td style='font-weight:600;color:#0F172A;'>{t['name']}</td>"
                          f"<td><span class='pill {level_pill[t['level']]}'>{t['level']}风险</span></td>"
                          f"<td>{t['status']}</td><td>{t['owner']}</td><td>{t['src']}</td>"
                          f"<td>SLA 剩 <b style='color:{'#DC2626' if t['level']=='高' else '#334155'}'>{t['sla']}</b></td></tr>")
        st.markdown(f"""
<div class="panel" style="padding:6px 18px 12px 18px;">
<table style="width:100%;border-collapse:collapse;font-size:13px;color:#475569;">
<tr style="color:#94A3B8;font-size:12px;text-align:left;">
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">任务 / 工单主题</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">风险等级</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">状态</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">当前处理方</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">来源</th>
<th style="padding:10px 8px;border-bottom:1px solid #E2E8F0;">时效</th>
</tr>{rows_html}</table></div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-t" style="margin-top:16px;">🀄 待人工审批（AI 处理到边界，人做最终决定）</div>', unsafe_allow_html=True)
        pending = [t for t in ss["tasks"] if t["status"] == "待审批"]
        if not pending:
            st.success("当前无待审批任务 —— 全部任务在边界内由 AI 自主闭环或已转派处理。")
        for i, t in enumerate(pending):
            with st.container():
                cA, cB, cC = st.columns([3, 1, 1])
                with cA:
                    st.markdown(f'<div class="panel" style="padding:10px 16px;font-size:13px;"><b style="color:#0F172A;">{t["name"]}</b>'
                                f'<span class="pill risk" style="margin-left:8px;">{t["level"]}风险</span><br>'
                                f'<span style="color:#64748B;font-size:12px;">AI 建议：转人工专项处理 · 已附会话摘要与客户档案</span></div>', unsafe_allow_html=True)
                with cB:
                    if st.button("✔ 通过", key=f"ok_{i}", use_container_width=True):
                        t["status"] = "处理中"
                        st.rerun()
                with cC:
                    if st.button("✖ 驳回", key=f"no_{i}", use_container_width=True):
                        ss["tasks"].remove(t)
                        st.rerun()
        st.markdown('<div class="callout"><b>设计要点：</b>任务中心不是"人工替补 AI"，而是"AI 处理到能力边界，人做最终决定"——'
                    '每条任务的来源、风险分级、SLA、AI 处理痕迹全部可见，运营后台只处理例外。</div>', unsafe_allow_html=True)

    # ============ 屏 7：后台设置 ============
    with s_set:
        st.markdown('<div class="section-t">⚙️ 智能客服后台设置 <span style="color:#64748B;font-size:12px;font-weight:400;">—— 配置实时生效，直接 influence 屏 1 / 屏 2 的对话路由</span></div>', unsafe_allow_html=True)
        st.markdown("**🧩 能力开关**")
        t1, t2, t3, t4 = st.columns(4)
        toggles = {}
        for col, name, default, help_t in [
            (t1, "知识库自动更新", True, "审核通过的知识自动同步到检索库"),
            (t2, "多轮会话记忆", True, "跨轮次理解上下文"),
            (t3, "情绪预警推送", True, "负面情绪达阈值推送坐席组长"),
            (t4, "敏感词实时拦截", True, "违规话术即时提醒坐席"),
        ]:
            with col:
                toggles[name] = st.toggle(name, default, help=help_t)

        st.markdown('<div class="section-t" style="margin-top:16px;">🎚 人机协同边界（与屏 1 的滑杆联动）</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            ss["th"]["conf"] = st.slider("模型置信度阈值", 0.30, 0.95, ss["th"]["conf"], 0.01, key="th_conf_set",
                                         help="低于该阈值不直接作答，转澄清或人工 —— 拉高后到屏 1 问同一句话试试")
        with g2:
            ss["th"]["emotion"] = st.slider("客户情绪阈值", 0.20, 1.00, ss["th"]["emotion"], 0.05, key="th_emo_set",
                                            help="负面情绪超过该值即触发转人工")

        st.markdown('<div class="section-t" style="margin-top:16px;">🛡 质检规则 / 风险策略</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("""
<div class="panel">
<div class="feat"><div class="fi">🚫</div><div><div class="ft">高风险业务强制转人工</div>
<div class="fd">退款、数据安全、投诉、监管类诉求，不允许模型自主办理。</div></div></div>
<div class="feat"><div class="fi">📝</div><div><div class="ft">知识库写保护</div>
<div class="fd">AI 发现的知识缺口只生成补录任务，写库必须人工审核。</div></div></div>
</div>
""", unsafe_allow_html=True)
        with r2:
            st.markdown("""
<div class="panel">
<div class="feat"><div class="fi">📢</div><div><div class="ft">生效范围</div>
<div class="fd">全渠道（官网 PC / APP / 小程序）· 售前 + 售后；渠道级灰度可单独配置。</div></div></div>
<div class="feat"><div class="fi">🕘</div><div><div class="ft">变更留痕</div>
<div class="fd">阈值与策略调整全部留痕，支持一键回滚历史版本。</div></div></div>
</div>
""", unsafe_allow_html=True)

        if st.button("💾 保存设置", type="primary"):
            st.success("设置已保存并实时生效（演示：阈值已同步到对话路由）")
        st.markdown('<div class="note">👆 保存后回到「PC 客服对话」问同一句话，可看到阈值对路由决策的实际影响。</div>', unsafe_allow_html=True)

    # ============ 屏 8：质检工作台 ============
    with s_qc:
        st.markdown('<div class="section-t">🔍 质检与「作业即标注」审核工作台 <span style="color:#64748B;font-size:12px;font-weight:400;">—— AI 全量质检 + 人工复核，双维度打分</span></div>', unsafe_allow_html=True)
        qk1, qk2, qk3 = st.columns(3)
        with qk1:
            st.markdown('<div class="panel" style="text-align:center;padding:12px;"><div style="color:#64748B;font-size:12px;">今日质检会话</div><div style="font-size:22px;font-weight:800;color:#0F172A;">1,842</div></div>', unsafe_allow_html=True)
        with qk2:
            st.markdown('<div class="panel" style="text-align:center;padding:12px;"><div style="color:#64748B;font-size:12px;">AI 拦截违规话术</div><div style="font-size:22px;font-weight:800;color:#DC2626;">17</div></div>', unsafe_allow_html=True)
        with qk3:
            st.markdown('<div class="panel" style="text-align:center;padding:12px;"><div style="color:#64748B;font-size:12px;">人工复核完成率</div><div style="font-size:22px;font-weight:800;color:#16A34A;">100%</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-t" style="margin-top:14px;">质检任务列表</div>', unsafe_allow_html=True)
        qc_pill = {"待复核": "wait", "已通过": "ok", "已标记违规": "risk"}
        for i, q in enumerate(ss["qc"]):
            with st.expander(f"{q['sess']} ｜ {q['agent']} ｜ 命中：{q['rule']} ｜ 质检分 {q['score']} ｜ {q['status']}"):
                st.markdown(f'<div class="panel" style="font-size:13px;">{q["clip"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="note">AI 质检依据：服务规范 · 承诺一致性 · 禁语库 · 情绪处置 SOP（双维度：合规 × 体验）</div>', unsafe_allow_html=True)
                if q["status"] == "待复核":
                    cA, cB = st.columns(2)
                    if cA.button("✔ 复核通过", key=f"qc_ok_{i}", use_container_width=True):
                        q["status"] = "已通过"; st.rerun()
                    if cB.button("⚠ 标记违规并生成培训任务", key=f"qc_no_{i}", use_container_width=True):
                        q["status"] = "已标记违规"; st.rerun()

        st.markdown('<div class="callout"><b>闭环价值：</b>质检结果自动回流——违规样本进入坐席培训任务、优秀样本（如 AI 处置规范）进入话术推荐库、'
                    '规则误判样本回流质检模型迭代——这就是「作业即标注」：服务过程本身就是训练数据。</div>', unsafe_allow_html=True)

st.markdown('<div class="note">演示为纯本地规则实现（意图识别 / RAG 检索 / 三维路由 / 工具编排 / 配置联动），结构与大模型版一致，可直接替换推理引擎 ｜ 示例数据均为模拟数据</div>', unsafe_allow_html=True)
