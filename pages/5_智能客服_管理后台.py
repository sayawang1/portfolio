import streamlit as st
import pandas as pd

st.set_page_config(page_title="客服管理后台", layout="wide")
st.title("⚙️ 智能客服管理后台")

tab1, tab2, tab3 = st.tabs(["话术管理", "质检管理", "机器人设置"])

with tab1:
    st.subheader("知识库话术列表")
    df = pd.DataFrame({
        "问题": ["如何重置云服务器密码？", "云服务发票怎么开？"],
        "状态": ["上线", "下线"],
        "分类": ["ECS", "费用"]
    })
    st.data_editor(df)

with tab2:
    st.subheader("质检规则配置")
    st.write("支持规则导入、搜索、分类（关键因素/非关键因素）")
    st.code("当前规则：触发'投诉' -> 预警推送")
