<template>
  <div class="app-container">
    <!-- Фоновый градиент -->
    <div class="background"></div>
    
    <div class="content">
      <!-- Шапка -->
      <div class="header">
        <div class="coin-animation">🪙</div>
        <h1>Спорная монетка</h1>
        <p>Не хочешь выбирать — получишь спор</p>
      </div>
      
      <!-- Выбор режима -->
      <div class="mode-card">
        <p class="mode-title">🎭 Выбери характер спорщика</p>
        <div class="mode-buttons">
          <button 
            @click="selectedMode = 'cynic'" 
            :class="['mode-btn', selectedMode === 'cynic' && 'mode-active-cynic']"
          >
            <span>🤡</span> Циник
          </button>
          <button 
            @click="selectedMode = 'kind'" 
            :class="['mode-btn', selectedMode === 'kind' && 'mode-active-kind']"
          >
            <span>😇</span> Добрый
          </button>
          <button 
            @click="selectedMode = 'devil'" 
            :class="['mode-btn', selectedMode === 'devil' && 'mode-active-devil']"
          >
            <span>👿</span> Адвокат
          </button>
          <button 
            @click="selectedMode = 'lazy'" 
            :class="['mode-btn', selectedMode === 'lazy' && 'mode-active-lazy']"
          >
            <span>😴</span> Ленивец
          </button>
          <button
            @click="openTherapyMode"
            class="mode-btn special"
          >
            <span>🧠</span> Психолог
          </button>
        </div>
      </div>
      
      <!-- Форма - ВАЖНО: @submit.prevent -->
      <div v-if="!store.currentDecision && !isFlipping" class="form-card">
        <form @submit.prevent="handleSubmit">
          <div class="input-group">
            <label>Вариант А</label>
            <input v-model="form.optionA" type="text" required placeholder="Уйти с работы" />
          </div>
          
          <div class="input-group">
            <label>Вариант Б</label>
            <input v-model="form.optionB" type="text" required placeholder="Остаться" />
          </div>
          
          <button type="submit" :disabled="store.loading" class="submit-btn">
            {{ store.loading ? 'Кидаю монетку...' : '🪙 Подбросить монетку' }}
          </button>
        </form>
        <p v-if="store.error" class="error">{{ store.error }}</p>
      </div>
      
      <!-- Анимация подбрасывания монеты -->
      <div v-if="isFlipping" class="flip-animation-card">
        <div class="coin-flip-container">
          <div :class="['coin', { 'flipping': isFlipping, 'show-heads': coinFace === 'heads', 'show-tails': coinFace === 'tails' }]">
            <div class="coin-front">
              <div class="coin-emoji">🪙</div>
              <div class="coin-text">?</div>
            </div>
            <div class="coin-back">
              <div class="coin-emoji">💰</div>
              <div class="coin-text">?</div>
            </div>
          </div>
        </div>
        <p class="flip-text">Монетка в воздухе...</p>
      </div>
      
      <!-- Результат -->
      <div v-else-if="store.currentDecision" class="result-card">
        <div class="coin-result">
          <div class="coin-result-emoji" :class="{'heads': coinFace === 'heads', 'tails': coinFace === 'tails'}">
            {{ coinFace === 'heads' ? '🪙' : '💰' }}
          </div>
          <p>Монетка показала:</p>
          <h2>{{ store.currentDecision.coin_result }}</h2>
        </div>
        
        <div class="debate-card">
          <div class="mode-indicator">
            <span class="mode-emoji">
              {{ selectedMode === 'cynic' ? '🤡' : selectedMode === 'kind' ? '😇' : selectedMode === 'devil' ? '👿' : '😴' }}
            </span>
            <div>
              <div class="mode-label">Режим</div>
              <div class="mode-name">
                {{ selectedMode === 'cynic' ? 'Циник' : 
                   selectedMode === 'kind' ? 'Добрый советчик' : 
                   selectedMode === 'devil' ? 'Адвокат дьявола' : 'Ленивец' }}
              </div>
            </div>
          </div>
          
          <div class="question">
            <span>💭</span>
            <p>{{ store.currentDecision.provocative_question }}</p>
          </div>
          
          <p class="arguments-title">Вот почему стоит выбрать противоположный вариант:</p>
          
          <ul class="arguments-list">
            <li v-for="(arg, idx) in store.currentDecision.counter_arguments" :key="idx">
              <span class="arg-number">{{ idx + 1 }}</span>
              <span>{{ arg }}</span>
            </li>
          </ul>
          
          <div class="action-buttons">
            <button @click="shareResult" class="share-btn">
              <span>📤</span> Поделиться
            </button>
            <button @click="resetAndKeepMode" class="new-btn">
              <span>🔄</span> Сделать новый выбор
            </button>
          </div>
          
          <!-- Уведомление о копировании -->
          <div v-if="showCopyNotification" class="copy-notification">
            ✅ Результат скопирован в буфер обмена!
          </div>
        </div>
      </div>
      
      <div class="footer">
        <p>🪙 Монетка не предсказывает будущее. Она просто заставляет думать</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useDecisionStore } from '../stores/decision'

const store = useDecisionStore()
const form = reactive({ optionA: '', optionB: '' })
const selectedMode = ref('cynic')
const isFlipping = ref(false)
const coinFace = ref('heads')
const showCopyNotification = ref(false)

// Функция для генерации текста результата
function generateShareText() {
  const decision = store.currentDecision
  if (!decision) return ''
  
  const modeName = selectedMode.value === 'cynic' ? 'Циник' : 
                   selectedMode.value === 'kind' ? 'Добрый советчик' : 
                   selectedMode.value === 'devil' ? 'Адвокат дьявола' : 'Ленивец'
  
  const modeEmoji = selectedMode.value === 'cynic' ? '🤡' : 
                    selectedMode.value === 'kind' ? '😇' : 
                    selectedMode.value === 'devil' ? '👿' : '😴'
  
  let text = `🪙 Спорная монетка выпала: ${decision.coin_result}\n\n`
  text += `Выбор между:\n🔹 ${form.optionA}\n🔹 ${form.optionB}\n\n`
  text += `🎭 Режим: ${modeEmoji} ${modeName}\n\n`
  text += `💭 Провокационный вопрос:\n"${decision.provocative_question}"\n\n`
  text += `📢 Аргументы «против» выпавшего варианта:\n`
  
  decision.counter_arguments.forEach((arg, idx) => {
    text += `${idx + 1}. ${arg}\n`
  })
  
  text += `\n✨ Результат от «Спорной монетки» — попробуй сам: https://flipble.it-atp.ru`
  return text
}

// Функция поделиться результатом
async function shareResult() {
  const shareText = generateShareText()
  
  // Проверяем, поддерживается ли Web Share API
  if (navigator.share) {
    try {
      await navigator.share({
        title: 'Спорная монетка — результат',
        text: shareText,
      })
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Ошибка при попытке поделиться:', error)
        fallbackCopy(shareText)
      }
    }
  } else {
    // Fallback: копируем в буфер обмена
    fallbackCopy(shareText)
  }
}

// Резервное копирование в буфер обмена
async function fallbackCopy(text) {
  try {
    await navigator.clipboard.writeText(text)
    showCopyNotification.value = true
    setTimeout(() => {
      showCopyNotification.value = false
    }, 3000)
  } catch (error) {
    console.error('Не удалось скопировать текст:', error)
    alert('Не удалось поделиться результатом. Вы можете скопировать его вручную.')
  }
}

async function handleSubmit() {
  if (!form.optionA || !form.optionB) {
    alert('Пожалуйста, введите оба варианта')
    return
  }
  
  // Запускаем анимацию подбрасывания
  isFlipping.value = true
  coinFace.value = Math.random() < 0.5 ? 'heads' : 'tails'
  
  // Ждём анимацию (1.5 секунды)
  setTimeout(async () => {
    try {
      await store.flipCoin(form.optionA, form.optionB, selectedMode.value)
      // После получения результата обновляем лицо монетки в соответствии с результатом
      const coinResult = store.currentDecision?.coin_result?.toLowerCase()
      if (coinResult === 'орёл') {
        coinFace.value = 'heads'
      } else if (coinResult === 'решка') {
        coinFace.value = 'tails'
      }
    } catch (error) {
      console.error('Ошибка:', error)
    } finally {
      isFlipping.value = false
    }
  }, 1500)
}

function openTherapyMode() {
  window.location.href = '/therapy'
}

function resetAndKeepMode() {
  store.reset()
  form.optionA = ''
  form.optionB = ''
  coinFace.value = 'heads'
  showCopyNotification.value = false
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  min-height: 100vh;
  position: relative;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Фон */
.background {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 50%, #be185d 100%);
  z-index: 0;
}

.background::before {
  content: '';
  position: absolute;
  top: 20%;
  left: 10%;
  width: 300px;
  height: 300px;
  background: #8b5cf6;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.background::after {
  content: '';
  position: absolute;
  bottom: 20%;
  right: 10%;
  width: 400px;
  height: 400px;
  background: #ec4899;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
}

.content {
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Шапка */
.header {
  text-align: center;
  margin-bottom: 2rem;
}

.coin-animation {
  font-size: 5rem;
  display: inline-block;
  animation: bounce 2s ease-in-out infinite;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
}

.header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin-top: 1rem;
  background: linear-gradient(135deg, #fde047, #f97316, #ef4444);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.header p {
  color: #fcd34dcc;
  margin-top: 0.5rem;
  font-size: 1.1rem;
}

/* Карточка режимов */
.mode-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.mode-title {
  text-align: center;
  color: #fcd34d;
  margin-bottom: 1rem;
  font-weight: 500;
}

.mode-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: space-around;
}

.mode-btn {
  padding: 0.75rem 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.75rem;
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  min-width: 80px;
  flex: 1;
}

.mode-btn span {
  font-size: 1.5rem;
}

.mode-btn:hover {
  background: rgb(93, 45, 124);
  transform: scale(1.02);
}

.mode-active-cynic {
  background: linear-gradient(135deg, #9333ea, #4f46e5);
  box-shadow: 0 0 15px rgba(147, 51, 234, 0.5);
}

.mode-active-kind {
  background: linear-gradient(135deg, #059669, #0d9488);
  box-shadow: 0 0 15px rgba(5, 150, 105, 0.5);
}

.mode-active-devil {
  background: linear-gradient(135deg, #dc2626, #e11d48);
  box-shadow: 0 0 15px rgba(220, 38, 38, 0.5);
}

.mode-active-lazy {
  background: linear-gradient(135deg, #2563eb, #0891b2);
  box-shadow: 0 0 15px rgba(37, 99, 235, 0.5);
}

.special {
  background: linear-gradient(135deg, #7c3aed, #c026d3);
}

/* Форма */
.form-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.input-group {
  margin-bottom: 1.25rem;
}

.input-group label {
  display: block;
  color: #fcd34d;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  transition: all 0.2s;
}

.input-group input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(251, 146, 60, 0.5);
  background: white;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #eab308, #f97316, #ef4444);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #fca5a5;
  text-align: center;
  margin-top: 1rem;
  padding: 0.5rem;
  background: rgba(239, 68, 68, 0.2);
  border-radius: 0.5rem;
}

/* Анимация подбрасывания монеты */
.flip-animation-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.coin-flip-container {
  perspective: 1000px;
  width: 150px;
  height: 150px;
  margin: 0 auto;
}

.coin {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.2s;
  transform-style: preserve-3d;
  cursor: pointer;
}

.coin.flipping {
  animation: flipCoin 0.8s cubic-bezier(0.4, 0.0, 0.2, 1) 3;
}

.coin-front, .coin-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 35% 30%, #ffd700, #daa520);
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.coin-front {
  transform: rotateY(0deg);
}

.coin-back {
  transform: rotateY(180deg);
}

.coin-emoji {
  font-size: 4rem;
  filter: drop-shadow(0 2px 5px rgba(0,0,0,0.2));
}

.coin-text {
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 0.5rem;
  color: #b45309;
}

@keyframes flipCoin {
  0% {
    transform: rotateY(0deg);
  }
  100% {
    transform: rotateY(1080deg);
  }
}

.flip-text {
  text-align: center;
  color: #fcd34d;
  margin-top: 1.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

/* Результат */
.result-card {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.coin-result {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.coin-result-emoji {
  font-size: 5rem;
  animation: resultPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: inline-block;
}

.coin-result-emoji.heads {
  animation: bounceAndRotate 0.5s ease-out;
}

.coin-result-emoji.tails {
  animation: bounceAndRotateReverse 0.5s ease-out;
}

@keyframes bounceAndRotate {
  0% { transform: scale(0) rotate(-180deg); opacity: 0; }
  50% { transform: scale(1.2) rotate(0deg); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

@keyframes bounceAndRotateReverse {
  0% { transform: scale(0) rotate(180deg); opacity: 0; }
  50% { transform: scale(1.2) rotate(0deg); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

@keyframes resultPop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.coin-result p {
  color: #fcd34dcc;
  font-size: 0.8rem;
  text-transform: uppercase;
  margin-top: 0.5rem;
}

.coin-result h2 {
  font-size: 1.8rem;
  color: white;
  margin-top: 0.5rem;
}

.debate-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.mode-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 1rem;
}

.mode-emoji {
  font-size: 3rem;
}

.mode-label {
  font-size: 0.7rem;
  color: #fcd34dcc;
  text-transform: uppercase;
}

.mode-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: white;
}

.question {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  gap: 0.75rem;
  border-left: 4px solid #f97316;
  margin-bottom: 1rem;
}

.question span {
  font-size: 1.5rem;
}

.question p {
  color: #fcd34d;
  font-style: italic;
}

.arguments-title {
  font-weight: bold;
  color: white;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.arguments-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background: #f97316;
  border-radius: 2px;
}

.arguments-list {
  list-style: none;
  margin-bottom: 1.5rem;
}

.arguments-list li {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
}

.arg-number {
  width: 1.75rem;
  height: 1.75rem;
  background: linear-gradient(135deg, #f97316, #ef4444);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.arguments-list li span:last-child {
  color: #f3f4f6;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.share-btn, .new-btn {
  flex: 1;
  padding: 0.75rem;
  border-radius: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.share-btn {
  background: linear-gradient(135deg, #0ea5e9, #3b82f6);
  border: none;
  color: white;
}

.share-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.new-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.new-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.copy-notification {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(34, 197, 94, 0.9);
  border-radius: 0.75rem;
  text-align: center;
  color: white;
  font-weight: 500;
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.footer {
  text-align: center;
  margin-top: 2rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.8rem;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>