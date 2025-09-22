<template>
  <div class="chat">
    <div v-for="m in store.messages" :key="m?.id || ('u-' + $index)" class="item user">
      <div class="bubble user">{{ m.userText }}</div>
    </div>
    <template v-for="m in store.messages" :key="(m?.id || 'x') + '-ai'">
      <div v-if="m && (m.replyText || m.audioUrl)" class="item ai">
        <div class="bubble ai">
          <div v-if="m.replyText">{{ m.replyText }}</div>
          <audio v-if="m.audioUrl" :src="m.audioUrl" controls style="margin-top:6px; width:100%"></audio>
        </div>
      </div>
    </template>
    <div v-if="store.isSending" class="loading">正在生成…</div>
  </div>
</template>

<script setup lang="ts">
import { useSessionStore } from '../store/session'
const store = useSessionStore()
</script>

<style scoped>
.chat { display:flex; flex-direction:column; gap:10px; padding-bottom:90px; max-width: 900px; }
.item { display:flex; }
.item.user { justify-content:flex-end; }
.item.ai { justify-content:flex-start; }
.bubble { max-width: 80%; padding:12px 14px; border-radius: 14px; line-height: 1.7; }
.bubble.user { background:#16a34a; color:#ffffff; border:1px solid #15803d; box-shadow: 0 8px 18px rgba(22,163,74,0.25); }
.bubble.ai { background:#111827; color:#e5e7eb; border:1px solid #374151; box-shadow: 0 8px 18px rgba(0,0,0,0.35); }
.loading { color:#a3a3a3; font-size: 13px; }
</style>
