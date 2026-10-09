import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

class RAGService:
    def __init__(self):
        with open(DATA_DIR / "knowledge_base.json", "r", encoding="utf-8") as f:
            self.faqs = json.load(f).get("faqs", [])

    def answer(self, query: str, threshold: float = 0.3):
        # 极简版检索：简单计算字符重合率
        query_chars = set(query)
        best_match = None
        max_score = 0.0

        for faq in self.faqs:
            text = faq["question"] + faq["answer"]
            score = len(query_chars & set(text)) / len(query_chars) if query_chars else 0
            if score > max_score:
                max_score = score
                best_match = faq

        if max_score >= threshold and best_match:
            return {"answer": best_match["answer"], "need_human": False, "source": best_match}
        
        # 触发兜底策略
        return {"answer": "正在学习中，请转人工", "need_human": True, "source": None}
