import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = '/api'

export const useDecisionStore = defineStore('decision', {
  state: () => ({
    currentDecision: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async flipCoin(optionA, optionB, mode = 'cynic') {
      this.loading = true
      this.error = null
      
      try {
        // Используем новый эндпоинт с кэшированием по режимам
        const response = await axios.post(`${API_URL}/flip-cached/`, {
          option_a: optionA,
          option_b: optionB,
          mode: mode
        })
        
        console.log(response.data.message)
        this.currentDecision = response.data
        return response.data
      } catch (err) {
        console.error('Ошибка:', err)
        this.error = err.response?.data?.error || 'Ошибка соединения с сервером'
        throw this.error
      } finally {
        this.loading = false
      }
    },
    
    reset() {
      this.currentDecision = null
      this.error = null
    }
  }
})