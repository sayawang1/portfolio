import streamlit as st

# 1. 页面基本设置
st.set_page_config(
    page_title="Saya | 产品经理作品集",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 自定义 CSS
st.markdown("""
<style>
/* 隐藏 Streamlit 默认的侧边栏导航 */
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] { display: none; }

/* 页面整体背景 */
.stApp {
    background-color: #0B0E11;
    color: #E2E8F0;
}

/* 个人名片卡片 */
.profile-card {
    background-color: #15181E;
    border-radius: 16px;
    padding: 32px 24px;
    border: 1px solid #2A2F3A;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    margin-bottom: 24px;
    text-align: center;
}

/* 专属头像（渐变圆 + 字母S） */
.profile-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF4B4B 0%, #6B46C1 100%);
    color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 36px;
    font-weight: 800;
    margin: 0 auto 20px auto;
    box-shadow: 0 4px 10px rgba(255, 75, 75, 0.3);
}

/* 字体与标签 */
.profile-name {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: 1px;
}
.tag {
    display: inline-block;
    background-color: #2A2F3A;
    color: #E2E8F0;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    margin: 4px 4px;
    border: 1px solid #3A404D;
}

/* 顶部 Timeline */
.timeline-card {
    background-color: #15181E;
    border-radius: 16px;
    padding: 16px 24px;
    border: 1px solid #2A2F3A;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.timeline-title { color: #A0A6B1; font-size: 14px; letter-spacing: 1px; font-weight: 600; }

/* 项目卡片 */
.project-card {
    background-color: #15181E;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #2A2F3A;
    margin-bottom: 24px;
}
.project-card:hover {
    border-color: #FF4B4B;
    transition: border-color 0.3s;
}
.project-title { color: #FFFFFF; font-size: 22px; font-weight: 600; margin-bottom: 12px; }
.project-desc { color: #A0A6B1; font-size: 15px; line-height: 1.6; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# 3. 布局：左侧个人信息，右侧内容区
col1, col2 = st.columns([1, 2.2], gap="large")

# ================= 左侧：个人名片 =================
with col1:
    st.markdown("""
    <div class="profile-card">
        <div class="profile-avatar">S</div>
        <div class="profile-name">saya</div>
        <div style="margin-top: 16px;">
            <span class="tag">产品经理</span>
            <span class="tag">AI 产品</span>
            <span class="tag">推荐系统</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= 右侧：项目与列表 =================
with col2:
    # 顶部 Timeline 状态栏
    st.markdown("""
    <div class="timeline-card">
        <div>
            <div class="timeline-title">TIMELINE</div>
            <div style="font-size: 18px; font-weight: 600; color: #FFF; margin-top: 4px;">最近记录</div>
        </div>
        <div style="text-align: right;">
            <span class="tag">Beta</span>
            <span style="color: #A0A6B1; font-size: 13px;">2026/05/19 更新</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 核心项目卡片：推荐系统
    st.markdown("""
    <div class="project-card">
        <div class="project-title">🎯 推荐策略配置平台</div>
        <div class="project-desc">
            <b>业务背景：</b>金融推荐系统需要同时满足运营可控、算法个性化和系统兜底。<br>
            <b>核心设计：</b>三级策略优先级（人工强干预 > 算法推荐 > 全量兜底）。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 跳转按钮
    if st.button("🚀 进入推荐系统 Demo", use_container_width=True, type="primary"):
        st.switch_page("pages/1_推荐系统Demo.py")

    # 预留占位卡片
    st.markdown("""
    <div class="project-card" style="opacity: 0.6;">
        <div class="project-title">📚 更多项目筹备中...</div>
        <div class="project-desc">这里将来可以展示你的其他产品项目。</div>
    </div>
    """, unsafe_allow_html=True)
