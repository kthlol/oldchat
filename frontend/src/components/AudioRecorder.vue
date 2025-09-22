<template>
  <div class="recorder-wrap">
    <div class="composer">
      <button class="mic-btn" :class="{ active: store.isRecording }" :aria-pressed="store.isRecording"
              :title="store.isRecording ? '点击结束' : '点击开始说话'" @click="toggleRecord" :disabled="store.isSending">
        <svg v-if="!store.isRecording" viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
          <path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
          <path fill="currentColor" d="M6 6h12v12H6z"/>
        </svg>
      </button>
      <input class="upload" type="file" accept="audio/*" @change="onUpload" title="上传音频文件" />
    </div>
    <div v-if="store.error" class="error">{{ store.error }}</div>
  </div>
 </template>
 
 <script setup lang="ts">
 import { ref, onBeforeUnmount } from 'vue'
 import { createWs } from '../api/websocket'
 import { useSessionStore } from '../store/session'
 
 const store = useSessionStore()
 let mediaRecorder: MediaRecorder | null = null
 let ws: WebSocket | null = null
 const chunks: ArrayBuffer[] = []
 
 function ensureWs() {
   if (!ws || ws.readyState === WebSocket.CLOSED) {
     ws = createWs()
     ws.binaryType = 'arraybuffer'
     ws.onmessage = (ev) => {
       if (typeof ev.data === 'string') {
         try {
           const msg = JSON.parse(ev.data)
           if (msg.type === 'stt') {
             store.updateSTT(msg.text)
           } else if (msg.type === 'reply') {
             store.updateReply(msg.text)
             // 临时将文本写入最后一条
             const last = store.messages[store.messages.length-1]
             if (last) store.updateMessage(last.id, { replyText: msg.text })
           }
         } catch {}
       } else if (ev.data instanceof ArrayBuffer) {
         const blob = new Blob([ev.data], { type: 'audio/mpeg' })
         const url = URL.createObjectURL(blob)
         const last = store.messages[store.messages.length-1]
         if (last) store.updateMessage(last.id, { audioUrl: url })
         store.setSending(false)
       }
     }
     ws.onclose = () => { /* 断线后下次会重连 */ }
   }
 }
 
 async function start() {
   try {
     ensureWs()
     const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
     mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
     chunks.length = 0
     mediaRecorder.ondataavailable = async (e) => {
       const buf = await e.data.arrayBuffer()
       chunks.push(buf)
       if (ws && ws.readyState === WebSocket.OPEN) ws.send(buf)
     }
     mediaRecorder.onstart = () => store.setRecording(true)
     mediaRecorder.onstop = () => store.setRecording(false)
     mediaRecorder.start(250)
   } catch (e: any) {
     store.setError(e?.message || '无法访问麦克风')
   }
 }
 
 function stop() {
   mediaRecorder?.stop()
   // 通知后端合并并进入 STT/LLM/TTS，附带当前角色
   ensureWs()
   const id = crypto.randomUUID()
   store.pushMessage({ id, userText: store.sttText, replyText: '' })
   store.setSending(true)
   ws?.send(JSON.stringify({ type: 'END', role: store.role }))
 }

 function toggleRecord(){
   if (store.isRecording) {
     stop()
   } else {
     start()
   }
 }
 
 async function onUpload(e: Event) {
   const input = e.target as HTMLInputElement
   const file = input.files?.[0]
   if (!file) return
   ensureWs()
   store.setSending(true)
   const ab = await file.arrayBuffer()
   ws!.send(ab)
   ws!.send(JSON.stringify({ type: 'END', role: store.role }))
 }
 
 onBeforeUnmount(() => { if (ws && ws.readyState === WebSocket.OPEN) ws.close() })
 </script>

<style scoped>
.recorder-wrap { padding: 8px 0; }
.composer {
  display: flex;
  gap: 12px;
  align-items: center;
}
.mic-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 9999px;
  border: 1px solid #dcdcdc;
  background: #fff;
  color: #111;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all .15s ease;
}
.mic-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.mic-btn:active { transform: translateY(0); }
.mic-btn.active { background: #10a37f; color: #fff; border-color: #0e8e6e; }
.upload { font-size: 14px; }
.error { color: #c00; margin-top: 6px; }
</style>