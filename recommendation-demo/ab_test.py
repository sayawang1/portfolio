"""AB测试稳定分流"""
import hashlib

def assign_group(user_id, slot_id, ab_config):
    """同一个 user_id+slot_id 永远分到同一组，保证用户体验稳定"""
    if not ab_config or not ab_config.get("enabled"):
        return "default"
    key = f"{user_id}_{slot_id}"
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    ratio = ab_config.get("group_a_ratio", 50)
    if (hash_val % 100) < ratio:
        return "A"
    return "B"
