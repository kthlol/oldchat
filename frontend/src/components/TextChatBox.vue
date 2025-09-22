<template>
  <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px;">
    <input v-model="text" placeholder="输入文本与当前角色对话" style="flex:1; padding:8px;" @keydown.enter.prevent="send" />
    <button @click="send" :disabled="!text.trim() || store.isSending">发送</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '../store/session'
import { createWs } from '../api/websocket'

const store = useSessionStore()
const text = ref('')
let ws: WebSocket | null = null

function ensureWs(){ if(!ws || ws.readyState===WebSocket.CLOSED){ ws = createWs(); ws.binaryType='arraybuffer'; ws.onmessage = onMessage } }

function onMessage(ev: MessageEvent){
  if (typeof ev.data === 'string') {
    try {
      const msg = JSON.parse(ev.data)
      if (msg.type === 'stt') store.updateSTT(msg.text)
      else if (msg.type === 'reply') {
        store.updateReply(msg.text)
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

function send(){
  const t = text.value.trim()
  if(!t) return
  ensureWs()
  const id = crypto.randomUUID()
  store.pushMessage({ id, userText: t, replyText: '' })
  store.setSending(true)
  ws!.send(JSON.stringify({ type: 'TEXT', role: store.role, text: t }))
  text.value = ''
}
</script>


