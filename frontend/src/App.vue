<script setup>
import ChatPanel from './components/ChatPanel.vue'
import RoleSelector from './components/RoleSelector.vue'
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="container header-row">
        <div class="brand">
          <h1 class="title">AI 角色语音对话</h1>
          <p class="subtitle">选择角色 · 语音/文本对话 · 听取合成语音</p>
        </div>
        <div class="header-role"><RoleSelector /></div>
      </div>
    </header>

    <main class="main container">
      <ChatPanel />
    </main>
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; background: #0a0f1e; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 16px; }
.header-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.brand { display:flex; flex-direction:column; }
.header { position: sticky; top: 0; background: #0f172a; color:#e5e7eb; backdrop-filter: blur(6px); border-bottom: 1px solid #334155; }
.title { margin: 10px 0 2px; font-size: 20px; }
.subtitle { margin: 0 0 10px; color: #9ca3af; font-size: 13px; }
.main { padding: 16px 0 120px; }

@media (max-width: 860px) {
  .main { }
}
</style>
