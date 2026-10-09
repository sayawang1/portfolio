import streamlit as st
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from intelligent_customer_service.services.emotion_service import detect_emotion
from intelligent_customer_service.services.quality_service import check_quality

st.set_page_config(page_title="智能坐席辅助", layout="wide")
st.title("🎧 智能坐席辅助 Demo")

# 模拟通话
dialogue = [
    ("customer", "你们这个服务太差了，我要投诉！"),
    ("agent", "您好，非常抱歉给您带来不好的体验，我先帮您核实。"),
    ("agent", "请您提供一下您的账号，我帮您核对信息。")
]

if st.button("▶️ 开始模拟通话"):
    placeholder = st.empty()
    for speaker, text in dialogue:
        with placeholder.container():
            # 情绪识别
            emo = detect_emotion(text)
            # 实时质检
            warnings = check_quality(text)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if speaker == "customer":
                    st.info(f"**客户** {emo['emoji']}：{text}")
                else:
                    st.success(f"**坐席** {emo['emoji']}：{text}")
            
            with col2:
                if warnings:
                    st.error("\n".join(warnings))
            
            time.sleep(1.5)
