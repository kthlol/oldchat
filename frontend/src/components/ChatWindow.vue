<template>
  <div class="chat">
    <div v-for="(m, index) in store.messages" :key="m?.id || ('u-' + index)" class="item user">
      <div class="bubble user">{{ m.userText }}</div>
    </div>
    <template v-for="m in store.messages" :key="(m?.id || 'x') + '-ai'">
      <div v-if="m && (m.replyText || m.audioUrl || m.videoUrl)" class="item ai">
        <div class="bubble ai">
          <div v-if="m.replyText">{{ m.replyText }}</div>
          <div v-if="m.videoUrl" class="video-content">
            <video :src="m.videoUrl" controls autoplay muted class="talking-head-video">
              您的浏览器不支持视频播放
            </video>
          </div>
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
.chat { display:flex; flex-direction:column; gap:16px; padding-bottom:20px; max-width: 100%; }
.item { display:flex; }
.item.user { justify-content:flex-end; }
.item.ai { justify-content:flex-start; }
.bubble { max-width: 75%; padding:16px 20px; border-radius: 18px; line-height: 1.6; font-size: 15px; }
.bubble.user { background:#3b82f6; color:#ffffff; border:1px solid #3b82f6; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2); }
.bubble.ai { background:#f3f4f6; color:#333333; border:1px solid #e5e7eb; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.video-content {
  margin-top: 12px;
}

.talking-head-video {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
