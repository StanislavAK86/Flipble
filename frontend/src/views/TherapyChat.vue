<template>
  <div class="therapy-container">
    <div class="therapy-background"></div>
    
    <div class="therapy-content">
      <div class="therapy-header">
        <button @click="goBack" class="back-btn">← Назад</button>
        <div class="header-icon">🧠</div>
        <h1>AI-психолог</h1>
        <p>Напиши свою дилемму, и я помогу разобраться</p>
      </div>
      
      <div class="progress-bar" v-if="sessionId && !isFinished">
        <div class="progress-fill" :style="{ width: `${(userAnswersCount) / maxAnswers * 100}%` }"></div>
        <span class="progress-text">{{ userAnswersCount }} из {{ maxAnswers }} ответов</span>
      </div>
      
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.sender]">
          <div class="message-avatar">{{ msg.sender === 'user' ? '👤' : '🧠' }}</div>
          <div class="message-bubble">
            <div class="message-text">{{ msg.text }}</div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>
        
        <div v-if="isTyping" class="message bot">
          <div class="message-avatar">🧠</div>
          <div class="message-bubble typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      
      <div class="chat-input-area" v-if="!isFinished">
        <textarea
          v-model="userInput"
          @keypress="handleKeyPress"
          :disabled="isTyping"
          placeholder="Напишите свою дилемму или ответ..."
          rows="2"
        ></textarea>
        <button @click="sendMessage" :disabled="!userInput.trim() || isTyping" class="send-btn">
          📤
        </button>
      </div>
      
      <div v-if="showConclusionBtn && !isFinished" class="conclusion-area">
        <button @click="getConclusion" class="conclusion-btn">
          🧠 Получить вывод
        </button>
      </div>
      
      <div v-if="isFinished && conclusion" class="conclusion-card">
        <div class="conclusion-icon">📋</div>
        <div class="conclusion-text" v-html="conclusion"></div>
        <div class="conclusion-buttons">
          <button @click="startNewSession" class="new-session-btn">
            🔄 Новая консультация
          </button>
          <button @click="shareResult" class="share-btn">
            📤 Поделиться
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_URL = '/api'

const messages = ref([])
const userInput = ref('')
const isTyping = ref(false)
const isFinished = ref(false)
const showConclusionBtn = ref(false)
const conclusion = ref('')
const conclusionAdded = ref(false)
const sessionId = ref(null)
const messagesContainer = ref(null)
const maxAnswers = 5
const userAnswersCount = ref(0)
let waitingForDilemma = true
let optionA = '', optionB = ''

onMounted(() => {
  messages.value.push({
    sender: 'bot',
    text: 'Привет! Я AI-психолог. Напиши свою дилемму в формате:\n\n**Вариант А** vs **Вариант Б**\n\nНапример: "Уйти с работы vs Остаться"',
    time: getCurrentTime()
  })
  scrollToBottom()
})

async function sendMessage() {
  if (!userInput.value.trim() || isTyping.value || isFinished.value) return
  
  const message = userInput.value.trim()
  
  messages.value.push({
    sender: 'user',
    text: message,
    time: getCurrentTime()
  })
  
  userInput.value = ''
  scrollToBottom()
  
  if (waitingForDilemma) {
    parseDilemma(message)
    return
  }
  
  isTyping.value = true
  
  try {
    const response = await axios.post(`${API_URL}/therapy/chat/`, {
      session_id: sessionId.value,
      message: message,
      round: userAnswersCount.value + 1
    })
    
    userAnswersCount.value++
    
    const reply = response.data.reply
    if (reply) {
      messages.value.push({
        sender: 'bot',
        text: reply,
        time: getCurrentTime()
      })
    }
    
    if (userAnswersCount.value >= maxAnswers) {
      showConclusionBtn.value = true
    }
    
  } catch (error) {
    console.error('Ошибка:', error)
    messages.value.push({
      sender: 'bot',
      text: 'Извини, произошла ошибка. Попробуй ещё раз.',
      time: getCurrentTime()
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

function parseDilemma(message) {
  let a = '', b = ''
  
  if (message.includes(' vs ')) {
    const parts = message.split(' vs ')
    a = parts[0].trim()
    b = parts[1].trim()
  } else if (message.includes(' или ')) {
    const parts = message.split(' или ')
    a = parts[0].trim()
    b = parts[1].trim()
  } else if (message.includes(' - ')) {
    const parts = message.split(' - ')
    a = parts[0].trim()
    b = parts[1].trim()
  } else {
    messages.value.push({
      sender: 'bot',
      text: 'Пожалуйста, напиши дилемму в формате: "Вариант А vs Вариант Б"\n\nНапример: "Уйти с работы vs Остаться"',
      time: getCurrentTime()
    })
    scrollToBottom()
    return
  }
  
  if (a && b) {
    optionA = a
    optionB = b
    messages.value.push({
      sender: 'bot',
      text: `Понял! Твоя дилемма: "${optionA}" или "${optionB}".\n\nРасскажи, что тебя беспокоит в этом выборе?`,
      time: getCurrentTime()
    })
    startTherapySession()
  } else {
    messages.value.push({
      sender: 'bot',
      text: 'Не удалось распознать дилемму. Попробуй ещё раз.',
      time: getCurrentTime()
    })
  }
  scrollToBottom()
}

async function startTherapySession() {
  try {
    const response = await axios.post(`${API_URL}/therapy/start/`, {
      option_a: optionA,
      option_b: optionB
    })
    sessionId.value = response.data.session_id
    waitingForDilemma = false
    userAnswersCount.value = 0
  } catch (error) {
    console.error('Ошибка:', error)
    messages.value.push({
      sender: 'bot',
      text: 'Извини, произошла ошибка. Попробуй позже.',
      time: getCurrentTime()
    })
  }
}

async function getConclusion() {
  if (isTyping.value || conclusionAdded.value) return
  
  isTyping.value = true
  showConclusionBtn.value = false
  
  messages.value.push({
    sender: 'bot',
    text: 'Анализирую наш диалог...',
    time: getCurrentTime()
  })
  scrollToBottom()
  
  try {
    const response = await axios.post(`${API_URL}/therapy/conclusion/`, {
      session_id: sessionId.value
    })
    
    conclusion.value = response.data.conclusion
    isFinished.value = true
    conclusionAdded.value = true
    
    messages.value.pop()
    messages.value.push({
      sender: 'bot',
      text: '📋 Вот мой анализ:\n\n' + conclusion.value,
      time: getCurrentTime()
    })
    
  } catch (error) {
    console.error('Ошибка:', error)
    messages.value.pop()
    messages.value.push({
      sender: 'bot',
      text: 'Извини, произошла ошибка при анализе.',
      time: getCurrentTime()
    })
    conclusion.value = '**Вывод:** Доверься себе\n**Совет:** Сделай маленький шаг\n**Поддержка:** Ты справишься!'
    isFinished.value = true
    conclusionAdded.value = true
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

function startNewSession() {
  conclusion.value = ''
  conclusionAdded.value = false
  isFinished.value = false
  showConclusionBtn.value = false
  messages.value = []
  sessionId.value = null
  waitingForDilemma = true
  optionA = ''
  optionB = ''
  userAnswersCount.value = 0
  
  messages.value.push({
    sender: 'bot',
    text: 'Привет! Напиши свою новую дилемму в формате:\n\n**Вариант А** vs **Вариант Б**',
    time: getCurrentTime()
  })
  scrollToBottom()
}

function shareResult() {
  const text = `🧠 AI-психолог помог мне с выбором!\n\nДилемма: ${optionA} или ${optionB}\n\n${conclusion.value}`
  
  if (navigator.share) {
    navigator.share({ title: 'Спорная монетка - AI психолог', text: text })
  } else {
    navigator.clipboard.writeText(text)
    alert('Результат скопирован в буфер обмена!')
  }
}

function goBack() {
  router.push('/')
}

function handleKeyPress(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

function getCurrentTime() {
  return new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.therapy-container {
  min-height: 100vh;
  position: relative;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.therapy-background {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #2e1065 100%);
  z-index: 0;
}

.therapy-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.therapy-header {
  text-align: center;
  padding: 1rem;
  position: relative;
  flex-shrink: 0;
}

.back-btn {
  position: absolute;
  left: 0;
  top: 1rem;
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  cursor: pointer;
}

.header-icon {
  font-size: 3rem;
}

.therapy-header h1 {
  color: white;
  margin: 0.5rem 0 0;
}

.therapy-header p {
  color: #a5b4fc;
  margin: 0;
}

.progress-bar {
  background: rgba(255,255,255,0.2);
  border-radius: 1rem;
  height: 0.75rem;
  margin: 1rem 0;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.progress-fill {
  background: linear-gradient(90deg, #818cf8, #c084fc);
  height: 100%;
  border-radius: 1rem;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  right: 0;
  top: -1.5rem;
  font-size: 0.7rem;
  color: #a5b4fc;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  animation: fadeIn 0.3s ease;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 1.25rem;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #818cf8, #c084fc);
}

.message-text {
  color: white;
  line-height: 1.4;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.65rem;
  color: #a5b4fc;
  margin-top: 0.25rem;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
}

.typing-indicator span {
  width: 0.5rem;
  height: 0.5rem;
  background: #a5b4fc;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-0.5rem); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-input-area {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 2rem;
  margin-top: 1rem;
  flex-shrink: 0;
}

.chat-input-area textarea {
  flex: 1;
  background: rgba(255,255,255,0.9);
  border: none;
  border-radius: 1.5rem;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  resize: none;
  font-family: inherit;
}

.chat-input-area textarea:focus {
  outline: none;
  box-shadow: 0 0 0 2px #818cf8;
}

.send-btn {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #818cf8, #c084fc);
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.conclusion-area {
  text-align: center;
  padding: 1rem;
  flex-shrink: 0;
}

.conclusion-btn {
  background: linear-gradient(135deg, #10b981, #14b8a6);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
}

.conclusion-btn:hover {
  transform: scale(1.02);
}

.conclusion-card {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border-radius: 1.5rem;
  padding: 1.5rem;
  margin-top: 1rem;
  flex-shrink: 0;
  animation: fadeIn 0.5s ease;
}

.conclusion-icon {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}

.conclusion-text {
  color: white;
  line-height: 1.6;
  white-space: pre-wrap;
}

.conclusion-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.new-session-btn, .share-btn {
  flex: 1;
  padding: 0.75rem;
  margin-top: 0;
  border: none;
  border-radius: 2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.new-session-btn {
  background: rgba(255,255,255,0.2);
  color: white;
}

.new-session-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: scale(1.02);
}

.share-btn {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
}

.share-btn:hover {
  transform: scale(1.02);
}
</style>