import os
import asyncio
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

ROLE_TEMPLATES = {
    "socrates": "You are Socrates, ask leading questions.",
    "storyteller": "You are a fantasy storyteller.",
    "interviewer": "You are a professional interviewer."
}

async def chat_with_llm(user_text: str, role: str) -> str:
    system = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["socrates"])
    loop = asyncio.get_event_loop()
    def _call():
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system},{"role":"user","content":user_text}],
            max_tokens=300,
            request_timeout=30
        )
        return resp.choices[0].message.content.strip()
    return await loop.run_in_executor(None, _call)
