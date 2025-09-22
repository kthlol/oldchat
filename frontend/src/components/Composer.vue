<template>
  <div class="composer" :class="{ inline }">
    <div class="card">
      <input class="input" v-model="text" placeholder="给 {{ roleName }} 说点什么…（回车发送）" @keydown.enter.prevent="send" />
      <div class="actions">
        <button class="send" @click="send" :disabled="!canSend">发送</button>
        <button class="mic" :class="{ active: store.isRecording }" :title="store.isRecording ? '结束录音' : '开始说话'" @click="toggleRecord" :disabled="store.isSending">
          <svg v-if="!store.isRecording" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/></svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M6 6h12v12H6z"/></svg>
        </button>
      </div>
    </div>
  </div>
  <div v-if="store.error" class="error">{{ store.error }}</div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSessionStore } from '../store/session'
import { createWs } from '../api/websocket'

const props = defineProps<{ inline?: boolean }>()

const store = useSessionStore()
const text = ref('')
let ws: WebSocket | null = null
let mediaRecorder: MediaRecorder | null = null
const chunks: ArrayBuffer[] = []

const canSend = computed(() => !!text.value.trim() && !store.isSending)
const roleName = computed(() => store.role === 'socrates' ? '苏格拉底' : store.role === 'storyteller' ? '故事叙述者' : store.role === 'interviewer' ? '面试官' : store.role)

function ensureWsReady(): Promise<void> {
  return new Promise((resolve) => {
    const resolveWhenOpen = () => resolve()
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      ws = createWs()
      ws.binaryType = 'arraybuffer'
      ws.addEventListener('open', resolveWhenOpen, { once: true })
      ws.onmessage = (ev) => {
      if (typeof ev.data === 'string') {
        try {
          const msg = JSON.parse(ev.data)
          if (msg.type === 'stt') store.updateSTT(msg.text)
          else if (msg.type === 'reply') {
            store.updateReply(msg.text)
            const last = store.messages[store.messages.length-1]
            if (last) store.updateMessage(last.id, { replyText: msg.text })
          } else if (msg.type === 'error') {
            store.setError(msg.message || '处理失败')
            store.setSending(false)
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
    } else if (ws.readyState === WebSocket.CONNECTING) {
      ws.addEventListener('open', resolveWhenOpen, { once: true })
    } else if (ws.readyState === WebSocket.OPEN) {
      resolve()
    }
  })
}

async function send(){
  const t = text.value.trim()
  if (!t || store.isSending) return
  await ensureWsReady()
  const id = crypto.randomUUID()
  store.pushMessage({ id, userText: t, replyText: '' })
  store.setSending(true)
  ws!.send(JSON.stringify({ type: 'TEXT', role: store.role, text: t }))
  text.value = ''
}

async function start(){
  try {
    await ensureWsReady()
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

function stop(){
  mediaRecorder?.stop()
  // 结束后发送控制消息，确保连接已就绪
  ensureWsReady().then(() => {
  const id = crypto.randomUUID()
  store.pushMessage({ id, userText: store.sttText, replyText: '' })
  store.setSending(true)
  ws?.send(JSON.stringify({ type: 'END', role: store.role }))
  })
}

function toggleRecord(){ store.isRecording ? stop() : start() }
</script>

<style scoped>
.composer { position: fixed; left: 0; right: 0; bottom: 0; padding: 16px 16px 20px; background: transparent; }
.composer.inline { position: static; padding: 0; }
.card { margin:0 auto; max-width:1100px; display:grid; grid-template-columns:1fr auto auto; gap:10px; padding:12px; background:#0b1223; border:1px solid #334155; border-radius:16px; box-shadow:0 10px 28px rgba(0,0,0,0.4); }
.composer.inline .card { max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
.input {
  flex:1; padding:12px 14px; border:1px solid #334155; background:#0f172a; color:#e5e7eb; border-radius:10px; font-size:14px;
}
.actions { display: flex; gap: 8px; align-items: center; }
.send {
  padding:0 14px; border:1px solid #16a34a; background:#16a34a; color:#fff; border-radius:10px; height:42px;
}
.mic {
  width:44px; height:42px; border-radius:9999px; border:1px solid #334155; background:#0f172a; color:#e5e7eb;
}
.mic.active { background:#16a34a; color:#fff; border-color:#15803d; }
.error { color: #c00; margin: 6px auto; max-width: 900px; }
</style>


