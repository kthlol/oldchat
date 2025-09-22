import edge_tts

async def synthesize_to_mp3(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    with open(out_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
