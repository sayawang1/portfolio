from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FAQ:
    id: str
    question: str
    answer: str
    category: str
    status: str = "online"
    score: float = 0.0  # 检索匹配得分

@dataclass
class DialogTurn:
    speaker: str  # "customer" 或 "agent"
    text: str
    emotion: Optional[str] = None
    emotion_emoji: Optional[str] = None
    quality_warning: Optional[str] = None
    suggested_reply: Optional[str] = None
