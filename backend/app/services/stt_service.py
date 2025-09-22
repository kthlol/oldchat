from faster_whisper import WhisperModel
import asyncio

# 更轻量的模型，响应更快；如有 GPU 可改 device="cuda"
model = WhisperModel("base", device="cpu", compute_type="int8")

async def transcribe_file(filepath: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _sync_transcribe(filepath))

def _sync_transcribe(filepath: str) -> str:
    segments, _ = model.transcribe(filepath)
    return " ".join(seg.text for seg in segments)
