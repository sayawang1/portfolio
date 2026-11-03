# -*- coding: utf-8 -*-
"""
pages/5_监管报送规则引擎.py  ·  v2 重设计
信托监管报送平台 —— 校验规则系统化：政策更新 = 配置变更，不是改代码
设计：深色卡片 + 流程管线 + 规则卡 + 异常告警卡。
"""
import streamlit as st

st.set_page_config(page_title="监管报送规则引擎", page_icon="🏦", layout="wide", initial_sidebar_state="collapsed")

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

    .kpi-row { display:flex; gap:14px; margin:16px 0 4px 0; }
    .kpi { flex:1; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px; }
    .kpi .label { color:#64748B; font-size:12px; margin-bottom:6px; }
    .kpi .value { color:#0F172A; font-size:26px; font-weight:800; }
    .kpi .value em { font-style:normal; font-size:14px; color:#64748B; font-weight:500; margin-left:4px; }
    .kpi.warn .value { color:#D97706; }
    .kpi.ok .value { color:#16A34A; }

    /* 流程管线 */
    .pipe { display:flex; align-items:center; gap:8px; margin:14px 0 18px 0; flex-wrap:wrap; }
    .pstep { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:9px 16px;
             font-size:13px; color:#475569; font-weight:600; }
    .pstep.hl { border-color:#2563EB; color:#1D4ED8; background:#EFF6FF; }
    .parrow { color:#94A3B8; font-size:14px; }

    /* 数据表（自绘） */
    .dtable { width:100%; border-collapse:collapse; font-size:12.5px; margin:10px 0 4px 0; }
    .dtable th { color:#64748B; text-align:left; padding:8px 10px; border-bottom:1px solid #E2E8F0; font-weight:600; white-space:nowrap; }
    .dtable td { padding:8px 10px; border-bottom:1px solid #E9EEF5; color:#475569; white-space:nowrap; }
    .dtable tr:hover td { background:#F8FAFC; }
    .bad td { background:#FEF2F2 !important; }
    .bad td:first-child { border-left:3px solid #DC2626; }

    /* 规则卡 */
    .rule { display:flex; align-items:center; gap:14px; background:#FFFFFF; border:1px solid #E2E8F0;
            border-radius:12px; padding:13px 18px; margin:8px 0; }
    .rule .rid { font-family:monospace; color:#1D4ED8; font-weight:700; font-size:13px; width:44px; flex-shrink:0; }
    .rule .rname { color:#0F172A; font-weight:600; font-size:14px; width:150px; flex-shrink:0; }
    .rule .rtype { padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700; width:64px; text-align:center; flex-shrink:0; }
    .rt-完整性 { background:#FFFBEB; color:#D97706; }
    .rt-一致性 { background:#FEF2F2; color:#1D4ED8; }
    .rt-逻辑性 { background:#EFF6FF; color:#2563EB; }
    .rt-合规性 { background:#F5F3FF; color:#7C3AED; }
    .rule .rparam { color:#64748B; font-size:12.5px; font-family:monospace; flex:1; }
    .rule .ron { color:#16A34A; font-size:12px; font-weight:700; flex-shrink:0; }
    .rule .roff { color:#94A3B8; font-size:12px; flex-shrink:0; }

    /* 异常告警卡 */
    .issue { background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #DC2626;
             border-radius:10px; padding:12px 16px; margin:8px 0; }
    .issue .top { display:flex; align-items:center; gap:10px; margin-bottom:4px; }
    .issue .plan { color:#0F172A; font-weight:700; font-size:13.5px; font-family:monospace; }
    .issue .rbadge { padding:2px 10px; border-radius:10px; background:#FEF2F2; color:#1D4ED8;
                     font-size:11.5px; font-weight:700; font-family:monospace; }
    .issue .desc { color:#475569; font-size:13px; }

    .verdict { border-radius:12px; padding:16px 20px; margin:14px 0; }
    .verdict.fail { background:#FEF2F2; border:1px solid #BFDBFE; }
    .verdict.pass { background:#F0FDF4; border:1px solid #BBF7D0; }
    .verdict .vt { font-size:16px; font-weight:800; }
    .verdict.fail .vt { color:#2563EB; }
    .verdict.pass .vt { color:#16A34A; }
    .verdict .vd { color:#64748B; font-size:13px; margin-top:4px; }

    .big-num { font-size:40px; font-weight:800; line-height:1.1; }
    .callout { background:#F8FAFC; border-left:3px solid #DC2626; border-radius:8px;
               padding:12px 16px; color:#475569; font-size:13.5px; line-height:1.7; margin-top:14px; }
    .section-t { color:#0F172A; font-weight:700; font-size:15px; margin:8px 0 10px 0; }
    .note { color:#64748B; font-size:12px; margin-top:14px; }
    /* 一次通过率条 */
    .prow { display:flex; align-items:center; gap:12px; margin:10px 0; }
    .prow .pname { width:110px; color:#64748B; font-size:13px; text-align:right; flex-shrink:0; }
    .prow .pbar-wrap { flex:1; height:24px; background:#E9EEF5; border-radius:8px; overflow:hidden; }
    .prow .pbar { height:100%; background:linear-gradient(90deg,#2563EB,#2563EB); border-radius:8px; }
    .prow .pval { width:60px; color:#1E293B; font-size:13px; font-weight:700; flex-shrink:0; }
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
    ("🎯 营销", "pages/4_精准营销平台.py", False),
    ("🏦 报送", "", True),
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
  <div class="eyebrow">REGULATORY REPORTING RULE ENGINE</div>
  <h1><span class="h1chip" style="background:linear-gradient(135deg,#C98F68,#D9A883)">🏦</span>监管报送规则引擎</h1>
  <div class="sub">信托全流程监管报送：登记数据 → 规则校验 → 异常闭环 → 报送中信登 ｜ 政策更新 = 配置变更，不是改代码</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="callout">💡 <b>演示说明：</b>本页面基于真实项目经验还原——校验规则体系与业务流程源自实际工作中的方案，数据已脱敏，交互原型由本人独立设计并借助 AI 编程工具实现。</div>', unsafe_allow_html=True)

# ============================================================
# 状态与数据
# ============================================================
ss = st.session_state
ss.setdefault("rules", [
    {"规则ID": "R01", "名称": "关键字段完整性", "类型": "完整性", "参数": "必填:计划编号,名称,设立日,募集金额,投资者数", "启用": True},
    {"规则ID": "R02", "名称": "金额勾稽一致", "类型": "一致性", "参数": "募集金额 ≈ 份额 × 单位净值 (容差0.5%)", "启用": True},
    {"规则ID": "R03", "名称": "日期顺序合法", "类型": "逻辑性", "参数": "备案日 ≤ 设立日 ≤ 起息日", "启用": True},
    {"规则ID": "R04", "名称": "投资者人数上限", "类型": "合规性", "参数": "单一计划投资者数 ≤ 200", "启用": True},
    {"规则ID": "R05", "名称": "状态与日期一致", "类型": "逻辑性", "参数": "状态=终止 → 必有终止日", "启用": True},
])
ss.setdefault("rule_version", "v1.0")

RECORDS = [
    {"计划编号": "XT2026-001", "名称": "稳健1号集合资金信托", "备案日": "2026-08-01", "设立日": "2026-08-05", "起息日": "2026-08-06", "终止日": "", "状态": "存续", "份额(万份)": 20000, "单位净值": 1.02, "募集金额(万)": 20600, "投资者数": 156},
    {"计划编号": "XT2026-002", "名称": "汇金2号单一资金信托", "备案日": "2026-08-12", "设立日": "2026-08-20", "起息日": "2026-08-21", "终止日": "", "状态": "存续", "份额(万份)": 50000, "单位净值": 1.00, "募集金额(万)": 50200, "投资者数": 1},
    {"计划编号": "XT2026-003", "名称": "玉兰3号集合资金信托", "备案日": "2026-09-01", "设立日": "2026-08-28", "起息日": "2026-08-29", "终止日": "", "状态": "存续", "份额(万份)": 12000, "单位净值": 1.01, "募集金额(万)": 12000, "投资者数": 230},
    {"计划编号": "XT2025-118", "名称": "聚力11号集合资金信托", "备案日": "2025-11-10", "设立日": "2025-11-15", "起息日": "2025-11-16", "终止日": "2026-09-30", "状态": "终止", "份额(万份)": 8000, "单位净值": 1.03, "募集金额(万)": 8240, "投资者数": 98},
    {"计划编号": "XT2026-004", "名称": "晨曦5号家族信托", "备案日": "2026-09-15", "设立日": "2026-09-20", "起息日": "", "终止日": "", "状态": "存续", "份额(万份)": 3000, "单位净值": 1.00, "募集金额(万)": 3000, "投资者数": 3},
]

def validate(records, rules):
    issues = []
    enabled = {r["规则ID"]: r for r in rules if r["启用"]}
    for rec in records:
        rid = rec["计划编号"]
        if "R01" in enabled:
            for f in ["计划编号", "名称", "设立日", "募集金额(万)", "投资者数"]:
                if rec.get(f) in ("", None):
                    issues.append((rid, "R01", f"关键字段缺失：{f}"))
        if "R02" in enabled:
            expect = rec["份额(万份)"] * rec["单位净值"]
            if abs(expect - rec["募集金额(万)"]) / max(expect, 1) > 0.005:
                issues.append((rid, "R02", f"勾稽不符：份额×净值={expect:,.0f}万 ≠ 募集 {rec['募集金额(万)']:,.0f}万"))
        if "R03" in enabled:
            if rec["备案日"] > rec["设立日"]:
                issues.append((rid, "R03", f"备案日 {rec['备案日']} 晚于设立日 {rec['设立日']}"))
            if rec["起息日"] and rec["设立日"] > rec["起息日"]:
                issues.append((rid, "R03", "设立日晚于起息日"))
        if "R04" in enabled:
            try:
                limit = int(enabled["R04"]["参数"].split("≤")[-1].strip())
            except Exception:
                limit = 200
            if rec["投资者数"] > limit:
                issues.append((rid, "R04", f"投资者数 {rec['投资者数']} 超上限 {limit}"))
        if "R05" in enabled:
            if rec["状态"] == "终止" and not rec["终止日"]:
                issues.append((rid, "R05", "状态为终止但无终止日期"))
        if "R06" in enabled:
            if rec["状态"] == "存续" and not rec["起息日"]:
                issues.append((rid, "R06", "存续计划未起息，报送前需补齐"))
    return issues

issues = validate(RECORDS, ss["rules"])
bad_plans = {i[0] for i in issues}

# ============================================================
# Tabs
# ============================================================
tab1, tab2, tab3 = st.tabs(["报送校验台", "规则配置中心", "报送看板"])

# ---------------- Tab 1：校验台 ----------------
with tab1:
    st.markdown(
        """<div class="pipe">
          <div class="pstep">📥 登记数据</div><div class="parrow">→</div>
          <div class="pstep hl">⚙️ 规则引擎（本地预校验）</div><div class="parrow">→</div>
          <div class="pstep">🧾 异常清单</div><div class="parrow">→</div>
          <div class="pstep">🔧 修复闭环</div><div class="parrow">→</div>
          <div class="pstep">📤 报送中信登</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-t">在管信托计划（{} 只，异常 {} 只）</div>'.format(len(RECORDS), len(bad_plans)), unsafe_allow_html=True)
    rows_html = ""
    for rec in RECORDS:
        cls = ' class="bad"' if rec["计划编号"] in bad_plans else ""
        rows_html += (
            f'<tr{cls}><td>{rec["计划编号"]}</td><td>{rec["名称"]}</td><td>{rec["状态"]}</td>'
            f'<td>{rec["募集金额(万)"]:,.0f}</td><td>{rec["投资者数"]}</td>'
            f'<td>{rec["设立日"] or "—"}</td><td>{rec["起息日"] or "—"}</td></tr>'
        )
    st.markdown(
        """<table class="dtable">
        <tr><th>计划编号</th><th>名称</th><th>状态</th><th>募集金额(万)</th><th>投资者数</th><th>设立日</th><th>起息日</th></tr>
        """ + rows_html + "</table>",
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="verdict {"fail" if issues else "pass"}">'
                f'<div class="vt">{"❌ 发现 " + str(len(issues)) + " 条异常（" + str(len(bad_plans)) + " 只计划），修复完成前不可报送" if issues else "✅ 全部通过，可生成报送报文"}</div>'
                f'<div class="vd">规则版本 {ss["rule_version"]} ｜ 校验在报送中信登之前本地完成，替代原有人工逐条核对</div></div>',
                unsafe_allow_html=True)

    for plan, rule, desc in issues:
        st.markdown(
            f"""<div class="issue"><div class="top">
              <div class="plan">{plan}</div><div class="rbadge">{rule}</div>
            </div><div class="desc">{desc}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("""<div class="callout"><b>异常处理与问题跟踪机制（合规流程闭环）：</b><br>
    数据缺失类 → 打回客户经理补录，超期自动升级提醒 ｜ 勾稽不一致类 → 联动估值/账务系统核对口径差异 ｜
    逻辑/合规类 → 法律合规部出具处理意见后重校验 ｜ 系统无法处理 → 问题清单 + 业务/合规/技术三方例会</div>""",
    unsafe_allow_html=True)

# ---------------- Tab 2：规则配置中心 ----------------
with tab2:
    c_head, c_ver = st.columns([3, 1])
    with c_head:
        st.markdown('<div class="section-t" style="margin-top:4px;">规则库 · 政策更新以配置生效</div>', unsafe_allow_html=True)
    with c_ver:
        st.markdown(f'<div style="text-align:right;margin-top:8px;"><span class="pill run" style="font-size:13px;">规则版本 {ss["rule_version"]}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="callout" style="margin-top:0;">监管政策高频更新，<b>平台不做填报工具，做规则引擎</b>：'
                '把监管条文拆解为数据指标与自动化校验规则，政策变化只需增改配置、版本号升级，无需研发排期。</div>',
                unsafe_allow_html=True)

    for r in ss["rules"]:
        st.markdown(
            f"""<div class="rule">
              <div class="rid">{r["规则ID"]}</div>
              <div class="rname">{r["名称"]}</div>
              <div class="rtype rt-{r["类型"]}">{r["类型"]}</div>
              <div class="rparam">{r["参数"]}</div>
              <div class="{'ron' if r["启用"] else 'roff'}">{'● 启用' if r["启用"] else '○ 停用'}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-t" style="margin-top:22px;">🧪 模拟一次政策更新</div>', unsafe_allow_html=True)
    st.markdown('新规示例：「单一集合计划投资者数上限由 200 调整为 150」，并新增「存续计划必须已起息」。保存后回「报送校验台」重新校验，观察异常数量变化。', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c1:
        new_limit = st.number_input("R04 投资者数上限", 50, 500, 200, step=10)
    with c2:
        add_r06 = st.checkbox("新增 R06：存续计划必须已起息")
    with c3:
        st.write("")
        st.write("")
        do_save = st.button("💾 保存规则变更", type="primary", use_container_width=True)

    if do_save:
        for r in ss["rules"]:
            if r["规则ID"] == "R04":
                r["参数"] = f"单一计划投资者数 ≤ {new_limit}"
        if add_r06 and not any(r["规则ID"] == "R06" for r in ss["rules"]):
            ss["rules"].append({"规则ID": "R06", "名称": "存续计划已起息", "类型": "逻辑性", "参数": "状态=存续 → 起息日非空", "启用": True})
        parts = ss["rule_version"].split(".")
        ss["rule_version"] = f"v1.{int(parts[1]) + 1}"
        new_issues = validate(RECORDS, ss["rules"])
        st.markdown(
            f"""<div class="verdict fail" style="margin-top:14px;">
              <div class="vt">📌 规则已生效 · 版本升级至 {ss["rule_version"]}</div>
              <div class="vd">R04 上限 = {new_limit} ｜ R06 = {'已新增' if add_r06 else '未新增'} ｜ 重新校验后当前异常 <b style="color:#2563EB;">{len(new_issues)} 条</b>（政策更新前为 {len(issues)} 条）——去「报送校验台」看明细</div>
            </div>""",
            unsafe_allow_html=True,
        )

# ---------------- Tab 3：报送看板 ----------------
with tab3:
    n_rules = sum(1 for r in ss["rules"] if r["启用"])
    st.markdown(
        f"""<div class="kpi-row">
          <div class="kpi"><div class="label">在管信托计划</div><div class="value">{len(RECORDS)}<em>只</em></div></div>
          <div class="kpi"><div class="label">启用规则</div><div class="value">{n_rules}<em>条</em></div></div>
          <div class="kpi warn"><div class="label">当前待处理异常</div><div class="value">{len(issues)}<em>条</em></div></div>
          <div class="kpi ok"><div class="label">中信登接口</div><div class="value">已对接</div></div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-t" style="margin-top:22px;">各类业务一次通过率（本期）</div>', unsafe_allow_html=True)
    biz = [("初始登记", 12, 0.83), ("变更登记", 8, 0.75), ("事前报告", 5, 0.90), ("终止登记", 3, 0.67)]
    st.markdown("".join(
        f'<div class="prow"><div class="pname">{n}（{c} 笔）</div>'
        f'<div class="pbar-wrap"><div class="pbar" style="width:{p*100:.0f}%"></div></div>'
        f'<div class="pval">{p*100:.0f}%</div></div>'
        for n, c, p in biz
    ), unsafe_allow_html=True)

    st.markdown('<div class="callout"><b>一次通过率是运营重点：</b>终止登记通过率偏低（67%）的主因是终止日期回填不及时——'
                '已推动业务流程改造：终止审批通过即自动回写终止日，无需人工补录。</div>', unsafe_allow_html=True)
    st.caption(f"全流程覆盖：预登记 → 初始登记 → 事前报告 → 终止登记（含补充/重新登记场景） ｜ 规则版本 {ss['rule_version']}")

st.markdown('<div class="note">数据为演示用模拟数据，业务口径与真实项目一致 ｜ 平台：Streamlit ｜ 无外部依赖</div>', unsafe_allow_html=True)
