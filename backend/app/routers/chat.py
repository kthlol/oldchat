import os, uuid, json, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.stt_service import transcribe_file
from app.services.llm_service import chat_with_llm
from app.services.tts_service import synthesize_to_mp3
from app.services.musetalk_service import generate_talking_head

router = APIRouter()
TMP_DIR = os.path.join(os.path.dirname(__file__), "../../tmp")
os.makedirs(TMP_DIR, exist_ok=True)

@router.websocket("/ws/chat")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    chunks = []

    try:
        while True:
            data = await ws.receive()
            if data.get("type") == "websocket.receive":
                if "bytes" in data:
                    chunks.append(data["bytes"])
                elif "text" in data:
                    # 控制消息
                    ctrl = json.loads(data["text"])
                    msg_type = ctrl.get("type")
                    role = ctrl.get("role", "socrates")
                    if msg_type == "END":
                        try:
                            # 音频工作流：保存 + FunASR + Qwen + Edge-TTS + MuseTalk
                            fname = os.path.join(TMP_DIR, f"{session_id}.webm")
                            with open(fname, "wb") as f:
                                for c in chunks:
                                    f.write(c)
                            
                            # 1. FunASR 语音识别
                            stt_text = await transcribe_file(fname)
                            await ws.send_text(json.dumps({"type":"stt","text": stt_text}))
                            
                            # 2. Qwen 大语言模型对话
                            reply = await chat_with_llm(stt_text, role)
                            await ws.send_text(json.dumps({"type":"reply","text": reply}))
                            
                            # 3. Edge-TTS 文本转语音
                            mp3_path = os.path.join(TMP_DIR, f"{session_id}.mp3")
                            await synthesize_to_mp3(reply, mp3_path)
                            
                            # 4. MuseTalk 生成说话人视频（暂时跳过）
                            # video_path = await generate_talking_head(mp3_path)
                            
                            # 发送音频文件
                            with open(mp3_path, "rb") as f:
                                await ws.send_bytes(f.read())
                            
                            # 暂时不发送视频文件
                            # if video_path and os.path.exists(video_path):
                            #     with open(video_path, "rb") as f:
                            #         await ws.send_bytes(f.read())
                            #     await ws.send_text(json.dumps({"type":"video","format":"mp4"}))
                            #     os.remove(video_path)
                            
                            # 清理临时文件
                            os.remove(fname)
                            os.remove(mp3_path)
                            
                        except Exception as e:
                            await ws.send_text(json.dumps({"type":"error","message": str(e)}))
                        finally:
                            chunks = []
                    elif msg_type == "TEXT":
                        try:
                            # 纯文本工作流：LLM + 可选 TTS
                            text = ctrl.get("text", "")
                            reply = await chat_with_llm(text, role)
                            await ws.send_text(json.dumps({"type":"reply","text": reply}))
                            mp3_path = os.path.join(TMP_DIR, f"{session_id}.mp3")
                            await synthesize_to_mp3(reply, mp3_path)
                            with open(mp3_path, "rb") as f:
                                await ws.send_bytes(f.read())
                            os.remove(mp3_path)
                        except Exception as e:
                            await ws.send_text(json.dumps({"type":"error","message": str(e)}))
            elif data.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        print("client disconnected")
