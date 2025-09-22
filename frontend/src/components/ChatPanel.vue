<template>
  <section class="panel">
    <div class="topbar">
      <div class="role"><RoleSelector /></div>
    </div>
    <div class="center">
      <AudioRecorder />
    </div>
    <div class="bottom section">
      <h3 class="h">对话</h3>
      <ChatWindow />
      <Composer :inline="true" />
    </div>
  </section>
  
</template>

<script setup>
import RoleSelector from './RoleSelector.vue'
import AudioRecorder from './AudioRecorder.vue'
import ChatWindow from './ChatWindow.vue'
import Composer from './Composer.vue'
</script>

<style scoped>
.panel { display:flex; flex-direction:column; gap:16px; }
.topbar { display:flex; align-items:center; justify-content:flex-end; }
.role { min-width: 320px; }
.center { display:flex; justify-content:center; }
.bottom { background:#0b1223; border:1px solid #334155; border-radius:12px; padding:12px; }
.h { margin:0 0 10px; font-size:14px; color:#86efac; }

@media (max-width: 980px) {
  .role { min-width: auto; width:100%; }
}
</style>


