"""个人作品集 - 总览首页"""
import streamlit as st

st.set_page_config(page_title="我的产品作品集", page_icon="🧑‍💻", layout="wide")

st.title("🧑‍💻 产品经理作品集")
st.markdown("欢迎来到我的项目总览。这里展示了我在推荐系统、数据分析等领域的实践 Demo。")
st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🎛️ 推荐策略配置平台")
        st.markdown("**业务背景：** 金融推荐系统需要同时满足运营可控、算法个性化和系统兜底。")
        st.markdown("**核心设计：** 三级策略优先级（人工强干预 > 算法推荐 > 全量兜底）。")
        st.page_link("pages/1_推荐系统Demo.py", label="👉 进入推荐系统 Demo", icon="🚀")

with col2:
    with st.container(border=True):
        st.subheader("📊 更多项目筹备中...")
        st.button("敬请期待", disabled=True)
