import os
import asyncio

# 模拟 Qwen 服务 - 使用本地回复
ROLE_TEMPLATES = {
    "socrates": "你是苏格拉底，善于通过提问引导思考，用简洁而深刻的问题启发对方。",
    "storyteller": "你是一个富有想象力的故事叙述者，能够创造引人入胜的故事。",
    "interviewer": "你是一个专业的面试官，善于提出有深度的问题。",
    "harry_potter": "你是哈利波特，勇敢的魔法师，来自霍格沃茨，用魔法世界的视角回答问题。",
    "sherlock": "你是夏洛克·福尔摩斯，天才侦探，善于逻辑推理和观察细节。",
    "einstein": "你是爱因斯坦，伟大的物理学家，用科学思维和哲学智慧回答问题。"
}

async def chat_with_llm(user_text: str, role: str) -> str:
    """模拟 Qwen 大语言模型对话"""
    loop = asyncio.get_event_loop()
    
    def _call():
        # 模拟AI回复
        role_responses = {
            "socrates": f"有趣的问题。让我问你：{user_text} 这个问题背后，你真正想了解的是什么？",
            "storyteller": f"让我为你讲一个故事。从前有一个勇敢的冒险者，他听到了'{user_text}'，于是踏上了寻找答案的旅程...",
            "interviewer": f"这是一个很好的问题。基于你提到的'{user_text}'，我想进一步了解你的想法。",
            "harry_potter": f"哇！关于'{user_text}'，这让我想起了在霍格沃茨的时光。你知道吗，魔法世界中有很多类似的奇妙现象！",
            "sherlock": f"从你提到的'{user_text}'中，我观察到几个关键细节。让我分析一下这个情况...",
            "einstein": f"关于'{user_text}'，这让我想起了相对论。你知道吗，时间和空间的关系比我们想象的要复杂得多。"
        }
        
        return role_responses.get(role, f"我理解你说的'{user_text}'。这是一个很有趣的话题，让我们继续探讨吧。")
    
    return await loop.run_in_executor(None, _call)