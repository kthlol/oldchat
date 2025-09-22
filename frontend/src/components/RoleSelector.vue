<template>
  <div class="role-box">
    <button class="trigger avatar" @click="open = true" :title="mapName(store.role)">
      <img v-if="current && current.img" :src="current.img" alt="role" />
      <span class="label">{{ label }}</span>
    </button>
    <div v-if="open" class="overlay" @click.self="open = false">
      <div class="modal">
        <div class="modal-head">
          <input v-model="query" placeholder="搜索角色，如：哈利波特、苏格拉底" class="search" />
          <button class="close" @click="open = false">×</button>
        </div>
        <div class="grid">
          <button v-for="r in suggestionsEx" :key="r.key" class="item" @click="select(r.key)">
            <img v-if="r.img" :src="r.img" alt="avatar" />
            <span>{{ r.name }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSessionStore } from '../store/session'
const store = useSessionStore()

const query = ref('')
const open = ref(false)
const candidate = ['socrates','storyteller','interviewer']
const roleMeta: Record<string, { key: string, name: string, img?: string }> = {
  socrates: { key: 'socrates', name: '苏格拉底' },
  storyteller: { key: 'storyteller', name: '故事叙述者' },
  interviewer: { key: 'interviewer', name: '面试官' },
}
const suggestions = computed(() => {
  if (!query.value.trim()) return candidate
  const q = query.value.toLowerCase()
  return candidate.filter(c => mapName(c).toLowerCase().includes(q))
})

const suggestionsEx = computed(() => suggestions.value.map(k => ({ key: k, name: mapName(k), img: roleMeta[k]?.img })))
const current = computed(() => roleMeta[store.role])
const label = computed(() => {
  const name = mapName(store.role)
  const max = 14
  if (name.length <= max) return name
  const head = name.slice(0, Math.ceil((max - 1) / 2))
  const tail = name.slice(-Math.floor((max - 1) / 2))
  return head + '…' + tail
})

function mapName(key: string){
  return key === 'socrates' ? '苏格拉底' : key === 'storyteller' ? '故事叙述者' : key === 'interviewer' ? '面试官' : key
}

function select(r: string){ store.setRole(r); open.value = false }
</script>
 
<style scoped>
.role-box { display:flex; align-items:center; gap:8px; }
.trigger { border:1px solid #334155; background:#0f172a; color:#e5e7eb; border-radius:9999px; height:40px; padding:0 12px; display:inline-flex; align-items:center; gap:8px; max-width: 260px; }
.trigger.avatar img { width:24px; height:24px; object-fit:cover; border-radius:9999px; }
.trigger .label { font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:50 }
.modal { width: 560px; max-width: 90vw; background:#0b1223; border:1px solid #334155; border-radius:12px; padding:12px; box-shadow:0 14px 40px rgba(0,0,0,0.5) }
.modal-head { display:flex; gap:8px; align-items:center; }
.search { flex:1; padding:8px 10px; border:1px solid #334155; border-radius:10px; background:#0f172a; color:#e5e7eb }
.close { width:34px; height:34px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:#e5e7eb }
.grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-top:10px; }
.item { padding:10px; border:1px solid #334155; background:#0f172a; color:#e5e7eb; border-radius:10px; text-align:center }
.item:hover { background:#111827 }
@media (max-width: 520px){ .grid { grid-template-columns: repeat(2, 1fr); } }
</style>
  