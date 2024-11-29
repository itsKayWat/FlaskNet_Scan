import { createStore } from 'vuex'
import servers from './modules/servers'
import auth from './modules/auth'
import notifications from './modules/notifications'
import monitoring from './modules/monitoring'

export default createStore({
  modules: {
    servers,
    auth,
    notifications,
    monitoring
  },
  
  state: {
    loading: false,
    darkMode: localStorage.getItem('darkMode') === 'true',
    sidebarCollapsed: false
  },
  
  mutations: {
    SET_LOADING(state, value) {
      state.loading = value
    },
    TOGGLE_DARK_MODE(state) {
      state.darkMode = !state.darkMode
      localStorage.setItem('darkMode', state.darkMode)
      document.documentElement.classList.toggle('dark-mode')
    },
    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    }
  },
  
  actions: {
    setLoading({ commit }, value) {
      commit('SET_LOADING', value)
    },
    toggleDarkMode({ commit }) {
      commit('TOGGLE_DARK_MODE')
    },
    toggleSidebar({ commit }) {
      commit('TOGGLE_SIDEBAR')
    }
  }
}) 