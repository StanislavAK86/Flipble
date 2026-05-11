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
      <div v-if="!store.currentDecision" class="form-card">
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
      
      <!-- Результат -->
      <div v-else class="result-card">
        <div class="coin-result">
          <div class="coin-big">🪙</div>
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
          
          <button @click="resetAndKeepMode" class="new-btn">🔄 Сделать новый выбор</button>
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

async function handleSubmit() {
  if (!form.optionA || !form.optionB) {
    alert('Пожалуйста, введите оба варианта')
    return
  }
  
  try {
    await store.flipCoin(form.optionA, form.optionB, selectedMode.value)
  } catch (error) {
    console.error('Ошибка:', error)
  }
}

function openTherapyMode() {
  // Просто переходим на страницу психолога без параметров
  window.location.href = '/therapy'
}

function resetAndKeepMode() {
  store.reset()
  form.optionA = ''
  form.optionB = ''
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
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
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
}

.mode-btn span {
  font-size: 1.5rem;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.3);
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

.coin-big {
  font-size: 5rem;
  animation: bounce 0.6s ease-in-out infinite;
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

.new-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.75rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.new-btn:hover {
  background: rgba(255, 255, 255, 0.3);
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