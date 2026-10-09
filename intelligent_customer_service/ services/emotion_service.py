def detect_emotion(text: str):
    angry_words = ["投诉", "垃圾", "骗人", "曝光", "无语", "太差"]
    if any(word in text for word in angry_words):
        return {"label": "愤怒", "emoji": "😡", "score": 0.9}
    return {"label": "平静", "emoji": "🙂", "score": 0.5}
