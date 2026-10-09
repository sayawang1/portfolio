import streamlit as st
import sys
from pathlib import Path

# 将项目根目录加入路径，保证能 import 到 intelligent_customer_service
sys.path.append(str(Path(__file__).parent.parent))
from intelligent_customer_service.services.rag_service import RAGService

st.set_page_config(page_title="智能客服", layout="wide")
st.title("🤖 智能客服 Demo")

# 侧边栏：机器人设置
st.sidebar.header("机器人设置")
threshold = st.sidebar.slider("相似度阈值", 0.0, 1.0, 0.3)

rag = RAGService()

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # 获取回答
    result = rag.answer(prompt, threshold=threshold)
    
    with st.chat_message("assistant"):
        st.write(result["answer"])
        if result["need_human"]:
            st.error("⚠️ 触发兜底策略：是否转人工？")
    
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
