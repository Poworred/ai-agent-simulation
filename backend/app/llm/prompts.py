SYSTEM_PROMPT = """你是 AI 南大校园社会模拟系统中的结构化生成模块。
只生成虚构校园 Agent 的对话、反思和决策解释。
不要生成真实个人信息、攻击、骚扰、歧视、违法或不适合校园展示的内容。
输出必须符合调用方提供的 JSON schema。
"""


def dialogue_prompt(context: dict) -> str:
    return f"""请为两个校园 Agent 生成一次简短、有校园语境的对话。
上下文：{context}
要求：对话自然、短、具体；输出结构化 JSON。
"""


def reflection_prompt(context: dict) -> str:
    return f"""请为一个校园 Agent 生成一天结束后的反思。
上下文：{context}
要求：反思要引用当天事件，给出明天目标更新；输出结构化 JSON。
"""


def intervention_prompt(context: dict) -> str:
    return f"""请判断用户建议是否应影响 Agent 下一步计划。
上下文：{context}
要求：只在符合 Agent 目标、状态和安全边界时接受；输出结构化 JSON。
"""
