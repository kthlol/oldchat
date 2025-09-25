import edge_tts
import os
import asyncio

# Edge-TTS 配置
TTS_VOICE = os.environ.get("TTS_VOICE", "zh-CN-XiaoxiaoNeural")

async def synthesize_to_mp3(text: str, out_path: str):
    """使用 Edge-TTS 进行文本转语音"""
    try:
        communicate = edge_tts.Communicate(text, voice=TTS_VOICE)
        with open(out_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
    except Exception as e:
        print(f"TTS 合成失败: {e}")
        # 创建一个空的音频文件作为备用
        with open(out_path, "wb") as f:
            f.write(b"")