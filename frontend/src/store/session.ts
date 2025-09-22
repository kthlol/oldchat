import { defineStore } from 'pinia'

export interface ChatMessage {
  id: string
  userText: string
  replyText: string
  audioUrl?: string
}

export const useSessionStore = defineStore('session', {
  state: () => ({
    sttText: '',
    replyText: '',
    role: 'socrates',
    messages: [] as ChatMessage[],
    isRecording: false,
    isSending: false,
    error: ''
  }),
  actions: {
    updateSTT(text: string) { this.sttText = text },
    updateReply(text: string) { this.replyText = text },
    setRole(r: string) { this.role = r },
    pushMessage(msg: ChatMessage) { this.messages.push(msg) },
    updateMessage(id: string, partial: Partial<ChatMessage>) {
      const idx = this.messages.findIndex(m => m.id === id)
      if (idx !== -1) this.messages[idx] = { ...this.messages[idx], ...partial }
    },
    setRecording(v: boolean){ this.isRecording = v },
    setSending(v: boolean){ this.isSending = v },
    setError(msg: string){ this.error = msg }
  }
})
