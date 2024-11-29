import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import { createRouter, createWebHistory } from 'vue-router'
import ServerManagement from '@/views/ServerManagement.vue'
import { fetchServers, createServer } from '@/api/servers'

jest.mock('@/api/servers')

describe('Server Management Integration', () => {
  let store
  let router
  let wrapper

  beforeEach(() => {
    store = createStore({
      modules: {
        servers: {
          namespaced: true,
          state: {
            servers: [],
            loading: false,
            error: null
          },
          mutations: {
            SET_SERVERS(state, servers) {
              state.servers = servers
            },
            ADD_SERVER(state, server) {
              state.servers.push(server)
            }
          },
          actions: {
            async fetchAllServers({ commit }) {
              const response = await fetchServers()
              commit('SET_SERVERS', response.data)
            },
            async createNewServer({ commit }, serverData) {
              const response = await createServer(serverData)
              commit('ADD_SERVER', response.data)
            }
          }
        }
      }
    })

    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/servers',
          name: 'servers',
          component: ServerManagement
        }
      ]
    })

    wrapper = mount(ServerManagement, {
      global: {
        plugins: [store, router],
        stubs: {
          'line-chart': true
        }
      }
    })
  })

  test('loads and displays servers', async () => {
    const servers = [
      { id: 1, name: 'Server 1' },
      { id: 2, name: 'Server 2' }
    ]
    
    fetchServers.mockResolvedValue({ data: servers })
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.findAll('.server-card')).toHaveLength(2)
  })

  test('creates new server and updates list', async () => {
    const newServer = {
      name: 'New Server',
      host: 'localhost',
      port: 8080
    }
    
    const createdServer = { id: 3, ...newServer }
    createServer.mockResolvedValue({ data: createdServer })
    
    await wrapper.find('[data-test="add-server"]').trigger('click')
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(createServer).toHaveBeenCalledWith(newServer)
    expect(wrapper.findAll('.server-card')).toHaveLength(3)
  })

  test('handles server filtering and sorting', async () => {
    const servers = [
      { id: 1, name: 'Production', status: 'running' },
      { id: 2, name: 'Development', status: 'stopped' },
      { id: 3, name: 'Testing', status: 'running' }
    ]
    
    fetchServers.mockResolvedValue({ data: servers })
    await wrapper.vm.$nextTick()
    
    // Test search
    await wrapper.find('[data-test="search-input"]').setValue('prod')
    expect(wrapper.findAll('.server-card')).toHaveLength(1)
    
    // Test status filter
    await wrapper.find('[data-test="status-filter"]').setValue('running')
    expect(wrapper.findAll('.server-card')).toHaveLength(2)
    
    // Test sorting
    await wrapper.find('[data-test="sort-select"]').setValue('name')
    const serverNames = wrapper.findAll('.server-title h3')
    expect(serverNames[0].text()).toBe('Development')
  })
}) 