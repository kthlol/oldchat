# 简单内存 session 管理
sessions = {}

def get_session(session_id: str):
    return sessions.get(session_id, {"history":[]})

def update_session(session_id: str, user_text: str, bot_text: str):
    s = sessions.setdefault(session_id, {"history":[]})
    s["history"].append({"user":user_text,"bot":bot_text})
