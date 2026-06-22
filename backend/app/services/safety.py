BLOCKED_TERMS = ["攻击", "骚扰", "歧视", "违法", "人肉", "真实个人信息"]


def is_safe_user_intervention(content: str) -> bool:
    normalized = content.strip().lower()
    if not normalized:
        return False
    return not any(term in normalized for term in BLOCKED_TERMS)
