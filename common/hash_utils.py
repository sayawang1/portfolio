"""哈希工具：分流与去重"""
import mmh3  # MurmurHash3，需要 pip install mmh3

def stable_hash(key: str, mod: int = 100) -> int:
    """稳定哈希，返回 0 到 mod-1 的整数"""
    return mmh3.hash(key, signed=False) % mod

def hit_ratio(user_id, slot_id, position_id, pct, salt=""):
    """按百分比稳定分流"""
    if pct >= 100:
        return True
    if pct <= 0:
        return False
    key = f"{user_id}_{slot_id}_{position_id}_{salt}"
    return stable_hash(key) < pct
