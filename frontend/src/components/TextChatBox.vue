<template>
  <div class="text-chat-box">
    <div class="input-container">
      <input 
        v-model="text" 
        :placeholder="store.isVoiceMode ? '点击麦克风开始语音输入' : '输入文本与当前角色对话'" 
        class="text-input" 
        @keydown.enter.prevent="send" 
      />
      <div class="input-actions">
        <!-- 听写模式按钮 - 始终显示 -->
        <button 
          class="dictate-btn" 
          @click="startDictate"
          title="听写模式"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/>
          </svg>
        </button>
        
        <!-- 语音输入按钮 - 始终显示 -->
        <button 
          class="voice-input-btn" 
          :class="{ recording: isRecording }"
          @click="toggleVoiceInput"
          :title="isRecording ? '停止录音' : '语音输入'"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/>
          </svg>
        </button>
        
        <!-- 发送按钮 - 有文字时显示 -->
        <button 
          v-if="text.trim()" 
          class="send-btn" 
          @click="send" 
          :disabled="store.isSending"
          title="发送消息"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
    <!-- 暂时隐藏上传功能 -->
    <!-- <input type="file" accept="audio/*" @change="onUpload" class="upload-btn" title="上传音频文件" /> -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '../store/session'
import { createWs } from '../api/websocket'

const store = useSessionStore()
const text = ref('')
const isRecording = ref(false)
const recognition = ref<any>(null)
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

function startDictate() {
  // 启动听写功能 - 语音转文字到输入框
  console.log('启动听写模式')
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.lang = 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = false
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      text.value = transcript
    }
    
    recognition.onerror = (event: any) => {
      console.error('语音识别错误:', event.error)
    }
    
    recognition.start()
  } else {
    alert('您的浏览器不支持语音识别功能')
  }
}

function toggleVoiceInput() {
  if (isRecording.value) {
    stopVoiceInput()
  } else {
    startVoiceInput()
  }
}

function startVoiceInput() {
  console.log('开始语音输入')
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    
    recognition.value.lang = 'zh-CN'
    recognition.value.continuous = false
    recognition.value.interimResults = true
    
    recognition.value.onstart = () => {
      isRecording.value = true
      console.log('语音识别开始')
    }
    
    recognition.value.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      text.value = transcript
      
      // 如果是最终结果，自动发送
      if (event.results[0].isFinal) {
        console.log('语音识别完成:', transcript)
        setTimeout(() => {
          send()
        }, 500) // 延迟500ms发送，让用户看到识别结果
      }
    }
    
    recognition.value.onerror = (event: any) => {
      console.error('语音识别错误:', event.error)
      isRecording.value = false
      if (event.error === 'no-speech') {
        console.log('没有检测到语音')
      }
    }
    
    recognition.value.onend = () => {
      isRecording.value = false
      console.log('语音识别结束')
    }
    
    recognition.value.start()
  } else {
    alert('您的浏览器不支持语音识别功能')
  }
}

function stopVoiceInput() {
  console.log('停止语音输入')
  if (recognition.value) {
    recognition.value.stop()
    isRecording.value = false
  }
}

function startVoiceMode() {
  // 启动语音模式 - 切换到主页面的语音功能
  console.log('启动语音模式')
  store.setVoiceMode(true)
  // 这里可以触发主页面麦克风按钮的激活状态
}

async function onUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  ensureWs()
  store.setSending(true)
  const id = crypto.randomUUID()
  store.pushMessage({ id, userText: `[上传音频: ${file.name}]`, replyText: '' })
  const ab = await file.arrayBuffer()
  ws!.send(ab)
  ws!.send(JSON.stringify({ type: 'END', role: store.role }))
}
</script>

<style scoped>
.text-chat-box {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 0;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  max-width: 800px;
  margin: 0 auto;
}
.input-container {
  display: flex;
  align-items: center;
  flex: 1;
  position: relative;
}
.text-input {
  flex: 1;
  padding: 14px 20px;
  padding-right: 120px; /* 为右侧按钮留出空间 */
  border: 1px solid #d1d5db;
  border-radius: 24px;
  background: #ffffff;
  color: #333333;
  font-size: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  min-height: 48px;
}
.text-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.input-actions {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 8px;
  align-items: center;
}

.dictate-btn, .voice-input-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #6b7280;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.dictate-btn:hover, .voice-input-btn:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.voice-input-btn {
  background: #8b5cf6;
  border-color: #8b5cf6;
  color: #fff;
}

.voice-input-btn:hover {
  background: #7c3aed;
  border-color: #7c3aed;
}

.voice-input-btn.recording {
  background: #ef4444;
  border-color: #ef4444;
  animation: pulse 1.5s infinite;
}

.voice-input-btn.recording:hover {
  background: #dc2626;
  border-color: #dc2626;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
.send-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #3b82f6;
  background: #3b82f6;
  color: #fff;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.send-btn:hover:not(:disabled) {
  background: #2563eb;
}
.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.upload-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #6b7280;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.upload-btn:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}
</style>
