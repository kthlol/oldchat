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
            <div class="avatar">
              <img v-if="r.img" :src="r.img" alt="avatar" />
              <span v-else>{{ r.name.slice(0,1) }}</span>
            </div>
            <div class="info">
              <div class="name">{{ r.name }}</div>
              <div class="desc">{{ roleMeta[r.key]?.description }}</div>
            </div>
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
const candidate = ['socrates','storyteller','interviewer','harry_potter','sherlock','einstein']
const roleMeta: Record<string, { key: string, name: string, img?: string, description?: string }> = {
  socrates: { key: 'socrates', name: '苏格拉底', description: '古希腊哲学家，善于提问引导思考' },
  storyteller: { key: 'storyteller', name: '故事叙述者', description: '富有想象力的故事创作者' },
  interviewer: { key: 'interviewer', name: '面试官', description: '专业的职场面试专家' },
  harry_potter: { key: 'harry_potter', name: '哈利波特', description: '勇敢的魔法师，来自霍格沃茨' },
  sherlock: { key: 'sherlock', name: '夏洛克', description: '天才侦探，逻辑推理大师' },
  einstein: { key: 'einstein', name: '爱因斯坦', description: '伟大的物理学家，相对论之父' },
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
  const max = 8  // 减少最大长度，确保在200px宽度内显示
  if (name.length <= max) return name
  const head = name.slice(0, Math.ceil((max - 1) / 2))
  const tail = name.slice(-Math.floor((max - 1) / 2))
  return head + '…' + tail
})

function mapName(key: string){
  return roleMeta[key]?.name || key
}

function select(r: string){ store.setRole(r); open.value = false }
</script>
 
<style scoped>
.role-box { display:flex; align-items:center; gap:8px; }
.trigger { border:1px solid #d1d5db; background:#ffffff; color:#333333; border-radius:9999px; height:44px; padding:0 16px; display:inline-flex; align-items:center; gap:10px; max-width: 200px; min-width: 120px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.trigger.avatar img { width:28px; height:28px; object-fit:cover; border-radius:9999px; }
.trigger .label { font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex: 1; min-width: 0; }
.overlay { 
  position:fixed; 
  top:0; left:0; right:0; bottom:0; 
  background:rgba(0,0,0,.45); 
  display:flex; 
  align-items:center; 
  justify-content:center; 
  z-index:50; 
  padding:20px; 
  box-sizing:border-box;
}
.modal { width: 520px; max-width: 90vw; max-height: 80vh; overflow:auto; background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; box-shadow:0 14px 40px rgba(0,0,0,0.15) }
.modal-head { display:flex; gap:8px; align-items:center; }
.search { flex:1; padding:8px 10px; border:1px solid #d1d5db; border-radius:10px; background:#ffffff; color:#333333 }
.close { width:34px; height:34px; border-radius:8px; border:1px solid #d1d5db; background:#ffffff; color:#6b7280 }
.grid { display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:12px; }
.item { display:flex; align-items:center; gap:12px; padding:12px; border:1px solid #e5e7eb; background:#ffffff; color:#333333; border-radius:12px; text-align:left; transition:all 0.2s }
.item:hover { background:#f9fafb; border-color:#d1d5db }
.avatar { width:40px; height:40px; border-radius:50%; background:#f3f4f6; display:flex; align-items:center; justify-content:center; flex-shrink:0 }
.avatar img { width:100%; height:100%; object-fit:cover; border-radius:50% }
.avatar span { font-weight:600; font-size:16px }
.info { flex:1; min-width:0 }
.name { font-weight:600; margin-bottom:2px }
.desc { font-size:12px; color:#6b7280; line-height:1.4 }
@media (max-width: 520px){ .grid { grid-template-columns: 1fr; } }
</style>
  