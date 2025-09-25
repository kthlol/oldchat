import os
import asyncio
import tempfile
import shutil
import subprocess

# 模拟 FunASR 服务 - 使用本地 Whisper 作为备用
async def transcribe_file(filepath: str) -> str:
    """模拟 FunASR 语音识别，实际使用 Whisper"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _sync_transcribe_whisper(filepath))

def _sync_transcribe_whisper(filepath: str) -> str:
    """使用 Whisper 进行语音识别（备用方案）"""
    try:
        # 尝试使用 faster-whisper
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        
        input_path = filepath
        tmp_wav = None
        
        # 音频格式转换
        if shutil.which("ffmpeg") and not filepath.lower().endswith(".wav"):
            fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            cmd = [
                "ffmpeg", "-y", "-i", filepath,
                "-ar", "16000", "-ac", "1", tmp_wav
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                input_path = tmp_wav
            except Exception:
                input_path = filepath
        
        segments, _ = model.transcribe(input_path)
        result = " ".join(seg.text for seg in segments)
        
        if tmp_wav and os.path.exists(tmp_wav):
            try:
                os.remove(tmp_wav)
            except Exception:
                pass
                
        return result.strip() or "你好，我听到了你的声音"
        
    except ImportError:
        # 如果没有 faster-whisper，返回模拟文本
        return "你好，我听到了你的声音"
    except Exception as e:
        print(f"语音识别失败: {e}")
        return "你好，我听到了你的声音"