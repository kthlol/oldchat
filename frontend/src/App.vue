<script setup>
import { ref, onUnmounted } from 'vue'
import RoleSelector from './components/RoleSelector.vue'
import AudioRecorder from './components/AudioRecorder.vue'
import ChatWindow from './components/ChatWindow.vue'
import TextChatBox from './components/TextChatBox.vue'
import { useSessionStore } from './store/session'
import { createWs } from './api/websocket'

const store = useSessionStore();
const text = ref('');
const weatherText = ref('今天是晴天');
const currentDate = ref('');
const dateText = ref('');
const weatherInfo = ref('');
const apiError = ref('');
let ws = null;
let weatherTimer = null;

// 获取当前日期
function getCurrentDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const day = now.getDate();
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  const weekday = weekdays[now.getDay()];
  
  return `${year}年${month}月${day}日 ${weekday}`;
}

// 获取天气信息
async function getWeather() {
  try {
    // 调用后端天气API，默认获取郑州天气
    const response = await fetch('http://localhost:8000/api/weather?city=410100');
    const data = await response.json();
    
    // 分离日期和天气信息
    const dateStr = getCurrentDate();
    dateText.value = `今天是${dateStr}`;
    
    // 更新错误信息（只在有错误时显示）
    apiError.value = data.error || '';
    
    // 格式化天气信息
    if (data.description) {
      // 从description中提取天气和温度信息
      const weatherMatch = data.description.match(/今天是(.+?)，(.+)/);
      if (weatherMatch) {
        weatherInfo.value = weatherMatch[2]; // 提取天气部分
      } else {
        weatherInfo.value = data.description;
      }
    } else {
      weatherInfo.value = `天气${data.weather || '晴天'}，温度${data.temperature || '18'}°C`;
    }
    
    // 保持原有的weatherText用于兼容
    weatherText.value = `${dateText.value}，${weatherInfo.value}`;
  } catch (error) {
    console.error('获取天气失败:', error);
    const dateStr = getCurrentDate();
    dateText.value = `今天是${dateStr}`;
    weatherInfo.value = '天气晴天，温度18°C';
    weatherText.value = `${dateText.value}，${weatherInfo.value}`;
    apiError.value = `无法连接到后端服务: ${error.message}`;
  }
}

// 启动定时器，每小时获取一次天气
function startWeatherTimer() {
  // 立即获取一次天气
  getWeather();
  
  // 设置定时器，每小时（3600000毫秒）获取一次天气
  weatherTimer = setInterval(() => {
    console.log('定时获取天气数据...');
    getWeather();
  }, 3600000); // 1小时 = 3600000毫秒
}

// 停止定时器
function stopWeatherTimer() {
  if (weatherTimer) {
    clearInterval(weatherTimer);
    weatherTimer = null;
    console.log('天气定时器已停止');
  }
}

// 页面加载时启动定时器
startWeatherTimer();

// 页面卸载时清理定时器
onUnmounted(() => {
  stopWeatherTimer();
});

function ensureWs(){ 
  if(!ws || ws.readyState===WebSocket.CLOSED){ 
    ws = createWs(); 
    ws.binaryType='arraybuffer'; 
    ws.onmessage = onMessage; 
  } 
}

function ensureWsReady() {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      ws = createWs();
      ws.binaryType = 'arraybuffer';
      ws.onmessage = onMessage;
    }
    
    if (ws.readyState === WebSocket.OPEN) {
      resolve(ws);
    } else if (ws.readyState === WebSocket.CONNECTING) {
      ws.onopen = () => resolve(ws);
      ws.onerror = (error) => reject(error);
    } else {
      reject(new Error('WebSocket connection failed'));
    }
  });
}

function onMessage(ev){
  if (typeof ev.data === 'string') {
    try {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'stt') store.updateSTT(msg.text);
      else if (msg.type === 'reply') {
        store.updateReply(msg.text);
        const last = store.messages[store.messages.length-1];
        if (last) store.updateMessage(last.id, { replyText: msg.text });
      } else if (msg.type === 'video') {
        // 处理视频消息
        const last = store.messages[store.messages.length-1];
        if (last) store.updateMessage(last.id, { videoFormat: msg.format });
      }
    } catch {}
  } else if (ev.data instanceof ArrayBuffer) {
    // 处理音频数据
    const blob = new Blob([ev.data], { type: 'audio/mpeg' });
    const url = URL.createObjectURL(blob);
    const last = store.messages[store.messages.length-1];
    if (last) store.updateMessage(last.id, { audioUrl: url });
    store.setSending(false);
  }
}

async function sendMessage(){
  const t = text.value.trim();
  if(!t) return;
  
  try {
    await ensureWsReady();
    const id = crypto.randomUUID();
    store.pushMessage({ id, userText: t, replyText: '' });
    store.setSending(true);
    ws.send(JSON.stringify({ type: 'TEXT', role: store.role, text: t }));
    text.value = '';
  } catch (error) {
    console.error('发送消息失败:', error);
    store.setSending(false);
  }
}

function startDictate() {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'zh-CN';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      text.value = transcript;
    };
    
    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error);
    };
    
    recognition.start();
  } else {
    alert('您的浏览器不支持语音识别功能');
  }
}

function startVoiceInput() {
  // 启动语音录制和对话
  console.log('启动语音模式');
  store.setVoiceMode(true);
  
  // 检查浏览器是否支持录音
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('您的浏览器不支持录音功能');
    return;
  }
  
  // 请求麦克风权限并开始录音
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];
      
      // 开始录音
      mediaRecorder.start();
      store.setRecording(true);
      
      // 收集音频数据
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      // 录音结束处理
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
        
        try {
          // 发送音频到后端
          await ensureWsReady();
          const id = crypto.randomUUID();
          store.pushMessage({ id, userText: '[语音消息]', replyText: '' });
          store.setSending(true);
          
          // 发送音频数据
          ws.send(audioBlob);
          ws.send(JSON.stringify({ type: 'END', role: store.role }));
        } catch (error) {
          console.error('发送音频失败:', error);
          store.setSending(false);
        }
        
        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };
      
      // 3秒后自动停止录音
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
          store.setRecording(false);
        }
      }, 3000);
      
    })
    .catch(error => {
      console.error('录音失败:', error);
      alert('无法访问麦克风，请检查权限设置');
      store.setRecording(false);
    });
}
</script>

<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo">
            <span class="logo-text">AI 角色对话</span>
            <svg class="chevron-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
            </svg>
          </div>
        </div>
        <div class="header-center">
          <button class="plus-button">
            <svg class="sparkle-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span>获取 Plus</span>
          </button>
        </div>
        <div class="header-right">
          <RoleSelector />
          <button class="menu-button">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main">
      <div class="main-content">
        <!-- 欢迎文本 -->
        <div class="welcome-section" v-if="store.messages.length === 0">
          <h1 class="welcome-text">
            <div class="date-line">{{ dateText || '今天是2025年9月24日 星期三' }}</div>
            <div class="weather-line">{{ weatherInfo || '天气阴天，温度18°C' }}</div>
          </h1>
          <!-- API状态提示 -->
          <div class="api-status" v-if="apiError">
            <div class="status-indicator error">
              <span class="status-icon">⚠️</span>
              <span class="status-text">{{ apiError }}</span>
            </div>
          </div>
        </div>
        
        <!-- 麦克风图标 -->
        <div class="microphone-section" v-if="store.messages.length === 0">
          <button 
            class="microphone-button" 
            :class="{ recording: store.isRecording }"
            @click="startVoiceInput"
            :disabled="store.isRecording"
          >
            <svg viewBox="0 0 24 24" width="80" height="80">
              <path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/>
            </svg>
          </button>
          <p class="recording-hint" v-if="store.isRecording">正在录音中...</p>
        </div>
        
        <!-- 聊天记录 -->
        <div class="chat-section" v-if="store.messages.length > 0">
          <ChatWindow />
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-container">
          <button class="attach-button" title="附加文件">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
            </svg>
          </button>
          
          <div class="input-wrapper">
            <input 
              v-model="text" 
              placeholder="询问任何问题" 
              class="main-input" 
              @keydown.enter.prevent="sendMessage"
            />
            <div class="input-actions">
              <button 
                class="voice-button" 
                @click="startDictate"
                title="语音输入"
              >
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"/>
                </svg>
              </button>
              <button 
                class="send-button" 
                @click="sendMessage"
                :disabled="!text.trim() || store.isSending"
                title="发送消息"
              >
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout { 
  min-height: 100vh; 
  background: #F5F5DC; 
  display: flex; 
  flex-direction: column; 
}

/* 顶部导航栏 */
.header {
  position: sticky;
  top: 0;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  z-index: 10;
  padding: 0 24px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}

.chevron-icon {
  color: #666666;
}

.header-center {
  display: flex;
  align-items: center;
}

.plus-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #8b5cf6;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.plus-button:hover {
  background: #7c3aed;
}

.sparkle-icon {
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-button {
  background: none;
  border: none;
  color: #666666;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.menu-button:hover {
  background: #f3f4f6;
}

/* 主内容区域 */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px 0;
  min-height: 60vh;
}

/* 欢迎文本 */
.welcome-section {
  text-align: center;
  margin-bottom: 50px;
  max-width: 600px;
}

.welcome-text {
  font-size: 28px;
  font-weight: 400;
  color: #333333;
  margin: 0;
  line-height: 1.4;
}

.date-line {
  margin-bottom: 12px;
  font-size: 28px;
}

.weather-line {
  font-size: 24px;
  color: #666666;
  font-weight: 300;
}

/* API状态提示 */
.api-status {
  margin-top: 20px;
  text-align: center;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  background: #f0f9ff;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.status-indicator.warning {
  background: #fef3c7;
  color: #d97706;
  border-color: #fde68a;
}

.status-indicator.error {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}

.status-icon {
  font-size: 16px;
}

.status-text {
  font-size: 13px;
}

.error-details {
  margin-top: 8px;
  color: #6b7280;
}

.error-details small {
  font-size: 12px;
  line-height: 1.4;
}

/* 麦克风图标 */
.microphone-section {
  text-align: center;
  margin-bottom: 50px;
}

.microphone-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 20px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  position: relative;
}

.microphone-button:hover {
  background: rgba(139, 92, 246, 0.1);
  transform: scale(1.05);
}

.microphone-button.recording {
  background: rgba(239, 68, 68, 0.1);
  animation: pulse 1.5s infinite;
}

.microphone-button svg {
  width: 60px;
  height: 60px;
  color: #8b5cf6;
  transition: color 0.3s ease;
}

.microphone-button.recording svg {
  color: #ef4444;
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

.recording-hint {
  margin-top: 16px;
  font-size: 14px;
  color: #ef4444;
  font-weight: 500;
}

/* 聊天区域 */
.chat-section {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* 输入区域 */
.input-section {
  padding: 30px 0 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 600px;
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input-container:focus-within {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.attach-button {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.attach-button:hover {
  background: #f3f4f6;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.main-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 12px 16px;
  font-size: 16px;
  color: #333333;
  min-height: 24px;
}

.main-input::placeholder {
  color: #9ca3af;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
}

.voice-button, .send-button {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-button:hover, .send-button:hover {
  background: #f3f4f6;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button:not(:disabled) {
  color: #3b82f6;
}

.send-button:not(:disabled):hover {
  background: #eff6ff;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .main {
    padding: 0 16px;
    max-width: 100%;
  }
  
  .main-content {
    padding: 40px 0;
    min-height: 50vh;
  }
  
  .welcome-section {
    margin-bottom: 40px;
    max-width: 100%;
  }
  
  .welcome-text {
    font-size: 24px;
  }
  
  .date-line {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .weather-line {
    font-size: 20px;
  }
  
  .microphone-section {
    margin-bottom: 40px;
  }
  
  .microphone-button {
    width: 100px;
    height: 100px;
  }
  
  .microphone-button svg {
    width: 50px;
    height: 50px;
  }
  
  .input-section {
    max-width: 100%;
    padding: 20px 0 30px;
  }
  
  .input-container {
    max-width: 100%;
    padding: 10px 12px;
  }
  
  .role-box .trigger {
    max-width: 150px;
    min-width: 100px;
  }
  
  .plus-button span {
    display: none;
  }
}

@media (max-width: 480px) {
  .welcome-text {
    font-size: 20px;
  }
  
  .date-line {
    font-size: 20px;
  }
  
  .weather-line {
    font-size: 18px;
  }
  
  .microphone-button {
    width: 80px;
    height: 80px;
  }
  
  .microphone-button svg {
    width: 40px;
    height: 40px;
  }
  
  .input-container {
    padding: 8px 10px;
    border-radius: 8px;
  }
  
  .main-content {
    padding: 30px 0;
    min-height: 40vh;
  }
  
  .main-input {
    font-size: 14px;
    padding: 10px 12px;
  }
}
</style>

